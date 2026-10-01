"""Deterministic account-intelligence layer built on validated role predictions."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from typing import Any, Iterable

from accountlens.schemas import (
    DecisionChainEdge,
    DecisionChainMap,
    DecisionChainNode,
    DecisionRole,
    DeterministicRiskSignal,
    RolePrediction,
    TeamActivityDigest,
)


DECISION_ROLES = (
    DecisionRole.CHAMPION,
    DecisionRole.TECHNICAL_EVALUATOR,
    DecisionRole.PROCUREMENT_LEGAL,
    DecisionRole.ECONOMIC_BUYER,
    DecisionRole.END_USER,
)

WORKFLOW_EDGES = (
    (DecisionRole.END_USER, DecisionRole.CHAMPION, "requirements_flow"),
    (DecisionRole.CHAMPION, DecisionRole.TECHNICAL_EVALUATOR, "mobilises_evaluation"),
    (DecisionRole.TECHNICAL_EVALUATOR, DecisionRole.PROCUREMENT_LEGAL, "technical_handoff"),
    (DecisionRole.PROCUREMENT_LEGAL, DecisionRole.ECONOMIC_BUYER, "commercial_clearance"),
    (DecisionRole.CHAMPION, DecisionRole.ECONOMIC_BUYER, "internal_advocacy"),
)


def filter_recent_interactions(
    interactions: Iterable[dict[str, Any]],
    reference_date: date,
    days: int = 30,
) -> list[dict[str, Any]]:
    """Return events inside an inclusive rolling window, newest first."""
    if days < 1:
        raise ValueError("days must be at least 1")
    cutoff = reference_date - timedelta(days=days)
    recent = [
        row
        for row in interactions
        if cutoff <= date.fromisoformat(str(row["date"])) <= reference_date
    ]
    return sorted(recent, key=lambda row: (str(row["date"]), str(row["event_id"])), reverse=True)


def aggregate_cross_team_activity(interactions: Iterable[dict[str, Any]]) -> list[TeamActivityDigest]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in interactions:
        grouped[str(row["internal_team"])].append(row)

    digests: list[TeamActivityDigest] = []
    for team, rows in grouped.items():
        rows = sorted(rows, key=lambda row: str(row["date"]), reverse=True)
        has_open_item = any(str(row.get("status", "")).lower() not in {"completed", "closed", "resolved"} for row in rows)
        importance = "high" if has_open_item else "medium" if len(rows) >= 3 else "low"
        channels = sorted({str(row["channel"]) for row in rows})
        digests.append(
            TeamActivityDigest(
                internal_team=team,
                event_count=len(rows),
                latest_date=str(rows[0]["date"]),
                channels=channels,
                event_ids=[str(row["event_id"]) for row in rows],
                importance=importance,
                summary=f"{team} recorded {len(rows)} event(s) across {', '.join(channels)}.",
            )
        )
    priority = {"high": 0, "medium": 1, "low": 2}
    digests.sort(key=lambda row: row.latest_date, reverse=True)
    digests.sort(key=lambda row: priority[row.importance])
    return digests


def detect_risk_signals(interactions: Iterable[dict[str, Any]]) -> list[DeterministicRiskSignal]:
    risks: list[DeterministicRiskSignal] = []
    for row in interactions:
        channel = str(row.get("channel", "")).lower()
        status = str(row.get("status", "")).lower()
        text = f"{row.get('subject', '')} {row.get('content', '')}".lower()
        event_id = str(row["event_id"])

        if channel == "ticket" and status not in {"completed", "closed", "resolved"}:
            risks.append(
                DeterministicRiskSignal(
                    category="unresolved_ticket",
                    severity="high",
                    description="An unresolved support ticket may affect customer confidence.",
                    event_ids=[event_id],
                )
            )
        if channel == "email" and (
            status in {"awaiting_response", "unanswered", "no_response"}
            or any(phrase in text for phrase in ("no response", "unanswered", "has not replied", "awaiting response"))
        ):
            risks.append(
                DeterministicRiskSignal(
                    category="unanswered_email",
                    severity="medium",
                    description="An email appears to require follow-up because no response is recorded.",
                    event_ids=[event_id],
                )
            )
        if any(phrase in text for phrase in ("competitor", "competing vendor", "alternative supplier")):
            risks.append(
                DeterministicRiskSignal(
                    category="competitor_signal",
                    severity="high",
                    description="The source record contains an explicit competitor-engagement signal.",
                    event_ids=[event_id],
                )
            )
    return risks


def build_decision_chain(
    account_id: str,
    contacts: Iterable[dict[str, Any]],
    predictions: Iterable[dict[str, Any] | RolePrediction],
    threshold: float = 0.65,
) -> DecisionChainMap:
    contacts_by_id = {str(row["contact_id"]): row for row in contacts}
    parsed = [row if isinstance(row, RolePrediction) else RolePrediction.model_validate(row) for row in predictions]
    nodes: list[DecisionChainNode] = []
    by_role: dict[DecisionRole, DecisionChainNode] = {}

    for prediction in parsed:
        contact = contacts_by_id.get(prediction.contact_id)
        if not contact:
            continue
        review_status = (
            "human_review"
            if prediction.abstained or prediction.confidence < threshold or prediction.role == DecisionRole.UNKNOWN
            else "candidate"
        )
        node = DecisionChainNode(
            contact_id=prediction.contact_id,
            name=str(contact["name"]),
            title=str(contact["title"]),
            role=prediction.role,
            confidence=prediction.confidence,
            evidence_ids=prediction.evidence_ids,
            review_status=review_status,
        )
        nodes.append(node)
        if prediction.role != DecisionRole.UNKNOWN and review_status == "candidate":
            by_role[prediction.role] = node

    edges: list[DecisionChainEdge] = []
    for source_role, target_role, relationship in WORKFLOW_EDGES:
        source = by_role.get(source_role)
        target = by_role.get(target_role)
        if not source or not target:
            continue
        evidence_ids = list(dict.fromkeys([*source.evidence_ids, *target.evidence_ids]))
        edges.append(
            DecisionChainEdge(
                source_contact_id=source.contact_id,
                target_contact_id=target.contact_id,
                relationship=relationship,
                confidence=round(min(source.confidence, target.confidence) * 0.85, 2),
                evidence_ids=evidence_ids,
                rationale=(
                    f"Workflow hypothesis connecting {source.role.value} to {target.role.value}; "
                    "confirm the relationship with the account team before acting."
                ),
            )
        )

    missing = [role for role in DECISION_ROLES if role not in by_role]
    return DecisionChainMap(
        account_id=account_id,
        nodes=nodes,
        edges=edges,
        missing_roles=missing,
        limitations=[
            "Edges describe a likely buying-workflow path, not a verified reporting line or personal power relationship.",
            "Every inferred node and edge requires human confirmation before account strategy is changed.",
        ],
    )


def decision_chain_graphviz(chain: DecisionChainMap) -> str:
    role_colours = {
        DecisionRole.CHAMPION: "#2563EB",
        DecisionRole.TECHNICAL_EVALUATOR: "#7C3AED",
        DecisionRole.PROCUREMENT_LEGAL: "#D97706",
        DecisionRole.ECONOMIC_BUYER: "#DC2626",
        DecisionRole.END_USER: "#059669",
        DecisionRole.UNKNOWN: "#64748B",
    }
    lines = [
        "digraph DecisionChain {",
        'rankdir="LR";',
        'graph [bgcolor="transparent", pad="0.2", nodesep="0.35", ranksep="0.6"];',
        'node [shape="box", style="rounded,filled", fontname="Arial", fontcolor="white", margin="0.15"];',
        'edge [fontname="Arial", fontsize="9", color="#64748B"];',
    ]
    visible_nodes = [
        node for node in chain.nodes if node.role != DecisionRole.UNKNOWN and node.review_status == "candidate"
    ]
    for node in visible_nodes:
        label = f"{node.role.value}\\n{node.name}\\n{node.confidence:.0%}".replace('"', "'")
        lines.append(f'"{node.contact_id}" [label="{label}", fillcolor="{role_colours[node.role]}"];')
    for edge in chain.edges:
        label = edge.relationship.replace("_", " ")
        lines.append(f'"{edge.source_contact_id}" -> "{edge.target_contact_id}" [label="{label}"];')
    lines.append("}")
    return "\n".join(lines)
