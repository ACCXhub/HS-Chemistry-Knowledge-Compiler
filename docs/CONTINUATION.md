# Continuing curriculum and prediction work

[简体中文](CONTINUATION.zh-CN.md)

The long-term mainland compulsory/selective-compulsory goal remains incomplete. Preserve shared canonical identities across independently published element, substance and equation modules. Predictions must remain separate from curated facts; UNKNOWN is not impossible. Safe main commits/pushes are authorized. No subagents, repeated M0–M25 audit, reset, stash or rebase.

## Current batch: copper oxide and nitrates, 2026-09-27

Based on ferrous commit `0db354e2aae013f0b8ca36e6be0028057b8f01b9`, add CuO, Ca(NO3)2 and Cu(NO3)2, eight Reactions, one CuO/strong-acid Rule and eight positive cases. Seven paths reuse existing Rules. Nitrate spectators do not make nitric acid non-oxidizing. No runtime/schema changes. M12/M13 tests now check their own displacement targets and evidence without freezing every future relation. Bilingual current counts, roadmap and historical audit labels are synchronized.

Current source: 272 records, 113 Entities, 91 Reactions, 20 Rules, 146 cases, 42 dissociation profiles. Outcomes: 92 inferred covering all 91 canonical equations plus one unstored equation, 41 indeterminate, 12 no_match, one blocked.

Compiler 0.5.0 exports the complete InferenceSession bundle and independent modules: elements 18 roots/6 dependencies, substances 95/59, equations 111/155. See [modules](contracts/DATA_PACKAGES.md), [Python API](contracts/APPLICATION_API.md) and [chem-wiki integration](contracts/CHEM_WIKI_INTEGRATION.md). HTTP adaptation and actual database import remain unimplemented.

## Validation and preservation

Validation and 18 focused tests pass, including generation of all 92 positive cases after removal of stored Reactions. All 466 tests were executed: 464 passed and two stale relation-list assertions failed; those assertions were then corrected. All 27 tests in the affected M12/M13 files then passed; no runtime or Rule changes followed. Full log: `build/current-final-pytest.txt`; no repeat full run is required.

Compile/audit/bundle/modules are byte-identical across hash seeds 3 and 941; evidence: `build/copper-verification/`. Two M25 replays agree: 21 mapped, 122 unsupported, nine rejected. Historical reports remain unchanged. After committing, regenerate `build/application-bundle` and `build/data-modules` from the final SHA and verify manifest.source_revision.

## Exact resume point

Run `git status --short --branch`, `git diff --stat`, `git rev-parse HEAD` and query actual quota. Preserve any dirty work. Freeze a finite textbook equation inventory; the [coverage matrix](CURRICULUM_COVERAGE.md) is not an exhaustive textbook list. Prioritize bounded evidence-backed Fe interconversion, Al and nonmetal gaps. Concentration, excess, catalysts, reversibility and electrodes need explicit semantics before their reactions. Automated case transfer is pending; current Rules infer unstored equations only when supporting knowledge is sufficient.

Usage reached 93%; finish closeout only. Reset: 2026-09-27 08:43:54 Beijing. Heartbeat `automation` remains ACTIVE every five hours at minute 50, after this reset. Check actual recovery each time, wait quietly if unavailable, and never mark the long-term goal complete. Full-test session 14838 has ended; do not restart it.
