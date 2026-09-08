# Canonical Data Model

Status: **draft contract for `workstream/data-contracts`**

This document defines the editable source-record model for the new HS-Chemistry-Knowledge-Compiler. The model is intentionally independent from textbook chapter trees and from the legacy `chem-knowledge-data` layout.

## 1. Design invariants

1. **Identity is not presentation.** Permanent IDs do not encode Chinese names, English names, formula strings, ontology hierarchy, or teaching paths.
2. **Entity is the identity carrier.** `Element`, `Ion`, `Species`, and `Substance` are typed entity payload contracts, not parallel identity systems.
3. **Facts are assertions.** A property value is not silently embedded as timeless truth when it depends on context, evidence, or derivation.
4. **Absence, unknown, and false are distinct.** Missing data is not interpreted as false.
5. **Reactions and inferred candidates are different record classes.** A candidate never becomes canonical merely because an inference rule generated it or a matcher found an equivalent canonical equation.
6. **Teaching organization is a projection.** D01-D11 and later curriculum paths reference canonical records; they never own their identity.
7. **Source and generated data are separated.** Editable source records are Git-versioned. Compiler outputs are reproducible artifacts.

## 2. Common source-record envelope

Every top-level source record uses this envelope:

```yaml
id: ent_01991c2e-7a10-7a01-8a01-000000000003
record_type: entity
schema_version: 0.1.0
record_revision: 1
status: active            # active | deprecated | withdrawn
curation:
  change_reason: initial import
  evidence_refs: []       # or derivation/provenance where required
```

Contract rules:

- `id` is stable for the lifetime of the conceptual record.
- `schema_version` versions the record contract, not the chemistry claim.
- `record_revision` increments when the semantic content of that record changes.
- Git commit history is the authoritative historical log. `record_revision` is a convenient record-level audit coordinate.
- Renaming a label, moving a file, changing a teaching path, or changing a display formula does not change an entity ID.
- A genuinely different chemical concept receives a new entity ID; it is never forced into an old ID for compatibility.

## 3. Entity and typed chemical identity

### 3.1 Entity

`Entity` is the only permanent identity owner for chemical things that participate in facts, relations, reactions, and teaching views.

Required fields:

```yaml
id: ent_...
record_type: entity
entity_kind: element      # element | species | ion | substance
semantic_keys: []
terms:
  preferred: []
  aliases: []
payload: {}
```

### 3.2 Semantic keys

Semantic keys are lookup and reconciliation aids, not primary IDs.

```yaml
semantic_keys:
  - scheme: element.atomic_number
    value: "26"
  - scheme: element.symbol
    value: Fe
```

A semantic key may be unique within a declared scheme, but changing or correcting it does not rewrite the entity ID. Formula strings may be semantic keys for formula-oriented records, but they are never the permanent identity themselves.

### 3.3 Terms and aliases

```yaml
terms:
  preferred:
    - lang: zh-CN
      value: 二氧化硫
    - lang: en
      value: sulfur dioxide
  aliases:
    - lang: zh-CN
      value: 亚硫酸酐
      scope: historical_or_teaching
```

Aliases may carry language, scope, register, source, and deprecation metadata. Search aliases do not define equivalence between entities.

### 3.4 Element payload

An `element` entity represents the periodic-table element concept, not automatically the bulk elemental substance.

```yaml
entity_kind: element
payload:
  atomic_number: 26
  symbol: Fe
```

Atomic number is a strong semantic key and validated invariant, but the permanent ID remains opaque.

### 3.5 Species payload

A `species` entity represents a definite microscopic/formula-level chemical species.

```yaml
entity_kind: species
payload:
  composition_ref: cmp_...
  formal_charge: 0
  structure_refs: []
```

A molecular formula is a representation or semantic key. Isomers with the same formula require different entity IDs and normally different structure references.

### 3.6 Ion payload

`ion` is a charged species with explicit charge and optional parent/conjugate relations expressed separately.

```yaml
entity_kind: ion
payload:
  composition_ref: cmp_...
  formal_charge: -1
  ion_kind: polyatomic    # monatomic | polyatomic | complex
  structure_refs: []
```

### 3.7 Substance payload

A `substance` represents a macroscopic material identity used in laboratory, reaction, or teaching statements. It may be pure or mixture-like. Phase is not permanently baked into the identity unless phase distinction is itself the intended material concept.

```yaml
entity_kind: substance
payload:
  substance_kind: pure_compound  # elemental | pure_compound | solution | mixture
  composition_ref: cmp_...
  constituent_entity_ids: []
```

Example: an aqueous sulfuric-acid solution should not be silently conflated with the `H2SO4` molecular species. It can be represented as a distinct substance/material entity plus context and composition facts.

## 4. Composition

`Composition` is reusable normalized composition data.

```yaml
id: cmp_...
record_type: composition
subject_entity_id: ent_...
components:
  - element_entity_id: ent_element_h
    count: 2
  - element_entity_id: ent_element_s
    count: 1
  - element_entity_id: ent_element_o
    count: 4
net_charge: 0
```

Rules:

- Components reference element entities, not element-name strings.
- Counts are exact integers for discrete formulas where applicable.
- Non-stoichiometric or mixture composition is represented with an appropriate substance/composition contract rather than fake integer counts.
- Display ordering such as `H2SO4` is a notation concern and may be compiled from or associated with this composition.

## 5. Structure reference

A `StructureReference` links an entity to a structural representation without making the representation the permanent identity.

```yaml
id: str_...
record_type: structure_reference
subject_entity_id: ent_...
representation_type: smiles   # smiles | inchi | lewis | crystal | asset | external
value: O=S(=O)(O)O
qualifiers: {}
evidence_refs: [ev_...]
```

Multiple structure references may coexist. A structure reference may be deprecated without changing the entity ID.

## 6. Facet assertion

Classification is expressed as assertions over controlled facet vocabularies.

```yaml
id: fas_...
record_type: facet_assertion
subject_entity_id: ent_...
facet_key: chem.acid_base.role
value_key: acid
context_ref: null
assertion_kind: intrinsic     # intrinsic | contextual | derived
value_state: known            # known | unknown | not_applicable
evidence_refs: [ev_...]
```

A deep textbook classification path is not required. The same entity can carry multiple independent facet assertions.

## 7. Property fact and fact semantics

A `PropertyFact` stores one auditable assertion.

```yaml
id: fact_...
record_type: property_fact
subject_id: ent_...
property_key: physical.boiling_point
fact_kind: contextual         # intrinsic | contextual | derived
value_state: known            # known | unknown | not_applicable
value:
  number: -10.0
  unit: degC
context_ref: ctx_...
evidence_refs: [ev_...]
derivation: null
```

### 7.1 Three fact kinds

- **intrinsic**: intended to hold for the entity independent of an experimental context within the model, such as atomic number or formal charge.
- **contextual**: only meaningful under qualifiers such as phase, temperature, pressure, solvent, concentration, pH, or measurement method.
- **derived**: reproducibly computed from other records or a rule; must include derivation provenance.

### 7.2 Missing, unknown, false

The compiler must preserve these distinctions:

| State | Meaning |
|---|---|
| no fact record | dataset has no assertion for this property |
| `value_state: unknown` | dataset explicitly knows the value is unresolved/unknown in this scope |
| `value_state: not_applicable` | property does not apply in this scope |
| `value_state: known`, `value: false` | a known boolean false assertion |

Consumers must never coerce the first three states to `false`.

## 8. Context

`Context` is a reusable qualifier bundle for facts and relations.

```yaml
id: ctx_...
record_type: context
qualifiers:
  phase: aqueous
  temperature:
    number: 298.15
    unit: K
  pressure:
    number: 100
    unit: kPa
  solvent_entity_id: ent_water
```

Context records should contain semantic qualifiers, not prose-only descriptions.

## 9. Relation

A `Relation` connects canonical subjects and objects.

```yaml
id: rel_...
record_type: relation
subject_id: ent_...
relation_key: chem.conjugate_base_of
object_id: ent_...
relation_kind: contextual     # intrinsic | contextual | derived
context_ref: null
value_state: known
evidence_refs: [ev_...]
derivation: null
```

Relations are directed. Symmetric or inverse behavior is declared by the relation vocabulary/compiler, not inferred from label wording.

## 10. Reaction model

### 10.1 Canonical Reaction

A canonical `Reaction` is curated source truth. It has its own stable reaction ID.

```yaml
id: rxn_...
record_type: reaction
canonical_status: canonical
representation: molecular     # molecular | ionic | net_ionic | conceptual
participant_refs: [rpart_..., rpart_..., rpart_..., rpart_...]
condition_refs: [cond_...]
evidence_refs: [ev_...]
notes: []
```

The display equation is compiled from participants and notation preferences; it is not the reaction identity.

### 10.2 ReactionParticipant

```yaml
id: rpart_...
record_type: reaction_participant
reaction_id: rxn_...
entity_id: ent_...
role: reactant                # reactant | product | catalyst | solvent | reagent
coefficient:
  numerator: 1
  denominator: 1
phase: aqueous                # solid | liquid | gas | aqueous | dissolved | unknown
participant_qualifiers: {}
```

Stoichiometric coefficients are exact rationals. Phase is participant/context information, not part of entity identity.

### 10.3 Condition

`Condition` represents reaction applicability or experimental requirements.

```yaml
id: cond_...
record_type: condition
condition_key: operation.temperature
operator: gte
value:
  number: 373
  unit: K
qualifiers: {}
evidence_refs: [ev_...]
```

Conditions may represent catalyst, heat, light, concentration regime, atmosphere, pH regime, solvent, electrode setup, or other standardized requirements.

## 11. Canonical Reaction vs ReactionCandidate

`ReactionCandidate` is generated/inferred data and is never a canonical `Reaction` record.

Required candidate fields:

```yaml
id: rcand_...
record_type: reaction_candidate
candidate_status: generated
proposed_participants: []
proposed_conditions: []
provenance:
  origin: inference
  rule_ref: rule_...
  input_entity_ids: []
  input_record_ids: []
  derived_product_ids: []
  conditions_considered: []
  exceptions_checked: []
  validation_results: []
  canonical_match:
    state: unchecked          # unchecked | none | exact | equivalent | ambiguous | conflict
    reaction_id: null
  proof_trace: []
  generator:
    name: hs-chem-compiler
    version: 0.1.0
    source_git_sha: "..."
```

Rules:

1. A candidate remains `rcand_*` even when `canonical_match.state` becomes `exact`.
2. Promotion to canonical truth is an explicit curation action that creates or edits an `rxn_*` source record with evidence.
3. Generated candidates belong in generated/staging artifacts unless deliberately checked in as review fixtures; they are not mixed into curated reaction sources.
4. Validation failures remain part of provenance and must not be erased to make a candidate appear canonical.

## 12. Source and Evidence

### 12.1 Source

```yaml
id: src_...
record_type: source
source_type: textbook         # textbook | standard | paper | database | website | manual
citation:
  title: "..."
  authors: []
  publisher: "..."
  year: 2026
identifiers: []
url: null
```

### 12.2 Evidence

`Evidence` locates and interprets a claim inside a source.

```yaml
id: ev_...
record_type: evidence
source_id: src_...
locator:
  page: 42
  section: "2.3"
claim_summary: "SO2 is a colorless gas under the stated conditions."
stance: supports            # supports | contradicts | qualifies
extraction_method: manual   # manual | import | parser
```

Every nontrivial curated assertion should be auditable through `evidence_refs`, or through a `derivation` whose own inputs are auditable.

## 13. Teaching views

### 13.1 TeachingView

```yaml
id: view_...
record_type: teaching_view
view_key: hs-cn-framework-11
name:
  zh-CN: 高中化学十一框架
path_refs: [path_...]
```

### 13.2 TeachingViewPath

```yaml
id: path_...
record_type: teaching_view_path
view_id: view_...
path_key: D08/substances/inorganic/acids
parent_path_id: path_...
label:
  zh-CN: 酸
members:
  - target_type: entity
    target_id: ent_...
ordering: 20
```

`D08/...` is a navigation/projection key. It is intentionally separate from `ent_*` identity and may be reorganized without remapping chemistry records.

## 14. Rule reference

A `RuleReference` gives inference provenance a stable, reviewable rule identity without making this workstream implement the inference engine.

```yaml
id: rule_...
record_type: rule_reference
rule_key: precipitation.double_displacement
rule_version: 1
status: active
inputs_contract: "two compatible aqueous ionic substances"
outputs_contract: "candidate products by ion exchange"
exception_policy_refs: []
evidence_refs: [ev_...]
implementation_ref: null
```

A later engine implementation can point at the rule record. Changing code does not silently rewrite what historical candidates claim they used.

## 15. Concrete entity examples

The following IDs are illustrative but follow the selected ID format.

### 15.1 Fe — element concept

```yaml
id: ent_01991c2e-7a10-7a01-8a01-000000000001
record_type: entity
schema_version: 0.1.0
record_revision: 1
status: active
entity_kind: element
semantic_keys:
  - {scheme: element.atomic_number, value: "26"}
  - {scheme: element.symbol, value: Fe}
terms:
  preferred:
    - {lang: zh-CN, value: 铁}
    - {lang: en, value: iron}
  aliases: []
payload:
  atomic_number: 26
  symbol: Fe
curation:
  change_reason: initial curated identity
  evidence_refs: [ev_periodic_table_fe]
```

A bulk iron material used as `Fe(s)` may receive a separate `substance` entity linked to this element; the element concept itself is not phase-bearing.

### 15.2 H2SO4 — molecular species

```yaml
id: ent_01991c2e-7a10-7a01-8a01-000000000003
record_type: entity
schema_version: 0.1.0
record_revision: 1
status: active
entity_kind: species
semantic_keys:
  - {scheme: formula.molecular, value: H2SO4}
terms:
  preferred:
    - {lang: zh-CN, value: 硫酸分子}
    - {lang: en, value: sulfuric acid molecule}
  aliases:
    - {lang: zh-CN, value: 硫酸, scope: formula_level_teaching}
payload:
  composition_ref: cmp_01991c2e-7a10-7a02-8a01-000000000003
  formal_charge: 0
  structure_refs: [str_01991c2e-7a10-7a03-8a01-000000000003]
curation:
  change_reason: initial curated identity
  evidence_refs: [ev_h2so4_identity]
```

### 15.3 NaCl — macroscopic pure compound

```yaml
id: ent_01991c2e-7a10-7a01-8a01-000000000005
record_type: entity
schema_version: 0.1.0
record_revision: 1
status: active
entity_kind: substance
semantic_keys:
  - {scheme: formula.stoichiometric, value: NaCl}
terms:
  preferred:
    - {lang: zh-CN, value: 氯化钠}
    - {lang: en, value: sodium chloride}
  aliases:
    - {lang: zh-CN, value: 食盐, scope: common_name_approximate}
payload:
  substance_kind: pure_compound
  composition_ref: cmp_01991c2e-7a10-7a02-8a01-000000000005
  constituent_entity_ids: [ent_na_plus, ent_cl_minus]
curation:
  change_reason: initial curated identity
  evidence_refs: [ev_nacl_identity]
```

### 15.4 SO2 — molecular species

```yaml
id: ent_01991c2e-7a10-7a01-8a01-000000000007
record_type: entity
schema_version: 0.1.0
record_revision: 1
status: active
entity_kind: species
semantic_keys:
  - {scheme: formula.molecular, value: SO2}
terms:
  preferred:
    - {lang: zh-CN, value: 二氧化硫}
    - {lang: en, value: sulfur dioxide}
  aliases: []
payload:
  composition_ref: cmp_01991c2e-7a10-7a02-8a01-000000000007
  formal_charge: 0
  structure_refs: [str_01991c2e-7a10-7a03-8a01-000000000007]
curation:
  change_reason: initial curated identity
  evidence_refs: [ev_so2_identity]
```

## 16. Canonical reaction example

Canonical molecular precipitation reaction:

```yaml
id: rxn_01991c2e-7a10-7a10-8a01-000000000001
record_type: reaction
schema_version: 0.1.0
record_revision: 1
status: active
canonical_status: canonical
representation: molecular
participant_refs:
  - rpart_nacl_aq_reactant
  - rpart_agno3_aq_reactant
  - rpart_agcl_s_product
  - rpart_nano3_aq_product
condition_refs: [cond_aqueous_mixing]
evidence_refs: [ev_precipitation_nacl_agno3]
```

Representative participant:

```yaml
id: rpart_nacl_aq_reactant
record_type: reaction_participant
schema_version: 0.1.0
record_revision: 1
status: active
reaction_id: rxn_01991c2e-7a10-7a10-8a01-000000000001
entity_id: ent_01991c2e-7a10-7a01-8a01-000000000005
role: reactant
coefficient: {numerator: 1, denominator: 1}
phase: aqueous
participant_qualifiers: {}
```

The compiled display may be `NaCl(aq) + AgNO3(aq) → AgCl(s)↓ + NaNO3(aq)`, but that string is not the reaction ID.

## 17. Inferred reaction candidate example

```yaml
id: rcand_01991c2e-7a10-7a11-8a01-000000000001
record_type: reaction_candidate
schema_version: 0.1.0
record_revision: 1
status: active
candidate_status: generated
proposed_participants:
  - {entity_id: ent_01991c2e-7a10-7a01-8a01-000000000005, role: reactant, coefficient: 1, phase: aqueous}
  - {entity_id: ent_agno3, role: reactant, coefficient: 1, phase: aqueous}
  - {entity_id: ent_agcl, role: product, coefficient: 1, phase: solid}
  - {entity_id: ent_nano3, role: product, coefficient: 1, phase: aqueous}
proposed_conditions:
  - cond_aqueous_mixing
provenance:
  origin: inference
  rule_ref: rule_precipitation_double_displacement
  input_entity_ids:
    - ent_01991c2e-7a10-7a01-8a01-000000000005
    - ent_agno3
  input_record_ids:
    - fact_agcl_solubility
    - fact_nano3_solubility
  derived_product_ids: [ent_agcl, ent_nano3]
  conditions_considered: [cond_aqueous_mixing]
  exceptions_checked:
    - check_id: solubility_exception_policy
      result: passed
      details: AgCl is classified insoluble under the rule context.
  validation_results:
    - {validator: atom_balance, status: passed}
    - {validator: charge_balance, status: passed}
    - {validator: participant_resolution, status: passed}
  canonical_match:
    state: exact
    reaction_id: rxn_01991c2e-7a10-7a10-8a01-000000000001
  proof_trace:
    - step: 1
      operation: exchange_ions
      inputs: [ent_nacl, ent_agno3]
      outputs: [ent_agcl, ent_nano3]
    - step: 2
      operation: evaluate_precipitation_condition
      result: ent_agcl qualifies as precipitate
    - step: 3
      operation: normalize_and_balance
      result: coefficients [1, 1, 1, 1]
  generator:
    name: hs-chem-compiler
    version: 0.1.0
    source_git_sha: example
```

This record is still a candidate despite `canonical_match.state: exact`. The canonical `rxn_*` record remains independently curated truth.

## 18. Generated/inferred record provenance contract

Any generated record, not only reaction candidates, must carry enough provenance to reproduce and audit it:

- generator name and version;
- source Git SHA or immutable input snapshot digest;
- rule/reference ID when rule-driven;
- input record IDs and entity IDs;
- context/conditions used;
- exception checks and their outcomes;
- validation results;
- proof/derivation trace at a level sufficient for deterministic re-evaluation;
- canonical-match state where the generated object may correspond to curated truth.

Generated records must not cite themselves as evidence.

## 19. Legacy migration note

Legacy `chem-knowledge-data` records can later be migrated through an adapter/staging pipeline:

1. read a legacy record without treating its path/schema as canonical;
2. resolve or mint a new opaque `ent_*` identity;
3. copy legacy names/formulas into `semantic_keys` and `terms` only where semantically valid;
4. map classification paths to independent `FacetAssertion` and/or `TeachingViewPath` records;
5. split embedded values into `PropertyFact`, `Relation`, `Reaction`, `Evidence`, and `Context` records;
6. attach migration provenance pointing to the legacy source record and migration tool version;
7. validate before promotion into curated source data.

No legacy field, directory, or identifier is required to survive as the new permanent identity. Compatibility is an adapter concern, not a constraint on this data model.
