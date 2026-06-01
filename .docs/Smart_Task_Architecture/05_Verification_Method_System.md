# Verification Method System

## Overview

Every micro-task ticket must be verifiable. The `verification_method` field uses a prefix-based encoding system that tells both the human sub-agent and automated tools exactly how to verify the ticket's acceptance criteria.

## Prefix System

```
{SHELL|PATH|BDD|SMOKE|MANUAL|MIXED}: <content>
```

### SHELL

An executable shell command. The sub-agent must run this and verify exit code 0.

```
SHELL: python -m pytest tests/unit/test_structural_element.py -v
SHELL: python -c "from smart_task.schema import ensure_schema; import sqlite3; conn = sqlite3.connect(':memory:'); ensure_schema(conn); print('OK')"
```

### PATH

A path that must exist after implementation. Used for file/directory creation verification.

```
PATH: graph/scanner/identity_model.py
PATH: tests/unit/test_identity_model.py
```

### BDD

A Behave feature file reference. Format: `{file}:{line}`.

```
BDD: features/structural_element/ddl_creation.feature:5
```

### SMOKE

A smoke test script that performs a quick end-to-end verification.

```
SMOKE: smoke/verify_import_pipeline.sh
```

### MANUAL

A human-verified instruction. The review cycle checks this.

```
MANUAL: Run task-cli import and verify no errors in output
```

### MIXED

Multiple verification methods combined, separated by newlines.

```
MIXED:
  SHELL: python -m pytest tests/test_identity_model.py -v
  SMOKE: smoke/verify_roundtrip.sh
  PATH: graph/scanner/identity_model.py
```

## Acceptance Criteria

The `acceptance_criteria` field stores a JSON array of measurable criteria:

```json
[
  "SQL script executes without error against SQLite",
  "All CHECK constraints accept valid values and reject invalid ones",
  "All 6 indexes created"
]
```

Each criterion should be:
- **Specific** — not "works correctly" but "returns UUID when called"
- **Measurable** — can be checked programmatically or manually
- **Independent** — one criterion per assertion

## Verification Flow

```
1. Sub-agent implements ticket
2. Sub-agent runs each verification_method
3. Sub-agent checks each acceptance_criterion
4. If ALL pass → ticket status = 'completed'
5. If any fail → fix implementation, retry
```

## Configuration

The `VERIFICATION_PREFIXES` dictionary in `config.py` is the single source of truth:

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

## Extending the System

To add a new verification method:
1. Add a new entry to `VERIFICATION_PREFIXES` in `config.py`
2. Document the prefix format in this document
3. Update any CLI formatting that displays verification methods

No code changes needed in the parser or exporter — they treat the field as opaque text.
