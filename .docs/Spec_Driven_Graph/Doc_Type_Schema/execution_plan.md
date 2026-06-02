# مخطط كيان خطة التنفيذ التقنية (Execution Plan Schema)

## تعريف

يمثل كيان `execution_plan` الخوارزمية وتفاصيل التنفيذ المطلوبة لتحقيق أهداف الموجة (Wave). يحدد **كيفية كتابة الكود** — الخوارزميات الأساسية، تدفق البيانات، قواعد العمل، والمنهجية التقنية لكل وحدة. لا يتعلق بتنسيق الوكلاء (هذا دور Wave). يتعلق بتعليمات التنفيذ القابلة للتنفيذ التي تخبر الوكيل الفرعي بكيفية كتابة الكود.

## الفرق بين Interface و Execution Plan و Wave

- **Interface**: العقد الخارجي — ما الذي تبدو عليه API (التوقيع، السلوك، أخطاء، شروط)
- **Execution Plan**: المنطق الداخلي — كيف يعمل الكود من الداخل (خوارزميات، تدفق بيانات، قواعد عمل)
- **Wave**: تنسيق الوكلاء — من يدير ماذا ومتى (توجيه الـ sub-agents)

## DDL

```sql
CREATE TABLE execution_plans (
    id                  TEXT PRIMARY KEY,       -- EP-001
    plan_id             TEXT NOT NULL REFERENCES plans(id),
    wave_id             TEXT NOT NULL REFERENCES task_waves(id),
    title               TEXT NOT NULL,
    status              TEXT NOT NULL CHECK (status IN ('draft', 'approved', 'implemented', 'verified')),
    algorithm_spec      TEXT NOT NULL,           -- JSON: core algorithm pseudocode + steps
    implementation_details TEXT NOT NULL,        -- JSON: technical approach per module
    data_flow_logic     TEXT NOT NULL,           -- JSON: data transformation within the system
    business_rules      TEXT NOT NULL,           -- JSON: business logic rules to implement
    complexity_analysis TEXT,                    -- JSON: time/space complexity notes
    edge_case_handling  TEXT,                    -- JSON: how to handle edge cases
    file_touches        TEXT,                    -- JSON: expected files to create/modify
    context_bundle      TEXT,                    -- JSON: pre-loaded context for sub-agent (architecture overview, relevant entities, invariants, spec snippets)
    context_sources     TEXT,                    -- JSON: traceability — which docs the context_bundle was derived from
    xspec_ids           TEXT,                    -- JSON: convenience -> cross_cutting_specs
    dst_ids             TEXT,                    -- JSON: convenience -> data_structures
    tags                TEXT NOT NULL DEFAULT '[]',
    version             TEXT NOT NULL DEFAULT '1.0',
    created_at          TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at          TEXT NOT NULL DEFAULT (datetime('now'))
);
```

## شرح الحقول

| الحقل | النوع | إلزامي | مثال JSON | الغرض |
|-------|-------|--------|-----------|-------|
| `id` | TEXT | نعم | `"EP-001"` | معرف فريد وفق نظام ترقيم خطط التنفيذ |
| `plan_id` | TEXT | نعم | `"PLAN-001"` | معرف الخطة الرئيسية التي تنتمي إليها خطة التنفيذ |
| `wave_id` | TEXT | نعم | `"WAVE-001"` | معرف الموجة التي تنفذ هذه الخطة |
| `title` | TEXT | نعم | `"تنفيذ خوارزمية المطابقة"` | عنوان وصفي لخطة التنفيذ |
| `status` | TEXT | نعم | `"approved"` | حالة دورة حياة خطة التنفيذ: draft, approved, implemented, verified |
| `algorithm_spec` | TEXT | نعم | `{"overview": "...", "steps": [{"step": 1, "action": "...", "input": "...", "output": "..."}], "pseudocode": "...", "flow_diagram": "..."}` | مواصفات الخوارزمية الأساسية — الخطوات، الكود الزائف، مخطط التدفق |
| `implementation_details` | TEXT | نعم | `[{"module": "...", "file": "src/module.py", "approach": "...", "classes": ["..."], "patterns": ["..."]}]` | تفاصيل التنفيذ التقني لكل وحدة — المنهجية، الكلاسات، الأنماط |
| `data_flow_logic` | TEXT | نعم | `[{"from": "...", "to": "...", "transformation": "...", "condition": "..."}]` | منطق تدفق البيانات — التحويلات داخل النظام |
| `business_rules` | TEXT | نعم | `[{"rule_id": "BR-001", "condition": "...", "action": "...", "priority": 1}]` | قواعد العمل التي يجب تنفيذها في الكود |
| `complexity_analysis` | TEXT | لا | `{"time": "O(n log n)", "space": "O(n)", "bottleneck": "...", "optimization_notes": "..."}` | تحليل التعقيد الزمني والمكاني |
| `edge_case_handling` | TEXT | لا | `[{"case": "...", "expected": "...", "handling": "..."}]` | معالجة الحالات الحدية — كيف تتعامل مع المدخلات غير المتوقعة |
| `file_touches` | TEXT | لا | `[{"path": "src/module/file.py", "purpose": "...", "change_type": "create", "depends_on": ["..."]}]` | الملفات المتوقع إنشاؤها أو تعديلها أو حذفها |
| `context_bundle` | TEXT | لا | `{"architecture_overview":"...","relevant_entities":[...],"relevant_invariants":[...],"relevant_spec_snippets":[...]}` | السياق المُحمّل مسبقًا للـ sub-agent — يجمع architecture overview، الـ entities ذات الصلة، الـ invariants، spec snippets من الـ cross_cutting_specs و data_structures اللي الـ EP يرتبط بها |
| `context_sources` | TEXT | لا | `[{"doc_type":"architecture_docs","doc_id":"ARCH-001","edge_type":"implements"},{"doc_type":"data_structures","doc_id":"DST-001","edge_type":"uses"}]` | traceability — يسجل إيه الـ docs الـ context_bundle اشتق منها، لضمان إمكانية التتبع والتحديث |
| `xspec_ids` | TEXT | لا | `["XSPEC-001"]` | معرفات المواصفات العرضية المرجعية — مرآة لروابط doc_edges من نوع references |
| `dst_ids` | TEXT | لا | `["DST-001"]` | معرفات هياكل البيانات المستخدمة — مرآة لروابط doc_edges من نوع uses |
| `tags` | TEXT | نعم | `["execution", "algorithm"]` | وسوم لتصنيف خطة التنفيذ وتصفيتها |
| `version` | TEXT | نعم | `"1.0"` | إصدار خطة التنفيذ |
| `created_at` | TEXT | نعم | `"2025-01-01T00:00:00Z"` | طابع زمني للإنشاء |
| `updated_at` | TEXT | نعم | `"2025-01-15T00:00:00Z"` | طابع زمني لآخر تحديث |

## الروابط عبر doc_edges

| المصدر | نوع الحافة | الهدف | المعنى |
|--------|-----------|-------|--------|
| `EP-001` | `implements` | `PLAN-001` | الخطة الرئيسية التي تنفذها خطة التنفيذ هذه |
| `EP-001` | `belongs_to` | `WAVE-001` | الموجة التي تنتمي إليها خطة التنفيذ |
| `EP-001` | `references` | `XSPEC-001` | مرجع إلى مواصفة عرضية تنطبق على خطة التنفيذ |
| `EP-001` | `uses` | `DST-001` | هيكل بيانات تستخدمه خطة التنفيذ |
| `EP-001` | `produces` | `AUDIT-001` | تقرير التدقيق الناتج عن التحقق من خطة التنفيذ |

### مصدر الحقيقة

`doc_edges` هو مصدر الحقيقة الوحيد للربط. الحقول `xspec_ids` و `dst_ids` هي **حقول تسهيل (convenience)** — تعكس الروابط الموجودة في `doc_edges` لتسريع الاستعلام دون الحاجة لضم جداول `doc_edges` في كل استعلام. يجب أن تظل متزامنة مع `doc_edges` عبر منطق التطبيق.

### دورة حياة الربط

```
1. إنشاء Execution Plan جديد ← إنشاء edges في doc_edges
2. تحديث `xspec_ids` / `dst_ids` ← mirror من doc_edges
3. استعلام سريع ← استخدام الـ convenience fields
4. استعلام دقيق (للتحقق) ← استعلام doc_edges مباشرة
```
