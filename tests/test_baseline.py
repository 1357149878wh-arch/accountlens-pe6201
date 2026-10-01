from __future__ import annotations

import unittest

from accountlens.baseline.rules import infer_contact_role


class BaselineTests(unittest.TestCase):
    def test_economic_buyer_inference(self) -> None:
        contact = {
            "contact_id": "CON-1",
            "account_id": "ACC-1",
            "name": "Alex Chen",
            "title": "Finance Director",
            "department": "Finance",
            "seniority": "director",
        }
        events = [
            {
                "event_id": "EVT-1",
                "account_id": "ACC-1",
                "participant_ids": ["CON-1"],
                "subject": "Budget approval review",
                "content": "Requested ROI before approving the purchase.",
            }
        ]
        prediction = infer_contact_role(contact, events)
        self.assertEqual(prediction["role"], "economic_buyer")
        self.assertIn("EVT-1", prediction["evidence_ids"])

    def test_unknown_contact_abstains(self) -> None:
        contact = {
            "contact_id": "CON-2",
            "account_id": "ACC-1",
            "name": "Jordan Lim",
            "title": "Coordinator",
            "department": "Administration",
            "seniority": "manager",
        }
        prediction = infer_contact_role(contact, [])
        self.assertEqual(prediction["role"], "unknown")
        self.assertTrue(prediction["abstained"])


if __name__ == "__main__":
    unittest.main()

