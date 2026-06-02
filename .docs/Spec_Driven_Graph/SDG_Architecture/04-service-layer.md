# طبقة الخدمات — Service Layer

## مبدأ Service Layer

الـ Service Layer هو **قلب التطبيق**. يحتوي كل Business Logic و Use Cases. يستدعي `EntityRegistry` و `Repository` و `GraphCache`. **لا يعرف MCP ولا HTTP ولا أي شيء عن طبقة العرض.**

```python
# ✅  Service يعمل business logic
class DocumentService:
    def approve_prd(self, prd_id: str) -> PRDEntity:
        prd = self._registry.get("prd", prd_id)
        if prd.status != "reviewed":
            raise InvalidTransition(f"PRD {prd_id} needs 'reviewed' status, got '{prd.status}'")
        prd.status = "approved"
        prd.approved_at = datetime.now()
        self._registry.save(prd)
        return prd
```

## أنواع الخدمات

### DocumentService — CRUD لكل doc types

```python
class DocumentService:
    def create_entity(self, doc_type: str, data: dict) -> Entity: ...
    def get_entity(self, doc_type: str, doc_id: str) -> Entity: ...
    def update_entity(self, doc_type: str, doc_id: str, data: dict) -> Entity: ...
    def delete_entity(self, doc_type: str, doc_id: str) -> None: ...
    def list_entities(self, doc_type: str, filters: FilterSpec) -> list[Entity]: ...
```

### GraphService — traversals و path queries

```python
class GraphService:
    def __init__(self, cache: GraphCache, registry: EntityRegistry): ...

    def get_chain(self, doc_id: str) -> list[Entity]:
        """إرجاع السلسلة الكاملة من PRD حتى الـ node."""

    def get_impact_analysis(self, doc_id: str) -> ImpactReport:
        """تحليل تأثير التغيير — من يتأثر بهذه الوثيقة."""

    def find_gaps(self, spec_id: str) -> list[Entity]:
        """إيجاد الفجوات: Topic بدون Interface, Task بدون Test."""

    def trace_requirement(self, req_id: str) -> TraceResult:
        """تتبع متطلب من PRD إلى Test."""
```

### ValidationService — التحقق من القواعد

```python
class ValidationService:
    def validate_status_transition(self, entity: Entity, new_status: str) -> bool: ...
    def validate_fk_references(self, entity: Entity) -> list[str]: ...
    def validate_capability_matrix(self, test_entity) -> ValidationReport: ...
    def validate_chain_completeness(self, prd_id: str) -> ChainReport: ...
```

### OrchestrationService — عمليات متعددة الخطوات

```python
class OrchestrationService:
    def create_full_chain(self, prd_data: dict) -> ChainResult:
        """إنشاء PRD → ARCH → SPEC → TOPICs → TASKs → TESTs كامل."""
        prd = self._doc_service.create_prd(prd_data)
        arch = self._doc_service.create_architecture(prd.id, prd_data)
        specs = [self._doc_service.create_spec(arch.id, s) for s in prd_data["specs"]]
        # ... and so on
        return ChainResult(prd=prd, arch=arch, specs=specs)
```

## Use Case Pattern

كل use case هو method واحد في Service. الميثود:
1. يستقبل data (Pydantic model أو dict)
2. يتحقق من business rules
3. يستدعي Registry/Repository
4. يرجع Entity أو Result

```python
class DocumentService:
    def create_prd(self, data: PRDCreate) -> PRDEntity:
        # 1. Validate input
        self._validator.validate_prd_data(data)
        # 2. Build entity
        prd = PRDEntity(
            id=generate_id("PRD"),
            title=data.title,
            status="draft",
            created_at=now(),
        )
        # 3. Save
        self._registry.save(prd)
        # 4. Register edge
        self._cache.add_edge(Edge(source_id=prd.id, edge_type="root"))
        return prd

    def approve_prd(self, prd_id: str) -> PRDEntity:
        prd = self._registry.get("prd", prd_id)
        # Business rule: only 'reviewed' PRDs can be approved
        if prd.status not in ("reviewed",):
            raise InvalidTransition(f"Cannot approve PRD in status '{prd.status}'")
        prd.status = "approved"
        prd.approved_at = datetime.now()
        self._registry.save(prd)
        return prd

    def get_prd_chain(self, prd_id: str) -> ChainResult:
        # Business rule: verify PRD exists
        prd = self._registry.get("prd", prd_id)
        chain = self._graph.get_chain(prd_id)
        return ChainResult(root=prd, chain=chain)
```

## Business Rules Enforcement

Business rules تُطبّق **داخل** Service methods، ليس في Repository أو MCP Handler:

| القاعدة | أين تُطبّق | مثال |
|---------|-----------|------|
| Status transitions | DocumentService | draft → reviewed → approved |
| FK integrity | ValidationService | كل doc له parent موجود |
| Test قبل Task | GraphService | Task لا يكتمل بدون Test |
| capability_matrix صحة | ValidationService | كل قدرة مرتبطة بـ domain/layer مسجلة |
| Chain completeness | OrchestrationService | PRD لازم يكون عنده ARCH قبل approval |

## Error Handling — ServiceException Hierarchy

```python
class ServiceError(Exception):
    def __init__(self, message: str, code: str = "SERVICE_ERROR"):
        self.code = code
        super().__init__(message)

class EntityNotFound(ServiceError):
    def __init__(self, doc_type: str, doc_id: str):
        self.doc_type = doc_type
        self.doc_id = doc_id
        super().__init__(f"{doc_type} '{doc_id}' غير موجود", "ENTITY_NOT_FOUND")

class InvalidTransition(ServiceError):
    def __init__(self, doc_type: str, doc_id: str, current: str, expected: str):
        super().__init__(
            f"{doc_type} '{doc_id}' في حالة '{current}'، يتطلب '{expected}'",
            "INVALID_TRANSITION")

class ValidationError(ServiceError):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("فشل التحقق: " + "; ".join(errors), "VALIDATION_ERROR")

class DuplicateEntity(ServiceError): ...
class FKNotFound(ServiceError): ...
```

## علاقته بالـ EntityRegistry

```
Service ──get/query──▶ EntityRegistry ──cache miss──▶ Repository
   │                       │                              │
   │                       │ (WeakValueDictionary)        │ (SQLite)
   │                       ▼                              │
   └────save/write────▶ EntityRegistry ──write-through──▶ Repository
```

**مبدأ رئيسي:** Service لا يعرف عن SQLite ولا عن SQL. كل تفاعل مع البيانات يتم عبر `EntityRegistry.get()` و `EntityRegistry.save()`. هذا يسمح بـ:
- Unit testing: Mock EntityRegistry بسهولة
- تغيير DB engine بدون تغيير Service
- Identity Map يظل مصدر الحقيقة للكيانات في الميموري

## Diagram — MCP Handler → Service → Registry → Repository

```
┌──────────────────────────────────────────────────┐
│                   MCP Layer                       │
│  (Thin Handlers — no business logic)             │
└──────────────────────┬───────────────────────────┘
                       │ call
                       ▼
┌──────────────────────────────────────────────────┐
│                 Service Layer                     │
│  ┌────────────┐ ┌──────────┐ ┌────────────────┐  │
│  │ Document   │ │ Graph    │ │ Orchestration  │  │
│  │ Service    │ │ Service  │ │ Service        │  │
│  └─────┬──────┘ └────┬─────┘ └───────┬────────┘  │
│        │              │               │            │
│        └──────┬───────┴───────┬───────┘            │
│               ▼               ▼                     │
│  ┌────────────────┐ ┌────────────────┐              │
│  │ EntityRegistry │ │  GraphCache   │              │
│  │ (Identity Map) │ │  (ABC→NX)    │              │
│  └───────┬────────┘ └───────┬────────┘              │
└──────────┼──────────────────┼───────────────────────┘
           │                  │
           ▼                  ▼
     ┌──────────────┐  ┌──────────────┐
     │  Repository  │  │  Repository  │
     │  (entities)  │  │  (edges)     │
     └──────┬───────┘  └──────┬───────┘
            │                  │
            ▼                  ▼
     ┌──────────────────────────┐
     │         SQLite           │
     └──────────────────────────┘
```
