# Wave 1: config.py

## Dependency
- Depends on: *(none — foundation)*
- Required by: Wave 2 (schema.py + models.py)

## Target
`smart_task/config.py`

## Scope

Implement the full `config.py` module — the lowest-level dependency in `smart_task`. It contains runtime configuration constants and defaults used by all other modules.

## What to Implement

### `VERIFICATION_PREFIXES: dict[str, str]`

A mapping of verification method prefix → description:

```python
VERIFICATION_PREFIXES = {
    "SHELL":  "Execute shell command and verify exit code 0",
    "PATH":   "Path to test file/directory that must exist after implementation",
    "BDD":    "Behave feature file + line number to run",
    "SMOKE":  "Smoke test script path to execute",
    "MANUAL": "Human-verified — documented in review_notes",
    "MIXED":  "Combination of multiple prefixes (separated by newlines)",
}
```

### `DEFAULT_DB_PATH: Path`

Default SQLite database location. Must be configurable via environment variable `SMART_TASK_DB_PATH`:

```python
DEFAULT_DB_PATH = Path(os.getenv("SMART_TASK_DB_PATH", str(Path.home() / ".smart_task" / "tasks.db")))
```

### `class SmartTaskConfig`

A dataclass holding all configurable parameters:

| Field | Type | Default |
|-------|------|---------|
| `db_path` | `Path` | `DEFAULT_DB_PATH` |
| `verification_prefixes` | `dict[str, str]` | `VERIFICATION_PREFIXES` |
| `topics_dir_name` | `str` | `"topic_based_microtasks"` |
| `mappings_file_name` | `str` | `"topic_to_ticket_mappings.json"` |
| `priority_order` | `dict[str, int]` | `{"Critical": 4, "High": 3, "Medium": 2, "Low": 1}` |

### `load_config() -> SmartTaskConfig`

Factory function that creates a `SmartTaskConfig` by reading environment variables (with fallbacks to defaults).

## Verification

| # | Criterion |
|---|-----------|
| 1 | `config.py` is importable without errors: `python -c "from smart_task.config import SmartTaskConfig, load_config, DEFAULT_DB_PATH"` |
| 2 | `VERIFICATION_PREFIXES` contains all 6 keys |
| 3 | `load_config()` returns a valid `SmartTaskConfig` instance |
| 4 | Setting `SMART_TASK_DB_PATH` env var overrides `DEFAULT_DB_PATH` |

## Delivery
Single file: `smart_task/config.py` (complete, not stub)
