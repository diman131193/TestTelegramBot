from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import app.db as db
from app.diagnostics import analyze_answers, build_recommendation, load_diagnostic_sources
from app.diagnostics_validation import TELEGRAM_TEXT_LIMIT, enumerate_paths, validate_sources
from app.paths import DATA_DIR


def load_questions() -> dict:
    with (DATA_DIR / "diagnostics_snapshot.json").open(encoding="utf-8") as file:
        return json.load(file)["questions"]


class DiagnosticsTests(unittest.TestCase):
    def test_all_paths_are_valid_and_fit_telegram_limit(self):
        questions = load_questions()
        report = validate_sources(questions, *load_diagnostic_sources())

        self.assertTrue(report.ok, report.errors)
        self.assertEqual(report.terminal_paths, 3696)
        self.assertLess(report.longest_result, TELEGRAM_TEXT_LIMIT)

    def test_primary_module_follows_explicit_main_problem(self):
        cases = {
            "3.1": "primary_volume",
            "3.2": "primary_oily_roots",
            "3.3": "primary_shape_control",
            "3.4": "primary_dry_length",
        }
        for answer_id, expected_module in cases.items():
            with self.subTest(answer_id=answer_id):
                result = analyze_answers(["1.1", "2.1", answer_id, "4.1", "5.1", "8.1"])
                self.assertEqual(result.primary["id"], expected_module)

    def test_result_combines_primary_alert_and_addons(self):
        answers = ["1.6", "2.4", "3.3", "4.1", "5.3"]
        result = analyze_answers(answers)

        self.assertEqual(result.primary["id"], "primary_shape_control")
        self.assertEqual([item["id"] for item in result.alerts], ["alert_chemical_damage"])
        self.assertEqual(
            [item["id"] for item in result.addons],
            ["addon_styling_residue", "addon_long_hair"],
        )

    def test_duplicate_answer_does_not_increase_score(self):
        single = analyze_answers(["1.4", "2.3", "3.4", "4.2", "6.2"])
        duplicate = analyze_answers(["1.4", "1.4", "2.3", "3.4", "4.2", "6.2"])
        self.assertEqual(single.scores, duplicate.scores)
        self.assertEqual(single.answers, duplicate.answers)

    def test_internal_scores_are_not_shown_to_client(self):
        text = build_recommendation(["1.1", "2.1", "3.1", "4.1", "5.1", "8.1"])
        self.assertNotIn("volume_sensitivity", text)
        self.assertNotIn("/10", text)

    def test_questions_have_no_legacy_exact_path_rules(self):
        self.assertNotIn("rules", load_questions())

    def test_enumeration_is_deterministic(self):
        paths = enumerate_paths(load_questions())
        self.assertEqual(paths[0], ["1.1", "2.1", "3.1", "4.1", "5.1", "8.1"])
        self.assertEqual(len(paths), len({tuple(path) for path in paths}))


class DiagnosticSessionTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_db_path = db.DB_PATH
        db.DB_PATH = Path(self.temp_dir.name) / "test.db"
        await db.init_db()

    async def asyncTearDown(self):
        db.DB_PATH = self.original_db_path
        self.temp_dir.cleanup()

    async def test_session_survives_memory_cache_loss(self):
        await db.save_diagnostic_session(42, ["1.1", "2.1"], "3")
        progress = await db.load_diagnostic_session(42)
        self.assertEqual(progress, {"answers": ["1.1", "2.1"], "question_id": "3"})

    async def test_session_can_be_deleted(self):
        await db.save_diagnostic_session(42, ["1.1"], "2")
        await db.delete_diagnostic_session(42)
        self.assertIsNone(await db.load_diagnostic_session(42))


if __name__ == "__main__":
    unittest.main()
