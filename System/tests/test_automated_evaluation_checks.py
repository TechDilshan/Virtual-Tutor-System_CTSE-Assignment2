"""Unit tests for evaluation property checks (no Ollama, no full pipeline)."""

from __future__ import annotations

import unittest

from evaluation.check_properties import (
    check_content_file_resolves_inside_domain,
    check_evaluation_result,
    check_exam_filename_security,
    check_generated_questions,
    check_structured_questions,
    check_text_safety,
)


class TestAutomatedEvaluationChecks(unittest.TestCase):
    def test_exam_filename_rejects_traversal(self) -> None:
        self.assertGreater(len(check_exam_filename_security("../../../etc/passwd")), 0)
        self.assertGreater(len(check_exam_filename_security("bad/name.txt")), 0)

    def test_exam_filename_accepts_basename(self) -> None:
        self.assertEqual(check_exam_filename_security("exam1.txt"), [])

    def test_content_path_resolves_inside_domain(self) -> None:
        self.assertEqual(check_content_file_resolves_inside_domain("math", "exam1.txt"), [])
        self.assertGreater(len(check_content_file_resolves_inside_domain("math", "../../main.py")), 0)

    def test_structured_questions_valid(self) -> None:
        structured = [
            {
                "question": "What is 2 + 2?",
                "topic": "arithmetic",
                "difficulty": "easy",
                "type": "general-math",
            }
        ]
        self.assertEqual(check_structured_questions(structured), [])

    def test_structured_questions_rejects_short_question(self) -> None:
        structured = [
            {"question": "Why?", "topic": "arithmetic", "difficulty": "easy", "type": "x"},
        ]
        self.assertGreater(len(check_structured_questions(structured)), 0)

    def test_generated_questions_valid(self) -> None:
        gen = [
            {
                "question": "What is 3 + 3?",
                "answer": "6",
                "topic": "arithmetic",
                "difficulty": "easy",
                "type": "general-math",
            }
        ]
        self.assertEqual(check_generated_questions(gen, expected_count=1), [])

    def test_generated_questions_duplicate(self) -> None:
        gen = [
            {
                "question": "Same?",
                "answer": "1",
                "topic": "arithmetic",
                "difficulty": "easy",
                "type": "general-math",
            },
            {
                "question": "Same?",
                "answer": "2",
                "topic": "arithmetic",
                "difficulty": "easy",
                "type": "general-math",
            },
        ]
        self.assertGreater(len(check_generated_questions(gen, expected_count=2)), 0)

    def test_evaluation_shape(self) -> None:
        ev = {
            "summary": {"score": 0, "correct": 0, "total": 2},
            "details": [{"x": 1}, {"x": 2}],
        }
        self.assertEqual(check_evaluation_result(ev, question_count=2), [])

    def test_text_safety_script_tag(self) -> None:
        self.assertGreater(len(check_text_safety("<script>alert(1)</script>", "t")), 0)

    def test_text_safety_clean(self) -> None:
        self.assertEqual(check_text_safety("What is 5 + 5?", "t"), [])


if __name__ == "__main__":
    unittest.main()
