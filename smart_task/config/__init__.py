"""
Configuration module for smart_task micro-task system.

Lowest-level dependency — no local imports from other smart_task modules.
Provides runtime configuration constants, defaults, and environment variable handling.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


VERIFICATION_PREFIXES: dict[str, str] = {
    "SHELL":  "Execute shell command and verify exit code 0",
    "PATH":   "Path to test file/directory that must exist after implementation",
    "BDD":    "Behave feature file + line number to run",
    "SMOKE":  "Smoke test script path to execute",
    "MANUAL": "Human-verified — documented in review_notes",
    "MIXED":  "Combination of multiple prefixes (separated by newlines)",
}

DEFAULT_DB_PATH: Path = Path(
    os.getenv("SMART_TASK_DB_PATH", str(Path.home() / ".smart_task" / "tasks.db"))
)


@dataclass
class SmartTaskConfig:
    """Central configuration for the smart-task system."""

    db_path: Path = field(default_factory=lambda: DEFAULT_DB_PATH)
    verification_prefixes: dict[str, str] = field(default_factory=lambda: dict(VERIFICATION_PREFIXES))
    topics_dir_name: str = "topic_based_microtasks"
    mappings_file_name: str = "topic_to_ticket_mappings.json"
    priority_order: dict[str, int] = field(default_factory=lambda: {
        "Critical": 4, "High": 3, "Medium": 2, "Low": 1,
    })

    def __post_init__(self) -> None:
        if isinstance(self.db_path, str):
            self.db_path = Path(self.db_path)


def load_config() -> SmartTaskConfig:
    """Build and return a SmartTaskConfig, reading env var overrides."""
    db_path_env = os.getenv("SMART_TASK_DB_PATH")
    config = SmartTaskConfig()
    if db_path_env:
        config.db_path = Path(db_path_env)
    return config
