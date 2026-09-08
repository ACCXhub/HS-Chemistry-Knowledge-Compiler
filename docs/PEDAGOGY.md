# Canonical Pedagogical View Model

Status: **canonical pedagogical projection foundation for the new compiler**

This document defines how high-school chemistry knowledge is organized for teaching, curriculum coverage, explanation, and learner reasoning **without turning textbook chapter structure into domain ontology inheritance**.

The 11 user-provided high-school chemistry framework diagrams are treated as important pedagogical evidence and canonical **TeachingView candidates**:

- D01 chemical kinetics and equilibrium
- D02 electrolyte solutions
- D03 chemical reaction types
- D04 chemical calculations
- D05 chemical experiments
- D06 chemical notation and stoichiometry
- D07 solutions and colloids
- D08 classification of substances
- D09 structure and periodicity
- D10 elements and their compounds
- D11 organic compounds

They are not automatically ontology roots. The same domain entity may appear in many views without duplication.

## 1. Purpose of a TeachingView

A `TeachingView` is a projection over canonical domain knowledge for a pedagogical purpose.

It may select and organize:

- domain entities;
- facets;
- relations;
- context lenses;
- properties and quantities;
- experiments and observations;
- macro/micro/symbolic representations;
- prerequisite and explanatory paths;
- curriculum references;
- calculation/reasoning paths.

A TeachingView changes **what is shown, grouped, sequenced, and emphasized**. It does not change chemical truth.

This separation lets the compiler support many organizations simultaneously:

```text
canonical domain knowledge
        ↓
TeachingView: D08 classification
TeachingView: D10 element-centered inorganic chemistry
TeachingView: D03 reaction types
TeachingView: exam review / prerequisite / misconception views later
```

No view owns the identity of `H2SO4`, `Fe`, `NaCl`, or a canonical reaction.

## 2. Conceptual TeachingView contract

This is a semantic model, not a persistence schema.

A TeachingView should be able to express:

```text
TeachingView
- stable view identity
- title / purpose
- learner level or curriculum target
- entry points / anchor entities or concepts
- selection of entity kinds and facets
- relation paths to traverse
- context dimensions to expose
- representation modes
- sequence / grouping / prerequisite edges
- reasoning paths
- experiments / observations used as evidence
- quantity/calculation lenses
- curriculum mappings
- coverage notes
```

A view may be graph-like rather than linear. `prerequisite_of`, `explains`, `contrasts_with`, or `recommended_next` are pedagogical edges in the view layer unless they express durable domain semantics.

## 3. Curriculum mapping boundary

Curriculum structure is an external pedagogical coordinate system, not the core ontology.

For the current Chinese senior-high baseline, the Ministry of Education's 2017 curriculum standards as revised in 2020 provide the authoritative national reference. The chemistry curriculum is organized around compulsory themes and selective-compulsory modules rather than a single chemical taxonomy. A 2025 Ministry teaching-equipment standard continues to anchor school chemistry to the current curriculum standard and explicitly references the chemistry core competencies, including macro/micro analysis, change/equilibrium thinking, evidence/model reasoning, inquiry/innovation, and scientific attitude/social responsibility.

The compiler should therefore use a `CurriculumRef`-style external mapping concept with metadata such as:

- jurisdiction/system;
- school level;
- curriculum-standard edition;
- compulsory / selective-compulsory / elective layer;
- theme/module;
- learning objective or competency;
- optional textbook edition/chapter reference.

A TeachingView or knowledge item can `addresses` / `supports` one or more curriculum references. Curriculum labels must not be encoded into chemical identity.

### 3.1 Current national structural anchors

Useful national curriculum anchors include the compulsory themes:

1. chemical science and experimental inquiry;
2. common inorganic substances and their applications;
3. basic substance structure and chemical-reaction laws;
4. simple organic compounds and their applications;
5. chemistry and social development;

and selective-compulsory modules:

1. chemical reaction principles;
2. substance structure and properties;
3. fundamentals of organic chemistry.

These provide coverage coordinates. They do not define entity inheritance.

## 4. Mapping the 11 diagrams to TeachingViews

| Diagram | TeachingView role | Primary domain anchors | Key facets / relations / contexts | Why it is a View rather than an ontology root |
| --- | --- | --- | --- | --- |
| **D01 chemical kinetics and equilibrium** | Reaction-principle / causal reasoning view | Reaction, QuantityKind, Substance/Species | rate, equilibrium constant, reversible reaction; concentration, temperature, pressure, catalyst; condition → outcome explanation | Rate/equilibrium are properties and contextual/derived states of reactions, not families of chemical entities |
| **D02 electrolyte solutions** | Solution/speciation/ionic-equilibrium view | MaterialSystem/Solution, Species, Ion, Reaction | electrolyte and acid/base facets; dissolution/ionization/dissociation/conjugate relations; solvent, concentration, pH, temperature | Electrolyte behavior depends on medium; solution knowledge cuts across many substances |
| **D03 chemical reaction types** | Multi-axial reaction classification view | Reaction | ReactionClass facets: redox, acid-base, precipitation, combination, substitution, organic transformation, etc. | One reaction can belong to several types simultaneously; a single class tree is misleading |
| **D04 chemical calculations** | Quantitative reasoning view | Reaction, Substance/Species, QuantityKind | amount, mass, volume, concentration, molar mass, stoichiometric ratio; scenario context | Calculations are reasoning paths over entities and quantities, not chemical entities/classes |
| **D05 chemical experiments** | Evidence/inquiry view | Experiment, Substance/MaterialSystem, Reaction, observation assertions | uses substance, tests property, observes, supports assertion; procedural context | Experiments support and reveal domain knowledge but should not own the entities they investigate |
| **D06 chemical notation and stoichiometry** | Symbolic representation / translation view | Species, Substance, Reaction, QuantityKind | formula/equation representations, stoichiometric coefficients, phase notation; represents / derived-from links | Symbols are representations of domain referents, not the referents themselves |
| **D07 solutions and colloids** | Material-system / dispersion view | MaterialSystem, Solution, Species | mixture/dispersion facets, concentration, solute/solvent/component relations, Tyndall/precipitation observations | Solution/colloid organization is material-system centered and overlaps D02/D05/D08 |
| **D08 classification of substances** | Faceted classification view | Element, Species, Substance, MaterialSystem | elemental/compound, metal/nonmetal, oxide/acid/base/salt, organic families, electrolyte behavior | Classification dimensions overlap; the view composes facets instead of deep inheritance |
| **D09 structure and periodicity** | Structure → property → trend reasoning view | Element, Atom/Species, Structure, Bond | electronic structure, group/period, bonding, geometry; periodic trends as derived comparisons | Periodicity is a relation/order/projection over elements and properties, not a chapter-shaped entity tree |
| **D10 elements and their compounds** | Element-centered relational knowledge map | Element, Species, Substance, Reaction | contains/corresponds-to element, oxidation-state assignments, preparation/conversion reactions, context | “Sulfur and its compounds” is a traversal centered on S, not a new ontological parent of every sulfur compound |
| **D11 organic compounds** | Structure/function/transformation view | Species, Substance, Structure, Bond | FunctionalGroup facets, organic classes, isomer relations, ReactionClass organic transformations, conditions | Organic teaching is best organized by structure/facets/reaction patterns without duplicating entities |

### 4.1 Important consequence

The diagrams overlap by design. For example:

- `H2SO4` belongs in D02, D03, D04, D05, D06, D08, and D10;
- `NaCl` belongs in D02, D04, D05, D06, D07, and D08;
- ethanol belongs in D04, D05, D06, D08, and D11.

The compiler should reuse one canonical identity and project it differently in each TeachingView.

## 5. Macro / micro / symbolic representation

High-school chemistry explanation depends on moving between three levels. These are **pedagogical representation dimensions**, not mutually exclusive chemical entity classes.

### 5.1 Macroscopic layer

Focuses on observable material and experimental behavior:

- Substance;
- MaterialSystem / Solution;
- phase and bulk properties;
- Experiment;
- contextual Observation/Phenomenon;
- measurable QuantityValues.

Examples: iron powder burns; a precipitate appears; sodium chloride dissolves; sulfur dioxide has an observable odor only where safety/teaching context permits mentioning it.

### 5.2 Microscopic layer

Focuses on explanatory particles and structure:

- Element/Atom;
- Species, Ion, Molecule;
- Structure;
- Bond;
- constituent particles;
- speciation and particle-level transformation.

### 5.3 Symbolic layer

Focuses on representations:

- element symbols;
- chemical formulas;
- ionic/formula-unit notation;
- structural/Lewis formulas;
- chemical equations;
- ionic equations;
- oxidation-state notation;
- quantity expressions and units.

A symbolic artifact should point back to what it represents. An ionic equation should normally be derived from a canonical reaction plus medium/speciation assumptions instead of becoming a competing reaction identity.

### 5.4 Required bridge pattern

TeachingViews should be able to expose explicit bridges:

```text
MACRO observation
    ↓ explained by
MICRO species / structure / particles
    ↓ represented by
SYMBOLIC formula / equation / quantity expression
```

The reverse traversal should also work:

```text
symbolic equation
    → resolve participants
    → inspect microscopic change
    → predict/interpret macroscopic phenomenon under context
```

### 5.5 Example: NaCl dissolving in water

**Macro:** sodium chloride solid disappears into a homogeneous solution up to the solubility limit.

**Micro:** the ionic lattice is disrupted and Na+ / Cl- become solvated aqueous species at the intended school-model resolution.

**Symbolic:** `NaCl(s) → Na+(aq) + Cl-(aq)` as a representation of the dissolution/speciation process under an aqueous context.

The three descriptions are not three separate truths; they are linked representations of one domain situation at different explanatory levels.

## 6. Pedagogical relation types

Relations in a TeachingView can include view-specific learning organization that should not pollute domain truth.

Useful pedagogical edges include:

- `prerequisite_of`;
- `explains`;
- `illustrates`;
- `contrasts_with`;
- `analogy_to` where carefully curated;
- `example_of`;
- `common_error_about` later if a misconception layer is justified;
- `recommended_next`;
- `uses_representation`;
- `addresses_curriculum_ref`.

Domain relations such as `has_structure`, `is_conjugate_base_of`, and reaction participation remain owned by the ontology. The TeachingView only selects/traverses them.

## 7. Knowledge-organization and reasoning paths

A TeachingView should support paths, not just lists of topics.

### 7.1 Structure-to-behavior path

```text
identity
→ composition / structure
→ functional or chemical-class facets
→ intrinsic properties
→ context-qualified behavior
→ canonical reactions / observations
→ symbolic representation
```

Useful in D09, D10, and D11.

### 7.2 Observation-to-explanation path

```text
experiment / macro observation
→ evidence
→ candidate species/structure change
→ canonical reaction or equilibrium
→ contextual qualification
→ symbolic equation / explanation
```

Useful in D05 and D02.

### 7.3 Classification path

```text
entity identity
→ independent facet dimensions
→ compare sibling facet values
→ retrieve representative reactions/properties
→ expose exceptions/context
```

Useful in D08. The important feature is that the learner sees **why** several labels can coexist.

### 7.4 Quantitative path

```text
problem scenario
→ resolve substances/species/reaction
→ identify known/unknown QuantityKinds
→ normalize units/context
→ use canonical stoichiometric/quantity relations
→ derive requested result
→ preserve explanation path
```

Useful in D04 and D06. Runtime calculation semantics are outside this document.

### 7.5 Periodicity path

```text
Element position / electronic structure
→ comparable property set
→ derived trend/contrast
→ structure/property explanation
→ prediction for related substances/reactions
```

Useful in D09. A “periodic trend” is a derived pedagogical ordering, not an entity superclass.

### 7.6 Reaction-principle path

```text
canonical Reaction
→ thermodynamic/kinetic/equilibrium quantities
→ Context dimensions
→ perturb one dimension
→ explain expected direction/rate change
→ connect to experiment or application
```

Useful in D01. The TeachingView can visualize cause/effect without defining the runtime inference engine.

### 7.7 Organic structure-to-transformation path

```text
Species
→ Structure
→ FunctionalGroup facets
→ ChemicalClass facets
→ candidate ReactionClass patterns
→ required Context/conditions
→ canonical example reactions
→ macro/symbolic explanation
```

Useful in D11.

## 8. Detailed view guidance for D01–D11

### D01 — Chemical kinetics and equilibrium

Emphasize:

- Reaction identity;
- reversible-process representation;
- reaction rate as a contextual quantity;
- equilibrium constant with temperature qualification;
- dynamic equilibrium as a contextual/derived system state;
- concentration, pressure, temperature, catalyst as exposed context dimensions;
- distinction between **rate change** and **equilibrium-position change**.

Avoid creating classes such as `FastReaction`, `HighYieldReaction`, or `EquilibriumReactionAtHighPressure` as permanent domain types.

### D02 — Electrolyte solutions

Emphasize:

- Solution/MaterialSystem as macro subject;
- ions/molecules as micro species;
- concentration, pH, solvent, temperature;
- electrolyte/strong/weak behavior as qualified facets;
- acid/base/conjugate relations;
- ion reaction and equilibrium links;
- macro conductivity/indicator/precipitation observations connected to micro species.

This view is a major consumer of context-qualified truth.

### D03 — Chemical reaction types

Teach reaction typing as a matrix of independent questions:

1. What is the gross composition pattern?
2. Is electron transfer involved?
3. Is proton transfer involved?
4. What drives the ionic process?
5. Is there a named process family such as combustion?
6. For organic chemistry, what structural transformation occurred?

A reaction may answer “yes” in several dimensions.

### D04 — Chemical calculations

Organize around quantities and invariants rather than memorized chapter formulas:

- amount of substance;
- mass / molar mass;
- gas volume with T/P context;
- solution concentration;
- stoichiometric coefficients;
- yield/purity/composition where curriculum requires;
- limiting/excess role as derived scenario knowledge.

The view should make the underlying domain participants visible so calculations do not become detached arithmetic.

### D05 — Chemical experiments

A useful experiment view connects:

```text
purpose
→ domain claim to test
→ materials/substances
→ setup/procedure context
→ observation
→ evidence
→ conclusion/explanation
```

Observation must remain context-qualified. A color, precipitate, gas evolution, or other phenomenon should not be stored as an unconditional property of a reactant.

### D06 — Chemical notation and stoichiometry

This is primarily a **representation and translation view**.

Include:

- symbol ↔ element;
- formula ↔ species/substance/structure as appropriate;
- phase annotation ↔ context;
- coefficient ↔ stoichiometric participant relation;
- molecular/structural formula ↔ Structure;
- full equation / ionic equation ↔ canonical Reaction + context;
- quantity notation ↔ QuantityKind/value/unit.

This view is a natural place to teach why `NaCl` is a formula unit in an ionic solid rather than evidence of discrete NaCl molecules.

### D07 — Solutions and colloids

Center on MaterialSystem and scale/dispersion behavior:

- homogeneous solution vs other dispersed systems;
- solute/solvent/components;
- concentration;
- solubility and saturation with context;
- colloidal/dispersion facets only to the granularity needed by curriculum;
- Tyndall effect and other named phenomena connected to the relevant material system/conditions.

Do not duplicate D02 electrolyte knowledge; traverse the same Solution and Species entities through a different lens.

### D08 — Classification of substances

This view demonstrates faceted classification directly.

A learner should be able to filter the same canonical items by independent dimensions such as:

- element vs compound;
- metal vs nonmetal;
- oxide / acid / base / salt;
- organic family;
- functional group;
- electrolyte behavior in a specified medium;
- oxidation/reduction role in a specified reaction.

Combined labels are query results, not permanent composite subclasses.

### D09 — Structure and periodicity

Connect:

- Element ↔ atomic number ↔ electronic structure;
- position/group/period ↔ comparable element properties;
- Species ↔ Structure ↔ Bond;
- structure ↔ physical/chemical property explanation;
- periodic trends as derived comparisons;
- representative compounds/reactions as evidence/applications.

This view should support “position → structure → property → behavior” reasoning without claiming that periodic position alone deterministically explains every reaction.

### D10 — Elements and their compounds

Use an element-centered graph traversal:

```text
Element S
→ elemental substances/species
→ compounds containing S
→ structures / classes
→ oxidation-state assignments
→ canonical interconversion reactions
→ experiments / phenomena
→ contexts
```

This is a TeachingView, not a hierarchy in which all sulfur compounds inherit from a `SulfurChapter` class.

### D11 — Organic compounds

Organize around structure and transformations:

- Species/Substance identity;
- carbon skeleton / molecular Structure;
- FunctionalGroup facets;
- independent organic ChemicalClass facets;
- isomer relations;
- ReactionClass facets for transformations;
- condition-qualified reactions;
- macro properties/experiments;
- symbolic structural formulas/equations.

This permits the same molecule to be retrieved by functional group, structure, reaction pattern, use, or curriculum sequence without creating duplicate records.

## 9. Example entities across TeachingViews

### 9.1 H2SO4

Potential view participation:

- **D02:** aqueous ionization/speciation, strong-acid/electrolyte classification with context;
- **D03:** acid-base and redox reactions;
- **D04:** concentration/stoichiometry calculations;
- **D05:** dilution, ion tests, contextual experimental phenomena;
- **D06:** formula, phase notation, equations/ionic equations;
- **D08:** acid / oxoacid / compound facets;
- **D10:** sulfur oxidation-state and sulfur-compound network.

The concentrated-acid oxidizing behavior must be shown through the qualifying context and reaction partner, not as a universal species label.

### 9.2 SO2

Potential view participation:

- **D03:** redox and other reaction classifications;
- **D05:** gas-property/reaction experiments and observations;
- **D06:** formula/equation representation;
- **D08:** oxide/compound classification;
- **D10:** sulfur-compound interconversion network.

The view should explicitly allow SO2 to appear as reductant in one reaction and oxidant in another.

### 9.3 Fe

Potential view participation:

- **D03:** substitution/redox reactions;
- **D04:** reaction stoichiometry;
- **D05:** reactivity experiments;
- **D06:** symbol/ion/equation notation;
- **D08:** metal/elemental-substance facets;
- **D09:** atomic structure/periodic position/metallic structure;
- **D10:** iron, Fe2+, Fe3+, oxides/hydroxides/salts and interconversion reactions.

Do not conflate the Element `Fe`, Fe atom species, Fe2+/Fe3+ ions, and bulk iron substance.

### 9.4 NaCl

Potential view participation:

- **D02:** electrolyte solution and aqueous ions;
- **D04:** molar/concentration calculations;
- **D05:** dissolution/precipitation-related experiments;
- **D06:** formula-unit and ionic equation teaching;
- **D07:** solution material system;
- **D08:** salt/ionic-compound facets.

This is a strong macro/micro/symbolic bridge example because `NaCl` notation must not imply a molecular crystal.

### 9.5 Ethanol

Potential view participation:

- **D04:** combustion/solution quantitative problems;
- **D05:** property/reaction experiments;
- **D06:** molecular/structural formula and reaction equations;
- **D08:** organic compound/alcohol classification;
- **D11:** hydroxyl group, alcohol family, oxidation/esterification/combustion transformations.

The same canonical entity should support all of these views.

## 10. Justified pedagogical additions beyond the 11 diagrams

The diagrams are strong topic maps, but the compiler needs several cross-cutting concepts to make them interoperable.

### 10.1 Context lens

Why added: D01/D02/D05/D07/D10/D11 all contain knowledge whose truth depends on conditions. A TeachingView must expose or intentionally fix those conditions.

### 10.2 Evidence/provenance path

Why added: learners and compilers both need to distinguish “the experiment showed X”, “the source states X”, and “X was derived from Y”. This supports explanation and auditing.

### 10.3 Macro/micro/symbolic bridge

Why added: it is central to chemical understanding and is explicitly aligned with the Chinese high-school chemistry competency emphasis on macroscopic identification and microscopic analysis. It also prevents symbols from being mistaken for physical entities.

### 10.4 Reasoning path

Why added: a knowledge graph that only groups concepts cannot explain how to move from evidence to conclusion, structure to property, or quantities to a calculation. Reasoning paths are pedagogical traversals, not runtime inference rules.

### 10.5 CurriculumRef mapping

Why added: national standards, provincial exam requirements, and textbook editions can change while chemical identity remains stable. External mapping prevents curriculum churn from rewriting the ontology.

### 10.6 Representation artifact

Why added: formulas, equations, particle diagrams, Lewis structures, and macro illustrations are essential teaching objects but are not themselves chemical entities. A representation layer lets multiple depictions point to one canonical referent.

## 11. Knowledge-organization rules

1. **One chemical identity, many views.** Never duplicate H2SO4/NaCl/etc. merely because they occur in different diagrams.
2. **A view may group; it may not redefine truth.** D08 can group acids, D10 can group sulfur compounds, D11 can group alcohols, but canonical identity/facts stay domain-owned.
3. **Context is visible when it changes meaning.** Especially acid/base strength, electrolyte behavior, oxidant/reductant roles, kinetics, equilibrium, solubility, phase, and experimental phenomena.
4. **Composite labels are queries.** “strong oxygen-containing diprotic acid” is a facet intersection, not a required class.
5. **Symbols point to referents.** Formula/equation nodes are pedagogical representations or derived projections.
6. **Observations point to evidence.** Experiment phenomena are not detached slogans.
7. **Derived claims keep derivation.** Molar mass, ionic equations, trends, limiting reagent roles, and similar results remain explainable.
8. **Curriculum mapping is many-to-many.** A domain item may support several themes/modules; one curriculum target may require many entities and relations.

## 12. Coverage model

Coverage should be measurable without hard-coding chapter ownership.

A TeachingView can report coverage across:

- required domain entity kinds;
- target facets;
- target relation types;
- required context dimensions;
- curriculum references;
- macro/micro/symbolic representation presence;
- experiment/evidence links;
- reasoning-path anchors;
- representative examples.

This lets the compiler later answer questions such as:

- Does D02 cover both macro solution behavior and micro ion speciation?
- Does D03 classify reactions on more than one axis?
- Does D05 connect observations to supported claims?
- Does D06 provide symbolic representations for the canonical reactions in D03?
- Does D10 cover the required element-compound network without duplicating entities?

The exact coverage-audit implementation is outside this document.

## 13. Explicit non-goals

This pedagogical model does not define:

- textbook page/chapter storage schema;
- UI layout for graphs or lessons;
- persistence details;
- reaction-rule execution;
- automatic balancing/matching/inference algorithms;
- scoring, adaptive learning, spaced repetition, or exam recommendation engines;
- an exhaustive misconception taxonomy;
- a complete apparatus/procedure ontology;
- migration compatibility with legacy `chem-knowledge-data` teaching trees.

## 14. External references

These references support the pedagogical boundary but are not runtime dependencies:

- Ministry of Education of the PRC, *General Senior High School Curriculum Plan and Subject Curriculum Standards (2017 Edition, 2020 Revision)*: https://www.moe.gov.cn/srcsite/A26/s8001/202006/t20200603_462199.html
- Ministry of Education of the PRC, *JY/T 0655—2025 General Senior High School Chemistry Teaching Equipment Configuration Standard*: https://www.moe.gov.cn/srcsite/A06/s3732/202507/W020250701322477393561.pdf
- EMBL-EBI ChEBI ontology materials: https://www.ebi.ac.uk/training/online/courses/chebi-the-online-chemical-dictionary-for-small-molecules/chebi-ontology/
- OBO Relation Ontology: https://oborel.github.io/obo-relations/

The compiler uses these as evidence for separation of identity, classification, relations, context, and pedagogy; it remains a purpose-built high-school chemistry knowledge compiler rather than a wrapper around any external ontology.
