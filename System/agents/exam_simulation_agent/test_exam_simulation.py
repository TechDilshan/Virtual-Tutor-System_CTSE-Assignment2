import unittest
from .agent import ExamSimulationAgent

class TestExamSimulationAgent(unittest.TestCase):
    def setUp(self):
        self.agent = ExamSimulationAgent()

    def test_simulate_exam(self):
        questions = ["What is 2 + 2?", "Solve for x: 5x = 25"]
        results = self.agent.simulate_exam(questions, duration=5)
        self.assertIsInstance(results, dict)
        self.assertGreater(len(results), 0, "Results should not be empty.")

if __name__ == "__main__":
    unittest.main()