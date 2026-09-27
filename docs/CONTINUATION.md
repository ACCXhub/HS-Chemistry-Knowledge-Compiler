# Continuing curriculum and prediction work

[简体中文](CONTINUATION.zh-CN.md)

The mainland compulsory/selective-compulsory goal remains incomplete: elements, substances, equations, general Rules, exact cases, independently distributed modules with shared identities, and later evidence-backed case transfer/prediction explanations. Predictions are not canonical facts; UNKNOWN is not impossible. Safe main commits/pushes are authorized. No subagents, repeat M0–M25 audit, reset, stash or rebase.

## Latest completed batch: iron solid oxides/hydroxides with acid

Published baseline: `3ab77d93b6f93b8744e10a7b22eb62fa015fa0ff` (iron chloride interconversion). This batch adds FeO, Fe2O3 and Fe(NO3)3, eight Reactions, four declarative Rules, eight positives and two UNKNOWN cases. Ordinary FeO/Fe(OH)2 dissolution requires positive non-oxidizing-acid evidence; HNO3 must not generate unreviewed Fe(II) salts. Fe(III) oxide/hydroxide dissolution supports HCl/HNO3, and ferric nitrate precipitation reuses M15. Runtime, schema, compatibility coordinates and migration code are unchanged.

Current source: 297 records, 117 Entities, 102 Reactions, 27 Rules, 159 cases, 43 profiles; 103 inferred, 43 indeterminate, 12 no_match, one blocked. All 102 canonical reactions have positives; removing all Reactions still generates 103 positives. Compiler 0.5.0; module roots/dependencies: elements 18/6, substances 99/62, equations 129/162.

## Validation and preservation

Validate and 35 focused tests pass, including valence, ionic equations, atom/charge conservation, phases, context, positive non-oxidizing evidence, input/Rule order and generation without stored Reactions. All 508 tests pass (443.48 seconds), log: `build/iron-solid-acid-pytest.txt`. Session `69693` has ended and needs no rerun. Bundle InferenceSession checks pass for eight positives and two UNKNOWN boundaries.

Compile/audit/bundle/modules are byte-identical across hash seeds 3/941; evidence: `build/iron-solid-acid-verification/`. Two M25 replays agree at 21 mapped, 122 unsupported and nine rejected. Historical reports remain unchanged. This batch is committed/pushed to main and final application-bundle/data-modules are regenerated from its SHA. Compare both manifest.source_revision values with HEAD to verify publication identity.

The previous batch passed all 482 tests (`build/iron-interconversion-pytest.txt`); that result does not replace this batch's validation. Earlier copper oxide work is preserved in `c751cf4`. Do not repeat completed audits/tests.

## Exact next steps

Run `git status --short --branch`, `git diff --stat`, `git rev-parse HEAD`, read this record and check actual quota. Preserve dirty work. Next prioritize Fe3O4/HCl mixed-valence dissolution and the separate Fe(OH)2/O2/H2O oxidation step in the [equation queue](CURRICULUM_COVERAGE.md). Do not guess one valence or merge later oxidation into precipitation.

Continue a finite textbook equation inventory, Al/nonmetal/organic/electrochemical coverage and necessary concentration, excess, catalyst, reversible and electrode semantics. Current counts do not prove textbook completeness. Automated analogy/model prediction is pending; existing Rules infer unstored equations only when supporting knowledge is sufficient.

## Website delivery and automation

The full bundle is the InferenceSession input; independent modules support database import, not runtime plugins. See [modules](contracts/DATA_PACKAGES.md), [Python API](contracts/APPLICATION_API.md) and [chem-wiki integration](contracts/CHEM_WIKI_INTEGRATION.md). Actual HTTP adaptation/database import remain unimplemented. README now points to the coverage matrix instead of duplicating counts.

Heartbeat `automation` remains ACTIVE with repaired Chinese encoding, every five hours and ten minutes, leaving ten minutes beyond the five-hour quota window. Check actual quota/reset each trigger; start closeout around 80%, preserve progress before exhaustion, wait quietly if quota has not recovered, never disable the schedule or declare the long-term goal complete. Usage reached 73% at closeout; do not open another Rule workstream this window. Reset: 2026-09-27 14:51:13 Beijing.
