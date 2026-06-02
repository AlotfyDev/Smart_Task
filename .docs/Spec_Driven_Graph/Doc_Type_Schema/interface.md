# مخطط كيان وثيقة الواجهة (Interface Schema)

## تعريف

يمثل كيان `interface` العقد الرسمي (API / CLI / Event) الذي يحدد كيفية تواصل المكون مع العالم الخارجي. يصف التوقيع (signature) والسلوك (behavior) والشروط المسبقة واللاحقة والثوابت وأكواد الخطأ المتوقعة. الواجهة مستقلة عن موضوع المواصفة (Spec Topic) — فقد يحتوي الموضوع على واجهة أو لا، كما قد توجد واجهات غير مرتبطة بموضوع حاليا.

## DDL

```sql
CREATE TABLE interfaces (
    id              TEXT PRIMARY KEY,        -- INTF-001
    title           TEXT NOT NULL,
    status          TEXT NOT NULL CHECK (status IN ('draft', 'reviewed', 'approved', 'deprecated', 'superseded')),
    kind            TEXT NOT NULL CHECK (kind IN ('rest', 'graphql', 'grpc', 'event', 'cli', 'function')),
    signature       TEXT NOT NULL,            -- JSON: method + path / function sig / request + response shapes
    behavior        TEXT NOT NULL,
    preconditions   TEXT,                     -- JSON: optional
    postconditions  TEXT,                     -- JSON: optional
    invariants      TEXT,                     -- JSON: optional
    error_codes     TEXT NOT NULL,            -- JSON: [{"code":"ERR-001", "http_status":400, "message":"...", "description":"..."}]
    version         TEXT NOT NULL DEFAULT '1.0',
    deprecated_by   TEXT,                     -- optional: INTF-XXX
    example         TEXT,                     -- optional: request/response example
    spec_topic_ids  TEXT,                     -- JSON: convenience -> [TOPIC-001]
    dst_ids         TEXT,                     -- JSON: convenience -> data_structures
    xspec_ids       TEXT,                     -- JSON: convenience -> cross_cutting_specs
    tags            TEXT NOT NULL DEFAULT '[]',
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
```

## شرح الحقول

| الحقل | النوع | إلزامي | مثال JSON | الغرض |
|-------|-------|--------|-----------|-------|
| `id` | TEXT | نعم | `"INTF-001"` | معرف فريد وفق نظام ترقيم الواجهات |
| `title` | TEXT | نعم | `"واجهة تنفيذ الأمر"` | عنوان وصفي للواجهة |
| `status` | TEXT | نعم | `"approved"` | حالة دورة حياة الواجهة: draft, reviewed, approved, deprecated, superseded |
| `kind` | TEXT | نعم | `"rest"` | نوع الواجهة: rest, graphql, grpc, event, cli, function |
| `signature` | TEXT | نعم | `{"method": "POST", "path": "/api/v1/execute", "request": {"body": {"command_id": "string"}}, "response": {"status": 200, "body": {"result": "object"}}}` | توقيع الواجهة — يعتمد على النوع (راجع JSON Schema) |
| `behavior` | TEXT | نعم | `"ينفذ الأمر الوارد ويرجع النتيجة بعد التحقق من الصلاحيات"` | وصف نصي لسلوك الواجهة |
| `preconditions` | TEXT | لا | `[{"condition": "المستخدم مصادق", "description": "يجب أن يكون رمز المصادقة صالحا"}]` | الشروط المسبقة التي يجب توفرها قبل تنفيذ الواجهة |
| `postconditions` | TEXT | لا | `[{"condition": "تم تسجيل العملية", "description": "تسجل عملية التنفيذ في سجل التدقيق"}]` | الشروط اللاحقة التي تضمن بعد التنفيذ |
| `invariants` | TEXT | لا | `[{"expression": "عدد المحاولات <= 3", "description": "لا يتجاوز عدد محاولات التنفيذ ثلاث مرات"}]` | الثوابت التي تبقى صحيحة قبل وبعد التنفيذ |
| `error_codes` | TEXT | نعم | `[{"code": "ERR-001", "http_status": 400, "message": "معامل غير صالح", "description": "أحد المعاملات المطلوبة مفقود أو تنسيقه خاطئ"}]` | أكواد الخطأ التي قد تعيدها الواجهة مع رموز HTTP |
| `version` | TEXT | نعم | `"1.0"` | إصدار الواجهة |
| `deprecated_by` | TEXT | لا | `"INTF-002"` | معرف الواجهة التي حلت محل هذه الواجهة (عند الحذف) |
| `example` | TEXT | لا | `{"request": {"body": {"command_id": "cmd-123"}}, "response": {"body": {"result": {"status": "done"}}}}` | مثال طلب/استجابة للواجهة |
| `spec_topic_ids` | TEXT | لا | `["TOPIC-001"]` | معرفات مواضيع المواصفات المرتبطة — مرآة لروابط doc_edges من نوع defines |
| `dst_ids` | TEXT | لا | `["DST-001"]` | معرفات هياكل البيانات المستخدمة — مرآة لروابط doc_edges من نوع uses |
| `xspec_ids` | TEXT | لا | `["XSPEC-001"]` | معرفات المواصفات العرضية المرجعية — مرآة لروابط doc_edges من نوع references |
| `tags` | TEXT | نعم | `["execution", "core"]` | وسوم لتصنيف الواجهة وتصفيتها |
| `created_at` | TEXT | نعم | `"2025-01-01T00:00:00Z"` | طابع زمني للإنشاء |
| `updated_at` | TEXT | نعم | `"2025-01-15T00:00:00Z"` | طابع زمني لآخر تحديث |

## الروابط عبر doc_edges

| المصدر | نوع الحافة | الهدف | المعنى |
|--------|-----------|-------|--------|
| `INTF-001` | `defines` | `TOPIC-001` | الموضوع الذي يحدد هذه الواجهة (قد يكون صفرا أو أكثر) |
| `INTF-001` | `implements` | `TASK-001` | المهمة التي تنفذ هذا العقد (قد تكون صفرا أو أكثر) |
| `INTF-001` | `references` | `XSPEC-001` | مرجع إلى مواصفة عرضية تنطبق على هذه الواجهة |
| `INTF-001` | `uses` | `DST-001` | هيكل بيانات تستخدمه هذه الواجهة |

### مصدر الحقيقة

`doc_edges` هو مصدر الحقيقة الوحيد للربط. الحقول `spec_topic_ids` و `dst_ids` و `xspec_ids` هي **حقول تسهيل (convenience)** — تعكس الروابط الموجودة في `doc_edges` لتسريع الاستعلام دون الحاجة لضم جداول `doc_edges` في كل استعلام. يجب أن تظل متزامنة مع `doc_edges` عبر منطق التطبيق.

### دورة حياة الربط

```
1. إنشاء Interface جديد ← إنشاء edges في doc_edges
2. تحديث `spec_topic_ids` / `dst_ids` / `xspec_ids` ← mirror من doc_edges
3. استعلام سريع ← استخدام الـ convenience fields
4. استعلام دقيق (للتحقق) ← استعلام doc_edges مباشرة
```
