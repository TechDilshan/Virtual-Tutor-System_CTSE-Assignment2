import unittest
from framework.state_manager import StateManager

class TestStateManager(unittest.TestCase):
    def setUp(self):
        self.state_manager = StateManager()

    def test_update_state(self):
        self.state_manager.update_state("score", 50)
        self.assertEqual(self.state_manager.get_state("score"), 50)

    def test_clear_state(self):
        self.state_manager.update_state("score", 90)
        self.state_manager.clear_state()
        self.assertEqual(self.state_manager.get_state("score"), 0)
        self.assertEqual(self.state_manager.get_state("questions"), [])

if __name__ == "__main__":
    unittest.main()