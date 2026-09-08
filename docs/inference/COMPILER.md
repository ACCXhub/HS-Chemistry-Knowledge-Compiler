# Knowledge Compiler Architecture

Status: **F3A executable compiler boundary**

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

The compiler owns the implementation of the source-level typed operator registry. Source semantics are stable operator names and typed arguments, not Python function names. F3A intentionally keeps the registry small and rejects malformed arguments during compilation.

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

`exact_entity` and `semantic_key` are the only F3A constructors. Both resolve against canonical source indexes. Ambiguity is preserved as an error; no constructor mints canonical identity.

## ReactionForm projection

Projection is an explicit API over curated forms. Required assumptions gate availability, and the result retains the canonical Reaction identity.

## Artifact/version boundary

Version axes are separate:

```text
source schema     3.0.0
Rule DSL          1.0.0
RulePlan          1.0.0
artifact format   1.0.0
```

External artifacts include `artifact_format_version`; manifests include all four. Consumers can reject unsupported external format versions. F3A does not promise compatibility across unspecified future versions.

## Performance policy

Python-first remains the reference implementation. F3A adds no RETE, database, native extension, or plugin runtime. Small typed indexes and compiled plans are preferred; optimization requires measured evidence.
