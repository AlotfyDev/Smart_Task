"""
Tests for TopicToTicketImporter functionality.
"""

import json
import pytest
from pathlib import Path
import tempfile

from smart_task.importer import TopicToTicketImporter
from smart_task.repository import TicketRepository
from smart_task.models import MicroTaskTicket


class TestTopicToTicketImporter:
    """Test TopicToTicketImporter class."""

    def test_init_creates_repository(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            importer = TopicToTicketImporter(db_path)
            importer._repo.close()
            assert importer._repo is not None

    def test_load_mappings(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mapping_path = Path(tmpdir) / "mappings.json"
            mapping_data = {
                "prefix": "IDM",
                "topics": {
                    "test_topic.md": {
                        "sequences": [{"seq": 1, "title": "Test"}]
                    }
                }
            }
            mapping_path.write_text(json.dumps(mapping_data), encoding="utf-8")

            importer = TopicToTicketImporter(Path(tmpdir) / "test.db")
            loaded = importer.load_mappings(mapping_path)
            importer._repo.close()

            assert loaded["prefix"] == "IDM"
            assert "test_topic.md" in loaded["topics"]

    def test_import_topic_file_generates_ticket(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            topic_path = Path(tmpdir) / "test_topic.md"
            topic_content = """---
source: identity_model_spec.md
start_line: 11
end_line: 28
---
# Test Topic Content"""
            topic_path.write_text(topic_content, encoding="utf-8")

            mapping = {
                "prefix": "IDM",
                "topics": {
                    "test_topic.md": {
                        "sequences": [{"seq": 1, "title": "Create DDL"}]
                    }
                }
            }

            importer = TopicToTicketImporter(Path(tmpdir) / "test.db")
            tickets = importer.import_topic_file(topic_path, mapping)

            assert len(tickets) == 1
            assert tickets[0].id == "TASK-IDM-001"
            assert tickets[0].source_spec == "identity_model_spec.md"

    def test_import_topic_file_multiple_sequences(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            topic_path = Path(tmpdir) / "test_topic.md"
            topic_path.write_text("---\nsource: test.md\n---\nContent", encoding="utf-8")

            mapping = {
                "prefix": "TST",
                "topics": {
                    "test_topic.md": {
                        "sequences": [{"seq": 1}, {"seq": 2}, {"seq": 3}]
                    }
                }
            }

            importer = TopicToTicketImporter(Path(tmpdir) / "test.db")
            tickets = importer.import_topic_file(topic_path, mapping)

            assert len(tickets) == 3
            assert tickets[0].id == "TASK-TST-001"
            assert tickets[1].id == "TASK-TST-002"
            assert tickets[2].id == "TASK-TST-003"

    def test_import_all_with_explicit_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"

            # Create mapping file - unique IDs per topic
            mapping_path = Path(tmpdir) / "mappings.json"
            mapping_data = {
                "prefix": "TST",
                "topics": {
                    "topic1.md": {"sequences": [{"seq": 1}]},
                    "topic2.md": {"sequences": [{"seq": 2}]},
                }
            }
            mapping_path.write_text(json.dumps(mapping_data), encoding="utf-8")

            # Create topic files
            Path(tmpdir, "topic1.md").write_text("---\nsource: topic1.md\n---\nContent", encoding="utf-8")
            Path(tmpdir, "topic2.md").write_text("---\nsource: topic2.md\n---\nContent", encoding="utf-8")

            importer = TopicToTicketImporter(db_path)
            topic_files = [
                Path(tmpdir) / "topic1.md",
                Path(tmpdir) / "topic2.md",
            ]
            count = importer.import_all(Path(tmpdir), mapping_path, topic_files=topic_files)

            assert count == 2

            # Verify tickets in same connection
            all_tickets = importer._repo.list_tickets()
            assert len(all_tickets) == 2
            importer._repo.close()

    def test_context_manager(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"

            with TopicToTicketImporter(db_path) as importer:
                assert importer._repo is not None
                assert importer._owns_repo is True

            # After context exit, repo should be closed
            assert importer._repo is None