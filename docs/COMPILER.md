# Knowledge Compiler Architecture

## 1. Purpose

This document defines the compiler architecture that turns validated canonical chemistry source plus declarative inference rules into deterministic machine-consumable plans, diagnostics, indexes, and generated reaction candidates.

It defines execution and build semantics, not a production implementation. The design intentionally keeps the source DSL and canonical contracts language-neutral.

The compiler must preserve the repository's source/generated boundary:

```text
curated source records + schemas + rule definitions
                  |
                  v
        deterministic compiler
 parse -> validate -> resolve -> normalize -> plan
      -> derive/audit -> index -> emit + manifest
                  |
                  v
 generated artifacts / runtime plans / diagnostics
```

Generated artifacts are disposable and reproducible. They never become the editable owner of chemistry truth.

## 2. Canonical inputs

The compiler consumes, through the data-contract boundary, at least:

- `Entity` records (`ent_*`) and typed element/species/ion/substance payloads;
- `Composition` records (`cmp_*`);
- `FacetAssertion` records (`fas_*`);
- `PropertyFact` and `Context` records (`fact_*`, `ctx_*`);
- typed `Relation` records (`rel_*`);
- canonical `Reaction`, `ReactionParticipant`, and `Condition` records (`rxn_*`, `rpart_*`, `cond_*`);
- `Evidence` and `Source` records (`ev_*`, `src_*`);
- stable `RuleReference` records (`rule_*`);
- declarative rule source conforming to `docs/RULE_DSL.md`;
- teaching-view inputs owned by their workstream when whole-repository compilation is performed;
- schema/vocabulary versions and the source Git revision.

The compiler treats the explicit data-contract distinction between no assertion, `unknown`, `not_applicable`, and known values as semantic input. It never maps record absence to boolean false.

If a future contract introduces an explicit completeness/closed-world declaration for a fact or facet domain, the compiler may use it to materialize definite negative knowledge for that exact scope. In the absence of such a declaration, missing knowledge remains unknown.

## 3. Compiler outputs

The inference/compiler workstream may emit these conceptual artifact families:

```text
manifest.json
runtime-id-map.json or embedded equivalent
entity/facet/fact/relation indexes
composition cache
canonical-reaction signature index
compiled-rule-plan artifact
rule-resolution graph
compiler diagnostics
coverage-audit reports
reaction-candidates.jsonl
proof traces or trace indexes
```

The exact external artifact schema is owned by Canonical Data Contracts. Internal runtime-plan layout is compiler-owned but versioned and must be reproducible.

Canonical reactions and generated candidates remain separate channels. A candidate that exactly matches an `rxn_*` record remains an `rcand_*` candidate with canonical-match metadata.

## 4. Build pipeline

Strict compilation uses the following ordered passes.

```text
A. source parse and safe normalization
B. schema validation
C. stable-ID/reference indexing
D. cross-record semantic validation
E. vocabulary/operator registry resolution
F. rule parse + type checking
G. rule lowering to normalized IR
H. overlap / precedence / unknown-policy analysis
I. chemistry-plan validation
J. runtime-ID assignment and data-layout planning
K. index/cache construction
L. canonical reaction signature compilation
M. optional deterministic derivation / coverage audit
N. artifact emission + manifest + diagnostics
```

Validation must precede executable derivation.

### Pass A — Source parse and safe normalization

The compiler follows the canonical YAML-source strategy:

- safe parsing only;
- duplicate mapping keys are errors;
- unsupported YAML aliases/merge behavior is rejected unless a future contract defines deterministic normalization;
- line endings and scalar representations are normalized for hashing;
- file traversal order has no semantic effect.

Source locations are retained for diagnostics.

### Pass B — Schema validation

Run the owning JSON Schema/contracts before inference-specific work. Structural invalidity is not repaired by the rule engine.

### Pass C — Stable-ID/reference indexing

Build stable source indexes for all canonical IDs and semantic vocabularies. Check reference integrity before rule lowering.

Important invariant:

```text
stable source ID != dense runtime ID
```

Stable IDs remain the audit/provenance identity. Dense IDs are bundle-local implementation details.

### Pass D — Cross-record semantic validation

Validate chemistry/data invariants required by inference, including:

- compositions resolve to canonical elements;
- formal/net charge information is coherent where contracts require it;
- contextual facts resolve to context records;
- derived facts retain derivation provenance;
- reaction participants resolve and carry exact positive rational coefficients;
- canonical reactions are balance-checkable for representations that require balancing;
- rule/evidence references resolve.

This pass does not infer new products.

### Pass E — Vocabulary/operator registry resolution

Resolve every facet key, property key, relation key, context dimension, constructor, validator, and predicate operator used by rules.

Each executable DSL operator has a versioned semantic contract containing:

- stable operator key;
- argument/result types;
- three-valued behavior where applicable;
- deterministic semantics;
- trace event encoding;
- implementation version compatibility.

A host-language function name is not a semantic contract.

### Pass F — Rule parse and type checking

Check each rule for:

- stable `rule_*` identity / RuleReference resolution;
- readable rule key consistency if present;
- rule semantic version;
- participant-role types;
- binding cardinalities;
- context dimension types;
- predicate argument types;
- constructor input/output types;
- product binding validity;
- validator keys;
- evidence/provenance requirements;
- references in rule-resolution relationships.

### Pass G — Lowering to normalized rule IR

Source syntax is lowered to a language-neutral normalized intermediate representation.

Conceptual `RulePlanIR`:

```text
rule_ref
rule_version
family_id
decision_domain_id
reactant_role_patterns[]
required_facet_sets[]
forbidden_facet_sets[]
context_guards[]
relation_bindings[]
preconditions[]
exceptions[]
blockers[]
product_constructor_ir[]
postmatch_predicates[]
resolution_edges[]
validators[]
evidence_refs[]
source_location
```

The IR contains no source-file ordering semantics.

### Pass H — Overlap, precedence, and unknown-policy analysis

This is a compile-time correctness gate.

#### Resolution graph

Build a directed graph for `overrides`, `specializes`, and `fallback_for`; normalize symmetric relations such as `equivalent_to` and declared mutual exclusion.

Reject:

- precedence cycles;
- unknown rule refs;
- fallback cycles;
- semantically contradictory resolution declarations.

#### Potential-overlap detection

Within each `decision_domain`, compare rules using statically visible constraints:

- participant arity/kind;
- required/forbidden facets;
- exact identity constraints;
- context enum/range constraints;
- relation-binding domains where the registry provides analyzable constraints;
- product constructor signatures.

If two rules can overlap and can produce non-equivalent effects, strict compilation requires an explicit resolution relationship.

The analyzer does not need to solve arbitrary theorem proving. If it cannot prove disjointness, the conservative result is `potential_overlap`; authors must resolve or specialize the pair explicitly.

#### UNKNOWN audit

Reject source constructs that silently coerce open-world unknown knowledge to false. Verify that every applicability-affecting predicate has the default indeterminate behavior or a contract-approved explicit semantics.

### Pass I — Chemistry-plan validation

Validate rule architecture independent of a full corpus:

- normal product rules do not own balancing coefficients;
- product constructors return canonical refs/queries only;
- product-dependent driving-force tests are in `postmatch`, not hidden validators;
- validators do not decide product identity;
- canonical comparison is not used as a product inference oracle;
- blocking rules have explicit decision-domain effects;
- evidence is present for chemistry-bearing rule semantics.

Representative compile fixtures must include the five baseline families from `docs/RULE_DSL.md`.

### Pass J — Dense runtime-ID assignment and layout planning

Assign dense bundle-local integers after all stable refs resolve.

Deterministic assignment rule:

1. partition by runtime table/type;
2. sort by stable canonical ID/key using a specified byte ordering;
3. assign dense IDs from zero or one consistently;
4. emit/reconstruct a mapping for trace/debug use.

Never persist a dense runtime ID as canonical identity.

### Pass K — Index and cache construction

Build only indexes justified by the rule workload.

Recommended first-line structures:

- entity-kind -> dense entity IDs;
- facet -> entity bitset/list;
- property key + context bucket -> fact/value table;
- relation key + subject -> target list;
- semantic key/alias -> canonical-ID candidates for input normalization;
- rule family -> rule plan IDs;
- decision domain -> plan IDs;
- required-facet signature -> candidate plan IDs;
- exact/specialized override signature -> plan IDs;
- entity ID -> cached exact composition/charge vector;
- canonical reaction signature -> `rxn_*` IDs.

#### Facet bitsets

Facet bitsets are appropriate for high-frequency positive membership checks. For open-world semantics, a single zero bit cannot automatically mean false.

When explicit positive and negative knowledge both exist, a runtime may use two bitsets:

```text
known_true
known_false
```

with neither bit set meaning `UNKNOWN`. If the source contracts do not support explicit negative facet assertions, only definite positive membership should be represented; absence remains unknown.

#### Fact representation

Boolean facts can similarly use compact two-bit/two-mask encodings. Enum/numeric facts use dense tables plus a known/unknown/applicability tag. Context keys may be interned for fast equality/range tests.

#### Composition cache

Balancing and atom validation read canonical `Composition`, not display formulas. Precompute immutable composition vectors keyed by dense entity ID. Charge may be stored as a separate exact integer and optionally appended as a pseudo-row during ionic balancing.

### Pass L — Canonical reaction signature compilation

For each canonical reaction:

1. resolve participants to dense/stable entity IDs;
2. normalize exact rational coefficients to a canonical signed integer vector where possible;
3. normalize participant ordering;
4. include identity-relevant representation/context dimensions from the canonical reaction contract;
5. hash/index the signature;
6. retain `rxn_*` link and evidence/provenance refs.

Do not collapse molecular, complete-ionic, and net-ionic forms unless a separately defined projection declares the equivalence.

### Pass M — Deterministic derivation and coverage audit

Candidate generation may run as an explicit build/audit mode rather than automatically materializing the Cartesian product of all entities.

Offline audit responsibilities include:

- representative positive cases;
- definite no-match cases;
- blocker cases;
- unknown-fact cases;
- precedence/override cases;
- overlap witnesses;
- balancing failures/underdetermined cases;
- canonical exact/equivalent/no-match/conflict comparisons;
- coverage summaries by rule family.

Generated candidates use the data-contract `ReactionCandidate` provenance channel.

### Pass N — Artifact emission and manifest

Emit deterministic artifacts and a manifest containing at least:

```text
compiler name/version/revision
source Git SHA
source normalized digest
schema/contract version(s)
rule DSL version
rule bundle digest
internal plan format version
artifact names + hashes
build diagnostics summary
```

Artifacts are serialized in deterministic stable order. Timestamps, local paths, process IDs, and nondeterministic worker ordering are excluded from semantic digests.

## 5. Runtime plan architecture

The compiled runtime performs bounded indexed matching, not general graph reteaching.

Recommended execution:

```text
normalized request
  -> participant kind/facet signature
  -> rule-family + decision-domain index
  -> small candidate-plan set
  -> tri-valued predicate/binding evaluation
  -> product construction/resolution for surviving plans
  -> postmatch driving-force checks
  -> explicit resolution graph
  -> balance selected candidate
  -> validate
  -> canonical reaction lookup
  -> ReactionCandidate + proof trace
```

Precompiled plans can store predicates as compact typed instruction sequences or normalized AST nodes. The representation is an implementation detail; evaluation order is compiler-determined and trace-stable.

Safe short-circuiting is allowed under three-valued logic only when it cannot change the result or required trace semantics. For example, `FALSE AND UNKNOWN` is definitely `FALSE`; the runtime may skip the second term for decision purposes, but audit mode may evaluate it when complete dependency reporting is requested.

## 6. Why not RETE by default

A full RETE network is not the default architecture because the expected workload is primarily:

- immutable or batch-compiled chemistry knowledge;
- small reaction participant arity;
- strongly typed/faceted candidate narrowing;
- many independent inference/audit requests;
- relatively infrequent incremental mutation of the fact base.

Rete-style alpha/beta memories add complexity, memory overhead, and invalidation semantics that are not currently justified.

Revisit RETE or another incremental discrimination network only if benchmarks show that repeated incremental updates to a large working memory dominate runtime and simpler indexing cannot meet targets.

## 7. Balancing subsystem

### 7.1 Responsibility

Balancing receives a fixed set of canonical reactant/product identities. It does not guess products.

### 7.2 Mathematical model

Construct an exact composition matrix whose columns are participants and whose rows are conserved elements, plus charge when required by representation. Solve for the nullspace:

```text
A x = 0
```

Then require a chemically admissible positive solution, orient sides according to the request, convert exact rationals to the least integer ratio, and divide by the gcd.

### 7.3 Underdetermined systems

If the admissible solution space has more than one chemically distinct degree of freedom, do not let a math library choose a convenient answer. Return an underdetermined diagnostic unless a declarative, evidence-backed balance constraint resolves the chemistry.

This is especially important because “minimal integer solution” is a mathematical convention, not automatically the intended chemical reaction.

### 7.4 Reference implementation strategy

The first Python implementation may use an internal exact-rational solver or SymPy behind a narrow adapter. The adapter owns:

- construction from canonical composition;
- exactness requirements;
- positivity checks;
- nullspace-dimension checks;
- integer normalization;
- deterministic diagnostics.

External library return shapes never become the source contract.

## 8. External library policy

### SymPy

Useful for:

- exact matrix/rational arithmetic;
- RREF/nullspace reference implementation;
- prototyping balancing constraints;
- differential tests against a smaller internal solver.

Risks/limits:

- general symbolic machinery may be heavier than the final hot path needs;
- library behavior/ordering must be normalized by our adapter;
- a nullspace basis is mathematical data, not chemical truth.

Decision: strong candidate for the Python reference balancer, behind an owned deterministic adapter.

### ChemPy

Useful for:

- independent formula/balancing checks;
- migration/prototype parsing experiments;
- differential validation of known equations.

ChemPy exposes formula composition and stoichiometric balancing, including behavior for underdetermined systems. That makes it useful as an independent comparator, but also illustrates why the compiler must own ambiguity handling and canonical normalization.

Decision: optional validation/reference dependency; not the owner of species identity, products, solubility truth, reaction applicability, or canonical balancing policy.

### Formula parsers generally

Formula parsing may support user-input normalization or legacy migration. Once a canonical entity resolves, the compiler uses canonical `Composition` records for balancing and validation. Re-parsing a display formula at runtime must not override canonical composition truth.

### Dependency rule

Any external library is replaceable behind a narrow adapter. A library upgrade that changes candidate semantics must be detected by differential/golden tests and cannot silently redefine compiler output.

## 9. Language strategy

### Python first

Python is the default reference compiler/runtime because the current risk is semantic correctness, not raw throughput.

Strengths:

- fast DSL/schema/compiler iteration;
- strong YAML/JSON Schema/testing ecosystem;
- SymPy integration for exact reference math;
- easy audit tooling and corpus analysis;
- low cost for experimenting with data layouts before freezing native APIs.

Weaknesses:

- per-object overhead can be high for very large corpora;
- tight predicate loops and large bitset/scanning workloads may eventually need optimization;
- multiprocessing introduces serialization overhead if data layout is not planned carefully.

The design therefore uses compact compiled plans and dense IDs even in Python rather than relying on nested dynamic dictionaries forever.

### Rust as preferred future native accelerator

Rust is the first native option if profiling identifies hot paths such as:

- candidate filtering over large bitsets;
- repeated exact balance solves;
- canonical signature hashing/comparison;
- high-volume coverage audit kernels.

Advantages include memory safety, predictable performance, strong enums/types for tri-valued/IR data, and relatively clean Python bindings.

Native code consumes the same compiled plan semantics. It does not receive authority to interpret YAML differently.

### C++

C++ remains viable when a specific mature numerical/chemistry dependency or integration requirement justifies it. For this project, absent such evidence, it has a higher ownership/FFI/safety cost than Rust for a new acceleration layer.

### Decision rule

Do not rewrite the compiler because “native is faster.” Profile first. Optimize algorithms/data layout in Python, then isolate measured kernels. Semantic tests must run against both reference and accelerated implementations.

## 10. Deterministic parallel offline audit

Coverage analysis is naturally parallel because scenarios can be evaluated against an immutable compiled bundle.

### Partitioning

Partition by a stable scenario key, for example:

```text
(rule_family_id, normalized reactant ID multiset, context fixture ID)
```

Sort the full scenario list before partitioning. Workers receive immutable bundle data and do not mint canonical IDs.

### Merge

Worker output is merged by the same stable scenario key, not completion time. Aggregate counters are derived from sorted records.

### Audit outputs

At minimum report per family:

- total scenarios evaluated;
- `INFERRED`;
- `NO_MATCH`;
- `BLOCKED`;
- `INDETERMINATE`;
- `AMBIGUOUS`;
- `INVALID`;
- decisive unknown fact/property keys;
- blocker frequency;
- rule overlap witnesses;
- canonical match distribution;
- balancing diagnostic distribution.

This turns coverage gaps into actionable data-contract/domain-rule work rather than silently guessing missing chemistry.

## 11. Conflict detection strategy

Conflict analysis combines static compilation and runtime witnesses.

### Static

For each decision domain:

1. build a coarse signature from reactant roles/kinds/facets/context;
2. use inverted indexes to generate only plausible overlapping rule pairs;
3. prove simple disjointness from contradictory exact/facet/context constraints;
4. otherwise classify as potential overlap;
5. require explicit resolution for potential non-equivalent overlap.

### Corpus witness audit

Run representative/corpus-generated scenarios through potentially overlapping pairs. Store minimal deterministic witness inputs when both become applicable.

A witness does not replace the static relationship; it helps authors understand the conflict.

## 12. Proof trace compilation

The compiler assigns stable event/expression IDs within the bundle and retains source mappings.

A runtime trace event should contain structured fields such as:

```text
sequence
stage
code
rule_ref
expression_id
subject/input refs
truth/result
fact/relation/evidence refs
details payload
```

The human explanation is rendered from event codes and referenced labels. This permits localization and UI changes without changing proof semantics.

For generated `rcand_*` artifacts, the trace plus rule/input/validator metadata maps directly into the provenance requirements defined by the data contract.

## 13. Canonical comparison implementation

Compile a lookup index from normalized canonical reaction signatures.

Candidate comparison must distinguish:

- exact normalized signature match;
- contract-approved equivalent representation match;
- no canonical match;
- ambiguous multiple canonical matches;
- semantic conflict.

The compiler emits match metadata; it never rewrites the candidate into an `rxn_*` record.

## 14. Diagnostics

Compiler diagnostics are stable machine-readable records with at least:

```text
code
severity
source location
record/rule ref
message arguments
related refs
suggested ownership area (contract/domain/rule/compiler) where useful
```

Core error classes:

- schema/reference invalid;
- missing RuleReference/evidence;
- operator type error;
- illegal UNKNOWN coercion;
- product constructor type error;
- manual coefficient misuse;
- unresolved rule overlap;
- precedence/fallback cycle;
- invalid canonical reaction signature;
- composition/charge inconsistency;
- non-deterministic artifact ordering detected by reproducibility tests.

## 15. Verification strategy

Before a production engine exists, the semantic design can be validated with small fixtures rather than broad implementation.

Required golden scenarios include:

1. `Mg + dilute HCl` -> salt + H2, balanced and traced;
2. a metal below hydrogen with a known activity relation -> definite no-match/block as modeled by the family;
3. the same family with unknown activity relation -> `INDETERMINATE`;
4. metal + salt solution generic displacement;
5. water-preemption override suppressing the generic metal/salt rule;
6. acid + base where coefficients are not in the rule source;
7. carbonate + acid -> salt + CO2 + H2O;
8. `BaCl2 + Na2SO4` precipitation example;
9. precipitation with both products definitely soluble -> rule inapplicable;
10. precipitation with decisive solubility unknown -> `INDETERMINATE`;
11. two artificial overlapping rules without resolution -> compile error;
12. precedence cycle -> compile error;
13. underdetermined balance -> explicit diagnostic;
14. inferred candidate exact canonical match remains `rcand_*`;
15. repeat build from the same source/compiler -> identical semantic artifact hashes.

Differential balancing tests may compare the owned adapter against SymPy/ChemPy, but golden expected chemistry is stored in repository fixtures/reviewed canonical data, not copied from a library at runtime.

## 16. Performance plan

Performance work follows this order:

1. measure representative compiler/runtime/audit workloads;
2. narrow candidates with rule-family/facet/entity indexes;
3. intern stable refs into dense runtime IDs;
4. use bitsets and compact fact tables for hot predicates;
5. cache immutable composition and canonical signatures;
6. remove avoidable allocations/object churn;
7. parallelize independent offline audit partitions;
8. introduce Rust/C++ kernels only for measured remaining hotspots;
9. consider RETE only if incremental-working-memory benchmarks justify it.

Performance changes must pass semantic golden traces and deterministic artifact tests unchanged.

## 17. Current implementation boundary

This workstream defines the executable model and compile plan only. It does not yet require:

- a production Python package;
- a runtime service/API;
- a full rule corpus;
- a native extension;
- a RETE network;
- generated database artifacts;
- migration of legacy chemistry data.

The next implementation milestone should be a deliberately small reference compiler slice proving:

```text
validated canonical fixture
+ compiled declarative rules
-> deterministic inferred ReactionCandidate
-> exact balancing/validation
-> canonical comparison
-> structured proof trace
-> reproducible manifest
```

Only after that vertical slice passes should corpus-scale optimization or native acceleration begin.
