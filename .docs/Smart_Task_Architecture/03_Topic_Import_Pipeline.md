# Topic Import Pipeline

## Overview

The import pipeline transforms structured specification documents into actionable micro-task tickets. It bridges the gap between "what needs to be built" (specs) and "what a sub-agent executes" (tickets).

## Pipeline Flow

```
Topic .md files          Mapping Rules           Tickets
─────────────────    ──────────────────    ─────────────────
identity_model_spec     mapping.json         TASK-IDM-001
  ├─ 01_Overview.md      ┌──────────┐         TASK-IDM-002
  ├─ 02_Schema...md ────→│  seq: 1  │────→    TASK-IDM-003
  ├─ 03_Field...md       │  seq: 2  │         ...
  │                      │  seq: 3  │         TASK-SCN-001
entry_scanner_spec       └──────────┘         TASK-SCN-002
  ├─ 01_What_Is...md          │                ...
  ├─ 02_Scanning...md         │                TASK-FLT-001
  └─ ...                     │                ...
```

## Input: Topic Files

Topic files are extracted from spec documents by the `_TOPICS` extraction process. Each file contains:
- **YAML front matter** with metadata: `source`, `topic`, `heading_level`, `start_line`, `end_line`
- **Body content**: the verbatim spec text for that topic

**Example header:**
```yaml
---
source: "identity_model_spec.md"
topic: "2. Schema structural_elements Table"
heading_level: 2
start_line: 11
end_line: 28
---
```

## Input: Mapping Rules

A JSON file that defines how each topic file maps to tickets:

```json
{
  "identity_model_spec": {
    "prefix": "IDM",
    "topic_dir": "path/to/identity_model_spec_TOPICS",
    "topics": {
      "02_schema_structural_elements_table.md": {
        "sequences": [
          {"seq": 1, "title": "Create DDL", "effort": "S", "tags": ["ddl"]},
          {"seq": 2, "title": "Define dataclass", "effort": "S", "tags": ["models"]}
        ]
      }
    }
  }
}
```

**Design principle:** Not 1:1. A single topic can generate multiple tickets (complex topics like "Three-Tier Filtering" might generate 3 tickets). Some topics generate 0 tickets (informational sections like "Overview").

## Processing: Importer

The `TopicToTicketImporter.import_topic_file()` method:

1. Read topic `.md` file
2. Parse YAML front matter → extract `source_spec`, `start_line`, `end_line`
3. Extract body text after front matter → `spec_context`
4. Look up mapping entry for this topic file name
5. For each `sequence` in the mapping:
   - Generate ticket ID: `TASK-{prefix}-{seq:03d}`
   - Fill title, objective from templates
   - Set `spec_context` from topic body
   - Set `source_spec`, `source_topic_file`, `source_line_range` from YAML
   - Set `phase`, `effort`, `tags` from mapping entry
6. Insert all generated tickets into DB via batch insert

## Output: Tickets in Database

After import, the `micro_task_tickets` table contains all tickets with:
- All traceability fields populated
- `status = 'pending'`
- No wave assignment yet
- No `assignee` yet

## Post-Import: Wave Assignment

After import, the `WaveManager` assigns tickets to waves based on:
1. Phase (tickets from the same phase go to the same wave groups)
2. Dependencies (tickets with fewer dependencies are assigned first)
3. Priority (higher priority tickets are assigned first within same-dependency group)

This is a separate step from import, allowing the orchestrator to:
- Review all tickets before creating waves
- Adjust priorities or dependencies
- Balance wave sizes manually
