from __future__ import annotations

import random
import re
from typing import List, Optional

from tools.llm_tool import generate_with_ollama


def _extract_questions_from_text(content: List[str]) -> List[str]:
    pattern = re.compile(r"(?im)^\s*(?:q?\d+[\).:-]?\s*)?(.*?)\s*$")
    command_starts = ("solve", "differentiate", "integrate", "find", "calculate", "evaluate", "simplify", "prove")
    questions: List[str] = []

    for block in content:
        for line in block.splitlines():
            match = pattern.match(line.strip())
            if match:
                question = match.group(1).strip()
                normalized = question.lower()
                looks_like_question = question.endswith("?") or normalized.startswith(command_starts)
                if looks_like_question and 8 <= len(question) <= 220:
                    questions.append(question)

    return list(dict.fromkeys(questions))


def generate_question(
    domain: str,
    content: Optional[List[str]] = None,
    count: int = 3,
) -> List[str]:
    """
    Generate exam questions from content with optional local LLM enhancement.

    Args:
        domain: Subject domain.
        content: Local context content.
        count: Number of questions to produce.
    """
    sample_questions = {
        "math": [
            "What is 2 + 2?",
            "Solve for x: 5x = 25.",
            "What is the derivative of x^2?",
            "Find the integral of 2x.",
            "What is the area of a circle with radius 7?",
        ],
        "english": [
            "Write a summary of the text provided.",
            "What is the theme of the novel?",
            "Explain the use of metaphors in this poem.",
            "How does tone influence the reader?",
        ],
    }

    extracted = _extract_questions_from_text(content or [])
    if extracted:
        return extracted[:count]

    fallback_pool = sample_questions.get(domain, sample_questions["math"])
    prompt = (
        f"Generate {count} short exam questions for {domain}. "
        "Return each question on a new line and end each with a question mark."
    )
    llm_output = generate_with_ollama(prompt)
    if llm_output:
        llm_questions = [
            line.strip("- ").strip()
            for line in llm_output.splitlines()
            if line.strip().endswith("?")
        ]
        if llm_questions:
            unique = list(dict.fromkeys(llm_questions))
            return unique[:count]

    return random.sample(fallback_pool, min(count, len(fallback_pool)))