"""Class 5 cost-to-serve calculations for AccountLens."""

from __future__ import annotations


def cost_to_serve(
    *,
    variable_cost_usd: float,
    success_rate: float,
    fallback_minutes: float,
    loaded_hourly_rate_usd: float,
    fixed_monthly_cost_usd: float,
    monthly_volume: int,
) -> dict:
    if variable_cost_usd < 0:
        raise ValueError("variable_cost_usd must be non-negative")
    if not 0 <= success_rate <= 1:
        raise ValueError("success_rate must be between 0 and 1")
    if fallback_minutes < 0 or loaded_hourly_rate_usd < 0 or fixed_monthly_cost_usd < 0:
        raise ValueError("cost assumptions must be non-negative")
    if monthly_volume <= 0:
        raise ValueError("monthly_volume must be positive")

    fallback_cost = (1 - success_rate) * (fallback_minutes / 60) * loaded_hourly_rate_usd
    fixed_cost_per_task = fixed_monthly_cost_usd / monthly_volume
    total = variable_cost_usd + fallback_cost + fixed_cost_per_task
    return {
        "variable_cost_usd": round(variable_cost_usd, 6),
        "success_rate": round(success_rate, 4),
        "expected_fallback_cost_usd": round(fallback_cost, 6),
        "fixed_cost_per_task_usd": round(fixed_cost_per_task, 6),
        "cost_per_successful_briefing_usd": round(total, 6),
    }


def break_even_hourly_rate(cost_per_successful_briefing_usd: float, seconds_saved: float) -> float | None:
    if cost_per_successful_briefing_usd < 0:
        raise ValueError("cost must be non-negative")
    if seconds_saved <= 0:
        return None
    return round(cost_per_successful_briefing_usd / (seconds_saved / 3600), 2)
