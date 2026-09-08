# Declarative Reaction Rule DSL

Status: **F1 semantic contract; concrete serialization deferred to F2**

## 1. Rule ownership

Each rule definition owns one stable `rule_*` ID, semantic version, evidence, and resolution relationships. There is no separate canonical `RuleReference` record.

## 2. Conceptual shape

```yaml
id: rule_...
version: 1.0.0
family: precipitation
decision_domain: aqueous_double_displacement
match:
  participants: []
required_facets: []
context_predicates: []
conditions: []
exceptions: []
blockers: []
resolution:
  specializes: []
  overrides: []
  fallback_for: []
products: []
postmatch: []
validators: [atom_balance, charge_balance]
evidence_ids: []
```

## 3. Semantic requirements

A rule may express:

- match patterns and bindings;
- required/forbidden facets;
- typed relation bindings;
- context predicates;
- conditions;
- exceptions;
- blockers;
- explicit precedence/resolution edges;
- product templates/constructors;
- postmatch predicates;
- validators/postconditions;
- evidence;
- rule version.

## 4. Determinism

Rule semantics cannot depend on source file order, YAML map order, hash-map iteration order, or arbitrary integer priority alone.

Matching and resolution operate on canonical typed values and stable semantic operators.

## 5. Three-valued predicates

Predicate results may be TRUE, FALSE, or UNKNOWN. Operators must declare their UNKNOWN behavior. Rules cannot silently treat missing open-world facts as false.

## 6. Product constructors

Product constructors return canonical IDs or resolvable semantic descriptors. They do not own balancing coefficients and do not emit final equation text.

## 7. Resolution graph

Supported semantic relationships may include:

- `specializes`;
- `overrides`;
- `fallback_for`;
- `equivalent_to`;
- `mutually_exclusive_with`.

Cycles/contradictions in precedence/fallback graphs are compile errors. Potential overlap with incompatible effects requires an explicit relationship or proof of disjointness.

## 8. Validation boundary

Validators confirm conservation and declared postconditions after candidate product identity is fixed. Canonical reaction lookup is downstream and cannot be used to decide what products should be.

## 9. Versioning and provenance

Changing chemistry-bearing semantics requires a rule-version change according to the future compatibility policy. Proof traces record rule ID/version and evidence so generated candidates remain auditable across compiler releases.
