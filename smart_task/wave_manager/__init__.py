"""
Wave lifecycle management — creation, ticket assignment, and summary stats.

Exports
-------
- WaveManager : orchestrates wave-level operations
"""

from __future__ import annotations

from typing import Any

from smart_task.models import TaskWave
from smart_task.repository import TicketRepository
from smart_task.wave_manager.assigner import sort_by_dependency, sort_by_priority, sort_balanced
from smart_task.wave_manager.stats import calculate_project_summary


class WaveManager:
    """
    High-level operations for creating waves, assigning tickets, and
    gathering summary statistics.
    """

    def __init__(self, repository: TicketRepository) -> None:
        self._repo = repository

    def create_wave(
        self,
        wave_id: str,
        phase: int,
        description: str,
    ) -> TaskWave:
        """
        Create a new wave and insert into database.

        Returns:
            The created TaskWave instance.
        """
        wave = TaskWave(
            id=wave_id,
            phase=phase,
            description=description,
            status="pending",
        )
        self._repo.insert_wave(wave)
        return wave

    def assign_tickets(
        self,
        wave_id: str,
        count: int | None = None,
        strategy: str = "by_dependency",
    ) -> int:
        """
        Auto-assign pending tickets to a wave.

        Args:
            wave_id: The wave to assign tickets to
            count: Maximum number of tickets to assign (None = all ready)
            strategy: 'by_dependency', 'by_priority', or 'balanced'

        Returns:
            Number of tickets assigned.
        """
        wave = self._repo.get_wave(wave_id)
        if wave is None:
            raise ValueError(f"Wave {wave_id} not found")

        phase = wave.phase

        ready_tickets = self._repo.get_ready_tickets(phase)

        if strategy == "by_dependency":
            ready_tickets = sort_by_dependency(ready_tickets, self._repo)
        elif strategy == "by_priority":
            ready_tickets = sort_by_priority(ready_tickets)
        elif strategy == "balanced":
            ready_tickets = sort_balanced(ready_tickets)

        if count is not None:
            ready_tickets = ready_tickets[:count]

        for ticket in ready_tickets:
            self._repo.update_ticket_wave(ticket.id, wave_id)

        self._repo.update_wave_status(wave_id, "active")

        return len(ready_tickets)

    def get_wave_summary(self, wave_id: str) -> dict[str, Any]:
        """
        Get summary stats for a specific wave.

        Returns:
            Dict with: id, phase, description, status, ticket_count
        """
        wave = self._repo.get_wave(wave_id)
        if wave is None:
            raise ValueError(f"Wave {wave_id} not found")

        tickets = self._repo.list_tickets(wave_id=wave_id)

        return {
            "id": wave.id,
            "phase": wave.phase,
            "description": wave.description,
            "status": wave.status,
            "ticket_count": len(tickets),
        }

    def list_waves(
        self,
        phase: int | None = None,
        status: str | None = None,
    ) -> list[TaskWave]:
        """List waves with optional phase/status filters."""
        return self._repo.list_waves(phase=phase, status=status)

    def get_project_summary(self) -> dict[str, Any]:
        """
        Get comprehensive project statistics.

        Returns:
            Dict with all statistics in the specified format.
        """
        return calculate_project_summary(self._repo)