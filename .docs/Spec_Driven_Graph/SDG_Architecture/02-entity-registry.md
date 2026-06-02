# سجل الكيانات — Entity Registry (Identity Map)

## مبدأ Identity Map

**المشكلة:** بدون Identity Map، كل `get()` يخلق instance Entity جديد. هذا يعني أن `repo.get("spec", "SPEC-001") is repo.get("spec", "SPEC-001")` يعيد `False` — كائنان مختلفان يمثلان نفس الصف في DB. هذا يكسر referential equality ويسبب:
- تعديلات غير متوقعة (تعدّل object ولا الـ cache يعرف)
- تكرار الذاكرة (نسخ متعددة من نفس entity)
- عدم تناسق (object قديم وآخر محدث)

**الحل:** Identity Map — pool مركزي يضمن أن لكل `(doc_type, doc_id)` instance واحد فقط في الميموري.

```python
# ✅ Identity Map يضمن:
registry.get("spec", "SPEC-001") is registry.get("spec", "SPEC-001")  # True
```

## EntityRegistry API

```python
class EntityRegistry:
    def __init__(self, repo: Repository): ...

    def get(self, doc_type: str, doc_id: str) -> Entity:
        """إرجاع entity من registry (أو يجلبها من DB ويسجلها)."""

    def get_batch(self, doc_type: str, doc_ids: list[str]) -> list[Entity]:
        """جلب مجموعة entities دفعة واحدة."""

    def register(self, entity: Entity) -> None:
        """تسجيل entity في registry (hydration)."""

    def evict(self, doc_type: str, doc_id: str) -> None:
        """إزالة entity من registry (invalidation بعد تعديل)."""

    def clear(self) -> None:
        """مسح الـ registry بالكامل (flush)."""
```

## WeakValueDictionary — لماذا؟

```python
from weakref import WeakValueDictionary

class EntityRegistry:
    def __init__(self, repo: Repository):
        self._repo = repo
        self._map: dict[str, WeakValueDictionary[str, Entity]] = {}
```

`WeakValueDictionary` يخزّن references ضعيفة للـ entities. هذا يعني:

1. **لا تسريب ذاكرة:** GC يستطيع جمع الـ entities اللي محدش يحتاجها. لو Service استخدم entity وانتهى منها، و registry هو المرجع الوحيد، GC يجمعها.
2. **لا حاجة لإدارة الـ lifecycle يدويًا:** ما فيش حاجة `remove()` لكل entity بعد الاستخدام.
3. **الـ eviction تلقائي:** لما entity تموت من GC، الـ `WeakValueDictionary` يزيل الـ entry تلقائيًا.
4. **التحذير:** الـ entity لازم يكون reference قوي خارج registry عشان تفضل حية. Service أو Cache لازم يمسك reference.

```python
_map = {
    "spec": WeakValueDictionary({"SPEC-001": <SpecEntity obj>, ...}),
    "prd":  WeakValueDictionary({"PRD-001": <PRDEntity obj>, ...}),
}
```

## Write-Through Policy

كل `save()` يكتب على DB و registry معًا:

```python
def save(self, entity: Entity) -> None:
    self._repo.save(entity)                    # 1. اكتب على DB
    self._ensure_type_map(entity.doc_type)     # 2. تأكد من وجود dict للنوع
    self._map[entity.doc_type][entity.doc_id] = entity  # 3. سجّل في registry
```

**لماذا write-through?**
- DB دائمًا محدث (لو الكراش صار، DB سليم)
- registry دائمًا محدث (لو استعلمنا بعد save مباشرة، نلقى entity محدثة)
- الـ eviction يحدث فقط في حالات نادرة (مثل تعديل يدوي على DB خارج التطبيق)

## Thread Safety

Locking strategy للـ concurrent access:

```python
class EntityRegistry:
    def __init__(self, repo: Repository):
        self._repo = repo
        self._map: dict[str, WeakValueDictionary[str, Entity]] = {}
        self._lock = threading.RLock()  # Reentrant — service قد يستدعي registry من nested calls

    def get(self, doc_type: str, doc_id: str) -> Entity:
        with self._lock:
            type_map = self._map.get(doc_type)
            if type_map and doc_id in type_map:
                return type_map[doc_id]
            entity = self._repo.get(doc_type, doc_id)
            if entity is None:
                raise EntityNotFoundError(doc_type, doc_id)
            self._ensure_type_map(doc_type)
            self._map[doc_type][doc_id] = entity
            return entity
```

`RLock` (reentrant) مهم لأن Service method قد يستدعي registry.get() أكثر من مرة في نفس call chain.

## Hydration Flow — كيف يجيب entity من DB

```
Service.get(doc_type="spec", doc_id="SPEC-001")
    │
    ▼
EntityRegistry.get("spec", "SPEC-001")
    │
    ├── Is "SPEC-001" in _map["spec"]?
    │   ├── Yes → return cached instance (identity guaranteed)
    │   └── No  → continue
    │
    ▼
Repository.get("spec", "SPEC-001")
    │
    ▼
SQLiteRepo: SELECT * FROM specs WHERE id = 'SPEC-001'
    │
    ▼
Row → EntityFactory.create("spec", row_dict) → SpecEntity
    │
    ▼
EntityRegistry.register(entity) → _map["spec"]["SPEC-001"] = entity
    │
    ▼
Return entity
```

## Diagram — العلاقات

```
┌──────────────┐
│   Service    │
│   Layer      │
└──────┬───────┘
       │ get(entity)
       ▼
┌──────────────────┐
│ EntityRegistry   │ ◄── WeakValueDictionary pool
│ Identity Map     │
└──────┬───────────┘
       │ get (cache miss)
       ▼
┌──────────────┐
│  Repository  │
│  (SQLiteRepo)│
└──────────────┘
```

الـ Service لا يعرف عن الـ SQLite أبدًا. يتعامل مع `EntityRegistry` كـ "مصدر الحقيقة للكيانات في الميموري".
