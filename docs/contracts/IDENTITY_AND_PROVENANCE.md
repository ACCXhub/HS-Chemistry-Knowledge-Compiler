# Identity and Provenance

Status: **F1 canonical policy**

## 1. Identity rule

Stable identity is independent from names, aliases, formula display, classification, curriculum path, file path, YAML ordering, and runtime representation.

Opaque durable IDs are used only when an object/assertion has an independent lifecycle or requires durable external reference.

## 2. Semantic keys

Semantic keys support lookup, reconciliation, validation, and migration. They do not replace permanent identity. Examples include atomic number, element symbol, curated registry keys, and canonicalized notation keys.

## 3. Provenance

Curated knowledge records carry evidence and curation history appropriate to their lifecycle. Derived/generated outputs carry derivation provenance including source revision, rule identity/version, inputs, validation, and compiler revision.

## 4. Candidate provenance

A deterministic candidate key is part of generated semantic identity. It is reproducible from canonical semantic content and declared derivation inputs.

A persistent review ID identifies a review workflow object, not the pure compiler output.

## 5. Migration

Legacy IDs and paths are migration aliases only. Migration may merge multiple legacy records into one canonical record or split a conflated legacy record into multiple canonical identities.

No legacy schema field is required to survive as a permanent canonical field.

The migration layer owns only a durable legacy-to-canonical crosswalk or an explicit bounded disposition (`mapped_existing`, `created_canonical`, `skipped_unsupported`, `ambiguous`, or `rejected_invalid`). Formula, name, and legacy path may locate candidates but cannot establish identity without referent-level kind, composition, charge, symbol, or atomic-number checks as applicable. Ambiguity never selects a winner by record or file order.

Canonical creation remains a separate evidence-gated source-curation action. Legacy `reviewed` state, consolidation readiness, editorial sources, and verification targets are not authoritative evidence. Migration status does not enter Entity aliases, Rule DSL, or compiled inference artifacts.

`migration/legacy_identity.py` is the single canonical owner of offline identity reconciliation and deterministic crosswalk generation. Milestone-specific cohort manifests and immutable reports may remain separate; compatibility entry points must delegate to this owner rather than implement parallel matching semantics.
