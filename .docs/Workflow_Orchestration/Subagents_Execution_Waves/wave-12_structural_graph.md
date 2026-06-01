# Wave 12: Structural Graph ← DB

## Dependency
- Depends on: Wave 10 (db_persistence.py), Wave 11 (identity_cache.py)
- Source Specs: `samples/scanner_specs/four_graphs_integration_spec.md` section 2

## Targets
Potentially modifies: `samples/parsers/structural_parser.py` (rewrite to DB source)
Or new file: `samples/parsers/structural_graph_from_db.py`

## Scope

Rewrite the structural graph builder to consume data from the `structural_elements` table + `IdentityCache` instead of parsing CSV files.

## What to Implement

### `build_structural_graph(cache: IdentityCache) -> dict`

From `four_graphs_integration_spec.md` section 2:

```python
def build_structural_graph(cache: IdentityCache) -> dict:
    return {
        "entry_points": [e for e in cache.get_all() if e.entity_type == "entry_point"],
        "folders":      [e for e in cache.get_all() if e.entity_type == "folder"],
        "files":        [e for e in cache.get_all() if e.entity_type == "file" and e.classification == "exists"],
        "file_stubs":   [e for e in cache.get_all() if e.classification == "to_be_implemented"],
    }
```

### `get_structural_nodes(db_path: Path, entry_point_id: str) -> dict`

From `four_graphs_integration_spec.md` section 2:

```python
def get_structural_nodes(db_path: Path, entry_point_id: str) -> dict:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT * FROM structural_elements
        WHERE entry_point_id = ?
        ORDER BY depth, sort_order
    """, (entry_point_id,))
    return {row["id"]: dict(row) for row in rows}
```

### Old-to-New Mapping

Implement the mapping from old CSV concepts to new DB fields:

| Old CSV Concept | New DB Equivalent |
|-----------------|-------------------|
| `domain` | `entity_type = 'folder'` where `depth = 1` |
| `subdomain` | `entity_type = 'folder'` where `depth >= 2` |
| `file` | `entity_type = 'file'`, `classification = 'exists'` |
| `file_stub` | `entity_type = 'file'`, `classification = 'to_be_implemented'` |
| `element_number` | `topo_key` |
| `full_path` | `relative_path` |
| parent from element_number | `parent_id` FK |

## Verification

| # | Criterion |
|---|-----------|
| 1 | `build_structural_graph()` with test cache returns correct structure for a known directory tree |
| 2 | `get_structural_nodes()` returns same results from DB as from cache |
| 3 | Output format matches what the presentation layer expects (backward compat) |
| 4 | Old CSV-based parser still works alongside (coexistence mode) |

## Delivery
New or modified file in `samples/parsers/`
