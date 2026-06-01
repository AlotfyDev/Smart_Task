# Wave 11: Identity Cache

## Dependency
- Depends on: Wave 7 (identity_model.py — needs `StructuralElement`)
- Source Specs: `samples/scanner_specs/cache_layer_spec.md`

## Target
`samples/scanner/identity_cache.py` (new file)

## Scope

Implement the in-memory cache that holds `StructuralElement` objects between identity creation and DB persistence, serving as the working set for the 4 Graphs.

## What to Implement

### `class IdentityCache`

From `cache_layer_spec.md` section 2:

```python
class IdentityCache:
    def __init__(self):
        self._elements: dict[str, StructuralElement] = {}   # uuid → element
        self._path_to_uuid: dict[str, str] = {}             # relative_path → uuid
        self._entry_point: StructuralElement | None = None
```

**Methods:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `add` | `(element: StructuralElement) -> None` | Add, raises `ValueError` on duplicate UUID or duplicate relative_path |
| `get_by_uuid` | `(uuid: str) -> StructuralElement \| None` | O(1) lookup |
| `get_by_path` | `(rel_path: str) -> StructuralElement \| None` | O(1) via secondary index |
| `get_all` | `() -> list[StructuralElement]` | All elements |
| `get_by_parent` | `(parent_uuid: str) -> list[StructuralElement]` | Direct children |
| `get_by_type` | `(entity_type: str) -> list[StructuralElement]` | Filter by entry_point/folder/file |
| `get_by_depth` | `(max_depth: int) -> list[StructuralElement]` | Filter by depth <= max |
| `count` | `() -> int` | Total element count |
| `clear` | `() -> None` | Purge all — for fresh scan |

### `class ThreadSafeIdentityCache(IdentityCache)`

From `cache_layer_spec.md` section 3:

```python
class ThreadSafeIdentityCache(IdentityCache):
    def __init__(self):
        super().__init__()
        self._lock = threading.RLock()

    def add(self, element): ...
    def get_by_uuid(self, uuid): ...
    def get_by_path(self, path): ...
    def get_all(self): ...
    def get_by_parent(self, parent_uuid): ...
    def get_by_type(self, entity_type): ...
    def count(self): ...
    def clear(self): ...
```

All methods use `with self._lock:`.

### `class IdentityCacheBuilder`

Helper class that orchestrates the scan → filter → identity → cache flow:

```python
class IdentityCacheBuilder:
    def __init__(self, entry: EntryPoint, user_rules: list[UserExclusionRule] | None = None):
        self.entry = entry
        self.user_rules = user_rules or []
        self.cache = IdentityCache()

    def build(self) -> IdentityCache:
        """Run full pipeline: scan → filter → identity → cache."""
        raw_items = scan_entry_point(self.entry)
        filter_result = apply_all_filters(raw_items, self.entry, self.user_rules)
        ep_elem, elements_by_path = assign_uuids(filter_result.remaining, self.entry)
        # Add entry point first
        self.cache.add(ep_elem)
        # Add remaining elements
        for path, elem in elements_by_path.items():
            if elem.entity_type != 'entry_point':
                self.cache.add(elem)
        assign_sort_orders(self.cache.get_all())
        return self.cache
```

## Verification

| # | Criterion |
|---|-----------|
| 1 | `add()` and `get_by_uuid()` round-trips correctly |
| 2 | Adding duplicate UUID raises `ValueError` |
| 3 | Adding duplicate relative_path raises `ValueError` |
| 4 | `get_by_parent()` returns correct children for a given parent UUID |
| 5 | `clear()` empties all structures |
| 6 | `ThreadSafeIdentityCache` can be used from multiple threads without data corruption |
| 7 | `IdentityCacheBuilder.build()` runs end-to-end with a test directory |

## Delivery
Single file: `samples/scanner/identity_cache.py`
