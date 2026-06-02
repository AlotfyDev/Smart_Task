# ADR — سجل القرارات المعمارية (Architectural Decision Record)

## الغرض

توثيق القرارات المعمارية الهامة مع شرح السياق والبدائل والنتائج.  
ADR ليس جزءًا من السلسلة الهرمية الأساسية بل هو فئة **عرضية** (cross-cutting) يمكن أن تشير إلى أي وثيقة.

## المخطط (DDL)

```sql
CREATE TABLE adrs (
    id                TEXT    PRIMARY KEY,                -- ADR-001
    classification_id INTEGER REFERENCES adr_classifications(id),
    title             TEXT    NOT NULL,
    context           TEXT    NOT NULL,                   -- السياق الذي دفع للقرار
    decision          TEXT    NOT NULL,                   -- القرار المتخذ
    consequences      TEXT    NOT NULL,                   -- النتائج المترتبة (إيجابية وسلبية)
    alternatives      TEXT,                               -- البدائل التي تم النظر فيها
    status            TEXT    NOT NULL DEFAULT 'proposed',-- proposed / accepted / deprecated / superseded
    superseded_by     TEXT,                               -- ADR-ID الذي حل محل هذا القرار
    target_id         TEXT,                               -- معرف الوثيقة التي يتعلق بها القرار (نصي — أي نوع)
    target_type       TEXT,                               -- نوع الوثيقة المستهدفة
    version           INTEGER NOT NULL DEFAULT 1,
    created_at        TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at        TEXT    NOT NULL DEFAULT (datetime('now'))
);
```

## adr_classifications

```sql
CREATE TABLE adr_classifications (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    code        TEXT    UNIQUE NOT NULL,
    name        TEXT    NOT NULL,
    description TEXT    NOT NULL
);
```

أنواع التصنيفات: `technology-choice`, `architecture-change`, `interface-design`, `process-decision`, `data-model`, `security`, `deployment`, `dependency`.

## علاقة الوالد

- **الوالد**: لا يوجد FK مباشر — ADR يمكن أن يشير إلى أي وثيقة.
- **الربط**: عبر حقل `target_id` (نصي) أو عبر doc_edges بنوع `references`.
- **التصنيف**: عبر FK اختياري إلى `adr_classifications`.

## مثال

```sql
INSERT INTO adrs (id, classification_id, title, context, decision, consequences, status, target_id, target_type)
VALUES (
    'ADR-001',
    (SELECT id FROM adr_classifications WHERE code = 'architecture-change'),
    'النموذج البياني المختلط لوثائق Smart Task',
    'كان النظام يستخدم ملفات Markdown غير منظمة مع عدم وجود تكامل مرجعي أو إمكانية استعلام.',
    'اعتماد نموذج مختلط: جداول منفصلة لكل فئة وثيقة مع FK مباشر + جدول حواف عام doc_edges.',
    '["+ تتبع كامل للوثائق", "+ إمكانية الاستعلام SQL", "+ مرونة في العلاقات", "- تعقيد إضافي في طبقة التطبيق"]',
    'accepted',
    NULL,
    NULL
);
```

## الاستخدام في سير العمل الوكيل

1. **وكيل القرارات** (ADR Agent) يسجل القرارات المهمة أثناء مرحلة التصميم.
2. يتم ربط ADR بالوثائق المتأثرة عبر doc_edges: `(adr, ADR-NNN, prd, PRD-001, 'references')`.
3. عند تغيير قرار معماري، يتم إنشاء ADR جديد مع `supersedes` يشير إلى ADR القديم.
4. تُستخدم تصنيفات ADR لتصفية القرارات حسب النوع في واجهة المستخدم.
