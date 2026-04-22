from __future__ import annotations

from copy import deepcopy
from threading import Lock
from typing import Any, Dict, Optional


class StateManager:
    def __init__(self) -> None:
        self._lock = Lock()
        self.global_state: Dict[str, Any] = {}

    def update_state(self, key: str, value: Any) -> None:
        """
        Update a value in the shared global state.
        """
        with self._lock:
            self.global_state[key] = value

    def get_state(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the shared global state.
        """
        with self._lock:
            return self.global_state.get(key)

    def snapshot(self) -> Dict[str, Any]:
        """
        Return a deep copy of the current global state.
        """
        with self._lock:
            return deepcopy(self.global_state)

    def clear_state(self) -> None:
        """
        Clear all global state data.
        """
        with self._lock:
            self.global_state = {}