# F3B Aqueous Chemistry Pilot Audit

Starting canonical main: `8d92d19b8ebbbcb0f8a9fdaceb7eb895da381447`

Branch: `workstream/f3b-aqueous-chemistry-pilot`

## Curated scope

F3B adds a small real aqueous inorganic corpus around three transformations:

1. `BaCl2(aq) + Na2SO4(aq) -> BaSO4(s) + 2 NaCl(aq)` — precipitation.
2. `HNO3(aq) + KOH(aq) -> KNO3(aq) + H2O(l)` — strong acid/base neutralization.
3. `HCl(aq) + NaHCO3(aq) -> NaCl(aq) + CO2(g) + H2O(l)` — hydrogen-carbonate + acid gas evolution.

Each reaction is one canonical `Reaction` with authored molecular, complete-ionic, and net-ionic `ReactionForm` projections. Generated inference candidates are audit outputs only.

The pilot also adds the minimal ion/compound set required by those forms, plus an explicit HCl identity pressure test:
`HCl molecule (Species)` / existing hydrogen-chloride `Substance` / `hydrochloric-acid aqueous solution (MaterialSystem)`.

## Evidence

Canonical source record:

- OpenStax, *Chemistry 2e*.

Evidence scopes:

- Section 4.2, “Classifying Chemical Reactions”: precipitation, common aqueous solubility rules, AgCl/BaSO4 examples, molecular/net-ionic representations.
  https://openstax.org/books/chemistry-2e/pages/4-2-classifying-chemical-reactions
- Section 14.3, “Relative Strengths of Acids and Bases”: HNO3 as a common strong acid and KOH as a common strong base in water.
  https://openstax.org/books/chemistry-2e/pages/14-3-relative-strengths-of-acids-and-bases
- Section 18.6, “Occurrence, Preparation, and Properties of Carbonates”: hydrogen carbonates/carbonates reacting with acids to produce CO2 and water.
  https://openstax.org/books/chemistry-2e/pages/18-6-occurrence-preparation-and-properties-of-carbonates

The source is used as an authoritative educational chemistry reference. Evidence records are claim-scoped rather than repeated on every structural atom-count field.

## Canonical additions

### Entities

20 entities:

- Elements: C, S, K, Ba.
- Species: HCl molecule; Na+, K+, Ba2+, NO3-, SO4^2-, HCO3-.
- Material system: hydrochloric-acid aqueous solution.
- Substances: BaCl2, Na2SO4, BaSO4, HNO3, KOH, KNO3, NaHCO3, CO2.

25 facet assertions cover the bounded pilot classifications/behaviors, including acid/base/salt, strong-electrolyte-in-water, soluble/insoluble-in-water, and hydrogen-carbonate classification.

### Reactions

- `rxn_f3b_baso4_precipitation`
- `rxn_f3b_hno3_koh_neutralization`
- `rxn_f3b_hcl_nahco3_gas_evolution`

Each contains `molecular`, `complete_ionic`, and `net_ionic` forms with explicit projection assumptions.

### Teaching view

`view_f3b_hs_aqueous_core` reuses canonical entities/reactions across:

- D02 electrolyte solutions
- D03 reaction types
- D06 notation / ionic equations
- D08 substance classification
- D10 elements and compounds

No chemistry identity is duplicated per teaching path.

## No-net-reaction contrast

Audit case: aqueous NaCl + KNO3.

Under the bounded common-solubility teaching model, the exchange pairings remain soluble and no canonical transformation is authored. This is deliberately treated as a contrast/audit case, not as a universal `false` reaction fact. The current F2 inference engine returns `no_match`, which is not promoted to canonical negative knowledge.

## F2 inference coverage

The current F2 rules are exact-identity demonstration rules, not reusable chemistry-family rules.

Observed/expected audit matrix:

| Case | F2 result | Canonical coverage |
| --- | --- | --- |
| NaCl + AgNO3 | `inferred` | exact `rxn_agcl_precipitation` |
| HCl + NaOH | `inferred` | exact `rxn_hcl_naoh_neutralization` |
| BaCl2 + Na2SO4 | `no_match` | curated F3B reaction exists |
| HNO3 + KOH | `no_match` | curated F3B reaction exists |
| HCl + NaHCO3 | `no_match` | curated F3B reaction exists |
| NaCl + KNO3 contrast | `no_match` | intentionally no canonical reaction |

The three F3B reactions therefore expose missing reusable matching/operator capability rather than chemistry errors.

## Legacy migration comparison

Relevant legacy material was inspected only after the new records were designed.

Directly reusable chemistry content:
- legacy `barium-chloride`, `barium-sulfate`, `carbon-dioxide` composition/name content;
- legacy `bacl2-na2so4` reaction stoichiometry and net-ionic chemistry;
- legacy AgNO3 + NaCl precipitation record as a chemistry cross-check.

Needs identity reconciliation:
- legacy records use IDs such as `substance:barium-chloride` and `ion:barium`; none are preserved as canonical IDs.
- equation-oriented `species_id` fields do not determine the new referent level.

Needs split/re-modeling:
- legacy substance rows combine `category`, `ambient_phase`, `aqueous_behavior`, and ion lists on one record.
- the new model separates stable substance identity, microscopic ion species, contextual/faceted claims, and teaching projection.

Classification paths that become facets/TeachingViews:
- legacy `category: salt/base/acid` and teaching-priority organization are migration material, not inheritance or identity.

Flattened context:
- legacy `aqueous_behavior: strong_electrolyte|insoluble` is useful chemistry content but flattens solvent/conditions.
- F3B uses bounded `..._in_water` facet keys only because F2 has no structured context field on facet assertions; this is recorded below as a contract pressure point.

Legacy reactions:
- `reaction:bacl2-na2so4` and `reaction:agno3-nacl` are useful cross-check/reference material.
- they are not bulk-imported and their legacy IDs/shapes are not preserved.

## Architecture pressure points

### 1. Structured context missing from F2 facet assertions

Concrete example:
`BaSO4` insolubility and HNO3/KOH strong-electrolyte behavior are claims about water/aqueous conditions.

Current limitation:
F1 describes structured `Context`, but the F2 record schema gives embedded facet assertions only `facet_key`, `value_state`, `value`, `evidence_ids`.

Current bounded representation:
`solubility.insoluble_in_water`, `electrolyte.strong_in_water`.

Minimal proposed change:
allow a structured `context` object on facet/property assertions without encoding context dimensions into facet-key strings.

Owner:
F3A / F3 convergence contracts.

### 2. TeachingView is canonical in F1 but absent from the F2 executable source contract

Concrete example:
the same precipitation reaction should appear under D03 and D06 without duplicate chemistry identity.

Current limitation:
F2 source traversal reads only `knowledge/domain` and `knowledge/rules`; `f2-record.schema.json` accepts no `teaching_view`.

F3B action:
author `knowledge/teaching/f3b_aqueous_views.yaml` in the canonical architecture location and validate its members in F3B tests, without changing the F3A-owned compiler/schema.

Minimal proposed change:
add TeachingView source schema + loader/index/reference validation.

Owner:
F3A/F3C convergence depending final ownership split.

### 3. MaterialSystem composition/speciation is too weak for reaction participants

Concrete example:
hydrochloric acid aqueous solution is a `MaterialSystem`, while balancing requires the chemical HCl stoichiometric unit.

Current limitation:
the F2 `material_system` payload can identify a solution but cannot represent solute/solvent/speciation composition, and the balancer requires exact elemental composition on each participant.

F3B action:
curate the HCl `Species` / existing `Substance` / aqueous `MaterialSystem` identities distinctly, but retain the substance-level HCl participant for the current molecular reaction.

Minimal proposed change:
define how a reaction participant referring to a MaterialSystem projects to stoichiometric/speciation participants for balancing/ionic forms.

Owner:
F3C convergence, coordinated with F3A ReactionForm operators.

### 4. Rule matching is exact-ID, not reusable/faceted

Concrete example:
F2 can infer HCl + NaOH but not the chemistry-equivalent HNO3 + KOH neutralization; it can infer AgCl fixture precipitation but not BaSO4 precipitation.

Current limitation:
each F2 rule binds exact `target_id` values before facet predicates.

Minimal proposed change:
support reusable typed/faceted reactant patterns and product construction/resolution without relaxing deterministic proof traces.

Owner:
F3A.

### 5. Complete-ionic projection is authored, not compiler-derived

Concrete example:
BaCl2 + Na2SO4 needs spectator-ion expansion and cancellation.

Current limitation:
F2 stores ReactionForms but does not provide a general speciation/dissociation projection operator.

Minimal proposed change:
explicit projection/speciation operator(s) with assumptions and evidence/context requirements.

Owner:
F3A/F3C convergence.

## Validation

F3B test coverage is designed to prove:

- durable IDs/references resolve through the existing F2 loader;
- ion formal charge equals composition net charge;
- key formula compositions are exact;
- the three canonical reactions balance;
- every authored molecular/complete-ionic/net-ionic form conserves atoms and charge;
- semantic keys do not collide;
- evidence refs resolve, including facet assertion evidence;
- TeachingView members resolve to canonical entity/reaction IDs;
- F2 inference coverage audit executes;
- generated candidates retain deterministic candidate keys and never become `rxn_*` source records.

No generated candidate is promoted automatically.

## Convergence status

`READY_FOR_F3_CONVERGENCE`

The corpus is intentionally small. Its value is the pressure-test evidence: real aqueous chemistry fits the identity/reaction model, while structured contextual assertions, TeachingView executable support, MaterialSystem reaction projection, reusable faceted rules, and derived ionic forms need convergence work.
