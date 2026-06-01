"""
JSON Schema definitions for ticket, wave, and mapping artifacts.
"""

from typing import Any

TICKET_JSON_SCHEMA: dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "MicroTaskTicket",
    "type": "object",
    "properties": {
        "id": {"type": "string", "pattern": "^TASK-[A-Z]{2,4}-\\d{3}$"},
        "source_spec": {"type": "string"},
        "source_topic_file": {"type": "string"},
        "source_line_range": {"type": "string"},
        "topic_sequence": {"type": "integer", "minimum": 1},
        "title": {"type": "string"},
        "objective": {"type": "string"},
        "spec_context": {"type": "string"},
        "dependencies": {"type": "array", "items": {"type": "string"}},
        "file_targets": {"type": "array", "items": {"type": "string"}},
        "acceptance_criteria": {"type": "array", "items": {"type": "string"}},
        "verification_method": {"type": "string"},
        "review_notes": {"type": ["string", "null"]},
        "blocker_reason": {"type": ["string", "null"]},
        "phase": {"type": "integer", "enum": [1, 2, 3]},
        "priority": {"type": "string", "enum": ["High", "Medium", "Low"]},
        "estimated_effort": {"type": "string", "enum": ["S", "M", "L", "XL"]},
        "tags": {"type": "array", "items": {"type": "string"}},
        "assignee": {"type": ["string", "null"]},
        "wave_id": {"type": ["string", "null"]},
        "status": {
            "type": "string",
            "enum": ["pending", "in_progress", "completed", "blocked", "cancelled"],
        },
        "created_at": {"type": "string"},
        "updated_at": {"type": "string"},
        "completed_at": {"type": ["string", "null"]},
    },
    "required": [
        "id",
        "title",
        "objective",
        "phase",
        "priority",
        "estimated_effort",
        "status",
    ],
}

WAVE_JSON_SCHEMA: dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "TaskWave",
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "phase": {"type": "integer", "enum": [1, 2, 3]},
        "description": {"type": "string"},
        "ticket_count": {"type": "integer", "minimum": 0},
        "status": {"type": "string", "enum": ["pending", "active", "completed"]},
        "created_at": {"type": "string"},
        "completed_at": {"type": ["string", "null"]},
    },
    "required": ["id", "phase"],
}

MAPPING_JSON_SCHEMA: dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "TopicToTicketMapping",
    "type": "object",
    "properties": {
        "source_topic_file": {"type": "string"},
        "sequence": {"type": "integer", "minimum": 1},
        "title_template": {"type": "string"},
        "objective_template": {"type": "string"},
        "phase": {"type": "integer", "enum": [1, 2, 3]},
        "effort": {"type": "string", "enum": ["S", "M", "L", "XL"]},
        "tags": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["source_topic_file", "sequence"],
}