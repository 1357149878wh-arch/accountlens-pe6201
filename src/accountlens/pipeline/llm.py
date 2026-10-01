"""OpenAI Responses API pipeline with validation, retries, and usage logging."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Callable

from accountlens.baseline.rules import infer_roles
from accountlens.config import (
    DEFAULT_ABSTENTION_THRESHOLD,
    DEFAULT_LOG_DIR,
    DEFAULT_MODEL,
    DEFAULT_PROMPT_PATH,
    INPUT_COST_PER_MILLION_USD,
    M1_PROMPT_PATH,
    MAX_OUTPUT_TOKENS,
    OUTPUT_COST_PER_MILLION_USD,
    PROJECT_ROOT,
)
from accountlens.pipeline.run_logging import append_usage_log
from accountlens.schemas import (
    AccountBriefing,
    BriefingRun,
    DecisionRole,
    EvidenceValidationReport,
    RolePrediction,
    UsageSummary,
)


EXPERIMENT_PROMPTS = {"M1": M1_PROMPT_PATH, "M2": DEFAULT_PROMPT_PATH, "H1": DEFAULT_PROMPT_PATH}


def _load_local_env() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(PROJECT_ROOT / ".env", override=False)


def build_account_context(
    account: dict,
    contacts: list[dict],
    interactions: list[dict],
    rules_predictions: list[dict] | None = None,
) -> str:
    # Ground-truth evaluation labels must never enter the model prompt.
    model_account = {
        key: value
        for key, value in account.items()
        if key != "true_signatory_contact_id"
    }
    payload: dict[str, Any] = {
        "account": model_account,
        "contacts": contacts,
        "interactions": interactions,
    }
    if rules_predictions is not None:
        payload["deterministic_rule_features"] = rules_predictions
        payload["rule_feature_note"] = "These are fallible baseline features, not ground truth."
    return json.dumps(payload, ensure_ascii=False, indent=2)


def estimate_cost_usd(input_tokens: int, output_tokens: int) -> float:
    return round(
        input_tokens / 1_000_000 * INPUT_COST_PER_MILLION_USD
        + output_tokens / 1_000_000 * OUTPUT_COST_PER_MILLION_USD,
        6,
    )


def _collect_references(briefing: AccountBriefing) -> list[str]:
    references: list[str] = []
    for role in briefing.decision_roles:
        references.extend(role.evidence_ids)
    for activity in briefing.cross_team_activity:
        references.extend(activity.event_ids)
    for risk in briefing.risks:
        references.extend(risk.evidence_ids)
    for action in briefing.recommended_actions:
        references.extend(action.evidence_ids)
    return references


def validate_evidence(
    briefing: AccountBriefing,
    account: dict,
    contacts: list[dict],
    interactions: list[dict],
    *,
    require_evidence: bool = True,
) -> EvidenceValidationReport:
    errors: list[str] = []
    warnings: list[str] = []
    valid_event_ids = {event["event_id"] for event in interactions}
    valid_contact_ids = {contact["contact_id"] for contact in contacts}

    if briefing.account_id != account["account_id"]:
        errors.append(f"Briefing account_id {briefing.account_id!r} does not match the requested account.")

    predicted_ids = [role.contact_id for role in briefing.decision_roles]
    duplicate_ids = sorted({contact_id for contact_id in predicted_ids if predicted_ids.count(contact_id) > 1})
    if duplicate_ids:
        errors.append(f"Duplicate role predictions: {duplicate_ids}")
    missing_contacts = sorted(valid_contact_ids - set(predicted_ids))
    unknown_contacts = sorted(set(predicted_ids) - valid_contact_ids)
    if missing_contacts:
        errors.append(f"Missing contact predictions: {missing_contacts}")
    if unknown_contacts:
        errors.append(f"Unknown contact IDs: {unknown_contacts}")

    for prediction in briefing.decision_roles:
        if require_evidence and prediction.role != DecisionRole.UNKNOWN and not prediction.abstained and not prediction.evidence_ids:
            errors.append(f"Role prediction for {prediction.contact_id} has no evidence IDs.")
        if prediction.role == DecisionRole.UNKNOWN and not prediction.abstained:
            warnings.append(f"Unknown role for {prediction.contact_id} should normally be marked abstained.")
    for index, activity in enumerate(briefing.cross_team_activity, start=1):
        if require_evidence and not activity.event_ids:
            errors.append(f"Activity {index} has no evidence IDs.")
    for index, risk in enumerate(briefing.risks, start=1):
        if require_evidence and not risk.evidence_ids:
            errors.append(f"Risk {index} has no evidence IDs.")
    for index, action in enumerate(briefing.recommended_actions, start=1):
        if require_evidence and not action.evidence_ids:
            errors.append(f"Recommended action {index} has no evidence IDs.")

    references = _collect_references(briefing)
    invalid_ids = sorted({event_id for event_id in references if event_id not in valid_event_ids})
    if invalid_ids:
        errors.append(f"Invalid evidence IDs: {invalid_ids}")
    valid_count = sum(event_id in valid_event_ids for event_id in references)
    precision = valid_count / len(references) if references else 0.0
    if not briefing.cross_team_activity:
        warnings.append("The briefing contains no cross-team activity.")
    if not briefing.limitations:
        warnings.append("The briefing contains no explicit limitations.")

    return EvidenceValidationReport(
        passed=not errors,
        errors=errors,
        warnings=warnings,
        total_reference_count=len(references),
        valid_reference_count=valid_count,
        evidence_precision=round(precision, 4),
    )


def reconcile_hybrid_roles(
    briefing: AccountBriefing,
    contacts: list[dict],
    rules_predictions: list[dict],
    threshold: float = DEFAULT_ABSTENTION_THRESHOLD,
) -> AccountBriefing:
    llm_by_contact = {prediction.contact_id: prediction for prediction in briefing.decision_roles}
    rules_by_contact = {prediction["contact_id"]: prediction for prediction in rules_predictions}
    reconciled: list[RolePrediction] = []

    for contact in contacts:
        contact_id = contact["contact_id"]
        llm_prediction = llm_by_contact.get(contact_id)
        rule_prediction = rules_by_contact.get(contact_id)
        if llm_prediction and not llm_prediction.abstained and llm_prediction.confidence >= threshold:
            disagreement = (
                rule_prediction
                and not rule_prediction.get("abstained", False)
                and rule_prediction["role"] != llm_prediction.role.value
            )
            suffix = " Rule and model disagree; human review is recommended." if disagreement else ""
            reconciled.append(
                llm_prediction.model_copy(update={"source": "hybrid", "reason": llm_prediction.reason + suffix})
            )
        elif rule_prediction and not rule_prediction.get("abstained", False) and rule_prediction["confidence"] >= threshold:
            fallback = RolePrediction.model_validate(rule_prediction)
            reconciled.append(
                fallback.model_copy(
                    update={"source": "hybrid", "reason": "LLM abstained or fell below threshold; " + fallback.reason}
                )
            )
        else:
            evidence_ids = llm_prediction.evidence_ids if llm_prediction else []
            reconciled.append(
                RolePrediction(
                    contact_id=contact_id,
                    role=DecisionRole.UNKNOWN,
                    confidence=llm_prediction.confidence if llm_prediction else 0.0,
                    evidence_ids=evidence_ids,
                    reason="Neither the model nor the rules baseline supplied sufficient reliable evidence.",
                    abstained=True,
                    source="hybrid",
                )
            )

    limitations = list(briefing.limitations)
    limitations.append(f"Hybrid role threshold was {threshold:.2f}; borderline cases were abstained or used rules fallback.")
    return briefing.model_copy(update={"decision_roles": reconciled, "limitations": limitations})


def _usage_tokens(response: Any) -> tuple[int, int, int]:
    usage = getattr(response, "usage", None)
    if usage is None:
        return 0, 0, 0
    input_tokens = int(getattr(usage, "input_tokens", 0) or 0)
    output_tokens = int(getattr(usage, "output_tokens", 0) or 0)
    total_tokens = int(getattr(usage, "total_tokens", input_tokens + output_tokens) or 0)
    return input_tokens, output_tokens, total_tokens


def run_briefing(
    account: dict,
    contacts: list[dict],
    interactions: list[dict],
    *,
    experiment: str = "M2",
    model: str = DEFAULT_MODEL,
    prompt_path: Path | None = None,
    threshold: float = DEFAULT_ABSTENTION_THRESHOLD,
    client: Any | None = None,
    log_path: Path | None = None,
    max_attempts: int = 3,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> BriefingRun:
    if experiment not in EXPERIMENT_PROMPTS:
        raise ValueError(f"Unsupported experiment: {experiment}")
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")
    prompt_path = prompt_path or EXPERIMENT_PROMPTS[experiment]
    log_path = log_path or DEFAULT_LOG_DIR / "api_runs.jsonl"
    _load_local_env()

    if client is None:
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is not set. Use --dry-run or configure .env locally.")
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install the project dependencies before using the AI briefing.") from exc
        client = OpenAI(max_retries=0)

    rules_predictions = infer_roles(contacts, interactions) if experiment == "H1" else None
    context = build_account_context(account, contacts, interactions, rules_predictions)
    prompt = prompt_path.read_text(encoding="utf-8")
    correction = ""
    total_input_tokens = 0
    total_output_tokens = 0
    total_tokens = 0
    started = time.perf_counter()
    last_error: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            response = client.responses.parse(
                model=model,
                input=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": context + correction},
                ],
                text_format=AccountBriefing,
                max_output_tokens=MAX_OUTPUT_TOKENS,
                temperature=0,
                store=False,
            )
            input_tokens, output_tokens, response_total = _usage_tokens(response)
            total_input_tokens += input_tokens
            total_output_tokens += output_tokens
            total_tokens += response_total
            parsed = getattr(response, "output_parsed", None)
            if parsed is None:
                raise RuntimeError("The model returned no parsed AccountBriefing.")
            briefing = parsed if isinstance(parsed, AccountBriefing) else AccountBriefing.model_validate(parsed)
            if experiment == "H1":
                briefing = reconcile_hybrid_roles(briefing, contacts, rules_predictions or [], threshold)
            validation = validate_evidence(
                briefing,
                account,
                contacts,
                interactions,
                require_evidence=experiment != "M1",
            )
            if not validation.passed:
                if attempt < max_attempts:
                    correction = (
                        "\n\nThe previous answer failed deterministic validation. Correct every issue and return the full briefing again. "
                        + " | ".join(validation.errors)
                    )
                    continue
                raise RuntimeError("Evidence validation failed: " + " | ".join(validation.errors))

            latency = time.perf_counter() - started
            summary = UsageSummary(
                request_id=getattr(response, "id", None),
                experiment=experiment,
                model=model,
                prompt_version=prompt_path.stem,
                status="success",
                attempts=attempt,
                latency_seconds=round(latency, 4),
                input_tokens=total_input_tokens,
                output_tokens=total_output_tokens,
                total_tokens=total_tokens,
                estimated_cost_usd=estimate_cost_usd(total_input_tokens, total_output_tokens),
                validation_passed=True,
            )
            append_usage_log(log_path, summary)
            return BriefingRun(briefing=briefing, validation=validation, usage=summary)
        except Exception as exc:  # Retry boundary includes transport, parsing, and evidence repair.
            last_error = exc
            if attempt < max_attempts:
                sleep_fn(min(2 ** (attempt - 1), 4))
                continue
            latency = time.perf_counter() - started
            summary = UsageSummary(
                request_id=None,
                experiment=experiment,
                model=model,
                prompt_version=prompt_path.stem,
                status="failed",
                attempts=attempt,
                latency_seconds=round(latency, 4),
                input_tokens=total_input_tokens,
                output_tokens=total_output_tokens,
                total_tokens=total_tokens,
                estimated_cost_usd=estimate_cost_usd(total_input_tokens, total_output_tokens),
                validation_passed=False,
                error_type=type(exc).__name__,
            )
            append_usage_log(log_path, summary)

    assert last_error is not None
    raise RuntimeError(f"Briefing generation failed after {max_attempts} attempts: {last_error}") from last_error


def generate_briefing(
    account: dict,
    contacts: list[dict],
    interactions: list[dict],
    model: str = DEFAULT_MODEL,
    prompt_path: Path = DEFAULT_PROMPT_PATH,
) -> AccountBriefing:
    """Backward-compatible convenience wrapper used by the Streamlit app."""
    return run_briefing(
        account,
        contacts,
        interactions,
        experiment="M2",
        model=model,
        prompt_path=prompt_path,
    ).briefing
