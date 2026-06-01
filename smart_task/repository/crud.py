"""
CRUD operations for tickets, waves, and mappings.
"""

from datetime import datetime
from typing import Any

from smart_task.models import MicroTaskTicket, TaskWave, TopicToTicketMapping

VALID_TICKET_STATUSES = frozenset({"pending", "in_progress", "completed", "blocked", "cancelled"})
VALID_WAVE_STATUSES = frozenset({"pending", "active", "completed"})


INSERT_TICKET_SQL = """
INSERT OR REPLACE INTO micro_task_tickets (
    id, source_spec, source_topic_file, source_line_range, topic_sequence,
    title, objective, spec_context, dependencies, file_targets,
    acceptance_criteria, verification_method, review_notes, blocker_reason,
    phase, priority, estimated_effort, tags, assignee, wave_id,
    status, created_at, updated_at, completed_at
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

INSERT_WAVE_SQL = """
INSERT OR IGNORE INTO task_waves (
    id, phase, description, ticket_count, status, created_at, completed_at
) VALUES (?, ?, ?, ?, ?, ?, ?)
"""

INSERT_MAPPING_SQL = """
INSERT OR IGNORE INTO topic_to_ticket_mapping (
    source_topic_file, sequence, title_template, objective_template, phase, effort, tags
) VALUES (?, ?, ?, ?, ?, ?, ?)
"""

UPDATE_TICKET_WAVE_SQL = """
UPDATE micro_task_tickets SET wave_id = ? WHERE id = ?
"""

UPDATE_STATUS_SQL = """
UPDATE micro_task_tickets
SET status = ?, review_notes = ?, blocker_reason = ?, updated_at = ?, completed_at = ?
WHERE id = ?
"""

UPDATE_WAVE_STATUS_SQL = """
UPDATE task_waves
SET status = ?, completed_at = ?
WHERE id = ?
"""

DELETE_TICKET_SQL = """
DELETE FROM micro_task_tickets WHERE id = ?
"""


def insert_ticket(conn: Any, ticket: MicroTaskTicket) -> None:
    """Insert a single ticket into the database."""
    row = ticket.to_row()
    conn.execute(INSERT_TICKET_SQL, row)
    conn.commit()


def insert_tickets_batch(conn: Any, tickets: list[MicroTaskTicket]) -> int:
    """Batch insert tickets in a transaction, returns count."""
    if not tickets:
        return 0

    rows = [t.to_row() for t in tickets]
    conn.executemany(INSERT_TICKET_SQL, rows)
    conn.commit()
    return len(rows)


def insert_wave(conn: Any, wave: TaskWave) -> None:
    """Insert a wave into the database."""
    row = wave.to_row()
    conn.execute(INSERT_WAVE_SQL, row)
    conn.commit()


def insert_mapping(conn: Any, mapping: TopicToTicketMapping) -> None:
    """Insert a mapping into the database."""
    row = mapping.to_row()
    conn.execute(INSERT_MAPPING_SQL, row)
    conn.commit()


def update_ticket_wave(conn: Any, ticket_id: str, wave_id: str) -> None:
    """Update ticket's wave assignment."""
    conn.execute(UPDATE_TICKET_WAVE_SQL, (wave_id, ticket_id))
    conn.commit()


def update_ticket_status(
    conn: Any,
    ticket_id: str,
    status: str,
    review_notes: str | None = None,
    blocker_reason: str | None = None,
) -> int:
    """Update ticket status and optional fields. Returns rowcount (0 if not found)."""
    now = datetime.utcnow().isoformat()
    completed_at = now if status == "completed" else None
    cursor = conn.execute(
        UPDATE_STATUS_SQL,
        (status, review_notes, blocker_reason, now, completed_at, ticket_id),
    )
    conn.commit()
    return cursor.rowcount


def update_wave_status(conn: Any, wave_id: str, status: str) -> None:
    """Update wave status."""
    completed_at = datetime.utcnow().isoformat() if status == "completed" else None
    conn.execute(UPDATE_WAVE_STATUS_SQL, (status, completed_at, wave_id))
    conn.commit()


def delete_ticket(conn: Any, ticket_id: str) -> bool:
    """Delete a ticket by ID, returns True if deleted."""
    cursor = conn.execute(DELETE_TICKET_SQL, (ticket_id,))
    conn.commit()
    return cursor.rowcount > 0