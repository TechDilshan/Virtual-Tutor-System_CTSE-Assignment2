import unittest
from framework.orchestrator import Orchestrator

class TestOrchestratorIntegration(unittest.TestCase):
    def setUp(self):
        self.orchestrator = Orchestrator()

    def test_start_exam_simulation(self):
        results = self.orchestrator.start_exam_simulation()
        self.assertIsInstance(results, dict)
        self.assertGreater(len(results), 0, "Exam results should not be empty.")

if __name__ == "__main__":
    unittest.main()