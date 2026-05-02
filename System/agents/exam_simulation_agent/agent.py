from __future__ import annotations

import logging
from typing import Dict, List, Optional

from .tools import evaluation_tool
from tools.question_generator_tool import GeneratedQuestion


class ExamSimulationAgent:
    def __init__(self):
        self.results: Dict[str, object] = {}
        self.logger = logging.getLogger("virtual_tutor")

    def simulate_exam(
        self,
        questions: List[GeneratedQuestion],
        provided_answers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, object]:
        """
        Evaluate exam answers and generate performance output.
        """
        self.logger.info("ExamSimulationAgent input: questions=%s", len(questions))
        self.results = evaluation_tool(questions=questions, provided_answers=provided_answers)
        self.logger.info("ExamSimulationAgent output: keys=%s", list(self.results.keys()))
        return self.results

    def display_results(self):
        """
        Display the results of the simulated exam.
        """
        if not self.results:
            print("No exam results to display.")
        else:
            print(f"Exam Results: {self.results}")