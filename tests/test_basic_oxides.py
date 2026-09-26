from copy import deepcopy
from pathlib import Path

import pytest

from compiler.engine import infer_case
from compiler.reaction_forms import derive_aqueous_ionic_form
from compiler.rules import compile_rules
from compiler.source import load_cases, load_knowledge


ROOT = Path(__file__).resolve().parents[1]
PATHS = ["na2o_hcl", "na2o_hno3", "na2o_hbr", "mgo_hcl", "mgo_hno3", "cao_hcl"]


@pytest.fixture(scope="module")
def source():
    kb = load_knowledge(ROOT)
    return kb, compile_rules(kb), {case["id"]: case for case in load_cases(ROOT)}


@pytest.mark.parametrize("path", PATHS)
def test_basic_oxide_acid_generation_and_net_ionic_equation(source, path):
    kb, plans, cases = source
    case = cases[f"case_basic_oxide_{path}"]
    result = infer_case(kb, plans, case)
    assert result["status"] == "inferred"
    assert result["rule_id"] == f"rule_basic_oxide_{path.split('_')[0]}_acid"
    reaction_id = f"rxn_basic_oxide_{path}"
    assert result["canonical_match"]["reaction_ids"] == [reaction_id]
    assert result["validation"] == {"atoms": True, "charge": True}
    assert sorted(item["coefficient"]["numerator"] for item in result["participants"]) == (
        [1, 1, 2, 2] if path.startswith("na2o") else [1, 1, 1, 2]
    )
    form = derive_aqueous_ionic_form(kb, reaction_id, "net_ionic", case["context"])
    assert form["status"] == "derived"
    assert form["validation"] == {"atoms": True, "charge": True}
    assert not kb.entities[case["reactants"][0]["target_id"]].get("speciation_profiles")
    reversed_case = deepcopy(case)
    reversed_case["reactants"].reverse()
    assert infer_case(kb, plans, reversed_case) == result


def test_sodium_oxide_hydration_is_balanced_not_copied_from_printed_coefficient(source):
    kb, plans, cases = source
    result = infer_case(kb, plans, cases["case_sodium_oxide_water"])
    assert result["status"] == "inferred"
    assert result["rule_id"] == "rule_sodium_oxide_water"
    assert {item["target_id"]: item["coefficient"]["numerator"] for item in result["participants"]} == {
        "ent_substance_na2o": 1, "ent_substance_h2o": 1, "ent_substance_naoh": 2,
    }


@pytest.mark.parametrize("change", ["phase", "medium", "temperature", "weak_acid"])
def test_oxide_rule_does_not_ignore_phase_conditions_or_acid_strength(source, change):
    kb, plans, cases = source
    case = deepcopy(cases["case_basic_oxide_na2o_hcl"])
    if change == "phase":
        case["reactants"][0]["phase"] = "aqueous"
    elif change == "medium":
        del case["context"]["medium"]
    elif change == "temperature":
        case["context"]["temperature_regime"] = "heated"
    else:
        kb = deepcopy(kb)
        fact = next(p for p in kb.entities["ent_substance_hcl"]["property_assertions"]
                    if p["property_key"] == "acid.strength")
        fact["value"] = "weak"
    assert infer_case(kb, plans, case)["status"] != "inferred"


def test_sodium_oxide_hydration_does_not_generalize_to_magnesium_oxide(source):
    kb, plans, cases = source
    case = deepcopy(cases["case_sodium_oxide_water"])
    case["reactants"][0]["target_id"] = "ent_substance_mgo"
    assert infer_case(kb, plans, case)["status"] != "inferred"
