# Wave 8 Execution Plan: Entry Point Scanner

**Generated:** 2026-05-31  
**Status:** READY FOR IMPLEMENTATION  
**Dependency:** Wave 7 (identity_model.py) COMPLETE  
**Target:** `<CONFIGURABLE>/entry_point.py` (see Configuration section)

---

## Configuration

### Path Configuration

**Smart Task is project-agnostic.** Scanner operates on any directory passed via:

| Source | Usage |
|--------|-------|
| CLI `--entry-point` | Target directory for scanning |
| `EntryPoint.path` | Configurable via consumers |
| Environment variables | Optional default paths |

---

## Required Implementation

| Component | Spec Requirement | Status |
|-----------|------------------|--------|
| `EntryPoint` dataclass | 7 fields per spec | ❌ MISSING |
| `scan_entry_point()` | Iterative stack DFS | ❌ MISSING |
| `_compute_depth()` | Depth calculation | ❌ MISSING |
| Symlink validation | Boundary check logic | ❌ MISSING |
| Error handling | PermissionError, OSError, FileNotFoundError | ❌ MISSING |

---

## Step 1: Define EntryPoint Dataclass (spec-aligned)

- [ ] Import dependencies: dataclasses, pathlib, typing
- [ ] Create `EntryPoint` with exact spec fields (7 total):
  - `path: Path`
  - `depth_limit: int = 0`           # 0 = unlimited
  - `include_patterns: list[str] | None = None`
  - `exclude_patterns: list[str] | None = None`   # applied AFTER filter stage
  - `follow_symlinks: bool = False`
  - `scan_hidden: bool = False`
  - `entry_point_id: str | None = None`  # assigned at scan time

---

## Step 2: Implement Iterative DFS Scanner

### Algorithm for `scan_entry_point(entry: EntryPoint) -> list[RawScanItem]`

- [ ] Initialize stack: `[(entry.path, 0)]`
- [ ] While stack not empty:
  - [ ] Pop `(current_path, current_depth)`
  - [ ] Depth limit check: `entry.depth_limit` (0 = unlimited)
  - [ ] Hidden file check: skip if name starts with `.` and `entry.scan_hidden=False`
  - [ ] Symlink check: skip symlinks outside entry boundary unless `entry.follow_symlinks=True`
  - [ ] Try-except for PermissionError, OSError, FileNotFoundError
  - [ ] Directory: sort children (dirs first, then alpha), push to stack
  - [ ] File: record with size

---

## Step 3: Implement `_compute_depth()`

- [ ] Count path components beyond entry root
- [ ] Entry root = 0, children = 1, nested = 2+

---

## Step 4: Error Handling

- [ ] PermissionError → log warning, continue
- [ ] OSError → log warning, continue
- [ ] FileNotFoundError → skip silently

---

## Step 5: Deterministic Ordering

- [ ] Sort children: directories first, then alphabetical
- [ ] Stable sort for reproducibility

---

## Step 6: Verification

| # | Criterion | Test |
|---|-----------|------|
| 1 | Correct item count | `len(scan(...))` matches directory |
| 2 | Depth correctness | Entry=0, child=1, nested=2+ |
| 3 | Hidden file skip | `.git` excluded when `scan_hidden=False` |
| 4 | Error handling | No crash on permission error |
| 5 | Type match | Returns `RawScanItem` tuples |
| 6 | Determinism | Same results on repeated runs |

---

## File-Level Modular Architecture

| Module | File Decomposition | Rationale |
|--------|-------------------|-----------|
| `samples/scanner/entry_scanner/` | `__init__.py` (facade) → `models.py` (`EntryPoint` dataclass with all 7 fields: path, depth_limit, include_patterns, exclude_patterns, follow_symlinks, scan_hidden, entry_point_id) → `scanner.py` (`scan_entry_point()`, `_compute_depth()`) | Separate data model from scanning logic |

---

## Test Strategy

### Philosophy
- **No gap masking** — if a capability is missing, fix the architecture, don't paper over it with trivial tests
- Every test MUST validate a real capability, not just "runs without error"
- All tests are runnable via `python -m pytest tests/ -v`

### Smoke Tests (end-to-end capability validation)
| # | Smoke Test | Validates |
|---|-----------|-----------|
| 1 | `scan_entry_point()` on a small directory returns `list[RawScanItem]` | Function exists, returns correct type, directory walked |
| 2 | Recursive scan with `depth_limit=0` walks all nested subdirectories | Recursion/stack algorithm works |
| 3 | Hidden files excluded with `scan_hidden=False` | `.git`, `.venv`, `.DS_Store` filtered out from results |

### Behavioral Tests (capability-revealing, BDD-style)
| # | Behaviour | Given | When | Then |
|---|-----------|-------|------|------|
| 1 | `include_patterns` filter | An `EntryPoint` with `include_patterns=["*.py"]` | `scan_entry_point()` scans directory | Only `.py` files appear in results |
| 2 | `exclude_patterns` filter | An `EntryPoint` with `exclude_patterns=["__pycache__"]` | `scan_entry_point()` scans directory | `__pycache__` directories excluded from results |
| 3 | Depth calculation | A file at `a/b/c/file.txt` relative to entry root `a` | `_compute_depth()` calculates depth | Depth equals 2 (two levels below entry root) |
| 4 | Non-existent path error | An `EntryPoint` with `path` pointing to non-existent directory | `scan_entry_point()` is called | `FileNotFoundError` caught and logged; empty list returned |
| 5 | `EntryPoint` field completeness | All 7 fields instantiated | `dataclasses.fields(EntryPoint)` inspected | Fields match spec: `path`, `depth_limit`, `include_patterns`, `exclude_patterns`, `follow_symlinks`, `scan_hidden`, `entry_point_id` |
| 6 | Deterministic ordering | Same directory scanned twice | `scan_entry_point()` called in sequence | Both results identical (same order, same items) |

### Gap → Architecture Fix Rule
If a test reveals a missing capability:
1. **DO NOT** write a test that passes trivially (e.g. `assert True`)
2. **DO NOT** skip the test with `@pytest.mark.skip`
3. **INSTEAD**: Identify the architectural layer where the gap belongs, implement, then test passes

### Test Files
| File | Scope |
|------|-------|
| `tests/entry_scanner/test_models.py` | `EntryPoint` dataclass (all 7 fields, field completeness check) |
| `tests/entry_scanner/test_scanner.py` | `scan_entry_point()`, `_compute_depth()`, error handling, deterministic ordering |