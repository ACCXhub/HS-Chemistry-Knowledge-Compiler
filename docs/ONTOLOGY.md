# Canonical Domain Ontology

Status: **canonical architecture foundation for the new compiler**

This document defines the semantic boundary of the HS-Chemistry-Knowledge-Compiler. It replaces the architectural assumptions of the legacy `chem-knowledge-data` project; legacy schemas are migration/reference material only.

The ontology is deliberately **not** a textbook chapter tree. It models stable chemical referents and independent semantic dimensions, then allows curriculum and teaching views to project those facts in different ways.

## 1. Design goals

The ontology must support, without class explosion:

- stable identity for chemical referents;
- faceted classification;
- intrinsic, contextual, and derived facts;
- explicit semantic relations;
- canonical reactions as knowledge entities;
- future deterministic inference without embedding rule execution semantics here;
- experiments, observations, and evidence;
- curriculum/pedagogical projections;
- macro / micro / symbolic explanation;
- provenance and explainability.

A concept is added only when it materially improves classification, inference, explanation, curriculum coverage, or long-term extensibility.

## 2. Core modeling rule

Prefer **shallow identity kinds + independent facets + qualified assertions** over deep inheritance.

For example, `H2SO4` does not need a class such as `StrongOxyDiproticAcid`. Instead, separate assertions can state that it:

- belongs to the chemical class `acid`;
- is oxygen-containing;
- has a maximum acidic-proton capacity of 2 under the intended acid model;
- is classified as a strong acid in aqueous high-school chemistry contexts;
- behaves as a strong electrolyte in the relevant aqueous context;
- can exhibit oxidizing behavior only under qualifying conditions such as sufficiently concentrated acid and an appropriate reaction partner.

The last three statements are not unconditional identity facts.

## 3. Semantic categories

| Category | Meaning | Typical examples |
| --- | --- | --- |
| **Entity** | An identity-bearing domain referent that can be the subject/object of relations and provenance. | Element, Species, Substance, Solution, Structure, Reaction, Experiment |
| **Facet** | An independent classification dimension or reusable class/role term. | metal, oxide, acid, alcohol, strong-electrolyte-in-water, redox reaction |
| **Property** | A typed value-bearing assertion about an entity. | atomic number, formula, charge, melting point, concentration, rate |
| **Relation** | A typed semantic edge between referents. | has structure, contains element, conjugate base of, participates in |
| **Context** | A qualifier bundle under which a fact is valid. | phase, solvent, temperature, concentration regime, atmosphere, catalyst |
| **View** | A projection for teaching/curriculum/reasoning. It does not change domain truth. | D01 kinetics/equilibrium view, D08 substance-classification view |
| **Derived concept** | A result recomputed or inferred from canonical facts and context. | molar mass, ionic equation projection, limiting reagent role, periodic trend |

A shallow `is-a` hierarchy is allowed when it expresses an identity-defining kind. Facets are preferred when multiple dimensions can overlap independently.

## 4. Entity boundary

### 4.1 `ChemicalEntity`

`ChemicalEntity` is the umbrella for identity-bearing chemical referents. It is intentionally broad enough for high-school chemistry but narrower than “anything mentioned in chemistry”.

Recommended shallow kinds:

```text
ChemicalEntity
├─ Element
├─ Species
│  ├─ Atom
│  ├─ Ion
│  ├─ Molecule
│  └─ Radical / other distinguishable microscopic species when needed
├─ Substance
└─ MaterialSystem
   ├─ Mixture
   └─ Solution
```

This tree is about **identity kind**, not textbook classification.

### 4.2 `Element` — Entity

An `Element` is the chemical-element concept identified by atomic number, for example iron (`Fe`, Z=26).

Intrinsic/derived data may include:

- atomic number;
- symbol;
- relative atomic mass (with version/source caveats where needed);
- periodic-table position;
- electronic-structure descriptors;
- element-family facets such as metal/nonmetal or alkali metal when useful.

Do not attach the properties of bulk elemental iron directly to the `Element` concept. Magnetic behavior, phase, color, density, and reactions generally belong to a `Substance` or context-qualified assertion.

### 4.3 `Species` — Entity

A `Species` is a chemically distinguishable microscopic species used as a participant in composition, reaction, structure, and symbolic reasoning.

Examples:

- `Fe` atom;
- `Na+` ion;
- `SO4^2-` ion;
- `H2SO4` molecule;
- `SO2` molecule;
- `C2H5OH` molecule.

`Atom`, `Ion`, and `Molecule` are shallow identity kinds of `Species`.

A formula string is **not** the species itself. Formula, charge notation, Lewis formula, structural formula, and SMILES-like encodings are representations of a species.

For ionic solids, do not invent a discrete molecule merely because a formula unit is written. `NaCl` in a crystal is modeled as a `Substance` with ionic `Structure`, constituent ions, and a symbolic formula unit `NaCl`; there is no requirement for a standalone `NaCl molecule` entity.

### 4.4 `Substance` — Entity

A `Substance` is a macroscopic pure chemical material whose identity is stable enough to carry bulk properties, phases, preparations, uses, and experimental observations.

Examples:

- sulfuric acid;
- sulfur dioxide;
- iron;
- sodium chloride;
- ethanol.

A `Substance` links to the microscopic species and/or extended structure that explains it. This separation is critical for macro/micro explanation:

```text
Substance sodium chloride
  → has_structure → ionic crystal structure
  → has_constituent_species → Na+
  → has_constituent_species → Cl-
  → has_symbolic_representation → NaCl
```

### 4.5 `MaterialSystem`, `Mixture`, `Solution` — Entity when identity matters

A mixture or solution is an entity when a particular material system is itself the subject of composition, concentration, phase, experiment, equilibrium, or observation.

Examples:

- aqueous sodium chloride solution;
- sulfuric-acid solution;
- a colloidal dispersion used in an experiment.

Do not create a new ontology class for every recipe or concentration label. Composition and concentration belong to properties/context. “Concentrated sulfuric acid” is normally represented as sulfuric-acid material under a concentration-qualified context, not as a new chemical species or a new subclass of acid.

A `Solution` is a useful shallow kind of `MaterialSystem`; terms such as colloid/suspension may be represented by material-system facets unless a stable identity kind is needed later.

### 4.6 `Structure` — Entity

A `Structure` is a stable structural model that can be related to species or substances and can carry structural parts and properties.

Useful structure kinds include:

- atomic/electronic structure;
- molecular connectivity and geometry;
- ionic lattice;
- metallic structure;
- covalent/network structure.

`Structure` is not the same thing as a drawing. A Lewis diagram or ball-and-stick image is a representation of a structure.

### 4.7 `Bond` — structural component Entity

A `Bond` is an identity-bearing component of a `Structure` when bond-local facts are needed, such as:

- connected atoms;
- bond order;
- polarity;
- bond length;
- bond-energy reference data;
- participation in structural transformations.

For simple traversal, `bonded_to` may be exposed as a derived relation from bond entities. Keeping a bond entity prevents later property data from being forced onto an anonymous graph edge.

### 4.8 `Reaction` — Entity

A canonical chemical reaction is an identity-bearing knowledge entity because it can have:

- participants and stoichiometry;
- conditions;
- multiple independent reaction-class facets;
- equations/ionic-equation representations;
- thermochemical and equilibrium quantities;
- experiments and evidence;
- provenance.

This document does **not** define reaction-rule execution, matching, balancing algorithms, or runtime inference semantics.

### 4.9 `Experiment` — Entity

An `Experiment` is a reusable, identity-bearing experimental design or canonical procedure when the compiler needs to connect:

- purpose;
- substances/material systems;
- controlled conditions;
- operations;
- expected observations;
- evidence for a claim.

Fine-grained laboratory workflow schemas are outside this ontology foundation.

### 4.10 `Phenomenon` / observation — usually contextual knowledge, not a root entity

Most “phenomena” in high-school chemistry are better represented as context-qualified observations/assertions attached to a reaction or experiment:

- gas evolves;
- precipitate forms;
- solution changes color;
- solid dissolves;
- temperature changes.

Reusable named phenomena such as the Tyndall effect may have a stable concept identifier, but the observed occurrence remains linked to its material system and context. Do not build a deep phenomenon taxonomy unless later coverage requires it.

## 5. Facet taxonomy

Facets are reusable classification dimensions. A referent can carry multiple facet values simultaneously.

### 5.1 Chemical-class facets

Typical dimensions include:

| Facet dimension | Illustrative values | Notes |
| --- | --- | --- |
| elemental character | metal, nonmetal, metalloid | Mainly on `Element` or elemental `Substance` |
| composition family | elemental substance, compound | Broad, shallow classification |
| inorganic family | oxide, hydride, acid, base, salt | Not forced into one inheritance chain |
| oxide behavior | acidic oxide, basic oxide, amphoteric oxide | May be derived/context-sensitive where appropriate |
| organic family | hydrocarbon, alcohol, phenol, aldehyde, ketone, carboxylic acid, ester, amine | Expand only to curriculum need |
| functional group | hydroxyl, carbonyl, carboxyl, ester, amino, C=C, etc. | Structural motif classification |
| electrolyte behavior | electrolyte, nonelectrolyte, strong, weak | Must carry medium/context where validity depends on it |
| acid/base role | Brønsted acid/base and later models if required | Role is contextual when solvent/partner matters |
| oxidation/reduction role | oxidant, reductant | Always attached to a reaction/context, never unconditional |

### 5.2 `FunctionalGroup` — Facet / structural motif concept

A functional group is not a separate chemical substance in this model. It is a reusable structural motif concept linked to a `Structure` or `Species` through relations such as `has_functional_group`.

Example:

```text
ethanol molecule
  → has_structure → ethanol molecular structure
  → has_functional_group → hydroxyl
  → chemical_class → alcohol
```

The `alcohol` class can be derived from structural criteria, while the functional group remains independently queryable.

### 5.3 `ChemicalClass` — Facet vocabulary, not a root entity hierarchy

`ChemicalClass` is the controlled vocabulary for classification assertions. Some parent/child organization inside the vocabulary is acceptable for navigation, but chemical entities should not be modeled by multiplying classes for every combination of facets.

### 5.4 `ReactionClass` — Facet vocabulary

Reaction classification is explicitly multi-axial. A single reaction may satisfy several independent facets.

Recommended dimensions include:

| Dimension | Values/examples |
| --- | --- |
| gross composition pattern | combination, decomposition, substitution, metathesis |
| electron transfer | redox, non-redox |
| proton / acid-base process | acid-base, neutralization |
| ionic driving process | precipitation, gas evolution, weak-electrolyte formation |
| combustion/process family | combustion and other named high-school process classes |
| organic transformation | substitution, addition, elimination, oxidation, reduction, esterification, hydrolysis, polymerization |

Do not force these into a single mutually exclusive tree. For example, one reaction can simultaneously be `redox` and `combustion`.

## 6. Property and fact model

A property is conceptually a typed assertion:

```text
subject + property/relation + value/object
        + fact_kind
        + optional context
        + provenance/evidence
        + optional derivation metadata
```

This is a semantic contract, not a persistence schema.

### 6.1 Intrinsic facts

Intrinsic facts remain true for the identified referent independent of ordinary experimental context.

Examples:

- atomic number of an element;
- elemental composition of a species;
- net charge of a canonical ion;
- canonical molecular connectivity;
- stoichiometric composition represented by a formula;
- identity of constituent elements.

### 6.2 Contextual facts

A contextual fact can change while the referent identity remains the same because conditions change. It must not be promoted to an unconditional property.

Common examples:

- phase;
- solubility;
- color when phase/speciation matters;
- electrical conductivity;
- acid/base strength in a solvent;
- electrolyte behavior;
- oxidizing/reducing behavior;
- reaction occurrence;
- reaction rate;
- equilibrium composition;
- equilibrium constant as a function of temperature;
- gas volume/density under stated T/P;
- experiment phenomenon.

Rule of thumb: **if changing conditions can change the truth value without changing the entity identity, require context**.

### 6.3 Derived facts

Derived facts are recomputable from canonical facts, context, and an explicit derivation method.

Examples:

- molar mass from composition and atomic-mass references;
- electron count from atomic number and charge;
- some chemical-class memberships from structure;
- oxidation-state assignments under a defined convention;
- stoichiometric mole ratios from a canonical balanced reaction;
- limiting/excess reagent roles in a particular calculation scenario;
- ionic-equation projection from a reaction plus speciation/medium assumptions;
- periodic trends as an ordering/projection over element properties.

Derived results should preserve their derivation/provenance rather than masquerading as independently curated intrinsic truth.

## 7. Context model

`Context` is a structured qualifier bundle, not a chemical entity. Context dimensions should be composable so that facts can be reused without creating classes such as `HotConcentratedSulfuricAcid`.

Recommended dimensions:

| Context dimension | Examples | Why it matters |
| --- | --- | --- |
| phase/material state | solid, liquid, gas, aqueous, dissolved species | reactions, properties, symbolic equations |
| solvent/medium | water, ethanol, molten state, acidic/basic medium | ionization, acid/base behavior, electrochemistry |
| concentration/composition | molarity, mass fraction, dilute/concentrated, saturated | kinetics, equilibrium, oxidizing behavior, observations |
| temperature | exact value or qualitative heating/cooling | rate, equilibrium, phase, solubility |
| pressure | exact/standard/high/low | gas properties, equilibrium, phase |
| pH / acidity / basicity | pH or qualitative regime | speciation and reactions |
| atmosphere | air, oxygen-rich, inert, chlorine, etc. | combustion/oxidation and experiment outcomes |
| reagent availability | excess, limiting, presence/absence | products and reaction path |
| catalyst | catalyst identity/presence | reaction rate/path |
| energy/stimulus | heat, light, electrical current | photochemistry, electrolysis, decomposition |
| material form | powder, wire, bulk, particle-size regime | rate and apparent reactivity |
| surface/electrode | electrode/material surface | electrochemistry and heterogeneous reactions |
| procedure | order of addition, mixing, duration where essential | experiment outcome and observation |
| system boundary | open/closed when relevant | equilibrium and gas systems |

Not every statement needs every dimension. Context is sparse: include only qualifiers needed to make the assertion correct and reusable.

## 8. Relation taxonomy

Use a small set of semantically clear relations. Reuse general relations such as `part_of`/`has_part` rather than creating many near-synonyms.

### 8.1 Identity / composition / structure

- `has_element` / `element_of`
- `has_structure`
- `has_part` / `part_of`
- `has_bond`
- `has_functional_group`
- `has_constituent_species`
- `has_component` (mixture/material-system composition)
- `dissolved_in` or equivalent solution relation when a stable relation is needed

### 8.2 Chemical semantic relations

- `is_conjugate_acid_of` / `is_conjugate_base_of`
- `is_isomer_of`
- `is_allotrope_of`
- `is_hydrate_of` when curriculum coverage requires it
- `corresponds_to_element` for elemental substances/species when useful

Add relations only when they express reusable domain semantics rather than one-off teaching wording.

### 8.3 Reaction participation

Represent the canonical reaction as the hub:

- `has_reactant`
- `has_product`
- `has_catalyst` where appropriate
- `participates_in`

Participant roles/stoichiometry/phase belong to the reaction knowledge model, but algorithmic balancing and rule execution are outside this document.

A convenience relation such as `reacts_with` should normally be **derived** from one or more canonical reactions plus context, because a bare unconditional `A reacts_with B` edge hides conditions and products.

### 8.4 Experiment / evidence

- `uses_substance`
- `uses_material_system`
- `tests_property`
- `observes`
- `supports_assertion`
- `demonstrates_relation`

These relations allow experiments to support explanation without turning laboratory chapter structure into ontology inheritance.

## 9. Quantity concepts

Quantities are needed for calculations, thermodynamics, kinetics, equilibrium, solutions, gases, and experiments.

Use:

- `QuantityKind` as a controlled semantic term, e.g. amount of substance, mass, molar mass, volume, concentration, pressure, temperature, pH, reaction rate, equilibrium constant, enthalpy;
- `QuantityValue` as a typed value with unit and uncertainty/conditions where relevant.

A numerical value is not a domain entity. It is the value of a property/assertion. Calculation formulas and algorithms belong to derived/reasoning layers, not the entity hierarchy.

## 10. Phase

`Phase` is primarily a **Context dimension**, not an entity and not a chemical class.

This prevents errors such as treating `H2O(l)` and `H2O(g)` as unrelated chemical identities. The underlying species/substance identity is linked to a phase-qualified state/participant.

Phase-specific thermodynamic data or reaction participants can therefore be represented without duplicating the core species.

## 11. Concepts that should remain derived

The following should not become primary ontology roots unless later evidence proves otherwise:

- `StrongOxyDiproticAcid`-style combined classes;
- “strong oxidizer” as an unconditional substance class;
- “active metal” as a timeless intrinsic class when defined by a curriculum activity series;
- periodic trends;
- activity-series ordering;
- ionic equations;
- limiting reagent / excess reagent roles;
- equilibrium position/state;
- reaction feasibility under a scenario;
- calculation templates;
- textbook chapter membership.

These are better represented as derived facts, contextual roles, or TeachingView projections.

## 12. Worked examples

### 12.1 H2SO4 / sulfuric acid

**Entities**

- `Element`: H, S, O
- `Species`: H2SO4 molecule; HSO4-; SO4^2-; H+ / hydron representation according to chosen aqueous model
- `Substance`: sulfuric acid
- optionally a `Solution` entity for a specific sulfuric-acid solution
- relevant molecular `Structure`

**Facets / properties**

- chemical class: acid
- structural/composition class: oxoacid / oxygen-containing acid
- acidic-proton capacity: 2, modeled as a structural/derived property under the selected acid model
- strong-acid classification: contextual, normally in aqueous curriculum context
- strong-electrolyte classification: contextual, in relevant aqueous solution context

**Relations**

- H2SO4 `has_structure` sulfuric-acid molecular structure
- H2SO4/HSO4-/SO4^2- linked by conjugate acid/base relations
- sulfuric acid `has_element` H, S, O

**Contextual behavior**

Do not state simply `sulfuric acid is a strong oxidizer`. Represent oxidizing behavior with a context including concentration regime, temperature if needed, and the reaction partner. Dilute acid reactions and concentrated-acid oxidations can then coexist without contradiction.

### 12.2 SO2 / sulfur dioxide

**Entities**: SO2 molecular species, sulfur-dioxide substance, molecular structure.

**Facets**:

- compound;
- oxide;
- acidic-oxide classification when justified by the high-school behavior model;
- sulfur oxidation-state information as a derived assignment.

**Contextual roles**:

SO2 can act as a reducing agent in one reaction and as an oxidizing agent in another. `reductant` and `oxidant` therefore belong to reaction/context-qualified role assertions, not to permanent species classes.

### 12.3 Fe / iron

**Entities**:

- `Element`: iron;
- `Species`: Fe atom, Fe2+, Fe3+ where relevant;
- `Substance`: metallic iron;
- metallic `Structure`.

**Facets/properties**:

- iron element: metal / transition-element facets as curriculum requires;
- atomic number and periodic position on `Element`;
- density, phase, color, magnetic/physical behavior on `Substance` under suitable context.

**Context**:

Reaction rate and apparent reactivity may depend on powder/wire form, temperature, atmosphere, acidity, and reactant concentration. Do not encode “Fe reacts with X” without the reaction/context that makes the claim valid.

### 12.4 NaCl / sodium chloride

**Entities**:

- `Substance`: sodium chloride;
- `Structure`: ionic crystal;
- `Species`: Na+, Cl-;
- `Solution`: aqueous sodium chloride solution when the material system is itself studied.

**Facets**:

- salt;
- ionic compound / ionic-solid structural classification;
- strong-electrolyte behavior only in the relevant aqueous/molten context.

**Important boundary**:

`NaCl` is a symbolic formula/formula unit for the solid; the ontology does not require a fictitious discrete NaCl molecule in the crystal. In aqueous solution, the microscopic participants are hydrated/dissolved ions according to the chosen level of detail.

### 12.5 Ethanol

**Entities**: ethanol molecular species, ethanol substance, molecular structure.

**Facets**:

- organic compound;
- alcohol;
- `has_functional_group` hydroxyl;
- additional independent structural facets only when instruction/inference needs them.

**Contextual properties**:

Phase, density, miscibility/solubility, combustion conditions, oxidation products, and experimental observations are qualified by temperature, pressure, partner, catalyst, etc. “Alcohol” remains a structural chemical class, while particular reaction behavior remains linked to canonical reactions and conditions.

## 13. Explicit decisions by requested concept

| Concept | Decision | Reason |
| --- | --- | --- |
| ChemicalEntity | **Entity umbrella** | Stable identity-bearing chemical referents |
| Element | **Entity** | Atomic-number identity; distinct from atom/substance |
| Atom | **Entity; Species subtype** | Microscopic chemical participant |
| Ion | **Entity; Species subtype** | Charge-bearing microscopic participant |
| Species | **Entity** | Canonical microscopic identity |
| Substance | **Entity** | Bulk/macroscopic chemical material |
| Mixture | **Entity; MaterialSystem subtype** | Composition/system-level facts need identity |
| Solution | **Entity; MaterialSystem subtype** | Solvent/solute/concentration/equilibrium facts |
| Structure | **Entity** | Stable structural model; separate from drawings |
| Bond | **Entity/component** | Bond-local properties and transformations |
| FunctionalGroup | **Facet / structural motif concept** | Independent reusable structural classification |
| Phase | **Context dimension** | Condition/state, not chemical identity |
| Property | **Typed assertion/value** | Avoid property-as-class modeling |
| ChemicalClass | **Facet vocabulary** | Multi-axial classification |
| Reaction | **Entity** | Stable participants, provenance, conditions, views |
| ReactionClass | **Facet vocabulary** | One reaction can have multiple overlapping types |
| Experiment | **Entity** | Reusable procedure/evidence anchor |
| Phenomenon | **Usually contextual observation; named type optionally a concept** | Avoid detached phenomenon hierarchy |
| QuantityKind | **Controlled term used by properties/derivations** | Enables calculations without quantity entities explosion |
| Relation types | **Relation vocabulary** | Explicit typed semantic graph |
| Context | **Qualifier object/dimensions** | Makes conditional truth first-class |
| TeachingView | **View** | Pedagogical projection, never domain truth root |
| Curriculum mapping | **View metadata / external mapping** | Curriculum editions must not own ontology identity |
| macro/micro/symbolic | **Pedagogical representation dimensions** | Connect explanations across levels |

## 14. Justified additions beyond the 11 diagrams

The following are added because they materially improve the target compiler:

1. **Knowledge assertion with fact kind** — necessary to separate intrinsic, contextual, and derived truth.
2. **Context qualifiers** — necessary for safe reaction/property reasoning and to avoid false unconditional claims.
3. **Evidence/provenance links** — necessary for explainability, source auditing, and curriculum trust.
4. **Structure/Bond separation from drawings** — necessary for structural reasoning and multiple representations.
5. **MaterialSystem/Solution identity** — necessary for electrolyte, equilibrium, colloid, concentration, and experiment knowledge.
6. **Reaction as an entity with independent ReactionClass facets** — necessary for reuse across D01/D03/D04/D05/D06/D10/D11.
7. **QuantityKind/value semantics** — necessary for D01/D02/D04/D06 and future deterministic calculations.
8. **Explicit macro/micro/symbolic bridge** — necessary for explanation rather than mere fact lookup.

No additional taxonomy is introduced merely to make the ontology look comprehensive.

## 15. Non-goals

This document does not define:

- database tables, JSON/YAML schemas, ORM models, or persistence layout;
- compiler/runtime implementation;
- reaction-rule execution semantics;
- balancing, matching, or inference algorithms;
- exhaustive IUPAC or research-grade chemistry coverage;
- a full laboratory-information-management model;
- a question-bank/exam-item ontology;
- textbook chapter inheritance;
- backward compatibility with `chem-knowledge-data` schemas.

## 16. External design references

These are **design references, not dependencies**:

- Ministry of Education of the PRC, *General Senior High School Curriculum Plan and Subject Curriculum Standards (2017 Edition, 2020 Revision)*: https://www.moe.gov.cn/srcsite/A26/s8001/202006/t20200603_462199.html
- Ministry of Education of the PRC, *JY/T 0655—2025 General Senior High School Chemistry Teaching Equipment Configuration Standard*: https://www.moe.gov.cn/srcsite/A06/s3732/202507/W020250701322477393561.pdf
- EMBL-EBI ChEBI: https://www.ebi.ac.uk/chebi/about
- ChEBI ontology overview: https://www.ebi.ac.uk/training/online/courses/chebi-the-online-chemical-dictionary-for-small-molecules/chebi-ontology/
- OBO Relation Ontology: https://oborel.github.io/obo-relations/

The useful lesson from mature resources is to keep chemical identity, structure/classification, roles, and semantic relations distinct. This project adapts that lesson to high-school chemistry and pedagogical inference rather than importing an external ontology wholesale.
