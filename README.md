# Virtual-Tutor-System_CTSE-Assignment2

This MAS now uses a CrewAI-style sequential pipeline with 4 distinct agents:

1. Content Retrieval Agent
2. Question Generator Agent
3. Exam Simulation Agent
4. Hint Provider Agent (runs when weak topics are detected)

Pipeline: `Content -> Question -> Exam -> Hint (conditional)`

Run from `System/` directory:

1) Content Retrieval Agent
python main.py --domain math --mode content_retrieval_agent --exam-file exam1.txt
2) Question Generator Agent
python main.py --domain math --mode question_generator_agent --questions 5 --exam-file exam1.txt
3) Hint Provider Agent
python main.py --domain math --mode hint_provider_agent --questions 5 --exam-file exam1.txt
4) Exam Simulation Agent
python main.py --domain math --mode exam_simulation_agent --questions 5 --exam-file exam1.txt
5) Full CrewAI orchestration
python main.py --domain math --mode full --questions 5 --exam-file exam1.txt

Desktop UI (CustomTkinter):
python ui/app.py

## Tests

From repo root:
python3 -m unittest discover -s System -p "test*.py"

If you are already inside the `System/` folder:
python3 -m unittest discover -s . -p "test*.py"

Run tests from anywhere (recommended):
python3 run_tests.py

## Automated Evaluation (accuracy + security properties)

Property-based style checks + optional "LLM-as-a-Judge" (Ollama):

python3 -m System.evaluation.run_agent_eval --domain math --exam-file exam1.txt --count 5
python3 -m System.evaluation.run_agent_eval --domain science --exam-file sci1.txt --count 5

Enable Ollama judge (skips automatically if Ollama not running/model missing):
python3 -m System.evaluation.run_agent_eval --domain science --exam-file sci1.txt --count 5 --llm-judge