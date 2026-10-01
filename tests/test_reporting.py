from __future__ import annotations

import unittest

from accountlens.reporting import build_briefing_pdf, build_slack_summary
from accountlens.schemas import (
    AccountBriefing,
    DecisionChainMap,
    DecisionChainNode,
    DecisionRole,
    RecommendedAction,
    RolePrediction,
    TeamActivityDigest,
)


class ReportingTests(unittest.TestCase):
    def test_single_page_pdf_and_slack_export(self) -> None:
        account = {
            "account_id": "A1",
            "name": "Fictional Beacon Group",
            "industry": "Enterprise Software",
            "stage": "commercial_review",
            "annual_value_usd": 250000,
        }
        role = RolePrediction(
            contact_id="C1",
            role=DecisionRole.CHAMPION,
            confidence=0.9,
            evidence_ids=["E1"],
            reason="Supported fixture.",
            abstained=False,
            source="llm",
        )
        briefing = AccountBriefing(
            account_id="A1",
            decision_roles=[role],
            cross_team_activity=[],
            risks=[],
            recommended_actions=[
                RecommendedAction(action="Confirm the decision path.", rationale="Reduce uncertainty.", evidence_ids=["E1"])
            ],
            limitations=["Synthetic fixture."],
        )
        chain = DecisionChainMap(
            account_id="A1",
            nodes=[
                DecisionChainNode(
                    contact_id="C1",
                    name="Alex Chen",
                    title="Programme Lead",
                    role=DecisionRole.CHAMPION,
                    confidence=0.9,
                    evidence_ids=["E1"],
                    review_status="candidate",
                )
            ],
            edges=[],
            missing_roles=[DecisionRole.ECONOMIC_BUYER],
            limitations=["Human confirmation required."],
        )
        activity = [
            TeamActivityDigest(
                internal_team="Sales",
                event_count=1,
                latest_date="2026-09-01",
                channels=["meeting"],
                event_ids=["E1"],
                importance="low",
                summary="Sales recorded one event.",
            )
        ]

        pdf = build_briefing_pdf(account, briefing, chain, activity, [])
        self.assertTrue(pdf.startswith(b"%PDF"))
        self.assertIn(b"/Count 1", pdf)
        slack = build_slack_summary(account, briefing, chain, activity, [])
        self.assertIn("Account Panorama Briefing", slack)
        self.assertIn("Confirm the decision path", slack)


if __name__ == "__main__":
    unittest.main()
