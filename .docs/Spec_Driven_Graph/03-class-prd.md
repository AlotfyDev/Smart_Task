# PRD — وثيقة متطلبات المنتج (Product Requirements Document)

## الغرض

PRD هو **جذر السلسلة** — يحدد رؤية الأعمال، الأهداف الاستراتيجية، واحتياجات المستخدم.  
يمثل "لماذا" نبني هذا المنتج قبل "ماذا" أو "كيف".

## المخطط (DDL)

```sql
CREATE TABLE prds (
    id              TEXT    PRIMARY KEY,                -- PRD-001
    title           TEXT    NOT NULL,
    business_goals  TEXT    NOT NULL,                   -- أهداف الأعمال
    user_personas   TEXT,                               -- شخصيات المستخدمين (JSON array)
    success_metrics TEXT,                               -- مقاييس النجاح (JSON array)
    stakeholders    TEXT,                               -- أصحاب المصلحة (JSON array)
    scope           TEXT,                               -- نطاق المشروع
    constraints     TEXT,                               -- قيود
    status          TEXT    NOT NULL DEFAULT 'draft',   -- draft / reviewed / approved
    version         INTEGER NOT NULL DEFAULT 1,
    tags            TEXT,                               -- JSON array
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);
```

## علاقة الوالد

- **الوالد**: لا يوجد (جذر السلسلة)
- **الأبناء المباشرون**: architecture_docs (عبر FK: `architecture_docs.prd_id`)
- **العلاقات البيانية**: تدخل في doc_edges كـ `source_type = 'prd'`

## مثال

```sql
INSERT INTO prds (id, title, business_goals, status)
VALUES (
    'PRD-001',
    'نظام التداول الآلي الذكي',
    '["توفير منصة تداول آلية تدعم استراتيجيات متعددة", "تقليل وقت تنفيذ الصفقات إلى أقل من 100ms"]',
    'approved'
);
```

## الاستخدام في سير العمل الوكيل (Agentic Workflow)

1. **منسق المستوى الأعلى** (Orchestrator) يقوم بإنشاء PRD بناءً على طلب المستخدم.
2. يتم تمرير PRD إلى **وكيل معماري** (Architecture Agent) لاستخراج التصميم المعماري.
3. تُستخدم مقاييس النجاح من PRD لاحقًا في **تقرير التدقيق** (Audit Report) لتقييم النتائج.
4. يمكن ربط ADRs بـ PRD عبر doc_edges لتوثيق القرارات التي تؤثر على متطلبات المنتج.
