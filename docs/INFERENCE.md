# Deterministic Reaction Inference Semantics

## 1. Purpose

This document defines the execution semantics for deterministic reaction inference in HS-Chemistry-Knowledge-Compiler.

The inference system consumes validated canonical chemistry knowledge plus declarative rule plans and produces auditable `ReactionCandidate` records. It does not turn generated candidates into canonical `Reaction` records, and it does not make presentation structure or implementation language part of chemistry truth.

The execution model is designed to be:

- deterministic for a fixed source revision, contract revision, rule bundle, and compiler revision;
- explicit about unknown knowledge;
- chemically staged so product inference, balancing, validation, and canonical comparison have separate responsibilities;
- faithful to the ontology distinction between `Element`, microscopic `Species`/`Ion`, macroscopic `Substance`/`MaterialSystem`, and reaction representation;
- explainable through a replayable proof trace;
- compilable into efficient runtime plans without changing source semantics.

## 2. Architectural and contract boundary

Inference owns executable semantics, not the canonical field schemas or domain ontology.

It consumes the parallel canonical contracts for at least:

- `Entity` (`ent_*`) identity and typed element/species/ion/substance payloads;
- `Composition` (`cmp_*`);
- `FacetAssertion` (`fas_*`);
- `PropertyFact` and `Context` (`fact_*`, `ctx_*`);
- typed `Relation` (`rel_*`);
- canonical `Reaction`, `ReactionParticipant`, and `Condition` (`rxn_*`, `rpart_*`, `cond_*`);
- `Evidence`/`Source` (`ev_*`, `src_*`);
- stable `RuleReference` (`rule_*`);
- generated `ReactionCandidate` (`rcand_*`) provenance.

The chemistry meaning of facets, properties, relations, and context dimensions is owned by Domain Ontology & Pedagogy. Their field serialization is owned by Canonical Data Contracts.

Rules may read those semantics but must not redefine them through hidden Python callbacks, formula-string heuristics, or runtime-only special cases.

## 3. Reaction representation and participant layer

A formula is a representation, not a chemical identity. The same formula can participate in different semantic layers.

The inference request therefore carries or derives a target reaction representation such as:

```text
molecular
ionic / complete_ionic
net_ionic
conceptual
```

Participant resolution must select canonical entities appropriate to that representation and context.

Examples:

- a molecular equation may use canonical macroscopic substances/materials as participants;
- an ionic equation may use canonical dissolved ions/species;
- `NaCl` must not be invented as a discrete “NaCl molecule” merely because the formula is displayed;
- aqueous sulfuric-acid solution must not be silently conflated with an isolated `H2SO4` molecule.

Projection between molecular and ionic representations is a separate deterministic transform. It is not an implicit identity merge.

## 4. Result model

A single inference request ends in exactly one top-level outcome class:

| Outcome | Meaning |
| --- | --- |
| `INFERRED` | One deterministic, validated inferred candidate was produced. |
| `NO_MATCH` | All potentially relevant rules were definitely inapplicable. |
| `BLOCKED` | A definite blocker prevents the requested reaction family from being inferred. |
| `INDETERMINATE` | Missing/unknown knowledge could change the result. |
| `AMBIGUOUS` | More than one unresolved, non-equivalent applicable rule/candidate remains. |
| `INVALID` | A selected rule produced a candidate that cannot satisfy balancing or chemical validation. |

`NO_MATCH` and `INDETERMINATE` are deliberately different. Absence of knowledge is never reported as definite non-applicability unless the relevant knowledge domain has an explicit completeness/closed-world contract.

An `INFERRED` result contains an `rcand_*` candidate or an equivalent generated-candidate representation. Canonical comparison may link it to an existing `rxn_*`, but that does not change candidate lifecycle.

## 5. Three-valued fact semantics

### 5.1 Truth domain

All rule-relevant predicates operate over:

```text
TRUE
FALSE
UNKNOWN
```

The default logic is strong Kleene logic:

| A | B | A AND B | A OR B |
| --- | --- | --- | --- |
| T | T | T | T |
| T | F | F | T |
| T | U | U | T |
| F | F | F | F |
| F | U | F | U |
| U | U | U | U |

`NOT TRUE = FALSE`, `NOT FALSE = TRUE`, and `NOT UNKNOWN = UNKNOWN`.

Comparisons involving a missing value are `UNKNOWN`, not `FALSE`.

### 5.2 Mapping from canonical knowledge state

The data contract distinguishes:

```text
no assertion record
explicit value_state: unknown
value_state: not_applicable
known value, including known boolean false
```

Inference preserves those distinctions.

- no record: `UNKNOWN` unless completeness metadata says absence is a definite negative;
- explicit `unknown`: `UNKNOWN`;
- `not_applicable`: a typed non-value that normally makes a predicate inapplicable/false only according to that predicate's declared semantics, never by generic falsy coercion;
- known false: `FALSE` for the corresponding boolean proposition;
- known true/value satisfying comparison: `TRUE`.

### 5.3 Open-world default

Canonical authored chemistry knowledge is open-world by default. If no assertion establishes that a product is insoluble, the runtime must not infer that it is soluble.

A missing fact may become definite `FALSE` only when Canonical Data Contracts define completeness for the relevant predicate, entity scope, and context scope. That conversion happens during context construction and emits a proof event such as `closed_world_completion_applied`.

Until such a completeness contract exists, missing knowledge remains `UNKNOWN` everywhere.

Rules cannot silently opt into `UNKNOWN -> FALSE`.

### 5.4 Predicate use

For a required predicate:

- `TRUE`: continue;
- `FALSE`: the candidate is definitely inapplicable;
- `UNKNOWN`: the candidate is epistemically indeterminate.

For a blocker:

- `TRUE`: the candidate is definitely blocked;
- `FALSE`: blocker cleared;
- `UNKNOWN`: the candidate is indeterminate because the blocker may apply.

For an exception declaring that a rule does not cover a case:

- `TRUE`: that rule is definitely inapplicable;
- `FALSE`: continue;
- `UNKNOWN`: that rule remains indeterminate.

A predicate may be advisory and non-applicability-affecting, but advisory predicates cannot control product identity, precedence, or chemical validity.

## 6. Runtime request

A request is normalized into a semantic input containing:

- canonical reactant identities or unresolved tokens awaiting canonical resolution;
- requested/derived reaction representation;
- participant phase/material-state annotations where supplied;
- explicit context such as medium, solvent, concentration regime, temperature, pressure, pH, atmosphere, catalyst, reagent excess/limitation, or procedure when chemically decisive;
- optional known products for verification/comparison mode;
- provenance for supplied context where the calling contract provides it.

Names and displayed formulas are accepted only as syntax. Once resolved, matching uses canonical identity, facets, facts, relations, and context.

## 7. Execution pipeline

The runtime uses the following staged pipeline. Implementations may fuse adjacent stages for performance only if observable semantics and proof ordering remain equivalent.

```text
0. bundle selection
1. input normalization + canonical reactant resolution
2. context construction
3. global hard blockers
4. exact/specialized override candidate lookup
5. rule-family candidate retrieval
6. preconstruction match, bind, conditions, exceptions, blockers
7. product construction for surviving candidates
8. canonical product resolution
9. product-dependent postmatch predicates
10. explicit conflict / precedence resolution
11. stoichiometric balancing
12. chemical validation
13. canonical reaction comparison
14. proof finalization + deterministic result emission
```

This order is intentional: precipitation and similar rules need constructed canonical products before their driving-force predicates can be evaluated, while balancing still remains downstream and independent.

### Stage 0 — Bundle selection

Select one immutable compiled bundle identified by source revision, schema/contract versions, rule DSL version, rule bundle digest, and compiler identity. Runtime execution never reads a mixture of rule plans from different bundles.

### Stage 1 — Input normalization and canonical reactant resolution

Normalize aliases, formula tokens, charge/phase notation, and representation syntax through the canonical identity layer.

Possible results:

- unique canonical identity at the required participant layer: continue;
- no resolvable identity: input diagnostic / `INDETERMINATE` according to API mode;
- multiple identities: `AMBIGUOUS` unless context deterministically resolves them.

Normalization does not infer products.

### Stage 2 — Context construction

Build an immutable `InferenceContext` from:

1. explicit request context;
2. canonical context-qualified facts;
3. independently deterministic derived context facts;
4. contract-defined completeness closure, if and only if available for the exact scope.

Each fact read into context retains:

- subject/ref;
- property/relation/facet key;
- value/truth state;
- context qualifiers;
- evidence/provenance ref;
- authored/derived/completeness origin.

Contradictory applicable facts are never resolved by file order. They produce a context conflict diagnostic and normally `INDETERMINATE`/`AMBIGUOUS` until a canonical resolution policy exists.

### Stage 3 — Global hard blockers

Global hard blockers are narrow, domain-approved constraints that apply before generic rule selection, such as an unsupported representation or a context that makes the selected inference mode semantically invalid.

A blocker is declarative, versioned, and traceable. This stage must not become an implementation exception list.

### Stage 4 — Exact/specialized override candidate lookup

Compiled indices may retrieve exact or specialized override/block plans before broader family retrieval.

This is only candidate discovery. Override semantics are finalized at Stage 10 after applicability, product resolution, and postmatch predicates are known.

If an overriding rule is only `UNKNOWN`, a lower rule that would be suppressed if the override applied cannot be finalized as though the override were false.

### Stage 5 — Rule-family candidate retrieval

Retrieve plausible rule plans using precompiled indices such as:

- participant arity;
- canonical entity kind/participant layer;
- required facet bitsets;
- role signatures;
- context dimensions;
- rule-family keys;
- exact-identity or typed-relation indices.

Index membership is a performance filter, not proof of applicability.

### Stage 6 — Preconstruction match, bind, conditions, exceptions, blockers

For each retrieved plan in deterministic plan order:

1. bind reactants to semantic roles;
2. check entity-kind/participant-layer constraints;
3. evaluate required/forbidden facets;
4. resolve typed relation/fact bindings;
5. evaluate context predicates;
6. evaluate positive conditions;
7. evaluate exceptions;
8. evaluate blockers;
9. record every truth result used.

Bindings are canonical refs/typed values, not labels. A binding declared `exactly_one` that resolves to multiple chemically distinct values makes the candidate ambiguous; the runtime never picks the first relation target.

### Stage 7 — Product construction

Every surviving definite or indeterminate rule constructs an **unbalanced semantic product specification**.

A product expression may:

- reference a known canonical entity;
- create a canonical entity query such as “ionic substance formed from this cation and anion under molecular representation”;
- bind a product through a typed relation;
- constrain participant layer/representation;
- request phase/context postconditions.

It does not choose normal stoichiometric coefficients.

For metal + dilute non-oxidizing acid, the semantic result may be conceptually:

```text
ionic_product(cation = $metal_cation,
              anion = $acid_anion,
              representation = molecular)
hydrogen product
```

The constructor must resolve to an existing canonical entity; it does not create one.

### Stage 8 — Canonical product resolution

Resolve every product ref/query through canonical identity at the required participant layer.

Possible results:

- one identity: continue;
- zero identities: `INDETERMINATE` with `unresolved_constructed_product`;
- multiple identities: `AMBIGUOUS` unless context supplies an explicit discriminator.

Formula equality alone cannot resolve a substance/species ambiguity.

### Stage 9 — Product-dependent postmatch predicates

Some rule applicability depends on the resolved products. These predicates are evaluated now, before final precedence selection.

Primary baseline case: precipitation.

```text
constructed exchanged products
-> resolve canonical product identities
-> query solubility/phase in context
-> at least one definite precipitate?
```

For an applicability postmatch predicate:

- `TRUE`: candidate remains applicable;
- `FALSE`: candidate is definitely inapplicable;
- `UNKNOWN`: candidate is indeterminate.

A false driving-force predicate is not a validation failure. It means the rule does not apply.

### Stage 10 — Conflict and precedence resolution

Resolve surviving candidates using the compiled rule-resolution graph.

Allowed semantic relationships include:

- `overrides`: A suppresses B when A definitely applies;
- `specializes`: A is a narrower case of B and wins when A applies;
- `fallback_for`: A runs only when all targets are definitely inapplicable, never merely unknown;
- `equivalent_to`: co-match is allowed because semantic candidates are equivalent;
- `mutually_exclusive`: compiler-verified reason they cannot co-apply.

File order and a bare integer priority are not valid resolution mechanisms.

If two definitely applicable non-equivalent candidates remain in one decision domain without a valid relationship, return `AMBIGUOUS`. Strict compilation is expected to detect most potential conflicts before runtime.

If a higher-precedence candidate is `UNKNOWN` and would suppress a lower candidate if true, the lower candidate cannot be finalized; the decision is `INDETERMINATE`.

### Stage 11 — Stoichiometric balancing

Balancing receives one selected set of canonical reactant/product identities.

Input:

- canonical participant identities;
- cached exact elemental composition;
- charge information when representation requires it;
- only rare, explicitly justified declarative stoichiometric constraints.

Solve an exact rational/integer conservation problem.

Requirements:

1. every mandatory participant has a positive coefficient;
2. all conserved elements balance;
3. charge balances when required;
4. rationals normalize to the least positive integer ratio;
5. common gcd is removed;
6. requested reactant/product orientation is preserved;
7. an underdetermined solution is not resolved by arbitrary library choice.

If multiple chemically distinct positive solutions remain and no justified constraint resolves them, return `INVALID` with `balance_underdetermined`.

Rules may own coefficient constraints only when the constraint itself is independently justified chemistry. None of the baseline five families requires manual coefficients.

### Stage 12 — Chemical validation

Validation is independent of product inference and balancing. At minimum check:

- canonical participant validity;
- atom conservation from canonical `Composition`;
- charge conservation where applicable;
- positive normalized coefficients;
- required phase/context compatibility;
- required gas/precipitate/weak-electrolyte postconditions where they are validation properties rather than applicability guards;
- no impossible empty/duplicate participant state after canonical normalization.

A balanced equation can still be chemically invalid. Balance success is never evidence that the inferred products are true.

### Stage 13 — Canonical reaction comparison

Normalize the validated candidate to a canonical reaction signature based on:

- canonical participant IDs;
- normalized signed stoichiometric coefficients;
- reaction representation;
- identity-relevant reaction context/conditions defined by the canonical reaction contract.

Normative stored comparison states are the data-contract values:

```text
unchecked | none | exact | equivalent | ambiguous | conflict
```

`exact` or `equivalent` sets `canonical_match.reaction_id` when uniquely resolved. It does not promote the candidate or change its `rcand_*` identity.

### Stage 14 — Proof finalization

Emit one deterministic result plus a stable ordered structured trace.

The same semantic request against the same immutable bundle must produce the same semantic result and trace. Generated artifact identity must also be reproducible: the compiler must not mint a fresh random/time-dependent candidate ID on every pure rebuild. Canonical Data Contracts therefore needs a deterministic generated-candidate identity/key rule, or generated IDs must be excluded from semantic reproducibility until a candidate is deliberately persisted. Implementations may not hide this issue behind nondeterministic UUID creation.

## 8. Rule-candidate state during evaluation

Each rule candidate moves through explicit internal states:

```text
RETRIEVED
PREMATCH_TRUE | PREMATCH_FALSE | PREMATCH_UNKNOWN
PRODUCT_RESOLVED | PRODUCT_UNRESOLVED | PRODUCT_AMBIGUOUS
POSTMATCH_TRUE | POSTMATCH_FALSE | POSTMATCH_UNKNOWN
SUPPRESSED_BY(rule_ref)
SELECTED
```

`UNKNOWN` state is carried until the final decision; it is not collapsed merely because another lower-precedence candidate exists.

## 9. Proof trace

### 9.1 Requirements

A trace must answer:

- what normalized canonical inputs were used and at what participant layer;
- what context facts were read and with what knowledge states;
- which rules were retrieved and why;
- why rules were rejected, blocked, indeterminate, or selected;
- which resolution edges were applied;
- how products were constructed and resolved;
- how balancing was solved;
- what validators ran and passed/failed;
- whether a canonical reaction matched;
- which evidence/rule/source revisions justify the result.

Canonical trace events are machine-readable. Human explanation is a downstream rendering, not the trace authority.

### 9.2 Trace envelope

At least:

```text
trace_version
bundle_id / bundle_hash
source_git_sha
compiler_revision
schema/contract version
rule_ref + rule_version for every rule used
input_semantic_hash
ordered events[]
final outcome
```

Facts, relations, entities, evidence, rules, and canonical reactions are referenced by stable canonical refs.

### 9.3 Example — Mg + dilute HCl

Illustrative trace:

```text
input_normalized
  representation = molecular
  reactants = [canonical Mg substance, canonical HCl-containing acid material]
  medium = aqueous
  concentration_class = dilute

role_bound
  $metal = Mg
  $acid = HCl acid material

facet_checked
  metal($metal) = TRUE
  acid($acid) = TRUE

condition_checked
  nonoxidizing_acid_under($acid, context) = TRUE
  activity_above(Mg, H) = TRUE

blocker_checked
  oxidizing_acid_under($acid, context) = FALSE

relation_bound
  forms_cation_in_nonoxidizing_acid(Mg) -> Mg2+
  conjugate_anion(HCl) -> Cl-

product_constructed
  ionic_product(Mg2+, Cl-, molecular) -> query
  hydrogen -> query/ref

product_resolved
  salt product -> canonical MgCl2 participant entity
  hydrogen -> canonical H2 participant entity

postmatch = TRUE
rule_selected
  rule_ref = rule_...

balanced
  Mg + 2 HCl -> MgCl2 + H2

atom_validation = PASS
charge_validation = PASS
context_validation = PASS

canonical_comparison
  state = exact | none

final
  outcome = INFERRED
  record_type = reaction_candidate
```

A learner-facing explanation can render this as “matched metal; matched dilute non-oxidizing acid; Mg is above H; blockers cleared; salt + hydrogen constructed; equation balanced and validated,” while the structured trace remains canonical.

## 10. Baseline rule-family behavior

These families define required semantics; exact vocabulary IDs belong to the ontology/contracts.

### 10.1 Metal + dilute non-oxidizing acid

Required knowledge:

- metal classification;
- acid role/classification in context;
- dilute/non-oxidizing acid behavior in context;
- activity relation relative to hydrogen;
- metal cation formed under this reaction context;
- acid-derived anion.

Products: corresponding salt participant + H2.

Unknown activity gives `INDETERMINATE`, not “no reaction.” Oxidizing-acid cases must be handled by explicit blocker/specialized rules, not by file position.

### 10.2 Metal + salt solution

Required knowledge:

- incoming elemental metal/substance;
- dissolved cation and anion of the salt solution;
- displaced metal identity;
- activity relation;
- incoming metal cation under displacement context;
- possible water-reaction preemption for sufficiently active metals.

Products: new salt + displaced metal.

A specialized water-preemption/block rule can explicitly override the generic simple-displacement rule. If preemption is unknown, the generic result cannot be finalized.

### 10.3 Acid + base

Products: salt + water.

The rule constructs semantic products only. For sulfuric acid + sodium hydroxide, balancing independently derives `1 : 2 : 1 : 2` for the full-neutralization product set.

Partial neutralization or alternative products under excess/stoichiometric context require explicit specialized/contextual semantics; they are not represented by manually tweaking coefficients in the generic rule.

### 10.4 Carbonate + acid

Products: corresponding salt + CO2 + H2O.

Carbonate/bicarbonate distinctions and acid availability are explicit match/context semantics. If a broader carbonate rule and a bicarbonate-specific rule overlap, their `specializes` relationship is declared.

### 10.5 Precipitation double-displacement

Inputs: two compatible aqueous ionic substances/material systems.

The rule:

1. binds dissolved cations/anions;
2. constructs exchanged products;
3. resolves canonical product entities;
4. queries context-qualified solubility/phase facts;
5. proceeds only if a precipitation driving-force predicate is definitely true.

For `BaCl2 + Na2SO4`, exchanged products resolve to `BaSO4` and `NaCl`; the insolubility/precipitation fact for `BaSO4` makes postmatch true; balancing derives `1 : 1 : 1 : 2`.

If both products are definitely soluble, the rule is definitely inapplicable. If decisive solubility is unknown, result is `INDETERMINATE`.

## 11. Determinism rules

Determinism requires:

1. stable canonical source IDs/keys and explicit versions;
2. immutable compiled bundles;
3. deterministic candidate retrieval and plan ordering;
4. no filesystem traversal semantics;
5. no map/hash iteration semantics;
6. no undeclared numeric rule priority;
7. exact balancing arithmetic;
8. deterministic rule-resolution graph behavior;
9. sorted canonical serialization for hashes/artifacts/traces;
10. no wall-clock, random, locale, or network dependency in semantic execution;
11. deterministic handling of symmetric reactant-role bindings;
12. reproducible generated-candidate semantic identity/key.

Parallel evaluation is allowed only over immutable reads with deterministic merge.

## 12. Diagnostic requirements

Diagnostics distinguish at least:

- unresolved/ambiguous input identity;
- participant-layer mismatch;
- unknown required fact;
- contradictory applicable facts;
- unresolved relation binding;
- unresolved constructed product;
- product identity ambiguity;
- unresolved rule overlap;
- precedence/fallback cycle;
- underdetermined balance;
- no positive integer balance;
- atom conservation failure;
- charge conservation failure;
- phase/context validation failure;
- canonical reaction ambiguity/conflict;
- nondeterministic generated-candidate identity.

Every diagnostic has a stable code, severity, source/record/rule refs, and relevant trace slice.

## 13. Non-goals

This semantics does not:

- implement the production engine;
- define final field-by-field canonical schemas;
- make an external chemistry/math library authoritative for truth;
- infer reaction mechanism from a balanced equation;
- choose products by statistical plausibility;
- silently create canonical entities or canonical reactions;
- conflate species with substances or formulas with identity;
- require a RETE network;
- require Python, Rust, or C++ as part of the source DSL.
