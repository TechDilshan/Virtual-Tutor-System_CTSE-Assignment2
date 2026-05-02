import unittest
from .agent import ExamSimulationAgent

class TestExamSimulationAgent(unittest.TestCase):
    def setUp(self):
        self.agent = ExamSimulationAgent()

    def test_simulate_exam(self):
        questions = [
            {
                "question": "What is 2 + 2?",
                "difficulty": "easy",
                "topic": "arithmetic",
                "type": "general-math",
                "answer": "4",
            },
            {
                "question": "Solve for x: 5x = 25",
                "difficulty": "medium",
                "topic": "algebra",
                "type": "equation-solving",
                "answer": "5",
            },
        ]
        results = self.agent.simulate_exam(questions)
        self.assertIsInstance(results, dict)
        self.assertIn("summary", results)
        self.assertIn("details", results)
        self.assertEqual(results["summary"]["total"], 2)

if __name__ == "__main__":
    unittest.main()