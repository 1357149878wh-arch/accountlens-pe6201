"""Dependency-light classification metrics for reproducible evaluation."""

from __future__ import annotations

from accountlens.schemas import DecisionRole


LABELS = [role.value for role in DecisionRole]


def classification_metrics(truth_rows: list[dict], prediction_rows: list[dict]) -> dict:
    truth_by_contact = {row["contact_id"]: str(row["role"]) for row in truth_rows}
    pred_by_contact = {row["contact_id"]: str(row["role"]) for row in prediction_rows}
    missing = sorted(set(truth_by_contact) - set(pred_by_contact))
    if missing:
        raise ValueError(f"Missing predictions for {len(missing)} contacts")

    confusion = {actual: {predicted: 0 for predicted in LABELS} for actual in LABELS}
    for contact_id, actual in truth_by_contact.items():
        predicted = pred_by_contact[contact_id]
        if actual not in confusion or predicted not in confusion[actual]:
            raise ValueError(f"Unknown label: actual={actual}, predicted={predicted}")
        confusion[actual][predicted] += 1

    per_class: dict[str, dict[str, float | int]] = {}
    for label in LABELS:
        tp = confusion[label][label]
        fp = sum(confusion[other][label] for other in LABELS if other != label)
        fn = sum(confusion[label][other] for other in LABELS if other != label)
        support = sum(confusion[label].values())
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        per_class[label] = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "support": support,
        }

    total = len(truth_by_contact)
    correct = sum(confusion[label][label] for label in LABELS)
    macro_f1 = sum(float(per_class[label]["f1"]) for label in LABELS) / len(LABELS)
    coverage = sum(not bool(row.get("abstained")) for row in prediction_rows) / total if total else 0.0
    return {
        "samples": total,
        "accuracy": round(correct / total if total else 0.0, 4),
        "macro_f1": round(macro_f1, 4),
        "coverage": round(coverage, 4),
        "per_class": per_class,
        "confusion_matrix": confusion,
    }


def signatory_selection_metrics(
    accounts: list[dict],
    contacts: list[dict],
    prediction_rows: list[dict],
) -> dict:
    """Evaluate one selected commercial signatory per account.

    The system selects the highest-confidence, non-abstained economic-buyer
    prediction. Precision measures whether selected contacts are correct;
    recall measures how many accounts receive a correct selection. The
    per-account record keeps omissions and multiple-candidate cases visible.
    """

    contact_to_account = {row["contact_id"]: row["account_id"] for row in contacts}
    account_ids = {row["account_id"] for row in accounts}
    predictions_by_account: dict[str, list[dict]] = {account_id: [] for account_id in account_ids}
    for row in prediction_rows:
        account_id = contact_to_account.get(row["contact_id"])
        if account_id in predictions_by_account:
            predictions_by_account[account_id].append(row)

    per_account: list[dict] = []
    selected_count = 0
    correct_count = 0
    multiple_candidate_accounts = 0
    for account in sorted(accounts, key=lambda item: item["account_id"]):
        account_id = account["account_id"]
        true_contact_id = account.get("true_signatory_contact_id")
        if not true_contact_id:
            raise ValueError(f"Missing true_signatory_contact_id for {account_id}")
        if contact_to_account.get(true_contact_id) != account_id:
            raise ValueError(f"Invalid true signatory {true_contact_id} for {account_id}")

        candidates = [
            row
            for row in predictions_by_account[account_id]
            if str(row.get("role")) == DecisionRole.ECONOMIC_BUYER.value
            and not bool(row.get("abstained"))
        ]
        candidates.sort(key=lambda row: (-float(row.get("confidence", 0.0)), row["contact_id"]))
        if len(candidates) > 1:
            multiple_candidate_accounts += 1
        selected = candidates[0] if candidates else None
        selected_contact_id = selected["contact_id"] if selected else None
        correct = selected_contact_id == true_contact_id
        if selected:
            selected_count += 1
        if correct:
            correct_count += 1
        per_account.append(
            {
                "account_id": account_id,
                "true_signatory_contact_id": true_contact_id,
                "selected_signatory_contact_id": selected_contact_id,
                "selected_confidence": round(float(selected.get("confidence", 0.0)), 4) if selected else None,
                "candidate_count": len(candidates),
                "correct": correct,
            }
        )

    total_accounts = len(accounts)
    precision = correct_count / selected_count if selected_count else 0.0
    recall = correct_count / total_accounts if total_accounts else 0.0
    selection_rate = selected_count / total_accounts if total_accounts else 0.0
    return {
        "accounts": total_accounts,
        "selections": selected_count,
        "correct_selections": correct_count,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "selection_rate": round(selection_rate, 4),
        "multiple_candidate_accounts": multiple_candidate_accounts,
        "per_account": per_account,
    }
