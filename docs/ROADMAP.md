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

## M10 — Metal + non-oxidizing acid hydrogen evolution

M10 adds the first bounded metal-displacement/redox family:

```text
sufficiently active elemental metal
+ aqueous non-oxidizing strong acid
-> canonical metal salt + H2(g)
```

Canonical Mg, Zn, and Cu Elements remain distinct from elemental Substances. Contextual activity facts place Mg/Zn above hydrogen and Cu below it; the solid metal Substances have no aqueous speciation. Evidence-bearing embedded `metal.product_cation` relations connect Mg and Zn to their canonical divalent Species. A typed ion-source extension lets the existing `ionic_pair` constructor combine that relation-derived cation with the acid-speciation anion without formula parsing or valence guessing.

Zn + HCl and Mg + HCl use the same declarative Rule. Exact balancing derives `1:2:1:1`, while existing complete/net ionic projection yields `Zn + 2 H+ -> Zn2+ + H2` and `Mg + 2 H+ -> Mg2+ + H2`. Cu fails the known activity predicate and emits no M10 candidate; Zn + HNO3 remains UNKNOWN because acid strength does not imply non-oxidizing character.

M10 advances the independently owned compatibility coordinates to source schema `3.2.0`, Rule DSL `1.1.0`, RulePlan `1.1.0`, and artifact format `1.2.0`. The artifact bump is required by the externally emitted typed ion-source plan shape, while historical artifact formats and legacy ionic-pair Rule syntax remain readable.

## M11 — Bounded alkali-metal + liquid-water hydrogen evolution

M11 adds one bounded reusable family:

```text
ambient solid water-reactive metal
+ liquid H2O
-> canonical aqueous metal hydroxide + H2(g)
```

Elemental Na/K Substances remain distinct from Na/K Elements and carry no fake aqueous speciation. Evidence-backed contextual `metal.water_reactivity = reacts` facts gate the family independently of M10's relative-to-hydrogen facts. Their established `metal.product_cation` relation supplies Na+/K+, while the new generic `exact_entity` ion source supplies canonical OH-. The existing `ionic_pair` resolver selects existing NaOH/KOH; no product identity is minted.

One phase-bounded Rule handles both metals. Exact balancing derives `2:2:2:1`; aqueous product dissociation produces complete and net ionic forms `2 M(s) + 2 H2O(l) -> 2 M+(aq) + 2 OH-(aq) + H2(g)`, which are equal because no spectators cancel. Cu/Zn/Mg remain UNKNOWN for M11 when ambient liquid-water reactivity is absent, and M10 behavior remains unchanged.

M11 advances source schema to `3.3.0`, Rule DSL and RulePlan to `1.2.0`, and artifact format to `1.3.0`. These are independent consequences of exact-ion authoring/reference validation, participant phase authoring/lowering, ambient Reaction conditions, and the externally emitted plan fields. Artifact formats `1.0.0` through `1.2.0` remain readable.

## M12 — Bounded elemental-metal + aqueous CuSO4 displacement

M12 adds one deliberately Cu2+-bounded family:

```text
evidence-backed compatible elemental metal
+ aqueous CuSO4
-> canonical sulfate of the incoming metal + Cu(s)
```

Zn and Mg own contextual `metal.displaces_cation -> Cu2+` assertions; Cu, Na, and K do not receive fabricated negatives or positives. Relation-family cardinality keeps `metal.product_cation` at one target per context while allowing `metal.displaces_cation` to have multiple distinct targets per context. One exact-target, one-hop Relation predicate gates a single Rule. The existing `metal.product_cation` relation supplies Zn2+/Mg2+, CuSO4 speciation supplies sulfate, and the existing `ionic_pair` constructor resolves canonical ZnSO4/MgSO4. Elemental Cu remains an exact canonical product.

Exact balancing derives `1:1:1:1`. Canonical complete ionic forms dissociate only the soluble sulfates; sulfate cancellation yields `Zn + Cu2+ -> Zn2+ + Cu` and `Mg + Cu2+ -> Mg2+ + Cu`. Missing displacement assertions remain UNKNOWN, so Cu/Na/K + CuSO4 emit no false M12 candidate. Cu + ZnSO4 cannot match the exact CuSO4 participant.

M12 advances source schema to `3.4.0`, Rule DSL and RulePlan to `1.3.0`, and artifact format to `1.4.0`. The new coordinates reflect relation-family cardinality, exact-target Relation predicate authoring/lowering, and the externally emitted `PredicatePlan.target_id`. Artifact formats `1.0.0` through `1.3.0` remain readable.

## Coverage & Migration slice — silver nitrate reuse proof (working label M13)

This bounded slice reuses the existing Ag, Ag+, and AgNO3 identities, hardens their relied-upon facts and aqueous speciation with OpenStax Chemistry 2e evidence, and adds canonical elemental Ag, Zn(NO3)2, and Mg(NO3)2. Zn and Mg now each retain both aqueous `metal.displaces_cation -> Cu2+` and `metal.displaces_cation -> Ag+` targets, providing real-source proof of the existing many-target Relation contract.

One AgNO3-bounded Rule reuses the unchanged exact-target Relation predicate and unchanged `ionic_pair` constructor. Relation-derived Zn2+/Mg2+ combines with nitrate from AgNO3 speciation, while elemental Ag is an exact canonical product. Exact balancing derives `1:2:1:2`; nitrate cancellation yields `Zn + 2 Ag+ -> Zn2+ + 2 Ag` and `Mg + 2 Ag+ -> Mg2+ + 2 Ag`. Ag/Na/K/Cu + AgNO3 remain open-world UNKNOWN without authored Ag+ displacement relations.

This is a coverage reuse proof, not a new formal roadmap phase. Source schema remains `3.4.0`, Rule DSL and RulePlan remain `1.3.0`, and artifact format remains `1.4.0`; no compiler or schema extension is introduced.

## M15 — Bounded hydroxide precipitation

M15 adds one reusable aqueous-exchange family:

```text
aqueous soluble strong-electrolyte salt
+ aqueous strong base
-> insoluble hydroxide precipitate + soluble spectator salt
```

CuSO4 + NaOH, MgCl2 + NaOH, and FeCl3 + NaOH use the same declarative Rule. Canonical speciation supplies Cu2+, Mg2+, exact Fe3+, OH-, and the spectator ions; the existing `ionic_exchange.driving_force` predicate and `exchange_product` constructor select one known-insoluble hydroxide and one known-soluble counterproduct. Exact balancing derives the `1:2:1:1`, `1:2:1:2`, and `1:3:1:3` molecular coefficients, while existing ionic projection yields `M^n+ + n OH- -> M(OH)n(s)`.

A canonical-salt corpus audit rejected a new `classification.metal_salt` facet for this slice: applying it consistently would require broad reclassification while duplicating the actual speciation/solubility gates. The Rule therefore remains bounded by existing salt/base facets, aqueous participant phases, contextual strong-electrolyte/solubility facts, and unique exchange-product resolution. Missing hydroxide identity or solubility remains UNKNOWN; Zn/Al amphoterism, excess hydroxide, weak bases, variable-valence inference, and equilibrium semantics remain outside M15.

M15 requires no compiler, schema, Rule DSL, RulePlan, or artifact-format change. Compatibility remains source schema `3.4.0`, Rule DSL `1.3.0`, RulePlan `1.3.0`, and artifact format `1.4.0`.

## Still out of scope

- full high-school chemistry population or wholesale legacy migration;
- transition-metal redox, concentrated-acid/passivation, or organic families;
- variable-valence metal product selection, arbitrary metal/salt displacement, broader metal/water reactions, or general activity-series/electrode-potential reasoning;
- universal equilibrium/speciation solving;
- nitric-acid/thiosulfate prediction, oxidation-number/electrode-potential inference, or broader thiosulfate/redox chemistry;
- UI integration, database services, Neo4j, or RETE;
- Rust/C++ or native acceleration without profiling evidence;
- speculative plugin infrastructure.
