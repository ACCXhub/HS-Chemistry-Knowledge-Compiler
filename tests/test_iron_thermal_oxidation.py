from copy import deepcopy
from pathlib import Path

import pytest

from compiler.engine import infer_case
from compiler.application import InferenceSession, export_bundle
from compiler.reaction_forms import derive_aqueous_ionic_form
from compiler.rules import compile_rules
from compiler.source import SourceError, load_cases, load_knowledge


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "magnetite_hcl": {"fe3o4": 1, "hcl": 8, "fecl2": 1, "fecl3": 2, "h2o": 4},
    "ferrous_hydroxide_oxidation": {"fe_oh_2": 4, "o2": 1, "h2o": 2, "fe_oh_3": 4},
    "iron_steam": {"elemental_fe": 3, "h2o": 4, "fe3o4": 1, "h2": 4},
    "iron_oxygen": {"elemental_fe": 3, "o2": 2, "fe3o4": 1},
    "iron_chlorine": {"elemental_fe": 2, "cl2": 3, "fecl3": 2},
    "ferric_hydroxide_decomposition": {"fe_oh_3": 2, "fe2o3": 1, "h2o": 3},
}
THERMAL = ["iron_steam", "iron_oxygen", "iron_chlorine", "ferric_hydroxide_decomposition"]


@pytest.fixture(scope="module")
def source():
    kb = load_knowledge(ROOT)
    return kb, compile_rules(kb), {case["id"]: case for case in load_cases(ROOT)}


@pytest.mark.parametrize("path", EXPECTED)
def test_explicit_products_balance_and_input_order(source, path):
    kb, plans, cases = source
    case = cases["case_curriculum_" + path]
    result = infer_case(kb, plans, case)
    assert result["status"] == "inferred"
    assert result["rule_id"] == "rule_curriculum_" + path
    assert result["validation"] == {"atoms": True, "charge": True}
    assert result["canonical_match"]["reaction_ids"] == ["rxn_curriculum_" + path]
    assert {p["target_id"].removeprefix("ent_substance_"): p["coefficient"]
            for p in result["participants"]} == {
        key: {"numerator": n, "denominator": 1} for key, n in EXPECTED[path].items()
    }
    reverse = deepcopy(case)
    reverse["reactants"].reverse()
    assert infer_case(kb, tuple(reversed(plans)), reverse) == result
    if path == "iron_chlorine":
        assert next(p for p in result["participants"] if p["role"] == "product")["phase"] == "solid"
    if path == "ferric_hydroxide_decomposition":
        assert next(p for p in result["participants"] if p["target_id"] == "ent_substance_h2o")["phase"] == "gas"


def test_magnetite_net_ionic_equation_retains_both_iron_valences(source):
    kb, _, _ = source
    form = derive_aqueous_ionic_form(kb, "rxn_curriculum_magnetite_hcl", "net_ionic", {"medium": "aqueous"})
    assert form["status"] == "derived"
    assert form["validation"] == {"atoms": True, "charge": True}
    assert {(p["role"], p["target_id"]): p["coefficient"] for p in form["participants"]} == {
        (role, identity): {"numerator": n, "denominator": 1} for role, identity, n in [
            ("reactant", "ent_substance_fe3o4", 1), ("reactant", "ent_species_h_plus", 8),
            ("product", "ent_species_fe_2plus", 1), ("product", "ent_species_fe_3plus", 2),
            ("product", "ent_substance_h2o", 4),
        ]
    }


@pytest.mark.parametrize("path", THERMAL)
@pytest.mark.parametrize("temperature", [None, "ambient", "warmed"])
def test_thermal_paths_require_heated_context(source, path, temperature):
    kb, plans, cases = source
    case = deepcopy(cases["case_curriculum_" + path])
    case["context"] = {"medium": "non_aqueous"}
    if temperature is not None:
        case["context"]["temperature_regime"] = temperature
    result = infer_case(kb, plans, case)
    assert result["status"] != "inferred"
    assert "candidate_key" not in result


@pytest.mark.parametrize("path", THERMAL)
def test_dry_thermal_products_are_not_asserted_in_aqueous_medium(source, path):
    kb, plans, cases = source
    case = deepcopy(cases["case_curriculum_" + path])
    case["context"]["medium"] = "aqueous"
    result = infer_case(kb, plans, case)
    assert result["status"] != "inferred"
    assert "candidate_key" not in result


@pytest.mark.parametrize("path", THERMAL)
def test_missing_medium_is_unknown_not_implicitly_non_aqueous(source, path):
    kb, plans, cases = source
    case = deepcopy(cases["case_curriculum_" + path])
    del case["context"]["medium"]
    result = infer_case(kb, plans, case)
    assert result["status"] == "indeterminate"
    assert "candidate_key" not in result
    assert any(event.get("rule_id") == "rule_curriculum_" + path
               and event.get("key") == "medium" and event.get("truth") == "UNKNOWN"
               for event in result["proof_trace"])


def test_bundle_api_admits_explicit_non_aqueous_and_three_reactants(source, tmp_path):
    _, _, cases = source
    manifest = export_bundle(ROOT, tmp_path, "TEST")
    assert manifest["versions"]["source_schema"] == "3.9.0"
    session = InferenceSession(tmp_path)
    for name in ["iron_steam", "ferrous_hydroxide_oxidation"]:
        result = session.infer(cases["case_curriculum_" + name])["result"]
        assert result["status"] == "inferred"
    bad = deepcopy(cases["case_curriculum_iron_steam"])
    bad["context"]["medium"] = "dry"
    with pytest.raises(SourceError):
        session.infer(bad)


@pytest.mark.parametrize("case_id", ["case_curriculum_magnetite_nitric_unknown",
                                   "case_curriculum_ferrous_hydroxide_without_oxygen"])
def test_missing_redox_knowledge_or_oxygen_does_not_create_products(source, case_id):
    kb, plans, cases = source
    result = infer_case(kb, plans, cases[case_id])
    assert result["status"] == "indeterminate"
    assert "candidate_key" not in result


def test_iron_liquid_water_does_not_reuse_steam_path(source):
    kb, plans, cases = source
    case = deepcopy(cases["case_curriculum_iron_steam"])
    case["reactants"][1]["phase"] = "liquid"
    assert infer_case(kb, plans, case)["status"] != "inferred"


def test_precipitation_does_not_implicitly_oxidize_ferrous_hydroxide(source):
    kb, plans, cases = source
    result = infer_case(kb, plans, cases["case_curriculum_fecl2_naoh"])
    products = {p["target_id"] for p in result["participants"] if p["role"] == "product"}
    assert "ent_substance_fe_oh_2" in products
    assert "ent_substance_fe_oh_3" not in products
