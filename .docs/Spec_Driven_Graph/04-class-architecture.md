# Architecture — وثيقة النظام المعماري (System Architecture Document)

## الغرض

توثيق التصميم عالي المستوى للنظام: المكونات الرئيسية، العلاقات بينها، القيود التقنية، والقرارات المعمارية الأساسية.  
ترجمة أهداف PRD إلى هيكل تقني ملموس.

## المخطط (DDL)

```sql
CREATE TABLE architecture_docs (
    id                   TEXT    PRIMARY KEY,                -- ARCH-001
    prd_id               INTEGER NOT NULL REFERENCES prds(id),
    title                TEXT    NOT NULL,
    overview             TEXT    NOT NULL,                   -- نظرة عامة على النظام
    components           TEXT    NOT NULL,                   -- المكونات (JSON array)
    constraints          TEXT,                               -- القيود التقنية (JSON array)
    technology_decisions TEXT,                               -- القرارات التقنية (JSON array)
    diagrams             TEXT,                               -- روابط أو أوصاف للرسوم البيانية
    status               TEXT    NOT NULL DEFAULT 'draft',   -- draft / reviewed / approved
    version              INTEGER NOT NULL DEFAULT 1,
    tags                 TEXT,
    created_at           TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at           TEXT    NOT NULL DEFAULT (datetime('now'))
);
```

## علاقة الوالد

- **الوالد**: prds(id) — كل وثيقة معمارية تنتمي إلى PRD واحد.
- **الأبناء المباشرون**: specs (عبر FK: `specs.arch_id`)
- **المفتاح الخارجي**: `prd_id REFERENCES prds(id)`

## مثال

```sql
INSERT INTO architecture_docs (id, prd_id, title, overview, components)
VALUES (
    'ARCH-001',
    'PRD-001',
    'معمارية نظام التداول الآلي',
    'نظام يعتمد على معمارية الخدمات المصغرة مع ناقل رسائل مركزي.',
    '["واجهة التداول", "محرر الاستراتيجيات", "مدير المخاطر", "ناقل الرسائل", "قاعدة البيانات"]'
);
```

## الاستخدام في سير العمل الوكيل

1. **الوكيل المعماري** (Architecture Agent) يستلم PRD-ID وينشئ وثيقة Architecture.
2. يتم تحويل components إلى **مواصفات سلوك** (Specs) بواسطة وكيل المواصفات.
3. تُستخدم القيود التقنية لتوجيه القرارات في ADR.
4. يمكن ربط ADR بالـ Architecture عبر doc_edges لإظهار القرارات التي تؤثر على المعمارية.
