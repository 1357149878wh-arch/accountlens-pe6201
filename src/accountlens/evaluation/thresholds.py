"""Tune the hybrid abstention threshold without making additional API calls."""

from __future__ import annotations

import argparse
from pathlib import Path

from accountlens.baseline.rules import infer_roles
from accountlens.config import (
    DEFAULT_ABSTENTION_THRESHOLD,
    DEFAULT_DATA_DIR,
    DEFAULT_RESULTS_DIR,
)
from accountlens.evaluation.metrics import classification_metrics
from accountlens.io import load_dataset, read_json, write_json
from accountlens.pipeline.llm import reconcile_hybrid_roles
from accountlens.schemas import AccountBriefing


DEFAULT_THRESHOLDS = (0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95)


def select_threshold(rows: list[dict], default: float = DEFAULT_ABSTENTION_THRESHOLD) -> float:
    """Prefer quality, then coverage, then the threshold closest to the preset default."""
    if not rows:
        raise ValueError("At least one threshold result is required")
    best = max(
        rows,
        key=lambda row: (
            row["macro_f1"],
            row["accuracy"],
            row["coverage"],
            -abs(row["threshold"] - default),
        ),
    )
    return float(best["threshold"])


def sweep_hybrid_thresholds(dataset: dict, saved_result: dict, thresholds: tuple[float, ...]) -> dict:
    account_ids = [row["account_id"] for row in saved_result["runs"]]
    briefings = saved_result["briefings"]
    if len(account_ids) != len(briefings):
        raise ValueError("Saved H1 runs and briefings must have matching lengths")

    contacts_by_account = {
        account_id: [row for row in dataset["contacts"] if row["account_id"] == account_id]
        for account_id in account_ids
    }
    selected_ids = set(account_ids)
    truth = [row for row in dataset["role_truth"] if row["account_id"] in selected_ids]
    rows: list[dict] = []

    for threshold in thresholds:
        predictions: list[dict] = []
        for account_id, briefing_row in zip(account_ids, briefings, strict=True):
            contacts = contacts_by_account[account_id]
            rules_predictions = infer_roles(
                contacts,
                [row for row in dataset["interactions"] if row["account_id"] == account_id],
            )
            briefing = AccountBriefing.model_validate(briefing_row)
            reconciled = reconcile_hybrid_roles(briefing, contacts, rules_predictions, threshold)
            predictions.extend(role.model_dump(mode="json") for role in reconciled.decision_roles)
        metrics = classification_metrics(truth, predictions)
        rows.append(
            {
                "threshold": threshold,
                "accuracy": metrics["accuracy"],
                "macro_f1": metrics["macro_f1"],
                "coverage": metrics["coverage"],
            }
        )

    return {
        "experiment": "H1_threshold_sweep",
        "split": saved_result["split"],
        "source_result": "h1_validation.json",
        "additional_api_calls": 0,
        "selection_rule": "max macro_f1, then accuracy, coverage, then closest to preset default",
        "recommended_threshold": select_threshold(rows),
        "results": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_RESULTS_DIR / "h1_validation.json")
    parser.add_argument("--output", type=Path, default=DEFAULT_RESULTS_DIR / "h1_threshold_sweep_validation.json")
    args = parser.parse_args()
    result = sweep_hybrid_thresholds(load_dataset(DEFAULT_DATA_DIR), read_json(args.input), DEFAULT_THRESHOLDS)
    write_json(args.output, result)
    print(f"Recommended threshold: {result['recommended_threshold']:.2f}")
    print(f"Saved threshold sweep: {args.output}")


if __name__ == "__main__":
    main()
