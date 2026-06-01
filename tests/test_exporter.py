"""
Tests for WaveExporter functionality.
"""

import json
import pytest
from pathlib import Path
import tempfile

from smart_task.exporter import WaveExporter, export_wave_to_markdown, format_wave_json
from smart_task.models import MicroTaskTicket, TaskWave
from smart_task.repository import TicketRepository


class TestWaveExporter:
    """Test WaveExporter class."""

    def test_init_with_repository(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            repo = TicketRepository(db_path)
            exporter = WaveExporter(repo)
            assert exporter._repo is not None

    def test_export_wave_to_markdown(self):
        tickets = [
            MicroTaskTicket(
                id="TASK-TEST-001",
                title="Test ticket",
                objective="Test objective",
                source_topic_file="test.md",
                source_line_range="1-10",
                phase=1,
                priority="High",
                estimated_effort="M",
                status="pending",
            )
        ]
        wave = TaskWave(
            id="wave-01",
            phase=1,
            description="Test wave",
            status="active",
        )

        exporter = WaveExporter.__new__(WaveExporter)
        exporter._repo = None

        markdown = export_wave_to_markdown(tickets, wave)

        assert "# Wave: wave-01" in markdown
        assert "Phase: 1" in markdown
        assert "TASK-TEST-001" in markdown
        assert "Test ticket" in markdown
        assert "**Source:**" in markdown

    def test_export_wave_to_json(self):
        tickets = [
            MicroTaskTicket(
                id="TASK-TEST-001",
                title="Test ticket",
                phase=1,
                priority="Medium",
                estimated_effort="M",
                status="pending",
            )
        ]
        wave = TaskWave(id="wave-01", phase=1, description="Test wave")

        json_output = format_wave_json(tickets, wave)
        data = json.loads(json_output)

        assert data["wave"]["id"] == "wave-01"
        assert len(data["tickets"]) == 1

    def test_export_wave_method(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            with TicketRepository(db_path) as repo:
                wave = TaskWave(id="wave-01", phase=1, description="Test wave")
                repo.insert_wave(wave)

                exporter = WaveExporter(repo)

                # Should raise for non-existent wave initially
                with pytest.raises(ValueError):
                    exporter.export_wave("nonexistent", "markdown")

    def test_export_to_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            with TicketRepository(db_path) as repo:
                wave = TaskWave(id="wave-01", phase=1, description="Test wave")
                repo.insert_wave(wave)

                tickets = [
                    MicroTaskTicket(
                        id="TASK-TEST-001",
                        title="Test",
                        objective="Obj",
                        phase=1,
                        priority="Medium",
                        estimated_effort="M",
                        status="pending",
                        wave_id="wave-01",
                    )
                ]
                for t in tickets:
                    repo.insert_ticket(t)

                exporter = WaveExporter(repo)
                output_dir = Path(tmpdir) / "output"

                paths = exporter.export_to_files("wave-01", output_dir, "markdown")

                assert len(paths) == 1
                assert paths[0].exists()