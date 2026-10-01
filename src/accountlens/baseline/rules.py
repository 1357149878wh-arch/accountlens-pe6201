"""Deterministic decision-role inference baseline."""

from __future__ import annotations

from collections import defaultdict


ROLE_KEYWORDS = {
    "champion": ["champion", "coordinate", "adoption", "promoted", "organise", "priorities", "alignment"],
    "economic_buyer": ["chief financial", "finance director", "business unit vp", "budget", "roi", "approve", "sign-off", "expenditure"],
    "technical_evaluator": ["architect", "technology", "security", "technical", "integration", "api", "scalability", "identity"],
    "procurement_legal": ["procurement", "legal", "vendor", "contract", "liability", "terms", "compliance", "commercial manager"],
    "end_user": ["analyst", "supervisor", "service manager", "workflow", "usability", "daily", "user", "training"],
}


def infer_contact_role(contact: dict, interactions: list[dict]) -> dict:
    scores: dict[str, float] = defaultdict(float)
    evidence: dict[str, list[str]] = defaultdict(list)
    title_text = f"{contact['title']} {contact['department']}".lower()

    for role, keywords in ROLE_KEYWORDS.items():
        for keyword in keywords:
            if keyword in title_text:
                scores[role] += 3.0

    for event in interactions:
        if contact["contact_id"] not in event["participant_ids"]:
            continue
        event_text = f"{event['subject']} {event['content']}".lower()
        for role, keywords in ROLE_KEYWORDS.items():
            matches = sum(keyword in event_text for keyword in keywords)
            if matches:
                scores[role] += min(3.0, float(matches))
                evidence[role].append(event["event_id"])

    if not scores:
        return {
            "contact_id": contact["contact_id"],
            "role": "unknown",
            "confidence": 0.45,
            "evidence_ids": [],
            "reason": "No role-specific title or behavioural evidence was found.",
            "abstained": True,
            "source": "rules",
        }

    ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    best_role, best_score = ranked[0]
    second_score = ranked[1][1] if len(ranked) > 1 else 0.0
    margin = best_score - second_score
    abstained = best_score < 3.0 or margin < 1.0
    role = "unknown" if abstained else best_role
    confidence = round(min(0.95, 0.45 + best_score / 20.0 + margin / 30.0), 2)
    selected_evidence = list(dict.fromkeys(evidence.get(best_role, [])))[:4]
    return {
        "contact_id": contact["contact_id"],
        "role": role,
        "confidence": confidence,
        "evidence_ids": selected_evidence,
        "reason": f"Rules score={best_score:.1f}, margin={margin:.1f}, based on title and interaction keywords.",
        "abstained": abstained,
        "source": "rules",
    }


def infer_roles(contacts: list[dict], interactions: list[dict]) -> list[dict]:
    events_by_account: dict[str, list[dict]] = defaultdict(list)
    for event in interactions:
        events_by_account[event["account_id"]].append(event)
    return [infer_contact_role(contact, events_by_account[contact["account_id"]]) for contact in contacts]

