from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, TypedDict


logger = logging.getLogger("virtual_tutor")


class StructuredQuestion(TypedDict):
    question: str
    topic: str
    difficulty: str
    type: str


def file_reader_tool(domain: str, exam_file: Optional[str] = None) -> List[str]:
    """
    Read raw exam text blocks from local content files.
    """
    try:
        base_dir = Path(__file__).resolve().parents[1]
        content_dir = base_dir / "content" / domain
        if not content_dir.exists() or not content_dir.is_dir():
            logger.warning("file_reader_tool: content directory missing for domain=%s", domain)
            return []

        blocks: List[str] = []
        if exam_file:
            file_path = content_dir / exam_file
            if file_path.exists() and file_path.suffix == ".txt":
                blocks.append(file_path.read_text(encoding="utf-8").strip())
        else:
            for file_path in sorted(content_dir.glob("*.txt")):
                blocks.append(file_path.read_text(encoding="utf-8").strip())
        logger.info("file_reader_tool: loaded %s block(s)", len(blocks))
        return [item for item in blocks if item]
    except OSError as exc:
        logger.error("file_reader_tool failed: %s", exc)
        return []


def _detect_topic(question: str) -> str:
    lower = question.lower()
    has_math_symbol = bool(re.search(r"[=+\-*/^]|\\d", lower))
    if any(
        keyword in lower
        for keyword in (
            "atom",
            "molecule",
            "symbol",
            "oxygen",
            "hydrogen",
            "water",
            "salt",
            "made of",
            "photosynthesis",
            "gravity",
            "cell",
            "energy",
            "ph",
            "acid",
            "base",
        )
    ):
        return "science"
    if any(keyword in lower for keyword in ("theme", "metaphor", "grammar", "novel", "poem", "summary", "tone", "passage", "essay")):
        return "language"
    if any(keyword in lower for keyword in ("differentiate", "integrate", "derivative", "integral", "dx")):
        return "calculus"
    if any(keyword in lower for keyword in ("solve", "equation", "x =", "for x")):
        return "algebra"
    if has_math_symbol:
        return "arithmetic"
    return "language"


def _detect_type(question: str) -> str:
    lower = question.lower()
    if any(keyword in lower for keyword in ("symbol", "formula", "element", "compound")):
        return "scientific-fact"
    if any(keyword in lower for keyword in ("experiment", "process", "reaction", "photosynthesis")):
        return "scientific-process"
    if any(keyword in lower for keyword in ("summary", "theme", "tone", "metaphor")):
        return "comprehension"
    if any(keyword in lower for keyword in ("essay", "explain", "discuss")):
        return "writing"
    if "integrate" in lower or "integral" in lower:
        return "integration"
    if "differentiate" in lower or "derivative" in lower:
        return "differentiation"
    if "solve" in lower or "equation" in lower:
        return "equation-solving"
    if "square root" in lower:
        return "root-calculation"
    return "general-math" if _detect_topic(question) != "language" else "comprehension"


def _detect_difficulty(topic: str) -> str:
    if topic == "calculus":
        return "hard"
    if topic in {"algebra", "language", "science"}:
        return "medium"
    return "easy"


def parser_tool(raw_blocks: List[str]) -> List[StructuredQuestion]:
    """
    Parse raw exam lines into normalized structured question records.
    """
    parsed: List[StructuredQuestion] = []
    seen: set[str] = set()
    line_pattern = re.compile(r"^\s*(?:q?\d+[\).:-]?\s*)?(?P<question>.+?)\s*$", re.IGNORECASE)
    try:
        for block in raw_blocks:
            for raw_line in block.splitlines():
                stripped = raw_line.strip()
                if not stripped:
                    continue
                match = line_pattern.match(stripped)
                question = match.group("question").strip() if match else stripped
                if len(question) < 6:
                    continue
                normalized = re.sub(r"\s+", " ", question.lower())
                if normalized in seen:
                    continue
                seen.add(normalized)
                topic = _detect_topic(question)
                parsed.append(
                    {
                        "question": question,
                        "topic": topic,
                        "difficulty": _detect_difficulty(topic),
                        "type": _detect_type(question),
                    }
                )
        logger.info("parser_tool: parsed %s structured question(s)", len(parsed))
    except (AttributeError, IndexError, TypeError) as exc:
        logger.error("parser_tool failed: %s", exc)
        return []
    return parsed