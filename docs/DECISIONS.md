# Architecture Decision Log

This file records durable cross-workstream decisions owned by the Architecture Lead. Detailed chemistry ontology choices, schema field definitions, and reaction-rule semantics belong in their specialist canonical areas and should be referenced here only when they alter an architecture boundary.

Decision states:

- **Accepted** — current canonical direction.
- **Provisional** — working direction allowed for implementation, subject to evidence-driven revision.
- **Open** — explicitly unresolved; owned by the named workstream.
- **Superseded** — retained for history after a later decision replaces it.

## D-001 — This repository replaces, rather than wraps, `chem-knowledge-data`

**Status:** Accepted

`chem-knowledge-data` is legacy reference, migration input, and comparison material only. Its architecture, package boundaries, identifiers, schemas, and denormalized outputs do not constrain the new canonical model.

Migration must adapt legacy data into this repository's contracts rather than preserve legacy structure for compatibility.

## D-002 — Git-versioned authored knowledge is the initial source of truth

**Status:** Accepted

Canonical authored chemistry knowledge, teaching views, rules, and contracts are maintained as reviewable Git-versioned source data. A runtime database is not introduced as the authority during the foundation phase.

Generated/runtime stores may later consume compiled artifacts, but they remain downstream of canonical source.

## D-003 — Chemical identity uses stable opaque IDs

**Status:** Accepted

Canonical chemical entities and canonical reactions require stable opaque identity independent of names, formulas, file paths, facet memberships, and teaching paths.

Inference rules also require stable identity when referenced by outputs, diagnostics, provenance, or versioned behavior. Independently curated/provenance-bearing assertions and evidence records require durable IDs when their lifecycle needs independent reference.

Readable semantic keys remain appropriate for controlled vocabularies and lookup namespaces, but do not replace canonical object identity.

## D-004 — Classification is faceted, not inheritance-driven

**Status:** Accepted

Classification memberships are modeled as data in independent schemes. They do not create chemical identity and do not require a deep subtype tree for every curriculum or chemistry classification.

Scheme-local hierarchy may exist for navigation or semantics, but it remains a classification structure rather than the root entity ontology.

## D-005 — Facts distinguish intrinsic, contextual, and derived claims

**Status:** Accepted

A context-dependent chemistry statement must explicitly retain its context semantics instead of being flattened into an unconditional field, subtype name, or teaching label.

Derived facts are compiler-produced knowledge with derivation traceability and remain distinguishable from authored claims.

The exact source schema is owned by Canonical Data Contracts; determining which chemistry claims require context is owned by Domain Ontology & Pedagogy.

## D-006 — Semantic relations are explicit and typed

**Status:** Accepted

Cross-entity semantic meaning that is not identity, facet membership, fact value, reaction structure, or teaching navigation is represented as explicit typed relations.

A generic graph edge with undefined semantics is insufficient as canonical knowledge.

## D-007 — Canonical reactions and inferred reaction candidates are different lifecycle objects

**Status:** Accepted

Canonical reactions are curated chemistry knowledge with stable identity. Inference rules may deterministically produce reaction candidates or derived reaction knowledge, but those outputs are not silently promoted into canonical reaction source data.

Promotion, when justified, occurs through the canonical data workflow and may require evidence/review.

## D-008 — Inference rules are declarative, deterministic, and traceable

**Status:** Accepted

Given the same validated source revision and compiler revision, inference must produce the same semantic result. Rules must be inspectable and attributable so derived outputs can reference the responsible rule and source knowledge.

Detailed reaction-rule semantics remain owned by Inference & Compiler Semantics.

## D-009 — Teaching/curriculum structures are views over canonical chemistry knowledge

**Status:** Accepted

The user's 11 high-school chemistry framework diagrams are pedagogical/knowledge views, not assumed ontology roots. They may group, sequence, annotate, simplify, or cross-link canonical entities, facts, relations, and reactions.

Teaching paths are allowed as readable view-local locators, but they are not chemical identity.

Additional curriculum classifications should be introduced only when supported by chemistry semantics or curriculum evidence.

## D-010 — Evidence and derivation provenance survive compilation

**Status:** Accepted

Compiled runtime artifacts must preserve sufficient traceability to connect runtime records back to canonical source identities and, where relevant, evidence records and inference rules.

The exact provenance schema is delegated to Canonical Data Contracts, with derivation behavior owned by Inference & Compiler Semantics.

## D-011 — The repository is knowledge-compiler-first

**Status:** Accepted

The compiler is the boundary between editable canonical source and machine-consumable runtime artifacts. Conceptual compilation stages are:

```text
parse
→ contract validation
→ identity/reference resolution
→ semantic validation
→ normalization
→ deterministic derivation/inference
→ teaching-view projection
→ indexing
→ artifact emission + diagnostics
```

The precise implementation may evolve, but validation precedes derivation and generated outputs never become the editable authority.

## D-012 — Python is the default implementation language; optimization follows profiling

**Status:** Provisional

Compiler/runtime implementation begins Python-first because the domain is data/validation/compiler heavy and rapid semantic iteration is more important than premature low-level optimization.

Native acceleration remains an allowed later optimization behind stable boundaries if profiling identifies a justified hot path.

This decision may be revised if concrete ecosystem, tooling, interoperability, or performance evidence favors another language.

## D-013 — Parallel workstreams have non-overlapping canonical ownership

**Status:** Accepted

### Architecture Lead

Owns:

```text
README.md
docs/ARCHITECTURE.md
docs/ROADMAP.md
docs/DECISIONS.md
```

### Domain Ontology & Pedagogy

Owns:

```text
knowledge/domain/**
knowledge/teaching/**
docs/domain/**
docs/pedagogy/**
```

### Canonical Data Contracts

Owns:

```text
schemas/**
docs/contracts/**
```

### Inference & Compiler Semantics

Owns:

```text
knowledge/rules/**
compiler/**
docs/inference/**
tests/inference/**
```

Paths are ownership boundaries and should be created only when needed. Cross-workstream concepts have one canonical owner; consumers reference them rather than create parallel definitions.

## D-014 — Generated artifacts may be denormalized but cannot redefine source semantics

**Status:** Accepted

Runtime artifacts may optimize lookup, traversal, search, rendering, or runtime service needs through denormalization and indexing. Those optimizations are downstream compilation concerns.

No runtime convenience should require changing chemical identity, flattening contextual facts, merging canonical and inferred reactions, or making generated files hand-edited source truth.

## D-015 — Detailed ontology, schema, and inference designs remain intentionally unresolved in the foundation

**Status:** Accepted

The foundation establishes boundaries rather than prematurely freezing specialist designs.

### Open: detailed chemistry ontology

**Owner:** Domain Ontology & Pedagogy

Resolve the minimum entity/concept vocabulary, valid facet schemes, context semantics, and teaching-view mappings needed for high-school chemistry.

### Open: field-by-field source and artifact contracts

**Owner:** Canonical Data Contracts

Resolve concrete serialization, validation, reference, versioning, and artifact schemas while preserving the identity/source/generated boundaries in `docs/ARCHITECTURE.md`.

### Open: reaction-rule and compiler execution semantics

**Owner:** Inference & Compiler Semantics

Resolve rule language/representation, matching and derivation semantics, diagnostics, pass implementation, and deterministic candidate production without collapsing inferred candidates into canonical reaction source.

These open decisions should converge through the representative vertical slice in `docs/ROADMAP.md` rather than through speculative architecture expansion.
