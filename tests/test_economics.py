from __future__ import annotations

import unittest

from accountlens.evaluation.economics import break_even_hourly_rate, cost_to_serve


class EconomicsTests(unittest.TestCase):
    def test_cost_to_serve_keeps_three_layers_separate(self) -> None:
        result = cost_to_serve(
            variable_cost_usd=0.02,
            success_rate=0.9,
            fallback_minutes=10,
            loaded_hourly_rate_usd=60,
            fixed_monthly_cost_usd=500,
            monthly_volume=500,
        )
        self.assertEqual(result["expected_fallback_cost_usd"], 1.0)
        self.assertEqual(result["fixed_cost_per_task_usd"], 1.0)
        self.assertEqual(result["cost_per_successful_briefing_usd"], 2.02)

    def test_break_even_rate(self) -> None:
        self.assertEqual(break_even_hourly_rate(0.50, 60), 30.0)
        self.assertIsNone(break_even_hourly_rate(0.50, 0))


if __name__ == "__main__":
    unittest.main()
