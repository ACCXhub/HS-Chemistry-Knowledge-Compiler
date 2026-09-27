from copy import deepcopy
from pathlib import Path

import pytest

from compiler.engine import infer_case
from compiler.reaction_forms import derive_aqueous_ionic_form
from compiler.rules import compile_rules
from compiler.source import load_cases, load_knowledge


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "iron_ferric_chloride": {"elemental_fe": 1, "fecl3": 2, "fecl2": 3},
    "copper_ferric_chloride": {"elemental_cu": 1, "fecl3": 2, "cucl2": 1, "fecl2": 2},
    "ferrous_chloride_chlorine": {"fecl2": 2, "cl2": 1, "fecl3": 2},
}
NET_IONIC = {
    "iron_ferric_chloride": {
        ("reactant", "ent_substance_elemental_fe"): 1,
        ("reactant", "ent_species_fe_3plus"): 2,
        ("product", "ent_species_fe_2plus"): 3,
    },
    "copper_ferric_chloride": {
        ("reactant", "ent_substance_elemental_cu"): 1,
        ("reactant", "ent_species_fe_3plus"): 2,
        ("product", "ent_species_cu_2plus"): 1,
        ("product", "ent_species_fe_2plus"): 2,
    },
    "ferrous_chloride_chlorine": {
        ("reactant", "ent_species_fe_2plus"): 2,
        ("reactant", "ent_substance_cl2"): 1,
        ("product", "ent_species_fe_3plus"): 2,
        ("product", "ent_species_cl_minus"): 2,
    },
}


@pytest.fixture(scope="module")
def source():
    kb = load_knowledge(ROOT)
    return kb, compile_rules(kb), {case["id"]: case for case in load_cases(ROOT)}


@pytest.mark.parametrize("path", EXPECTED)
def test_specific_redox_products_and_ionic_coefficients(source, path):
    kb, plans, cases = source
    case = cases["case_curriculum_" + path]
    result = infer_case(kb, plans, case)
    assert result["status"] == "inferred"
    assert result["rule_id"] == "rule_curriculum_" + path
    assert result["validation"] == {"atoms": True, "charge": True}
    assert result["canonical_match"]["reaction_ids"] == ["rxn_curriculum_" + path]
    assert {item["target_id"].removeprefix("ent_substance_"): item["coefficient"]
            for item in result["participants"]} == {
        key: {"numerator": value, "denominator": 1} for key, value in EXPECTED[path].items()
    }
    assert "ev_curriculum_iron_chloride_redox" in result["provenance"]["evidence_ids"]
    reversed_case = deepcopy(case)
    reversed_case["reactants"].reverse()
    assert infer_case(kb, tuple(reversed(plans)), reversed_case) == result
    form = derive_aqueous_ionic_form(kb, "rxn_curriculum_" + path, "net_ionic", case["context"])
    assert form["status"] == "derived"
    assert form["validation"] == {"atoms": True, "charge": True}
    assert {(item["role"], item["target_id"]): item["coefficient"]
            for item in form["participants"]} == {
        key: {"numerator": value, "denominator": 1} for key, value in NET_IONIC[path].items()
    }


@pytest.mark.parametrize("path", EXPECTED)
@pytest.mark.parametrize("change", ["missing_medium", "missing_temperature", "dry_salt", "heated"])
def test_redox_special_cases_require_declared_phase_and_context(source, path, change):
    kb, plans, cases = source
    case = deepcopy(cases["case_curriculum_" + path])
    if change == "missing_medium":
        del case["context"]["medium"]
    elif change == "missing_temperature":
        del case["context"]["temperature_regime"]
    elif change == "heated":
        case["context"]["temperature_regime"] = "heated"
    else:
        next(item for item in case["reactants"] if item["phase"] == "aqueous")["phase"] = "solid"
    result = infer_case(kb, plans, case)
    assert result["status"] != "inferred"
    assert "candidate_key" not in result
    if change.startswith("missing_"):
        assert result["status"] == "indeterminate"


def test_copper_reduction_does_not_turn_ferric_or_ferrous_iron_into_iron_metal(source):
    kb, plans, cases = source
    case = deepcopy(cases["case_curriculum_copper_ferric_chloride"])
    result = infer_case(kb, plans, case)
    assert "ent_substance_elemental_fe" not in {p["target_id"] for p in result["participants"]}
    case["reactants"][1]["target_id"] = "ent_substance_fecl2"
    result = infer_case(kb, plans, case)
    assert result["status"] != "inferred"
    assert "candidate_key" not in result
    assert any(event.get("key") == "metal.displaces_cation"
               and event.get("target_id") == "ent_species_fe_2plus"
               and event.get("truth") == "FALSE" for event in result["proof_trace"])
