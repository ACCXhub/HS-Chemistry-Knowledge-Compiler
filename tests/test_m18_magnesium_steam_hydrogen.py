from __future__ import annotations

import json
from pathlib import Path

from compiler.build import ARTIFACT_FORMAT_VERSION, artifact_versions, compile_repository
from compiler.engine import infer_case
from compiler.model import KnowledgeState
from compiler.rules import RULE_DSL_VERSION, RULE_PLAN_VERSION, compile_rules
from compiler.source import SOURCE_SCHEMA_VERSION, load_cases, load_knowledge


ROOT = Path(__file__).resolve().parents[1]
RULE_ID = "rule_m18_magnesium_steam_hydrogen"
REACTION_ID = "rxn_m18_magnesium_steam_hydrogen"


def _case(
    case_id: str,
    *,
    water_phase: str = "gas",
    temperature: str | None = "heated",
) -> dict:
    context = {}
    if temperature is not None:
        context["temperature_regime"] = temperature
    return {
        "id": case_id,
        "reactants": [
            {"target_id": "ent_substance_elemental_mg", "phase": "solid"},
            {"target_id": "ent_substance_h2o", "phase": water_phase},
        ],
        "context": context,
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


def test_m18_magnesium_steam_heated_infers_exact_canonical_reaction_deterministically() -> None:
    kb = load_knowledge(ROOT)
    plans = compile_rules(kb)
    case = _case("m18_magnesium_steam_heated")

    first = infer_case(kb, plans, case)
    second = infer_case(kb, plans, case)

    assert first == second
    assert first["status"] == "inferred"
    assert first["rule_id"] == RULE_ID
    assert first["canonical_match"]["state"] == "exact"
    assert first["canonical_match"]["reaction_ids"] == [REACTION_ID]
    assert first["canonical_match"]["condition_evidence_ids"] == [
        "ev_m18_magnesium_steam_hydrogen"
    ]
    assert first["provenance"]["condition_evidence_ids"] == [
        "ev_m18_magnesium_steam_hydrogen"
    ]
    assert first["validation"] == {"atoms": True, "charge": True}
    assert _normalized(first["participants"]) == [
        ("product", "ent_substance_h2", "gas", 1),
        ("product", "ent_substance_mgo", "solid", 1),
        ("reactant", "ent_substance_elemental_mg", "solid", 1),
        ("reactant", "ent_substance_h2o", "gas", 1),
    ]
    assert first["provenance"]["evidence_ids"] == [
        "ev_m18_magnesium_steam_hydrogen"
    ]
    assert any(
        item.get("event") == "input.normalized"
        and item.get("context") == {"temperature_regime": "heated"}
        for item in first["proof_trace"]
    )


def test_m18_fixture_matrix_enforces_phase_and_temperature_boundaries() -> None:
    kb = load_knowledge(ROOT)
    plans = compile_rules(kb)
    cases = {case["id"]: case for case in load_cases(ROOT)}

    positive = infer_case(kb, plans, cases["case_m18_magnesium_steam_heated"])
    liquid_heated = infer_case(kb, plans, cases["case_m18_magnesium_liquid_heated"])
    liquid_ambient = infer_case(kb, plans, cases["case_m18_magnesium_liquid_ambient"])
    gas_ambient = infer_case(kb, plans, cases["case_m18_magnesium_steam_ambient"])
    gas_warmed = infer_case(kb, plans, cases["case_m18_magnesium_steam_warmed"])
    missing = infer_case(kb, plans, cases["case_m18_magnesium_steam_missing_temperature"])

    assert positive["status"] == "inferred"
    assert positive["rule_id"] == RULE_ID
    for result in (liquid_heated, liquid_ambient, gas_ambient, gas_warmed):
        assert result.get("rule_id") != RULE_ID
        assert "candidate_key" not in result
    assert not any(
        item.get("event") == "rule.match" and item.get("rule_id") == RULE_ID
        for result in (liquid_heated, liquid_ambient)
        for item in result["proof_trace"]
    )
    for result in (gas_ambient, gas_warmed):
        assert any(
            item.get("rule_id") == RULE_ID
            and item.get("key") == "temperature_regime"
            and item.get("truth") == "FALSE"
            for item in result["proof_trace"]
        )
    assert missing["status"] == "indeterminate"
    assert "candidate_key" not in missing
    assert any(
        item.get("rule_id") == RULE_ID
        and item.get("key") == "temperature_regime"
        and item.get("truth") == "UNKNOWN"
        for item in missing["proof_trace"]
    )


def test_m18_rule_is_exact_and_does_not_define_dynamic_metal_oxide_products() -> None:
    kb = load_knowledge(ROOT)
    plan = next(plan for plan in compile_rules(kb) if plan.rule_id == RULE_ID)

    assert [(pattern.target_id, pattern.phase) for pattern in plan.patterns] == [
        ("ent_substance_elemental_mg", "solid"),
        ("ent_substance_h2o", "gas"),
    ]
    assert [(product.target_id, product.phase) for product in plan.products] == [
        ("ent_substance_mgo", "solid"),
        ("ent_substance_h2", "gas"),
    ]


def test_m18_reaction_has_no_ionic_forms_or_dissolved_magnesium(tmp_path: Path) -> None:
    kb = load_knowledge(ROOT)
    reaction = kb.reactions[REACTION_ID]
    assert reaction["forms"] == []

    compile_repository(ROOT, tmp_path / "compile", "m18-test")
    derived = json.loads((tmp_path / "compile" / "derived-reaction-forms.json").read_text(encoding="utf-8"))
    assert all(item["reaction_id"] != REACTION_ID for item in derived["forms"])

    result = infer_case(kb, compile_rules(kb), _case("m18-no-dissolved-magnesium"))
    participant_ids = {item["target_id"] for item in result["participants"]}
    assert "ent_species_mg_2plus" not in participant_ids
    assert "ent_substance_mg_oh_2" not in participant_ids


def test_m18_mgo_identity_is_unique_and_evidence_backed() -> None:
    kb = load_knowledge(ROOT)

    assert kb.semantic_key_candidates("formula.unit", "MgO") == ("ent_substance_mgo",)
    mgo = kb.entities["ent_substance_mgo"]
    assert mgo["evidence_ids"] == ["ev_m18_magnesium_steam_hydrogen"]
    assert mgo["payload"]["composition"] == {
        "components": [
            {"element_id": "ent_element_mg", "count": 1},
            {"element_id": "ent_element_o", "count": 1},
        ],
        "net_charge": 0,
    }


def test_m18_does_not_overload_m11_magnesium_water_reactivity() -> None:
    kb = load_knowledge(ROOT)
    fact = kb.property_fact(
        "ent_substance_elemental_mg",
        "metal.water_reactivity",
        {"medium": "aqueous", "temperature_regime": "ambient"},
    )

    assert fact.state is KnowledgeState.ABSENT


def test_m18_reuses_compatibility_coordinates_unchanged() -> None:
    assert SOURCE_SCHEMA_VERSION == "3.5.0"
    assert RULE_DSL_VERSION == "1.3.0"
    assert RULE_PLAN_VERSION == "1.3.0"
    assert ARTIFACT_FORMAT_VERSION == "1.4.0"
    assert artifact_versions() == {
        "source_schema": "3.5.0",
        "rule_dsl": "1.3.0",
        "rule_plan": "1.3.0",
        "artifact_format": "1.4.0",
    }


def test_m18_teaching_view_reuses_existing_view_without_claiming_ionic_equations() -> None:
    kb = load_knowledge(ROOT)
    assert tuple(kb.teaching_views) == ("view_f3b_hs_aqueous_core",)
    nodes = {
        node["path_key"]: set(node.get("members", []))
        for node in kb.teaching_views["view_f3b_hs_aqueous_core"]["nodes"]
    }

    assert REACTION_ID in nodes["D03/reaction-types/single-displacement"]
    assert REACTION_ID not in nodes["D06/notation/ionic-equations"]
    assert "ent_substance_mgo" in nodes["D10/elements-and-compounds/representative-elements"]


def test_m18_preserves_m11_liquid_water_and_m16_m17_heated_inference() -> None:
    kb = load_knowledge(ROOT)
    plans = compile_rules(kb)
    cases = {case["id"]: case for case in load_cases(ROOT)}
    expected = {
        "case_m11_na_water": "rule_m11_water_reactive_metal_hydrogen",
        "case_m11_k_water": "rule_m11_water_reactive_metal_hydrogen",
        "case_m16_caco3_heated": "rule_m16_caco3_heated_decomposition",
        "case_m17_nahco3_heated": "rule_m17_nahco3_heated_decomposition",
    }

    for case_id, rule_id in expected.items():
        result = infer_case(kb, plans, cases[case_id])
        assert result["status"] == "inferred", case_id
        assert result["rule_id"] == rule_id, case_id
        assert result["canonical_match"]["state"] == "exact", case_id
