# التصنيف المعماري (Architectural Taxonomy)

## تعريف

`01-architectural-taxonomy` هو **تصنيف معياري لمكونات النظام المستهدف**. يوفر لغة مشتركة لوصف المكونات والعلاقات عبر النظام من خلال:

- **arch_domains**: مجالات الأعمال — تقسيم النظام إلى نطاقات أعمال
- **arch_layers**: الطبقات المعمارية — المستويات التنظيمية للمكونات
- **arch_component_types**: أنواع المكونات — تصنيف نمطي للمكونات
- **arch_bounded_contexts**: السياقات المحددة (Bounded Contexts) — حدود السياقات مع خريطة السياق
- **arch_integration_patterns**: أنماط التكامل — كيف تتواصل المكونات
- **arch_styles**: الأنماط المعمارية — الطراز المعماري العام للنظام

أي capability في `capability_matrix` يجب أن تشير إلى domain و layer و component_type من هذا السجل.

## الفرق بين 00-document-registry و 01-architectural-taxonomy

| البعد | 00-document-registry | 01-architectural-taxonomy |
|-------|---------------------|---------------------------|
| **الطبقة** | Meta layer — عن الوثائق نفسها | Model layer — عن النظام المستهدف |
| **السؤال** | ما أنواع الوثائق الموجودة؟ وما حالاتها وعلاقاتها؟ | ما مكونات النظام؟ وما طبقاته وسياقاته؟ |
| **المحتوى** | doc classes, statuses, edge types | domains, layers, component types, bounded contexts, integration patterns, styles |
| **يُستخدم لـ** | ضبط جودة المستندات، التحقق من صحة المسار | فهم هيكل النظام، توجيه القرارات المعمارية |

## كيف تستخدمها Test class؟

الـ `capability_matrix` في Test تشير إلى `capabilities` التي ترتبط بـ domains و layers. Architectural Taxonomy يوفر الـ taxonomy reference للـ capability_matrix:

- كل capability ترتبط بـ domain (مجال أعمال)
- كل capability ترتبط بـ layer (طبقة معمارية)
- كل capability ترتبط بـ component_type (نوع مكون)

مثلاً:
- capability: `order_execution` ← domain: `trading`, layer: `application`, component_type: `service`
- capability: `risk_check` ← domain: `risk`, layer: `domain`, component_type: `module`

## DDL

```sql
-- مجالات الأعمال — تقسيم النظام إلى نطاقات أعمال
CREATE TABLE arch_domains (
    code        TEXT PRIMARY KEY,       -- 'trading', 'risk', 'reporting', 'compliance', ...
    name        TEXT NOT NULL,
    description TEXT NOT NULL,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- الطبقات المعمارية — المستويات التنظيمية للمكونات
CREATE TABLE arch_layers (
    code        TEXT PRIMARY KEY,       -- 'presentation', 'application', 'domain', 'infrastructure', 'cross_cutting'
    name        TEXT NOT NULL,
    description TEXT NOT NULL,
    sort_order  INTEGER NOT NULL,       -- 0 = outermost, 4 = innermost
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- أنواع المكونات — تصنيف نمطي للمكونات
CREATE TABLE arch_component_types (
    code            TEXT PRIMARY KEY,       -- 'service', 'module', 'library', 'adapter', 'repository', 'pipeline', 'agent', 'worker', 'function'
    name            TEXT NOT NULL,
    description     TEXT NOT NULL,
    typical_layer   TEXT REFERENCES arch_layers(code),  -- layer where this type typically lives
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- السياقات المحددة (Bounded Contexts) — حدود السياقات مع خريطة السياق
CREATE TABLE arch_bounded_contexts (
    code            TEXT PRIMARY KEY,       -- 'ctx-trading', 'ctx-risk', 'ctx-reporting'
    name            TEXT NOT NULL,
    domain_code     TEXT NOT NULL REFERENCES arch_domains(code),
    description     TEXT NOT NULL,
    context_map     TEXT,                   -- JSON: array of { target_context, relationship_type, communication_pattern }
    shared_entities TEXT,                   -- JSON: array of entity names shared with other contexts
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- أنماط التكامل — كيف تتواصل المكونات
CREATE TABLE arch_integration_patterns (
    code        TEXT PRIMARY KEY,       -- 'rest', 'event', 'grpc', 'messaging', 'cli', 'file', 'websocket', 'shared_db'
    name        TEXT NOT NULL,
    description TEXT NOT NULL,
    protocol    TEXT,                   -- 'HTTP', 'gRPC', 'AMQP', 'Kafka', 'WebSocket', 'filesystem'
    async       INTEGER NOT NULL DEFAULT 0 CHECK (async IN (0, 1)),
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- الأنماط المعمارية — الطراز المعماري العام للنظام
CREATE TABLE arch_styles (
    code        TEXT PRIMARY KEY,       -- 'clean_architecture', 'hexagonal', 'layered', 'event_driven', 'microservices'
    name        TEXT NOT NULL,
    description TEXT NOT NULL,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
```

## arch_domains — مجالات الأعمال

| الحقل | النوع | إلزامي | مثال | الغرض |
|-------|-------|--------|------|-------|
| `code` | TEXT | نعم | `"trading"` | معرف فريد (snake_case) يُستخدم كـ FK |
| `name` | TEXT | نعم | `"Trading"` | الاسم الرسمي الإنجليزي |
| `description` | TEXT | نعم | `"..."` | وصف موجز بالعربية |

### القيم الافتتاحية (Pre-seeded)

| code | name | description |
|------|------|-------------|
| `trading` | Trading | تنفيذ الصفقات، إدارة الأوامر، دفتر الطلبات |
| `risk` | Risk | إدارة المخاطر، الحدود، التحقق |
| `reporting` | Reporting | التقارير، التحليلات، السجلات |
| `compliance` | Compliance | الامتثال، التدقيق، مكافحة غسل الأموال |
| `market_data` | Market Data | بيانات السوق، المؤشرات، التغذية السعرية |
| `account` | Account | حسابات المستخدمين، المحافظ، الأرصدة |
| `notification` | Notification | الإشعارات، التنبيهات، الرسائل |
| `integration` | Integration | التكامل مع الأنظمة الخارجية، API gateway |
| `system` | System | إدارة النظام، المراقبة، logging |

## arch_layers — الطبقات المعمارية

| الحقل | النوع | إلزامي | مثال | الغرض |
|-------|-------|--------|------|-------|
| `code` | TEXT | نعم | `"presentation"` | معرف فريد (snake_case) |
| `name` | TEXT | نعم | `"Presentation"` | الاسم الرسمي الإنجليزي |
| `description` | TEXT | نعم | `"..."` | وصف موجز بالعربية |
| `sort_order` | INTEGER | نعم | `0` | ترتيب الطبقة من الخارج للداخل (0 = أقصى الخارج) |

### القيم الافتتاحية

| code | name | sort_order | description |
|------|------|:----------:|-------------|
| `presentation` | Presentation | 0 | واجهة المستخدم، dashboard، CLI |
| `application` | Application | 1 | حالات الاستخدام، orchestrators، واجهات API |
| `domain` | Domain | 2 | منطق الأعمال، الكيانات، قواعد المجال |
| `infrastructure` | Infrastructure | 3 | التخزين، الشبكة، external services |
| `cross_cutting` | Cross-Cutting | 4 | أمن، مراقبة، caching، logging (تشمل كل الطبقات) |

## arch_component_types — أنواع المكونات

| الحقل | النوع | إلزامي | مثال | الغرض |
|-------|-------|--------|------|-------|
| `code` | TEXT | نعم | `"service"` | معرف فريد (snake_case) |
| `name` | TEXT | نعم | `"Service"` | الاسم الرسمي الإنجليزي |
| `description` | TEXT | نعم | `"..."` | وصف موجز بالعربية |
| `typical_layer` | TEXT (FK) | لا | `"application"` | الطبقة التي يسكن فيها هذا النوع غالباً |

### القيم الافتتاحية

| code | name | typical_layer | description |
|------|------|:-------------:|-------------|
| `service` | Service | application | خدمة مستقلة ذات حدود واضحة |
| `module` | Module | domain | وحدة برمجية داخل خدمة |
| `library` | Library | domain | مكتبة قابلة لإعادة الاستخدام |
| `adapter` | Adapter | infrastructure | محول للتكامل مع نظام خارجي |
| `repository` | Repository | infrastructure | مخزن بيانات (واجهة تخزين) |
| `pipeline` | Pipeline | application | خط أنابيب معالجة (processing pipeline) |
| `agent` | Agent | application | وكيل مستقل (قد يكون sub-agent في سياق Smart Task) |
| `worker` | Worker | infrastructure | عامل خلفية (background worker) |
| `function` | Function | application | دالة منفردة (serverless) |

## arch_bounded_contexts — السياقات المحددة

| الحقل | النوع | إلزامي | مثال | الغرض |
|-------|-------|--------|------|-------|
| `code` | TEXT | نعم | `"ctx-order-execution"` | معرف فريد |
| `name` | TEXT | نعم | `"Order Execution"` | الاسم الرسمي |
| `domain_code` | TEXT (FK) | نعم | `"trading"` | المجال التابع له |
| `description` | TEXT | نعم | `"..."` | وصف موجز بالعربية |
| `context_map` | TEXT (JSON) | لا | `[{...}]` | خريطة السياق — ارتباط مع السياقات الأخرى |
| `shared_entities` | TEXT (JSON) | لا | `["Order", "Trade"]` | الكيانات المشتركة مع سياقات أخرى |

### القيم الافتتاحية (أمثلة)

| code | name | domain_code | context_map | shared_entities |
|------|------|:-----------:|-------------|-----------------|
| `ctx-order-execution` | Order Execution | trading | `[{"target_context": "ctx-risk-mgmt", "relationship_type": "upstream", "communication_pattern": "event"}, {"target_context": "ctx-reporting", "relationship_type": "notifies", "communication_pattern": "event"}]` | `["Order", "Trade", "Position"]` |
| `ctx-risk-mgmt` | Risk Management | risk | `[{"target_context": "ctx-order-execution", "relationship_type": "downstream", "communication_pattern": "event"}, {"target_context": "ctx-reporting", "relationship_type": "notifies", "communication_pattern": "event"}]` | `["Order", "Position", "RiskLimit"]` |
| `ctx-reporting` | Reporting | reporting | `[{"target_context": "ctx-order-execution", "relationship_type": "subscribes", "communication_pattern": "event"}, {"target_context": "ctx-risk-mgmt", "relationship_type": "subscribes", "communication_pattern": "event"}, {"target_context": "ctx-market-feed", "relationship_type": "subscribes", "communication_pattern": "event"}]` | `["Trade", "Position"]` |
| `ctx-market-feed` | Market Feed | market_data | `[{"target_context": "ctx-order-execution", "relationship_type": "feeds", "communication_pattern": "event"}, {"target_context": "ctx-risk-mgmt", "relationship_type": "feeds", "communication_pattern": "event"}]` | `["Price", "Instrument"]` |

## arch_integration_patterns — أنماط التكامل

| الحقل | النوع | إلزامي | مثال | الغرض |
|-------|-------|--------|------|-------|
| `code` | TEXT | نعم | `"rest"` | معرف فريد (snake_case) |
| `name` | TEXT | نعم | `"RESTful API"` | الاسم الرسمي |
| `description` | TEXT | نعم | `"..."` | وصف موجز بالعربية |
| `protocol` | TEXT | لا | `"HTTP"` | البروتوكول المستخدم |
| `async` | INTEGER | نعم | `0` | `1` = غير متزامن، `0` = متزامن |

### القيم الافتتاحية

| code | name | protocol | async | description |
|------|------|----------|:-----:|-------------|
| `rest` | RESTful API | HTTP | 0 | RESTful HTTP — متزامن (sync) |
| `event` | Event-Driven | AMQP / Kafka | 1 | Event-driven via message broker — غير متزامن (async) |
| `grpc` | gRPC | gRPC | 0 | gRPC bidirectional — متزامن |
| `messaging` | Message Queue | AMQP | 1 | Message queue — غير متزامن |
| `cli` | Command-Line Interface | stdio | 0 | Command-line interface — متزامن |
| `file` | File Exchange | filesystem | 1 | File-based exchange — غير متزامن |
| `websocket` | WebSocket | WebSocket | 1 | WebSocket persistent connection — غير متزامن |
| `shared_db` | Shared Database | SQL | 0 | Shared database — متزامن |

## arch_styles — الأنماط المعمارية

| الحقل | النوع | إلزامي | مثال | الغرض |
|-------|-------|--------|------|-------|
| `code` | TEXT | نعم | `"clean_architecture"` | معرف فريد (snake_case) |
| `name` | TEXT | نعم | `"Clean Architecture"` | الاسم الرسمي |
| `description` | TEXT | نعم | `"..."` | وصف موجز بالعربية |

### القيم الافتتاحية

| code | name | description |
|------|------|-------------|
| `clean_architecture` | Clean Architecture | طبقات مع اعتماد الداخل على الخارج (inward dependency) |
| `hexagonal` | Hexagonal (Ports & Adapters) | Ports & Adapters — عزل الأساسي عن التقني |
| `layered` | Layered Architecture | طبقات تقليدية (presentation → business → data) |
| `event_driven` | Event-Driven Architecture | اتصال عبر الأحداث |
| `microservices` | Microservices Architecture | خدمات مستقلة موزعة |

## كيفية التوسع

هذه taxonomy مرنة: المجالات والطبقات مش مقيدة — أي مشروع يمكن أن يضيف ما يحتاجه. الموجود هنا هو الـ baseline الذي يغطي الحالات الشائعة في نظام Smart Task.

لإضافة:
- **مجال جديد**: سجل في `arch_domains` ثم أنشئ bounded contexts المرتبطة به
- **طبقة جديدة**: سجل في `arch_layers` مع `sort_order` مناسب
- **نوع مكون جديد**: سجل في `arch_component_types` مع `typical_layer` المناسب
- **سياق محدود جديد**: سجل في `arch_bounded_contexts` مع `context_map` و `shared_entities`
- **نمط تكامل جديد**: سجل في `arch_integration_patterns`
- **طراز معماري جديد**: سجل في `arch_styles`

## مصدر الحقيقة

هذه الجداول هي السجل الرسمي للتاكسونومي المعمارية. أي capability في `capability_matrix` يجب أن تشير إلى domain و layer و component_type من هذا السجل. لا يُسمح باستخدام قيم غير مسجلة في هذه الجداول.

الدورة لإضافة عنصر معماري جديد:
1. يُسجل في الجدول المناسب مع `code`، `name`، `description`
2. إذا كان مرتبطاً بجداول أخرى (مثل `typical_layer` في `arch_component_types`) يُتحقق من وجود المرجع
3. يُحدث ملف JSON Schema في `Json_Schema/` إذا لزم الأمر
4. يُوثق بالعربية هنا
