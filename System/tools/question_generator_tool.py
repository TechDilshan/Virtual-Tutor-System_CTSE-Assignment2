from __future__ import annotations

import random
from typing import Dict, List, Optional

from tools.llm_tool import generate_with_ollama

def generate_question(
    domain: str,
    content: Optional[List[str]] = None,
    count: int = 3,
    difficulty: str = "medium",
    student_accuracy: Optional[float] = None,
) -> List[str]:
    """
    Generate new exam questions dynamically for a given domain.

    Args:
        domain: Subject domain.
        content: Optional context (not used as direct source questions).
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

    if student_accuracy is not None:
        if student_accuracy >= 0.8:
            difficulty = "hard"
        elif student_accuracy <= 0.4:
            difficulty = "easy"

    fallback_pool = sample_questions.get(domain, sample_questions["math"])
    difficulty_rules: Dict[str, str] = {
        "easy": "Focus on foundational single-step questions.",
        "medium": "Generate balanced conceptual and computational questions.",
        "hard": "Generate multi-step, challenging exam-level questions.",
    }
    prompt = (
        f"Generate {count} short exam questions for {domain} at {difficulty} difficulty. "
        f"{difficulty_rules.get(difficulty, difficulty_rules['medium'])} "
        "Generate fresh questions, do not copy from previous exam papers. "
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