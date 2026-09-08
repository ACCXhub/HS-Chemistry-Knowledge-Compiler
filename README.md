# HS-Chemistry-Knowledge-Compiler

Canonical architecture for a deterministic, evidence-aware high-school chemistry knowledge compiler.

This repository replaces the legacy `chem-knowledge-data` architecture. Legacy schemas, paths, identifiers, and package boundaries are migration/reference material only and are not compatibility constraints.

## F1 architecture master

F1 converges four architecture workstreams into one source model:

- stable chemical and knowledge identity;
- shallow ontology + faceted classification;
- intrinsic, contextual, derived, unknown, false, and not-applicable semantics;
- typed relations;
- canonical reactions separated from inferred candidates;
- deterministic declarative inference;
- teaching/curriculum views that never own chemistry identity;
- evidence/provenance that survives compilation;
- human-reviewable Git source separated from generated runtime artifacts.

The architecture is language-neutral. Python remains a provisional reference implementation choice; optimization follows profiling.

## Canonical ownership

| Concern | Canonical owner |
| --- | --- |
| Cross-workstream boundaries and decisions | `docs/ARCHITECTURE.md`, `docs/DECISIONS.md` |
| Domain ontology | `docs/domain/**` |
| Pedagogy / teaching views | `docs/pedagogy/**` |
| Source and external artifact contracts | `docs/contracts/**`, future `schemas/**` |
| Inference, rule semantics, compiler internals | `docs/inference/**`, future `knowledge/rules/**`, `compiler/**` |
| Next executable phase | `docs/ROADMAP.md` |

## Canonical semantic shape

```text
editable Git source
  ├─ identity-bearing domain records
  ├─ assertions / relations / reactions
  ├─ teaching views
  ├─ evidence / provenance
  └─ declarative rules
          │
          ▼
canonical contracts + deterministic compiler
  validate → resolve → normalize → infer → balance → validate → compare → trace
          │
          ▼
generated runtime artifacts
```

Generated artifacts are reproducible outputs and never become editable chemistry truth.

## Core identity decisions

- `Element`, `Species`, `Substance`, and `MaterialSystem` are distinct identity kinds.
- `Ion` is a `Species` subtype, not a competing peer entity kind.
- `Solution` and `Mixture` are `MaterialSystem` kinds, not `Substance` subtypes.
- `Structure` is a stable identity-bearing domain record when the structural model needs durable reference.
- a `Bond` is an embedded structure component by default; it receives only a structure-local key unless an independent lifecycle is later demonstrated.
- formulas, names, SMILES, Lewis drawings, images, teaching paths, and runtime dense IDs are representations/locators, not canonical identity.

## Reaction decisions

A canonical `Reaction` owns one chemical transformation. It may expose multiple `ReactionForm` projections such as molecular, complete ionic, net ionic, symbolic, or thermochemical forms when those are representations of the same transformation.

A chemically distinct half-reaction is a separate related `Reaction`, not merely another display form. This is required for electrochemistry.

Generated `ReactionCandidate` values use deterministic content-derived candidate keys. A separately persisted review/curation candidate may receive a durable `rcand_*` ID while retaining its immutable deterministic candidate key.

See [Architecture](docs/ARCHITECTURE.md), [Decisions](docs/DECISIONS.md), and [Roadmap](docs/ROADMAP.md).