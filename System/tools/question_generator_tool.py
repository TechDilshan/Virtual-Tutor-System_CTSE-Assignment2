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


def _sanitize_llm_question(raw_text: str) -> str | None:
    candidate = raw_text.strip().splitlines()[0].strip("- ").strip()
    candidate = re.sub(r"^here(?:'s| is)\s+(?:a\s+)?new\s+exam-style\s+\w+\s+question:\s*", "", candidate, flags=re.IGNORECASE)
    candidate = re.sub(r"^here(?:'s| is)\s+(?:a\s+)?new\s+variant:\s*", "", candidate, flags=re.IGNORECASE)
    candidate = re.sub(r"^question:\s*", "", candidate, flags=re.IGNORECASE)
    if not candidate or len(candidate) < 6:
        return None
    if not candidate.endswith("?"):
        candidate = f"{candidate}?"
    return candidate


def _mutate_numbers_from_source(source_question: str, i: int) -> str:
    numbers = re.findall(r"-?\d+", source_question)
    if not numbers:
        return f"{source_question.rstrip('?')} (Variant {i})?"
    replacements = [str(int(value) + i) for value in numbers]
    idx = 0

    def repl(_: re.Match[str]) -> str:
        nonlocal idx
        value = replacements[idx] if idx < len(replacements) else replacements[-1]
        idx += 1
        return value

    return re.sub(r"-?\d+", repl, source_question, count=len(replacements))


def _generate_linear_variant(question: str, i: int) -> tuple[str, str]:
    match = re.search(r"([+-]?\d+)\s*x\s*([+-])\s*(\d+)\s*=\s*([+-]?\d+)", question.replace(" ", ""))
    if not match:
        variant = _mutate_numbers_from_source(question, i)
        return (variant, "Derived from source equation")
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
        ask = _mutate_numbers_from_source(question, i)
        answer = "Derived anti-derivative from source integral"
        return ask, answer, "integration"
    ask = _mutate_numbers_from_source(question, i)
    answer = "Derived derivative from source function"
    return ask, answer, "differentiation"


def _generate_arithmetic_variant(source_question: str, i: int) -> tuple[str, str]:
    variant = _mutate_numbers_from_source(source_question, i)
    return (variant, "Derived from source arithmetic question")


def _generate_language_variant(source_question: str, i: int) -> tuple[str, str, str]:
    llm_variant = generate_with_ollama(
        (
            "Create one new exam-style English/language question variant from this source question. "
            "Keep similar difficulty and return question only.\n"
            f"Source: {source_question}"
        )
    )
    if llm_variant:
        question = _sanitize_llm_question(llm_variant)
        if question:
            return question, "Open-ended", "comprehension"
    return f"{source_question.rstrip('?')} (Practice Variant {i})?", "Open-ended", "comprehension"


def _generate_science_variant(source_question: str, i: int) -> tuple[str, str, str]:
    llm_variant = generate_with_ollama(
        (
            "Create one new exam-style science question variant from this source question. "
            "Keep similar concept and return only the question.\n"
            f"Source: {source_question}"
        )
    )
    if llm_variant:
        question = _sanitize_llm_question(llm_variant)
        if question:
            return question, "Derived from science concept", "scientific-fact"
    fallback = _mutate_numbers_from_source(source_question, i)
    if fallback == source_question:
        fallback = f"{source_question.rstrip('?')} (Science Variant {i})?"
    return fallback, "Derived from science concept", "scientific-fact"


def question_generation_tool(
    base_questions: List[StructuredQuestion],
    count: int,
    difficulty: str = "medium",
) -> List[GeneratedQuestion]:
    """
    Generate unique question variants from structured source questions.
    """
    logger.info("question_generation_tool input: base=%s count=%s difficulty=%s", len(base_questions), count, difficulty)
    if count <= 0 or not base_questions:
        return []

    generated: List[GeneratedQuestion] = []
    seen: set[str] = set()
    filtered = [q for q in base_questions if q["difficulty"] == difficulty] or base_questions

    llm_strategy = generate_with_ollama(
        (
            f"Provide one short strategy to generate {count} {difficulty} "
            "question variants from a base exam set."
        )
    )
    if llm_strategy:
        logger.info("question_generation_tool ollama_strategy: %s", llm_strategy[:120])
    else:
        logger.info("question_generation_tool ollama_strategy: unavailable (using deterministic templates)")

    try:
        for i in range(count * 3):
            source = filtered[i % len(filtered)]
            source_topic = source.get("topic", "arithmetic")
            topic = source_topic if source_topic in {"algebra", "calculus", "arithmetic", "language", "science"} else "arithmetic"
            if difficulty == "easy" and topic not in {"language", "science"}:
                topic = "arithmetic"
            elif difficulty == "hard" and topic not in {"language", "science"}:
                topic = "calculus"

            if topic == "algebra":
                question_text, answer = _generate_linear_variant(source["question"], i + 1)
                q_type = "equation-solving"
            elif topic == "calculus":
                question_text, answer, q_type = _generate_calculus_variant(source["question"], i + 1)
            elif topic == "language":
                question_text, answer, q_type = _generate_language_variant(source["question"], i + 1)
            elif topic == "science":
                question_text, answer, q_type = _generate_science_variant(source["question"], i + 1)
            else:
                question_text, answer = _generate_arithmetic_variant(source["question"], i + 1)
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