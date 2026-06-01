"""
Project statistics for wave manager.
"""

from typing import Any

from smart_task.repository import TicketRepository


def calculate_project_summary(repo: TicketRepository) -> dict[str, Any]:
    """
    Calculate comprehensive project statistics.

    Returns:
        Dict with: total_tickets, by_phase, by_status, by_priority, waves, completion_pct
    """
    total = repo.count_tickets()
    completed = repo.count_tickets(status="completed")

    by_phase: dict[int, int] = {}
    for phase in [1, 2, 3]:
        by_phase[phase] = repo.count_tickets(phase=phase)

    by_status: dict[str, int] = {}
    for status in ["pending", "in_progress", "completed", "blocked", "cancelled"]:
        count = repo.count_tickets(status=status)
        by_status[status] = count

    by_priority: dict[str, int] = {}
    for priority in ["High", "Medium", "Low"]:
        by_priority[priority] = repo.count_tickets(priority=priority)

    waves: dict[str, int] = {}
    all_waves = repo.list_waves()
    waves["total"] = len(all_waves)
    waves["active"] = sum(1 for w in all_waves if w.status == "active")
    waves["completed"] = sum(1 for w in all_waves if w.status == "completed")

    completion_pct = (completed / total * 100) if total > 0 else 0.0

    return {
        "total_tickets": total,
        "by_phase": by_phase,
        "by_status": by_status,
        "by_priority": by_priority,
        "waves": waves,
        "completion_pct": completion_pct,
    }