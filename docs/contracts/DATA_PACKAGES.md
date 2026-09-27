# Element, substance and equation datasets

[简体中文](DATA_PACKAGES.zh-CN.md)

Compiler 0.6.0 implements `export-modules`. All modules reuse canonical IDs, record schemas, evidence and exact coefficients rather than creating parallel knowledge stores.

```powershell
python -m compiler.cli export-modules --output build/data-modules --source-revision WORKTREE
```

Use a verified clean checkout and full commit SHA for release. Output contains manifest.json, knowledge-record.schema.json and three JSON datasets. Full inference deployment still uses `export` and InferenceSession; these modules are import/query dictionaries, not runtime plugins replacing the complete knowledge snapshot.

| File | Root records | Included dependencies |
| --- | --- | --- |
| elements.json | Element Entities: symbols, atomic numbers, reviewed properties | Evidence and Sources |
| substances.json | All non-Element Entities: Substances, Species including ions, MaterialSystems | Elements, referenced species/substances, Evidence/Sources |
| equations.json | Reactions with subordinate forms, and Rules | Participants, Rule targets, elements, Evidence/Sources |

MaterialSystems remain distinct from directly balanceable pure substances. Each module includes its transitive reference closure and can be distributed independently. Shared dependencies retain identical IDs/content. TeachingViews remain available in the full bundle but are not roots of these datasets.

Each document contains module_format_version (1.0.0), module_id, source_schema_version (3.8.0), source_semantic_digest (full snapshot), record_digest (this module), sorted root_ids, sorted dependency_ids and records sorted by record_type/id. Root and dependency IDs are disjoint and together identify exactly the exported records.

The manifest records source revision, compiler/version coordinates, file SHA-256 hashes, counts and release_id. Its ID is `hschem_modules_` plus the canonical manifest hash excluding release_id. Record digests exclude trailing newlines; file hashes include LF. Export reuses schema, uniqueness, reference, chemistry and Rule compilation checks for every standalone module.

Import a trusted fixed release, verify hashes/versions/digests/closure, and only combine modules with the same source_semantic_digest. Merge records by canonical ID; shared dependencies must have identical content or import fails. Count roots separately from dependencies. Import release, records and reviewed application-ID mappings transactionally and idempotently. Missing facts must never become FALSE.

Use composition, charge and participant identities for reviewed mappings. Names, Chinese aliases and formulas are search signals, not identity authority. Preserve Source/Evidence for explanations and integer numerator/denominator coefficients for exact normalization. Keep Rules as declarative records/in-memory plans, not SQL inference machinery.

For chem-wiki reuse knowledge_catalog release/crosswalk/read models and reaction_core materialization. Unsupported application shapes remain catalog-only. See the [Chinese integration note](CHEM_WIKI_INTEGRATION.md). For a new site, minimal import storage consists of a release table, a canonical record table keyed by (release_id, canonical_id) with kind plus JSONB payload, and reviewed UUID mappings. Project the three modules by kind/root membership; add typed columns/indexes only for real queries.

Later analogy/model proposals should retain supporting examples, counterexamples, missing conditions, conservation results, model/Rule versions and review state separately from curated records. Missing identities/composition must be curated rather than fabricated from names. Dataset export does not itself implement automatic learning or prove curriculum completeness.
