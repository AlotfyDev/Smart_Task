# Data Schema & Persistence

## Overview

Smart Task uses SQLite as its persistence engine. The schema is versioned, constraint-rich, and optimized for the ticket lifecycle queries.

## Schema Versioning

```sql
CREATE TABLE schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT (datetime('now')),
    description TEXT NOT NULL
);
```

The `ensure_schema()` function:
1. Checks `MAX(version) FROM schema_version`
2. If current_ver < `CURRENT_SCHEMA_VERSION`, runs `_apply_migrations(conn, current_ver)`
3. Each migration is a sequential step (v1 → v2 → v3...)
4. After each migration, inserts a row into `schema_version`

## Tables

### `micro_task_tickets` — Core entity storage

24 columns covering: identity, traceability, content, dependencies, verification, review, organization, assignment, lifecycle.

**Key constraints:**
- `phase IN (1, 2, 3)` — only valid phases
- `priority IN ('High', 'Medium', 'Low')`
- `estimated_effort IN ('S', 'M', 'L', 'XL')`
- `status IN ('pending', 'in_progress', 'completed', 'blocked', 'cancelled')`
- `dependencies`, `file_targets`, `acceptance_criteria`, `tags` — validated as JSON via application layer (SQLite stores as TEXT)

**Indexes:**
| Index | Purpose | Used by |
|-------|---------|---------|
| `idx_tickets_status` | Filter by status | `list --status`, wave assignment |
| `idx_tickets_phase` | Filter by phase | `list --phase`, stats |
| `idx_tickets_wave` | Filter by wave | `wave show`, export |
| `idx_tickets_priority` | Sort by priority | wave assignment, `stats` |

### `task_waves` — Wave groupings

7 columns: id, phase, description, ticket_count, status, created_at, completed_at.

**Constraints:**
- `phase IN (1, 2, 3)`
- `status IN ('pending', 'active', 'completed')`

**Indexes:**
- `idx_waves_phase` — filter waves by phase

### `topic_to_ticket_mapping` — Mapping rules

8 columns: id (auto PK), source_topic_file, sequence, title_template, objective_template, phase, effort, tags.

**Constraints:**
- UNIQUE(source_topic_file, sequence)
- `phase IN (1, 2, 3)`
- `effort IN ('S', 'M', 'L', 'XL')`

**Indexes:**
- `idx_mapping_topic` — look up all tickets for a topic file

## Persistence Strategy

### Batch Insert

```python
conn.execute("BEGIN")
try:
    conn.executemany(INSERT_SQL, rows)
    conn.execute("COMMIT")
except:
    conn.execute("ROLLBACK")
    raise
```

Single transaction for atomicity. All-or-nothing. Used by:
- `TicketRepository.insert_tickets_batch()`

### Read Patterns

All reads are simple SELECTs with WHERE + ORDER BY. No complex joins needed because:
- Tickets reference waves by `wave_id` TEXT, not FK
- Dependencies are stored as JSON array, resolved in application code
- Filtering is done by indexed columns

## Query Performance

Expected volumes:
- Tickets: ~200-500 per project
- Waves: ~16-20 per project
- Mappings: ~80-157 per project

At these volumes, even unindexed full-table scans complete in <1ms. Indexes are for code clarity and future scale, not current necessity.
