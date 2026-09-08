# Roadmap

## Current state

Historical F1/F2 and F3A/F3B workstreams established the ontology, executable compiler contracts, and the bounded aqueous pilot. Their provenance and branch names remain historical facts.

## M4 — Chemistry Model Convergence

M4 integrates those workstreams on `workstream/f3-convergence` and verifies this pipeline:

```text
canonical YAML source
→ schema + reference + evidence validation
→ typed participant/property/context predicates
→ deterministic RulePlan matching and resolution
→ bounded canonical product construction
→ exact balancing and atom/charge validation
→ canonical Reaction comparison
→ ReactionCandidate + proof trace
→ TeachingView/speciation/derived-ReactionForm artifacts
```

M4 acceptance requires:

- structured context-qualified properties while stable classifications remain facets;
- validated executable TeachingView source that does not enter reaction inference;
- an explicit MaterialSystem-to-stoichiometric projection boundary;
- evidence-aware canonical aqueous speciation with exact coefficients;
- reusable neutralization and precipitation without exact-case engine branches;
- no fabricated canonical entities or negative Reaction truth;
- deterministic complete/net ionic projection subordinate to the owning Reaction;
- byte-stable semantic artifacts and a fully passing compiler/CLI suite.

The bounded no-net NaCl + KNO3 contrast records a known `driving_force = none` for the precipitation rule. Overall inference remains `indeterminate` when another structurally possible rule family depends on absent open-world facts; no candidate or canonical negative reaction is emitted.

## M5 — next bounded decisions

The one demonstrated next-family gap is reusable acid + hydrogen-carbonate gas evolution. M5 may add it only through generic typed semantics and bounded product construction; the curated HCl + NaHCO3 Reaction is not justification for an exact-ID engine branch.

Any broader relation/numeric predicates or speciation capability still requires a concrete corpus case and a compatible contract change.

## Still out of scope

- full high-school chemistry population or wholesale legacy migration;
- transition-metal redox, concentrated-acid/passivation, or organic families;
- universal equilibrium/speciation solving;
- UI integration, database services, Neo4j, or RETE;
- Rust/C++ or native acceleration without profiling evidence;
- speculative plugin infrastructure.
