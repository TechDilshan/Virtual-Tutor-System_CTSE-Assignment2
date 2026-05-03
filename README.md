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




On the **Dashboard**, use **Run automated evaluation** (optional **LLM-as-judge**). Reports appear under **Results → Automated evaluation** (tab). **Exam results** stays on the other tab.

## Tests

From the **repository root** (recommended):

```bash
python3 run_tests.py
```

From the **`System/`** directory:

```bash
cd System
python3 -m unittest discover -s . -p 'test*.py' -v
```

Run only the automated evaluation **property-check** tests (fast, no Ollama):

```bash
cd System
python3 -m unittest tests.test_automated_evaluation_checks -v
```

## Automated agent evaluation (properties + optional LLM judge)

This script exercises the same tools as the live pipeline (content → questions → exam evaluation) and runs **property / security checks** on their outputs. It does not replace your normal `main.py` workflow.

From **`System/`**:

```bash
cd System
python3 -m evaluation.automated_agent_eval --domain math --exam-file exam1.txt --questions 3
```

Machine-readable report:

```bash
python3 -m evaluation.automated_agent_eval --domain math --exam-file exam1.txt --questions 3 --json
```

Optional **LLM-as-judge** (requires `ollama serve` and a working model; uses your existing `tools.llm_tool`):

```bash
python3 -m evaluation.automated_agent_eval --domain math --exam-file exam1.txt --questions 3 --llm-judge
```

Exit code **0** means all checks passed, **1** means at least one failed.