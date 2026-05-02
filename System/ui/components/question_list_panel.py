from __future__ import annotations

import customtkinter as ctk


class QuestionListPanel(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self, text="Generated Questions", font=ctk.CTkFont(size=24, weight="bold")).grid(
            row=0, column=0, padx=20, pady=(20, 10), sticky="w"
        )
        self.summary_label = ctk.CTkLabel(self, text="No generated questions yet.")
        self.summary_label.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")
        self.question_box = ctk.CTkTextbox(self, height=500)
        self.question_box.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")

    def set_questions(self, questions: list[dict]) -> None:
        self.summary_label.configure(text=f"Total generated questions: {len(questions)}")
        self.question_box.delete("1.0", "end")
        for idx, item in enumerate(questions, start=1):
            self.question_box.insert(
                "end",
                (
                    f"{idx}. {item.get('question', 'N/A')}\n"
                    f"   Difficulty: {item.get('difficulty', 'N/A')} | "
                    f"Topic: {item.get('topic', 'N/A')} | Type: {item.get('type', 'N/A')}\n\n"
                ),
            )
