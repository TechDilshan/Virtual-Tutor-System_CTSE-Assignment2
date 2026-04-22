from __future__ import annotations

import random
import re
from typing import Dict, List, Optional

from tools.llm_tool import generate_with_ollama, get_last_ollama_error


def _safe_ollama(prompt: str, fallback: str) -> str:
    output = generate_with_ollama(prompt)
    if output:
        return output.strip()
    reason = get_last_ollama_error()
    return f"{fallback} [{reason}]" if reason else fallback


def _compact_text(value: str) -> str:
    text = " ".join(value.strip().split())
    text = re.sub(r"^mode:\s*(correct|incorrect|partial)\s*!\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^answer:\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^the correct answer is:\s*", "", text, flags=re.IGNORECASE)
    return text


def simulate_exam(
    questions: List[str],
    duration: int = 30,
    seed: Optional[int] = None,
) -> Dict[str, Dict[str, str]]:
    """
    Simulate an exam result set without blocking execution.

    Args:
        questions: Questions to evaluate.
        duration: Retained for compatibility and reporting.
        seed: Optional deterministic random seed.
    """
    results: Dict[str, Dict[str, str]] = {}
    rng = random.Random(seed)

    for question in questions:
        expected_prompt = (
            "You are a strict exam evaluator. Provide only the final expected answer for the "
            f"following question in one concise line.\nQuestion: {question}"
        )
        expected = _safe_ollama(expected_prompt, "Expected answer unavailable (Ollama offline).")
        expected = _compact_text(expected)

        student_mode = rng.choice(["correct", "partial", "incorrect"])
        student_prompt = (
            "Act as a student and answer this question in one short line. "
            f"Mode: {student_mode}. "
            "If mode is correct, give a fully correct answer. "
            "If mode is partial, give an incomplete but relevant answer. "
            "If mode is incorrect, give a clearly wrong answer.\n"
            f"Question: {question}"
        )
        student_answer = _safe_ollama(student_prompt, f"{student_mode} answer unavailable (Ollama offline).")
        student_answer = _compact_text(student_answer)

        judge_prompt = (
            "Evaluate the student's answer compared to expected answer. Return exactly one label only: "
            "Correct or Incorrect or Partially Correct.\n"
            f"Question: {question}\n"
            f"Expected: {expected}\n"
            f"Student: {student_answer}"
        )
        status = _safe_ollama(judge_prompt, "Partially Correct")
        status = _compact_text(status)
        if status not in {"Correct", "Incorrect", "Partially Correct"}:
            status = "Partially Correct"

        results[question] = {
            "status": status,
            "expected_answer": expected,
            "student_answer": student_answer,
        }

    return results