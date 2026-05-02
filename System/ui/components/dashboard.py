from __future__ import annotations

import customtkinter as ctk


class DashboardFrame(ctk.CTkFrame):
    def __init__(
        self,
        master,
        on_refresh_files,
        on_browse_file,
        on_load_content,
        on_generate_questions,
        on_start_exam,
    ):
        super().__init__(master)
        self.on_refresh_files = on_refresh_files
        self.on_browse_file = on_browse_file
        self.on_load_content = on_load_content
        self.on_generate_questions = on_generate_questions
        self.on_start_exam = on_start_exam
        self._build()

    def _build(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(self, text="Dashboard", font=ctk.CTkFont(size=24, weight="bold")).grid(
            row=0, column=0, columnspan=3, sticky="w", padx=20, pady=(20, 10)
        )

        ctk.CTkLabel(self, text="Domain").grid(row=1, column=0, padx=20, pady=8, sticky="w")
        self.domain_menu = ctk.CTkOptionMenu(self, values=["math", "english"], command=lambda _: self.on_refresh_files())
        self.domain_menu.grid(row=1, column=1, padx=20, pady=8, sticky="ew")

        ctk.CTkLabel(self, text="Exam File").grid(row=2, column=0, padx=20, pady=8, sticky="w")
        self.file_menu = ctk.CTkOptionMenu(self, values=["<no files>"])
        self.file_menu.grid(row=2, column=1, padx=20, pady=8, sticky="ew")
        ctk.CTkButton(self, text="Refresh", command=self.on_refresh_files, width=110).grid(
            row=2, column=2, padx=(0, 20), pady=8, sticky="e"
        )
        ctk.CTkButton(self, text="Browse File", command=self.on_browse_file, width=110).grid(
            row=3, column=2, padx=(0, 20), pady=8, sticky="e"
        )

        ctk.CTkLabel(self, text="Difficulty").grid(row=3, column=0, padx=20, pady=8, sticky="w")
        self.difficulty_menu = ctk.CTkOptionMenu(self, values=["easy", "medium", "hard"])
        self.difficulty_menu.grid(row=3, column=1, padx=20, pady=8, sticky="ew")

        ctk.CTkLabel(self, text="Question Count").grid(row=4, column=0, padx=20, pady=8, sticky="w")
        self.question_count_entry = ctk.CTkEntry(self, placeholder_text="5")
        self.question_count_entry.insert(0, "5")
        self.question_count_entry.grid(row=4, column=1, padx=20, pady=8, sticky="ew")

        self.load_btn = ctk.CTkButton(self, text="Load Content", command=self.on_load_content, height=42)
        self.load_btn.grid(row=5, column=0, padx=20, pady=(16, 10), sticky="ew")
        self.generate_btn = ctk.CTkButton(self, text="Generate Questions", command=self.on_generate_questions, height=42)
        self.generate_btn.grid(row=5, column=1, padx=20, pady=(16, 10), sticky="ew")
        self.start_exam_btn = ctk.CTkButton(self, text="Start Exam", command=self.on_start_exam, height=42)
        self.start_exam_btn.grid(row=5, column=2, padx=20, pady=(16, 10), sticky="ew")

    def get_form_data(self) -> dict:
        count_raw = self.question_count_entry.get().strip() or "5"
        return {
            "domain": self.domain_menu.get(),
            "exam_file": self.file_menu.get(),
            "difficulty": self.difficulty_menu.get(),
            "question_count": int(count_raw),
        }

    def update_exam_files(self, files: list[str]) -> None:
        values = files if files else ["<no files>"]
        self.file_menu.configure(values=values)
        self.file_menu.set(values[0])
