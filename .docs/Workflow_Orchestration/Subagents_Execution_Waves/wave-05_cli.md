# Wave 5: cli.py

## Dependency
- Depends on: Wave 4 (importer + exporter + wave_manager)
- Required by: Wave 6 (topic import)

## Target
`smart_task/cli/` (package with `__init__.py` — thin entry point, handlers extracted if >400 lines)

## Scope

Implement the user-facing CLI using Python's built-in `argparse`. All business logic is delegated to the modules from Waves 1-4. The CLI is thin — only argument parsing and result display.

## Commands

### `init`
Create the database and schema, create default directories.

```
task-cli init [--db-path PATH]
```

### `import`
Import topic files into tickets using mapping rules.

```
task-cli import --topic-dir PATH [--mappings PATH] [--db-path PATH]
```

- Default `--topic-dir`: looks for `*_TOPICS` directories relative to config
- Default `--mappings`: `topic_to_ticket_mappings.json` relative to config
- Output: "Imported {N} tickets from {M} topic files"

### `list`
List tickets with optional filters.

```
task-cli list [--phase 1|2|3] [--status pending|in_progress|completed|blocked] [--wave WAVE_ID] [--format json|text]
```

- Text format: table with ID, title, phase, priority, status
- JSON format: full ticket objects

### `get`
Show full details of a single ticket.

```
task-cli get TICKET_ID [--format json|text]
```

### `wave`

Subcommands for wave management:

```
task-cli wave create --id NAME --phase N --desc "Description"
task-cli wave assign --wave NAME [--count N] [--strategy auto|by_priority|by_dependency]
task-cli wave show --wave NAME [--format json|text]
task-cli wave list [--phase N]
```

### `export`
Export a wave as a deliverable file for a sub-agent.

```
task-cli export --wave NAME [--format markdown|json] [--output DIR]
```

- `--output`: directory to write files to (default: `./waves/{wave_id}/`)

### `status`
Update ticket status.

```
task-cli status TICKET_ID --set STATUS [--notes "text"] [--blocker "reason"]
```

- STATUS must be one of: `pending`, `in_progress`, `completed`, `blocked`, `cancelled`
- `--notes`: fills `review_notes`
- `--blocker`: fills `blocker_reason` and sets status to `blocked`

### `stats`
Show project statistics.

```
task-cli stats [--phase N] [--json]
```

## Example Flow

```bash
# 1. Initialize
task-cli init

# 2. Import topic files
task-cli import --topic-dir samples/docs/File_System_Scanner_Module --mappings mappings.json

# 3. Create waves
task-cli wave create --id wave-1 --phase 1 --desc "Identity Model"
task-cli wave create --id wave-2 --phase 1 --desc "Entry Point Scanner"

# 4. Assign tickets to waves
task-cli wave assign --wave wave-1 --count 10 --strategy by_dependency

# 5. Export wave for sub-agent
task-cli export --wave wave-1 --format markdown --output ./waves/

# 6. Check progress
task-cli stats
```

## Implementation Notes

- Use `argparse` with subparsers for command hierarchy
- Add `main()` as the entry point (registered in `pyproject.toml` as `task-cli`)
- Color output optional (use ANSI escape codes, not external deps)
- Error messages must be clear: "Error: ticket TASK-XXX not found"
- `--help` on each subcommand must be descriptive

## Verification

| # | Criterion |
|---|-----------|
| 1 | `python -m smart_task.cli --help` shows all commands |
| 2 | `task-cli init` creates DB file at default or specified path |
| 3 | `task-cli list` returns empty list on fresh DB |
| 4 | `python -m smart_task.cli stats` returns valid JSON with `total_tickets: 0` |
| 5 | Using `--help` on every subcommand shows usage without errors |
| 6 | `task-cli status NONEXISTENT --set completed` returns meaningful error |

## Delivery
Single package: `smart_task/cli/` (update `pyproject.toml` `[project.scripts]` if needed)
