"""
Domain model for a task wave — a logical grouping of tickets processed as a unit.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


_VALID_PHASES = {1, 2, 3}
_VALID_WAVE_STATUSES = {"pending", "active", "completed"}


@dataclass
class TaskWave:
    """A named collection of tickets processed as a unit."""

    id: str
    phase: int = 1
    description: str = ""
    ticket_count: int = 0
    status: str = "pending"
    created_at: str = ""
    completed_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TaskWave:
        return cls(**data)

    def to_row(self) -> tuple[Any, ...]:
        d = self.to_dict()
        return (
            d["id"], d["phase"], d["description"],
            d["ticket_count"], d["status"],
            d["created_at"], d["completed_at"],
        )

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.id:
            errors.append("id is required")
        if self.phase not in _VALID_PHASES:
            errors.append(f"phase must be one of {_VALID_PHASES}, got {self.phase}")
        if self.status not in _VALID_WAVE_STATUSES:
            errors.append(f"status must be one of {_VALID_WAVE_STATUSES}, got {self.status!r}")
        return errors
