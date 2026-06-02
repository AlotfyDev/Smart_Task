# سجل أنواع الوثائق (Document Registry)

## تعريف

`00-document-registry` هو **سجل مركزي لجميع أنواع الوثائق في النظام**. يوفر مصدر حقيقة واحد (single source of truth) لكل:

- **doc_classes**: أنواع الوثائق المسموحة في النظام
- **doc_statuses**: دورات الحالة المسموحة لكل نوع وثيقة
- **edge_types**: أنواع العلاقات المسموحة بين الوثائق

أي صنف وثيقة جديد يجب أن يُسجل هنا أولاً قبل إنشاء جدول SQL له.

## الفرق بين 00-document-registry و 01-architectural-taxonomy

| البعد | 00-document-registry | 01-architectural-taxonomy |
|-------|---------------------|---------------------------|
| **الطبقة** | Meta layer — عن الوثائق نفسها | Model layer — عن النظام المستهدف |
| **السؤال** | ما أنواع الوثائق الموجودة؟ وما حالاتها وعلاقاتها؟ | ما مكونات النظام؟ وما طبقاته وسياقاته؟ |
| **المحتوى** | doc classes, statuses, edge types | domains, layers, component types, bounded contexts |
| **يُستخدم لـ** | ضبط جودة المستندات، التحقق من صحة المسار | فهم هيكل النظام، توجيه القرارات المعمارية |

## DDL

```sql
-- جدول أنواع الوثائق — السجل الرسمي لكل doc class
CREATE TABLE doc_classes (
    code            TEXT PRIMARY KEY,       -- 'prd', 'architecture', 'spec', ...
    name            TEXT NOT NULL,           -- 'Product Requirements Document'
    prefix          TEXT NOT NULL,           -- 'PRD', 'ARCH', 'SPEC', ...
    description     TEXT NOT NULL,
    chain_order     INTEGER,                -- position in vertical chain (0-based, NULL for cross-cutting)
    parent_code     TEXT REFERENCES doc_classes(code),  -- immediate parent in chain (null for root / cross-cutting)
    is_cross_cutting INTEGER NOT NULL DEFAULT 0 CHECK (is_cross_cutting IN (0, 1)),
    is_mandatory    INTEGER NOT NULL DEFAULT 1,  -- 1 = essential part of chain
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- جدول حالات كل نوع وثيقة — ما هي الحالات المسموحة لكل doc class
CREATE TABLE doc_statuses (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_code        TEXT NOT NULL REFERENCES doc_classes(code),
    status          TEXT NOT NULL,
    sort_order      INTEGER NOT NULL,
    description     TEXT,
    UNIQUE(doc_code, status)
);

-- جدول أنواع الحواف (edge types) — كتالوج العلاقات المسموحة
CREATE TABLE edge_types (
    code            TEXT PRIMARY KEY,       -- 'parent', 'child', 'references', ...
    name            TEXT NOT NULL,
    description     TEXT NOT NULL,
    is_directional  INTEGER NOT NULL DEFAULT 1,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
```

## doc_classes — شرح الحقول

| الحقل | النوع | إلزامي | مثال | الغرض |
|-------|-------|--------|------|-------|
| `code` | TEXT | نعم | `"prd"` | معرف فريد (snake_case) يُستخدم كـ FK في الجداول الأخرى |
| `name` | TEXT | نعم | `"Product Requirements Document"` | الاسم الرسمي الإنجليزي للبشر |
| `prefix` | TEXT | نعم | `"PRD"` | البادئة المستخدمة في معرفات الوثائق (مثل `PRD-001`) |
| `description` | TEXT | نعم | `"..."` | وصف موجز بالعربية |
| `chain_order` | INTEGER | لا | `0` | الموقع في السلسلة الرأسية (0-based). `NULL` للعرضية (cross-cutting) |
| `parent_code` | TEXT | لا | `"prd"` | الأصل المباشر في السلسلة. `NULL` للجذور والعرضية |
| `is_cross_cutting` | INTEGER | لا | `0` | `1` = وثيقة عرضية غير مرتبطة بسلسلة رأسية |
| `is_mandatory` | INTEGER | لا | `1` | `1` = جزء أساسي من السلسلة، لا يمكن تخطيه |

### القيم الافتتاحية (Pre-seeded)

| code | name | prefix | chain_order | parent_code | is_cross_cutting | is_mandatory |
|------|------|--------|-------------|-------------|------------------|--------------|
| `prd` | Product Requirements Document | PRD | 0 | NULL | 0 | 1 |
| `architecture` | Architecture Document | ARCH | 1 | prd | 0 | 1 |
| `spec` | Specification | SPEC | 2 | architecture | 0 | 1 |
| `spec_topic` | Spec Topic | TOPIC | 3 | spec | 0 | 1 |
| `interface` | Interface Contract | INTF | 4 | spec_topic | 0 | 0 |
| `task` | Task | TASK-{SOURCE} | 5 | spec_topic | 0 | 1 |
| `test` | Test | TEST-{CATEGORY} | 6 | task | 0 | 1 |
| `wave` | Wave | WAVE | 7 | task | 0 | 1 |
| `execution_plan` | Execution Plan | EP | 8 | wave | 0 | 1 |
| `audit_report` | Audit Report | AR | 9 | execution_plan | 0 | 1 |
| `adr` | Architecture Decision Record | ADR | NULL | NULL | 1 | 0 |
| `plan` | Technical Plan | PLAN | NULL | NULL | 1 | 0 |
| `constitution` | Constitution | CONST | NULL | NULL | 1 | 0 |
| `cross_cutting_spec` | Cross-Cutting Spec | XSPEC | NULL | NULL | 1 | 0 |
| `data_structure` | Data Structure | DST | NULL | NULL | 1 | 0 |
| `dependency_graph` | Dependency Graph | DG | NULL | NULL | 1 | 0 |

ملاحظات:
- `task.prefix` = `TASK-{SOURCE}` حيث SOURCE رمز المصدر (مثل OPENAI, VECTOR, WEB)
- `test.prefix` = `TEST-{CATEGORY}` حيث CATEGORY رمز فئة الاختبار (CA, GA, AP, RC)
- `interface` هو الوحيد غير الإلزامي (`is_mandatory = 0`) في السلسلة الأساسية لأنه قد لا تحتاج كل Topic إلى Interface

### السلسلة الرأسية الأساسية

```
PRD (0) → ARCH (1) → SPEC (2) → TOPIC (3) → TASK (5) → TEST (6)
                                            → INTF (4)
                                      TASK → WAVE (7) → EP (8) → AR (9)
```

## doc_statuses — حالات الوثائق

| doc_code | status | sort_order | description |
|----------|--------|------------|-------------|
| prd | draft | 1 | مسودة قيد الإنشاء |
| prd | reviewed | 2 | تمت المراجعة |
| prd | approved | 3 | تمت الموافقة |
| prd | superseded | 4 | تم استبداله بإصدار أحدث |
| architecture | draft | 1 | مسودة قيد الإنشاء |
| architecture | reviewed | 2 | تمت المراجعة |
| architecture | approved | 3 | تمت الموافقة |
| architecture | superseded | 4 | تم استبداله بإصدار أحدث |
| spec | draft | 1 | مسودة قيد الإنشاء |
| spec | reviewed | 2 | تمت المراجعة |
| spec | approved | 3 | تمت الموافقة |
| spec | superseded | 4 | تم استبداله بإصدار أحدث |
| spec_topic | draft | 1 | مسودة قيد الإنشاء |
| spec_topic | reviewed | 2 | تمت المراجعة |
| spec_topic | approved | 3 | تمت الموافقة |
| spec_topic | superseded | 4 | تم استبداله بإصدار أحدث |
| interface | draft | 1 | مسودة قيد الإنشاء |
| interface | reviewed | 2 | تمت المراجعة |
| interface | approved | 3 | تمت الموافقة |
| interface | deprecated | 4 | لم يعد صالحًا للاستخدام |
| task | draft | 1 | مسودة قيد الإنشاء |
| task | approved | 2 | تمت الموافقة على المهمة |
| task | in_progress | 3 | قيد التنفيذ |
| task | completed | 4 | تم الإنجاز |
| task | blocked | 5 | محظورة بانتظار معالجة |
| test | draft | 1 | قيد الصياغة — تحديد الفئة والسيناريوهات |
| test | approved | 2 | تمت الموافقة على خطة الاختبار |
| test | executed | 3 | نُفذ الاختبار — capability_matrix ممتلئة |
| test | resolved | 4 | الفجوات عولجت معماريًا أو أُغلقت بقرار |
| test | failed | 5 | فجوات حرجة غير محلولة — يُنتج ADR إجباريًا |
| wave | planned | 1 | مخطط له |
| wave | in_progress | 2 | قيد التنفيذ |
| wave | completed | 3 | تم الإنجاز |
| wave | verified | 4 | تم التحقق |
| execution_plan | draft | 1 | مسودة قيد الإنشاء |
| execution_plan | approved | 2 | تمت الموافقة |
| execution_plan | implemented | 3 | تم التنفيذ |
| execution_plan | verified | 4 | تم التحقق |
| audit_report | pending | 1 | معلق بانتظار البدء |
| audit_report | in_review | 2 | قيد المراجعة |
| audit_report | passed | 3 | اجتاز التدقيق بنجاح |
| audit_report | failed | 4 | فشل في التدقيق |
| adr | proposed | 1 | مقترح قيد المناقشة |
| adr | accepted | 2 | تم قبوله |
| adr | deprecated | 3 | لم يعد صالحًا |
| adr | superseded | 4 | تم استبداله بقرار أحدث |
| plan | draft | 1 | مسودة قيد الإنشاء |
| plan | reviewed | 2 | تمت المراجعة |
| plan | approved | 3 | تمت الموافقة |
| plan | superseded | 4 | تم استبداله |
| constitution | draft | 1 | مسودة قيد الصياغة |
| constitution | ratified | 2 | تم التصديق |
| constitution | amended | 3 | تم التعديل |
| cross_cutting_spec | draft | 1 | مسودة قيد الإنشاء |
| cross_cutting_spec | reviewed | 2 | تمت المراجعة |
| cross_cutting_spec | approved | 3 | تمت الموافقة |
| cross_cutting_spec | deprecated | 4 | لم يعد صالحًا |
| data_structure | draft | 1 | مسودة قيد الإنشاء |
| data_structure | reviewed | 2 | تمت المراجعة |
| data_structure | approved | 3 | تمت الموافقة |
| data_structure | deprecated | 4 | لم يعد صالحًا |
| dependency_graph | draft | 1 | مسودة قيد الإنشاء |
| dependency_graph | reviewed | 2 | تمت المراجعة |
| dependency_graph | approved | 3 | تمت الموافقة |

## edge_types — أنواع الحواف

| code | name | is_directional | description |
|------|------|:--------------:|-------------|
| `parent` | Parent | 1 | عامودي — أب-ابن |
| `child` | Child | 1 | عامودي — ابن-أب (عكسي) |
| `references` | References | 1 | إشارة إلى وثيقة أخرى |
| `informs` | Informs | 1 | وثيقة تزود معلومات لوثيقة أخرى |
| `implements` | Implements | 1 | تنفيذ لوثيقة أخرى |
| `supersedes` | Supersedes | 1 | استبدال وثيقة قديمة بوثيقة أحدث |
| `sibling` | Sibling | 0 | علاقة أفقية بين وثيقتين من نفس المستوى |
| `decomposes` | Decomposes | 1 | تفكيك وثيقة إلى وثائق أصغر |
| `verifies` | Verifies | 1 | اختبار يتحقق من سلوك وثيقة أخرى |
| `triggers` | Triggers | 1 | فجوة تكتشف → تؤدي إلى قرار معماري |
| `informed_by` | Informed By | 1 | تدقيق يسترشد بنتائج اختبار |
| `belongs_to` | Belongs To | 1 | انتماء لمجموعة |

## مصدر الحقيقة

**`doc_classes`** هو السجل الرسمي لكل doc class. أي doc class جديد يجب أن يُسجل هنا أولاً قبل إنشاء جدول SQL له أو إضافة منطق في الكود. لا يُسمح بأي doc class غير مسجل في هذا الجدول.

الدورة لإضافة doc class جديد:
1. يُسجل في `doc_classes` مع `code`، `name`، `prefix`
2. تُسجل حالاته المسموحة في `doc_statuses`
3. يُنشأ جدول SQL إذا لزم الأمر (اختياري للكيانات البسيطة)
4. يُنشأ ملف JSON Schema في `Json_Schema/`
5. يُوثق بالعربية في `Doc_Type_Schema/`
