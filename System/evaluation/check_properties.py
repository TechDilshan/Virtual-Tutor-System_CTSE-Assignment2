"""
Property-style invariant checks on agent outputs (accuracy/consistency) and
lightweight security heuristics (path safety, suspicious payloads in text).

These functions do not call external services; they are safe to import from unit tests.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Mapping, Sequence

SYSTEM_ROOT = Path(__file__).resolve().parents[1]
CONTENT_ROOT = SYSTEM_ROOT / "content"

ALLOWED_TOPICS = frozenset({"algebra", "calculus", "arithmetic", "language", "science"})

_MAX_FIELD_LEN = 8000

# Heuristic patterns that should not appear in tutoring content (injection / exfil hints).
_SUSPICIOUS_PATTERNS = (
    re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions", re.I),
    re.compile(r"system\s*prompt", re.I),
    re.compile(r"<\s*script", re.I),
    re.compile(r"javascript\s*:", re.I),
    re.compile(r"eval\s*\(", re.I),
    re.compile(r"rm\s+-rf", re.I),
    re.compile(r"\.\./\.\.", re.I),
)


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    details: str


def check_exam_filename_security(exam_file: str | None) -> List[str]:
    """Reject path traversal or odd filenames before any disk read."""
    errors: List[str] = []
    if exam_file is None:
        return errors
    if not exam_file.endswith(".txt"):
        errors.append("exam_file must be a .txt basename")
    if "/" in exam_file or "\\" in exam_file:
        errors.append("exam_file must be a basename only (no path separators)")
    if ".." in exam_file:
        errors.append("exam_file must not contain '..'")
    if not exam_file.strip():
        errors.append("exam_file is empty")
    return errors


def check_content_file_resolves_inside_domain(domain: str, exam_file: str | None) -> List[str]:
    """Ensure content_dir / exam_file stays under content/<domain>."""
    errors = []
    errors.extend(check_exam_filename_security(exam_file))
    if errors or not exam_file:
        return errors
    base = (CONTENT_ROOT / domain).resolve()
    target = (base / exam_file).resolve()
    try:
        target.relative_to(base)
    except ValueError:
        errors.append("resolved exam path would escape content directory")
    return errors


def check_text_safety(text: str, label: str) -> List[str]:
    if len(text) > _MAX_FIELD_LEN:
        return [f"{label}: exceeds max length {_MAX_FIELD_LEN}"]
    errors: List[str] = []
    for pat in _SUSPICIOUS_PATTERNS:
        if pat.search(text):
            errors.append(f"{label}: matched suspicious pattern ({pat.pattern!r})")
    return errors


def check_structured_questions(structured: Sequence[Mapping[str, Any]]) -> List[str]:
    errors: List[str] = []
    if not structured:
        errors.append("structured questions list is empty")
        return errors
    for i, item in enumerate(structured):
        prefix = f"structured[{i}]"
        for key in ("question", "topic", "difficulty", "type"):
            if key not in item:
                errors.append(f"{prefix}: missing key {key!r}")
        q = str(item.get("question", "")).strip()
        if len(q) < 6:
            errors.append(f"{prefix}: question too short")
        errors.extend(check_text_safety(q, f"{prefix}.question"))
        topic = item.get("topic", "")
        if topic not in ALLOWED_TOPICS:
            errors.append(f"{prefix}: topic {topic!r} not in allowed set")
    return errors


def check_generated_questions(generated: Sequence[Mapping[str, Any]], expected_count: int) -> List[str]:
    errors: List[str] = []
    if not generated:
        errors.append("generated questions list is empty")
        return errors
    if len(generated) != expected_count:
        errors.append(f"expected {expected_count} generated questions, got {len(generated)}")
    texts = [str(g.get("question", "")).strip() for g in generated]
    if len(set(texts)) != len(texts):
        errors.append("duplicate question strings in generated set")
    for i, g in enumerate(generated):
        prefix = f"generated[{i}]"
        for key in ("question", "answer", "topic", "difficulty", "type"):
            if key not in g:
                errors.append(f"{prefix}: missing key {key!r}")
        ans = str(g.get("answer", "")).strip()
        if not ans:
            errors.append(f"{prefix}: empty answer")
        errors.extend(check_text_safety(str(g.get("question", "")), f"{prefix}.question"))
        errors.extend(check_text_safety(ans, f"{prefix}.answer"))
    return errors


def check_evaluation_result(evaluation: Mapping[str, Any], question_count: int) -> List[str]:
    errors: List[str] = []
    summary = evaluation.get("summary")
    if not isinstance(summary, dict):
        errors.append("evaluation.summary is missing or not a dict")
        return errors
    for key in ("score", "correct", "total"):
        if key not in summary:
            errors.append(f"evaluation.summary missing {key!r}")
    try:
        score = int(summary["score"])
        correct = int(summary["correct"])
        total = int(summary["total"])
    except (KeyError, TypeError, ValueError):
        return errors + ["evaluation.summary has non-integer score/correct/total"]

    if not (0 <= score <= 100):
        errors.append(f"score {score} not in [0, 100]")
    if correct < 0 or total < 0:
        errors.append("correct/total must be non-negative")
    if correct > total:
        errors.append("correct cannot exceed total")
    if total != question_count:
        errors.append(f"evaluation total {total} != expected question count {question_count}")

    details = evaluation.get("details")
    if not isinstance(details, list):
        errors.append("evaluation.details is not a list")
    elif len(details) != question_count:
        errors.append(f"details length {len(details)} != question count {question_count}")
    return errors
