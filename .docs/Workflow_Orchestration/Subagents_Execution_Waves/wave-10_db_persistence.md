# Wave 10: DB Persistence

## Dependency
- Depends on: Wave 7 (identity_model.py — needs `StructuralElement`)
- Source Specs: `samples/scanner_specs/db_persistence_spec.md`

## Target
`samples/scanner/db_persistence.py` (new file)

## Scope

Implement the SQLite persistence layer that writes `IdentityCache` contents to the `structural_elements` table, manages schema versioning, and provides JSON1 query patterns.

## What to Implement

### `persist_to_db(cache: IdentityCache, db_path: Path) -> int`

From `db_persistence_spec.md` section 4. Single transaction batch insert:

1. `db_path.parent.mkdir(parents=True, exist_ok=True)`
2. Connect with `PRAGMA journal_mode=WAL`, `PRAGMA synchronous=NORMAL`
3. Call `ensure_schema(conn)`
4. `PRAGMA foreign_keys=OFF`
5. `BEGIN TRANSACTION`
6. `DELETE FROM structural_elements WHERE entry_point_id = ?` (re-scan)
7. Sort elements: entry point first (FK dependency), then by depth
8. `executemany` INSERT
9. `COMMIT` / `ROLLBACK` on error
10. `PRAGMA foreign_keys=ON`
11. Return row count

### `persist_to_db_chunked(cache, db_path, chunk_size=5000) -> int`

Chunked variant for larger scans (>5000 elements).

### DDL from `db_persistence_spec.md` section 2:

```sql
CREATE TABLE structural_elements (
    id              TEXT PRIMARY KEY,
    entity_type     TEXT NOT NULL CHECK (entity_type IN ('entry_point', 'folder', 'file')),
    parent_id       TEXT REFERENCES structural_elements(id) ON DELETE SET NULL,
    entry_point_id  TEXT NOT NULL REFERENCES structural_elements(id) ON DELETE CASCADE,
    ancestry_ids    TEXT NOT NULL CHECK (json_valid(ancestry_ids)),
    ancestry_names  TEXT NOT NULL CHECK (json_valid(ancestry_names)),
    name            TEXT NOT NULL,
    relative_path   TEXT NOT NULL,
    topo_key        TEXT,
    depth           INTEGER NOT NULL DEFAULT 0 CHECK (depth >= 0),
    sort_order      INTEGER NOT NULL DEFAULT 0 CHECK (sort_order >= 0),
    classification  TEXT NOT NULL DEFAULT 'exists' CHECK (classification IN ('exists', 'to_be_implemented')),
    file_extension  TEXT,
    file_size       INTEGER CHECK (file_size IS NULL OR file_size >= 0),
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
```

With all indexes from section 2.

### `class DatabaseManager`

Context manager for database connection with retry logic:

```python
class DatabaseManager:
    def __init__(self, db_path: Path): ...
    def connect(self) -> sqlite3.Connection: ...
    def close(self): ...
    def __enter__ -> sqlite3.Connection: ...
    def __exit__: ...
```

### `ensure_schema(conn) -> None`

Create/upgrade schema using `schema_version` table.

### `backup_db(db_path, backup_path=None) -> Path`

File-copy backup with timestamped default name.

### Query functions from `db_persistence_spec.md` section 5:

```python
def get_ancestors(conn, element_id: str) -> list[dict]: ...
def get_descendants(conn, element_id: str) -> list[dict]: ...
def get_by_depth(conn, max_depth: int) -> list[dict]: ...
def get_siblings(conn, element_id: str) -> list[dict]: ...
def count_by_type(conn) -> dict: ...
def get_by_extension(conn, ext: str) -> list[dict]: ...
```

## Verification

| # | Criterion |
|---|-----------|
| 1 | `persist_to_db()` with test cache creates valid DB with correct rows |
| 2 | All indexes present: `SELECT * FROM sqlite_master WHERE type='index'` |
| 3 | `get_ancestors()` returns correct chain for a nested element |
| 4 | Re-scan replaces old data, doesn't accumulate duplicates |
| 5 | `DatabaseManager` context manager works correctly |
| 6 | `ensure_schema()` with missing DB file creates all tables |

## Delivery
Single file: `samples/scanner/db_persistence.py`
