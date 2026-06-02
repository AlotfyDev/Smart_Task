# مخطط كيان خطة التنفيذ (Plan Schema)

## تعريف

خطة التنفيذ مشتقة من الترتيب الطوبولوجي (Topological Sort) للرسم البياني للاعتماديات. تحدد الخطة ترتيب البناء:

- **المرحلة 1**: العقد ذات الاعتماديات الصفرية (لا تعتمد على أي شيء).
- **المرحلة 2**: العقد التي تعتمد على عناصر المرحلة 1 فقط.
- **المرحلة 3**: العقد التي تعتمد على عناصر المراحل السابقة، وهكذا.

كل مرحلة تبني على ما قبلها، ولا يمكن تجاوز ترتيب المراحل.

## DDL

```sql
CREATE TABLE plans (
    id             TEXT PRIMARY KEY,     -- PLAN-001
    graph_id       TEXT REFERENCES dependency_graphs(id),
    title          TEXT NOT NULL,
    status         TEXT NOT NULL CHECK (status IN ('draft', 'approved')),
    phases         TEXT NOT NULL,         -- JSON: مراحل مرتبة مستخرجة من الترتيب الطوبولوجي لـ DAG
    critical_path  TEXT,                  -- JSON: أطول سلسلة اعتماديات
    tech_stack     TEXT NOT NULL,         -- JSON: [{"technology":"...","version":"...","purpose":"..."}]
    risks          TEXT NOT NULL,         -- JSON: [{"phase":1,"risk":"...","mitigation":"..."}]
    satisfies_refs TEXT NOT NULL,         -- JSON: ["SPEC-001", "TOPIC-001"]
    xspec_ids      TEXT,                  -- JSON: اختصار → cross_cutting_specs
    dst_ids        TEXT,                  -- JSON: اختصار → data_structures
    tags           TEXT NOT NULL DEFAULT '[]',
    version        TEXT NOT NULL DEFAULT '1.0',
    created_at     TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at     TEXT NOT NULL DEFAULT (datetime('now'))
);
```

## هيكل الجدول

| الحقل | النوع | الوصف |
|-------|------|-------|
| id | TEXT PRIMARY KEY | المعرف الفريد، تنسيق `PLAN-XXX` (مثال: PLAN-001) |
| graph_id | TEXT REFERENCES | معرف الرسم البياني للاعتماديات المصدر (اختياري) |
| title | TEXT NOT NULL | عنوان خطة التنفيذ |
| status | TEXT NOT NULL | حالة الخطة: `draft` | `approved` |
| phases | TEXT NOT NULL | JSON يمثل المراحل مرتبة حسب الترتيب الطوبولوجي |
| critical_path | TEXT | JSON لأطول سلسلة اعتماديات (اختياري) |
| tech_stack | TEXT NOT NULL | JSON لقائمة التقنيات المستخدمة |
| risks | TEXT NOT NULL | JSON لقائمة المخاطر والتخفيف منها |
| satisfies_refs | TEXT NOT NULL | JSON لقائمة المراجع التي تلبيها الخطة (SPEC, TOPIC) |
| xspec_ids | TEXT | JSON لقائمة معرفات المواصفات العرضية (اختياري) |
| dst_ids | TEXT | JSON لقائمة معرفات هياكل البيانات (اختياري) |
| tags | TEXT NOT NULL | JSON لوسوم الخطة، افتراضي `[]` |
| version | TEXT NOT NULL | إصدار الخطة، افتراضي `1.0` |
| created_at | TEXT NOT NULL | تاريخ الإنشاء، افتراضي `datetime('now')` |
| updated_at | TEXT NOT NULL | تاريخ آخر تحديث، افتراضي `datetime('now')` |

## مبدأ الاعتماديات أولا

- **المراحل يجب أن تحترم الترتيب الطوبولوجي للـ DAG**. لا يمكن بناء عقدة في مرحلة متقدمة إذا كانت تعتمد على عقدة في مرحلة لاحقة.
- **المسار الحرج (Critical Path)** يمثل أطول سلسلة اعتماديات ويحدد أقل مدة زمنية ممكنة لإنجاز الخطة.
- **كل مرحلة** تحتوي على مجموعة من العقد (`node_ids`) التي يمكن بناؤها بالتوازي لأنها لا تعتمد على بعضها البعض.

## علاقات الوثائق

```
PLAN ──[implements]──→ SPEC / TOPIC
PLAN ──[precedes]────→ EXECUTION_PLAN
PLAN ──[references]──→ XSPEC
PLAN ──[uses]────────→ DST
```

| العلاقة | الشرح |
|---------|-------|
| PLAN ──[implements]──→ SPEC / TOPIC | الخطة تنفذ المواصفات والمواضيع المحددة |
| PLAN ──[precedes]────→ EXECUTION_PLAN | الخطة تسبق خطة التنفيذ التفصيلية |
| PLAN ──[references]──→ XSPEC | الخطة تشير إلى المواصفات العرضية |
| PLAN ──[uses]────────→ DST | الخطة تستخدم هياكل البيانات المحددة |
