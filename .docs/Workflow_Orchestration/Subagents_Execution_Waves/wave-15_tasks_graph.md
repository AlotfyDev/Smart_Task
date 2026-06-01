# Wave 15: Tasks Graph ← Stubs + Buggy Components

## Dependency
- Depends on: Wave 10 (db_persistence.py), Wave 11 (identity_cache.py)
- Source Specs: `samples/scanner_specs/four_graphs_integration_spec.md` section 5

## Targets
Potentially modifies: `samples/parsers/tasks_parser.py`

## Scope

Rewrite the tasks graph to use `classification = 'to_be_implemented'` structural elements and the `concern_element_links` bridge table instead of the old file-stubs-plus-CSV approach.

## What to Implement

### Tasks Table DDL

```sql
CREATE TABLE IF NOT EXISTS tasks (
    id                      TEXT PRIMARY KEY,
    task_type               TEXT NOT NULL CHECK (task_type IN ('implement', 'debug')),
    target_element_id       TEXT REFERENCES structural_elements(id),
    priority                TEXT NOT NULL DEFAULT 'medium',
    status                  TEXT NOT NULL DEFAULT 'not_started',
    required_concerns       TEXT,
    bug_type                TEXT,
    proposed_fix            TEXT,
    evidence                TEXT,
    created_at              TEXT NOT NULL DEFAULT (datetime('now'))
);
```

### `create_implementation_tasks_from_db(db_path, entry_point_id) -> list[dict]`

From `four_graphs_integration_spec.md` section 5:

1. Query `structural_elements WHERE classification = 'to_be_implemented'`
2. For each stub, look up linked concerns via `concern_element_links`
3. Derive priority from highest linked concern severity
4. Return task dicts with UUID-based IDs

### `parse_buggy_components_with_db(filepath, db_path) -> list[dict]`

From `four_graphs_integration_spec.md` section 5:

1. Parse buggy_components CSV (same as before)
2. Resolve `component` field to UUID via `SELECT id FROM structural_elements WHERE relative_path = ?`
3. Return task dicts with UUID-targeted IDs

## Keep (unchanged)

- `parse_buggy_components()` — still loads raw CSV (used by `parse_buggy_components_with_db()`)
- `parse_all_buggy_components()` — still loads all CSV files
- `calculate_priority()` — priority calculation logic stays

## Remove (obsolete)

- `create_implementation_tasks()` — replaced by `create_implementation_tasks_from_db()`

## Verification

| # | Criterion |
|---|-----------|
| 1 | `create_implementation_tasks_from_db()` creates correct tasks for `to_be_implemented` elements |
| 2 | Task priority correctly derives from highest concern severity |
| 3 | `parse_buggy_components_with_db()` resolves component paths to UUIDs correctly |
| 4 | Output task dict format is backward-compatible with presentation layer |

## Delivery
Modified `samples/parsers/tasks_parser.py`
