# مخطط كيان سجل القرارات المعمارية (ADR Schema)

## 1. تعريف

سجل القرارات المعمارية (Architectural Decision Record - ADR) هو وثيقة توثق قراراً معمارياً مهماً مع سياقه والخيارات المتاحة وآثاره. يُسجّل القرار فور اتخاذه ويُعتبر ثابتاً (immutable) بعد اعتماده — لا يُعدّل بل يُستبدل بقرار جديد. يضمن ADR إمكانية تتبع الأساس المنطقي لكل قرار معماري عبر دورة حياة المشروع.

## 2. تعريف الجداول (DDL)

```sql
CREATE TABLE adr_classifications (
    id    INTEGER PRIMARY KEY,
    code  TEXT NOT NULL UNIQUE,
    name  TEXT NOT NULL,
    desc  TEXT
);

CREATE TABLE adrs (
    id                 TEXT PRIMARY KEY,       -- ADR-001
    classification_id  INTEGER REFERENCES adr_classifications(id),
    title              TEXT NOT NULL,
    status             TEXT NOT NULL CHECK (status IN ('proposed', 'accepted', 'deprecated', 'superseded')),
    context            TEXT NOT NULL,           -- المشكلة والظروف
    decision           TEXT NOT NULL,           -- القرار (active voice, present tense)
    consequences       TEXT NOT NULL,           -- الآثار الإيجابية والسلبية
    considered_options TEXT NOT NULL,           -- JSON: [{"option":"...","pros":["..."],"cons":["..."],"reason_rejected":"..."}]
    deciders           TEXT,                    -- JSON: [{"name":"...","role":"..."}] -- اختياري
    supersedes         TEXT,                    -- JSON: [ADR-001] ADRs اللي يحل محلهم -- اختياري
    superseded_by      TEXT,                    -- ADR-XXX -- اختياري -- ADR اللي حل محله
    compliance         TEXT,                    -- إزاي نتحقق من الالتزام بالقرار
    target_id          TEXT,                    -- الوثيقة المستهدفة (PRD-001, ARCH-001, SPEC-001...)
    xspec_ids          TEXT,                    -- JSON: convenience -> cross_cutting_specs
    dst_ids            TEXT,                    -- JSON: convenience -> data_structures
    tags               TEXT NOT NULL DEFAULT '[]',
    version            TEXT NOT NULL DEFAULT '1.0',
    created_at         TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at         TEXT NOT NULL DEFAULT (datetime('now'))
);
```

## 3. قيم تصنيفات ADR

| id | code | name | desc |
|----|------|------|------|
| 1 | `tech-choice` | Technology Choice | اختيار تقنية أو مكتبة أو إطار عمل |
| 2 | `arch-change` | Architecture Change | تغيير هيكل النظام أو حدود المكونات |
| 3 | `interface-design` | Interface Design | قرار بشأن عقد API أو بروتوكول تواصل |
| 4 | `process-decision` | Process Decision | قرار بشأن عملية التطوير أو الأدوات أو سير العمل |

## 4. شرح حقول adrs

| الحقل | النوع | مطلوب | بنية JSON | الغرض الدلالي |
|-------|-------|--------|-----------|---------------|
| `id` | TEXT | نعم | - | معرف فريد للمستند بصيغة ADR-XXX |
| `classification_id` | INTEGER | لا | - | مرجع لتصنيف القرار من جدول `adr_classifications` |
| `title` | TEXT | نعم | - | عنوان وصفي مختصر للقرار |
| `status` | TEXT | نعم | - | حالة القرار: `proposed` (مقترح)، `accepted` (مقبول)، `deprecated` (مهمل)، `superseded` (مستبدل) |
| `context` | TEXT | نعم | - | وصف المشكلة والظروف المحيطة التي استدعت القرار |
| `decision` | TEXT | نعم | - | القرار المتخذ بصيغة المضارع المبني للمعلوم (active voice, present tense) |
| `consequences` | TEXT | نعم | - | الآثار الإيجابية والسلبية المترتبة على القرار |
| `considered_options` | TEXT | نعم | `[{"option":"خيار","pros":["ميزة"],"cons":["عيب"],"reason_rejected":"سبب الرفض"}]` | الخيارات التي تمت دراستها مع تقييم كل منها |
| `deciders` | TEXT | لا | `[{"name":"أحمد","role":"مهندس معماري"}]` | الأشخاص المشاركون في اتخاذ القرار |
| `supersedes` | TEXT | لا | `["ADR-001","ADR-002"]` | معرفات ADRs التي يحل هذا القرار محلها |
| `superseded_by` | TEXT | لا | `"ADR-005"` | معرف ADR الذي حل محل هذا القرار |
| `compliance` | TEXT | لا | - | كيفية التحقق من الالتزام بالقرار (إجراءات المراجعة، الأدوات، الاختبارات) |
| `target_id` | TEXT | لا | - | معرف الوثيقة المستهدفة التي يخصها القرار (PRD-001، ARCH-001، SPEC-001...) |
| `xspec_ids` | TEXT | لا | `["XSPEC-001","XSPEC-002"]` | معرفات وثائق المواصفات العرضية المرتبطة |
| `dst_ids` | TEXT | لا | `["DST-001","DST-002"]` | معرفات وثائق هياكل البيانات المرتبطة |
| `tags` | TEXT | نعم | `["أداء","أمان"]` | وسوم لتصنيف المستند والبحث |
| `version` | TEXT | نعم | `"1.0"` | إصدار المستند باستخدام الصياغة الدلالية (Semantic Versioning) |
| `created_at` | TEXT | نعم | - | طابع زمني لإنشاء المستند |
| `updated_at` | TEXT | نعم | - | طابع زمني لآخر تحديث |

## 5. علاقات الحواف (doc_edges)

| من | العلاقة | إلى | ملاحظات |
|----|---------|-----|---------|
| ADR | `references` | أي وثيقة (عبر `target_id`) | `target_id` من نوع TEXT بدون مفتاح خارجي لأنه يمكن أن يشير إلى أي نوع وثيقة |
| ADR | `supersedes` | ADR | استبدال قرار بقرار آخر |
| ADR | `references` | XSPEC | ربط قرار بوثيقة مواصفات عرضية |
| ADR | `uses` | DST | استخدام هيكل بيانات معين في القرار |
