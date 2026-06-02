# طبقة المعالجات — MCP Handler Layer

## مبدأ Thin Handler

MCP Handler هو **طبقة رقيقة جدًا**. دوره الوحيد: استقبال request من MCP، استدعاء Service، إرجاع النتيجة. **لا يحتوي أي business logic.**

```python
# ✅  Handler جيد: رقيق، يستدعي Service فقط
@mcp.tool()
def approve_prd(prd_id: str) -> str:
    try:
        prd = doc_service.approve_prd(prd_id)
        return json.dumps(prd.to_dict(), ensure_ascii=False)
    except InvalidTransition as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

# ❌ Handler سيء: يحتوي business logic
@mcp.tool()
def approve_prd(prd_id: str) -> str:
    prd = repo.get("prd", prd_id)          # ❌ يعرف Repository مباشرة
    if prd.status != "reviewed":            # ❌ Business logic في Handler
        return '{"error": "wrong status"}'
    prd.status = "approved"                 # ❌ يعدّل entity مباشرة
    repo.save(prd)                          # ❌ يتفاعل مع DB مباشرة
    return json.dumps(prd.to_dict())
```

## MCP Handler مثال كامل

MCP Tool — للعمليات (create, update, delete, validate):

```python
@mcp.tool()
def get_document(doc_type: str, doc_id: str) -> str:
    """الحصول على وثيقة حسب نوعها ومعرفها."""
    try:
        doc = doc_service.get_entity(doc_type, doc_id)
        return json.dumps(doc.to_dict(), ensure_ascii=False)
    except EntityNotFound as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

@mcp.tool()
def create_document(doc_type: str, data: str) -> str:
    """إنشاء وثيقة جديدة. data: JSON string."""
    try:
        parsed = json.loads(data)
        doc = doc_service.create_entity(doc_type, parsed)
        return json.dumps(doc.to_dict(), ensure_ascii=False)
    except (ValidationError, DuplicateEntity) as e:
        return json.dumps({"error": str(e.code), "detail": str(e)}, ensure_ascii=False)

@mcp.tool()
def delete_document(doc_type: str, doc_id: str) -> str:
    """حذف وثيقة."""
    try:
        doc_service.delete_entity(doc_type, doc_id)
        return json.dumps({"deleted": True, "id": doc_id}, ensure_ascii=False)
    except EntityNotFound as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

@mcp.tool()
def get_graph_neighbors(doc_id: str, edge_type: str | None = None) -> str:
    """جلب neighbors لوثيقة في الـ graph."""
    try:
        neighbors = graph_service.get_neighbors(doc_id, edge_type)
        return json.dumps(neighbors, ensure_ascii=False)
    except EntityNotFound as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
```

## Error Mapping

كل Service exception يُرسم إلى MCP error message:

| Service Exception | MCP Response |
|-------------------|--------------|
| `EntityNotFound(doc_type, doc_id)` | `{"error": "spec 'SPEC-001' غير موجود"}` |
| `InvalidTransition(doc_type, doc_id, current, expected)` | `{"error": "prd 'PRD-001' في حالة 'draft'، يتطلب 'reviewed'"}` |
| `ValidationError(errors_list)` | `{"error": "VALIDATION_ERROR", "detail": "فشل التحقق: ..."}` |
| `DuplicateEntity(doc_type, doc_id)` | `{"error": "spec 'SPEC-001' موجود مسبقًا"}` |
| `FKNotFound(doc_type, fk_field, fk_value)` | `{"error": "المرجع 'prd_id=PRD-999' غير موجود"}` |
| أي ServiceError غير متوقع | `{"error": "SERVICE_ERROR", "detail": "<message>"}` |
| استثناء غير متوقع (Exception) | `{"error": "INTERNAL_ERROR", "detail": "خطأ داخلي في النظام"}` |

```python
def _handle_error(e: Exception) -> str:
    """تحويل أي Service exception إلى MCP response."""
    if isinstance(e, EntityNotFound):
        return json.dumps({"error": f"{e.doc_type} '{e.doc_id}' غير موجود"}, ensure_ascii=False)
    if isinstance(e, InvalidTransition):
        return json.dumps({"error": str(e)}, ensure_ascii=False)
    if isinstance(e, ValidationError):
        return json.dumps({"error": "VALIDATION_ERROR", "detail": e.errors}, ensure_ascii=False)
    if isinstance(e, DuplicateEntity):
        return json.dumps({"error": str(e)}, ensure_ascii=False)
    # Fallback: أي خطأ غير متوقع
    logger.exception("خطأ غير متوقع في MCP Handler")
    return json.dumps({"error": "INTERNAL_ERROR", "detail": "خطأ داخلي في النظام"}, ensure_ascii=False)
```

## ما يدخلش في الـ Handler

| ✅ مسموح | ❌ ممنوع |
|----------|----------|
| parse input (json.loads) | Business logic (if/else على status) |
| call service method | DB queries مباشرة |
| format output (json.dumps) | Entity construction |
| error mapping | تعديل حالة entity يدويًا |
| logging (basic) | تحقق من validity قبل الـ save |

## Resource Definition

MCP Resources — واجهة قراءة للوثائق عبر URI موحد:

```python
@mcp.resource("spec-dg://{doc_type}/{doc_id}")
def get_spec_dg_resource(doc_type: str, doc_id: str) -> str:
    """MCP Resource للوصول للوثائق عبر URI."""
    try:
        doc = doc_service.get_entity(doc_type, doc_id)
        return json.dumps(doc.to_dict(), ensure_ascii=False)
    except EntityNotFound:
        raise ValueError(f"{doc_type} '{doc_id}' غير موجود")

@mcp.resource("spec-dg://{doc_type}")
def list_spec_dg_resources(doc_type: str) -> str:
    """MCP Resource لسرد كل الوثائق من نوع معين."""
    docs = doc_service.list_entities(doc_type, FilterSpec())
    return json.dumps([d.to_dict() for d in docs], ensure_ascii=False)
```

**URI schema:**
| URI | الإرجاع |
|-----|---------|
| `spec-dg://prd/PRD-001` | PRD entity كـ JSON |
| `spec-dg://spec` | قائمة كل specs كـ JSON array |
| `spec-dg://graph/neighbors/TEST-001` | Neighbors كـ JSON array |

## Tool Definition

MCP Tools — للعمليات:

| الـ Tool | المعاملات | الوظيفة |
|----------|-----------|---------|
| `get_document` | doc_type, doc_id | قراءة وثيقة |
| `create_document` | doc_type, data (JSON) | إنشاء وثيقة |
| `update_document` | doc_type, doc_id, data (JSON) | تحديث وثيقة |
| `delete_document` | doc_type, doc_id | حذف وثيقة |
| `validate_document` | doc_type, doc_id | تحقق من صحة وثيقة |
| `get_chain` | doc_id | إرجاع السلسلة الكاملة |
| `get_impact` | doc_id | تحليل تأثير التغيير |
| `find_gaps` | spec_id | إيجاد الفجوات |

## Separation Example — مقارنة

**Bad Handler — منطق منتشر:**

```python
@mcp.tool()
def create_task(topic_id: str, title: str) -> str:
    # ❌ Business logic في Handler
    topic = repo.get("spec_topic", topic_id)
    if topic.status != "approved":
        return '{"error": "Topic must be approved first"}'

    # ❌ Entity construction في Handler
    task_id = f"TASK-OPENAI-{uuid4().hex[:4]}"
    task = TaskEntity(id=task_id, title=title, status="draft", topic_id=topic_id)

    # ❌ Direct DB interaction
    repo.save(task)
    edge = Edge(source_id=topic_id, target_id=task_id, edge_type="decomposes")
    repo.save_edge(edge)

    return json.dumps(task.to_dict())
```

**Good Handler — Service يتولى كل شيء:**

```python
@mcp.tool()
def create_task(topic_id: str, title: str) -> str:
    try:
        task = orchestration_service.create_task(topic_id, title)
        return json.dumps(task.to_dict(), ensure_ascii=False)
    except (ValidationError, FKNotFound) as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
```

**الفرق:** Bad handler يعرف عن Repository, Entity construction, Edge creation, Business rules. Good handler يستدعي Service method واحد ويعيد النتيجة. التغيير على business logic يتم في Service فقط، لا يحتاج تعديل handlers.
