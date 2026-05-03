from __future__ import annotations

import customtkinter as ctk


class ResultPanel(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self, text="Results", font=ctk.CTkFont(size=24, weight="bold")).grid(
            row=0, column=0, padx=20, pady=(20, 10), sticky="w"
        )
        self.summary_label = ctk.CTkLabel(self, text="No results yet.")
        self.summary_label.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")
        self.eval_label = ctk.CTkLabel(self, text="Evaluation: not run yet.")
        self.eval_label.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="w")
        self.detail_box = ctk.CTkTextbox(self, height=380)
        self.detail_box.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")

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

    def set_evaluation(self, report: dict) -> None:
        overall_ok = report.get("overall_ok", False)
        self.eval_label.configure(
            text=(
                f"Evaluation: {'PASS' if overall_ok else 'FAIL'} | "
                f"Domain: {report.get('domain')} | File: {report.get('exam_file')} | "
                f"Checks: {len(report.get('checks', []))}"
            )
        )
        self.detail_box.delete("1.0", "end")
        self.detail_box.insert("end", "=== Automated Evaluation Report ===\n\n")
        for row in report.get("checks", []):
            status = "PASS" if row.get("ok") else "FAIL"
            name = row.get("name", "")
            details = row.get("details", "")
            self.detail_box.insert("end", f"[{status}] {name}\n")
            if details:
                self.detail_box.insert("end", f"  - {details}\n")
        self.detail_box.insert("end", "\n(You can also run this from CLI: python3 -m System.evaluation.run_agent_eval ...)\n")
