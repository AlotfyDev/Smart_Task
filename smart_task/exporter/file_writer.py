"""
File output utilities for wave exports.
"""

import json
from pathlib import Path
from typing import Any

from smart_task.models import MicroTaskTicket, TaskWave
from smart_task.parser import write_artifact, serialize_ticket


def write_wave_file(output_dir: Path, wave: TaskWave, tickets: list[MicroTaskTicket]) -> Path:
    """Write a wave.json file containing wave metadata and all tickets."""
    wave_data = {
        "id": wave.id,
        "phase": wave.phase,
        "description": wave.description,
        "status": wave.status,
        "ticket_count": len(tickets),
        "tickets": [serialize_ticket(t) for t in tickets],
    }
    output_path = output_dir / f"{wave.id}.json"
    write_artifact(output_path, wave_data)
    return output_path


def write_ticket_files(
    output_dir: Path,
    tickets: list[MicroTaskTicket],
) -> list[Path]:
    """Write each ticket to its own file in output_dir."""
    paths: list[Path] = []
    for ticket in tickets:
        ticket_path = output_dir / f"{ticket.id}.json"
        ticket_data = serialize_ticket(ticket)
        write_artifact(ticket_path, ticket_data)
        paths.append(ticket_path)
    return paths