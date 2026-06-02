# Audit Report — تقرير التدقيق (Verification Results)

## الغرض

نتائج التحقق من تنفيذ المهام بواسطة الوكيل الفرعي — توثق ما إذا كان التنفيذ ناجحًا، ما هي النتائج، ومن قام بالتدقيق.  
تمثل حلقة الإغلاق في سلسلة التطوير الموجّه بالمواصفات.

## المخطط (DDL)

```sql
CREATE TABLE audit_reports (
    id             TEXT    PRIMARY KEY,                -- AR-001
    ep_id          INTEGER NOT NULL REFERENCES execution_plans(id),
    task_id        INTEGER NOT NULL REFERENCES micro_task_tickets(id),
    status         TEXT    NOT NULL DEFAULT 'pending', -- pending / in_review / passed / failed
    findings       TEXT,                               -- النتائج والملاحظات (JSON array)
    passed         INTEGER NOT NULL DEFAULT 0,         -- 0 = failed, 1 = passed
    score          REAL,                               -- درجة التقييم (0.0 - 1.0)
    audited_by     TEXT    NOT NULL,                   -- من قام بالتدقيق (وكيل أو مستخدم)
    evidence       TEXT,                               -- أدلة التنفيذ (روابط، مخرجات)
    comments       TEXT,                               -- تعليقات إضافية
    started_at     TEXT,
    completed_at   TEXT,
    created_at     TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at     TEXT    NOT NULL DEFAULT (datetime('now'))
);
```

## علاقة الوالد

- **الوالد**: execution_plans(id) عبر `ep_id`، و micro_task_tickets(id) عبر `task_id`.
- **الأبناء**: لا يوجد.

## مثال

```sql
INSERT INTO audit_reports (id, ep_id, task_id, status, findings, passed, score, audited_by)
VALUES (
    'AR-001',
    'EP-001',
    'TASK-OPENAI-001',
    'passed',
    '[
        {"check": "وحدة تنفيذ أمر الشراء أنشئت بنجاح", "result": "pass"},
        {"check": "اختبارات الوحدة جميعها تجتاز", "result": "pass"},
        {"check": "توثيق API مكتمل", "result": "pass"}
    ]',
    1,
    1.0,
    'audit-agent-v1'
);
```

## الاستخدام في سير العمل الوكيل

1. **وكيل التدقيق** (Audit Agent) يستلم EP-ID ويبدأ في التحقق من كل مهمة.
2. لكل مهمة، يتم إنشاء Audit Report يوثق نتائج التحقق.
3. إذا فشلت مهمة (`passed = 0`)، يتم إنشاء **مهمة جديدة** أو إعادة توجيه الوكيل الفرعي للمراجعة.
4. تُستخدم تقارير التدقيق لتحديث حالة الموجة (Wave) — إذا اجتازت جميع المهام، تكتمل الموجة.
5. يمكن ربط Audit Reports بـ ADRs عبر doc_edges إذا كشفت نتائج التدقيق عن حاجة لقرار معماري جديد.
