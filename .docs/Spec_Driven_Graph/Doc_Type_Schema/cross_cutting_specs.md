# مخطط كيان وثيقة المواصفات العرضية (Cross-Cutting Spec Schema)

## 1. تعريف

المواصفات العرضية (Cross-Cutting Concerns) هي متطلبات ومبادئ تسري على نطاق النظام ككل أو على عدة مكونات/نطاقات فرعية، ولا تنتمي حصريا إلى Spec واحد. تشمل: الثوابت (invariants)، المراقبة (observability)، الأمان (security)، الأداء (performance)، التوافق (compatibility)، والتشغيل (operational).

فصل هذه المواصفات في كيان مستقل يمنع تكرارها عبر ملفات Specs متعددة، ويجعل تتبعها والتحقق منها مركزيا. كل سجل من هذا النوع يرتبط بواحد أو أكثر من الـ domains/components عبر doc_edges.

## 2. DDL

```sql
CREATE TABLE cross_cutting_specs (
    id                 TEXT PRIMARY KEY,      -- XSPEC-001
    title              TEXT NOT NULL,
    status             TEXT NOT NULL CHECK (status IN ('draft', 'reviewed', 'approved', 'superseded')),
    cc_type            TEXT NOT NULL,         -- 'invariant' | 'observability' | 'security' | 'performance' | 'compatibility' | 'operational'
    specification      TEXT NOT NULL,          -- JSON: التفاصيل حسب الـ type
    applies_to_domains TEXT,                   -- JSON: domains اللي ينطبق عليهم (null = ALL)
    rationale          TEXT,                   -- ليه موجود ده
    verification       TEXT,                   -- إزاي نتحقق منه
    satisfies_req      TEXT,                   -- JSON: PRD req IDs
    version            TEXT NOT NULL DEFAULT '1.0',
    tags               TEXT NOT NULL DEFAULT '[]',
    created_at         TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at         TEXT NOT NULL DEFAULT (datetime('now'))
);
```

## 3. شرح الحقول

| الحقل | النوع | إلزامي | مثال JSON | الغرض الدلالي |
|-------|-------|--------|-----------|---------------|
| `id` | TEXT | نعم | `"XSPEC-001"` | معرّف فريد للمواصفة العرضية، بادئة XSPEC |
| `title` | TEXT | نعم | `"ثبات توازن دفتر الأوامر"` | عنوان وصفي واضح |
| `status` | TEXT | نعم | `"draft"` | مرحلة النضج: draft → reviewed → approved → superseded |
| `cc_type` | TEXT | نعم | `"invariant"` | تصنيف الاهتمام العرضي (أنظر الجدول أدناه) |
| `specification` | TEXT | نعم | `"{\\"rule\\": \\"sum(bids) == sum(asks)\\", \\"enforcement\\": \\"reject\\"}"` | جسم المواصفة – بنية JSON تتغير حسب cc_type |
| `applies_to_domains` | TEXT | لا | `"[\"order-book\", \"matching-engine\"]"` | النطاقات المنطبقة عليها؛ null يعني كل النطاقات |
| `rationale` | TEXT | لا | `"ضمان اتساق البيانات قبل وبعد كل صفقة"` | المبرر المنطقي لوجود هذه المواصفة |
| `verification` | TEXT | لا | `"تشغيل اختبار InvariantTest كل 1000 مللي"` | كيفية التحقق من الالتزام بها (اختبار، رصد، مراجعة) |
| `satisfies_req` | TEXT | لا | `"[\"REQ-007\", \"REQ-012\"]"` | معرفات متطلبات PRD التي تحققها هذه المواصفة |
| `version` | TEXT | لا (default `'1.0'`) | `"2.1"` | إصدار المواصفة للتحكم في التغيير |
| `tags` | TEXT | لا (default `'[]'`) | `"[\"critical\", \"compliance\"]"` | وسوم للتصنيف والبحث |
| `created_at` | TEXT | لا (default now) | `"2026-01-15T10:00:00Z"` | طابع زمني للإنشاء |
| `updated_at` | TEXT | لا (default now) | `"2026-03-01T14:30:00Z"` | طابع زمني لآخر تعديل |

## 4. قيم cc_type

| cc_type | المعنى | محتوى specification المتوقع (JSON) |
|---------|--------|-----------------------------------|
| `invariant` | ثابت (constraint) يجب أن يظل صحيحا في كل الأوقات | `{"rule": "تعبير منطقي", "scope": "نطاق التطبيق", "enforcement": "reject | warn | log"}` |
| `observability` | مراقبة وقياس وتتبع السلوك | `{"metrics": ["قائمة المقاييس"], "logging": {...}, "alert_rules": [...], "dashboard_ref": "..."}` |
| `security` | أمان وسرية وسلامة البيانات | `{"policy": "سياسة", "authentication": {...}, "authorization": {...}, "encryption": {...}, "audit": "..."}` |
| `performance` | أداء وزمن استجابة وإنتاجية | `{"latency_p99": "value", "throughput": "value", "concurrency": number, "scalability": "..."}` |
| `compatibility` | توافق مع أنظمة أو إصدارات أو واجهات خارجية | `{"interfaces": [...], "versions": [...], "protocols": [...], "backwards": boolean}` |
| `operational` | تشغيل ونشر واستضافة | `{"deployment": "strategy", "recovery": {...}, "backup": {...}, "maintenance_window": "..."}` |

## 5. الربط عبر الحواف (doc_edges)

الـ CrossCuttingSpecs ترتبط بالـ Specs عبر جدول doc_edges كالتالي:

- **edge_type = `references`**: الـ Spec يشير إلى CrossCuttingSpec كمصدر معلومة أو تفصيل إضافي. مثال: MatchingEngineSpec.references = XSPEC-001 (ثبات توازن الدفتر).
- **edge_type = `constrained_by`**: الـ Spec مقيد بالـ CrossCuttingSpec ويجب ألا يخالفه. مثال: OrderBookSpec.constrained_by = XSPEC-002 (سياسة الأمان).
- **from_type**: `spec`
- **to_type**: `cross_cutting_spec`

يمكن للـ CrossCuttingSpec الواحد أن يرتبط بعدة Specs من عدة نطاقات، مما يتيح تتبع تأثير أي تعديل في المواصفة العرضية على جميع المكونات المتأثرة.
