from __future__ import annotations

import copy
import json
from pathlib import Path

from compiler.source import load_knowledge
from migration.m22_legacy_pilot import build_report, reconcile_record, report_bytes


ROOT = Path(__file__).resolve().parents[1]


def _ion_record() -> dict:
    return {
        "id": "ion:sodium",
        "kind": "ion",
        "name_en": "deliberately not authoritative",
        "formula": "wrong lookup label",
        "charge": 1,
        "composition": {"Na": 1},
        "ion_type": "monatomic",
    }


def test_reconciliation_uses_referent_facts_and_stops_on_ambiguity() -> None:
    kb = load_knowledge(ROOT)
    policy = {"intent": "reconcile"}

    mapped = reconcile_record("ion", _ion_record(), kb.entities, kb.evidence, kb.sources, policy)
    assert mapped["disposition"] == "mapped_existing"
    assert mapped["canonical_id"] == "ent_species_na_plus"

    entities = dict(kb.entities)
    duplicate = copy.deepcopy(entities["ent_species_na_plus"])
    duplicate["id"] = "ent_species_na_plus_duplicate_for_test"
    entities[duplicate["id"]] = duplicate
    ambiguous = reconcile_record("ion", _ion_record(), entities, kb.evidence, kb.sources, policy)
    assert ambiguous["disposition"] == "ambiguous"
    assert ambiguous["reason_code"] == "multiple_verified_canonical_matches"
    assert ambiguous["candidate_ids"] == [
        "ent_species_na_plus",
        "ent_species_na_plus_duplicate_for_test",
    ]


def test_invalid_legacy_shape_is_rejected_without_guessing() -> None:
    kb = load_knowledge(ROOT)
    invalid = _ion_record()
    invalid["charge"] = "1+"
    invalid.pop("composition")

    decision = reconcile_record(
        "ion", invalid, kb.entities, kb.evidence, kb.sources, {"intent": "reconcile"}
    )
    assert decision["disposition"] == "rejected_invalid"
    assert decision["reason_code"] == "invalid_legacy_record"


def test_report_is_order_independent_and_idempotent() -> None:
    kb = load_knowledge(ROOT)
    records = [
        {
            "id": "element-scope:na",
            "kind": "element_scope",
            "symbol": "Na",
            "atomic_number": 11,
        },
        _ion_record(),
    ]
    cohort = [
        {"legacy_id": "element-scope:na", "record_family": "element_scope", "intent": "reconcile"},
        {"legacy_id": "ion:sodium", "record_family": "ion", "intent": "reconcile"},
    ]
    before_ids = tuple(sorted(kb.entities))

    first = build_report(
        records,
        cohort,
        kb,
        legacy_revision="a" * 40,
        legacy_manifest={"package": "inorganic", "version": "test"},
        input_files=["data/ions.jsonl", "data/element_scope.jsonl"],
    )
    second = build_report(
        list(reversed(records)),
        list(reversed(cohort)),
        kb,
        legacy_revision="a" * 40,
        legacy_manifest={"version": "test", "package": "inorganic"},
        input_files=list(reversed(["data/ions.jsonl", "data/element_scope.jsonl"])),
    )

    assert report_bytes(first) == report_bytes(second)
    assert tuple(sorted(kb.entities)) == before_ids


def test_tracked_real_pilot_report_and_created_entity_are_auditable() -> None:
    kb = load_knowledge(ROOT)
    report_path = ROOT / "migration" / "reports" / "m22_pilot_report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert report["input_summary"]["selected_count"] == 20
    assert report["disposition_counts"] == {
        "ambiguous": 0,
        "created_canonical": 1,
        "mapped_existing": 16,
        "rejected_invalid": 0,
        "skipped_unsupported": 3,
    }
    assert len({item["legacy_id"] for item in report["decisions"]}) == 20

    created = [item for item in report["decisions"] if item["disposition"] == "created_canonical"]
    assert created == [
        next(item for item in report["decisions"] if item["legacy_id"] == "element-scope:li")
    ]
    assert created[0]["canonical_id"] == "ent_element_li"
    assert kb.entities["ent_element_li"]["payload"] == {"atomic_number": 3, "symbol": "Li"}
    assert kb.entities["ent_element_li"]["evidence_ids"] == ["ev_m22_lithium_identity"]
    evidence = kb.evidence["ev_m22_lithium_identity"]
    assert kb.sources[evidence["source_id"]]["source_type"] != "fixture"

    element_li = [
        entity_id
        for entity_id, entity in kb.entities.items()
        if entity.get("entity_kind") == "element"
        and entity.get("payload", {}).get("symbol") == "Li"
        and entity.get("payload", {}).get("atomic_number") == 3
    ]
    assert element_li == ["ent_element_li"]
