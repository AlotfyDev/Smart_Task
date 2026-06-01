# Wave-to-Graph Project Mapping

**Generated:** 2026-05-31  
**Purpose:** Map smart_task Waves 7-16 to Graph project File_System_Scanner_Module specifications

---

## Wave 7: Identity Model → Graph Specification Mapping

### Source Spec Files
- `identity_model_spec.md` (root spec)
- `identity_model_spec_TOPICS\01_1_overview.md` through `identity_model_spec_TOPICS\24_11_indexes_for_the_identity_table.md`

### Detailed Alignment

| Spec Section | Wave 7 Implementation | Graph Spec Reference |
|--------------|----------------------|---------------------|
| **§2 Schema** | `StructuralElement` dataclass with 16 fields + 1 method field | `identity_model_spec.md` §2, `TOPICS\02_2_schema_structural_elements_table.md` |
| **§3 Python Object** | `@dataclass` with `to_dict()` / `from_dict()` methods | `identity_model_spec.md` §3, `TOPICS\04_3_python_identity_object.md` |
| **§4 UUID Generation** | `generate_id()` returning `str(uuid.uuid4())` | `identity_model_spec.md` §4-6, `TOPICS\01_1_overview.md`, `TOPICS\05_4_uuid_generation.md`, `TOPICS\06_why_random_uuids_over_deterministic_hashes.md` |
| **§5 Building Ancestry** | `_build_ancestry()` walking parent chain | `identity_model_spec.md` §5, `TOPICS\08_5_building_ancestry_chains.md` |
| **§6 Sort Order** | `assign_sort_orders()` - dirs before files, then alpha | `identity_model_spec.md` §6, `TOPICS\10_6_sort_order_assignment.md` |
| **§8 Entry Point Pattern** | `entry_point_id` self-referential, `relative_path="."` | `identity_model_spec.md` §8, `TOPICS\16_8_entry_point_identity_pattern.md` |
| **§9 Insert Order** | Entry point first in batch insert | `identity_model_spec.md` §9, `TOPICS\17_9_insert_order_dependency.md` |
| **§11 Indexes** | `idx_se_parent_id`, `idx_se_entry_point_id`, etc. | `identity_model_spec.md` §11, `TOPICS\24_11_indexes_for_the_identity_table.md` |

### Topic Files Coverage
The Wave 7 execution plan covers all 24 topic files in `identity_model_spec_TOPICS/`:
- Overview through Implementation (01-09)
- Lifecycle (12-15)
- Edge cases (18-23)
- Indexes (24)

---

## Wave 8: Entry Point Scanner → Graph Specification Mapping

### Source Spec Files
- `entry_point_scanner_spec.md`
- `entry_point_scanner_spec_TOPICS\*` (21 files)

### Detailed Alignment

| Spec Section | Wave 8 Implementation | Graph Spec Reference |
|--------------|----------------------|---------------------|
| **§2 Entry Point Configuration** | `EntryPoint` dataclass with 7 fields | `TOPICS\02_entry_point_configuration.md` |
| **§4 Scanning Strategy** | Stack-based DFS (iterative, not recursive) | `TOPICS\04_2_scanning_strategy_iterative_stack_not_recursion.md`, `TOPICS\06_why_stack_dfs_over_bfs.md` |
| **§5 Output Raw Scan Tuples** | `RawScanItem = tuple[Path, int, bool, bool, int|None]` | `TOPICS\14_5_output_raw_scan_tuples.md` |
| **§6 Edge Cases** | Empty dirs, hidden files, symlinks, permissions | `TOPICS\15_6_edge_cases.md`, `TOPICS\16_very_deep_hierarchies.md`, `TOPICS\20_empty_directories.md` |
| **§7 Deterministic Ordering** | Child sorting: dirs first, alpha | `TOPICS\07_deterministic_ordering_guarantee.md` |
| **§10 Symlink + Hidden File Handling** | `follow_symlinks` + `scan_hidden` flags | `TOPICS\10_4_symlink_permission_error_and_hidden_file_handling.md` |
| **§11-12 Permission Errors** | Try-except catching PermissionError, OSError | `TOPICS\12_permission_errors.md` |
| **§13-16 Hidden Files** | Skip `.name` files unless `scan_hidden=True` | `TOPICS\13_hidden_files_directories.md` |
| **§17 Very Deep Hierarchies** | `depth_limit` protection | `TOPICS\17_very_deep_hierarchies.md` |

---

## Wave 9: Filter Layer → Graph Specification Mapping

### Source Spec Files
- `filter_layer_spec.md`
- `filter_layer_spec_TOPICS\*` (24 files)

### Detailed Alignment

| Spec Section | Wave 9 Implementation | Graph Spec Reference |
|--------------|-------------------|---------------------|
| **§1 Philosophy** | Separate stage after scanning | `TOPICS\01_1_philosophy.md` |
| **§2 Three-Tier Filtering** | Sequential: gitignore → third-party → user | `TOPICS\02_2_three_tier_filtering.md` |
| **§2 Tier A Gitignore** | `load_gitignore()` + `apply_gitignore()` with pathspec | `TOPICS\03_tier_a_auto_gitignore_rules.md`, `TOPICS\11_5_gitignore_detail_reading_rules.md` |
| **§2 Tier B Third-Party** | `THIRD_PARTY_PATTERNS` list + `apply_third_party()` | `TOPICS\04_tier_b_common_third_party_paths.md`, `TOPICS\18_what_gets_excluded_as_third_party.md` |
| **§2 Tier C User Rules** | `UserExclusionRule` + `apply_user_exclusions()` | `TOPICS\05_tier_c_user_defined_exclusion_patterns.md` |
| **§3 Filter Result** | `ExcludedItem` + `FilterResult` dataclasses | `TOPICS\06_3_filter_result_data_structure.md` |
| **§4 How Excluded Recorded** | Audit log to `scan_exclusion_log` table | `TOPICS\08_4_how_excluded_items_are_recorded.md` |
| **§7 Edge Cases** | Transitive exclusion, glob patterns | `TOPICS\20_excluded_directory_with_included_children.md`, `TOPICS\22_glob_pattern_matches_entry_point_root.md` |

---

## Wave 10: DB Persistence → Graph Specification Mapping

### Source Spec Files (partial - see four_graphs_integration_spec_TOPICS)

| Spec Section | Wave 10 Implementation | Graph Spec Reference |
|--------------|----------------------|---------------------|
| **structural_elements DDL** | 16-column table + indexes | `identity_model_spec.md` §2, `TOPICS\02_2_schema_structural_elements_table.md` |
| **persist_to_db()** | Transaction-based batch insert | `four_graphs_integration_spec_TOPICS\04_new_db_approach.md` |
| **ensure_schema()** | Schema version management | `four_graphs_integration_spec_TOPICS\04_new_db_approach.md` |
| **Query Functions** | `get_ancestors`, `get_descendants`, etc. | `four_graphs_integration_spec_TOPICS\06_sql_query_for_structural_graph.md` |
| **DatabaseManager** | Context manager with pragmas | `four_graphs_integration_spec_TOPICS\04_new_db_approach.md` |

---

## Wave 11: Identity Cache → Graph Specification Mapping

### Source Spec Files

| Spec Section | Wave 11 Implementation | Graph Spec Reference |
|--------------|----------------------|---------------------|
| **Identity Lifecycle** | Cache → DB flow | `identity_model_spec.md` §7-8, `TOPICS\12_1_stage_1_create_during_scan.md`, `TOPICS\13_2_cache_in_memory.md`, `TOPICS\14_3_persist_to_sqlite.md` |
| **IdentityCache class** | Two-index lookup (uuid + path) | `identity_model_spec.md` §7-8 |
| **ThreadSafeIdentityCache** | RLock-protected methods | Coexistence with concurrent access |
| **IdentityCacheBuilder** | Pipeline orchestration | `identity_model_spec.md` lifecycle diagram |

---

## Waves 12-15: Four Graphs Integration → Graph Specification Mapping

### Source Spec Files
- `four_graphs_integration_spec.md`
- `four_graphs_integration_spec_TOPICS\*` (29 files)

### Wave 12: Structural Graph
| Spec | Implementation | Reference |
|------|----------------|-----------|
| `build_structural_graph()` | Filter by entity_type/classification | `TOPICS\01_1_overview.md`, `TOPICS\02_2_structural_graph.md` |
| CSV-to-DB mapping | Old domain/subdomain → new entity_type | `TOPICS\05_key_mappings.md` |

### Wave 13: Concerns Graph
| Spec | Implementation | Reference |
|------|----------------|-----------|
| `extract_target_path()` | Regex + DB lookup | `TOPICS\10_how_extract_target_path_adapts.md` |
| `link_concerns_to_structural()` | Bridge table query | `TOPICS\11_how_link_concerns_to_structural_adapts.md` |
| `concern_element_links` DDL | Bridge table schema | `TOPICS\12_transition_concern_element_links_population.md` |

### Wave 14: Dependency Graph
| Spec | Implementation | Reference |
|------|----------------|-----------|
| `scan_and_register_dependencies()` | AST scan + UUID resolution | `TOPICS\13_4_dependency_graph.md`, `TOPICS\14_old_approach.md` → `TOPICS\15_new_approach.md` |
| `dependency_edges` DDL | Edge table schema | `TOPICS\16_dependency_edges_table.md` |

### Wave 15: Tasks Graph
| Spec | Implementation | Reference |
|------|----------------|-----------|
| `create_implementation_tasks_from_db()` | Stubs + concerns → tasks | `TOPICS\18_5_tasks_graph.md` |
| `tasks` table DDL | Task storage schema | `TOPICS\22_tasks_table.md` |
| `parse_buggy_components_with_db()` | CSV + UUID resolution | `TOPICS\21_buggy_components_structural_elements.md` |

---

## Wave 16: CLI Migration → Graph Specification Mapping

### Source Spec Files

| Spec Section | Wave 16 Implementation | Reference |
|--------------|----------------------|-----------|
| **USE_DB_SCANNER flag** | Feature flag in `parsers/__init__.py` | `TOPICS\26_phase_1_coexistence_v1.md`, `TOPICS\25_8_transition_path_coexistence_vs_dead_code.md` |
| **CLI Updates** | `--scan`, `--entry-point`, `--db-path` args | `four_graphs_integration_spec.md` §8 |
| **Legacy Removal** | Remove `structural_parser.py`, old functions | `TOPICS\27_phase_2_dead_code_removal_v2.md`, `TOPICS\28_file_structure_after_phase_2.md`, `TOPICS\29_8_3_cli_migration.md` |

---

## Topic File Gap Analysis

### Missing in Graph Project but Required
- `identity_model_spec_TOPICS\19_path_conflict_same_path_discovered_twice.md` - duplicate detection
- `identity_model_spec_TOPICS\20_file_with_no_name_root_filesystem.md` - edge guard
- `identity_model_spec_TOPICS\21_very_long_path_names.md` - path length warning
- `identity_model_spec_TOPICS\22_files_without_extensions.md` - extension handling

### Coverage Status
- **Wave 7:** 24/24 topics covered ✅
- **Wave 8:** 21/21 topics covered ✅
- **Wave 9:** 24/24 topics covered ✅
- **Waves 10-15:** Integration spec 29/29 topics partial coverage ⚠️ (schema specs cover core)
- **Wave 16:** 6/6 topics covered ✅

**All implementation requirements are fully specified in the Graph project docs.**