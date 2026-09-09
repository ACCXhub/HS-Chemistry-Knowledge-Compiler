# Declarative Reaction Rule DSL

Status: **M10 typed ionic-pair ion sources**

## 1. Ownership and version

Each authored Rule owns one stable `rule_*` ID, semantic version, evidence, and explicit resolution relationships. The Rule DSL version is independent from source-schema, compiler-plan, and external-artifact versions.

M10 advances Rule DSL to `1.1.0` because an `ionic_pair` product may now declare typed `cation_source` and `anion_source` values. RulePlan advances independently to `1.1.0` for the lowered `IonSourcePlan` representation. Reaction conditions remain part of the Reaction source contract, not the Rule DSL.

## 2. Participant patterns

A reactant pattern binds one canonical participant and may constrain:

```yaml
- bind: chloride_salt
  entity_kind: substance
  species_kind: ion        # only when relevant
  target_id: ent_...       # optional exact identity
  required_facets: []
  forbidden_facets: []
```

`target_id` is optional. Pattern identity/kind constraints establish possible bindings; facet constraints are evaluated with open-world three-valued semantics so missing knowledge does not become false.

## 3. Typed predicates

The current DSL exposes only these source operators:

| Operator | Subjects | Input types | Expected argument | UNKNOWN behavior |
| --- | --- | --- | --- | --- |
| `equals` | context, facet, property, ionic_exchange | string / boolean / integer | one scalar | non-known fact → UNKNOWN |
| `not_equals` | context, facet, property, ionic_exchange | string / boolean / integer | one scalar | non-known fact → UNKNOWN |
| `is_known` | context, facet, property, ionic_exchange | any fact state | none | returns TRUE only for known; otherwise FALSE |
| `in_set` | context, facet, property | string / boolean / integer | homogeneous non-empty scalar list | non-known fact → UNKNOWN |

Example:

```yaml
predicates:
  - operator: equals
    subject: context
    key: medium
    expected: aqueous
```

Legacy F2 `context: {key: value}` authoring lowers to the same typed `equals/context` semantics. M6 intentionally has no arbitrary-expression or disjunction language.

## 4. Knowledge states

Applicability preserves:

```text
known(value, including false)
explicit unknown
not_applicable
absent/open-world
```

and traces fact origin as intrinsic, contextual, or derived. Except for epistemic operators such as `is_known`, non-known states propagate as `UNKNOWN` rather than false.

## 5. Blockers

Blockers use the same typed predicate semantics. A true blocker blocks that rule path; an unknown blocker makes that path indeterminate. Blockers are not integer-priority shortcuts.

## 6. Product constructors

The current DSL supports bounded canonical constructors:

```yaml
products:
  - phase: solid
    target_id: ent_substance_agcl
```

or:

```yaml
products:
  - phase: solid
    construct:
      kind: semantic_key
      scheme: formula.unit
      value: AgCl
```

A constructor must resolve to exactly one existing canonical Entity. It never invents identity and does not own balancing coefficients.

`ionic_pair` resolves a canonical cation and anion from independently typed sources, charge-balances their exact compositions, and selects one existing neutral Substance. The M10 syntax is:

```yaml
construct:
  kind: ionic_pair
  cation_source:
    kind: relation_target
    binding: metal
    relation_key: metal.product_cation
  anion_source:
    kind: speciation
    binding: acid
```

`speciation` selects the unique sign-appropriate ion from the bound Entity's context-matching aqueous profile. `relation_target` performs one controlled, context-aware relation lookup and requires one target. It is not arbitrary graph traversal. Legacy `cation_from`/`anion_from` authoring is still valid and lowers to two `speciation` sources.

`exchange_product` reuses the same bounded exchange resolution to select the unique precipitate or soluble counterproduct. Zero or multiple product/ion/relation matches are explicit failures.

Ionic-pair resolution returns speciation-profile provenance and relation-assertion provenance separately, including the evidence actually used. This is deterministic compiler output metadata, not a new chemistry truth owner or formula parser.

## 7. Rule-resolution relationships

Rules may declare:

- `overrides`;
- `specializes`;
- `fallback_for`;
- `equivalent_to`;
- `mutually_exclusive_with`.

Unknown references, self edges, contradictory equivalent declarations, and precedence cycles are compile errors. File order, definition order, and arbitrary integer priority are never semantic tie-breakers.

## 8. Static overlap analysis

Within a `decision_domain`, the compiler analyzes participant count/kind, exact identity, required/forbidden facets, and simple context-equality constraints. If it cannot prove disjointness it emits conservative `potential_overlap`.

Non-equivalent overlapping outcomes require an explicit relationship or strict compilation fails with both rule IDs and a deterministic reason/signature.

## 9. Validation boundary

Rules fix canonical product identity before exact balancing. Validators then check conservation/postconditions. Canonical reaction lookup is downstream comparison and never an inference oracle.
