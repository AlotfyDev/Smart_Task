"""
Batch insertion utilities for tickets.
"""

from pathlib import Path
from typing import Any

from smart_task.models import MicroTaskTicket
from smart_task.repository import TicketRepository


def insert_tickets_batch_to_db(
    tickets: list[MicroTaskTicket],
    repo: TicketRepository,
) -> int:
    """Insert a list of tickets using batch operation."""
    if not tickets:
        return 0
    return repo.insert_tickets_batch(tickets)