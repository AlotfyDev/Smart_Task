# Wave 13 Execution Plan: Concerns Graph ← Bridge Table

**Generated:** 2026-05-31  
**Status:** READY FOR IMPLEMENTATION  
**Dependency:** Wave 10 (db_persistence.py), Wave 11 (identity_cache.py)  
**Target:** `<CONFIGURABLE>/concerns_parser.py` + `<CONFIGURABLE>/concern_element_links.py`

---

## Configuration

### Path Configuration

Conchmarks modules accept configurable paths:

| Source | Usage |
|--------|-------|
| `db_path` parameter | Database connection |
| Environment variables | Optional default paths |
| CLI arguments | Runtime path overrides |

---

## Required Implementation

| Component | Spec Requirement | Status |
|-----------|------------------|--------|
| `concern_element_links` DDL | Bridge table schema | ❌ MISSING |
| `extract_target_path()` | Path extraction from evidence | ❌ MISSING |
| `link_concerns_to_structural()` | Concern-to-element UUID mapping | ❌ MISSING |
| `populate_concern_links_from_csv()` | CSV migration to bridge table | ❌ MISSING |

---

## Step 1: Create Bridge Table DDL

- [ ] Define `CONCERN_ELEMENT_LINKS_DDL` with 5 columns
- [ ] Create index on `concern_id`

---

## Step 2: Implement `extract_target_path()`

- [ ] Extract `.py` file references using regex
- [ ] Query `structural_elements` by `relative_path`
- [ ] Return matched UUIDs

---

## Step 3: Implement `link_concerns_to_structural()`

- [ ] Connect to DB
- [ ] Read existing links from `concern_element_links`
- [ ] Extract new links via `extract_target_path()`
- [ ] Return `dict[concern_id, list[element_id]]`

---

## Step 4: Implement `populate_concern_links_from_csv()`

- [ ] Read `files.csv` (old format)
- [ ] Parse `required_concerns` column
- [ ] Resolve component paths to UUIDs
- [ ] Insert into `concern_element_links`

---

## Step 5: Preserve Existing Functions

- [ ] Keep `parse_domain_gap_csv()` - NO CHANGES
- [ ] Keep `parse_all_domain_gaps()` - NO CHANGES
- [ ] Keep `parse_concern_dependencies()` - NO CHANGES

---

## Step 6: Verification

| # | Criterion | Test |
|---|-----------|------|
| 1 | Path resolution | Concern → element UUID |
| 2 | Link mapping correct | Valid dict returned |
| 3 | CSV migration works | Bridge table populated |
| 4 | Old functions work | Unchanged behavior |

---

## File-Level Modular Architecture

| File | Purpose | Layer |
|------|---------|-------|
| `concern_element_links.py` | DDL + queries | Layer 1 (Toolbox) |
| `concerns_parser.py` | Main parser logic | Layer 3 (Stateful) |

Separate files for clean separation.

✅ This module follows the correct multi-file pattern. Other waves should replicate this approach.

## Test Strategy

### Philosophy
- **No gap masking** — if a capability is missing, fix the architecture, don't paper over it with trivial tests
- Every test MUST validate a real capability, not just "runs without error"
- All tests are runnable via `python -m pytest tests/ -v`

### Smoke Tests (end-to-end capability validation)
| # | Smoke Test | Validates |
|---|-----------|-----------|
| 1 | `link_concerns_to_structural()` creates bridge records for known concerns | Concern → element UUID mapping works end-to-end |
| 2 | `populate_concern_links_from_csv()` imports old `files.csv` → `concern_element_links` | CSV migration populates bridge table correctly |
| 3 | `extract_target_path()` resolves `.py` file references from concern evidence | Path resolution against `structural_elements.relative_path` |
| 4 | Old `parse_domain_gap_csv()` returns identical output before and after migration | No regression on preserved functions |

### Behavioral Tests (capability-revealing, BDD-style)
| # | Behaviour | Given | When | Then |
|---|-----------|-------|------|------|
| 1 | Link accuracy | A concern with `evidence="see src/core/engine.py"` | `extract_target_path()` is called | Returns UUID of `core/engine.py` from DB |
| 2 | No orphan links | A populated `concern_element_links` table | `SELECT element_id` where element doesn't exist in `structural_elements` | Zero rows returned |
| 3 | CSV parse edge cases | A `files.csv` with empty `required_concerns` column, malformed paths, duplicate entries | `populate_concern_links_from_csv()` runs | No crash; valid rows inserted, malformed skipped |
| 4 | UNIQUE constraint dedup | Same `(concern_id, element_id, link_type)` inserted twice | Second insert attempted | Constraint violation raised; no duplicate rows |

### Gap → Architecture Fix Rule
If a test reveals a missing capability:
1. **DO NOT** write a test that passes trivially (e.g. `assert True`)
2. **DO NOT** skip the test with `@pytest.mark.skip`
3. **INSTEAD**: Identify the architectural layer where the gap belongs, implement, then test passes

### Test Files
| File | Scope |
|------|-------|
| `tests/test_concerns_graph/test_links.py` | Bridge table operations (DDL, link_concerns_to_structural) |
| `tests/test_concerns_graph/test_extraction.py` | Path extraction via regex + DB resolve |
| `tests/test_concerns_graph/test_csv_migration.py` | CSV import to bridge table |
| `tests/test_concerns_graph/test_preserved.py` | Old functions unchanged |