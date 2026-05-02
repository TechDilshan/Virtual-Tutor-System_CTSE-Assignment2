from __future__ import annotations

import customtkinter as ctk


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, on_navigate):
        super().__init__(master, corner_radius=0)
        self.on_navigate = on_navigate
        self.grid_rowconfigure(6, weight=1)
        self._build()

    def _build(self) -> None:
        ctk.CTkLabel(self, text="Virtual Tutor MAS", font=ctk.CTkFont(size=20, weight="bold")).grid(
            row=0, column=0, padx=16, pady=(20, 24), sticky="w"
        )
        buttons = [
            ("Dashboard", "dashboard"),
            ("Questions", "questions"),
            ("Exam", "exam"),
            ("Results", "results"),
        ]
        for row, (title, key) in enumerate(buttons, start=1):
            ctk.CTkButton(
                self,
                text=title,
                command=lambda k=key: self.on_navigate(k),
                height=40,
            ).grid(row=row, column=0, padx=16, pady=8, sticky="ew")
