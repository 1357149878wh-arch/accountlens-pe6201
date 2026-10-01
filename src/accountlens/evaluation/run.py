"""Run the rules baseline on one frozen data split."""

from __future__ import annotations

import argparse
from pathlib import Path

from accountlens.baseline.rules import infer_roles
from accountlens.config import DEFAULT_DATA_DIR, DEFAULT_RESULTS_DIR
from accountlens.evaluation.metrics import classification_metrics
from accountlens.io import load_dataset, write_json


def run_evaluation(data_dir: Path, split: str) -> dict:
    dataset = load_dataset(data_dir)
    if split not in dataset["splits"]:
        raise ValueError(f"Unknown split: {split}")
    account_ids = set(dataset["splits"][split])
    contacts = [row for row in dataset["contacts"] if row["account_id"] in account_ids]
    interactions = [row for row in dataset["interactions"] if row["account_id"] in account_ids]
    truth = [row for row in dataset["role_truth"] if row["account_id"] in account_ids]
    predictions = infer_roles(contacts, interactions)
    metrics = classification_metrics(truth, predictions)
    return {"experiment": "rules_baseline", "split": split, "metrics": metrics, "predictions": predictions}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--split", choices=["development", "validation", "test"], default="validation")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or DEFAULT_RESULTS_DIR / f"baseline_{args.split}.json"
    result = run_evaluation(args.data_dir, args.split)
    write_json(output, result)
    metrics = result["metrics"]
    print(f"Rules baseline ({args.split})")
    print(f"Samples: {metrics['samples']}")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"Macro-F1: {metrics['macro_f1']:.4f}")
    print(f"Coverage: {metrics['coverage']:.4f}")
    print(f"Saved: {output}")


if __name__ == "__main__":
    main()

