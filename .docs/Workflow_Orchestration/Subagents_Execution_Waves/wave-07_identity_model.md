# Wave 7: Identity Model

## Dependency
- Depends on: (none for Phase 1 — scanner core is independent of smart_task)
- Source Specs: `samples/scanner_specs/identity_model_spec.md`

## Target
`samples/scanner/identity_model.py` (new file)

## Scope

Implement the `StructuralElement` dataclass — the canonical representation of every filesystem element discovered by the scanner. This is the **foundation of Phase 1**.

## What to Implement

### `class StructuralElement`

Complete dataclass matching `identity_model_spec.md` section 3:

```python
@dataclass
class StructuralElement:
    id: str                              # UUID string
    entity_type: str                     # 'entry_point' | 'folder' | 'file'
    parent_id: str | None = None
    entry_point_id: str | None = None
    ancestry_ids: list[str] = ...
    ancestry_names: list[str] = ...
    name: str = ""
    relative_path: str = ""              # Posix, from entry point
    topo_key: str | None = None
    depth: int = 0
    sort_order: int = 0
    classification: str = "exists"
    file_extension: str | None = None
    file_size: int | None = None
    created_at: str = ""
```

**Methods:**
- `to_dict() -> dict` — serialization (JSON-dumps the list fields)
- `from_dict(d: dict) -> StructuralElement` — factory (JSON-loads list fields)

### `generate_id() -> str`

```python
def generate_id() -> str:
    return str(uuid.uuid4())
```

### `assign_uuids(raw_items: list[RawScanItem], entry: EntryPoint) -> tuple[StructuralElement, dict[Path, StructuralElement]]`

From `identity_model_spec.md` section 4. Must:
1. Create the entry point element first (depth=0)
2. For each subsequent item, create a StructuralElement with:
   - UUID-generated id
   - ancestry_ids = parent.ancestry_ids + [self.id]
   - ancestry_names = parent.ancestry_names + [self.name]
3. Return the entry point element and a path-keyed dict

### `_build_ancestry(elem, elements_by_path) -> tuple[list[str], list[str]]`

From `identity_model_spec.md` section 5. Walk parent chain to build full ancestry.

### `assign_sort_orders(elements: list[StructuralElement]) -> None`

From `identity_model_spec.md` section 6. Skip entry_point elements. Sort dirs before files, then alphabetical.

### `RawScanItem` Type Alias

```python
RawScanItem = tuple[Path, int, bool, bool, int | None]
# (absolute_path, depth, is_dir, is_file, file_size)
```

## Additional Requirements

- All paths in `relative_path` must use Posix forward slashes (`.replace("\\", "/")`)
- `ancestry_ids` and `ancestry_names` arrays always include the element itself as last entry
- `entry_point_id` is self-referential for the entry point element
- File with no extension → `file_extension = None`
- Entry point gets `sort_order = 0`, `depth = 0`, `relative_path = "."`

## Verification

| # | Criterion |
|---|-----------|
| 1 | `from smart_task...` wait — this is a standalone module. Must import without smart_task dependency |
| 2 | `StructuralElement()` creates valid instance |
| 3 | `to_dict()` → JSON → `from_dict()` round-trips correctly |
| 4 | `assign_uuids()` with 5 sample raw items produces correct ancestry chains |
| 5 | `assign_sort_orders()` sorts dirs before files, alphabetical within groups |
| 6 | `generate_id()` returns valid UUID v4 string |

## Delivery
Single file: `samples/scanner/identity_model.py`
