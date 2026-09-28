from copy import deepcopy
from pathlib import Path

import pytest

from compiler.engine import infer_case
from compiler.rules import compile_rules
from compiler.source import load_cases, load_knowledge


@pytest.fixture(scope="module")
def source():
    root = Path(__file__).resolve().parents[1]
    kb = load_knowledge(root)
    return kb, compile_rules(kb), {c["id"]: c for c in load_cases(root)}


@pytest.mark.parametrize("name,expected", [
    ("copper_oxygen", {"elemental_cu": 2, "o2": 1, "cuo": 2}),
    ("aluminium_oxygen", {"elemental_al": 4, "o2": 3, "al2o3": 2}),
    ("aluminium_steam", {"elemental_al": 2, "h2o": 3, "al2o3": 1, "h2": 3}),
    ("aluminium_hydroxide_thermal", {"al_oh_3": 2, "al2o3": 1, "h2o": 3}),
])
def test_explicit_thermal_path(source, name, expected):
    kb, plans, cases = source
    case = cases["case_curriculum_" + name]
    result = infer_case(kb, plans, case)
    assert result["status"] == "inferred"
    assert result["canonical_match"]["reaction_ids"] == ["rxn_curriculum_" + name]
    assert {p["target_id"].removeprefix("ent_substance_"): p["coefficient"]
            for p in result["participants"]} == {
                k: {"numerator": v, "denominator": 1} for k, v in expected.items()}
    for key in ("medium", "temperature_regime"):
        missing = deepcopy(case)
        del missing["context"][key]
        assert infer_case(kb, plans, missing)["status"] == "indeterminate"
    for key, value in [("medium", "aqueous"), ("temperature_regime", "ambient")]:
        wrong = deepcopy(case)
        wrong["context"][key] = value
        assert infer_case(kb, plans, wrong)["status"] != "inferred"
    if name == "aluminium_steam":
        wrong = deepcopy(case)
        wrong["reactants"][1]["phase"] = "liquid"
        assert infer_case(kb, plans, wrong)["status"] != "inferred"
