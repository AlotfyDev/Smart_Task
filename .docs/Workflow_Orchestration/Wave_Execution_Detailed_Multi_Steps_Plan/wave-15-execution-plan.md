# Wave 15 Execution Plan: Tasks Graph ← Stubs + Buggy Components

**Generated:** 2026-05-31  
**Status:** READY FOR IMPLEMENTATION  
**Dependency:** Wave 10 (db_persistence.py), Wave 11 (identity_cache.py)  
**Target:** `<CONFIGURABLE>/tasks_parser.py` (see Configuration section)

---

## Configuration

### Path Configuration

Tasks modules accept configurable paths:

| Source | Usage |
|--------|-------|
| `db_path` parameter | Database connection |
| `filepath` parameter | CSV file path |
| `entry_point_id` parameter | Scan identifier |
| Environment variables | Optional default paths |

---

## Required Implementation

| Component | Spec Requirement | Status |
|-----------|------------------|--------|
| `tasks` table DDL | Task storage schema | ❌ MISSING |
| `create_implementation_tasks_from_db()` | DB stub-to-task conversion | ❌ MISSING |
| `parse_buggy_components_with_db()` | CSV + UUID resolution | ❌ MISSING |

---

## Step 1: Add Tasks Table DDL

- [ ] Define `TASKS_DDL` with 10 columns
- [ ] Add to schema or import from Wave 10

---

## Step 2: Implement `create_implementation_tasks_from_db()`

### Tasks

1. [ ] Query DB: `SELECT * FROM structural_elements WHERE classification = 'to_be_implemented'`
2. [ ] For each stub:
   - Look up concerns via `concern_element_links`
   - Derive priority from highest concern severity
3. [ ] Generate task dict with UUID target
4. [ ] Return list of task dicts

---

## Step 3: Implement `parse_buggy_components_with_db()`

- [ ] Call `parse_buggy_components(filepath)` - returns raw list
- [ ] For each buggy component:
  - Resolve `component` field to UUID via DB
- [ ] Build task dict with UUID target
- [ ] Return list of task dicts

---

## Step 4: Remove Obsolete Functions

- [ ] Remove `create_implementation_tasks()` - replaced by DB version

---

## Step 5: Preserve Existing Functions

- [ ] Keep `parse_buggy_components()`, `parse_all_buggy_components()`, `calculate_priority()`

---

## Step 6: Verification

| # | Criterion | Test |
|---|-----------|------|
| 1 | Tasks created | Stubs → tasks |
| 2 | Priority derived | Highest concern severity mapped |
| 3 | UUID resolved | CSV component → element UUID |
| 4 | Backward compat output | Task dict format unchanged |

---

## File-Level Modular Architecture

| Module | File Decomposition | Rationale |
|--------|-------------------|-----------|
| `samples/scanner/tasks_parser/` | `__init__.py` (facade) → `ddl.py` (tasks DDL — schema definition) → `priority.py` (`calculate_priority()` — pure priority derivation) → `generator.py` (`create_implementation_tasks_from_db()` — main task creation) | 3 concerns: schema, priority logic, task generation — like Wave 13 pattern |

## Test Strategy

### Philosophy
- **No gap masking** — if a capability is missing, fix the architecture, don't paper over it with trivial tests
- Every test MUST validate a real capability, not just "runs without error"
- All tests are runnable via `python -m pytest tests/ -v`

### Smoke Tests (end-to-end capability validation)
| # | Smoke Test | Validates |
|---|-----------|-----------|
| 1 | `create_implementation_tasks_from_db()` generates tasks only for `to_be_implemented` stubs | Correct stub → task filtering |
| 2 | `calculate_priority()` returns correct priority level for known concern severity | Priority derivation algorithm |
| 3 | `parse_buggy_components_with_db()` resolves CSV component paths to UUIDs | CSV + UUID resolution integration |
| 4 | Task output dict format matches old `create_implementation_tasks()` format | Backward compatibility with presentation layer |

### Behavioral Tests (capability-revealing, BDD-style)
| # | Behaviour | Given | When | Then |
|---|-----------|-------|------|------|
| 1 | Correct stub filtering | DB has 5 `to_be_implemented` elements and 20 `exists` elements | `create_implementation_tasks_from_db()` called | Exactly 5 tasks returned |
| 2 | Priority from highest severity | A stub linked to concerns with severities `["low", "critical", "medium"]` | Task priority derived | Priority equals `"critical"` |
| 3 | CSV UUID resolution | `buggy_components.csv` with `component=src/core/engine.py` | `parse_buggy_components_with_db()` called | Task dict contains correct UUID for `core/engine.py` |
| 4 | Old function removed | Module no longer exports `create_implementation_tasks()` | Attempt `from tasks_parser import create_implementation_tasks` | `ImportError` raised |

### Gap → Architecture Fix Rule
If a test reveals a missing capability:
1. **DO NOT** write a test that passes trivially (e.g. `assert True`)
2. **DO NOT** skip the test with `@pytest.mark.skip`
3. **INSTEAD**: Identify the architectural layer where the gap belongs, implement, then test passes

### Test Files
| File | Scope |
|------|-------|
| `tests/test_tasks_graph/test_generator.py` | Task generation from DB stubs |
| `tests/test_tasks_graph/test_priority.py` | Priority derivation from concern severity |
| `tests/test_tasks_graph/test_buggy_components.py` | Buggy component CSV parsing + UUID resolution |
| `tests/test_tasks_graph/test_preserved.py` | Old functions (`parse_buggy_components`, `calculate_priority`) unchanged |