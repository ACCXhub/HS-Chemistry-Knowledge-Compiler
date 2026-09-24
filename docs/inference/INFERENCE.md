# Deterministic Reaction Inference Semantics

Status: **M25 baseline with equation-integrity corrections**

## Pipeline

```text
input normalization
→ reference/context resolution
→ structural participant identity/kind/phase binding candidates
→ typed predicate evaluation, including bounded exact/dynamic-target Relations (TRUE/FALSE/UNKNOWN)
→ blockers
→ applicable-rule resolution graph
→ typed relation/speciation/exact-entity ion-source resolution
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

Participant binding uses canonical identity/kind/phase constraints. All aqueous-only families require aqueous reagent phases; M10 additionally requires solid metal. Aqueous medium alone does not dissolve an input or convert its phase. Required/forbidden facets and context conditions use the typed predicate registry. Multiple possible participant bindings are evaluated deterministically; a failed arbitrary binding cannot suppress another valid binding.

Missing/open-world knowledge is `UNKNOWN`, not false. Explicit `unknown`, `not_applicable`, and absent facts remain distinguishable in the trace.

Relation predicates resolve `(source binding, controlled relation key, canonical target ID, context)` where the target is either exact or obtained from a typed entity source. M19 may select the unique positive ion from a bound salt's context-matching canonical speciation. Matching evidence-backed assertions are known true; no assertion or unavailable/ambiguous target source is ABSENT/UNKNOWN. Only `equals expected: true` is accepted. Equally specific assertions for the same target are combined deterministically with merged evidence, and only assertions from the finally applicable binding enter candidate provenance.

## Rule resolution

All fully applicable rules are considered before a winner is selected. Explicit `overrides`, `specializes`, and `fallback_for` edges define precedence; transitive precedence is respected. A blocked path does not suppress an independent UNKNOWN path: without a fully applicable rule, that result remains indeterminate. If multiple non-equivalent winners remain, inference returns structured `ambiguous_rule_resolution` rather than selecting by source order.

A declared `mutually_exclusive_with` pair that becomes simultaneously applicable is a runtime ambiguity, because the authored exclusivity assumption was violated by the actual inputs.

## Product construction and validation

Products resolve only through bounded canonical constructors. Ionic-pair construction uses canonical ion charge/composition plus exact positive integer coefficients and must resolve one existing neutral Substance. Unresolved or ambiguous lookup is explicit and cannot fabricate an Entity.

When ionic-pair construction consumes bound aqueous reactants, the generated candidate and `products.constructed` proof event retain the normalized profile key, model, target, and evidence IDs for each speciation profile used. When it consumes a one-hop relation target, they separately retain source ID, controlled relation key, target ID, normalized context, and evidence IDs. Relation target construction checks equally specific TRUE/FALSE contradictions before filtering positives. Relation provenance is omitted for candidates that did not use a relation. This metadata is deterministic and does not create a second source of chemistry truth.

M10 uses this boundary for `elemental metal -> product cation` plus `acid -> speciated anion`. Solid metals never receive fake aqueous speciation, and the compiler does not guess oxidation state or valence. Missing or ambiguous relation targets produce structured relation-resolution diagnostics before balancing.

M11 reuses the relation path for the metal cation and resolves OH- through an exact canonical ion source. The fixed ion is not attributed to water speciation. Solid-metal and liquid-water phase constraints are checked before predicates; `metal.water_reactivity` is a separate ambient contextual fact, so M10 activity relative to hydrogen cannot make Zn/Mg water positives. Missing reactivity remains UNKNOWN, while a missing cation relation or exact ion target is an explicit resolution failure once the Rule is otherwise applicable.

M19 uses one generic Rule for aqueous metal-salt displacement. The salt's canonical speciation supplies its unique positive ion to the dynamic `metal.displaces_cation` predicate and its negative ion to product construction. A separate `metal.product_cation` Relation supplies the incoming metal's cation, and the unchanged ionic-pair resolver selects the canonical neutral salt. The displaced cation reaches its elemental-metal Substance through exactly one `ion.elemental_substance` Relation hop. CuSO4, AgNO3, and CuCl2 therefore reuse the same family without activity ranking, formula parsing, reverse inference, valence guessing, or product fabrication.

M20 gives the same one-hop Relation lookup three explicit outcomes: applicable positive assertion is TRUE, applicable `truth: false` is FALSE, and no assertion is UNKNOWN. A FALSE displacement predicate rejects only that M19 binding/pathway; it is not a canonical negative Reaction or global no-reaction conclusion. Dynamic cation resolution and negative assertion evidence both remain visible in the proof trace.

`EntitySourcePlan` has four closed forms: exact entity, participant binding, unique signed speciation ion, and one Relation target whose source cannot itself be a Relation target. Resolution preserves consumed profile/assertion/evidence provenance. Missing or ambiguous speciation, product cation, or ion-to-elemental mapping produces a structured indeterminate/resolution diagnostic; it never creates a target.

Balancing receives fixed canonical reactants/products and uses exact arithmetic. The M6 carbonate family demonstrates that multi-proton molecular stoichiometry follows from canonical composition after product identities are fixed; no Rule or engine branch supplies coefficients. Atom and charge validation are separate stages and diagnostics.

## Canonical comparison

Canonical comparison happens after validation. The normalized participant signature merges identical role/entity/phase terms and reduces exact rational coefficients to primitive integers before retrieving chemical matches; each canonical Reaction's embedded conditions are then treated as required key/value constraints. Extra candidate context is ignored for compatibility, while missing/conflicting required conditions reject that canonical match. `none`, exact single match, and multi-match conflict remain distinguishable. Condition evidence and compatibility decisions remain in generated proof/provenance. Even an exact match remains a generated `ReactionCandidate` until separate curation changes canonical source.

## ReactionForm projection

A `ReactionForm` is projected only when its declared `required_assumptions` and a unique context-matching canonical speciation profile are available. The projection response retains the owning `reaction_id`, exact coefficients, atom/charge validation, derivation operators, Reaction conditions, and evidence; no new Reaction identity is created. Net ionic participants are reduced to their smallest exact rational scale after spectator cancellation.

M7 still covers bounded strong-electrolyte aqueous projection only. The ammonium/base family emits `NH3(g)` only for aqueous warmed context. Missing or ambiguous speciation is explicit; this is not a universal aqueous speciation solver, ammonia equilibrium model, or relative-acid-strength model.

An overall `indeterminate/unknown_applicability` result can coexist with a known-false predicate in one rule family when another structurally possible family depends on absent open-world knowledge. This does not emit a candidate or author canonical negative reaction truth.

## Structured diagnostics

Runtime/source failures use deterministic objects containing `code`, `stage`, `message`, and optional details. Current distinguished codes include:

`schema_invalid`, `reference_unresolved`, `unknown_applicability`, `blocked`, `no_rule_match`, `ambiguous_rule_resolution`, `rule_overlap_compile_error`, `product_unresolved`, `balance_failure`, `atom_validation_failure`, `charge_validation_failure`, `canonical_no_match`, and `canonical_conflict`.

## Proof trace

Trace events retain normalized inputs, rule IDs/versions, predicate operator/subject/key/target/expected value, truth result, knowledge state, fact origin, matched Relation assertions and evidence, blocker checks, rule resolution, speciation/relation product inputs, balancing, conservation validation, canonical comparison, and emitted candidate key.
