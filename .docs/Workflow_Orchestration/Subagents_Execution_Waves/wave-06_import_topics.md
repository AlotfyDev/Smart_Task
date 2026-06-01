# Wave 6: Import 157 Topic Files → Tickets

## Dependency
- Depends on: Wave 5 (cli.py)
- Required by: Waves 7-16 (all use tickets created here)

## Scope

This is a data-processing wave, not a code-writing wave. Use the `task-cli` tool (from Wave 5) to:
1. Create the mapping rules JSON
2. Import all 157 topic files into tickets
3. Validate the result
4. Assign tickets to waves

## Mapping Rules

Create a single JSON file at:
`.docs/Workflow_Orchestration/topic_to_ticket_mappings.json`

### Format

```json
{
  "identity_model_spec": {
    "prefix": "IDM",
    "topic_dir": "samples/scanner_specs/identity_model_spec_TOPICS",
    "phase": 1,
    "topics": {
      "02_schema_structural_elements_table.md": {
        "sequences": [
          {"seq": 1, "title": "Create structural_elements DDL table", "effort": "S", "tags": ["ddl", "sqlite"]},
          {"seq": 2, "title": "Define StructuralElement dataclass", "effort": "S", "tags": ["models", "dataclass"]}
        ]
      },
      "04_3_python_identity_object.md": {
        "sequences": [
          {"seq": 1, "title": "Implement to_dict() and from_dict() methods", "effort": "S", "tags": ["serialization"]}
        ]
      }
    }
  },
  "entry_point_scanner_spec": {
    "prefix": "SCN",
    "topic_dir": "samples/scanner_specs/entry_point_scanner_spec_TOPICS",
    "phase": 1,
    "topics": { "...": "..." }
  },
  "filter_layer_spec": { "...": "..." },
  "cache_layer_spec": { "...": "..." },
  "db_persistence_spec": { "...": "..." },
  "four_graphs_integration_spec": { "...": "..." }
}
```

### Mapping Rule Guidelines

Each topic file must map to at least 1 ticket. Complex topics (e.g., with tables, multiple code blocks, or multi-step processes) should map to 2-4 tickets. Some examples:

| Topic File | Tickets | Rationale |
|------------|---------|-----------|
| Schema DDL table definition | 1 | Single CREATE TABLE |
| Python identity object (dataclass) | 2 | 1 for class def, 1 for to_dict/from_dict |
| UUID Assignment During Scan | 2 | 1 for algorithm, 1 for edge cases |
| Three-Tier Filtering | 3 | 1 per tier (gitignore, third-party, user) |
| Batch Insert Strategy | 2 | 1 for single transaction, 1 for chunked |
| JSON1 Query Patterns | 4 | 1 per query type (ancestors, descendants, depth, etc.) |
| Structural Graph | 3 | DDL, queries, backward compat mapping |
| CLI Migration | 1 | Single command flow |

### Estimated Ticket Count

| Spec | Topic Files | Est. Tickets |
|------|-------------|--------------|
| identity_model_spec | 24 | 35-40 |
| entry_point_scanner_spec | 21 | 25-30 |
| filter_layer_spec | 24 | 35-40 |
| cache_layer_spec | 26 | 30-35 |
| db_persistence_spec | 33 | 45-50 |
| four_graphs_integration_spec | 29 | 40-45 |
| **Total** | **157** | **~210-240 tickets** |

## Execution

```bash
cd .

# 1. Initialize
python -m smart_task.cli init

# 2. Import all topic files
python -m smart_task.cli import \
  --topic-dir samples/docs/File_System_Scanner_Module \
  --mappings smart_task/.docs/Workflow_Orchestration/topic_to_ticket_mappings.json

# 3. Verify
python -m smart_task.cli stats
python -m smart_task.cli list --phase 1 | head -20
python -m smart_task.cli list --phase 2 | head -20
python -m smart_task.cli list --status pending

# 4. Create waves (from _index.md plan)
python -m smart_task.cli wave create --id wave-01_config --phase 0 --desc "config.py"
python -m smart_task.cli wave create --id wave-02_schema_models --phase 0 --desc "schema.py + models.py"
# ... one per wave file ...

# 5. Assign tickets to waves
python -m smart_task.cli wave assign --wave wave-01_config --strategy by_dependency
python -m smart_task.cli wave assign --wave wave-02_schema_models --strategy by_dependency
# ...

# 6. Export first wave
python -m smart_task.cli export --wave wave-01_config --format markdown
```

## Validation

| # | Criterion |
|---|-----------|
| 1 | `stats` shows total tickets matching expected range (~200-240) |
| 2 | Every topic file in every `_TOPICS` dir has at least one ticket |
| 3 | No duplicate ticket IDs |
| 4 | All tickets have non-empty `spec_context`, `objective`, `acceptance_criteria` |
| 5 | `list --phase 1` returns Phase 1 tickets only |
| 6 | Each wave has been assigned 5-15 tickets (balanced) |
| 7 | First wave export produces valid markdown with correct ticket details |

## Delivery
One mapping JSON file + populated SQLite database + exported wave markdown files for Waves 1-16.
