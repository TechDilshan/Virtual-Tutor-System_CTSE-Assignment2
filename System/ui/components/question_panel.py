from __future__ import annotations

import customtkinter as ctk

from .hint_panel import HintPanel


class QuestionPanel(ctk.CTkFrame):
    def __init__(self, master, on_submit, on_get_hint, on_next, on_finish):
        super().__init__(master)
        self.on_submit = on_submit
        self.on_get_hint = on_get_hint
        self.on_next = on_next
        self.on_finish = on_finish
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.current_question_text = ""
        self._build()

    def _build(self) -> None:
        ctk.CTkLabel(self, text="Question & Exam Panel", font=ctk.CTkFont(size=24, weight="bold")).grid(
            row=0, column=0, padx=20, pady=(20, 10), sticky="w"
        )
        self.timer_label = ctk.CTkLabel(self, text="Timer: 00:00")
        self.timer_label.grid(row=0, column=1, padx=20, pady=(20, 10), sticky="e")

        self.question_box = ctk.CTkTextbox(self, height=160)
        self.question_box.grid(row=1, column=0, padx=20, pady=8, sticky="nsew")

        ctk.CTkLabel(self, text="Your Answer").grid(row=2, column=0, padx=20, pady=(8, 2), sticky="w")
        self.answer_entry = ctk.CTkEntry(self, placeholder_text="Type your answer here...")
        self.answer_entry.grid(row=3, column=0, padx=20, pady=(0, 8), sticky="ew")

        controls = ctk.CTkFrame(self)
        controls.grid(row=4, column=0, padx=20, pady=(8, 20), sticky="ew")
        for col in range(4):
            controls.grid_columnconfigure(col, weight=1)
        self.submit_btn = ctk.CTkButton(controls, text="Submit Answer", command=self.on_submit)
        self.hint_btn = ctk.CTkButton(controls, text="Get Hint", command=self.on_get_hint)
        self.next_btn = ctk.CTkButton(controls, text="Next", command=self.on_next)
        self.finish_btn = ctk.CTkButton(controls, text="Finish Exam", command=self.on_finish)
        self.submit_btn.grid(row=0, column=0, padx=6, pady=8, sticky="ew")
        self.hint_btn.grid(row=0, column=1, padx=6, pady=8, sticky="ew")
        self.next_btn.grid(row=0, column=2, padx=6, pady=8, sticky="ew")
        self.finish_btn.grid(row=0, column=3, padx=6, pady=8, sticky="ew")

        self.hint_panel = HintPanel(self)
        self.hint_panel.grid(row=1, column=1, rowspan=4, padx=(8, 20), pady=8, sticky="nsew")

    def set_question(self, question_text: str, position: int, total: int) -> None:
        self.current_question_text = question_text
        self.question_box.delete("1.0", "end")
        self.question_box.insert("1.0", f"Question {position}/{total}\n\n{question_text}")
        self.answer_entry.delete(0, "end")

    def get_answer(self) -> str:
        return self.answer_entry.get().strip()

    def set_timer(self, label: str) -> None:
        self.timer_label.configure(text=f"Timer: {label}")
