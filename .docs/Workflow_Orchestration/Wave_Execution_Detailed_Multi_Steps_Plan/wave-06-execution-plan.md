# Wave 6 Execution Plan: Import 157 Topic Files → Tickets

**Generated:** 2026-05-31  
**Status:** DATA PROCESSING WAVE (NOT CODE WRITING)  
**Dependency:** Wave 5 (cli.py) COMPLETE

---

## Critical Analysis

### Wave Type Classification

This is a **DATA PROCESSING** wave, NOT a code implementation wave. The code is already provided by Waves 1-5.

### Current State Requirements

| Requirement | Status | Notes |
|-------------|--------|-------|
| Topic files available | ? | Need to verify `_TOPICS` directories |
| Mapping rules JSON | MISSING | Must be created |
| CLI tools operational | INCOMPLETE | Wave 5 must be complete first |

---

## Step 1: Create Topic-to-Ticket Mappings JSON

### Target File
`.docs/Workflow_Orchestration/topic_to_ticket_mappings.json`

### Tasks

- [ ] Create JSON structure with all spec modules:
  ```json
  {
    "identity_model_spec": { "prefix": "IDM", "topic_dir": "...", "phase": 1, "topics": {...} },
    "entry_point_scanner_spec": { "prefix": "SCN", "topic_dir": "...", "phase": 1, "topics": {...} },
    "filter_layer_spec": { "prefix": "FLT", "topic_dir": "...", "phase": 1, "topics": {...} },
    "cache_layer_spec": { "prefix": "CAC", "topic_dir": "...", "phase": 1, "topics": {...} },
    "db_persistence_spec": { "prefix": "DBP", "topic_dir": "...", "phase": 1, "topics": {...} },
    "four_graphs_integration_spec": { "prefix": "GRH", "topic_dir": "...", "phase": 2, "topics": {...} }
  }
  ```

- [ ] For each topic file in each spec:
  - Identify sequences (1-4 tickets per topic based on complexity)
  - Set `title`, `effort` (S/M/L/XL), `tags`
  - Use naming convention from examples

- [ ] Apply ticket count guidelines:
  | Topic Type | Tickets | Examples |
  |------------|---------|----------|
  | DDL table | 1 | `CREATE_TABLE` + constraints |
  | Dataclass | 2 | class def + to_dict/from_dict |
  | Algorithm | 2 | main + edge cases |
  | Multi-tier | 3 | one per tier |
  | Integration | 2-4 | multiple components |

---

## Step 2: Verify Topic Files Availability

### Tasks

- [ ] Locate all `_TOPICS` directories:
  - `samples/scanner_specs/identity_model_spec_TOPICS/`
  - `samples/scanner_specs/entry_point_scanner_spec_TOPICS/`
  - `samples/scanner_specs/filter_layer_spec_TOPICS/`
  - `samples/scanner_specs/cache_layer_spec_TOPICS/`
  - `samples/scanner_specs/db_persistence_spec_TOPICS/`
  - `samples/scanner_specs/four_graphs_integration_spec_TOPICS/`

- [ ] Count topic files per directory:
  - identity_model_spec: ~24 files
  - entry_point_scanner_spec: ~21 files
  - filter_layer_spec: ~24 files
  - cache_layer_spec: ~26 files
  - db_persistence_spec: ~33 files
  - four_graphs_integration_spec: ~29 files
  - **Total: ~157 files**

- [ ] Verify each topic file has YAML front matter format:
  ```yaml
  ---
  source: "spec_name.md"
  topic: "Topic Title"
  heading_level: N
  start_line: N
  end_line: N
  ---
  ```

---

## Step 3: Execute Import Pipeline

### Tasks

- [ ] Initialize database:
  ```bash
  python -m smart_task.cli init
  ```

- [ ] Run import command:
  ```bash
  python -m smart_task.cli import \
    --topic-dir samples/scanner_specs \
    --mappings .docs/Workflow_Orchestration/topic_to_ticket_mappings.json
  ```

- [ ] Verify import completion:
  - Check total ticket count (expected: 210-240)
  - Verify all topic files processed
  - Check for duplicate ID errors

---

## Step 4: Validate Import Results

### Tasks

- [ ] Check total ticket count:
  ```bash
  python -m smart_task.cli stats --json
  ```
  - Expected: `"total_tickets": ~210-240`

- [ ] Verify phase distribution:
  ```bash
  python -m smart_task.cli list --phase 1 --format json | wc -l
  python -m smart_task.cli list --phase 2 --format json | wc -l
  python -m smart_task.cli list --phase 3 --format json | wc -l
  ```

- [ ] Verify required fields populated:
  - `spec_context` must be non-empty
  - `objective` must be non-empty
  - `acceptance_criteria` must be non-empty array

- [ ] Check for duplicate IDs:
  ```bash
  python -m smart_task.cli list --format json | jq '.[].id' | sort | uniq -d
  ```

---

## Step 5: Create Waves for Orchestration

### Tasks

- [ ] Create Phase 0 waves (infrastructure):
  ```bash
  task-cli wave create --id wave-01_config --phase 0 --desc "config.py"
  task-cli wave create --id wave-02_schema_models --phase 0 --desc "schema.py + models.py"
  task-cli wave create --id wave-03_json_parser_repo --phase 0 --desc "json_schema.py + parser.py + repository.py"
  task-cli wave create --id wave-04_importer_exporter_wave --phase 0 --desc "importer.py + exporter.py + wave_manager.py"
  task-cli wave create --id wave-05_cli --phase 0 --desc "cli.py"
  task-cli wave create --id wave-06_import_topics --phase 0 --desc "Import 157 topic files"
  ```

- [ ] Create Phase 1 waves (scanner core):
  ```bash
  task-cli wave create --id wave-07_identity_model --phase 1 --desc "Identity Model"
  task-cli wave create --id wave-08_entry_scanner --phase 1 --desc "Entry Point Scanner"
  task-cli wave create --id wave-09_filter_layer --phase 1 --desc "Filter Layer"
  task-cli wave create --id wave-10_db_persistence --phase 1 --desc "DB Persistence"
  task-cli wave create --id wave-11_cache_layer --phase 1 --desc "Cache Layer"
  ```

- [ ] Create Phase 2 waves (4 graphs):
  ```bash
  task-cli wave create --id wave-12_structural_graph --phase 2 --desc "Structural Graph"
  task-cli wave create --id wave-13_concerns_graph --phase 2 --desc "Concerns Graph"
  task-cli wave create --id wave-14_dependency_graph --phase 2 --desc "Dependency Graph"
  task-cli wave create --id wave-15_tasks_graph --phase 2 --desc "Tasks Graph"
  ```

- [ ] Create Phase 3 wave (CLI migration):
  ```bash
  task-cli wave create --id wave-16_cli_migration --phase 3 --desc "CLI Migration + Legacy Cleanup"
  ```

---

## Step 6: Assign Tickets to Waves

### Tasks

- [ ] Assign Phase 0 tickets:
  ```bash
  task-cli wave assign --wave wave-01_config --strategy by_dependency
  task-cli wave assign --wave wave-02_schema_models --strategy by_dependency
  task-cli wave assign --wave wave-03_json_parser_repo --strategy by_dependency
  task-cli wave assign --wave wave-04_importer_exporter_wave --strategy by_dependency
  task-cli wave assign --wave wave-05_cli --strategy by_dependency
  task-cli wave assign --wave wave-06_import_topics --strategy by_dependency
  ```

- [ ] Assign Phase 1 tickets:
  ```bash
  task-cli wave assign --wave wave-07_identity_model --count 10 --strategy by_dependency
  task-cli wave assign --wave wave-08_entry_scanner --count 10 --strategy by_dependency
  task-cli wave assign --wave wave-09_filter_layer --count 10 --strategy by_dependency
  task-cli wave assign --wave wave-10_db_persistence --count 10 --strategy by_dependency
  task-cli wave assign --wave wave-11_cache_layer --count 10 --strategy by_dependency
  ```

- [ ] Assign Phase 2 tickets:
  ```bash
  task-cli wave assign --wave wave-12_structural_graph --strategy by_dependency
  task-cli wave assign --wave wave-13_concerns_graph --strategy by_dependency
  task-cli wave assign --wave wave-14_dependency_graph --strategy by_dependency
  task-cli wave assign --wave wave-15_tasks_graph --strategy by_dependency
  ```

- [ ] Assign Phase 3 ticket:
  ```bash
  task-cli wave assign --wave wave-16_cli_migration --strategy by_dependency
  ```

---

## Step 7: Export Wave Deliverables

### Tasks

- [ ] Export first wave for execution:
  ```bash
  task-cli export --wave wave-07_identity_model --format markdown --output ./waves/
  ```

- [ ] Verify export format:
  - Markdown contains all ticket fields
  - Acceptance criteria as checklists (`- [ ]`)
  - Verification commands in code blocks

---

## Verification Criteria

| # | Criterion | Verification Command |
|---|-----------|---------------------|
| 1 | Total tickets in expected range (~200-240) | `task-cli stats --json \| jq '.total_tickets'` |
| 2 | Every topic file has at least one ticket | Compare file count to tickets count |
| 3 | No duplicate ticket IDs | `jq '.[].id' \| sort \| uniq -d` |
| 4 | All tickets have required fields | SQL query or validation script |
| 5 | Phase filtering works | `task-cli list --phase 1 --format json` |
| 6 | Waves have balanced ticket counts | `task-cli wave list --format json` |
| 7 | First wave export is valid markdown | Check exported file |

---

## File Deliverables

1. **Mapping JSON:** `.docs/Workflow_Orchestration/topic_to_ticket_mappings.json`
2. **Database:** `.smart_task/tasks.db` (populated with tickets)
3. **Wave exports:** `./waves/wave-*_*.md` files

---

## File-Level Modular Architecture

| Aspect | Approach |
|--------|----------|
| Modularity | N/A — this wave processes existing Topic files; no new module code is created. Outputs: JSON mapping file + populated SQLite DB. |

## Test Strategy

### Philosophy
- **No gap masking** — if a capability is missing, fix the architecture, don't paper over it with trivial tests
- Every test MUST validate a real capability, not just "runs without error"
- All tests are runnable via `python -m pytest tests/ -v`

### Smoke Tests (end-to-end capability validation)
| # | Smoke Test | Validates |
|---|-----------|-----------|
| 1 | Count all `.md` files across all 6 `_TOPICS` directories — total is 157 | All topic files exist and are accessible |
| 2 | Parse each topic file's YAML front matter — all have `source`, `topic`, `heading_level`, `start_line`, `end_line` | Topic file format compliance |
| 3 | Load `topic_to_ticket_mappings.json` — valid JSON with all 6 spec module keys | Mapping JSON is well-formed and complete |
| 4 | Run `task-cli import --topic-dir samples/scanner_specs --mappings mappings.json` — exits 0 and reports ticket count | Full import pipeline executes without error |
| 5 | Run `task-cli stats --json` — output shows `total_tickets` in 200-240 range | Expected ticket volume generated |
| 6 | Run `task-cli wave create` for each of 16 waves — all 16 created without errors | All waves creatable |
| 7 | Run `task-cli wave assign` for Phase 0 waves — assignment succeeds and waves become active | Wave assignment works end-to-end |
| 8 | Run `task-cli export --wave wave-07_identity_model --format markdown` — produces valid markdown file | Export pipeline works end-to-end |

### Behavioral Tests (capability-revealing, BDD-style)
| # | Behaviour | Given | When | Then |
|---|-----------|-------|------|------|
| 1 | Every topic produces at least one ticket | All 157 topic files exist with YAML front matter | Import completes successfully | Number of tickets >= number of topic files (each topic >= 1 ticket) |
| 2 | Traceability fields populated | Import has completed | Query `source_spec`, `source_topic_file`, `source_line_range` on any ticket | All three fields are non-empty and match the source topic's YAML front matter |
| 3 | Default status is pending | Import has completed | Query `status` on any ticket | `status == 'pending'` |
| 4 | No duplicate IDs | Import has completed | Query all `id` values | All IDs are unique — no two tickets share the same ID |
| 5 | Phase filtering works | Tickets exist in phases 1, 2, 3 | Run `task-cli list --phase 1 --format json` | All returned tickets have `phase == 1` |
| 6 | Ticket ID pattern matches spec prefix | A mapping entry with prefix `IDM` | Import processes `identity_model_spec` topics | All generated tickets have IDs matching `^TASK-IDM-\d{3}$` |
| 7 | Wave assignment respects strategy | Pending tickets exist across phases | Assign tickets with `by_dependency` | Tickets with 0 dependencies assigned before tickets with dependencies |

### Gap -> Architecture Fix Rule
If a test reveals a missing capability (e.g. "no validation for traceability fields"):

1. **DO NOT** write a test that passes trivially (e.g. `assert True`)
2. **DO NOT** skip the test with `@pytest.mark.skip`
3. **INSTEAD**: Identify the architectural layer where the gap belongs
4. Implement the capability at the correct layer
5. Then the test passes naturally

### Test Files
| File | Scope |
|------|-------|
| `tests/test_data_import.py` | Data integrity validation — topic file count, mapping JSON structure, traceability field completeness, duplicate ID detection |
| `tests/test_end_to_end.py` | Full pipeline smoke tests — init -> import -> wave create/assign -> export -> stats verification |

---

## Dependencies Verification

- [ ] Wave 5 CLI is fully functional
- [ ] Topic files exist in expected locations
- [ ] All modules from Waves 1-4 import without errors
- [ ] Repository pattern works for batch operations