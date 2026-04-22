from .tools import provide_hint


class HintProviderAgent:
    def __init__(self, domain: str = "math"):
        self.domain = domain

    def provide_hint(self, question: str) -> str:
        """
        Provide hints based on question text and configured domain.
        """
        return provide_hint(question=question, domain=self.domain)