import unittest
from .agent import QuestionGeneratorAgent

class TestQuestionGeneratorAgent(unittest.TestCase):
    def setUp(self):
        self.agent = QuestionGeneratorAgent(domain="math")

    def test_generate_questions(self):
        questions = self.agent.generate_questions()
        self.assertIsInstance(questions, list)
        self.assertGreater(len(questions), 0, "No questions generated.")

if __name__ == "__main__":
    unittest.main()