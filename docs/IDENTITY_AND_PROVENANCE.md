# Identity and Provenance

Status: **draft canonical policy for `workstream/data-contracts`**

This document defines how records are identified, renamed, reconciled, versioned, evidenced, derived, and audited.

## 1. Identity requirements

Permanent identity must survive changes to:

- Chinese or English names;
- aliases and spelling;
- displayed chemical formula;
- preferred structural notation;
- ontology/facet classification;
- textbook chapter or D01-D11 path;
- source-file location;
- compiler output layout.

Therefore these values are forbidden as permanent IDs.

## 2. Alternatives considered

| Policy | Advantages | Failure mode | Decision |
|---|---|---|---|
| name/formula slug (`h2so4`, `sulfuric-acid`) | readable | names/formulas are presentation/semantic keys; collisions and corrections are inevitable | reject |
| ontology/path ID (`D08/...`) | easy navigation | identity changes when teaching structure changes; conflates curriculum with chemistry | reject |
| external registry ID as primary (CAS, InChIKey, PubChem CID, etc.) | useful reconciliation | incomplete coverage for ions, mixtures, abstractions and teaching entities; external semantics may differ | reject as primary; keep as semantic/external keys |
| deterministic UUIDv5 from a semantic key | reproducible | identity changes when the seed semantic key is corrected; forces one canonical key too early | reject as general primary ID |
| random UUIDv4 | opaque and stable | no locality/creation ordering | acceptable but not preferred |
| UUIDv7 with a type prefix | opaque, stable, globally unique, roughly time sortable, hierarchy-free | creation time is observable; still requires semantic keys for human lookup | **chosen** |

## 3. Chosen ID policy

Use a short **record-kind prefix + lowercase UUIDv7**.

Examples:

```text
ent_01991c2e-7a10-7a01-8a01-000000000003
fact_01991c2e-7a10-7a08-8a01-000000000001
rxn_01991c2e-7a10-7a10-8a01-000000000001
rcand_01991c2e-7a10-7a11-8a01-000000000001
```

The prefix describes only the record class. It does **not** encode chemistry hierarchy.

Recommended prefixes:

| Record | Prefix |
|---|---|
| Entity | `ent_` |
| Composition | `cmp_` |
| StructureReference | `str_` |
| FacetAssertion | `fas_` |
| PropertyFact | `fact_` |
| Context | `ctx_` |
| Relation | `rel_` |
| Reaction | `rxn_` |
| ReactionParticipant | `rpart_` |
| Condition | `cond_` |
| Source | `src_` |
| Evidence | `ev_` |
| TeachingView | `view_` |
| TeachingViewPath | `path_` |
| RuleReference | `rule_` |
| ReactionCandidate | `rcand_` |

Rules:

1. IDs are minted once and never regenerated from current record content.
2. File moves and renames do not affect IDs.
3. A corrected semantic key does not affect the ID.
4. A split of one incorrectly conflated concept into two concepts creates at least one new ID and records the replacement relationship explicitly.
5. IDs are not recycled after withdrawal.
6. A compiler may validate UUID version/prefix compatibility but must not infer chemistry meaning from an ID.

## 4. Identity vs semantic keys

A permanent ID answers: **which conceptual record is this?**

A semantic key answers: **by which chemistry-aware scheme can this record be found or reconciled?**

Example:

```yaml
id: ent_01991c2e-7a10-7a01-8a01-000000000001
semantic_keys:
  - {scheme: element.atomic_number, value: "26"}
  - {scheme: element.symbol, value: Fe}
```

Suggested semantic-key schemes include:

- `element.atomic_number`;
- `element.symbol`;
- `formula.molecular`;
- `formula.stoichiometric`;
- `inchi` / `inchikey` where appropriate;
- trusted external database identifiers;
- legacy identifiers under an explicit namespace such as `legacy.chem_knowledge_data`.

A semantic key must declare its scheme. Bare strings such as `SO2` are not globally meaningful enough to serve as unique identifiers.

## 5. Alias policy

Aliases are language/search/display metadata attached to an entity or other named record.

```yaml
terms:
  preferred:
    - {lang: zh-CN, value: 二氧化硫}
  aliases:
    - lang: zh-CN
      value: 亚硫酸酐
      scope: historical_or_teaching
      deprecated: false
```

Alias equality does not imply entity equality. Importers must resolve aliases through a reconciliation step rather than automatically merging records with the same text.

## 6. Teaching path policy

Teaching paths are maintained only by `TeachingView` and `TeachingViewPath` records.

```text
D08/substances/inorganic/acids
```

is allowed as `TeachingViewPath.path_key`; it is forbidden as an `Entity.id` or `Reaction.id`.

The path may be reorganized, localized, or replaced while every referenced `ent_*`, `fact_*`, `rel_*`, and `rxn_*` remains stable.

## 7. Record revision and schema version

Two independent version axes exist:

### 7.1 `schema_version`

Describes the contract shape expected by validators and compilers.

```yaml
schema_version: 0.1.0
```

A schema migration can update many records without changing their chemical identity.

### 7.2 `record_revision`

A monotonically increasing integer for semantic edits to one stable record.

```yaml
record_revision: 3
```

Examples that should increment `record_revision`:

- correcting a stoichiometric coefficient;
- changing a preferred name because the curated record itself changed;
- adding/removing an evidence-supported fact qualifier;
- changing a reaction condition;
- withdrawing an invalid semantic key.

Git remains the complete historical store. `record_revision` is not a substitute for Git commits.

## 8. Lifecycle changes

Top-level records use:

```yaml
status: active   # active | deprecated | withdrawn
```

When replacement semantics matter, record explicit links in curation metadata:

```yaml
curation:
  change_reason: split previously conflated material and molecular species
  replaces_ids: []
  replaced_by_ids: [ent_..., ent_...]
  evidence_refs: [ev_...]
```

Deprecation does not permit ID reuse.

## 9. Source and evidence model

`Source` identifies a publication/database/manual/web resource. `Evidence` points to a specific claim-bearing location in that source.

This separation allows one source to support many assertions and one assertion to cite multiple independent evidence records.

### 9.1 Source example

```yaml
id: src_01991c2e-7a10-7a20-8a01-000000000001
record_type: source
schema_version: 0.1.0
record_revision: 1
status: active
source_type: textbook
citation:
  title: Example Chemistry Textbook
  authors: [Example Author]
  publisher: Example Publisher
  year: 2026
identifiers: []
url: null
```

### 9.2 Evidence example

```yaml
id: ev_01991c2e-7a10-7a21-8a01-000000000001
record_type: evidence
schema_version: 0.1.0
record_revision: 1
status: active
source_id: src_01991c2e-7a10-7a20-8a01-000000000001
locator:
  page: 42
  section: "2.3"
claim_summary: "The cited passage supports the target assertion."
stance: supports
extraction_method: manual
```

`claim_summary` is an audit aid, not a replacement for structured chemistry fields.

## 10. Assertion provenance requirements

Every nontrivial curated assertion must have at least one of:

1. `evidence_refs` pointing to evidence records; or
2. a derivation/provenance object whose inputs ultimately resolve to auditable source assertions.

This applies to:

- facet assertions;
- property facts;
- contextual facts;
- relations;
- reaction conditions;
- canonical reactions;
- rule definitions.

Minimal deterministic identity invariants such as an internally validated UUID do not need external evidence. Chemistry claims do.

## 11. Intrinsic, contextual, and derived facts

### Intrinsic

The assertion is modeled as belonging to the entity itself under the contract, for example element atomic number or formal charge.

### Contextual

The assertion is qualified by a `ctx_*` record. Typical qualifiers:

- phase;
- temperature;
- pressure;
- solvent;
- concentration;
- pH;
- ionic strength;
- measurement method;
- teaching approximation scope where explicitly needed.

### Derived

The assertion is generated from other records or a rule and must carry derivation data:

```yaml
derivation:
  origin: compiler
  rule_ref: rule_...
  input_record_ids: [fact_..., rel_...]
  proof_trace:
    - operation: normalize
    - operation: compute
```

A derived fact is not silently rewritten as source truth. A curator may later author an independently evidenced intrinsic/contextual fact if appropriate.

## 12. Knowledge-state semantics

The data model deliberately distinguishes four cases:

```yaml
# 1. No record at all: no assertion in this dataset.

# 2. Explicit unknown:
value_state: unknown

# 3. Not applicable:
value_state: not_applicable

# 4. Known false:
value_state: known
value: false
```

Compilers and APIs must preserve this distinction. `unknown` is not falsy chemistry.

## 13. Generated/inferred provenance

Generated records require an immutable-enough audit trail to reproduce how they were obtained.

For a rule-driven record, provenance includes:

```yaml
provenance:
  origin: inference
  rule_ref: rule_...
  input_entity_ids: [ent_...]
  input_record_ids: [fact_..., rel_...]
  derived_product_ids: [ent_...]
  conditions_considered: [cond_...]
  exceptions_checked:
    - check_id: some_exception
      result: passed
      details: "..."
  validation_results:
    - validator: atom_balance
      status: passed
      details: null
  proof_trace:
    - step: 1
      operation: "..."
      inputs: []
      outputs: []
  generator:
    name: hs-chem-compiler
    version: 0.1.0
    source_git_sha: "<source snapshot commit>"
```

The compiler may additionally include content digests of normalized inputs to detect accidental non-reproducibility.

## 14. ReactionCandidate provenance and canonical matching

A `ReactionCandidate` must preserve all of the following:

- origin;
- `rule_ref` / stable `rule_id`;
- input entities;
- input records/facts used;
- proposed/derived products;
- conditions considered;
- exception checks and outcomes;
- validators run and results;
- proof trace;
- generator version and source snapshot;
- canonical match state.

Canonical match state is explicit:

```yaml
canonical_match:
  state: exact       # unchecked | none | exact | equivalent | ambiguous | conflict
  reaction_id: rxn_...
```

An `exact` or `equivalent` match does **not** change the candidate's record type or ID. It only says that comparison found a canonical record.

## 15. Canonical promotion gate

There is no automatic `rcand_* -> rxn_*` mutation.

The only valid canonicalization flow is conceptually:

```text
ReactionCandidate
    -> validation/review evidence
    -> explicit curator decision
    -> create/update canonical Reaction source record
    -> preserve candidate provenance and canonical match
```

If a canonical reaction already exists, the candidate links to it. If none exists, a curator may author a new `rxn_*` record using evidence. The candidate itself remains generated history/staging material.

## 16. Compiler manifest provenance

Every reproducible build should emit a manifest similar to:

```json
{
  "compiler": "hs-chem-compiler",
  "compiler_version": "0.1.0",
  "schema_version": "0.1.0",
  "source_git_sha": "<commit>",
  "source_digest": "sha256:<normalized-source-digest>",
  "outputs": [
    {"path": "generated/entities.jsonl", "sha256": "..."}
  ]
}
```

The manifest lets a consumer answer: **which exact source snapshot and compiler produced this artifact?**

## 17. Legacy migration provenance

Legacy identifiers may be retained only as namespaced semantic/migration keys:

```yaml
semantic_keys:
  - scheme: legacy.chem_knowledge_data
    value: "<legacy-id>"
```

or in migration provenance:

```yaml
migration:
  origin_system: chem-knowledge-data
  source_record_key: "<legacy key>"
  migration_tool_version: 1
```

They are not promoted to new permanent IDs. A migration adapter may map many legacy records to one new entity or split one legacy record into multiple new records when the old architecture conflated concepts.
