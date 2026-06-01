"""
Tests for TicketRepository CRUD operations.
"""

import json
import pytest
from pathlib import Path
import tempfile

from smart_task.repository import TicketRepository
from smart_task.models import MicroTaskTicket, TaskWave


class TestTicketRepositoryLifecycle:
    """Test repository lifecycle and connection management."""

    def test_init_creates_schema(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            repo = TicketRepository(db_path, auto_create=True)

            assert db_path.exists()

    def test_context_manager(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            with TicketRepository(db_path) as repo:
                assert repo._connection is not None


class TestInsertTicket:
    """Test ticket insertion."""

    def test_insert_single_ticket(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            with TicketRepository(db_path) as repo:
                ticket = MicroTaskTicket(
                    id="TASK-TEST-001",
                    title="Test ticket",
                    objective="Test objective",
                    phase=1,
                    priority="Medium",
                    estimated_effort="M",
                    status="pending",
                )
                repo.insert_ticket(ticket)

                loaded = repo.get_ticket("TASK-TEST-001")
                assert loaded is not None
                assert loaded.id == "TASK-TEST-001"

    def test_insert_tickets_batch(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            with TicketRepository(db_path) as repo:
                tickets = [
                    MicroTaskTicket(
                        id=f"TASK-TEST-{i:03d}",
                        title=f"Test ticket {i}",
                        objective="Test objective",
                        phase=1,
                        priority="Medium",
                        estimated_effort="M",
                        status="pending",
                    )
                    for i in range(1, 4)
                ]
                count = repo.insert_tickets_batch(tickets)

                assert count == 3
                assert repo.count_tickets() == 3


class TestGetReadyTickets:
    """Test get_ready_tickets dependency resolution."""

    def test_no_dependencies_returns_ready(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            with TicketRepository(db_path) as repo:
                ticket = MicroTaskTicket(
                    id="TASK-TEST-001",
                    title="Test ticket",
                    objective="Test objective",
                    phase=1,
                    priority="High",
                    estimated_effort="M",
                    status="pending",
                )
                repo.insert_ticket(ticket)

                ready = repo.get_ready_tickets(phase=1, limit=10)
                assert len(ready) == 1
                assert ready[0].id == "TASK-TEST-001"

    def test_dependency_not_completed_excludes_dependent(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            with TicketRepository(db_path) as repo:
                dep_ticket = MicroTaskTicket(
                    id="TASK-TEST-001",
                    title="Dependency",
                    objective="Test objective",
                    phase=1,
                    priority="Medium",
                    estimated_effort="M",
                    status="pending",  # Not completed
                )
                dependent = MicroTaskTicket(
                    id="TASK-TEST-002",
                    title="Dependent",
                    objective="Test objective",
                    dependencies=json.dumps(["TASK-TEST-001"]),
                    phase=1,
                    priority="Medium",
                    estimated_effort="M",
                    status="pending",
                )
                repo.insert_tickets_batch([dep_ticket, dependent])

                ready = repo.get_ready_tickets(phase=1, limit=10)
                # Only dep_ticket is ready (no dependencies), dependent is not (depends on pending)
                ready_ids = {t.id for t in ready}
                assert "TASK-TEST-001" in ready_ids  # No deps, should be ready
                assert "TASK-TEST-002" not in ready_ids  # Dep not completed, not ready

    def test_all_dependencies_completed_includes_dependent(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            with TicketRepository(db_path) as repo:
                dep_ticket = MicroTaskTicket(
                    id="TASK-TEST-001",
                    title="Dependency",
                    objective="Test objective",
                    phase=1,
                    priority="Medium",
                    estimated_effort="M",
                    status="completed",
                )
                dependent = MicroTaskTicket(
                    id="TASK-TEST-002",
                    title="Dependent",
                    objective="Test objective",
                    dependencies=json.dumps(["TASK-TEST-001"]),
                    phase=1,
                    priority="High",
                    estimated_effort="M",
                    status="pending",
                )
                repo.insert_tickets_batch([dep_ticket, dependent])

                ready = repo.get_ready_tickets(phase=1, limit=10)
                # Only dependent is returned (it's pending and its dep is completed)
                # dep_ticket with "completed" status is NOT returned because it's not pending
                assert len(ready) == 1
                assert ready[0].id == "TASK-TEST-002"

    def test_sorted_by_priority(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            with TicketRepository(db_path) as repo:
                tickets = [
                    MicroTaskTicket(
                        id=f"TASK-TEST-{i:03d}",
                        title=f"Priority {p}",
                        objective="Test objective",
                        phase=1,
                        priority=p,
                        estimated_effort="M",
                        status="pending",
                    )
                    for i, p in enumerate(["Low", "High", "Medium"])
                ]
                repo.insert_tickets_batch(tickets)

                ready = repo.get_ready_tickets(phase=1, limit=10)
                assert len(ready) == 3
                assert ready[0].priority == "High"
                assert ready[1].priority == "Medium"
                assert ready[2].priority == "Low"


class TestUpdateStatus:
    """Test status update operations."""

    def test_update_status_to_completed(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            with TicketRepository(db_path) as repo:
                ticket = MicroTaskTicket(
                    id="TASK-TEST-001",
                    title="Test ticket",
                    objective="Test objective",
                    phase=1,
                    priority="Medium",
                    estimated_effort="M",
                    status="pending",
                )
                repo.insert_ticket(ticket)

                repo.update_ticket_status("TASK-TEST-001", "completed", review_notes="Done")

                loaded = repo.get_ticket("TASK-TEST-001")
                assert loaded.status == "completed"

    def test_delete_ticket(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            with TicketRepository(db_path) as repo:
                ticket = MicroTaskTicket(
                    id="TASK-TEST-001",
                    title="Test ticket",
                    objective="Test objective",
                    phase=1,
                    priority="Medium",
                    estimated_effort="M",
                    status="pending",
                )
                repo.insert_ticket(ticket)

                deleted = repo.delete_ticket("TASK-TEST-001")
                assert deleted is True

                loaded = repo.get_ticket("TASK-TEST-001")
                assert loaded is None


class TestWaveOperations:
    """Test wave CRUD operations."""

    def test_insert_and_get_wave(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            with TicketRepository(db_path) as repo:
                wave = TaskWave(id="wave-01", phase=1, description="Test wave")
                repo.insert_wave(wave)

                loaded = repo.get_wave("wave-01")
                assert loaded is not None
                assert loaded.id == "wave-01"
                assert loaded.phase == 1

    def test_list_waves(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            with TicketRepository(db_path) as repo:
                waves = [
                    TaskWave(id=f"wave-{i:02d}", phase=1, description=f"Wave {i}")
                    for i in range(1, 4)
                ]
                for w in waves:
                    repo.insert_wave(w)

                loaded = repo.list_waves()
                assert len(loaded) == 3