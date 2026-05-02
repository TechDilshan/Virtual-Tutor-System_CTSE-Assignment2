from __future__ import annotations

import logging
import re
from typing import List, TypedDict

from tools.content_retrieval_tool import StructuredQuestion
from tools.llm_tool import generate_with_ollama


logger = logging.getLogger("virtual_tutor")


class GeneratedQuestion(TypedDict):
    question: str
    difficulty: str
    topic: str
    type: str
    answer: str


def _generate_linear_variant(question: str, i: int) -> tuple[str, str]:
    match = re.search(r"([+-]?\d+)\s*x\s*([+-])\s*(\d+)\s*=\s*([+-]?\d+)", question.replace(" ", ""))
    if not match:
        a = 2 + i
        b = 3 + i
        x = 2 + i
        c = a * x + b
        return (f"Solve for x: {a}x + {b} = {c}", str(x))
    a = int(match.group(1))
    sign = match.group(2)
    b = int(match.group(3))
    c = int(match.group(4))
    b = b if sign == "+" else -b
    new_x = i + 2
    new_a = a + i if a + i != 0 else a + i + 1
    new_b = b - i
    new_c = new_a * new_x + new_b
    sign_symbol = "+" if new_b >= 0 else "-"
    return (f"Solve for x: {new_a}x {sign_symbol} {abs(new_b)} = {new_c}", str(new_x))


def _generate_calculus_variant(question: str, i: int) -> tuple[str, str, str]:
    lower = question.lower()
    if "integrate" in lower:
        power = i + 2
        coeff = i + 3
        ask = f"Integrate: {coeff}x^{power} dx"
        answer = f"{coeff/(power+1):g}x^{power+1} + C"
        return ask, answer, "integration"
    coeff = i + 2
    power = i + 2
    ask = f"Differentiate: {coeff}x^{power} + {i + 1}x"
    answer = f"{coeff * power}x^{power-1} + {i + 1}"
    return ask, answer, "differentiation"


def _generate_arithmetic_variant(i: int) -> tuple[str, str]:
    a = 10 + i
    b = 4 + (i * 2)
    return (f"What is {a} + {b}?", str(a + b))


def question_generation_tool(
    base_questions: List[StructuredQuestion],
    count: int,
    difficulty: str = "medium",
) -> List[GeneratedQuestion]:
    """
    Generate unique question variants from structured source questions.
    """
    logger.info("question_generation_tool input: base=%s count=%s difficulty=%s", len(base_questions), count, difficulty)
    if count <= 0:
        return []

    generated: List[GeneratedQuestion] = []
    seen: set[str] = set()
    filtered = [q for q in base_questions if q["difficulty"] == difficulty] or base_questions

    llm_strategy = generate_with_ollama(
        (
            f"Provide one short strategy to generate {count} {difficulty} "
            "math question variants from a base exam set."
        )
    )
    if llm_strategy:
        logger.info("question_generation_tool ollama_strategy: %s", llm_strategy[:120])
    else:
        logger.info("question_generation_tool ollama_strategy: unavailable (using deterministic templates)")

    try:
        for i in range(count * 3):
            source = filtered[i % len(filtered)] if filtered else {"question": "", "topic": "arithmetic", "difficulty": difficulty, "type": "general-math"}
            topic = source["topic"] if source["topic"] in {"algebra", "calculus", "arithmetic"} else "arithmetic"
            if difficulty == "easy":
                topic = "arithmetic"
            elif difficulty == "hard":
                topic = "calculus"

            if topic == "algebra":
                question_text, answer = _generate_linear_variant(source["question"], i + 1)
                q_type = "equation-solving"
            elif topic == "calculus":
                question_text, answer, q_type = _generate_calculus_variant(source["question"], i + 1)
            else:
                question_text, answer = _generate_arithmetic_variant(i + 1)
                q_type = "general-math"

            normalized = re.sub(r"\s+", " ", question_text.lower())
            if normalized in seen:
                continue
            seen.add(normalized)
            generated.append(
                {
                    "question": question_text,
                    "difficulty": difficulty,
                    "topic": topic,
                    "type": q_type,
                    "answer": answer,
                }
            )
            if len(generated) == count:
                break
    except (ValueError, IndexError, TypeError) as exc:
        logger.error("question_generation_tool failed: %s", exc)
        return []

    logger.info("question_generation_tool output: generated=%s", len(generated))
    return generated