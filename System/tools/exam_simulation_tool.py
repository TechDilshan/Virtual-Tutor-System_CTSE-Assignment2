from __future__ import annotations

import logging
from typing import Dict, List, TypedDict

from tools.question_generator_tool import GeneratedQuestion


logger = logging.getLogger("virtual_tutor")


class EvaluationSummary(TypedDict):
    score: int
    correct: int
    total: int
    weak_topics: List[str]


def _simulated_answer(question: GeneratedQuestion, index: int) -> str:
    """
    Produce deterministic simulated answers for non-interactive runs.
    """
    if index % 3 == 0:
        return question["answer"]
    if question["topic"] == "algebra":
        return str(int(float(question["answer"])) + 1) if question["answer"].replace(".", "", 1).isdigit() else "0"
    if question["topic"] == "calculus":
        return "Needs more steps"
    return str(max(0, int(question["answer"]) - 1)) if question["answer"].isdigit() else "0"


def evaluation_tool(
    questions: List[GeneratedQuestion],
    provided_answers: Dict[str, str] | None = None,
) -> Dict[str, object]:
    """
    Evaluate answers against expected answers and produce performance summary.
    """
    logger.info("evaluation_tool input: questions=%s provided_answers=%s", len(questions), bool(provided_answers))
    provided_answers = provided_answers or {}
    correct = 0
    details: List[Dict[str, str]] = []
    topic_misses: Dict[str, int] = {}

    try:
        for index, item in enumerate(questions):
            question_text = item["question"]
            expected = item["answer"].strip().lower()
            student_raw = provided_answers.get(question_text, _simulated_answer(item, index))
            student = str(student_raw).strip().lower()
            is_correct = student == expected
            if is_correct:
                correct += 1
            else:
                topic_misses[item["topic"]] = topic_misses.get(item["topic"], 0) + 1
            details.append(
                {
                    "question": question_text,
                    "student_answer": str(student_raw),
                    "correct_answer": item["answer"],
                    "is_correct": str(is_correct),
                    "topic": item["topic"],
                }
            )
    except (AttributeError, KeyError, TypeError, ValueError) as exc:
        logger.error("evaluation_tool failed: %s", exc)
        return {"summary": {"score": 0, "correct": 0, "total": len(questions), "weak_topics": []}, "details": []}

    total = len(questions)
    score = int((correct / total) * 100) if total else 0
    weak_topics = [topic for topic, misses in topic_misses.items() if misses > 0]
    summary: EvaluationSummary = {"score": score, "correct": correct, "total": total, "weak_topics": weak_topics}
    logger.info("evaluation_tool output: score=%s/%s", correct, total)
    return {"summary": summary, "details": details}