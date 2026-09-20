# Architecture Decision Log

Status: **M11 bounded alkali-metal/liquid-water hydrogen-evolution decisions**

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

- source schema: `3.1.0`;
- Rule DSL: `1.0.0`;
- internal RulePlan: `1.0.0`;
- external artifact format: `1.1.0`.

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

## ADR-M7-001 — Executable embedded Reaction conditions

Canonical Reaction conditions are embedded, evidence-bearing values with controlled `key` and `value` fields. M7 executes only `medium = aqueous` and `temperature_regime = warmed`; duplicate keys and unresolved condition evidence are source errors. Conditions do not receive ordinary durable IDs and free text is not semantic truth.

Canonical comparison keeps the normalized participant signature as its first-stage index, then filters signature matches by each Reaction's required conditions. Extra request context is allowed; a missing or conflicting required value is incompatible; multiple compatible reactions remain an explicit conflict. Existing conditionless reactions remain compatible. Candidate semantic identity continues to include the request context, so unchanged M4-M6 candidate keys do not change.

This source and artifact shape change advances source schema to `3.1.0` and artifact format to `1.1.0`; artifact reader compatibility retains `1.0.0`. Rule DSL and internal RulePlan remain `1.0.0` because no Rule syntax or lowered plan contract changed.

## ADR-M7-002 — Conditioned ammonium/strong-base gas-liberation family

M7 adds canonical `NH4+`, `NH3`, `NH4Cl`, and `(NH4)2SO4`, with `classification.ammonium` as a stable identity facet on ammonium-bearing salts/species. The reusable Rule requires a soluble, strongly dissociated ammonium salt, a strongly dissociated strong base, aqueous medium, and warmed temperature regime. It uses existing aqueous speciation and `ionic_pair` construction to resolve the spectator salt and never parses formula text or creates `NH4OH`.

The canonical M7 reactions intentionally represent the high-school warmed test with `NH3(g)`. OpenStax supports ammonia preparation from an ammonium salt and strong base; the Cambridge IGCSE qualitative-analysis specification supplies the warming condition. General aqueous `NH4+ + OH- -> NH3(aq) + H2O` chemistry and ammonia equilibria remain outside this gas-specific Rule.

The exact balancer derives both molecular equations. The projector now reduces any common rational scale after spectator cancellation, allowing the ammonium-sulfate case to normalize from two reactive equivalents to `NH4+ + OH- -> NH3(g) + H2O` while retaining Reaction-condition and evidence provenance.

Static overlap analysis finds conservative same-domain overlaps with neutralization and the two strong-acid carbonate families. M7 declares them mutually exclusive because its bounded strong-base participant cannot simultaneously be the strong-acid participant required by those families; cross-domain precipitation remains outside the same-domain overlap graph. No priority or source order is used.

## M7 remaining limitations

Unconditioned dissolved-ammonia projection, ammonia equilibrium constants, generic weak acid/base reasoning, buffers, broader nitrogen chemistry, and sulfite/SO2 gas evolution remain deferred.

## ADR-M8-001 — Sibling strong-acid sulfite rule on the established pipeline

M8 represents `SO3^2-`, `SO2`, Na2SO3, and K2SO3 as canonical identities with exact composition, charge, and evidence-aware aqueous speciation. Strong-acid sulfite gas evolution is a sibling Rule to the M5 hydrogen-carbonate and M6 carbonate families. It retains their bounded strong-acid gate and adds the chemically distinct `classification.sulfite` salt constraint; no umbrella gas-evolving-anion facet, formula parsing, OR syntax, or exact reactant branch is introduced.

The existing `ionic_pair` constructor resolves the spectator salt, the exact balancer derives `2 acid : 1 sulfite : 2 salt : 1 SO2 : 1 H2O`, and existing complete/net ionic projection yields `2 H+ + SO3^2- -> SO2(g) + H2O`. M8 carries only aqueous applicability: ordinary aqueous acidification supports SO2 liberation, so no warmed condition or D05 experiment mapping is authored. M7 condition-aware comparison remains unchanged.

The sulfite Rule `specializes` strong-acid/base neutralization for conservative same-domain overlap resolution. It is mutually exclusive with the hydrogen-carbonate, carbonate, and ammonium/strong-base families because the bounded participant classifications and acid/base orientations are chemically distinct. Sulfate is not sulfite and cannot match from formula similarity.

M8 composes the existing source, Rule DSL, RulePlan, artifact, balancing, and projection contracts. Compatibility versions therefore remain source schema `3.1.0`, Rule DSL `1.0.0`, RulePlan `1.0.0`, and artifact format `1.1.0`; no compiler dependency or infrastructure primitive is added.

## M8 remaining limitations

Hydrogen sulfite, weak-acid applicability, relative acid strength, sulfurous-acid and SO2/H2SO3 equilibria, sulfite oxidation, SO2 reducing/bleaching behavior, sulfur oxidation-state inference, H2S, thiosulfate, and broader sulfur chemistry remain deferred.

## ADR-M9-001 — Context-bounded thiosulfate decomposition and mixed-phase products

M9 represents `S2O3^2-`, Na2S2O3, K2S2O3, and elemental sulfur as canonical identities. `classification.thiosulfate` is distinct from sulfite and sulfate. Elemental sulfur is a macroscopic `Substance` distinct from the abstract sulfur `Element`; its `S: 1` composition is only the exact stoichiometric basis required by balancing and makes no monatomic or allotrope-structure claim.

Acid strength alone is insufficient for thiosulfate decomposition because strong oxidizing acids may introduce competing chemistry. The M9 Rule therefore also requires contextual `acid.redox_character = non_oxidizing`. Aqueous HCl owns an evidence-backed known value for the bounded pathway; HNO3 owns no fabricated compatible or incompatible value, so its applicability remains UNKNOWN and emits no M9 candidate.

The sibling Rule uses `classification.acid`, `classification.salt`, `classification.thiosulfate`, contextual strength/electrolyte/solubility/redox facts, and aqueous context. It reuses `ionic_pair`, exact balancing, and ReactionForm projection. The existing pipeline preserves the simultaneous aqueous spectator salt, SO2 gas, elemental-sulfur solid, and liquid water products and normalizes both sodium and potassium cases to `2 H+ + S2O3^2- -> SO2(g) + S(s) + H2O(l)`.

No warmed condition, exact reactant-ID engine branch, formula parsing, general redox inference, new dependency, compiler/schema/DSL/artifact change, or D05 experiment mapping is introduced. Compatibility coordinates remain source schema `3.1.0`, Rule DSL `1.0.0`, RulePlan `1.0.0`, and artifact format `1.1.0`.

## M9 remaining limitations

Nitric-acid/thiosulfate product prediction, general acid redox classification, oxidation-number or electrode-potential reasoning, iodine/chlorine thiosulfate chemistry, H2S/polysulfides, sulfur allotrope structure, weak-acid generalization, and broader sulfur/redox systems remain deferred.

## ADR-M10-001 — Embedded typed product-cation relations and typed ion sources

M10 makes one bounded Relation family executable without introducing a generic graph subsystem. An elemental-metal `Substance` with known-true `classification.metal` may own an evidence-bearing, context-qualified `metal.product_cation` assertion whose target must be a positively charged canonical ion `Species`. Source and target constraints are enforced during semantic reference validation, not deferred to product construction. The assertion has no ordinary durable UUID: its deterministic provenance is the tuple of source entity, controlled relation key, target entity, context, and evidence. Lookup is one hop, uses existing context specificity, returns zero targets explicitly, and preserves equally specific multiple targets so a uniqueness-requiring product resolver can report ambiguity.

The `ionic_pair` Rule constructor now accepts independently typed `cation_source` and `anion_source` values. M10 combines a metal's `relation_target` cation with the acid's existing `speciation` anion, then delegates unchanged charge/composition matching to the canonical neutral ionic-pair resolver. Historical `cation_from` and `anion_from` source syntax remains accepted and lowers to speciation-backed `IonSourcePlan` values. Neither path parses formula text, guesses valence, or creates an Entity.

These changes independently advance source schema to `3.2.0`, Rule DSL to `1.1.0`, and internal RulePlan to `1.1.0`. External artifact format advances to `1.2.0` because emitted `compiled-rule-plans.json` products now expose typed nested ion sources rather than the `1.1.0` flat `cation_from`/`anion_from` shape; an old consumer cannot safely interpret the relation-backed M10 plan. The reader continues to accept artifact formats `1.0.0`, `1.1.0`, and `1.2.0`. Relation provenance is emitted only when a generated candidate actually consumed a relation, so unchanged M4-M9 candidate semantic keys remain unchanged.

## ADR-M10-002 — Bounded metal/non-oxidizing-acid hydrogen evolution

M10 represents Mg, Zn, and Cu Element identities separately from their elemental solid Substances. Solid metals have no fabricated aqueous speciation. Evidence-backed contextual `metal.activity.relative_to_hydrogen` facts classify Mg and Zn as `above` and Cu as `below`; Mg and Zn additionally own their typed product-cation relations to `Mg2+` and `Zn2+`. Acid strength remains independent from the existing contextual `acid.redox_character` fact.

One declarative Rule requires an elemental metal classified as a metal and above hydrogen, an aqueous strong/strong-electrolyte acid with `acid.redox_character = non_oxidizing`, and resolves the canonical chloride plus H2(g). Exact balancing derives `metal : HCl : metal chloride : H2 = 1:2:1:1`. Canonical complete/net ionic projection retains the solid metal, dissociates only HCl and the soluble product salt, cancels chloride, and yields `Zn + 2 H+ -> Zn2+ + H2` or `Mg + 2 H+ -> Mg2+ + H2`.

Cu's M10 binding fails on a known activity predicate and emits no hydrogen candidate. The overall open-world result may remain indeterminate because other structurally possible families/bindings lack facts; this does not weaken the known M10 failure. HNO3 has no fabricated non-oxidizing compatibility value, so Zn/HNO3 remains UNKNOWN. Numeric electrode potentials, oxidation-state inference, electron/half-reaction balancing, variable-valence metals, passivation, concentration effects, and general redox inference remain deferred.

## ADR-M11-001 — Exact canonical ion sources and phase-bounded participant patterns

M11 adds `exact_entity` as the third typed `IonSourcePlan` kind. It means “use this exact canonical ion Species”: source/reference validation requires the target to exist, be an ion, and have the sign required by its cation/anion position. Runtime resolution repeats the same bounded checks for altered in-memory knowledge, includes the target Entity's evidence, and then delegates unchanged charge/composition matching to `ionic_pair`. It does not parse formulas, create an Entity, or introduce a hydroxide-specific constructor.

Reactant patterns may now constrain an authored participant `phase`. Phase is checked against the normalized input participant before predicate evaluation and also participates in conservative same-domain overlap analysis. M11 uses this generic constraint to require solid metal and liquid H2O; a gas-phase water input cannot enter the liquid-water Rule. Embedded Reaction conditions now admit the controlled `temperature_regime = ambient` value so the canonical Na/K records state their bounded condition explicitly.

These source changes advance source schema to `3.3.0`. The new `exact_entity` ion-source syntax and participant `phase` constraint advance Rule DSL to `1.2.0`; their lowered `IonSourcePlan.target_id` and `ParticipantPatternPlan.phase` fields advance RulePlan to `1.2.0`. Because `compiled-rule-plans.json` exposes those fields, artifact format independently advances to `1.3.0`. The reference reader continues to accept artifact formats `1.0.0`, `1.1.0`, and `1.2.0`.

## ADR-M11-002 — Bounded alkali-metal/liquid-water hydrogen evolution

Elemental Na and K are canonical solid Substances distinct from their Element identities. They own evidence-backed `metal.water_reactivity = reacts` facts qualified by `temperature_regime = ambient` and one-hop `metal.product_cation` relations to canonical Na+ and K+. The relation assertions are unqualified because the product-cation identity is not itself a medium-dependent dissociation claim; M10's existing aqueous-qualified Mg/Zn assertions remain unchanged. No elemental metal and no H2O record receives a speciation profile.

One Rule matches a solid classified metal plus exact liquid H2O, requires the ambient water-reactivity fact, and constructs the hydroxide through relation-derived cation + exact canonical OH- + the existing neutral `ionic_pair` resolver. Existing H2 is the other exact product. The exact balancer derives `2 metal : 2 H2O : 2 hydroxide : 1 H2` for both Na and K; there is no exact Na/K engine branch and no fabricated product identity.

Canonical Na/K Reactions require ambient temperature. Aqueous hydroxide product speciation yields `2 M(s) + 2 H2O(l) -> 2 M+(aq) + 2 OH-(aq) + H2(g)`; because there are no spectators, complete and net ionic forms are semantically equal. Cu, Zn, and Mg lack the M11 water-reactivity fact and remain UNKNOWN rather than being promoted from M10 activity facts. A separate `metal_liquid_water_hydrogen` decision domain is structurally and semantically distinct from M10's acid-displacement domain, so no synthetic rule relationship or priority is added.

Steam/hot-water chemistry, calcium, passivation, activity-series ordering, variable valence, oxidation states, half-reactions, electron balancing, and general metal/water or redox inference remain deferred.

## ADR-M12-001 — Per-family Relation cardinality and exact-target applicability

M12 generalizes Relation contract metadata only as far as the new family requires. `metal.product_cation` remains `one_target_per_context`: a source metal cannot declare different product-cation targets under the same normalized context. `metal.displaces_cation` is `many_targets_per_context`: the same source/context may name distinct positive-ion targets, while an exact duplicate source/key/target/context assertion remains invalid. Both relations retain the bounded elemental-metal Substance domain and positive-ion Species range. Context is structured assertion data, so aqueous truth is not encoded into the relation name.

Rule applicability gains only an exact-target, one-hop Relation predicate using `equals expected: true`. It requires one valid source binding, one controlled relation key, and one canonical target ID satisfying the relation range. A matching assertion is known true; no match is ABSENT/UNKNOWN rather than false. Equally specific assertions for the same target are combined deterministically with merged evidence. The proof event retains source/key/target/context/evidence, and only assertions belonging to the finally applicable binding enter candidate provenance.

This source change advances source schema to `3.4.0`; the new predicate source shape advances Rule DSL to `1.3.0`; `PredicatePlan.target_id` advances RulePlan to `1.3.0`; and its external serialization advances artifact format to `1.4.0`. The reference reader continues to accept artifact formats `1.0.0` through `1.3.0`.

## ADR-M12-002 — CuSO4-bounded reusable metal displacement

M12 represents canonical Cu2+, CuSO4, ZnSO4, and MgSO4 with exact composition, charge, salt/sulfate classifications, and evidence-backed aqueous complete-dissociation profiles. Elemental Zn and Mg own positive aqueous `metal.displaces_cation -> Cu2+` assertions. Cu, Na, and K receive no inferred or authored displacement relation; missing pairwise knowledge remains open-world UNKNOWN, including where competing aqueous chemistry is outside the model.

One Rule matches a generic solid classified metal plus exact aqueous CuSO4 and gates applicability on the displacement Relation. The product sulfate is built exclusively by the existing generic `ionic_pair` path: the incoming cation comes from `metal.product_cation`, and sulfate comes from CuSO4 canonical speciation. Existing elemental Cu is the exact second product. Exact balancing derives `1:1:1:1`; complete ionic projection dissociates only CuSO4 and ZnSO4/MgSO4; sulfate cancels to `Zn + Cu2+ -> Zn2+ + Cu` or `Mg + Cu2+ -> Mg2+ + Cu`.

The dedicated `aqueous_copper_salt_displacement` decision domain has no static overlap with existing families, so no synthetic relationship or priority is authored. M12 deliberately does not add formula parsing, valence guessing, product fabrication, reverse or chained Relation traversal, a numeric activity series, electrode-potential execution, oxidation-number inference, a general redox engine, or arbitrary metal-salt target resolution.

## M12 remaining limitations

General metal A + salt of metal B inference still requires evidence-driven salt-cation discovery, ion-to-element resolution, pairwise or ordered activity semantics, displaced-metal construction, aqueous water-competition handling, variable valence, passivation, and concentration/temperature effects. These remain later design pressures rather than hidden M12 behavior.

## Coverage decision — M13 silver-nitrate reuse proof

The bounded silver-nitrate slice demonstrates that M12's existing Relation semantics are reusable in canonical data. Elemental Zn and Mg each own distinct aqueous `metal.displaces_cation` targets for Cu2+ and Ag+, while `metal.product_cation` remains one-target per context and exact duplicate displacement assertions remain invalid. Existing Ag, Ag+, and AgNO3 IDs are retained; historical fixture evidence remains as provenance, and OpenStax Chemistry 2e evidence now supports the silver identities, nitrate solubility/strong-electrolyte treatment, aqueous AgNO3 speciation, and bounded Zn/Mg displacement assertions.

One exact-AgNO3 Rule uses the unchanged exact-target Relation predicate, unchanged relation-derived cation source, unchanged speciation-derived anion source, and unchanged canonical `ionic_pair` resolver. It selects existing Zn(NO3)2 or Mg(NO3)2 and exact elemental Ag; the balancer derives `1:2:1:2`, and derived ionic forms cancel nitrate. No entity is fabricated and no Ag-specific compiler path is introduced.

Ag, Na, K, and Cu receive no synthetic Ag+ displacement assertions in this slice. Their AgNO3 cases remain open-world UNKNOWN, preserving water-competition and variable-valence pressure for later work. The compatibility coordinates remain source schema `3.4.0`, Rule DSL `1.3.0`, RulePlan `1.3.0`, and artifact format `1.4.0`.

## ADR-M15-001 — Bounded salt/strong-base exchange without a metal-salt facet

M15 adds one Rule in the existing `aqueous_exchange` decision domain. It requires an aqueous salt with known soluble and strong-electrolyte facts plus an aqueous classified base with known strong-base and strong-electrolyte facts. The unchanged `ionic_exchange.driving_force` predicate uses both canonical speciation profiles and requires exactly one known-insoluble exchange product and one known-soluble counterproduct; unchanged `exchange_product` constructors then return those existing canonical identities. The salt/strong-base participant pattern is declared mutually exclusive with the existing two-salt precipitation pattern. If future source data makes both patterns applicable, rule resolution reports ambiguity rather than selecting by order.

A corpus-wide audit found that `classification.metal_salt` would apply to nearly all existing non-ammonium salts and would require broad historical reclassification without adding the knowledge actually consumed by M15. It is therefore not introduced as a Rule-gating convenience. Metal-ion identity comes only from the selected salt's evidence-backed complete-dissociation profile. FeCl3 names exact canonical Fe3+; no elemental-iron, formula-derived, valence-selection, reverse-relation, or graph-traversal path exists.

Cu(OH)2, Mg(OH)2, and Fe(OH)3 are canonical insoluble Substances with no fake aqueous speciation. Missing product identity or `solubility.class`, missing aqueous medium, non-aqueous input phase, and unsupported salts remain UNKNOWN or non-matching. The existing projector derives complete and net ionic forms and cancels only canonical spectators. No amphoteric dissolution, excess-OH-, complex-ion, Ksp, weak-base, equilibrium, or redox semantics are implied.

The Rule and data compose existing contracts, so source schema remains `3.4.0`, Rule DSL and RulePlan remain `1.3.0`, and artifact format remains `1.4.0`.

## ADR-M16-001 — Controlled heated value with an exact CaCO3 pilot

M16 adds `heated` to the controlled `temperature_regime` vocabulary as a value distinct from `warmed`; it does not introduce ordering, numeric temperature, or an implication between the two regimes. The existing generic scalar context/condition execution already provides the required three-valued behavior: missing temperature is UNKNOWN, a different known regime is FALSE, and an exact match carries canonical condition evidence into comparison and provenance. No heated-specific runtime branch is added.

One exact declarative Rule matches only solid canonical CaCO3 under `heated` and selects exact canonical CaO(s) plus existing CO2(g). The exact balancer derives `1:1:1`, conservation validators remain unchanged, and the canonical Reaction deliberately owns no ionic forms. CaO is the only new Entity; CaCO3, CO2, Ca, C, and O are reused.

The Rule does not classify or dynamically map carbonates to oxides. MgCO3 under `heated` remains unsupported, and generic carbonate, bicarbonate, nitrate, catalyst, steam, kinetics, equilibrium, and redox behavior remain deferred because substrate-derived product selection has no current semantic owner.

Admitting `heated` changes the source contract, so source schema advances from `3.4.0` to `3.5.0`. Rule source syntax, lowered RulePlan shape, and emitted artifact shape are unchanged; Rule DSL and RulePlan therefore remain `1.3.0`, and artifact format remains `1.4.0`. `compiler/source.py` changes only its source-schema compatibility coordinate; compiler behavior does not change.

## ADR-M18-001 — Steam as gaseous canonical H2O plus heated context

M18 represents steam with the existing canonical H2O identity authored as a gas-phase reactant together with `temperature_regime = heated`. It does not create a steam Substance, add a `steam` condition value, or equate heated liquid water with gaseous water. Existing generic participant-phase matching rejects H2O(l), while generic scalar context evaluation preserves known FALSE for `ambient`/`warmed` and UNKNOWN for a missing temperature.

One exact declarative Rule binds only elemental Mg(s) and H2O(g), then selects canonical MgO(s) and H2(g). MgO is the only new Entity. The Rule does not use Mg's aqueous `metal.product_cation` Relation, does not add or overload `metal.water_reactivity`, and does not construct oxides dynamically. Exact balancing derives `1:1:1:1`; atom and charge conservation remain structural validation rather than general redox inference; the canonical Reaction owns no ionic forms.

This bounded phase/pathway proof changes no compiler, schema, Rule DSL, RulePlan, or artifact contract. Hot liquid water, phase-transition semantics, generic metal + steam inference, other metal/steam pathways, oxide selection, and redox prediction remain outside M18.

## ADR-M19-001 — Bounded typed entity sources own generic displacement indirection

M19 introduces one `EntitySourcePlan` shared by dynamic Relation-predicate targets and source-derived products. Its closed forms are exact canonical entity, bound participant, unique positive/negative ion from a context-matching canonical speciation profile, and one Relation target whose source is one of the non-Relation forms. Relation-to-Relation nesting is rejected, so this is not recursive traversal or a query language.

The sole active aqueous metal-salt displacement Rule binds a generic solid metal and aqueous salt. The salt's canonical speciation supplies the displaced cation dynamically; the incoming metal must own an exact evidence-backed `metal.displaces_cation` assertion to that cation. Missing or ambiguous speciation and missing pairwise assertions remain UNKNOWN. `metal.product_cation` plus the unchanged `ionic_pair` constructor selects the incoming metal salt, so formulas and valence are never guessed.

The controlled `ion.elemental_substance` Relation maps a positive ion Species to one canonical elemental-metal Substance and has `one_target_per_context` cardinality. M19 authors only the required Cu2+ -> Cu and Ag+ -> Ag mappings. The displaced product follows exactly one such Relation hop, preserves the consumed speciation/assertion evidence, and never performs reverse inference.

The exact active M12 CuSO4 and M13 AgNO3 Rules are retired because the repository has no deprecation/alias mechanism and retaining them would duplicate semantics. Their Entity IDs, Reaction IDs, evidence, fixtures, TeachingView coverage, and historical ADRs remain. One M19 Rule now covers CuSO4, AgNO3, and CuCl2 for the authorized Zn/Mg pairwise facts. Activity ranking, transitivity, explicit known-negative ownership, water competition, variable valence, passivation, concentration effects, and general redox inference remain deferred.

These source, DSL, lowered-plan, and emitted-plan additions advance source schema to `3.6.0`, Rule DSL and RulePlan to `1.4.0`, and artifact format to `1.5.0`. The reference reader intentionally retains formats `1.0.0` through `1.4.0`.
