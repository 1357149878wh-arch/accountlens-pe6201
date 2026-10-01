from __future__ import annotations

import json
import unittest
from datetime import date
from pathlib import Path
from types import SimpleNamespace

from accountlens.data.generate import build_dataset
from accountlens.pipeline.llm import build_account_context, run_briefing, validate_evidence
from accountlens.schemas import (
    AccountBriefing,
    ActivitySummary,
    DecisionRole,
    RolePrediction,
)


class FakeResponses:
    def __init__(self, responses: list[object]) -> None:
        self.responses = responses
        self.calls: list[dict] = []

    def parse(self, **kwargs):
        self.calls.append(kwargs)
        response = self.responses[len(self.calls) - 1]
        if isinstance(response, Exception):
            raise response
        return response


class FakeClient:
    def __init__(self, responses: list[object]) -> None:
        self.responses = FakeResponses(responses)


def sample_case() -> tuple[dict, list[dict], list[dict]]:
    dataset = build_dataset(6, 6201, date(2026, 9, 1))
    account = dataset["accounts"][0]
    account_id = account["account_id"]
    contacts = [row for row in dataset["contacts"] if row["account_id"] == account_id]
    interactions = [row for row in dataset["interactions"] if row["account_id"] == account_id]
    return account, contacts, interactions


def make_briefing(account: dict, contacts: list[dict], interactions: list[dict], event_id: str) -> AccountBriefing:
    roles = [
        RolePrediction(
            contact_id=contact["contact_id"],
            role=DecisionRole.UNKNOWN,
            confidence=0.4,
            evidence_ids=[],
            reason="Insufficient evidence in this test fixture.",
            abstained=True,
            source="llm",
        )
        for contact in contacts
    ]
    return AccountBriefing(
        account_id=account["account_id"],
        decision_roles=roles,
        cross_team_activity=[
            ActivitySummary(event_ids=[event_id], summary="A supported account event occurred.", importance="medium")
        ],
        risks=[],
        recommended_actions=[],
        limitations=["Synthetic test fixture."],
    )


def fake_response(briefing: AccountBriefing, request_id: str) -> object:
    return SimpleNamespace(
        id=request_id,
        output_parsed=briefing,
        usage=SimpleNamespace(input_tokens=100, output_tokens=50, total_tokens=150),
    )


class PipelineTests(unittest.TestCase):
    def test_signatory_ground_truth_is_not_sent_to_the_model(self) -> None:
        account, contacts, interactions = sample_case()
        context = build_account_context(account, contacts, interactions)
        self.assertNotIn("true_signatory_contact_id", context)
        self.assertNotIn(account["true_signatory_contact_id"], json.loads(context)["account"].values())

    def test_validation_rejects_invalid_evidence(self) -> None:
        account, contacts, interactions = sample_case()
        briefing = make_briefing(account, contacts, interactions, "EVT-NOT-REAL")
        report = validate_evidence(briefing, account, contacts, interactions)
        self.assertFalse(report.passed)
        self.assertTrue(any("Invalid evidence IDs" in error for error in report.errors))

    def test_m1_style_validation_allows_missing_but_not_invalid_evidence(self) -> None:
        account, contacts, interactions = sample_case()
        briefing = make_briefing(account, contacts, interactions, interactions[0]["event_id"])
        briefing = briefing.model_copy(update={"cross_team_activity": []})
        report = validate_evidence(
            briefing,
            account,
            contacts,
            interactions,
            require_evidence=False,
        )
        self.assertTrue(report.passed)

    def test_invalid_evidence_is_retried_and_usage_is_accumulated(self) -> None:
        account, contacts, interactions = sample_case()
        invalid = make_briefing(account, contacts, interactions, "EVT-NOT-REAL")
        valid = make_briefing(account, contacts, interactions, interactions[0]["event_id"])
        client = FakeClient([fake_response(invalid, "resp-1"), fake_response(valid, "resp-2")])
        log_path = Path(__file__).parent / ".tmp_dataset" / "pipeline_log.jsonl"
        log_path.parent.mkdir(exist_ok=True)
        log_path.unlink(missing_ok=True)

        run = run_briefing(
            account,
            contacts,
            interactions,
            experiment="M2",
            client=client,
            log_path=log_path,
            max_attempts=2,
            sleep_fn=lambda _: None,
        )

        self.assertTrue(run.validation.passed)
        self.assertEqual(run.usage.attempts, 2)
        self.assertEqual(run.usage.input_tokens, 200)
        self.assertEqual(run.usage.output_tokens, 100)
        self.assertEqual(len(client.responses.calls), 2)
        log_row = json.loads(log_path.read_text(encoding="utf-8").strip())
        self.assertEqual(log_row["request_id"], "resp-2")
        self.assertNotIn(account["name"], log_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
