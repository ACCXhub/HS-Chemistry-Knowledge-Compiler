# Knowledge Compiler Architecture

Status: **M19 generic bounded entity-source execution**

## Responsibility

The compiler converts validated canonical source and declarative rules into deterministic internal plans, diagnostics, candidates, proof traces, and external artifacts. Generated output is reproducible and never becomes editable chemistry truth.

## Ordered compile responsibilities

```text
parse YAML safely
→ JSON Schema validation
→ durable-ID/reference resolution
→ controlled relation-target validation
→ semantic indexes
→ Rule parse/type checking
→ typed PredicatePlan / ParticipantPatternPlan / IonSourcePlan / EntitySourcePlan / ProductPlan lowering
→ rule relationship graph validation
→ static overlap analysis
→ deterministic runtime plan
→ inference/audit
→ versioned artifact emission
```

Validation precedes derivation.

## Operator registry

The compiler owns the implementation of the source-level typed operator registry. Source semantics are stable operator names and typed arguments, not Python function names. The registry remains small and rejects malformed arguments during compilation. A Relation predicate under `equals expected: true` accepts one binding and exactly one exact target or typed target source. Dynamic target resolution preserves UNKNOWN on absent/ambiguous sources and does not add graph traversal or a query language.

## Overlap analysis

Strict compilation compares rules only inside the same decision domain. It can currently reason about participant arity, exact IDs, entity/species kinds, participant phase, required/forbidden facets, and simple context equality. Unprovable disjointness is conservative `potential_overlap`.

Non-equivalent potential overlap without explicit resolution is `rule_overlap_compile_error`.

## Resolution graph

The compiler validates relationship references and builds precedence from:

```text
overrides: declaring rule > referenced rule
specializes: declaring rule > referenced rule
fallback_for: referenced rule > declaring fallback
```

Precedence cycles are rejected. Runtime resolution uses transitive reachability and does not depend on file ordering.

## Product resolution

`exact_entity`, `semantic_key`, `ionic_pair`, `exchange_product`, and `entity_source` are bounded constructors. They resolve against canonical source indexes and canonical composition/speciation/relation records. `EntitySourcePlan` resolves an exact entity, binding, one signed speciation ion, or one Relation target from a non-Relation source. Ionic-pair ion sources remain speciation-, relation-, or exact-ion-backed; after both ions resolve, the unchanged neutral composition/charge resolver selects a canonical Substance. Zero or multiple matches remain explicit; no constructor parses display formulas, guesses valence, or mints canonical identity.

## ReactionForm projection

Projection is an explicit API over curated/golden forms and canonical speciation profiles. Required assumptions gate availability; derived complete/net ionic forms retain their canonical Reaction identity, exact coefficients, validation results, and derivation provenance.

## Condition execution

Rule context requirements and canonical Reaction conditions use the existing generic scalar equality path. M16 adds `heated` to the source vocabulary but no heated-specific or CaCO3-specific compiler branch: missing context remains UNKNOWN, unequal known values are FALSE, and matched canonical condition evidence is retained in comparison and provenance.

## Artifact/version boundary

Version axes are separate:

```text
source schema     3.7.0
Rule DSL          1.4.0
RulePlan          1.4.0
artifact format   1.5.0
```

External artifacts include `artifact_format_version`; manifests include all four. Artifact `1.5.0` reflects emitted nested `PredicatePlan.target_source` and `ProductPlan.entity_source`. The reader also accepts historical formats `1.0.0` through `1.4.0`; consumers reject unknown versions.

M20 changes only source Relation data: an applicable explicit `truth: false` assertion produces a known FALSE predicate result, while absence remains UNKNOWN. Rule DSL, RulePlan, and artifact format remain unchanged.

## Performance policy

Python-first remains the reference implementation. M19 adds no external dependency, RETE, database, native extension, generic graph engine, activity-ranking engine, or plugin runtime. Small typed indexes and compiled plans are preferred; optimization requires measured evidence.
