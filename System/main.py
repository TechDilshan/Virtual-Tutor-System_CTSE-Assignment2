import argparse

from framework.orchestrator import Orchestrator


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Virtual Tutor Multi-Agent System")
    parser.add_argument("--domain", default="math", help="Subject domain, e.g. math")
    parser.add_argument("--questions", type=int, default=3, help="Number of questions to generate")
    parser.add_argument(
        "--difficulty",
        default="medium",
        choices=["easy", "medium", "hard"],
        help="Difficulty level for generated questions",
    )
    parser.add_argument("--duration", type=int, default=30, help="Mock exam duration in minutes")
    parser.add_argument(
        "--exam-file",
        default=None,
        help="Optional single exam file inside domain folder, e.g. exam1.txt",
    )
    parser.add_argument(
        "--mode",
        default="full",
        choices=[
            "full",
            "content",
            "questions",
            "hints",
            "exam",
            "content_retrieval_agent",
            "question_generator_agent",
            "hint_provider_agent",
            "exam_simulation_agent",
        ],
        help="Run full workflow or a single agent function",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable INFO console logs")
    args = parser.parse_args()

    orchestrator = Orchestrator(
        domain=args.domain,
        question_count=args.questions,
        verbose=args.verbose,
        exam_file=args.exam_file,
        difficulty=args.difficulty,
        exam_duration_minutes=args.duration,
    )

    mode = args.mode
    if mode == "content_retrieval_agent":
        mode = "content"
    elif mode == "question_generator_agent":
        mode = "questions"
    elif mode == "hint_provider_agent":
        mode = "hints"
    elif mode == "exam_simulation_agent":
        mode = "exam"

    if mode == "content":
        items = orchestrator.run_content_retrieval()
        print(f"Content Retrieval Agent Output ({len(items)} structured question(s)):")
        for idx, item in enumerate(items, start=1):
            print(f"{idx}. {item}")
    elif mode == "questions":
        questions = orchestrator.run_question_generation()
        print("Question Generator Agent Output:")
        for idx, question in enumerate(questions, start=1):
            print(f"{idx}. {question}")
    elif mode == "hints":
        hints = orchestrator.run_hint_provider()
        print("Hint Provider Agent Output:")
        for idx, (question, hint) in enumerate(hints.items(), start=1):
            print(f"{idx}. Q: {question}")
            print(f"   Hint: {hint.get('hint_level_1')}")
    elif mode == "exam":
        results = orchestrator.run_exam_simulation()
        print("Exam Simulation Agent Output:")
        for idx, detail in enumerate(results.get("details", []), start=1):
            print(f"{idx}. Q: {detail.get('question')}")
            print(f"   Student: {detail.get('student_answer')}")
            print(f"   Correct: {detail.get('correct_answer')}")
            print(f"   Correct?: {detail.get('is_correct')}")
        summary = results.get("summary")
        if isinstance(summary, dict):
            print(f"\nOverall: Score={summary.get('score', 0)} Correct={summary.get('correct', 0)}/{summary.get('total', 0)}")
    else:
        orchestrator.start_exam_simulation()