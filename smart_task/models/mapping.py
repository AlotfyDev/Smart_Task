"""
Domain model for topic-to-ticket mapping — associates a topic file with ticket templates.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from typing import Any


_VALID_PHASES = {1, 2, 3}
_VALID_EFFORTS = {"S", "M", "L", "XL"}


@dataclass
class TopicToTicketMapping:
    """Associates a topic file specification with generated ticket templates."""

    id: int = 0
    source_topic_file: str = ""
    sequence: int = 1
    title_template: str = ""
    objective_template: str = ""
    phase: int = 1
    effort: str = "M"
    tags: str = "[]"

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        raw = d.get("tags", "[]")
        if isinstance(raw, (list, tuple)):
            d["tags"] = json.dumps(raw)
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TopicToTicketMapping:
        kwargs = dict(data)
        tags_raw = kwargs.get("tags", "[]")
        if isinstance(tags_raw, (list, tuple)):
            kwargs["tags"] = json.dumps(tags_raw)
        elif isinstance(tags_raw, str):
            try:
                json.loads(tags_raw)
            except (json.JSONDecodeError, TypeError):
                pass
        return cls(**kwargs)

    def to_row(self) -> tuple[Any, ...]:
        d = self.to_dict()
        return (
            d["id"], d["source_topic_file"], d["sequence"],
            d["title_template"], d["objective_template"],
            d["phase"], d["effort"], d["tags"],
        )

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.source_topic_file:
            errors.append("source_topic_file is required")
        if self.phase not in _VALID_PHASES:
            errors.append(f"phase must be one of {_VALID_PHASES}, got {self.phase}")
        if self.effort not in _VALID_EFFORTS:
            errors.append(f"effort must be one of {_VALID_EFFORTS}, got {self.effort!r}")
        if isinstance(self.tags, str):
            try:
                parsed = json.loads(self.tags)
                if not isinstance(parsed, list):
                    errors.append("tags must be a JSON array")
            except json.JSONDecodeError:
                errors.append(f"tags is not valid JSON: {self.tags}")
        return errors
