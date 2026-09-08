# Architecture Decision Log

Status: **F1 convergence accepted decisions**

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

## F1 open decisions

No blocking architecture contradiction remains for F1.

The following are intentionally deferred and **do not block F1**:

1. exact YAML/JSON Schema field syntax and file sharding strategy — owner: Data Contracts; needed for the next vertical slice;
2. exact deterministic hash canonicalization encoding for `candidate_key` and artifact digests — joint Data Contracts + Compiler; needed before implementation emits persistent fixtures;
3. whether any future bond use case justifies top-level durable bond identity — owner: Domain Ontology; deferred until a concrete bond-local lifecycle exists.
