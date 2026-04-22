import unittest
from tools.content_retrieval_tool import fetch_exam_content
from tools.question_generator_tool import generate_question

class TestToolIntegration(unittest.TestCase):
    def test_content_retrieval_tool(self):
        content = fetch_exam_content("math")
        self.assertIsInstance(content, list)
        self.assertGreater(len(content), 0, "Content retrieval failed.")

    def test_question_generation_tool(self):
        questions = generate_question("math")
        self.assertIsInstance(questions, list)
        self.assertGreater(len(questions), 0, "No questions generated.")

if __name__ == "__main__":
    unittest.main()