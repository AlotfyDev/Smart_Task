"""
Domain model for a single micro-task ticket with JSON serialisation and validation.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from typing import Any


_TICKET_ID_PATTERN = re.compile(r"^TASK-[A-Z]{2,4}-\d{3}$")
_VERIFICATION_PATTERN = re.compile(r"^(SHELL|PATH|BDD|SMOKE|MANUAL|MIXED):")
_VALID_PHASES = {1, 2, 3}
_VALID_PRIORITIES = {"High", "Medium", "Low"}
_VALID_EFFORTS = {"S", "M", "L", "XL"}
_VALID_TICKET_STATUSES = {"pending", "in_progress", "completed", "blocked", "cancelled"}

_LIST_FIELDS = {"dependencies", "tags", "acceptance_criteria", "file_targets"}


def _json_list(value: Any) -> str:
    if not value:
        return "[]"
    if isinstance(value, str):
        try:
            json.loads(value)
            return value
        except (json.JSONDecodeError, TypeError):
            return json.dumps([value])
    return json.dumps(value if isinstance(value, list) else [])


@dataclass
class MicroTaskTicket:
    """A single micro-task ticket produced from a specification topic."""

    id: str
    source_spec: str = ""
    source_topic_file: str = ""
    source_line_range: str = ""
    topic_sequence: int = 1
    title: str = ""
    objective: str = ""
    spec_context: str = ""
    dependencies: str = "[]"
    file_targets: str = "[]"
    acceptance_criteria: str = "[]"
    verification_method: str = ""
    review_notes: str | None = None
    blocker_reason: str | None = None
    phase: int = 1
    priority: str = "Medium"
    estimated_effort: str = "M"
    tags: str = "[]"
    assignee: str | None = None
    wave_id: str | None = None
    status: str = "pending"
    created_at: str = ""
    updated_at: str = ""
    completed_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        for field_name in _LIST_FIELDS:
            if field_name in d:
                raw = d[field_name]
                if isinstance(raw, (list, tuple)):
                    d[field_name] = json.dumps(raw)
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MicroTaskTicket:
        kwargs = dict(data)
        for field_name in _LIST_FIELDS:
            if field_name in kwargs:
                kwargs[field_name] = _json_list(kwargs[field_name])
        return cls(**kwargs)

    def to_row(self) -> tuple[Any, ...]:
        d = self.to_dict()
        return (
            d["id"], d["source_spec"], d["source_topic_file"],
            d["source_line_range"], d["topic_sequence"],
            d["title"], d["objective"], d["spec_context"],
            d["dependencies"], d["file_targets"],
            d["acceptance_criteria"], d["verification_method"],
            d["review_notes"], d["blocker_reason"],
            d["phase"], d["priority"], d["estimated_effort"],
            d["tags"], d["assignee"], d["wave_id"],
            d["status"], d["created_at"], d["updated_at"], d["completed_at"],
        )

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.id or not _TICKET_ID_PATTERN.match(self.id):
            errors.append(
                f"id must match pattern TASK-XX-000, got {self.id!r}"
            )
        if not self.title:
            errors.append("title is required")
        if not self.objective:
            errors.append("objective is required")
        if self.phase not in _VALID_PHASES:
            errors.append(f"phase must be one of {_VALID_PHASES}, got {self.phase}")
        if self.priority not in _VALID_PRIORITIES:
            errors.append(f"priority must be one of {_VALID_PRIORITIES}, got {self.priority!r}")
        if self.estimated_effort not in _VALID_EFFORTS:
            errors.append(f"estimated_effort must be one of {_VALID_EFFORTS}, got {self.estimated_effort!r}")
        if self.status not in _VALID_TICKET_STATUSES:
            errors.append(f"status must be one of {_VALID_TICKET_STATUSES}, got {self.status!r}")
        if self.verification_method and not _VERIFICATION_PATTERN.match(self.verification_method):
            errors.append(
                f"verification_method must match pattern SHELL|PATH|BDD|SMOKE|MANUAL|MIXED:, got {self.verification_method!r}"
            )
        for fname in _LIST_FIELDS:
            raw = getattr(self, fname)
            if isinstance(raw, str):
                try:
                    parsed = json.loads(raw)
                    if not isinstance(parsed, list):
                        errors.append(f"{fname} must be a JSON array, got {type(parsed).__name__}")
                except json.JSONDecodeError:
                    errors.append(f"{fname} is not valid JSON: {raw}")
        if isinstance(self.dependencies, str):
            try:
                deps = json.loads(self.dependencies)
                if isinstance(deps, list):
                    for dep_id in deps:
                        if not _TICKET_ID_PATTERN.match(str(dep_id)):
                            errors.append(f"dependency {dep_id!r} does not match ticket ID pattern")
            except json.JSONDecodeError:
                pass
        return errors
