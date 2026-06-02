# Spec-Driven Graph — تصنيف وثائق Smart Task

## نظرة عامة

**Smart Task** هو نظام تذاكر مهام مصغرة لتنسيق التطوير الموجّه بالمواصفات (Spec-Driven Development).  
يمثل هذا الدليل **النموذج البياني للوثائق** (Document Graph Model) الذي يغطي سلسلة التوثيق الكاملة من المنتج إلى التنفيذ والتدقيق.

## فئات الوثائق

| الفئة | البادئة | التعريف |
|-------|----------|----------|
| **PRD** (Product Requirements Document) | PRD-NNN | جذر السلسلة — رؤية الأعمال، الأهداف، احتياجات المستخدم |
| **Architecture** (وثيقة النظام المعماري) | ARCH-NNN | التصميم عالي المستوى، المكونات، العلاقات، القيود |
| **Spec** (مواصفات السلوك) | SPEC-NNN | مواصفات السلوك التفصيلية، قصص المستخدم، معايير القبول |
| **Spec Topic** (تفكيك المواصفات) | TOPIC-NNN | تفكيك المواصفات إلى اهتمامات أصغر مركزة |
| **Interface** (عقود API) | INTF-NNN | العقود الرسمية، endpoints، مخططات الطلب/الاستجابة |
| **Task** (تذكرة مهمة) | TASK-XX-NNN | مهمة قابلة للتنفيذ مشتقة من موضوع المواصفات |
| **Test** (تحليل كفاءات معماري) | TEST-XX-NNN | كشف الفجوات المنطقية والضعف الوظيفي — إلزامي لإكمال Task |
| **Wave** (موجة مهام) | WAVE-NNN | مجموعة من المهام تُنفذ معًا في مرحلة واحدة |
| **ADR** (سجل القرارات المعمارية) | ADR-NNN | توثيق القرارات المعمارية مع السياق والنتائج |
| **Plan** (خطة التصميم التقني) | PLAN-NNN | خطة التنفيذ المشتقة من المواصفات |
| **Execution Plan** (استراتيجية المنسق) | EP-NNN | استراتيجية تنفيذ المنسّق — ترتيب المهام، المجموعات المتوازية |
| **Audit Report** (تقرير التدقيق) | AR-NNN | نتائج التحقق بعد تنفيذ الوكيل الفرعي |
| **Constitution** (الدستور) | CONST-NNN | القواعد الثابتة والاتفاقيات الخاصة بالمشروع |

## التسلسل الهرمي للسلسلة

```
PRD
 └── Architecture
      └── Spec
           └── Spec Topic
                ├── Interface
                └── Task
                     ├── Test (capability_audit — إلزامي)
                     │    ├── Test (gap_analysis)
                     │    ├── Test (architectural_property)
                     │    └── Test (root_cause_regression)
                     └── Wave
                          └── Execution Plan
                               └── Audit Report
```

## نموذج البيان المختلط (Hybrid Graph Model)

يجمع النموذج بين نهجين:

1. **المفتاح الخارجي المباشر (Direct FK)** — كل جدول يحتوي على FK يشير إلى parent المباشر في السلسلة لضمان التكامل المرجعي.
2. **جدول الحواف (doc_edges)** — جدول تجاور عام يدعم أي علاقة بيانية (رأسية + أفقية).

### مصفوفة الحواف (doc_edges)

| المصدر | العلاقات الممكنة |
|--------|-------------------|
| PRD | parent → Architecture |
| Architecture | parent → Spec; references → PRD, ADR |
| Spec | parent → Architecture; parent → Spec Topic; decomposes → Spec Topic |
| Spec Topic | parent → Spec; child → Interface, Task; references → ADR |
| Interface | parent → Spec Topic |
| Task | parent → Spec Topic; child → Wave, Test |
| Test | parent → Task; verifies → Interface, Spec, Spec Topic; triggers → ADR; informs → Execution Plan |
| Wave | child → Execution Plan |
| Execution Plan | parent → Wave; child → Audit Report |
| ADR | references → أي وثيقة (target_id نصي) |
| Plan | parent → Spec/Spec Topic; references → ADR |
| Audit Report | parent → Execution Plan; informed_by → Test; references → ADR |

### الفئات العرضية (Cross-cutting)

- **ADR**: يمكن أن يشير إلى أي وثيقة في chain.
- **Plan**: ينشأ من Spec أو Spec Topic.
- **Execution Plan**: يربط Plan بـ Wave.
- **Audit Report**: يوثق نتائج التحقق من التنفيذ.
- **Constitution**: قواعد المشروع الثابتة (مستقلة عن chain).

---

## روابط الملفات

| الملف | المحتوى |
|-------|---------|
| [00-document-registry.md](Doc_Type_Schema/00-document-registry.md) | سجل الوثائق — doc classes, statuses, edge types |
| [01-architectural-taxonomy.md](Doc_Type_Schema/01-architectural-taxonomy.md) | تصنيف معماري — domains, layers, component types, bounded contexts |
| [02-chain-graph-model.md](02-chain-graph-model.md) | النموذج البياني المختلط — FK + edges |
| [03-class-prd.md](03-class-prd.md) | PRD — وثيقة متطلبات المنتج |
| [04-class-architecture.md](04-class-architecture.md) | Architecture — وثيقة النظام المعماري |
| [05-class-spec.md](05-class-spec.md) | Spec — مواصفات السلوك |
| [06-class-spec-topic.md](06-class-spec-topic.md) | Spec Topic — تفكيك المواصفات |
| [07-class-interface.md](07-class-interface.md) | Interface — عقود API |
| [08-class-adr.md](08-class-adr.md) | ADR — سجل القرارات المعمارية |
| [09-class-plan.md](09-class-plan.md) | Plan — خطة التصميم التقني |
| [10-class-execution-plan.md](10-class-execution-plan.md) | Execution Plan — استراتيجية المنسق |
| [11-class-audit-report.md](11-class-audit-report.md) | Audit Report — تقرير التدقيق |
| [12-class-task-wave.md](12-class-task-wave.md) | Task + Wave — المهام والموجات |
| [Constitution](Doc_Type_Schema/constitution.md) | Constitution — دستور المشروع |
| [Test](Doc_Type_Schema/test.md) | Test — تحليل الكفاءات المعماري |
| [Audit Report](Doc_Type_Schema/audit_report.md) | Audit Report — تقرير التدقيق |
| [ADR-001-graph-model-decision.md](ADR-001-graph-model-decision.md) | ADR-001 — قرار النموذج البياني |
