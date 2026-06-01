# Wave 14 Execution Plan: Dependency Graph ← UUID Resolution

**Generated:** 2026-05-31  
**Status:** READY FOR IMPLEMENTATION  
**Dependency:** Wave 10 (db_persistence.py), Wave 11 (identity_cache.py)  
**Target:** `<CONFIGURABLE>/dependency_parser.py` (see Configuration section)

---

## Configuration

### Path Configuration

Dependency modules accept configurable paths:

| Source | Usage |
|--------|-------|
| `db_path` parameter | Database connection |
| `src_dir` parameter | Source directory for AST scan |
| `entry_point_id` parameter | Scan identifier |
| Environment variables | Optional default paths |

---

## Required Implementation

| Component | Spec Requirement | Status |
|-----------|------------------|--------|
| `scan_and_register_dependencies()` | AST scan + UUID resolution | ❌ MISSING |
| `dependency_edges` DDL | Edge table schema | ❌ MISSING |
| `register_dependency_edges()` | Edge insertion with transaction | ❌ MISSING |
| Remove obsolete functions | Remove old CSV-based logic | ❌ MISSING |

---

## Step 1: Add Bridge Table DDL

- [ ] Define `DEPENDENCY_EDGES_DDL` with 5 columns
- [ ] Add to schema or import from Wave 10

---

## Step 2: Implement `scan_and_register_dependencies()`

### Tasks

1. [ ] Build `relative_path → uuid` lookup from DB
2. [ ] AST-scan `.py` files in `src_dir`
3. [ ] Resolve imports to UUIDs via `_resolve_module()`
4. [ ] Return `(module_nodes, import_edges)`

---

## Step 3: Implement `register_dependency_edges()`

- [ ] Connect to DB
- [ ] `DELETE FROM dependency_edges WHERE entry_point_id = ?`
- [ ] Begin transaction
- [ ] Batch insert edges
- [ ] Commit or rollback on error

---

## Step 4: Remove Obsolete Functions

- [ ] Remove `map_imports_to_taxonomy()`
- [ ] Remove `register_file_dependencies()`

---

## Step 5: Preserve Existing Functions

- [ ] Keep `_resolve_module()`, `_resolve_from_node()`, `scan_source_modules()`, `detect_cycles()`, `topological_sort()`

---

## Step 6: Verification

| # | Criterion | Test |
|---|-----------|------|
| 1 | UUID pairs correct | Test src/ with known imports → verify UUIDs |
| 2 | Edge table populated | Check `SELECT * FROM dependency_edges` |
| 3 | Cycle detection works | Existing tests pass |
| 4 | Old functions removed | Functions no longer accessible |

---

## File-Level Modular Architecture

| Module | File Decomposition | Rationale |
|--------|-------------------|-----------|
| `samples/scanner/dependency_parser/` | `__init__.py` (facade) → `ddl.py` (dependency_edges DDL + `register_dependency_edges()` for DB writes — Layer 3) → `ast_scanner.py` (AST import scanning — pure Layer 1) → `graph.py` (edge resolution + UUID dedup — Layer 2) | 3 concerns: DDL/persistence, AST scanning, graph resolution — like Wave 13 pattern |

## Test Strategy

### Philosophy
- **No gap masking** — if a capability is missing, fix the architecture, don't paper over it with trivial tests
- Every test MUST validate a real capability, not just "runs without error"
- All tests are runnable via `python -m pytest tests/ -v`

### Smoke Tests (end-to-end capability validation)
| # | Smoke Test | Validates |
|---|-----------|-----------|
| 1 | `scan_and_register_dependencies()` on a `src/` dir with known `import foo` | AST scanner detects imports and resolves to UUIDs |
| 2 | `register_dependency_edges()` writes correct edges to `dependency_edges` table | DB persistence with transaction semantics |
| 3 | `detect_cycles()` returns correct cycle set for a known cyclic import graph | Cycle detection correctness |
| 4 | `topological_sort()` returns valid order (predecessors before dependents) | Topological ordering validity |

### Behavioral Tests (capability-revealing, BDD-style)
| # | Behaviour | Given | When | Then |
|---|-----------|-------|------|------|
| 1 | UUID dedup | File A imports file B twice (in two different import statements) | `scan_and_register_dependencies()` runs | Only one edge `(A_uuid, B_uuid)` appears in the result |
| 2 | Cycle correctness | Files A→B→C→A with known circular dependency | `detect_cycles()` called | Cycle `[A, B, C, A]` detected with correct UUIDs |
| 3 | Valid topological order | A depends on B, B depends on C, C depends on nothing | `topological_sort()` called | Result order: `[C, B, A]` |
| 4 | Obsolete removal | Module no longer exports `map_imports_to_taxonomy` or `register_file_dependencies` | Attempt `from dependency_parser import map_imports_to_taxonomy` | `ImportError` raised |

### Gap → Architecture Fix Rule
If a test reveals a missing capability:
1. **DO NOT** write a test that passes trivially (e.g. `assert True`)
2. **DO NOT** skip the test with `@pytest.mark.skip`
3. **INSTEAD**: Identify the architectural layer where the gap belongs, implement, then test passes

### Test Files
| File | Scope |
|------|-------|
| `tests/test_dependency_graph/test_ast_scanner.py` | AST import detection and module resolution |
| `tests/test_dependency_graph/test_edges.py` | Edge registration, UUID dedup, transaction rollback |
| `tests/test_dependency_graph/test_cycles.py` | Cycle detection on known cyclic graphs |
| `tests/test_dependency_graph/test_topological.py` | Topological sort correctness |