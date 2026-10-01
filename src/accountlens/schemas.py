"""Pydantic schemas shared by generation, evaluation, and the AI pipeline."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class DecisionRole(str, Enum):
    CHAMPION = "champion"
    ECONOMIC_BUYER = "economic_buyer"
    TECHNICAL_EVALUATOR = "technical_evaluator"
    PROCUREMENT_LEGAL = "procurement_legal"
    END_USER = "end_user"
    UNKNOWN = "unknown"


class Account(StrictModel):
    account_id: str
    name: str
    industry: str
    stage: str
    annual_value_usd: int = Field(ge=0)
    true_signatory_contact_id: str


class Contact(StrictModel):
    contact_id: str
    account_id: str
    name: str
    title: str
    department: str
    seniority: str


class Interaction(StrictModel):
    event_id: str
    account_id: str
    date: str
    channel: str
    internal_team: str
    participant_ids: list[str]
    subject: str
    content: str
    status: str
    thread_id: str | None = None
    sender_id: str | None = None
    to_ids: list[str] = Field(default_factory=list)
    cc_ids: list[str] = Field(default_factory=list)
    meeting_id: str | None = None
    attendee_ids: list[str] = Field(default_factory=list)
    internal_attendees: list[str] = Field(default_factory=list)
    ticket_id: str | None = None
    priority: str | None = None


class RoleGroundTruth(StrictModel):
    contact_id: str
    account_id: str
    role: DecisionRole


class CriticalEventGroundTruth(StrictModel):
    event_id: str
    account_id: str
    category: str
    importance: str


class RolePrediction(StrictModel):
    contact_id: str
    role: DecisionRole
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_ids: list[str]
    reason: str
    abstained: bool = False
    source: str = "rules"


class ActivitySummary(StrictModel):
    event_ids: list[str]
    summary: str
    importance: str


class RiskAlert(StrictModel):
    category: str
    severity: str
    description: str
    evidence_ids: list[str]


class RecommendedAction(StrictModel):
    action: str
    rationale: str
    evidence_ids: list[str]


class DecisionChainNode(StrictModel):
    contact_id: str
    name: str
    title: str
    role: DecisionRole
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_ids: list[str]
    review_status: str


class DecisionChainEdge(StrictModel):
    source_contact_id: str
    target_contact_id: str
    relationship: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_ids: list[str]
    rationale: str
    inference_type: str = "workflow_hypothesis"
    human_review_required: bool = True


class DecisionChainMap(StrictModel):
    account_id: str
    nodes: list[DecisionChainNode]
    edges: list[DecisionChainEdge]
    missing_roles: list[DecisionRole]
    limitations: list[str]


class TeamActivityDigest(StrictModel):
    internal_team: str
    event_count: int = Field(ge=1)
    latest_date: str
    channels: list[str]
    event_ids: list[str]
    importance: str
    summary: str


class DeterministicRiskSignal(StrictModel):
    category: str
    severity: str
    description: str
    event_ids: list[str]
    requires_human_confirmation: bool = True


class AccountBriefing(StrictModel):
    account_id: str
    decision_roles: list[RolePrediction]
    cross_team_activity: list[ActivitySummary]
    risks: list[RiskAlert]
    recommended_actions: list[RecommendedAction]
    limitations: list[str]


class EvidenceValidationReport(StrictModel):
    passed: bool
    errors: list[str]
    warnings: list[str]
    total_reference_count: int = Field(ge=0)
    valid_reference_count: int = Field(ge=0)
    evidence_precision: float = Field(ge=0.0, le=1.0)


class UsageSummary(StrictModel):
    request_id: str | None = None
    experiment: str
    model: str
    prompt_version: str
    status: str
    attempts: int = Field(ge=1)
    latency_seconds: float = Field(ge=0.0)
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    total_tokens: int = Field(ge=0)
    estimated_cost_usd: float = Field(ge=0.0)
    validation_passed: bool
    error_type: str | None = None


class BriefingRun(StrictModel):
    briefing: AccountBriefing
    validation: EvidenceValidationReport
    usage: UsageSummary
