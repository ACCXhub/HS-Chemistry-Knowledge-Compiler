from copy import deepcopy
from pathlib import Path

import pytest

from compiler.engine import infer_case
from compiler.reaction_forms import derive_aqueous_ionic_form
from compiler.rules import compile_rules
from compiler.source import load_cases, load_knowledge


ROOT = Path(__file__).resolve().parents[1]
PATHS = ["iron_hcl", "iron_cuso4", "iron_cucl2", "zinc_feso4", "magnesium_feso4",
         "fecl2_naoh", "fecl2_koh", "feso4_naoh", "feso4_koh", "fecl3_koh"]


@pytest.fixture(scope="module")
def source():
    kb = load_knowledge(ROOT)
    return kb, compile_rules(kb), {case["id"]: case for case in load_cases(ROOT)}


@pytest.mark.parametrize("path", PATHS)
def test_iron_examples_reuse_existing_rules_and_conserve_ionic_forms(source, path):
    kb, plans, cases = source
    case = cases[f"case_curriculum_{path}"]
    result = infer_case(kb, plans, case)
    assert result["status"] == "inferred"
    assert result["rule_id"] in {
        "rule_m10_active_metal_non_oxidizing_acid_hydrogen",
        "rule_m19_generic_aqueous_metal_salt_displacement",
        "rule_m15_hydroxide_precipitation",
    }
    reaction_id = f"rxn_curriculum_{path}"
    assert result["canonical_match"]["reaction_ids"] == [reaction_id]
    assert result["validation"] == {"atoms": True, "charge": True}
    for kind in ["complete_ionic", "net_ionic"]:
        form = derive_aqueous_ionic_form(kb, reaction_id, kind, case["context"])
        assert form["status"] == "derived"
        assert form["validation"] == {"atoms": True, "charge": True}
    reversed_case = deepcopy(case)
    reversed_case["reactants"].reverse()
    assert infer_case(kb, plans, reversed_case) == result


def test_non_oxidizing_acid_forms_ferrous_not_ferric_chloride(source):
    kb, plans, cases = source
    result = infer_case(kb, plans, cases["case_curriculum_iron_hcl"])
    assert {item["target_id"]: item["coefficient"]["numerator"] for item in result["participants"]} == {
        "ent_substance_elemental_fe": 1, "ent_substance_hcl": 2,
        "ent_substance_fecl2": 1, "ent_substance_h2": 1,
    }
    result = infer_case(kb, plans, cases["case_curriculum_fecl3_koh"])
    assert {item["target_id"]: item["coefficient"]["numerator"] for item in result["participants"]} == {
        "ent_substance_fecl3": 1, "ent_substance_koh": 3,
        "ent_substance_fe_oh_3": 1, "ent_substance_kcl": 3,
    }


def test_known_displacement_negative_remains_distinct_from_missing_acid_redox(source):
    kb, plans, cases = source
    negative = infer_case(kb, plans, cases["case_curriculum_iron_zinc_negative"])
    unknown = infer_case(kb, plans, cases["case_curriculum_iron_nitric_unknown"])
    assert "candidate_key" not in negative and "candidate_key" not in unknown
    assert any(item.get("key") == "metal.displaces_cation" and item.get("truth") == "FALSE"
               for item in negative["proof_trace"])
    assert any(item.get("key") == "acid.redox_character" and item.get("truth") == "UNKNOWN"
               for item in unknown["proof_trace"])


def test_iron_displacement_does_not_invent_a_transitive_activity_order(source):
    kb, plans, _ = source
    result = infer_case(kb, plans, {
        "id": "iron_magnesium_unknown",
        "reactants": [{"target_id": "ent_substance_elemental_fe", "phase": "solid"},
                      {"target_id": "ent_substance_mgso4", "phase": "aqueous"}],
        "context": {"medium": "aqueous", "temperature_regime": "ambient"},
    })
    assert "candidate_key" not in result
    assert any(item.get("key") == "metal.displaces_cation" and item.get("truth") == "UNKNOWN"
               for item in result["proof_trace"])
