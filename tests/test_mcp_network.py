"""Tests for MCP network server."""

from __future__ import annotations

import json
from pathlib import Path

import pytest


class TestSseAppCreation:
    def test_create_sse_app_defaults(self, tmp_path):
        from smart_task.mcp_network import create_sse_app
        from smart_task.repository import TicketRepository
        from smart_task.wave_manager import WaveManager
        db = tmp_path / "test.db"
        repo = TicketRepository(db)
        wm = WaveManager(repo)
        app = create_sse_app(repo, wm)
        assert app.name == "smart-task-network"

    def test_create_sse_app_with_host_port(self, tmp_path):
        from smart_task.mcp_network import create_sse_app
        from smart_task.repository import TicketRepository
        from smart_task.wave_manager import WaveManager
        db = tmp_path / "test.db"
        repo = TicketRepository(db)
        wm = WaveManager(repo)
        app = create_sse_app(repo, wm, host="0.0.0.0", port=9090)
        assert app.name == "smart-task-network"


class TestHandlerIntegration:
    def test_init_database_via_handler(self, tmp_path):
        from smart_task.mcp_local.handlers import handle_init_database
        from smart_task.repository import TicketRepository
        db = tmp_path / "init.db"
        repo = TicketRepository(db)
        result = handle_init_database(repo, str(db))
        data = json.loads(result)
        assert data["status"] == "ok"
        assert db.exists()

    def test_wave_lifecycle_round_trip(self, tmp_path):
        from smart_task.mcp_local.handlers import handle_create_wave, handle_show_wave, handle_list_waves
        from smart_task.repository import TicketRepository
        from smart_task.wave_manager import WaveManager
        db = tmp_path / "wave.db"
        repo = TicketRepository(db)
        wm = WaveManager(repo)
        result = handle_create_wave(wm, "wave-test", 1, "Test wave")
        data = json.loads(result)
        assert data["id"] == "wave-test"
        result = handle_show_wave(wm, "wave-test")
        data = json.loads(result)
        assert data["id"] == "wave-test"
        result = handle_list_waves(repo, None)
        data = json.loads(result)
        assert any(w["id"] == "wave-test" for w in data)

    def test_update_ticket_status_invalid(self, tmp_path):
        from smart_task.mcp_local.handlers import handle_update_ticket_status
        from smart_task.repository import TicketRepository
        db = tmp_path / "status.db"
        repo = TicketRepository(db)
        with pytest.raises(ValueError, match="invalid status"):
            handle_update_ticket_status(repo, "TASK-XXX-999", "bad_status", None, None)

    def test_get_ticket_not_found(self, tmp_path):
        from smart_task.mcp_local.handlers import handle_get_ticket
        from smart_task.repository import TicketRepository
        db = tmp_path / "notfound.db"
        repo = TicketRepository(db)
        with pytest.raises(ValueError, match="not found"):
            handle_get_ticket(repo, "TASK-NONEXISTENT")


class TestModuleImport:
    def test_module_importable(self):
        from smart_task.mcp_network import create_sse_app, run_network_server, main
        assert callable(run_network_server)
