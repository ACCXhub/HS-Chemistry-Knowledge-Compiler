# Canonical Data Model

Status: **F1 canonical source-contract semantics**

This document defines conceptual source record shapes. Exact YAML/JSON Schema syntax is finalized in F2.

## 1. Top-level identity-bearing records

Canonical F1 top-level records include:

- `Entity` (`element | species | substance | material_system`);
- `Structure`;
- `Reaction`;
- `TeachingView`;
- `Rule`;
- `Source`;
- `Evidence`;
- independently curated/evidenced `FacetAssertion`, `PropertyFact`, and `Relation` when durable assertion identity is required;
- optional reusable `Experiment`.

A record receives a durable ID only when an independent lifecycle or durable reference requires it.

## 2. Entity

Conceptual shape:

```yaml
id: ent_...
record_type: entity
entity_kind: species
semantic_keys: []
terms:
  preferred: []
  aliases: []
payload:
  species_kind: ion
  composition: {}
  formal_charge: -1
  structure_ids: []
```

`species_kind` may be atom/ion/molecule/etc. `substance` payload describes pure material identity. `material_system` payload describes solution/mixture/system composition.

Formula strings are representations/semantic lookup keys, not durable IDs.

## 3. Embedded composition

`Composition` is an exact value object on its owner rather than a top-level `cmp_*` record by default.

```yaml
composition:
  components:
    - element_id: ent_element_h
      count: 2
    - element_id: ent_element_o
      count: 1
  net_charge: 0
```

Non-stoichiometric mixture/system composition uses appropriate quantitative components rather than fake integer formula counts.

## 4. Structure

```yaml
id: str_...
record_type: structure
structure_kind: molecular_connectivity
subject_ids: [ent_...]
components: []
bonds:
  - key: b1
    from: a1
    to: a2
    order: 1
motifs: []
representations:
  - kind: smiles
    value: CCO
```

Representations never replace structure identity.

## 5. Assertion semantics

A fact/assertion envelope includes:

```yaml
id: fact_...
subject_id: ent_...
fact_kind: contextual
value_state: known
context: {}
evidence_ids: [ev_...]
derivation: null
```

`value_state` distinguishes known, unknown, and not-applicable. No record means no assertion.

`FacetAssertion` and `Relation` use the same fact-state/context/provenance principles.

## 6. Embedded Context

`Context` is a structured qualifier bundle, not a top-level record by default:

```yaml
context:
  phase: aqueous
  solvent_id: ent_water
  temperature: {number: 298.15, unit: K}
  pressure: {number: 100, unit: kPa}
  concentration_regime: dilute
```

Context dimension keys and enums are controlled vocabularies.

## 7. Reaction

```yaml
id: rxn_...
record_type: reaction
participants:
  - target_id: ent_...
    target_kind: substance
    role: reactant
    coefficient: {numerator: 1, denominator: 1}
    phase: aqueous
conditions: []
forms: []
facet_assertions: []
evidence_ids: [ev_...]
```

Participants and conditions are embedded values. The display equation is compiled from semantic participants/forms.

## 8. ReactionForm

```yaml
forms:
  - form_key: net_ionic
    form_kind: net_ionic
    participants: []
    projection:
      method: aqueous_strong_electrolyte_v1
      assumptions: []
```

Molecular, complete ionic, net ionic, and thermochemical forms may coexist for one reaction when they represent the same transformation.

Half-reactions are separate `Reaction` records linked by typed relations.

## 9. ReactionCandidate

Generated candidate:

```yaml
record_type: reaction_candidate
candidate_key: cand_sha256_...
proposed_participants: []
proposed_conditions: []
provenance:
  rule_id: rule_...
  rule_version: 1.0.0
  input_ids: []
  validation_results: []
  canonical_match: {}
  proof_trace: []
```

No time-based ID is minted during pure compilation.

Persistent review object:

```yaml
id: rcand_...
candidate_key: cand_sha256_...
review_status: pending
```

Promotion creates/edits canonical `rxn_*` source separately.

## 10. Rule

`Rule` owns `rule_*` identity directly. Other records reference the ID; there is no separate `RuleReference` source type.

## 11. TeachingView

```yaml
id: view_...
record_type: teaching_view
view_key: hs-cn-framework-11
nodes:
  - path_key: D08/substances/inorganic/acids
    parent_path_key: D08/substances/inorganic
    members: []
```

View nodes/paths are embedded and view-local.

## 12. Source and Evidence

`Source` identifies a publication/database/standard/manual. `Evidence` locates and interprets a claim in a source and can support or qualify a curated assertion, relation, reaction, teaching claim, or rule.

## 13. External generated artifacts

The exact emitted artifact contract is owned here. F2 must define:

- manifest schema;
- stable-ID/runtime-ID mapping contract;
- candidate artifact schema;
- proof-trace external schema;
- artifact versioning/compatibility rules;
- deterministic canonical serialization used for semantic hashes.

Compiler-internal plans and indexes are explicitly out of scope for this document.
