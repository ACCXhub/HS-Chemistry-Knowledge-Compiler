# HS-Chemistry-Knowledge-Compiler

Canonical foundation for a high-school chemistry knowledge compiler.

This repository is intended to replace the architecture of `chem-knowledge-data`, not wrap it. The older repository may be consulted as legacy reference, migration input, or comparison material, but its package structure, identifiers, schemas, and runtime assumptions are not compatibility constraints here.

## Outcome

Build an editable, evidence-aware chemistry knowledge source that can be compiled into deterministic machine-consumable runtime artifacts:

```text
chemical entities
+ faceted classification
+ contextual facts
+ semantic relations
+ canonical reactions
+ deterministic reaction inference
+ teaching/curriculum views
+ provenance/evidence
        ↓
knowledge compiler
        ↓
validated runtime artifacts
```

The project is compiler-first rather than database-first. Human-editable source data and contracts remain canonical in Git; generated artifacts are reproducible outputs and are never hand-edited.

## Architecture principles

- Chemical identity is stable and independent from labels, classifications, teaching chapters, and file paths.
- Classification is faceted: one entity may participate in many orthogonal schemes without inheritance-tree explosion.
- Facts distinguish intrinsic claims, context-dependent claims, and derived claims.
- Semantic relations are explicit assertions between canonical subjects; they are not hidden inside taxonomy or presentation structure.
- Canonical reactions are curated chemical knowledge. Inferred reaction candidates are compiler outputs until separately promoted through the canonical data workflow.
- Inference rules are declarative, deterministic, inspectable, and traceable to rule/evidence provenance.
- Teaching/curriculum structures are views over chemistry knowledge, not the root chemical ontology. The user's 11 framework diagrams belong here.
- Evidence/provenance remains traceable through compilation.
- Python is the default compiler/runtime language until profiling or ecosystem evidence justifies another implementation.
- Native acceleration remains possible behind stable compiler boundaries; performance work follows profiling.

## Canonical architecture layers

The repository separates eleven concerns:

1. Identity
2. Domain ontology
3. Facets / classifications
4. Facts and context
5. Relations
6. Reactions
7. Inference rules
8. Teaching / curriculum views
9. Evidence / provenance
10. Compiler
11. Generated / runtime artifacts

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the boundaries and data flow.

## Canonical ownership

This branch establishes ownership before parallel implementation begins.

| Owner | Canonical scope | Expected path ownership |
| --- | --- | --- |
| Architecture Lead | Cross-workstream architecture, roadmap, decision log, repository-level coordination | `README.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, `docs/DECISIONS.md` |
| Domain Ontology & Pedagogy | Chemistry concepts, valid classification schemes, teaching structures and curriculum semantics | `knowledge/domain/**`, `knowledge/teaching/**`, `docs/domain/**`, `docs/pedagogy/**` |
| Canonical Data Contracts | Source-data contracts, validation boundaries, identifier/reference representation, artifact contract definitions | `schemas/**`, `docs/contracts/**` |
| Inference & Compiler Semantics | Rule semantics, deterministic inference behavior, compilation passes, diagnostics and inference-focused tests | `knowledge/rules/**`, `compiler/**`, `docs/inference/**`, `tests/inference/**` |

The listed paths are ownership boundaries, not a requirement to create empty scaffolding. Each workstream should create only the files it needs. Cross-boundary changes should be coordinated rather than duplicated.

## Source of truth

Editable canonical inputs are expected to live in Git-owned source areas such as `knowledge/**` plus their contracts under `schemas/**`. Compiler code interprets those inputs and emits generated artifacts.

Generated outputs must satisfy three rules:

1. reproducible from a declared source revision and compiler version;
2. never edited as the authority for chemistry knowledge;
3. carry enough trace metadata to map runtime data back to source identities, rules, and evidence.

The exact artifact packaging format is owned by the Canonical Data Contracts workstream; compilation behavior is owned by the Inference & Compiler Semantics workstream.

## Current phase

This repository currently contains only the architecture foundation. It deliberately does **not** implement the full compiler or freeze field-by-field chemistry schemas.

Next work proceeds through the three parallel workstreams, converging through the architecture boundaries in this repository. See [docs/ROADMAP.md](docs/ROADMAP.md).
