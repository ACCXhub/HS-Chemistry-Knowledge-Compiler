# Mainland high-school curriculum coverage

[简体中文](CURRICULUM_COVERAGE.zh-CN.md)

The acceptance target is mainland China's compulsory and selective-compulsory high-school chemistry. **Coverage is incomplete; arbitrary reactions cannot be inferred from element tags.** This engineering checklist groups common teaching topics; it is not an official curriculum or a textbook's exhaustive equation inventory.

There are 108 canonical Reactions, 33 Rules and 167 fixtures. The 109 inferred cases cover all 108 canonical Reactions plus one unstored equation. The remaining 45 indeterminate, 12 no_match and one blocked outcomes are boundary proofs, not covered equations.

## Coverage checklist

Partial coverage applies only to admitted identities, properties, phases and conditions. Missing means no reviewed family, not proof that no chemical reaction occurs. Gap examples identify teaching needs rather than unvalidated source records.

| Topic | Status | Implemented scope / missing work |
| --- | --- | --- |
| Strong acid/base neutralization | Partial | HCl/HNO3/HBr with NaOH/KOH |
| Salt exchange precipitation | Partial | AgCl/AgBr, BaSO4 and selected carbonates; all cross-products require identity/solubility facts |
| Salt/base hydroxide precipitation | Partial | Cu/Mg/Fe(II)/Fe(III) hydroxides; Zn/Al and excess-base paths missing |
| Acid/bicarbonate and soluble carbonate | Partial | HCl/HNO3/HBr and Na/K salts; reagent-ratio intermediates missing |
| Acid/solid carbonate | Partial; extended here | Solid CaCO3/HCl and HNO3 now inferred; other solids, weak acids and coatings remain outside scope |
| Non-oxidizing acid/sulfite | Partial; corrected here | HCl/HBr and Na/K salts; two insufficiently supported nitric-acid gas-evolution records withdrawn |
| Acid/thiosulfate | Partial | Two HCl cases and unstored HBr/Na2S2O3; HNO3 UNKNOWN |
| Ammonium/strong base | Partial | Explicit warmed condition; missing heat does not assert ammonia evolution |
| Metal/non-oxidizing acid | Partial | Zn/Mg/Fe with HCl; Al, passivation and variable valence missing |
| Metal/water or steam | Partial | Na/K ambient liquid water, exact Mg/heated steam and Fe/heated non-aqueous steam |
| Metal/salt displacement | Partial | Twelve curated Zn/Mg/Fe cases; explicit Cu/Fe-to-Zn2+ and Cu-to-Fe2+ negatives; missing relations UNKNOWN |
| Thermal decomposition | Exact pilots | CaCO3, NaHCO3 and Fe(OH)3; permanganate/chlorate, nitrates and other hydroxides missing |
| Basic oxide/acid and acidic oxide/base | Partial | Twelve Na2O/MgO/CaO/CuO/FeO/Fe2O3 acid cases plus three solid Fe hydroxide acid cases; CO2/NaOH still missing |
| Sodium oxides/peroxides | Partial | Na2O/water implemented; Na2O2 with water/CO2 still missing |
| Aluminum and amphoteric chemistry | Missing | Al/base, Al(OH)3 with acid/base, excess-reagent pathways |
| Iron and Fe2+/Fe3+ interconversion | Partial | Fe/acid, Cu salt displacement, Fe hydroxides and three FeCl2/FeCl3 redox cases; FeO/Fe2O3 and solid hydroxide acid dissolution now supported; Fe3O4/HCl, explicit hydroxide oxidation and heated Fe/O2, Fe/Cl2, Fe/steam are now supported; further anions remain missing |
| Halogens and halide redox | Two exact cases | Cl2(g) oxidizes FeCl2(aq); heated non-aqueous Fe/Cl2 yields solid FeCl3; chlorine water/bleaching, Cl2/base, displacement and reversibility remain missing |
| Sulfur redox | Missing | SO2 oxidation/reduction, concentrated H2SO4/Cu, selected H2S chemistry |
| Nitrogen chemistry | Missing | Ammonia synthesis/oxidation, NO/NO2, dilute/concentrated HNO3 with metals |
| Carbon, silicon and materials | Missing | C/CO reduction, Si/SiO2/silicates, industrial preparation |
| Reversible reactions/equilibrium | Missing | Ammonia synthesis, SO2 oxidation; irreversible records cannot represent full equilibrium |
| Weak electrolytes and hydrolysis | Missing | Acetic acid, aqueous ammonia, water, Fe/Al salts; no fictional complete dissociation |
| Solubility equilibria and complexes | Missing | Ksp, AgCl/ammonia, competing complexation/dissolution |
| Cells, electrolysis and half-reactions | Missing | Electrons, electrode/medium conditions; molecular balance is insufficient |
| Compulsory organic chemistry | Missing | Combustion, substitution/addition, ethanol oxidation, esterification |
| Selective-compulsory organic chemistry | Missing | Functional groups, elimination/hydrolysis, carbonyl/carboxyl chemistry, polymers and biomolecules |

## Proof of generation without stored equations

The pipeline matches identity/classification/phase and contextual facts or one-hop Relations, selects a Rule, resolves canonical products, balances and validates atoms/charge, then compares with stored Reactions. Stored equations do not select products.

Removing every Reaction and recompiling still generates all 109 positive cases across all 33 Rules with unchanged participants/candidate keys and canonical_match none. An evidence-backed HBr non-oxidizing-acid fact enables existing M9 to generate the unstored `2 HBr + Na2S2O3 -> 2 NaBr + SO2 + S + H2O`; no Reaction was added for it.

New combinations therefore work when identity/composition, classifications, contextual properties, speciation/Relations, canonical products and evidence are sufficient. A tag such as “active metal” or “oxidant” alone does not determine valence, selectivity or products. Conservation is necessary but does not establish chemical feasibility.

## Next acceptance work

Curriculum expansion is ongoing. Next acceptance step: freeze a finite equation checklist by chosen textbook chapters and prioritize common inorganic acid/base/oxide and Fe/Al gaps with evidence and boundary cases. Define necessary concentration, excess-reagent, catalyst, reversibility and electrode semantics before populating reactions that need them. Cover remaining organic/selective-compulsory topics in separate bounded batches. Count stored equations, executable coverage and boundaries separately. The oxide, ferrous and copper-nitrate batches are implemented; the listed missing families remain pending.

See the [application contract](contracts/APPLICATION_API.md) and [Chinese chem-wiki database integration note](contracts/CHEM_WIKI_INTEGRATION.md).

2026-09-27 oxide batch: one Na2O identity, six oxide/strong-acid equations, one Na2O/water special case and four Rules. Independent conservation supplies the missing coefficient (2 NaOH) in the printed OpenStax 18.9 example. All 443 tests pass. The curriculum and prediction objective remains ongoing; see [continuation](CONTINUATION.md).

2026-09-27 ferrous batch: five identities and ten canonical equations reuse M10/M15/M19 without new Rules. Added a pathway-local Fe-to-Zn2+ negative and Fe/HNO3 UNKNOWN boundary; later oxygen oxidation of Fe(OH)2 is a separate process. All 70 relevant tests pass.

2026-09-27 copper oxide/nitrate batch: three identities and eight equations, one CuO/acid Rule. Validate and 18 focused tests pass. Full run: 464 passed, two stale M12/M13 relation assertions corrected; all 27 affected tests then pass. Compile/audit/bundle/modules match across two hash seeds. See continuation for the exact ongoing scope.

## Next equation-level acceptance queue for iron chemistry

This is a finite engineering queue, not an exhaustive textbook inventory. Pending rows are teaching targets awaiting source, phase, condition and boundary review; they are not inference facts.

| Equation / pathway | Status |
| --- | --- |
| Fe + 2FeCl3 -> 3FeCl2 | Implemented: aqueous, ambient; Fe(s) |
| Cu + 2FeCl3 -> CuCl2 + 2FeCl2 | Implemented: aqueous, ambient; Cu(s), no elemental Fe product |
| 2FeCl2 + Cl2 -> 2FeCl3 | Implemented: aqueous, ambient; Cl2(g) |
| FeO + 2HCl -> FeCl2 + H2O | Implemented; requires known non-oxidizing acid, HNO3 stays UNKNOWN |
| Fe2O3 + 6HCl -> 2FeCl3 + 3H2O | Implemented for HCl and HNO3; ferric nitrate identity also supports hydroxide precipitation |
| Fe3O4 + 8HCl -> FeCl2 + 2FeCl3 + 4H2O | Implemented: aqueous/ambient, explicit Fe(II):Fe(III) = 1:2 |
| 4Fe(OH)2 + O2 + 2H2O -> 4Fe(OH)3 | Implemented: O2(g) and H2O(l) are explicit inputs; precipitation is unchanged |
| 2Fe(OH)3 -> Fe2O3 + 3H2O | Implemented: heated/non_aqueous; product water is gas |
| 3Fe + 4H2O(g) -> Fe3O4 + 4H2 | Implemented: heated/non_aqueous, water vapor required |
| 2Fe + 3Cl2 -> 2FeCl3 | Implemented: heated/non_aqueous, solid FeCl3 product |
| Fe2O3 + 3CO -> 2Fe + 3CO2 | Pending high-temperature reduction and identities |
| Fe2O3 + 2Al -> 2Fe + Al2O3 | Pending thermite initiation conditions and identities |

All 25 focused and 482 full-suite tests pass. The three implemented transformations use existing declarative exact Rules, balancing and ionic projection. No general redox engine is added. The Cu-to-Fe2+ negative excludes only the M19 displacement pathway; other UNKNOWN paths do not mean no reaction.

2026-09-27 iron solid/acid batch: FeO, Fe2O3 and Fe(NO3)3 identities, eight canonical equations and four Rules reuse ionic-pair construction and M15 precipitation. FeO/Fe(OH)2 acid dissolution requires positive non-oxidizing evidence; missing facts yield UNKNOWN and explicit oxidizing character yields FALSE for that pathway only. Other redox outcomes are not declared impossible. Neither solid hydroxide receives a fictional complete-dissociation profile. All 35 focused and 508 full-suite tests pass, along with two-seed compile/audit/bundle/modules determinism, M25 replay and bundle API checks.

2026-09-27 iron thermal/oxidation batch: six exact pathways and Fe3O4/O2 identities. New thermal cases require explicit non_aqueous plus heated; compiler 0.6.0/source schema 3.8.0 expose that condition. All 41 focused and 540 full-suite tests pass; two-seed outputs, migration replay and installed-wheel bundle inference also pass.
