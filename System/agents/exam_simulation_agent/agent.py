from .tools import simulate_exam

class ExamSimulationAgent:
    def __init__(self):
        self.results = {}

    def simulate_exam(self, questions, duration=30, seed=None):
        """
        Simulate an exam with the given questions and time limit.
        """
        self.results = simulate_exam(questions=questions, duration=duration, seed=seed)
        return self.results

    def display_results(self):
        """
        Display the results of the simulated exam.
        """
        if not self.results:
            print("No exam results to display.")
        else:
            print(f"Exam Results: {self.results}")