# مخطط كيان وثيقة المواصفات (Spec Schema)

## تعريف

يمثل كيان `spec` مواصفات سلوك أحد مكونات النظام. يرتبط هذا الكيان بأصل واحد من نوع `architecture_doc` (الوالد) ويُستخدم كمدخل رئيسي لتوليد سلسلة مواضيع المواصفات (Spec Topic chain). كما يرتبط بكيانات فرعية من نوع `cross_cutting_spec` و `data_structure` عبر روابط وثائقية (doc_edges) تنعكس في حقول `xspec_ids` و `dst_ids` للوصول السريع دون الحاجة لاستعلام الروابط.

## DDL

```sql
CREATE TABLE specs (
    id               TEXT PRIMARY KEY,      -- SPEC-001
    arch_id          TEXT NOT NULL REFERENCES architecture_docs(id),
    title            TEXT NOT NULL,
    status           TEXT NOT NULL CHECK (status IN ('draft', 'reviewed', 'approved', 'superseded')),
    version          TEXT NOT NULL DEFAULT '1.0',
    tags             TEXT NOT NULL DEFAULT '[]',
    scope            TEXT NOT NULL,          -- JSON: {"in_scope": ["..."], "out_of_scope": ["..."]}
    interfaces       TEXT NOT NULL,          -- JSON: [{"name":"...", "kind":"command|query|event", "behavior":"...", "preconditions":["..."], "postconditions":["..."]}] ← decomposition driver → Spec Topic
    validation_rules TEXT NOT NULL,          -- JSON: [{"field":"...", "rule":"...", "error_message":"..."}]
    edge_cases       TEXT NOT NULL,          -- JSON: [{"id":"EC-001", "scenario":"...", "expected":"..."}]
    verify_criteria  TEXT NOT NULL,          -- JSON: [{"id":"VC-001", "criterion":"...", "type":"unit|integration|e2e"}]
    state_transitions TEXT,                  -- JSON: optional — [{"from":"pending","to":"approved","trigger":"..."}]
    compatibility    TEXT,                   -- JSON: optional — [{"concern":"...", "requirement":"..."}]
    satisfies_req    TEXT NOT NULL,          -- JSON: ["FR-001", "NFR-002"]
    xspec_ids        TEXT,                   -- JSON: optional convenience — ["XSPEC-001", "XSPEC-002"]
    dst_ids          TEXT,                   -- JSON: optional convenience — ["DST-001", "DST-002"]
    created_at       TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at       TEXT NOT NULL DEFAULT (datetime('now'))
);
```

## شرح الحقول

| الحقل | النوع | إلزامي | مثال JSON | الغرض |
|-------|-------|--------|-----------|-------|
| `id` | TEXT | نعم | `"SPEC-001"` | معرف فريد وفق نظام ترقيم المواصفات |
| `arch_id` | TEXT | نعم | `"ARCH-001"` | معرف وثيقة العمارة الأصل (الوالد) |
| `title` | TEXT | نعم | `"مواصفة محرك التنفيذ"` | عنوان وصفي للمواصفة |
| `status` | TEXT | نعم | `"approved"` | حالة دورة حياة المواصفة: draft, reviewed, approved, superseded |
| `version` | TEXT | نعم | `"1.0"` | إصدار المواصفة |
| `tags` | TEXT | نعم | `["execution", "core"]` | وسوم لتصنيف المواصفة وتصفيتها |
| `scope` | TEXT | نعم | `{"in_scope": ["تنفيذ الأوامر"], "out_of_scope": ["إدارة الجلسات"]}` | نطاق المواصفة (ما يدخل وما يخرج) |
| `interfaces` | TEXT | نعم | `[{"name": "execute", "kind": "command", "behavior": "ينفذ عملية", "preconditions": ["المعاملات صالحة"], "postconditions": ["تم التنفيذ"]}]` | تعريف واجهات المكون — المحرك الرئيسي لتوليد سلسلة مواضيع المواصفات (Spec Topic chain) |
| `validation_rules` | TEXT | نعم | `[{"field": "command_id", "rule": "يجب ألا يكون فارغا", "error_message": "معرف الأمر مطلوب"}]` | قواعد التحقق من صحة البيانات |
| `edge_cases` | TEXT | نعم | `[{"id": "EC-001", "scenario": "قيمة فارغة", "expected": "خطأ في التحقق"}]` | حالات الحافة والنادر حدوثها مع النتائج المتوقعة |
| `verify_criteria` | TEXT | نعم | `[{"id": "VC-001", "criterion": "يعيد النتيجة الصحيحة", "type": "unit"}]` | معايير التحقق والاختبار مع نوع الاختبار |
| `state_transitions` | TEXT | لا | `[{"from": "draft", "to": "reviewed", "trigger": "مراجعة مكتملة"}]` | انتقالات الحالة المسموحة (اختياري) |
| `compatibility` | TEXT | لا | `[{"concern": "توافقية الإصدارات", "requirement": "يدعم v2"}]` | متطلبات التوافقية (اختياري) |
| `satisfies_req` | TEXT | نعم | `["FR-001", "NFR-002"]` | قائمة بمتطلبات النظام (FR/NFR) التي تلبيها هذه المواصفة |
| `xspec_ids` | TEXT | لا | `["XSPEC-001", "XSPEC-002"]` | معرّفات المواصفات العرضية (cross-cutting specs) المرتبطة — مرآة لروابط doc_edges للوصول السريع |
| `dst_ids` | TEXT | لا | `["DST-001", "DST-002"]` | معرّفات هياكل البيانات (data structures) المرتبطة — مرآة لروابط doc_edges للوصول السريع |
| `created_at` | TEXT | نعم | `"2025-01-01T00:00:00Z"` | طابع زمني للإنشاء |
| `updated_at` | TEXT | نعم | `"2025-01-15T00:00:00Z"` | طابع زمني لآخر تحديث |

## التفكيك عبر واجهات (Interfaces Decomposition)

حقل `interfaces` هو المحرك الأساسي لتوليد سلسلة مواضيع المواصفات (Spec Topic chain). كل واجهة معرفة في هذا الحقل — من نوع `command` أو `query` أو `event` — تؤدي إلى إنشاء موضوع مواصفة فرعي (Spec Topic) يصف سلوك تلك الواجهة بالتفصيل، بما يشمل الشروط المسبقة (preconditions)، الشروط اللاحقة (postconditions)، والأخطاء المحتملة. يضمن هذا النهج تفكيكا منهجيا كاملا لكل واجهة.

## الروابط عبر doc_edges

نظام الربط الأساسي هو جدول `doc_edges`. تربط Spec بالكيانات الأخرى عبر أنواع حواف محددة:

| المصدر | نوع الحافة | الهدف | المعنى |
|--------|-----------|-------|--------|
| `SPEC-001` | `references` | `XSPEC-001` | Spec يخضع لـ cross-cutting constraint |
| `SPEC-001` | `uses` | `DST-001` | Spec يستخدم entity/data structure معين |
| `SPEC-001` | `satisfies` | `FR-001` | Spec يحقق functional requirement معين |
| `SPEC-001` | `parent` | `TOPIC-001` | Spec يتحلل إلى Spec Topic |

### مصدر الحقيقة

`doc_edges` هو مصدر الحقيقة الوحيد للربط. الحقلان `xspec_ids` و `dst_ids` هما **حقلَا تسهيل (convenience)** — يعكسان الروابط الموجودة في `doc_edges` لتسريع الاستعلام دون الحاجة لضم جداول `doc_edges` في كل استعلام. يجب أن يظلا متزامنين مع `doc_edges` عبر منطق التطبيق.

### دورة حياة الربط

```
1. إنشاء Spec جديد ← إنشاء edges في doc_edges
2. تحديث `xspec_ids` / `dst_ids` ← mirror من doc_edges
3. استعلام سريع ← استخدام الـ convenience fields
4. استعلام دقيق (للتحقق) ← استعلام doc_edges مباشرة
```
