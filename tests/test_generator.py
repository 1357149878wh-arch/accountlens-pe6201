from __future__ import annotations

import unittest
from datetime import date
from pathlib import Path

from accountlens.data.generate import build_dataset, save_dataset
from accountlens.io import load_dataset


class GeneratorTests(unittest.TestCase):
    def test_generator_is_reproducible_and_complete(self) -> None:
        first = build_dataset(12, 6201, date(2026, 9, 1))
        second = build_dataset(12, 6201, date(2026, 9, 1))
        self.assertEqual(first, second)
        self.assertEqual(len(first["accounts"]), 12)
        self.assertEqual(len(first["contacts"]), 72)
        self.assertEqual(len(first["role_truth"]), 72)
        economic_buyers = {
            row["account_id"]: row["contact_id"]
            for row in first["role_truth"]
            if row["role"] == "economic_buyer"
        }
        for account in first["accounts"]:
            self.assertEqual(
                account["true_signatory_contact_id"],
                economic_buyers[account["account_id"]],
            )

    def test_saved_dataset_can_be_loaded(self) -> None:
        dataset = build_dataset(12, 6201, date(2026, 9, 1))
        output = Path(__file__).parent / ".tmp_dataset"
        output.mkdir(exist_ok=True)
        manifest = save_dataset(dataset, output, 6201, date(2026, 9, 1))
        loaded = load_dataset(output)
        self.assertEqual(manifest["splits"], {"development": 6, "validation": 2, "test": 4})
        self.assertEqual(len(loaded["accounts"]), 12)


if __name__ == "__main__":
    unittest.main()
