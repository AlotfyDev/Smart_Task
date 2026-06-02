# مخطط كيان وثيقة بنية البيانات (Data Structure Schema)

## 1. التعريف

وثائق بنية البيانات (Data Structures) هي فئة وثائقية مستقلة داخل تصنيف Smart Task، مسؤولة عن تعريف الكيانات والحقول والعلاقات والقيود بشكل مركزي. تهدف هذه الفئة إلى أن تكون **المصدر الوحيد والحقيقي (Single Source of Truth)** لكل كيان في النظام مثل `Order` و `User` و `Trade`.

### لماذا فئة منفصلة؟

- **تجنب التكرار:** بدلا من تكرار تعريف الحقول داخل كل وثيقة Spec، تشير Specs إلى بنية البيانات عبر `doc_edges`.
- **قابلية التوسع:** أي تغيير في هيكل كيان يحدث في مكان واحد فقط، وينعكس تلقائيا على جميع الوثائق المرجعية.
- **فصل الاهتمامات:** تفصل بنية البيانات (ماذا يوجد) عن المواصفات (كيف يستخدم).
- **التناسق:** ضمان تعريف موحد للأنواع والقيود والعلاقات عبر النظام بأكمله.

### موقعها في التصنيف

- **Architecture Document:** يحتوي على `data_model` عالي المستوى يصف خريطة الكيانات والعلاقات الكلية.
- **Data Structure:** وثيقة تفصيلية لكل كيان على حدة، تحدد الحقول والأنواع والعلاقات والقيود.
- **Spec Document:** يستخدم `doc_edges` بنوع `uses` أو `references` لربط المواصفات ببنية البيانات دون إعادة تعريف الحقول.

---

## 2. DDL

```sql
CREATE TABLE data_structures (
    id              TEXT PRIMARY KEY,      -- DST-001
    arch_id         TEXT REFERENCES architecture_docs(id),
    title           TEXT NOT NULL,
    entity_name     TEXT NOT NULL,         -- 'Order', 'Trade', 'User'
    description     TEXT NOT NULL,
    fields          TEXT NOT NULL,          -- JSON: [{"name":"order_id","type":"UUID","required":true,"description":"..."},...]
    relationships   TEXT,                   -- JSON: [{"type":"belongs_to","target":"User","via":"user_id"},...]
    constraints     TEXT,                   -- JSON: [{"type":"unique","fields":["order_id"]},...]
    indexes         TEXT,                   -- JSON: [{"name":"idx_status","fields":["status"]},...]
    status          TEXT NOT NULL CHECK (status IN ('draft', 'reviewed', 'approved', 'superseded')),
    version         TEXT NOT NULL DEFAULT '1.0',
    tags            TEXT NOT NULL DEFAULT '[]',
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
```

---

## 3. شرح الحقول


### 3.1 الحقول الأساسية

| الحقل | النوع | إلزامي | مثال JSON | الغرض |
|-------|-------|--------|-----------|-------|
| `id` | TEXT | نعم | `"DST-001"` | معرّف فريد للوثيقة وفق نظام الترقيم المعتمد |
| `arch_id` | TEXT | لا | `"ARC-001"` | معرّف وثيقة الـ Architecture التي ينتمي إليها هذا الكيان |
| `title` | TEXT | نعم | `"هيكل كيان الطلب (Order)"` | عنوان وصفي للوثيقة |
| `entity_name` | TEXT | نعم | `"Order"` | اسم الكيان كما سيستخدم في الكود وقواعد البيانات (PascalCase) |
| `description` | TEXT | نعم | `"يمثل أمر تداول يقدمه المستخدم لشراء أو بيع أصل مالي"` | وصف نصي لدور الكيان في النظام |

### 3.2 حقول المحتوى (JSON)

| الحقل | النوع | إلزامي | مثال JSON | الغرض |
|-------|-------|--------|-----------|-------|
| `fields` | TEXT (JSON) | نعم | `[{"name":"order_id","type":"UUID","required":true,"description":"معرّف فريد للأمر","default":null,"example":"550e8400-e29b-..."}]` | مصفوفة تعريفات الحقول. كل حقل يتضمن: الاسم، النوع، هل هو إلزامي، وصف، قيمة افتراضية، مثال |
| `relationships` | TEXT (JSON) | لا | `[{"type":"belongs_to","target":"User","via":"user_id","description":"المستخدم المالك للأمر"},{"type":"has_many","target":"Trade","via":"order_id"}]` | مصفوفة العلاقات مع الكيانات الأخرى. الأنواع المدعومة: `belongs_to`, `has_one`, `has_many`, `has_many_through` |
| `constraints` | TEXT (JSON) | لا | `[{"type":"unique","fields":["order_id"],"name":"uq_order_id"},{"type":"check","expression":"quantity > 0","name":"ck_positive_qty"}]` | مصفوفة القيود. الأنواع المدعومة: `unique`, `primary_key`, `foreign_key`, `check`, `not_null` |
| `indexes` | TEXT (JSON) | لا | `[{"name":"idx_orders_status","fields":["status"],"unique":false},{"name":"idx_orders_user","fields":["user_id","status"]}]` | مصفوفة الفهارس المقترحة لتحسين أداء الاستعلامات |

### 3.3 حقول الإدارة والحالة

| الحقل | النوع | إلزامي | مثال JSON | الغرض |
|-------|-------|--------|-----------|-------|
| `status` | TEXT | نعم | `"reviewed"` | حالة نضج الوثيقة. القيم المسموحة: `draft`, `reviewed`, `approved`, `superseded` |
| `version` | TEXT | نعم | `"1.0"` | رقم إصدار الوثيقة، يزداد مع التعديلات الجوهرية |
| `tags` | TEXT (JSON) | لا | `["core","trading","order-management"]` | وسوم لتصنيف وتصفية الوثائق |
| `created_at` | TEXT | نعم | `"2026-01-15T10:30:00Z"` | طابع زمني لإنشاء الوثيقة |
| `updated_at` | TEXT | نعم | `"2026-03-20T14:22:00Z"` | طابع زمني لآخر تعديل |

---

## 4. ملاحظات العلاقات

### 4.1 Architecture → Data Structure

- يحتوي `architecture_docs.data_model` على خريطة عالية المستوى لجميع الكيانات والعلاقات البينية (مخطط ERD مفاهيمي).
- كل `Data Structure` ترتبط بوثيقة Architecture عبر `arch_id`.
- تمثل Data Structure التفاصيل التنفيذية الدقيقة لكيان واحد.

### 4.2 Data Structure → Spec

- تستخدم وثائق Spec حقل `doc_edges` (في جدول `spec_docs`) للارتباط ببنية البيانات.
- أنواع الحواف المدعومة:
  - `uses`: عندما تستخدم الـ Spec الكيان كجزء من منطق الأعمال (مثل `OrderSpec` يستخدم `Order`).
  - `references`: عندما تشير الـ Spec إلى الكيان بشكل غير مباشر (مثل `ReportSpec` يشير إلى `User` لعرض البيانات).
- لا يجوز تكرار تعريف الحقول في الـ Spec؛ أي حقل مستخدم يجب أن يأتي من `Data Structure` عبر الحافة.

### 4.3 مثال لتدفق المرجعية

```
Architecture (ARC-001)
  └── data_model: { "Order" → "User", "Order" → "Trade" }
       │
       ├── Data Structure: DST-001 (Order)
       │     ├── fields: order_id, user_id, symbol, quantity, status
       │     ├── relationships: belongs_to User, has_many Trade
       │     └── constraints: unique(order_id), check(quantity > 0)
       │
       └── Data Structure: DST-002 (User)
             ├── fields: user_id, name, email, role
             └── relationships: has_many Order

Spec: OrderExecutionSpec (SPC-042)
  └── doc_edges:
        ├── { target_id: "DST-001", edge_type: "uses", note: "يستخدم Order ككيان رئيسي" }
        └── { target_id: "DST-002", edge_type: "references", note: "يراجع مالك الأمر" }
```

بهذه الطريقة، أي تعديل على `Order.fields` يحدث في `DST-001` فقط، وكل Spec يستخدم `Order` يستفيد تلقائيا من أحدث تعريف دون الحاجة لتحديث منفصل.
