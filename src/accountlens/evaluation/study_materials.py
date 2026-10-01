"""Build masked A/B participant packets from saved validation artifacts."""

from __future__ import annotations

import argparse
import random
from datetime import date
from pathlib import Path
from typing import Any

from accountlens.intelligence import (
    aggregate_cross_team_activity,
    build_decision_chain,
    detect_risk_signals,
    filter_recent_interactions,
)
from accountlens.io import load_dataset, read_json


SEED = 6201
PARTICIPANTS = ["P01", "P02", "P03", "P04", "P05"]
STUDY_ACCOUNTS = ["ACC-014", "ACC-020", "ACC-040", "ACC-058"]


def _group_predictions(
    predictions: list[dict[str, Any]], contacts_by_id: dict[str, dict[str, Any]]
) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for prediction in predictions:
        account_id = contacts_by_id[prediction["contact_id"]]["account_id"]
        grouped.setdefault(account_id, []).append(prediction)
    return grouped


def _evidence_text(ids: list[str]) -> str:
    return ", ".join(ids) if ids else "No supporting event - human verification required"


def _baseline_actions(chain: Any, risks: list[Any]) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    if risks:
        first = risks[0]
        actions.append(
            {
                "action": "Review the highest-priority flagged record with the account team before the meeting.",
                "rationale": "The deterministic alert indicates an open issue that may affect the customer conversation.",
                "evidence_ids": first.event_ids,
            }
        )
    if chain.missing_roles:
        labels = ", ".join(role.value.replace("_", " ") for role in chain.missing_roles)
        actions.append(
            {
                "action": f"Confirm the missing decision roles with the account team: {labels}.",
                "rationale": "The available records do not support a confident candidate for every required role.",
                "evidence_ids": [],
            }
        )
    if not actions:
        actions.append(
            {
                "action": "Verify the cited role evidence with the account team before changing the account plan.",
                "rationale": "Rule-based candidates remain decision-support hypotheses.",
                "evidence_ids": [],
            }
        )
    return actions[:2]


def _build_variant(
    system: str,
    account: dict[str, Any],
    contacts: list[dict[str, Any]],
    recent_interactions: list[dict[str, Any]],
    predictions: list[dict[str, Any]],
    m2_briefing: dict[str, Any],
) -> dict[str, Any]:
    chain = build_decision_chain(account["account_id"], contacts, predictions, threshold=0.65)
    deterministic_activity = aggregate_cross_team_activity(recent_interactions)
    deterministic_risks = detect_risk_signals(recent_interactions)

    if system == "B0":
        activity = [
            {
                "summary": item.summary,
                "importance": item.importance,
                "event_ids": item.event_ids,
            }
            for item in deterministic_activity[:5]
        ]
        risks = [
            {
                "severity": item.severity,
                "description": item.description,
                "evidence_ids": item.event_ids,
            }
            for item in deterministic_risks
        ]
        actions = _baseline_actions(chain, deterministic_risks)
    else:
        activity = m2_briefing["cross_team_activity"][:5]
        risks = [
            {
                "severity": item.severity,
                "description": item.description,
                "evidence_ids": item.event_ids,
            }
            for item in deterministic_risks
        ]
        risks.extend(m2_briefing["risks"])
        actions = m2_briefing["recommended_actions"][:2]

    contact_by_id = {row["contact_id"]: row for row in contacts}
    roles = []
    for prediction in predictions:
        contact = contact_by_id[prediction["contact_id"]]
        roles.append(
            {
                "name": contact["name"],
                "title": contact["title"],
                "role": prediction["role"],
                "confidence": prediction["confidence"],
                "evidence_ids": prediction["evidence_ids"],
                "review": prediction.get("abstained", False) or prediction["role"] == "unknown",
            }
        )

    return {
        "account": account,
        "roles": roles,
        "activity": activity,
        "risks": risks[:5],
        "actions": actions,
        "evidence_register": recent_interactions,
        "limitations": [
            "Decision roles and workflow relationships are hypotheses requiring human confirmation.",
            "Only the fixed 30-day synthetic record window is represented.",
        ],
    }


def _render_briefing(label: str, variant: dict[str, Any]) -> str:
    account = variant["account"]
    lines = [
        f"### Briefing {label}",
        "",
        f"**Account:** {account['name']}  ",
        f"**Industry:** {account['industry']}  ",
        f"**Stage:** {account['stage']}  ",
        f"**Annual value:** USD {account['annual_value_usd']:,}",
        "",
        "#### Decision roles",
        "",
        "| Contact | Title | Candidate role | Confidence | Evidence | Review status |",
        "|---|---|---|---:|---|---|",
    ]
    for role in variant["roles"]:
        review = "Human review required" if role["review"] else "Candidate"
        lines.append(
            f"| {role['name']} | {role['title']} | {role['role'].replace('_', ' ')} | "
            f"{role['confidence']:.0%} | {_evidence_text(role['evidence_ids'])} | {review} |"
        )

    lines.extend(["", "#### Cross-team activity - fixed 30-day window", ""])
    if variant["activity"]:
        for index, item in enumerate(variant["activity"], 1):
            lines.append(
                f"{index}. **{str(item['importance']).upper()}** - {item['summary']} "
                f"Evidence: {_evidence_text(item['event_ids'])}."
            )
    else:
        lines.append("No recent activity identified.")

    lines.extend(["", "#### Risks requiring confirmation", ""])
    if variant["risks"]:
        for index, item in enumerate(variant["risks"], 1):
            lines.append(
                f"{index}. **{str(item['severity']).upper()}** - {item['description']} "
                f"Evidence: {_evidence_text(item['evidence_ids'])}."
            )
    else:
        lines.append("No explicit risk signal identified in the available 30-day records.")

    lines.extend(["", "#### Recommended next actions", ""])
    for index, action in enumerate(variant["actions"], 1):
        lines.append(
            f"{index}. **{action['action']}**  \n"
            f"   Rationale: {action['rationale']}  \n"
            f"   Evidence: {_evidence_text(action['evidence_ids'])}."
        )

    lines.extend(["", "#### Limitations", ""])
    lines.extend(f"- {item}" for item in variant["limitations"])
    lines.append("")
    return "\n".join(lines)


def _render_evidence_register(interactions: list[dict[str, Any]]) -> str:
    lines = [
        "#### Shared evidence register",
        "",
        "The same evidence register applies to Briefings A and B.",
        "",
        "| Event ID | Date | Channel | Internal team | Subject | Status |",
        "|---|---|---|---|---|---|",
    ]
    for row in interactions:
        subject = str(row["subject"]).replace("|", "/")
        lines.append(
            f"| {row['event_id']} | {row['date']} | {row['channel']} | "
            f"{row['internal_team']} | {subject} | {row['status']} |"
        )
    lines.append("")
    return "\n".join(lines)


def build_materials(data_dir: Path, results_dir: Path, output_dir: Path, seed: int = SEED) -> list[Path]:
    dataset = load_dataset(data_dir)
    if not set(STUDY_ACCOUNTS).issubset(set(dataset["splits"]["validation"])):
        raise ValueError("Study materials may only use the validation split.")

    baseline = read_json(results_dir / "baseline_validation.json")
    m2 = read_json(results_dir / "m2_validation.json")
    contacts_by_id = {row["contact_id"]: row for row in dataset["contacts"]}
    accounts_by_id = {row["account_id"]: row for row in dataset["accounts"]}
    baseline_predictions = _group_predictions(baseline["predictions"], contacts_by_id)
    m2_predictions = _group_predictions(m2["predictions"], contacts_by_id)
    m2_briefings = {row["account_id"]: row for row in m2["briefings"]}
    reference_date = date.fromisoformat(read_json(data_dir / "manifest.json")["reference_date"])

    variants: dict[str, dict[str, dict[str, Any]]] = {}
    for account_id in STUDY_ACCOUNTS:
        account = accounts_by_id[account_id]
        contacts = [row for row in dataset["contacts"] if row["account_id"] == account_id]
        interactions = [row for row in dataset["interactions"] if row["account_id"] == account_id]
        recent = filter_recent_interactions(interactions, reference_date, days=30)
        variants[account_id] = {
            "B0": _build_variant(
                "B0", account, contacts, recent, baseline_predictions[account_id], m2_briefings[account_id]
            ),
            "M2": _build_variant(
                "M2", account, contacts, recent, m2_predictions[account_id], m2_briefings[account_id]
            ),
        }

    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    key_rows: list[tuple[str, str, str, str, str]] = []
    for participant in PARTICIPANTS:
        packet = [
            f"# Blinded AccountLens study packet - {participant}",
            "",
            "> Participant material. Do not distribute the facilitator key. All organisations and people are fictional.",
            "",
            "For each account, review the first briefing, record its time and scores, then review the second. Do not compare with another participant until the session is complete.",
            "",
        ]
        for account_id in STUDY_ACCOUNTS:
            rng = random.Random(f"{seed}:{participant}:{account_id}")
            a_system = rng.choice(["B0", "M2"])
            mapping = {"A": a_system, "B": "M2" if a_system == "B0" else "B0"}
            first = rng.choice(["A", "B"])
            second = "B" if first == "A" else "A"
            key_rows.append((participant, account_id, mapping["A"], mapping["B"], first))
            evidence = variants[account_id]["B0"]["evidence_register"]
            packet.extend(
                [
                    "---",
                    "",
                    f"## Account {account_id}",
                    "",
                    f"**Review order:** Briefing {first}, then Briefing {second}.",
                    "",
                    _render_briefing(first, variants[account_id][mapping[first]]),
                    _render_evidence_register(evidence),
                    "#### Record scores before continuing",
                    "",
                    f"- Briefing {first} preparation time: ______ seconds",
                    f"- Briefing {first} scores: role ___ / evidence ___ / risk ___ / action ___ / clarity ___ / uncertainty ___",
                    "",
                    _render_briefing(second, variants[account_id][mapping[second]]),
                    "#### Record paired assessment",
                    "",
                    f"- Briefing {second} preparation time: ______ seconds",
                    f"- Briefing {second} scores: role ___ / evidence ___ / risk ___ / action ___ / clarity ___ / uncertainty ___",
                    "- Preferred briefing: A / B / tie",
                    "- Reason and observed problems: ________________________________________________",
                    "",
                ]
            )
        packet_path = output_dir / f"{participant}_participant_packet.md"
        packet_path.write_text("\n".join(packet), encoding="utf-8")
        written.append(packet_path)

    key_lines = [
        "# Facilitator key - keep private until all scoring is complete",
        "",
        "> Do not send this file to participants. B0 is the deterministic baseline; M2 is the frozen evidence-grounded validation output.",
        "",
        "| Participant | Account | Briefing A | Briefing B | First shown |",
        "|---|---|---|---|---|",
    ]
    key_lines.extend(f"| {p} | {a} | {sa} | {sb} | {first} |" for p, a, sa, sb, first in key_rows)
    key_lines.extend(
        [
            "",
            "## Pre-registered pilot targets",
            "",
            "- M2 median mean rating at least 0.5 points above B0.",
            "- M2 median preparation time at least 15% lower than B0.",
            "- At least 60% of paired preferences favour M2.",
            "",
            "These targets are internal study decisions, not instructor-mandated thresholds. Do not alter them after viewing participant results.",
            "",
        ]
    )
    key_path = output_dir / "facilitator_key.md"
    key_path.write_text("\n".join(key_lines), encoding="utf-8")
    written.append(key_path)

    recording_lines = [
        "# Facilitator recording sheet",
        "",
        "> Enter only anonymous participant codes. Keep the A/B mapping hidden until every row is complete.",
        "",
        "## Briefing scores",
        "",
        "Use 1-5 for each rating and seconds for preparation time.",
        "",
        "| Participant | Account | Briefing | Time (s) | Role | Evidence | Risk | Action | Clarity | Uncertainty |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for participant in PARTICIPANTS:
        for account_id in STUDY_ACCOUNTS:
            for label in ("A", "B"):
                recording_lines.append(
                    f"| {participant} | {account_id} | {label} |  |  |  |  |  |  |  |"
                )
    recording_lines.extend(
        [
            "",
            "## Paired preference and observations",
            "",
            "| Participant | Account | Preferred (A/B/tie) | Reason | Error, unsupported claim or confusing abstention |",
            "|---|---|---|---|---|",
        ]
    )
    for participant in PARTICIPANTS:
        for account_id in STUDY_ACCOUNTS:
            recording_lines.append(f"| {participant} | {account_id} |  |  |  |")
    recording_lines.extend(
        [
            "",
            "Do not replace blank fields with estimated or simulated values. If a session is incomplete, mark the affected cells `missing`.",
            "",
        ]
    )
    recording_path = output_dir / "facilitator_recording_sheet.md"
    recording_path.write_text("\n".join(recording_lines), encoding="utf-8")
    written.append(recording_path)

    readme = """# Blinded study materials

These files were built from validation artifacts only. No API call or frozen test-set run is required.

- Send each participant only their matching `Pxx_participant_packet.md` file.
- Keep `facilitator_key.md` private until all scoring is complete.
- Enter observed times and ratings in `facilitator_recording_sheet.md`; never fill missing observations with simulated values.
- Do not tell participants which briefing is B0 or M2.
- Record only anonymous participant codes; do not collect employer or customer data.
- These packets use the same headings, account metadata, evidence register, rating scale and limitations for both systems.
- B0 contains deterministic activity/risk logic and rule-based roles; M2 contains the saved evidence-grounded validation briefing plus the same deterministic risk layer.
- Real participant results must be reported separately from the synthetic evaluator pilot.
"""
    readme_path = output_dir / "README.md"
    readme_path.write_text(readme, encoding="utf-8")
    written.append(readme_path)
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description="Create masked A/B user-study packets from validation artifacts.")
    parser.add_argument("--data-dir", type=Path, default=Path("data/generated"))
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--output-dir", type=Path, default=Path("docs/user_study_materials"))
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()
    written = build_materials(args.data_dir, args.results_dir, args.output_dir, args.seed)
    for path in written:
        print(f"Saved: {path}")


if __name__ == "__main__":
    main()
