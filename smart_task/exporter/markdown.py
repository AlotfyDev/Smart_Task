"""
Markdown export formatting for waves and tickets.
"""

import json
from typing import Any

from smart_task.models import MicroTaskTicket, TaskWave


def format_ticket_markdown(ticket: MicroTaskTicket) -> str:
    """Format a single ticket as markdown."""
    lines = [
        f"## {ticket.id}: {ticket.title}",
        "",
    ]

    source_info = f"{ticket.source_topic_file}"
    if ticket.source_line_range:
        source_info += f" (lines {ticket.source_line_range})"
    lines.append(f"**Source:** {source_info}")

    effort = ticket.estimated_effort or "M"
    lines.append(f"**Priority:** {ticket.priority} | **Effort:** {effort} | **Phase:** {ticket.phase}")

    if ticket.objective:
        lines.append("")
        lines.append(f"**Objective:**")
        lines.append(ticket.objective)

    if ticket.spec_context:
        lines.append("")
        lines.append("**Spec Context:**")
        lines.append("```")
        lines.append(ticket.spec_context.strip())
        lines.append("```")

    deps = []
    if ticket.dependencies:
        try:
            deps = json.loads(ticket.dependencies)
        except (json.JSONDecodeError, TypeError):
            pass

    lines.append("")
    if deps:
        lines.append(f"**Dependencies:** {', '.join(deps)}")
    else:
        lines.append("**Dependencies:** *none*")

    targets = []
    if ticket.file_targets:
        try:
            targets = json.loads(ticket.file_targets)
        except (json.JSONDecodeError, TypeError):
            pass

    if targets:
        lines.append(f"**File Targets:** `{'`, `'.join(map(str, targets))}`")

    criteria = []
    if ticket.acceptance_criteria:
        try:
            criteria = json.loads(ticket.acceptance_criteria)
        except (json.JSONDecodeError, TypeError):
            pass

    if criteria:
        lines.append("")
        lines.append("**Acceptance Criteria:**")
        for criterion in criteria:
            lines.append(f"- [ ] {criterion}")

    if ticket.verification_method:
        lines.append("")
        lines.append("**Verification:**")
        lines.append(f"```{ticket.verification_method.split(':')[0].lower()}")
        if ":" in ticket.verification_method:
            lines.append(ticket.verification_method.split(":", 1)[1].strip())
        lines.append("```")

    return "\n".join(lines)


def export_wave_to_markdown(
    tickets: list[MicroTaskTicket],
    wave: TaskWave,
) -> str:
    """
    Build full markdown with all fields.

    Format:
    # Wave: {wave_id}
    Phase: {phase} | Status: {status} | Tickets: {count}

    ---

    ## Ticket sections...
    """
    lines = [
        f"# Wave: {wave.id}",
        f"Phase: {wave.phase} | Status: {wave.status} | Tickets: {len(tickets)}",
        "",
        "---",
        "",
    ]

    for ticket in tickets:
        lines.append(format_ticket_markdown(ticket))
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)
