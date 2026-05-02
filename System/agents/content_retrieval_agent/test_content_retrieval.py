import unittest

from .agent import ContentRetrievalAgent


class TestContentRetrievalAgent(unittest.TestCase):
    def setUp(self):
        self.agent = ContentRetrievalAgent(domain="math", exam_file="exam1.txt")

    def test_retrieve_structured_content(self):
        data = self.agent.retrieve_structured_content()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0, "Expected parsed exam questions.")
        self.assertEqual(set(data[0].keys()), {"question", "topic", "difficulty", "type"})


if __name__ == "__main__":
    unittest.main()
