"""
JSON Schema validation functions for artifacts.
"""

import json
import re
from typing import Any

from smart_task.json_schema.schemas import (
    TICKET_JSON_SCHEMA,
    WAVE_JSON_SCHEMA,
    MAPPING_JSON_SCHEMA,
)


def _validate_array_field(value: Any, field: str, field_schema: dict[str, Any]) -> list[str]:
    """Validate an array field, handling both list and JSON string."""
    errors: list[str] = []

    if isinstance(value, list):
        items_schema = field_schema.get("items", {})
        items_type = items_schema.get("type")
        if items_type:
            for i, item in enumerate(value):
                if items_type == "string" and not isinstance(item, str):
                    errors.append(f"{field}[{i}] must be a string")
    elif isinstance(value, str):
        try:
            parsed = json.loads(value)
            if not isinstance(parsed, list):
                errors.append(f"{field} must be a JSON array, got {type(parsed).__name__}")
        except json.JSONDecodeError:
            errors.append(f"{field} is not valid JSON: {value}")
    else:
        errors.append(f"{field} must be an array or JSON string")

    return errors


def _validate_against_schema(data: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    """Validate data against a JSON schema (draft-07 subset)."""
    errors: list[str] = []

    for field in schema.get("required", []):
        if field not in data:
            errors.append(f"missing required field: {field}")

    for field, field_schema in schema.get("properties", {}).items():
        if field not in data:
            continue

        value = data[field]
        field_type = field_schema.get("type")
        target_type = field_schema.get("type")

        if target_type == "string":
            if not isinstance(value, str):
                errors.append(f"{field} must be a string")
        elif target_type == "integer":
            if not isinstance(value, int) or isinstance(value, bool):
                errors.append(f"{field} must be an integer")
        elif target_type == "array":
            errors.extend(_validate_array_field(value, field, field_schema))
        elif isinstance(target_type, list):
            if not any(
                (t == "string" and isinstance(value, str))
                or (t == "null" and value is None)
                for t in target_type
            ):
                if value is not None:
                    errors.append(f"{field} must be one of {target_type}, got {type(value).__name__}")

        if "enum" in field_schema and value not in field_schema["enum"]:
            errors.append(f"{field} must be one of {field_schema['enum']}, got {value!r}")

        if "pattern" in field_schema and isinstance(value, str):
            if not re.match(field_schema["pattern"], value):
                errors.append(f"{field} does not match pattern {field_schema['pattern']}")

    return errors


def validate_ticket(data: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate a ticket dict against TICKET_JSON_SCHEMA."""
    if not isinstance(data, dict):
        return (False, ["data must be a dictionary"])
    errors = _validate_against_schema(data, TICKET_JSON_SCHEMA)
    return (len(errors) == 0, errors)


def validate_wave(data: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate a wave dict against WAVE_JSON_SCHEMA."""
    if not isinstance(data, dict):
        return (False, ["data must be a dictionary"])
    errors = _validate_against_schema(data, WAVE_JSON_SCHEMA)
    return (len(errors) == 0, errors)


def validate_mapping(data: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate a mapping dict against MAPPING_JSON_SCHEMA."""
    if not isinstance(data, dict):
        return (False, ["data must be a dictionary"])
    errors = _validate_against_schema(data, MAPPING_JSON_SCHEMA)
    return (len(errors) == 0, errors)