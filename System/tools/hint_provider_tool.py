from __future__ import annotations

import logging
from typing import Dict, TypedDict

from tools.llm_tool import generate_with_ollama
from tools.question_generator_tool import GeneratedQuestion


logger = logging.getLogger("virtual_tutor")


class HintBundle(TypedDict):
    hint_level_1: str
    hint_level_2: str
    hint_level_3: str


def hint_generation_tool(question_item: GeneratedQuestion) -> HintBundle:
    """
    Generate 3-level hints dynamically from question topic/type.
    """
    topic = question_item.get("topic", "arithmetic")
    q_type = question_item.get("type", "general-math")
    logger.info("hint_generation_tool input: topic=%s type=%s", topic, q_type)

    llm_hint = generate_with_ollama(
        (
            "Provide exactly three progressive hints separated by || for this question. "
            f"Topic={topic}, type={q_type}, question={question_item.get('question', '')}"
        )
    )
    if llm_hint and "||" in llm_hint:
        segments = [part.strip() for part in llm_hint.split("||") if part.strip()]
        if len(segments) >= 3:
            logger.info("hint_generation_tool output from ollama")
            return {
                "hint_level_1": segments[0],
                "hint_level_2": segments[1],
                "hint_level_3": segments[2],
            }

    try:
        if topic == "algebra" or q_type == "equation-solving":
            hints: HintBundle = {
                "hint_level_1": "Think about isolating the variable on one side.",
                "hint_level_2": "Move constants first, then simplify coefficients.",
                "hint_level_3": "Apply inverse operations in reverse order and verify by substitution.",
            }
        elif topic == "calculus" and q_type == "integration":
            hints = {
                "hint_level_1": "Use the power rule for integration.",
                "hint_level_2": "Increase the exponent by one before dividing by the new exponent.",
                "hint_level_3": "Integrate each term independently and include + C in the final expression.",
            }
        elif topic == "calculus":
            hints = {
                "hint_level_1": "Identify each term and apply derivative rules term by term.",
                "hint_level_2": "Use the power rule and keep constant multipliers.",
                "hint_level_3": "Differentiate each term separately, then combine and simplify.",
            }
        elif topic == "science":
            hints = {
                "hint_level_1": "Identify the key scientific concept in the question.",
                "hint_level_2": "Recall the related definition, symbol, or process from your notes.",
                "hint_level_3": "Connect the concept to a real example to choose the most accurate answer.",
            }
        else:
            hints = {
                "hint_level_1": "Rewrite the expression clearly before solving.",
                "hint_level_2": "Break the problem into a single operation at a time.",
                "hint_level_3": "Check the final value by plugging it back into the original statement.",
            }
        logger.info("hint_generation_tool output ready")
        return hints
    except (AttributeError, TypeError) as exc:
        logger.error("hint_generation_tool failed: %s", exc)
        return {
            "hint_level_1": "Focus on the main concept used in the question.",
            "hint_level_2": "Solve one step at a time and keep track of operations.",
            "hint_level_3": "Recheck each step to catch arithmetic or sign mistakes.",
        }