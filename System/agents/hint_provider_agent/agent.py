from __future__ import annotations

import logging
from typing import Dict, List

from .tools import hint_generation_tool
from tools.hint_provider_tool import HintBundle
from tools.question_generator_tool import GeneratedQuestion

class HintProviderAgent:
    def __init__(self, domain: str = "math"):
        self.domain = domain
        self.logger = logging.getLogger("virtual_tutor")

    def provide_hints(self, questions: List[GeneratedQuestion]) -> Dict[str, HintBundle]:
        """
        Provide progressive hints for each generated question.
        """
        self.logger.info("HintProviderAgent input: questions=%s", len(questions))
        hints = {item["question"]: hint_generation_tool(item) for item in questions}
        self.logger.info("HintProviderAgent output: hints=%s", len(hints))
        return hints