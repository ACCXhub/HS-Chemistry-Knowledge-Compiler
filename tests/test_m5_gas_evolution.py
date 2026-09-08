from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml

from compiler.build import audit_repository
from compiler.engine import infer_case
from compiler.reaction_forms import derive_aqueous_ionic_form
from compiler.rules import analyze_rule_overlaps, compile_rules
from compiler.source import load_knowledge


ROOT = Path(__file__).resolve().parents[1]
RULE_ID = "rule_m5_strong_acid_hydrogen_carbonate_gas_evolution"


def _case(case_id: str, acid_id: str, *, include_medium: bool = True) -> dict:
    context = {"temperature_regime": "ambient"}
    if include_medium:
        context["medium"] = "aqueous"
    return {
        "id": case_id,
        "reactants": [
            {"target_id": acid_id, "phase": "aqueous"},
            {"target_id": "ent_substance_nahco3", "phase": "aqueous"},
        ],
        "context": context,
    }


def _normalized(participants: list[dict]) -> list[tuple[str, str, int, int]]:
    return sorted(
        (
            item["role"],
            item["target_id"],
            item["coefficient"]["numerator"],
            item["coefficient"]["denominator"],
        )
        for item in participants
    )


@pytest.mark.parametrize(
    ("acid_id", "reaction_id", "salt_id"),
    [
        ("ent_substance_hcl", "rxn_f3b_hcl_nahco3_gas_evolution", "ent_substance_nacl"),
        ("ent_substance_hno3", "rxn_m5_hno3_nahco3_gas_evolution", "ent_substance_nano3"),
    ],
)
def test_two_strong_acids_reuse_one_hydrogen_carbonate_rule(
    acid_id: str,
    reaction_id: str,
    salt_id: str,
) -> None:
    kb = load_knowledge(ROOT)
    result = infer_case(kb, compile_rules(kb), _case(reaction_id, acid_id))

    assert result["status"] == "inferred"
    assert result["rule_id"] == RULE_ID
    assert result["canonical_match"] == {
        "state": "exact",
        "reaction_ids": [reaction_id],
        "reaction_forms": {reaction_id: ["molecular", "complete_ionic", "net_ionic"]},
    }
    assert result["validation"] == {"atoms": True, "charge": True}
    assert _normalized(result["participants"]) == sorted(
        [
            ("reactant", acid_id, 1, 1),
            ("reactant", "ent_substance_nahco3", 1, 1),
            ("product", salt_id, 1, 1),
            ("product", "ent_substance_co2", 1, 1),
            ("product", "ent_substance_h2o", 1, 1),
        ]
    )
    profiles = result["provenance"]["speciation_profiles"]
    assert {item["target_id"] for item in profiles} == {acid_id, "ent_substance_nahco3"}
    assert all(item["profile_key"] == "aqueous_complete_dissociation" for item in profiles)
    assert all(item["model"] == "strong_electrolyte_complete_dissociation" for item in profiles)
    assert all(item["evidence_ids"] for item in profiles)


def test_gas_evolution_net_ionic_form_is_acid_independent_and_matches_golden() -> None:
    kb = load_knowledge(ROOT)
    expected = sorted(
        [
            ("reactant", "ent_species_h_plus", 1, 1),
            ("reactant", "ent_species_hco3_minus", 1, 1),
            ("product", "ent_substance_co2", 1, 1),
            ("product", "ent_substance_h2o", 1, 1),
        ]
    )
    for reaction_id in (
        "rxn_f3b_hcl_nahco3_gas_evolution",
        "rxn_m5_hno3_nahco3_gas_evolution",
    ):
        derived = derive_aqueous_ionic_form(kb, reaction_id, "net_ionic", {"medium": "aqueous"})
        golden = next(form for form in kb.reactions[reaction_id]["forms"] if form["form_kind"] == "net_ionic")
        assert derived["status"] == "derived"
        assert derived["reaction_id"] == reaction_id
        assert derived["validation"] == {"atoms": True, "charge": True}
        assert _normalized(derived["participants"]) == expected
        assert _normalized(derived["participants"]) == _normalized(golden["participants"])
        assert {item["target_id"] for item in derived["derivation"]["speciation_profiles"]} == {
            "ent_substance_nahco3",
            kb.reactions[reaction_id]["participants"][0]["target_id"],
            kb.reactions[reaction_id]["participants"][2]["target_id"],
        }


def test_missing_aqueous_context_keeps_gas_evolution_applicability_unknown() -> None:
    kb = load_knowledge(ROOT)
    result = infer_case(kb, compile_rules(kb), _case("missing-medium", "ent_substance_hcl", include_medium=False))

    assert result["status"] == "indeterminate"
    assert result["diagnostic"]["code"] == "unknown_applicability"
    assert "candidate_key" not in result
    assert any(
        event["event"] == "predicate.eval"
        and event["rule_id"] == RULE_ID
        and event["subject"] == "context"
        and event["key"] == "medium"
        and event["truth"] == "UNKNOWN"
        for event in result["proof_trace"]
    )


def test_missing_strong_acid_fact_keeps_gas_evolution_applicability_unknown(tmp_path: Path) -> None:
    work = tmp_path / "repo"
    shutil.copytree(ROOT, work)
    path = work / "knowledge" / "domain" / "f3b_aqueous_entities.yaml"
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    acid = next(record for record in document["records"] if record.get("id") == "ent_substance_hno3")
    acid["property_assertions"] = [
        assertion for assertion in acid["property_assertions"] if assertion["property_key"] != "acid.strength"
    ]
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")

    kb = load_knowledge(work)
    result = infer_case(kb, compile_rules(kb), _case("unknown-acid-strength", "ent_substance_hno3"))
    assert result["status"] == "indeterminate"
    assert "candidate_key" not in result
    assert any(
        event["event"] == "predicate.eval"
        and event["rule_id"] == RULE_ID
        and event["binding"] == "acid"
        and event["key"] == "acid.strength"
        and event["truth"] == "UNKNOWN"
        for event in result["proof_trace"]
    )


def test_teaching_view_contains_both_reusable_gas_evolution_cases() -> None:
    view = load_knowledge(ROOT).teaching_views["view_f3b_hs_aqueous_core"]
    gas_node = next(node for node in view["nodes"] if node["path_key"] == "D03/reaction-types/gas-evolution")
    assert set(gas_node["members"]) == {
        "rxn_f3b_hcl_nahco3_gas_evolution",
        "rxn_m5_hno3_nahco3_gas_evolution",
        "rxn_m6_hcl_na2co3_gas_evolution",
        "rxn_m6_hno3_na2co3_gas_evolution",
        "rxn_m6_hcl_k2co3_gas_evolution",
        "rxn_m7_nh4cl_naoh_ammonia_liberation",
        "rxn_m7_nh4_2so4_naoh_ammonia_liberation",
    }


def test_audit_executes_m5_positive_and_unknown_cases(tmp_path: Path) -> None:
    audit = audit_repository(ROOT, tmp_path / "audit", "m5-fixture")
    results = {result["case_id"]: result for result in audit["results"]}
    assert results["case_m5_hcl_nahco3"]["status"] == "inferred"
    assert results["case_m5_hno3_nahco3"]["status"] == "inferred"
    assert results["case_m5_hcl_nahco3_unknown_medium"]["status"] == "indeterminate"
    assert results["case_m5_hcl_nahco3"]["rule_id"] == RULE_ID
    assert results["case_m5_hno3_nahco3"]["rule_id"] == RULE_ID


def test_gas_evolution_rule_resolves_acid_family_overlap_explicitly() -> None:
    overlaps = analyze_rule_overlaps(compile_rules(load_knowledge(ROOT)))
    overlap = next(
        item
        for item in overlaps
        if set(item["rule_ids"])
        == {RULE_ID, "rule_f2_strong_acid_base_neutralization"}
    )
    assert overlap["relationships"] == ["specializes"]
