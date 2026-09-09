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

## M7 — Ammonium + strong base and Reaction conditions

M7 adds a conditioned high-school laboratory family:

```text
aqueous soluble ammonium salt
+ strong aqueous base
+ warmed condition
-> canonical spectator salt + NH3(g) + H2O
```

`NH4Cl + NaOH` and `(NH4)2SO4 + 2 NaOH` use one generic Rule and the existing `ionic_pair` constructor. Exact balancing handles the multi-ammonium case; complete ionic projection and normalized spectator cancellation yield `NH4+ + OH- -> NH3(g) + H2O` for both.

M7 also makes embedded Reaction conditions executable. Participant signatures remain the canonical lookup index, while required conditions filter signature matches and preserve evidence in comparison/projection provenance. The gas phase is limited to the evidence-backed warmed test; general dissolved-ammonia equilibrium remains deferred.

## M8 — Strong-acid sulfite gas evolution

M8 adds a third chemically distinct strong-acid gas-evolution sibling using the established compiler pipeline:

```text
aqueous strong acid
+ soluble, strongly dissociated sulfite salt
-> canonical salt + SO2(g) + H2O
```

Canonical `SO3^2-`, SO2, Na2SO3, and K2SO3 data support acid and cation substitutions. HCl + Na2SO3, HNO3 + Na2SO3, and HCl + K2SO3 use one typed Rule and the existing `ionic_pair` constructor. Exact balancing derives the `2:1:2:1:1` molecular ratio, while complete ionic projection and spectator cancellation normalize all three cases to `2 H+ + SO3^2- -> SO2(g) + H2O`.

M8 requires no compiler, DSL, schema, artifact-format, or dependency change. It adds no warmed condition because ordinary aqueous acidification is sufficient for the represented transformation. Sulfate remains an explicit negative contrast; hydrogen sulfite, weak-acid displacement, sulfurous-acid equilibrium, sulfite redox, and broader sulfur chemistry remain later milestones.

## M9 — Thiosulfate acid decomposition

M9 adds a chemically distinct mixed-phase sibling family:

```text
aqueous non-oxidizing strong acid
+ soluble, strongly dissociated thiosulfate salt
-> canonical salt + SO2(g) + elemental sulfur(s) + H2O(l)
```

Canonical `S2O3^2-`, Na2S2O3, K2S2O3, and elemental-sulfur Substance data support two HCl cation-substitution cases through one declarative Rule. The existing `ionic_pair` constructor resolves NaCl/KCl, exact balancing derives the `2:1:2:1:1:1` molecular ratio, and complete/net ionic projection preserves all gas, solid, and liquid products before normalizing to `2 H+ + S2O3^2- -> SO2(g) + S(s) + H2O(l)`.

M9 adds the contextual property `acid.redox_character = non_oxidizing` for evidence-backed aqueous HCl applicability. It does not infer the same pathway for HNO3: the absent compatibility fact remains UNKNOWN. The milestone requires no compiler, schema, DSL, artifact-format, condition-contract, or dependency change and adds no general redox engine.

## Still out of scope

- full high-school chemistry population or wholesale legacy migration;
- transition-metal redox, concentrated-acid/passivation, or organic families;
- universal equilibrium/speciation solving;
- nitric-acid/thiosulfate prediction, oxidation-number/electrode-potential inference, or broader thiosulfate/redox chemistry;
- UI integration, database services, Neo4j, or RETE;
- Rust/C++ or native acceleration without profiling evidence;
- speculative plugin infrastructure.
