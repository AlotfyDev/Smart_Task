"""
SQLite-backed persistence layer for tickets, waves, and topic mappings.

Exports
-------
- TicketRepository : full CRUD + query operations on the task database
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from smart_task.models import MicroTaskTicket, TaskWave, TopicToTicketMapping
from smart_task.repository.connection import init_database
from smart_task.schema import ensure_schema
from smart_task.repository.crud import (
    insert_ticket,
    insert_tickets_batch,
    insert_wave,
    insert_mapping,
    update_ticket_status,
    update_ticket_wave,
    update_wave_status,
    delete_ticket,
)
from smart_task.repository.queries import (
    get_ticket,
    get_wave,
    list_tickets,
    list_waves,
    get_ready_tickets,
    count_tickets,
)


class TicketRepository:
    """
    Repository that wraps an SQLite connection and provides typed
    read/write access to all smart-task tables.
    """

    def __init__(self, db_path: Path, auto_create: bool = True) -> None:
        self._db_path = db_path
        self._connection: Any = None
        if auto_create:
            conn = init_database(db_path)
            conn.close()

    def __enter__(self) -> "TicketRepository":
        self._connection = init_database(self._db_path)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self._connection:
            self._connection.close()
            self._connection = None

    def _conn(self) -> Any:
        if self._connection is None:
            self._connection = init_database(self._db_path)
        return self._connection

    def ensure_schema(self) -> None:
        """Ensure schema exists."""
        conn = init_database(self._db_path)
        ensure_schema(conn)
        conn.close()

    def insert_ticket(self, ticket: MicroTaskTicket) -> None:
        """INSERT INTO micro_task_tickets."""
        insert_ticket(self._conn(), ticket)

    def insert_tickets_batch(self, tickets: list[MicroTaskTicket]) -> int:
        """Batch insert in transaction, returns count."""
        return insert_tickets_batch(self._conn(), tickets)

    def insert_wave(self, wave: TaskWave) -> None:
        """INSERT INTO task_waves."""
        insert_wave(self._conn(), wave)

    def insert_mapping(self, mapping: TopicToTicketMapping) -> None:
        """INSERT INTO topic_to_ticket_mapping."""
        insert_mapping(self._conn(), mapping)

    def get_ticket(self, ticket_id: str) -> MicroTaskTicket | None:
        """SELECT by id."""
        return get_ticket(self._conn(), ticket_id)

    def get_wave(self, wave_id: str) -> TaskWave | None:
        """SELECT by id."""
        return get_wave(self._conn(), wave_id)

    def list_tickets(
        self,
        phase: int | None = None,
        status: str | None = None,
        wave_id: str | None = None,
    ) -> list[MicroTaskTicket]:
        """Filtered query."""
        return list_tickets(self._conn(), phase, status, wave_id)

    def list_waves(
        self,
        phase: int | None = None,
        status: str | None = None,
    ) -> list[TaskWave]:
        """Filtered query."""
        return list_waves(self._conn(), phase, status)

    def update_ticket_status(
        self,
        ticket_id: str,
        status: str,
        review_notes: str | None = None,
        blocker_reason: str | None = None,
    ) -> None:
        """UPDATE status + optional fields. Raises ValueError if ticket not found."""
        rowcount = update_ticket_status(
            self._conn(), ticket_id, status, review_notes, blocker_reason
        )
        if rowcount == 0:
            raise ValueError(f"ticket {ticket_id} not found")

    def update_ticket_wave(self, ticket_id: str, wave_id: str) -> None:
        """Update ticket's wave assignment."""
        update_ticket_wave(self._conn(), ticket_id, wave_id)

    def update_wave_status(self, wave_id: str, status: str) -> None:
        """UPDATE status."""
        update_wave_status(self._conn(), wave_id, status)

    def delete_ticket(self, ticket_id: str) -> bool:
        """DELETE by id, returns True if deleted."""
        return delete_ticket(self._conn(), ticket_id)

    def count_tickets(
        self, phase: int | None = None, status: str | None = None, priority: str | None = None
    ) -> int:
        """COUNT query."""
        return count_tickets(self._conn(), phase, status, priority)

    def get_ready_tickets(self, phase: int, limit: int = 10) -> list[MicroTaskTicket]:
        """Tickets whose dependencies' statuses are all 'completed'."""
        return get_ready_tickets(self._conn(), phase, limit)

    def close(self) -> None:
        """Close connection."""
        if self._connection:
            self._connection.close()
            self._connection = None