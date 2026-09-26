# Coverage & Migration Audit — post-M25

[简体中文](COVERAGE_AUDIT.zh-CN.md)

## Decision

M25 runs the M24 reconciliation owner over all 152 declared legacy Reactions. After one bounded, independently evidenced canonical curation, 20 map to existing canonical Reactions, 123 remain explicit unsupported cases, and nine reversible records remain outside the current architecture boundary. The audit itself creates no canonical truth.

Batch A remains historical input. M19 resolved exact-salt duplication pressure with one bounded generic family, and M20 added exact pairwise negative Relation truth; neither authorizes activity ordering, transitivity, or a general no-reaction/redox engine.

## Post-M25 equation-integrity pass

This bounded pass reviewed the implemented compiler, Rules and canonical data across the foundation–M25 history, source/artifact contracts, offline migration, regression tests, and current documentation. It adds no chemistry family, milestone, or migration scope.

- Canonical matching now honors rational denominators and merges repeated role/entity/phase terms before primitive-integer normalization. Numerator-only signatures could previously conflate unequal equations.
- Eight early aqueous Rules now constrain reagent phases explicitly (and solid metal for M10), with Rule patch versions `1.0.1`. Aqueous context alone previously admitted gaseous reagents. All 66 positive fixture equations and canonical matches are unchanged; four invalid/unrelated pathways now terminate as `no_match` instead of `indeterminate`.
- Source validation now checks atom/charge conservation of all canonical Reactions, stored ReactionForms, and speciation profiles, and rejects duplicate composition elements, duplicate facets, and inconsistent formal/net charge. The current 68 Reactions and 38 profiles pass.
- Product Relation lookup rejects equally specific TRUE/FALSE contradictions before discarding negatives. An independently UNKNOWN rule path is no longer hidden by a blocked path. Rule evaluation is sorted by durable Rule ID so caller ordering cannot change the proof trace.
- Exact rational normalization and participant conservation reuse `compiler/balance.py`; duplicate ReactionForm arithmetic was removed. Test repository copies exclude Git metadata, generated builds, and caches (the local build directory alone contained about 40 MB). One duplicate candidate-key snapshot test was removed; the retained superset checks legacy keys and deliberate Rule-version invalidation. The M5 TeachingView test now asserts its own membership instead of freezing every later family.

The installation follow-up fixes setuptools flat-layout auto-discovery by explicitly packaging `compiler` and `migration`; schemas and canonical knowledge remain repository inputs. Editable installation and wheel installation both pass in an isolated verification environment, including the installed `hs-chem-compiler validate` entry point from outside the repository. Generated egg metadata is ignored.

Compiler patch version is `0.3.2`; the four format/DSL/schema coordinates are unchanged. No fields or constructors were added. Existing integer participant signatures remain stable, while corrected Rule versions intentionally change their candidate keys.

M22–M25 were rerun twice against the pinned legacy revision. Outputs were byte-identical within each pair. M22/M23/M25 decisions match their tracked historical reports. Current M24 maps 17 instead of its historical 16 because M25 already added CaCO3/HCl; this is expected canonical-data evolution, not a new migration action. Tracked reports retain their original source digests and remain historical snapshots.

Installation validation on 2026-09-25 passed all 406 tests in 341.82 seconds. All 18 integrity regressions passed, including all 117 cases under reversed reactant and RulePlan order. `validate` and both installed CLI modes passed; that packaging-only follow-up retained the earlier compile/audit determinism and M22–M25 migration evidence.

The highest-value next bounded work is executable coverage for already-curated high-school equations, starting with solid CaCO3 + acid after its phase/solubility boundary is explicitly designed. That work has not started. Weak-acid/equilibrium behavior, variable-valence selection, concentrated acids/passivation, and generic thermal/steam families remain unsupported.

## Rule product-resolution follow-up

Two equally specific positive Relation assertions may support the same canonical target. Ionic-pair and entity-source construction previously counted assertions and incorrectly returned `relation_ambiguous`. Both now count distinct target IDs, retain every supporting assertion, and union their evidence deterministically. Zero targets still fail unavailable; genuinely different targets still fail ambiguous. Context specificity and TRUE/FALSE/UNKNOWN ownership are unchanged. The M10 Zn/HCl and M19 Zn/CuSO4 regressions cover both construction paths and evidence-order invariance. No Rule, chemistry family, source record, or format coordinate changes.

Verification on 2026-09-25: all 20 equation-integrity tests pass; the full suite passes all 408 tests in 343.07 seconds. `validate` passes. Compile and audit each produce six byte-identical files under two different `PYTHONHASHSEED` values; all 117 existing case outputs are byte-identical to the previous audit. The source semantic digest remains `a2b1e55ba04f680371c1a29c2ee315290e8932c1001c1044181cd0e81cafe6c1`. Migration source, reconciliation code, and tracked reports are unchanged, so migration audits were not repeated for this fix.

The proposed chem-wiki integration and database boundary is recorded in [the integration note](contracts/CHEM_WIKI_INTEGRATION.md); it is not an implemented adapter or migration.

## Baseline and method

The audit uses the canonical YAML source, all 14 compiled Rules, all 117 fixtures, current contracts and architecture documents, the active schema, and the compiler product/balancing/aqueous-projection paths. The sibling package remains explicit offline migration input, not canonical truth or a runtime dependency.

The canonical corpus now contains 68 Reactions. M25's added solid-CaCO3/HCl Reaction is intentionally canonical coverage only: its canonical signature and derived ionic forms validate, while the existing soluble-carbonate Rule remains unchanged and does not infer the solid-carbonate case.

### Current counts

| Measure | Count |
|---|---:|
| all canonical records | 227 |
| Entity | 104 |
| Evidence | 33 |
| Reaction | 68 |
| Rule | 14 |
| Source | 7 |
| TeachingView | 1 |
| Element / Species / Substance / MaterialSystem | 18 / 22 / 63 / 1 |
| inference cases | 117 |
| speciation profiles | 38 |
| facet assertions | 104 |
| property assertions | 97 |
| `metal.product_cation` assertions | 4 |
| `metal.displaces_cation` assertions | 5 (4 positive, 1 negative) |
| TeachingView paths / memberships / unique members | 15 / 251 / 144 |
| fixture results: inferred / indeterminate / no-match / blocked | 66 / 38 / 12 / 1 |

Raw record volume is diagnostic, not the KPI. The useful KPI is the number of important high-school chemistry families that are correctly expressible, canonically matched, provenance-bearing, and conservative under missing knowledge.

### Locked compatibility coordinates

| Axis | Version |
|---|---|
| source schema | `3.7.0` |
| Rule DSL | `1.4.0` |
| RulePlan | `1.4.0` |
| artifact format | `1.5.0` |

## What the current compiler actually supports

The executable core is sufficient when all of the following are true:

- reactants can be selected through exact identities, entity kinds, phases, facets, contextual property predicates, or exact/dynamic-target Relation predicates;
- products are already canonical and can be selected by `exact_entity`, `semantic_key`, `ionic_pair`, `exchange_product`, or a bounded `entity_source`;
- any required aqueous ions come from a unique evidence-bearing `strong_electrolyte_complete_dissociation` profile;
- the products are fixed before balancing and the exact integer balance has one free variable;
- canonical comparison is based on the balanced participant signature plus compatible stored Reaction conditions;
- missing facts and Relations may remain UNKNOWN without being converted to known negatives.

Important boundaries are equally concrete:

- precipitation currently requires two aqueous `classification.salt` participants, unique complete-dissociation profiles, pre-existing cross-pair products, and exactly one insoluble driving product;
- ionic projection does not model weak/partial equilibria, hydrolysis, or concentration-dependent speciation;
- Relation execution remains one-hop: predicates may use an exact target or a target resolved from canonical speciation, and products may use one Relation target from a non-Relation entity source; it is not graph traversal or activity ranking;
- `metal.product_cation` is one-positive-target-per-context; `metal.displaces_cation` is many-positive-targets-per-context; exact duplicates and same-tuple truth contradictions are invalid, while explicit negative targets do not consume positive cardinality;
- `ion.elemental_substance` is one-target-per-context from a positive ion Species to an elemental-metal Substance;
- canonical Reaction conditions are limited to `medium` and `temperature_regime`, with the currently admitted values `aqueous`, `ambient`, `warmed`, and `heated`; `heated` is distinct from `warmed`;
- active source records do not include executable Structure or Experiment record families;
- formula text, names, file placement, and TeachingView paths never create chemistry truth or identity.

## Coverage classification

Categories are primary and mutually exclusive in the matrices below:

- **A — supported now / data-only gap:** an existing Rule and the complete execution path already suffice.
- **B — very small bounded semantic gap:** the architecture remains suitable, but a bounded Rule or narrowly typed primitive/condition is missing.
- **C — architecture pressure:** a semantic decision is required before safe inference.
- **D — later domain expansion:** outside the current compiler's near-term equation/inference scope.

### Acid/base/electrolyte

| Family or cluster | Primary | Current assessment and required coverage evidence |
|---|:---:|---|
| strong acid + strong base | A | Existing neutralization Rule, exchange products, exact balancing, strong-electrolyte projection, water retention, and canonical comparison are sufficient. Add cross-combinations and all-soluble/weak/missing-medium contrasts. |
| strong acid + hydrogen carbonate | A | Existing M5 Rule is reusable across counterions and HCl/HNO3 when canonical salts and speciation exist. |
| strong acid + carbonate | A | Existing M6 Rule already handles monovalent counterions and divalent carbonate stoichiometry. |
| strong acid + sulfite | A | Existing M8 Rule supports canonical acid/counterion substitution; sulfate must remain a non-match contrast. |
| HCl + thiosulfate | A | Existing M9 Rule supports bounded non-oxidizing acid decomposition and mixed gas/solid/liquid products. HNO3 remains UNKNOWN. |
| ammonium salt + strong base, warmed | A | Existing M7 Rule supports counterion/base substitution, exact coefficients, condition evidence, and ammonia ionic projection. |
| bounded weak acid + strong base equation family | B | A narrowly scoped Rule and weak-electrolyte molecular-retention contract can fit the current model, but no such executable family exists. It must not become an equilibrium solver by implication. |
| weak acid + weak base | C | Applicability and products depend on coupled equilibria, extent, and context not represented by current facts/projection. |
| generic acid displacement from a weaker acid | C | Requires evidence-backed relative-acid semantics, participant-derived product selection, and competing gas/solubility/equilibrium decisions. |
| generic weak-electrolyte driving force | C | Water generation is supported only in bounded Rules; a general driving-force model would require typed weak-species and equilibrium semantics. |
| salt hydrolysis | C | Requires contextual acid/base speciation and equilibrium rather than complete-dissociation projection alone. |

### Precipitation and ionic exchange

| Family or cluster | Primary | Current assessment and required coverage evidence |
|---|:---:|---|
| halide precipitates | A | AgCl already proves the Rule. AgBr and AgI need canonical Br/I identities, salts, solubility, speciation, Reactions, and contrasts only. |
| sulfate precipitates | A | BaSO4 already proves the Rule. Additional soluble sulfate counterions are data-only. |
| carbonate precipitates | A | Existing ions, exchange construction, and exact balancing suffice once each insoluble carbonate and soluble input/product salt is canonical. |
| hydroxide precipitates from soluble salt + strong base | A | M15 adds one bounded salt + strong-base Rule reusing canonical speciation, exchange products, solubility, exact balancing, and ionic projection for Cu2+, Mg2+, and exact Fe3+ cases; amphoterism, excess OH-, weak bases, and unmodeled hydroxides remain deferred. |
| multi-precipitation competition | C | The current Rule deliberately requires exactly one insoluble product; selection among multiple driving products needs explicit pathway semantics. |
| amphoteric hydroxides | C | Acid/base-dependent dissolution, excess-reagent behavior, and complex ions require conditional competing pathways and richer speciation. |
| dissolution of precipitates by acid/base | C | A general family needs solid-reactivity/complexation/equilibrium semantics; isolated exact reactions should not be mistaken for a reusable inference model. |

### Metals

| Family or cluster | Primary | Current assessment and required coverage evidence |
|---|:---:|---|
| Mg/Zn + non-oxidizing acid | A | M10 already resolves relation-derived cations and acid-speciation-derived anions. Further cases are data-only only when acid redox character, products, and cation identity are unambiguous. |
| Na/K + liquid water, ambient | A | M11 already uses phase-bounded participants, contextual reactivity, exact OH- and canonical hydroxides. Li could be a data-only extension if evidence is added. |
| Ca + liquid water | B | Existing product construction is close, but Ca(OH)2 phase/solubility and ionic projection must be decided in one bounded slice. |
| Mg + hot water/steam | B | M18 implements exact Mg(s) + H2O(g) under `heated` as MgO(s) + H2(g), using canonical H2O with participant phase `gas`. Hot liquid water remains unsupported, and this exact pilot does not generalize metal + steam or authorize Fe/Zn/Ca pathways. |
| Fe + steam | B | A bounded exact-product Rule is plausible after adding steam/temperature context; this does not authorize general iron redox or valence inference. |
| aluminium behavior | C | Oxide film/passivation, amphoterism, medium, and product state create competing pathways beyond current one-hop facts. |
| existing Zn/Mg + CuSO4 and AgNO3 | A | M12/M13 are complete bounded families and remain regression anchors. |
| arbitrary metal + salt displacement | C | Needs dynamic salt-cation discovery, ion-to-elemental mapping, variable-valence product selection, activity/context competition, and water competition. |
| self-displacement and general no-reaction truth | C | M20 supports auditable exact pairwise known-negative Relation assertions. Missing pairs remain UNKNOWN, and a failed Relation pathway is not a canonical or global no-reaction claim. |
| variable-valence metals | C | A canonical product-cation cannot be selected safely from element identity alone. |
| passivation | C | Requires material surface/state and acid concentration/context, not a global activity value. |
| oxidizing-acid metal reactions | C | Products depend on acid identity/concentration and redox conditions; hydrogen evolution is not a safe default. |
| general activity-series reasoning | C | Pairwise Relations do not provide ordering, transitivity, context competition, or aqueous-water override semantics. |

### Nonmetal and inorganic redox

| Family or cluster | Primary | Current assessment and required coverage evidence |
|---|:---:|---|
| halogen displacement | C | Requires activity/order semantics plus dynamic halide and elemental-halogen product resolution; a chain of exact salt Rules would duplicate M12/M13 pressure. |
| Cl2 + alkali | C | Cold/dilute versus hot/concentrated products are competing condition-dependent pathways. |
| H2S / sulfide chemistry | C | Acid/base, precipitation, gas evolution, and redox pathways overlap and require explicit pathway ownership. |
| SO2 oxidation/reduction | C | Current M8 owns SO2 formation only; oxidation-state/electron semantics and competing products are absent. |
| Fe2+/Fe3+ | C | Variable valence, redox applicability, and product selection require new canonical semantics. |
| Cu+/Cu2+ | C | Existing Cu2+ data does not authorize valence selection or Cu+ disproportionation/redox behavior. |
| MnO4- / Cr2O7^2- acidic redox | C | Oxidation-state reasoning, electron balance, medium-dependent products, and multiple half-reactions are absent. |
| peroxide redox chemistry | C | Oxidant/reductant dual behavior and context-dependent products need broader redox semantics. |
| nitric-acid redox | C | Concentration, metal identity, passivation, and nitrogen-oxide product competition are architectural inputs. |
| concentrated sulfuric-acid redox | C | Concentration and product competition are not captured by the current non-oxidizing-acid family. |

### Gas preparation, decomposition, and thermal reactions

| Family or cluster | Primary | Current assessment and required coverage evidence |
|---|:---:|---|
| carbonate thermal decomposition | B | M16 implements one exact CaCO3(s) `heated` pilot with canonical CaO(s) + CO2(g). The broader family remains unsupported because substrate-derived oxide selection is not modeled and products must not be dynamically fabricated. |
| bicarbonate thermal decomposition | B | M17 implements exact NaHCO3(s) under `heated` as Na2CO3(s) + H2O(g) + CO2(g), reusing the generic condition path and canonical products. The broader family remains unsupported: KHCO3 is a negative boundary, and cation-derived carbonate selection must not be dynamically fabricated. |
| nitrate thermal decomposition | C | Product families vary by cation and can involve nitrites, oxides, NO2, and O2; generic selection requires classification and redox decisions. |
| chlorate / permanganate decomposition | C | Catalyst/heat context and redox-dependent products exceed current controlled conditions and simple eligibility facts. |
| ammonium-salt decomposition | C | Products vary substantially by anion and conditions; no single safe generic family exists. |
| H2O2 decomposition | B | One bounded exact-product Rule is feasible after adding evidence-backed catalyst/condition representation; broader peroxide redox remains C. |
| common laboratory gas preparation | B | Existing CO2, SO2, NH3, and H2 preparations are A; extending the cluster to O2/Cl2 and heated preparations needs a small condition-aware family or, for redox cases, escalation to C. |

### Representative elements

| Cluster | Primary | Current assessment |
|---|:---:|---|
| Na | A | Strong-electrolyte salts, Na + water, and multiple acid/gas-evolution counterions are established. |
| Mg | A | Acid, CuSO4, and AgNO3 paths are established; hot-water/steam is separately B. |
| Al | C | Passivation, amphoterism, aluminate/speciation, and variable conditions dominate the missing coverage. |
| Fe | C | Fe2+/Fe3+, steam, displacement, and redox selection need coordinated semantics; only a bounded steam case is plausibly B. |
| Cu | C | Cu2+ is canonical, but Cu+/Cu2+, oxidizing acids, and displacement-product selection remain unresolved. |
| Ag | A | Ag+, AgNO3, AgCl/AgBr/AgI, and elemental Ag are established and reusable. |
| C / CO / CO2 | B | Carbonate acid evolution is A, but combustion/CO oxidation and broader interconversion need a small bounded exact-product family. |
| Si / SiO2 | B | Canonical identities and a few exact high-school transformations are feasible, but no current Rule family selects them. |
| N / NH3 / NO / NO2 / HNO3 | C | Ammonia liberation is A; oxidation sequence, nitric-acid redox, and competing nitrogen oxides require new redox/condition semantics. |
| S / H2S / SO2 / SO3 / H2SO4 | C | Sulfite/thiosulfate acidification is A; the broader oxidation-state network is not. |
| Cl2 / HCl / hypochlorite | C | HCl families are A; chlorine displacement and alkali disproportionation need ordering and conditional redox pathways. |

### Organic architecture readiness

| Family | Primary | Current assessment |
|---|:---:|---|
| complete combustion of a bounded canonical substrate | B | Existing composition and balancer can validate fixed CO2/H2O products, but no organic classification/Rule family exists. |
| substitution | D | Requires organic identity, structural sites, and product/regioselectivity semantics outside the active schema. |
| addition | D | Requires bond/structure semantics and competing products. |
| elimination | D | Requires structural and condition-dependent product selection. |
| esterification | D | Requires functional-group identity, reversible/equilibrium semantics, and broader organic ownership. |
| hydrolysis | D | Requires functional groups, medium/context, and equilibrium/product selection. |
| organic oxidation | D | Requires functional-group/oxidation-state transformations and reagent-dependent products. |
| polymerization | D | Requires repeat-unit/polymer identity and non-discrete stoichiometric semantics. |

## TeachingView coverage across D01–D11

TeachingView is a pedagogical projection, not ontology or inference ownership. The single current view has nodes only in D02, D03, D05, D06, D08, and D10.

| Area | Primary | Current state and next use |
|---|:---:|---|
| D01 kinetics and equilibrium | D | No kinetics/equilibrium engine; retain as later domain expansion. |
| D02 electrolyte solutions | C | Strong-electrolyte projection is mature, but the area as a whole needs weak/partial equilibrium semantics. |
| D03 reaction types | C | Fourteen bounded Rules exist; broad redox and competing pathways keep the overall area architecture-limited. |
| D04 chemical calculations | D | Exact equation balancing exists, but a general quantitative calculation engine is not in current scope. |
| D05 chemical experiments | C | The ammonium test is mapped through Reactions; active schema has no executable Experiment owner. |
| D06 notation and stoichiometry | A | Molecular, complete ionic, net ionic, exact balancing, and conservation are the strongest current coverage; all M21 Reactions are mapped. |
| D07 solutions and colloids | D | One MaterialSystem and strong-electrolyte projection do not constitute a solution/colloid state model. |
| D08 classification of substances | A | Faceted canonical classification is established; add only evidence-backed facets and memberships. |
| D09 structure and periodicity | D | Active schema has no Structure record or structure-aware inference. Element identity alone is not D09 coverage. |
| D10 elements and compounds | C | Several inorganic clusters are present, but representative-element transformation networks remain architecture-sensitive. |
| D11 organic compounds | D | No active organic/structure owner; audit only until a separate domain expansion is approved. |

## Rule reuse audit

The canonical-example counts below are exact canonical matches, not merely fixture matches.

| Existing Rule | Canonical positives | Current reuse | Required negative / UNKNOWN pressure | Post-M21 result |
|---|---:|---|---|---|
| `rule_f2_agcl_precipitation` | 19 | AgCl/AgBr/AgI, BaSO4, Ca/Ba/Mg/Zn carbonates | all-soluble pairs; missing medium; unknown product solubility; insoluble input; two-precipitate ambiguity | Batch A data reuse |
| `rule_f2_strong_acid_base_neutralization` | 6 | HCl/HNO3/HBr across NaOH/KOH | missing medium; weak/absent strength; non-base salt contrast | 2 M21 Reactions |
| `rule_m5_strong_acid_hydrogen_carbonate_gas_evolution` | 6 | HCl/HNO3/HBr across NaHCO3/KHCO3 | missing medium; carbonate/sulfite must not bind | 2 M21 Reactions |
| `rule_m6_strong_acid_carbonate_gas_evolution` | 6 | HCl/HNO3/HBr across Na2CO3/K2CO3 | missing medium; hydrogen carbonate and sulfate contrasts | 2 M21 Reactions |
| `rule_m7_ammonium_strong_base_gas_evolution` | 6 | NH4Cl/(NH4)2SO4/NH4NO3 across NaOH/KOH | missing warmed condition; non-ammonium salt; missing speciation | unchanged regression coverage |
| `rule_m8_strong_acid_sulfite_gas_evolution` | 6 | HCl/HNO3/HBr across Na2SO3/K2SO3 | missing medium; sulfate and thiosulfate contrasts | 2 M21 Reactions |
| `rule_m9_acid_thiosulfate_decomposition` | 2 | Existing Na/K thiosulfates already provide counterion coverage | HNO3 redox fact absent => UNKNOWN; sulfate contrast; missing medium | regressions only |
| `rule_m10_active_metal_non_oxidizing_acid_hydrogen` | 2 | Additional cases only where cation and non-oxidizing acid behavior are unambiguous | Cu below H; HNO3 UNKNOWN; missing medium; no valence guessing | regressions only |
| `rule_m11_water_reactive_metal_hydrogen` | 2 | Li is a possible later data-only case | Cu/Zn/Mg UNKNOWN; wrong water phase; missing temperature | regressions only |
| `rule_m19_generic_aqueous_metal_salt_displacement` | 6 | Zn/Mg reuse the same pairwise Cu2+/Ag+ assertions across CuSO4, AgNO3, and CuCl2 | self/reverse/Na/K and unsupported pairs remain UNKNOWN; missing/ambiguous speciation or product relations never mint products | active generic owner; M12/M13 reactions remain regressions |

## M12/M13 duplication threshold

Resolved by M19 without a third exact-salt Rule. The bound salt exposes one positive ion through canonical complete-dissociation speciation; applicability compares that ion with an authored pairwise `metal.displaces_cation` assertion; the displaced metal follows one evidence-backed `ion.elemental_substance` hop; and the incoming salt still uses `metal.product_cation` plus `ionic_pair`.

M12/M13 remain historical chemistry and canonical-Reaction regression anchors, but their exact CuSO4/AgNO3 Rule records are no longer active. CuCl2 is the third-salt proof for the same M19 family. M20 now owns exact pairwise known-negative Relation facts through `relation_assertions[].truth`; still unresolved are general no-reaction truth, activity ordering/transitivity, water competition, variable valence, passivation, concentration-sensitive redox, and a general redox engine.

## Historical Batch A — data-first cross-family expansion

### Scope and acceptance

Batch A added **21 canonical Entities** and **27 canonical Reactions**, plus authoritative evidence, focused positive/negative/UNKNOWN cases, and TeachingView memberships. Its accepted scope was designed to reuse six existing Rules with zero changes to compiler, schema, DSL, RulePlan, and artifact format. The retained list below records that accepted scope.

### Candidate Entity set (21)

- salts/products: K2SO4, KHCO3, NH4NO3, CuCl2;
- bromine set: Br Element, Br- Species, NaBr, KBr, AgBr;
- iodine set: I Element, I- Species, NaI, KI, AgI;
- calcium/carbonate set: Ca Element, Ca2+ Species, CaCl2, CaCO3, BaCO3, MgCO3, ZnCO3.

Reuse all existing H+, OH-, Cl-, NO3-, SO4^2-, CO3^2-, NH4+, Na+, K+, Mg2+, Zn2+, Ba2+, Ag+, H2O, CO2, SO2, NH3, acids, bases, and established salts. Do not duplicate any stable identity.

### Canonical Reaction set (27)

**Neutralization — 2**

- `HCl + KOH -> KCl + H2O`
- `HNO3 + NaOH -> NaNO3 + H2O`

Also add the missing positive fixture for the already-canonical `HNO3 + KOH` Reaction.

**Hydrogen carbonate, carbonate, and sulfite gas evolution — 4**

- `HCl + KHCO3 -> KCl + CO2 + H2O`
- `HNO3 + KHCO3 -> KNO3 + CO2 + H2O`
- `2 HNO3 + K2CO3 -> 2 KNO3 + CO2 + H2O`
- `2 HNO3 + K2SO3 -> 2 KNO3 + SO2 + H2O`

**Ammonium + strong base, warmed — 4**

- `NH4Cl + KOH -> KCl + NH3 + H2O`
- `(NH4)2SO4 + 2 KOH -> K2SO4 + 2 NH3 + 2 H2O`
- `NH4NO3 + NaOH -> NaNO3 + NH3 + H2O`
- `NH4NO3 + KOH -> KNO3 + NH3 + H2O`

**Halide precipitation — 5**

- `AgNO3 + KCl -> AgCl + KNO3`
- `AgNO3 + NaBr -> AgBr + NaNO3`
- `AgNO3 + KBr -> AgBr + KNO3`
- `AgNO3 + NaI -> AgI + NaNO3`
- `AgNO3 + KI -> AgI + KNO3`

**Sulfate precipitation — 4**

- `BaCl2 + K2SO4 -> BaSO4 + 2 KCl`
- `BaCl2 + MgSO4 -> BaSO4 + MgCl2`
- `BaCl2 + ZnSO4 -> BaSO4 + ZnCl2`
- `BaCl2 + CuSO4 -> BaSO4 + CuCl2`

**Carbonate precipitation — 8**

- `CaCl2 + Na2CO3 -> CaCO3 + 2 NaCl`
- `CaCl2 + K2CO3 -> CaCO3 + 2 KCl`
- `BaCl2 + Na2CO3 -> BaCO3 + 2 NaCl`
- `BaCl2 + K2CO3 -> BaCO3 + 2 KCl`
- `MgSO4 + Na2CO3 -> MgCO3 + Na2SO4`
- `MgSO4 + K2CO3 -> MgCO3 + K2SO4`
- `ZnSO4 + Na2CO3 -> ZnCO3 + Na2SO4`
- `ZnSO4 + K2CO3 -> ZnCO3 + K2SO4`

### Evidence and fixture gates

Batch A must use authoritative, claim-scoped evidence for identity/composition, solubility, strong-electrolyte treatment, complete-dissociation profiles, reaction applicability, phase, and any warmed condition. Existing OpenStax Chemistry 2e and Cambridge/RSC sources may be reused only where their actual cited sections support the claim; legacy editorial provenance is a migration lead, not sufficient authority by itself.

Required contrasts include:

- all-soluble exchange pairs such as NaCl + KNO3 and KCl + NaNO3, with no precipitate candidate;
- missing aqueous medium => UNKNOWN where applicability depends on it;
- missing product solubility => UNKNOWN, never guessed from formula;
- insoluble input salts do not enter the two-soluble-salt precipitation family;
- an ambiguous two-precipitate outcome is not arbitrarily selected;
- HNO3 + thiosulfate remains UNKNOWN;
- missing warmed condition keeps ammonium/base applicability indeterminate;
- all M10–M13 positive and open-world regressions remain unchanged.

Every positive must prove exact balancing, atom/charge conservation, exact canonical match, complete/net ionic projection where applicable, spectator cancellation, provenance, and deterministic artifacts. TeachingView additions should use the existing D02, D03, D06, D08, and D10 paths; no new view is needed.

### Explicitly not in Batch A

- hydroxide precipitation;
- Ca/Mg/Fe + water or steam;
- weak acid/base or hydrolysis;
- thermal decomposition;
- halogen displacement or any broader redox family;
- Al/passivation/amphoterism;
- Fe/Cu variable-valence expansion;
- a third bounded metal/salt displacement Rule;
- generic metal/salt displacement or activity ordering;
- new Context, Relation, product-constructor, compiler, schema, or artifact semantics;
- legacy bulk import.

## Prioritized architecture-pressure backlog

| Priority | Chemistry pressure | Missing primitive / why current model is insufficient | Likely canonical owner | Dependencies and recommended timing |
|---|---|---|---|---|
| P0 | variable-valence product selection | `metal.product_cation` is intentionally one target per context; Fe/Cu/Mn chemistry needs evidence-backed context/pathway selection rather than a guessed charge | domain facts/Relations plus applicability contract | Resolve before Fe/Cu displacement or broad redox |
| P0 | activity ordering and general no-reaction truth | Pairwise positive/negative Relations are non-transitive and absence is UNKNOWN; general ordering, self-displacement, water competition, and global pathway exclusion remain unowned | ontology/Relation and pathway semantics | Separate future architecture; do not weaken M19/M20's pairwise gate |
| P1 | oxidizing-acid metal reactions | Concentration, passivation, metal identity, and NO/NO2/SO2 product competition are not represented | Context, reaction-family applicability, canonical redox model | After condition vocabulary and redox direction are settled |
| P1 | passivation | Surface/material state and concentration-qualified reactivity cannot be represented by a global activity facet | contextual Fact/MaterialSystem design | Before Al/Fe concentrated-acid coverage |
| P1 | broader redox semantics | Oxidation states, electron conservation, half-reaction composition, medium-dependent products, and competing pathways are absent | separate redox compiler/domain contract; exact balancer remains downstream | Dedicated architecture milestone; do not accrete exact-ID branches |
| P1 | weak/partial equilibrium and speciation | Complete dissociation cannot represent weak acids/bases, hydrolysis, buffers, amphoterism, or concentration-dependent species | speciation/equilibrium domain model and aqueous projector | Start with a bounded decision record; full solver remains D |
| P1 | richer controlled conditions | `heated` is now persistable and distinct from `warmed`; hot water, steam, concentrated/dilute reagent, catalyst, and light remain unmodeled | Context vocabulary and Reaction schema | Add only in separate bounded contract slices before dependent families |
| P2 | executable experiments | D05 currently maps Reactions only; safety, observation, apparatus, and procedure have no active record owner | source schema + Experiment contract + TeachingView projection | Later, independently of equation Batch A |
| P2 | structure-aware inorganic/organic inference | Active schema has no Structure owner, so functional groups, sites, isomers, and polymers cannot drive products | separate Structure/domain architecture | Later domain expansion before D09/D11 inference |

## Legacy migration audit

The sibling inorganic package declares and physically contains 642 reviewed records:

| Legacy family | Count |
|---|---:|
| element projections | 48 |
| ions | 58 |
| substances | 194 |
| reactions | 152 |
| concepts | 64 |
| phenomena | 63 |
| experiments | 31 |
| exam tags | 32 |

Its seven rule projections are consumer aids, not authoritative chemistry records. `reviewed` and `READY_FOR_CONSOLIDATION` also do not mean that a claim is published or authoritative in this repository.

### Useful migration inputs

- reviewed formula/composition/charge candidates, stable legacy IDs as aliases, and element symbol/atomic-number cross-checks;
- Reaction participants, coefficients, phases, taxonomy, and net-ionic forms as review candidates;
- source references, solubility/electrolyte candidates, and curriculum groupings;
- curriculum coverage as input to existing TeachingView mappings.

### Required semantic reinterpretation

- legacy `species_id` must resolve separately to Element, Species, Substance, or MaterialSystem rather than be copied as one universal identity type;
- `category` becomes evidence-backed facets, not subclasses;
- `ambient_phase = aq` is a teaching/default-context statement, not an intrinsic pure-substance phase;
- `aqueous_behavior` and `ions` must become contextual properties and eligible speciation profiles; ionic composition alone never asserts free aqueous ions;
- condition strings must normalize into controlled Context or remain deferred;
- legacy IDs are aliases/crosswalk inputs and cannot bypass canonical identity reconciliation;
- Concept, Phenomenon, Experiment, and ExamTag records need an approved active owner before migration.

### Unsafe to bulk import

- editorial-only records without claim-level authoritative verification;
- generated consolidated outputs or cached projections;
- metal-activity, oxidation-state, solubility, or equation-composer rule projections as if they were canonical truth;
- variable-valence outputs collapsed to one guessed ion;
- weak-electrolyte, sparingly soluble, hydrolysis, or acid-equilibrium data forced into complete dissociation;
- phase/context flattened into identity;
- formula/name-only merges, including hydrates, allotropes, polymorphs, complexes, or polymers;
- symbolic/polymeric/non-discrete reactions without a stoichiometric projection basis;
- unverified external enrichment or a verification target treated as evidence.

### Future importer gates

Any future importer must be deterministic and idempotent and must stop for human resolution on ambiguity. Minimum gates are:

1. identity reconciliation and legacy-to-canonical crosswalk;
2. semantic-key collision and duplicate-referent review;
3. Entity-kind and referent-level separation;
4. active schema and reference validation;
5. claim-scoped evidence authority and redistribution review;
6. exact composition, charge, participant, atom, and charge-conservation validation;
7. controlled context/phase normalization;
8. speciation-profile eligibility, including explicit rejection of false complete dissociation;
9. preservation of UNKNOWN versus known false;
10. canonical Reaction/form ownership and no direct Substance-to-Substance truth edges;
11. repeated-run byte determinism and no generated-source contamination;
12. a review report for every skipped, merged, split, or downgraded record.

### M22 implemented pilot

The tracked cohort contains seven Element projections, six monatomic ions, and seven simple substances. Reconciliation is independent of legacy file order and verifies canonical referent facts rather than trusting formula/name lookup signals. Its five closed dispositions are `mapped_existing`, `created_canonical`, `skipped_unsupported`, `ambiguous`, and `rejected_invalid`; every decision is retained in `migration/reports/m22_pilot_report.json`.

Li is the sole canonical creation (`ent_element_li`, atomic number 3), supported by `ev_m22_lithium_identity` from the existing OpenStax source. Cu(I), aqueous/weak-equilibrium carbonic acid, and chlorine without authoritative creation evidence remain explicit skips. Synthetic proof covers equal-valid-candidate ambiguity and invalid legacy shapes. Reordered inputs and repeated runs produce byte-identical reports and never mutate canonical source.

Bulk migration, legacy Reactions, formula-derived creation, variable-valence selection, weak-equilibrium/speciation semantics, and Concept/Phenomenon/Experiment/ExamTag ownership remain unsafe and deferred.

### M23 identity Batch B

M23 promotes `migration/legacy_identity.py` as the sole reconciliation owner while retaining the M22 module as a compatibility entry point. The explicit 100-record cohort covers 48 Element, 32 monatomic-ion, and 20 simple-neutral-Substance candidates. Existing results are 18 Element, 13 ion, and 14 Substance mappings; the remaining 55 records are skipped with deterministic evidence or referent-shape reason codes. No M23 Entity or Evidence is added.

The strict Substance profile requires canonical Substance/pure-compound kind, neutral charge, exact composition, an exact canonical formula semantic key as a corroborating lookup signal, and an explicit curated simple-neutral referent-shape gate. It therefore cannot collapse Element into elemental Substance, Species into Substance, MaterialSystem into pure compound, or a network/allotrope/complex shape into a composition-only match. Synthetic ambiguity/invalid proofs remain in the shared M22 regression suite because the selected real records contain no natural collision or invalid row.

### M24 Reaction Pilot A

`migration/legacy_reaction.py` orchestrates participant resolution through `migration/legacy_identity.py`, validates roles, positive integral coefficients, common-factor normalization, exact atom/charge conservation, explicit phases, and the existing canonical Reaction signature/condition comparison. The 18 selected records span neutralization, precipitation, carbonate/hydrogen-carbonate and sulfite gas evolution, ammonium/base reactions, Zn/CuSO4 displacement, and CaCO3/NaHCO3 thermal decomposition. Sixteen map to existing canonical Reactions; calcium carbonate + HCl has no canonical Reaction and catalytic ammonia oxidation requires unsupported catalyst vocabulary, so both are deterministic `skipped_unsupported` results. Ambiguity and rejection remain zero in the real cohort and are covered synthetically.

Only explicit `s/l/g/aq` phases and the existing `aqueous`, `warmed`, and `heated` context meanings are admitted. Missing or conflicting required conditions, reverse direction, incompatible phase, unresolved identity, malformed coefficients, and failed conservation all fail closed. Legacy net-ionic data is diagnostic only: the cohort contains `compatible`, `unavailable`, and `unsupported_inconsistent` comparisons, while canonical ReactionForms continue to be derived exclusively from canonical Reaction/speciation data.

M25 pressure is therefore evidence rather than authorization: missing canonical Reaction ownership, catalyst/light and richer condition vocabulary, and broader polyatomic-ion identity support require separate bounded contracts. M24 does not bulk-process all 152 records or create any missing truth.

### M25 full Reaction audit and bounded curation

The full-corpus mode in `migration/legacy_reaction.py` consumes every Reaction file declared by the fixed legacy manifest revision and emits one sorted decision for each of 152 records. Before bounded curation it found 19 mappings, 124 unsupported skips, and nine rejected records; final dispositions are 20 `mapped_existing`, 123 `skipped_unsupported`, nine `rejected_invalid`, and zero ambiguous or automatically created results. Non-mapped records are classified as 88 `identity_gap`, 25 `context_gap`, ten `curation_gap`, nine `chemistry_architecture_gap`, and zero `invalid_legacy`. The nine reversible records are architecture gaps because equilibrium/reversibility is not owned by the current model; their migration disposition remains the existing fail-closed rejection.

The one Layer B curation is `rxn_m25_hcl_caco3_gas_evolution`: `CaCO3(s) + 2 HCl(aq) -> CaCl2(aq) + CO2(g) + H2O(l)`. Every participant and phase already existed, exact atom/charge conservation passes, and existing OpenStax-backed carbonate/acid and identity evidence supports the record independently of legacy data. No Evidence or Rule is added. CaCO3 remains known insoluble, so the soluble-carbonate Rule is neither weakened nor generalized; complete and net ionic forms are derived by the canonical projector.

ReactionForm diagnostics remain review material rather than a coverage KPI: among the 20 mappings, one legacy projection is compatible, 12 are unavailable, and seven are unsupported/inconsistent. Unresolved polyatomic ions in those diagnostics do not authorize identity expansion.

## Current migration decision

**M25 REACTION MIGRATION AUDIT COMPLETE; M6 EXIT READY.**

`M6_EXIT_READY = true`. Identity and Reaction migration are deterministic; all 152 legacy Reactions have explicit outcomes and future-action buckets; canonical source remains independently evidence-gated; and legacy data remains outside runtime. The remaining gaps are ordinary future curation or explicit context/identity/equilibrium architecture work, not missing migration machinery. No further migration milestone is required. The historical `M6_EXIT_READY` flag denotes migration exit, not completion of the M6 carbonate family or universal equation generation.
