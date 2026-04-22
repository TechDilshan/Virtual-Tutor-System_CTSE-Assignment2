from pathlib import Path
import re
from typing import Dict, List, Optional


def fetch_exam_content(domain: str, exam_file: Optional[str] = None) -> List[str]:
    """
    Fetch exam content for a given domain from local text files.

    Args:
        domain: Subject domain (e.g., "math").
        exam_file: Optional single file name (e.g., "exam1.txt") to load.

    Returns:
        Ordered list of text snippets loaded from domain files.
    """
    base_dir = Path(__file__).resolve().parents[1]
    content_dir = base_dir / "content" / domain

    if not content_dir.exists() or not content_dir.is_dir():
        return []

    content: List[str] = []
    if exam_file:
        file_path = content_dir / exam_file
        if file_path.exists() and file_path.suffix == ".txt":
            content.append(file_path.read_text(encoding="utf-8").strip())
    else:
        for file_path in sorted(content_dir.glob("*.txt")):
            content.append(file_path.read_text(encoding="utf-8").strip())

    return [item for item in content if item]


def extract_structured_content(raw_blocks: List[str]) -> Dict[str, List[str]]:
    """
    Convert unstructured text blocks into structured exam data.
    """
    question_pattern = re.compile(r"(?im)^\s*(?:q?\d+[\).:-]?\s*)?(.*?)\s*$")
    command_starts = ("solve", "differentiate", "integrate", "find", "calculate", "evaluate", "simplify", "prove")

    questions: List[str] = []
    study_notes: List[str] = []
    seen_questions = set()

    for block in raw_blocks:
        for line in block.splitlines():
            text = line.strip()
            if not text:
                continue
            match = question_pattern.match(text)
            candidate = match.group(1).strip() if match else text
            lower = candidate.lower()
            looks_like_question = candidate.endswith("?") or lower.startswith(command_starts)
            if looks_like_question and 8 <= len(candidate) <= 220:
                normalized = re.sub(r"\s+", " ", lower)
                if normalized not in seen_questions:
                    seen_questions.add(normalized)
                    questions.append(candidate)
            elif len(text) >= 20:
                study_notes.append(text)

    return {"questions": questions, "study_notes": study_notes}