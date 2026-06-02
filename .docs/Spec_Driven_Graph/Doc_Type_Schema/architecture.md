# مخطط كيان وثيقة العمارة (Architecture Document Schema)

## 1. تعريف

وثيقة العمارة (Architecture Document) هي الوثيقة الثانية في سلسلة التخصيص بعد PRD. تترجم متطلبات PRD إلى قرارات معمارية ملموسة: تحليل المجالات (domains)، تحديد الطبقات (layers)، والمكونات (components). كل مكون يُسجّل هنا يصبح لاحقا وثيقة Spec مستقلة. العمارة تُجبر على ذكر non-goals صراحة (عكس PRD حيث كانت اختيارية)، وتوفّر خريطة تتبع (req_coverage) تربط كل متطلب PRD بقسم معماري يوفيه.

## 2. DDL

```sql
CREATE TABLE architecture_docs (
    id               TEXT PRIMARY KEY,      -- ARCH-001
    prd_id           TEXT NOT NULL REFERENCES prds(id),
    title            TEXT NOT NULL,
    status           TEXT NOT NULL CHECK (status IN ('draft', 'reviewed', 'approved', 'superseded')),
    version          TEXT NOT NULL DEFAULT '1.0',
    tags             TEXT NOT NULL DEFAULT '[]',
    context          TEXT NOT NULL,
    goals            TEXT NOT NULL,          -- JSON
    non_goals        TEXT NOT NULL,          -- JSON
    component_map    TEXT NOT NULL,          -- JSON: domain -> layer -> component
    data_model       TEXT NOT NULL,          -- JSON
    data_flow        TEXT NOT NULL,          -- JSON
    risks            TEXT NOT NULL,          -- JSON
    req_coverage     TEXT NOT NULL,          -- JSON: PRD req -> domain/layer mapping
    alternatives     TEXT,                   -- JSON: اختياري
    open_questions   TEXT,                   -- JSON: اختياري
    created_at       TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at       TEXT NOT NULL DEFAULT (datetime('now'))
);
```

## 3. شرح الحقول

| الحقل | النوع | إجباري | مثال بنية JSON | الغرض الدلالي |
|---|---|---|---|---|
| `id` | TEXT | نعم | `"ARCH-001"` | معرف فريد للوثيقة، نمط ARCH-XXX |
| `prd_id` | TEXT | نعم | `"PRD-001"` | مفتاح خارجي يربط بوثيقة PRD الأم |
| `title` | TEXT | نعم | `"عمارة نظام التداول"` | عنوان وصفي للوثيقة |
| `status` | TEXT | نعم | `"draft"` | حالة دورة الحياة: draft -> reviewed -> approved -> superseded |
| `version` | TEXT | نعم | `"1.0"` | إصدار الوثيقة، يبدأ بـ 1.0 |
| `tags` | TEXT | نعم | `["trading", "core"]` | وسوم لتصنيف الوثيقة والبحث |
| `context` | TEXT | نعم | `"نظام التداول يحتاج إلى..."` | سياق معماري يصف المشكلة والقيود والافتراضات |
| `goals` | TEXT | نعم | `[{"id": "G1", "desc": "دعم 10k طلب/ثانية"}]` | قائمة الأهداف المعمارية التي يحققها التصميم |
| `non_goals` | TEXT | نعم | `[{"id": "NG1", "desc": "التكامل مع blockchain"}]` | قائمة non-goals — إجباري هنا (عكس PRD) |
| `component_map` | TEXT | نعم | `{"trading": {"application": ["order-executor", "market-data"]}}` | **خريطة التحلل المعماري** — domain -> layer -> component. هذا الحقل هو محرك التحلل إلى Specs |
| `data_model` | TEXT | نعم | `{"entities": [{"name": "Order", "fields": [...]}]}` | نموذج البيانات الرئيسية: الكيانات، العلاقات، الحقول |
| `data_flow` | TEXT | نعم | `{"flows": [{"from": "Trader", "to": "OrderBook", "data": "Order"}]}` | تدفقات البيانات بين المكونات والجهات الخارجية |
| `risks` | TEXT | نعم | `[{"risk": "زمن استجابة مرتفع", "mitigation": "استخدام in-memory cache"}]` | تحليل المخاطر المعمارية مع خطط التخفيف |
| `req_coverage` | TEXT | نعم | `[{"req_id": "REQ-001", "domains": ["trading"], "layers": ["application"]}]` | **خريطة تتبع المتطلبات**: كل متطلب PRD يُربط بالمجال والطبقة المسؤولة عنه |
| `alternatives` | TEXT | لا | `[{"option": "استخدام RabbitMQ", "tradeoff": "مقابل Kafka"}]` | حلول معمارية بديلة تم بحثها (اختياري) |
| `open_questions` | TEXT | لا | `[{"question": "هل نستخدم REST أم gRPC؟", "assigned_to": "team"}]` | أسئلة مفتوحة تحتاج قرارا (اختياري) |
| `created_at` | TEXT | نعم | `"2026-06-02T10:00:00"` | طابع زمني لإنشاء الوثيقة |
| `updated_at` | TEXT | نعم | `"2026-06-02T12:00:00"` | طابع زمني لآخر تحديث |

## 4. ملاحظة تحلل: component_map -> يقود سلسلة Specs

`component_map` هو **محرك التحلل (decomposition driver)** في النظام. كل مكون (component) يُعرّف في هذه الخريطة يصبح تلقائيا وثيقة Spec جديدة في سلسلة التخصيص. آلية العمل:

```
component_map -> لكل مكون -> توليد Spec
```

على سبيل المثال، إذا كان `component_map` يحتوي على:
```json
{
  "trading": {
    "application": ["order-executor", "market-data"],
    "domain":  ["order-book"]
  }
}
```

فإن النظام يولّد الوثائق التالية:
- `SPEC-001: order-executor`
- `SPEC-002: market-data`
- `SPEC-003: order-book`

كل Spec يرث metadata من وثيقة العمارة (مثل `prd_id`) ويضيف تفاصيل التنفيذ الخاصة به. هذا يضمن أن كل كود مكتوب له أصل معماري مباشر.

## 5. ملاحظة تصنيف: domain -> layer -> component

بنية `component_map` مرنة عمدا لتدعم أنماط معمارية مختلفة:

- **Monolith**: `{"app": {"presentation": ["ui-layer"], "business": ["service"], "data": ["repo"]}}`
- **Microservices**: `{"payments": {"service": ["payment-svc"]}, "notifications": {"service": ["notif-svc"]}}`
- **Hexagonal**: `{"core": {"domain": ["order"], "adapters": ["rest-adapter", "db-adapter"]}}`
- **Event-Driven**: `{"analytics": {"processors": ["click-processor"], "streams": ["click-stream"]}}`

المجالات (domains) والطبقات (layers) ليست مقيدة بقائمة ثابتة — يحددها المهندس المعماري حسب سياق المشروع. الشرط الوحيد هو أن تكون بنية JSON ثلاثية المستويات صالحة: `domain -> layer -> component[]`.
