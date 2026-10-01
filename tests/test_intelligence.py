from __future__ import annotations

import unittest
from datetime import date

from accountlens.intelligence import (
    aggregate_cross_team_activity,
    build_decision_chain,
    decision_chain_graphviz,
    detect_risk_signals,
    filter_recent_interactions,
)


class IntelligenceTests(unittest.TestCase):
    def test_recent_window_is_inclusive_and_sorted(self) -> None:
        rows = [
            {"event_id": "E1", "date": "2026-08-02"},
            {"event_id": "E2", "date": "2026-09-01"},
            {"event_id": "E3", "date": "2026-08-01"},
        ]
        recent = filter_recent_interactions(rows, date(2026, 9, 1), days=30)
        self.assertEqual([row["event_id"] for row in recent], ["E2", "E1"])

    def test_risk_detectors_cover_statement_categories(self) -> None:
        rows = [
            {
                "event_id": "E1",
                "channel": "ticket",
                "status": "open",
                "subject": "Deployment incident",
                "content": "Still unresolved",
            },
            {
                "event_id": "E2",
                "channel": "email",
                "status": "awaiting_response",
                "subject": "Proposal follow-up",
                "content": "Awaiting response",
            },
            {
                "event_id": "E3",
                "channel": "meeting",
                "status": "completed",
                "subject": "Alternative review",
                "content": "The customer is evaluating a competitor.",
            },
        ]
        categories = {risk.category for risk in detect_risk_signals(rows)}
        self.assertEqual(categories, {"unresolved_ticket", "unanswered_email", "competitor_signal"})

    def test_chain_and_team_aggregation(self) -> None:
        roles = ["end_user", "champion", "technical_evaluator", "procurement_legal", "economic_buyer"]
        contacts = [
            {
                "contact_id": f"C{index}",
                "account_id": "A1",
                "name": f"Person {index}",
                "title": role,
                "department": "Test",
                "seniority": "manager",
            }
            for index, role in enumerate(roles, 1)
        ]
        predictions = [
            {
                "contact_id": contact["contact_id"],
                "role": role,
                "confidence": 0.9,
                "evidence_ids": [f"E{index}"],
                "reason": "Supported fixture.",
                "abstained": False,
                "source": "llm",
            }
            for index, (contact, role) in enumerate(zip(contacts, roles, strict=True), 1)
        ]
        chain = build_decision_chain("A1", contacts, predictions)
        self.assertEqual(len(chain.edges), 5)
        self.assertFalse(chain.missing_roles)
        self.assertIn("requirements flow", decision_chain_graphviz(chain))

        activity = aggregate_cross_team_activity(
            [
                {
                    "event_id": "E1",
                    "date": "2026-09-01",
                    "channel": "ticket",
                    "internal_team": "Customer Success",
                    "status": "open",
                },
                {
                    "event_id": "E2",
                    "date": "2026-08-31",
                    "channel": "email",
                    "internal_team": "Sales",
                    "status": "completed",
                },
            ]
        )
        self.assertEqual(activity[0].internal_team, "Customer Success")
        self.assertEqual(activity[0].importance, "high")


if __name__ == "__main__":
    unittest.main()
