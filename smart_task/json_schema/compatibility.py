"""
JSON Schema version migration helpers (schema v1→v2→…).
"""

from typing import Any


def migrate_ticket_v1_to_v2(data: dict[str, Any]) -> dict[str, Any]:
    """Migrate ticket schema from v1 to v2 format."""
    result = dict(data)

    if "ticket_id" in result:
        result.setdefault("id", result.pop("ticket_id"))

    return result


def migrate_wave_v1_to_v2(data: dict[str, Any]) -> dict[str, Any]:
    """Migrate wave schema from v1 to v2 format."""
    return dict(data)


def migrate_mapping_v1_to_v2(data: dict[str, Any]) -> dict[str, Any]:
    """Migrate mapping schema from v1 to v2 format."""
    result = dict(data)

    if "topic_path" in result:
        result.setdefault("source_topic_file", result.pop("topic_path"))

    if "ticket_id" in result:
        del result["ticket_id"]

    if "id" in result and "sequence" not in result:
        id_val = result["id"]
        if isinstance(id_val, int) or (isinstance(id_val, str) and id_val.isdigit()):
            result["sequence"] = result.pop("id")

    return result