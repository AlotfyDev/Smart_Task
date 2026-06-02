"""
Tests for MCP local server — handler, server, and integration tests.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest


class TestHandlers:
    """Unit tests for handler functions."""

    def test_handle_init_database(self, tmp_path):
        from smart_task.mcp_local.handlers import handle_init_database
        from smart_task.repository import TicketRepository

        db_path = tmp_path / "test_init.db"
        repo = TicketRepository(db_path)
        result = handle_init_database(repo, str(db_path))
        data = json.loads(result)
        assert data["status"] == "ok"
        assert db_path.exists()

    def test_handle_list_tickets_returns_json(self, tmp_path):
        from smart_task.mcp_local.handlers import handle_list_tickets
        from smart_task.repository import TicketRepository

        db_path = tmp_path / "test_list.db"
        repo = TicketRepository(db_path)
        result = handle_list_tickets(repo, None, None, None)
        data = json.loads(result)
        assert isinstance(data, list)
        assert data == []

    def test_handle_update_ticket_status_invalid(self, tmp_path):
        from smart_task.mcp_local.handlers import handle_update_ticket_status
        from smart_task.repository import TicketRepository

        db_path = tmp_path / "test_invalid.db"
        repo = TicketRepository(db_path)
        repo.ensure_schema()

        with pytest.raises(ValueError, match="invalid status"):
            handle_update_ticket_status(repo, "TASK-XXX-999", "invalid_status", None, None)


class TestServerCreation:
    """Tests for server building."""

    def test_create_local_server(self, tmp_path):
        from smart_task.mcp_local import create_local_server
        from smart_task.repository import TicketRepository
        from smart_task.wave_manager import WaveManager

        db_path = tmp_path / "test_server.db"
        repo = TicketRepository(db_path)
        repo.ensure_schema()
        wm = WaveManager(repo)

        server = create_local_server(repo, wm)
        assert server.name == "smart-task-local"


class TestToolMetadata:
    """Tests for tool definitions."""

    def test_tool_definitions_exist(self):
        from smart_task.mcp_local.tools import TOOL_DEFINITIONS

        expected_tools = [
            "init_database",
            "import_topics",
            "list_tickets",
            "get_ticket",
            "create_wave",
            "assign_tickets",
            "show_wave",
            "list_waves",
            "export_wave",
            "update_ticket_status",
            "get_project_stats",
        ]

        for tool in expected_tools:
            assert tool in TOOL_DEFINITIONS
            assert "description" in TOOL_DEFINITIONS[tool]
            assert "input_schema" in TOOL_DEFINITIONS[tool]


class TestRealWorld:
    """Real-world scenario tests."""

    def _make_ticket(self, repo, ticket_id: str, phase: int = 1, priority: str = "Medium",
                     dependencies: str | None = None) -> None:
        from smart_task.models import MicroTaskTicket

        ticket = MicroTaskTicket(
            id=ticket_id,
            source_spec="test-spec",
            source_topic_file="test.md",
            source_line_range="1-10",
            topic_sequence=1,
            title=f"Ticket {ticket_id}",
            objective=f"Objective for {ticket_id}",
            spec_context="context",
            dependencies=dependencies,
            file_targets="",
            acceptance_criteria="criterion",
            verification_method="manual",
            review_notes=None,
            blocker_reason=None,
            phase=phase,
            priority=priority,
            estimated_effort="M",
            tags="",
            assignee="",
            wave_id=None,
            status="pending",
            created_at="2025-01-01T00:00:00",
            updated_at="2025-01-01T00:00:00",
            completed_at=None,
        )
        repo.insert_ticket(ticket)

    def test_wave_lifecycle_round_trip(self, tmp_path):
        from smart_task.mcp_local.handlers import (
            handle_create_wave,
            handle_assign_tickets,
            handle_show_wave,
            handle_list_waves,
            handle_export_wave,
        )
        from smart_task.repository import TicketRepository
        from smart_task.wave_manager import WaveManager

        db_path = tmp_path / "wave_lifecycle.db"
        repo = TicketRepository(db_path)
        wm = WaveManager(repo)

        self._make_ticket(repo, "TASK-TEST-001", phase=1, priority="High")

        result = handle_create_wave(wm, "wave-1", 1, "First wave")
        data = json.loads(result)
        assert data["id"] == "wave-1"

        result = handle_assign_tickets(wm, "wave-1", count=1, strategy="by_dependency")
        data = json.loads(result)
        assert data["assigned"] >= 1

        result = handle_show_wave(wm, "wave-1")
        data = json.loads(result)
        assert data["id"] == "wave-1"

        waves_result = handle_list_waves(repo, phase=1)
        waves = json.loads(waves_result)
        assert any(w["id"] == "wave-1" for w in waves)

        export_result = handle_export_wave(repo, wm, "wave-1", "json", str(tmp_path))
        export_data = json.loads(export_result)
        assert len(export_data["files"]) > 0

    def test_assign_tickets_by_dependency(self, tmp_path):
        from smart_task.mcp_local.handlers import handle_assign_tickets, handle_create_wave
        from smart_task.repository import TicketRepository
        from smart_task.wave_manager import WaveManager

        db_path = tmp_path / "dep_assign.db"
        repo = TicketRepository(db_path)
        wm = WaveManager(repo)

        self._make_ticket(repo, "TASK-A-001", phase=1, dependencies=None)
        self._make_ticket(repo, "TASK-B-001", phase=1, dependencies="TASK-A-001")
        self._make_ticket(repo, "TASK-C-001", phase=1, dependencies="TASK-A-001,TASK-B-001")

        handle_create_wave(wm, "wave-dep", 1, "Dependency test")
        result = handle_assign_tickets(wm, "wave-dep", count=3, strategy="by_dependency")
        data = json.loads(result)
        assert data["assigned"] > 0

    def test_assign_tickets_by_priority(self, tmp_path):
        from smart_task.mcp_local.handlers import handle_assign_tickets, handle_create_wave
        from smart_task.repository import TicketRepository
        from smart_task.wave_manager import WaveManager

        db_path = tmp_path / "prio_assign.db"
        repo = TicketRepository(db_path)
        wm = WaveManager(repo)

        self._make_ticket(repo, "TASK-HIGH-001", phase=1, priority="High")
        self._make_ticket(repo, "TASK-LOW-001", phase=1, priority="Low")

        handle_create_wave(wm, "wave-prio", 1, "Priority test")
        result = handle_assign_tickets(wm, "wave-prio", count=2, strategy="by_priority")
        data = json.loads(result)
        assert data["assigned"] == 2

    def test_status_transitions(self, tmp_path):
        from smart_task.mcp_local.handlers import handle_update_ticket_status, handle_get_ticket
        from smart_task.repository import TicketRepository

        db_path = tmp_path / "transitions.db"
        repo = TicketRepository(db_path)
        self._make_ticket(repo, "TASK-TRANS-001", phase=1)

        result = handle_update_ticket_status(repo, "TASK-TRANS-001", "in_progress", None, None)
        data = json.loads(result)
        assert data["status"] == "in_progress"

        result = handle_update_ticket_status(repo, "TASK-TRANS-001", "completed", "Done", None)
        data = json.loads(result)
        assert data["status"] == "completed"
        assert data["review_notes"] == "Done"

    def test_export_wave_creates_files(self, tmp_path):
        from smart_task.mcp_local.handlers import handle_create_wave, handle_assign_tickets, handle_export_wave
        from smart_task.repository import TicketRepository
        from smart_task.wave_manager import WaveManager

        db_path = tmp_path / "export_test.db"
        repo = TicketRepository(db_path)
        wm = WaveManager(repo)

        self._make_ticket(repo, "TASK-EXP-001", phase=1)
        handle_create_wave(wm, "wave-exp", 1, "Export test")
        handle_assign_tickets(wm, "wave-exp", count=1, strategy="by_dependency")

        result = handle_export_wave(repo, wm, "wave-exp", "markdown", str(tmp_path))
        data = json.loads(result)
        files = [Path(f) for f in data["files"]]
        assert all(f.exists() for f in files)

    def test_get_ticket_not_found(self, tmp_path):
        from smart_task.mcp_local.handlers import handle_get_ticket
        from smart_task.repository import TicketRepository

        db_path = tmp_path / "notfound.db"
        repo = TicketRepository(db_path)

        with pytest.raises(ValueError, match="not found"):
            handle_get_ticket(repo, "TASK-NONEXIST-999")

    def test_update_ticket_status_not_found(self, tmp_path):
        from smart_task.mcp_local.handlers import handle_update_ticket_status
        from smart_task.repository import TicketRepository

        db_path = tmp_path / "notfound2.db"
        repo = TicketRepository(db_path)

        with pytest.raises(ValueError, match="not found"):
            handle_update_ticket_status(repo, "TASK-NONEXIST-999", "in_progress", None, None)