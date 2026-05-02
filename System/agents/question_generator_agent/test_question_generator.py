import unittest
from .agent import QuestionGeneratorAgent
from agents.content_retrieval_agent.agent import ContentRetrievalAgent

class TestQuestionGeneratorAgent(unittest.TestCase):
    def setUp(self):
        self.agent = QuestionGeneratorAgent(domain="math")
        self.content_agent = ContentRetrievalAgent(domain="math", exam_file="exam1.txt")

    def test_generate_questions(self):
        base = self.content_agent.retrieve_structured_content()
        questions = self.agent.generate_questions(content=base, count=3, difficulty="medium")
        self.assertIsInstance(questions, list)
        self.assertGreater(len(questions), 0, "No questions generated.")
        self.assertIn("question", questions[0])
        self.assertIn("difficulty", questions[0])
        self.assertIn("topic", questions[0])

if __name__ == "__main__":
    unittest.main()