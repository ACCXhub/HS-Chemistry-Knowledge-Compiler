# Continuing curriculum and prediction work

[简体中文](CONTINUATION.zh-CN.md)

The mainland compulsory/selective-compulsory goal remains incomplete: elements, substances, equations, general Rules and exact cases, independent modules with shared identities, and later evidence-backed case transfer/prediction explanations. Predictions are not canonical facts; UNKNOWN is not impossible. Safe main commits/pushes are authorized. No subagents, repeated M0–M25 audit, reset, stash or rebase.

## Latest completed batch: M16–M18 medium boundaries

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

Then continue Fe2O3/CO, thermite and the [equation queue](CURRICULUM_COVERAGE.md), Al/nonmetal/organic/electrochemical gaps and a finite textbook inventory. Current counts do not prove curriculum completeness. Concentration, excess, catalysts, reversibility and electrodes require necessary semantics; automated analogy/model prediction is not implemented.

## Website and automation

[Modules](contracts/DATA_PACKAGES.md), [Python API](contracts/APPLICATION_API.md) and [chem-wiki integration](contracts/CHEM_WIKI_INTEGRATION.md) are synchronized. Full bundles run InferenceSession; independent modules support database import. HTTP adaptation and actual database import remain pending.

Heartbeat `automation` remains ACTIVE every five hours and ten minutes. Check quota each trigger, start closeout around 80%, wait quietly if unrecovered, never disable the schedule or mark the long-term goal complete. This turn started with ordinary quota recovered, five-hour usage 5%; reset 2026-09-28 01:20:55 Beijing. Query current limits on each trigger.
