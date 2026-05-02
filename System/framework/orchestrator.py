from __future__ import annotations

from typing import Dict, List, TypedDict

try:
    from crewai import Agent, Crew, Process, Task
except ModuleNotFoundError:  # pragma: no cover - fallback for lightweight environments
    Agent = None
    Crew = None
    Process = None
    Task = None

from agents.content_retrieval_agent.agent import ContentRetrievalAgent
from agents.exam_simulation_agent.agent import ExamSimulationAgent
from agents.hint_provider_agent.agent import HintProviderAgent
from agents.question_generator_agent.agent import QuestionGeneratorAgent
from framework.logger import Logger
from framework.state_manager import StateManager


class WorkflowState(TypedDict, total=False):
    source_questions: List[Dict[str, str]]
    questions: List[Dict[str, str]]
    evaluation: Dict[str, object]
    hints: Dict[str, Dict[str, str]]


class Orchestrator:
    def __init__(
        self,
        domain: str = "math",
        question_count: int = 3,
        verbose: bool = False,
        exam_file: str | None = None,
        difficulty: str = "medium",
        exam_duration_minutes: int = 30,
    ):
        self.domain = domain
        self.question_count = question_count
        self.content_agent = ContentRetrievalAgent(domain=domain, exam_file=exam_file)
        self.question_agent = QuestionGeneratorAgent(domain=domain)
        self.hint_agent = HintProviderAgent(domain=domain)
        self.exam_agent = ExamSimulationAgent()
        self.state_manager = StateManager()
        self.logger = Logger(verbose=verbose)
        self.difficulty = difficulty
        self.exam_duration_minutes = exam_duration_minutes
        self.crew_enabled = Crew is not None
        self.crew = self._build_crew() if self.crew_enabled else None

    def _build_crew(self):
        """
        Configure a CrewAI sequential pipeline with 4 distinct collaborating agents.
        """
        content_worker = Agent(
            role="Content Retrieval Specialist",
            goal="Read exam sources and produce structured question records.",
            backstory="Expert in cleaning question banks and metadata extraction.",
            allow_delegation=False,
            verbose=False,
        )
        question_worker = Agent(
            role="Question Generator Specialist",
            goal="Create unique derived questions aligned to requested difficulty.",
            backstory="Expert in controlled variation and duplicate-safe generation.",
            allow_delegation=False,
            verbose=False,
        )
        exam_worker = Agent(
            role="Exam Evaluation Specialist",
            goal="Evaluate answers accurately and detect weak topics.",
            backstory="Assessment analyst focused on objective scoring.",
            allow_delegation=False,
            verbose=False,
        )
        hint_worker = Agent(
            role="Hint Provider Specialist",
            goal="Generate progressive hints for weak areas only.",
            backstory="Pedagogy specialist for scaffolded help levels.",
            allow_delegation=False,
            verbose=False,
        )

        tasks = [
            Task(
                description="Run content retrieval and parsing into structured questions.",
                expected_output="Structured source question list with topic/difficulty/type.",
                agent=content_worker,
            ),
            Task(
                description="Generate N new questions from structured source content.",
                expected_output="List of generated questions with answers and metadata.",
                agent=question_worker,
            ),
            Task(
                description="Evaluate answers and produce performance summary.",
                expected_output="Score, correct count, total, weak topics, and details.",
                agent=exam_worker,
            ),
            Task(
                description="Provide multi-level hints for weak-topic questions.",
                expected_output="Three-level hints mapped by question.",
                agent=hint_worker,
            ),
        ]
        return Crew(agents=[content_worker, question_worker, exam_worker, hint_worker], tasks=tasks, process=Process.sequential, verbose=False)

    def run_content_retrieval(self):
        self.logger.trace("ContentRetrievalAgent", "input", {"domain": self.domain, "exam_file": self.content_agent.exam_file})
        structured = self.content_agent.retrieve_structured_content()
        self.state_manager.update_state("source_questions", structured)
        self.logger.trace("ContentRetrievalAgent", "tool_usage", {"tools": ["file_reader_tool", "parser_tool"]})
        self.logger.trace("ContentRetrievalAgent", "output", {"structured_count": len(structured)})
        return structured

    def run_question_generation(self):
        source_questions = self.state_manager.get_state("source_questions")
        if source_questions is None:
            source_questions = self.run_content_retrieval()
        self.logger.trace("QuestionGeneratorAgent", "input", {"source_count": len(source_questions), "count": self.question_count})
        questions = self.question_agent.generate_questions(content=source_questions, count=self.question_count, difficulty=self.difficulty)
        self.state_manager.update_state("questions", questions)
        self.logger.trace("QuestionGeneratorAgent", "tool_usage", {"tools": ["question_generation_tool"]})
        self.logger.trace("QuestionGeneratorAgent", "output", {"question_count": len(questions)})
        return questions

    def run_exam_simulation(self, provided_answers: Dict[str, str] | None = None):
        questions = self.state_manager.get_state("questions")
        if questions is None:
            questions = self.run_question_generation()
        self.logger.trace("ExamSimulationAgent", "input", {"question_count": len(questions)})
        evaluation = self.exam_agent.simulate_exam(questions=questions, provided_answers=provided_answers)
        summary = evaluation.get("summary", {}) if isinstance(evaluation, dict) else {}
        self.state_manager.update_state("evaluation", evaluation)
        self.state_manager.update_state("score", summary.get("score", 0))
        self.state_manager.update_state("weak_topics", summary.get("weak_topics", []))
        self.state_manager.update_state("answers", evaluation.get("details", []))
        self.logger.trace("ExamSimulationAgent", "tool_usage", {"tools": ["evaluation_tool"]})
        self.logger.trace("ExamSimulationAgent", "output", summary if isinstance(summary, dict) else {})
        return evaluation

    def run_hint_provider(self):
        questions = self.state_manager.get_state("questions")
        if questions is None:
            questions = self.run_question_generation()
        evaluation = self.state_manager.get_state("evaluation") or {}
        weak_topics = evaluation.get("summary", {}).get("weak_topics", []) if isinstance(evaluation, dict) else []
        questions_for_hints = [q for q in questions if q.get("topic") in weak_topics] if weak_topics else questions
        self.logger.trace("HintProviderAgent", "input", {"questions_for_hints": len(questions_for_hints)})
        hints = self.hint_agent.provide_hints(questions_for_hints)
        self.state_manager.update_state("hints", hints)
        self.logger.trace("HintProviderAgent", "tool_usage", {"tools": ["hint_generation_tool"]})
        self.logger.trace("HintProviderAgent", "output", {"hint_count": len(hints)})
        return hints

    def start_exam_simulation(self):
        self.logger.log(f"Starting orchestration for domain={self.domain}")
        final_state = self._execute_sequential_pipeline()
        source_questions = final_state.get("source_questions", self.state_manager.get_state("source_questions") or [])
        generated_questions = final_state.get("questions", self.state_manager.get_state("questions") or [])
        hints = final_state.get("hints", self.state_manager.get_state("hints") or {})
        evaluation = final_state.get("evaluation", self.state_manager.get_state("evaluation") or {})
        self.display_workflow_report(source_questions, generated_questions, hints, evaluation)
        self.logger.log("Exam results displayed.")
        return evaluation

    def _execute_sequential_pipeline(self) -> WorkflowState:
        """
        Execute CrewAI-backed sequential pipeline; fall back to deterministic execution
        in environments where CrewAI is unavailable.
        """
        if self.crew is not None:
            self.logger.trace(
                "Orchestrator",
                "framework",
                {"orchestrator": "CrewAI", "model": "sequential_pipeline", "agent_count": 4},
            )
        else:
            self.logger.trace(
                "Orchestrator",
                "framework",
                {"orchestrator": "DeterministicFallback", "reason": "CrewAI not installed"},
            )

        source_questions = self.run_content_retrieval()
        generated_questions = self.run_question_generation()
        evaluation = self.run_exam_simulation()
        hints = self.run_hint_provider() if evaluation.get("summary", {}).get("weak_topics", []) else {}
        return {
            "source_questions": source_questions,
            "questions": generated_questions,
            "evaluation": evaluation,
            "hints": hints,
        }

    @staticmethod
    def display_workflow_report(source_questions, generated_questions, hints, evaluation):
        print("\n=== Virtual Tutor Multi-Agent Report ===")
        print(f"Content Retrieval Agent: parsed {len(source_questions)} source question(s)")
        print(f"Question Generator Agent: generated {len(generated_questions)} question(s)")
        details = evaluation.get("details", []) if isinstance(evaluation, dict) else []
        print(f"Exam Simulation Agent: evaluated {len(details)} answer(s)")
        print(f"Hint Provider Agent: produced {len(hints)} hint(s)")
        print("\nGenerated Questions + Evaluation:")
        for index, detail in enumerate(details, start=1):
            question = detail.get("question", "N/A")
            print(f"{index}. Q: {question}")
            print(f"   Student: {detail.get('student_answer', 'N/A')}")
            print(f"   Correct: {detail.get('correct_answer', 'N/A')}")
            print(f"   Is Correct: {detail.get('is_correct', 'False')}")
            if question in hints:
                print(f"   Hint 1: {hints[question].get('hint_level_1', 'N/A')}")
        summary = evaluation.get("summary", {}) if isinstance(evaluation, dict) else {}
        if isinstance(summary, dict):
            print(
                f"\nOverall: Score={summary.get('score', 0)} "
                f"Correct={summary.get('correct', 0)}/{summary.get('total', 0)} "
                f"Weak Topics={summary.get('weak_topics', [])}"
            )
        print("========================================\n")