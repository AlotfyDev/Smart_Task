# Wave 5 Execution Plan: CLI Implementation

**Generated:** 2026-05-31  
**Status:** READY FOR IMPLEMENTATION  
**Dependency:** Wave 4 (importer + exporter + wave_manager) COMPLETE

---

## Configuration

### Path Configuration

CLI uses configurable paths via:

| Source | Description |
|--------|-------------|
| CLI `--db-path` | Database file path |
| CLI `--topic-dir` | Topic files directory |
| CLI `--mappings` | Mapping rules JSON |
| CLI `--entry-point` | Scanner entry point directory |
| CLI `--output` | Export output directory |
| Environment variables | Optional default paths |

---

## Critical Gaps Analysis

### Required Implementation

| Component | Spec Requirement | Status |
|-----------|------------------|--------|
| CLI argparse structure | 8 commands with subcommands | ❌ MISSING |
| Command handlers | Delegation to Wave 1-4 modules | ❌ MISSING |
| Output formatting | Text table + JSON formatters | ❌ MISSING |
| Entry point registration | `task-cli` in pyproject.toml | ❌ MISSING |

---

## Step 1: Implement argparse Command Structure

### Tasks

- [ ] Create `build_parser() -> argparse.ArgumentParser`
- [ ] Add commands: `init`, `import`, `list`, `get`, `wave`, `export`, `status`, `stats`
- [ ] Add wave subcommands: `create`, `assign`, `show`, `list`

---

## Step 2: Implement Command Handlers

- [ ] `init`: create database via `ensure_schema()`
- [ ] `import`: delegate to `TopicToTicketImporter.import_all()`
- [ ] `list`: delegate to `TicketRepository.list_tickets()`
- [ ] `get`: call `TicketRepository.get_ticket()`
- [ ] `wave create/assign/show/list`: delegate to `WaveManager`
- [ ] `export`: delegate to `WaveExporter.export_to_files()`
- [ ] `status`: call `TicketRepository.update_ticket_status()`
- [ ] `stats`: delegate to `WaveManager.get_project_summary()`

---

## Step 3: Implement Output Formatting

- [ ] Text table formatter for `list`
- [ ] JSON output formatter for `stats`
- [ ] Error message format: `Error: {message}`
- [ ] Exit codes: 0=success, 1=user error, 2=system error

---

## Step 4: Implement main() Function

- [ ] Parse arguments via `build_parser()`
- [ ] Dispatch to appropriate handler
- [ ] Handle exceptions gracefully
- [ ] Call `sys.exit(code)`

---

## Step 5: Update pyproject.toml

- [ ] Add `[project.scripts]` entry: `task-cli = "smart_task.cli:main"`

---

## Step 6: Verification

| # | Criterion | Test |
|---|-----------|------|
| 1 | `--help` shows all commands | `python -m smart_task.cli --help` |
| 2 | `init` creates DB | `task-cli init --db-path test.db` |
| 3 | `list` returns empty on fresh DB | `task-cli list --format json` |
| 4 | `stats` returns valid JSON | `task-cli stats --json` |
| 5 | All `--help` work | Each subcommand help |
| 6 | Error handling works | Nonexistent ticket error |

---

## File-Level Modular Architecture

| Module | File Decomposition | Rationale |
|--------|-------------------|-----------|
| `cli/` | `__init__.py` (single entry — thin orchestration layer) | CLI is a thin orchestration layer wrapping wave_manager; single file is correct unless it exceeds ~400 lines, at which point handlers should be extracted to `cli/handlers.py` |

---

## Test Strategy

### Philosophy
- **No gap masking** — if a capability is missing, fix the architecture, don't paper over it with trivial tests
- Every test MUST validate a real capability, not just "runs without error"
- All tests are runnable via `python -m pytest tests/ -v`

### Smoke Tests (end-to-end capability validation)
| # | Smoke Test | Validates |
|---|-----------|-----------|
| 1 | `python -m smart_task.cli --help` exits 0, output contains `init`, `import`, `list`, `get`, `wave`, `export`, `status`, `stats` | All 8 commands registered in argparse |
| 2 | `task-cli init --db-path test.db` creates valid SQLite DB with schema | Database initialization |
| 3 | `task-cli list --format json` on fresh DB outputs `[]` | Query returns empty list when no tickets |
| 4 | `task-cli get TASK-NONEXISTENT` exits 1 with "Error: ticket TASK-NONEXISTENT not found" | Error handling for missing ticket |
| 5 | `task-cli wave create --id test-wave --phase 1 --desc "Test wave"` exits 0 | Wave creation via CLI |
| 6 | `task-cli wave show --wave test-wave` output contains wave metadata | Wave retrieval via CLI |
| 7 | `task-cli wave list` output contains `test-wave` | Wave listing via CLI |
| 8 | `task-cli stats --json` outputs valid JSON with key `total_tickets` | Statistics via CLI |
| 9 | `task-cli export --wave test-wave --format markdown --output ./test-out` creates file in output dir | Wave export via CLI |
| 10 | `task-cli status TASK-NONEXISTENT --set completed` exits 1 with "Error:" message | Status update error handling |

### Behavioral Tests (capability-revealing, BDD-style)
| # | Behaviour | Given | When | Then |
|---|-----------|-------|------|------|
| 1 | Exit code 0 on success | Valid arguments for any command | Command executes successfully | `sys.exit(0)` is called |
| 2 | Exit code 1 on user error | Invalid arguments (e.g. missing required flag) | Command handler raises error | `sys.exit(1)` is called and message starts with `Error:` |
| 3 | Exit code 2 on system error | DB file is corrupt or unreadable | Any command tries to access DB | `sys.exit(2)` is called and message starts with `Error:` |
| 4 | JSON output format | `--format json` flag passed | `list` or `get` command runs | Output is valid JSON parseable by `json.loads()` |
| 5 | Text output format | No `--format` flag (default) | `list` command runs | Output is human-readable table with aligned columns |
| 6 | Error message format | Any error condition occurs | Error is printed | Message starts with exactly `Error: ` prefix |
| 7 | Wave assign with strategy flag | Tickets exist in DB, wave exists | `task-cli wave assign --wave test-wave --strategy by_priority` | Tickets assigned with correct ordering, exit code 0 |
| 8 | Wave assign with count limit | 20 pending tickets exist | `task-cli wave assign --wave test-wave --count 5` | Exactly 5 tickets are assigned to the wave |
| 9 | Each subcommand `--help` works | Subcommand name (e.g. `wave create`) | Run `task-cli wave create --help` | Shows usage, arguments, and description, exits 0 |

### Gap -> Architecture Fix Rule
If a test reveals a missing capability (e.g. "no validation for error message format"):

1. **DO NOT** write a test that passes trivially (e.g. `assert True`)
2. **DO NOT** skip the test with `@pytest.mark.skip`
3. **INSTEAD**: Identify the architectural layer where the gap belongs
4. Implement the capability at the correct layer
5. Then the test passes naturally

### Test Files
| File | Scope |
|------|-------|
| `tests/test_cli.py` | `build_parser()` argument parsing, command dispatch, exit codes, output formatting, error messages |
| `tests/test_cli_commands.py` | End-to-end CLI smoke tests — run CLI subprocesses and verify stdout/stderr/exit codes |