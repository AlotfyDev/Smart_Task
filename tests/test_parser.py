"""
Tests for TicketParser functionality.
"""

import json
import pytest
from pathlib import Path
import tempfile

from smart_task.parser import (
    parse_ticket_file,
    parse_wave_file,
    serialize_ticket,
    serialize_wave,
    write_artifact,
)
from smart_task.models import MicroTaskTicket, TaskWave


class TestParseTicketFile:
    """Test parse_ticket_file function."""

    def test_parse_valid_ticket(self):
        ticket_data = {
            "id": "TASK-TEST-001",
            "title": "Test ticket",
            "objective": "Test objective",
            "phase": 1,
            "priority": "Medium",
            "estimated_effort": "M",
            "status": "pending",
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(ticket_data, f)
            temp_path = Path(f.name)

        try:
            ticket = parse_ticket_file(temp_path)
            assert isinstance(ticket, MicroTaskTicket)
            assert ticket.id == "TASK-TEST-001"
            assert ticket.title == "Test ticket"
        finally:
            temp_path.unlink()

    def test_parse_ticket_with_all_fields(self):
        ticket_data = {
            "id": "TASK-TEST-001",
            "source_spec": "identity_model_spec.md",
            "source_topic_file": "01_overview.md",
            "source_line_range": "1-25",
            "topic_sequence": 1,
            "title": "Test ticket",
            "objective": "Test objective",
            "spec_context": "Some spec context",
            "dependencies": ["TASK-OTH-001"],
            "file_targets": ["file.py"],
            "acceptance_criteria": ["Criterion 1"],
            "verification_method": "SHELL: pytest",
            "review_notes": "Notes",
            "blocker_reason": None,
            "phase": 1,
            "priority": "High",
            "estimated_effort": "L",
            "tags": ["tag1", "tag2"],
            "assignee": "agent-1",
            "wave_id": "wave-01",
            "status": "in_progress",
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(ticket_data, f)
            temp_path = Path(f.name)

        try:
            ticket = parse_ticket_file(temp_path)
            assert ticket.source_spec == "identity_model_spec.md"
            assert ticket.source_topic_file == "01_overview.md"
            assert ticket.priority == "High"
            assert ticket.estimated_effort == "L"
        finally:
            temp_path.unlink()

    def test_file_not_found_raises(self):
        with pytest.raises(FileNotFoundError):
            parse_ticket_file(Path("/nonexistent/ticket.json"))

    def test_invalid_json_raises(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            f.write("not valid json{")
            temp_path = Path(f.name)

        try:
            with pytest.raises(json.JSONDecodeError):
                parse_ticket_file(temp_path)
        finally:
            temp_path.unlink()

    def test_invalid_ticket_raises_value_error(self):
        invalid_ticket = {"id": "BAD"}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(invalid_ticket, f)
            temp_path = Path(f.name)

        try:
            with pytest.raises(ValueError):
                parse_ticket_file(temp_path)
        finally:
            temp_path.unlink()

    def test_missing_objective_raises_value_error(self):
        invalid_ticket = {
            "id": "TASK-TEST-001",
            "title": "Test ticket",
            "phase": 1,
            "priority": "Medium",
            "estimated_effort": "M",
            "status": "pending",
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(invalid_ticket, f)
            temp_path = Path(f.name)

        try:
            with pytest.raises(ValueError):
                parse_ticket_file(temp_path)
        finally:
            temp_path.unlink()


class TestParseWaveFile:
    """Test parse_wave_file function."""

    def test_parse_valid_wave(self):
        wave_data = {
            "id": "wave-01",
            "phase": 1,
            "description": "Test wave",
            "status": "pending",
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(wave_data, f)
            temp_path = Path(f.name)

        try:
            wave = parse_wave_file(temp_path)
            assert isinstance(wave, TaskWave)
            assert wave.id == "wave-01"
            assert wave.phase == 1
        finally:
            temp_path.unlink()

    def test_parse_wave_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            parse_wave_file(Path("/nonexistent/wave.json"))


class TestSerializeTicket:
    """Test serialize_ticket function."""

    def test_serialize_valid_ticket(self):
        ticket = MicroTaskTicket(
            id="TASK-TEST-001",
            title="Test ticket",
            objective="Test objective",
            phase=1,
            priority="Medium",
            estimated_effort="M",
            status="pending",
        )
        data = serialize_ticket(ticket)
        assert data["id"] == "TASK-TEST-001"
        assert data["title"] == "Test ticket"

    def test_serialize_includes_list_fields_as_json(self):
        ticket = MicroTaskTicket(
            id="TASK-TEST-001",
            title="Test ticket",
            objective="Test objective",
            dependencies='["TASK-OTH-001"]',
            tags='["tag1"]',
            phase=1,
            priority="Medium",
            estimated_effort="M",
            status="pending",
        )
        data = serialize_ticket(ticket)
        assert data["dependencies"] == '["TASK-OTH-001"]'
        assert data["tags"] == '["tag1"]'


class TestSerializeWave:
    """Test serialize_wave function."""

    def test_serialize_valid_wave(self):
        wave = TaskWave(
            id="wave-01",
            phase=1,
            description="Test wave",
            status="active",
        )
        data = serialize_wave(wave)
        assert data["id"] == "wave-01"
        assert data["status"] == "active"


class TestWriteArtifact:
    """Test write_artifact function."""

    def test_write_creates_file(self):
        data = {"id": "TASK-TEST-001", "title": "Test"}
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "artifact.json"
            write_artifact(path, data)

            assert path.exists()
            content = path.read_text(encoding="utf-8")
            loaded = json.loads(content)
            assert loaded["id"] == "TASK-TEST-001"

    def test_write_pretty_printed(self):
        data = {"id": "TASK-TEST-001", "title": "Test"}
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "artifact.json"
            write_artifact(path, data)

            content = path.read_text(encoding="utf-8")
            assert "  " in content  # Has indentation

    def test_write_creates_parent_directories(self):
        data = {"id": "TASK-TEST-001"}
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "subdir" / "nested" / "artifact.json"
            write_artifact(path, data)

            assert path.exists()


class TestRoundTrip:
    """Test serialize → write → read → compare round trip."""

    def test_ticket_round_trip(self):
        original = MicroTaskTicket(
            id="TASK-TEST-001",
            title="Test ticket",
            objective="Test objective",
            phase=1,
            priority="Medium",
            estimated_effort="M",
            status="pending",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "ticket.json"

            data = serialize_ticket(original)
            write_artifact(path, data)
            loaded = parse_ticket_file(path)

            assert loaded.id == original.id
            assert loaded.title == original.title
            assert loaded.objective == original.objective
            assert loaded.phase == original.phase

    def test_wave_round_trip(self):
        original = TaskWave(
            id="wave-01",
            phase=1,
            description="Test wave",
            status="active",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "wave.json"

            data = serialize_wave(original)
            write_artifact(path, data)
            loaded = parse_wave_file(path)

            assert loaded.id == original.id
            assert loaded.phase == original.phase
            assert loaded.description == original.description