# Schema Strategy

Status: **draft storage and compilation strategy for `workstream/data-contracts`**

This document chooses how canonical source records are authored, validated, versioned, and compiled during the current Git-first phase.

## 1. Decision summary

Use:

- **YAML** for curated editable source data;
- **JSON Schema** for machine validation of source contracts;
- **JSON/JSONL** for normalized generated artifacts and interchange;
- **SQLite only as an optional generated index/cache**, never as the current editable canonical source;
- **Git** as the source-history and review system.

Do not introduce a production database service in this phase.

## 2. Alternatives evaluated

| Format | Strengths | Weaknesses | Role |
|---|---|---|---|
| YAML | human-readable, review-friendly, supports structured nested records, low ceremony | parser differences, duplicate-key hazards, less ideal for streaming | **canonical curated source** |
| JSON | strict, ubiquitous tooling, close to schema validators | noisy for hand editing, no comments | normalized artifact / fixtures |
| JSONL | streamable, append/partition friendly, efficient for large machine datasets | poor for nested multi-record hand editing and comments | **generated datasets / large staging imports** |
| SQLite | queryable, indexed, compact, transactions | binary diff/merge, weak Git review, hidden mutation history | optional **generated** query index only |
| production DB | concurrency, transactions, service integration | unnecessary operational complexity and makes Git review less central | out of scope until a concrete runtime need exists |

## 3. Canonical repository layout

Recommended initial layout:

```text
README.md
docs/
  DATA_MODEL.md
  IDENTITY_AND_PROVENANCE.md
  SCHEMA_STRATEGY.md
schemas/
  draft/
    data-contracts.schema.json
data/
  source/
    entities/
    facts/
    relations/
    reactions/
    contexts/
    conditions/
    evidence/
    sources/
    teaching_views/
    rules/
  staging/
    legacy/
    imports/
  generated/
    .gitkeep              # generated artifacts may later be ignored or release-only
```

The directory path is organizational only. It never contributes to record identity.

## 4. YAML source package shape

Curated YAML should use small reviewable packages rather than requiring one file per record or one monolithic file.

Example:

```yaml
schema_version: 0.1.0
package:
  package_key: inorganic.core-species
  description: Core curated inorganic identities
records:
  - id: ent_01991c2e-7a10-7a01-8a01-000000000003
    record_type: entity
    schema_version: 0.1.0
    record_revision: 1
    status: active
    entity_kind: species
    semantic_keys:
      - {scheme: formula.molecular, value: H2SO4}
    terms:
      preferred:
        - {lang: zh-CN, value: 硫酸分子}
    payload:
      composition_ref: cmp_01991c2e-7a10-7a02-8a01-000000000003
      formal_charge: 0
      structure_refs: []
```

Package rules:

1. `package_key` is for ownership/navigation, not record identity.
2. Records can move between files/packages without ID changes.
3. Prefer coherent files small enough for meaningful code review.
4. Duplicate YAML mapping keys are validation errors.
5. YAML anchors/merge keys should be disallowed in canonical chemistry data unless a future compiler explicitly normalizes them; hidden alias expansion makes audits harder.

## 5. Source vs staging vs generated

### 5.1 `data/source/`

Only curated records that satisfy schema, reference, evidence, and semantic validation.

This is the canonical editable data layer.

### 5.2 `data/staging/`

Non-canonical imported material:

- legacy `chem-knowledge-data` snapshots;
- external extracts;
- unresolved aliases;
- inference review fixtures;
- migration mapping reports.

Staging records may use JSONL when volume makes it useful. A staging record is not canonical merely because it lives in Git.

### 5.3 `data/generated/`

Compiler products only. Examples:

```text
data/generated/entities.jsonl
data/generated/facts.jsonl
data/generated/reactions.jsonl
data/generated/teaching-view-index.json
data/generated/knowledge.sqlite
data/generated/manifest.json
```

Generated files must be reproducible from `data/source/` + schema/rule inputs + compiler version. Whether large generated artifacts are committed, attached to releases, or ignored can be decided later; they never become the editable truth owner.

## 6. JSON Schema role

The JSON Schema under `schemas/draft/` is a machine-readable companion to the prose contracts.

Schema validation should cover structural invariants such as:

- required fields;
- record-type enumerations;
- ID prefix/UUID shape;
- `value_state` vocabulary;
- reaction candidate provenance fields;
- coefficient shape;
- valid status fields.

JSON Schema is not sufficient for chemistry semantics. The compiler/validator layer must later perform cross-record checks.

## 7. Validation layers

Validation should be deterministic and ordered.

### Layer 1 — parse/canonicalize

- parse YAML safely;
- reject duplicate keys;
- normalize line endings and scalar representations;
- prohibit unsupported YAML features.

### Layer 2 — schema validation

- validate each record against the record-type schema;
- validate ID prefix and required fields;
- validate enums and primitive types.

### Layer 3 — reference integrity

Examples:

- `composition.subject_entity_id` exists;
- all composition component elements exist and are element entities;
- `ReactionParticipant.reaction_id` resolves to a canonical reaction;
- teaching path members resolve;
- evidence references resolve to evidence records and sources;
- `ReactionCandidate.canonical_match.reaction_id`, when present, resolves to `rxn_*`.

### Layer 4 — semantic invariants

Examples:

- element atomic numbers are positive and unique;
- known ion charge is integral;
- composition charge agrees with ion payload where applicable;
- reaction participant coefficients are positive rational values;
- canonical reactions are balance-checkable when their representation requires it;
- contextual facts point to context records;
- derived facts contain derivation provenance;
- `value_state: unknown` does not contain a fake fallback value.

### Layer 5 — provenance/evidence policy

- nontrivial curated assertions have evidence or auditable derivation;
- generated records identify source snapshot/compiler;
- reaction candidates preserve rule/input/exception/validation/proof metadata;
- generated candidate records are not loaded as canonical reactions.

### Layer 6 — compilation

Only validated source records enter deterministic generated artifacts.

## 8. Deterministic compilation

For the same:

- source Git commit;
- schema version;
- compiler version;
- rule definitions;

compilation should produce byte-stable normalized artifacts wherever practical.

The compiler should:

1. load source packages independent of file traversal order;
2. validate IDs and references;
3. sort normalized records by stable ID before serialization;
4. serialize JSON deterministically;
5. emit source/record indexes;
6. generate teaching projections from `TeachingViewPath`, never by changing entity identity;
7. keep inferred candidates in a separate output namespace;
8. emit a build manifest with hashes.

Example manifest:

```json
{
  "schema_version": "0.1.0",
  "compiler": "hs-chem-compiler",
  "compiler_version": "0.1.0",
  "source_git_sha": "<sha>",
  "source_digest": "sha256:<digest>",
  "outputs": [
    {"path": "entities.jsonl", "sha256": "<digest>"},
    {"path": "reactions.jsonl", "sha256": "<digest>"},
    {"path": "reaction-candidates.jsonl", "sha256": "<digest>"}
  ]
}
```

## 9. Canonical reaction artifact boundary

Compiled reaction outputs must preserve two channels:

```text
canonical reactions      <- curated `record_type: reaction`
reaction candidates      <- generated `record_type: reaction_candidate`
```

A consumer must never need heuristics to distinguish them.

Recommended output split:

```text
generated/reactions.jsonl
generated/reaction-candidates.jsonl
```

The candidate file may include canonical-match metadata, but canonical matches do not get copied into `reactions.jsonl` unless a real canonical source record exists.

## 10. Schema evolution

Use semantic versioning for the data contract while it remains practical:

- patch: clarifications/constraints that do not require source rewrites;
- minor: backwards-compatible optional fields or new record types;
- major: incompatible field semantics/required-shape changes.

During the current draft phase, schemas live under `schemas/draft/`. Stabilization should be an explicit milestone, not inferred from usage.

Schema migrations should be deterministic scripts/tools that:

1. read an old schema version;
2. transform the structure without changing permanent IDs unless concepts truly split/merge;
3. preserve audit metadata;
4. update `schema_version`;
5. produce a reviewable Git diff.

## 11. File and package ownership

A future contributor may reorganize source packages for reviewability. The following are never identity-bearing:

- filename;
- directory;
- YAML document order;
- array order where semantically unordered;
- package key;
- teaching-view path.

Where order is meaningful, the contract must say so explicitly, e.g. `TeachingViewPath.ordering`.

## 12. SQLite boundary

SQLite is useful later for local queries, compiler inspection, and tests, but only as a generated artifact:

```text
YAML source
  -> validate/normalize
  -> JSONL canonical artifacts
  -> optional SQLite index
```

The SQLite file must be disposable and regenerable. No manual chemistry edit is permitted only inside SQLite.

A production database becomes justified only if a later runtime needs features such as concurrent writes, user-owned mutable data, remote query service SLAs, or transactional workflows that Git source cannot provide. None of those needs exists in this workstream.

## 13. Migration strategy from legacy `chem-knowledge-data`

Legacy data is migration input, not a schema parent.

Recommended migration pipeline:

```text
legacy files
  -> staging importer
  -> normalized legacy rows with source locator
  -> identity reconciliation
  -> proposed new records
  -> validation + review
  -> curated `data/source/`
```

Mapping principles:

| Legacy shape | New destination |
|---|---|
| name/formula used as ID | `semantic_keys` / aliases plus newly minted `ent_*` |
| textbook/category path | `FacetAssertion` and/or `TeachingViewPath` |
| embedded property columns | `PropertyFact` + optional `Context` |
| relationship-like columns | `Relation` |
| equation strings | parsed `Reaction` + `ReactionParticipant` only after review |
| legacy source metadata | `Source` + `Evidence` |
| generated relation/reaction rows | generated provenance / `ReactionCandidate`, not canonical truth |

The importer should emit reconciliation warnings instead of preserving a legacy conflation. For example, if a legacy record uses one row for an element concept, bulk elemental substance, and reaction participant, the new model may split those concepts and link them explicitly.

## 14. Initial implementation sequence after this contract

This workstream does not implement the compiler, but the contract supports the following next steps:

1. stabilize draft JSON Schema;
2. add safe YAML loader + structural validator;
3. add cross-reference index and reference validation;
4. seed a small curated chemistry fixture containing the examples in `DATA_MODEL.md`;
5. add deterministic JSONL compiler and build manifest;
6. only then add migration tooling and inference-engine consumers.

This order protects the new architecture from becoming a thin wrapper around legacy data.
