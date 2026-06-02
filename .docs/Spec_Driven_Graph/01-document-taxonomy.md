# نظام تصنيف الوثائق

## جدول `doc_types` (مفهومي)

```sql
CREATE TABLE doc_types (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    code        TEXT    UNIQUE NOT NULL,  -- 'prd', 'architecture', 'spec', 'spec_topic', 'interface', 'task', 'wave', 'adr', 'plan', 'execution_plan', 'audit_report', 'constitution'
    name        TEXT    NOT NULL,
    prefix      TEXT    NOT NULL,          -- 'PRD', 'ARCH', 'SPEC', 'TOPIC', 'INTF', 'TASK', 'WAVE', 'ADR', 'PLAN', 'EP', 'AR', 'CONST'
    description TEXT    NOT NULL
);
```

## البادئات وأنواع المعرفات

| النوع | البادئة | مثال | ملاحظات |
|-------|---------|-------|---------|
| PRD | PRD- | PRD-001 | الترقيم تسلسلي مستقل |
| Architecture | ARCH- | ARCH-001 | الترقيم تسلسلي مستقل |
| Spec | SPEC- | SPEC-001 | الترقيم تسلسلي مستقل |
| Spec Topic | TOPIC- | TOPIC-001 | الترقيم تسلسلي مستقل |
| Interface | INTF- | INTF-001 | الترقيم تسلسلي مستقل |
| Task | TASK-XX- | TASK-OPENAI-001 | يحمل رمز المصدر (مثل OPENAI, VECTOR) |
| Wave | WAVE- | WAVE-001 | الترقيم تسلسلي مستقل |
| ADR | ADR- | ADR-001 | الترقيم تسلسلي مستقل |
| Plan | PLAN- | PLAN-001 | الترقيم تسلسلي مستقل |
| Execution Plan | EP- | EP-001 | الترقيم تسلسلي مستقل |
| Test | TEST-XX- | TEST-CA-001 | يحمل رمز الفئة: CA (capability_audit), GA (gap_analysis), AP (architectural_property), RC (root_cause_regression) |
| Audit Report | AR- | AR-001 | الترقيم تسلسلي مستقل |
| Constitution | CONST- | CONST-001 | عادة ما يكون مستندًا واحدًا أو عدد محدود |

ملاحظة: بالنسبة للمهام، التنسيق هو `TASK-{SOURCE}-{NNN}` حيث SOURCE هو رمز يمثل مصدر المهمة (مثل OPENAI, VECTOR, WEB).
ملاحظة: بالنسبة للاختبارات، التنسيق هو `TEST-{CATEGORY}-{NNN}` حيث CATEGORY هو رمز يمثل فئة الاختبار (CA = capability_audit, GA = gap_analysis, AP = architectural_property, RC = root_cause_regression).

## `adr_classifications` — تصنيفات ADR

```sql
CREATE TABLE adr_classifications (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    code        TEXT    UNIQUE NOT NULL,
    name        TEXT    NOT NULL,
    description TEXT    NOT NULL
);

INSERT INTO adr_classifications (code, name, description) VALUES
    ('technology-choice',     'اختيار تقنية',       'قرار يتعلق باختيار إطار عمل، مكتبة، أو تقنية معينة'),
    ('architecture-change',   'تغيير معماري',        'قرار يتغير بهيكل النظام أو توزيع المكونات'),
    ('interface-design',      'تصميم واجهة',         'قرار يتعلق بتصميم API أو واجهات التبادل'),
    ('process-decision',      'قرار إجرائي',         'قرار يتعلق بعمليات التطوير أو سير العمل'),
    ('data-model',            'نموذج بيانات',        'قرار يتعلق بهيكلة البيانات وقواعد البيانات'),
    ('security',              'أمان',                'قرار يتعلق بالسياسات الأمنية والمصادقة'),
    ('deployment',            'نشر',                 'قرار يتعلق ببيئة النشر والاستضافة'),
    ('dependency',            'اعتماد خارجي',        'قرار يتعلق باعتماد مكتبة أو خدمة خارجية');
```

## دورات الحالة (Status Lifecycle)

### لمستندات السلسلة الأساسية (PRD, ARCH, SPEC, TOPIC, INTF, TASK, PLAN, EP)

```sql
CREATE TABLE doc_statuses (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_type    TEXT    NOT NULL,   -- نوع المستند
    status      TEXT    NOT NULL,   -- حالة المستند
    sort_order  INTEGER NOT NULL    -- ترتيب الحالة في الدورة
);

-- الحالات الشائعة:
-- 'draft'      — مسودة قيد الإنشاء
-- 'reviewed'   — تمت المراجعة
-- 'approved'   — تمت الموافقة
-- 'implemented'— تم التنفيذ (للمهام والموجات)
-- 'verified'   — تم التحقق (لتقارير التدقيق)
```

### لـ ADR

```
proposed → accepted
        → deprecated
        → superseded
```

- `proposed`: مقترح قيد المناقشة
- `accepted`: تم قبوله
- `deprecated`: لم يعد صالحًا
- `superseded`: تم استبداله بقرار أحدث

### للموجات (Waves)

```
planned → in_progress → completed → verified
```

### لتقارير التدقيق (Audit Reports)

```
pending → in_review → passed → failed
```

### للاختبارات (Tests)

```
draft → approved → executed → resolved
                              → failed (يُنتج ADR إجباريًا)
```

- `draft`: قيد الصياغة — تحديد الفئة، expected capabilities، السيناريوهات
- `approved`: تمت الموافقة على خطة الاختبار
- `executed`: نُفذ الاختبار — capability_matrix ممتلئة
- `resolved`: الفجوات عولجت معماريًا أو أُغلقت بقرار
- `failed`: فجوات حرجة غير محلولة — يُنتج ADR إجباريًا لحجب Task
