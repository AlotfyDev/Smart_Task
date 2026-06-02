# Spec — مواصفات السلوك (Behavior Specification)

## الغرض

توثيق سلوك النظام بالتفصيل: قصص المستخدم، معايير القبول، نماذج البيانات، وسيناريوهات الاستخدام.  
تمثل "ماذا" يجب أن يفعل النظام بالضبط.

## المخطط (DDL)

```sql
CREATE TABLE specs (
    id                 TEXT    PRIMARY KEY,                -- SPEC-001
    arch_id            INTEGER NOT NULL REFERENCES architecture_docs(id),
    title              TEXT    NOT NULL,
    user_stories       TEXT    NOT NULL,                   -- قصص المستخدم (JSON array)
    acceptance_criteria TEXT   NOT NULL,                   -- معايير القبول (JSON array)
    data_models        TEXT,                               -- نماذج البيانات (JSON)
    scenarios          TEXT,                               -- سيناريوهات الاستخدام
    business_rules     TEXT,                               -- قواعد الأعمال
    status             TEXT    NOT NULL DEFAULT 'draft',   -- draft / reviewed / approved
    version            INTEGER NOT NULL DEFAULT 1,
    tags               TEXT,
    created_at         TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at         TEXT    NOT NULL DEFAULT (datetime('now'))
);
```

## علاقة الوالد

- **الوالد**: architecture_docs(id) — كل مواصفات تنتمي إلى وثيقة معمارية واحدة.
- **الأبناء المباشرون**: spec_topics (عبر FK: `spec_topics.spec_id`)
- **المفتاح الخارجي**: `arch_id REFERENCES architecture_docs(id)`

## مثال

```sql
INSERT INTO specs (id, arch_id, title, user_stories, acceptance_criteria)
VALUES (
    'SPEC-001',
    'ARCH-001',
    'مواصفات نظام تنفيذ الصفقات',
    '["كمستخدم، أريد تنفيذ صفقة شراء بسرعة لتجنب تقلبات السوق."]',
    '["يجب أن لا تتجاوز مدة التنفيذ 100ms", "يجب تسجيل كل صفقة في قاعدة البيانات"]'
);
```

## الاستخدام في سير العمل الوكيل

1. **وكيل المواصفات** (Spec Agent) يستلم ARCH-ID وينشئ المواصفات.
2. يتم تفكيك المواصفات إلى **Spec Topics** بواسطة وكيل التفكيك.
3. تُستخدم acceptance_criteria لاحقًا كمعايير للتحقق في Audit Report.
4. يتم تسجيل القرارات المتعلقة بالمواصفات في ADRs عبر doc_edges.
