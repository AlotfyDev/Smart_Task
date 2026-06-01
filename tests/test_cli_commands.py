"""
Smoke tests for CLI commands - end-to-end validation via subprocess.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


def run_cli(*args: str, db_path: str | None = None) -> tuple[int, str, str]:
    """Helper to run task-cli and capture exit code and output."""
    cmd = [sys.executable, "-m", "smart_task.cli"] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


class TestHelpCommands:
    def test_main_help_shows_all_commands(self):
        code, stdout, _ = run_cli("--help")
        assert code == 0
        assert "init" in stdout
        assert "import" in stdout
        assert "list" in stdout
        assert "get" in stdout
        assert "wave" in stdout
        assert "export" in stdout
        assert "status" in stdout
        assert "stats" in stdout

    def test_wave_subcommand_help(self):
        code, stdout, _ = run_cli("wave", "--help")
        assert code == 0
        assert "create" in stdout
        assert "assign" in stdout
        assert "show" in stdout
        assert "list" in stdout


class TestInitCommand:
    def test_init_creates_database(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_file = Path(tmpdir) / "test.db"
            code, _, _ = run_cli("init", "--db-path", str(db_file))
            assert code == 0
            assert db_file.exists()


class TestListCommand:
    def test_list_returns_empty_on_fresh_db(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_file = Path(tmpdir) / "test.db"
            run_cli("init", "--db-path", str(db_file))
            code, stdout, stderr = run_cli("list", "--format", "json", "--db-path", str(db_file))
            # Empty list returns []
            assert code == 0
            assert stdout.strip() == "[]"


class TestGetCommand:
    def test_get_nonexistent_ticket_returns_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_file = Path(tmpdir) / "test.db"
            run_cli("init", "--db-path", str(db_file))
            code, _, _ = run_cli("get", "TASK-NONEXISTENT", "--db-path", str(db_file))
            assert code == 1


class TestWaveCreate:
    def test_wave_create_exits_success(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_file = Path(tmpdir) / "test.db"
            run_cli("init", "--db-path", str(db_file))
            code, stdout, _ = run_cli("wave", "create", "--id", "test-wave", "--phase", "1", "--desc", "Test wave", "--db-path", str(db_file))
            assert code == 0
            assert "Created wave test-wave" in stdout


class TestWaveShow:
    def test_wave_show_returns_metadata(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_file = Path(tmpdir) / "test.db"
            run_cli("init", "--db-path", str(db_file))
            run_cli("wave", "create", "--id", "show-wave", "--phase", "2", "--desc", "Show test", "--db-path", str(db_file))
            code, stdout, _ = run_cli("wave", "show", "--wave", "show-wave", "--db-path", str(db_file))
            assert code == 0
            assert "show-wave" in stdout


class TestWaveList:
    def test_wave_list_returns_created_waves(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_file = Path(tmpdir) / "test.db"
            run_cli("init", "--db-path", str(db_file))
            run_cli("wave", "create", "--id", "list-wave", "--phase", "1", "--desc", "List test", "--db-path", str(db_file))
            code, stdout, _ = run_cli("wave", "list", "--db-path", str(db_file))
            assert code == 0
            assert "list-wave" in stdout


class TestStats:
    def test_stats_returns_valid_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_file = Path(tmpdir) / "test.db"
            run_cli("init", "--db-path", str(db_file))
            code, stdout, _ = run_cli("stats", "--json", "--db-path", str(db_file))
            assert code == 0
            import json
            data = json.loads(stdout)
            assert "total_tickets" in data


class TestStatusError:
    def test_status_nonexistent_returns_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_file = Path(tmpdir) / "test.db"
            run_cli("init", "--db-path", str(db_file))
            code, _, _ = run_cli("status", "TASK-NONEXISTENT", "--set", "completed", "--db-path", str(db_file))
            assert code == 1


class TestExportCommand:
    def test_export_creates_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_file = Path(tmpdir) / "test.db"
            output_dir = Path(tmpdir) / "output"
            run_cli("init", "--db-path", str(db_file))
            run_cli("wave", "create", "--id", "export-wave", "--phase", "1", "--desc", "Test", "--db-path", str(db_file))
            code, _, _ = run_cli("export", "--wave", "export-wave", "--output", str(output_dir), "--db-path", str(db_file))
            assert code == 0
            # Check markdown file was created
            md_file = output_dir / "export-wave.md"
            assert md_file.exists() or len(list(output_dir.iterdir())) > 0


class TestWaveAssign:
    def test_wave_assign_with_count_limit(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_file = Path(tmpdir) / "test.db"
            run_cli("init", "--db-path", str(db_file))
            run_cli("wave", "create", "--id", "assign-wave", "--phase", "1", "--desc", "Test", "--db-path", str(db_file))
            # No tickets to assign, should return 0
            code, stdout, _ = run_cli("wave", "assign", "--wave", "assign-wave", "--count", "5", "--db-path", str(db_file))
            assert code == 0
            assert "Assigned 0 tickets" in stdout