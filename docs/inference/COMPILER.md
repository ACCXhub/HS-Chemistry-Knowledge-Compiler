# Knowledge Compiler Architecture

Status: **M4 Chemistry Model Convergence compiler boundary**

## Responsibility

The compiler converts validated canonical source and declarative rules into deterministic internal plans, diagnostics, candidates, proof traces, and external artifacts. Generated output is reproducible and never becomes editable chemistry truth.

## Ordered compile responsibilities

```text
parse YAML safely
→ JSON Schema validation
→ durable-ID/reference resolution
→ semantic indexes
→ Rule parse/type checking
→ typed PredicatePlan / ParticipantPatternPlan / ProductPlan lowering
→ rule relationship graph validation
→ static overlap analysis
→ deterministic runtime plan
→ inference/audit
→ versioned artifact emission
```

Validation precedes derivation.

## Operator registry

The compiler owns the implementation of the source-level typed operator registry. Source semantics are stable operator names and typed arguments, not Python function names. M4 keeps the registry small, adds structured property and bounded ionic-exchange subjects, and rejects malformed arguments during compilation.

## Overlap analysis

Strict compilation compares rules only inside the same decision domain. It can currently reason about participant arity, exact IDs, entity/species kinds, required/forbidden facets, and simple context equality. Unprovable disjointness is conservative `potential_overlap`.

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

`exact_entity`, `semantic_key`, `ionic_pair`, and `exchange_product` are bounded constructors. They resolve against canonical source indexes and canonical composition/speciation records. Zero or multiple matches remain explicit; no constructor parses display formulas or mints canonical identity.

## ReactionForm projection

Projection is an explicit API over curated/golden forms and canonical speciation profiles. Required assumptions gate availability; derived complete/net ionic forms retain their canonical Reaction identity, exact coefficients, validation results, and derivation provenance.

## Artifact/version boundary

Version axes are separate:

```text
source schema     3.0.0
Rule DSL          1.0.0
RulePlan          1.0.0
artifact format   1.0.0
```

External artifacts include `artifact_format_version`; manifests include all four. Consumers can reject unsupported external format versions. M4 does not promise compatibility across unspecified future versions.

## Performance policy

Python-first remains the reference implementation. M4 adds no RETE, database, native extension, or plugin runtime. Small typed indexes and compiled plans are preferred; optimization requires measured evidence.
