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


def _case(case_id: str, left: str, right: str, *, warmed: bool = False) -> dict:
    return {
        "id": case_id,
        "reactants": [
            {"target_id": left, "phase": "aqueous"},
            {"target_id": right, "phase": "aqueous"},
        ],
        "context": {
            "medium": "aqueous",
            "temperature_regime": "warmed" if warmed else "ambient",
        },
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


EARLY_CASES = (
    (
        "batch_a_hcl_koh",
        "ent_substance_hcl",
        "ent_substance_koh",
        "rule_f2_strong_acid_base_neutralization",
        "rxn_batch_a_hcl_koh_neutralization",
        [("reactant", "ent_substance_hcl", "aqueous", 1), ("reactant", "ent_substance_koh", "aqueous", 1), ("product", "ent_substance_kcl", "aqueous", 1), ("product", "ent_substance_h2o", "liquid", 1)],
    ),
    (
        "batch_a_hno3_naoh",
        "ent_substance_hno3",
        "ent_substance_naoh",
        "rule_f2_strong_acid_base_neutralization",
        "rxn_batch_a_hno3_naoh_neutralization",
        [("reactant", "ent_substance_hno3", "aqueous", 1), ("reactant", "ent_substance_naoh", "aqueous", 1), ("product", "ent_substance_nano3", "aqueous", 1), ("product", "ent_substance_h2o", "liquid", 1)],
    ),
    (
        "batch_a_hcl_khco3",
        "ent_substance_hcl",
        "ent_substance_khco3",
        "rule_m5_strong_acid_hydrogen_carbonate_gas_evolution",
        "rxn_batch_a_hcl_khco3_gas_evolution",
        [("reactant", "ent_substance_hcl", "aqueous", 1), ("reactant", "ent_substance_khco3", "aqueous", 1), ("product", "ent_substance_kcl", "aqueous", 1), ("product", "ent_substance_co2", "gas", 1), ("product", "ent_substance_h2o", "liquid", 1)],
    ),
    (
        "batch_a_hno3_khco3",
        "ent_substance_hno3",
        "ent_substance_khco3",
        "rule_m5_strong_acid_hydrogen_carbonate_gas_evolution",
        "rxn_batch_a_hno3_khco3_gas_evolution",
        [("reactant", "ent_substance_hno3", "aqueous", 1), ("reactant", "ent_substance_khco3", "aqueous", 1), ("product", "ent_substance_kno3", "aqueous", 1), ("product", "ent_substance_co2", "gas", 1), ("product", "ent_substance_h2o", "liquid", 1)],
    ),
    (
        "batch_a_hno3_k2co3",
        "ent_substance_hno3",
        "ent_substance_k2co3",
        "rule_m6_strong_acid_carbonate_gas_evolution",
        "rxn_batch_a_hno3_k2co3_gas_evolution",
        [("reactant", "ent_substance_hno3", "aqueous", 2), ("reactant", "ent_substance_k2co3", "aqueous", 1), ("product", "ent_substance_kno3", "aqueous", 2), ("product", "ent_substance_co2", "gas", 1), ("product", "ent_substance_h2o", "liquid", 1)],
    ),
)


@pytest.mark.parametrize(
    ("case_id", "left", "right", "rule_id", "reaction_id", "expected"),
    EARLY_CASES,
)
def test_batch_a_neutralization_and_gas_cases_are_exact_and_deterministic(
    case_id: str,
    left: str,
    right: str,
    rule_id: str,
    reaction_id: str,
    expected: list[tuple[str, str, str, int]],
) -> None:
    kb = load_knowledge(ROOT)
    plans = compile_rules(kb)
    first = infer_case(kb, plans, _case(case_id, left, right))
    second = infer_case(kb, plans, _case(case_id, left, right))

    assert first == second
    assert first["status"] == "inferred"
    assert first["rule_id"] == rule_id
    assert first["canonical_match"]["state"] == "exact"
    assert first["canonical_match"]["reaction_ids"] == [reaction_id]
    assert first["validation"] == {"atoms": True, "charge": True}
    assert _normalized(first["participants"]) == sorted(expected)
    assert first["provenance"]["evidence_ids"]


@pytest.mark.parametrize(
    ("reaction_id", "expected_net"),
    [
        (
            "rxn_batch_a_hcl_koh_neutralization",
            [("reactant", "ent_species_h_plus", "dissolved", 1), ("reactant", "ent_species_oh_minus", "dissolved", 1), ("product", "ent_substance_h2o", "liquid", 1)],
        ),
        (
            "rxn_batch_a_hcl_khco3_gas_evolution",
            [("reactant", "ent_species_h_plus", "dissolved", 1), ("reactant", "ent_species_hco3_minus", "dissolved", 1), ("product", "ent_substance_co2", "gas", 1), ("product", "ent_substance_h2o", "liquid", 1)],
        ),
        (
            "rxn_batch_a_hno3_k2co3_gas_evolution",
            [("reactant", "ent_species_h_plus", "dissolved", 2), ("reactant", "ent_species_co3_2minus", "dissolved", 1), ("product", "ent_substance_co2", "gas", 1), ("product", "ent_substance_h2o", "liquid", 1)],
        ),
    ],
)
def test_batch_a_early_cluster_ionic_forms_are_derived(
    reaction_id: str,
    expected_net: list[tuple[str, str, str, int]],
) -> None:
    kb = load_knowledge(ROOT)
    complete = derive_aqueous_ionic_form(kb, reaction_id, "complete_ionic", AMBIENT)
    net = derive_aqueous_ionic_form(kb, reaction_id, "net_ionic", AMBIENT)

    assert complete["status"] == "derived"
    assert complete["validation"] == {"atoms": True, "charge": True}
    assert net["status"] == "derived"
    assert net["validation"] == {"atoms": True, "charge": True}
    assert _normalized(net["participants"]) == sorted(expected_net)
    assert net["derivation"]["evidence_ids"]


def test_batch_a_adds_fixture_for_existing_hno3_koh_reaction() -> None:
    cases = {case["id"]: case for case in load_cases(ROOT)}
    assert "case_batch_a_hno3_koh" in cases
    kb = load_knowledge(ROOT)
    result = infer_case(kb, compile_rules(kb), cases["case_batch_a_hno3_koh"])
    assert result["status"] == "inferred"
    assert result["rule_id"] == "rule_f2_strong_acid_base_neutralization"
    assert result["canonical_match"]["reaction_ids"] == ["rxn_f3b_hno3_koh_neutralization"]


AMMONIUM_CASES = (
    ("ent_substance_nh4cl", "ent_substance_koh", "rxn_batch_a_nh4cl_koh", 1),
    ("ent_substance_nh4_2so4", "ent_substance_koh", "rxn_batch_a_nh4_2so4_koh", 2),
    ("ent_substance_nh4no3", "ent_substance_naoh", "rxn_batch_a_nh4no3_naoh", 1),
    ("ent_substance_nh4no3", "ent_substance_koh", "rxn_batch_a_nh4no3_koh", 1),
)


@pytest.mark.parametrize(("salt", "base", "reaction_id", "ammonia_coefficient"), AMMONIUM_CASES)
def test_batch_a_ammonium_cases_reuse_warmed_m7_rule(
    salt: str,
    base: str,
    reaction_id: str,
    ammonia_coefficient: int,
) -> None:
    kb = load_knowledge(ROOT)
    result = infer_case(kb, compile_rules(kb), _case(reaction_id, salt, base, warmed=True))

    assert result["status"] == "inferred"
    assert result["rule_id"] == "rule_m7_ammonium_strong_base_gas_evolution"
    assert result["canonical_match"]["state"] == "exact"
    assert result["canonical_match"]["reaction_ids"] == [reaction_id]
    assert result["validation"] == {"atoms": True, "charge": True}
    ammonia = next(item for item in result["participants"] if item["target_id"] == "ent_substance_nh3")
    assert ammonia["phase"] == "gas"
    assert ammonia["coefficient"]["numerator"] == ammonia_coefficient

    complete = derive_aqueous_ionic_form(kb, reaction_id, "complete_ionic", {"medium": "aqueous", "temperature_regime": "warmed"})
    net = derive_aqueous_ionic_form(kb, reaction_id, "net_ionic", {"medium": "aqueous", "temperature_regime": "warmed"})
    assert complete["validation"] == {"atoms": True, "charge": True}
    assert _normalized(net["participants"]) == sorted(
        [
            ("reactant", "ent_species_nh4_plus", "dissolved", 1),
            ("reactant", "ent_species_oh_minus", "dissolved", 1),
            ("product", "ent_substance_nh3", "gas", 1),
            ("product", "ent_substance_h2o", "liquid", 1),
        ]
    )
    assert "ev_m7_ammonia_warmed_test" in result["provenance"]["condition_evidence_ids"]


def test_batch_a_ammonium_without_warmed_condition_remains_indeterminate() -> None:
    kb = load_knowledge(ROOT)
    case = _case("batch_a_nh4no3_koh_missing_warmed", "ent_substance_nh4no3", "ent_substance_koh")
    case["context"] = {"medium": "aqueous"}
    result = infer_case(kb, compile_rules(kb), case)

    assert result["status"] == "indeterminate"
    assert result["diagnostic"]["code"] == "unknown_applicability"
    assert "candidate_key" not in result


HALIDE_CASES = (
    ("ent_substance_kcl", "ent_species_cl_minus", "ent_substance_agcl", "rxn_batch_a_agno3_kcl"),
    ("ent_substance_nabr", "ent_species_br_minus", "ent_substance_agbr", "rxn_batch_a_agno3_nabr"),
    ("ent_substance_kbr", "ent_species_br_minus", "ent_substance_agbr", "rxn_batch_a_agno3_kbr"),
    ("ent_substance_nai", "ent_species_i_minus", "ent_substance_agi", "rxn_batch_a_agno3_nai"),
    ("ent_substance_ki", "ent_species_i_minus", "ent_substance_agi", "rxn_batch_a_agno3_ki"),
)


@pytest.mark.parametrize(("halide_salt", "halide_ion", "precipitate", "reaction_id"), HALIDE_CASES)
def test_batch_a_halide_precipitation_reuses_one_rule_and_projects_ions(
    halide_salt: str,
    halide_ion: str,
    precipitate: str,
    reaction_id: str,
) -> None:
    kb = load_knowledge(ROOT)
    result = infer_case(kb, compile_rules(kb), _case(reaction_id, "ent_substance_agno3", halide_salt))

    assert result["status"] == "inferred"
    assert result["rule_id"] == "rule_f2_agcl_precipitation"
    assert result["canonical_match"]["reaction_ids"] == [reaction_id]
    assert result["validation"] == {"atoms": True, "charge": True}
    solid = next(item for item in result["participants"] if item["phase"] == "solid")
    assert solid["target_id"] == precipitate
    assert solid["coefficient"]["numerator"] == 1

    complete = derive_aqueous_ionic_form(kb, reaction_id, "complete_ionic", AMBIENT)
    net = derive_aqueous_ionic_form(kb, reaction_id, "net_ionic", AMBIENT)
    assert complete["validation"] == {"atoms": True, "charge": True}
    assert _normalized(net["participants"]) == sorted(
        [
            ("reactant", "ent_species_ag_plus", "dissolved", 1),
            ("reactant", halide_ion, "dissolved", 1),
            ("product", precipitate, "solid", 1),
        ]
    )


def test_batch_a_insoluble_silver_halides_have_no_fake_aqueous_speciation() -> None:
    kb = load_knowledge(ROOT)
    for entity_id in ("ent_substance_agbr", "ent_substance_agi"):
        assert kb.property_fact(entity_id, "solubility.class", {"medium": "aqueous"}).value == "insoluble"
        assert kb.speciation_profiles(entity_id, {"medium": "aqueous"}) == ()


SULFATE_CASES = (
    ("ent_substance_k2so4", "rxn_batch_a_bacl2_k2so4", "ent_substance_kcl", 2),
    ("ent_substance_mgso4", "rxn_batch_a_bacl2_mgso4", "ent_substance_mgcl2", 1),
    ("ent_substance_znso4", "rxn_batch_a_bacl2_znso4", "ent_substance_zncl2", 1),
    ("ent_substance_cuso4", "rxn_batch_a_bacl2_cuso4", "ent_substance_cucl2", 1),
)


@pytest.mark.parametrize(("sulfate", "reaction_id", "counterproduct", "counter_coefficient"), SULFATE_CASES)
def test_batch_a_sulfate_precipitation_reuses_one_rule(
    sulfate: str,
    reaction_id: str,
    counterproduct: str,
    counter_coefficient: int,
) -> None:
    kb = load_knowledge(ROOT)
    result = infer_case(kb, compile_rules(kb), _case(reaction_id, "ent_substance_bacl2", sulfate))

    assert result["status"] == "inferred"
    assert result["rule_id"] == "rule_f2_agcl_precipitation"
    assert result["canonical_match"]["reaction_ids"] == [reaction_id]
    assert result["validation"] == {"atoms": True, "charge": True}
    counter = next(item for item in result["participants"] if item["target_id"] == counterproduct)
    assert counter["coefficient"]["numerator"] == counter_coefficient

    net = derive_aqueous_ionic_form(kb, reaction_id, "net_ionic", AMBIENT)
    assert _normalized(net["participants"]) == sorted(
        [
            ("reactant", "ent_species_ba_2plus", "dissolved", 1),
            ("reactant", "ent_species_so4_2minus", "dissolved", 1),
            ("product", "ent_substance_baso4", "solid", 1),
        ]
    )


CARBONATE_CASES = (
    ("ent_substance_cacl2", "ent_species_ca_2plus", "ent_substance_na2co3", "ent_substance_caco3", "rxn_batch_a_cacl2_na2co3"),
    ("ent_substance_cacl2", "ent_species_ca_2plus", "ent_substance_k2co3", "ent_substance_caco3", "rxn_batch_a_cacl2_k2co3"),
    ("ent_substance_bacl2", "ent_species_ba_2plus", "ent_substance_na2co3", "ent_substance_baco3", "rxn_batch_a_bacl2_na2co3"),
    ("ent_substance_bacl2", "ent_species_ba_2plus", "ent_substance_k2co3", "ent_substance_baco3", "rxn_batch_a_bacl2_k2co3"),
    ("ent_substance_mgso4", "ent_species_mg_2plus", "ent_substance_na2co3", "ent_substance_mgco3", "rxn_batch_a_mgso4_na2co3"),
    ("ent_substance_mgso4", "ent_species_mg_2plus", "ent_substance_k2co3", "ent_substance_mgco3", "rxn_batch_a_mgso4_k2co3"),
    ("ent_substance_znso4", "ent_species_zn_2plus", "ent_substance_na2co3", "ent_substance_znco3", "rxn_batch_a_znso4_na2co3"),
    ("ent_substance_znso4", "ent_species_zn_2plus", "ent_substance_k2co3", "ent_substance_znco3", "rxn_batch_a_znso4_k2co3"),
)


@pytest.mark.parametrize(("cation_salt", "cation", "carbonate_salt", "precipitate", "reaction_id"), CARBONATE_CASES)
def test_batch_a_carbonate_precipitation_reuses_one_rule(
    cation_salt: str,
    cation: str,
    carbonate_salt: str,
    precipitate: str,
    reaction_id: str,
) -> None:
    kb = load_knowledge(ROOT)
    first = infer_case(kb, compile_rules(kb), _case(reaction_id, cation_salt, carbonate_salt))
    second = infer_case(kb, compile_rules(kb), _case(reaction_id, cation_salt, carbonate_salt))

    assert first == second
    assert first["status"] == "inferred"
    assert first["rule_id"] == "rule_f2_agcl_precipitation"
    assert first["canonical_match"]["reaction_ids"] == [reaction_id]
    assert first["validation"] == {"atoms": True, "charge": True}
    assert next(item for item in first["participants"] if item["phase"] == "solid")["target_id"] == precipitate

    complete = derive_aqueous_ionic_form(kb, reaction_id, "complete_ionic", AMBIENT)
    net = derive_aqueous_ionic_form(kb, reaction_id, "net_ionic", AMBIENT)
    assert complete["validation"] == {"atoms": True, "charge": True}
    assert _normalized(net["participants"]) == sorted(
        [
            ("reactant", cation, "dissolved", 1),
            ("reactant", "ent_species_co3_2minus", "dissolved", 1),
            ("product", precipitate, "solid", 1),
        ]
    )


def test_batch_a_insoluble_carbonates_have_no_fake_aqueous_speciation() -> None:
    kb = load_knowledge(ROOT)
    for entity_id in ("ent_substance_caco3", "ent_substance_baco3", "ent_substance_mgco3", "ent_substance_znco3"):
        assert kb.property_fact(entity_id, "solubility.class", {"medium": "aqueous"}).value == "insoluble"
        assert kb.speciation_profiles(entity_id, {"medium": "aqueous"}) == ()


NEW_ENTITY_KEYS = {
    ("formula.unit", "K2SO4"): "ent_substance_k2so4",
    ("formula.unit", "KHCO3"): "ent_substance_khco3",
    ("formula.unit", "NH4NO3"): "ent_substance_nh4no3",
    ("formula.unit", "CuCl2"): "ent_substance_cucl2",
    ("element.symbol", "Br"): "ent_element_br",
    ("formula.ion", "Br-"): "ent_species_br_minus",
    ("formula.unit", "NaBr"): "ent_substance_nabr",
    ("formula.unit", "KBr"): "ent_substance_kbr",
    ("formula.unit", "AgBr"): "ent_substance_agbr",
    ("element.symbol", "I"): "ent_element_i",
    ("formula.ion", "I-"): "ent_species_i_minus",
    ("formula.unit", "NaI"): "ent_substance_nai",
    ("formula.unit", "KI"): "ent_substance_ki",
    ("formula.unit", "AgI"): "ent_substance_agi",
    ("element.symbol", "Ca"): "ent_element_ca",
    ("formula.ion", "Ca2+"): "ent_species_ca_2plus",
    ("formula.unit", "CaCl2"): "ent_substance_cacl2",
    ("formula.unit", "CaCO3"): "ent_substance_caco3",
    ("formula.unit", "BaCO3"): "ent_substance_baco3",
    ("formula.unit", "MgCO3"): "ent_substance_mgco3",
    ("formula.unit", "ZnCO3"): "ent_substance_znco3",
}


def test_batch_a_reconciles_exactly_21_unique_canonical_entities() -> None:
    kb = load_knowledge(ROOT)
    assert len(NEW_ENTITY_KEYS) == 21
    for semantic_key, entity_id in NEW_ENTITY_KEYS.items():
        assert kb.semantic_key_candidates(*semantic_key) == (entity_id,)
        assert set(kb.entities[entity_id]["evidence_ids"]) & {
            "ev_batch_a_ionic_identity_and_solubility",
            "ev_batch_a_element_identities",
        }
    assert all(len(entity_ids) == 1 for entity_ids in kb.semantic_keys.values())


def _with_product_solubility(kb, entity_id: str, value: str | None):
    entities = deepcopy(kb.entities)
    entity = entities[entity_id]
    assertions = [
        item for item in entity.get("property_assertions", [])
        if item["property_key"] != "solubility.class"
    ]
    if value is not None:
        assertions.append(
            {
                "property_key": "solubility.class",
                "value_state": "known",
                "value": value,
                "fact_kind": "contextual",
                "context": {"medium": "aqueous"},
                "evidence_ids": ["ev_batch_a_ionic_identity_and_solubility"],
            }
        )
    entity["property_assertions"] = assertions
    return replace(kb, entities=entities)


def test_batch_a_missing_product_solubility_stays_unknown() -> None:
    kb = _with_product_solubility(load_knowledge(ROOT), "ent_substance_nacl", None)
    result = infer_case(
        kb,
        compile_rules(kb),
        _case("batch_a_missing_product_solubility", "ent_substance_bacl2", "ent_substance_na2co3"),
    )
    assert result["status"] == "indeterminate"
    assert "candidate_key" not in result
    driving = next(item for item in result["proof_trace"] if item.get("subject") == "ionic_exchange")
    assert driving["truth"] == "UNKNOWN"


def test_batch_a_two_precipitates_are_not_arbitrarily_selected() -> None:
    kb = _with_product_solubility(load_knowledge(ROOT), "ent_substance_nacl", "insoluble")
    result = infer_case(
        kb,
        compile_rules(kb),
        _case("batch_a_two_precipitates", "ent_substance_bacl2", "ent_substance_na2co3"),
    )
    assert result["status"] == "indeterminate"
    assert "candidate_key" not in result
    driving = next(item for item in result["proof_trace"] if item.get("subject") == "ionic_exchange")
    assert driving["truth"] == "UNKNOWN"


def test_batch_a_open_world_fixture_boundaries_remain_conservative() -> None:
    kb = load_knowledge(ROOT)
    plans = compile_rules(kb)
    cases = {case["id"]: case for case in load_cases(ROOT)}
    for case_id in (
        "case_batch_a_kcl_nano3_all_soluble",
        "case_batch_a_agno3_nabr_unknown_medium",
        "case_batch_a_agbr_nano3_insoluble_input",
        "case_m9_hno3_na2s2o3_unknown_redox",
        "case_batch_a_nh4no3_koh_unknown_temperature",
    ):
        result = infer_case(kb, plans, cases[case_id])
        assert result["status"] == "indeterminate"
        assert "candidate_key" not in result


def test_batch_a_teaching_view_reuses_existing_paths() -> None:
    kb = load_knowledge(ROOT)
    assert tuple(kb.teaching_views) == ("view_f3b_hs_aqueous_core",)
    view = kb.teaching_views["view_f3b_hs_aqueous_core"]
    by_path = {node["path_key"]: set(node.get("members", [])) for node in view["nodes"]}
    new_reactions = {reaction_id for reaction_id in kb.reactions if reaction_id.startswith("rxn_batch_a_")}
    assert len(new_reactions) == 26
    assert new_reactions <= by_path["D06/notation/ionic-equations"]
    assert {reaction_id for reaction_id in new_reactions if "neutralization" in reaction_id} <= by_path["D03/reaction-types/neutralization"]
    assert {reaction_id for reaction_id in new_reactions if any(token in reaction_id for token in ("gas_evolution", "nh4"))} <= by_path["D03/reaction-types/gas-evolution"]
    assert {reaction_id for reaction_id in new_reactions if reaction_id not in by_path["D03/reaction-types/neutralization"] and reaction_id not in by_path["D03/reaction-types/gas-evolution"]} <= by_path["D03/reaction-types/precipitation"]
    assert set(NEW_ENTITY_KEYS.values()) <= set().union(*by_path.values())


def test_batch_a_retained_cases_use_existing_rules_and_track_current_compatibility() -> None:
    kb = load_knowledge(ROOT)
    plans = compile_rules(kb)
    cases = [case for case in load_cases(ROOT) if case["id"].startswith("case_batch_a_")]
    selected = {
        result["rule_id"]
        for case in cases
        if (result := infer_case(kb, plans, case))["status"] == "inferred"
    }
    assert selected == {
        "rule_f2_agcl_precipitation",
        "rule_f2_strong_acid_base_neutralization",
        "rule_m5_strong_acid_hydrogen_carbonate_gas_evolution",
        "rule_m6_strong_acid_carbonate_gas_evolution",
        "rule_m7_ammonium_strong_base_gas_evolution",
    }
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


def test_batch_a_audit_document_records_six_rules() -> None:
    text = (ROOT / "docs" / "COVERAGE_AUDIT.md").read_text(encoding="utf-8")
    assert "reuse six existing Rules" in text
    assert "reuse seven existing Rules" not in text
