from copy import deepcopy
from dataclasses import replace
from pathlib import Path

import pytest

from compiler.engine import infer_case
from compiler.rules import compile_rules
from compiler.source import load_cases, load_knowledge


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def source():
    kb = load_knowledge(ROOT)
    return kb, compile_rules(kb), {case["id"]: case for case in load_cases(ROOT)}


def test_equation_generation_does_not_read_stored_reactions(source):
    kb, plans, cases = source
    without_reactions = replace(
        kb, reactions={}, records=tuple(record for record in kb.records if record["record_type"] != "reaction")
    )
    independent_plans = compile_rules(without_reactions)
    exercised = set()
    for case in cases.values():
        expected = infer_case(kb, plans, case)
        if expected["status"] != "inferred":
            continue
        result = infer_case(without_reactions, independent_plans, case)
        assert result["status"] == "inferred", case["id"]
        assert result["participants"] == expected["participants"], case["id"]
        assert result["candidate_key"] == expected["candidate_key"], case["id"]
        assert result["canonical_match"]["state"] == "none", case["id"]
        assert result["validation"] == {"atoms": True, "charge": True}
        exercised.add(result["rule_id"])
    assert exercised == set(kb.rules), "Every active Rule needs an independent generation proof"


@pytest.mark.parametrize("case_id", ["case_m8_hno3_na2so3", "case_batch_a_hno3_k2so3"])
def test_nitric_acid_is_not_assumed_to_give_simple_sulfite_gas_evolution(source, case_id):
    kb, plans, cases = source
    result = infer_case(kb, plans, cases[case_id])
    assert result["status"] == "indeterminate"
    assert "candidate_key" not in result
    redox = [item for item in result["proof_trace"]
             if item.get("rule_id") == "rule_m8_strong_acid_sulfite_gas_evolution"
             and item.get("key") == "acid.redox_character"]
    assert redox and all(item["truth"] == "UNKNOWN" for item in redox)
    for reaction in kb.reactions.values():
        reactants = {item["target_id"] for item in reaction["participants"] if item["role"] == "reactant"}
        assert not ("ent_substance_hno3" in reactants and reactants & {"ent_substance_na2so3", "ent_substance_k2so3"})


@pytest.mark.parametrize("value", [None, "oxidizing"])
def test_sulfite_rule_requires_known_non_oxidizing_acid(source, value):
    kb, plans, cases = source
    entities = deepcopy(kb.entities)
    acid = entities["ent_substance_hcl"]
    acid["property_assertions"] = [p for p in acid["property_assertions"] if p["property_key"] != "acid.redox_character"]
    if value is not None:
        acid["property_assertions"].append({
            "property_key": "acid.redox_character", "fact_kind": "contextual", "value_state": "known",
            "value": value, "context": {"medium": "aqueous"}, "evidence_ids": [],
        })
    result = infer_case(replace(kb, entities=entities), plans, cases["case_m8_hcl_na2so3"])
    assert "candidate_key" not in result
    redox = [item for item in result["proof_trace"]
             if item.get("rule_id") == "rule_m8_strong_acid_sulfite_gas_evolution"
             and item.get("key") == "acid.redox_character"]
    assert any(item["truth"] == ("UNKNOWN" if value is None else "FALSE") for item in redox)


def test_new_hbr_fact_generates_an_unstored_equation_through_existing_rule(source):
    kb, plans, cases = source
    result = infer_case(kb, plans, cases["case_hbr_na2s2o3_unstored"])
    assert result["status"] == "inferred"
    assert result["rule_id"] == "rule_m9_acid_thiosulfate_decomposition"
    assert result["canonical_match"]["state"] == "none"
    assert result["validation"] == {"atoms": True, "charge": True}
    assert "ev_hbr_non_oxidizing_acid" in result["provenance"]["evidence_ids"]
    assert {item["target_id"]: item["coefficient"] for item in result["participants"]} == {
        "ent_substance_hbr": {"numerator": 2, "denominator": 1},
        "ent_substance_na2s2o3": {"numerator": 1, "denominator": 1},
        "ent_substance_nabr": {"numerator": 2, "denominator": 1},
        "ent_substance_so2": {"numerator": 1, "denominator": 1},
        "ent_substance_elemental_sulfur": {"numerator": 1, "denominator": 1},
        "ent_substance_h2o": {"numerator": 1, "denominator": 1},
    }


@pytest.mark.parametrize("value", [None, "insoluble"])
def test_aqueous_salt_product_requires_contextual_solubility(source, value):
    kb, plans, cases = source
    entities = deepcopy(kb.entities)
    salt = entities["ent_substance_nacl"]
    salt["property_assertions"] = [p for p in salt.get("property_assertions", []) if p["property_key"] != "solubility.class"]
    if value is not None:
        salt["property_assertions"].append({
            "property_key": "solubility.class", "fact_kind": "contextual", "value_state": "known",
            "value": value, "context": {"medium": "aqueous"}, "evidence_ids": [],
        })
    result = infer_case(replace(kb, entities=entities), plans, cases["case_m8_hcl_na2so3"])
    assert result["status"] == "invalid"
    assert result["diagnostic"]["code"] == ("product_phase_unverified" if value is None else "product_phase_conflict")
    assert "candidate_key" not in result


def test_solid_calcium_carbonate_keeps_solid_identity_and_ionic_projection(source):
    from compiler.reaction_forms import derive_aqueous_ionic_form

    kb, plans, cases = source
    case = cases["case_solid_caco3_hcl"]
    result = infer_case(kb, plans, case)
    assert result["status"] == "inferred"
    assert result["canonical_match"]["reaction_ids"] == ["rxn_m25_hcl_caco3_gas_evolution"]
    assert not kb.entities["ent_substance_caco3"].get("speciation_profiles")
    form = derive_aqueous_ionic_form(kb, "rxn_m25_hcl_caco3_gas_evolution", "net_ionic", case["context"])
    assert form["status"] == "derived"
    assert form["validation"] == {"atoms": True, "charge": True}
    for phase in ["aqueous", "gas", "unknown"]:
        wrong = deepcopy(case)
        wrong["reactants"][1]["phase"] = phase
        assert infer_case(kb, plans, wrong)["status"] != "inferred"
    missing_medium = deepcopy(case)
    missing_medium["context"] = {}
    assert infer_case(kb, plans, missing_medium)["status"] == "indeterminate"
