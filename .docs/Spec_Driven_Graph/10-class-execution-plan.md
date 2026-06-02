# Execution Plan — استراتيجية المنسق (Orchestrator Strategy)

## الغرض

استراتيجية تنفيذ المنسّق (Orchestrator) — تحدد ترتيب المهام، المجموعات التي يمكن تنفيذها بالتوازي، وسياق الوكيل الفرعي.  
تمثل "متى" و "بأي ترتيب" يتم تنفيذ المهام.

## المخطط (DDL)

```sql
CREATE TABLE execution_plans (
    id               TEXT    PRIMARY KEY,                -- EP-001
    plan_id          INTEGER NOT NULL REFERENCES plans(id),
    wave_id          INTEGER NOT NULL REFERENCES task_waves(id),
    task_order       TEXT    NOT NULL,                   -- ترتيب المهام (JSON array)
    parallel_groups  TEXT,                               -- المجموعات المتوازية (JSON array)
    sub_agent_context TEXT,                              -- سياق الوكيل الفرعي (JSON)
    dependencies     TEXT,                               -- تبعيات إضافية (JSON array)
    status           TEXT    NOT NULL DEFAULT 'draft',   -- draft / active / completed / failed
    started_at       TEXT,
    completed_at     TEXT,
    version          INTEGER NOT NULL DEFAULT 1,
    created_at       TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at       TEXT    NOT NULL DEFAULT (datetime('now'))
);
```

## علاقة الوالد

- **الوالد**: plans(id) عبر `plan_id`، و task_waves(id) عبر `wave_id`.
- **الأبناء المباشرون**: audit_reports (عبر FK: `audit_reports.ep_id`)

## مثال

```sql
INSERT INTO execution_plans (id, plan_id, wave_id, task_order, parallel_groups, sub_agent_context)
VALUES (
    'EP-001',
    'PLAN-001',
    'WAVE-001',
    '["TASK-OPENAI-001", "TASK-OPENAI-002", "TASK-OPENAI-003"]',
    '[
        {"group": 1, "tasks": ["TASK-OPENAI-001", "TASK-OPENAI-002"], "run_parallel": true},
        {"group": 2, "tasks": ["TASK-OPENAI-003"], "run_parallel": false}
    ]',
    '{
        "agent_type": "openai",
        "model": "gpt-4",
        "instructions_file": "instructions/execution-v1.md",
        "max_retries": 3
    }'
);
```

## الاستخدام في سير العمل الوكيل

1. **المنسّق** (Orchestrator) يستلم PLAN-ID و WAVE-ID وينشئ Execution Plan.
2. تحدد parallel_groups المهام التي يمكن تشغيلها بالتوازي عبر وكلاء فرعيين.
3. يُمرّر sub_agent_context لكل وكيل فرعي لتزويده بالسياق اللازم.
4. بعد اكتمال التنفيذ، يتم إنشاء **Audit Report** لكل مهمة.
