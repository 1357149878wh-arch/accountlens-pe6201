"""Test experiment dry runs and hybrid-context payload construction."""

from __future__ import annotations

import unittest
from datetime import date

from accountlens.data.generate import build_dataset
from accountlens.evaluation.experiments import dry_run_experiment


class ExperimentTests(unittest.TestCase):
    def test_hybrid_dry_run_includes_rules_context(self) -> None:
        dataset = build_dataset(12, 6201, date(2026, 9, 1))
        account_ids = [row["account_id"] for row in dataset["accounts"]]
        dataset["splits"] = {
            "development": account_ids[:6],
            "validation": account_ids[6:8],
            "test": account_ids[8:],
        }
        m2 = dry_run_experiment(dataset, "M2", "validation", None)
        h1 = dry_run_experiment(dataset, "H1", "validation", None)
        self.assertEqual(m2["api_calls_planned"], 2)
        self.assertGreater(h1["average_payload_characters"], m2["average_payload_characters"])


if __name__ == "__main__":
    unittest.main()

