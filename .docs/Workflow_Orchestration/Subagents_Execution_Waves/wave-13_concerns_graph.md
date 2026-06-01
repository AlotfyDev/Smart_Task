# Wave 13: Concerns Graph ← Bridge Table

## Dependency
- Depends on: Wave 10 (db_persistence.py), Wave 11 (identity_cache.py)
- Source Specs: `samples/scanner_specs/four_graphs_integration_spec.md` section 3

## Targets
Potentially modifies: `samples/parsers/concerns_parser.py`
New file: `samples/scanner/concern_element_links.py` (bridge table DDL + queries)

## Scope

Rewrite the concerns graph to use the `concern_element_links` bridge table instead of the old `required_concerns` CSV column. Keep existing `parse_domain_gap_csv()`.

## What to Implement

### Concern-Element Links DDL

```sql
CREATE TABLE IF NOT EXISTS concern_element_links (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    concern_id      TEXT NOT NULL,
    element_id      TEXT NOT NULL REFERENCES structural_elements(id),
    link_type       TEXT NOT NULL DEFAULT 'affects',
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(concern_id, element_id, link_type)
);
```

### `extract_target_path(concern: dict, db_path: Path) -> list[str]`

From `four_graphs_integration_spec.md` section 3. Use DB queries instead of iterating all nodes:

1. Extract `.py` file references from evidence/proposed_solution using regex
2. Query `structural_elements` by `relative_path` (direct match, then LIKE)
3. Return matched UUIDs

### `link_concerns_to_structural(concerns: list[dict], db_path: Path) -> dict`

From `four_graphs_integration_spec.md` section 3. Two methods:
1. Read existing links from `concern_element_links` table
2. Extract new links via `extract_target_path()`
3. Return `dict[concern_id, list[element_id]]`

### `populate_concern_links_from_csv(files_csv: Path, db_path: Path)`

One-time migration from old `files.csv` required_concerns column → `concern_element_links` bridge table.

## Keep (unchanged)

- `parse_domain_gap_csv()` — still loads concerns from CSV files
- `parse_all_domain_gaps()` — still loads all domain gaps
- `parse_concern_dependencies()` — still parses dependency strings

## Verification

| # | Criterion |
|---|-----------|
| 1 | `extract_target_path()` correctly resolves paths from concern evidence against structural_elements DB |
| 2 | `link_concerns_to_structural()` returns correct concern-to-element UUID mapping |
| 3 | `populate_concern_links_from_csv()` populates bridge table correctly from existing CSV |
| 4 | Old `parse_domain_gap_csv()` still works unchanged |

## Delivery
Modified `samples/parsers/concerns_parser.py` + any new supporting files
