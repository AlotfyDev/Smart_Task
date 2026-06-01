# Wave 8: Entry Point Scanner

## Dependency
- Depends on: Wave 7 (identity_model.py — needs `StructuralElement` and `RawScanItem`)
- Source Specs: `samples/scanner_specs/entry_point_scanner_spec.md`

## Target
`samples/scanner/entry_point.py` (new file)

## Scope

Implement the filesystem scanner that walks from an entry point directory and produces raw scan tuples ready for filtering and identity assignment.

## What to Implement

### `class EntryPoint`

```python
@dataclass
class EntryPoint:
    path: Path
    depth_limit: int = 0           # 0 = unlimited
    include_patterns: list[str] | None = None
    exclude_patterns: list[str] | None = None   # applied AFTER filter stage
    follow_symlinks: bool = False
    scan_hidden: bool = False
    entry_point_id: str | None = None  # assigned at scan time
```

### `scan_entry_point(entry: EntryPoint) -> list[RawScanItem]`

Iterative stack-based DFS scan. From `entry_point_scanner_spec.md` section 2:

```python
RawScanItem = tuple[Path, int, bool, bool, int | None]
# (absolute_path, depth, is_dir, is_file, file_size)
```

**Algorithm (iterative stack):**
1. Push `(root, 0)` onto stack
2. While stack not empty:
   - Pop `(current_path, current_depth)`
   - Enforce depth limit
   - Skip hidden files unless `scan_hidden=True`
   - Handle symlinks: skip unless `follow_symlinks=True` + validate boundary
   - If directory: record it, sort children (dirs first, then alpha), push onto stack
   - If file: record it with size
   - Catch PermissionError, OSError → log warning, continue

**Edge cases:**
- Empty directories → recorded with no children
- Very deep hierarchies → depth limit protects
- Network drives → timeout wrapper (documented, not required yet)
- File deleted between iterdir() and stat() → FileNotFoundError → skip

### `_compute_depth(absolute_path: Path, entry_root: Path) -> int`

Depth = number of path components beyond entry root. Entry root = 0.

### Symlink boundary validation

When `follow_symlinks = True`, validate:
```python
real = current_path.resolve()
if entry.path.resolve() not in real.parents and real != entry.path.resolve():
    continue  # skip symlinks outside entry point boundary
```

## Verification

| # | Criterion |
|---|-----------|
| 1 | `scan_entry_point(EntryPoint(path=Path("smart_task/")))` returns correct number of items matching the directory |
| 2 | Depth values are correct: entry=0, direct child=1, nested=2+ |
| 3 | Hidden files are skipped when `scan_hidden=False` |
| 4 | Permission errors are caught and logged, not crashed |
| 5 | Output matches `RawScanItem` type exactly |
| 6 | Same directory scanned twice produces identical results (deterministic ordering) |

## Delivery
Single file: `samples/scanner/entry_point.py`
