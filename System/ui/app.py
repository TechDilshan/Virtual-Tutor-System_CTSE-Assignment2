from __future__ import annotations

from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from components.dashboard import DashboardFrame
from components.question_list_panel import QuestionListPanel
from components.question_panel import QuestionPanel
from components.result_panel import ResultPanel
from components.sidebar import Sidebar
from controllers.app_controller import AppController


class VirtualTutorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.title("Virtual Tutor for Exam Preparation")
        self.geometry("1320x820")
        self.minsize(1180, 760)

        self.controller = AppController(log_callback=self.append_log)
        self.questions: list[dict] = []
        self.current_idx = 0
        self.timer_seconds = 0
        self.timer_after_id = None

        self._build_layout()
        self.refresh_files()
        self.show_screen("dashboard")

    def _build_layout(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        self.sidebar = Sidebar(self, self.show_screen)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")

        self.content_host = ctk.CTkFrame(self)
        self.content_host.grid(row=0, column=1, sticky="nsew")
        self.content_host.grid_rowconfigure(0, weight=1)
        self.content_host.grid_columnconfigure(0, weight=1)

        self.dashboard = DashboardFrame(
            self.content_host,
            on_refresh_files=self.refresh_files,
            on_browse_file=self.browse_exam_file,
            on_load_content=self.handle_load_content,
            on_generate_questions=self.handle_generate_questions,
            on_start_exam=self.handle_start_exam,
        )
        self.question_screen = QuestionPanel(
            self.content_host,
            on_submit=self.handle_submit_answer,
            on_get_hint=self.handle_get_hint,
            on_next=self.handle_next_question,
            on_finish=self.handle_finish_exam,
        )
        self.questions_overview = QuestionListPanel(self.content_host)
        self.result_screen = ResultPanel(self.content_host)

        self.screens = {
            "dashboard": self.dashboard,
            "questions": self.questions_overview,
            "exam": self.question_screen,
            "results": self.result_screen,
        }

        self.log_panel = ctk.CTkTextbox(self, height=140)
        self.log_panel.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="nsew")
        self.dashboard.generate_btn.configure(state="disabled")
        self.dashboard.start_exam_btn.configure(state="disabled")
        self.append_log("[System] UI ready. Select domain and exam file.")

    def append_log(self, text: str) -> None:
        self.log_panel.insert("end", f"{text}\n")
        self.log_panel.see("end")

    def show_screen(self, name: str) -> None:
        for frame in self.screens.values():
            frame.grid_forget()
        self.screens[name].grid(row=0, column=0, sticky="nsew")

    def refresh_files(self) -> None:
        domain = self.dashboard.domain_menu.get()
        files = self.controller.get_available_exam_files(domain=domain)
        self.dashboard.update_exam_files(files)
        self.append_log(f"[Content Agent] Found {len(files)} exam file(s) for {domain}")

    def browse_exam_file(self) -> None:
        chosen = filedialog.askopenfilename(
            title="Choose exam text file",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        )
        if not chosen:
            return
        self._sync_controller_config()
        try:
            filename = self.controller.attach_exam_file(chosen)
            self.refresh_files()
            self.dashboard.file_menu.set(filename)
            messagebox.showinfo("File Added", f"Exam file '{filename}' is ready for this domain.")
        except (FileNotFoundError, ValueError) as exc:
            messagebox.showerror("File Error", str(exc))

    def _sync_controller_config(self) -> None:
        try:
            form = self.dashboard.get_form_data()
            count = max(1, form["question_count"])
        except ValueError:
            raise ValueError("Question count must be a valid number.")
        exam_file = form["exam_file"]
        if exam_file == "<no files>":
            exam_file = None
        self.controller.set_config(
            domain=form["domain"],
            exam_file=exam_file,
            difficulty=form["difficulty"],
            question_count=count,
        )

    def handle_load_content(self) -> None:
        try:
            self._sync_controller_config()
            structured = self.controller.load_content()
            self.dashboard.generate_btn.configure(state="normal")
            messagebox.showinfo("Content Loaded", f"Loaded {len(structured)} structured questions.")
        except (ValueError, FileNotFoundError) as exc:
            messagebox.showerror("Load Error", str(exc))

    def handle_generate_questions(self) -> None:
        try:
            self._sync_controller_config()
            self.questions = self.controller.generate_questions()
            if not self.questions:
                raise ValueError("No generated questions available.")
            self.current_idx = 0
            self.dashboard.start_exam_btn.configure(state="normal")
            self.questions_overview.set_questions(self.questions)
            self.question_screen.set_question(self.questions[0]["question"], 1, len(self.questions))
            self.show_screen("questions")
            messagebox.showinfo("Questions Generated", f"{len(self.questions)} questions generated.")
        except ValueError as exc:
            messagebox.showerror("Generation Error", str(exc))

    def handle_start_exam(self) -> None:
        if not self.questions:
            messagebox.showwarning("Exam", "Generate questions first.")
            return
        self.show_screen("exam")
        self.current_idx = 0
        self.question_screen.set_question(self.questions[0]["question"], 1, len(self.questions))
        self.timer_seconds = max(60, len(self.questions) * 60)
        self._run_timer()
        self.append_log("[Exam Agent] Exam simulation started")

    def _run_timer(self) -> None:
        mins = self.timer_seconds // 60
        secs = self.timer_seconds % 60
        self.question_screen.set_timer(f"{mins:02d}:{secs:02d}")
        if self.timer_seconds <= 0:
            self.handle_finish_exam()
            return
        self.timer_seconds -= 1
        self.timer_after_id = self.after(1000, self._run_timer)

    def _current_question_text(self) -> str:
        if not self.questions:
            return ""
        return self.questions[self.current_idx]["question"]

    def handle_submit_answer(self) -> None:
        question = self._current_question_text()
        answer = self.question_screen.get_answer()
        try:
            self.controller.submit_answer(question, answer)
            messagebox.showinfo("Answer Saved", "Your answer was submitted.")
        except ValueError as exc:
            messagebox.showwarning("Answer Error", str(exc))

    def handle_get_hint(self) -> None:
        question = self._current_question_text()
        if not question:
            messagebox.showwarning("Hint", "No active question.")
            return
        try:
            hints = self.controller.get_hint(question)
            self.question_screen.hint_panel.set_hints(hints)
        except ValueError as exc:
            messagebox.showerror("Hint Error", str(exc))

    def handle_next_question(self) -> None:
        if not self.questions:
            return
        if self.current_idx < len(self.questions) - 1:
            self.current_idx += 1
            self.question_screen.set_question(
                self.questions[self.current_idx]["question"],
                self.current_idx + 1,
                len(self.questions),
            )
            return
        messagebox.showinfo("Exam", "You are on the last question. Click Finish Exam.")

    def handle_finish_exam(self) -> None:
        if self.timer_after_id is not None:
            self.after_cancel(self.timer_after_id)
            self.timer_after_id = None
        results = self.controller.start_exam()
        self.result_screen.set_results(results)
        self.show_screen("results")
        messagebox.showinfo("Exam Completed", "Results are ready.")


if __name__ == "__main__":
    app = VirtualTutorApp()
    app.mainloop()
