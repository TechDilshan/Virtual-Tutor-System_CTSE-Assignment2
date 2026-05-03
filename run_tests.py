#!/usr/bin/env python3
"""Discover and run all tests under System/. Invoke from the repository root."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parent
    system_dir = repo_root / "System"
    if not system_dir.is_dir():
        print("Error: System/ directory not found.", file=sys.stderr)
        return 2
    sys.path.insert(0, str(system_dir))
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=str(system_dir), pattern="test*.py", top_level_dir=str(repo_root))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
