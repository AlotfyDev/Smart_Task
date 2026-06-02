# طبقة التخزين — Repository Layer

## مبدأ Dumb Store

**الفلسفة:** SQLite يخزّن ويسترجع فقط. Repository ينظّم ويعالج. لا business logic في SQL.

الـ Repository ليس ORM، وليس active record. دوره الوحيد: ترجمة استدعاءات Python إلى استعلامات SQLite بسيطة، وإرجاع كائنات Entity جاهزة. أي منطق شرطي (if/else على status, joins معقدة, aggregation) ممنوع في هذه الطبقة.

```python
# ✅  مسموح: SELECT بسيط
cursor.execute("SELECT * FROM specs WHERE id = ?", (doc_id,))

# ❌ ممنوع: Business logic في SQL
cursor.execute("""
    UPDATE specs SET status = 'approved'
    WHERE id = ? AND status IN ('draft', 'reviewed')
""")
```

## Repository ABC — الواجهة المجردة

```python
from abc import ABC, abstractmethod
from typing import Any

class Repository(ABC):
    @abstractmethod
    def get(self, doc_type: str, doc_id: str) -> Entity | None: ...

    @abstractmethod
    def save(self, entity: Entity) -> None: ...

    @abstractmethod
    def delete(self, doc_type: str, doc_id: str) -> None: ...

    @abstractmethod
    def query(self, doc_type: str, filters: FilterSpec) -> list[Entity]: ...

    @abstractmethod
    def get_neighbors(self, source_id: str, edge_type: str | None = None) -> list[Edge]: ...
```

## SQLiteRepo — التنفيذ الملموس

```python
class SQLiteRepo(Repository):
    def __init__(self, db_path: str):
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
```

### Connection Pool — Thread-Safe

الاتصال حاليًا connection واحد مع `threading.Lock`. كل عملية (get, save, delete, query) تكتسب الـ lock قبل تنفيذ SQL وتحرره بعده. هذا يضمن thread safety بدون تعقيد pool connections متعددة.

```python
def _execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
    with self._lock:
        return self._conn.execute(sql, params)
```

### SQL بسيط — لا JOINs معقدة

```python
def get(self, doc_type: str, doc_id: str) -> Entity | None:
    table = _doc_type_to_table(doc_type)
    row = self._execute(f"SELECT * FROM {table} WHERE id = ?", (doc_id,)).fetchone()
    if row is None:
        return None
    return self._row_to_entity(doc_type, row)
```

**قواعد كتابة SQL في Repository:**
- كل SELECT * (لأننا نعرف الـ columns في `_row_to_entity`)
- JSON في TEXT columns يُحلل في Python (`json.loads`)، ليس في SQL
- لا JOINs — تجميع النتائج في Python إذا لزم الأمر
- لا Subqueries — استعلامان منفصلان أفضل من subquery معقدة

### JSON Parsing

```python
def _row_to_entity(self, doc_type: str, row: sqlite3.Row) -> Entity:
    data = dict(row)
    for col in _json_columns(doc_type):
        if col in data and isinstance(data[col], str):
            data[col] = json.loads(data[col])
    return EntityFactory.create(doc_type, data)
```

## Diagram — Service → Repository

```
┌─────────────┐     get / save / query     ┌──────────────┐
│   Service   │ ──────────────────────────▶ │  Repository  │
│   Layer     │                             │    (ABC)     │
└─────────────┘                             └──────┬───────┘
                                                   │ implements
                                           ┌───────▼───────┐
                                           │  SQLiteRepo   │
                                           │  (concrete)   │
                                           └───────┬───────┘
                                                   │ SQL (SELECT/INSERT/DELETE)
                                           ┌───────▼───────┐
                                           │    SQLite     │
                                           │  (db file)    │
                                           └───────────────┘
```

## Transaction Management

Context manager pattern لتجميع عمليات متعددة في transaction واحدة:

```python
@contextmanager
def transaction(self):
    with self._lock:
        self._conn.execute("BEGIN")
        try:
            yield self
            self._conn.execute("COMMIT")
        except Exception:
            self._conn.execute("ROLLBACK")
            raise
```

الـ Service يستخدمها هكذا:

```python
with repo.transaction():
    repo.save(prd_entity)
    repo.save(edge_entity)
```

## Error Handling — RepositoryException Hierarchy

```python
class RepositoryError(Exception): ...
class EntityNotFoundError(RepositoryError): ...
class DuplicateEntityError(RepositoryError): ...
class ConstraintViolationError(RepositoryError): ...
class StorageEngineError(RepositoryError): ...  # SQLite I/O errors wrapped
```

كل `get()` يفشل يرمي `EntityNotFoundError`، كل `save()` مع id مكرر يرمي `DuplicateEntityError`، SQLite integrity errors تُلف في `ConstraintViolationError`.

## FilterSpec — بناء الاستعلامات

```python
@dataclass
class FilterSpec:
    conditions: dict[str, Any]    # {"status": "draft", "chain_order": 1}
    order_by: str | None = None   # "created_at DESC"
    limit: int | None = None
    offset: int | None = None

    def to_sql(self, table: str) -> tuple[str, tuple]:
        clauses = []
        params = []
        for col, val in self.conditions.items():
            clauses.append(f"{col} = ?")
            params.append(val)
        where = " AND ".join(clauses) if clauses else "1=1"
        sql = f"SELECT * FROM {table} WHERE {where}"
        if self.order_by:
            sql += f" ORDER BY {self.order_by}"
        if self.limit:
            sql += f" LIMIT {self.limit}"
        if self.offset:
            sql += f" OFFSET {self.offset}"
        return sql, tuple(params)
```

**مبدأ مهم:** FilterSpec يبقى بسيطًا (es = equals only). لا يدعم LIKE، IN، OR. التعقيد يُرفع إلى Service layer عند الحاجة.
