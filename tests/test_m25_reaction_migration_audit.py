from __future__ import annotations

import hashlib
import json
from pathlib import Path

from compiler.engine import canonical_reaction_index, compare_canonical_reactions, infer_case
from compiler.reaction_forms import derive_aqueous_ionic_form
from compiler.rules import compile_rules
from compiler.source import load_knowledge


ROOT = Path(__file__).resolve().parents[1]
REACTION_ID = "rxn_m25_hcl_caco3_gas_evolution"


def _report(name: str = "m25_reaction_audit_report.json") -> dict:
    return json.loads((ROOT / "migration" / "reports" / name).read_text(encoding="utf-8"))


def test_full_audit_covers_every_legacy_reaction_with_closed_outcomes() -> None:
    report = _report()

    assert report["milestone"] == "M25"
    assert report["audit_scope"] == "full_corpus"
    assert report["input_summary"]["selected_count"] == 152
    assert report["input_summary"]["by_family"] == {"reaction": 152}
    assert report["input_summary"]["full_input_sha256"] == report["input_summary"][
        "selected_records_sha256"
    ]
    assert report["disposition_counts"] == {
        "ambiguous": 0,
        "created_canonical": 0,
        "mapped_existing": 20,
        "rejected_invalid": 9,
        "skipped_unsupported": 123,
    }
    assert report["future_action_bucket_counts"] == {
        "chemistry_architecture_gap": 9,
        "context_gap": 25,
        "curation_gap": 10,
        "identity_gap": 88,
        "invalid_legacy": 0,
    }
    assert report["m6_exit_ready"] is True
    assert len(report["decisions"]) == 152
    assert len({item["legacy_id"] for item in report["decisions"]}) == 152
    assert not any(item["disposition"] == "created_canonical" for item in report["decisions"])
    assert all(
        "future_action_bucket" in item
        for item in report["decisions"]
        if item["disposition"] != "mapped_existing"
    )
    assert "C:\\" not in json.dumps(report)


def test_future_action_buckets_preserve_the_first_auditable_blocker() -> None:
    decisions = {item["legacy_id"]: item for item in _report()["decisions"]}

    assert decisions["reaction:ag2co3-thermal"]["future_action_bucket"] == "identity_gap"
    assert decisions["reaction:ammonia-catalytic-oxidation"]["future_action_bucket"] == (
        "context_gap"
    )
    assert decisions["reaction:ammonia-catalytic-oxidation"]["reason_code"] == (
        "unsupported_condition"
    )
    assert decisions["reaction:chlorine-water"]["future_action_bucket"] == (
        "chemistry_architecture_gap"
    )
    assert decisions["reaction:chlorine-water"]["reason_code"] == (
        "reversible_reaction_not_supported"
    )
    assert decisions["reaction:ammonia-hydrogen-chloride"]["future_action_bucket"] == (
        "curation_gap"
    )
    assert decisions["reaction:ammonia-hydrogen-chloride"]["reason_code"] == (
        "canonical_reaction_no_match"
    )


def test_bounded_caco3_curation_maps_without_legacy_authority() -> None:
    kb = load_knowledge(ROOT)
    reaction = kb.reactions[REACTION_ID]
    decision = next(
        item
        for item in _report()["decisions"]
        if item["legacy_id"] == "reaction:calcium-carbonate-hcl"
    )

    assert decision["disposition"] == "mapped_existing"
    assert decision["canonical_id"] == REACTION_ID
    assert decision["conservation"] == {"atoms": True, "charge": True}
    assert len(reaction["participants"]) == 5
    assert reaction["forms"] == []
    assert all(
        kb.sources[kb.evidence[evidence_id]["source_id"]]["source_type"] != "fixture"
        for evidence_id in reaction["evidence_ids"]
    )

    comparison = compare_canonical_reactions(
        kb, reaction["participants"], {"medium": "aqueous"}
    )
    assert comparison["state"] == "exact"
    assert comparison["reaction_ids"] == [REACTION_ID]
    signature = next(
        key
        for key, reaction_ids in canonical_reaction_index(kb).items()
        if REACTION_ID in reaction_ids
    )
    assert canonical_reaction_index(kb)[signature] == [REACTION_ID]


def test_caco3_forms_are_derived_but_existing_soluble_rule_is_not_weakened() -> None:
    kb = load_knowledge(ROOT)
    context = {"medium": "aqueous"}

    for form_kind in ("complete_ionic", "net_ionic"):
        form = derive_aqueous_ionic_form(kb, REACTION_ID, form_kind, context)
        assert form["status"] == "derived"
        assert form["validation"] == {"atoms": True, "charge": True}

    inference = infer_case(
        kb,
        compile_rules(kb),
        {
            "id": "m25-solid-caco3-hcl",
            "reactants": [
                {"target_id": "ent_substance_hcl", "phase": "aqueous"},
                {"target_id": "ent_substance_caco3", "phase": "solid"},
            ],
            "context": {"medium": "aqueous", "temperature_regime": "ambient"},
        },
    )
    assert inference["status"] == "indeterminate"
    assert "rule_id" not in inference
    assert len(compile_rules(kb)) == 14


def test_reaction_form_diagnostics_are_not_a_mapping_kpi() -> None:
    mapped = [item for item in _report()["decisions"] if item["disposition"] == "mapped_existing"]
    states = [item["reaction_form_comparison"]["state"] for item in mapped]

    assert states.count("compatible") == 1
    assert states.count("unavailable") == 12
    assert states.count("unsupported_inconsistent") == 7
    assert all("reaction_form" not in item["canonical_match_basis"] for item in mapped)


def test_m24_historical_report_is_unchanged_and_runtime_remains_isolated() -> None:
    m24_path = ROOT / "migration" / "reports" / "m24_reaction_pilot_report.json"
    normalized_bytes = m24_path.read_bytes().replace(b"\r\n", b"\n")
    assert hashlib.sha256(normalized_bytes).hexdigest() == (
        "7e650fc0778db066231d7c1652a40ee86514adcca3550317d97b2126a8593c7b"
    )

    for path in (ROOT / "compiler").glob("*.py"):
        source = path.read_text(encoding="utf-8")
        assert "from migration" not in source
        assert "import migration" not in source
