"""
Read / write JSON ticket and wave artifacts with optional schema validation.

Exports
-------
- TicketParser : stateless helper for serialising and deserialising artifacts
- parse_topic_file : helper for extracting front matter from topic files
- extract_front_matter : low-level front matter extraction
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from smart_task.parser.parsing import (
    parse_ticket_file,
    parse_wave_file,
    serialize_ticket,
    serialize_wave,
    write_artifact,
)
from smart_task.parser.front_matter import extract_front_matter, parse_topic_file

__all__ = [
    "parse_ticket_file",
    "parse_wave_file",
    "serialize_ticket",
    "serialize_wave",
    "write_artifact",
    "extract_front_matter",
    "parse_topic_file",
]