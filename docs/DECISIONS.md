# Architecture Decision Log

Status: **F2 executable architecture decisions**

## ADR-F1-001 — Entity-kind alignment

**Decision:** canonical `entity_kind` is `element | species | substance | material_system`. `Ion` is `species_kind: ion`. `Solution` and `Mixture` are `material_system_kind` values.

**Why:** this keeps microscopic species, pure macroscopic material, and composed experimental systems distinct without competing identity systems.

## ADR-F1-002 — Structure ownership

**Decision:** `Structure` is a stable identity-bearing domain record when durable structural reference is required. Representations are subordinate values. `Bond` is embedded with a structure-local key by default.

**Why:** a stable structure must not collapse into SMILES/Lewis/image strings, while top-level bond UUIDs are unnecessary without an independent lifecycle.

## ADR-F1-003 — Source normalization

**Decision:** the following are embedded value objects in F1 source: `Composition`, `Context`, `ReactionParticipant`, `Condition`, `TeachingViewPath`, and default `Bond`.

`FacetAssertion` is durable only for authored/evidenced claims that need independent provenance/revision identity; generated memberships are compiler output.

**Why:** canonical source should be practical to author and audit, not a UUID-heavy normalized graph.

## ADR-F1-004 — ReactionCandidate lifecycle

**Decision:** pure compilation emits a deterministic content-derived `candidate_key` and mints no UUID. A persistent human-review candidate may additionally receive a durable `rcand_*` ID while retaining that candidate key.

**Why:** deterministic builds and persistent review objects have different lifecycles.

## ADR-F1-005 — Rule identity owner

**Decision:** the declarative `Rule` definition is the sole canonical owner of `rule_*` identity, semantic version, resolution edges, evidence, and provenance. `RuleReference` is not a separate source-record type.

## ADR-F1-006 — Reaction identity vs representation

**Decision:** use `Reaction + ReactionForm`.

Molecular, complete ionic, net ionic, symbolic, and thermochemical forms may belong to one reaction when they are projections/representations of the same transformation. A chemically distinct transformation remains a separate related reaction.

Half-reactions are separate `Reaction` records and may compose an overall electrochemical reaction.

## ADR-F1-007 — Macro/micro reaction referents

**Decision:** participants may target `Species`, `Substance`, or `MaterialSystem`. Alternate molecular/ionic forms must state projection/speciation assumptions when they change referent level.

**Consequence:** NaCl crystal never requires a fictional NaCl molecule.

## ADR-F1-008 — Canonical specialist locations

**Decision:** specialist canonical documents live only under:

- `docs/domain/**`;
- `docs/pedagogy/**`;
- `docs/contracts/**`;
- `docs/inference/**`.

No duplicate root-level specialist copies are canonical.

## ADR-F1-009 — Compiler-contract ownership

**Decision:** Data Contracts owns exact external generated artifact schemas and compatibility contracts. Compiler owns internal plans, indexes, caches, operator lowering, and runtime layout.

## ADR-F1-010 — Identity remains independent from presentation

Names, aliases, formulas, classification paths, teaching paths, file paths, YAML order, and runtime dense IDs do not define permanent identity.

## ADR-F1-011 — Open-world fact semantics

Absence, explicit `unknown`, `not_applicable`, and known false remain distinct. Missing knowledge cannot be silently used as false by rules.

## ADR-F1-012 — Canonical Reaction != ReactionCandidate

A candidate remains generated even if canonical comparison finds an exact/equivalent reaction. Canonical promotion is a separate evidence-backed curation action.

## ADR-F1-013 — Language and optimization

The architecture and source DSL remain language-neutral. Python-first is provisional. Performance changes require profiling and must stay behind stable semantic boundaries.

## ADR-F2-001 — Deterministic canonical JSON

**Decision:** F2 semantic hashing and deterministic artifact payloads use an owned canonical JSON encoding:

- UTF-8;
- Unicode strings and mapping keys normalized to NFC;
- mapping keys sorted lexicographically after normalization;
- no insignificant whitespace;
- semantic numbers in the F2 hash domain are integers only; floating-point values are rejected;
- lists preserve declared semantic order;
- top-level source records are sorted by `(record_type, id)` before source hashing;
- timestamps, local paths, process IDs, filesystem traversal order, and worker ordering are excluded from semantic payloads.

`candidate_key` is `cand_sha256_` plus SHA-256 of the canonicalized semantic candidate payload. External JSON artifact files append one LF byte; artifact hashes cover the exact emitted bytes.

**Why:** this gives a narrow byte-stable contract without inventing a binary format or inheriting implementation-specific JSON behavior.

## ADR-F2-002 — Minimal executable source/schema boundary

**Decision:** F2 authored chemistry/rule source remains YAML and is validated by the minimal executable schemas under `schemas/`.

- `schemas/f2-record.schema.json` validates the identity-bearing record shapes used by the slice;
- `schemas/f2-case.schema.json` validates audit/example requests;
- `Composition` remains embedded;
- reaction/request participants carry phase explicitly;
- rule product templates carry product phase explicitly;
- phase is not promoted into Entity identity or a timeless default identity fact.

Source files may be split or renamed without changing identity or semantic output.

## ADR-F2-003 — F2 source Rule vs internal RulePlan

**Decision:** authored `Rule` YAML is compiled into an internal typed Python `RulePlan`. `RulePlan` is compiler-owned runtime structure and is not a source contract.

F2 implements only the operators needed by the two executable families: exact participant binding, required facet checks, context equality predicates, declared context blockers, canonical product templates, and atom/charge validators. Rule selection does not use file order or integer priority.

Balancing receives fixed canonical reactants/products and exact composition/charge data. Canonical reaction comparison runs only after product resolution, balancing, and conservation validation.

## F2 remaining non-blocking decisions

The following do not block F2 and are candidates for F3:

1. broaden source Rule patterns from the deliberately exact F2 fixture bindings to reusable typed/facet/relation patterns while retaining compile-time overlap analysis;
2. generalize `ReactionForm` projection/speciation beyond the two curated aqueous examples;
3. extend external artifact compatibility/versioning beyond the F2 `f2.0` slice contract;
4. decide whether any concrete bond-local lifecycle justifies top-level bond identity;
5. migrate a small evidence-backed real corpus sample only after the executable contracts remain stable.
