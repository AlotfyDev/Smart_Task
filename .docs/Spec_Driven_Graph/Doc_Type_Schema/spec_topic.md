# مخطط كيان وثيقة موضوع المواصفات (Spec Topic Schema)

## تعريف

يمثل كيان `spec_topic` تفكيك المواصفة (Spec) إلى اهتمامات مركزة ومحددة. يعالج كل موضوع جانبا واحدا من جوانب المواصفة — سواء كان واجهة (interface)، قاعدة تحقق (validation)، سير عمل (workflow)، نموذج بيانات (data model)، أو حالة حافة (edge case). ينشأ كل موضوع كنتيجة مباشرة لتفكيك حقول المواصفة الأم (لا سيما `interfaces` و `validation_rules` و `edge_cases`) ويشكل الوحدة الأساسية القابلة للتكليف والتنفيذ.

## DDL

```sql
CREATE TABLE spec_topics (
    id                  TEXT PRIMARY KEY,      -- TOPIC-001
    spec_id             TEXT NOT NULL REFERENCES specs(id),
    title               TEXT NOT NULL,
    status              TEXT NOT NULL CHECK (status IN ('draft', 'reviewed', 'approved')),
    topic_type          TEXT NOT NULL CHECK (topic_type IN ('interface', 'validation', 'workflow', 'data_model', 'edge_case')),
    interface_ref       TEXT,                   -- اختياري: اسم الواجهة من المواصفة الأصل
    objective           TEXT NOT NULL,
    detailed_spec       TEXT NOT NULL,           -- JSON
    test_scenarios      TEXT NOT NULL,           -- JSON
    satisfies_spec_refs TEXT NOT NULL,           -- JSON: أسماء واجهات ومعايير التحقق من المواصفة الأم التي يلبيها هذا الموضوع
    file_touches        TEXT,                    -- JSON: اختياري — الملفات المتوقع تعديلها
    dependencies        TEXT,                    -- JSON: اختياري — معرفات مواضيع أخرى ["TOPIC-002"]
    xspec_ids           TEXT,                    -- JSON: اختياري — اختصار لـ cross_cutting_specs المرتبطة
    dst_ids             TEXT,                    -- JSON: اختياري — اختصار لـ data_structures المرتبطة
    version             TEXT NOT NULL DEFAULT '1.0',
    tags                TEXT NOT NULL DEFAULT '[]',
    created_at          TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at          TEXT NOT NULL DEFAULT (datetime('now'))
);
```

## شرح الحقول

| الحقل | النوع | إلزامي | مثال JSON | الغرض |
|-------|-------|--------|-----------|-------|
| `id` | TEXT | نعم | `"TOPIC-001"` | معرف فريد وفق نظام ترقيم مواضيع المواصفات |
| `spec_id` | TEXT | نعم | `"SPEC-001"` | معرف المواصفة الأم (الوالد) |
| `title` | TEXT | نعم | `"واجهة تنفيذ الأمر"` | عنوان وصفي للموضوع |
| `status` | TEXT | نعم | `"approved"` | حالة دورة حياة الموضوع: draft, reviewed, approved |
| `topic_type` | TEXT | نعم | `"interface"` | نوع الجانب الذي يعالجه الموضوع: interface, validation, workflow, data_model, edge_case |
| `interface_ref` | TEXT | لا | `"execute"` | اسم الواجهة من المواصفة الأصل (interface/validation rule ID) التي يفككها هذا الموضوع |
| `objective` | TEXT | نعم | `"توثيق سلوك واجهة تنفيذ الأمر بشكل تفصيلي"` | الهدف من هذا الموضوع |
| `detailed_spec` | TEXT | نعم | `{"behavior": "ينفذ عملية", "input": {"command_id": "string"}, "output": {"result": "object"}, "preconditions": ["المعاملات صالحة"], "postconditions": ["تم التنفيذ"], "invariants": ["النظام يبقى مستقرا"], "error_handling": [{"condition": "معرف غير موجود", "response": "خطأ 404"}]}` | المواصفة التفصيلية الكاملة — السلوك، المدخلات، المخرجات، الشروط، معالجة الأخطاء |
| `test_scenarios` | TEXT | نعم | `[{"id": "TEST-001", "scenario": "تنفيذ أمر صحيح", "type": "unit", "expected": "يعيد النتيجة بنجاح"}]` | سيناريوهات الاختبار المرتبطة بهذا الموضوع |
| `satisfies_spec_refs` | TEXT | نعم | `["execute", "VC-001"]` | أسماء الواجهات أو معايير التحقق (verify_criteria) من المواصفة الأم التي يلبيها هذا الموضوع |
| `file_touches` | TEXT | لا | `[{"path": "src/module/executor.py", "purpose": "تنفيذ الواجهة", "change_type": "modify"}]` | الملفات المتوقع إنشاؤها أو تعديلها أو حذفها لتنفيذ هذا الموضوع |
| `dependencies` | TEXT | لا | `["TOPIC-002"]` | معرفات المواضيع الأخرى التي يعتمد عليها هذا الموضوع — مرآة لروابط doc_edges من نوع depends_on |
| `xspec_ids` | TEXT | لا | `["XSPEC-001"]` | معرفات المواصفات العرضية المرتبطة — مرآة لروابط doc_edges من نوع references |
| `dst_ids` | TEXT | لا | `["DST-001"]` | معرفات هياكل البيانات المرتبطة — مرآة لروابط doc_edges من نوع uses |
| `version` | TEXT | نعم | `"1.0"` | إصدار الموضوع |
| `tags` | TEXT | نعم | `["execution", "interface"]` | وسوم لتصنيف الموضوع وتصفيفه |
| `created_at` | TEXT | نعم | `"2025-01-01T00:00:00Z"` | طابع زمني للإنشاء |
| `updated_at` | TEXT | نعم | `"2025-01-15T00:00:00Z"` | طابع زمني لآخر تحديث |

## التفكيك عبر واجهات المواصفة (Spec Interfaces Decomposition)

تشكل واجهات المواصفة (`interfaces`) وحقولها الأخرى (`validation_rules`, `edge_cases`) المحرك الأساسي لتوليد مواضيع المواصفات. كل واجهة من نوع `command` أو `query` أو `event` تؤدي إلى إنشاء موضوع من نوع `interface`. وبالمثل، تولد قواعد التحقق مواضيع من نوع `validation`، وتولد حالات الحافة مواضيع من نوع `edge_case`. يحدد حقل `topic_type` الجانب الذي يعالجه الموضوع، بينما يربطه `interface_ref` بالعنصر الأصلي في المواصفة الأم.

## الروابط عبر doc_edges

نظام الربط الأساسي هو جدول `doc_edges`. تربط Spec Topic بالكيانات الأخرى عبر أنواع حواف محددة:

| المصدر | نوع الحافة | الهدف | المعنى |
|--------|-----------|-------|--------|
| `TOPIC-001` | `depends_on` | `TOPIC-002` | موضوع يعتمد على موضوع آخر |
| `TOPIC-001` | `references` | `XSPEC-001` | موضوع يخضع لـ cross-cutting constraint |
| `TOPIC-001` | `uses` | `DST-001` | موضوع يستخدم entity/data structure معين |
| `TOPIC-001` | `decomposes` | `TASK-001` | موضوع يتحلل إلى مهمة تنفيذية (Task) |

### مصدر الحقيقة

`doc_edges` هو مصدر الحقيقة الوحيد للربط. الحقول `dependencies` و `xspec_ids` و `dst_ids` هي **حقول تسهيل (convenience)** — تعكس الروابط الموجودة في `doc_edges` لتسريع الاستعلام دون الحاجة لضم جداول `doc_edges` في كل استعلام. يجب أن تظل متزامنة مع `doc_edges` عبر منطق التطبيق.

### دورة حياة الربط

```
1. إنشاء Spec Topic جديد ← إنشاء edges في doc_edges
2. تحديث `dependencies` / `xspec_ids` / `dst_ids` ← mirror من doc_edges
3. استعلام سريع ← استخدام الـ convenience fields
4. استعلام دقيق (للتحقق) ← استعلام doc_edges مباشرة
```
