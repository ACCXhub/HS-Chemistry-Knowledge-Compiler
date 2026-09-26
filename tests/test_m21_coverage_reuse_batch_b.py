from __future__ import annotations

from pathlib import Path

import pytest

from compiler.build import ARTIFACT_FORMAT_VERSION, artifact_versions
from compiler.engine import infer_case
from compiler.reaction_forms import derive_aqueous_ionic_form
from compiler.rules import RULE_DSL_VERSION, RULE_PLAN_VERSION, compile_rules
from compiler.source import SOURCE_SCHEMA_VERSION, load_cases, load_knowledge


ROOT = Path(__file__).resolve().parents[1]
AMBIENT = {"medium": "aqueous", "temperature_regime": "ambient"}


CASES = (
    ("naoh", "rule_f2_strong_acid_base_neutralization", "rxn_m21_hbr_naoh_neutralization", 1),
    ("koh", "rule_f2_strong_acid_base_neutralization", "rxn_m21_hbr_koh_neutralization", 1),
    ("nahco3", "rule_m5_strong_acid_hydrogen_carbonate_gas_evolution", "rxn_m21_hbr_nahco3_gas_evolution", 1),
    ("khco3", "rule_m5_strong_acid_hydrogen_carbonate_gas_evolution", "rxn_m21_hbr_khco3_gas_evolution", 1),
    ("na2co3", "rule_m6_strong_acid_carbonate_gas_evolution", "rxn_m21_hbr_na2co3_gas_evolution", 2),
    ("k2co3", "rule_m6_strong_acid_carbonate_gas_evolution", "rxn_m21_hbr_k2co3_gas_evolution", 2),
    ("na2so3", "rule_m8_strong_acid_sulfite_gas_evolution", "rxn_m21_hbr_na2so3_gas_evolution", 2),
    ("k2so3", "rule_m8_strong_acid_sulfite_gas_evolution", "rxn_m21_hbr_k2so3_gas_evolution", 2),
)


@pytest.mark.parametrize(("partner", "rule_id", "reaction_id", "h_coefficient"), CASES)
def test_m21_hbr_cases_reuse_existing_rules_exactly(
    partner: str,
    rule_id: str,
    reaction_id: str,
    h_coefficient: int,
) -> None:
    kb = load_knowledge(ROOT)
    cases = {case["id"]: case for case in load_cases(ROOT)}

    first = infer_case(kb, compile_rules(kb), cases[f"case_m21_hbr_{partner}"])
    second = infer_case(kb, compile_rules(kb), cases[f"case_m21_hbr_{partner}"])

    assert first == second
    assert first["status"] == "inferred"
    assert first["rule_id"] == rule_id
    assert first["canonical_match"]["state"] == "exact"
    assert first["canonical_match"]["reaction_ids"] == [reaction_id]
    assert first["validation"] == {"atoms": True, "charge": True}
    hbr = next(item for item in first["participants"] if item["target_id"] == "ent_substance_hbr")
    assert hbr["coefficient"]["numerator"] == h_coefficient
    assert "ev_m21_hydrobromic_acid" in first["provenance"]["evidence_ids"]


@pytest.mark.parametrize(
    ("reaction_id", "expected"),
    [
        (
            "rxn_m21_hbr_naoh_neutralization",
            [("reactant", "ent_species_h_plus", 1), ("reactant", "ent_species_oh_minus", 1), ("product", "ent_substance_h2o", 1)],
        ),
        (
            "rxn_m21_hbr_nahco3_gas_evolution",
            [("reactant", "ent_species_h_plus", 1), ("reactant", "ent_species_hco3_minus", 1), ("product", "ent_substance_co2", 1), ("product", "ent_substance_h2o", 1)],
        ),
        (
            "rxn_m21_hbr_na2co3_gas_evolution",
            [("reactant", "ent_species_h_plus", 2), ("reactant", "ent_species_co3_2minus", 1), ("product", "ent_substance_co2", 1), ("product", "ent_substance_h2o", 1)],
        ),
        (
            "rxn_m21_hbr_na2so3_gas_evolution",
            [("reactant", "ent_species_h_plus", 2), ("reactant", "ent_species_so3_2minus", 1), ("product", "ent_substance_so2", 1), ("product", "ent_substance_h2o", 1)],
        ),
    ],
)
def test_m21_representative_ionic_forms_cancel_bromide_spectator(
    reaction_id: str,
    expected: list[tuple[str, str, int]],
) -> None:
    kb = load_knowledge(ROOT)
    complete = derive_aqueous_ionic_form(kb, reaction_id, "complete_ionic", AMBIENT)
    net = derive_aqueous_ionic_form(kb, reaction_id, "net_ionic", AMBIENT)

    assert complete["status"] == "derived"
    assert complete["validation"] == {"atoms": True, "charge": True}
    assert net["status"] == "derived"
    assert net["validation"] == {"atoms": True, "charge": True}
    normalized = sorted(
        (item["role"], item["target_id"], item["coefficient"]["numerator"])
        for item in net["participants"]
    )
    assert normalized == sorted(expected)
    assert all(item["target_id"] != "ent_species_br_minus" for item in net["participants"])


def test_m21_hbr_identity_evidence_and_teaching_projection() -> None:
    kb = load_knowledge(ROOT)
    assert kb.semantic_key_candidates("formula.molecular", "HBr") == ("ent_substance_hbr",)
    entity = kb.entities["ent_substance_hbr"]
    assert entity["evidence_ids"] == ["ev_m21_hydrobromic_acid"]
    assert kb.property_fact("ent_substance_hbr", "acid.strength", {"medium": "aqueous"}).value == "strong"
    profiles = kb.speciation_profiles("ent_substance_hbr", {"medium": "aqueous"})
    assert len(profiles) == 1

    view = kb.teaching_views["view_f3b_hs_aqueous_core"]
    by_path = {node["path_key"]: set(node.get("members", [])) for node in view["nodes"]}
    reaction_ids = {reaction_id for _, _, reaction_id, _ in CASES}
    assert "ent_substance_hbr" in by_path["D02/electrolyte-solutions/strong-electrolytes"]
    assert "ent_substance_hbr" in by_path["D08/substance-classification/acids"]
    assert "ent_substance_hbr" in by_path["D10/elements-and-compounds/representative-elements"]
    assert reaction_ids <= by_path["D06/notation/ionic-equations"]
    assert {item for item in reaction_ids if "neutralization" in item} <= by_path["D03/reaction-types/neutralization"]
    assert {item for item in reaction_ids if "gas_evolution" in item} <= by_path["D03/reaction-types/gas-evolution"]


def test_m21_unsupported_neighbors_remain_unknown() -> None:
    kb = load_knowledge(ROOT)
    plans = compile_rules(kb)
    cases = {case["id"]: case for case in load_cases(ROOT)}
    for case_id in ("case_m21_hbr_na2co3_unknown_medium",):
        result = infer_case(kb, plans, cases[case_id])
        assert result["status"] == "indeterminate"
        assert "candidate_key" not in result


def test_m21_is_data_only_and_preserves_compatibility() -> None:
    kb = load_knowledge(ROOT)
    plans = compile_rules(kb)
    selected = {
        infer_case(kb, plans, case)["rule_id"]
        for case in load_cases(ROOT)
        if case["id"].startswith("case_m21_hbr_")
        and not case["id"].endswith(("unknown_redox", "unknown_medium"))
    }
    assert selected == {
        "rule_f2_strong_acid_base_neutralization",
        "rule_m5_strong_acid_hydrogen_carbonate_gas_evolution",
        "rule_m6_strong_acid_carbonate_gas_evolution",
        "rule_m8_strong_acid_sulfite_gas_evolution",
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
