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

## M5 — Bounded hydrogen-carbonate gas evolution

M5 extends the M4 pipeline with one reusable family:

```text
aqueous strong acid
+ soluble, strongly dissociated hydrogen-carbonate salt
-> canonical salt + CO2 + H2O
```

HCl + NaHCO3 and HNO3 + NaHCO3 use the same declarative rule. Context-qualified acid/electrolyte strength, solubility, and canonical speciation gate applicability; the existing `ionic_pair` constructor selects the salt without formula parsing or entity fabrication. Exact balancing produces molecular coefficients, and the existing ReactionForm projection reduces both reactions to `H+ + HCO3- -> CO2 + H2O` while retaining speciation/evidence provenance.

The gas-evolution rule explicitly specializes neutralization for conservative overlap resolution.

## M6 — Strong-acid carbonate gas evolution

M6 adds a distinct sibling family using the same M4/M5 execution architecture:

```text
aqueous strong acid
+ soluble, strongly dissociated carbonate salt
-> canonical salt + CO2 + H2O
```

Canonical `CO3^2-`, Na2CO3, and K2CO3 data pressure-test divalent speciation and exact coefficients. HCl + Na2CO3, HNO3 + Na2CO3, and HCl + K2CO3 all use one typed carbonate Rule. The existing exact balancer derives `2 acid : 1 carbonate : 2 salt : 1 CO2 : 1 H2O`; complete ionic projection and spectator cancellation yield `2 H+ + CO3^2- -> CO2 + H2O` for every case.

The sibling design deliberately avoids OR syntax and a synthetic carbonate-family facet. Relative acid-strength reasoning, weak-acid applicability, pKa/equilibrium modeling, and any broader speciation capability remain later evidence-driven work.

## Still out of scope

- full high-school chemistry population or wholesale legacy migration;
- transition-metal redox, concentrated-acid/passivation, or organic families;
- universal equilibrium/speciation solving;
- UI integration, database services, Neo4j, or RETE;
- Rust/C++ or native acceleration without profiling evidence;
- speculative plugin infrastructure.
