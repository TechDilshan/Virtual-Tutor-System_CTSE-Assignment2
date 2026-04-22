from .tools import generate_question

class QuestionGeneratorAgent:
    def __init__(self, domain="math"):
        self.domain = domain

    def generate_questions(self, content=None, count=3):
        """
        Generate new questions based on the subject domain.
        """
        questions = generate_question(self.domain, content=content, count=count)
        return questions