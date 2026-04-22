import unittest
from framework.orchestrator import Orchestrator

class TestFullSystem(unittest.TestCase):
    def setUp(self):
        self.orchestrator = Orchestrator()

    def test_full_system_workflow(self):
        results = self.orchestrator.start_exam_simulation()
        self.assertIsInstance(results, dict)
        self.assertGreater(len(results), 0, "System workflow failed.")

if __name__ == "__main__":
    unittest.main()