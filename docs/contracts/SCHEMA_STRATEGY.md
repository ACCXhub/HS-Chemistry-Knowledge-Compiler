# Schema Strategy

Status: **M10 relation assertion, typed ion-source, and artifact contract**

## 1. Authoring boundary

Canonical chemistry remains human-reviewable YAML. Structural validation uses JSON Schema Draft 2020-12, followed by compiler-owned semantic validation. Runtime layout, indexes, and `RulePlan` remain generated implementation details and are not authoring contracts.

M4 keeps the principle that file layout is not identity-bearing. Stable IDs and semantic content determine meaning; source traversal order does not.

## 2. Active source schema

The active source schema is:

```text
schemas/knowledge-record.schema.json
source schema version: 3.2.0
```

It covers the M4 executable subset of:

- Entity;
- embedded typed Entity relation assertions;
- Reaction / ReactionForm;
- TeachingView;
- Rule;
- Source;
- Evidence.

`schemas/f2-record.schema.json` remains historical F2 material. The M4 loader does not use it as the active source contract.

`schemas/f2-case.schema.json` remains the deterministic audit/example request schema because M4 does not broaden the request surface.

## 3. Validation order

M4 validation is deliberately staged:

1. safe YAML parsing with duplicate-key rejection;
2. JSON Schema validation;
3. stable-ID uniqueness and reference validation;
4. entity/participant/relation-target semantic validation;
5. typed predicate/operator and ion-source validation;
6. Rule lowering to compiler-owned `RulePlan`/`IonSourcePlan`;
7. rule relationship graph validation;
8. conservative overlap/conflict analysis;
9. inference-time product resolution;
10. exact balancing and atom/charge validation;
11. participant-signature canonical Reaction lookup;
12. required-condition compatibility filtering.

Malformed or semantically ambiguous source is rejected rather than repaired by hidden defaults.

## 4. Fact and facet state

Facet assertions may state `fact_kind` as:

```text
intrinsic | contextual | derived
```

Knowledge state distinguishes:

```text
known
unknown
not_applicable
absent
```

`absent` is the compiler observation that no matching assertion is present; it is not serialized as a fabricated source assertion. A known boolean `false` remains distinct from every non-known state.

## 5. Rule source contract

A participant pattern may constrain a binding by:

- exact canonical `target_id` when identity-specific behavior is required;
- `entity_kind`;
- `species_kind`;
- required facets;
- forbidden facets.

Predicates use the versioned Rule DSL operator names rather than Python function names. M4 intentionally supports a small registry only: `equals`, `not_equals`, `is_known`, and `in_set`.

Rule relationships are explicit source semantics: `overrides`, `specializes`, `fallback_for`, `equivalent_to`, and `mutually_exclusive_with`.

Product templates may use an exact canonical ID or bounded semantic-key, ionic-pair, and exchange-product resolvers. M10 ionic-pair products may source each ion from canonical speciation or a controlled one-hop relation target; construction uses canonical compositions/speciation/relations and never creates a new canonical entity. Historical `cation_from`/`anion_from` syntax remains accepted and lowers to speciation ion sources.

## 6. ReactionForm projection contract

`ReactionForm` remains subordinate to its canonical `Reaction`. A projection declares:

```yaml
projection:
  method: aqueous_strong_electrolyte_v1
  required_assumptions: []
  notes: []
```

A consumer/compiler may expose the form only when the required assumptions and canonical context-matching speciation are available. Projection does not mint a second Reaction identity.

## 7. Version axes

M4 separates four compatibility coordinates:

| Coordinate | M10 value | Owner |
| --- | --- | --- |
| source schema | `3.2.0` | source/data contract |
| Rule DSL | `1.1.0` | rule source contract |
| compiler RulePlan | `1.1.0` | compiler internal contract |
| external artifact format | `1.2.0` | external generated contract |

These axes are intentionally independent. A source schema change does not automatically imply an external artifact-format change, and an internal RulePlan revision is not a source DSL revision by definition.

M4 does not promise long-term backward compatibility beyond these explicit coordinates.

The `1.2.0` reader accepts historical artifact formats `1.0.0` and `1.1.0`. Existing source Reaction records may omit `conditions`, Entity records may omit `relation_assertions`, and legacy ionic-pair Rules may retain `cation_from`/`anion_from`. The artifact bump is independently required because `compiled-rule-plans.json` now emits nested typed ion-source objects that a `1.1.0` consumer cannot safely interpret.

## 8. Generated artifacts

M4 emits deterministic JSON artifacts under caller-selected build output. Manifests carry all four version coordinates. External payloads carry `artifact_format_version`; compiled plans additionally identify `rule_plan_version`.

Consumers must reject an artifact format version they do not support. The reference compiler exposes validation for this compatibility gate.

Generated artifacts remain reproducible outputs and never become editable chemistry truth.

## 9. Deterministic serialization

F2 canonical JSON rules remain in force:

- UTF-8;
- NFC normalization of strings and mapping keys;
- lexicographically sorted mapping keys;
- compact JSON separators;
- integer-only semantic numeric domain;
- no timestamps, local paths, process IDs, or traversal-order metadata in semantic identities.

The same canonicalization continues to protect semantic digests and deterministic candidate keys.
