from __future__ import annotations

import json
from pathlib import Path

from compiler.source import load_knowledge
from migration import legacy_identity, m22_legacy_pilot


ROOT = Path(__file__).resolve().parents[1]


def _report(name: str) -> dict:
    return json.loads((ROOT / "migration" / "reports" / name).read_text(encoding="utf-8"))


def test_m23_reuses_one_canonical_migration_engine() -> None:
    assert m22_legacy_pilot.reconcile_record is legacy_identity.reconcile_record
    assert m22_legacy_pilot.build_report is legacy_identity.build_report
    assert m22_legacy_pilot.run_pilot is legacy_identity.run_identity_batch


def test_m23_real_batch_is_explicit_bounded_and_auditable() -> None:
    report = _report("m23_identity_batch_report.json")

    assert report["milestone"] == "M23"
    assert report["input_summary"]["selected_count"] == 100
    assert report["input_summary"]["by_family"] == {
        "element_scope": 48,
        "ion": 32,
        "substance": 20,
    }
    assert report["disposition_counts"] == {
        "ambiguous": 0,
        "created_canonical": 0,
        "mapped_existing": 45,
        "rejected_invalid": 0,
        "skipped_unsupported": 55,
    }
    assert len(report["decisions"]) == len({item["legacy_id"] for item in report["decisions"]})
    assert not any(item["disposition"] == "created_canonical" for item in report["decisions"])
    assert "C:\\" not in json.dumps(report)


def test_m23_strict_substance_profile_does_not_merge_on_composition_alone() -> None:
    kb = load_knowledge(ROOT)
    legacy_record = {
        "id": "substance:synthetic-not-sodium-chloride",
        "kind": "substance",
        "name_en": "not sodium chloride",
        "formula": "DifferentReferent",
        "composition": {"Na": 1, "Cl": 1},
    }
    policy = {
        "identity_profile": "strict_simple_substance_v1",
        "intent": "reconcile",
        "referent_shape": "simple_neutral_pure_compound",
    }

    decision = legacy_identity.reconcile_record(
        "substance", legacy_record, kb.entities, kb.evidence, kb.sources, policy
    )
    assert decision["disposition"] == "skipped_unsupported"
    assert decision["reason_code"] == "no_verified_canonical_match"


def test_m23_risky_referent_shapes_remain_explicit_skips() -> None:
    decisions = {item["legacy_id"]: item for item in _report("m23_identity_batch_report.json")["decisions"]}
    expected = {
        "substance:carbonic-acid": "weak_equilibrium_aqueous_referent_not_owned",
        "substance:iron-iii-thiocyanate": "complex_speciation_referent_ambiguous",
        "substance:silicon-dioxide": "network_referent_shape_not_owned",
        "substance:sulfur": "allotrope_referent_not_explicit",
    }
    for legacy_id, reason_code in expected.items():
        assert decisions[legacy_id]["disposition"] == "skipped_unsupported"
        assert decisions[legacy_id]["reason_code"] == reason_code


def test_m22_crosswalk_continuity_and_no_duplicate_m23_targets() -> None:
    m22 = {item["legacy_id"]: item for item in _report("m22_pilot_report.json")["decisions"]}
    m23 = {item["legacy_id"]: item for item in _report("m23_identity_batch_report.json")["decisions"]}

    for legacy_id in sorted(set(m22) & set(m23)):
        if legacy_id == "element-scope:li":
            assert m22[legacy_id]["disposition"] == "created_canonical"
            assert m23[legacy_id]["disposition"] == "mapped_existing"
            assert m22[legacy_id]["canonical_id"] == m23[legacy_id]["canonical_id"]
        else:
            assert m22[legacy_id]["disposition"] == m23[legacy_id]["disposition"]
            assert m22[legacy_id].get("canonical_id") == m23[legacy_id].get("canonical_id")

    mapped_ids = [
        item["canonical_id"]
        for item in m23.values()
        if item["disposition"] == "mapped_existing"
    ]
    assert len(mapped_ids) == len(set(mapped_ids))


def test_compiler_runtime_has_no_migration_dependency() -> None:
    for path in (ROOT / "compiler").glob("*.py"):
        source = path.read_text(encoding="utf-8")
        assert "from migration" not in source
        assert "import migration" not in source
