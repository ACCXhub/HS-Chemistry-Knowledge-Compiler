# Continuing curriculum and prediction work

[简体中文](CONTINUATION.zh-CN.md)

The long-term mainland compulsory/selective-compulsory goal remains incomplete. Preserve shared canonical identities across independently published element, substance and equation modules. Predictions must remain separate from curated facts; UNKNOWN is not impossible. Safe main commits/pushes are authorized. No subagents, repeated M0–M25 audit, reset, stash or rebase.

## Latest completed batch: Fe2+/Fe3+ chloride interconversion

Published baseline `c751cf4fb530ca8af334caccd43a4d291fcb358a` has matching final bundle/modules. This batch adds Cl2 identity, three exact declarative Rules/Reactions (Fe/FeCl3, Cu/FeCl3, FeCl2/Cl2), and explicit Cu-to-Fe2+ displacement FALSE. No potential calculation or general redox runtime.

Current source: 280 records, 114 Entities, 94 Reactions, 23 Rules, 149 cases and 42 profiles; 95 inferred, 41 indeterminate, 12 no_match, one blocked. Module roots/dependencies: elements 18/6, substances 96/60, equations 117/157. All 25 focused tests pass, covering ionic products, phase/context boundaries, independent generation and order invariance. All 482 tests pass (406.48 seconds); log: `build/iron-interconversion-pytest.txt`. InferenceSession also loads the bundle and infers all three new cases.

Validate passes; compile/audit/bundle/modules are byte-identical across hash seeds 3/941. All 94 canonical equations have positives. Two M25 replays still agree at 21 mapped, 122 unsupported, nine rejected. Evidence: `build/iron-interconversion-verification/`. The coverage matrix now contains a finite iron equation queue; next prioritize FeO/Fe2O3 acid pathways before mixed-valence oxides and hydroxide oxidation.

## Published baseline: copper oxide and nitrates, 2026-09-27

Based on ferrous commit `0db354e2aae013f0b8ca36e6be0028057b8f01b9`, add CuO, Ca(NO3)2 and Cu(NO3)2, eight Reactions, one CuO/strong-acid Rule and eight positive cases. Seven paths reuse existing Rules. Nitrate spectators do not make nitric acid non-oxidizing. No runtime/schema changes. M12/M13 tests now check their own displacement targets and evidence without freezing every future relation. Bilingual current counts, roadmap and historical audit labels are synchronized.

Current source: 272 records, 113 Entities, 91 Reactions, 20 Rules, 146 cases, 42 dissociation profiles. Outcomes: 92 inferred covering all 91 canonical equations plus one unstored equation, 41 indeterminate, 12 no_match, one blocked.

Compiler 0.5.0 exports the complete InferenceSession bundle and independent modules: elements 18 roots/6 dependencies, substances 95/59, equations 111/155. See [modules](contracts/DATA_PACKAGES.md), [Python API](contracts/APPLICATION_API.md) and [chem-wiki integration](contracts/CHEM_WIKI_INTEGRATION.md). HTTP adaptation and actual database import remain unimplemented.

## Previous batch validation and preservation

Validation and 18 focused tests pass, including generation of all 92 positive cases after removal of stored Reactions. All 466 tests were executed: 464 passed and two stale relation-list assertions failed; those assertions were then corrected. All 27 tests in the affected M12/M13 files then passed; no runtime or Rule changes followed. Full log: `build/current-final-pytest.txt`; no repeat full run is required.

Compile/audit/bundle/modules are byte-identical across hash seeds 3 and 941; evidence: `build/copper-verification/`. Two M25 replays agree: 21 mapped, 122 unsupported, nine rejected. Historical reports remain unchanged. After committing, regenerate `build/application-bundle` and `build/data-modules` from the final SHA and verify manifest.source_revision.

## Exact resume point

Run `git status --short --branch`, `git diff --stat`, `git rev-parse HEAD` and query actual quota. Preserve any dirty work. Freeze a finite textbook equation inventory; the [coverage matrix](CURRICULUM_COVERAGE.md) is not an exhaustive textbook list. Next prioritize bounded FeO/Fe2O3 acid pathways, then Al and nonmetal gaps. Concentration, excess, catalysts, reversibility and electrodes need explicit semantics before their reactions. Automated case transfer is pending; current Rules infer unstored equations only when supporting knowledge is sufficient.

The previous window reached 93% and its batch was preserved. At 2026-09-27 09:51 Beijing quota recovered to 1%, enabling the iron interconversion batch. Heartbeat `automation` remains ACTIVE every five hours at minute 50, with actual recovery checked on each trigger. Check actual recovery each time, wait quietly if unavailable, and never mark the long-term goal complete. Full-test sessions 14838 and 71460 have ended; neither needs repeating. The heartbeat Chinese encoding was repaired and verified.
