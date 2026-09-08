# Architecture Decision Log

Status: **M6 strong-acid carbonate gas-evolution decisions**

## ADR-F1-001 — Entity-kind alignment

Canonical `entity_kind` is `element | species | substance | material_system`. `Ion` is `species_kind: ion`; solution/mixture are `material_system_kind` values.

## ADR-F1-002 — Structure ownership

`Structure` is stable identity when durable structural reference is required. Representations are subordinate values. `Bond` is embedded with a structure-local key by default.

## ADR-F1-003 — Source normalization

`Composition`, `Context`, `ReactionParticipant`, `Condition`, `TeachingViewPath`, and default `Bond` are embedded value objects unless independent lifecycle/provenance requires durable identity.

## ADR-F1-004 — ReactionCandidate lifecycle

Pure compilation emits a deterministic content-derived `candidate_key` and mints no UUID. Persistent review state may additionally own `rcand_*` while retaining the immutable candidate key.

## ADR-F1-005 — Rule identity owner

The declarative `Rule` is the sole canonical owner of `rule_*` identity, semantic version, evidence, provenance, and rule-resolution relationships.

## ADR-F1-006 — Reaction identity vs representation

Use `Reaction + ReactionForm`. Molecular, complete ionic, net ionic, symbolic, and thermochemical forms may be projections of one transformation. Chemically distinct half-reactions remain separate related `Reaction` records.

## ADR-F1-007 — Macro/micro reaction referents

Reaction participants may target `Species`, `Substance`, or `MaterialSystem`. Projection between referent levels must declare speciation/dissociation assumptions.

## ADR-F1-008 — Canonical specialist locations

Specialist canonical documents live under `docs/domain/**`, `docs/pedagogy/**`, `docs/contracts/**`, and `docs/inference/**`. Do not create duplicate root-level specialist owners.

## ADR-F1-009 — Compiler-contract ownership

Data Contracts owns external artifact/source contracts. Compiler owns internal plans, indexes, caches, operator lowering, and runtime layout.

## ADR-F1-010 — Identity remains independent from presentation

Names, formulas, aliases, paths, file order, and runtime dense IDs never define durable chemistry identity.

## ADR-F1-011 — Open-world fact semantics

Absence, explicit `unknown`, `not_applicable`, and known values including boolean `false` remain distinct. Missing knowledge is never silently coerced to false.

## ADR-F1-012 — Canonical Reaction != ReactionCandidate

Canonical comparison never promotes a generated candidate. Promotion remains an evidence-backed source curation action.

## ADR-F1-013 — Language and optimization

The source contracts and DSL remain language-neutral. Python-first remains the reference implementation; performance changes require evidence and stable semantic boundaries.

## ADR-F2-001 — Deterministic canonical JSON

Semantic hashing/artifact payloads use owned deterministic JSON semantics: UTF-8, NFC-normalized strings/keys, lexicographically sorted mappings, compact separators, integer-only semantic numeric values, semantic list order, and no timestamps/local paths/process IDs/traversal-order metadata. `candidate_key` is `cand_sha256_` plus SHA-256 of canonical semantic candidate content.

## ADR-F2-002 — Executable YAML + JSON Schema boundary

Authored chemistry/rules use human-reviewable YAML. Structural validation precedes stable-ID/reference checks, rule compilation, balancing, and conservation checks. Phase remains participant/template context rather than identity.

## ADR-F2-003 — Source Rule vs internal RulePlan

Authored `Rule` source compiles into typed compiler-owned `RulePlan`. Balancing receives fixed canonical reactants/products; canonical comparison occurs only after product resolution and conservation validation. File order and integer priority are not resolution semantics.

## ADR-F3A-001 — Reusable participant pattern contract

A rule participant pattern may constrain exact identity, `entity_kind`, `species_kind`, required facets, and forbidden facets. Required/forbidden facet truth is evaluated through the normal three-valued predicate model rather than hidden closed-world matching.

Ordinary reaction-family expansion should normally add canonical data plus declarative Rule source, not an engine branch. The AgCl precipitation fixture is the architecture proof: exact NaCl/AgNO3 participant IDs were replaced by typed/faceted participant patterns without changing its canonical `ReactionCandidate` result.

## ADR-F3A-002 — Small typed predicate registry

F3A source semantics use a bounded operator registry rather than host-language function names or arbitrary expressions. The executable registry contains:

- `equals`;
- `not_equals`;
- `is_known`;
- `in_set`.

Each operator declares allowed subjects, input types, expected-argument shape, and UNKNOWN behavior. F3A supports `context` and `facet` predicate subjects. Relation and numeric operators remain deferred until executable source data justifies them.

## ADR-F3A-003 — Fact state and origin boundary

Fact state distinguishes `known`, explicit `unknown`, `not_applicable`, and compiler-observed `absent`. Known boolean `false` remains a known value. Fact origin is `intrinsic | contextual | derived`; request context is traced as contextual. Absence is not authored as a fake fact record.

## ADR-F3A-004 — Conservative static overlap analysis

Within one `decision_domain`, the compiler statically analyzes participant count/kind, exact identity, required/forbidden facets, and simple context-equality constraints. If disjointness cannot be proven, `potential_overlap` is conservative and acceptable.

Potentially overlapping rules with non-equivalent outcomes require an explicit semantic relationship. Strict compilation rejects unresolved overlap and reports both rule IDs plus the overlap reason/signature.

## ADR-F3A-005 — Explicit rule-resolution graph

Supported relationships are `overrides`, `specializes`, `fallback_for`, `equivalent_to`, and `mutually_exclusive_with`.

Unknown rule references, self relationships, contradictory equivalent declarations, and precedence cycles are compile errors. `overrides`/`specializes` mean the declaring rule wins; `fallback_for` means the referenced rule wins while both apply. Runtime precedence is transitive and deterministic.

## ADR-F3A-006 — Canonical product construction remains bounded

F3A product constructors are limited to:

- `exact_entity` resolution;
- canonical `semantic_key` resolution.

A constructor must resolve to exactly one existing canonical Entity. Zero matches or ambiguity is `product_unresolved`; the compiler never fabricates canonical identity. Variable-valence or other chemically ambiguous construction remains unresolved until source/context semantics justify a unique entity.

## ADR-F3A-007 — ReactionForm projection is assumption-gated

`ReactionForm` remains a projection of its owning `Reaction`, not a second reaction identity. Projection records declare stable `required_assumptions` such as aqueous medium, strong-electrolyte dissociation, precipitate integrity, or weak-electrolyte molecular retention. Projection is available only when all required assumptions are supplied.

F3A does not implement a universal aqueous speciation solver. Half-reactions remain independent `Reaction` records.

## ADR-F3A-008 — Separate compatibility version axes

The compiler now exposes independent version axes:

- source schema: `3.0.0`;
- Rule DSL: `1.0.0`;
- internal RulePlan: `1.0.0`;
- external artifact format: `1.0.0`.

Artifacts carry the external format version and manifests carry all four versions. Consumers can reject unsupported artifact format versions. No broader long-term backwards-compatibility promise is made by F3A.

## ADR-F3A-009 — Structured diagnostic codes

Compiler/inference failures use deterministic structured diagnostics with `code`, `stage`, `message`, and optional sorted `details`. Current codes distinguish schema invalidity, unresolved references, unknown applicability, blockers, no match, ambiguous rule resolution, overlap compile errors, product resolution, balancing, atom/charge validation, and canonical no-match/conflict.

## F3A remaining limitations

F3A intentionally does not yet provide relation-predicate execution, numeric chemistry predicates, arbitrary expression evaluation, a general speciation solver, broad chemistry-family population, redox/organic inference, database/runtime services, RETE, or native acceleration.

## ADR-M4-001 — Context-qualified properties

Behavioral facts such as electrolyte strength and solubility class are typed property assertions qualified by structured context. Stable chemical classifications remain facets. Required facets and properties retain open-world TRUE/FALSE/UNKNOWN evaluation; a missing assertion is not silently converted to false.

## ADR-M4-002 — Evidence-aware aqueous projection

Canonical aqueous speciation profiles own exact canonical species IDs, rational coefficients, context, model, and evidence. Bounded ionic product construction combines canonical compositions and charges, resolves exactly one existing neutral Substance, and never parses display formulas or creates an Entity.

`MaterialSystem` cannot enter exact balancing without an explicit stoichiometric/speciation projection. Aqueous complete/net ionic forms are deterministic derived projections of their owning Reaction, retain derivation/evidence provenance, and never become independent Reaction identities.

## ADR-M4-003 — Teaching and generated truth boundaries

`TeachingView` is schema- and reference-validated executable canonical source, but it does not participate in reaction inference. Generated `ReactionCandidate` and derived `ReactionForm` artifacts remain compiler output and cannot enter canonical reaction source implicitly.

## ADR-M5-001 — Strong-acid hydrogen-carbonate scope

M5 supports gas evolution only when an aqueous reactant is a classified acid with contextual `acid.strength = strong` and `electrolyte.strength = strong`, and the other reactant is a classified salt and hydrogen carbonate with contextual `electrolyte.strength = strong` and `solubility.class = soluble`. Missing facts remain UNKNOWN and emit no candidate.

The rule reuses canonical aqueous speciation profiles and the existing `ionic_pair` constructor to form the salt, while CO2 and H2O resolve as existing canonical entities. The constructor records the exact speciation profiles and their evidence in candidate provenance. Formula parsing, exact HCl/NaHCO3 branches, and runtime external chemistry truth remain prohibited.

The rule declares `specializes` against strong-acid/base neutralization so conservative overlap is resolved by an explicit semantic relationship, never file order or integer priority.

## ADR-M6-001 — Sibling strong-acid carbonate rule

M6 represents `CO3^2-` as a canonical divalent Species and soluble sodium/potassium carbonate as canonical Substances with evidence-aware complete-dissociation profiles. Exact profile coefficients (`2 Na+` or `2 K+` per `CO3^2-`) are authored data, not formula-derived runtime truth.

Carbonate gas evolution is a sibling Rule rather than a generalization of M5. This preserves the chemical distinction between carbonate and hydrogen carbonate without adding disjunction syntax, a synthetic umbrella facet, or hidden stoichiometric branching. Both rules reuse the existing `ionic_pair` constructor, exact balancer, and ReactionForm projector. The balancer derives the two-acid stoichiometry; the Rule contains no carbonate-specific coefficients or reactant IDs.

The carbonate Rule `specializes` strong-acid/base neutralization when their broad structural patterns could overlap. It is `mutually_exclusive_with` the hydrogen-carbonate Rule because those canonical classifications identify distinct reactants; simultaneous applicability is therefore a data/model contradiction reported as ambiguity.

## M6 remaining limitation

Relative acid strength, weak-acid carbonate applicability, pKa comparison, equilibrium direction, concentration-sensitive displacement, carbonate/CO2/H2CO3 equilibria, buffers, and universal speciation remain deferred. M6 supports only aqueous strong acids and soluble, strongly dissociated carbonate salts.
