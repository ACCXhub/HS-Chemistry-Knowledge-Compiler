# Architecture

## 1. Purpose

HS-Chemistry-Knowledge-Compiler is a source-to-artifact knowledge system for high-school chemistry. Its job is to preserve chemically meaningful editable knowledge, validate and normalize it, derive deterministic knowledge where justified, and emit runtime-oriented artifacts without allowing presentation structure or legacy storage formats to become the chemistry model.

The architecture is designed to replace `chem-knowledge-data`. Legacy data can be imported through migration tooling, but legacy package boundaries, identifiers, schemas, and denormalizations do not define this repository.

## 2. System shape

```text
                     editable Git source
                           │
          ┌────────────────┼────────────────┐
          │                │                │
     domain knowledge   teaching views   inference rules
          │                │                │
          └──────────────┬─┴────────────────┘
                         │
                 canonical contracts
                         │
                         ▼
                  knowledge compiler
       validate → resolve → normalize → derive
              → project → index → emit
                         │
                         ▼
              generated runtime artifacts
```

A runtime database may later consume compiled artifacts, but it is not the source of truth for the initial architecture.

## 3. Architectural boundaries

### 3.1 Identity

Identity answers only: **what chemical or knowledge object is this?**

Canonical chemical entities receive stable opaque IDs whose meaning does not depend on names, formulas, classifications, curriculum chapters, or file locations. Human-readable labels and semantic descriptors may change without changing identity.

Identity must be reusable by facts, relations, reactions, teaching views, evidence links, and compiler indexes. Identity resolution may use semantic keys as lookup aids, but lookup keys do not become the canonical identity authority.

Identity does not own taxonomy, teaching placement, or reaction behavior.

### 3.2 Domain ontology

The domain ontology defines the chemistry-level kinds and semantic categories that are necessary to state high-school chemistry knowledge correctly.

It answers questions such as whether a record represents a chemical entity, a reaction-like concept, a property concept, or another domain-level concept. It should remain shallow and compositional. It must not encode every curriculum classification as a subtype hierarchy.

Detailed ontology choices belong to **Domain Ontology & Pedagogy**.

### 3.3 Facets / classifications

Classifications are independent schemes attached to canonical subjects.

Examples of distinct classification dimensions might include composition-based grouping, behavior under a specified curriculum convention, material class, laboratory role, or curriculum categorization. An entity can carry multiple memberships in the same or different schemes when chemically and pedagogically valid.

This avoids structures such as:

```text
Entity
  └─ Inorganic
      └─ Oxide
          └─ AcidicOxide
              └─ ...
```

becoming the sole representation of knowledge. Classification membership is data, not identity and not inheritance.

A classification scheme may have semantic keys and hierarchical display relationships inside the scheme, but those paths do not define entity identity.

### 3.4 Facts and context

Facts are explicit claims about canonical subjects. The architecture distinguishes three categories:

- **Intrinsic facts**: claims intended to hold for the entity independent of a teaching or experimental context within the modeled domain.
- **Contextual facts**: claims valid only under declared conditions, scope, convention, phase, environment, measurement basis, curriculum framing, or other relevant context.
- **Derived facts**: deterministic outputs computed from canonical source knowledge and rules; they retain derivation traceability and are not silently rewritten as authored facts.

Context is part of the claim semantics. A context-dependent statement must not be flattened into an unconditional attribute merely because doing so is convenient for a UI.

The field-level representation of claims and context belongs to **Canonical Data Contracts**; deciding which chemistry claims require which contexts belongs to **Domain Ontology & Pedagogy**.

### 3.5 Relations

Relations are typed semantic assertions connecting canonical subjects.

They represent meaning such as structural, compositional, conceptual, transformational, evidential, or pedagogical associations when those meanings are best expressed as edges rather than attributes or taxonomy membership.

Relations must have declared semantics. A relation is not a generic catch-all graph edge, and a teaching link is not automatically promoted into a chemical relation.

Relations that are independently cited, curated, or provenance-bearing may require stable assertion IDs. Purely structural or compiler-generated index edges may instead use deterministic semantic keys, subject to the contracts workstream.

### 3.6 Reactions

Canonical reactions are curated chemistry knowledge objects with stable identity. They describe accepted reaction knowledge in a canonical form suitable for reference, evidence attachment, teaching projection, and compiler processing.

A canonical reaction is distinct from:

- a rule that can infer reactions;
- a candidate produced by a rule;
- a UI rendering of an equation;
- a curriculum grouping of reactions.

Canonical reactions may reference canonical chemical identities and reaction-level context. Exact participant and condition contracts are delegated to the relevant workstreams.

### 3.7 Inference rules

Inference rules express deterministic, declarative transformations from known canonical knowledge to derived claims or **inferred candidates**.

Rules must be inspectable and attributable. Given the same validated source revision and compiler version, they must produce the same semantic output.

An inferred reaction candidate is not canonical merely because a rule produced it. Promotion into canonical reaction knowledge requires the canonical data workflow and, where appropriate, evidence or review.

Rules should have stable rule identity when they appear in diagnostics, provenance, derived outputs, or compatibility/versioning decisions.

Detailed rule semantics belong to **Inference & Compiler Semantics**.

### 3.8 Teaching / curriculum views

Teaching views are curated projections over canonical chemistry knowledge. They may group, order, annotate, simplify, sequence, or cross-link entities, reactions, facts, and relations for a curriculum or learning task.

The user's 11 high-school chemistry framework diagrams are modeled here as teaching/knowledge views. They may become multiple linked projections rather than one ontology tree.

Teaching views may use readable paths or view-local keys for navigation, but those paths must resolve to canonical identities and must not become the identity of the chemistry objects they display.

Additional teaching classifications should be added only when supported by chemistry semantics or curriculum evidence.

### 3.9 Evidence / provenance

Evidence and provenance answer: **where did this authored or derived knowledge come from, and how was it produced?**

Evidence can support entities, facts, classifications, relations, canonical reactions, teaching assertions, or inference rules where appropriate. Provenance also records derivation lineage for compiler-produced knowledge.

Compiled artifacts must preserve enough trace information to connect runtime records back to canonical source identities and, when relevant, source evidence and inference rules.

Evidence is not itself a substitute for semantic modeling: a citation does not decide what a fact means.

### 3.10 Compiler

The compiler is the boundary between editable knowledge and generated runtime data. Conceptually it performs ordered passes such as:

1. parse source files;
2. validate against canonical contracts;
3. resolve stable identities and references;
4. validate cross-record chemistry and semantic invariants;
5. normalize canonical representations;
6. execute deterministic derivations/inference;
7. compile teaching projections;
8. build indexes and lookup structures;
9. emit runtime artifacts and diagnostics.

The exact pass implementation may evolve, but source validation must precede derivation, and generated data must remain reproducible.

Python is the default implementation language. Native acceleration may be introduced behind measured hot paths without changing source semantics or canonical contracts.

### 3.11 Generated / runtime artifacts

Generated artifacts are compiler outputs optimized for consumers. They may denormalize, index, precompute, or reshape canonical knowledge for fast lookup, graph traversal, teaching applications, or runtime services.

Generated artifacts are **not editable truth**. Consumers must not require authors to patch generated files in order to change canonical chemistry knowledge.

Artifact formats and compatibility/versioning policies belong to **Canonical Data Contracts**. Compiler emission and deterministic build behavior belong to **Inference & Compiler Semantics**.

## 4. Identity policy

### Stable opaque IDs are required for

- canonical chemical entities;
- canonical reactions;
- inference rules when referenced by outputs, diagnostics, provenance, or versioned behavior;
- independently curated/provenance-bearing assertions when their lifecycle requires identity;
- evidence/source records when they are referenced from multiple claims or need durable citation identity.

Opaque IDs should remain stable across file moves, renames, label changes, taxonomy changes, and teaching-view reorganizations.

### Semantic keys are appropriate for

- property/type vocabularies;
- relation-type vocabularies;
- facet scheme keys and facet value keys;
- context-dimension vocabularies;
- compiler pass names, artifact names, and other controlled technical namespaces;
- deterministic lookup aliases that are not canonical identity.

Semantic keys should be stable within their vocabulary but may carry readable meaning.

### Teaching paths are locators, not identity

A teaching path such as a chapter/section/view node may be readable and hierarchical. It is allowed to change as curriculum presentation evolves. It must point to canonical identities rather than replace them.

## 5. Source-of-truth and generated-data boundary

### Editable source of truth

Canonical authored knowledge lives in Git-managed source files, expected under ownership-separated areas such as:

```text
knowledge/domain/**
knowledge/teaching/**
knowledge/rules/**
schemas/**
```

These directories are conceptual ownership boundaries. They should be created by their owning workstreams only when concrete files are needed.

### Generated outputs

Compiler outputs are produced into a generated area chosen by the contracts/compiler workstreams. They may be committed for releases or published separately, but their authority is always the source revision plus compiler implementation.

Every artifact build should eventually be identifiable by at least:

- source revision;
- compiler version/revision;
- contract/artifact version;
- deterministic build diagnostics or manifest.

The exact manifest schema is not fixed by this architecture document.

## 6. Interaction rules between layers

1. **Identity precedes reference.** Facts, relations, reactions, and teaching views reference canonical identities rather than duplicating entities.
2. **Ontology defines meaning; facets classify.** A facet membership must not create a new chemical identity.
3. **Context qualifies claims.** Context-dependent chemistry is represented on the claim/reaction semantics, not hidden in labels or teaching paths.
4. **Relations assert; rules derive.** A semantic relation is curated knowledge unless explicitly generated; an inference rule is executable semantics.
5. **Canonical reactions are reviewed knowledge; candidates are derived output.** Candidate generation never silently mutates canonical reaction source.
6. **Teaching views project chemistry knowledge.** Teaching structure can organize and annotate canonical objects without owning their chemical identity.
7. **Evidence supports source knowledge; provenance traces derivation.** Both remain accessible after compilation.
8. **Compiler output may denormalize but may not redefine truth.** Runtime convenience cannot leak back into the canonical model as an architectural requirement.

## 7. Canonical owner map

| Concern | Primary owner | Architecture Lead responsibility |
| --- | --- | --- |
| Chemical concept boundaries and ontology semantics | Domain Ontology & Pedagogy | Maintain cross-layer boundary only |
| Facet/classification meaning | Domain Ontology & Pedagogy | Ensure classification remains separate from identity |
| 11 framework diagrams and teaching projections | Domain Ontology & Pedagogy | Ensure they remain views, not ontology roots |
| Field-by-field source schemas | Canonical Data Contracts | Define only cross-workstream contract boundary |
| ID/reference serialization and validation format | Canonical Data Contracts | Maintain identity policy |
| Artifact schemas/versioning | Canonical Data Contracts | Maintain generated-vs-source boundary |
| Reaction rule semantics | Inference & Compiler Semantics | Maintain canonical-vs-inferred distinction |
| Compiler passes and deterministic execution | Inference & Compiler Semantics | Maintain compiler role and reproducibility boundary |
| Architecture, roadmap, cross-stream decisions | Architecture Lead | Canonical owner |

## 8. Expected repository ownership

To minimize merge overlap:

```text
README.md                              Architecture Lead
docs/ARCHITECTURE.md                   Architecture Lead
docs/ROADMAP.md                        Architecture Lead
docs/DECISIONS.md                      Architecture Lead

knowledge/domain/**                    Domain Ontology & Pedagogy
knowledge/teaching/**                  Domain Ontology & Pedagogy
docs/domain/**                         Domain Ontology & Pedagogy
docs/pedagogy/**                       Domain Ontology & Pedagogy

schemas/**                             Canonical Data Contracts
docs/contracts/**                      Canonical Data Contracts

knowledge/rules/**                     Inference & Compiler Semantics
compiler/**                            Inference & Compiler Semantics
docs/inference/**                      Inference & Compiler Semantics
tests/inference/**                     Inference & Compiler Semantics
```

Shared examples or fixtures should have one declared owner rather than parallel copies. A workstream that needs a change in another owner's canonical file should coordinate that change instead of creating a competing definition.

## 9. Legacy migration boundary

`chem-knowledge-data` may provide:

- candidate records for import;
- terminology or coverage comparisons;
- evidence/source references worth preserving;
- regression cases showing what knowledge must remain expressible.

Migration should flow through explicit adapters or one-time transforms into the new canonical contracts. Legacy structure must not be preserved solely to make migration easy. No new architecture decision should cite legacy compatibility as sufficient justification.

## 10. Non-goals of the foundation phase

This phase does not:

- freeze the detailed chemistry ontology;
- freeze field-by-field schemas;
- define all reaction rule semantics;
- implement the complete compiler;
- introduce a runtime database;
- optimize native code paths;
- reproduce every legacy package or field.

Those decisions should be made by the owning workstreams with evidence and then reconciled through the architecture boundaries above.
