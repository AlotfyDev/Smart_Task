"""
SELECT and COUNT query operations for tickets, waves, and mappings.
"""

import json
from typing import Any

from smart_task.models import MicroTaskTicket, TaskWave, TopicToTicketMapping


GET_TICKET_SQL = """
SELECT * FROM micro_task_tickets WHERE id = ?
"""

GET_WAVE_SQL = """
SELECT * FROM task_waves WHERE id = ?
"""

LIST_TICKETS_SQL = """
SELECT * FROM micro_task_tickets
WHERE (?1 IS NULL OR phase = ?1)
  AND (?2 IS NULL OR status = ?2)
  AND (?3 IS NULL OR wave_id = ?3)
ORDER BY priority DESC, created_at ASC
"""

LIST_WAVES_SQL = """
SELECT * FROM task_waves
WHERE (?1 IS NULL OR phase = ?1)
  AND (?2 IS NULL OR status = ?2)
ORDER BY created_at ASC
"""

COUNT_TICKETS_SQL = """
SELECT COUNT(*) as count FROM micro_task_tickets
WHERE (?1 IS NULL OR phase = ?1)
  AND (?2 IS NULL OR status = ?2)
  AND (?3 IS NULL OR priority = ?3)
"""


def row_to_ticket(row: Any) -> MicroTaskTicket:
    """Convert a database row to MicroTaskTicket dataclass."""
    data = dict(row)
    return MicroTaskTicket.from_dict(data)


def row_to_wave(row: Any) -> TaskWave:
    """Convert a database row to TaskWave dataclass."""
    data = dict(row)
    return TaskWave.from_dict(data)


def row_to_mapping(row: Any) -> TopicToTicketMapping:
    """Convert a database row to TopicToTicketMapping dataclass."""
    data = dict(row)
    return TopicToTicketMapping.from_dict(data)


def get_ticket(conn: Any, ticket_id: str) -> MicroTaskTicket | None:
    """Get a ticket by ID."""
    cursor = conn.execute(GET_TICKET_SQL, (ticket_id,))
    row = cursor.fetchone()
    return row_to_ticket(row) if row else None


def get_wave(conn: Any, wave_id: str) -> TaskWave | None:
    """Get a wave by ID."""
    cursor = conn.execute(GET_WAVE_SQL, (wave_id,))
    row = cursor.fetchone()
    return row_to_wave(row) if row else None


def list_tickets(
    conn: Any,
    phase: int | None = None,
    status: str | None = None,
    wave_id: str | None = None,
) -> list[MicroTaskTicket]:
    """List tickets with optional filters."""
    cursor = conn.execute(LIST_TICKETS_SQL, (phase, status, wave_id))
    return [row_to_ticket(row) for row in cursor.fetchall()]


def list_waves(
    conn: Any,
    phase: int | None = None,
    status: str | None = None,
) -> list[TaskWave]:
    """List waves with optional filters."""
    cursor = conn.execute(LIST_WAVES_SQL, (phase, status))
    return [row_to_wave(row) for row in cursor.fetchall()]


def count_tickets(conn: Any, phase: int | None = None, status: str | None = None, priority: str | None = None) -> int:
    """Count tickets matching filters."""
    cursor = conn.execute(COUNT_TICKETS_SQL, (phase, status, priority))
    row = cursor.fetchone()
    return row["count"] if row else 0


def get_ready_tickets(conn: Any, phase: int, limit: int = 10) -> list[MicroTaskTicket]:
    """
    Get tickets whose dependencies are all completed.
    Returns tickets ready for assignment to a wave.
    Uses two queries total regardless of dependency count.
    """
    all_tickets = list_tickets(conn, phase=phase, status="pending")
    if not all_tickets:
        return []

    ticket_deps: list[tuple[MicroTaskTicket, list[str]]] = []
    all_dep_ids: set[str] = set()
    for ticket in all_tickets:
        deps = json.loads(ticket.dependencies) if ticket.dependencies else []
        ticket_deps.append((ticket, deps))
        all_dep_ids.update(deps)

    if not all_dep_ids:
        ready = [t for t, _ in ticket_deps]
    else:
        placeholders = ",".join("?" for _ in all_dep_ids)
        cursor = conn.execute(
            f"SELECT id FROM micro_task_tickets WHERE id IN ({placeholders}) AND status != 'completed'",
            tuple(all_dep_ids),
        )
        non_completed = {row["id"] for row in cursor.fetchall()}

        ready = [
            t for t, deps in ticket_deps
            if not any(d in non_completed for d in deps)
        ]

    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    ready.sort(key=lambda t: priority_order.get(t.priority, 99))

    return ready[:limit]