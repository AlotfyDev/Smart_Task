# Wave 11 Execution Plan: Identity Cache

**Generated:** 2026-05-31  
**Status:** READY FOR IMPLEMENTATION  
**Dependency:** Wave 7 (identity_model.py) COMPLETE  
**Target:** `<CONFIGURABLE>/identity_cache.py` (see Configuration section)

---

## Configuration

### Path Configuration

Cache modules are configurable via:

| Source | Description |
|--------|-------------|
| CLI `--entry-point` | Entry point directory for scanning |
| CLI `--db-path` | Database path for persistence |
| `IdentityCacheBuilder.entry` | Configurable EntryPoint |
| `persist_to_db()` parameter | Configurable db_path |

---

## Required Implementation

| Component | Spec Requirement | Status |
|-----------|------------------|--------|
| `IdentityCache` class | Two-index dictionary lookup | ❌ MISSING |
| `ThreadSafeIdentityCache` | RLock-protected methods | ❌ MISSING |
| `IdentityCacheBuilder` | Pipeline orchestration | ❌ MISSING |
| `db_path` integration | Optional persistence param | ⚠️ NEEDS ADDITION |

---

## Step 1: Implement `IdentityCache` Class

### Tasks

```python
class IdentityCache:
```

- [ ] **Constructor:** `__init__(self)`:
  - `self._elements: dict[str, StructuralElement] = {}` (uuid → element)
  - `self._path_to_uuid: dict[str, str] = {}` (relative_path → uuid)
  - `self._entry_point: StructuralElement | None = None`

- [ ] **`add(self, element) -> None`**: Check duplicates, raise ValueError

- [ ] **`get_by_uuid(self, uuid)`**: O(1) lookup

- [ ] **`get_by_path(self, rel_path)`**: O(1) via secondary index

- [ ] **`get_all()`**, **`get_by_parent()`**, **`get_by_type()`**, **`get_by_depth()`**, **`count()`**, **`clear()`**

---

## Step 2: Implement `ThreadSafeIdentityCache`

- [ ] Inherit from `IdentityCache`
- [ ] Add `self._lock = threading.RLock()`
- [ ] Override all public methods with `with self._lock:`

---

## Step 3: Implement `IdentityCacheBuilder`

### Tasks

- [ ] Constructor: store `entry` and `user_rules`, create `IdentityCache()`

- [ ] **`build(self, db_session: Callable | None = None) -> IdentityCache`**:
  - Call `scan_entry_point(self.entry)` → `raw_items`
  - Call `apply_all_filters(raw_items, self.entry, self.user_rules)` → `filter_result`
  - Call `assign_uuids(filter_result.remaining, self.entry)` → `(ep_elem, elements_by_path)`
  - `self.cache.add(ep_elem)` (entry point first)
  - For each `(path, elem)` in `elements_by_path.items()`:
    - If `elem.entity_type != 'entry_point'`: `self.cache.add(elem)`
  - Call `assign_sort_orders(self.cache.get_all())`
  - **Integrate persistence via DI (not direct import):**
    - If `db_session` provided: call `db_session(self.cache)`
    - `builder.py` must NOT import `persist_to_db` directly — accept via `db_session: Callable`
  - Return `self.cache`

---

## Step 4: Verification

| # | Criterion | Test |
|---|-----------|------|
| 1 | Add/get round-trip | Cache operations work correctly |
| 2 | Duplicate detection | ValueError on duplicate UUID/path |
| 3 | Thread-safe operations | Concurrent access without corruption |
| 4 | Builder end-to-end | Full pipeline on test directory |
| 5 | Persistence integration | `db_path` parameter triggers save |

---

## File-Level Modular Architecture

| Module | File Decomposition | Rationale |
|--------|-------------------|-----------|
| `samples/scanner/identity_cache/` | `__init__.py` (facade) → `cache.py` (`IdentityCache` + `ThreadSafeIdentityCache` — data management + thread safety) → `builder.py` (`IdentityCacheBuilder` — orchestration of scan → filter → identity → persist) | Cache data management is separate from orchestration logic; builder also avoids direct coupling to Wave 10 via dependency injection |

---

## Test Strategy

### Philosophy
- **No gap masking** — if a capability is missing, fix the architecture, don't paper over it with trivial tests
- Every test MUST validate a real capability, not just "runs without error"
- All tests are runnable via `python -m pytest tests/ -v`

### Smoke Tests (end-to-end capability validation)
| # | Smoke Test | Validates |
|---|-----------|-----------|
| 1 | `IdentityCache.add()` then `get_by_uuid()` returns same element | O(1) primary index lookup, identity round-trip |
| 2 | `ThreadSafeIdentityCache` accessed from 4 concurrent threads | `RLock` prevents data corruption on simultaneous `add()`/`clear()` |
| 3 | `IdentityCacheBuilder.build()` runs full pipeline on a temp directory | End-to-end: scan → filter → identity → cache assembly succeeds |

### Behavioral Tests (capability-revealing, BDD-style)
| # | Behaviour | Given | When | Then |
|---|-----------|-------|------|------|
| 1 | `IdentityCacheBuilder.build()` accepts `db_session` via DI | A `Callable[[IdentityCache], None]` function | `builder.build(db_session=persist_fn)` is called | `persist_fn` receives the built `IdentityCache`; no direct `sqlite3` or `persist_to_db` import in `builder.py` |
| 2 | Cache hit vs miss correct | 3 elements added to cache | `get_by_uuid()` called with existing UUID then non-existing UUID | Hit returns `StructuralElement`; miss returns `None` |
| 3 | Duplicate detection | An element with UUID already in cache | `cache.add(duplicate_element)` is called | `ValueError` raised; cache state unchanged |
| 4 | `get_by_path()` secondary index | Element with `relative_path="src/main.py"` | `cache.get_by_path("src/main.py")` is called | Returns the same element as `get_by_uuid()` for the same entity |
| 5 | `get_by_parent()` children | Element A with 3 direct children B, C, D | `cache.get_by_parent(A.id)` is called | Returns `[B, C, D]` in insertion order; no grandchildren included |

### Gap → Architecture Fix Rule
If a test reveals a missing capability:
1. **DO NOT** write a test that passes trivially (e.g. `assert True`)
2. **DO NOT** skip the test with `@pytest.mark.skip`
3. **INSTEAD**: Identify the architectural layer where the gap belongs, implement, then test passes

### Test Files
| File | Scope |
|------|-------|
| `tests/identity_cache/test_cache.py` | `IdentityCache` all methods (add, get_by_uuid, get_by_path, get_all, get_by_parent, get_by_type, get_by_depth, count, clear), `ThreadSafeIdentityCache` concurrent access |
| `tests/identity_cache/test_builder.py` | `IdentityCacheBuilder.build()` pipeline, `db_session` DI (no direct imports from persistence layer), error propagation |