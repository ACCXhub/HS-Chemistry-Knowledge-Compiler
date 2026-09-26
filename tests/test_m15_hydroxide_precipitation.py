from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from pathlib import Path

import pytest

from compiler.build import ARTIFACT_FORMAT_VERSION, artifact_versions
from compiler.engine import infer_case
from compiler.reaction_forms import derive_aqueous_ionic_form
from compiler.rules import RULE_DSL_VERSION, RULE_PLAN_VERSION, compile_rules
from compiler.source import SOURCE_SCHEMA_VERSION, load_cases, load_knowledge


ROOT = Path(__file__).resolve().parents[1]
AMBIENT = {"medium": "aqueous", "temperature_regime": "ambient"}


def _case(case_id: str, salt: str, base: str) -> dict:
    return {
        "id": case_id,
        "reactants": [
            {"target_id": salt, "phase": "aqueous"},
            {"target_id": base, "phase": "aqueous"},
        ],
        "context": {"medium": "aqueous", "temperature_regime": "ambient"},
    }


def _normalized(participants: list[dict]) -> list[tuple[str, str, str, int]]:
    return sorted(
        (
            item["role"],
            item["target_id"],
            item["phase"],
            item["coefficient"]["numerator"],
        )
        for item in participants
    )


def test_m15_copper_sulfate_and_sodium_hydroxide_infer_exact_precipitation() -> None:
    kb = load_knowledge(ROOT)
    result = infer_case(
        kb,
        compile_rules(kb),
        _case("m15_cuso4_naoh", "ent_substance_cuso4", "ent_substance_naoh"),
    )

    assert result["status"] == "inferred"
    assert result["rule_id"] == "rule_m15_hydroxide_precipitation"
    assert result["canonical_match"]["state"] == "exact"
    assert result["canonical_match"]["reaction_ids"] == ["rxn_m15_cuso4_naoh_precipitation"]
    assert result["validation"] == {"atoms": True, "charge": True}
    assert _normalized(result["participants"]) == [
        ("product", "ent_substance_cu_oh_2", "solid", 1),
        ("product", "ent_substance_na2so4", "aqueous", 1),
        ("reactant", "ent_substance_cuso4", "aqueous", 1),
        ("reactant", "ent_substance_naoh", "aqueous", 2),
    ]
    assert result["provenance"]["evidence_ids"]


def test_m15_magnesium_chloride_substitution_reuses_the_same_rule() -> None:
    kb = load_knowledge(ROOT)
    plans = compile_rules(kb)
    case = _case("m15_mgcl2_naoh", "ent_substance_mgcl2", "ent_substance_naoh")
    first = infer_case(kb, plans, case)
    second = infer_case(kb, plans, case)

    assert first == second
    assert first["status"] == "inferred"
    assert first["rule_id"] == "rule_m15_hydroxide_precipitation"
    assert first["canonical_match"]["state"] == "exact"
    assert first["canonical_match"]["reaction_ids"] == ["rxn_m15_mgcl2_naoh_precipitation"]
    assert first["validation"] == {"atoms": True, "charge": True}
    assert _normalized(first["participants"]) == [
        ("product", "ent_substance_mg_oh_2", "solid", 1),
        ("product", "ent_substance_nacl", "aqueous", 2),
        ("reactant", "ent_substance_mgcl2", "aqueous", 1),
        ("reactant", "ent_substance_naoh", "aqueous", 2),
    ]


def test_m15_exact_ferric_ion_case_derives_trivalent_stoichiometry() -> None:
    kb = load_knowledge(ROOT)
    result = infer_case(
        kb,
        compile_rules(kb),
        _case("m15_fecl3_naoh", "ent_substance_fecl3", "ent_substance_naoh"),
    )

    assert result["status"] == "inferred"
    assert result["rule_id"] == "rule_m15_hydroxide_precipitation"
    assert result["canonical_match"]["state"] == "exact"
    assert result["canonical_match"]["reaction_ids"] == ["rxn_m15_fecl3_naoh_precipitation"]
    assert result["validation"] == {"atoms": True, "charge": True}
    assert _normalized(result["participants"]) == [
        ("product", "ent_substance_fe_oh_3", "solid", 1),
        ("product", "ent_substance_nacl", "aqueous", 3),
        ("reactant", "ent_substance_fecl3", "aqueous", 1),
        ("reactant", "ent_substance_naoh", "aqueous", 3),
    ]


@pytest.mark.parametrize(
    ("reaction_id", "cation_id", "hydroxide_id", "hydroxide_coefficient", "spectator_ids"),
    [
        ("rxn_m15_cuso4_naoh_precipitation", "ent_species_cu_2plus", "ent_substance_cu_oh_2", 2, {"ent_species_na_plus", "ent_species_so4_2minus"}),
        ("rxn_m15_mgcl2_naoh_precipitation", "ent_species_mg_2plus", "ent_substance_mg_oh_2", 2, {"ent_species_na_plus", "ent_species_cl_minus"}),
        ("rxn_m15_fecl3_naoh_precipitation", "ent_species_fe_3plus", "ent_substance_fe_oh_3", 3, {"ent_species_na_plus", "ent_species_cl_minus"}),
    ],
)
def test_m15_ionic_projection_cancels_spectators_without_authored_forms(
    reaction_id: str,
    cation_id: str,
    hydroxide_id: str,
    hydroxide_coefficient: int,
    spectator_ids: set[str],
) -> None:
    kb = load_knowledge(ROOT)
    complete = derive_aqueous_ionic_form(kb, reaction_id, "complete_ionic", AMBIENT)
    net = derive_aqueous_ionic_form(kb, reaction_id, "net_ionic", AMBIENT)

    assert kb.reactions[reaction_id]["forms"] == []
    assert complete["status"] == "derived"
    assert complete["validation"] == {"atoms": True, "charge": True}
    complete_ids = {item["target_id"] for item in complete["participants"]}
    assert spectator_ids <= complete_ids
    assert net["status"] == "derived"
    assert net["validation"] == {"atoms": True, "charge": True}
    assert _normalized(net["participants"]) == sorted(
        [
            ("product", hydroxide_id, "solid", 1),
            ("reactant", "ent_species_oh_minus", "dissolved", hydroxide_coefficient),
            ("reactant", cation_id, "dissolved", 1),
        ]
    )
    assert not spectator_ids & {item["target_id"] for item in net["participants"]}
    assert net["derivation"]["evidence_ids"]


def _without_property(kb, entity_id: str, property_key: str):
    entities = deepcopy(kb.entities)
    entity = entities[entity_id]
    entity["property_assertions"] = [
        item
        for item in entity.get("property_assertions", [])
        if item["property_key"] != property_key
    ]
    return replace(kb, entities=entities)


def _m15_trace(result: dict, *, subject: str | None = None, key: str | None = None) -> list[dict]:
    return [
        item
        for item in result["proof_trace"]
        if item.get("rule_id") == "rule_m15_hydroxide_precipitation"
        and (subject is None or item.get("subject") == subject)
        and (key is None or item.get("key") == key)
    ]


def test_m15_all_soluble_exchange_is_known_not_to_precipitate() -> None:
    kb = load_knowledge(ROOT)
    result = infer_case(
        kb,
        compile_rules(kb),
        _case("m15_nacl_koh_all_soluble", "ent_substance_nacl", "ent_substance_koh"),
    )

    assert result["status"] != "inferred"
    assert "candidate_key" not in result
    driving = _m15_trace(result, subject="ionic_exchange", key="driving_force")
    assert any(item["truth"] == "FALSE" and item["knowledge_state"] == "known" for item in driving)


def test_m15_missing_aqueous_medium_remains_unknown() -> None:
    kb = load_knowledge(ROOT)
    case = _case("m15_missing_medium", "ent_substance_cuso4", "ent_substance_naoh")
    case["context"] = {"temperature_regime": "ambient"}
    result = infer_case(kb, compile_rules(kb), case)

    assert result["status"] == "indeterminate"
    assert "candidate_key" not in result
    medium = _m15_trace(result, subject="context", key="medium")
    assert any(item["truth"] == "UNKNOWN" for item in medium)


def test_m15_missing_hydroxide_solubility_remains_unknown() -> None:
    kb = _without_property(load_knowledge(ROOT), "ent_substance_cu_oh_2", "solubility.class")
    result = infer_case(
        kb,
        compile_rules(kb),
        _case("m15_missing_hydroxide_solubility", "ent_substance_cuso4", "ent_substance_naoh"),
    )

    assert result["status"] == "indeterminate"
    assert "candidate_key" not in result
    driving = _m15_trace(result, subject="ionic_exchange", key="driving_force")
    assert any(item["truth"] == "UNKNOWN" for item in driving)


def test_m15_insoluble_solid_salt_input_does_not_enter_aqueous_family() -> None:
    kb = load_knowledge(ROOT)
    case = _case("m15_solid_agcl", "ent_substance_agcl", "ent_substance_naoh")
    case["reactants"][0]["phase"] = "solid"
    result = infer_case(kb, compile_rules(kb), case)

    assert result["status"] != "inferred"
    assert "candidate_key" not in result
    assert not any(
        item.get("event") == "rule.match"
        and item.get("rule_id") == "rule_m15_hydroxide_precipitation"
        for item in result["proof_trace"]
    )


def test_m15_non_authorized_ammonia_base_does_not_match() -> None:
    kb = load_knowledge(ROOT)
    result = infer_case(
        kb,
        compile_rules(kb),
        _case("m15_nh3_not_authorized", "ent_substance_cuso4", "ent_substance_nh3"),
    )

    assert result["status"] != "inferred"
    assert "candidate_key" not in result
    base_facts = _m15_trace(result, subject="facet", key="classification.base")
    assert any(item["truth"] == "UNKNOWN" for item in base_facts)


def test_m15_unmodeled_zinc_hydroxide_is_not_inferred() -> None:
    kb = load_knowledge(ROOT)
    result = infer_case(
        kb,
        compile_rules(kb),
        _case("m15_znso4_naoh_deferred", "ent_substance_znso4", "ent_substance_naoh"),
    )

    assert result["status"] == "indeterminate"
    assert "candidate_key" not in result
    driving = _m15_trace(result, subject="ionic_exchange", key="driving_force")
    assert any(item["truth"] == "UNKNOWN" for item in driving)


def test_m15_unmodeled_aluminium_input_is_rejected_before_inference() -> None:
    kb = load_knowledge(ROOT)
    result = infer_case(
        kb,
        compile_rules(kb),
        _case("m15_alcl3_naoh_deferred", "ent_substance_alcl3", "ent_substance_naoh"),
    )

    assert result["status"] == "invalid"
    assert result["diagnostic"]["code"] == "reference_unresolved"
    assert "candidate_key" not in result


def test_m15_does_not_change_batch_a_sulfate_precipitation_selection() -> None:
    kb = load_knowledge(ROOT)
    result = infer_case(
        kb,
        compile_rules(kb),
        _case("m15_m14_regression", "ent_substance_bacl2", "ent_substance_cuso4"),
    )

    assert result["status"] == "inferred"
    assert result["rule_id"] == "rule_f2_agcl_precipitation"
    assert result["canonical_match"]["reaction_ids"] == ["rxn_batch_a_bacl2_cuso4"]


def test_m15_repository_fixtures_cover_positive_and_open_world_matrix() -> None:
    kb = load_knowledge(ROOT)
    plans = compile_rules(kb)
    cases = {case["id"]: case for case in load_cases(ROOT)}
    expected = {
        "case_m15_cuso4_naoh": ("inferred", "rule_m15_hydroxide_precipitation"),
        "case_m15_mgcl2_naoh": ("inferred", "rule_m15_hydroxide_precipitation"),
        "case_m15_fecl3_naoh": ("inferred", "rule_m15_hydroxide_precipitation"),
        "case_m15_nacl_koh_all_soluble": ("indeterminate", None),
        "case_m15_cuso4_naoh_unknown_medium": ("indeterminate", None),
        "case_m15_agcl_solid_naoh": ("indeterminate", None),
        "case_m15_cuso4_nh3_unauthorized_base": ("indeterminate", None),
        "case_m15_znso4_naoh_deferred": ("indeterminate", None),
    }

    for case_id, (status, rule_id) in expected.items():
        result = infer_case(kb, plans, cases[case_id])
        assert result["status"] == status, case_id
        if rule_id is None:
            assert "candidate_key" not in result, case_id
        else:
            assert result["rule_id"] == rule_id, case_id


def test_m15_teaching_view_reuses_existing_paths() -> None:
    kb = load_knowledge(ROOT)
    assert tuple(kb.teaching_views) == ("view_f3b_hs_aqueous_core",)
    nodes = {
        node["path_key"]: set(node.get("members", []))
        for node in kb.teaching_views["view_f3b_hs_aqueous_core"]["nodes"]
    }
    reactions = {
        "rxn_m15_cuso4_naoh_precipitation",
        "rxn_m15_mgcl2_naoh_precipitation",
        "rxn_m15_fecl3_naoh_precipitation",
    }

    assert reactions <= nodes["D03/reaction-types/precipitation"]
    assert reactions <= nodes["D06/notation/ionic-equations"]
    assert "ent_substance_fecl3" in nodes["D02/electrolyte-solutions/strong-electrolytes"]
    assert "ent_substance_fecl3" in nodes["D08/substance-classification/salts"]
    assert {
        "ent_substance_cu_oh_2",
        "ent_substance_mg_oh_2",
        "ent_substance_fe_oh_3",
    } <= nodes["D08/substance-classification/bases"]
    assert {
        "ent_element_fe",
        "ent_species_fe_3plus",
        "ent_substance_fecl3",
        "ent_substance_fe_oh_3",
    } <= nodes["D10/elements-and-compounds/representative-elements"]


def test_m15_new_identities_are_unique_and_exactly_evidenced() -> None:
    kb = load_knowledge(ROOT)
    expected = {
        ("element.symbol", "Fe"): "ent_element_fe",
        ("formula.ion", "Fe3+"): "ent_species_fe_3plus",
        ("formula.unit", "FeCl3"): "ent_substance_fecl3",
        ("formula.unit", "Cu(OH)2"): "ent_substance_cu_oh_2",
        ("formula.unit", "Mg(OH)2"): "ent_substance_mg_oh_2",
        ("formula.unit", "Fe(OH)3"): "ent_substance_fe_oh_3",
    }

    for semantic_key, entity_id in expected.items():
        assert kb.semantic_key_candidates(*semantic_key) == (entity_id,)
        assert kb.entities[entity_id]["evidence_ids"]
    assert kb.entities["ent_species_fe_3plus"]["payload"]["formal_charge"] == 3


def test_m15_adds_one_rule_without_compatibility_drift() -> None:
    kb = load_knowledge(ROOT)
    assert {plan.rule_id for plan in compile_rules(kb)} == set(kb.rules)
    assert SOURCE_SCHEMA_VERSION == "3.7.0"
    assert RULE_DSL_VERSION == "1.4.0"
    assert RULE_PLAN_VERSION == "1.4.0"
    assert ARTIFACT_FORMAT_VERSION == "1.5.0"
    assert artifact_versions() == {
        "source_schema": "3.7.0",
        "rule_dsl": "1.4.0",
        "rule_plan": "1.4.0",
        "artifact_format": "1.5.0",
    }
