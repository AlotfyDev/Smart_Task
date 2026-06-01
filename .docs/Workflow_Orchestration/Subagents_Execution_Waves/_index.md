# Smart Task — Waves Orchestration Index

## Overview

This document defines the full execution plan for building the `smart_task` micro-task infrastructure and then implementing the File System Scanner Module (Phase 1-3). Each wave is self-contained, executed by a dedicated sub-agent, and follows structural dependency ordering.

## Wave Summary

```
PHASE 0: smart_task Infrastructure (Waves 1-6)
  Wave  1 ── config.py                          ● foundation
  Wave  2 ── schema.py + models.py               ○ depends on 1
  Wave  3 ── json_schema.py + parser.py + repo   ○ depends on 2
  Wave  4 ── importer + exporter + wave_manager  ○ depends on 3
  Wave  5 ── cli.py                              ○ depends on 4
  Wave  6 ── Import 157 topic files → tickets    ○ depends on 5

PHASE 1: Scanner Core (Waves 7-11)
  Wave  7 ── Identity Model + UUID + ancestry    ● foundation
  Wave  8 ── Entry Point Scanner (DFS scan)      ○ depends on 7
  Wave  9 ── Filter Layer (3 tiers)              ○ depends on 7
  Wave 10 ── DB Persistence (DDL + batch + JSON1) ○ depends on 7
  Wave 11 ── IdentityCache + Thread Safety       ○ depends on 7

PHASE 2: 4 Graphs Rewire (Waves 12-15)
  Wave 12 ── Structural Graph ← DB               ○ depends on 10, 11
  Wave 13 ── Concerns Graph ← Bridge Table       ○ depends on 10, 11
  Wave 14 ── Dependency Graph ← UUID resolution  ○ depends on 10, 11
  Wave 15 ── Tasks Graph ← stubs + buggy_comp    ○ depends on 10, 11

PHASE 3: CLI Migration & Cleanup (Wave 16)
  Wave 16 ── graph/cli.py migration + legacy rm  ○ depends on 12-15
```

## Dependency Graph

```
        Wave 1
          |
        Wave 2
          |
        Wave 3
          |
        Wave 4
          |
        Wave 5
          |
        Wave 6
          |
     +----+----+
     |    |    |
  Wave7  |    |
     |   |    |
  +--+---+    |
  |  |   |    |
  W8 W9 W10--+
  |       |    |
  +---+---+    |
      |        |
  Wave 12  Wave 13  Wave 14  Wave 15
      |        |        |        |
      +--------+--------+--------+
                   |
                Wave 16
```

## Key Principles

1. **Each wave is a single sub-agent task.** The sub-agent receives the wave file + all prior deliverables + relevant spec docs, and returns implemented code.
2. **No wave starts before its dependencies complete.** This ensures the sub-agent always has real code to build on (not stubs).
3. **Verification is part of the wave.** Every wave file includes `acceptance_criteria` + `verification_method` that the sub-agent MUST satisfy before marking done.
4. **Load balancing**: Waves 7, 8, 9, 10, 11 can theoretically run in parallel after Wave 7 completes. Waves 12-15 can also run in parallel after Waves 10-11.
5. **No monolithic sub-agents.** Each wave is scoped to 1-3 files max.

## Wave Files

| # | File | Phase | Depends On | Files |
|---|------|-------|------------|-------|
| 1 | `wave-01_config.md` | 0 | — | `config.py` |
| 2 | `wave-02_schema_models.md` | 0 | 1 | `schema.py`, `models.py` |
| 3 | `wave-03_json_parser_repo.md` | 0 | 2 | `json_schema.py`, `parser.py`, `repository.py` |
| 4 | `wave-04_importer_exporter_wave.md` | 0 | 3 | `importer.py`, `exporter.py`, `wave_manager.py` |
| 5 | `wave-05_cli.md` | 0 | 4 | `cli.py` |
| 6 | `wave-06_import_topics.md` | 0 | 5 | mapping rules + DB population |
| 7 | `wave-07_identity_model.md` | 1 | — | `samples/scanner/identity_model.py` |
| 8 | `wave-08_entry_scanner.md` | 1 | 7 | `samples/scanner/entry_point.py` |
| 9 | `wave-09_filter_layer.md` | 1 | 7 | `samples/scanner/filter_layer.py` |
| 10 | `wave-10_db_persistence.md` | 1 | 7 | `samples/scanner/db_persistence.py` |
| 11 | `wave-11_cache_layer.md` | 1 | 7 | `samples/scanner/identity_cache.py` |
| 12 | `wave-12_structural_graph.md` | 2 | 10, 11 | `samples/parsers/structural_parser.py` (rewrite) |
| 13 | `wave-13_concerns_graph.md` | 2 | 10, 11 | `samples/parsers/concerns_parser.py` (rewrite) |
| 14 | `wave-14_dependency_graph.md` | 2 | 10, 11 | `samples/parsers/dependency_parser.py` (rewrite) |
| 15 | `wave-15_tasks_graph.md` | 2 | 10, 11 | `samples/parsers/tasks_parser.py` (rewrite) |
| 16 | `wave-16_cli_migration_legacy.md` | 3 | 12-15 | `samples/cli.py` + `samples/__init__.py` + remove legacy |

## Total Waves: 16
## Total Sub-Agent Invocations: 16 (sequential by dependency)
