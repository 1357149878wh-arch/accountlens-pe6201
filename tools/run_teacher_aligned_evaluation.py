"""Evaluate M2 once on the frozen, instructor-aligned ten-account dataset."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from accountlens.config import DEFAULT_ABSTENTION_THRESHOLD, DEFAULT_MODEL
from accountlens.evaluation.metrics import classification_metrics, signatory_selection_metrics
from accountlens.io import load_dataset, write_json
from accountlens.pipeline.llm import build_account_context, run_briefing


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "teacher_aligned_10"
RESULT_PATH = ROOT / "results" / "teacher_aligned_m2.json"


def _percentile_95(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    return ordered[max(0, math.ceil(0.95 * len(ordered)) - 1)]


def _references(briefing: dict) -> set[str]:
    references: set[str] = set()
    for row in briefing["decision_roles"]:
        references.update(row["evidence_ids"])
    for row in briefing["cross_team_activity"]:
        references.update(row["event_ids"])
    for row in briefing["risks"]:
        references.update(row["evidence_ids"])
    for row in briefing["recommended_actions"]:
        references.update(row["evidence_ids"])
    return references


def dry_run(dataset: dict) -> dict:
    account_by_id = {row["account_id"]: row for row in dataset["accounts"]}
    payload_sizes: list[int] = []
    for account_id in dataset["splits"]["teacher_validation"]:
        contacts = [row for row in dataset["contacts"] if row["account_id"] == account_id]
        interactions = [row for row in dataset["interactions"] if row["account_id"] == account_id]
        payload_sizes.append(len(build_account_context(account_by_id[account_id], contacts, interactions)))
    return {
        "mode": "dry_run",
        "dataset": "teacher_aligned_10",
        "accounts": len(payload_sizes),
        "model": DEFAULT_MODEL,
        "api_calls_planned": len(payload_sizes),
        "average_payload_characters": round(sum(payload_sizes) / len(payload_sizes), 1),
        "estimated_upper_bound_usd": 0.25,
        "note": "Upper bound is a planning allowance, not a billing quote.",
    }


def run_live(dataset: dict) -> dict:
    account_ids = list(dataset["splits"]["teacher_validation"])
    account_by_id = {row["account_id"]: row for row in dataset["accounts"]}
    predictions: list[dict] = []
    briefings: list[dict] = []
    runs: list[dict] = []

    for index, account_id in enumerate(account_ids, start=1):
        account = account_by_id[account_id]
        contacts = [row for row in dataset["contacts"] if row["account_id"] == account_id]
        interactions = [row for row in dataset["interactions"] if row["account_id"] == account_id]
        print(f"[{index}/{len(account_ids)}] M2 {account_id}")
        run = run_briefing(
            account,
            contacts,
            interactions,
            experiment="M2",
            threshold=DEFAULT_ABSTENTION_THRESHOLD,
        )
        briefing = run.briefing.model_dump(mode="json")
        briefings.append(briefing)
        predictions.extend(row.model_dump(mode="json") for row in run.briefing.decision_roles)
        runs.append(
            {
                "account_id": account_id,
                "usage": run.usage.model_dump(mode="json"),
                "validation": run.validation.model_dump(mode="json"),
            }
        )

    referenced_ids: set[str] = set()
    for briefing in briefings:
        referenced_ids.update(_references(briefing))
    critical_found = sum(row["event_id"] in referenced_ids for row in dataset["critical_truth"])
    total_references = sum(row["validation"]["total_reference_count"] for row in runs)
    valid_references = sum(row["validation"]["valid_reference_count"] for row in runs)
    latencies = [row["usage"]["latency_seconds"] for row in runs]

    manifest = json.loads((DATA_DIR / "manifest.json").read_text(encoding="utf-8"))
    return {
        "mode": "live",
        "dataset": "teacher_aligned_10",
        "dataset_hashes": manifest["sha256"],
        "experiment": "M2",
        "accounts": len(account_ids),
        "model": DEFAULT_MODEL,
        "threshold": DEFAULT_ABSTENTION_THRESHOLD,
        "classification_metrics": classification_metrics(dataset["role_truth"], predictions),
        "signatory_metrics": signatory_selection_metrics(dataset["accounts"], dataset["contacts"], predictions),
        "critical_event_recall": round(critical_found / len(dataset["critical_truth"]), 4),
        "evidence_precision": round(valid_references / total_references if total_references else 0.0, 4),
        "usage": {
            "input_tokens": sum(row["usage"]["input_tokens"] for row in runs),
            "output_tokens": sum(row["usage"]["output_tokens"] for row in runs),
            "estimated_cost_usd": round(sum(row["usage"]["estimated_cost_usd"] for row in runs), 6),
            "p95_latency_seconds": round(_percentile_95(latencies), 4),
        },
        "runs": runs,
        "predictions": predictions,
        "briefings": briefings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--confirm-paid-run",
        action="store_true",
        help="Make the ten live API calls. Without this flag, only a dry run is shown.",
    )
    args = parser.parse_args()
    dataset = load_dataset(DATA_DIR)
    if not args.confirm_paid_run:
        print(json.dumps(dry_run(dataset), indent=2))
        return

    result = run_live(dataset)
    write_json(RESULT_PATH, result)
    print(f"Saved: {RESULT_PATH}")


if __name__ == "__main__":
    main()
