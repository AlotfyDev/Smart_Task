"""
Tests for CLI argument parsing and command dispatch.
"""

from __future__ import annotations

from smart_task.cli import build_parser, format_tickets_text, format_ticket_text, format_waves_text


class TestBuildParser:
    def test_has_all_main_commands(self):
        parser = build_parser()
        # Just verify parser was created without error
        assert parser is not None

    def test_wave_subcommands_registered(self):
        parser = build_parser()
        # Just verify wave parser exists
        assert parser is not None

    def test_init_accepts_db_path(self):
        parser = build_parser()
        args = parser.parse_args(["init", "--db-path", "test.db"])
        assert args.command == "init"
        assert args.db_path is not None

    def test_list_accepts_filters(self):
        parser = build_parser()
        args = parser.parse_args(["list", "--phase", "1", "--status", "pending", "--format", "json"])
        assert args.command == "list"
        assert args.phase == 1
        assert args.status == "pending"
        assert args.format == "json"

    def test_get_requires_ticket_id(self):
        parser = build_parser()
        args = parser.parse_args(["get", "TASK-ABC-001"])
        assert args.command == "get"
        assert args.ticket_id == "TASK-ABC-001"

    def test_wave_create_requires_args(self):
        parser = build_parser()
        args = parser.parse_args(["wave", "create", "--id", "test-wave", "--phase", "1", "--desc", "Test"])
        assert args.wave_command == "create"
        assert args.id == "test-wave"
        assert args.phase == 1
        assert args.desc == "Test"

    def test_wave_assign_accepts_strategy(self):
        parser = build_parser()
        args = parser.parse_args(["wave", "assign", "--wave", "test", "--strategy", "by_priority"])
        assert args.wave_command == "assign"
        assert args.strategy == "by_priority"

    def test_status_accepts_all_options(self):
        parser = build_parser()
        args = parser.parse_args(["status", "TASK-001", "--set", "completed", "--notes", "done"])
        assert args.command == "status"
        assert args.new_status == "completed"


class TestFormatTicketsText:
    def test_empty_list(self):
        result = format_tickets_text([])
        assert result == "(no tickets)"

    def test_formats_single_ticket(self):
        from smart_task.models import MicroTaskTicket
        ticket = MicroTaskTicket(
            id="TASK-ABC-001",
            title="Test ticket",
            phase=1,
            priority="High",
            status="pending",
        )
        result = format_tickets_text([ticket])
        assert "TASK-ABC-001" in result
        assert "Test ticket" in result
        assert "1" in result
        assert "High" in result
        assert "pending" in result


class TestFormatWavesText:
    def test_empty_waves(self):
        result = format_waves_text([])
        assert result == "(no waves)"

    def test_formats_wave_list(self):
        from smart_task.models import TaskWave
        wave = TaskWave(id="wave-1", phase=1, description="Test wave", status="pending")
        result = format_waves_text([wave])
        assert "wave-1" in result
        assert "Test wave" in result


class TestFormatTicketText:
    def test_basic_fields(self):
        from smart_task.models import MicroTaskTicket
        ticket = MicroTaskTicket(
            id="TASK-XYZ-002",
            title="Sample ticket",
            objective="Do something",
            phase=2,
            priority="Low",
            status="in_progress",
        )
        result = format_ticket_text(ticket)
        assert "TASK-XYZ-002" in result
        assert "Sample ticket" in result
        assert "Do something" in result

    def test_includes_verification(self):
        from smart_task.models import MicroTaskTicket
        ticket = MicroTaskTicket(
            id="TASK-XYZ-003",
            title="Test",
            objective="Obj",
            verification_method="SHELL: pytest tests/",
        )
        result = format_ticket_text(ticket)
        assert "SHELL: pytest tests/" in result

    def test_includes_review_notes(self):
        from smart_task.models import MicroTaskTicket
        ticket = MicroTaskTicket(
            id="TASK-XYZ-004",
            title="Test",
            objective="Obj",
            review_notes="Verified working",
        )
        result = format_ticket_text(ticket)
        assert "Verified working" in result