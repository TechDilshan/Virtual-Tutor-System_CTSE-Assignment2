from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


class Logger:
    def __init__(self, trace_file: str = "logs/agent_trace.jsonl", verbose: bool = False) -> None:
        self.logger = logging.getLogger("virtual_tutor")
        self.logger.setLevel(logging.INFO if verbose else logging.WARNING)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        self.logger.propagate = False

        self.trace_path = Path(trace_file)
        self.trace_path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, message: str) -> None:
        self.logger.info(message)

    def error(self, message: str) -> None:
        self.logger.error(message)

    def trace(self, agent: str, step: str, payload: Dict[str, Any]) -> None:
        """
        Persist structured execution traces for observability.
        """
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": agent,
            "step": step,
            "payload": payload,
        }
        with self.trace_path.open("a", encoding="utf-8") as trace_file:
            trace_file.write(json.dumps(record, ensure_ascii=True) + "\n")