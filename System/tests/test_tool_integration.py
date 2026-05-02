import unittest
from tools.content_retrieval_tool import file_reader_tool, parser_tool
from tools.hint_provider_tool import hint_generation_tool
from tools.question_generator_tool import question_generation_tool
from tools.exam_simulation_tool import evaluation_tool

class TestToolIntegration(unittest.TestCase):
    def test_content_retrieval_tool(self):
        raw = file_reader_tool("math", "exam1.txt")
        parsed = parser_tool(raw)
        self.assertIsInstance(parsed, list)
        self.assertGreater(len(parsed), 0, "Content parser returned no questions.")
        self.assertIn("question", parsed[0])
        self.assertIn("topic", parsed[0])
        self.assertIn("difficulty", parsed[0])
        self.assertIn("type", parsed[0])

    def test_question_generation_tool(self):
        base = parser_tool(file_reader_tool("math", "exam1.txt"))
        questions = question_generation_tool(base, count=4, difficulty="medium")
        self.assertIsInstance(questions, list)
        self.assertGreater(len(questions), 0, "No questions generated.")
        self.assertEqual(len({q["question"] for q in questions}), len(questions), "Duplicate questions generated.")

    def test_hint_and_evaluation_tools(self):
        base = parser_tool(file_reader_tool("math", "exam1.txt"))
        generated = question_generation_tool(base, count=3, difficulty="medium")
        hint = hint_generation_tool(generated[0])
        self.assertEqual(set(hint.keys()), {"hint_level_1", "hint_level_2", "hint_level_3"})
        evaluation = evaluation_tool(generated)
        self.assertIn("summary", evaluation)
        self.assertIn("details", evaluation)
        self.assertGreater(evaluation["summary"]["total"], 0)

if __name__ == "__main__":
    unittest.main()