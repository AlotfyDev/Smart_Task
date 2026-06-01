# Wave 16 Execution Plan: CLI Migration + Legacy Cleanup

**Generated:** 2026-05-31  
**Status:** READY FOR IMPLEMENTATION  
**Dependency:** Waves 12-15 (all 4 graphs rewired to DB)  
**Targets:** `<CONFIGURABLE>/cli.py`, `<CONFIGURABLE>/parsers/__init__.py`, legacy files

---

## Configuration

### Path Configuration

CLI and parser modules accept configurable paths:

| Source | Usage |
|--------|-------|
| CLI `--entry-point` | Target directory for scanning |
| CLI `--db-path` | Database file path |
| CLI `--topic-dir` | Topic files directory |
| Environment variables | Optional default paths |

---

## Required Changes

| Target | Action | Status |
|--------|--------|--------|
| `cli.py` | Add `--scan`, `--entry-point`, `--db-path` | ❌ MISSING |
| `parsers/__init__.py` | Add `USE_DB_SCANNER` flag | ❌ MISSING |
| `structural_parser.py` | Remove entirely | ⚠️ NEEDS REMOVAL |
| `parsers.py` | Remove entirely | ⚠️ NEEDS REMOVAL |
| Obsolete functions | Remove or deprecate | ⚠️ NEEDS DEPRECATION |

---

## Module Dependency Diagram

```
CLI Layer:
  cli/__init__.py          ← entry point, click commands
      ↓
Parsers Layer (after cleanup):
  parsers/__init__.py      ← re-exports: structural_parser, tasks_parser, dependency_parser
      ├── structural_parser.py    ← imports structural_graph module
      ├── tasks_parser.py         ← imports tasks_graph module  
      └── dependency_parser.py    ← imports dependency_graph module
```

**⚠️ Import chain precautions after file removal:**
1. `structural_parser.py` imports from `samples/scanner/structural_graph/` — verify before removing old `parsers/structural.py`
2. `tasks_parser.py` imports from `samples/scanner/tasks_parser/` — verify before removing old `parsers/tasks.py`
3. `dependency_parser.py` imports from `samples/scanner/dependency_parser/` — verify before removing old `parsers/dependency.py`
4. The `USE_DB_SCANNER` flag in `parsers/__init__.py` controls which parser set is active — ensure all 6+ affected files check this flag consistently

### File-Level Modular Architecture

| Module | File Decomposition | Rationale |
|--------|-------------------|-----------|
| `cli/` | `__init__.py` (single thin orchestration) | CLI remains single file unless >400 lines |
| `parsers/` | `__init__.py` (re-exports + USE_DB_SCANNER flag) → `structural_parser.py` (legacy) → `tasks_parser.py` (legacy) → `dependency_parser.py` (legacy) → `concerns_parser.py` (legacy) | After Wave 16, some files are deleted; remaining legacy parsers are pure re-exports wrapping new module-based implementations |

## Test Strategy

### Philosophy
- **No gap masking** — if a capability is missing, fix the architecture, don't paper over it with trivial tests
- Every test MUST validate a real capability, not just "runs without error"
- All tests are runnable via `python -m pytest tests/ -v`

### Smoke Tests (end-to-end capability validation)
| # | Smoke Test | Validates |
|---|-----------|-----------|
| 1 | `python -m graph.cli --summary` with `USE_DB_SCANNER=1` | All CLI commands work with DB pipeline |
| 2 | `python -m graph.cli --summary` with `USE_DB_SCANNER=0` | All CLI commands work with CSV fallback |
| 3 | `python -m graph.cli --scan --entry-point src/ --summary` | `--scan` flag triggers full pipeline (scan → filter → identity → persist → 4 graphs) |
| 4 | `python -c "from samples.parsers import structural_parser"` after file removal | Removed `structural_parser.py` and `parsers.py` cause zero import errors |

### Behavioral Tests (capability-revealing, BDD-style)
| # | Behaviour | Given | When | Then |
|---|-----------|-------|------|------|
| 1 | Feature flag fallback | `USE_DB_SCANNER=0` and no DB available | CLI runs `--summary` | Output matches old CSV-based behavior exactly |
| 2 | Export correctness | `parsers/__init__.py` defines `__all__` | `from parsers import *` executed | Only expected names are imported; removed functions absent |
| 3 | No regression after cleanup | All legacy files removed except `concerns_parser.py` | Every CLI command (`--taxonomy`, `--concerns`, `--tasks`, `--cycles`, `--topo`) invoked | Zero `ModuleNotFoundError` or `ImportError` |
| 4 | Graceful degradation | No DB file exists and `USE_DB_SCANNER=1` | `build_graph()` called | Falls back to CSV parser; user warned via stderr |

### Gap → Architecture Fix Rule
If a test reveals a missing capability:
1. **DO NOT** write a test that passes trivially (e.g. `assert True`)
2. **DO NOT** skip the test with `@pytest.mark.skip`
3. **INSTEAD**: Identify the architectural layer where the gap belongs, implement, then test passes

### Test Files
| File | Scope |
|------|-------|
| `tests/test_cli_migration/test_commands.py` | All CLI commands execute without error in both DB and CSV modes |
| `tests/test_cli_migration/test_feature_flag.py` | `USE_DB_SCANNER` flag toggles between DB and CSV pipelines |
| `tests/test_cli_migration/test_legacy_removal.py` | Removed files/functions cause no import errors |
| `tests/test_cli_migration/test_exports.py` | `__all__` correctness and export consistency |

## Step 1: Update `cli.py`

### Tasks

- [ ] Add `--scan` flag:
  - Triggers: scan → filter → identity → persist → 4 graphs
  - Default: use cached DB

- [ ] Add `--entry-point` argument:
  - Default: configurable (not hardcoded `src/`)
  - Passed to `IdentityCacheBuilder`

- [ ] Add `--db-path` argument:
  - Default: configurable (not hardcoded `.scanner/`)
  - Used for all DB operations

- [ ] Modify `build_graph()`:
  - Check DB availability first
  - Prefer DB pipeline if available
  - Fallback to CSV if not

- [ ] Ensure all existing commands work

---

## Step 2: Update `parsers/__init__.py`

- [ ] Add `USE_DB_SCANNER = os.getenv("USE_DB_SCANNER", "1") == "1"`
- [ ] Create `parse_structural_taxonomy(roadmap_dir=None, db_path=None)`:
  - If `USE_DB_SCANNER=True`: use DB pipeline
  - If `False`: delegate to old CSV parser

---

## Step 3: Legacy Code Removal

**Remove entirely:**
- [ ] `structural_parser.py` (replaced by DB + scanner)
- [ ] `parsers.py` (legacy root file)

**Remove functions:**
- [ ] `tasks_parser.py`: `create_implementation_tasks()`
- [ ] `dependency_parser.py`: `map_imports_to_taxonomy()`, `register_file_dependencies()`

**Keep unchanged:**
- [ ] `concerns_parser.py`: `parse_domain_gap_csv()`
- [ ] `tasks_parser.py`: `parse_buggy_components()`
- [ ] `dependency_parser.py`: `scan_source_modules()`, `detect_cycles()`, `topological_sort()`

---

## Step 4: Update Exports

- [ ] Update `__all__` in `parsers/__init__.py`
- [ ] Remove exports for deleted functions
- [ ] Verify no import errors

---

## Step 5: Verification

| # | Criterion | Test |
|---|-----------|------|
| 1 | Field names preserved | `--summary` output unchanged |
| 2 | `--scan` pipeline works | Full scan → output works |
| 3 | All CLI commands work | Test each command |
| 4 | Feature flag fallback | `USE_DB_SCANNER=0` uses CSV |
| 5 | Legacy files removed | No import errors |
| 6 | Functions not exported | `__all__` updated |

---

## Migration Pattern

Feature flag (`USE_DB_SCANNER`) enables gradual rollout + rollback capability.