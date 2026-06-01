"""Tests for smart_task.models module."""

from __future__ import annotations

import json

import pytest

from smart_task.models import MicroTaskTicket, TaskWave, TopicToTicketMapping


# ── MicroTaskTicket Tests ──────────────────────────────────────────────


class TestMicroTaskTicketCreation:
    def test_create_valid_ticket(self):
        ticket = MicroTaskTicket(
            id="TASK-IDM-001",
            title="Implement authentication",
            objective="Add login flow",
            phase=1,
            priority="High",
            estimated_effort="M",
        )
        assert ticket.id == "TASK-IDM-001"
        assert ticket.phase == 1

    def test_default_list_fields_are_json_arrays(self):
        ticket = MicroTaskTicket(id="TASK-IDM-002", title="Test", objective="Test")
        assert json.loads(ticket.dependencies) == []
        assert json.loads(ticket.tags) == []
        assert json.loads(ticket.acceptance_criteria) == []
        assert json.loads(ticket.file_targets) == []


class TestMicroTaskTicketRoundTrip:
    def test_to_dict_from_dict_round_trip(self):
        ticket = MicroTaskTicket(
            id="TASK-IDM-010",
            title="Test ticket",
            objective="Test objective",
            phase=2,
            priority="High",
            estimated_effort="L",
            dependencies=json.dumps(["TASK-IDM-001"]),
            tags=json.dumps(["auth", "security"]),
            acceptance_criteria=json.dumps(["criterion 1"]),
            file_targets=json.dumps(["src/auth.py"]),
        )
        d = ticket.to_dict()
        restored = MicroTaskTicket.from_dict(d)
        assert restored.id == ticket.id
        assert restored.title == ticket.title
        assert restored.phase == ticket.phase
        assert restored.priority == ticket.priority
        assert restored.estimated_effort == ticket.estimated_effort
        assert restored.dependencies == ticket.dependencies
        assert restored.tags == ticket.tags
        assert restored.acceptance_criteria == ticket.acceptance_criteria
        assert restored.file_targets == ticket.file_targets

    def test_to_dict_serializes_lists_to_json(self):
        ticket = MicroTaskTicket(
            id="TASK-IDM-011",
            title="Test",
            objective="Test",
            phase=1,
        )
        d = ticket.to_dict()
        assert isinstance(d["dependencies"], str)
        assert isinstance(d["tags"], str)

    def test_from_dict_accepts_list_values(self):
        data = {
            "id": "TASK-IDM-012",
            "title": "Test",
            "objective": "Test",
            "phase": 1,
            "dependencies": ["TASK-IDM-001"],
            "tags": ["urgent"],
        }
        ticket = MicroTaskTicket.from_dict(data)
        assert json.loads(ticket.dependencies) == ["TASK-IDM-001"]
        assert json.loads(ticket.tags) == ["urgent"]


class TestMicroTaskTicketToRow:
    def test_to_row_length(self):
        ticket = MicroTaskTicket(id="TASK-IDM-020", title="Test", objective="Test", phase=1)
        row = ticket.to_row()
        assert len(row) == 24


class TestMicroTaskTicketValidate:
    def test_valid_ticket_returns_empty(self):
        ticket = MicroTaskTicket(
            id="TASK-IDM-030",
            title="Valid ticket",
            objective="Valid objective",
            phase=1,
            priority="Medium",
            estimated_effort="M",
            status="pending",
        )
        assert ticket.validate() == []

    def test_missing_id_returns_error(self):
        ticket = MicroTaskTicket(id="", title="Test", objective="Test", phase=1)
        errors = ticket.validate()
        assert len(errors) > 0
        assert any("id" in e for e in errors)

    def test_invalid_id_pattern(self):
        ticket = MicroTaskTicket(id="TASK-001", title="Test", objective="Test", phase=1)
        errors = ticket.validate()
        assert len(errors) > 0

    def test_valid_id_pattern(self):
        ticket = MicroTaskTicket(id="TASK-IDM-001", title="Test", objective="Test", phase=1)
        errors = ticket.validate()
        assert "id" not in " ".join(errors).lower() or all("id" not in e for e in errors)

    def test_invalid_phase(self):
        ticket = MicroTaskTicket(
            id="TASK-IDM-031", title="Test", objective="Test", phase=4,
        )
        errors = ticket.validate()
        assert any("phase" in e for e in errors)

    def test_invalid_priority(self):
        ticket = MicroTaskTicket(
            id="TASK-IDM-032", title="Test", objective="Test", phase=1,
            priority="Urgent",
        )
        errors = ticket.validate()
        assert any("priority" in e for e in errors)

    def test_invalid_effort(self):
        ticket = MicroTaskTicket(
            id="TASK-IDM-033", title="Test", objective="Test", phase=1,
            estimated_effort="XXL",
        )
        errors = ticket.validate()
        assert any("effort" in e for e in errors)

    def test_invalid_status(self):
        ticket = MicroTaskTicket(
            id="TASK-IDM-034", title="Test", objective="Test", phase=1,
            status="failed",
        )
        errors = ticket.validate()
        assert any("status" in e for e in errors)

    def test_invalid_json_dependencies(self):
        ticket = MicroTaskTicket(
            id="TASK-IDM-035", title="Test", objective="Test", phase=1,
            dependencies="{bad json",
        )
        errors = ticket.validate()
        assert any("dependencies" in e for e in errors)

    def test_missing_title_returns_error(self):
        ticket = MicroTaskTicket(id="TASK-IDM-036", title="", objective="Test", phase=1)
        errors = ticket.validate()
        assert any("title" in e for e in errors)

    def test_missing_objective_returns_error(self):
        ticket = MicroTaskTicket(id="TASK-IDM-037", title="Test", objective="", phase=1)
        errors = ticket.validate()
        assert any("objective" in e for e in errors)


# ── TaskWave Tests ─────────────────────────────────────────────────────


class TestTaskWave:
    def test_create_valid_wave(self):
        wave = TaskWave(id="wave-01", phase=1, description="First wave")
        assert wave.id == "wave-01"
        assert wave.phase == 1

    def test_to_dict_from_dict_round_trip(self):
        wave = TaskWave(
            id="wave-02", phase=2, description="Second wave",
            ticket_count=5, status="active",
        )
        d = wave.to_dict()
        restored = TaskWave.from_dict(d)
        assert restored.id == wave.id
        assert restored.phase == wave.phase
        assert restored.ticket_count == wave.ticket_count
        assert restored.status == wave.status

    def test_to_row_length(self):
        wave = TaskWave(id="wave-03", phase=1)
        row = wave.to_row()
        assert len(row) == 7

    def test_validate_valid(self):
        wave = TaskWave(id="wave-04", phase=1, status="pending")
        assert wave.validate() == []

    def test_validate_missing_id(self):
        wave = TaskWave(id="", phase=1)
        errors = wave.validate()
        assert any("id" in e for e in errors)

    def test_validate_invalid_phase(self):
        wave = TaskWave(id="wave-05", phase=4)
        errors = wave.validate()
        assert any("phase" in e for e in errors)

    def test_validate_invalid_status(self):
        wave = TaskWave(id="wave-06", phase=1, status="failed")
        errors = wave.validate()
        assert any("status" in e for e in errors)


# ── TopicToTicketMapping Tests ─────────────────────────────────────────


class TestTopicToTicketMapping:
    def test_create_valid_mapping(self):
        mapping = TopicToTicketMapping(
            source_topic_file="topics/auth.md",
            sequence=1,
            title_template="Implement {feature}",
            objective_template="Add {feature} to the system",
            phase=1,
            effort="M",
        )
        assert mapping.source_topic_file == "topics/auth.md"
        assert mapping.sequence == 1

    def test_to_dict_from_dict_round_trip(self):
        mapping = TopicToTicketMapping(
            id=1,
            source_topic_file="topics/auth.md",
            sequence=1,
            title_template="Title",
            objective_template="Objective",
            phase=1,
            effort="L",
            tags=json.dumps(["auth"]),
        )
        d = mapping.to_dict()
        restored = TopicToTicketMapping.from_dict(d)
        assert restored.id == mapping.id
        assert restored.source_topic_file == mapping.source_topic_file
        assert restored.sequence == mapping.sequence
        assert restored.phase == mapping.phase
        assert restored.effort == mapping.effort
        assert restored.tags == mapping.tags

    def test_to_dict_serializes_tags_to_json(self):
        mapping = TopicToTicketMapping(
            source_topic_file="test.md",
            sequence=1,
            title_template="T",
            objective_template="O",
            phase=1,
            effort="S",
        )
        d = mapping.to_dict()
        assert isinstance(d["tags"], str)

    def test_from_dict_accepts_list_tags(self):
        data = {
            "source_topic_file": "test.md",
            "sequence": 1,
            "title_template": "T",
            "objective_template": "O",
            "phase": 1,
            "effort": "S",
            "tags": ["fast", "critical"],
        }
        mapping = TopicToTicketMapping.from_dict(data)
        assert json.loads(mapping.tags) == ["fast", "critical"]

    def test_to_row_length(self):
        mapping = TopicToTicketMapping(
            source_topic_file="test.md",
            sequence=1,
            title_template="T",
            objective_template="O",
            phase=1,
            effort="M",
        )
        row = mapping.to_row()
        assert len(row) == 8

    def test_validate_valid(self):
        mapping = TopicToTicketMapping(
            source_topic_file="topics/auth.md",
            sequence=1,
            title_template="T",
            objective_template="O",
            phase=2,
            effort="XL",
        )
        assert mapping.validate() == []

    def test_validate_missing_source_topic_file(self):
        mapping = TopicToTicketMapping(
            source_topic_file="",
            sequence=1,
            title_template="T",
            objective_template="O",
            phase=1,
            effort="M",
        )
        errors = mapping.validate()
        assert any("source_topic_file" in e for e in errors)

    def test_validate_invalid_phase(self):
        mapping = TopicToTicketMapping(
            source_topic_file="test.md",
            sequence=1,
            title_template="T",
            objective_template="O",
            phase=0,
            effort="M",
        )
        errors = mapping.validate()
        assert any("phase" in e for e in errors)

    def test_validate_invalid_effort(self):
        mapping = TopicToTicketMapping(
            source_topic_file="test.md",
            sequence=1,
            title_template="T",
            objective_template="O",
            phase=1,
            effort="XXXL",
        )
        errors = mapping.validate()
        assert any("effort" in e for e in errors)

    def test_validate_invalid_tags_json(self):
        mapping = TopicToTicketMapping(
            source_topic_file="test.md",
            sequence=1,
            title_template="T",
            objective_template="O",
            phase=1,
            effort="M",
            tags="not json at all",
        )
        errors = mapping.validate()
        assert any("tags" in e for e in errors)
