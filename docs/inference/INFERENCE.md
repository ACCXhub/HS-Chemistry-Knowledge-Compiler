# Deterministic Reaction Inference Semantics

Status: **F1 canonical**

## 1. Input

An inference request identifies reactants/material systems, supplied context, and an inference scope. Input names/formulas are normalized to canonical candidates before rule execution; ambiguity must remain explicit.

## 2. Context construction

Construct a typed context from explicit request qualifiers plus only contract-approved defaults. Defaults must be deterministic and visible in the proof trace.

## 3. Hard blockers

Blockers represent conditions that make a decision domain inapplicable or unsafe to infer. They are evaluated before ordinary product inference when their semantics require it.

## 4. Matching

Rule matching uses canonical identity constraints, entity/species/material kinds, facets, typed relations, context predicates, and condition predicates.

UNKNOWN does not equal FALSE.

## 5. Product construction

Rules construct semantic product descriptors/queries, not display equation strings and not balancing coefficients.

Constructed products are resolved against canonical entity/structure semantics. Failure or ambiguity is explicit.

## 6. Postmatch tests

Driving-force or product-dependent tests that require resolved products belong after product construction. Validators validate a proposed chemistry state; they do not secretly choose product identity.

## 7. Resolution

If multiple rules survive, use explicit resolution relationships. Unrelated conflicting survivors are an error/ambiguity, not an invitation to pick by file order.

## 8. Balancing and validation

After products are fixed:

1. balance exactly;
2. validate atom conservation;
3. validate charge conservation where applicable;
4. run declared chemistry postconditions.

A failed candidate remains traceable; failures are not erased.

## 9. Canonical comparison

Compare the validated candidate against canonical `Reaction` signatures/forms. Comparison states may include none, exact, equivalent, ambiguous, and conflict.

The candidate remains generated even on exact match.

## 10. Proof trace

A proof trace must record at least:

- normalized inputs and resolutions;
- constructed context/defaults;
- blockers checked;
- rules considered and match outcomes;
- UNKNOWN dependencies;
- exceptions/overrides/resolution edges used;
- product construction/resolution;
- balancing result;
- atom/charge validation;
- postconditions;
- canonical comparison;
- rule/version/evidence provenance;
- compiler/source revision.

## 11. Representative semantics

### Precipitation

Aqueous NaCl + AgNO3 may normalize to material/substance participants, project to ionic species under declared strong-electrolyte assumptions, infer AgCl(s) formation, and expose molecular/ionic/net-ionic forms for the same precipitation reaction.

### Neutralization

HCl + NaOH under the declared aqueous strong-electrolyte model can project to H+ + OH- → H2O as a net-ionic form. The projection assumptions must be traceable.

### Electrochemistry

For a Cu-Zn galvanic system, the overall cell reaction and the two half-reactions are separate related canonical reactions. Rule execution may reason about electrode/material-system context without collapsing all three into one equation representation.
