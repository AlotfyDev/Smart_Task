"""
Ticket generation from topic files and mapping templates.
"""

import json
from pathlib import Path
from typing import Any

from smart_task.models import MicroTaskTicket


def generate_ticket_id(prefix: str, sequence: int) -> str:
    """Generate a ticket ID in the format TASK-{PREFIX}-{NNN}."""
    return f"TASK-{prefix}-{sequence:03d}"


def render_template(template: str, context: dict[str, Any]) -> str:
    """Render an f-string template with context values."""
    try:
        return template.format(**context)
    except KeyError:
        return template


def create_ticket_from_mapping(
    topic_file: str,
    topic_front_matter: dict[str, Any],
    topic_body: str,
    mapping_entry: dict[str, Any],
    spec_prefix: str,
    sequence: int,
) -> MicroTaskTicket:
    """Create a MicroTaskTicket from a mapping entry."""
    context = {
        **topic_front_matter,
        "topic_file": topic_file,
    }

    title_template = mapping_entry.get("title", "{title}")
    objective_template = mapping_entry.get("objective", "{objective}")

    return MicroTaskTicket(
        id=generate_ticket_id(spec_prefix, sequence),
        source_spec=topic_front_matter.get("source", ""),
        source_topic_file=topic_file,
        source_line_range=f"{topic_front_matter.get('start_line', 1)}-{topic_front_matter.get('end_line', 1)}",
        topic_sequence=sequence,
        title=render_template(title_template, context),
        objective=render_template(objective_template, context),
        spec_context=topic_body,
        dependencies="[]",
        file_targets="[]",
        acceptance_criteria="[]",
        verification_method="",
        phase=mapping_entry.get("phase", 1),
        priority=mapping_entry.get("priority", "Medium"),
        estimated_effort=mapping_entry.get("effort", "M"),
        tags=json.dumps(mapping_entry.get("tags", [])),
        status="pending",
    )