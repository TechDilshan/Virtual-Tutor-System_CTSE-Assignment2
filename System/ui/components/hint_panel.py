from __future__ import annotations

import customtkinter as ctk


class HintPanel(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self, text="Hints", font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, padx=14, pady=(14, 8), sticky="w"
        )
        self.level_1 = ctk.CTkLabel(self, text="Level 1: -", justify="left", wraplength=320)
        self.level_2 = ctk.CTkLabel(self, text="Level 2: -", justify="left", wraplength=320)
        self.level_3 = ctk.CTkLabel(self, text="Level 3: -", justify="left", wraplength=320)
        self.level_1.grid(row=1, column=0, padx=14, pady=6, sticky="w")
        self.level_2.grid(row=2, column=0, padx=14, pady=6, sticky="w")
        self.level_3.grid(row=3, column=0, padx=14, pady=6, sticky="w")

    def set_hints(self, hints: dict[str, str]) -> None:
        self.level_1.configure(text=f"Level 1: {hints.get('hint_level_1', '-')}")
        self.level_2.configure(text=f"Level 2: {hints.get('hint_level_2', '-')}")
        self.level_3.configure(text=f"Level 3: {hints.get('hint_level_3', '-')}")
