# Wave Assignment System

## Overview

A **wave** is a self-contained batch of tickets delivered to a single sub-agent. The wave system ensures:
1. **Load balancing**: No sub-agent gets too many or too few tickets
2. **Dependency ordering**: Tickets are assigned only after their dependencies are resolved
3. **Traceability**: Every ticket knows which wave it belongs to

## Wave Lifecycle

```
┌──────────┐    assign tickets    ┌────────┐    sub-agent    ┌───────────┐
│ PENDING  │ ──────────────────→  │ ACTIVE │ ─────────────→  │ COMPLETED │
│ (empty)  │                      │ (has   │                 │ (all done)│
│          │                      │  tickets)               │           │
└──────────┘                      └────────┘                └───────────┘
```

**States:**
- `pending`: Empty wave, ready for ticket assignment
- `active`: Has assigned tickets, sub-agent is working
- `completed`: All tickets completed or cancelled

## Wave Creation

```bash
task-cli wave create --id wave-07_identity_model --phase 1 --desc "Identity Model"
```

Each wave corresponds to one step in the 16-wave orchestration plan. The `id` convention matches the wave filename for traceability.

## Ticket Assignment

### Algorithm

```
1. Collect all pending (unassigned) tickets for wave.phase
2. Sort by assignment strategy:
   a. by_dependency: parse dependencies JSON, count unresolved, sort ascending
   b. by_priority: sort by priority order (High > Medium > Low)
   c. balanced: interleave across priority levels
3. Take first N tickets (or all if count is None)
4. UPDATE wave_id on selected tickets
5. UPDATE ticket_count on the wave row
6. SET wave status = 'active'
```

### Dependency Resolution

The `get_ready_tickets()` method:
1. Finds all tickets matching the requested phase
2. Excludes tickets already assigned to another wave
3. For each ticket, parses `dependencies` JSON array
4. Checks if every dependency ID has `status = 'completed'`
5. Returns only tickets where all dependencies are met
6. Sorts by the selected strategy

**Example:** Ticket `TASK-IDM-003` (Field Semantics) depends on `TASK-IDM-001` (DDL Schema) and `TASK-IDM-002` (Dataclass). It won't be assigned to a wave until both are completed.

## Wave Balancing

### Manual (Recommended for v1)

The orchestrator manually creates waves and specifies `--count`:
```bash
task-cli wave assign --wave wave-01 --count 5 --strategy by_dependency
```

This guarantees each wave has exactly the right number of tickets for a single sub-agent invocation.

### Automatic

If `--count` is omitted, ALL matching pending tickets are assigned to the wave. Use with caution — a single wave could get 50+ tickets (too many for one sub-agent).

## Wave Export

After assignment, the wave is exported for the sub-agent:

```bash
task-cli export --wave wave-07_identity_model --format markdown --output ./waves/
```

The export produces a single markdown file with:
- Wave metadata (id, phase, status, ticket count)
- Each ticket as a section with all fields including `spec_context`
- Checklists from `acceptance_criteria`
- Shell commands from `verification_method`

The sub-agent receives this file and executes each ticket in sequence.
