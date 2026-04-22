import unittest
from .agent import HintProviderAgent

class TestHintProviderAgent(unittest.TestCase):
    def setUp(self):
        self.agent = HintProviderAgent()

    def test_provide_hint(self):
        hint = self.agent.provide_hint("What is 2 + 2?")
        self.assertEqual(hint, "Think of counting small objects like apples.")

    def test_no_hint(self):
        hint = self.agent.provide_hint("Unknown question")
        self.assertEqual(hint, "No hint available.")

if __name__ == "__main__":
    unittest.main()