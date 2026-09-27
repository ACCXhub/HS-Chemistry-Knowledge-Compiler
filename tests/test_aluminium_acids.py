from copy import deepcopy
from pathlib import Path

import pytest

from compiler.engine import infer_case
from compiler.reaction_forms import derive_aqueous_ionic_form
from compiler.rules import compile_rules
from compiler.source import load_cases, load_knowledge


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def source():
    kb = load_knowledge(ROOT)
    return kb, compile_rules(kb), {c["id"]: c for c in load_cases(ROOT)}


@pytest.mark.parametrize("name,rule,expected", [
    ("aluminium_hcl", "rule_m10_active_metal_non_oxidizing_acid_hydrogen",
     {"elemental_al": 2, "hcl": 6, "alcl3": 2, "h2": 3}),
    ("alumina_hcl", "rule_curriculum_alumina_acid",
     {"al2o3": 1, "hcl": 6, "alcl3": 2, "h2o": 3}),
])
def test_existing_product_construction_balances_aluminium(source, name, rule, expected):
    kb, plans, cases = source
    case = deepcopy(cases["case_curriculum_" + name])
    result = infer_case(kb, plans, case)
    assert result["status"] == "inferred"
    assert result["rule_id"] == rule
    assert result["canonical_match"]["reaction_ids"] == ["rxn_curriculum_" + name]
    assert result["validation"] == {"atoms": True, "charge": True}
    assert {p["target_id"].removeprefix("ent_substance_"): p["coefficient"]
            for p in result["participants"]} == {
        k: {"numerator": n, "denominator": 1} for k, n in expected.items()
    }
    case["reactants"].reverse()
    assert infer_case(kb, tuple(reversed(plans)), case) == result
    independent = deepcopy(kb)
    independent.reactions.clear()
    assert infer_case(independent, plans, case)["status"] == "inferred"


@pytest.mark.parametrize("name,reactant,n,water", [
    ("aluminium_hcl", "ent_substance_elemental_al", 2, False),
    ("alumina_hcl", "ent_substance_al2o3", 1, True),
])
def test_net_ionic_equations_retain_aluminium_three_plus(source, name, reactant, n, water):
    kb, _, _ = source
    result = derive_aqueous_ionic_form(kb, "rxn_curriculum_" + name, "net_ionic", {"medium": "aqueous"})
    assert result["status"] == "derived"
    assert result["validation"] == {"atoms": True, "charge": True}
    expected = {reactant: n, "ent_species_h_plus": 6, "ent_species_al_3plus": 2,
                "ent_substance_h2o" if water else "ent_substance_h2": 3}
    assert {p["target_id"]: p["coefficient"] for p in result["participants"]} == {
        k: {"numerator": v, "denominator": 1} for k, v in expected.items()
    }


def test_oxidizing_acid_does_not_take_hydrogen_path(source):
    kb, plans, cases = source
    case = deepcopy(cases["case_curriculum_aluminium_hcl"])
    case["reactants"][1]["target_id"] = "ent_substance_hno3"
    result = infer_case(kb, plans, case)
    assert result["status"] != "inferred"
    assert "candidate_key" not in result


@pytest.mark.parametrize("name", ["aluminium_hcl", "alumina_hcl"])
def test_missing_medium_preserves_unknown(source, name):
    kb, plans, cases = source
    case = deepcopy(cases["case_curriculum_" + name])
    del case["context"]["medium"]
    assert infer_case(kb, plans, case)["status"] == "indeterminate"


def test_alumina_is_not_falsely_dissociated_or_classified_basic(source):
    kb, _, _ = source
    oxide = kb.entities["ent_substance_al2o3"]
    assert not oxide.get("speciation_profiles")
    assert not any(f["facet_key"] == "classification.basic_oxide" and f.get("value") is True
                   for f in oxide.get("facet_assertions", []))
