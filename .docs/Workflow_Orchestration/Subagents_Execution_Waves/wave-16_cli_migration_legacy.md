# Wave 16: CLI Migration + Legacy Cleanup

## Dependency
- Depends on: Waves 12-15 (all 4 graphs rewired to DB)
- Source Specs: `samples/scanner_specs/four_graphs_integration_spec.md` section 8

## Targets
- `samples/cli.py` (modify)
- `samples/__init__.py` (modify)
- `samples/parsers/__init__.py` (modify)
- `samples/parsers/structural_parser.py` (deprecate/remove)
- `samples/parsers/tasks_parser.py` `create_implementation_tasks()` (remove)
- `samples/parsers/dependency_parser.py` `map_imports_to_taxonomy()` + `register_file_dependencies()` (remove)

## Scope

This is the final migration wave. Update the CLI to use the new DB-backed pipeline, remove/disable legacy CSV-based code, and ensure full backward-compatible output.

## What to Implement

### CLI Update (`samples/cli.py`)

Add the scan pipeline as an optional first step:

```
python -m graph.cli --scan --entry-point src/ --summary
python -m graph.cli --summary         # use cached DB
```

Key changes:
- `build_graph()` should detect if DB is available and prefer DB pipeline
- Add `--scan` flag that triggers: scan → filter → identity → persist → 4 graphs
- Add `--entry-point` argument (default: project `src/`)
- Add `--db-path` argument (default: `.scanner/structural_elements.db`)
- All existing commands (`--summary`, `--taxonomy`, `--taxonomy-text`, `--concerns`, `--tasks`, `--tasks-text`, `--cycles`, `--topo`, `--node`, `--html`, `--save-taxonomy`) must produce identical or improved output

### `USE_DB_SCANNER` Flag

In `samples/parsers/__init__.py`:

```python
USE_DB_SCANNER = os.getenv("USE_DB_SCANNER", "1") == "1"

def parse_structural_taxonomy(roadmap_dir=None, db_path=None):
    if USE_DB_SCANNER and db_path:
        from graph.scanner.identity_cache import IdentityCacheBuilder
        ... # run scanner pipeline
    else:
        from .structural_parser import parse_structural_taxonomy as _old
        return _old(roadmap_dir)
```

Default is `USE_DB_SCANNER=1` (new pipeline active by default).

### Legacy Code Cleanup

**Remove (code deleted or replaced with import to new module):**
- `samples/parsers/structural_parser.py` — entire file (replaced by scanner + DB)
- `samples/parsers/tasks_parser.py` `create_implementation_tasks()` — replaced by `create_implementation_tasks_from_db()`
- `samples/parsers/dependency_parser.py` `map_imports_to_taxonomy()` + `register_file_dependencies()` — replaced by UUID resolution
- `samples/parsers.py` (the legacy file at `samples/parsers.py`) — entire file removed

**Keep (still needed):**
- `samples/parsers/concerns_parser.py` `parse_domain_gap_csv()` — still loads concerns
- `samples/parsers/tasks_parser.py` `parse_buggy_components()` — still loads buggy entries
- `samples/parsers/dependency_parser.py` `scan_source_modules()` — AST scanning logic stays
- `samples/parsers/dependency_parser.py` `detect_cycles()` — cycle detection stays
- `samples/parsers/dependency_parser.py` `topological_sort()` — topological sort stays

## Verification

| # | Criterion |
|---|-----------|
| 1 | `python -m graph.cli --summary` produces same field names and structure as before |
| 2 | `python -m graph.cli --scan --entry-point src/ --summary` runs scan pipeline successfully |
| 3 | All existing CLI commands work without errors |
| 4 | `USE_DB_SCANNER=0` falls back to old CSV pipeline |
| 5 | Legacy `samples/parsers.py` is removed (no import errors because nothing imports it) |
| 6 | Removed functions are no longer exported from `samples/parsers/__init__.py` |

## Delivery
Multiple file modifications across `samples/`
