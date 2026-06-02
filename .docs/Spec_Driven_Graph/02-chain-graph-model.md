# النموذج البياني المختلط — Hybrid FK + Edges Model

## المبررات

اختيار النموذج المختلط يأتي من الحاجة إلى تحقيق هدفين متكاملين:

1. **التكامل المرجعي** (Referential Integrity) — ضمان أن كل وثيقة تابعة تشير إلى والد موجود فعلاً في قاعدة البيانات.
2. **المرونة البيانية** (Graph Flexibility) — القدرة على إنشاء أي علاقة بين أي وثيقتين دون التقيد بهيكل هرمي صارم.

## السلاسل الرأسية (Vertical Chain) — المفاتيح الخارجية المباشرة

تمتلك كل وثيقة مفتاحًا خارجيًا (FK) يشير إلى والدها المباشر في السلسلة:

```sql
-- PRD → Architecture
ALTER TABLE architecture_docs ADD COLUMN prd_id INTEGER REFERENCES prds(id);

-- Architecture → Spec
ALTER TABLE specs ADD COLUMN arch_id INTEGER REFERENCES architecture_docs(id);

-- Spec → Spec Topic
ALTER TABLE spec_topics ADD COLUMN spec_id INTEGER REFERENCES specs(id);

-- Spec Topic → Interface
ALTER TABLE interfaces ADD COLUMN topic_id INTEGER REFERENCES spec_topics(id);

-- Spec Topic → Task
ALTER TABLE micro_task_tickets ADD COLUMN topic_id INTEGER REFERENCES spec_topics(id);

-- Task → Test
ALTER TABLE tests ADD COLUMN task_id INTEGER REFERENCES micro_task_tickets(id);

-- Wave → Execution Plan
ALTER TABLE execution_plans ADD COLUMN wave_id INTEGER REFERENCES task_waves(id);

-- Execution Plan → Audit Report
ALTER TABLE audit_reports ADD COLUMN ep_id INTEGER REFERENCES execution_plans(id);

-- Plan → Execution Plan
ALTER TABLE execution_plans ADD COLUMN plan_id INTEGER REFERENCES plans(id);

-- Execution Plan → Task
ALTER TABLE audit_reports ADD COLUMN task_id INTEGER REFERENCES micro_task_tickets(id);
```

### استثناء ADR

جدول ADR لا يحتوي على FK تقليدي، بل يستخدم حقل `target_id` نصي:

```sql
ALTER TABLE adrs ADD COLUMN target_id TEXT;
```

السبب: ADR يمكن أن يشير إلى أي نوع من الوثائق (PRD, ARCH, SPEC, TOPIC, INTF, TASK, etc.)، وفرض FK واحد لا يخدم هذه المرونة.

## جدول الحواف البيانية (doc_edges)

```sql
CREATE TABLE doc_edges (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    source_type TEXT    NOT NULL,   -- نوع المصدر: 'prd', 'architecture', 'spec', 'spec_topic', 'interface', 'task', 'test', 'wave', 'adr', 'plan', 'execution_plan', 'audit_report', 'constitution'
    source_id   TEXT    NOT NULL,   -- معرف المصدر (PRD-001, ARCH-001, ...)
    target_type TEXT    NOT NULL,   -- نوع الهدف
    target_id   TEXT    NOT NULL,   -- معرف الهدف
    edge_type   TEXT    NOT NULL,   -- نوع العلاقة
    metadata    TEXT,               -- JSON optional: خصائص إضافية للعلاقة
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE(source_type, source_id, target_type, target_id, edge_type)
);

CREATE INDEX idx_doc_edges_source ON doc_edges(source_type, source_id);
CREATE INDEX idx_doc_edges_target ON doc_edges(target_type, target_id);
CREATE INDEX idx_doc_edges_type   ON doc_edges(edge_type);
```

### أنواع العلاقات (edge_type)

| النوع | المعنى | مثال |
|-------|--------|------|
| `parent` | علاقة أب-ابن مباشرة في السلسلة | PRD-001 → ARCH-001 |
| `child` | علاقة ابن-أب عكسية | ARCH-001 → PRD-001 |
| `references` | إشارة إلى وثيقة أخرى | ADR-001 → SPEC-001 |
| `informs` | وثيقة تزود معلومات لوثيقة أخرى | ARCH-001 → ADR-002 |
| `implements` | تنفيذ لوثيقة أخرى | TASK-OPENAI-001 → TOPIC-001 |
| `supersedes` | استبدال وثيقة قديمة بوثيقة أحدث | ADR-003 → ADR-001 |
| `sibling` | علاقة أفقية بين وثيقتين من نفس المستوى | TOPIC-001 → TOPIC-002 |
| `decomposes` | تفكيك وثيقة إلى وثائق أصغر | SPEC-001 → TOPIC-001 |
| `verifies` | اختبار يتحقق من سلوك وثيقة أخرى | TEST-CA-001 → INTF-001 |
| `triggers` | فجوة تكتشف → تؤدي إلى قرار أو إجراء جديد | TEST-GA-001 → ADR-002 |
| `informed_by` | تدقيق يسترشد بنتائج اختبار | AR-001 → TEST-CA-001 |

## لماذا النموذج المختلط؟

### المزايا

| الميزة | FK المباشر | doc_edges |
|--------|-----------|-----------|
| التكامل المرجعي | نعم (Cascade / Restrict) | لا (تطبيق على مستوى التطبيق) |
| سرعة الاستعلامات الهرمية | عالية (JOIN مباشر) | متوسطة (مسارات متعددة) |
| مرونة العلاقات | منخفضة (هرمية فقط) | عالية (أي علاقة) |
| سهولة التصحيح | عالية (FK violation يظهر فوراً) | منخفضة (أخطاء منطقية) |
| دعم العلاقات المتعددة | لا | نعم |
| التوافق مع SQLite | ممتاز | ممتاز |

### سيناريوهات الاستخدام

1. **السير الهرمي الأساسي**: استخدم FK المباشر (مثلاً: جلب كل المواصفات لمعمارية معينة).
2. **الاستعلامات البيانية العامة**: استخدم doc_edges (مثلاً: كل الوثائق التي تشير إليها وثيقة ADR).
3. **العلاقات الأفقية**: استخدم doc_edges حصراً (مثلاً: العلاقات بين مواضيع المواصفات).
4. **التتبع عبر السلسلة**: استخدم FK في JOINs متسلسلة (مثلاً: PRD → ARCH → SPEC → TOPIC → TASK).
