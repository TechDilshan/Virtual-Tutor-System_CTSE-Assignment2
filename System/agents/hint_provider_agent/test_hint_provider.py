import unittest
from .agent import HintProviderAgent

class TestHintProviderAgent(unittest.TestCase):
    def setUp(self):
        self.agent = HintProviderAgent()

    def test_provide_hints(self):
        hints = self.agent.provide_hints(
            [
                {
                    "question": "Solve for x: 4x + 2 = 18",
                    "difficulty": "medium",
                    "topic": "algebra",
                    "type": "equation-solving",
                    "answer": "4",
                }
            ]
        )
        self.assertIn("Solve for x: 4x + 2 = 18", hints)
        self.assertEqual(
            set(hints["Solve for x: 4x + 2 = 18"].keys()),
            {"hint_level_1", "hint_level_2", "hint_level_3"},
        )

if __name__ == "__main__":
    unittest.main()