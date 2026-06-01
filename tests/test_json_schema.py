"""
Tests for JSON schema definitions and validation functions.
"""

import pytest

from smart_task.json_schema import (
    TICKET_JSON_SCHEMA,
    WAVE_JSON_SCHEMA,
    MAPPING_JSON_SCHEMA,
    validate_ticket,
    validate_wave,
    validate_mapping,
    migrate_ticket_v1_to_v2,
    migrate_wave_v1_to_v2,
    migrate_mapping_v1_to_v2,
)


class TestTicketJsonSchema:
    """Test TICKET_JSON_SCHEMA field definitions."""

    def test_has_required_field_id(self):
        assert "id" in TICKET_JSON_SCHEMA["properties"]
        assert TICKET_JSON_SCHEMA["properties"]["id"]["pattern"] == r"^TASK-[A-Z]{2,4}-\d{3}$"

    def test_has_required_field_title(self):
        assert "title" in TICKET_JSON_SCHEMA["required"]

    def test_has_required_field_objective(self):
        assert "objective" in TICKET_JSON_SCHEMA["required"]

    def test_has_correct_status_enum(self):
        status_enum = TICKET_JSON_SCHEMA["properties"]["status"]["enum"]
        assert "pending" in status_enum
        assert "in_progress" in status_enum
        assert "completed" in status_enum
        assert "blocked" in status_enum
        assert "cancelled" in status_enum
        assert "failed" not in status_enum
        assert "skipped" not in status_enum

    def test_has_dependencies_as_array(self):
        assert TICKET_JSON_SCHEMA["properties"]["dependencies"]["type"] == "array"

    def test_has_estimated_effort_enum(self):
        assert TICKET_JSON_SCHEMA["properties"]["estimated_effort"]["enum"] == ["S", "M", "L", "XL"]

    def test_all_list_fields_are_array_type(self):
        for field in ["dependencies", "file_targets", "acceptance_criteria", "tags"]:
            assert TICKET_JSON_SCHEMA["properties"][field]["type"] == "array"


class TestValidateTicket:
    """Test validate_ticket function."""

    def test_valid_ticket_returns_true_with_empty_errors(self):
        valid_ticket = {
            "id": "TASK-TEST-001",
            "title": "Test ticket",
            "objective": "Test objective",
            "phase": 1,
            "priority": "Medium",
            "estimated_effort": "M",
            "status": "pending",
        }
        is_valid, errors = validate_ticket(valid_ticket)
        assert is_valid is True
        assert errors == []

    def test_missing_id_returns_error(self):
        invalid_ticket = {
            "title": "Test ticket",
            "phase": 1,
            "priority": "Medium",
            "estimated_effort": "M",
            "status": "pending",
        }
        is_valid, errors = validate_ticket(invalid_ticket)
        assert is_valid is False
        assert any("id" in e for e in errors)

    def test_invalid_status_enum_returns_error(self):
        invalid_ticket = {
            "id": "TASK-TEST-001",
            "title": "Test ticket",
            "objective": "Test objective",
            "phase": 1,
            "priority": "Medium",
            "estimated_effort": "M",
            "status": "failed",
        }
        is_valid, errors = validate_ticket(invalid_ticket)
        assert is_valid is False
        assert any("status" in e for e in errors)

    def test_invalid_id_pattern_returns_error(self):
        invalid_ticket = {
            "id": "BAD-NAME",
            "title": "Test ticket",
            "objective": "Test objective",
            "phase": 1,
            "priority": "Medium",
            "estimated_effort": "M",
            "status": "pending",
        }
        is_valid, errors = validate_ticket(invalid_ticket)
        assert is_valid is False
        assert any("id" in e for e in errors)

    def test_array_field_validation(self):
        invalid_ticket = {
            "id": "TASK-TEST-001",
            "title": "Test ticket",
            "objective": "Test objective",
            "phase": 1,
            "priority": "Medium",
            "estimated_effort": "M",
            "status": "pending",
            "dependencies": "not-an-array",
        }
        is_valid, errors = validate_ticket(invalid_ticket)
        assert is_valid is False
        assert any("dependencies" in e for e in errors)

    def test_json_string_array_is_valid(self):
        valid_ticket = {
            "id": "TASK-TEST-001",
            "title": "Test ticket",
            "objective": "Test objective",
            "phase": 1,
            "priority": "Medium",
            "estimated_effort": "M",
            "status": "pending",
            "dependencies": '["TASK-OTHER-001"]',
            "file_targets": "[]",
            "acceptance_criteria": "[]",
            "tags": "[]",
        }
        is_valid, errors = validate_ticket(valid_ticket)
        assert is_valid is True

    def test_null_optional_fields_valid(self):
        valid_ticket = {
            "id": "TASK-TEST-001",
            "title": "Test ticket",
            "objective": "Test objective",
            "phase": 1,
            "priority": "Medium",
            "estimated_effort": "M",
            "status": "pending",
            "review_notes": None,
            "blocker_reason": None,
            "assignee": None,
            "wave_id": None,
            "completed_at": None,
        }
        is_valid, errors = validate_ticket(valid_ticket)
        assert is_valid is True

    def test_all_required_priority_values(self):
        for priority in ["High", "Medium", "Low"]:
            valid_ticket = {
                "id": "TASK-TEST-001",
                "title": "Test ticket",
                "objective": "Test objective",
                "phase": 1,
                "priority": priority,
                "estimated_effort": "M",
                "status": "pending",
            }
            is_valid, _ = validate_ticket(valid_ticket)
            assert is_valid is True

    def test_all_required_effort_values(self):
        for effort in ["S", "M", "L", "XL"]:
            valid_ticket = {
                "id": "TASK-TEST-001",
                "title": "Test ticket",
                "objective": "Test objective",
                "phase": 1,
                "priority": "Medium",
                "estimated_effort": effort,
                "status": "pending",
            }
            is_valid, _ = validate_ticket(valid_ticket)
            assert is_valid is True

    def test_all_required_phase_values(self):
        for phase in [1, 2, 3]:
            valid_ticket = {
                "id": "TASK-TEST-001",
                "title": "Test ticket",
                "objective": "Test objective",
                "phase": phase,
                "priority": "Medium",
                "estimated_effort": "M",
                "status": "pending",
            }
            is_valid, _ = validate_ticket(valid_ticket)
            assert is_valid is True

    def test_all_valid_status_values(self):
        for status in ["pending", "in_progress", "completed", "blocked", "cancelled"]:
            valid_ticket = {
                "id": "TASK-TEST-001",
                "title": "Test ticket",
                "objective": "Test objective",
                "phase": 1,
                "priority": "Medium",
                "estimated_effort": "M",
                "status": status,
            }
            is_valid, _ = validate_ticket(valid_ticket)
            assert is_valid is True

    def test_missing_objective_returns_error(self):
        invalid_ticket = {
            "id": "TASK-TEST-001",
            "title": "Test ticket",
            "phase": 1,
            "priority": "Medium",
            "estimated_effort": "M",
            "status": "pending",
        }
        is_valid, errors = validate_ticket(invalid_ticket)
        assert is_valid is False
        assert any("objective" in e for e in errors)

    def test_invalid_phase_returns_error(self):
        invalid_ticket = {
            "id": "TASK-TEST-001",
            "title": "Test ticket",
            "objective": "Test objective",
            "phase": 5,
            "priority": "Medium",
            "estimated_effort": "M",
            "status": "pending",
        }
        is_valid, errors = validate_ticket(invalid_ticket)
        assert is_valid is False
        assert any("phase" in e for e in errors)


class TestValidateWave:
    """Test validate_wave function."""

    def test_valid_wave_returns_true(self):
        valid_wave = {"id": "wave-01", "phase": 1}
        is_valid, errors = validate_wave(valid_wave)
        assert is_valid is True
        assert errors == []

    def test_missing_required_field_returns_error(self):
        invalid_wave = {"phase": 1}
        is_valid, errors = validate_wave(invalid_wave)
        assert is_valid is False
        assert any("id" in e for e in errors)

    def test_all_valid_wave_statuses(self):
        for status in ["pending", "active", "completed"]:
            valid_wave = {"id": "wave-01", "phase": 1, "status": status}
            is_valid, _ = validate_wave(valid_wave)
            assert is_valid is True


class TestValidateMapping:
    """Test validate_mapping function."""

    def test_valid_mapping_returns_true(self):
        valid_mapping = {"source_topic_file": "test.md", "sequence": 1}
        is_valid, errors = validate_mapping(valid_mapping)
        assert is_valid is True
        assert errors == []

    def test_missing_required_field_returns_error(self):
        invalid_mapping = {"sequence": 1}
        is_valid, errors = validate_mapping(invalid_mapping)
        assert is_valid is False
        assert any("source_topic_file" in e for e in errors)


class TestCompatibilityMigration:
    """Test schema migration functions."""

    def test_migrate_ticket_v1_to_v2_ticket_id_to_id(self):
        v1_ticket = {"ticket_id": "TASK-TEST-001"}
        v2_ticket = migrate_ticket_v1_to_v2(v1_ticket)
        assert "id" in v2_ticket
        assert v2_ticket["id"] == "TASK-TEST-001"
        assert "ticket_id" not in v2_ticket

    def test_migrate_mapping_v1_to_v2_topic_path(self):
        v1_mapping = {"topic_path": "test.md"}
        v2_mapping = migrate_mapping_v1_to_v2(v1_mapping)
        assert "source_topic_file" in v2_mapping
        assert v2_mapping["source_topic_file"] == "test.md"

    def test_migrate_wave_v1_to_v2(self):
        v1_wave = {"wave_id": "wave-01", "phase": 1}
        v2_wave = migrate_wave_v1_to_v2(v1_wave)
        assert v2_wave == v1_wave