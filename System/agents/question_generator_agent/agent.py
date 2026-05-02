from __future__ import annotations

import logging
from typing import List

from .tools import question_generation_tool
from tools.content_retrieval_tool import StructuredQuestion
from tools.question_generator_tool import GeneratedQuestion


class QuestionGeneratorAgent:
    def __init__(self, domain: str = "math"):
        self.domain = domain
        self.logger = logging.getLogger("virtual_tutor")

    def generate_questions(
        self,
        content: List[StructuredQuestion],
        count: int = 3,
        difficulty: str = "medium",
    ) -> List[GeneratedQuestion]:
        """
        Generate new questions from parsed source content.
        """
        self.logger.info(
            "QuestionGeneratorAgent input: content=%s count=%s difficulty=%s",
            len(content),
            count,
            difficulty,
        )
        questions = question_generation_tool(base_questions=content, count=count, difficulty=difficulty)
        self.logger.info("QuestionGeneratorAgent output: generated=%s", len(questions))
        return questions