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


def _normalize_question_key(text: str) -> str:
    return " ".join(text.replace("\n", " ").split()).strip()


def _resolve_student_answer(question_text: str, provided_answers: Dict[str, str]) -> str | None:
    if not provided_answers:
        return None
    if question_text in provided_answers:
        return provided_answers[question_text]
    target = _normalize_question_key(question_text)
    for key, value in provided_answers.items():
        if _normalize_question_key(key) == target:
            return value
    return None


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
        for item in questions:
            question_text = item["question"]
            expected = item["answer"].strip().lower()
            resolved = _resolve_student_answer(question_text, provided_answers)
            # No submission (user skipped / Next without Save): show empty, grade as incorrect.
            student_raw = resolved if resolved is not None else ""
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