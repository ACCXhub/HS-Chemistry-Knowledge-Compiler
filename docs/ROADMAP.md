# Roadmap

## Current state

F1 architecture convergence established the canonical ontology, data-contract, pedagogy, inference, and compiler boundaries.

F2 executable contract-to-candidate work is complete at:

```text
8d92d19b8ebbbcb0f8a9fdaceb7eb895da381447
```

The repository's current `main` has not yet converged that F2 lineage. F3A therefore continues from the verified F2 head on `workstream/f3a-rule-contract-hardening`; main-line convergence remains a prerequisite before a later F3 integration step.

## F3A — Contract and Rule Hardening

F3A generalizes the deliberately fixture-oriented F2 slice while keeping the chemistry corpus tiny.

The implemented target pipeline is:

```text
canonical source
→ source schema + reference validation
→ typed participant/predicate compilation
→ RulePlan
→ relationship-graph + overlap analysis
→ deterministic matching/resolution
→ bounded canonical product construction
→ exact balancing
→ atom + charge validation
→ canonical Reaction comparison
→ ReactionCandidate + proof trace
→ versioned deterministic artifacts
```

F3A acceptance focuses on reusable architecture rather than chemistry coverage:

- generic entity/species/facet participant patterns;
- explicit TRUE/FALSE/UNKNOWN predicate behavior with known/unknown/not-applicable/absent fact states;
- typed predicate validation;
- conservative compile-time overlap diagnostics;
- explicit, validated rule resolution relationships;
- rule/file-order independence;
- assumption-gated ReactionForm projection that preserves Reaction identity;
- bounded semantic-key product resolution against canonical data;
- separate source/DSL/plan/artifact versions;
- structured diagnostics;
- retained F2 deterministic candidate behavior.

The AgCl precipitation fixture is the architecture proof that an exact F2 participant rule can become a reusable faceted rule without adding a chemistry-specific engine branch.

## F3 convergence gate

Before F3 convergence:

1. integrate/resolve the verified F2 → F3A lineage into the canonical main history;
2. review F3A overlap diagnostics and Rule DSL compatibility decisions;
3. retain deterministic build/test evidence;
4. only then begin a small evidence-backed real chemistry migration pilot.

## Next phase — small migration pilot

After F3A convergence, migrate a deliberately small real high-school chemistry subset to discover missing contract semantics. Add new compiler primitives only when the migrated data demonstrates a real reusable need.

Good pilot questions include:

- whether relation predicates are required by real families;
- whether additional numeric/context operators are justified;
- whether product constructors need one more typed canonical resolver;
- which aqueous speciation assumptions need canonical vocabulary/evidence;
- whether artifact consumers expose any compatibility requirement beyond F3A `1.0.0`.

## Still out of scope

- full D01-D11 chemistry population;
- wholesale `chem-knowledge-data` migration;
- dozens of reaction families;
- advanced redox or organic inference;
- universal aqueous speciation;
- UI / chem-wiki integration;
- PostgreSQL / Neo4j;
- RETE;
- Rust/C++ or native acceleration without profiling evidence;
- speculative plugin infrastructure.
