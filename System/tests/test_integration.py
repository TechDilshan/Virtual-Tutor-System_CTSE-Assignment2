import unittest
from framework.orchestrator import Orchestrator

class TestOrchestratorIntegration(unittest.TestCase):
    def setUp(self):
        self.orchestrator = Orchestrator(exam_file="exam1.txt", question_count=4, difficulty="medium")

    def test_start_exam_simulation(self):
        results = self.orchestrator.start_exam_simulation()
        self.assertIsInstance(results, dict)
        self.assertIn("summary", results)
        self.assertIn("details", results)
        self.assertEqual(results["summary"]["total"], 4)
        state = self.orchestrator.state_manager.snapshot()
        self.assertIn("questions", state)
        self.assertIn("score", state)
        self.assertIsInstance(state.get("weak_topics"), list)

if __name__ == "__main__":
    unittest.main()