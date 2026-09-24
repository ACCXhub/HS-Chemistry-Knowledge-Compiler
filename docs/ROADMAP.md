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

## M16 — Heated condition and CaCO3 thermal-decomposition pilot

M16 adds `heated` as a controlled `temperature_regime` distinct from `warmed`, then proves the existing generic scalar context/condition path with one exact bounded transformation:

```text
CaCO3(s) --heated--> CaO(s) + CO2(g)
```

The slice adds only the missing canonical CaO identity, one canonical Reaction, and one exact declarative Rule. The Rule requires exact solid CaCO3 plus `temperature_regime = heated`; missing temperature remains UNKNOWN, while known `ambient` or `warmed`, the wrong phase, and MgCO3 do not match. Exact balancing derives `1:1:1`; atom and charge conservation remain mandatory. The solid-state thermal Reaction has no ionic ReactionForms.

The generic runtime already carries scalar context through applicability, canonical comparison, proof trace, and condition-evidence provenance, so there is no heated-specific or CaCO3-specific Python branch. Source schema advances to `3.5.0` solely for the controlled value; Rule DSL and RulePlan remain `1.3.0`, and artifact format remains `1.4.0`.

This is not a generic carbonate-decomposition family. Substrate-derived oxide selection, MgCO3/ZnCO3 decomposition, generic bicarbonate/nitrate decomposition, numeric temperature, catalyst semantics, steam, kinetics, equilibrium, and redox remain deferred until they have explicit semantic owners.

## M17 — Heated-condition reuse with exact NaHCO3 decomposition

M17 reuses M16's unchanged `temperature_regime = heated` contract for a second real high-school thermal Reaction:

```text
2 NaHCO3(s) --heated--> Na2CO3(s) + H2O(g) + CO2(g)
```

The slice reuses all existing substance and element identities, adds one evidence-backed canonical Reaction and one exact declarative Rule, and requires exact solid NaHCO3 under `heated`. Missing temperature remains UNKNOWN; `ambient`, `warmed`, the wrong phase, and KHCO3 do not match. Exact balancing derives `2:1:1:1`, atom and charge conservation remain mandatory, and the Reaction has no ionic forms. The H2O(g) representation follows the cited Triton College laboratory manual, which explicitly presents both water and carbon dioxide as gases released while sodium carbonate remains solid.

M17 adds no condition vocabulary and changes no compiler, schema, Rule DSL, RulePlan, or artifact behavior. It is an exact reuse proof, not a generic bicarbonate family: cation-derived carbonate selection and KHCO3 decomposition remain unsupported.

## M18 — Magnesium + steam phase/pathway pilot

M18 proves that the existing participant-phase and condition contracts can represent one bounded steam pathway without a new steam Entity or condition:

```text
Mg(s) + H2O(g) --heated--> MgO(s) + H2(g)
```

Steam is canonical H2O used with reactant `phase = gas`; heating remains the existing distinct `temperature_regime = heated` value. One exact declarative Rule binds only elemental Mg(s) and H2O(g), selects exact canonical MgO(s) and H2(g), and relies on unchanged exact balancing and conservation validation for `1:1:1:1`. H2O(l) cannot enter the Rule, known `ambient` or `warmed` contexts fail it, and missing temperature remains UNKNOWN.

MgO is the only new Entity. The Reaction owns no ionic forms and does not consume Mg's aqueous product-cation Relation or add `metal.water_reactivity` for Mg. Hot liquid water, generic metal + steam inference, Fe/Zn/Ca pathways, dynamic oxide construction, phase transitions, numeric temperature, and general redox reasoning remain unsupported. Compatibility coordinates and compiler/schema behavior remain unchanged.

## M19 — Generic aqueous metal-salt displacement architecture

M19 retires the two active exact-salt M12/M13 Rules and replaces them with one declarative family, `rule_m19_generic_aqueous_metal_salt_displacement`. The bound aqueous salt supplies its unique positive and negative ions from canonical complete-dissociation speciation. Applicability then checks only an authored pairwise `metal.displaces_cation` assertion to that resolved cation; absence remains UNKNOWN and no activity ordering or transitivity is inferred.

A shared typed `EntitySourcePlan` supports exact entities, participant bindings, one signed speciation ion, and at most one controlled Relation hop. The incoming salt product still uses `metal.product_cation` plus the existing `ionic_pair` constructor. The displaced product uses the evidence-backed `ion.elemental_substance` Relation, currently only for Cu2+ -> Cu and Ag+ -> Ag. No formula is parsed and no canonical identity is minted.

The same Rule reproduces Zn/Mg + CuSO4 and Zn/Mg + AgNO3 and adds the third-salt proof Zn/Mg + CuCl2 without another salt-specific Rule. Existing M12/M13 Reaction IDs and regression fixtures remain canonical; only active Rule ownership moves to M19. Source schema advances to `3.6.0`, Rule DSL and RulePlan to `1.4.0`, and artifact format to `1.5.0`; the reader continues to accept artifact formats `1.0.0` through `1.4.0`.

## M20 — Explicit negative Relation knowledge

M20 extends the existing Entity-owned Relation assertion with optional `truth` (default `true`). An applicable positive assertion resolves TRUE, `truth: false` resolves FALSE, and no assertion remains UNKNOWN. Exact duplicates and same-tuple positive/negative contradictions are rejected deterministically; one-target cardinality continues to constrain only positive targets.

The bounded proof adds one evidence-backed aqueous `Cu -> Zn2+` negative under `metal.displaces_cation`. Cu + ZnSO4 therefore makes the generic M19 predicate known FALSE, while Cu + MgSO4 remains unsupported/UNKNOWN and all six Zn/Mg positive proofs still use the one M19 Rule. The negative does not create a Reaction or assert global no reaction, and no ranking, transitivity, potential calculation, or redox engine is introduced.

Only source schema advances to `3.7.0`; Rule DSL and RulePlan remain `1.4.0`, and artifact format remains `1.5.0`.

## M21 — Coverage Reuse Batch B

M21 adds one evidence-backed HBr Entity and eight canonical aqueous Reactions. The same HBr/Br- speciation is reused across Na/K counterions in four existing families: strong-acid/strong-base neutralization, hydrogen-carbonate gas evolution, carbonate gas evolution, and sulfite gas evolution. Exact balancing, canonical matching, complete/net ionic projection, bromide spectator cancellation, and TeachingView projection all use existing paths.

HBr + thiosulfate remains UNKNOWN because M21 does not author an acid redox-character fact, and missing aqueous medium remains UNKNOWN. No Rule, Relation, constructor, compiler primitive, schema, or compatibility coordinate changes. Source schema remains `3.7.0`, Rule DSL and RulePlan remain `1.4.0`, and artifact format remains `1.5.0`.

## M22 — Legacy Migration Pilot A

M22 processes a fixed 20-record cohort from the real sibling inorganic package at revision `a6311150436038ca06fa7b9d05de39da9e1de815`. Element, monatomic-ion, and simple-substance records are reconciled by referent-level kind, composition, charge, symbol, and atomic-number facts; formula/name values are lookup signals only. Sixteen identities are reused, Li is created as one OpenStax-backed canonical Element, and Cu(I), carbonic acid, and chlorine are explicitly skipped at unsupported/evidence boundaries.

The migration tool reads the external package only when explicitly invoked with `--legacy-root` and emits a byte-stable tracked report. It does not mutate canonical source, load legacy data at runtime, overload aliases, or enter Rule DSL/artifacts. Ambiguous and invalid synthetic cases fail closed, and repeated/reordered execution is idempotent. Source schema remains `3.7.0`, Rule DSL and RulePlan remain `1.4.0`, and artifact format remains `1.5.0`.

## M23 — Legacy Identity Migration Batch B

M23 promotes `migration/legacy_identity.py` as the single identity-migration owner and retains the M22 entry point as a thin compatibility delegate. One explicit 100-record cohort spans all 48 legacy Element projections, all 32 monatomic ions, and 20 representative neutral Substance records. It maps 45 existing identities and records 55 evidence/referent-shape skips, with no automatic or M23 canonical creation.

The larger cohort strengthens simple-Substance reconciliation with a curated referent-shape gate plus exact canonical formula semantic-key corroboration after kind, neutral charge, and composition checks. Network, allotrope, complex/speciation, weak-equilibrium, and uncurated-evidence cases remain skipped. M22 output remains reproducible, runtime inference imports no migration code, and no Reaction data is migrated. Source schema remains `3.7.0`, Rule DSL and RulePlan remain `1.4.0`, and artifact format remains `1.5.0`.

## Still out of scope

- full high-school chemistry population or wholesale legacy migration beyond the M22/M23 bounded cohorts;
- transition-metal redox, concentrated-acid/passivation, or organic families;
- variable-valence metal product selection, displacement beyond evidence-backed pairwise aqueous salt cases, broader metal/water reactions, or general activity-series/electrode-potential reasoning;
- generic carbonate-to-oxide or bicarbonate-to-carbonate product mapping, or broader thermal-decomposition inference beyond the exact M16 CaCO3 and M17 NaHCO3 pilots;
- generic metal + steam or hot-liquid-water inference beyond the exact M18 Mg + H2O(g) pilot;
- universal equilibrium/speciation solving;
- nitric-acid/thiosulfate prediction, oxidation-number/electrode-potential inference, or broader thiosulfate/redox chemistry;
- UI integration, database services, Neo4j, or RETE;
- Rust/C++ or native acceleration without profiling evidence;
- speculative plugin infrastructure.
