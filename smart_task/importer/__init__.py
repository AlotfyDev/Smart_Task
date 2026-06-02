"""
Ticket file import pipeline — transforms spec topics into actionable tickets.

Exports
-------
- TopicToTicketImporter : loads mappings, parses topics, generates tickets
- load_mappings : load mapping JSON file
- import_topic_file : process one topic into tickets
- import_all : batch import all topics
"""

import json
from pathlib import Path
from typing import Any, Sequence

from smart_task.models import MicroTaskTicket, TopicToTicketMapping
from smart_task.repository import TicketRepository
from smart_task.importer.yaml_parser import parse_topic_file
from smart_task.importer.ticket_generator import create_ticket_from_mapping


class TopicToTicketImporter:
    """
    Transform topic files into micro-task tickets using mapping rules.
    """

    def __init__(self, db_path: Path | None = None, repo: TicketRepository | None = None) -> None:
        self._db_path = db_path
        self._repo = repo
        if self._repo is None:
            self._repo = TicketRepository(db_path or Path("smart_task.db"))
        self._owns_repo = repo is None

    def __enter__(self) -> "TopicToTicketImporter":
        if self._owns_repo and self._repo is None:
            self._repo = TicketRepository(self._db_path)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self._owns_repo and self._repo is not None:
            self._repo.close()
            self._repo = None

    def load_mappings(self, path: Path) -> dict[str, Any]:
        """Load the JSON mapping file that defines how topic files become tickets."""
        if not path.exists():
            raise FileNotFoundError(f"Mapping file not found: {path}")

        content = path.read_text(encoding="utf-8")
        return json.loads(content)

    def import_topic_file(
        self,
        topic_path: Path,
        mapping: dict[str, Any],
    ) -> list[MicroTaskTicket]:
        """
        Process one topic file into tickets per its mapping entry.

        Returns:
            List of MicroTaskTicket objects generated from this topic.
        """
        topic_front_matter, topic_body = parse_topic_file(topic_path)

        source_spec = topic_front_matter.get("source", "")
        spec_prefix = mapping.get("prefix", source_spec[:3].upper())

        topic_file_name = topic_path.name
        topic_mapping = mapping.get("topics", {}).get(topic_file_name, {})

        tickets: list[MicroTaskTicket] = []
        sequences = topic_mapping.get("sequences", [])

        for seq_entry in sequences:
            sequence = seq_entry.get("seq", seq_entry.get("sequence", 1))
            ticket = create_ticket_from_mapping(
                topic_file=topic_file_name,
                topic_front_matter=topic_front_matter,
                topic_body=topic_body,
                mapping_entry=seq_entry,
                spec_prefix=spec_prefix,
                sequence=sequence,
            )
            tickets.append(ticket)

        return tickets

    def import_mapping_to_db(
        self,
        mapping: dict[str, Any],
    ) -> None:
        """Insert mapping entries into topic_to_ticket_mapping table for traceability."""
        for topic_file, topic_data in mapping.get("topics", {}).items():
            for seq_entry in topic_data.get("sequences", []):
                mapping_record = TopicToTicketMapping(
                    source_topic_file=topic_file,
                    sequence=seq_entry.get("seq", seq_entry.get("sequence", 1)),
                    title_template=seq_entry.get("title", ""),
                    objective_template=seq_entry.get("objective", ""),
                    phase=seq_entry.get("phase", 1),
                    effort=seq_entry.get("effort", "M"),
                    tags=json.dumps(seq_entry.get("tags", [])),
                )
                self._repo.insert_mapping(mapping_record)

    def import_all(
        self,
        topics_dir: Path,
        mappings_path: Path,
        topic_files: Sequence[Path] | None = None,
    ) -> int:
        """
        Iterate all topic files, apply mappings, insert into DB.

        Args:
            topics_dir: Directory containing topic files (used if topic_files is None)
            mappings_path: Path to the mappings JSON file
            topic_files: Optional explicit list of topic files to import.
                        If None, discovers all *.md files in topics_dir.

        Returns:
            Total count of tickets imported.
        """
        mapping = self.load_mappings(mappings_path)
        all_tickets: list[MicroTaskTicket] = []

        if topic_files is not None:
            files_to_process = topic_files
        else:
            files_to_process = list(topics_dir.glob("*.md"))

        for topic_file in files_to_process:
            if topic_file.name in mapping.get("topics", {}):
                tickets = self.import_topic_file(topic_file, mapping)
                all_tickets.extend(tickets)

        if all_tickets:
            self._repo.insert_tickets_batch(all_tickets)

        return len(all_tickets)