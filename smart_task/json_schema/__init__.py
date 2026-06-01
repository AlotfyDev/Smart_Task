"""
JSON Schema (draft-07) definitions for ticket / wave / mapping artifacts.

Exports
-------
- TICKET_JSON_SCHEMA   : schema for ticket JSON files
- WAVE_JSON_SCHEMA     : schema for wave JSON files
- MAPPING_JSON_SCHEMA  : schema for topic→ticket mapping files
- validate_ticket      : validate a dict against TICKET_JSON_SCHEMA
- validate_wave        : validate a dict against WAVE_JSON_SCHEMA
- validate_mapping     : validate a dict against MAPPING_JSON_SCHEMA
"""

from __future__ import annotations

from smart_task.json_schema.schemas import (
    TICKET_JSON_SCHEMA,
    WAVE_JSON_SCHEMA,
    MAPPING_JSON_SCHEMA,
)
from smart_task.json_schema.validators import (
    validate_ticket,
    validate_wave,
    validate_mapping,
)
from smart_task.json_schema.compatibility import (
    migrate_ticket_v1_to_v2,
    migrate_wave_v1_to_v2,
    migrate_mapping_v1_to_v2,
)

__all__ = [
    "TICKET_JSON_SCHEMA",
    "WAVE_JSON_SCHEMA",
    "MAPPING_JSON_SCHEMA",
    "validate_ticket",
    "validate_wave",
    "validate_mapping",
    "migrate_ticket_v1_to_v2",
    "migrate_wave_v1_to_v2",
    "migrate_mapping_v1_to_v2",
]