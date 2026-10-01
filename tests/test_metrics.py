"""Test role-classification and commercial-signatory selection metrics."""

from __future__ import annotations

import unittest

from accountlens.evaluation.metrics import classification_metrics, signatory_selection_metrics


class MetricsTests(unittest.TestCase):
    def test_perfect_predictions(self) -> None:
        labels = ["champion", "economic_buyer", "technical_evaluator", "procurement_legal", "end_user", "unknown"]
        truth = [{"contact_id": f"C-{i}", "role": label} for i, label in enumerate(labels)]
        predictions = [
            {"contact_id": f"C-{i}", "role": label, "abstained": label == "unknown"}
            for i, label in enumerate(labels)
        ]
        result = classification_metrics(truth, predictions)
        self.assertEqual(result["accuracy"], 1.0)
        self.assertEqual(result["macro_f1"], 1.0)
        self.assertAlmostEqual(result["coverage"], 5 / 6, places=4)

    def test_signatory_selection_reports_precision_and_coverage(self) -> None:
        accounts = [
            {"account_id": "A-1", "true_signatory_contact_id": "C-1"},
            {"account_id": "A-2", "true_signatory_contact_id": "C-3"},
        ]
        contacts = [
            {"account_id": "A-1", "contact_id": "C-1"},
            {"account_id": "A-1", "contact_id": "C-2"},
            {"account_id": "A-2", "contact_id": "C-3"},
            {"account_id": "A-2", "contact_id": "C-4"},
        ]
        predictions = [
            {"contact_id": "C-1", "role": "economic_buyer", "confidence": 0.9, "abstained": False},
            {"contact_id": "C-3", "role": "unknown", "confidence": 0.4, "abstained": True},
        ]
        result = signatory_selection_metrics(accounts, contacts, predictions)
        self.assertEqual(result["precision"], 1.0)
        self.assertEqual(result["recall"], 0.5)
        self.assertEqual(result["selection_rate"], 0.5)
        self.assertEqual(result["correct_selections"], 1)


if __name__ == "__main__":
    unittest.main()
