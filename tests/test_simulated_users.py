import unittest
from pathlib import Path

from accountlens.evaluation.simulated_users import PILOT_ACCOUNTS, run_simulation


class SimulatedUserStudyTests(unittest.TestCase):
    def test_pilot_is_reproducible_and_validation_only(self) -> None:
        root = Path(__file__).resolve().parents[1]
        first = run_simulation(root / "data/generated", root / "results", seed=6201)
        second = run_simulation(root / "data/generated", root / "results", seed=6201)

        self.assertEqual(first, second)
        self.assertEqual(first["study_type"], "synthetic_simulation_not_human_subject_research")
        self.assertEqual(len(first["records"]), 40)
        self.assertEqual(set(first["accounts"]), set(PILOT_ACCOUNTS))
        self.assertEqual(first["aggregate"]["B0"]["observations"], 20)
        self.assertEqual(first["aggregate"]["M2"]["observations"], 20)


if __name__ == "__main__":
    unittest.main()
