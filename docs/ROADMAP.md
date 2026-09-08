# Roadmap

## Current state

F1 architecture convergence is complete on `workstream/f1-convergence` once the repository-level verification gates pass.

The next phase is intentionally a **small executable vertical slice**, not corpus population and not runtime optimization.

## F2 — Contract-to-candidate vertical slice

### Outcome

Prove one deterministic end-to-end path:

```text
canonical source
→ schema validation
→ identity / ontology / facet / context resolution
→ 1–2 declarative rules
→ candidate product construction
→ canonical entity resolution
→ exact balancing
→ atom + charge validation
→ canonical reaction comparison
→ proof trace
→ deterministic external artifact
```

### Scope

Use a tiny representative fixture set containing at least:

- one precipitation case such as Ag+ / Cl- or NaCl + AgNO3;
- one acid-base neutralization case such as HCl + NaOH;
- enough entity/structure/context records to prove identity boundaries;
- at least one blocker/UNKNOWN case.

### Required work

1. freeze the minimum source schema for the fixture records;
2. define deterministic serialization/canonicalization used for hashes and candidate keys;
3. implement schema and semantic validation;
4. implement the minimum declarative rule parser/type checker;
5. implement deterministic inference stages and exact balancing;
6. emit candidate + proof trace + manifest;
7. add golden/differential tests for repeatability.

### Non-goals

- large chemistry corpus migration;
- full D01-D11 population;
- RETE or generic graph rule engines;
- database-first persistence;
- Rust/C++ optimization;
- broad UI/Equation Lab integration.

### F2 acceptance

- identical source + compiler revision produces byte-stable semantic artifacts;
- no rule depends on file order or integer priority alone;
- UNKNOWN cannot become false silently;
- generated candidate identity is deterministic;
- balancing does not infer products;
- atom and charge validation are explicit;
- canonical comparison is downstream of candidate construction/validation;
- proof trace identifies rule, inputs, decisions, exceptions/blockers checked, validation, and canonical comparison;
- the source fixture remains human-reviewable and schema-validatable.

Only after this slice passes should migration scale, curriculum population, artifact indexing, or native acceleration expand.
