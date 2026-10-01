"""Test blinded participant-packet generation and facilitator-key separation."""

import unittest
from pathlib import Path

from accountlens.evaluation.study_materials import PARTICIPANTS, STUDY_ACCOUNTS, build_materials


class StudyMaterialTests(unittest.TestCase):
    def test_builds_masked_validation_packets_and_private_key(self) -> None:
        root = Path(__file__).resolve().parents[1]
        output = root / "tests/.tmp_study_materials"
        output.mkdir(exist_ok=True)
        written = build_materials(root / "data/generated", root / "results", output, seed=6201)

        self.assertEqual(len(written), len(PARTICIPANTS) + 3)
        key = (output / "facilitator_key.md").read_text(encoding="utf-8")
        self.assertIn("B0", key)
        self.assertIn("M2", key)
        recording = (output / "facilitator_recording_sheet.md").read_text(encoding="utf-8")
        self.assertIn("Briefing scores", recording)
        self.assertIn("Do not replace blank fields", recording)
        for participant in PARTICIPANTS:
            packet = (output / f"{participant}_participant_packet.md").read_text(encoding="utf-8")
            self.assertNotIn("B0", packet)
            self.assertNotIn("M2", packet)
            self.assertNotIn("GPT", packet)
            for account_id in STUDY_ACCOUNTS:
                self.assertIn(account_id, packet)
            self.assertIn("Briefing A", packet)
            self.assertIn("Briefing B", packet)


if __name__ == "__main__":
    unittest.main()
