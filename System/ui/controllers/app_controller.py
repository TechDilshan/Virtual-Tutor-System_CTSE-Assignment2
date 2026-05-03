from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Callable, Dict, List, Optional

SYSTEM_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = SYSTEM_ROOT.parent
if str(SYSTEM_ROOT) not in sys.path:
    sys.path.insert(0, str(SYSTEM_ROOT))

from framework.orchestrator import Orchestrator
from evaluation.run_agent_eval import run as eval_run


class AppController:
    def __init__(self, log_callback: Optional[Callable[[str], None]] = None) -> None:
        self.log_callback = log_callback or (lambda _: None)
        self.domain = "math"
        self.exam_file: Optional[str] = None
        self.difficulty = "medium"
        self.question_count = 5
        self.orchestrator = Orchestrator(
            domain=self.domain,
            question_count=self.question_count,
            exam_file=self.exam_file,
            difficulty=self.difficulty,
        )
        self.user_answers: Dict[str, str] = {}

    def _log(self, message: str) -> None:
        self.log_callback(message)

    def get_available_exam_files(self, domain: Optional[str] = None) -> List[str]:
        selected_domain = domain or self.domain
        content_dir = SYSTEM_ROOT / "content" / selected_domain
        if not content_dir.exists():
            return []
        return sorted(file.name for file in content_dir.glob("*.txt"))

    def set_config(
        self,
        domain: str,
        exam_file: Optional[str],
        difficulty: str,
        question_count: int,
    ) -> None:
        self.domain = domain
        self.exam_file = exam_file
        self.difficulty = difficulty
        self.question_count = question_count
        self.orchestrator = Orchestrator(
            domain=domain,
            question_count=question_count,
            exam_file=exam_file,
            difficulty=difficulty,
        )
        self.user_answers = {}
        self._log(
            f"[Orchestrator] Config updated domain={domain}, exam_file={exam_file}, "
            f"difficulty={difficulty}, n={question_count}"
        )

    def attach_exam_file(self, selected_path: str) -> str:
        source = Path(selected_path).expanduser().resolve()
        if not source.exists():
            raise FileNotFoundError("Selected exam file does not exist.")
        if source.suffix.lower() != ".txt":
            raise ValueError("Exam file must be a .txt file.")
        target_dir = SYSTEM_ROOT / "content" / self.domain
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / source.name
        if source != target:
            shutil.copy2(source, target)
        self.exam_file = target.name
        self._log(f"[Content Agent] Attached exam file '{self.exam_file}'")
        return self.exam_file

    def load_content(self) -> List[Dict[str, str]]:
        structured = self.orchestrator.run_content_retrieval()
        if not structured:
            raise ValueError("No content loaded. Check the selected domain/file.")
        self._log(
            f"[Content Agent] Loaded {len(structured)} structured questions "
            f"(tools: file_reader_tool, parser_tool)"
        )
        return structured

    def generate_questions(self, count: Optional[int] = None, difficulty: Optional[str] = None) -> List[Dict[str, str]]:
        if count is not None:
            self.orchestrator.question_count = count
        if difficulty is not None:
            self.orchestrator.difficulty = difficulty
        questions = self.orchestrator.run_question_generation()
        if not questions:
            raise ValueError("No questions generated. Load content first.")
        self._log(
            f"[Question Agent] Generated {len(questions)} questions "
            f"(tool: question_generation_tool, llm: ollama-backed pipeline)"
        )
        return questions

    def submit_answer(self, question_text: str, answer: str) -> None:
        if not question_text.strip():
            raise ValueError("Question is missing.")
        if not answer.strip():
            raise ValueError("Answer cannot be empty.")
        self.user_answers[question_text] = answer.strip()
        self._log("[Exam Agent] Captured student answer")

    def start_exam(self) -> Dict[str, object]:
        results = self.orchestrator.run_exam_simulation(provided_answers=self.user_answers)
        summary = results.get("summary", {})
        self._log(
            "[Exam Agent] Evaluated answers "
            f"(score={summary.get('score', 0)}%, weak_topics={summary.get('weak_topics', [])}, tool: evaluation_tool)"
        )
        return results

    def get_hint(self, question_text: str) -> Dict[str, str]:
        questions = self.orchestrator.state_manager.get_state("questions") or []
        match = next((item for item in questions if item.get("question") == question_text), None)
        if match is None:
            raise ValueError("Question not found in generated question set.")
        hints = self.orchestrator.hint_agent.provide_hints([match])
        bundle = hints.get(question_text, {})
        if not bundle:
            raise ValueError("Hint generation failed.")
        current_hints = self.orchestrator.state_manager.get_state("hints") or {}
        current_hints[question_text] = bundle
        self.orchestrator.state_manager.update_state("hints", current_hints)
        self._log("[Hint Agent] Generated 3-level hint (tool: hint_generation_tool, llm: ollama)")
        return bundle

    def get_results(self) -> Dict[str, object]:
        return self.orchestrator.state_manager.get_state("evaluation") or {}

    def get_state_snapshot(self) -> Dict[str, object]:
        return self.orchestrator.state_manager.snapshot()

    def run_automated_evaluation(self, llm_judge: bool = False) -> Dict[str, object]:
        if not self.exam_file:
            raise ValueError("Select an exam file before running evaluation.")
        overall_ok, checks = eval_run(
            domain=self.domain,
            exam_file=self.exam_file,
            difficulty=self.difficulty,
            count=self.question_count,
            llm_judge=llm_judge,
        )
        report = {
            "overall_ok": overall_ok,
            "domain": self.domain,
            "exam_file": self.exam_file,
            "difficulty": self.difficulty,
            "count": self.question_count,
            "checks": [{"name": c.name, "ok": c.ok, "details": c.details} for c in checks],
        }
        self._log(f"[Eval] overall_ok={overall_ok}, checks={len(checks)} (llm_judge={llm_judge})")
        return report
