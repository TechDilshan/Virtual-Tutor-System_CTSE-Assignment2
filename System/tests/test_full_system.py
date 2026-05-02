import unittest
from framework.orchestrator import Orchestrator

class TestFullSystem(unittest.TestCase):
    def setUp(self):
        self.orchestrator = Orchestrator(exam_file="exam1.txt", question_count=5, difficulty="medium")

    def test_full_system_workflow(self):
        results = self.orchestrator.start_exam_simulation()
        self.assertIsInstance(results, dict)
        self.assertIn("summary", results)
        self.assertIn("details", results)
        self.assertGreater(results["summary"]["total"], 0, "System workflow failed.")
        self.assertGreater(len(results["details"]), 0, "No evaluated results returned.")

if __name__ == "__main__":
    unittest.main()