# Roadmap

## Purpose

This roadmap sequences the replacement architecture without prematurely coupling the three specialist workstreams. Each stage should end with a small canonical handoff that can be consumed by the next stage.

The Architecture Lead owns only the cross-workstream roadmap, architecture, and decision log. Specialist workstreams own their detailed designs and implementations.

## Phase F0 — Foundation architecture

**Owner:** Architecture Lead

**Status:** current

Deliver:

- repository purpose and replacement boundary;
- eleven architectural layers and their interaction rules;
- source-of-truth versus generated artifact boundary;
- identity policy;
- canonical owner map;
- workstream merge boundaries;
- initial decision log.

Exit when another engineer can identify the correct owner and boundary for every unresolved design question without relying on `chem-knowledge-data` architecture.

## Phase F1 — Parallel semantic foundations

Three workstreams proceed in parallel from the F0 boundaries.

### F1-A — Domain Ontology & Pedagogy

**Primary paths:**

```text
knowledge/domain/**
knowledge/teaching/**
docs/domain/**
docs/pedagogy/**
```

Goals:

- define the minimum chemistry concepts required by the target high-school scope;
- identify valid facet/classification schemes without turning them into inheritance roots;
- model the user's 11 framework diagrams as teaching/knowledge views;
- distinguish chemical semantics from curriculum-specific organization;
- document contextual chemistry requirements that schemas must be able to express.

Deliverable to other streams: a semantic vocabulary and representative examples sufficient to validate contracts, without prescribing field-by-field storage design.

### F1-B — Canonical Data Contracts

**Primary paths:**

```text
schemas/**
docs/contracts/**
```

Goals:

- define source contracts for canonical identities, references, authored assertions, and artifact boundaries;
- define how intrinsic/contextual/derived claims are represented structurally;
- define stable ID/reference serialization and validation rules;
- define contract versioning and generated artifact compatibility expectations;
- preserve provenance hooks without embedding curriculum presentation into chemical identity.

Deliverable to other streams: minimal versioned contracts plus representative valid/invalid fixtures.

### F1-C — Inference & Compiler Semantics

**Primary paths:**

```text
knowledge/rules/**
compiler/**
docs/inference/**
tests/inference/**
```

Goals:

- define deterministic rule semantics and candidate-generation boundaries;
- define compiler pass ordering and diagnostics;
- prove canonical-reaction versus inferred-candidate separation;
- establish reproducible compilation behavior;
- define how derivation provenance references source identities, rules, and evidence.

Deliverable to other streams: a minimal executable/compiler semantic slice operating on representative contracts, not a full chemistry corpus.

## F1 convergence gate

Architecture integration should occur only after all three workstreams can demonstrate compatibility on a deliberately small representative slice.

The convergence gate must answer:

1. Can one stable chemical entity be classified in multiple independent schemes without changing identity?
2. Can one contextual fact express a condition-dependent chemistry claim without encoding the condition in a label or subtype?
3. Can one canonical reaction be referenced by a teaching view and by evidence without duplication?
4. Can one declarative rule produce an inferred reaction candidate that remains distinct from canonical reaction source data?
5. Can the compiler emit a deterministic artifact with traceability back to the source entity/reaction/rule/evidence?
6. Can at least one of the 11 teaching diagrams compile as a view without becoming an ontology root?

If any answer is no, fix the owning boundary before expanding data volume.

## Phase F2 — Representative vertical slice

**Owners:** all three workstreams, integrated through Architecture Lead boundaries

Build a deliberately small end-to-end corpus covering:

- several entity kinds;
- multiple facet memberships;
- at least one intrinsic fact;
- at least one contextual fact;
- at least one explicit relation;
- at least one canonical reaction;
- at least one deterministic inference rule;
- at least one inferred candidate;
- at least one teaching view derived from the framework diagrams;
- evidence/provenance sufficient to trace authored and derived data;
- one generated runtime artifact family.

This phase validates architecture, not coverage.

Acceptance focuses on determinism, semantic separation, traceability, and editability of source data.

## Phase F3 — Migration and coverage planning

Only after the vertical slice is sound, inventory `chem-knowledge-data` as migration input.

Classify legacy material into:

- directly migratable knowledge;
- semantically useful but requiring transformation;
- duplicated/denormalized generated data;
- structurally incompatible legacy concepts;
- unsupported or questionable knowledge requiring review;
- evidence references worth preserving.

Migration tooling must target the new contracts. The new contracts must not be reshaped solely to reproduce legacy layout.

Deliver:

- migration matrix;
- coverage baseline;
- rejected/deferred legacy structures with reasons;
- deterministic import/check tooling where useful.

## Phase F4 — High-school knowledge expansion

Expand canonical authored knowledge by curriculum priority rather than taxonomy completeness.

Recommended order should be derived by the Domain Ontology & Pedagogy workstream, using curriculum evidence and learning value. Expansion should keep source records reviewable and compiler diagnostics bounded.

Architecture acceptance during expansion:

- no new identity tied to teaching paths;
- no new inheritance tree added merely to model classifications;
- no inferred candidate silently promoted to canonical reaction;
- no generated artifact edited as source truth;
- no context-dependent claim flattened into an unconditional fact for convenience.

## Phase F5 — Runtime artifact stabilization

Once source semantics are stable enough, stabilize runtime artifact families for downstream consumers such as interactive knowledge graphs, search, reaction exploration, teaching views, or APIs.

The contracts workstream owns artifact schemas and compatibility policy. The compiler workstream owns reproducible emission and performance behavior.

A runtime database may be introduced here only if consumer evidence justifies it. It remains downstream of compiled canonical knowledge.

## Phase F6 — Profiling and performance

Profile real compiler and consumer workloads before optimization.

Possible responses, in order:

1. improve algorithms/data layout in Python;
2. improve caching/index generation while preserving determinism;
3. parallelize safe compilation stages;
4. introduce native acceleration only for measured hot paths behind stable boundaries.

Performance work must not change chemistry semantics or canonical identities.

## Cross-workstream ownership matrix

| Unresolved problem | Primary owner | Consultation / integration |
| --- | --- | --- |
| What chemical concepts exist in the modeled domain? | Domain Ontology & Pedagogy | Architecture for boundary consistency |
| Which classifications are chemically/curricularly justified? | Domain Ontology & Pedagogy | Contracts for representation feasibility |
| How do the 11 framework diagrams map to views? | Domain Ontology & Pedagogy | Compiler for projection needs |
| What exact source fields and validation rules exist? | Canonical Data Contracts | Domain + compiler provide requirements |
| How are IDs/references serialized? | Canonical Data Contracts | Architecture preserves identity policy |
| What artifact formats/versions are emitted? | Canonical Data Contracts | Compiler implements emission |
| What makes a rule valid and deterministic? | Inference & Compiler Semantics | Domain validates chemistry meaning |
| How are inferred candidates represented and traced? | Inference & Compiler Semantics | Contracts define compatible representation |
| How are compiler passes ordered and diagnosed? | Inference & Compiler Semantics | Architecture protects source/generated boundary |
| When is a cross-layer architecture decision required? | Architecture Lead | Owning streams supply evidence |

## Merge discipline

Parallel branches should minimize overlap by respecting path ownership. Architecture files should change only for durable cross-workstream decisions, not as a scratchpad for specialist design.

When a specialist decision changes an architecture boundary:

1. the owning workstream documents the concrete evidence/design in its canonical area;
2. Architecture Lead records only the resulting cross-workstream decision in `docs/DECISIONS.md` and, if necessary, adjusts `docs/ARCHITECTURE.md`;
3. other workstreams consume the boundary rather than copying the detailed specialist design.

This keeps one canonical owner per concept while allowing the repository to converge incrementally.
