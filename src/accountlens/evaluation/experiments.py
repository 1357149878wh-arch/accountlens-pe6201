"""Run or dry-run the B0, M1, M2, and H1 AccountLens experiments."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

from accountlens.baseline.rules import infer_roles
from accountlens.config import (
    DEFAULT_ABSTENTION_THRESHOLD,
    DEFAULT_DATA_DIR,
    DEFAULT_MODEL,
    DEFAULT_RESULTS_DIR,
)
from accountlens.evaluation.metrics import classification_metrics
from accountlens.evaluation.run import run_evaluation
from accountlens.io import load_dataset, write_json
from accountlens.pipeline.llm import EXPERIMENT_PROMPTS, build_account_context, run_briefing


EXPERIMENTS = ("B0", "M1", "M2", "H1")


def _percentile_95(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    return ordered[max(0, math.ceil(0.95 * len(ordered)) - 1)]


def _references_from_briefing(briefing: dict) -> set[str]:
    references: set[str] = set()
    for role in briefing["decision_roles"]:
        references.update(role["evidence_ids"])
    for activity in briefing["cross_team_activity"]:
        references.update(activity["event_ids"])
    for risk in briefing["risks"]:
        references.update(risk["evidence_ids"])
    for action in briefing["recommended_actions"]:
        references.update(action["evidence_ids"])
    return references


def dry_run_experiment(
    dataset: dict,
    experiment: str,
    split: str,
    limit: int | None,
) -> dict:
    account_ids = list(dataset["splits"][split])
    if limit is not None:
        account_ids = account_ids[:limit]
    account_by_id = {row["account_id"]: row for row in dataset["accounts"]}
    payload_sizes: list[int] = []
    for account_id in account_ids:
        contacts = [row for row in dataset["contacts"] if row["account_id"] == account_id]
        interactions = [row for row in dataset["interactions"] if row["account_id"] == account_id]
        rules_predictions = infer_roles(contacts, interactions) if experiment == "H1" else None
        payload_sizes.append(
            len(build_account_context(account_by_id[account_id], contacts, interactions, rules_predictions))
        )
    return {
        "mode": "dry_run",
        "experiment": experiment,
        "split": split,
        "accounts": len(account_ids),
        "model": None if experiment == "B0" else DEFAULT_MODEL,
        "prompt": None if experiment == "B0" else EXPERIMENT_PROMPTS[experiment].name,
        "average_payload_characters": round(sum(payload_sizes) / len(payload_sizes), 1) if payload_sizes else 0,
        "api_calls_planned": 0 if experiment == "B0" else len(account_ids),
        "test_split_frozen": split == "test",
    }


def run_ai_experiment(
    dataset: dict,
    experiment: str,
    split: str,
    limit: int | None,
    threshold: float,
) -> dict:
    account_ids = list(dataset["splits"][split])
    if limit is not None:
        account_ids = account_ids[:limit]
    account_by_id = {row["account_id"]: row for row in dataset["accounts"]}
    predictions: list[dict] = []
    run_rows: list[dict] = []
    briefings: list[dict] = []

    for index, account_id in enumerate(account_ids, start=1):
        account = account_by_id[account_id]
        contacts = [row for row in dataset["contacts"] if row["account_id"] == account_id]
        interactions = [row for row in dataset["interactions"] if row["account_id"] == account_id]
        print(f"[{index}/{len(account_ids)}] {experiment} {account_id}")
        run = run_briefing(
            account,
            contacts,
            interactions,
            experiment=experiment,
            threshold=threshold,
        )
        briefing_row = run.briefing.model_dump(mode="json")
        briefings.append(briefing_row)
        predictions.extend(role.model_dump(mode="json") for role in run.briefing.decision_roles)
        run_rows.append(
            {
                "account_id": account_id,
                "usage": run.usage.model_dump(mode="json"),
                "validation": run.validation.model_dump(mode="json"),
            }
        )

    selected_ids = set(account_ids)
    truth = [row for row in dataset["role_truth"] if row["account_id"] in selected_ids]
    metrics = classification_metrics(truth, predictions)
    critical_truth = [row for row in dataset["critical_truth"] if row["account_id"] in selected_ids]
    all_references: set[str] = set()
    for briefing in briefings:
        all_references.update(_references_from_briefing(briefing))
    found_critical = sum(row["event_id"] in all_references for row in critical_truth)
    critical_recall = found_critical / len(critical_truth) if critical_truth else 0.0

    total_refs = sum(row["validation"]["total_reference_count"] for row in run_rows)
    valid_refs = sum(row["validation"]["valid_reference_count"] for row in run_rows)
    latencies = [row["usage"]["latency_seconds"] for row in run_rows]
    return {
        "mode": "live",
        "experiment": experiment,
        "split": split,
        "accounts": len(account_ids),
        "threshold": threshold,
        "model": DEFAULT_MODEL,
        "metrics": metrics,
        "critical_event_recall": round(critical_recall, 4),
        "evidence_precision": round(valid_refs / total_refs if total_refs else 0.0, 4),
        "usage": {
            "input_tokens": sum(row["usage"]["input_tokens"] for row in run_rows),
            "output_tokens": sum(row["usage"]["output_tokens"] for row in run_rows),
            "estimated_cost_usd": round(sum(row["usage"]["estimated_cost_usd"] for row in run_rows), 6),
            "p95_latency_seconds": round(_percentile_95(latencies), 4),
        },
        "runs": run_rows,
        "predictions": predictions,
        "briefings": briefings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", choices=[*EXPERIMENTS, "all"], default="all")
    parser.add_argument("--split", choices=["development", "validation", "test"], default="development")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--threshold", type=float, default=DEFAULT_ABSTENTION_THRESHOLD)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_RESULTS_DIR)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--confirm-test",
        action="store_true",
        help="Required for live AI runs on the frozen test split.",
    )
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be at least 1")
    if not 0.0 <= args.threshold <= 1.0:
        parser.error("--threshold must be between 0 and 1")

    selected = list(EXPERIMENTS) if args.experiment == "all" else [args.experiment]
    if args.split == "test" and not args.dry_run and any(name != "B0" for name in selected) and not args.confirm_test:
        parser.error("Live AI runs on test require --confirm-test. Freeze the prompt and threshold first.")

    dataset = load_dataset(args.data_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for experiment in selected:
        if args.dry_run:
            result = dry_run_experiment(dataset, experiment, args.split, args.limit)
        elif experiment == "B0":
            result = run_evaluation(args.data_dir, args.split)
        else:
            result = run_ai_experiment(dataset, experiment, args.split, args.limit, args.threshold)
        suffix = "dry_run" if args.dry_run else args.split
        output = args.output_dir / f"{experiment.lower()}_{suffix}.json"
        write_json(output, result)
        print(f"Saved {experiment}: {output}")


if __name__ == "__main__":
    main()
