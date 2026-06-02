# PRD Document Class Schema

## 1. تعريف المستند

مستند PRD (Product Requirements Document) هو الوثيقة الأساسية التي تحدد متطلبات المنتج من منظور القيمة والقابلية للتسليم. يمثل هذا المستند الطبقة الأولى في سلسلة التحلل (Decomposition Chain) حيث تُشتق منه وثائق العمارة (Architecture) والتصميم التفصيلي.

## 2. تعريف الجدول (DDL)

```sql
CREATE TABLE prds (
    id                      TEXT PRIMARY KEY,      -- PRD-001
    title                   TEXT NOT NULL,
    status                  TEXT NOT NULL CHECK (status IN ('draft', 'reviewed', 'approved', 'superseded')),
    version                 TEXT NOT NULL DEFAULT '1.0',
    tags                    TEXT NOT NULL DEFAULT '[]',
    summary                 TEXT NOT NULL,
    goals                   TEXT NOT NULL,          -- JSON: [{"id":"G1","description":"...","priority":"high"},...]
    personas                TEXT,                   -- JSON: optional
    user_stories            TEXT NOT NULL,          -- JSON: [{"id":"US-001","priority":"high",...}] -- decomposition driver
    functional_requirements TEXT NOT NULL,          -- JSON: [{"id":"FR-001","statement":"...","acceptance":"..."}]
    non_functional_req      TEXT NOT NULL,          -- JSON
    success_metrics         TEXT NOT NULL,          -- JSON
    constraints             TEXT NOT NULL,          -- JSON
    release_criteria        TEXT NOT NULL,          -- JSON
    assumptions             TEXT,                   -- JSON: optional
    open_questions          TEXT,                   -- JSON: optional
    created_at              TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at              TEXT NOT NULL DEFAULT (datetime('now'))
);
```

## 3. شرح الحقول

| الحقل | النوع | مطلوب | بنية JSON | الغرض الدلالي |
|-------|-------|--------|-----------|---------------|
| `id` | TEXT | نعم | - | معرف فريد للمستند بصيغة PRD-XXX. يستخدم كمرجع عند الربط مع وثائق Architecture. |
| `title` | TEXT | نعم | - | عنوان وصفي للمنتج أو الميزة. |
| `status` | TEXT | نعم | - | حالة دورة حياة المستند: `draft` (مسودة)، `reviewed` (مراجع)، `approved` (معتمد)، `superseded` (مستبدل). |
| `version` | TEXT | نعم | - | إصدار المستند باستخدام الصياغة الدلالية (Semantic Versioning). القيمة الافتراضية `1.0`. |
| `tags` | TEXT | نعم | `["tag1","tag2"]` | مصفوفة من النصوص لتصنيف المستند وتسهيل البحث والتصفية. |
| `summary` | TEXT | نعم | - | ملخص تنفيذي يصف المشكلة والحل المقترح في 3-5 جمل. |
| `goals` | TEXT | نعم | `[{"id":"G1","description":"نص الهدف","priority":"high"}]` | قائمة بالأهداف الاستراتيجية للمنتج. كل هدف يحمل معرّفاً وأولوية. |
| `personas` | TEXT | لا | `[{"id":"P1","name":"...","role":"..."}]` | شخصيات المستخدمين المستهدفين. اختياري ولكن موصى به لتوضيح السياق. |
| `user_stories` | TEXT | نعم | `[{"id":"US-001","as_a":"...","i_want":"...","so_that":"...","priority":"high","goal_ref":"G1"}]` | **محرك التحلل (Decomposition Driver)**. قصص المستخدم التي تمثل متطلبات قابلة للتنفيذ. كل قصة تحمل أولوية ومرجعاً للهدف. هذه القصص هي نقطة الانطلاق لسلسلة التحلل نحو Architecture. |
| `functional_requirements` | TEXT | نعم | `[{"id":"FR-001","statement":"...","acceptance":"...","story_ref":"US-001"}]` | المتطلبات الوظيفية المستخلصة من قصص المستخدم. كل متطلب يصف سلوكاً محددا للنظام مع معايير القبول. |
| `non_functional_req` | TEXT | نعم | `[{"id":"NFR-001","category":"performance","statement":"..."}]` | المتطلبات غير الوظيفية (الأداء، الأمان، التوفر، إلخ). |
| `success_metrics` | TEXT | نعم | `[{"id":"SM-001","metric":"...","target":"..."}]` | مقاييس النجاح القابلة للقياس لتحديد ما إذا كان المنتج يحقق أهدافه. |
| `constraints` | TEXT | نعم | `[{"id":"C-001","type":"technical","description":"..."}]` | القيود المفروضة على الحل (تقنية، تنظيمية، زمنية). |
| `release_criteria` | TEXT | نعم | `[{"id":"RC-001","criterion":"...","must_pass":true}]` | معايير الإطلاق التي يجب استيفاؤها قبل نشر المنتج. |
| `assumptions` | TEXT | لا | `[{"id":"A-001","assumption":"...","impact":"..."}]` | الافتراضات التي بُني عليها المستند مع تقييم أثر مخالفتها. |
| `open_questions` | TEXT | لا | `[{"id":"OQ-001","question":"...","assigned_to":"..."}]` | الأسئلة المفتوحة التي تحتاج إلى إجابة قبل اكتمال المستند. |
| `created_at` | TEXT | نعم | - | طابع زمني لتاريخ إنشاء المستند. |
| `updated_at` | TEXT | نعم | - | طابع زمني لآخر تحديث للمستند. |

## 4. ملاحظة التحلل (Decomposition Note)

**user_stories** هو محرك التحلل الأساسي في مستند PRD. تبدأ سلسلة التحلل (Decomposition Chain) كالتالي:

```
user_stories (PRD) --> Architecture (ARC) --> Design Docs (DSD) --> Implementation
```

كل قصة مستخدم (User Story) في `user_stories` تُستخدم كمدخل لاستخراج قرارات العمارة في مستند Architecture. لهذا السبب، تحمل كل قصة معرّفاً فريداً (`US-XXX`) يمكن الرجوع إليه من مستندات Architecture عبر حقل `story_ref` أو `derived_from`.

هذا الربط يضمن إمكانية التتبع (Traceability) الكاملة من الاحتياجات التجارية إلى قرارات العمارة إلى التصميم التفصيلي إلى التنفيذ.
