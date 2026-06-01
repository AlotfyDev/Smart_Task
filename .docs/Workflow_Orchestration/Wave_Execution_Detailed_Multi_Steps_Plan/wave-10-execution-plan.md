# Wave 10 Execution Plan: DB Persistence

**Generated:** 2026-05-31  
**Status:** READY FOR IMPLEMENTATION  
**Dependency:** Wave 7 (identity_model.py) COMPLETE  
**Target:** `<CONFIGURABLE>/db_persistence.py` (see Configuration section)

---

## Configuration

### Path Configuration

Database paths are configurable via:

| Source | Description |
|--------|-------------|
| CLI `--db-path` | Database file path override |
| `SMART_TASK_DB_PATH` env var | Default database location |
| `IdentityCache` consumers | Pass db_path parameter |
| Configuration file | Custom path mappings |

---

## Required Implementation

| Component | Spec Requirement | Status |
|-----------|------------------|--------|
| `persist_to_db()` | Single transaction batch insert | ❌ MISSING |
| `persist_to_db_chunked()` | Chunked variant for >5000 items | ❌ MISSING |
| `structural_elements` DDL | 16 columns with constraints | ❌ MISSING |
| `DatabaseManager` class | Context manager with pragmas | ❌ MISSING |
| `ensure_schema()` | Schema version management | ❌ MISSING |
| `backup_db()` | File copy backup | ❌ MISSING |
| Query functions | ancestors, descendants, depth, etc. | ❌ MISSING |

---

## Step 1: Define Structural Elements DDL

### Tasks

- [ ] Create `STRUCTURAL_ELEMENTS_DDL` with 16 columns
- [ ] Create indexes: `idx_se_parent_id`, `idx_se_entry_point_id`, `idx_se_entity_type`, `idx_se_depth`, `idx_se_relative_path`, `idx_se_ancestry_ids`

---

## Step 2: Implement DatabaseManager Class

- [ ] `__init__(self, db_path: Path)`: store path
- [ ] `connect()`: create dirs, connect, set pragmas
- [ ] `close()`: close connection
- [ ] `__enter__()` / `__exit__()`: context manager

---

## Step 3: Implement `ensure_schema()`

- [ ] Create `schema_version` table
- [ ] Check current version
- [ ] Apply migrations
- [ ] Create `structural_elements` table

---

## Step 4: Implement `persist_to_db()`

### Algorithm

```python
def persist_to_db(cache: IdentityCache, db_path: Path) -> int:
```

- [ ] mkdir parent dirs
- [ ] Connect with pragmas
- [ ] `ensure_schema(conn)`
- [ ] `PRAGMA foreign_keys=OFF`
- [ ] `BEGIN TRANSACTION`
- [ ] `DELETE FROM structural_elements WHERE entry_point_id = ?`
- [ ] Sort: entry point first, then by depth
- [ ] `executemany(INSERT...)`
- [ ] `COMMIT` / `ROLLBACK` on error
- [ ] `PRAGMA foreign_keys=ON`
- [ ] Return row count

---

## Step 5: Implement `persist_to_db_chunked()`

- [ ] Default `chunk_size=5000`
- [ ] Process in batches
- [ ] Multiple transactions

---

## Step 6: Implement Query Functions

- [ ] `get_ancestors(conn, element_id)`
- [ ] `get_descendants(conn, element_id)`
- [ ] `get_by_depth(conn, max_depth)`
- [ ] `get_siblings(conn, element_id)`
- [ ] `count_by_type(conn)`
- [ ] `get_by_extension(conn, ext)`
- [ ] `get_structural_element(conn, element_id)` — returns `None` if not found

---

## Step 7: Verification

| # | Criterion | Test |
|---|-----------|------|
| 1 | Valid DB creation | Create with test cache |
| 2 | Indexes present | Query sqlite_master |
| 3 | Ancestor chain correct | Nested element ancestry |
| 4 | Re-scan replaces | No duplicates on refresh |
| 5 | Context manager works | `with DatabaseManager()` |
| 6 | Schema creates | Missing DB creates tables |

---

## File-Level Modular Architecture

| Module | File Decomposition | Rationale |
|--------|-------------------|-----------|
| `samples/scanner/db_persistence/` | `__init__.py` (facade) → `ddl.py` (DDL constants + `ensure_schema()`) → `persistence.py` (`persist_to_db()`, `persist_to_db_chunked()`, `DatabaseManager`) → `queries.py` (7 query functions: `get_ancestors`, `get_descendants`, `get_by_depth`, `get_siblings`, `count_by_type`, `get_by_extension`, `get_structural_element`) | 3 architectural layers — DDL (schema), persistence (stateful), queries (read-only) MUST be separated |

---

## Test Strategy

### Philosophy
- **No gap masking** — if a capability is missing, fix the architecture, don't paper over it with trivial tests
- Every test MUST validate a real capability, not just "runs without error"
- All tests are runnable via `python -m pytest tests/ -v`

### Smoke Tests (end-to-end capability validation)
| # | Smoke Test | Validates |
|---|-----------|-----------|
| 1 | `ensure_schema()` on an in-memory SQLite database | Creates all tables: `structural_elements`, `schema_version`, all 6 indexes |
| 2 | `persist_to_db()` with a populated `IdentityCache` | Rows inserted into `structural_elements`; entry point inserted first (FK dependency) |
| 3 | `DatabaseManager` context manager | `with DatabaseManager(db_path) as conn:` opens connection, commits, closes without error |

### Behavioral Tests (capability-revealing, BDD-style)
| # | Behaviour | Given | When | Then |
|---|-----------|-------|------|------|
| 1 | Batch insert atomicity (rollback on error) | A malformed element with invalid `entity_type` | `persist_to_db()` attempts transaction | `ROLLBACK` is issued; zero rows committed; error raised to caller |
| 2 | `get_structural_element` returns None for missing | Element UUID that does not exist in database | `get_structural_element(conn, non_existent_id)` is called | Returns `None` (not `KeyError`, not empty dict) |
| 3 | All 7 query functions work | Database populated with 10+ structural elements across 3 depth levels | Each query function called with valid parameters | `get_ancestors`, `get_descendants`, `get_by_depth`, `get_siblings`, `count_by_type`, `get_by_extension`, `get_structural_element` all return correct typed results |
| 4 | 3-file separation | DDL, persistence, and queries are in separate files | Inspect `ddl.py` vs `persistence.py` vs `queries.py` | DDL has no persistence logic; queries have no DDL; persistence has no raw SQL for reads |

### Gap → Architecture Fix Rule
If a test reveals a missing capability:
1. **DO NOT** write a test that passes trivially (e.g. `assert True`)
2. **DO NOT** skip the test with `@pytest.mark.skip`
3. **INSTEAD**: Identify the architectural layer where the gap belongs, implement, then test passes

### Test Files
| File | Scope |
|------|-------|
| `tests/db_persistence/test_ddl.py` | DDL constants, `ensure_schema()`, index creation, schema versioning |
| `tests/db_persistence/test_persistence.py` | `persist_to_db()`, `persist_to_db_chunked()`, `DatabaseManager`, transaction atomicity |
| `tests/db_persistence/test_queries.py` | All 7 query functions, `get_structural_element` None edge case |