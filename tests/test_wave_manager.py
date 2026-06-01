"""
Tests for WaveManager functionality.
"""

import pytest
from pathlib import Path
import tempfile

from smart_task.wave_manager import WaveManager
from smart_task.models import MicroTaskTicket, TaskWave
from smart_task.repository import TicketRepository


class TestWaveManager:
    """Test WaveManager class."""

    def test_init_with_repository(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            repo = TicketRepository(db_path)
            manager = WaveManager(repo)
            assert manager._repo is not None

    def test_create_wave(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            with TicketRepository(db_path) as repo:
                manager = WaveManager(repo)
                wave = manager.create_wave("wave-01", 1, "Test wave")

                assert wave.id == "wave-01"
                assert wave.phase == 1
                assert wave.description == "Test wave"

                loaded = repo.get_wave("wave-01")
                assert loaded is not None

    def test_assign_tickets(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            with TicketRepository(db_path) as repo:
                manager = WaveManager(repo)

                wave = manager.create_wave("wave-01", 1, "Test wave")

                tickets = [
                    MicroTaskTicket(
                        id="TASK-TEST-001",
                        title="Ticket 1",
                        objective="Obj",
                        phase=1,
                        priority="High",
                        estimated_effort="M",
                        status="pending",
                    )
                ]
                for t in tickets:
                    repo.insert_ticket(t)

                count = manager.assign_tickets("wave-01", strategy="by_priority")

                assert count == 1

                loaded = repo.get_ticket("TASK-TEST-001")
                assert loaded.wave_id == "wave-01"

    def test_get_wave_summary(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            with TicketRepository(db_path) as repo:
                manager = WaveManager(repo)

                wave = manager.create_wave("wave-01", 1, "Test wave")

                tickets = [
                    MicroTaskTicket(
                        id="TASK-TEST-001",
                        title="Ticket 1",
                        objective="Obj",
                        phase=1,
                        priority="High",
                        estimated_effort="M",
                        status="pending",
                        wave_id="wave-01",
                    )
                ]
                for t in tickets:
                    repo.insert_ticket(t)

                summary = manager.get_wave_summary("wave-01")

                assert summary["id"] == "wave-01"
                assert summary["phase"] == 1
                assert summary["ticket_count"] == 1

    def test_get_project_summary(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            with TicketRepository(db_path) as repo:
                manager = WaveManager(repo)

                tickets = [
                    MicroTaskTicket(
                        id=f"TASK-TEST-{i:03d}",
                        title="Ticket",
                        objective="Obj",
                        phase=1,
                        priority="Medium",
                        estimated_effort="M",
                        status="pending",
                    )
                    for i in range(1, 4)
                ]
                for t in tickets:
                    repo.insert_ticket(t)

                summary = manager.get_project_summary()

                assert "total_tickets" in summary
                assert "by_phase" in summary
                assert "by_status" in summary
                assert "by_priority" in summary
                assert "waves" in summary
                assert "completion_pct" in summary
                assert summary["total_tickets"] == 3

    def test_assign_tickets_by_dependency_strategy(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            with TicketRepository(db_path) as repo:
                manager = WaveManager(repo)

                wave = manager.create_wave("wave-02", 1, "Test")

                # Ticket B depends on A
                tickets = [
                    MicroTaskTicket(
                        id="TASK-TEST-001",
                        title="No deps",
                        objective="Obj",
                        phase=1,
                        priority="High",
                        estimated_effort="M",
                        status="pending",
                    ),
                    MicroTaskTicket(
                        id="TASK-TEST-002",
                        title="Has deps",
                        objective="Obj",
                        dependencies='["TASK-TEST-001"]',
                        phase=1,
                        priority="Medium",
                        estimated_effort="M",
                        status="pending",
                    ),
                ]
                for t in tickets:
                    repo.insert_ticket(t)

                # Only ticket 001 should be ready (002 depends on it)
                count = manager.assign_tickets("wave-02", strategy="by_dependency")

                loaded = repo.list_tickets(wave_id="wave-02")
                assert all(t.id == "TASK-TEST-001" for t in loaded)