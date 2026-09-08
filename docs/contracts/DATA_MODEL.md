# Canonical Data Model

Status: **F3A executable subset over the F1 canonical model**

F3A hardens only the source records needed to prove reusable deterministic reaction inference. It does not narrow the broader F1 ontology or claim that the small executable schema is the final high-school chemistry corpus schema.

## 1. Stable identity

Canonical chemical identity remains independent from names, formulas, teaching paths, source file paths, and runtime IDs.

The executable Entity kinds remain:

```text
element | species | substance | material_system
```

`species_kind` carries microscopic refinements such as `ion`; macroscopic `Substance` and composed `MaterialSystem` remain separate concepts.

## 2. Composition

Exact stoichiometric composition remains an embedded value object on its owner. It provides the atom/charge information used by exact balancing and conservation validation.

Formula/semantic keys are lookup coordinates, not identity owners.

## 3. Fact / facet semantics

An authored facet assertion may declare:

```yaml
facet_key: electrolyte.strong_in_water
fact_kind: contextual
value_state: known
value: true
```

`fact_kind` is one of:

- `intrinsic` — intended to hold independent of an inference request context within the model boundary;
- `contextual` — meaningful only under an appropriate context;
- `derived` — deterministically derived from canonical data/rules.

Value state distinguishes:

- `known` with a value, including boolean `false`;
- explicit `unknown`;
- `not_applicable`;
- source absence/open-world knowledge, represented by no assertion and observed by the compiler as `absent`.

No rule may silently coerce absence, explicit unknown, or not-applicable into known false.

## 4. Reaction

A canonical `Reaction` owns one curated transformation. Embedded participants identify canonical entities, role, phase, and exact stoichiometric coefficient.

Reaction identity is independent from equation text, participant order, coefficient scaling, or teaching placement.

## 5. ReactionForm

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
```

A form may change referent level from macroscopic substances to ionic species only under declared assumptions. Missing assumptions make the projection unavailable rather than causing the compiler to guess speciation.

Half-reactions remain independent `Reaction` records because they are distinct transformations.

## 6. Rule

A Rule owns stable rule identity, semantic version, decision domain, evidence, participant patterns, predicates/blockers, product construction, validators, and explicit resolution relationships.

Participant patterns may combine exact identity and typed semantic constraints. Ordinary reusable families should normally be expressible through source Rule records without adding chemistry-specific branches to the engine.

F3A predicates are typed against `context` or a bound entity facet. The source vocabulary is intentionally small and versioned.

## 7. Rule relationship graph

Rules can declare:

```text
overrides
specializes
fallback_for
equivalent_to
mutually_exclusive_with
```

Unknown references, invalid cycles, contradictory declarations, and unresolved potentially conflicting overlaps are compile-time errors.

Rule/file order is not semantic precedence.

## 8. Product construction

A Rule product may be:

```yaml
- target_id: ent_substance_h2o
  phase: liquid
```

or a bounded canonical resolver request:

```yaml
- construct:
    kind: semantic_key
    scheme: formula.unit
    value: AgCl
  phase: solid
```

Resolution must return exactly one existing canonical entity. Zero or multiple matches remain explicit failures. The compiler never fabricates canonical identity and does not resolve variable-valence ambiguity without canonical chemistry/context evidence.

## 9. ReactionCandidate

A generated candidate remains separate from canonical Reaction source. It contains a deterministic `candidate_key`, selected Rule identity/version, normalized participants, validation results, canonical comparison, and proof trace.

An exact canonical match does not promote or mutate a candidate into canonical knowledge.

## 10. Diagnostics

Compiler/inference failures are represented by structured diagnostics carrying stable code, stage, message, and deterministic details. F3A distinguishes at least schema/reference errors, rule overlap and ambiguity, unknown applicability, blockers, product resolution, balancing, conservation, and canonical comparison outcomes.

## 11. Artifact compatibility

F3A generated artifacts expose independent versions for source schema, Rule DSL, internal RulePlan, and external artifact format. External consumers gate compatibility on the artifact format version rather than assuming a compiler package version implies payload compatibility.
