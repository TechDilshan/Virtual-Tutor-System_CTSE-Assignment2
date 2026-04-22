import time
from .tools import simulate_exam

class ExamSimulationAgent:
    def __init__(self):
        self.results = {}

    def simulate_exam(self, questions, duration=30):
        """
        Simulate an exam with the given questions and time limit.
        """
        print(f"Starting the exam with {len(questions)} questions for {duration} minutes...")
        self.results = simulate_exam(questions, duration)
        return self.results

    def display_results(self):
        """
        Display the results of the simulated exam.
        """
        if not self.results:
            print("No exam results to display.")
        else:
            print(f"Exam Results: {self.results}")