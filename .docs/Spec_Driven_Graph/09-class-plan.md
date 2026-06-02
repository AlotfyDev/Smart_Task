# Plan — خطة التصميم التقني (Technical Design Plan)

## الغرض

خطة تنفيذ تقنية مشتقة من المواصفات — تحدد كومة التقنيات (tech stack)، المنهجية، والخطوات التفصيلية للتنفيذ.  
تربط "ماذا" (المواصفات) بـ "كيف" (التنفيذ الفعلي).

## المخطط (DDL)

```sql
CREATE TABLE plans (
    id                  TEXT    PRIMARY KEY,                -- PLAN-001
    spec_id             TEXT    NOT NULL,                   -- SPEC-NNN أو TOPIC-NNN (نصي — مرن)
    title               TEXT    NOT NULL,
    tech_stack          TEXT    NOT NULL,                   -- كومة التقنيات (JSON array)
    approach            TEXT    NOT NULL,                   -- المنهجية المتبعة
    implementation_steps TEXT   NOT NULL,                   -- خطوات التنفيذ (JSON array)
    risks               TEXT,                               -- المخاطر (JSON array)
    estimated_effort    TEXT,                               -- الجهد التقديري
    status              TEXT    NOT NULL DEFAULT 'draft',   -- draft / reviewed / approved
    version             INTEGER NOT NULL DEFAULT 1,
    tags                TEXT,
    created_at          TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at          TEXT    NOT NULL DEFAULT (datetime('now'))
);
```

## علاقة الوالد

- **الوالد**: يمكن أن يشير إلى specs(id) أو spec_topics(id) عبر حقل `spec_id` النصي.
- **الأبناء المباشرون**: execution_plans (عبر FK: `execution_plans.plan_id`)
- **ملاحظة**: `spec_id` من نوع TEXT لاستيعاب كلا النوعين SPEC و TOPIC.

## مثال

```sql
INSERT INTO plans (id, spec_id, title, tech_stack, approach, implementation_steps, risks)
VALUES (
    'PLAN-001',
    'SPEC-001',
    'خطة تنفيذ نظام التداول',
    '["Python 3.12", "FastAPI", "SQLite", "Redis", "Celery"]',
    'التطوير باستخدام منهجية TDD مع اختبارات تغطي كل Topic',
    '[
        {"step": 1, "action": "إنشاء نماذج البيانات", "estimated_hours": 4},
        {"step": 2, "action": "تنفيذ واجهة API", "estimated_hours": 8},
        {"step": 3, "action": "ربط قاعدة البيانات", "estimated_hours": 6}
    ]',
    '["تغيير متطلبات API أثناء التنفيذ", "أداء منخفض مع كميات كبيرة"]'
);
```

## الاستخدام في سير العمل الوكيل

1. **وكيل التخطيط** (Plan Agent) يستلم SPEC-ID أو TOPIC-ID وينشئ خطة تنفيذ.
2. يتم تحويل implementation_steps إلى **مهام** (Tasks) في النظام.
3. ترتبط المخاطر (risks) مع ADRs عبر doc_edges لإظهار القرارات التي تعالج هذه المخاطر.
4. يتم تمرير الخطة إلى **وكيل التنسيق** (Orchestrator) لإنشاء Execution Plan.
