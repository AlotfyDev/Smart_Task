"""
JSON export formatting for waves and tickets.
"""

import json
from typing import Any

from smart_task.models import MicroTaskTicket, TaskWave


def format_ticket_json(ticket: MicroTaskTicket) -> dict[str, Any]:
    """Format a single ticket as JSON dict."""
    return ticket.to_dict()


def format_wave_json(
    tickets: list[MicroTaskTicket],
    wave: TaskWave,
) -> str:
    """
    Build JSON structure for wave export.

    Returns:
        JSON string with wave metadata and tickets array.
    """
    return json.dumps({
        "wave": {
            "id": wave.id,
            "phase": wave.phase,
            "description": wave.description,
            "status": wave.status,
            "ticket_count": len(tickets),
        },
        "tickets": [format_ticket_json(t) for t in tickets],
    }, indent=2, ensure_ascii=False)