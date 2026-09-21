from __future__ import annotations

import json
from pathlib import Path

from compiler.build import ARTIFACT_FORMAT_VERSION, artifact_versions, compile_repository
from compiler.engine import infer_case
from compiler.rules import RULE_DSL_VERSION, RULE_PLAN_VERSION, compile_rules
from compiler.source import SOURCE_SCHEMA_VERSION, load_cases, load_knowledge


ROOT = Path(__file__).resolve().parents[1]


def _case(
    case_id: str,
    substance_id: str = "ent_substance_nahco3",
    *,
    phase: str = "solid",
    temperature: str | None = "heated",
) -> dict:
    context = {}
    if temperature is not None:
        context["temperature_regime"] = temperature
    return {
        "id": case_id,
        "reactants": [{"target_id": substance_id, "phase": phase}],
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


def test_m17_nahco3_heated_infers_exact_canonical_decomposition_deterministically() -> None:
    kb = load_knowledge(ROOT)
    plans = compile_rules(kb)
    case = _case("m17_nahco3_heated")

    first = infer_case(kb, plans, case)
    second = infer_case(kb, plans, case)

    assert first == second
    assert first["status"] == "inferred"
    assert first["rule_id"] == "rule_m17_nahco3_heated_decomposition"
    assert first["canonical_match"]["state"] == "exact"
    assert first["canonical_match"]["reaction_ids"] == ["rxn_m17_nahco3_heated_decomposition"]
    assert first["canonical_match"]["condition_evidence_ids"] == ["ev_m17_nahco3_heated_decomposition"]
    assert first["provenance"]["condition_evidence_ids"] == ["ev_m17_nahco3_heated_decomposition"]
    assert first["validation"] == {"atoms": True, "charge": True}
    assert _normalized(first["participants"]) == [
        ("product", "ent_substance_co2", "gas", 1),
        ("product", "ent_substance_h2o", "gas", 1),
        ("product", "ent_substance_na2co3", "solid", 1),
        ("reactant", "ent_substance_nahco3", "solid", 2),
    ]
    assert first["provenance"]["evidence_ids"] == ["ev_m17_nahco3_heated_decomposition"]
    assert any(
        item.get("event") == "input.normalized"
        and item.get("context") == {"temperature_regime": "heated"}
        for item in first["proof_trace"]
    )


def test_m17_fixture_matrix_preserves_missing_unknown_and_rejects_other_inputs() -> None:
    kb = load_knowledge(ROOT)
    plans = compile_rules(kb)
    cases = {case["id"]: case for case in load_cases(ROOT)}
    expected = {
        "case_m17_nahco3_heated": ("inferred", "rule_m17_nahco3_heated_decomposition"),
        "case_m17_nahco3_missing_temperature": ("indeterminate", None),
        "case_m17_nahco3_ambient": ("no_match", None),
        "case_m17_nahco3_warmed": ("no_match", None),
        "case_m17_nahco3_wrong_phase": ("no_match", None),
        "case_m17_khco3_heated_deferred": ("no_match", None),
    }

    for case_id, (status, rule_id) in expected.items():
        result = infer_case(kb, plans, cases[case_id])
        assert result["status"] == status, case_id
        if rule_id is None:
            assert "candidate_key" not in result, case_id
        else:
            assert result["rule_id"] == rule_id, case_id

    missing = infer_case(kb, plans, cases["case_m17_nahco3_missing_temperature"])
    ambient = infer_case(kb, plans, cases["case_m17_nahco3_ambient"])
    warmed = infer_case(kb, plans, cases["case_m17_nahco3_warmed"])
    assert any(
        item.get("rule_id") == "rule_m17_nahco3_heated_decomposition"
        and item.get("key") == "temperature_regime"
        and item.get("truth") == "UNKNOWN"
        for item in missing["proof_trace"]
    )
    for result in (ambient, warmed):
        assert any(
            item.get("rule_id") == "rule_m17_nahco3_heated_decomposition"
            and item.get("key") == "temperature_regime"
            and item.get("truth") == "FALSE"
            for item in result["proof_trace"]
        )


def test_m17_rule_is_exact_and_does_not_define_dynamic_bicarbonate_products() -> None:
    kb = load_knowledge(ROOT)
    plan = next(plan for plan in compile_rules(kb) if plan.rule_id == "rule_m17_nahco3_heated_decomposition")

    assert len(plan.patterns) == 1
    assert plan.patterns[0].target_id == "ent_substance_nahco3"
    assert plan.patterns[0].phase == "solid"
    assert [(product.target_id, product.phase) for product in plan.products] == [
        ("ent_substance_na2co3", "solid"),
        ("ent_substance_h2o", "gas"),
        ("ent_substance_co2", "gas"),
    ]


def test_m17_thermal_reaction_has_no_ionic_reaction_forms(tmp_path: Path) -> None:
    kb = load_knowledge(ROOT)
    reaction = kb.reactions["rxn_m17_nahco3_heated_decomposition"]
    assert reaction["forms"] == []

    compile_repository(ROOT, tmp_path / "compile", "m17-test")
    derived = json.loads((tmp_path / "compile" / "derived-reaction-forms.json").read_text(encoding="utf-8"))
    assert all(item["reaction_id"] != reaction["id"] for item in derived["forms"])


def test_m17_reuses_existing_canonical_identities() -> None:
    kb = load_knowledge(ROOT)

    assert kb.semantic_key_candidates("formula.unit", "NaHCO3") == ("ent_substance_nahco3",)
    assert kb.semantic_key_candidates("formula.unit", "Na2CO3") == ("ent_substance_na2co3",)
    assert kb.semantic_key_candidates("formula.unit", "H2O") == ("ent_substance_h2o",)
    assert kb.semantic_key_candidates("formula.molecular", "CO2") == ("ent_substance_co2",)
    assert kb.semantic_key_candidates("formula.unit", "KHCO3") == ("ent_substance_khco3",)


def test_m17_reuses_compatibility_coordinates_unchanged() -> None:
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


def test_m17_teaching_view_reuses_existing_view_without_claiming_ionic_equations() -> None:
    kb = load_knowledge(ROOT)
    assert tuple(kb.teaching_views) == ("view_f3b_hs_aqueous_core",)
    nodes = {
        node["path_key"]: set(node.get("members", []))
        for node in kb.teaching_views["view_f3b_hs_aqueous_core"]["nodes"]
    }

    reaction_id = "rxn_m17_nahco3_heated_decomposition"
    assert reaction_id in nodes["D03/reaction-types/decomposition"]
    assert reaction_id not in nodes["D06/notation/ionic-equations"]
    assert {"ent_substance_nahco3", "ent_substance_na2co3"} <= nodes[
        "D10/elements-and-compounds/representative-elements"
    ]


def test_m17_preserves_m7_m11_m15_and_m16_conditioned_inference() -> None:
    kb = load_knowledge(ROOT)
    plans = compile_rules(kb)
    cases = {case["id"]: case for case in load_cases(ROOT)}
    expected = {
        "case_m7_nh4cl_naoh": "rule_m7_ammonium_strong_base_gas_evolution",
        "case_m11_na_water": "rule_m11_water_reactive_metal_hydrogen",
        "case_m15_cuso4_naoh": "rule_m15_hydroxide_precipitation",
        "case_m16_caco3_heated": "rule_m16_caco3_heated_decomposition",
    }

    for case_id, rule_id in expected.items():
        result = infer_case(kb, plans, cases[case_id])
        assert result["status"] == "inferred", case_id
        assert result["rule_id"] == rule_id, case_id
        assert result["canonical_match"]["state"] == "exact", case_id
