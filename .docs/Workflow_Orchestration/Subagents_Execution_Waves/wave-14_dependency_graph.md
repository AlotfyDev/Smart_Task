# Wave 14: Dependency Graph ← UUID Resolution

## Dependency
- Depends on: Wave 10 (db_persistence.py), Wave 11 (identity_cache.py)
- Source Specs: `samples/scanner_specs/four_graphs_integration_spec.md` section 4

## Targets
Potentially modifies: `samples/parsers/dependency_parser.py`

## Scope

Rewrite the dependency graph to resolve file paths to UUIDs via `structural_elements.relative_path` instead of the old CSV-based `path_to_taxonomy_id` mapping.

## What to Implement

### `scan_and_register_dependencies(src_dir, db_path, entry_point_id) -> tuple[list[dict], list[tuple]]`

From `four_graphs_integration_spec.md` section 4:

1. Build `relative_path → uuid` lookup from DB:
```sql
SELECT relative_path, id FROM structural_elements
WHERE entry_point_id = ? AND entity_type = 'file' AND classification = 'exists'
```
2. AST-scan all `.py` files in `src_dir`
3. For each import, resolve target module path
4. If target exists in `path_to_uuid`, record edge `(file_uuid, target_uuid)`
5. Return `(module_nodes, import_edges)`

### Dependency Edges DDL

```sql
CREATE TABLE IF NOT EXISTS dependency_edges (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    from_id     TEXT NOT NULL REFERENCES structural_elements(id) ON DELETE CASCADE,
    to_id       TEXT NOT NULL REFERENCES structural_elements(id) ON DELETE CASCADE,
    edge_type   TEXT NOT NULL DEFAULT 'imports',
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(from_id, to_id)
);
```

### `register_dependency_edges(edges, db_path)`

Write edges to DB in transaction. Delete old edges first (fresh per scan).

## Keep (unchanged)

- `_resolve_module()` — module name → path resolution
- `_resolve_from_node()` — ImportFrom node → module parts
- `scan_source_modules()` — AST scanning logic (the path resolution changes, but the AST walk stays)
- `detect_cycles()` — cycle detection
- `topological_sort()` — topological ordering

## Remove (obsolete)

- `map_imports_to_taxonomy()` — replaced by `path_to_uuid` DB lookup
- `register_file_dependencies()` — replaced by `register_dependency_edges()`

## Verification

| # | Criterion |
|---|-----------|
| 1 | `scan_and_register_dependencies()` on a test `src/` with known imports produces correct UUID pairs |
| 2 | `dependency_edges` table contains correct edges after registration |
| 3 | Existing `detect_cycles()` and `topological_sort()` still work with new UUID-based edge format |
| 4 | Old functions (`map_imports_to_taxonomy`) are removed or deprecated with clear note |

## Delivery
Modified `samples/parsers/dependency_parser.py`
