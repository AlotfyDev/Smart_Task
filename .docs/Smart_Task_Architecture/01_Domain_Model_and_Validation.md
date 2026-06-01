# Domain Model & Validation

## Overview

Smart Task defines three domain entities that represent the micro-task lifecycle from specification to execution. Each entity is a Python dataclass with a corresponding SQLite table and JSON Schema artifact.

## Entities

### MicroTaskTicket

The central entity. A ticket represents one atomic, implementable unit of work derived from a specification topic.

**Identity:** `TASK-{SPEC_PREFIX}-{NNN}` where:
- `SPEC_PREFIX` = 2-4 uppercase letters identifying the source spec (e.g., `IDM` for identity_model_spec, `SCN` for entry_point_scanner_spec)
- `NNN` = zero-padded 3-digit sequence number

**Traceability chain:**
```
Spec Document → Topic File → Ticket
     │               │            │
  source_spec    topic_file    id
     │               │            │
  line_range ────────┘            │
     │                            │
  spec_context ───────────────────┘
```

Each ticket carries the verbatim `spec_context` from its source topic, making it self-contained — a sub-agent needs no additional files to understand what to implement.

**State machine:**
```
pending → in_progress → completed
    ↓           ↓
 blocked     cancelled
```

Transitions:
- `pending → in_progress`: assigned to a wave, work started
- `in_progress → completed`: all acceptance criteria met, verification passed
- `in_progress → blocked`: external dependency or blocker_reason set
- `any → cancelled`: ticket no longer relevant

**Critical fields:**
| Field | Purpose | Validation |
|-------|---------|------------|
| `dependencies` | JSON array of ticket IDs that must be completed first | Each ID must match `^TASK-[A-Z]{2,4}-\d{3}$` |
| `acceptance_criteria` | JSON array of measurable criteria | Non-empty for `completed` status |
| `verification_method` | Prefix-encoded verification instructions | Must match `^(SHELL\|PATH\|BDD\|SMOKE\|MANUAL\|MIXED):` |

### TaskWave

A logical grouping of tickets assigned to a single sub-agent invocation.

**Wave lifecycle:**
```
pending → active → completed
```

A wave is `active` while the sub-agent is working. It becomes `completed` when all its tickets are `completed` or `cancelled`.

**Assignment strategies:**
- `by_dependency`: tickets with fewest unresolved dependencies first
- `by_priority`: highest priority first (High → Medium → Low)
- `balanced`: round-robin across priority levels

### TopicToTicketMapping

Defines how a single topic file is decomposed into one or more tickets. This is the bridge between the spec analysis phase and the execution phase.

**Example:** A topic file covering "Three-Tier Filtering" might generate 3 tickets:
1. Implement gitignore tier (S effort)
2. Implement third-party tier (S effort)
3. Implement user exclusion tier (S effort)

## Validation Philosophy

Validation follows a **defensive** approach, not a permissive one:
- SQL CHECK constraints at the database level (last line of defense)
- Python `validate()` methods at the application level (primary gate)
- JSON Schema validation at the artifact boundary (interchange format)

All three layers must agree. If a constraint exists in one but not another, it's a bug — as discovered in Wave 1.5 (missing `task_waves.phase CHECK`).

## Round-Trip Guarantee

Every entity supports:
```
dataclass → to_dict() → JSON string → from_dict() → dataclass
```

This is used for:
- Artifact export/import (JSON files)
- DB persistence (serialized rows)
- Sub-agent handoff (markdown + JSON)
