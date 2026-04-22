from agents.content_retrieval_agent.agent import ContentRetrievalAgent
from agents.question_generator_agent.agent import QuestionGeneratorAgent
from agents.hint_provider_agent.agent import HintProviderAgent
from agents.exam_simulation_agent.agent import ExamSimulationAgent
from framework.state_manager import StateManager
from framework.logger import Logger

class Orchestrator:
    def __init__(self):
        # Initialize agents and state manager
        self.content_agent = ContentRetrievalAgent()
        self.question_agent = QuestionGeneratorAgent()
        self.hint_agent = HintProviderAgent()
        self.exam_agent = ExamSimulationAgent()
        self.state_manager = StateManager()
        self.logger = Logger()

    def start_exam_simulation(self):
        """
        Start the full exam simulation process.
        1. Retrieve content
        2. Generate questions
        3. Provide hints if needed
        4. Simulate the exam
        """
        # Retrieve content
        content = self.content_agent.retrieve_content()
        self.logger.log("Content retrieved.")

        # Generate questions based on the retrieved content
        questions = self.question_agent.generate_questions()
        self.logger.log("Questions generated.")

        # Start the exam simulation
        results = self.exam_agent.simulate_exam(questions)
        self.logger.log("Exam simulation completed.")

        # Display results
        self.exam_agent.display_results()
        self.logger.log("Exam results displayed.")

        return results