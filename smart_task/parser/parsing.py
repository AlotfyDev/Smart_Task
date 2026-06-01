"""
Main parsing logic for JSON ticket and wave artifacts.
"""

import json
from pathlib import Path
from typing import Any

from smart_task.json_schema import validate_ticket, validate_wave
from smart_task.models import MicroTaskTicket, TaskWave


def parse_ticket_file(path: Path) -> MicroTaskTicket:
    """Read JSON file, validate, return MicroTaskTicket dataclass."""
    if not path.exists():
        raise FileNotFoundError(f"Ticket file not found: {path}")

    content = path.read_text(encoding="utf-8")
    if not content.strip():
        raise ValueError(f"Ticket file is empty: {path}")
    data = json.loads(content)

    is_valid, errors = validate_ticket(data)
    if not is_valid:
        raise ValueError("; ".join(errors))

    return MicroTaskTicket.from_dict(data)


def parse_wave_file(path: Path) -> TaskWave:
    """Read JSON file, validate, return TaskWave dataclass."""
    if not path.exists():
        raise FileNotFoundError(f"Wave file not found: {path}")

    content = path.read_text(encoding="utf-8")
    if not content.strip():
        raise ValueError(f"Wave file is empty: {path}")
    data = json.loads(content)

    is_valid, errors = validate_wave(data)
    if not is_valid:
        raise ValueError("; ".join(errors))

    return TaskWave.from_dict(data)


def serialize_ticket(ticket: MicroTaskTicket) -> dict[str, Any]:
    """Dataclass → validated dict."""
    data = ticket.to_dict()
    is_valid, errors = validate_ticket(data)
    if not is_valid:
        raise ValueError("; ".join(errors))
    return data


def serialize_wave(wave: TaskWave) -> dict[str, Any]:
    """Dataclass → validated dict."""
    data = wave.to_dict()
    is_valid, errors = validate_wave(data)
    if not is_valid:
        raise ValueError("; ".join(errors))
    return data


def write_artifact(path: Path, data: dict[str, Any]) -> None:
    """Write JSON to file (pretty-printed, utf-8)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(data, indent=2, ensure_ascii=False, sort_keys=False)
    path.write_text(content, encoding="utf-8")