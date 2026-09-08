# Knowledge Compiler Architecture

Status: **F1 canonical compiler boundary**

## 1. Responsibility

The compiler turns validated canonical source plus declarative rules into deterministic diagnostics, indexes, candidates, proof traces, teaching projections, and external artifacts.

Generated artifacts are disposable/reproducible and never become editable truth.

## 2. Ordered build passes

```text
A parse + safe normalization
B schema validation
C stable-ID/reference resolution
D cross-record semantic validation
E vocabulary/operator resolution
F rule parse + type checking
G rule lowering to normalized IR
H overlap / precedence / UNKNOWN-policy analysis
I chemistry-plan validation
J runtime-ID/layout planning
K index/cache construction
L canonical reaction signature compilation
M optional deterministic derivation / coverage audit
N artifact emission + manifest
```

Validation precedes derivation.

## 3. Ownership

Data Contracts owns exact external artifact schemas. Compiler owns:

- normalized rule IR / `RulePlan`;
- operator registry implementation contracts;
- runtime dense IDs;
- indexes/caches;
- balancing adapter;
- candidate execution pipeline;
- internal diagnostics/layout.

## 4. Runtime inference pipeline

```text
input normalization
→ context construction
→ hard blockers
→ explicit overrides/resolution gates
→ candidate rule matching
→ product construction
→ canonical entity resolution
→ postmatch predicates
→ resolution graph
→ balancing
→ atom validation
→ charge validation
→ canonical reaction comparison
→ ReactionCandidate + proof trace
```

The exact internal ordering may short-circuit safely, but trace semantics and deterministic outcomes must remain stable.

## 5. Rule conflict analysis

File order and raw integer priority are not semantic resolution mechanisms.

Rules use explicit relationships such as `overrides`, `specializes`, `fallback_for`, `equivalent_to`, and declared mutual exclusion. Potentially overlapping rules with non-equivalent effects and no explicit resolution relationship are compile errors in strict mode.

## 6. UNKNOWN semantics

Predicates use three-valued logic where required. Missing open-world knowledge remains UNKNOWN. The compiler rejects constructs that silently coerce UNKNOWN to false for applicability decisions unless an operator contract explicitly defines a closed-world scope.

## 7. Balancing

Balancing receives fixed canonical reactant/product identities. It does not guess products.

Use exact composition/charge data to solve conservation equations with exact arithmetic. If multiple chemically distinct admissible solutions remain, return an underdetermined diagnostic unless explicit evidence-backed constraints resolve the ambiguity.

## 8. Canonical reaction comparison

Canonical comparison occurs only after candidate construction, entity resolution, balancing, and validation. It cannot serve as an inference oracle.

Reaction signatures normalize participant ordering and coefficient scaling while retaining identity-relevant reaction/form/context boundaries.

## 9. Candidate determinism

Pure compilation derives `candidate_key` from canonical semantic content plus declared inference lineage. Timestamps, local paths, process IDs, nondeterministic traversal order, and time-based UUIDs are excluded from semantic identity/digests.

## 10. Performance policy

Start with bounded typed/faceted indexes and exact deterministic execution. RETE, native acceleration, or alternate languages require profiling evidence. Stable source contracts must not change solely for runtime convenience.
