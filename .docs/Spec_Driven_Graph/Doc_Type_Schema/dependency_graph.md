# مخطط كيان الرسم البياني للاعتماديات (Dependency Graph Schema)

## تعريف

الرسم البياني للاعتماديات يحدد الاعتماديات الهيكلية أولا. قبل بناء أي شيء، يجب التصريح بما يعتمد عليه. هذا يطبق المبدأ الأساسي: "حدد الاعتماديات قبل المعتمدات."

الرسم البياني للاعتماديات هو العمود الفقري لأي خطة تنفيذ. يمثل هذا الكيان العلاقات بين المواضيع والمكونات والمهام، ويضمن أن الترتيب المنطقي للبناء محدد بدقة قبل البدء في التنفيذ.

## DDL

```sql
CREATE TABLE dependency_graphs (
    id          TEXT PRIMARY KEY,    -- DG-001
    title       TEXT NOT NULL,
    status      TEXT NOT NULL CHECK (status IN ('draft', 'analyzed', 'approved')),
    description TEXT,
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE dependency_nodes (
    id          TEXT PRIMARY KEY,    -- DN-001
    graph_id    TEXT NOT NULL REFERENCES dependency_graphs(id),
    ref_type    TEXT NOT NULL,        -- 'topic' | 'component' | 'task'
    ref_id      TEXT NOT NULL,        -- 'TOPIC-001', 'CMP-001'
    title       TEXT NOT NULL,
    metadata    TEXT,                 -- JSON اختياري: { "estimated_effort": "S|M|L", "owner": "..." }
    UNIQUE(graph_id, ref_type, ref_id)
);

CREATE TABLE dependency_edges (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    graph_id     TEXT NOT NULL REFERENCES dependency_graphs(id),
    source_node  TEXT NOT NULL REFERENCES dependency_nodes(id),
    target_node  TEXT NOT NULL REFERENCES dependency_nodes(id),
    edge_type    TEXT NOT NULL DEFAULT 'depends_on',
                      -- 'depends_on' | 'blocks' | 'triggers'
    metadata     TEXT,                 -- JSON اختياري: { "rationale": "..." }
    UNIQUE(graph_id, source_node, target_node)
);
```

## هيكل الجداول

### جدول `dependency_graphs`

| الحقل | النوع | الوصف |
|-------|------|-------|
| id | TEXT PRIMARY KEY | المعرف الفريد، تنسيق `DG-XXX` (مثال: DG-001) |
| title | TEXT NOT NULL | عنوان الرسم البياني |
| status | TEXT NOT NULL | حالة الرسم البياني: `draft` | `analyzed` | `approved` |
| description | TEXT | وصف الرسم البياني والغرض منه |
| created_at | TEXT NOT NULL | تاريخ الإنشاء، افتراضي `datetime('now')` |
| updated_at | TEXT NOT NULL | تاريخ آخر تحديث، افتراضي `datetime('now')` |

### جدول `dependency_nodes`

| الحقل | النوع | الوصف |
|-------|------|-------|
| id | TEXT PRIMARY KEY | المعرف الفريد، تنسيق `DN-XXX` (مثال: DN-001) |
| graph_id | TEXT NOT NULL | معرف الرسم البياني الأب - مرجع إلى `dependency_graphs(id)` |
| ref_type | TEXT NOT NULL | نوع المرجع: `topic` | `component` | `task` |
| ref_id | TEXT NOT NULL | معرف المرجع: `TOPIC-XXX` أو `CMP-XXX` |
| title | TEXT NOT NULL | عنوان العقدة |
| metadata | TEXT | بيانات إضافية بصيغة JSON (اختياري) |
| _قيد UNIQUE_ | (graph_id, ref_type, ref_id) | يضمن عدم تكرار نفس المرجع داخل نفس الرسم البياني |

### جدول `dependency_edges`

| الحقل | النوع | الوصف |
|-------|------|-------|
| id | INTEGER PRIMARY KEY | معرف تلقائي متزايد |
| graph_id | TEXT NOT NULL | معرف الرسم البياني الأب - مرجع إلى `dependency_graphs(id)` |
| source_node | TEXT NOT NULL | معرف العقدة المصدر - مرجع إلى `dependency_nodes(id)` |
| target_node | TEXT NOT NULL | معرف العقدة الهدف - مرجع إلى `dependency_nodes(id)` |
| edge_type | TEXT NOT NULL | نوع العلاقة: `depends_on` | `blocks` | `triggers` |
| metadata | TEXT | بيانات إضافية بصيغة JSON (اختياري) |
| _قيد UNIQUE_ | (graph_id, source_node, target_node) | يضمن عدم تكرار نفس الحافة داخل نفس الرسم البياني |

## أنواع الحواف (edge_type)

| النوع | المعنى | الوصف |
|-------|--------|-------|
| `depends_on` | يعتمد على | المصدر يعتمد على الهدف - يجب أن يوجد الهدف أولا قبل المصدر. هذا هو النوع الافتراضي. |
| `blocks` | يمنع | المصدر يمنع الهدف - لا يمكن تنفيذ الهدف ما لم يتم حل المصدر. |
| `triggers` | يبدأ بعد | المصدر يبدأ بعد اكتمال الهدف - الهدف يحفز بدء المصدر. |

## ملاحظات مهمة

- `dependency_graphs` هو الحاوية الرئيسية للرسم البياني. يمثل مثيلاً كاملا من مخطط الاعتماديات.
- `dependency_nodes` هي العقد داخل الرسم البياني. يمكن أن تشير إلى مواضيع (`topic`) أو مكونات (`component`) أو مهام (`task`).
- `dependency_edges` تعرف العلاقات بين العقد وتشكل الرسوم البيانية الموجهة غير الدورية (DAG).
- يجب أن يكون الرسم البياني DAG (رسما بيانيا موجها غير دوري). لا يسمح بالتبعيات الدائرية.
- يمكن استخراج الترتيب الطوبولوجي (topological order) من الحواف لتحديد تسلسل البناء الصحيح.
- حقل `metadata` في كل جدول يسمح بإضافة معلومات إضافية دون تغيير هيكل الجدول الأساسي.
