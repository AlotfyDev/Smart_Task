# Interface — عقود API (Interface Contracts)

## الغرض

توثيق العقود الرسمية للواجهات: REST endpoints، WebSocket events، تنسيقات الطلب والاستجابة، ومخططات البيانات.  
تمثل "كيف" تتواصل المكونات مع بعضها.

## المخطط (DDL)

```sql
CREATE TABLE interfaces (
    id              TEXT    PRIMARY KEY,                -- INTF-001
    topic_id        INTEGER NOT NULL REFERENCES spec_topics(id),
    title           TEXT    NOT NULL,
    contract_format TEXT    NOT NULL DEFAULT 'openapi',  -- openapi, grpc, graphql, websocket, etc.
    endpoints       TEXT    NOT NULL,                   -- JSON array of endpoint definitions
    schemas         TEXT,                               -- JSON: request/response schemas
    auth_required   INTEGER NOT NULL DEFAULT 0,
    rate_limits     TEXT,                               -- JSON: rate limiting specs
    status          TEXT    NOT NULL DEFAULT 'draft',   -- draft / reviewed / approved
    version         INTEGER NOT NULL DEFAULT 1,
    tags            TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);
```

## علاقة الوالد

- **الوالد**: spec_topics(id) — كل واجهة تنتمي إلى Topic واحد.
- **الأبناء**: لا يوجد أبناء مباشرون عبر FK.
- **المفتاح الخارجي**: `topic_id REFERENCES spec_topics(id)`

## مثال

```sql
INSERT INTO interfaces (id, topic_id, title, endpoints, schemas)
VALUES (
    'INTF-001',
    'TOPIC-001',
    'واجهة تنفيذ أمر الشراء',
    '[
        {
            "method": "POST",
            "path": "/api/v1/orders/buy",
            "description": "تنفيذ أمر شراء",
            "request": "BuyOrderRequest",
            "response": "OrderConfirmation"
        }
    ]',
    '{
        "BuyOrderRequest": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string"},
                "quantity": {"type": "number"},
                "price_limit": {"type": "number"}
            }
        },
        "OrderConfirmation": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"},
                "status": {"type": "string"},
                "executed_at": {"type": "string"}
            }
        }
    }'
);
```

## الاستخدام في سير العمل الوكيل

1. **وكيل الواجهات** (Interface Agent) يستلم TOPIC-ID ويستخرج العقود.
2. تُستخدم الـ schemas لإنشاء نماذج Pydantic أو فئات TypeScript تلقائياً.
3. يتم ربط الـ Interface بـ ADR عبر doc_edges إذا كان هناك قرار معماري يؤثر على تصميم الواجهة.
4. توثق rate_limits و auth_required للاستخدام في اختبارات الأداء والأمان.
