# Deterministic Reaction Inference Semantics

Status: **M7 ammonium/base and condition-aware canonical semantics**

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
→ participant-signature canonical Reaction lookup
→ required-condition compatibility filtering
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

Products resolve only through bounded canonical constructors. Ionic-pair construction uses canonical ion charge/composition plus exact positive integer coefficients and must resolve one existing neutral Substance. Unresolved or ambiguous lookup is explicit and cannot fabricate an Entity.

When ionic-pair construction consumes bound aqueous reactants, the generated candidate and `products.constructed` proof event retain the normalized profile key, model, target, and evidence IDs for each speciation profile used. This provenance is deterministic and does not create a second source of chemistry truth.

Balancing receives fixed canonical reactants/products and uses exact arithmetic. The M6 carbonate family demonstrates that multi-proton molecular stoichiometry follows from canonical composition after product identities are fixed; no Rule or engine branch supplies coefficients. Atom and charge validation are separate stages and diagnostics.

## Canonical comparison

Canonical comparison happens after validation. The existing normalized participant signature retrieves chemical matches; each canonical Reaction's embedded conditions are then treated as required key/value constraints. Extra candidate context is ignored for compatibility, while missing/conflicting required conditions reject that canonical match. `none`, exact single match, and multi-match conflict remain distinguishable. Condition evidence and compatibility decisions remain in generated proof/provenance. Even an exact match remains a generated `ReactionCandidate` until separate curation changes canonical source.

## ReactionForm projection

A `ReactionForm` is projected only when its declared `required_assumptions` and a unique context-matching canonical speciation profile are available. The projection response retains the owning `reaction_id`, exact coefficients, atom/charge validation, derivation operators, Reaction conditions, and evidence; no new Reaction identity is created. Net ionic participants are reduced to their smallest exact rational scale after spectator cancellation.

M7 still covers bounded strong-electrolyte aqueous projection only. The ammonium/base family emits `NH3(g)` only for aqueous warmed context. Missing or ambiguous speciation is explicit; this is not a universal aqueous speciation solver, ammonia equilibrium model, or relative-acid-strength model.

An overall `indeterminate/unknown_applicability` result can coexist with a known-false predicate in one rule family when another structurally possible family depends on absent open-world knowledge. This does not emit a candidate or author canonical negative reaction truth.

## Structured diagnostics

Runtime/source failures use deterministic objects containing `code`, `stage`, `message`, and optional details. Current distinguished codes include:

`schema_invalid`, `reference_unresolved`, `unknown_applicability`, `blocked`, `no_rule_match`, `ambiguous_rule_resolution`, `rule_overlap_compile_error`, `product_unresolved`, `balance_failure`, `atom_validation_failure`, `charge_validation_failure`, `canonical_no_match`, and `canonical_conflict`.

## Proof trace

Trace events retain normalized inputs, rule IDs/versions, predicate operator/subject/key/expected value, truth result, knowledge state, fact origin, blocker checks, rule resolution, product resolution, balancing, conservation validation, canonical comparison, and emitted candidate key.
