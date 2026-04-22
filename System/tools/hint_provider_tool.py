def provide_hint(question, domain="math"):
    """
    Provide hints based on the student's question and domain.
    """
    hints = {
        "math": {
            "What is 2 + 2?": "Think of counting small objects like apples.",
            "Solve for x: 5x = 25": "Divide both sides of the equation by 5.",
            "What is the derivative of x^2?": "Use the power rule of differentiation."
        },
        "english": {
            "Write a summary of the text provided.": "Focus on the main ideas, avoid details.",
            "What is the theme of the novel?": "Look for the central message or lesson of the story.",
            "Explain the use of metaphors in this poem.": "Identify comparisons without using 'like' or 'as'."
        }
    }

    return hints.get(domain, {}).get(question, "No hint available.")