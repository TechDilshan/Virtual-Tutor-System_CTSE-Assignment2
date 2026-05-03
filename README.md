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