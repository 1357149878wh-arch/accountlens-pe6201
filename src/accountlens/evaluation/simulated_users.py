"""Reproducible synthetic pilot for the blinded user-study procedure.

This module does not create human-subject evidence. It uses transparent heuristics
to exercise the study design on validation accounts before recruiting people.
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from statistics import median
from typing import Any

from accountlens.io import load_dataset, read_json


SEED = 6201
PILOT_ACCOUNTS = ["ACC-014", "ACC-020", "ACC-040", "ACC-058"]
MEASURES = [
    "role_usefulness",
    "evidence_trust",
    "risk_relevance",
    "action_usefulness",
    "clarity",
    "confidence_calibration",
]
PERSONAS = [
    {
        "participant": "VP01",
        "role": "Key Account Manager",
        "experience": "8 years managing enterprise software accounts",
        "base_time_seconds": 145,
        "bias": {"role_usefulness": 0.2, "action_usefulness": 0.3},
    },
    {
        "participant": "VP02",
        "role": "Sales Director",
        "experience": "12 years reviewing strategic opportunities",
        "base_time_seconds": 125,
        "bias": {"role_usefulness": 0.3, "action_usefulness": 0.2},
    },
    {
        "participant": "VP03",
        "role": "Presales Engineer",
        "experience": "6 years in solution design and technical validation",
        "base_time_seconds": 155,
        "bias": {"evidence_trust": 0.3, "confidence_calibration": 0.2},
    },
    {
        "participant": "VP04",
        "role": "Customer Success Manager",
        "experience": "7 years managing adoption and service risks",
        "base_time_seconds": 150,
        "bias": {"risk_relevance": 0.35, "action_usefulness": 0.1},
    },
    {
        "participant": "VP05",
        "role": "Revenue Operations Analyst",
        "experience": "5 years in CRM governance and pipeline analysis",
        "base_time_seconds": 165,
        "bias": {"evidence_trust": 0.35, "clarity": 0.15},
    },
]


def _clamp_rating(value: float) -> float:
    return round(max(1.0, min(5.0, value)), 1)


def _jitter(seed: int, *parts: str, amplitude: float = 0.22) -> float:
    rng = random.Random(":".join([str(seed), *parts]))
    return rng.uniform(-amplitude, amplitude)


def _collect_briefing_evidence(briefing: dict[str, Any]) -> set[str]:
    evidence: set[str] = set()
    for prediction in briefing.get("decision_roles", []):
        evidence.update(prediction.get("evidence_ids", []))
    for activity in briefing.get("cross_team_activity", []):
        evidence.update(activity.get("event_ids", []))
    for risk in briefing.get("risks", []):
        evidence.update(risk.get("evidence_ids", []))
    for action in briefing.get("recommended_actions", []):
        evidence.update(action.get("evidence_ids", []))
    return evidence


def _system_features(
    account_id: str,
    system: str,
    predictions: list[dict[str, Any]],
    briefing: dict[str, Any] | None,
    truth_by_contact: dict[str, str],
    valid_event_ids: set[str],
    critical_event_ids: set[str],
) -> dict[str, float]:
    correct = sum(
        prediction["role"] == truth_by_contact[prediction["contact_id"]]
        for prediction in predictions
    )
    role_accuracy = correct / len(predictions)
    coverage = sum(not prediction.get("abstained", False) for prediction in predictions) / len(predictions)

    if briefing:
        evidence = _collect_briefing_evidence(briefing)
        risk_count = len(briefing.get("risks", []))
        action_count = len(briefing.get("recommended_actions", []))
    else:
        evidence = {
            event_id
            for prediction in predictions
            for event_id in prediction.get("evidence_ids", [])
        }
        risk_count = 0
        action_count = 0

    evidence_validity = len(evidence & valid_event_ids) / len(evidence) if evidence else 0.0
    critical_recall = (
        len(evidence & critical_event_ids) / len(critical_event_ids)
        if critical_event_ids
        else 1.0
    )
    abstention_present = any(prediction.get("abstained", False) for prediction in predictions)

    # B0 is intentionally a role-only baseline. The low risk/action values reflect
    # missing briefing functions, not fabricated model failures.
    risk_signal = min(1.0, 0.35 * risk_count + 0.65 * critical_recall) if system == "M2" else 0.1 * critical_recall
    action_signal = min(1.0, action_count / 2) if system == "M2" else 0.0
    clarity_signal = 0.86 if system == "B0" else 0.80

    return {
        "role_usefulness": 0.7 * role_accuracy + 0.3 * coverage,
        "evidence_trust": 0.75 * evidence_validity + 0.25 * min(1.0, len(evidence) / 12),
        "risk_relevance": risk_signal,
        "action_usefulness": action_signal,
        "clarity": clarity_signal,
        "confidence_calibration": 0.9 if abstention_present else 0.45,
        "role_accuracy": role_accuracy,
        "coverage": coverage,
        "critical_event_recall": critical_recall,
        "evidence_validity": evidence_validity,
    }


def run_simulation(
    data_dir: Path,
    results_dir: Path,
    seed: int = SEED,
) -> dict[str, Any]:
    dataset = load_dataset(data_dir)
    validation_ids = set(dataset["splits"]["validation"])
    if not set(PILOT_ACCOUNTS).issubset(validation_ids):
        raise ValueError("Synthetic pilot accounts must remain inside the validation split.")

    baseline = read_json(results_dir / "baseline_validation.json")
    m2 = read_json(results_dir / "m2_validation.json")
    contacts = {row["contact_id"]: row for row in dataset["contacts"]}
    truth_by_contact = {row["contact_id"]: row["role"] for row in dataset["role_truth"]}
    briefings = {row["account_id"]: row for row in m2["briefings"]}

    predictions_by_system: dict[str, dict[str, list[dict[str, Any]]]] = {"B0": {}, "M2": {}}
    for system, rows in (("B0", baseline["predictions"]), ("M2", m2["predictions"])):
        for prediction in rows:
            account_id = contacts[prediction["contact_id"]]["account_id"]
            predictions_by_system[system].setdefault(account_id, []).append(prediction)

    events_by_account = {
        account_id: {
            row["event_id"]
            for row in dataset["interactions"]
            if row["account_id"] == account_id
        }
        for account_id in PILOT_ACCOUNTS
    }
    critical_by_account = {
        account_id: {
            row["event_id"]
            for row in dataset["critical_truth"]
            if row["account_id"] == account_id
        }
        for account_id in PILOT_ACCOUNTS
    }

    records: list[dict[str, Any]] = []
    preferences: list[dict[str, str]] = []
    for persona in PERSONAS:
        for account_id in PILOT_ACCOUNTS:
            order_rng = random.Random(f"{seed}:{persona['participant']}:{account_id}:order")
            a_system = order_rng.choice(["B0", "M2"])
            mapping = {"A": a_system, "B": "M2" if a_system == "B0" else "B0"}
            pair_scores: dict[str, float] = {}

            for masked_label in ("A", "B"):
                system = mapping[masked_label]
                predictions = predictions_by_system[system][account_id]
                features = _system_features(
                    account_id=account_id,
                    system=system,
                    predictions=predictions,
                    briefing=briefings.get(account_id) if system == "M2" else None,
                    truth_by_contact=truth_by_contact,
                    valid_event_ids=events_by_account[account_id],
                    critical_event_ids=critical_by_account[account_id],
                )
                ratings = {
                    measure: _clamp_rating(
                        1
                        + 4 * features[measure]
                        + persona["bias"].get(measure, 0.0)
                        + _jitter(seed, persona["participant"], account_id, system, measure)
                    )
                    for measure in MEASURES
                }
                mean_rating = round(sum(ratings.values()) / len(ratings), 2)
                completeness = sum(features[measure] for measure in MEASURES) / len(MEASURES)
                time_seconds = round(
                    persona["base_time_seconds"]
                    * (1.28 - 0.42 * completeness)
                    + _jitter(seed, persona["participant"], account_id, system, "time", amplitude=9.0)
                )
                pair_scores[system] = mean_rating
                records.append(
                    {
                        "participant": persona["participant"],
                        "persona_role": persona["role"],
                        "account_id": account_id,
                        "masked_label": masked_label,
                        "system": system,
                        "time_seconds": time_seconds,
                        "ratings": ratings,
                        "mean_rating": mean_rating,
                        "objective_features": {key: round(value, 4) for key, value in features.items()},
                    }
                )

            difference = pair_scores["M2"] - pair_scores["B0"]
            preferred = "M2" if difference > 0.15 else "B0" if difference < -0.15 else "tie"
            preferences.append(
                {
                    "participant": persona["participant"],
                    "account_id": account_id,
                    "preferred_system": preferred,
                }
            )

    aggregate: dict[str, Any] = {}
    for system in ("B0", "M2"):
        system_rows = [row for row in records if row["system"] == system]
        aggregate[system] = {
            "observations": len(system_rows),
            "median_time_seconds": round(median(row["time_seconds"] for row in system_rows), 1),
            "median_mean_rating": round(median(row["mean_rating"] for row in system_rows), 2),
            "median_ratings": {
                measure: round(median(row["ratings"][measure] for row in system_rows), 1)
                for measure in MEASURES
            },
        }

    preference_counts = {
        system: sum(row["preferred_system"] == system for row in preferences)
        for system in ("B0", "M2", "tie")
    }
    return {
        "study_type": "synthetic_simulation_not_human_subject_research",
        "warning": "SIMULATED RESULTS - DO NOT REPORT AS REAL PARTICIPANT DATA",
        "seed": seed,
        "accounts": PILOT_ACCOUNTS,
        "personas": PERSONAS,
        "systems": {
            "B0": "deterministic role-inference baseline",
            "M2": "frozen evidence-grounded validation output",
        },
        "aggregate": aggregate,
        "preference_counts_across_account_pairs": preference_counts,
        "preferences": preferences,
        "records": records,
        "limitations": [
            "No real person viewed or scored a briefing.",
            "Likert ratings and preparation times are generated from disclosed heuristics.",
            "The simulator is not independent of the project design and cannot validate business value.",
            "Results are suitable only for piloting the study procedure and checking analysis code.",
        ],
    }


def render_markdown(payload: dict[str, Any]) -> str:
    aggregate = payload["aggregate"]
    lines = [
        "# Simulated blinded-evaluation pilot",
        "",
        "> **SIMULATED RESULTS - NOT HUMAN PARTICIPANT DATA.** This pilot validates the study procedure only and must not be presented as completed user research.",
        "",
        "## Purpose",
        "",
        "Five fictional evaluator personas reviewed four validation accounts under a reproducible A/B order. B0 is the deterministic role-only baseline; M2 uses the already-saved frozen validation briefings. No API call or test-set run was made.",
        "",
        "## Virtual evaluator panel",
        "",
        "| ID | Fictional role | Fictional experience |",
        "|---|---|---|",
    ]
    for persona in payload["personas"]:
        lines.append(f"| {persona['participant']} | {persona['role']} | {persona['experience']} |")

    lines.extend(
        [
            "",
            "## Aggregate simulated results",
            "",
            "| Measure | B0 | M2 |",
            "|---|---:|---:|",
            f"| Median preparation time (seconds) | {aggregate['B0']['median_time_seconds']} | {aggregate['M2']['median_time_seconds']} |",
            f"| Median mean rating (1-5) | {aggregate['B0']['median_mean_rating']} | {aggregate['M2']['median_mean_rating']} |",
        ]
    )
    labels = {
        "role_usefulness": "Role usefulness",
        "evidence_trust": "Evidence trust",
        "risk_relevance": "Risk relevance",
        "action_usefulness": "Action usefulness",
        "clarity": "Clarity",
        "confidence_calibration": "Confidence calibration",
    }
    for measure in MEASURES:
        lines.append(
            f"| {labels[measure]} (1-5) | {aggregate['B0']['median_ratings'][measure]} | {aggregate['M2']['median_ratings'][measure]} |"
        )

    preferences = payload["preference_counts_across_account_pairs"]
    lines.extend(
        [
            "",
            "Across 20 simulated participant-account pairs, preference counts were: "
            f"M2={preferences['M2']}, B0={preferences['B0']}, tie={preferences['tie']}.",
            "",
            "## Interpretation",
            "",
            "The synthetic panel is expected to favour M2 because M2 includes risk summaries and recommended actions while B0 is intentionally a role-only baseline. This is useful for checking whether the questionnaire detects the intended product difference, but it is not evidence that real users will agree, work faster, or make better decisions.",
            "",
            "## Method",
            "",
            "- Accounts: `ACC-014`, `ACC-020`, `ACC-040`, and `ACC-058`, all from the validation split.",
            "- Five fictional personas; four account pairs per persona; 40 masked briefing observations.",
            "- A/B order is deterministic but randomised from seed `6201`.",
            "- Role accuracy, coverage, evidence validity, and critical-event recall come from saved validation artifacts.",
            "- Likert scores and preparation times are transparent heuristic transformations with small seeded persona variation.",
            "- The test split, final metrics, frozen prompt, model, and threshold were not touched.",
            "",
            "## Limitations",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["limitations"])
    lines.extend(
        [
            "",
            "## Permitted claim",
            "",
            "The project completed a reproducible synthetic pilot of the blinded study procedure. The pilot identified no structural problem in the scoring or aggregation workflow. A real blinded participant study remains outstanding.",
            "",
            "## Prohibited claim",
            "",
            "Do not write that five users participated, that users preferred M2, or that preparation time improved. Those statements would misrepresent simulated observations as human research.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the synthetic blinded-study pilot on validation artifacts.")
    parser.add_argument("--data-dir", type=Path, default=Path("data/generated"))
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--json-output", type=Path, default=Path("results/simulated_user_evaluation.json"))
    parser.add_argument("--report-output", type=Path, default=Path("docs/simulated_user_evaluation.md"))
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()

    payload = run_simulation(args.data_dir, args.results_dir, args.seed)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.report_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.report_output.write_text(render_markdown(payload), encoding="utf-8")
    print(f"Saved synthetic results: {args.json_output}")
    print(f"Saved synthetic report: {args.report_output}")


if __name__ == "__main__":
    main()
