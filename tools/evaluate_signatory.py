"""Create the Class 5 signatory and cost-to-serve evaluation artifacts."""

from __future__ import annotations

import json
from pathlib import Path

from accountlens.config import DEFAULT_DATA_DIR, DEFAULT_RESULTS_DIR
from accountlens.evaluation.economics import break_even_hourly_rate, cost_to_serve
from accountlens.evaluation.metrics import signatory_selection_metrics
from accountlens.io import load_dataset, write_json


ROOT = Path(__file__).resolve().parents[1]


def build_signatory_evaluation() -> dict:
    dataset = load_dataset(DEFAULT_DATA_DIR)
    validation_ids = set(dataset["splits"]["validation"])
    accounts = [row for row in dataset["accounts"] if row["account_id"] in validation_ids]
    contacts = [row for row in dataset["contacts"] if row["account_id"] in validation_ids]

    systems = {}
    for label, filename in (("B0", "baseline_validation.json"), ("M2", "m2_validation.json")):
        result = json.loads((DEFAULT_RESULTS_DIR / filename).read_text(encoding="utf-8"))
        systems[label] = signatory_selection_metrics(accounts, contacts, result["predictions"])

    return {
        "definition": (
            "The true signatory is the contact with final commercial approval authority. "
            "A procurement or legal contact who only executes paperwork is not the signatory."
        ),
        "split": "validation",
        "post_freeze_supplement": True,
        "model_calls_made": 0,
        "selection_rule": (
            "Select the highest-confidence non-abstained economic_buyer prediction for each account."
        ),
        "systems": systems,
    }


def build_economics() -> dict:
    m2_test = json.loads((DEFAULT_RESULTS_DIR / "m2_test.json").read_text(encoding="utf-8"))
    user_study = json.loads((DEFAULT_RESULTS_DIR / "real_user_study.json").read_text(encoding="utf-8"))
    accounts = int(m2_test["accounts"])
    variable_cost = m2_test["usage"]["estimated_cost_usd"] / accounts
    seconds_saved = (
        user_study["summary"]["systems"]["B0"]["median_preparation_time_seconds"]
        - user_study["summary"]["systems"]["M2"]["median_preparation_time_seconds"]
    )

    scenario_inputs = [
        ("Observed prototype variable only", 1.00, 0, 0, 0, 500),
        ("Low overhead illustration", 0.95, 5, 30, 100, 500),
        ("Expected illustration", 0.90, 10, 45, 500, 500),
        ("Conservative illustration", 0.80, 20, 60, 1500, 250),
    ]
    scenarios = []
    for name, success_rate, minutes, hourly_rate, fixed, volume in scenario_inputs:
        row = cost_to_serve(
            variable_cost_usd=variable_cost,
            success_rate=success_rate,
            fallback_minutes=minutes,
            loaded_hourly_rate_usd=hourly_rate,
            fixed_monthly_cost_usd=fixed,
            monthly_volume=volume,
        )
        row.update(
            {
                "name": name,
                "fallback_minutes": minutes,
                "loaded_hourly_rate_usd": hourly_rate,
                "fixed_monthly_cost_usd": fixed,
                "monthly_volume": volume,
                "break_even_hourly_rate_usd": break_even_hourly_rate(
                    row["cost_per_successful_briefing_usd"], seconds_saved
                ),
            }
        )
        scenarios.append(row)

    return {
        "calibration": "Project estimates dated 24 September 2026; production assumptions are illustrative.",
        "formula": (
            "variable cost + (1 - success rate) * human fallback cost "
            "+ fixed monthly cost / monthly volume"
        ),
        "observed_test_accounts": accounts,
        "observed_test_cost_usd": m2_test["usage"]["estimated_cost_usd"],
        "observed_variable_cost_per_briefing_usd": round(variable_cost, 6),
        "ten_dollar_capacity_at_observed_variable_cost": int(10 / variable_cost),
        "pilot_seconds_saved": seconds_saved,
        "scenarios": scenarios,
        "limitations": [
            "The observed variable cost excludes production connectors, monitoring, maintenance and governance.",
            "The production success rate, human fallback time, loaded wage and fixed monthly cost are not yet measured.",
            "The five-person pilot time difference is directional and self-recorded.",
        ],
    }


def main() -> None:
    signatory = build_signatory_evaluation()
    economics = build_economics()
    write_json(DEFAULT_RESULTS_DIR / "signatory_validation.json", signatory)
    write_json(DEFAULT_RESULTS_DIR / "class5_economics.json", economics)
    print(DEFAULT_RESULTS_DIR / "signatory_validation.json")
    print(DEFAULT_RESULTS_DIR / "class5_economics.json")


if __name__ == "__main__":
    main()
