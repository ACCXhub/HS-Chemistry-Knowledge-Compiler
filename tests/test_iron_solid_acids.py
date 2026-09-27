from copy import deepcopy
from dataclasses import replace
from pathlib import Path

import pytest

from compiler.engine import infer_case
from compiler.reaction_forms import derive_aqueous_ionic_form
from compiler.rules import compile_rules
from compiler.source import load_cases, load_knowledge


ROOT = Path(__file__).resolve().parents[1]
# Independently specified net ionic coefficients (solid, H+, iron ion, H2O).
ACIDS = {
    "feo_hcl": ("feo", 1, 2, "fe_2plus", 1, 1),
    "fe2o3_hcl": ("fe2o3", 1, 6, "fe_3plus", 2, 3),
    "fe2o3_hno3": ("fe2o3", 1, 6, "fe_3plus", 2, 3),
    "fe_oh_2_hcl": ("fe_oh_2", 1, 2, "fe_2plus", 1, 2),
    "fe_oh_3_hcl": ("fe_oh_3", 1, 3, "fe_3plus", 1, 3),
    "fe_oh_3_hno3": ("fe_oh_3", 1, 3, "fe_3plus", 1, 3),
}


@pytest.fixture(scope="module")
def source():
    kb = load_knowledge(ROOT)
    return kb, compile_rules(kb), {case["id"]: case for case in load_cases(ROOT)}


@pytest.mark.parametrize("path", [*ACIDS, "ferric_nitrate_naoh", "ferric_nitrate_koh"])
def test_acid_dissolution_and_ferric_nitrate_precipitation(source, path):
    kb, plans, cases = source
    case = cases["case_curriculum_" + path]
    result = infer_case(kb, plans, case)
    assert result["status"] == "inferred"
    assert result["validation"] == {"atoms": True, "charge": True}
    assert result["canonical_match"]["reaction_ids"] == ["rxn_curriculum_" + path]
    reversed_case = deepcopy(case)
    reversed_case["reactants"].reverse()
    assert infer_case(kb, tuple(reversed(plans)), reversed_case) == result
    form = derive_aqueous_ionic_form(kb, "rxn_curriculum_" + path, "net_ionic", case["context"])
    assert form["status"] == "derived"
    assert form["validation"] == {"atoms": True, "charge": True}
    if path in ACIDS:
        solid, solid_n, protons, cation, ion_n, water = ACIDS[path]
        expected = {("reactant", "ent_substance_" + solid): solid_n,
                    ("reactant", "ent_species_h_plus"): protons,
                    ("product", "ent_species_" + cation): ion_n,
                    ("product", "ent_substance_h2o"): water}
        assert result["rule_id"] == "rule_solid_iron_" + solid + "_acid"
        assert not kb.entities["ent_substance_" + solid].get("speciation_profiles")
    else:
        expected = {("reactant", "ent_species_fe_3plus"): 1,
                    ("reactant", "ent_species_oh_minus"): 3,
                    ("product", "ent_substance_fe_oh_3"): 1}
        assert result["rule_id"] == "rule_m15_hydroxide_precipitation"
    assert {(p["role"], p["target_id"]): p["coefficient"] for p in form["participants"]} == {
        key: {"numerator": n, "denominator": 1} for key, n in expected.items()
    }


@pytest.mark.parametrize("solid", ["feo", "fe_oh_2"])
def test_nitric_acid_does_not_produce_unreviewed_ferrous_salt(source, solid):
    kb, plans, cases = source
    result = infer_case(kb, plans, cases["case_curriculum_" + solid + "_hno3_unknown"])
    assert result["status"] == "indeterminate"
    assert "candidate_key" not in result
    assert any(event.get("rule_id") == "rule_solid_iron_" + solid + "_acid"
               and event.get("key") == "acid.redox_character" and event.get("truth") == "UNKNOWN"
               for event in result["proof_trace"])


@pytest.mark.parametrize("solid", ["feo", "fe_oh_2"])
@pytest.mark.parametrize("redox", [None, "oxidizing"])
def test_ferrous_dissolution_needs_positive_non_oxidizing_evidence(source, solid, redox):
    kb, plans, cases = source
    entities = deepcopy(kb.entities)
    acid = entities["ent_substance_hcl"]
    fact = next(p for p in acid["property_assertions"] if p["property_key"] == "acid.redox_character")
    if redox is None:
        acid["property_assertions"].remove(fact)
    else:
        fact["value"] = redox
    result = infer_case(replace(kb, entities=entities), plans, cases["case_curriculum_" + solid + "_hcl"])
    assert result["status"] != "inferred"
    assert "candidate_key" not in result
    assert any(event.get("rule_id") == "rule_solid_iron_" + solid + "_acid"
               and event.get("key") == "acid.redox_character"
               and event.get("truth") == ("UNKNOWN" if redox is None else "FALSE")
               for event in result["proof_trace"])


@pytest.mark.parametrize("solid", ["feo", "fe2o3", "fe_oh_2", "fe_oh_3"])
@pytest.mark.parametrize("change", ["phase", "medium", "temperature"])
def test_solid_acid_rules_preserve_phase_and_context_boundaries(source, solid, change):
    kb, plans, cases = source
    case = deepcopy(cases["case_curriculum_" + solid + "_hcl"])
    if change == "phase":
        case["reactants"][0]["phase"] = "aqueous"
    else:
        del case["context"]["medium" if change == "medium" else "temperature_regime"]
    assert infer_case(kb, plans, case)["status"] != "inferred"
