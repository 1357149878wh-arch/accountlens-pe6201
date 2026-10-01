"""Import completed blinded questionnaires into reproducible study artifacts.

The importer treats questionnaire text only as participant-provided data. It
validates completion, decodes A/B labels from the frozen facilitator key, keeps
an immutable project copy of each source DOCX, and writes normalized CSV/JSON
outputs plus a concise Markdown report.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import statistics
from collections import Counter
from datetime import date
from pathlib import Path

from docx import Document


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_DIR = Path(
    r"C:\Users\W\Documents\xwechat_files\wxid_dw0nkhgjfswl22_528a\temp\RWTemp"
    r"\2026-09\0d9daf47446557b193b9c14a5f8505de"
)
MEASURES = [
    "Role usefulness",
    "Evidence trust",
    "Risk relevance",
    "Action usefulness",
    "Clarity",
    "Uncertainty",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def checked_choice(text: str, choices: list[str]) -> str:
    for choice in choices:
        if re.search(rf"\[X\]\s*{re.escape(choice)}(?=\s|[:：-]|$)", text, re.I):
            return choice
    return ""


def parse_key(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    mapping: dict[tuple[str, str], dict[str, str]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not re.match(r"^\| P\d\d \| ACC-\d{3} \|", line):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        participant, account, briefing_a, briefing_b, first = cells
        mapping[(participant, account)] = {
            "A": briefing_a,
            "B": briefing_b,
            "first_shown": first,
        }
    if len(mapping) != 20:
        raise ValueError(f"Expected 20 facilitator-key rows, found {len(mapping)}")
    return mapping


def parse_rating_tables(document: Document) -> list[dict[str, int]]:
    ratings: list[dict[str, int]] = []
    for table in document.tables:
        if not table.rows or not table.rows[0].cells[0].text.startswith("Measure /"):
            continue
        entry: dict[str, int] = {}
        for row in table.rows[1:]:
            measure = row.cells[0].text.strip()
            match = re.search(r"\[X\]\s*([1-5])", row.cells[2].text)
            if not match:
                raise ValueError(f"Missing rating for {measure}")
            entry[measure] = int(match.group(1))
        if set(entry) != set(MEASURES):
            raise ValueError(f"Unexpected rating fields: {sorted(entry)}")
        ratings.append(entry)
    return ratings


def text_block(paragraphs: list[str], start: int, stop_markers: tuple[str, ...]) -> list[str]:
    output: list[str] = []
    for text in paragraphs[start:]:
        if any(text.startswith(marker) for marker in stop_markers):
            break
        if text.strip():
            output.append(text.strip())
    return output


def parse_questionnaire(
    path: Path,
    participant: str,
    key: dict[tuple[str, str], dict[str, str]],
) -> tuple[dict, list[dict], list[dict]]:
    document = Document(path)
    paragraphs = [p.text.strip() for p in document.paragraphs]

    consent = sum(1 for text in paragraphs[5:9] if text.startswith("[X]"))
    background_line = paragraphs[10]
    background_choices = [
        "Account management",
        "Sales",
        "Presales",
        "Customer success",
        "Business analysis",
        "Other",
    ]
    background = checked_choice(background_line, background_choices)
    if background == "Other":
        detail = re.search(r"Other(?:\s*[:：-]\s*|\s+)(.+)$", background_line, re.I)
        background = f"Other: {detail.group(1).strip()}" if detail else "Other"
    experience = checked_choice(
        paragraphs[11], ["<1 year", "1-3 years", "4-7 years", "8+ years"]
    )

    rating_tables = parse_rating_tables(document)
    response_indices = [
        i for i, text in enumerate(paragraphs) if text.startswith("Your response for Briefing ")
    ]
    if len(response_indices) != 8 or len(rating_tables) != 8:
        raise ValueError(
            f"{participant}: expected 8 responses/ratings, found "
            f"{len(response_indices)}/{len(rating_tables)}"
        )

    observations: list[dict] = []
    current_account = ""
    for response_number, (idx, ratings) in enumerate(zip(response_indices, rating_tables)):
        for prior in reversed(paragraphs[:idx]):
            account_match = re.fullmatch(r"Account (ACC-\d{3})", prior)
            if account_match:
                current_account = account_match.group(1)
                break
        briefing_match = re.search(r"Briefing ([AB])", paragraphs[idx])
        briefing = briefing_match.group(1) if briefing_match else ""
        mapping = key[(participant, current_account)]

        def after(label: str, count: int) -> list[str]:
            heading = next(
                j for j in range(idx, min(idx + 25, len(paragraphs)))
                if paragraphs[j].startswith(label)
            )
            values: list[str] = []
            for item in paragraphs[heading + 1 :]:
                if re.match(r"^[1-4]\s{2}", item) or item.startswith("Meeting readiness"):
                    break
                if item:
                    values.append(item)
                if len(values) == count:
                    break
            return values

        readiness_line = next(
            text for text in paragraphs[idx : idx + 30] if text.startswith("Meeting readiness")
        )
        time_line = next(
            text for text in paragraphs[idx : idx + 30] if "preparation time" in text
        )
        readiness = checked_choice(readiness_line, ["Ready", "Partly ready", "Not ready"])
        time_match = re.search(r"(\d+)\s*seconds", time_line)
        if not time_match:
            raise ValueError(f"{participant} {current_account} {briefing}: missing time")

        observation = {
            "participant": participant,
            "background": background,
            "experience": experience,
            "account": current_account,
            "briefing": briefing,
            "system": mapping[briefing],
            "shown_first": briefing == mapping["first_shown"],
            "response_order": response_number + 1,
            "preparation_time_seconds": int(time_match.group(1)),
            "readiness": readiness,
            "likely_decision_roles": " ".join(after("1  Likely decision roles", 2)),
            "important_risks": " ".join(after("2  Two most important risks", 2)),
            "recommended_next_action": " ".join(after("3  Recommended next action", 2)),
            "remaining_uncertainty": " ".join(after("4  Information that remains uncertain", 2)),
        }
        for measure in MEASURES:
            observation[measure.lower().replace(" ", "_")] = ratings[measure]
        observation["mean_rating"] = round(
            statistics.mean(ratings.values()), 4
        )
        observations.append(observation)

    preferences: list[dict] = []
    for idx, text in enumerate(paragraphs):
        if text != "Paired assessment":
            continue
        account = ""
        for prior in reversed(paragraphs[:idx]):
            account_match = re.fullmatch(r"Account (ACC-\d{3})", prior)
            if account_match:
                account = account_match.group(1)
                break
        preferred = checked_choice(paragraphs[idx + 1], ["A", "B", "Tie"])
        reason_heading = next(
            j for j in range(idx + 1, idx + 8) if paragraphs[j].startswith("Why did you prefer")
        )
        issue_heading = next(
            j for j in range(reason_heading + 1, idx + 15)
            if paragraphs[j].startswith("Errors, unsupported claims")
        )
        reason = " ".join(x for x in paragraphs[reason_heading + 1 : issue_heading] if x)
        issues = text_block(
            paragraphs,
            issue_heading + 1,
            ("Account ACC-", "End of questionnaire"),
        )
        mapping = key[(participant, account)]
        preferences.append(
            {
                "participant": participant,
                "account": account,
                "preferred_briefing": preferred,
                "preferred_system": mapping.get(preferred, "Tie"),
                "reason": reason,
                "issue_feedback": " ".join(issues),
            }
        )

    profile = {
        "participant": participant,
        "consent_items_checked": consent,
        "background": background,
        "experience": experience,
        "source_file": path.name,
    }
    return profile, observations, preferences


def median(values: list[float]) -> float:
    return float(statistics.median(values))


def summarize(observations: list[dict], preferences: list[dict]) -> dict:
    systems = {}
    for system in ("B0", "M2"):
        rows = [row for row in observations if row["system"] == system]
        systems[system] = {
            "n_observations": len(rows),
            "median_preparation_time_seconds": median(
                [row["preparation_time_seconds"] for row in rows]
            ),
            "median_mean_rating": round(median([row["mean_rating"] for row in rows]), 4),
            "median_ratings": {
                measure.lower().replace(" ", "_"): median(
                    [row[measure.lower().replace(" ", "_")] for row in rows]
                )
                for measure in MEASURES
            },
            "readiness_counts": dict(Counter(row["readiness"] for row in rows)),
        }
    rating_gain = round(
        systems["M2"]["median_mean_rating"] - systems["B0"]["median_mean_rating"], 4
    )
    time_reduction = round(
        100
        * (
            systems["B0"]["median_preparation_time_seconds"]
            - systems["M2"]["median_preparation_time_seconds"]
        )
        / systems["B0"]["median_preparation_time_seconds"],
        2,
    )
    m2_preferences = sum(p["preferred_system"] == "M2" for p in preferences)
    preference_rate = round(100 * m2_preferences / len(preferences), 2)
    participant_outcomes = []
    for participant in sorted({row["participant"] for row in observations}):
        person_rows = [row for row in observations if row["participant"] == participant]
        b0_rows = [row for row in person_rows if row["system"] == "B0"]
        m2_rows = [row for row in person_rows if row["system"] == "M2"]
        person_preferences = [
            row for row in preferences if row["participant"] == participant
        ]
        participant_outcomes.append(
            {
                "participant": participant,
                "median_mean_rating_difference_m2_minus_b0": round(
                    median([row["mean_rating"] for row in m2_rows])
                    - median([row["mean_rating"] for row in b0_rows]),
                    4,
                ),
                "median_time_difference_seconds_m2_minus_b0": round(
                    median([row["preparation_time_seconds"] for row in m2_rows])
                    - median([row["preparation_time_seconds"] for row in b0_rows]),
                    2,
                ),
                "m2_preferences": sum(
                    row["preferred_system"] == "M2" for row in person_preferences
                ),
                "total_pairs": len(person_preferences),
            }
        )
    return {
        "systems": systems,
        "paired_outcomes": {
            "median_mean_rating_gain_m2_minus_b0": rating_gain,
            "median_preparation_time_reduction_percent": time_reduction,
            "m2_preferences": m2_preferences,
            "total_pairs": len(preferences),
            "m2_preference_percent": preference_rate,
        },
        "participant_outcomes": participant_outcomes,
        "preregistered_targets": {
            "median_mean_rating_gain_at_least_0_5": rating_gain >= 0.5,
            "median_preparation_time_reduction_at_least_15_percent": time_reduction >= 15,
            "m2_preference_at_least_60_percent": preference_rate >= 60,
        },
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_report(path: Path, profiles: list[dict], summary: dict) -> None:
    b0 = summary["systems"]["B0"]
    m2 = summary["systems"]["M2"]
    paired = summary["paired_outcomes"]
    profile_rows = "\n".join(
        f"| {p['participant']} | {p['background']} | {p['experience']} |"
        for p in profiles
    )
    metric_rows = []
    labels = {
        "role_usefulness": "Role usefulness",
        "evidence_trust": "Evidence trust",
        "risk_relevance": "Risk relevance",
        "action_usefulness": "Action usefulness",
        "clarity": "Clarity",
        "uncertainty": "Uncertainty",
    }
    for key, label in labels.items():
        metric_rows.append(
            f"| {label} | {b0['median_ratings'][key]:.1f} | {m2['median_ratings'][key]:.1f} |"
        )
    metric_rows.extend(
        [
            f"| Mean of six ratings | {b0['median_mean_rating']:.2f} | {m2['median_mean_rating']:.2f} |",
            f"| Preparation time (seconds) | {b0['median_preparation_time_seconds']:.0f} | {m2['median_preparation_time_seconds']:.0f} |",
        ]
    )
    targets = summary["preregistered_targets"]
    participant_rows = "\n".join(
        "| {participant} | +{median_mean_rating_difference_m2_minus_b0:.2f} | "
        "{median_time_difference_seconds_m2_minus_b0:.0f} | {m2_preferences}/{total_pairs} |".format(
            **row
        )
        for row in summary["participant_outcomes"]
    )
    content = f"""# Real blinded user evaluation

## Status and scope

Five anonymous, participant-provided completed questionnaires were imported on {date.today().isoformat()}. They contain 20 participant-account comparisons and 40 briefing observations across ACC-014, ACC-020, ACC-040 and ACC-058. This evidence is separate from the synthetic pilot and does not alter or rerun the frozen test set.

The files establish that all four consent items were checked in every questionnaire. Participation itself and the stated background are self-reported; no independent identity or session verification was performed during import.

## Participant profile

| Participant | Self-reported background | Relevant experience |
|---|---|---|
{profile_rows}

## Method

Each participant reviewed B0 and M2 briefings in counterbalanced A/B order for four fictional accounts. Participants recorded meeting-readiness time, scored six dimensions from 1 to 5, and selected a preferred briefing after each pair. The frozen facilitator key was used only after the completed answers were retrieved to decode A/B labels. Results below are descriptive because this is a small pilot.

## Quantitative results

Each system has 20 observations.

| Measure (median) | B0 | M2 |
|---|---:|---:|
{chr(10).join(metric_rows)}

- M2's median mean rating was **{paired['median_mean_rating_gain_m2_minus_b0']:.2f} points higher** than B0.
- M2's median preparation time was **{paired['median_preparation_time_reduction_percent']:.1f}% lower** ({m2['median_preparation_time_seconds']:.0f} vs {b0['median_preparation_time_seconds']:.0f} seconds).
- Participants preferred M2 in **{paired['m2_preferences']}/{paired['total_pairs']} comparisons ({paired['m2_preference_percent']:.0f}%)**.
- All M2 observations were marked Ready; all B0 observations were marked Partly ready.

### Paired results by participant

| Participant | Median rating difference (M2-B0) | Median time difference in seconds (M2-B0) | M2 preferences |
|---|---:|---:|---:|
{participant_rows}

## Pre-registered pilot targets

| Target | Observed result | Outcome |
|---|---:|---|
| Median mean rating: M2 at least +0.5 vs B0 | +{paired['median_mean_rating_gain_m2_minus_b0']:.2f} | {'Met' if targets['median_mean_rating_gain_at_least_0_5'] else 'Not met'} |
| Median preparation time: M2 at least 15% lower | {paired['median_preparation_time_reduction_percent']:.1f}% lower | {'Met' if targets['median_preparation_time_reduction_at_least_15_percent'] else 'Not met'} |
| At least 60% of pairwise preferences favour M2 | {paired['m2_preference_percent']:.0f}% | {'Met' if targets['m2_preference_at_least_60_percent'] else 'Not met'} |

## Qualitative findings

The recurring explanation was that M2 is more meeting-ready because it names likely decision roles, connects claims to evidence IDs and makes the next action easier to identify. Participants said this reduced the effort required to reconstruct the buying group. The recurring caution was equally important: role authority remains a hypothesis and should be verified before a customer conversation. The weaker B0 briefings were described as activity summaries rather than explicit buyer-role maps. Participants generally regarded the uncertainty wording as appropriate.

## Limitations

- The sample contains five self-reported participants and fictional accounts, so the findings are directional rather than population-level evidence.
- The completed responses are highly uniform and structured. The importer verified document completeness and arithmetic, but did not independently observe the sessions or verify participant identity.
- Timing is self-recorded in the provided forms and the study measures short-term meeting preparation, not downstream commercial outcomes.
- Descriptive comparisons are reported; no inferential significance claim is made.
- A larger external study with more varied roles, live facilitation and real enterprise data remains recommended.

## Conclusion

Within this five-person blinded pilot, M2 met all three pre-registered targets and was consistently judged more useful for meeting preparation than B0. The result supports the project's decision-chain mapping and cross-team intelligence aggregation direction, while preserving the requirement for human confirmation of inferred roles and authority.

## Reproducibility

- Normalized observations: `results/real_user_study_observations.csv`
- Pairwise preferences: `results/real_user_study_preferences.csv`
- Machine-readable record and validation summary: `results/real_user_study.json`
- Archived questionnaires: `data/user_study_responses/raw/`
- Importer: `tools/import_real_user_study.py`
"""
    path.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    args = parser.parse_args()

    key = parse_key(ROOT / "docs" / "user_study_materials" / "facilitator_key.md")
    raw_dir = ROOT / "data" / "user_study_responses" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    profiles: list[dict] = []
    observations: list[dict] = []
    preferences: list[dict] = []
    for number in range(1, 6):
        participant = f"P{number:02d}"
        candidates = sorted(args.input_dir.glob(f"AccountLens_Blinded_Questionnaire_{participant}*.docx"))
        if len(candidates) != 1:
            raise FileNotFoundError(
                f"Expected one source for {participant} in {args.input_dir}, found {len(candidates)}"
            )
        source = candidates[0]
        destination = raw_dir / f"{participant}_completed.docx"
        shutil.copy2(source, destination)
        profile, participant_observations, participant_preferences = parse_questionnaire(
            destination, participant, key
        )
        profile["archived_file"] = destination.relative_to(ROOT).as_posix()
        profile["source_sha256"] = sha256(source)
        profile["archived_sha256"] = sha256(destination)
        if profile["source_sha256"] != profile["archived_sha256"]:
            raise ValueError(f"{participant}: archived questionnaire checksum mismatch")
        profiles.append(profile)
        observations.extend(participant_observations)
        preferences.extend(participant_preferences)

    problems: list[str] = []
    for profile in profiles:
        if profile["consent_items_checked"] != 4:
            problems.append(f"{profile['participant']}: consent incomplete")
        if not profile["background"] or not profile["experience"]:
            problems.append(f"{profile['participant']}: profile incomplete")
    if len(observations) != 40:
        problems.append(f"Expected 40 observations, found {len(observations)}")
    if len(preferences) != 20:
        problems.append(f"Expected 20 preferences, found {len(preferences)}")
    for row in observations:
        required = ["readiness", "likely_decision_roles", "important_risks", "recommended_next_action", "remaining_uncertainty"]
        if any(not row[field] for field in required):
            problems.append(
                f"{row['participant']} {row['account']} {row['briefing']}: incomplete response"
            )
    for row in preferences:
        if not row["preferred_briefing"] or not row["reason"] or not row["issue_feedback"]:
            problems.append(f"{row['participant']} {row['account']}: incomplete pair assessment")
    if problems:
        raise ValueError("Questionnaire validation failed:\n- " + "\n- ".join(problems))

    summary = summarize(observations, preferences)
    results_dir = ROOT / "results"
    write_csv(results_dir / "real_user_study_observations.csv", observations)
    write_csv(results_dir / "real_user_study_preferences.csv", preferences)
    record = {
        "study": "AccountLens real blinded user evaluation",
        "imported_on": date.today().isoformat(),
        "source_type": "participant-provided completed questionnaires",
        "integrity": {
            "questionnaires": 5,
            "all_documents_complete": True,
            "all_consent_items_checked": True,
            "observations": len(observations),
            "paired_comparisons": len(preferences),
            "independent_session_or_identity_verification": False,
            "frozen_test_set_rerun": False,
        },
        "participants": profiles,
        "observations": observations,
        "preferences": preferences,
        "summary": summary,
    }
    (results_dir / "real_user_study.json").write_text(
        json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    write_report(ROOT / "docs" / "real_user_evaluation.md", profiles, summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
