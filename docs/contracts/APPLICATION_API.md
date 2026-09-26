# Application bundle and inference API

[简体中文](APPLICATION_API.zh-CN.md)

Compiler 0.4.0 implements offline export and a Python API. HTTP routes, the chem-wiki adapter and database migrations are not implemented.

## Publish and load

```powershell
python -m pip install .
python -m compiler.cli export --output build/application-bundle --source-revision WORKTREE
```

For a release, use a verified clean checkout and replace WORKTREE with the full `git rev-parse HEAD` SHA. The exporter does not verify that the supplied revision describes the checkout. Distribute the compiler wheel and the complete bundle with pinned versions. The wheel does not contain knowledge; the deployed loader needs no source checkout, YAML files, migration input or database.

| File | Contract |
| --- | --- |
| manifest.json | bundle_format_version 1.0.0, exact compiler version, four compatibility coordinates, source revision/digest, record counts, file SHA-256 hashes, release_id |
| knowledge.json | Complete canonical `records`: Entity, Reaction including forms, Rule, Evidence, Source, TeachingView; all facts, Relations, speciation and references retained |
| knowledge-record.schema.json | Canonical record JSON Schema; source and bundle loading share uniqueness, reference and chemistry validation |
| inference-request.schema.json | Public request JSON Schema, derived from the existing fixture shape and restricted to supported application inputs |

JSON is canonical UTF-8. File hashes include the trailing LF. The release ID is `hschem_` plus SHA-256 of canonical manifest JSON excluding release_id. Identical versions, revisions and content yield identical bytes. Loading rejects incompatible versions, checksum/count/digest mismatches and broken references, and recompiles Rules. Hashes establish integrity, not publisher authenticity; deployment must pin its trusted release.

```python
from pathlib import Path
from compiler.application import InferenceSession
from compiler.source import SourceError

session = InferenceSession(Path("build/application-bundle"))
response = session.infer({
    "id": "wiki_request_001",
    "reactants": [
        {"target_id": "ent_substance_hbr", "phase": "aqueous"},
        {"target_id": "ent_substance_na2s2o3", "phase": "aqueous"},
    ],
    "context": {"medium": "aqueous", "temperature_regime": "ambient"},
})
assert response["result"]["status"] == "inferred"
assert response["result"]["canonical_match"]["state"] == "none"
```

Load once per backend worker and reuse validated knowledge and RulePlans. Inference performs no filesystem/network reads. Do not mutate session internals; the manifest accessor returns a copy. `infer_case` is the internal execution layer, not a public request validator.

## Request

- `id` matches `^[a-z][a-z0-9_:-]+$` and correlates requests without affecting candidate chemistry identity.
- `reactants` currently accepts 1–2 canonical Entity IDs with explicit solid/liquid/gas/aqueous/dissolved/unknown phases. Repeated IDs, including across phases, are rejected rather than losing phase information.
- `context` is required but may be empty. Only `medium: aqueous` and `temperature_regime: ambient|warmed|heated|frozen` are supported. Missing conditions stay UNKNOWN; heated differs from warmed. Frozen exercises existing blockers.
- Free-text formulas, supplied products, reagent amounts/ratios, concentrations, catalysts, electrolysis, light and pressure are rejected. Stoichiometry describes the selected pathway, not limiting-reagent, excess-reagent or equilibrium behavior. Such conditions require implemented semantics before admission.
- Malformed inputs raise `SourceError(code="request_invalid", stage="request_validation")`. Unresolved canonical IDs return the chemistry outcome `invalid/reference_unresolved`.

## Response

The envelope contains `release_id`, `compiler_version`, `source_semantic_digest`, and `result`. Every result has `case_id`, `status`, and `proof_trace`. Inferred results also contain Rule ID/version, candidate_key, participants, validation, canonical_match and provenance. Participants retain role, target_id, target_kind, phase and exact numerator/denominator coefficients; never persist these via floats.

| status | Application meaning |
| --- | --- |
| inferred | Applicable Rule, resolved products and balanced atom/charge conservation; canonical_match may be none; never auto-publish |
| indeterminate | Required knowledge or conditions are absent |
| no_match | No pathway matches the current Rule scope; not proof of no chemical reaction |
| blocked | Considered pathways are condition-blocked; not global FALSE |
| ambiguous | Rule resolution has multiple unresolved winners; do not choose the first |
| invalid | Identity, product, phase evidence or conservation failure; not “no reaction” |

An aqueous ionic-pair product with absent solubility yields product_phase_unverified; known incompatible solubility yields product_phase_conflict. Both suppress candidate output. TRUE/FALSE/UNKNOWN in proof traces belong to individual predicates. A canonical_match conflict also warrants review.

## Proposed chem-wiki HTTP adapter

`POST /v1/reaction-builder/infer` should live in the existing reaction_builder owner. Map application UUIDs through the reviewed knowledge_catalog crosswalk to compiler IDs, then map results back to application DTOs. Catalog owns released facts and evidence; reaction_core owns application Reaction materialization; frontend EquationDraft owns no chemical truth.

Suggested HTTP behavior: 200 for all six chemistry outcomes; 422 for invalid requests or unmapped UUIDs; failed startup/503 for unavailable pinned bundles. Avoid exposing local paths. Keep detailed traces expandable. See the [Chinese integration/database note](CHEM_WIKI_INTEGRATION.md) for table reuse, exact coefficients, idempotency and rollback constraints.
