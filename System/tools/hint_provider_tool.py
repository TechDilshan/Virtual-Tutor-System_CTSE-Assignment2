from typing import Dict, List, Optional
import re
from tools.llm_tool import generate_with_ollama

def _compact_hint(text: str) -> str:
    cleaned = " ".join(text.strip().split())
    # Remove common verbose lead-ins from model outputs.
    cleaned = re.sub(r"^(here's|here is)\s+a\s+helpful\s+hint:\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^hint:\s*", "", cleaned, flags=re.IGNORECASE)
    return cleaned


def provide_hint(
    question: str,
    domain: str = "math",
    student_history: Optional[List[Dict[str, str]]] = None,
    hint_level: str = "standard",
) -> str:
    """
    Provide a domain-aware hint for a question.
    """
    hints: Dict[str, Dict[str, str]] = {
        "math": {
            "What is 2 + 2?": "Think of counting small objects like apples.",
            "Solve for x: 5x = 25": "Divide both sides of the equation by 5.",
            "Solve for x: 5x = 25.": "Divide both sides of the equation by 5.",
            "What is the derivative of x^2?": "Use the power rule of differentiation.",
            "Find the integral of 2x.": "Reverse differentiation and add the constant of integration.",
        },
        "english": {
            "Write a summary of the text provided.": "Focus on the main ideas, avoid details.",
            "What is the theme of the novel?": "Look for the central message or lesson of the story.",
            "Explain the use of metaphors in this poem.": "Identify comparisons without using 'like' or 'as'.",
        },
    }

    cleaned_question = re.sub(r"^\s*q?\d+[\).:-]?\s*", "", question, flags=re.IGNORECASE).strip()
    weakness_context = ""
    if student_history:
        recent_errors = [item for item in student_history[-5:] if item.get("result") in {"Incorrect", "Partially Correct"}]
        if recent_errors:
            weakness_context = (
                "Student recent weak areas: "
                + "; ".join(item.get("question", "")[:80] for item in recent_errors)
            )
    prompt = (
        f"Provide one {hint_level} helpful hint for this {domain} exam question. "
        "Do not give the final answer. Keep it concise and actionable.\n"
        f"{weakness_context}\n"
        f"Question: {cleaned_question}"
    )
    llm_hint = generate_with_ollama(prompt)
    if llm_hint:
        return _compact_hint(llm_hint)

    direct = hints.get(domain, {}).get(question) or hints.get(domain, {}).get(cleaned_question)
    if direct:
        return direct

    normalized = question.lower()
    if domain == "math":
        if "derivative" in normalized:
            return "Apply differentiation rules step by step and simplify the final expression."
        if "integral" in normalized:
            return "Use anti-derivative rules and remember the + C constant."
        if "solve for x" in normalized:
            return "Isolate x by applying inverse operations to both sides equally."
    return "No hint available."