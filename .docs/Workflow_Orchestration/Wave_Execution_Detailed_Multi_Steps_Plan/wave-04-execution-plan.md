# Wave 4 Execution Plan: importer.py + exporter.py + wave_manager.py

**Generated:** 2026-05-31  
**Status:** READY FOR IMPLEMENTATION  
**Dependency:** Wave 3 (json_schema.py + parser.py + repository.py) COMPLETE

---

## Critical Gaps Analysis

### Current State Issues

| Component | Current Implementation | Spec Requirement | Gap |
|-----------|------------------------|-----------------|-----|
| `smart_task/importer/` | **DOES NOT EXIST** | Full TopicToTicketImporter implementation | ❌ MISSING MODULE |
| `smart_task/exporter/__init__.py` | Stub methods (`...`) | WaveExporter full implementation | ❌ STUB ONLY |
| `smart_task/wave_manager/__init__.py` | Stub methods (`...`) | WaveManager full implementation | ❌ STUB ONLY |

### Specific Issues Identified

1. **Missing Module:** `importer/` directory does not exist
2. **Exporter Methods Stubbed:**
   - `export_wave` - incomplete signature (spec: `wave_id: str, output_format: str = 'markdown'`)
   - All export methods are stubs
   - Missing `export_to_files` method
3. **WaveManager Methods Stubbed:**
   - `create_wave`, `assign_tickets`, `get_wave_summary`, `get_project_summary` - all stubs
   - Missing strategy implementations (`by_dependency`, `by_priority`, `balanced`)

---

## Step 1: Create `smart_task/importer/__init__.py`

### Module Creation Required

```bash
mkdir smart_task/importer
touch smart_task/importer/__init__.py
```

### Tasks

- [ ] **Constructor:** `__init__(self, db_path: Path, repo: TicketRepository | None = None)`
  - Store `db_path`
  - Create repo if not provided (pass to WaveManager pattern)
  - No circular imports (use late imports or inject repo)

- [ ] **`load_mappings(path: Path) -> dict`**
  - Read JSON file from `path`
  - Return parsed mapping dictionary
  - No validation (trust the mapping format)

- [ ] **`import_topic_file(topic_path: Path, mapping: dict) -> list[MicroTaskTicket]`**
  - Read `.md` file content
  - Parse YAML front matter (lines after `---` delimiter to `---` or `---` at end)
  - Extract: `source_spec`, `start_line`, `end_line`
  - Extract body text as `spec_context`
  - Look up mapping entry by topic filename
  - For each sequence in mapping:
    - Generate ticket ID: `TASK-{spec_prefix}-{sequence:03d}`
    - Fill title, objective from templates
    - Set all traceability fields
    - Set `phase`, `effort`, `tags` from mapping
    - Set `status = 'pending'`
  - Return list of `MicroTaskTicket`

- [ ] **`import_all(topics_dir: Path, mappings_path: Path) -> int`**
  - Load mappings via `load_mappings()`
  - Iterate all `.md` files in `topics_dir`
  - For each file: call `import_topic_file()`
  - Batch insert via repository
  - Return total ticket count

- [ ] **`import_mapping_to_db(repo, mapping: dict)`**
  - Insert mapping entries into `topic_to_ticket_mapping` table
  - For traceability (optional, for audit)

---

## Step 2: Implement `smart_task/exporter/__init__.py`

### Tasks

- [ ] **Fix Constructor:** `__init__(self, repo: TicketRepository)`
- [ ] **Fix `export_wave(wave_id: str, output_format: str = 'markdown') -> str`**
  - Get wave via `repo.get_wave(wave_id)`
  - Get tickets via `repo.list_tickets(wave_id=wave_id)`
  - Dispatch to `export_to_markdown` or `export_to_json`

- [ ] **`export_to_markdown(tickets: list[MicroTaskTicket], wave: TaskWave) -> str`**
  - Build markdown according to spec format
  - Header: `# Wave: {wave_id}\nPhase: {phase} | Status: {status} | Tickets: {count}`
  - For each ticket section:
    ```markdown
    ## TASK-IDM-001: Create DDL schema
    **Source:** identity_model_spec.md (lines 11-28)
    **Priority:** High | **Effort:** S | **Phase:** 2
    **Objective:** Write the DDL...
    **Spec Context:** ``` ... ```
    **Dependencies:** *none* or list
    **Acceptance Criteria:** - [ ] Criterion 1
    **Verification:** ```shell ... ```
    ---
    ```

- [ ] **`export_to_json(tickets: list[MicroTaskTicket], wave: TaskWave) -> str`**
  - Build JSON: `{wave: {...}, tickets: [{...}, ...]}`

- [ ] **`export_to_files(wave_id: str, output_dir: Path, output_format: str) -> list[Path]`**
  - Create `output_dir` if needed
  - Write each ticket to individual file
  - Return list of created file paths

---

## Step 3: Implement `smart_task/wave_manager/__init__.py`

### Tasks

- [ ] **Constructor:** `__init__(self, repo: TicketRepository)`
  - Store repository reference

- [ ] **`create_wave(wave_id: str, phase: int, description: str) -> TaskWave`**
  - Create `TaskWave` instance
  - INSERT into database
  - Return the wave

- [ ] **`assign_tickets(wave_id: str, count: int | None = None, strategy: str = 'by_dependency') -> int`**
  - Get pending tickets: `repo.get_ready_tickets(phase)`
  - Apply strategy sorting:
    - `by_dependency`: fewest unresolved dependencies first
    - `by_priority`: High → Medium → Low
    - `balanced`: round-robin across priority levels
  - Limit to `count` if provided
  - UPDATE `wave_id` on selected tickets
  - UPDATE `ticket_count` on wave
  - Set wave status to `'active'`
  - Return count assigned

- [ ] **`get_wave_summary(wave_id: str) -> dict`**
  - Get wave details
  - Count tickets in wave
  - Return `{id, phase, description, status, ticket_count}`

- [ ] **`get_project_summary() -> dict`**
  - Query counts: total tickets, by phase, by status, by priority
  - Count waves: active, completed, total
  - Calculate completion percentage
  - Return exact format:
    ```python
    {
        "total_tickets": int,
        "by_phase": {1: int, 2: int, 3: int},
        "by_status": {"pending": int, "in_progress": int, "completed": int},
        "by_priority": {"High": int, "Medium": int, "Low": int},
        "waves": {"active": int, "completed": int, "total": int},
        "completion_pct": float,
    }
    ```

---

## Step 4: Integration Verification

### Verification Criteria (from spec)

- [ ] Criterion 1: All 3 files importable without errors
- [ ] Criterion 2: Can load sample JSON mapping file with `TopicToTicketImporter.load_mappings()`
- [ ] Criterion 3: `WaveExporter.export_to_markdown()` produces valid markdown with all ticket fields
- [ ] Criterion 4: `WaveManager.create_wave()` + `assign_tickets()` produces correct assignments
- [ ] Criterion 5: `WaveManager.get_project_summary()` returns complete stats dict without errors

---

## File-Level Modular Architecture

| Module | File Decomposition | Rationale |
|--------|-------------------|-----------|
| `importer/` | `__init__.py` (facade + orchestration) → `yaml_parser.py` (YAML front-matter parsing) → `ticket_generator.py` (ticket creation from templates) → `batch_inserter.py` (batch DB insertion) | 4 distinct concerns: parsing, generation, persistence, orchestration |
| `exporter/` | `__init__.py` (facade + dispatch) → `markdown.py` (markdown formatting) → `json_format.py` (JSON serialization) → `file_writer.py` (file output) | 3 concerns: markdown export, JSON export, file I/O |
| `wave_manager/` | `__init__.py` (facade + orchestration) → `assigner.py` (wave assignment strategies) → `stats.py` (statistics/completeness) | 3 concerns: assignment logic, statistics, orchestration |

## Test Strategy

### Philosophy
- **No gap masking** — if a capability is missing, fix the architecture, don't paper over it with trivial tests
- Every test MUST validate a real capability, not just "runs without error"
- All tests are runnable via `python -m pytest tests/ -v`

### Smoke Tests (end-to-end capability validation)
| # | Smoke Test | Validates |
|---|-----------|-----------|
| 1 | `TopicToTicketImporter.load_mappings(sample_mapping.json)` returns dict with expected spec keys | Importer can read and parse mapping JSON |
| 2 | `TopicToTicketImporter.import_topic_file(sample_topic.md, mapping)` returns list of `MicroTaskTicket` with correct IDs like `TASK-IDM-001` | YAML front-matter parsing + ticket generation from templates |
| 3 | `TopicToTicketImporter.import_all(topics_dir, mappings_path)` inserts tickets into DB and returns count | Batch import pipeline (parse -> generate -> persist) |
| 4 | `WaveExporter.export_to_markdown(tickets, wave)` returns string containing `# Wave:`, ticket sections, and `- [ ]` checklists | Markdown export with all ticket fields |
| 5 | `WaveExporter.export_to_json(tickets, wave)` returns valid JSON string parseable by `json.loads()` | JSON serialization |
| 6 | `WaveManager.create_wave(wave_id, phase, desc)` inserts into DB and returns `TaskWave` with correct fields | Wave creation + persistence |
| 7 | `WaveManager.assign_tickets(wave_id, strategy='by_dependency')` updates ticket `wave_id` and returns assignment count | Wave assignment logic |
| 8 | `WaveManager.get_project_summary()` returns dict with all keys: `total_tickets`, `by_phase`, `by_status`, `by_priority`, `waves`, `completion_pct` | Project statistics aggregation |

### Behavioral Tests (capability-revealing, BDD-style)
| # | Behaviour | Given | When | Then |
|---|-----------|-------|------|------|
| 1 | Ticket ID pattern enforcement | A mapping entry with prefix = `IDM`, sequence = 1 | `import_topic_file` processes matching topic | Generated ticket `id` matches regex `^TASK-IDM-001$` |
| 2 | Multi-ticket topic expansion | A mapping entry with 3 sequences | `import_topic_file` processes the topic | Returns list of length 3, IDs sequential (`TASK-IDM-001`, `TASK-IDM-002`, `TASK-IDM-003`) |
| 3 | Traceability fields populated | A topic file with YAML front matter `source: identity_model_spec.md`, `start_line: 11`, `end_line: 28` | `import_topic_file` processes it | Ticket has `source_spec = "identity_model_spec.md"`, `source_line_range = "11-28"` |
| 4 | Wave assignment by_dependency ordering | Tickets A (0 deps), B (depends on A), C (depends on A, B) | `assign_tickets(wave_id, strategy='by_dependency')` | Assignment order: A -> B -> C |
| 5 | Wave assignment by_priority ordering | Tickets with priorities High, Medium, Low, all 0 deps | `assign_tickets(wave_id, strategy='by_priority')` | Assignment order: High -> Medium -> Low |
| 6 | Wave assignment balanced ordering | Equal counts of High, Medium, Low priority tickets | `assign_tickets(wave_id, strategy='balanced')` | Assignment alternates: H, M, L, H, M, L, ... |
| 7 | Export markdown includes all fields | A wave with 3 tickets having title, objective, spec_context, dependencies, acceptance_criteria, verification_method | `export_to_markdown` is called | Output contains `**Source:**`, `**Priority:**`, `**Effort:**`, `**Objective:**`, `**Spec Context:**`, `**Acceptance Criteria:**`, `**Verification:**` for each ticket |
| 8 | Project summary counting | DB has tickets across phases 1, 2, 3 with various statuses and priorities | `get_project_summary()` is called | `by_phase` sums match total, `by_status` sums match total, `completion_pct` is correct |
| 9 | Status field default | A freshly imported ticket with no wave assignment | Inspect its `status` field | `status == 'pending'` |

### Gap -> Architecture Fix Rule
If a test reveals a missing capability (e.g. "no validation for ticket ID pattern"):

1. **DO NOT** write a test that passes trivially (e.g. `assert True`)
2. **DO NOT** skip the test with `@pytest.mark.skip`
3. **INSTEAD**: Identify the architectural layer where the gap belongs
4. Implement the capability at the correct layer
5. Then the test passes naturally

### Test Files
| File | Scope |
|------|-------|
| `tests/test_importer.py` | `TopicToTicketImporter` — mapping loading, topic file parsing, ticket generation, batch import |
| `tests/test_exporter.py` | `WaveExporter` — markdown export, JSON export, file output |
| `tests/test_wave_manager.py` | `WaveManager` — wave CRUD, assignment strategies, project statistics |

---

## Dependencies Verification

- [ ] Wave 3 must be complete (TicketRepository, parser functions available)
- [ ] No circular imports (importer doesn't import from exporter/wave_manager)
- [ ] All `smart_task.models` imports work
- [ ] Repository pattern properly integrated