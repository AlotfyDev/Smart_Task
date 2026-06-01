# Wave 9 Execution Plan: Filter Layer

**Generated:** 2026-05-31  
**Status:** READY FOR IMPLEMENTATION  
**Dependency:** Wave 7 (identity_model.py) COMPLETE  
**Target:** `<CONFIGURABLE>/filter_layer.py` (see Configuration section)

---

## Critical Analysis

### Module Purpose

Three-tier filter pipeline: gitignore → third-party → user exclusions. Transforms filtered `RawScanItem` results.

### Required Implementation

| Component | Spec Requirement | Status |
|-----------|------------------|--------|
| `ExcludedItem` dataclass | 3 fields | ❌ MISSING |
| `FilterResult` dataclass | 2 fields + methods | ❌ MISSING |
| `load_gitignore()` | PathSpec or None | ❌ MISSING |
| `apply_gitignore()` | Tier A filtering | ❌ MISSING |
| `apply_third_party()` | Tier B filtering | ❌ MISSING |
| `UserExclusionRule` dataclass | 3 fields | ❌ MISSING |
| `apply_user_exclusions()` | Tier C filtering | ❌ MISSING |
| `apply_all_filters()` | Orchestration function | ❌ MISSING |
| `_is_blocked()` | Transitive exclusion helper | ❌ MISSING |
| `scan_exclusion_log` table | Audit log DDL | ✅ ADDED (fix) |
| `log_exclusions()` | Audit persistence | ✅ ADDED (fix) |

---

## Configuration

### Path Configuration

**Smart Task is project-agnostic.** Target paths are determined by:

| Source | Description |
|--------|-------------|
| CLI `--topic-dir` | Topic files directory override |
| CLI `--db-path` | Database path override |
| `SMART_TASK_DB_PATH` env var | Default DB path |
| `load_config()` defaults | Standard fallback paths |

**Do NOT hardcode `samples/scanner/` paths.** Implementation modules should accept paths as parameters or read from configuration.

---

## Step 1: Define Data Classes

### Tasks

- [ ] **ExcludedItem dataclass:**
  ```python
  @dataclass
  class ExcludedItem:
      path: Path
      reason_code: str
      detail: str
  ```

- [ ] **UserExclusionRule dataclass:**
  ```python
  @dataclass
  class UserExclusionRule:
      pattern: str
      reason: str = "USER_EXCLUDED"
      description: str = ""
  ```

- [ ] **FilterResult dataclass:**
  ```python
  @dataclass
  class FilterResult:
      excluded: list[ExcludedItem]
      remaining: list[RawScanItem]
      
      @property
      def all_excluded_paths(self) -> set[Path]:
          return {item.path for item in self.excluded}
      
      def merge(self, other: "FilterResult") -> "FilterResult":
          return FilterResult(
              excluded=self.excluded + other.excluded,
              remaining=self.remaining + other.remaining
          )
  ```

---

## Step 2: Implement Third-Party Patterns

### Tasks

- [ ] Define constant `THIRD_PARTY_PATTERNS`:
  ```python
  THIRD_PARTY_PATTERNS = [
      "node_modules", ".venv", "venv", "env", ".env",
      "__pycache__", ".mypy_cache", ".pytest_cache",
      ".tox", "build", "dist", "*.egg-info", ".eggs",
      ".git", ".svn", ".hg", ".idea", ".vscode", ".vs",
      "__pypackages__", ".ruff_cache", ".nox",
      ".ds_store", "thumbs.db",
  ]
  ```

- [ ] No external dependency required - use string matching or fnmatch

---

## Step 3: Implement `load_gitignore()`

### Tasks

- [ ] Check for `.gitignore` at `entry_root / ".gitignore"`
- [ ] Return `None` if file doesn't exist
- [ ] Return `pathspec.PathSpec.from_lines()` if exists
- [ ] Handle encoding: UTF-8

---

## Step 4: Implement `apply_gitignore()`

### Algorithm

```python
def apply_gitignore(items: list[RawScanItem], entry_root: Path, spec: PathSpec | None) -> FilterResult:
```

### Tasks

- [ ] If `spec is None`: return all items as remaining
- [ ] For each `RawScanItem`:
  - Get relative path: `item[0].relative_to(entry_root)`
  - Check match: `spec.match_file(str(relative_path))`
  - If match: add to excluded with `reason_code="GITIGNORE"`
  - If not match: add to remaining

---

## Step 5: Implement `apply_third_party()`

### Algorithm

```python
def apply_third_party(items: list[RawScanItem], entry_root: Path) -> FilterResult:
```

### Tasks

- [ ] For each `RawScanItem`:
  - Get relative path string
  - Check if any pattern matches:
    - Exact match: `node_modules` in path parts
    - Prefix match: `.venv` matches `.venv/`, `.venv/lib`
    - Glob match: `*.egg-info` for egg-info directories
  - If match: exclude with `reason_code="THIRD_PARTY"`
  - If not: keep in remaining

---

## Step 6: Implement `apply_user_exclusions()`

### Algorithm

```python
def apply_user_exclusions(items: list[RawScanItem], entry_root: Path, rules: list[UserExclusionRule]) -> FilterResult:
```

### Tasks

- [ ] For each rule, build pattern matcher:
  - Use `fnmatch` or simple string matching
  - Handle `legacy/**` style patterns
- [ ] Track blocked directories for transitive exclusion
- [ ] For each item:
  - Check against all rules
  - If matched: exclude
  - If parent blocked: mark as blocked and skip

---

## Step 7: Implement `apply_all_filters()` (pure function)

### Algorithm

Pure function — no DB access, no file I/O beyond gitignore loading. Same input always produces same output.

### Tasks

- [ ] Signature: `def apply_all_filters(items: list[RawScanItem], entry: EntryPoint, user_rules: list[UserExclusionRule]) -> FilterResult`
- [ ] Call `load_gitignore(entry.path)`
- [ ] Apply `apply_gitignore(items, entry.path, spec)`
- [ ] Apply `apply_third_party(result.remaining, entry.path)`
- [ ] Apply `apply_user_exclusions(result.remaining, entry.path, rules)`
- [ ] **Handle transitive exclusion:**
  - Build set of excluded directories
  - For each remaining item, check `_is_blocked()`
  - Remove blocked items from remaining
- [ ] Merge all excluded lists
- [ ] Return final `FilterResult`

---

## Step 8: Implement Audit Log Persistence

### Tasks

- [ ] **Create audit log table DDL:**
  ```sql
  CREATE TABLE IF NOT EXISTS scan_exclusion_log (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      scan_id TEXT NOT NULL,
      excluded_path TEXT NOT NULL,
      reason_code TEXT NOT NULL,
      detail TEXT NOT NULL,
      created_at TEXT NOT NULL DEFAULT (datetime('now'))
  );
  ```

- [ ] **Create `log_exclusions()` function:**
  ```python
  def log_exclusions(conn: sqlite3.Connection, scan_id: str, exclusions: list[ExcludedItem]) -> None:
      for item in exclusions:
          conn.execute("""
              INSERT INTO scan_exclusion_log (scan_id, excluded_path, reason_code, detail)
              VALUES (?, ?, ?, ?)
          """, (scan_id, str(item.path), item.reason_code, item.detail))
  ```

- [ ] **Optional integration (via callback/decorator):**
  - Audit logging as an external callback or decorator, NOT coupled to filter logic

---

## Step 9: Implement `_is_blocked()`

### Tasks

```python
def _is_blocked(path: Path, blocked_dirs: set[Path]) -> bool:
```

- [ ] Iterate parents of `path`
- [ ] If any parent in `blocked_dirs`: return True
- [ ] Return False otherwise

---

## Step 10: Verification Test Cases

### Test Implementation

| # | Criterion | Test Code |
|---|-----------|-----------|
| 1 | Gitignore mock test | Create temp `.gitignore`, verify exclusion |
| 2 | Third-party patterns | `.venv`, `.git`, `__pycache__` excluded |
| 3 | User rules applied | `["legacy/**"]` excludes nested files |
| 4 | Transitive exclusion | Block `legacy/`, verify `legacy/sub/file.py` excluded |
| 5 | No gitignore works | Third-party still filtered without gitignore |
| 6 | FilterResult.merge | Combines excluded + remaining correctly |
| 7 | Audit log populated | Excluded items appear in `scan_exclusion_log` table |

---

## File-Level Modular Architecture

| Module | File Decomposition | Rationale |
|--------|-------------------|-----------|
| `samples/scanner/filter_layer/` | `__init__.py` (facade) → `rules.py` (`UserExclusionRule` dataclass + `is_third_party()` + `apply_user_rules()` + `THIRD_PARTY_PATTERNS`) → `filters.py` (`apply_all_filters()`, `should_exclude()`, `matches_any_pattern()`) | Pure filtering MUST NOT mix with DB persistence |

---

## Test Strategy

### Philosophy
- **No gap masking** — if a capability is missing, fix the architecture, don't paper over it with trivial tests
- Every test MUST validate a real capability, not just "runs without error"
- All tests are runnable via `python -m pytest tests/ -v`

### Smoke Tests (end-to-end capability validation)
| # | Smoke Test | Validates |
|---|-----------|-----------|
| 1 | `apply_all_filters()` on a list containing known third-party paths | `THIRD_PARTY_PATTERNS` correctly excludes `node_modules`, `.venv`, `__pycache__` |
| 2 | `UserExclusionRule` with glob pattern `["legacy/**"]` excludes nested files | `fnmatch`-based matching works for recursive patterns |
| 3 | `FilterResult.merge()` combines two filter passes | Excluded + remaining lists merge correctly without duplicates |

### Behavioral Tests (capability-revealing, BDD-style)
| # | Behaviour | Given | When | Then |
|---|-----------|-------|------|------|
| 1 | `THIRD_PARTY_PATTERNS` list complete | Patterns include all known VCS, IDE, package manager, and build tool dirs | Verify against known directory names | `node_modules`, `.venv`, `venv`, `env`, `.env`, `__pycache__`, `.mypy_cache`, `.pytest_cache`, `.tox`, `build`, `dist`, `*.egg-info`, `.eggs`, `.git`, `.svn`, `.hg`, `.idea`, `.vscode`, `.vs`, `__pypackages__`, `.ruff_cache`, `.nox`, `.ds_store`, `thumbs.db` all covered |
| 2 | Stable ordering | A list of 10 items with interleaved excluded/remaining | `apply_all_filters()` processes them | Results preserve input order — remaining items appear in the same relative order as in the input |
| 3 | Empty rules = no filtering | `apply_all_filters()` with empty `user_rules=[]` and no `.gitignore` | All items pass through | `FilterResult.remaining` equals input list; `FilterResult.excluded` only contains third-party matches |
| 4 | Pure function enforcement | `apply_all_filters()` signature inspected | Function signature checked | Does NOT accept `db_path` or any DB connection parameter — stateless, deterministic |
| 5 | Transitive exclusion | Directory `legacy/` excluded by user rule | Child `legacy/sub/file.py` checked | `_is_blocked()` returns True; child removed from remaining |

### Gap → Architecture Fix Rule
If a test reveals a missing capability:
1. **DO NOT** write a test that passes trivially (e.g. `assert True`)
2. **DO NOT** skip the test with `@pytest.mark.skip`
3. **INSTEAD**: Identify the architectural layer where the gap belongs, implement, then test passes

### Test Files
| File | Scope |
|------|-------|
| `tests/filter_layer/test_rules.py` | `THIRD_PARTY_PATTERNS` completeness, `UserExclusionRule`, `UserExclusionRule` pattern matching |
| `tests/filter_layer/test_filters.py` | `apply_all_filters()`, `FilterResult.merge()`, transitive exclusion, stable ordering |
| `tests/filter_layer/test_gitignore.py` | `load_gitignore()`, `apply_gitignore()` |

---

## Dependencies Verification

- [ ] Wave 7 `RawScanItem` type available
- [ ] `pathspec` library (optional - can use fnmatch)
- [ ] Standard library for pattern matching
- [ ] Compatible with Wave 10 (db_persistence) for logging