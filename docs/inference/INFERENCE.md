# Deterministic Reaction Inference Semantics

Status: **F3A executable canonical semantics**

## Pipeline

```text
input normalization
→ reference/context resolution
→ structural participant binding candidates
→ typed predicate evaluation (TRUE/FALSE/UNKNOWN)
→ blockers
→ applicable-rule resolution graph
→ typed product construction
→ canonical entity resolution
→ exact balancing
→ atom validation
→ charge validation
→ canonical Reaction comparison
→ ReactionCandidate + proof trace
```

The implementation may short-circuit only where the observable result and proof semantics remain deterministic.

## Matching and UNKNOWN

Participant binding uses canonical identity/kind constraints. Required/forbidden facets and context conditions use the typed predicate registry. Multiple possible participant bindings are evaluated deterministically; a failed arbitrary binding cannot suppress another valid binding.

Missing/open-world knowledge is `UNKNOWN`, not false. Explicit `unknown`, `not_applicable`, and absent facts remain distinguishable in the trace.

## Rule resolution

All fully applicable rules are considered before a winner is selected. Explicit `overrides`, `specializes`, and `fallback_for` edges define precedence; transitive precedence is respected. If multiple non-equivalent winners remain, inference returns structured `ambiguous_rule_resolution` rather than selecting by source order.

A declared `mutually_exclusive_with` pair that becomes simultaneously applicable is a runtime ambiguity, because the authored exclusivity assumption was violated by the actual inputs.

## Product construction and validation

Products resolve only through bounded canonical constructors. Unresolved or ambiguous semantic-key lookup is explicit and cannot fabricate an Entity.

Balancing receives fixed canonical reactants/products and uses exact arithmetic. Atom and charge validation are separate stages and diagnostics.

## Canonical comparison

Canonical comparison happens after validation. `none`, exact single match, and multi-match conflict remain distinguishable. Even an exact match remains a generated `ReactionCandidate` until separate curation changes canonical source.

## ReactionForm projection

A `ReactionForm` is projected only when its declared `required_assumptions` are satisfied. The projection response retains the owning `reaction_id`; no new Reaction identity is created.

F3A covers curated assumption-gated molecular/net-ionic examples only. It is not a universal aqueous speciation solver.

## Structured diagnostics

Runtime/source failures use deterministic objects containing `code`, `stage`, `message`, and optional details. Current distinguished codes include:

`schema_invalid`, `reference_unresolved`, `unknown_applicability`, `blocked`, `no_rule_match`, `ambiguous_rule_resolution`, `rule_overlap_compile_error`, `product_unresolved`, `balance_failure`, `atom_validation_failure`, `charge_validation_failure`, `canonical_no_match`, and `canonical_conflict`.

## Proof trace

Trace events retain normalized inputs, rule IDs/versions, predicate operator/subject/key/expected value, truth result, knowledge state, fact origin, blocker checks, rule resolution, product resolution, balancing, conservation validation, canonical comparison, and emitted candidate key.
