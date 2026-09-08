from __future__ import annotations

import copy
import shutil
from pathlib import Path

import pytest
import yaml

from compiler.balance import BalanceError, balance
from compiler.engine import infer_case
from compiler.reaction_forms import derive_aqueous_ionic_form, project_reaction_form
from compiler.rules import compile_rules
from compiler.source import SourceError, load_knowledge


ROOT = Path(__file__).resolve().parents[1]


def _case(case_id: str, left: str, right: str) -> dict:
    return {
        "id": case_id,
        "reactants": [
            {"target_id": left, "phase": "aqueous"},
            {"target_id": right, "phase": "aqueous"},
        ],
        "context": {"medium": "aqueous", "temperature_regime": "ambient"},
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


def test_structured_contextual_property_preserves_true_false_unknown(tmp_path: Path) -> None:
    kb = load_knowledge(ROOT)
    aqueous = kb.property_fact("ent_substance_hno3", "electrolyte.strength", {"medium": "aqueous"})
    assert aqueous.state.value == "known"
    assert aqueous.value == "strong"
    assert aqueous.origin == "contextual"
    assert aqueous.context == (("medium", "aqueous"),)

    missing_context = kb.property_fact("ent_substance_hno3", "electrolyte.strength", {"medium": "gas"})
    assert missing_context.state.value == "absent"

    work = tmp_path / "repo"
    shutil.copytree(ROOT, work)
    path = work / "knowledge" / "domain" / "f3b_aqueous_entities.yaml"
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    entity = next(record for record in doc["records"] if record.get("id") == "ent_substance_hno3")
    entity["property_assertions"].append(
        {
            "property_key": "fixture.flag",
            "value_state": "known",
            "value": False,
            "fact_kind": "contextual",
            "context": {"medium": "aqueous"},
            "evidence_ids": ["ev_f3b_strong_acid_base"],
        }
    )
    path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
    changed = load_knowledge(work)
    known_false = changed.property_fact("ent_substance_hno3", "fixture.flag", {"medium": "aqueous"})
    assert known_false.state.value == "known"
    assert known_false.value is False
    assert changed.property_fact("ent_substance_hno3", "fixture.absent", {"medium": "aqueous"}).state.value == "absent"


def test_old_context_in_facet_key_is_not_required_for_migrated_truth() -> None:
    kb = load_knowledge(ROOT)
    hno3 = kb.entities["ent_substance_hno3"]
    keys = {assertion["facet_key"] for assertion in hno3.get("facet_assertions", [])}
    assert "electrolyte.strong_in_water" not in keys
    assert "acid.strong_in_water" not in keys
    assert kb.property_fact("ent_substance_hno3", "electrolyte.strength", {"medium": "aqueous"}).value == "strong"
    assert kb.property_fact("ent_substance_hno3", "acid.strength", {"medium": "aqueous"}).value == "strong"


def test_teaching_view_is_loaded_and_dangling_member_is_rejected(tmp_path: Path) -> None:
    kb = load_knowledge(ROOT)
    assert "view_f3b_hs_aqueous_core" in kb.teaching_views
    view = kb.teaching_views["view_f3b_hs_aqueous_core"]
    members = [member for node in view["nodes"] for member in node.get("members", [])]
    assert len(set(members)) < len(members)

    work = tmp_path / "repo"
    shutil.copytree(ROOT, work)
    path = work / "knowledge" / "teaching" / "f3b_aqueous_views.yaml"
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    doc["records"][0]["nodes"][0]["members"].append("ent_missing")
    path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
    with pytest.raises(SourceError) as exc:
        load_knowledge(work)
    assert exc.value.code == "reference_unresolved"
    assert exc.value.stage == "reference_validation"


def test_material_system_never_enters_exact_balancing() -> None:
    kb = load_knowledge(ROOT)
    with pytest.raises(BalanceError, match="material_system"):
        balance(
            kb,
            ("ent_material_hydrochloric_acid_aqueous", "ent_substance_naoh"),
            ("ent_substance_nacl", "ent_substance_h2o"),
        )


def test_generic_neutralization_infers_f2_and_f3b_pairs() -> None:
    kb = load_knowledge(ROOT)
    plans = compile_rules(kb)
    f2 = infer_case(kb, plans, _case("f2-neutral", "ent_substance_hcl", "ent_substance_naoh"))
    f3b = infer_case(kb, plans, _case("f3b-neutral", "ent_substance_hno3", "ent_substance_koh"))
    assert f2["status"] == "inferred"
    assert f2["rule_id"] == "rule_f2_strong_acid_base_neutralization"
    assert f2["canonical_match"]["reaction_ids"] == ["rxn_hcl_naoh_neutralization"]
    assert f3b["status"] == "inferred"
    assert f3b["rule_id"] == "rule_f2_strong_acid_base_neutralization"
    assert f3b["canonical_match"]["reaction_ids"] == ["rxn_f3b_hno3_koh_neutralization"]


def test_reusable_precipitation_infers_baso4_and_no_net_contrast_stays_no_match() -> None:
    kb = load_knowledge(ROOT)
    plans = compile_rules(kb)
    baso4 = infer_case(kb, plans, _case("baso4", "ent_substance_bacl2", "ent_substance_na2so4"))
    contrast = infer_case(kb, plans, _case("contrast", "ent_substance_nacl", "ent_substance_kno3"))
    assert baso4["status"] == "inferred"
    assert baso4["canonical_match"]["reaction_ids"] == ["rxn_f3b_baso4_precipitation"]
    assert contrast["status"] == "no_match"
    assert contrast["diagnostic"]["code"] == "no_rule_match"


def test_ionic_pair_constructor_never_fabricates_unknown_or_ambiguous_product(tmp_path: Path) -> None:
    work = tmp_path / "repo"
    shutil.copytree(ROOT, work)
    entity_path = work / "knowledge" / "domain" / "f3b_aqueous_entities.yaml"
    doc = yaml.safe_load(entity_path.read_text(encoding="utf-8"))
    duplicate = copy.deepcopy(next(record for record in doc["records"] if record.get("id") == "ent_substance_baso4"))
    duplicate["id"] = "ent_substance_baso4_duplicate"
    duplicate["semantic_keys"] = [{"scheme": "fixture.slug", "value": "duplicate-baso4"}]
    doc["records"].append(duplicate)
    entity_path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")

    kb = load_knowledge(work)
    plans = compile_rules(kb)
    result = infer_case(kb, plans, _case("ambiguous-baso4", "ent_substance_bacl2", "ent_substance_na2so4"))
    assert result["status"] in {"indeterminate", "invalid"}
    diagnostic = result.get("diagnostic") or result.get("diagnostics", [{}])[0]
    assert diagnostic["code"] in {"product_unresolved", "unknown_applicability"}
    assert "ent_substance_baso4_duplicate" not in kb.reactions


def test_aqueous_speciation_profiles_and_derived_forms_match_f3b_golden() -> None:
    kb = load_knowledge(ROOT)
    for entity_id in ("ent_substance_bacl2", "ent_substance_na2so4", "ent_substance_hno3", "ent_substance_koh"):
        profiles = kb.speciation_profiles(entity_id, {"medium": "aqueous"})
        assert len(profiles) == 1
        assert profiles[0]["model"] == "strong_electrolyte_complete_dissociation"
        assert profiles[0]["evidence_ids"]

    for reaction_id in ("rxn_f3b_baso4_precipitation", "rxn_f3b_hno3_koh_neutralization"):
        reaction = kb.reactions[reaction_id]
        for form_kind in ("complete_ionic", "net_ionic"):
            golden = next(form for form in reaction["forms"] if form["form_kind"] == form_kind)
            derived = derive_aqueous_ionic_form(kb, reaction_id, form_kind, {"medium": "aqueous"})
            assert derived["status"] == "derived"
            assert derived["reaction_id"] == reaction_id
            assert derived["form_kind"] == form_kind
            assert _normalized(derived["participants"]) == _normalized(golden["participants"])
            assert derived["validation"] == {"atoms": True, "charge": True}
            assert derived["derivation"]["operators"]
            assert derived["derivation"]["source_reaction_id"] == reaction_id
            assert derived["derivation"]["evidence_ids"]


def test_missing_speciation_profile_is_explicitly_unavailable(tmp_path: Path) -> None:
    work = tmp_path / "repo"
    shutil.copytree(ROOT, work)
    path = work / "knowledge" / "domain" / "f3b_aqueous_entities.yaml"
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    entity = next(record for record in doc["records"] if record.get("id") == "ent_substance_bacl2")
    entity.pop("speciation_profiles")
    path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
    kb = load_knowledge(work)
    result = derive_aqueous_ionic_form(kb, "rxn_f3b_baso4_precipitation", "complete_ionic", {"medium": "aqueous"})
    assert result["status"] == "unavailable"
    assert result["diagnostic"]["code"] == "speciation_unavailable"


def test_project_reaction_form_preserves_owner_identity_and_is_deterministic() -> None:
    kb = load_knowledge(ROOT)
    assumptions = {"aqueous_medium", "strong_electrolyte_dissociation", "insoluble_precipitate_intact"}
    first = project_reaction_form(kb, "rxn_f3b_baso4_precipitation", "net_ionic", assumptions)
    second = project_reaction_form(kb, "rxn_f3b_baso4_precipitation", "net_ionic", reversed(sorted(assumptions)))
    assert first == second
    assert first is not None
    assert first["reaction_id"] == "rxn_f3b_baso4_precipitation"
    assert first["form_kind"] == "net_ionic"
    assert first["derivation"]["source_reaction_id"] == "rxn_f3b_baso4_precipitation"


def test_gas_evolution_family_remains_explicit_non_blocking_gap() -> None:
    kb = load_knowledge(ROOT)
    result = infer_case(kb, compile_rules(kb), _case("gas-gap", "ent_substance_hcl", "ent_substance_nahco3"))
    assert result["status"] == "no_match"
