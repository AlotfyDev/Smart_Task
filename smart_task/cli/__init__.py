"""
Command-line interface for the smart-task system.

Commands
--------
init      : create the database and schema
import    : import topic files from a directory
list      : list tickets with optional filters
get       : show a single ticket
wave      : wave sub-commands (create, assign, show, list)
export    : export a wave as markdown or JSON
status    : update a ticket's status
stats     : show project-level statistics
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from smart_task.config import load_config, DEFAULT_DB_PATH
from smart_task.exporter import WaveExporter
from smart_task.importer import TopicToTicketImporter
from smart_task.models import MicroTaskTicket, TaskWave
from smart_task.repository import TicketRepository
from smart_task.wave_manager import WaveManager


def build_parser() -> argparse.ArgumentParser:
    """Create and configure the argparse parser with all commands and subcommands."""
    parser = argparse.ArgumentParser(
        prog="task-cli",
        description="Micro-task ticket system for specification-driven implementation orchestration",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init command
    init_parser = subparsers.add_parser("init", help="Create database and schema")
    init_parser.add_argument("--db-path", type=Path, default=None, help="Database file path")

    # import command
    import_parser = subparsers.add_parser("import", help="Import topic files into tickets")
    import_parser.add_argument("--topic-dir", type=Path, required=True, help="Topic files directory")
    import_parser.add_argument("--mappings", type=Path, required=False, help="Mapping rules JSON path")
    import_parser.add_argument("--db-path", type=Path, default=None, help="Database file path")

    # list command
    list_parser = subparsers.add_parser("list", help="List tickets with optional filters")
    list_parser.add_argument("--phase", type=int, choices=[1, 2, 3], help="Filter by phase")
    list_parser.add_argument("--status", type=str, choices=["pending", "in_progress", "completed", "blocked", "cancelled"], help="Filter by status")
    list_parser.add_argument("--wave", type=str, dest="wave_id", help="Filter by wave ID")
    list_parser.add_argument("--format", type=str, choices=["json", "text"], default="text", help="Output format")
    list_parser.add_argument("--db-path", type=Path, default=None, help="Database file path")

    # get command
    get_parser = subparsers.add_parser("get", help="Show a single ticket")
    get_parser.add_argument("ticket_id", type=str, help="Ticket ID to retrieve")
    get_parser.add_argument("--format", type=str, choices=["json", "text"], default="text", help="Output format")
    get_parser.add_argument("--db-path", type=Path, default=None, help="Database file path")

    # wave subcommands
    wave_parser = subparsers.add_parser("wave", help="Wave management commands")
    wave_subparsers = wave_parser.add_subparsers(dest="wave_command", help="Wave actions")

    wave_create = wave_subparsers.add_parser("create", help="Create a new wave")
    wave_create.add_argument("--id", type=str, required=True, help="Wave ID")
    wave_create.add_argument("--phase", type=int, required=True, choices=[1, 2, 3], help="Wave phase")
    wave_create.add_argument("--desc", type=str, required=True, help="Wave description")
    wave_create.add_argument("--db-path", type=Path, default=None, help="Database file path")

    wave_assign = wave_subparsers.add_parser("assign", help="Assign tickets to a wave")
    wave_assign.add_argument("--wave", type=str, required=True, help="Wave ID to assign tickets to")
    wave_assign.add_argument("--count", type=int, default=None, help="Max tickets to assign")
    wave_assign.add_argument("--strategy", type=str, choices=["by_dependency", "by_priority", "balanced"], default="by_dependency", help="Assignment strategy")
    wave_assign.add_argument("--db-path", type=Path, default=None, help="Database file path")

    wave_show = wave_subparsers.add_parser("show", help="Show wave summary")
    wave_show.add_argument("--wave", type=str, required=True, help="Wave ID to show")
    wave_show.add_argument("--format", type=str, choices=["json", "text"], default="text", help="Output format")
    wave_show.add_argument("--db-path", type=Path, default=None, help="Database file path")

    wave_list = wave_subparsers.add_parser("list", help="List all waves")
    wave_list.add_argument("--phase", type=int, choices=[1, 2, 3], help="Filter by phase")
    wave_list.add_argument("--db-path", type=Path, default=None, help="Database file path")

    # export command
    export_parser = subparsers.add_parser("export", help="Export a wave as deliverable")
    export_parser.add_argument("--wave", type=str, required=True, help="Wave ID to export")
    export_parser.add_argument("--format", type=str, choices=["markdown", "json"], default="markdown", help="Output format")
    export_parser.add_argument("--output", type=Path, default=None, help="Output directory")
    export_parser.add_argument("--db-path", type=Path, default=None, help="Database file path")

    # status command
    status_parser = subparsers.add_parser("status", help="Update ticket status")
    status_parser.add_argument("ticket_id", type=str, help="Ticket ID to update")
    status_parser.add_argument("--set", type=str, required=True, dest="new_status", choices=["pending", "in_progress", "completed", "blocked", "cancelled"], help="New status")
    status_parser.add_argument("--notes", type=str, default=None, help="Review notes")
    status_parser.add_argument("--blocker", type=str, default=None, help="Blocker reason (auto-sets blocked)")
    status_parser.add_argument("--db-path", type=Path, default=None, help="Database file path")

    # stats command
    stats_parser = subparsers.add_parser("stats", help="Show project statistics")
    stats_parser.add_argument("--phase", type=int, choices=[1, 2, 3], help="Filter by phase")
    stats_parser.add_argument("--json", action="store_true", help="JSON output format")
    stats_parser.add_argument("--db-path", type=Path, default=None, help="Database file path")

    return parser


def format_tickets_text(tickets: list[MicroTaskTicket]) -> str:
    """Format tickets as aligned text table."""
    if not tickets:
        return "(no tickets)"

    lines = []
    header = f"{'ID':<20} {'Title':<40} {'Phase':<6} {'Priority':<10} {'Status':<12}"
    lines.append(header)
    lines.append("-" * len(header))

    for ticket in tickets:
        line = f"{ticket.id:<20} {ticket.title[:38]:<40} {ticket.phase:<6} {ticket.priority:<10} {ticket.status:<12}"
        lines.append(line)

    return "\n".join(lines)


def format_ticket_text(ticket: MicroTaskTicket) -> str:
    """Format single ticket as readable text sections."""
    lines = [
        f"ID: {ticket.id}",
        f"Title: {ticket.title}",
        f"Phase: {ticket.phase}",
        f"Priority: {ticket.priority}",
        f"Status: {ticket.status}",
        f"Effort: {ticket.estimated_effort}",
        "",
        "Objective:",
        ticket.objective,
    ]

    if ticket.source_spec:
        lines.extend(["", f"Source: {ticket.source_spec}"])
    if ticket.source_topic_file:
        lines.append(f"Topic: {ticket.source_topic_file}")
    if ticket.source_line_range:
        lines.append(f"Lines: {ticket.source_line_range}")

    if ticket.verification_method:
        lines.extend(["", "Verification:", ticket.verification_method])
    if ticket.review_notes:
        lines.extend(["", "Review Notes:", ticket.review_notes])
    if ticket.blocker_reason:
        lines.extend(["", "Blocker:", ticket.blocker_reason])

    return "\n".join(lines)


def format_wave_text(summary: dict) -> str:
    """Format wave summary dict as readable text."""
    lines = [
        f"ID: {summary['id']}",
        f"Phase: {summary['phase']}",
        f"Description: {summary['description']}",
        f"Status: {summary['status']}",
        f"Tickets: {summary['ticket_count']}",
    ]
    return "\n".join(lines)


def format_waves_text(waves: list[TaskWave]) -> str:
    """Format waves list as aligned text table."""
    if not waves:
        return "(no waves)"

    lines = []
    header = f"{'ID':<20} {'Phase':<6} {'Status':<12} {'Description':<40}"
    lines.append(header)
    lines.append("-" * len(header))

    for wave in waves:
        desc = wave.description[:38] if wave.description else ""
        line = f"{wave.id:<20} {wave.phase:<6} {wave.status:<12} {desc:<40}"
        lines.append(line)

    return "\n".join(lines)


def handle_init(args: argparse.Namespace) -> int:
    """Handle init command - create database and schema."""
    db_path = args.db_path if args.db_path else DEFAULT_DB_PATH
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with TicketRepository(db_path) as repo:
            repo.ensure_schema()
        print(f"Database initialized at {db_path}")
        return 0
    except Exception as e:
        print(f"Error: Failed to initialize database: {e}")
        return 2


def handle_import(args: argparse.Namespace) -> int:
    """Handle import command - import topic files."""
    db_path = args.db_path if args.db_path else DEFAULT_DB_PATH
    mappings_path = args.mappings if args.mappings else args.topic_dir.parent / "topic_to_ticket_mappings.json"

    try:
        with TicketRepository(db_path) as repo:
            importer = TopicToTicketImporter(db_path, repo)
            count = importer.import_all(args.topic_dir, mappings_path)
        print(f"Imported {count} tickets from topic files")
        return 0
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Error: Import failed: {e}")
        return 2


def handle_list(args: argparse.Namespace) -> int:
    """Handle list command - list tickets with filters."""
    db_path = args.db_path if args.db_path else DEFAULT_DB_PATH

    try:
        with TicketRepository(db_path) as repo:
            tickets = repo.list_tickets(phase=args.phase, status=args.status, wave_id=args.wave_id)

        if args.format == "json":
            output = [t.to_dict() for t in tickets]
            print(json.dumps(output, indent=2))
        else:
            print(format_tickets_text(tickets))

        return 0
    except Exception as e:
        print(f"Error: Failed to list tickets: {e}")
        return 2


def handle_get(args: argparse.Namespace) -> int:
    """Handle get command - show single ticket."""
    db_path = args.db_path if args.db_path else DEFAULT_DB_PATH

    try:
        with TicketRepository(db_path) as repo:
            ticket = repo.get_ticket(args.ticket_id)

        if ticket is None:
            print(f"Error: ticket {args.ticket_id} not found")
            return 1

        if args.format == "json":
            print(json.dumps(ticket.to_dict(), indent=2))
        else:
            print(format_ticket_text(ticket))

        return 0
    except Exception as e:
        print(f"Error: Failed to get ticket: {e}")
        return 2


def handle_wave_create(args: argparse.Namespace) -> int:
    """Handle wave create subcommand."""
    db_path = args.db_path if args.db_path else DEFAULT_DB_PATH

    try:
        with TicketRepository(db_path) as repo:
            manager = WaveManager(repo)
            manager.create_wave(args.id, args.phase, args.desc)
        print(f"Created wave {args.id}")
        return 0
    except Exception as e:
        print(f"Error: Failed to create wave: {e}")
        return 2


def handle_wave_assign(args: argparse.Namespace) -> int:
    """Handle wave assign subcommand."""
    db_path = args.db_path if args.db_path else DEFAULT_DB_PATH

    try:
        with TicketRepository(db_path) as repo:
            manager = WaveManager(repo)
            count = manager.assign_tickets(args.wave, args.count, args.strategy)
        print(f"Assigned {count} tickets to wave {args.wave}")
        return 0
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Error: Failed to assign tickets: {e}")
        return 2


def handle_wave_show(args: argparse.Namespace) -> int:
    """Handle wave show subcommand."""
    db_path = args.db_path if args.db_path else DEFAULT_DB_PATH

    try:
        with TicketRepository(db_path) as repo:
            manager = WaveManager(repo)
            summary = manager.get_wave_summary(args.wave)

        if args.format == "json":
            print(json.dumps(summary, indent=2))
        else:
            print(format_wave_text(summary))

        return 0
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Error: Failed to show wave: {e}")
        return 2


def handle_wave_list(args: argparse.Namespace) -> int:
    """Handle wave list subcommand."""
    db_path = args.db_path if args.db_path else DEFAULT_DB_PATH

    try:
        with TicketRepository(db_path) as repo:
            manager = WaveManager(repo)
            waves = manager.list_waves(phase=args.phase)

        print(format_waves_text(waves))
        return 0
    except Exception as e:
        print(f"Error: Failed to list waves: {e}")
        return 2


def handle_export(args: argparse.Namespace) -> int:
    """Handle export command - export wave to files."""
    db_path = args.db_path if args.db_path else DEFAULT_DB_PATH
    output_dir = args.output if args.output else Path(f"./waves/{args.wave}")

    try:
        with TicketRepository(db_path) as repo:
            exporter = WaveExporter(repo)
            paths = exporter.export_to_files(args.wave, output_dir, args.format)
        print(f"Exported {len(paths)} file(s) to {output_dir}")
        return 0
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Error: Failed to export wave: {e}")
        return 2


def handle_status(args: argparse.Namespace) -> int:
    """Handle status command - update ticket status."""
    db_path = args.db_path if args.db_path else DEFAULT_DB_PATH

    try:
        with TicketRepository(db_path) as repo:
            repo.update_ticket_status(
                args.ticket_id,
                args.new_status,
                review_notes=args.notes,
                blocker_reason=args.blocker,
            )
        if args.blocker:
            print(f"Set ticket {args.ticket_id} to blocked: {args.blocker}")
        else:
            print(f"Set ticket {args.ticket_id} to {args.new_status}")
        return 0
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Error: Failed to update status: {e}")
        return 2


def handle_stats(args: argparse.Namespace) -> int:
    """Handle stats command - show project statistics."""
    db_path = args.db_path if args.db_path else DEFAULT_DB_PATH

    try:
        with TicketRepository(db_path) as repo:
            manager = WaveManager(repo)
            summary = manager.get_project_summary()

        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            print(f"Total tickets: {summary['total_tickets']}")
            print(f"Completion: {summary['completion_pct']:.1f}%")
            print("\nBy Phase:")
            for phase, count in summary['by_phase'].items():
                print(f"  Phase {phase}: {count}")
            print("\nBy Status:")
            for status, count in summary['by_status'].items():
                print(f"  {status}: {count}")

        return 0
    except Exception as e:
        print(f"Error: Failed to get stats: {e}")
        return 2


def main() -> None:
    """Entry point registered as ``task-cli`` in pyproject.toml."""
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "init":
            exit_code = handle_init(args)
        elif args.command == "import":
            exit_code = handle_import(args)
        elif args.command == "list":
            exit_code = handle_list(args)
        elif args.command == "get":
            exit_code = handle_get(args)
        elif args.command == "wave":
            if not args.wave_command:
                print("Error: wave requires a subcommand (create, assign, show, list)")
                sys.exit(1)
            if args.wave_command == "create":
                exit_code = handle_wave_create(args)
            elif args.wave_command == "assign":
                exit_code = handle_wave_assign(args)
            elif args.wave_command == "show":
                exit_code = handle_wave_show(args)
            elif args.wave_command == "list":
                exit_code = handle_wave_list(args)
            else:
                print(f"Error: unknown wave subcommand {args.wave_command}")
                exit_code = 1
        elif args.command == "export":
            exit_code = handle_export(args)
        elif args.command == "status":
            exit_code = handle_status(args)
        elif args.command == "stats":
            exit_code = handle_stats(args)
        else:
            print(f"Error: unknown command {args.command}")
            exit_code = 1

    except Exception:
        print("Error: Unexpected system error")
        exit_code = 2

    sys.exit(exit_code)