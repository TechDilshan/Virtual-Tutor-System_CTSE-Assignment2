import random
from .tools import generate_question

class QuestionGeneratorAgent:
    def __init__(self, domain="math"):
        self.domain = domain

    def generate_questions(self):
        """
        Generate new questions based on the subject domain.
        """
        print(f"Generating questions for {self.domain}...")
        questions = generate_question(self.domain)
        return questions