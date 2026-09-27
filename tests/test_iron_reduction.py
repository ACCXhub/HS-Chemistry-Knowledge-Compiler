from copy import deepcopy
from pathlib import Path

import pytest

from compiler.engine import infer_case
from compiler.rules import compile_rules
from compiler.source import load_cases, load_knowledge


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "iron_co_reduction": {("fe2o3", "solid"): 1, ("co", "gas"): 3,
                          ("elemental_fe", "solid"): 2, ("co2", "gas"): 3},
    "iron_thermite": {("fe2o3", "solid"): 1, ("elemental_al", "solid"): 2,
                     ("elemental_fe", "liquid"): 2, ("al2o3", "solid"): 1},
}


@pytest.fixture(scope="module")
def source():
    kb = load_knowledge(ROOT)
    return kb, compile_rules(kb), {c["id"]: c for c in load_cases(ROOT)}


@pytest.mark.parametrize("name", EXPECTED)
def test_reduction_coefficients_phases_and_determinism(source, name):
    kb, plans, cases = source
    case = deepcopy(cases["case_curriculum_" + name])
    result = infer_case(kb, plans, case)
    assert result["status"] == "inferred"
    assert result["canonical_match"]["reaction_ids"] == ["rxn_curriculum_" + name]
    assert result["validation"] == {"atoms": True, "charge": True}
    assert {(p["target_id"].removeprefix("ent_substance_"), p["phase"]): p["coefficient"]
            for p in result["participants"]} == {
        key: {"numerator": n, "denominator": 1} for key, n in EXPECTED[name].items()
    }
    case["reactants"].reverse()
    assert infer_case(kb, tuple(reversed(plans)), case) == result


@pytest.mark.parametrize("name", EXPECTED)
@pytest.mark.parametrize("key,value,status", [
    ("medium", None, "indeterminate"),
    ("medium", "aqueous", "no_match"),
    ("temperature_regime", None, "indeterminate"),
    ("temperature_regime", "ambient", "no_match"),
    ("temperature_regime", "warmed", "no_match"),
])
def test_reduction_requires_explicit_thermal_conditions(source, name, key, value, status):
    kb, plans, cases = source
    case = deepcopy(cases["case_curriculum_" + name])
    if value is None:
        del case["context"][key]
    else:
        case["context"][key] = value
    result = infer_case(kb, plans, case)
    assert result["status"] == status
    assert "candidate_key" not in result


@pytest.mark.parametrize("name", EXPECTED)
def test_reduction_does_not_substitute_other_iron_oxides(source, name):
    kb, plans, cases = source
    case = deepcopy(cases["case_curriculum_" + name])
    case["reactants"][0]["target_id"] = "ent_substance_fe3o4"
    assert infer_case(kb, plans, case)["status"] != "inferred"


@pytest.mark.parametrize("name", EXPECTED)
def test_reduction_generates_without_stored_reaction(source, name):
    kb, plans, cases = source
    independent = deepcopy(kb)
    independent.reactions.clear()
    result = infer_case(independent, plans, cases["case_curriculum_" + name])
    assert result["status"] == "inferred"
    assert result["validation"] == {"atoms": True, "charge": True}
