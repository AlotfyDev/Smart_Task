# ذاكرة التخزين البيانية — Graph Cache Layer

## مبدأ Adapter Pattern

نفس فلسفة **Repository ABC → SQLiteRepo** و **VectorDB ABC → FAISSAdapter**: واجهة مجردة واحدة (ABC)، تنفيذات متعددة. الـ Service لا يعرف نوع الـ Graph Cache — يتعامل مع `GraphCache(ABC)` فقط.

**حاليًا:** NetworkX (in-process, ~1μs/call)
**مستقبلًا:** Memgraph, Neo4j, FalkorDB, أو أي graph engine (تغيير config فقط)

## GraphCache Factory

اختيار الـ engine يتم عبر Factory + Config (مثل بقية الـ Adapters):

```python
class GraphCacheFactory:
    @staticmethod
    def create(
        engine: str = "networkx",
        registry: EntityRegistry | None = None,
        repo: Repository | None = None,
    ) -> GraphCache:
        if engine == "networkx":
            return NetworkXGraphCache(registry, repo)
        if engine == "memgraph":
            return MemgraphGraphCache(registry, repo)   # مستقبلي
        if engine == "neo4j":
            return Neo4jGraphCache(registry, repo)      # مستقبلي
        raise ValueError(f"Unsupported graph engine: {engine}")
```

الـ Service يستقبل `GraphCache` عبر DI ولا يعرف نوع الـ engine:

```python
class GraphService:
    def __init__(self, cache: GraphCache, registry: EntityRegistry):
        self._cache = cache          # GraphCache ABC — أي engine
        self._registry = registry
```

تغيير الـ engine = تغيير config فقط، لا تغيير في Service أو Handler.

## GraphCache ABC — الواجهة المجردة

```python
from abc import ABC, abstractmethod
from typing import Any

class GraphCache(ABC):
    @abstractmethod
    def hydrate(self) -> None:
        """تحميل كل الحواف من DB."""

    @abstractmethod
    def get_neighbors(self, node_id: str, edge_type: str | None = None) -> list[str]:
        """جلب neighbors المباشرين (مع أو بدون فلترة edge_type)."""

    @abstractmethod
    def has_edge(self, source: str, target: str, edge_type: str) -> bool:
        """هل توجد حافة بين عقدتين؟"""

    @abstractmethod
    def shortest_path(self, source: str, target: str) -> list[str]:
        """أقصر مسار بين عقدتين."""

    @abstractmethod
    def subtree(self, root_id: str) -> list[str]:
        """إرجاع كل descendants لعقدة (ترافيرس عميق)."""

    @abstractmethod
    def add_edge(self, edge: Edge) -> None:
        """إضافة حافة — write-through: DB + cache."""

    @abstractmethod
    def remove_edge(self, edge_id: str) -> None:
        """حذف حافة — write-through: DB + cache."""

    @abstractmethod
    def rebuild(self) -> None:
        """إعادة تحميل كل الجراف من DB."""

    @property
    @abstractmethod
    def node_count(self) -> int: ...

    @property
    @abstractmethod
    def edge_count(self) -> int: ...
```

ملاحظة: `subtree` ترجع `list[str]` (list of IDs) بدل `nx.DiGraph` — الـ ABC لا تعرف عن NetworkX ولا تفرضه على الـ implementors.

## NetworkXGraphCache — التنفيذ الملموس

```python
import networkx as nx
from threading import Lock

class NetworkXGraphCache(GraphCache):
    def __init__(self, registry: EntityRegistry, repo: Repository):
        self._registry = registry
        self._repo = repo
        self._graph = nx.DiGraph()
        self._hydrated = False
        self._lock = Lock()
        self._node_soft_limit = 10_000

    def hydrate(self) -> None:
        with self._lock:
            if self._hydrated:
                return
            edges = self._repo.query_edges()
            for edge in edges:
                self._add_to_graph(edge)
            self._hydrated = True
            if self._graph.number_of_nodes() > self._node_soft_limit:
                logger.warning(f"GraphCache تجاوز الحد: {self._graph.number_of_nodes()} nodes")
```

**Node Attributes:** كل node تحمل (doc_type, title, status, entity_ref):

```python
def _add_to_graph(self, edge: Edge) -> None:
    # تأكد من وجود nodes المصدر والهدف
    for node_id, node_type in [(edge.source_id, edge.source_type),
                                (edge.target_id, edge.target_type)]:
        if not self._graph.has_node(node_id):
            entity = self._registry.get(node_type, node_id)
            self._graph.add_node(node_id,
                                 doc_type=node_type,
                                 title=entity.title if entity else "",
                                 status=entity.status if entity else "",
                                 entity_ref=entity)

    # أضف الحافة
    self._graph.add_edge(edge.source_id, edge.target_id,
                         id=edge.id,
                         edge_type=edge.edge_type,
                         metadata=edge.metadata)
```

## Hydration Strategy — Lazy Loading

```python
def _ensure_hydrated(self) -> None:
    if not self._hydrated:
        self.hydrate()

def get_neighbors(self, node_id: str, edge_type: str | None = None) -> list[str]:
    self._ensure_hydrated()
    if edge_type:
        return [n for n in self._graph.successors(node_id)
                if self._graph.edges[node_id, n].get("edge_type") == edge_type]
    return list(self._graph.successors(node_id))
```

**متى يُحمّل الجراف؟** Lazy — أول traversal يشغل `hydrate()`. هذا يتجنب تحميل الجراف عند start-up إذا Service ما استخدمش graph queries.

## Incremental Updates

`add_edge` و `remove_edge` يعدّلان الجراف بدون إعادة تحميل كامل:

```python
def add_edge(self, edge: Edge) -> None:
    with self._lock:
        self._repo.save_edge(edge)       # write-through: DB أولاً
        self._add_to_graph(edge)          # ثم NetworkX

def remove_edge(self, edge_id: str) -> None:
    with self._lock:
        edge = self._repo.get_edge(edge_id)
        if edge and self._graph.has_edge(edge.source_id, edge.target_id):
            self._graph.remove_edge(edge.source_id, edge.target_id)
        self._repo.delete_edge(edge_id)
```

**الترتيب مهم:** DB أولاً — لو الكراش صار، DB سليم. NetworkX ثانيًا — يعيد بناء من DB عند الـ hydrate التالي.

## Full Rebuild

متى نعمل rebuild كامل؟

```python
def rebuild(self) -> None:
    """إعادة تحميل كل الجراف من DB. يُستخدم بعد تغيير كبير (import, migration)."""
    with self._lock:
        self._graph.clear()
        self._hydrated = False
        self.hydrate()
```

**حالات تستدعي rebuild:**
- Bulk import لوثائق كاملة
- Schema migration
- تصحيح يدوي لـ DB خارج التطبيق

## Integration مع EntityRegistry

NetworkX nodes تحوي `entity_ref` — reference للـ Entity في Registry (وليس نسخة):

```python
# الوصول إلى entity من node attribute
entity = self._graph.nodes["SPEC-001"]["entity_ref"]
print(entity.title)  # "Authentication Module"
```

**لماذا reference وليس copy؟**
- تغيير entity في Registry ينعكس تلقائيًا في GraphCache
- لا تكرار بيانات في الذاكرة
- الاتساق مضمون

## Memory Consideration

NetworkX يستهلك ذاكرة لكل node (~500 bytes) و edge (~200 bytes). مع 10,000 node → ~5MB:

```python
_NODE_SOFT_LIMIT = 10_000

def hydrate(self) -> None:
    with self._lock:
        if self._hydrated:
            return
        edges = self._repo.query_edges()
        for edge in edges:
            self._add_to_graph(edge)
        self._hydrated = True
        if self._graph.number_of_nodes() > _NODE_SOFT_LIMIT:
            logger.warning(f"GraphCache تجاوز الحد الناعم: {self._graph.number_of_nodes()} nodes")
```

عند تجاوز `_NODE_SOFT_LIMIT`، نسجّل warning ونقترح:
1. تقليل عدد edges المسحوبة (فلترة بالـ edge_type)
2. إزالة الـ nodes القديمة (LRU eviction)
3. استخدام lazy subgraph بدل full graph
