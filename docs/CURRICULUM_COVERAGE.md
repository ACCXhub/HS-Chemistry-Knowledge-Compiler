# Mainland high-school curriculum coverage

[简体中文](CURRICULUM_COVERAGE.zh-CN.md)

The acceptance target is mainland China's compulsory and selective-compulsory high-school chemistry. **Coverage is incomplete; arbitrary reactions cannot be inferred from element tags.** This engineering checklist groups common teaching topics; it is not an official curriculum or a textbook's exhaustive equation inventory.

There are 66 canonical Reactions, 15 Rules and 119 fixtures. The 67 inferred cases cover all 66 canonical Reactions plus one unstored equation. The remaining 39 indeterminate, 12 no_match and one blocked outcomes are boundary proofs, not covered equations.

## Coverage checklist

Partial coverage applies only to admitted identities, properties, phases and conditions. Missing means no reviewed family, not proof that no chemical reaction occurs. Gap examples identify teaching needs rather than unvalidated source records.

| Topic | Status | Implemented scope / missing work |
| --- | --- | --- |
| Strong acid/base neutralization | Partial | HCl/HNO3/HBr with NaOH/KOH |
| Salt exchange precipitation | Partial | AgCl/AgBr, BaSO4 and selected carbonates; all cross-products require identity/solubility facts |
| Salt/base hydroxide precipitation | Partial | Cu/Zn/Mg hydroxides; Fe/Al and excess-base paths missing |
| Acid/bicarbonate and soluble carbonate | Partial | HCl/HNO3/HBr and Na/K salts; reagent-ratio intermediates missing |
| Acid/solid carbonate | Partial; extended here | Solid CaCO3/HCl now inferred; other solids, weak acids and coatings remain outside scope |
| Non-oxidizing acid/sulfite | Partial; corrected here | HCl/HBr and Na/K salts; two insufficiently supported nitric-acid gas-evolution records withdrawn |
| Acid/thiosulfate | Partial | Two HCl cases and unstored HBr/Na2S2O3; HNO3 UNKNOWN |
| Ammonium/strong base | Partial | Explicit warmed condition; missing heat does not assert ammonia evolution |
| Metal/non-oxidizing acid | Partial | Zn/Mg with HCl; Fe/Al, passivation and variable valence missing |
| Metal/water or steam | Partial | Na/K ambient liquid water, exact Mg/heated steam; Fe/steam missing |
| Metal/salt displacement | Partial | Six Zn/Mg with Cu2+/Ag+ cases; explicit Cu-to-Zn2+ negative; missing relations UNKNOWN |
| Thermal decomposition | Exact pilots | CaCO3 and NaHCO3; permanganate/chlorate, nitrates and hydroxides missing |
| Basic oxide/acid and acidic oxide/base | Missing | CuO/HCl, CO2/NaOH; amount-dependent products require explicit semantics |
| Sodium oxides/peroxides | Missing | Na2O/Na2O2 with water and CO2 |
| Aluminum and amphoteric chemistry | Missing | Al/base, Al(OH)3 with acid/base, excess-reagent pathways |
| Iron and Fe2+/Fe3+ interconversion | Missing | Oxidation, reduction, precipitation and observation evidence |
| Halogens and halide redox | Missing | Chlorine water/bleaching, Cl2/base, displacement and reversibility |
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

Removing every Reaction and recompiling still generates all 67 positive cases across all 15 Rules with unchanged participants/candidate keys and canonical_match none. An evidence-backed HBr non-oxidizing-acid fact enables existing M9 to generate the unstored `2 HBr + Na2S2O3 -> 2 NaBr + SO2 + S + H2O`; no Reaction was added for it.

New combinations therefore work when identity/composition, classifications, contextual properties, speciation/Relations, canonical products and evidence are sufficient. A tag such as “active metal” or “oxidant” alone does not determine valence, selectivity or products. Conservation is necessary but does not establish chemical feasibility.

## Next acceptance work

Recommend **curriculum coverage batch A** as the next milestone: freeze a finite equation checklist by chosen textbook chapters and prioritize common inorganic acid/base/oxide and Fe/Al gaps with evidence and boundary cases. Define necessary concentration, excess-reagent, catalyst, reversibility and electrode semantics before populating reactions that need them. Cover remaining organic/selective-compulsory topics in separate bounded batches. Count stored equations, executable coverage and boundaries separately. Those new families are not started in this pass.

See the [application contract](contracts/APPLICATION_API.md) and [Chinese chem-wiki database integration note](contracts/CHEM_WIKI_INTEGRATION.md).
