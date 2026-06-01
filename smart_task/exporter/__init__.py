"""
Export waves and tickets to human-readable (Markdown) or structured (JSON)
formats.

Exports
-------
- WaveExporter : produces formatted output for a single wave
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from smart_task.models import MicroTaskTicket, TaskWave
from smart_task.repository import TicketRepository
from smart_task.exporter.markdown import export_wave_to_markdown
from smart_task.exporter.json_format import format_wave_json
from smart_task.exporter.file_writer import write_ticket_files


class WaveExporter:
    """
    Produce Markdown or JSON representations of a wave and its tickets.
    """

    def __init__(self, repository: TicketRepository) -> None:
        self._repo = repository

    def export_wave(self, wave_id: str, output_format: str = "markdown") -> str:
        """
        Main dispatcher for wave export.

        Args:
            wave_id: The wave identifier
            output_format: 'markdown' or 'json'

        Returns:
            Formatted string (markdown or JSON)
        """
        wave = self._repo.get_wave(wave_id)
        if wave is None:
            raise ValueError(f"Wave {wave_id} not found")

        tickets = self._repo.list_tickets(wave_id=wave_id)

        if output_format == "markdown":
            return export_wave_to_markdown(tickets, wave)
        elif output_format == "json":
            return format_wave_json(tickets, wave)
        else:
            raise ValueError(f"Unknown format: {output_format}")

    def export_to_files(
        self,
        wave_id: str,
        output_dir: Path,
        output_format: str = "markdown",
    ) -> list[Path]:
        """
        Export wave to files in output_dir.

        Args:
            wave_id: The wave identifier
            output_dir: Directory to write files
            output_format: 'markdown' or 'json'

        Returns:
            List of created file paths
        """
        wave = self._repo.get_wave(wave_id)
        if wave is None:
            raise ValueError(f"Wave {wave_id} not found")

        tickets = self._repo.list_tickets(wave_id=wave_id)

        output_dir.mkdir(parents=True, exist_ok=True)

        if output_format == "json":
            return write_ticket_files(output_dir, tickets)
        else:
            wave_path = output_dir / f"{wave_id}.md"
            content = export_wave_to_markdown(tickets, wave)
            wave_path.write_text(content, encoding="utf-8")
            return [wave_path]