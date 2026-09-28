# Continuing curriculum and prediction work

[简体中文](CONTINUATION.zh-CN.md)

The mainland compulsory/selective-compulsory goal remains incomplete: elements, substances, equations, general Rules and exact cases, independent modules with shared identities, and later evidence-backed case transfer/prediction explanations. Predictions are not canonical facts; UNKNOWN is not impossible. Safe main commits/pushes are authorized. No subagents, repeated M0–M25 audit, reset, stash or rebase.

## Latest completed batch: aluminium alkali endpoints (2026-09-28)

Compiler 0.7.0/source schema 3.9.0 adds alkali_regime (precipitation_endpoint/excess) to public input and canonical conditions. Two AlCl3/NaOH Rules specialize M15 and choose Al(OH)3 or Na[Al(OH)4]; omission stays UNKNOWN. Existing match/balance/ionic/canonical owners are reused. Cached Chemguide material supports the endpoints under the documented coordinated-water convention. No numeric amount or equilibrium solver is implied.

All 51 focused tests and validate pass; the stale M15 unresolved-AlCl3 test now expects indeterminate for missing regime. Version assertions updated to 3.9.0. Current: 377 records, 127 Reactions, 51 Rules, 186 cases; 128 inferred, 45 indeterminate, 12 no_match, one blocked. No full-suite rerun. Next: CO2/base quantity branches and nonmetals; revisit prior Al/base source and ambient assumptions. Full curriculum, predictions, final audit and chem-wiki remain pending; existing automation stays ACTIVE.

## Previous batch: halogen displacement and metal thermal pathways (2026-09-28)

Add ten equations/Rules and Br2/I2 identities: Cl2 with NaBr/KBr/NaI/KI, Br2 with NaI/KI, Cu/O2, Al/O2, Al/steam, and Al(OH)3 thermal decomposition. Halogen paths use aqueous/ambient with separated Br2(l)/I2(s) teaching products, not final dilute-solution or triiodide speciation. Thermal paths require non_aqueous/heated and explicit steam where applicable.

Reviewed cached OpenStax 18.11/17.3/18.9 and NCERT 3.2.1/3.2.2. Corrected the 17.3 answer's Br2(s) typo using the ambient-liquid description in 18.11. Validate and 35 targeted tests pass, including Reaction-independent generation, boundaries, bundle and module exports. Current: 372 records, 125 Reactions, 49 Rules, 184 cases; 126 inferred, 45 indeterminate, 12 no_match, one blocked; all 125 Reactions have positive fixtures.

Next: quantity-qualified Al3+/OH- precipitation/excess dissolution, then CO2/base and nonmetal paths. Recheck the previous aluminium/base batch's broad OpenStax attribution and ambient applicability against specific source passages. Curriculum completion, model generalization, final audit and chem-wiki delivery remain pending.

## Previous batch: aqueous aluminium/alumina base pathways

Base `34f55f9ec0941560e9f16aa54cb67c0addaba1d3`. Add the canonical equations `2Al + 2NaOH + 6H2O -> 2Na[Al(OH)4] + 3H2` and `Al2O3 + 2NaOH + 3H2O -> 2Na[Al(OH)4]`, plus two exact declarative Rules. Liquid water, aqueous/ambient context and phases are explicit. Reuse the `[Al(OH)4]-`/`Na[Al(OH)4]` aqueous representation; do not alias `NaAlO2`, and do not choose a precipitation or excess-base endpoint from an unspecified `Al3+ + NaOH` amount.

Validate passes; 25 focused aluminium/aluminate/application-bundle tests pass; both net-ionic forms are derived by the existing projector and conserve atoms/charge. Current source has 345 records, 115 canonical Reactions, 39 Rules, 174 fixtures and 45 speciation profiles: 116 inferred, 45 indeterminate, 12 no_match and one blocked. Every canonical Reaction has a positive fixture. No compiler/schema change and no full-suite rerun.

Next: add the minimum quantity-boundary semantics needed for `Al3+ + NaOH` precipitation versus excess dissolution, then continue bounded aluminium acid/base cases. Follow the finite textbook equation queue for halogens, sulfur, nitrogen, organic and electrochemical topics. Model candidates remain separate from canonical facts; UNKNOWN is not impossible.

## Previous batch: aqueous aluminate and hydroxide/base dissolution

Base `5f4d322ba98f317f600dfa2d99b7f5fa9bb383d4`. Add Al(OH)3, [Al(OH)4]- and Na[Al(OH)4], one solid-hydroxide/NaOH Rule and canonical equation. No unspecified AlCl3/NaOH endpoint inference. Chemguide `inorganic/complexions/aquaoh.html` and `aloh.gif` were read; cached under `build/curriculum-review/`. Bilingual API explains omission of coordinated spectator water and forbids NaAlO2 as an identity alias.

Validate passed; 23 existing acid/bundle tests passed. The new test initially used aqueous instead of the established dissolved ionic phase; corrected test passed separately. Initial log `build/aluminate-tests.txt`; rerun terminal: 1 passed. Single-seed compile/audit/bundle/modules and complete positive coverage passed (`build/aluminate-verification/`, `build/aluminate-verification.txt`). No two-seed, M25 or full-suite rerun this batch; no compiler/schema edits. Quota reached 80%; closeout only, no live processes.

After this batch, Al/NaOH and Al2O3/NaOH are complete with explicit aqueous water inputs. The next bounded item is quantity semantics for precipitation/excess dissolution. Do not repeat source searches; guessed Chemguide group3/oxides(h).html and period3/oxides.html returned 404. Automation remains ACTIVE; query the live reset time on each trigger.

## Previous batch: aluminium and alumina with acid

Base `2f57d24d766d8a63101fdbd81c3aedd9452b32f7`. Add Al3+, aqueous AlCl3 dissociation and aluminium metal/activity/product-cation facts. 2Al+6HCl -> 2AlCl3+3H2 reuses unchanged M10; Al2O3+6HCl -> 2AlCl3+3H2O adds one ionic_pair-based acid Rule. No false basic-oxide classification, solid dissociation, valence guessing or activity ordering.

Evidence: saved NCERT 3.2.1 alumina/HCl equation and 3.2.3 aluminium/dilute-HCl experiment. All 38 focused equation/ionic-form/Reaction-independent/M10/bundle tests and validate pass. Initial missing ambient context correctly yielded UNKNOWN at the M10 frozen blocker; only the positive fixture was corrected. Compile/audit/bundle/modules match across seeds 3/941; M25 repeats at 19/124/9. Evidence `build/aluminium-acids-*`; no live process; no full-suite rerun.

Current: 333 records, 125 Entities, 112 Reactions, 36 Rules, 171 cases, 44 profiles; 113 inferred, 45 indeterminate, 12 no_match, one blocked. All 112 equations have positives. Module roots/dependencies: elements19/8, substances106/70, equations148/179. Re-export release bundles at final SHA.

Exact next step: explicitly distinguish aqueous [Al(OH)4]- from school NaAlO2 notation, then add Al/NaOH and Al2O3/NaOH. Al(OH)3 precipitation/excess dissolution needs explicit quantity boundaries rather than presenting an intermediate as the final excess-reagent outcome. Full curriculum and analogy goals remain incomplete.

## Previous batch: CO reduction and thermite

Base `03710ed66eec0cfc1b0dc86cc1c1fff609391d47`. Add Al element, CO/Al/Al2O3 substances, two canonical equations and exact declarative Rules: Fe2O3+3CO -> 2Fe(s)+3CO2; Fe2O3+2Al -> 2Fe(l)+Al2O3(s). Existing heated/non_aqueous contexts represent coarse school-level thermal conditions, not arbitrary mild warming, numeric temperatures, furnace intermediates, equilibrium gas ratios or kinetics.

Evidence: saved OpenStax 19.1 furnace reduction section and NCERT 3.4.4 explicit thermite equation. No generic redox engine. All 63 focused tests pass, including inference without stored Reactions, coefficients/phases, input order and context boundaries; validate passes. Compile/audit/bundle/modules match across seeds 3/941; M25 repeats at 19 mapped/124 skipped/9 rejected. Evidence `build/iron-reduction-*`; no live test processes; no full-suite rerun.

Current: 327 records, 123 Entities, 110 Reactions, 35 Rules, 169 cases; 111 inferred, 45 indeterminate, 12 no_match, one blocked. All 110 equations have positives. Module roots/dependencies: elements 19/8, substances 104/69, equations 145/176. Re-export release outputs using final commit SHA.

Next bounded batch: aluminium acid/base and amphoteric oxide paths. Inspect existing product construction and missing Al3+/aluminate representation; do not misclassify amphoteric oxide as solely basic. Explicitly distinguish school NaAlO2 from aqueous [Al(OH)4]-. Then continue the finite textbook inventory and nonmetal/organic/electrochemical gaps. Automated analogy is still pending.

## Previous batch: M16–M18 medium boundaries

Base `e7f8a71d07e82bf61b835fe8b22f1d64332c0d14`. All three Rules are now 1.1.0 and require both `medium: non_aqueous` and `temperature_regime: heated`. Canonical conditions, fixtures, tests and bilingual API/roadmap notes agree. Missing medium is indeterminate/UNKNOWN; aqueous is no_match. Neither produces a candidate. Compiler/schema versions and runtime code are unchanged.

Validation: 28 focused thermal tests and 21 application bundle/M25 tests pass; validate passes. No full-suite rerun under the current targeted-validation instruction. Compile/audit/bundle/modules are identical across seeds 3/941. All 108 canonical reactions retain positive cases; statuses remain 109 inferred, 45 indeterminate, 12 no_match, one blocked. Evidence/logs: `build/thermal-medium-*`.

M25 repeats identically at 19 mapped /124 skipped /9 rejected. Only `reaction:caco3-thermal` and `reaction:nahco3-thermal` changed from the previous batch, to context_gap because legacy conditions lack medium. Historical reports are preserved; migration was not loosened. Restoring these mappings requires sourced medium declarations, not assumptions from solid phases.

## Previous batch: mixed-valence iron oxide, oxidation and thermal reactions

Base: `89cb84993b7072eabe1d837f4a72beab11541fe8`. Add Fe3O4/O2 identities and six exact Rules/equations: Fe3O4/HCl, Fe(OH)2/O2/H2O, Fe/steam, Fe/O2, Fe/Cl2 and Fe(OH)3 decomposition. Magnetite retains Fe(II):Fe(III)=1:2. Hydroxide oxidation requires explicit oxygen and water, preserving the original precipitation step.

Initial tests exposed that missing medium makes an aqueous blocker UNKNOWN, not proof of a non-aqueous environment. Minimal extension: source schema 3.8.0/compiler 0.6.0 add `medium: non_aqueous`; all four new heated paths require it explicitly. It excludes an aqueous solution, not water vapor; omission has no default. Rule DSL/plan, artifact and bundle/module formats are unchanged. Version-coordinate tests are updated. API documentation corrects the former 1–2-reactant wording; the existing matcher supports three inputs.

Current source: 317 records, 119 Entities, 108 Reactions, 33 Rules, 167 cases, 43 profiles; 109 inferred, 45 indeterminate, 12 no_match, one blocked. All 108 canonical equations have positives; removal of Reactions preserves 109 generated cases. Module roots/dependencies: elements 18/6, substances 101/65, equations 141/170.

## Validation and preservation

Validate and 41 focused tests pass: mixed-valence ionic forms, coefficients/phases, missing heat/medium and aqueous boundaries, liquid-water exclusion, no assumed oxygen, and three-input public API. All 540 tests pass (463.78 seconds); log `build/iron-thermal-pytest.txt`. Session `34417` has ended; no rerun is needed.

Compile/audit/bundle/modules match across seeds 3/941; M25 replays agree at 21 mapped, 122 unsupported, nine rejected. Evidence: `build/iron-thermal-verification/`. Wheel 0.6.0 isolated build/install and isolated-Python inference pass; session `46005` ended, log `build/iron-thermal-wheel.txt`. The installed package/bundle infers explicit non-aqueous iron/steam and preserves UNKNOWN for missing medium. The global environment is unchanged.

Release outputs are `build/application-bundle` and `build/data-modules`; verify both manifest.source_revision values against final HEAD. Old 0.5.0 bundles must be re-exported; never edit manifests/hashes to bypass the strict loader.

Sources: OpenStax 19.1 (iron/chlorine, magnetite, oxides/hydroxides); Chemguide iron chemistry (air oxidation of Fe(OH)2); NCERT 3.2.2 PDF page 7 (iron/steam equation). NCERT supplies chemical evidence, not curriculum scope. Local source extracts are ignored under `build/curriculum-review/`.

## Exact next steps

Run `git status --short --branch`, `git diff --stat`, `git rev-parse HEAD`, read this record and check actual quota. Preserve dirty work; this batch has no remaining live test processes. M16–M18 medium corrections are complete; continue the equation queue without repeating this audit.

Fe2O3/CO and thermite are complete. Continue aluminium chemistry and the [equation queue](CURRICULUM_COVERAGE.md), Al/nonmetal/organic/electrochemical gaps and a finite textbook inventory. Current counts do not prove curriculum completeness. Concentration, excess, catalysts, reversibility and electrodes require necessary semantics; automated analogy/model prediction is not implemented.

## Website and automation

[Modules](contracts/DATA_PACKAGES.md), [Python API](contracts/APPLICATION_API.md) and [chem-wiki integration](contracts/CHEM_WIKI_INTEGRATION.md) are synchronized. Full bundles run InferenceSession; independent modules support database import. HTTP adaptation and actual database import remain pending.

Heartbeat `automation` remains ACTIVE every five hours and ten minutes. Check quota each trigger, start closeout around 80%, wait quietly if unrecovered, never disable the schedule or mark the long-term goal complete. This turn started with ordinary quota recovered, five-hour usage 5%; reset 2026-09-28 01:20:55 Beijing. Query current limits on each trigger.
