# Wave 12 Execution Plan: Structural Graph ← DB

**Generated:** 2026-05-31  
**Status:** READY FOR IMPLEMENTATION  
**Dependency:** Wave 10 (db_persistence.py), Wave 11 (identity_cache.py)  
**Target:** `<CONFIGURABLE>/structural_graph_from_db.py` (see Configuration section)

---

## Configuration

### Path Configuration

Graph modules accept configurable paths:

| Source | Usage |
|--------|-------|
| `db_path` parameter | Database location |
| `entry_point_id` parameter | Scan identifier |
| Environment variables | Optional default paths |

---

## Required Implementation

| Component | Spec Requirement | Status |
|-----------|------------------|--------|
| `build_structural_graph()` | Filter cache by entity_type | ❌ MISSING |
| `get_structural_nodes()` | Query DB for elements | ❌ MISSING |
| Old-to-new mapping | Backward compat translation | ❌ MISSING |
| Coexistence mode | USE_DB_SCANNER feature flag | ❌ MISSING |

---

## Step 1: Implement `build_structural_graph()`

- [ ] Get all elements via `cache.get_all()`
- [ ] Filter:
  - `entry_points`: `entity_type == "entry_point"`
  - `folders`: `entity_type == "folder"`
  - `files`: `entity_type == "file"` AND `classification == "exists"`
  - `file_stubs`: `classification == "to_be_implemented"`
- [ ] Return dict with four lists

---

## Step 2: Implement `get_structural_nodes()`

- [ ] Connect to SQLite
- [ ] Set `row_factory = sqlite3.Row`
- [ ] Execute query:
  ```sql
  SELECT * FROM structural_elements WHERE entry_point_id = ? ORDER BY depth, sort_order
  ```
- [ ] Return `{row["id"]: dict(row) for row in rows}`

---

## Step 3: Implement CSV-to-DB Mapping

| Old CSV | New DB Field |
|---------|--------------|
| `domain` | `entity_type = 'folder'` AND `depth = 1` |
| `subdomain` | `entity_type = 'folder'` AND `depth >= 2` |
| `file` | `entity_type = 'file'` AND `classification = 'exists'` |
| `file_stub` | `classification = 'to_be_implemented'` |
| `element_number` | `topo_key` |
| `full_path` | `relative_path` |

---

## Step 4: Backward Compatibility

- [ ] Ensure output format matches old CSV parser
- [ ] Create `USE_DB_SCANNER` feature flag check
- [ ] If `False`: delegate to old `structural_parser`

---

## Step 5: Verification

| # | Criterion | Test |
|---|-----------|------|
| 1 | Graph build correct | Cache elements correctly categorized |
| 2 | DB matches cache | `get_structural_nodes()` == `build_structural_graph()` |
| 3 | Backward compat | Old presentation layer works |
| 4 | Coexistence mode | Feature flag controls behavior |

---

## File-Level Modular Architecture

| Module | File Decomposition | Rationale |
|--------|-------------------|-----------|
| `samples/scanner/structural_graph/` | `__init__.py` (facade) → `queries.py` (structural element queries — pure read Layer 1) → `graph.py` (graph building logic) → `compat.py` (backward-compatibility layer with legacy parsers) | 3 concerns: DB queries, graph construction, compatibility — MUST be separated like Wave 13 |

## Test Strategy

### Philosophy
- **No gap masking** — if a capability is missing, fix the architecture, don't paper over it with trivial tests
- Every test MUST validate a real capability, not just "runs without error"
- All tests are runnable via `python -m pytest tests/ -v`

### Smoke Tests (end-to-end capability validation)
| # | Smoke Test | Validates |
|---|-----------|-----------|
| 1 | `build_structural_graph(cache)` constructs graph from populated IdentityCache | Correct dict with 4 lists: entry_points, folders, files, file_stubs |
| 2 | `get_structural_nodes()` returns same nodes as cache for same `entry_point_id` | DB ↔ cache parity across read paths |
| 3 | Old CSV `structural_parser` output matches new DB graph builder output format | Backward compatibility with presentation layer |
| 4 | `USE_DB_SCANNER=0` delegates to old CSV parser without error | Coexistence mode via feature flag |

### Behavioral Tests (capability-revealing, BDD-style)
| # | Behaviour | Given | When | Then |
|---|-----------|-------|------|------|
| 1 | Graph completeness | A cache with 3 entry_points, 5 folders, 10 files, 2 stubs | `build_structural_graph()` is called | 3 entry_points, 5 folders, 10 files, 2 stubs returned |
| 2 | Hierarchy integrity | structural_elements with known parent/child relationships | `get_structural_nodes()` returns rows | Every child's `parent_id` references a valid parent in the result set |
| 3 | Ordering preserved | Elements with depths 1..5 and sort_order 1..N | DB query orders by `depth, sort_order` | Result iteration order matches DFS traversal |
| 4 | CSV-to-DB mapping | A known CSV row with `domain=X, file=Y, element_number=Z` | Mapping translation applied | `entity_type='folder', depth=1` and `entity_type='file'` with `topo_key=Z` |

### Gap → Architecture Fix Rule
If a test reveals a missing capability:
1. **DO NOT** write a test that passes trivially (e.g. `assert True`)
2. **DO NOT** skip the test with `@pytest.mark.skip`
3. **INSTEAD**: Identify the architectural layer where the gap belongs, implement, then test passes

### Test Files
| File | Scope |
|------|-------|
| `tests/test_structural_graph/test_graph.py` | Graph construction from cache |
| `tests/test_structural_graph/test_queries.py` | DB query layer |
| `tests/test_structural_graph/test_compat.py` | Backward compatibility with legacy parsers |
| `tests/test_structural_graph/test_coexistence.py` | Feature flag (`USE_DB_SCANNER`) |