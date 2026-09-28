from copy import deepcopy
from pathlib import Path

import pytest

from compiler.engine import infer_case
from compiler.reaction_forms import derive_aqueous_ionic_form
from compiler.rules import compile_rules
from compiler.source import load_cases, load_knowledge


@pytest.fixture(scope="module")
def source():
    root = Path(__file__).resolve().parents[1]
    kb = load_knowledge(root)
    return kb, compile_rules(kb), {c["id"]: c for c in load_cases(root)}


@pytest.mark.parametrize("oxidant,halide", [("cl", "br"), ("cl", "i"), ("br", "i")])
@pytest.mark.parametrize("metal", ["na", "k"])
def test_halogen_displacement(source, oxidant, halide, metal):
    kb, plans, cases = source
    name = f"halogen_{oxidant}2_{metal}{halide}"
    case = cases["case_" + name]
    result = infer_case(kb, plans, case)
    assert result["status"] == "inferred"
    assert result["canonical_match"]["reaction_ids"] == ["rxn_" + name]
    assert result["validation"] == {"atoms": True, "charge": True}
    form = derive_aqueous_ionic_form(kb, "rxn_" + name, "net_ionic", case["context"])
    assert form["status"] == "derived"
    assert form["validation"] == {"atoms": True, "charge": True}
    assert {p["target_id"]: p["coefficient"]["numerator"] for p in form["participants"]} == {
        f"ent_substance_{oxidant}2": 1, f"ent_species_{halide}_minus": 2,
        f"ent_species_{oxidant}_minus": 2, f"ent_substance_{halide}2": 1,
    }
    for key in ("medium", "temperature_regime"):
        missing = deepcopy(case)
        del missing["context"][key]
        assert infer_case(kb, plans, missing)["status"] == "indeterminate"
    wrong = deepcopy(case)
    wrong["context"]["medium"] = "non_aqueous"
    assert infer_case(kb, plans, wrong)["status"] != "inferred"
    reverse = deepcopy(case)
    reverse["reactants"] = [{"target_id": p["target_id"], "phase": p["phase"]}
                            for p in result["participants"] if p["role"] == "product"]
    # No reverse path is authorized; no_match is not a global impossibility claim.
    assert infer_case(kb, plans, reverse)["status"] != "inferred"
