from __future__ import annotations

from typing import Any, Iterable

import customtkinter as ctk


class ResultPanel(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(self, text="Results", font=ctk.CTkFont(size=24, weight="bold")).grid(
            row=0, column=0, padx=20, pady=(20, 10), sticky="w"
        )
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, padx=20, pady=(0, 16), sticky="nsew")
        self.tabview.add("Exam results")
        self.tabview.add("Automated evaluation")

        exam_tab = self.tabview.tab("Exam results")
        exam_tab.grid_columnconfigure(0, weight=1)
        exam_tab.grid_rowconfigure(1, weight=1)
        self.summary_label = ctk.CTkLabel(exam_tab, text="No exam results yet. Finish an exam to see scoring.")
        self.summary_label.grid(row=0, column=0, padx=0, pady=(0, 10), sticky="w")
        self.detail_box = ctk.CTkTextbox(exam_tab, height=360)
        self.detail_box.grid(row=1, column=0, sticky="nsew")

        auto_tab = self.tabview.tab("Automated evaluation")
        auto_tab.grid_columnconfigure(0, weight=1)
        auto_tab.grid_rowconfigure(1, weight=1)
        self.autoeval_summary = ctk.CTkLabel(
            auto_tab,
            text="Run “Automated evaluation” from the Dashboard to validate the agent pipeline.",
            wraplength=700,
            justify="left",
        )
        self.autoeval_summary.grid(row=0, column=0, padx=0, pady=(0, 10), sticky="w")
        self.autoeval_box = ctk.CTkTextbox(auto_tab, height=360)
        self.autoeval_box.grid(row=1, column=0, sticky="nsew")

    def set_results(self, results: dict) -> None:
        summary = results.get("summary", {})
        self.summary_label.configure(
            text=(
                f"Score: {summary.get('score', 0)}% | "
                f"Correct: {summary.get('correct', 0)}/{summary.get('total', 0)} | "
                f"Weak Topics: {summary.get('weak_topics', [])}"
            )
        )
        self.detail_box.delete("1.0", "end")
        for idx, row in enumerate(results.get("details", []), start=1):
            self.detail_box.insert(
                "end",
                (
                    f"{idx}. {row.get('question')}\n"
                    f"   Your answer: {row.get('student_answer')}\n"
                    f"   Correct answer: {row.get('correct_answer')}\n"
                    f"   Correct: {row.get('is_correct')}\n"
                    f"   Topic: {row.get('topic')}\n\n"
                ),
            )
        self.tabview.set("Exam results")

    def set_automated_eval(self, overall_ok: bool, check_rows: Iterable[Any]) -> None:
        """Display output from evaluation.automated_agent_eval.run_checks (CheckResult-like rows)."""
        self.autoeval_summary.configure(
            text=(
                f"Overall: {'PASS' if overall_ok else 'FAIL'} — "
                f"property/security checks on content → generated questions → evaluation output."
            )
        )
        self.autoeval_box.delete("1.0", "end")
        lines = []
        for row in check_rows:
            name = getattr(row, "name", "?")
            ok = getattr(row, "ok", False)
            details = getattr(row, "details", "")
            status = "PASS" if ok else "FAIL"
            lines.append(f"[{status}] {name}\n    {details}\n")
        self.autoeval_box.insert("1.0", "\n".join(lines) if lines else "(no rows)")
        self.tabview.set("Automated evaluation")
