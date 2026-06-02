# Spec Topic — تفكيك المواصفات (Topic Decomposition)

## الغرض

تفكيك مواصفات (Spec) إلى **اهتمامات أصغر مركزة** (focused concerns) — لضمان التغطية الشاملة مع الحفاظ على التخصص.  
يمثل كل Topic جانبًا واحدًا قابلاً للفهم من المواصفات، ويمكن أن ينتج عنه مهمة واحدة أو أكثر.

## المخطط (DDL)

```sql
CREATE TABLE spec_topics (
    id                 TEXT    PRIMARY KEY,                -- TOPIC-001
    spec_id            INTEGER NOT NULL REFERENCES specs(id),
    title              TEXT    NOT NULL,
    objective          TEXT    NOT NULL,                   -- الهدف من هذا الموضوع
    aspect_focus       TEXT    NOT NULL,                   -- الجانب الذي يركز عليه (JSON أو نص)
    acceptance_criteria TEXT,                              -- معايير قبول خاصة بالموضوع
    dependencies       TEXT,                               -- تبعيات على Topics أخرى (JSON array)
    status             TEXT    NOT NULL DEFAULT 'draft',   -- draft / reviewed / approved
    version            INTEGER NOT NULL DEFAULT 1,
    tags               TEXT,
    created_at         TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at         TEXT    NOT NULL DEFAULT (datetime('now'))
);
```

## علاقة الوالد

- **الوالد**: specs(id) — كل Topic ينتمي إلى Spec واحد.
- **الأبناء المباشرون**: interfaces (عبر FK: `interfaces.topic_id`) و micro_task_tickets (عبر FK: `micro_task_tickets.topic_id`)
- **المفتاح الخارجي**: `spec_id REFERENCES specs(id)`

## مثال

```sql
INSERT INTO spec_topics (id, spec_id, title, objective, aspect_focus)
VALUES (
    'TOPIC-001',
    'SPEC-001',
    'تنفيذ أمر الشراء',
    'تغطية منطق تنفيذ أمر الشراء من الاستلام إلى التأكيد',
    '{"component": "محرر التنفيذ", "flow": "شراء", "priority": "عالية"}'
);

INSERT INTO spec_topics (id, spec_id, title, objective, aspect_focus)
VALUES (
    'TOPIC-002',
    'SPEC-001',
    'تسجيل الصفقات في قاعدة البيانات',
    'تغطية كتابة سجلات الصفقات وضمان الاتساق',
    '{"component": "قاعدة البيانات", "flow": "تسجيل", "priority": "عالية"}'
);
```

## الاستخدام في سير العمل الوكيل

1. **وكيل التفكيك** (Decomposition Agent) يستلم SPEC-ID ويقسمه إلى Topics.
2. كل Topic ينتج عنه **مهمة واحدة أو أكثر** (Tasks) يتم إنشاؤها بواسطة وكيل المهام.
3. Topics مرتبطة ببعضها عبر doc_edges بنوع `sibling` لتمثيل العلاقات الأفقية.
4. يتم ربط dependencies بين Topics لتحديد ترتيب التنفيذ.
5. **وكيل الواجهات** (Interface Agent) يستخرج عقود API من Topics المختارة.
