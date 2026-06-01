# Wave 7 Execution Plan: Identity Model

**Generated:** 2026-05-31  
**Status:** READY FOR IMPLEMENTATION  
**Dependency:** None (standalone module, independent of smart_task)  
**Target:** `<CONFIGURABLE>/identity_model.py` (see Configuration section)

---

## Configuration

### Path Configuration

**Smart Task is project-agnostic.** Target paths are determined by:

| Source | Description |
|--------|-------------|
| CLI `--topic-dir` | Topic files directory override |
| CLI `--output` | Output directory override |
| Environment variables | Project-specific path defaults |
| Configuration file | Custom path mappings |

**Do NOT hardcode project paths.** Modules should be importable from any location.

---

## Critical Gaps Analysis

### Module Purpose

Creates `StructuralElement` dataclass and identity management functions. Standalone - no smart_task dependency.

### Required Implementation

| Component | Spec Requirement | Status |
|-----------|------------------|--------|
| `StructuralElement` dataclass | 15 fields + 2 methods | ❌ MISSING |
| `RawScanItem` type alias | `tuple[Path, int, bool, bool, int|None]` | ❌ MISSING |
| `generate_id()` function | UUID v4 string | ❌ MISSING |
| `assign_uuids()` function | UUID assignment + ancestry | ❌ MISSING |
| `_build_ancestry()` function | Parent chain walking | ❌ MISSING |
| `assign_sort_orders()` function | Directory-first alphabetical | ❌ MISSING |

---

## Step 1: Define Type Aliases and Constants

### Tasks

- [ ] **RawScanItem:**
  ```python
  RawScanItem = tuple[Path, int, bool, bool, int | None]
  ```

- [ ] Import modules: dataclasses, pathlib, uuid, json

---

## Step 2: Implement `StructuralElement` Dataclass

### Tasks

- [ ] Create dataclass with 16 fields:
  - `id`, `entity_type`, `parent_id`, `entry_point_id`
  - `ancestry_ids`, `ancestry_names`, `name`, `relative_path`
  - `topo_key`, `depth`, `sort_order`, `classification`
  - `file_extension`, `file_size`, `created_at`

- [ ] Implement `to_dict()` - serialize lists as JSON
- [ ] Implement `from_dict()` - deserialize from JSON

---

## Step 3: Implement `generate_id()` Function

```python
def generate_id() -> str:
    return str(uuid.uuid4())
```

---

## Step 4: Implement `assign_uuids()` Function

### Algorithm

```python
def assign_uuids(raw_items: list[RawScanItem], entry_path: Path) -> tuple[StructuralElement, dict[Path, StructuralElement]]:
```

- [ ] Create entry point first (depth=0, relative_path=".")
- [ ] For remaining items, create StructuralElement with ancestry

---

## Step 5: Implement `_build_ancestry()` Function

- [ ] Walk parent chain
- [ ] Build ancestry_ids and ancestry_names lists

---

## Step 6: Implement `assign_sort_orders()` Function

- [ ] Skip entry_point elements
- [ ] Sort dirs before files, alphabetical within groups
- [ ] Assign sequential sort_order values

---

## Step 7: Verification

| # | Criterion | Test |
|---|-----------|------|
| 1 | Standalone import | Import without smart_task |
| 2 | Valid instance creation | Create StructuralElement |
| 3 | Round-trip serialization | to_dict/from_dict works |
| 4 | Ancestry chain correctness | Parent relationships correct |
| 5 | Sort order verification | Dirs before files |
| 6 | UUID format | Valid v4 UUID returned |

---

## File-Level Modular Architecture

| Module | File Decomposition | Rationale |
|--------|-------------------|-----------|
| `samples/scanner/identity_model/` | `__init__.py` (facade) → `types.py` (`RawScanItem` type alias, shared types) → `identity.py` (`StructuralElement` dataclass + `assign_uuids()` + `_build_ancestry()` + `assign_sort_orders()`) | Identity concerns: type definitions (shared across Waves 7-11), structural identity logic |

---

## Test Strategy

### Philosophy
- **No gap masking** — if a capability is missing, fix the architecture, don't paper over it with trivial tests
- Every test MUST validate a real capability, not just "runs without error"
- All tests are runnable via `python -m pytest tests/ -v`

### Smoke Tests (end-to-end capability validation)
| # | Smoke Test | Validates |
|---|-----------|-----------|
| 1 | `StructuralElement` constructed from `RawScanItem` tuple | Type alias + dataclass compatibility, all 15 fields populated |
| 2 | `generate_id()` returns UUID v4 string | UUID module import, string format `xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx` |
| 3 | `assign_uuids()` with 5 `RawScanItem` samples returns `(StructuralElement, dict[Path, StructuralElement])` | Correct output types, all items consumed, entry point created first |

### Behavioral Tests (capability-revealing, BDD-style)
| # | Behaviour | Given | When | Then |
|---|-----------|-------|------|------|
| 1 | entity_type assignment | A `RawScanItem` list with entry point, folders, and files | `assign_uuids()` processes all items | Root element has `entity_type="entry_point"`, directories get `"folder"`, files get `"file"` |
| 2 | STRUCTURAL_ORDER enforced | A mixed list of 3 directories and 3 files | `assign_sort_orders()` sorts elements | All directories precede all files; within each group, alphabetical |
| 3 | Root element invariants | Any valid `RawScanItem` list | `assign_uuids()` creates root element | Root has `depth=0`, `relative_path="."`, `sort_order=0`, `entry_point_id` equals its own `id` |
| 4 | Ancestry chain correctness | A deeply nested path `a/b/c/file.txt` | `_build_ancestry()` walks parent chain | `ancestry_ids` and `ancestry_names` each include the element itself as last entry |

### Gap → Architecture Fix Rule
If a test reveals a missing capability:
1. **DO NOT** write a test that passes trivially (e.g. `assert True`)
2. **DO NOT** skip the test with `@pytest.mark.skip`
3. **INSTEAD**: Identify the architectural layer where the gap belongs, implement, then test passes

### Test Files
| File | Scope |
|------|-------|
| `tests/identity_model/test_types.py` | `RawScanItem` type alias, `generate_id()` |
| `tests/identity_model/test_structural_element.py` | `StructuralElement` dataclass, `to_dict()`, `from_dict()` |
| `tests/identity_model/test_identity.py` | `assign_uuids()`, `_build_ancestry()`, `assign_sort_orders()` |