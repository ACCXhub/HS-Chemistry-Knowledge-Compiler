# Coverage & Migration Audit — Batch Planning 1

## Decision

The canonical M13 revision `20ae98c6dc1911da46705600f04a33308c01504d` is a sound base for a data-first coverage expansion. The next implementation slice should be **Batch A**, a bounded cross-family addition of canonical chemistry data, evidence, fixtures, and TeachingView memberships that reuses the existing 11 Rules without changing `compiler/**`, `schemas/**`, or any compatibility coordinate.

This audit does not authorize Batch A implementation. It also does not authorize a third salt-specific metal-displacement Rule. Generic metal/salt displacement must receive a separate architecture decision before that family is expanded beyond the existing CuSO4- and AgNO3-bounded Rules.

## Baseline and method

The audit used the canonical YAML source, all 11 compiled Rules, all 47 fixtures, current contracts and architecture documents, the active schema, compiler product/balancing/aqueous-projection paths, and the sibling legacy inorganic package as read-only migration material. The sibling package was inspected at `a6311150436038ca06fa7b9d05de39da9e1de815`; it is not a source of canonical truth for this repository.

Canonical Reaction coverage below was measured by submitting each Reaction's molecular reactants to the compiler with its required standard execution context. This matters because most Reaction records do not persist an aqueous/ambient condition while inference cases supply it; M7 and M11 do own explicit Reaction conditions. All 24 Reactions produced one exact canonical match under the applicable context.

### Current counts

| Measure | Count |
|---|---:|
| all canonical records | 135 |
| Entity | 73 |
| Evidence | 21 |
| Reaction | 24 |
| Rule | 11 |
| Source | 5 |
| TeachingView | 1 |
| Element / Species / Substance / MaterialSystem | 13 / 18 / 41 / 1 |
| inference cases | 47 |
| speciation profiles | 27 |
| facet assertions | 67 |
| property assertions | 64 |
| `metal.product_cation` assertions | 4 |
| `metal.displaces_cation` assertions | 4 |
| TeachingView paths / memberships / unique members | 14 / 115 / 70 |
| fixture results: inferred / indeterminate / blocked | 22 / 24 / 1 |

Raw record volume is diagnostic, not the KPI. The useful KPI is the number of important high-school chemistry families that are correctly expressible, canonically matched, provenance-bearing, and conservative under missing knowledge.

### Locked compatibility coordinates

| Axis | Version |
|---|---|
| source schema | `3.5.0` |
| Rule DSL | `1.3.0` |
| RulePlan | `1.3.0` |
| artifact format | `1.4.0` |

## What the current compiler actually supports

The executable core is sufficient when all of the following are true:

- reactants can be selected through exact identities, entity kinds, phases, facets, contextual property predicates, or the existing exact-target Relation predicate;
- products are already canonical and can be selected by `exact_entity`, `semantic_key`, `ionic_pair`, or `exchange_product`;
- any required aqueous ions come from a unique evidence-bearing `strong_electrolyte_complete_dissociation` profile;
- the products are fixed before balancing and the exact integer balance has one free variable;
- canonical comparison is based on the balanced participant signature plus compatible stored Reaction conditions;
- missing facts and Relations may remain UNKNOWN without being converted to known negatives.

Important boundaries are equally concrete:

- precipitation currently requires two aqueous `classification.salt` participants, unique complete-dissociation profiles, pre-existing cross-pair products, and exactly one insoluble driving product;
- ionic projection does not model weak/partial equilibria, hydrolysis, or concentration-dependent speciation;
- Relation execution is one-hop and exact-target only, for `metal.product_cation` and `metal.displaces_cation`; it is not graph traversal or activity ranking;
- `metal.product_cation` is one-target-per-context; `metal.displaces_cation` is many-target-per-context, but exact duplicate assertions are invalid;
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
| self-displacement and general no-reaction truth | C | Missing pairwise assertions currently mean UNKNOWN. Known negatives need an explicit, auditable semantic owner rather than absence-as-false. |
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
| Na | A | Strong-electrolyte salts and Na + water are established; Batch A can deepen counterion coverage. |
| Mg | A | Acid, CuSO4, and AgNO3 paths are established; hot-water/steam is separately B. |
| Al | C | Passivation, amphoterism, aluminate/speciation, and variable conditions dominate the missing coverage. |
| Fe | C | Fe2+/Fe3+, steam, displacement, and redox selection need coordinated semantics; only a bounded steam case is plausibly B. |
| Cu | C | Cu2+ is canonical, but Cu+/Cu2+, oxidizing acids, and displacement-product selection remain unresolved. |
| Ag | A | Ag+, AgNO3, AgCl, and elemental Ag are reusable; Batch A can add AgBr/AgI as precipitation data. |
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
| D02 electrolyte solutions | C | Strong-electrolyte projection is mature, but the area as a whole needs weak/partial equilibrium semantics. Batch A may add strong-electrolyte memberships only. |
| D03 reaction types | C | Eleven bounded families exist; broad redox and competing pathways keep the overall area architecture-limited. Batch A should deepen existing A families. |
| D04 chemical calculations | D | Exact equation balancing exists, but a general quantitative calculation engine is not in current scope. |
| D05 chemical experiments | C | The ammonium test is mapped through Reactions; active schema has no executable Experiment owner. |
| D06 notation and stoichiometry | A | Molecular, complete ionic, net ionic, exact balancing, and conservation are the strongest current coverage. Extend mappings with every Batch A Reaction. |
| D07 solutions and colloids | D | One MaterialSystem and strong-electrolyte projection do not constitute a solution/colloid state model. |
| D08 classification of substances | A | Faceted canonical classification is established; add only evidence-backed facets and memberships. |
| D09 structure and periodicity | D | Active schema has no Structure record or structure-aware inference. Element identity alone is not D09 coverage. |
| D10 elements and compounds | C | Several inorganic clusters are present, but representative-element transformation networks remain architecture-sensitive. |
| D11 organic compounds | D | No active organic/structure owner; audit only until a separate domain expansion is approved. |

## Rule reuse audit

The canonical-example counts below are exact canonical matches, not merely fixture matches.

| Existing Rule | Canonical positives | High-value reuse | Required negative / UNKNOWN pressure | Batch A disposition |
|---|---:|---|---|---|
| `rule_f2_agcl_precipitation` | 2 | AgCl/AgBr/AgI, BaSO4, Ca/Ba/Mg/Zn carbonates | all-soluble pairs; missing medium; unknown product solubility; insoluble input; two-precipitate ambiguity | 17 new Reactions |
| `rule_f2_strong_acid_base_neutralization` | 2 | HCl + KOH; HNO3 + NaOH | missing medium; weak/absent strength; non-base salt contrast | 2 new Reactions plus HNO3 + KOH fixture |
| `rule_m5_strong_acid_hydrogen_carbonate_gas_evolution` | 2 | HCl/HNO3 + KHCO3 | missing medium; carbonate/sulfite must not bind | 2 new Reactions |
| `rule_m6_strong_acid_carbonate_gas_evolution` | 3 | HNO3 + K2CO3 | missing medium; hydrogen carbonate and sulfate contrasts | 1 new Reaction |
| `rule_m7_ammonium_strong_base_gas_evolution` | 2 | NH4Cl/(NH4)2SO4 + KOH; NH4NO3 + NaOH/KOH | missing warmed condition; non-ammonium salt; missing speciation | 4 new Reactions |
| `rule_m8_strong_acid_sulfite_gas_evolution` | 3 | HNO3 + K2SO3 | missing medium; sulfate and thiosulfate contrasts | 1 new Reaction |
| `rule_m9_acid_thiosulfate_decomposition` | 2 | Existing Na/K thiosulfates already provide counterion coverage | HNO3 redox fact absent => UNKNOWN; sulfate contrast; missing medium | regressions only |
| `rule_m10_active_metal_non_oxidizing_acid_hydrogen` | 2 | Additional cases only where cation and non-oxidizing acid behavior are unambiguous | Cu below H; HNO3 UNKNOWN; missing medium; no valence guessing | regressions only |
| `rule_m11_water_reactive_metal_hydrogen` | 2 | Li is a possible later data-only case | Cu/Zn/Mg UNKNOWN; wrong water phase; missing temperature | regressions only |
| `rule_m12_metal_copper_sulfate_displacement` | 2 | Existing Zn/Mg targets already prove reuse | Cu/Na/K and unsupported salt targets remain UNKNOWN | regressions only |
| `rule_m13_metal_silver_nitrate_displacement` | 2 | Existing Zn/Mg multi-target assertions already prove reuse | Ag self-displacement and Na/K/Cu remain UNKNOWN | regressions only |

## M12/M13 duplication threshold

Do **not** add a third exact-salt displacement Rule.

M12 and M13 were deliberately healthy bounded proofs: the same one-hop exact-target Relation predicate, relation-derived product cation, speciation-derived anion, and canonical `ionic_pair` resolver worked for Cu2+/SO4^2- and Ag+/NO3-. A third salt-specific Rule would copy participant discovery and displaced-product mapping while avoiding the real design questions. Before another salt target is added, a separate architecture slice must decide:

1. how a bound salt exposes its displaced cation;
2. how that ion maps to an existing elemental Substance without reverse/arbitrary traversal;
3. how the incoming metal's product cation is chosen under variable valence;
4. whether applicability is pairwise evidence, an ordered activity model, or another controlled relation;
5. how aqueous water competition, passivation, and conditions override nominal activity;
6. how known negatives differ from absent/open-world knowledge.

Until then M12/M13 stay as regression anchors, not a template to multiply.

## Proposed Batch A — data-first cross-family expansion

### Scope and acceptance

Batch A should add approximately **21 new canonical Entities** and **27 canonical Reactions**, plus authoritative evidence, focused positive/negative/UNKNOWN cases, and TeachingView memberships. It should reuse six existing Rules and expect zero changes to compiler, schema, DSL, RulePlan, and artifact format. Exact IDs below are planning candidates following current conventions; implementation must reconcile identity and evidence before authoring.

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
| P0 | generic metal + salt displacement | Bound-salt cation discovery plus dynamic displaced-metal and incoming-salt product resolution; exact-target M12/M13 Rules cannot generalize this safely | Rule DSL/RulePlan product and predicate contracts, Relation contracts, canonical domain assertions | Design before any third salt-specific Rule |
| P0 | ion -> elemental Substance mapping | Current identities distinguish Element, ion Species, and elemental Substance; no controlled forward mapping exists and arbitrary reverse traversal is forbidden | source Relation contract and domain data, with one-hop runtime semantics if approved | Coordinate with generic displacement design |
| P0 | variable-valence product selection | `metal.product_cation` is intentionally one target per context; Fe/Cu/Mn chemistry needs evidence-backed context/pathway selection rather than a guessed charge | domain facts/Relations plus applicability contract | Resolve before Fe/Cu displacement or broad redox |
| P0 | activity ordering and known negatives | Pairwise positive Relations are non-transitive and absence is UNKNOWN; general ordering, self-displacement, water competition, and negative truth lack an owner | ontology/Relation and predicate semantics | Decide together with generic displacement, not as a numeric shortcut |
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

## Batch A readiness decision

**READY_FOR_BATCH_A**, subject to a new explicitly authorized implementation task.

Batch A should remain a data/evidence/test/TeachingView slice with zero production compiler and schema changes. Any discovered need for a new predicate, constructor, Relation family, condition vocabulary, or compatibility bump is a stop signal: remove that case from Batch A or promote it to the architecture backlog instead of expanding scope in place.
