"""
Handler implementations — thin wrappers that delegate to smart_task core.

Each handler:
  - Receives domain objects (repo, wm) + primitive parameters
  - Returns a JSON-serialisable string
  - Raises ValueError on invalid input, RuntimeError on system failure
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def handle_init_database(repo, db_path: str) -> str:
    repo.ensure_schema()
    return json.dumps({"status": "ok", "db_path": db_path})


def handle_import_topics(repo, topic_dir: str, mappings: str) -> str:
    from smart_task.importer import TopicToTicketImporter

    importer = TopicToTicketImporter(repo=repo)
    count = importer.import_all(Path(topic_dir), Path(mappings))
    return json.dumps({"status": "ok", "tickets_imported": count})


def handle_list_tickets(repo, phase: int | None, status: str | None, wave_id: str | None) -> str:
    tickets = repo.list_tickets(phase=phase, status=status, wave_id=wave_id)
    return json.dumps([t.to_dict() for t in tickets], default=str, ensure_ascii=False)


def handle_get_ticket(repo, ticket_id: str) -> str:
    ticket = repo.get_ticket(ticket_id)
    if ticket is None:
        raise ValueError(f"ticket {ticket_id} not found")
    return json.dumps(ticket.to_dict(), default=str, ensure_ascii=False)


def handle_create_wave(wm, wave_id: str, phase: int, description: str) -> str:
    wave = wm.create_wave(wave_id, phase, description)
    return json.dumps(wave.to_dict(), default=str, ensure_ascii=False)


def handle_assign_tickets(wm, wave_id: str, count: int | None, strategy: str) -> str:
    assigned = wm.assign_tickets(wave_id, count=count, strategy=strategy)
    return json.dumps({"wave_id": wave_id, "assigned": assigned})


def handle_show_wave(wm, wave_id: str) -> str:
    summary = wm.get_wave_summary(wave_id)
    return json.dumps(summary, default=str, ensure_ascii=False)


def handle_list_waves(repo, phase: int | None) -> str:
    waves = repo.list_waves(phase=phase)
    return json.dumps([w.to_dict() for w in waves], default=str, ensure_ascii=False)


def handle_export_wave(repo, wm, wave_id: str, format: str, output_dir: str) -> str:
    from smart_task.exporter import WaveExporter

    exporter = WaveExporter(repo)
    files = exporter.export_to_files(wave_id, Path(output_dir), format)
    return json.dumps({"files": [str(f) for f in files]}, ensure_ascii=False)


def handle_update_ticket_status(
    repo, ticket_id: str, status: str, notes: str | None, blocker: str | None
) -> str:
    valid = {"pending", "in_progress", "completed", "blocked", "cancelled"}
    if status not in valid:
        raise ValueError(f"invalid status '{status}'; must be one of {sorted(valid)}")

    effective_status = "blocked" if blocker else status
    kwargs = {"review_notes": notes} if notes else {}
    if blocker:
        kwargs["blocker_reason"] = blocker

    repo.update_ticket_status(ticket_id, effective_status, **kwargs)

    ticket = repo.get_ticket(ticket_id)
    return json.dumps(ticket.to_dict(), default=str, ensure_ascii=False)


def handle_get_project_stats(wm) -> str:
    stats = wm.get_project_summary()
    return json.dumps(stats, default=str, ensure_ascii=False)
