import random
import time

def simulate_exam(questions, duration=30):
    """
    Simulate an exam by timing the student and providing random answers.
    """
    print(f"Simulating exam for {duration} minutes...")
    time.sleep(duration)  # Simulate time taken for the exam
    results = {question: random.choice(['Correct', 'Incorrect']) for question in questions}
    return results