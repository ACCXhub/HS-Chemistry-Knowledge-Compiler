# Declarative Reaction Rule DSL

Status: **M4 Chemistry Model Convergence executable semantic contract**

## 1. Ownership and version

Each authored Rule owns one stable `rule_*` ID, semantic version, evidence, and explicit resolution relationships. The Rule DSL version is independent from source-schema, compiler-plan, and external-artifact versions.

M4 Rule DSL version: `1.0.0`.

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

M4 exposes only these source operators:

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

Legacy F2 `context: {key: value}` authoring lowers to the same typed `equals/context` semantics. M4 intentionally has no arbitrary-expression language.

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

M4 supports bounded canonical constructors:

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

`ionic_pair` resolves the canonical cation/anion from bound aqueous speciation profiles, charge-balances their exact compositions, and selects one existing neutral Substance. `exchange_product` reuses the same bounded exchange resolution to select the unique precipitate or soluble counterproduct. Zero or multiple matches are explicit failures.

## 7. Rule-resolution relationships

Rules may declare:

- `overrides`;
- `specializes`;
- `fallback_for`;
- `equivalent_to`;
- `mutually_exclusive_with`.

Unknown references, self edges, contradictory equivalent declarations, and precedence cycles are compile errors. File order, definition order, and arbitrary integer priority are never semantic tie-breakers.

## 8. Static overlap analysis

Within a `decision_domain`, M4 analyzes participant count/kind, exact identity, required/forbidden facets, and simple context-equality constraints. If it cannot prove disjointness it emits conservative `potential_overlap`.

Non-equivalent overlapping outcomes require an explicit relationship or strict compilation fails with both rule IDs and a deterministic reason/signature.

## 9. Validation boundary

Rules fix canonical product identity before exact balancing. Validators then check conservation/postconditions. Canonical reaction lookup is downstream comparison and never an inference oracle.
