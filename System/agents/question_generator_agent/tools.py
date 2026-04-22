import random

def generate_question(domain):
    """
    Generate new exam questions based on the domain (mock).
    """
    sample_questions = {
        "math": [
            "What is 2 + 2?",
            "Solve for x: 5x = 25",
            "What is the derivative of x^2?"
        ],
        "english": [
            "Write a summary of the text provided.",
            "What is the theme of the novel?",
            "Explain the use of metaphors in this poem."
        ]
    }

    if domain not in sample_questions:
        print(f"No questions available for {domain}.")
        return []

    return random.sample(sample_questions[domain], 3)