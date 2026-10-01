from __future__ import annotations

import unittest

from accountlens.data.teacher_aligned import build_teacher_aligned_dataset
from accountlens.pipeline.llm import build_account_context


class TeacherAlignedDatasetTests(unittest.TestCase):
    def setUp(self) -> None:
        self.dataset = build_teacher_aligned_dataset()

    def test_exact_instructor_requested_shape(self) -> None:
        self.assertEqual(len(self.dataset["accounts"]), 10)
        self.assertEqual(len(self.dataset["emails"]), 20)
        self.assertEqual(len(self.dataset["meetings"]), 10)
        self.assertEqual(len(self.dataset["tickets"]), 20)
        for account in self.dataset["accounts"]:
            account_id = account["account_id"]
            emails = [row for row in self.dataset["emails"] if row["account_id"] == account_id]
            meetings = [row for row in self.dataset["meetings"] if row["account_id"] == account_id]
            tickets = [row for row in self.dataset["tickets"] if row["account_id"] == account_id]
            self.assertEqual(len(emails), 2)
            self.assertTrue(all(row["cc_ids"] for row in emails))
            self.assertEqual(len(meetings), 1)
            self.assertGreaterEqual(len(meetings[0]["attendee_ids"]), 4)
            self.assertEqual(len(tickets), 2)

    def test_signatory_links_are_valid_and_hidden_from_model(self) -> None:
        contact_to_account = {row["contact_id"]: row["account_id"] for row in self.dataset["contacts"]}
        for account in self.dataset["accounts"]:
            self.assertEqual(contact_to_account[account["true_signatory_contact_id"]], account["account_id"])
            account_id = account["account_id"]
            contacts = [row for row in self.dataset["contacts"] if row["account_id"] == account_id]
            interactions = [row for row in self.dataset["interactions"] if row["account_id"] == account_id]
            context = build_account_context(account, contacts, interactions)
            self.assertNotIn("true_signatory_contact_id", context)

    def test_dataset_is_deterministic(self) -> None:
        self.assertEqual(self.dataset, build_teacher_aligned_dataset())


if __name__ == "__main__":
    unittest.main()
