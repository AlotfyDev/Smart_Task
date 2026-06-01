# Wave 9: Filter Layer

## Dependency
- Depends on: Wave 7 (identity_model.py — needs `RawScanItem`)
- Source Specs: `samples/scanner_specs/filter_layer_spec.md`

## Target
`samples/scanner/filter_layer.py` (new file)

## Scope

Implement the three-tier filter stage that sits between raw scanning and identity creation. Filters exclude unwanted items from the taxonomy (gitignore → third-party → user exclusions).

## What to Implement

### `class ExcludedItem`

```python
@dataclass
class ExcludedItem:
    path: Path
    reason_code: str
    detail: str
```

### `class FilterResult`

```python
@dataclass
class FilterResult:
    excluded: list[ExcludedItem]
    remaining: list[RawScanItem]

    @property
    def all_excluded_paths(self) -> set[Path]: ...
    def merge(self, other: "FilterResult") -> "FilterResult": ...
```

### `load_gitignore(entry_root: Path) -> pathspec.PathSpec | None`

Read `.gitignore` from the entry point root directory. Returns `None` if no `.gitignore` found.

**Note:** Only the root `.gitignore` is read. Nested `.gitignore` files are not parsed (design decision, covered by user exclusion rules).

### `apply_gitignore(items, entry_root, spec) -> FilterResult`

From `filter_layer_spec.md` section 2 Tier A. Match each item against gitignore patterns using `pathspec`.

### `apply_third_party(items, entry_root) -> FilterResult`

From `filter_layer_spec.md` section 2 Tier B. Static list of known third-party paths:

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

### `class UserExclusionRule`

```python
@dataclass
class UserExclusionRule:
    pattern: str
    reason: str = "USER_EXCLUDED"
    description: str = ""
```

### `apply_user_exclusions(items, entry_root, rules) -> FilterResult`

From `filter_layer_spec.md` section 2 Tier C.

### `apply_all_filters(items, entry, user_rules) -> FilterResult`

Orchestrate the three tiers in sequence. Apply gitignore → third-party → user. Merge excluded lists. Handle transitive directory exclusion (if a directory is excluded, all its children are transitively excluded).

**Transitive exclusion:**
```python
def _is_blocked(path: Path, blocked_dirs: set[Path]) -> bool:
    for parent in path.parents:
        if parent in blocked_dirs:
            return True
    return False
```

## Additional Files

Create the audit log table DDL alongside the filter layer — or ensure it's referenced:
```sql
CREATE TABLE IF NOT EXISTS scan_exclusion_log (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_id       TEXT NOT NULL,
    excluded_path TEXT NOT NULL,
    reason_code   TEXT NOT NULL,
    detail        TEXT NOT NULL,
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);
```

## Verification

| # | Criterion |
|---|-----------|
| 1 | `apply_gitignore()` with mock `.gitignore` correctly excludes matching items |
| 2 | `apply_third_party()` correctly excludes `.venv`, `.git`, `__pycache__` |
| 3 | `apply_user_exclusions()` with a `["legacy/**"]` rule correctly excludes nested files |
| 4 | Transitive exclusion: if `legacy/` is excluded, `legacy/sub/file.py` is also excluded |
| 5 | `apply_all_filters()` with no `.gitignore` and no user rules still removes third-party paths |
| 6 | `FilterResult.merge()` correctly combines multiple filter passes |

## Delivery
Single file: `samples/scanner/filter_layer.py`
