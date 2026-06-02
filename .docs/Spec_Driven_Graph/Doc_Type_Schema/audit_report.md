# مخطط كيان تقرير التدقيق (Audit Report Schema)

## تعريف

يمثل كيان `audit_report` وثيقة تحقق بعدي (post-execution verification). يتأكد من أن الـ Execution Plan نُفذ بشكل صحيح، ويوثق findings و violations ومدى تغطية الفجوات التي كشفها Test. بينما Test يكشف الفجوات قبليًا/أثناء التنفيذ، Audit Report يتحقق بعديًا من معالجتها.

## العلاقة مع Test

- **Test** يكشف الفجوات (قبلي/أثناء) ← **Audit Report** يتحقق من معالجتها (بعدي)
- Test `informs` → Audit Report: فجوات Test تُوجه تركيز التدقيق
- Audit Report `references` → Test: يتتبع نتائج التدقيق لفجوات محددة

## المسار في السلسلة

```
Task → Wave → Execution Plan → Audit Report
                                    ↑
                              Test (informs)
```

## DDL

```sql
CREATE TABLE audit_reports (
    id                  TEXT PRIMARY KEY,       -- AR-001
    execution_plan_id   TEXT NOT NULL REFERENCES execution_plans(id),
    task_id             TEXT NOT NULL REFERENCES tasks(id),
    title               TEXT NOT NULL,
    status              TEXT NOT NULL CHECK (status IN (
                            'pending',
                            'in_review',
                            'passed',
                            'failed'
                        )),
    findings            TEXT NOT NULL,          -- JSON: array of findings (pass/warning/violation)
    violations          TEXT,                    -- JSON: array of violations with remediation
    coverage_report     TEXT,                    -- JSON: tested vs total capabilities + missed gaps
    informed_by_tests   TEXT,                    -- JSON: array of test references influencing this audit
    recommendations     TEXT,                    -- JSON: array of recommendation objects
    tags                TEXT NOT NULL DEFAULT '[]',
    version             TEXT NOT NULL DEFAULT '1.0',
    created_at          TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at          TEXT NOT NULL DEFAULT (datetime('now'))
);
```

## شرح الحقول

| الحقل | النوع | إلزامي | مثال JSON | الغرض |
|-------|-------|--------|-----------|-------|
| `id` | TEXT | نعم | `"AR-001"` | معرف فريد لتقرير التدقيق |
| `execution_plan_id` | TEXT | نعم | `"EP-001"` | خطة التنفيذ التي يُدقق تنفيذها |
| `task_id` | TEXT | نعم | `"TASK-OPENAI-001"` | المهمة التي يُتدقق تنفيذها |
| `title` | TEXT | نعم | `"تدقيق تنفيذ خوارزمية المطابقة"` | عنوان وصفي لتقرير التدقيق |
| `status` | TEXT | نعم | `"in_review"` | دورة حياة التدقيق: pending → in_review → passed/failed |
| `findings` | TEXT | نعم | `[{"finding_id":"F-001","category":"violation","description":"...","severity":"critical","source":"...","recommendation":"...","related_test_gap":"GAP-001"}]` | مصفوفة findings — كل finding يمثل pass أو warning أو violation مع severity و source و recommendation |
| `violations` | TEXT | لا | `[{"violation_id":"V-001","rule_id":"R-001","description":"...","severity":"critical","affected_component":"...","remediation":"...","resolved":false}]` | مصفوفة violations — انتهاكات لقواعد محددة مع remediation وخطة حل |
| `coverage_report` | TEXT | لا | `{"tested_capabilities":8,"total_capabilities":10,"coverage_percentage":80.0,"missed_gaps":["GAP-002"],"untested_capabilities":["..."]}` | تقرير التغطية — tested vs total capabilities، missed gaps من Test لم تُغطَ، coverage_percentage |
| `informed_by_tests` | TEXT | لا | `[{"test_id":"TEST-CA-001","gap_ids":["GAP-001","GAP-002"],"relevance":"كشف فجوات في آلية إعادة المحاولة"}]` | مصفوفة Tests التي أثّرت في هذا التدقيق — كل عنصر يربط test_id بالفجوات التي ركز عليها التدقيق |
| `recommendations` | TEXT | لا | `[{"recommendation_id":"REC-001","action":"إعادة هيكلة وحدة إعادة المحاولة","priority":1,"target_type":"ep","target_id":"EP-002"}]` | مصفوفة توصيات قابلة للتنفيذ — كل توصية توجه إلى نوع مستهدف (adr/plan/ep/task) |
| `tags` | TEXT | نعم | `["audit", "verification"]` | وسوم لتصنيف تقارير التدقيق |
| `version` | TEXT | نعم | `"1.0"` | إصدار تقرير التدقيق |
| `created_at` | TEXT | نعم | `"2025-01-01T00:00:00Z"` | طابع زمني للإنشاء |
| `updated_at` | TEXT | نعم | `"2025-01-15T00:00:00Z"` | طابع زمني لآخر تحديث |

## الروابط عبر doc_edges

| المصدر | نوع الحافة | الهدف | المعنى |
|--------|-----------|-------|--------|
| `AR-001` | `belongs_to` | `EP-001` | تابع لخطة التنفيذ |
| `AR-001` | `belongs_to` | `TASK-001` | تابع للمهمة |
| `AR-001` | `informed_by` | `TEST-001` | نتائج Test أثّرت في تركيز التدقيق |
| `AR-001` | `references` | `ADR-001` | يشير إلى قرار معماري نتج عن الفجوة |
| `AR-001` | `references` | `REC-001` | يشير إلى توصية صدرت نتيجة التدقيق |

## دورة حالة Audit Report

```
pending → in_review → passed
                     → failed
```

- `pending`: في انتظار بدء التدقيق — لم يُنفذ بعد
- `in_review`: قيد المراجعة — جارٍ تحليل findings وتقييم violations
- `passed`: اجتاز التدقيق — التنفيذ متوافق مع الخطة وكل الفجوات مغطاة
- `failed`: فشل التدقيق — توجد violations أو gaps غير مغطاة

## دورة حياة الربط

```
1. Execution Plan يُنفذ ← يُنشأ Audit Report (status = pending)
2. Test يُنتج فجوات ← edges informed_by تُربط Audit Report بـ Test
3. يُجرى التدقيق ← findings تمتلئ بنتائج الفحص
4. إن وُجدت violations ← تُسجل في violations مع remediation
5. إن وُجدت gaps غير مغطاة ← تُسجل في coverage_report.missed_gaps
6. ينتج recommendations ← تُربط عبر edges references
7. يُغلق التدقيق ← status = passed أو failed
```

## مصدر الحقيقة

مثل بقية الكيانات، `doc_edges` هو مصدر الحقيقة للربط. حقول `execution_plan_id` و `task_id` هي FK مباشر لضمان التكامل المرجعي. الحواف الأخرى (informed_by, references) عبر `doc_edges`.
