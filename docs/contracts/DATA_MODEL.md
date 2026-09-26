# Canonical Data Model

[简体中文](DATA_MODEL.zh-CN.md)

Status: **Executable source contract through M25**

This document defines canonical source-record semantics. M4 converges the executable Rule/fact/speciation/TeachingView/ReactionForm/artifact subset without narrowing the broader model.

## 1. Top-level identity-bearing records

Canonical source records include:

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
  preferred: ...
  aliases: []
payload:
  species_kind: ion
  composition: {}
  formal_charge: -1
  structure_ids: []
relation_assertions:
  - relation_key: metal.product_cation
    target_id: ent_species_...
    context: {medium: aqueous}
    evidence_ids: [ev_...]
```

`species_kind` may be atom/ion/molecule/etc. `Substance` describes pure macroscopic material identity. `MaterialSystem` describes solution/mixture/system composition.

Formula strings and semantic keys are lookup/representation coordinates, not durable identity owners.

## 3. Embedded composition

`Composition` is an exact embedded value object on its owner rather than a top-level identity record by default.

```yaml
composition:
  components:
    - element_id: ent_element_h
      count: 2
    - element_id: ent_element_o
      count: 1
  net_charge: 0
```

Exact composition/charge supplies the conservation data used by deterministic balancing. Source validation rejects repeated element components, disagreement between formal and net charge, duplicate facet keys, and atom/charge imbalance in canonical Reactions, ReactionForms, and speciation profiles. Non-stoichiometric mixtures/material systems use appropriate quantitative components rather than fake integer formula counts.

## 4. Structure

`Structure` is a stable domain object distinct from any representation.

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

Representations never replace structure identity. Bonds remain embedded structure components by default unless an independent lifecycle later justifies top-level identity.

## 5. Assertion / fact semantics

An authored assertion distinguishes semantic origin:

```text
intrinsic | contextual | derived
```

and knowledge state:

```text
known(value, including boolean false)
explicit unknown
not_applicable
absent/open-world
```

`absent` is not serialized as a fabricated source assertion; it is the compiler-observed state when no matching assertion exists.

Executable contextual property example:

```yaml
property_key: electrolyte.strength
fact_kind: contextual
value_state: known
value: strong
context: {medium: aqueous}
evidence_ids: [ev_...]
```

Stable classifications such as acid, base, salt, chloride, sulfate, and hydrogen-carbonate remain facets.

No rule may silently coerce absence, explicit unknown, or not-applicable into known false.

A separately identity-bearing fact/assertion may additionally own durable provenance/revision metadata when its lifecycle requires it.

M10's minimum executable Relation is embedded on its source Entity:

```yaml
relation_assertions:
  - relation_key: metal.product_cation
    target_id: ent_species_zn_2plus
    truth: true  # optional; defaults to true
    context: {medium: aqueous}
    evidence_ids: [ev_...]
```

The relation key is controlled and its domain/range are validated semantically after reference resolution. For `metal.product_cation` and `metal.displaces_cation`, the source must be an elemental `Substance` with known-true `classification.metal`, and the target must be a positively charged ion `Species`. For `ion.elemental_substance`, the source is a positively charged ion `Species` and the target is an elemental `Substance` with known-true `classification.metal`. An ordinary embedded assertion has no durable relation UUID; deterministic lookup/provenance retains source ID, relation key, target ID, resolved truth, normalized context, and evidence IDs.

Each relation family declares positive-target cardinality. `metal.product_cation` and `ion.elemental_substance` permit one positive target per source/context. `metal.displaces_cation` permits multiple distinct positive targets per source/context. `truth: false` records a known negative without consuming positive-target cardinality. Exact duplicates and same-tuple positive/negative contradictions are rejected. Resolution selects the most-specific matching assertions; equally specific assertions with one truth value merge evidence, while mixed truth is an explicit semantic error. Target-producing resolution exposes only positive assertions. Absence remains an open-world fact state, not false.

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

Context dimension keys and enums are controlled vocabularies. M4's executable request fixture currently uses only a deliberately small scalar subset; that implementation subset does not narrow this canonical model.

## 7. Reaction

A canonical `Reaction` owns one curated chemical transformation:

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

Participants and conditions are embedded values. Reaction identity is independent from equation text, participant order, coefficient scaling, or teaching placement.

M7's executable condition subset is an ordered-insensitive list of evidence-bearing controlled values:

```yaml
conditions:
  - key: medium
    value: aqueous
    evidence_ids: [ev_...]
  - key: temperature_regime
    value: warmed
    evidence_ids: [ev_...]
```

Condition keys are unique within a Reaction. They are requirements for canonical comparison, not a demand that request context equal the Reaction condition object exactly; additional request dimensions are allowed.

The active scalar `temperature_regime` vocabulary is `ambient | warmed | heated`. `heated` is a distinct controlled value, not an alias or ordering inference for `warmed`. M16 uses the existing generic scalar context/condition comparison path; no temperature-specific runtime semantics are implied.

## 8. ReactionForm

`ReactionForm` is a representation/projection of the owning Reaction when the underlying transformation is the same.

```yaml
forms:
  - form_key: net_ionic
    form_kind: net_ionic
    participants: []
    projection:
      method: aqueous_strong_electrolyte_v1
      required_assumptions:
        - aqueous_medium
        - strong_electrolyte_dissociation
      notes: []
```

A form may change referent level from macroscopic substances to ionic species only under declared assumptions. M4 derives aqueous forms only from unique context-matching canonical speciation profiles; missing assumptions/speciation remain explicit rather than causing guessed speciation.

Molecular, complete-ionic, net-ionic, and thermochemical forms may coexist for one transformation. Half-reactions remain independent `Reaction` records because they are chemically distinct transformations.

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
  relation_assertions: []
```

Pure compilation mints no time-based review UUID. An exact canonical match does not promote or mutate a candidate into canonical knowledge.

A separately persisted human-review object may own a durable `rcand_*` ID while retaining the immutable deterministic `candidate_key`.

## 10. Rule

`Rule` owns `rule_*` identity, semantic version, decision domain, evidence, matching constraints, predicates/blockers, product construction, validators, and explicit resolution relationships. There is no separate canonical `RuleReference` record.

M4 participant patterns may combine:

- exact `target_id` where chemistry is identity-specific;
- `entity_kind`;
- `species_kind`;
- participant `phase`;
- required facets;
- forbidden facets.

The typed predicate registry supports `equals`, `not_equals`, `is_known`, and `in_set` over their declared subjects. A Relation predicate accepts `equals expected: true`, one valid source binding, one controlled relation key, and exactly one of an exact canonical `target_id` or typed `target_source`. A target source may resolve one signed ion from a bound participant's canonical speciation. This is a bounded executable vocabulary, not an arbitrary expression or graph-query language.

Rule relationships are:

```text
overrides
specializes
fallback_for
equivalent_to
mutually_exclusive_with
```

Unknown references, invalid precedence cycles, contradictory declarations, and unresolved non-equivalent potential overlaps are compile-time failures. Rule/file order is not semantic precedence.

### Product construction

A product may use an exact canonical ID:

```yaml
- target_id: ent_substance_h2o
  phase: liquid
```

or bounded semantic-key/ionic-pair/exchange-product resolvers:

```yaml
- construct:
    kind: semantic_key
    scheme: formula.unit
    value: AgCl
  phase: solid
```

Resolution must return exactly one existing canonical Entity. Zero or multiple matches remain explicit failures. The compiler never fabricates canonical identity and does not guess variable valence or other chemically ambiguous identities.

M10 extends `ionic_pair` with typed ion sources:

```yaml
- phase: aqueous
  construct:
    kind: ionic_pair
    cation_source:
      {kind: relation_target, binding: metal, relation_key: metal.product_cation}
    anion_source:
      {kind: speciation, binding: acid}
```

Once both canonical ion Species resolve, the existing neutral ionic-pair resolver remains the sole owner of exact charge/composition matching. Historical `cation_from`/`anion_from` Rule source remains valid and lowers to equivalent `speciation` ion sources.

M11 adds an exact canonical ion source:

```yaml
anion_source:
  kind: exact_entity
  target_id: ent_species_oh_minus
```

The target must resolve to a canonical ion Species with the sign required by its cation/anion position. This source carries no reactant binding and does not create a speciation assertion for water or any other Entity.

M19 adds a shared `EntitySourcePlan` with four closed forms: exact canonical entity, participant binding, unique signed ion from a bound participant's context-matching speciation, and one Relation target whose source is one of the non-Relation forms. Relation-to-Relation nesting is invalid. An `entity_source` product resolves exactly one existing canonical Entity and carries consumed speciation/assertion evidence; it never parses a formula or mints identity.

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

Teaching paths/nodes are embedded and view-local. A path may change without changing chemistry identity. Teaching views project canonical chemistry; they do not own or redefine chemical identity.

## 12. Source and Evidence

`Source` identifies a publication/database/standard/manual. `Evidence` locates/interprets a claim in a source and can support, qualify, or contradict a curated assertion, relation, reaction, teaching claim, or rule.

Evidence/provenance must remain traceable through compiler output when a generated result depends on it.

## 13. External generated artifacts

External generated artifacts remain contract-owned and reproducible. The four compatibility coordinates remain independent:

| Coordinate | Current value |
| --- | --- |
| source schema | `3.7.0` |
| Rule DSL | `1.4.0` |
| internal RulePlan | `1.4.0` |
| external artifact format | `1.5.0` |

Manifests carry all four coordinates. External payloads carry `artifact_format_version`; consumers must reject unsupported artifact-format versions rather than inferring payload compatibility from compiler package version alone.

Artifact `1.5.0` is required because externally emitted compiled plans now contain nested `EntitySourcePlan` values in `PredicatePlan.target_source` and `ProductPlan.entity_source`. The reference reader still accepts artifact formats `1.0.0` through `1.4.0`.

Compiler-internal plans, indexes, caches, and dense runtime IDs remain implementation details rather than canonical source contracts.
