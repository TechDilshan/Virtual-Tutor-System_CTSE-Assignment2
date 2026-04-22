from agents.content_retrieval_agent.agent import ContentRetrievalAgent
from agents.question_generator_agent.agent import QuestionGeneratorAgent
from agents.hint_provider_agent.agent import HintProviderAgent
from agents.exam_simulation_agent.agent import ExamSimulationAgent
from framework.state_manager import StateManager
from framework.logger import Logger
from typing import TypedDict, List, Dict

from langgraph.graph import END, START, StateGraph


class WorkflowState(TypedDict, total=False):
    content: List[str]
    questions: List[str]
    hints: Dict[str, str]
    results: Dict[str, Dict[str, str]]

class Orchestrator:
    def __init__(
        self,
        domain: str = "math",
        question_count: int = 3,
        verbose: bool = False,
        exam_file: str | None = None,
    ):
        self.domain = domain
        self.question_count = question_count
        self.content_agent = ContentRetrievalAgent(domain=domain, exam_file=exam_file)
        self.question_agent = QuestionGeneratorAgent(domain=domain)
        self.hint_agent = HintProviderAgent(domain=domain)
        self.exam_agent = ExamSimulationAgent()
        self.state_manager = StateManager()
        self.logger = Logger(verbose=verbose)
        self.workflow_graph = self._build_graph()

    def _build_graph(self):
        graph_builder = StateGraph(WorkflowState)
        graph_builder.add_node("content_retrieval", self._content_node)
        graph_builder.add_node("question_generation", self._question_node)
        graph_builder.add_node("hint_provider", self._hint_node)
        graph_builder.add_node("exam_simulation", self._exam_node)

        graph_builder.add_edge(START, "content_retrieval")
        graph_builder.add_edge("content_retrieval", "question_generation")
        graph_builder.add_edge("question_generation", "hint_provider")
        graph_builder.add_edge("hint_provider", "exam_simulation")
        graph_builder.add_edge("exam_simulation", END)

        return graph_builder.compile()

    def _content_node(self, state: WorkflowState) -> WorkflowState:
        content = self.run_content_retrieval()
        return {"content": content}

    def _question_node(self, state: WorkflowState) -> WorkflowState:
        content = state.get("content")
        if content is not None:
            self.state_manager.update_state("content", content)
        questions = self.run_question_generation()
        return {"questions": questions}

    def _hint_node(self, state: WorkflowState) -> WorkflowState:
        questions = state.get("questions")
        if questions is not None:
            self.state_manager.update_state("questions", questions)
        hints = self.run_hint_provider()
        return {"hints": hints}

    def _exam_node(self, state: WorkflowState) -> WorkflowState:
        questions = state.get("questions")
        if questions is not None:
            self.state_manager.update_state("questions", questions)
        results = self.run_exam_simulation()
        return {"results": results}

    def run_content_retrieval(self):
        content = self.content_agent.retrieve_content()
        self.state_manager.update_state("content", content)
        self.logger.trace("ContentRetrievalAgent", "retrieve_content", {"content_count": len(content)})
        return content

    def run_question_generation(self):
        content = self.state_manager.get_state("content")
        if content is None:
            content = self.run_content_retrieval()
        questions = self.question_agent.generate_questions(content=content, count=self.question_count)
        self.state_manager.update_state("questions", questions)
        self.logger.trace("QuestionGeneratorAgent", "generate_questions", {"question_count": len(questions)})
        return questions

    def run_hint_provider(self):
        questions = self.state_manager.get_state("questions")
        if questions is None:
            questions = self.run_question_generation()
        hints = {question: self.hint_agent.provide_hint(question) for question in questions}
        self.state_manager.update_state("hints", hints)
        self.logger.trace("HintProviderAgent", "provide_hints", {"hint_count": len(hints)})
        return hints

    def run_exam_simulation(self):
        questions = self.state_manager.get_state("questions")
        if questions is None:
            questions = self.run_question_generation()
        results = self.exam_agent.simulate_exam(questions=questions, duration=30, seed=42)
        self.state_manager.update_state("results", results)
        self.logger.trace("ExamSimulationAgent", "simulate_exam", {"results_count": len(results)})
        return results

    def start_exam_simulation(self):
        """
        Execute full end-to-end multi-agent flow via LangGraph.
        """
        self.logger.log(f"Starting orchestration for domain={self.domain}")
        final_state = self.workflow_graph.invoke({})

        content = final_state.get("content", self.state_manager.get_state("content") or [])
        questions = final_state.get("questions", self.state_manager.get_state("questions") or [])
        hints = final_state.get("hints", self.state_manager.get_state("hints") or {})
        results = final_state.get("results", self.state_manager.get_state("results") or {})

        self.display_workflow_report(content=content, questions=questions, hints=hints, results=results)
        self.logger.log("Exam results displayed.")

        return results

    @staticmethod
    def display_workflow_report(content, questions, hints, results):
        print("\n=== Virtual Tutor Multi-Agent Report ===")
        print(f"Content Retrieval Agent: loaded {len(content)} content file(s)")
        print(f"Question Generator Agent: generated {len(questions)} question(s)")
        print(f"Hint Provider Agent: produced {len(hints)} hint(s)")
        print(f"Exam Simulation Agent: simulated {len(results)} answer result(s)\n")

        print("Questions + Hints + Result:")
        for index, question in enumerate(questions, start=1):
            hint = hints.get(question, "No hint available.")
            result_info = results.get(question, {})
            status = result_info.get("status", "N/A") if isinstance(result_info, dict) else str(result_info)
            expected = result_info.get("expected_answer", "Not available") if isinstance(result_info, dict) else "Not available"
            student = result_info.get("student_answer", "Not available") if isinstance(result_info, dict) else "Not available"
            print(f"{index}. Q: {question}")
            print(f"   Hint: {hint}")
            print(f"   Expected: {expected}")
            print(f"   Student: {student}")
            print(f"   Result: {status}")
        print("========================================\n")