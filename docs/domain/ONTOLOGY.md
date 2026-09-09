# Canonical Domain Ontology

Status: **M10 canonical ontology with a bounded executable relation subset**

## 1. Modeling rule

Use shallow identity kinds plus independent facets, typed relations, structured context, and derived projections. Do not encode textbook chapter trees as class inheritance.

## 2. Chemical identity kinds

```text
Entity
├─ Element
├─ Species
│  ├─ Atom
│  ├─ Ion
│  ├─ Molecule
│  └─ other curriculum-justified microscopic species
├─ Substance
└─ MaterialSystem
   ├─ Mixture
   └─ Solution
```

`Ion` is a subtype discriminator of `Species`, not a peer `entity_kind`.

`Substance` is a pure macroscopic material identity. An elemental Substance is distinct from its abstract Element identity; a minimal elemental composition used for stoichiometric balancing is not itself a molecular-structure or allotrope claim. `MaterialSystem` is a composed sample/system identity used for solutions, mixtures, colloids, equilibrium systems, and experiment-specific compositions when the system itself needs durable reference.

## 3. Structure

`Structure` is a stable domain object distinct from any representation.

A structure may model molecular connectivity/geometry, ionic lattice, metallic structure, network covalent structure, or other curriculum-relevant structural semantics.

Representations include SMILES/InChI-like encodings, Lewis structures, structural formulae, crystal descriptions, and images/assets. These do not own structure identity.

Bonds are embedded structure components by default. Functional groups are reusable structural-motif/facet concepts linked to structures/species.

## 4. Facets

Facets represent independent classification dimensions such as:

- elemental character;
- compound/material family;
- acid/base/salt/oxide class;
- oxide behavior;
- organic family;
- functional group;
- electrolyte behavior;
- acid/base role;
- oxidation/reduction role;
- reaction class.

Context-sensitive roles must be contextual assertions rather than permanent labels.

## 5. Facts

Facts are intrinsic, contextual, or derived. Changing conditions without changing identity implies context is required.

Typical contextual dimensions include phase, solvent/medium, concentration, temperature, pressure, pH regime, atmosphere, reagent availability, catalyst, light/heat/electrical stimulus, and experimental setup.

Contextual chemistry properties may also bound reaction-family applicability. For example, acid strength and acid redox character are separate facts; knowing that an acid is strong does not establish that a non-oxidizing pathway applies.

Metal activity relative to hydrogen is likewise contextual chemistry knowledge, not a reaction-result facet. M10 uses only the evidence-backed controlled values `above` and `below`; it does not infer a numeric activity series or electrode potentials.

## 6. Relations

Relations are typed semantic assertions, not generic graph edges. Useful relation families include composition, structure, acid/base conjugacy, transformation, derivation, evidence, pedagogy, and reaction composition.

M10's executable subset contains the one-hop controlled relation `metal.product_cation`. The owning elemental-metal Substance embeds the context and evidence-bearing assertion, and the target must resolve to a Species. It does not receive a separate identity unless an independent lifecycle later requires one. This relation is chemical product-identity knowledge; it is not fake aqueous dissociation of the solid metal.

## 7. Reactions

A `Reaction` is a stable knowledge object for one transformation. Classification is multi-axial: redox, acid-base, precipitation, gas evolution, combustion, substitution, addition, esterification, etc. can overlap.

Reaction forms are representations/projections; chemically distinct half-reactions remain separate reactions.

## 8. Experiments and observations

A reusable `Experiment` may be identity-bearing when a canonical procedure/design needs durable reference. Individual observations are normally contextual facts attached to a reaction/material system/experiment.

## 9. Required examples

- Fe element concept != Fe(s) substance.
- S element concept != elemental sulfur Substance; an `S: 1` balancing basis does not assert monatomic bulk sulfur.
- NaCl crystal is a substance with ionic structure and constituent Na+/Cl- species; no NaCl molecule is required.
- H2SO4 molecular species != sulfuric-acid substance != sulfuric-acid solution/material system.
- SO2 oxidizing/reducing behavior is contextual/reaction-qualified.
- ethanol links to molecular structure and hydroxyl motif; alcohol is a facet/classification.
