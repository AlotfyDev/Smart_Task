# Task + Wave — المهام والموجات (Existing Entities)

## نظرة عامة

تمثل **MicroTaskTicket** و **TaskWave** الكيانين الموجودين فعلاً في قاعدة بيانات SQLite لمشروع Smart Task.  
يتم الآن دمجهما في التصنيف البياني الكامل مع إضافة المفتاح الخارجي `topic_id` لربط المهام بـ Spec Topics.

---

## MicroTaskTicket (تذكرة المهمة)

### الغرض

مهمة قابلة للتنفيذ مشتقة من موضوع مواصفات (Spec Topic). تمثل وحدة العمل الأدنى التي يمكن تخصيصها لوكيل فرعي.

### المخطط (DDL)

```sql
CREATE TABLE micro_task_tickets (
    id                    TEXT    PRIMARY KEY,                -- TASK-OPENAI-001
    topic_id              INTEGER REFERENCES spec_topics(id), -- FK جديد → Spec Topics
    source_spec           TEXT    NOT NULL,                   -- مصدر المهمة (OPENAI, VECTOR, etc.)
    title                 TEXT    NOT NULL,
    objective             TEXT    NOT NULL,                   -- الهدف من المهمة
    item_type             TEXT    NOT NULL DEFAULT 'task',     -- task / bug / chore
    dependencies          TEXT,                               -- تبعيات على مهام أخرى (JSON array)
    acceptance_criteria   TEXT,                               -- معايير القبول (JSON array)
    verification_method   TEXT,                               -- طريقة التحقق (JSON: type, tool, instructions)
    priority              TEXT    NOT NULL DEFAULT 'medium',   -- critical / high / medium / low
    effort                TEXT,                               -- الجهد التقديري (hours)
    status                TEXT    NOT NULL DEFAULT 'pending',  -- pending / in_progress / completed / failed / blocked
    verification_status   TEXT    DEFAULT 'unverified',        -- unverified / verified / failed
    result_summary        TEXT,                               -- ملخص النتائج بعد التنفيذ
    assigned_agent        TEXT,                               -- الوكيل المسند إليه المهمة
    tags                  TEXT,
    wave_id               INTEGER REFERENCES task_waves(id),  -- الموجة التابعة لها
    created_at            TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at            TEXT    NOT NULL DEFAULT (datetime('now'))
);
```

### علاقة الوالد

- **الوالد المباشر**: spec_topics(id) عبر `topic_id` (FK جديد تمت إضافته).
- **الوالد الآخر**: task_waves(id) عبر `wave_id` (موجود مسبقًا).
- **الأبناء**: audit_reports (عبر FK: `audit_reports.task_id`).

### مثال

```sql
INSERT INTO micro_task_tickets (id, topic_id, source_spec, title, objective, acceptance_criteria, priority)
VALUES (
    'TASK-OPENAI-001',
    'TOPIC-001',
    'OPENAI',
    'تنفيذ منطق أمر الشراء',
    'تطبيق وحدة تنفيذ أمر الشراء وفق مواصفات TOPIC-001',
    '["يجب إنشاء API endpoint POST /orders/buy", "يجب التحقق من الرصيد قبل التنفيذ"]',
    'high'
);
```

---

## TaskWave (موجة المهام)

### الغرض

مجموعة من المهام تُنفذ معًا في مرحلة واحدة. تمثل دورة تنفيذ كاملة ضمن سباق (sprint) أو مرحلة تطوير.

### المخطط (DDL)

```sql
CREATE TABLE task_waves (
    id            TEXT    PRIMARY KEY,                -- WAVE-001
    phase         INTEGER NOT NULL,                   -- رقم المرحلة
    title         TEXT    NOT NULL,
    description   TEXT,
    ticket_count  INTEGER DEFAULT 0,                  -- عدد المهام في الموجة
    status        TEXT    NOT NULL DEFAULT 'planned', -- planned / in_progress / completed / verified
    started_at    TEXT,
    completed_at  TEXT,
    notes         TEXT,
    created_at    TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at    TEXT    NOT NULL DEFAULT (datetime('now'))
);
```

### علاقة الوالد

- **الوالد**: ليس لها والد مباشر عبر FK (يمكن ربطها بـ PRD عبر doc_edges).
- **الأبناء**: micro_task_tickets (عبر FK: `micro_task_tickets.wave_id`)، execution_plans (عبر FK: `execution_plans.wave_id`).

### مثال

```sql
INSERT INTO task_waves (id, phase, title, description, ticket_count, status)
VALUES (
    'WAVE-001',
    1,
    'الموجة الأولى: البنية التحتية للتداول',
    'تنفيذ البنية التحتية الأساسية لنظام التداول — API، قاعدة البيانات، محرك التنفيذ',
    3,
    'in_progress'
);
```

---

## كيفية ارتباط Task و Wave في التصنيف الجديد

```
Spec
 └── Spec Topic (TOPIC-001)
      ├── Task (TASK-OPENAI-001) ──────────┐
      ├── Task (TASK-OPENAI-002) ──────────┤
      └── Interface (INTF-001)             │
                                           │
                                    Wave (WAVE-001)
                                           │
                                    Execution Plan (EP-001)
                                           │
                                    Audit Reports (AR-001, AR-002)
```

### التغييرات المطلوبة على الجداول الموجودة

1. إضافة `topic_id` إلى `micro_task_tickets` كـ FK يشير إلى `spec_topics(id)`.
2. إضافة `wave_id` إلى `micro_task_tickets` (موجود مسبقًا — تأكيد).
3. ملء جدول `doc_edges` بالعلاقات بين Task و Topic (type: `parent`)، وبين Task و Wave (type: `child`).
