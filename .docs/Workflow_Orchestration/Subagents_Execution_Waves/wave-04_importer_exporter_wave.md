# Wave 4: importer.py + exporter.py + wave_manager.py

## Dependency
- Depends on: Wave 3 (json_schema.py + parser.py + repository.py)
- Required by: Wave 5 (cli.py)

## Targets
- `smart_task/importer/` (package with `__init__.py`, `yaml_parser.py`, `ticket_generator.py`, `batch_inserter.py`)
- `smart_task/exporter/` (package with `__init__.py`, `markdown.py`, `json_format.py`, `file_writer.py`)
- `smart_task/wave_manager/` (package with `__init__.py`, `assigner.py`, `stats.py`)

## Scope

Implement the import pipeline (topic files → tickets), export pipeline (wave → deliverable files), and wave orchestration logic.

## importer.py

### `class TopicToTicketImporter`

**Constructor:** `__init__(self, db_path: Path, repo: TicketRepository | None = None)`

| Method | Signature | Description |
|--------|-----------|-------------|
| `load_mappings` | `(path: Path) -> dict` | Load the JSON mapping file that defines how topic files become tickets |
| `import_topic_file` | `(topic_path: Path, mapping: dict) -> list[MicroTaskTicket]` | Process one topic file into tickets per its mapping entry |
| `import_all` | `(topics_dir: Path, mappings_path: Path) -> int` | Iterate all topic files, apply mappings, insert into DB, return count |

**Algorithm for `import_topic_file`:**

1. Read the topic `.md` file
2. Parse its YAML front matter to get `source_spec`, `start_line`, `end_line`
3. Extract the body text after front matter as `spec_context`
4. Look up the mapping entry for this topic file name
5. For each mapping entry (can be multiple sequences per topic), generate a `MicroTaskTicket`:
   - `id` = `TASK-{spec_prefix}-{sequence:03d}`
   - `title` = render `title_template` (optional f-string substitution with topic metadata)
   - `objective` = render `objective_template`
   - `spec_context` = from topic file body
   - `source_spec`, `source_topic_file`, `source_line_range` = from YAML front matter
   - `phase`, `effort`, `tags` = from mapping entry
   - `status` = `'pending'`

### `import_mapping_to_db(repo: TicketRepository, mapping: dict) -> None`

Alternatively, insert mapping entries into the `topic_to_ticket_mapping` table for traceability.

## exporter.py

### `class WaveExporter`

| Method | Signature | Description |
|--------|-----------|-------------|
| `__init__` | `(repo: TicketRepository)` | |
| `export_wave` | `(wave_id: str, output_format: str = 'markdown') -> str` | Main dispatcher |
| `export_to_markdown` | `(tickets: list[MicroTaskTicket], wave: TaskWave) -> str` | Full markdown with all fields |
| `export_to_json` | `(tickets: list[MicroTaskTicket], wave: TaskWave) -> str` | JSON array |
| `export_to_files` | `(wave_id: str, output_dir: Path, output_format: str) -> list[Path]` | Write each ticket to its own file in `output_dir` |

**Markdown format:**

```markdown
# Wave: {wave_id}
Phase: {phase} | Status: {status} | Tickets: {count}

---

## TASK-IDM-001: Create DDL schema

**Source:** identity_model_spec.md (lines 11-28)
**Priority:** High | **Effort:** S | **Phase:** 2

**Objective:**
Write the DDL...

**Spec Context:**
```sql
...
```

**Dependencies:** *none*
**File Targets:** `samples/scanner/schema.py`

**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2

**Verification:**
```shell
python -m pytest ...
```

---
```

## wave_manager.py

### `class WaveManager`

| Method | Signature | Description |
|--------|-----------|-------------|
| `__init__` | `(repo: TicketRepository)` | |
| `create_wave` | `(wave_id: str, phase: int, description: str) -> TaskWave` | INSERT + return |
| `assign_tickets` | `(wave_id: str, count: int \| None = None, strategy: str = 'by_dependency') -> int` | Auto-assign pending tickets to wave |
| `get_wave_summary` | `(wave_id: str) -> dict` | Stats per wave |
| `get_project_summary` | `() -> dict` | Global stats across all phases |

**Strategies for `assign_tickets`:**

| Strategy | Behavior |
|----------|----------|
| `'by_dependency'` | Tickets with fewest unresolved dependencies first |
| `'by_priority'` | Highest priority first (High → Medium → Low) |
| `'balanced'` | Interleave: pick from each priority level in round-robin |

**`get_project_summary()` return format:**

```python
{
    "total_tickets": 157,
    "by_phase": {1: 84, 2: 56, 3: 17},
    "by_status": {"pending": 157, "in_progress": 0, "completed": 0},
    "by_priority": {"High": 45, "Medium": 82, "Low": 30},
    "waves": {"active": 0, "completed": 0, "total": 0},
    "completion_pct": 0.0,
}
```

## Verification

| # | Criterion |
|---|-----------|
| 1 | All 3 files importable without errors |
| 2 | Can load a sample JSON mapping file with `TopicToTicketImporter.load_mappings()` |
| 3 | `WaveExporter.export_to_markdown()` produces valid markdown with all ticket fields |
| 4 | `WaveManager.create_wave()` + `assign_tickets()` produces correct assignments |
| 5 | `WaveManager.get_project_summary()` returns complete stats dict without errors |

## Delivery
Three packages: `smart_task/importer/`, `smart_task/exporter/`, `smart_task/wave_manager/`
