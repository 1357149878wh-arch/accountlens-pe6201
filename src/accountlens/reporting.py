"""Presentation exports for the Account Panorama Briefing."""

from __future__ import annotations

from io import BytesIO
from typing import Any

from accountlens.schemas import AccountBriefing, DecisionChainMap, DeterministicRiskSignal, TeamActivityDigest


def _clean(value: object, limit: int = 110) -> str:
    text = " ".join(str(value).replace("\n", " ").split())
    if len(text) > limit:
        text = text[: limit - 3].rstrip() + "..."
    return text.encode("latin-1", "replace").decode("latin-1")


def build_slack_summary(
    account: dict[str, Any],
    briefing: AccountBriefing,
    chain: DecisionChainMap,
    team_activity: list[TeamActivityDigest],
    deterministic_risks: list[DeterministicRiskSignal],
) -> str:
    roles = []
    names = {node.contact_id: node.name for node in chain.nodes}
    signatory_candidates = [node for node in chain.nodes if node.role.value == "economic_buyer"]
    likely_signatory = max(signatory_candidates, key=lambda node: node.confidence) if signatory_candidates else None
    for role in briefing.decision_roles:
        if role.abstained:
            continue
        roles.append(f"- *{role.role.value.replace('_', ' ').title()}*: {names.get(role.contact_id, role.contact_id)} ({role.confidence:.0%})")
    activity = [f"- *{item.internal_team}*: {item.event_count} event(s), latest {item.latest_date}" for item in team_activity[:5]]
    risks = [f"- *{item.severity.upper()}* {item.description} [{', '.join(item.event_ids)}]" for item in deterministic_risks]
    risks.extend(f"- *{item.severity.upper()}* {item.description} [{', '.join(item.evidence_ids)}]" for item in briefing.risks)
    actions = [f"{index}. {item.action}" for index, item in enumerate(briefing.recommended_actions[:2], 1)]
    return "\n".join(
        [
            f"*Account Panorama Briefing - {account['name']}*",
            f"Stage: {account['stage']} | ACV: USD {account['annual_value_usd']:,}",
            (
                f"Likely commercial signatory: {likely_signatory.name} ({likely_signatory.confidence:.0%}) - verify before use"
                if likely_signatory
                else "Likely commercial signatory: not identified - human follow-up required"
            ),
            "",
            "*Decision roles*",
            *(roles or ["- No supported role predictions"]),
            "",
            "*Cross-team activity (last 30 days)*",
            *(activity or ["- No recent activity"]),
            "",
            "*Risks requiring human confirmation*",
            *(risks or ["- No explicit risk signal detected"]),
            "",
            "*Recommended next actions*",
            *(actions or ["1. Review the evidence with the account team."]),
            "",
            "_AI-assisted briefing. Verify evidence and relationships before taking action._",
        ]
    )


def build_briefing_pdf(
    account: dict[str, Any],
    briefing: AccountBriefing,
    chain: DecisionChainMap,
    team_activity: list[TeamActivityDigest],
    deterministic_risks: list[DeterministicRiskSignal],
) -> bytes:
    """Generate a compact, single-page A4 briefing."""
    try:
        from reportlab.lib.colors import HexColor
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except ImportError as exc:
        raise RuntimeError("PDF export requires reportlab. Install the project dependencies again.") from exc

    buffer = BytesIO()
    page_width, page_height = A4
    pdf = canvas.Canvas(buffer, pagesize=A4)
    navy = HexColor("#0F172A")
    blue = HexColor("#2563EB")
    slate = HexColor("#475569")
    light = HexColor("#E2E8F0")
    red = HexColor("#B91C1C")

    pdf.setFillColor(navy)
    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawString(34, page_height - 38, "Enterprise Account Decision-Chain Mapping")
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(34, page_height - 54, "& Cross-Team Intelligence Aggregation Assistant")
    pdf.setFillColor(slate)
    pdf.setFont("Helvetica", 8)
    pdf.drawRightString(page_width - 34, page_height - 40, "ACCOUNT PANORAMA BRIEFING")
    pdf.line(34, page_height - 63, page_width - 34, page_height - 63)

    pdf.setFillColor(navy)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(34, page_height - 82, _clean(account["name"], 60))
    pdf.setFont("Helvetica", 8)
    pdf.setFillColor(slate)
    pdf.drawString(34, page_height - 95, f"Industry: {_clean(account['industry'], 28)}")
    pdf.drawString(215, page_height - 95, f"Stage: {_clean(account['stage'], 24)}")
    pdf.drawString(390, page_height - 95, f"ACV: USD {account['annual_value_usd']:,}")

    left_x, right_x = 34, 315
    top_y = page_height - 122
    column_width = 246

    def heading(x: float, y: float, text: str) -> float:
        pdf.setFillColor(blue)
        pdf.setFont("Helvetica-Bold", 9)
        pdf.drawString(x, y, text.upper())
        pdf.setStrokeColor(light)
        pdf.line(x, y - 4, x + column_width, y - 4)
        return y - 17

    def line(x: float, y: float, text: str, colour=navy, font="Helvetica", size: float = 7.2) -> float:
        pdf.setFillColor(colour)
        pdf.setFont(font, size)
        pdf.drawString(x, y, _clean(text, 78))
        return y - 11

    y = heading(left_x, top_y, "Decision-chain candidates")
    node_by_role = {node.role.value: node for node in chain.nodes if node.role.value != "unknown"}
    for role in ("end_user", "champion", "technical_evaluator", "procurement_legal", "economic_buyer"):
        node = node_by_role.get(role)
        role_label = "Likely commercial signatory" if role == "economic_buyer" else role.replace("_", " ").title()
        if node:
            y = line(left_x, y, f"{role_label}: {node.name} ({node.confidence:.0%})", font="Helvetica-Bold")
        else:
            y = line(left_x, y, f"{role_label}: MISSING - human follow-up", colour=red)

    y -= 5
    y = heading(left_x, y, "Likely workflow")
    for edge in chain.edges[:5]:
        source = next(node for node in chain.nodes if node.contact_id == edge.source_contact_id)
        target = next(node for node in chain.nodes if node.contact_id == edge.target_contact_id)
        y = line(left_x, y, f"{source.name} -> {target.name}: {edge.relationship.replace('_', ' ')}")

    y -= 5
    y = heading(left_x, y, "Cross-team activity - 30 days")
    for item in team_activity[:6]:
        y = line(left_x, y, f"[{item.importance.upper()}] {item.internal_team}: {item.event_count} event(s), latest {item.latest_date}")

    y = heading(right_x, top_y, "Risk alerts")
    risk_rows = [
        f"[{item.severity.upper()}] {item.description} ({', '.join(item.event_ids)})"
        for item in deterministic_risks
    ]
    risk_rows.extend(
        f"[{item.severity.upper()}] {item.description} ({', '.join(item.evidence_ids)})"
        for item in briefing.risks
    )
    if not risk_rows:
        risk_rows = ["No explicit risk signal detected in the 30-day window."]
    for item in risk_rows[:5]:
        y = line(right_x, y, item, colour=red if "[HIGH]" in item else navy)

    y -= 5
    y = heading(right_x, y, "Recommended next actions")
    actions = briefing.recommended_actions[:2]
    if actions:
        for index, item in enumerate(actions, 1):
            y = line(right_x, y, f"{index}. {item.action}", font="Helvetica-Bold")
            y = line(right_x + 8, y, f"Why: {item.rationale}", colour=slate, size=6.8)
    else:
        y = line(right_x, y, "1. Review the evidence with the account team.")

    y -= 5
    y = heading(right_x, y, "Evidence and limitations")
    evidence_count = len({event_id for node in chain.nodes for event_id in node.evidence_ids})
    y = line(right_x, y, f"Decision-role evidence references: {evidence_count}")
    y = line(right_x, y, "Workflow edges are hypotheses, not verified reporting lines.")
    y = line(right_x, y, "Use only for meeting preparation; do not automate outreach.")
    for limitation in briefing.limitations[:2]:
        y = line(right_x, y, f"- {limitation}", colour=slate, size=6.8)

    pdf.setFillColor(light)
    pdf.rect(34, 28, page_width - 68, 28, fill=1, stroke=0)
    pdf.setFillColor(navy)
    pdf.setFont("Helvetica-Bold", 7.5)
    pdf.drawString(42, 44, "HUMAN CONFIRMATION REQUIRED")
    pdf.setFont("Helvetica", 7)
    pdf.drawString(42, 34, "AI-assisted output from synthetic data. Verify every role, relationship, risk and action against source records.")
    pdf.setFillColor(slate)
    pdf.drawRightString(page_width - 42, 34, "AccountLens")

    pdf.showPage()
    pdf.save()
    return buffer.getvalue()
