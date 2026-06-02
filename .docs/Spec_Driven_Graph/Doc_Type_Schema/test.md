# مخطط كيان الاختبار (Test Schema)

## تعريف

يمثل كيان `test` أداة كشف الفجوات المنطقية والضعف الوظيفي في النظام. **ليس** اختبارًا تقليديًا (unit/integration/e2e) بل **تحليل كفاءات معماري** يكشف:

- **Logical Gaps**: قدرات مفقودة كليًا في النظام
- **Functionality Weakness**: قدرات موجودة لكنها ضعيفة أو غير صحيحة
- **Root Cause**: الأسباب الجذرية المعمارية لكل فجوة
- **Architectural Insights**: توصيات لحلول معمارية جذرية

## مبدأ أساسي

لا يُعترف بـ Task بأنها منجزة إلا إذا اجتازت Test واحدًا على الأقل بفئة `capability_audit` أو `gap_analysis`. الاختبارات هنا **أداة كشف**، وليست أداة تمرير.

## فئات الاختبار

| الفئة | البادئة | الهدف |
|-------|---------|-------|
| `capability_audit` | TEST-CA-NNN | مسح منهجي للقدرات المتوقعة vs الموجودة — يحدد present/absent/weak/incorrect |
| `gap_analysis` | TEST-GA-NNN | تعمق في الفجوات: إيه المفقود، ليه، وأيه السبب المعماري الجذري |
| `architectural_property` | TEST-AP-NNN | يختبر خصائص معمارية: boundaries, data flow integrity, coupling, cohesion |
| `root_cause_regression` | TEST-RC-NNN | يتحقق إن جذر معماري معين اتعالج فعليًا (مش مجرد treat) |

## DDL

```sql
CREATE TABLE tests (
    id                      TEXT PRIMARY KEY,       -- TEST-CA-001, TEST-GA-001, etc.
    task_id                 TEXT NOT NULL REFERENCES tasks(id),
    title                   TEXT NOT NULL,
    test_category           TEXT NOT NULL CHECK (test_category IN (
                                'capability_audit',
                                'gap_analysis',
                                'architectural_property',
                                'root_cause_regression'
                            )),
    status                  TEXT NOT NULL CHECK (status IN (
                                'draft',
                                'approved',
                                'executed',
                                'resolved'
                            )),
    capability_matrix       TEXT NOT NULL,           -- JSON: القدرات المتوقعة → الحالة → severity → root cause
    logical_gaps            TEXT,                    -- JSON: الفجوات المنطقية مع الأسباب الجذرية
    architectural_insights  TEXT,                    -- JSON: توصيات لحلول معمارية جذرية
    scenarios               TEXT,                    -- JSON: سيناريوهات استخدام حقيقية
    production_readiness    TEXT,                    -- JSON: تقييم الجاهزية للإنتاج
    tags                    TEXT NOT NULL DEFAULT '[]',
    version                 TEXT NOT NULL DEFAULT '1.0',
    created_at              TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at              TEXT NOT NULL DEFAULT (datetime('now'))
);
```

## شرح الحقول

| الحقل | النوع | إلزامي | مثال JSON | الغرض |
|-------|-------|--------|-----------|-------|
| `id` | TEXT | نعم | `"TEST-CA-001"` | معرف فريد — البادئة حسب فئة الاختبار |
| `task_id` | TEXT | نعم | `"TASK-OPENAI-001"` | المهمة التي يختبرها هذا الكيان |
| `title` | TEXT | نعم | `"تدقيق قدرة نظام التداول على إعادة المحاولة"` | عنوان وصفي |
| `test_category` | TEXT | نعم | `"capability_audit"` | فئة الاختبار — تحدد منهجية التحليل |
| `status` | TEXT | نعم | `"executed"` | دورة حياة الاختبار: draft → approved → executed → resolved |
| `capability_matrix` | TEXT | نعم | `[{"capability":"...","expected_behavior":"...","status":"absent","gap_severity":"critical","root_cause":"..."}]` | مصفوفة الكفاءات — الحقل الأساسي: يرسم كل قدرة متوقعة مقابل واقعها وفجوتها وجذرها |
| `logical_gaps` | TEXT | لا | `[{"gap_id":"GAP-001","description":"...","capability":"...","root_cause":"...","affected_components":["..."],"architectural_impact":"...","proposed_adr":"ADR-002"}]` | الفجوات المنطقية المفصلة — كل فجوة مع جذرها المعماري ومكوناتها المتأثرة |
| `architectural_insights` | TEXT | لا | `[{"insight_id":"INS-001","observation":"...","root_architectural_cause":"...","suggested_approach":"...","recommended_adr":true,"priority":1}]` | توصيات معمارية قابلة للتنفيذ — مخرجات التحليل |
| `scenarios` | TEXT | لا | `[{"scenario":"...","input":"...","expected_system_behavior":"...","actual_system_behavior":"...","passed":false,"notes":"..."}]` | سيناريوهات استخدام حقيقية (production-grade) — تختبر النظام في مواقف فعلية |
| `production_readiness` | TEXT | لا | `{"overall_assessment":"not_ready","checks":[{"check":"...","passed":false,"details":"..."}],"blocking_gaps":["GAP-001"]}` | تقييم الجاهزية للإنتاج — هل الموديول جاهز للاستخدام الفعلي؟ |
| `tags` | TEXT | نعم | `["gap-analysis", "retry-mechanism"]` | وسوم لتصنيف وتحليل الفجوات |
| `version` | TEXT | نعم | `"1.0"` | إصدار الاختبار |
| `created_at` | TEXT | نعم | `"2025-01-01T00:00:00Z"` | طابع زمني للإنشاء |
| `updated_at` | TEXT | نعم | `"2025-01-15T00:00:00Z"` | طابع زمني لآخر تحديث |

## الروابط عبر doc_edges

| المصدر | نوع الحافة | الهدف | المعنى |
|--------|-----------|-------|--------|
| `TEST-001` | `belongs_to` | `TASK-001` | المهمة التي ينتمي إليها هذا الاختبار |
| `TEST-001` | `verifies` | `INTF-001` | واجهة API يتم التحقق من سلوكها عبر هذا الاختبار |
| `TEST-001` | `verifies` | `SPEC-001` | مواصفة يتم التحقق من اكتمالها |
| `TEST-001` | `verifies` | `SPEC-TOPIC-001` | موضوع مواصفة يُختبر |
| `TEST-001` | `triggers` | `ADR-001` | فجوة تكتشف → تؤدي إلى قرار معماري جديد |
| `TEST-001` | `informs` | `EP-001` | نتائج الاختبار تؤثر على خطة التنفيذ |

## دورة حياة الربط

```
1. Task تُنشأ ← ينشأ TEST من فئة capability_audit (إلزامي)
2. يُنفذ الاختبار ← capability_matrix تمتلئ بالنتائج
3. إن وُجدت فجوات ← تُسجل في logical_gaps مع root cause
4. root cause معماري ← يُنتج ADR (via edge triggers)
5. ADR يُعالج ← يُعاد اختبار root_cause_regression
6. عند زوال الفجوة ← status = resolved
7. Task تُعتبر منجزة فقط ← بعد resolved لجميع Tests المرتبطة
```

## دورة حالة Test

```
draft → approved → executed → resolved
                              → failed (يُنتج ADR إجباريًا)
```

- `draft`: قيد الصياغة — تحديد الفئة، expected capabilities، السيناريوهات
- `approved`: تمت الموافقة على خطة الاختبار
- `executed`: نُفذ الاختبار — capability_matrix ممتلئة
- `resolved`: الفجوات عولجت معماريًا أو أُغلقت بقرار

## مصدر الحقيقة

مثل بقية الكيانات، `doc_edges` هو مصدر الحقيقة للربط. حقول `task_id` هي FK مباشر لضمان التكامل المرجعي. الحواف الأخرى (verifies, triggers, informs) عبر `doc_edges`.
