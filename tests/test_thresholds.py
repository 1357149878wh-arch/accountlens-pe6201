from __future__ import annotations

import unittest

from accountlens.evaluation.thresholds import select_threshold


class ThresholdSelectionTests(unittest.TestCase):
    def test_quality_wins_before_default_proximity(self) -> None:
        rows = [
            {"threshold": 0.65, "macro_f1": 0.90, "accuracy": 0.90, "coverage": 0.80},
            {"threshold": 0.75, "macro_f1": 0.95, "accuracy": 0.92, "coverage": 0.75},
        ]
        self.assertEqual(select_threshold(rows), 0.75)

    def test_default_breaks_an_exact_quality_tie(self) -> None:
        rows = [
            {"threshold": 0.60, "macro_f1": 1.0, "accuracy": 1.0, "coverage": 0.8},
            {"threshold": 0.65, "macro_f1": 1.0, "accuracy": 1.0, "coverage": 0.8},
        ]
        self.assertEqual(select_threshold(rows), 0.65)


if __name__ == "__main__":
    unittest.main()
