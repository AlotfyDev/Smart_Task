"""
Wave assignment strategies.
"""

import json
from typing import Any

from smart_task.models import MicroTaskTicket
from smart_task.repository import TicketRepository


def _batch_unresolved_counts(
    tickets: list[MicroTaskTicket],
    repo: TicketRepository,
) -> dict[str, int]:
    """Return dict of ticket_id -> count of unresolved dependencies (single batch query)."""
    all_dep_ids: set[str] = set()
    ticket_deps: list[tuple[str, list[str]]] = []

    for t in tickets:
        try:
            deps = json.loads(t.dependencies) if t.dependencies else []
        except (json.JSONDecodeError, TypeError):
            deps = []
        ticket_deps.append((t.id, deps))
        all_dep_ids.update(deps)

    if not all_dep_ids:
        return {tid: 0 for tid, _ in ticket_deps}

    placeholders = ",".join("?" for _ in all_dep_ids)
    cursor = repo._conn().execute(
        f"SELECT id FROM micro_task_tickets WHERE id IN ({placeholders}) AND status != 'completed'",
        tuple(all_dep_ids),
    )
    non_completed = {row["id"] for row in cursor.fetchall()}

    return {
        tid: sum(1 for d in deps if d in non_completed)
        for tid, deps in ticket_deps
    }


def sort_by_dependency(tickets: list[MicroTaskTicket], repo: TicketRepository) -> list[MicroTaskTicket]:
    """Sort tickets with fewest unresolved dependencies first."""
    unresolved = _batch_unresolved_counts(tickets, repo)
    tickets_sorted = sorted(tickets, key=lambda t: unresolved.get(t.id, 0))
    return tickets_sorted


def sort_by_priority(tickets: list[MicroTaskTicket]) -> list[MicroTaskTicket]:
    """Sort tickets by priority: High > Medium > Low."""
    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    return sorted(tickets, key=lambda t: priority_order.get(t.priority, 1))


def sort_balanced(tickets: list[MicroTaskTicket]) -> list[MicroTaskTicket]:
    """Sort tickets in round-robin across priority levels."""
    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    by_priority: dict[str, list[MicroTaskTicket]] = {"High": [], "Medium": [], "Low": []}

    for t in tickets:
        p = t.priority or "Medium"
        if p in by_priority:
            by_priority[p].append(t)

    result: list[MicroTaskTicket] = []
    max_len = max(len(v) for v in by_priority.values())

    for _ in range(max_len):
        for priority in ["High", "Medium", "Low"]:
            if by_priority[priority]:
                result.append(by_priority[priority].pop(0))

    return result