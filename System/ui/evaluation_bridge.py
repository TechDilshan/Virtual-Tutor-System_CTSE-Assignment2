"""
UI-local bridge to the automated agent evaluation runner (no changes to evaluation package).
Ensures System/ is on sys.path when the app is launched as `python ui/app.py`.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, List, Tuple

_UI_DIR = Path(__file__).resolve().parent
_SYSTEM_ROOT = _UI_DIR.parent


def _ensure_system_path() -> None:
    if str(_SYSTEM_ROOT) not in sys.path:
        sys.path.insert(0, str(_SYSTEM_ROOT))


def execute_automated_eval(
    domain: str,
    exam_file: str | None,
    question_count: int,
    difficulty: str,
    llm_judge: bool,
) -> Tuple[bool, List[Any]]:
    _ensure_system_path()
    from evaluation.automated_agent_eval import run_checks

    return run_checks(
        domain=domain,
        exam_file=exam_file,
        question_count=question_count,
        difficulty=difficulty,
        llm_judge=llm_judge,
    )
