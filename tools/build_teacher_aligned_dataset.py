"""Build and validate the isolated ten-account instructor-aligned dataset."""

from __future__ import annotations

from pathlib import Path

from accountlens.baseline.rules import infer_roles
from accountlens.data.teacher_aligned import build_teacher_aligned_dataset, save_teacher_aligned_dataset
from accountlens.evaluation.metrics import classification_metrics, signatory_selection_metrics
from accountlens.io import write_json


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "teacher_aligned_10"
RESULT_PATH = ROOT / "results" / "teacher_aligned_baseline.json"


def main() -> None:
    dataset = build_teacher_aligned_dataset()
    manifest = save_teacher_aligned_dataset(dataset, DATA_DIR)
    predictions = infer_roles(dataset["contacts"], dataset["interactions"])
    result = {
        "dataset": "teacher_aligned_10",
        "experiment": "rules_baseline",
        "model_calls_made": 0,
        "classification_metrics": classification_metrics(dataset["role_truth"], predictions),
        "signatory_metrics": signatory_selection_metrics(dataset["accounts"], dataset["contacts"], predictions),
        "predictions": predictions,
    }
    write_json(RESULT_PATH, result)
    print(f"Built {manifest['counts']['accounts']} hand-authored accounts in {DATA_DIR}")
    print(f"Emails: {manifest['counts']['emails']}; meetings: {manifest['counts']['meetings']}; tickets: {manifest['counts']['tickets']}")
    print(f"Baseline result: {RESULT_PATH}")


if __name__ == "__main__":
    main()
