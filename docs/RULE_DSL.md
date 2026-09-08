# Declarative Reaction Rule DSL

## 1. Purpose

This document defines the semantic requirements of the reaction-rule DSL. The source notation is language-neutral. YAML is used only as the readable authoring example because the current data-contract strategy is YAML + JSON Schema; an equivalent representation is valid only if it preserves the same semantics.

A rule is declarative knowledge. It states:

- what semantic reactant/context pattern can match;
- what facts, facets, relations, and bindings are required;
- what knowledge blocks or excludes the rule;
- how overlap with other rules is resolved;
- how unbalanced semantic products are constructed;
- what product-dependent conditions must hold;
- what validators are required;
- what evidence supports the rule;
- what stable `RuleReference` and rule revision produced a derivation.

The DSL must not contain arbitrary host-language callbacks.

## 2. Alignment with canonical identity

Canonical Data Contracts defines `RuleReference` as the durable identity owner for inference rules:

```text
rule_* stable ID
+ readable rule_key
+ rule_version
```

Rule source therefore references the stable `rule_*` record and may repeat/verify its readable key for reviewability:

```yaml
rule_ref: rule_01991c2e-7b00-7001-8000-000000000001
rule_key: reaction.metal_dilute_nonoxidizing_acid
rule_version: 1
```

`rule_key` is a semantic lookup key; it is not the permanent identity. Provenance emitted into `ReactionCandidate` uses `rule_ref`.

`dsl_version` is a separate compatibility axis for the rule language itself.

## 3. Design principles

1. **Canonical refs over names/formulas.** Executable semantics use canonical identities and controlled vocabulary keys.
2. **Open-world logic by default.** Missing facts are `UNKNOWN`.
3. **No file-order semantics.** Moving rule files cannot change chemistry behavior.
4. **No bare numeric priority semantics.** Overlap is resolved by explicit semantic relationships.
5. **Products before coefficients.** Rules construct product identities/queries; balancing owns normal coefficients.
6. **Representation-aware identity.** Product queries specify enough semantic layer/context to avoid conflating substance, species, ion, and display formula.
7. **Pure operators only.** Predicates/constructors are deterministic versioned DSL operators, not arbitrary Python/Rust/C++ functions.
8. **Traceable evaluation.** Applicability-affecting expressions receive stable compiled expression IDs.
9. **Strict compilation.** Unresolved refs, unsafe UNKNOWN handling, precedence cycles, or unresolved potential conflicts block strict bundle emission.

## 4. Source envelope

Illustrative package:

```yaml
dsl_version: hsckc.rule/v1
namespace: hs.reaction
rules:
  - rule_ref: rule_01991c2e-7b00-7001-8000-000000000001
    rule_key: reaction.example
    rule_version: 1
    ...
```

Changing whitespace, comments, source path, or a non-semantic label does not change rule semantics. Changing match logic, context requirements, precedence, products, UNKNOWN behavior, or validators increments the canonical rule revision/version according to the data contract.

## 5. Product-producing rule shape

```yaml
rule_ref: <stable rule_* ref>
rule_key: <readable semantic key>
rule_version: <integer revision/version>
family: <rule-family key>
decision_domain: <overlap/conflict domain>

match:
  representation: <molecular | ionic | net_ionic | conceptual | ...>
  reactants: [...role patterns...]
  context: [...context constraints...]

bind:
  - <typed relation/fact binding>

when:
  all: [...three-valued predicates...]

exceptions:
  - <named exception predicate>

blockers:
  - <named blocker predicate>

construct:
  products: [...semantic product expressions...]

postmatch:
  all: [...predicates requiring resolved products...]

resolution:
  overrides: [...rule_* refs...]
  specializes: [...rule_* refs...]
  fallback_for: [...rule_* refs...]
  equivalent_to: [...rule_* refs...]
  mutually_exclusive_with: [...rule_* refs...]

validation:
  require: [...validator keys...]

provenance:
  evidence: [...ev_* refs...]
  rationale: <optional short authored rationale>
```

A blocking specialization may use declarative `effect: block` instead of `construct`, but it participates in the same match, truth, precedence, evidence, and trace semantics.

## 6. Match patterns

### 6.1 Reactant roles

```yaml
match:
  representation: molecular
  reactants:
    - bind: metal
      kind: chemical_entity
      require_facets:
        all: [facet.elemental_character.metal]
    - bind: acid
      kind: chemical_entity
      require_facets:
        all: [facet.inorganic_family.acid]
```

The exact facet keys are canonical vocabulary refs owned by the ontology/contracts; keys here illustrate their role.

Role matching is multiset-based unless ordered roles are explicitly required. `A + B` does not depend on user input order.

If multiple symmetric binding permutations satisfy a rule, runtime canonicalizes by stable entity IDs and verifies semantic equivalence. It never chooses a permutation because it appeared first.

### 6.2 Facet constraints

At least:

```yaml
require_facets:
  all: [facet.a, facet.b]
  any: [facet.c, facet.d]
forbid_facets:
  any: [facet.e]
```

A zero bit in an optimized facet bitset is not automatically false. Missing open-world membership remains `UNKNOWN` unless the canonical contracts define completeness for that scheme/scope.

### 6.3 Context constraints

Context is sparse and semantic:

```yaml
match:
  context:
    medium: aqueous
    concentration_regime: dilute
```

The concrete qualifier field/key vocabulary is contract-owned. A missing required context dimension evaluates to `UNKNOWN`.

## 7. Typed bindings

Rules bind semantic values through canonical relations/facts rather than parsing labels.

```yaml
bind:
  - name: metal_cation
    relation: relation.forms_cation_in_nonoxidizing_acid
    subject: $metal
    context: $context
    cardinality: exactly_one

  - name: acid_anion
    relation: relation.is_conjugate_base_of_inverse
    subject: $acid
    cardinality: exactly_one
```

The relation vocabulary may choose a different canonical direction/key; the rule compiler resolves only registered typed relations.

Cardinality semantics:

- zero results: unresolved/`UNKNOWN` unless the relation domain is explicitly complete and zero is definite;
- one result: bind;
- multiple results under `exactly_one`: candidate is ambiguous.

Rules cannot pick “the first” relation target.

## 8. Predicate expressions and three-valued logic

### 8.1 Primitive forms

Illustrative primitives:

```yaml
- id: activity_check
  predicate: relation.activity_above
  args: [$metal, entity.reference.hydrogen]
  expect: TRUE

- id: medium_check
  fact: context.medium
  op: eq
  value: aqueous

- id: solubility_check
  fact_of: $product1
  property: property.solubility_class
  context: $context
  op: eq
  value: insoluble
```

Every operator defines input types, output type, three-valued behavior, deterministic semantics, and trace encoding.

### 8.2 Composition

Predicates compose with `all`, `any`, and `not` under strong Kleene logic.

```yaml
when:
  all:
    - <predicate A>
    - any:
        - <predicate B>
        - <predicate C>
```

### 8.3 UNKNOWN handling

Normative default:

```yaml
on_unknown: indeterminate
```

A rule cannot declare `unknown_as_false: true` for open-world chemistry.

If a canonical completeness contract later proves a missing assertion is a definite negative, that conversion occurs before rule evaluation and is recorded in the proof trace. Closed-world policy is not duplicated inside individual rules.

Advisory predicates may declare:

```yaml
affects_applicability: false
```

but cannot influence product identity, precedence, or validation.

## 9. Conditions, exceptions, blockers

`when`
: positive applicability conditions.

`exceptions`
: cases intentionally outside this rule's coverage. `TRUE` makes this rule inapplicable; another specialization may apply.

`blockers`
: definite reasons not to produce this family candidate in the current context.

For exceptions/blockers, `UNKNOWN` remains indeterminate.

Example blocker:

```yaml
blockers:
  - id: oxidizing_behavior
    predicate: property.is_oxidizing_acid_under
    args: [$acid, $context]
    expect: TRUE
    effect: block
```

## 10. Product construction

### 10.1 Constructor algebra

The DSL exposes a small versioned algebra of pure semantic constructors. They return canonical refs or canonical entity queries; they never create canonical source entities.

Illustrative operators:

```text
entity(ref)
ionic_product(cation, anion, representation, context)
exchange_ions(cation_a, anion_a, cation_b, anion_b, representation, context)
relation_target(subject, relation, context)
```

`ionic_product` does not mean “make a molecule.” It means construct a query for the canonical reaction participant appropriate to the requested representation/context from the bound ions.

### 10.2 Unbalanced products

```yaml
construct:
  products:
    - bind: salt_product
      ionic_product:
        cation: $metal_cation
        anion: $acid_anion
        representation: $representation
        context: $context
    - bind: hydrogen_product
      entity: entity.species.hydrogen
```

No normal stoichiometric coefficient is authored here.

### 10.3 Rare balance constraints

A future DSL may expose audited exact `balance_constraints` only when coefficients carry independent chemistry not derivable from atom/charge conservation. Such rules require evidence/rationale and compiler warnings.

None of the baseline families below requires manual coefficients.

## 11. Product-dependent postmatch predicates

Some applicability conditions require resolved products. Precipitation is the baseline case.

```yaml
postmatch:
  any:
    - fact_of: $product1
      property: property.solubility_class
      context: $context
      op: eq
      value: insoluble
    - fact_of: $product2
      property: property.solubility_class
      context: $context
      op: eq
      value: insoluble
```

Semantics:

- `TRUE`: candidate remains applicable;
- `FALSE`: candidate is definitely inapplicable;
- `UNKNOWN`: candidate is indeterminate.

This is distinct from chemical validation. A false driving-force condition means “this rule does not apply,” not “the selected equation is invalid.”

## 12. Explicit rule resolution

### 12.1 Decision domain

Rules that can compete for one input decision declare a domain, e.g.:

```text
reaction.metal_acid
reaction.metal_salt_solution
reaction.acid_base
reaction.acid_carbonate
reaction.double_displacement_precipitation
```

This bounds conflict analysis without requiring a general-purpose production system.

### 12.2 Resolution relations

`overrides`
: A suppresses B when both apply.

`specializes`
: A is semantically narrower than B and takes precedence when applicable. Compiler should verify static narrowing where possible.

`fallback_for`
: A may apply only when all referenced rules are definitely inapplicable. `UNKNOWN` prevents fallback.

`equivalent_to`
: co-match is allowed because overlap constructs the same semantic candidate.

`mutually_exclusive_with`
: co-match is impossible by declared constraints; compiler verifies the disjointness it can prove.

No precedence/fallback cycle is allowed.

### 12.3 Conflict rule

Within one decision domain, if two rules may overlap and may yield non-equivalent effects, strict compilation fails unless an explicit resolution relationship exists.

A source order or numeric priority can be a non-semantic display/debug hint, but can never resolve chemistry.

## 13. Validation declarations

Rules name validators; they do not implement them.

```yaml
validation:
  require:
    - validator.canonical_participants
    - validator.positive_integer_balance
    - validator.atom_conservation
    - validator.charge_conservation
    - validator.context_compatible_phases
```

Validator implementation/version is compiler-owned. Validator results are proof events.

## 14. Evidence and provenance

Every chemistry-bearing rule references evidence or an auditable derivation basis:

```yaml
provenance:
  evidence:
    - ev_01991c2e-7b10-7001-8000-000000000001
  rationale: >-
    High-school displacement rule under the stated aqueous acid context.
```

A generated `ReactionCandidate` records at least:

- `rule_ref` and rule version/revision;
- decisive input `ent_*`, `fact_*`, `rel_*`, `ctx_*`, `cond_*` refs;
- evidence refs carried by decisive source knowledge/rules;
- conditions/exceptions/blockers considered;
- constructed products;
- validation results;
- canonical-match state;
- compiler/source snapshot identity;
- proof trace.

## 15. Baseline rule families

The following concrete rule IDs are illustrative valid-shape stable refs for documentation. Real curated IDs are minted by the canonical data workflow.

### 15.1 Metal + dilute non-oxidizing acid

```yaml
rule_ref: rule_01991c2e-7b00-7001-8000-000000000001
rule_key: reaction.metal_dilute_nonoxidizing_acid
rule_version: 1
family: family.displacement.metal_acid
decision_domain: reaction.metal_acid

match:
  representation: molecular
  reactants:
    - bind: metal
      kind: chemical_entity
      require_facets: {all: [facet.elemental_character.metal]}
    - bind: acid
      kind: chemical_entity
      require_facets: {all: [facet.inorganic_family.acid]}
  context:
    medium: aqueous
    concentration_regime: dilute

bind:
  - name: metal_cation
    relation: relation.forms_cation_in_nonoxidizing_acid
    subject: $metal
    context: $context
    cardinality: exactly_one
  - name: acid_anion
    relation: relation.conjugate_anion
    subject: $acid
    cardinality: exactly_one

when:
  all:
    - id: nonoxidizing
      predicate: property.is_nonoxidizing_acid_under
      args: [$acid, $context]
      expect: TRUE
    - id: above_hydrogen
      predicate: relation.activity_above
      args: [$metal, entity.reference.hydrogen]
      expect: TRUE

blockers:
  - id: oxidizing_behavior
    predicate: property.is_oxidizing_acid_under
    args: [$acid, $context]
    expect: TRUE
    effect: block

construct:
  products:
    - bind: salt
      ionic_product:
        cation: $metal_cation
        anion: $acid_anion
        representation: $representation
        context: $context
    - bind: hydrogen
      entity: entity.species.hydrogen

validation:
  require:
    - validator.positive_integer_balance
    - validator.atom_conservation
    - validator.charge_conservation

provenance:
  evidence: [ev_01991c2e-7b10-7001-8000-000000000001]
```

If `activity_above($metal, H)` is unknown, this rule is `INDETERMINATE`; it does not infer that the metal is below hydrogen.

### 15.2 Metal + salt solution

Generic displacement:

```yaml
rule_ref: rule_01991c2e-7b00-7001-8000-000000000002
rule_key: reaction.metal_salt_solution_displacement
rule_version: 1
family: family.displacement.metal_salt_solution
decision_domain: reaction.metal_salt_solution

match:
  representation: molecular
  reactants:
    - bind: incoming_metal
      require_facets: {all: [facet.elemental_character.metal]}
    - bind: salt_solution
      require_facets: {all: [facet.inorganic_family.salt]}
  context: {medium: aqueous}

bind:
  - name: displaced_cation
    relation: relation.dissolved_cation
    subject: $salt_solution
    context: $context
    cardinality: exactly_one
  - name: spectator_anion
    relation: relation.dissolved_anion
    subject: $salt_solution
    context: $context
    cardinality: exactly_one
  - name: displaced_metal
    relation: relation.corresponds_to_element
    subject: $displaced_cation
    cardinality: exactly_one
  - name: incoming_cation
    relation: relation.forms_cation_in_salt_displacement
    subject: $incoming_metal
    context: $context
    cardinality: exactly_one

when:
  all:
    - predicate: relation.activity_above
      args: [$incoming_metal, $displaced_metal]
      expect: TRUE

construct:
  products:
    - bind: new_salt
      ionic_product:
        cation: $incoming_cation
        anion: $spectator_anion
        representation: $representation
        context: $context
    - bind: displaced_metal_product
      entity: $displaced_metal

validation:
  require:
    - validator.positive_integer_balance
    - validator.atom_conservation
    - validator.charge_conservation
```

Explicit water-preemption specialization:

```yaml
rule_ref: rule_01991c2e-7b00-7001-8000-000000000003
rule_key: override.metal_salt_solution_water_preemption
rule_version: 1
family: family.displacement.metal_salt_solution
decision_domain: reaction.metal_salt_solution

match:
  representation: molecular
  reactants:
    - bind: incoming_metal
      require_facets: {all: [facet.elemental_character.metal]}
    - bind: salt_solution
      require_facets: {all: [facet.inorganic_family.salt]}
  context: {medium: aqueous}

when:
  all:
    - predicate: property.aqueous_water_reaction_preempts_displacement
      args: [$incoming_metal, $context]
      expect: TRUE

effect:
  block:
    reason: chemistry.water_reaction_preempts_simple_displacement

resolution:
  overrides:
    - rule_01991c2e-7b00-7001-8000-000000000002
```

The override is an explicit graph edge. Reordering the two source files changes nothing.

### 15.3 Acid + base

```yaml
rule_ref: rule_01991c2e-7b00-7001-8000-000000000004
rule_key: reaction.acid_base_neutralization
rule_version: 1
family: family.neutralization.acid_base
decision_domain: reaction.acid_base

match:
  representation: molecular
  reactants:
    - bind: acid
      require_facets: {all: [facet.inorganic_family.acid]}
    - bind: base
      require_facets: {all: [facet.inorganic_family.base]}

bind:
  - name: acid_anion
    relation: relation.conjugate_anion
    subject: $acid
    cardinality: exactly_one
  - name: base_cation
    relation: relation.base_counter_cation
    subject: $base
    cardinality: exactly_one

when:
  all:
    - predicate: property.neutralization_applicable_under
      args: [$acid, $base, $context]
      expect: TRUE

exceptions:
  - id: partial_neutralization
    predicate: context.requires_partial_neutralization_product
    args: [$acid, $base, $context]
    expect: TRUE
    effect: inapplicable

construct:
  products:
    - bind: salt
      ionic_product:
        cation: $base_cation
        anion: $acid_anion
        representation: $representation
        context: $context
    - bind: water
      entity: entity.species.water

validation:
  require:
    - validator.positive_integer_balance
    - validator.atom_conservation
    - validator.charge_conservation
```

The generic rule does not encode coefficients. For the full-neutralization product set, `H2SO4 + NaOH -> Na2SO4 + H2O` is balanced independently to `1 : 2 : 1 : 2`.

### 15.4 Carbonate + acid

```yaml
rule_ref: rule_01991c2e-7b00-7001-8000-000000000005
rule_key: reaction.carbonate_acid_gas_evolution
rule_version: 1
family: family.gas_evolution.carbonate_acid
decision_domain: reaction.acid_carbonate

match:
  representation: molecular
  reactants:
    - bind: carbonate
      require_facets: {all: [facet.contains_carbonate_anion]}
    - bind: acid
      require_facets: {all: [facet.inorganic_family.acid]}

bind:
  - name: carbonate_cation
    relation: relation.counter_cation
    subject: $carbonate
    cardinality: exactly_one
  - name: acid_anion
    relation: relation.conjugate_anion
    subject: $acid
    cardinality: exactly_one

when:
  all:
    - predicate: property.acid_can_protonate_carbonate_under
      args: [$acid, $carbonate, $context]
      expect: TRUE

construct:
  products:
    - bind: salt
      ionic_product:
        cation: $carbonate_cation
        anion: $acid_anion
        representation: $representation
        context: $context
    - bind: carbon_dioxide
      entity: entity.species.carbon_dioxide
    - bind: water
      entity: entity.species.water

validation:
  require:
    - validator.positive_integer_balance
    - validator.atom_conservation
    - validator.charge_conservation
    - validator.gas_product_context
```

A bicarbonate-specific rule may declare `specializes` against this rule if the canonical facet vocabulary intentionally makes their match domains overlap.

### 15.5 Precipitation double-displacement

```yaml
rule_ref: rule_01991c2e-7b00-7001-8000-000000000006
rule_key: reaction.double_displacement_precipitation
rule_version: 1
family: family.double_displacement.precipitation
decision_domain: reaction.double_displacement_precipitation

match:
  representation: molecular
  reactants:
    - bind: salt_a
      require_facets: {all: [facet.inorganic_family.salt]}
    - bind: salt_b
      require_facets: {all: [facet.inorganic_family.salt]}
  context: {medium: aqueous}

bind:
  - name: cation_a
    relation: relation.dissolved_cation
    subject: $salt_a
    context: $context
    cardinality: exactly_one
  - name: anion_a
    relation: relation.dissolved_anion
    subject: $salt_a
    context: $context
    cardinality: exactly_one
  - name: cation_b
    relation: relation.dissolved_cation
    subject: $salt_b
    context: $context
    cardinality: exactly_one
  - name: anion_b
    relation: relation.dissolved_anion
    subject: $salt_b
    context: $context
    cardinality: exactly_one

construct:
  products:
    - bind: product_ab
      ionic_product:
        cation: $cation_a
        anion: $anion_b
        representation: $representation
        context: $context
    - bind: product_ba
      ionic_product:
        cation: $cation_b
        anion: $anion_a
        representation: $representation
        context: $context

postmatch:
  any:
    - id: product_ab_precipitates
      fact_of: $product_ab
      property: property.solubility_class
      context: $context
      op: eq
      value: insoluble
    - id: product_ba_precipitates
      fact_of: $product_ba
      property: property.solubility_class
      context: $context
      op: eq
      value: insoluble

validation:
  require:
    - validator.at_least_one_precipitate
    - validator.positive_integer_balance
    - validator.atom_conservation
    - validator.charge_conservation
```

If both exchanged products are definitely soluble, `postmatch` is `FALSE` and the rule is definitely inapplicable. If decisive solubility is unknown, the rule is `INDETERMINATE`; unknown is not treated as soluble.

## 16. Compile-time invalid patterns

Strict compilation rejects these semantics.

### Bare priority as chemistry precedence

```yaml
priority: 100
```

### Host-language callback

```yaml
when_python: my_module.guess_products
```

### Open-world UNKNOWN collapse

```yaml
unknown_as_false: true
```

### Manual normal coefficients

```yaml
construct:
  products:
    - entity: ent_...
      coefficient: 1
```

unless the coefficient relation is an explicitly justified exceptional balance constraint.

### Unresolved overlap

Two rules in one `decision_domain` with compatible match domains and non-equivalent effects but no explicit resolution relation.

### Precedence cycle

```text
A overrides B
B specializes C
C overrides A
```

### Identity-by-formula constructor

A constructor that returns “whatever entity has display formula `NaCl`” without participant-layer/context semantics.

## 17. DSL evolution

Two independent axes are recorded in compiler bundles:

- `dsl_version`: source language/operator/type-system compatibility;
- canonical `rule_ref` + `rule_version`: chemistry semantics of an individual rule.

A compiler may lower multiple supported DSL versions to one normalized IR version, but a bundle uses one declared plan-format version.

Every new operator requires:

1. language-neutral semantic definition;
2. type signature;
3. three-valued behavior;
4. deterministic implementation requirements;
5. trace representation;
6. compatibility impact;
7. differential/golden tests where multiple implementations exist.
