# Architecture

Status: **F1 Architecture Master**

## 1. Purpose

HS-Chemistry-Knowledge-Compiler is a source-to-artifact knowledge system for high-school chemistry. It preserves stable chemistry identity, explicit semantics, context, evidence, and deterministic derivation while keeping curriculum organization and runtime layout from becoming the domain model.

The repository replaces `chem-knowledge-data`; legacy data may be migrated through adapters but does not constrain the canonical model.

## 2. Layer boundaries

```text
identity-bearing records
+ assertions / facets / relations
+ canonical reactions
+ teaching views
+ evidence
+ declarative rules
        │
        ▼
canonical source contracts
        │
        ▼
compiler
parse → schema validate → semantic validate → resolve → normalize
→ rule analysis → infer → construct products → resolve identities
→ balance → atom/charge validate → canonical compare → proof trace
        │
        ▼
deterministic external artifacts + internal runtime plans
```

External generated artifact schemas are owned by Data Contracts. Internal `RulePlan`, indexes, caches, operator lowering, and runtime layout are owned by Compiler.

## 3. Identity model

### 3.1 Identity-bearing chemical records

`Entity` is an envelope for stable chemical/material identity. Canonical `entity_kind` values are:

```text
element
species
substance
material_system
```

`Species` carries a shallow `species_kind` such as `atom`, `ion`, `molecule`, or another curriculum-justified microscopic kind. `Ion` therefore never competes with `Species` as a peer identity kind.

`Substance` means a macroscopic pure material identity capable of carrying bulk properties, preparations, uses, and phase-qualified observations.

`MaterialSystem` means a composed sample/system whose composition or experimental state matters. `Solution` and `Mixture` are `material_system_kind` values. Concentration does not create a new species and normally does not create a new identity unless the material system itself is curated as a reusable referent.

### 3.2 Non-chemical identity-bearing records

The F1 source model also permits stable IDs for objects whose independent lifecycle requires durable reference, including:

- `Structure`;
- `Reaction`;
- `Experiment` when a reusable procedure/design is curated;
- `TeachingView`;
- `Rule`;
- `Source` and `Evidence`;
- independently curated assertions/relations when their provenance or revision lifecycle requires it.

A durable ID is not required merely because a value can be normalized into its own table.

## 4. Structure boundary

`Structure` is the canonical owner of a stable structural model. It is not a SMILES string, Lewis drawing, image, or file asset.

A structure may contain:

- nodes/constituents;
- embedded bond components;
- connectivity and geometry facts;
- structural motif / functional-group links;
- representations such as SMILES, InChI, Lewis, crystal description, or asset references.

`Bond` is an embedded component by default and uses a structure-local key. F1 does not mint a top-level bond UUID solely for graph normalization. A later top-level bond identity is allowed only if bond-local evidence, revision, or external durable reference requires an independent lifecycle.

Functional groups are reusable motif/facet vocabulary concepts linked to structures/species; they are not substances.

## 5. Source normalization policy

Canonical authoring should be human-reviewable, diff-friendly, schema-validatable, and practical to edit.

The following are **embedded value objects by default**:

| Object | F1 source role |
| --- | --- |
| Composition | embedded exact composition on the owning species/substance/structure where applicable |
| Context | embedded structured qualifier bundle on a claim/reaction/form; context dimensions use controlled vocabularies |
| ReactionParticipant | embedded value object inside `Reaction` / `ReactionForm` |
| Condition | embedded value object inside reaction/rule scope |
| TeachingViewPath | embedded node/path inside a `TeachingView`; its path key is a view-local locator |
| Bond | embedded structure component with a structure-local key |

`FacetAssertion` is a canonical assertion only when it is an authored/evidenced claim with an independent provenance/revision lifecycle. Compiler-derived facet memberships are generated artifacts, not source records.

This policy prevents UUID-heavy source data while still allowing durable references where justified.

## 6. Fact semantics

A claim distinguishes:

- `intrinsic`;
- `contextual`;
- `derived`.

Value state distinguishes:

- no assertion present;
- explicit `unknown`;
- `not_applicable`;
- known value, including known boolean `false`.

Missing data is never coerced to false. Context-dependent claims cannot be flattened into unconditional attributes.

## 7. Reaction model

### 7.1 Canonical Reaction

A `Reaction` is one curated chemical transformation under a declared semantic boundary. It owns stable reaction identity, canonical participants, conditions/constraints, classifications, evidence, and related forms.

Reaction identity does not depend on equation text, participant ordering, coefficient scaling, or teaching placement.

### 7.2 ReactionForm / ReactionRepresentation

`ReactionForm` is an embedded or child representation/projection of the same reaction transformation. It may express:

- molecular equation;
- complete ionic equation;
- net ionic equation;
- thermochemical equation;
- other notation projections that preserve the same underlying transformation.

A form may use different referent levels from the canonical reaction, but must carry a derivation/projection basis when it is computed rather than authored.

Scaling an equation does not create a new reaction. Quantities such as reaction enthalpy are interpreted relative to the chosen stoichiometric extent/form multiplier.

### 7.3 Distinct related reactions

Chemically distinct transformations remain distinct `Reaction` records even when their equations are related. In electrochemistry, oxidation and reduction half-reactions are separate reactions related to an overall cell reaction by typed composition relations such as `component_of` / `composes`.

## 8. Reaction referent levels

Reaction participants may refer to:

- `Species` for microscopic ionic/molecular transformations;
- `Substance` for pure macroscopic materials;
- `MaterialSystem` when solution/mixture composition or experimental system identity matters.

A participant carries an explicit referent level or its target type makes that level unambiguous.

Molecular/ionic forms may project between levels using declared speciation/dissociation assumptions. `NaCl(s)` is never modeled as a fictional NaCl molecule merely to make equation syntax convenient.

## 9. ReactionCandidate lifecycle

Pure compilation must not mint time-based IDs.

A generated candidate has a deterministic `candidate_key` derived from canonicalized semantic content, relevant rule identity/version, and declared inference inputs. Repeated compilation of identical input produces the same candidate key.

If a candidate enters a persistent human review/curation workflow, a durable `rcand_*` ID may be minted for the review object. That review record retains the immutable deterministic `candidate_key`. Promotion to canonical knowledge creates or edits an `rxn_*` record; it never mutates the generated candidate into a canonical reaction.

## 10. Rule identity

The declarative `Rule` definition is the sole canonical owner of stable `rule_*` identity, semantic version, evidence, and resolution relationships.

There is no separate canonical `RuleReference` record. Other records contain scalar/reference values such as `rule_id` plus optional required version constraints.

## 11. Teaching views

Teaching views project canonical chemistry knowledge. They can group, order, annotate, simplify, and cross-link canonical objects for D01-D11 or later curricula.

A `TeachingView` has stable identity. Its path nodes are embedded and view-local. A path can change without changing chemistry identity.

## 12. Source and generated boundary

Editable canonical source is expected under areas such as:

```text
knowledge/domain/**
knowledge/teaching/**
knowledge/rules/**
schemas/**
```

Generated artifacts may be more normalized or denormalized than source data. Runtime dense IDs, database rows, graph edges, indexes, caches, and compiled rule plans are disposable/reproducible representations.

## 13. Canonical owner map

| Concern | Owner |
| --- | --- |
| Cross-workstream architecture | `docs/ARCHITECTURE.md`, `docs/DECISIONS.md` |
| Ontology meaning | `docs/domain/ONTOLOGY.md` |
| Teaching model | `docs/pedagogy/PEDAGOGY.md` |
| Source/external artifact contracts | `docs/contracts/**` |
| Inference semantics / runtime plan | `docs/inference/**` |

## 14. Representative consistency cases

### Fe element vs Fe(s)

`Element(Fe, Z=26)` is the element concept. Bulk iron is a `Substance`. Fe atoms, ions, and bulk iron do not share one identity merely because they share the symbol Fe.

### NaCl crystal

Sodium chloride crystal is a `Substance` linked to an ionic `Structure` containing Na+ and Cl- constituents. `NaCl` is a formula-unit representation. No NaCl molecule entity is required.

### H2SO4

`H2SO4` molecular species is distinct from sulfuric-acid `Substance` and from a sulfuric-acid `MaterialSystem`/solution. Strong-acid/electrolyte behavior is contextual in aqueous media.

### SO2

SO2 identity is stable while oxidant/reductant behavior is represented as reaction/context-qualified role assertions.

### Ethanol

Ethanol species/substance link to a stable molecular `Structure`; hydroxyl is a structural motif/facet and alcohol classification may be asserted or deterministically derived.

### NaCl + AgNO3

The macroscopic aqueous precipitation reaction may have molecular, complete-ionic, and net-ionic `ReactionForm`s. Ag+ + Cl- → AgCl(s) is a microscopic projection of the same precipitation transformation when the projection assumptions are explicit.

### HCl + NaOH

The aqueous neutralization reaction may expose molecular and ionic forms; H+ + OH- → H2O is the net-ionic form under the declared strong-electrolyte aqueous model.

### Cu-Zn galvanic cell

The overall cell transformation is one `Reaction`. Zn oxidation and Cu2+ reduction are separate half-reaction `Reaction` records related to the overall reaction and to electrode/material-system context.
