"""Tests for smart_task.schema module."""

from __future__ import annotations

import sqlite3

import pytest

from smart_task.schema import (
    CREATE_TICKETS_TABLE_SQL,
    CREATE_WAVES_TABLE_SQL,
    CREATE_MAPPINGS_TABLE_SQL,
    INDEXES_SQL,
    CURRENT_SCHEMA_VERSION,
    ensure_schema,
    get_ddl_statement,
)


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    yield c
    c.close()


class TestDDLStrings:
    def test_tickets_ddl_executes(self, conn):
        conn.execute(CREATE_TICKETS_TABLE_SQL)

    def test_waves_ddl_executes(self, conn):
        conn.execute(CREATE_WAVES_TABLE_SQL)

    def test_mappings_ddl_executes(self, conn):
        conn.execute(CREATE_MAPPINGS_TABLE_SQL)

    def test_all_ddl_together(self, conn):
        conn.execute(CREATE_TICKETS_TABLE_SQL)
        conn.execute(CREATE_WAVES_TABLE_SQL)
        conn.execute(CREATE_MAPPINGS_TABLE_SQL)
        conn.executescript(INDEXES_SQL)


class TestEnsureSchema:
    def test_creates_all_tables(self, conn):
        ensure_schema(conn)
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = {row[0] for row in cursor.fetchall()}
        for expected in ("micro_task_tickets", "task_waves", "topic_to_ticket_mapping", "schema_version"):
            assert expected in tables, f"Missing table: {expected}"

    def test_is_idempotent(self, conn):
        ensure_schema(conn)
        ensure_schema(conn)
        cursor = conn.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
        )
        count_before = cursor.fetchone()[0]
        ensure_schema(conn)
        cursor = conn.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
        )
        count_after = cursor.fetchone()[0]
        assert count_after == count_before

    def test_creates_indexes(self, conn):
        ensure_schema(conn)
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%' ORDER BY name"
        )
        indexes = {row[0] for row in cursor.fetchall()}
        expected = {
            "idx_tickets_status", "idx_tickets_phase", "idx_tickets_wave",
            "idx_tickets_priority", "idx_waves_phase", "idx_mapping_topic",
        }
        for idx in expected:
            assert idx in indexes, f"Missing index: {idx}"

    def test_records_schema_version(self, conn):
        ensure_schema(conn)
        cursor = conn.execute("SELECT MAX(version) FROM schema_version")
        version = cursor.fetchone()[0]
        assert version == CURRENT_SCHEMA_VERSION

    def test_tickets_columns(self, conn):
        ensure_schema(conn)
        cursor = conn.execute("PRAGMA table_info(micro_task_tickets)")
        columns = {row[1] for row in cursor.fetchall()}
        for col in ("id", "title", "objective", "phase", "priority", "status", "wave_id"):
            assert col in columns, f"Missing column: {col}"


class TestCheckConstraints:
    @pytest.mark.parametrize("phase", [1, 2, 3])
    def test_valid_ticket_phase(self, conn, phase):
        ensure_schema(conn)
        sql = """
            INSERT INTO micro_task_tickets
                (id, source_spec, source_topic_file, source_line_range,
                 title, objective, spec_context, phase, priority, estimated_effort)
            VALUES (?, 'spec', 'topic', '1-10', 'Test', 'Objective', 'ctx', ?, 'Medium', 'M')
        """
        conn.execute(sql, (f"TASK-IDM-00{phase}", phase))

    def test_invalid_ticket_phase(self, conn):
        ensure_schema(conn)
        sql = """
            INSERT INTO micro_task_tickets
                (id, source_spec, source_topic_file, source_line_range,
                 title, objective, spec_context, phase, priority, estimated_effort)
            VALUES (?, 'spec', 'topic', '1-10', 'Test', 'Objective', 'ctx', ?, 'Medium', 'M')
        """
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(sql, ("TASK-IDM-999", 4))

    @pytest.mark.parametrize("priority", ["High", "Medium", "Low"])
    def test_valid_ticket_priority(self, conn, priority):
        ensure_schema(conn)
        sql = """
            INSERT INTO micro_task_tickets
                (id, source_spec, source_topic_file, source_line_range,
                 title, objective, spec_context, phase, priority, estimated_effort)
            VALUES (?, 'spec', 'topic', '1-10', 'Test', 'Objective', 'ctx', 1, ?, 'M')
        """
        conn.execute(sql, (f"TASK-IDM-{priority}", priority))

    def test_invalid_ticket_priority(self, conn):
        ensure_schema(conn)
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("""
                INSERT INTO micro_task_tickets
                    (id, source_spec, source_topic_file, source_line_range,
                     title, objective, spec_context, phase, priority, estimated_effort)
                VALUES ('TASK-IDM-X01', 'spec', 'topic', '1-10', 'Test', 'Objective', 'ctx', 1, 'Urgent', 'M')
            """)

    @pytest.mark.parametrize("effort", ["S", "M", "L", "XL"])
    def test_valid_ticket_effort(self, conn, effort):
        ensure_schema(conn)
        conn.execute("""
            INSERT INTO micro_task_tickets
                (id, source_spec, source_topic_file, source_line_range,
                 title, objective, spec_context, phase, priority, estimated_effort)
            VALUES (?, 'spec', 'topic', '1-10', 'Test', 'Objective', 'ctx', 1, 'Medium', ?)
        """, (f"TASK-IDM-{effort}", effort))

    def test_invalid_ticket_effort(self, conn):
        ensure_schema(conn)
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("""
                INSERT INTO micro_task_tickets
                    (id, source_spec, source_topic_file, source_line_range,
                     title, objective, spec_context, phase, priority, estimated_effort)
                VALUES ('TASK-IDM-XXX', 'spec', 'topic', '1-10', 'Test', 'Objective', 'ctx', 1, 'Medium', 'XXL')
            """)

    @pytest.mark.parametrize("status", ["pending", "in_progress", "completed", "blocked", "cancelled"])
    def test_valid_ticket_status(self, conn, status):
        ensure_schema(conn)
        conn.execute("""
            INSERT INTO micro_task_tickets
                (id, source_spec, source_topic_file, source_line_range,
                 title, objective, spec_context, phase, priority, estimated_effort, status)
            VALUES (?, 'spec', 'topic', '1-10', 'Test', 'Objective', 'ctx', 1, 'Medium', 'M', ?)
        """, (f"TASK-IDM-{status}", status))

    def test_invalid_ticket_status(self, conn):
        ensure_schema(conn)
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("""
                INSERT INTO micro_task_tickets
                    (id, source_spec, source_topic_file, source_line_range,
                     title, objective, spec_context, phase, priority, estimated_effort, status)
                VALUES ('TASK-IDM-FAIL', 'spec', 'topic', '1-10', 'Test', 'Objective', 'ctx', 1, 'Medium', 'M', 'failed')
            """)

    @pytest.mark.parametrize("status", ["pending", "active", "completed"])
    def test_valid_wave_status(self, conn, status):
        ensure_schema(conn)
        conn.execute("""
            INSERT INTO task_waves (id, phase, description, status)
            VALUES (?, 1, 'Test wave', ?)
        """, (f"wave-{status}", status))

    def test_invalid_wave_status(self, conn):
        ensure_schema(conn)
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("""
                INSERT INTO task_waves (id, phase, description, status)
                VALUES ('wave-fail', 1, 'Test', 'failed')
            """)

    @pytest.mark.parametrize("phase", [1, 2, 3])
    def test_valid_wave_phase(self, conn, phase):
        ensure_schema(conn)
        conn.execute("""
            INSERT INTO task_waves (id, phase, description, status)
            VALUES (?, ?, 'Test wave', 'pending')
        """, (f"wave-phase-{phase}", phase))

    def test_invalid_wave_phase(self, conn):
        ensure_schema(conn)
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("""
                INSERT INTO task_waves (id, phase, description, status)
                VALUES ('wave-phase-fail', 0, 'Test', 'pending')
            """)

    @pytest.mark.parametrize("phase", [1, 2, 3])
    def test_valid_mapping_phase(self, conn, phase):
        ensure_schema(conn)
        conn.execute("""
            INSERT INTO topic_to_ticket_mapping
                (source_topic_file, sequence, title_template, objective_template, phase, effort)
            VALUES (?, ?, 'Title', 'Objective', ?, 'M')
        """, (f"phase-{phase}.md", phase, phase))

    def test_invalid_mapping_phase(self, conn):
        ensure_schema(conn)
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("""
                INSERT INTO topic_to_ticket_mapping
                    (source_topic_file, sequence, title_template, objective_template, phase, effort)
                VALUES ('invalid-phase.md', 1, 'Title', 'Objective', 0, 'M')
            """)

    @pytest.mark.parametrize("effort", ["S", "M", "L", "XL"])
    def test_valid_mapping_effort(self, conn, effort):
        ensure_schema(conn)
        conn.execute("""
            INSERT INTO topic_to_ticket_mapping
                (source_topic_file, sequence, title_template, objective_template, phase, effort)
            VALUES (?, 1, 'Title', 'Objective', 1, ?)
        """, (f"effort-{effort}.md", effort))

    def test_invalid_mapping_effort(self, conn):
        ensure_schema(conn)
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("""
                INSERT INTO topic_to_ticket_mapping
                    (source_topic_file, sequence, title_template, objective_template, phase, effort)
                VALUES ('invalid-effort.md', 1, 'Title', 'Objective', 1, 'XXXL')
            """)

    def test_mapping_unique_constraint(self, conn):
        ensure_schema(conn)
        conn.execute("""
            INSERT INTO topic_to_ticket_mapping
                (source_topic_file, sequence, title_template, objective_template, phase, effort)
            VALUES ('topic.md', 1, 'Title', 'Objective', 1, 'M')
        """)
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("""
                INSERT INTO topic_to_ticket_mapping
                    (source_topic_file, sequence, title_template, objective_template, phase, effort)
                VALUES ('topic.md', 1, 'Other', 'Other', 2, 'L')
            """)


class TestGetDdlStatement:
    def test_returns_tickets_ddl(self):
        stmt = get_ddl_statement("micro_task_tickets")
        assert "CREATE TABLE IF NOT EXISTS micro_task_tickets" in stmt

    def test_returns_waves_ddl(self):
        stmt = get_ddl_statement("task_waves")
        assert "CREATE TABLE IF NOT EXISTS task_waves" in stmt

    def test_returns_mappings_ddl(self):
        stmt = get_ddl_statement("topic_to_ticket_mapping")
        assert "CREATE TABLE IF NOT EXISTS topic_to_ticket_mapping" in stmt

    def test_invalid_table_raises(self):
        with pytest.raises(KeyError):
            get_ddl_statement("nonexistent")
