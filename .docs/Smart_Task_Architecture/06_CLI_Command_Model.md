# CLI Command Model

## Overview

The CLI follows a command/query separation pattern. Commands mutate state (import, assign, status update). Queries return state (list, get, stats). This separation simplifies testing and reasoning.

## Command Hierarchy

```
task-cli
├── init                          [command] Create DB + schema
├── import                        [command] Topic files → tickets
│   ├── --topic-dir PATH          Topic files directory
│   ├── --mappings PATH           Mapping rules JSON
│   └── --db-path PATH            Override DB location
├── list                          [query]  Filter tickets
│   ├── --phase 1|2|3             Filter by phase
│   ├── --status STATUS           Filter by status
│   ├── --wave WAVE_ID            Filter by wave
│   └── --format json|text        Output format
├── get                           [query]  Single ticket detail
│   ├── ticket_id                 Required: ticket ID
│   └── --format json|text
├── wave                          [group]  Wave management
│   ├── create                    [command]
│   │   ├── --id NAME             Required: wave ID
│   │   ├── --phase N             Required: phase
│   │   └── --desc TEXT           Required: description
│   ├── assign                    [command]
│   │   ├── --wave NAME           Required: target wave
│   │   ├── --count N             Max tickets (default: all)
│   │   └── --strategy STRATEGY   by_dependency|by_priority|balanced
│   ├── show                      [query]
│   │   ├── --wave NAME           Required
│   │   └── --format json|text
│   └── list                      [query]
│       └── --phase N             Optional filter
├── export                        [command] Wave → deliverable
│   ├── --wave NAME               Required: wave to export
│   ├── --format markdown|json    Output format
│   └── --output DIR              Output directory
├── status                        [command] Update ticket
│   ├── ticket_id                 Required
│   ├── --set STATUS              Required: new status
│   ├── --notes TEXT              Review notes
│   └── --blocker TEXT            Blocker reason → auto-sets blocked
└── stats                         [query]  Project statistics
    ├── --phase N                 Optional filter
    └── --json                    JSON output (vs formatted text)
```

## Implementation Architecture

```
cli.py (argparse + subparsers)
  │
  ├── TicketRepository       ← data access
  ├── WaveManager            ← wave logic
  ├── TopicToTicketImporter  ← import logic
  └── WaveExporter           ← export logic
```

The CLI is **thin** — no business logic, only:
1. Parse arguments
2. Validate arguments
3. Call the appropriate module function
4. Print the result

## Output Patterns

### Text Format (default)

Human-readable. Uses:
- Tables for lists (┌───┬───┐ style or aligned columns)
- Sections for detail views
- Color output optional (ANSI escape codes, no external deps)

### JSON Format (`--format json`)

Machine-readable. Returns JSON objects/arrays suitable for piping to other tools.

## Error Handling

All errors follow a consistent pattern:
```
Error: {message}
```

Examples:
```
Error: Ticket TASK-XXX-999 not found
Error: Wave wave-99 does not exist
Error: --wave is required for 'wave assign'
```

Exit codes:
- 0: success
- 1: user error (bad args, not found)
- 2: system error (DB corrupt, IO error)

## Extensibility

Adding a new command requires:
1. Add a new subparser in `build_parser()`
2. Add a handler function
3. Wire it into `main()`

No changes needed to the module layer unless the command requires new business logic.
