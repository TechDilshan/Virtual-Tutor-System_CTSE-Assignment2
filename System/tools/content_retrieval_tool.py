from pathlib import Path
from typing import List, Optional


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