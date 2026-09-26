from copy import deepcopy
from dataclasses import replace
from pathlib import Path

import pytest

from compiler.engine import infer_case, reaction_signature
from compiler.rules import compile_rules
from compiler.source import SourceError, load_cases, load_knowledge, validate_references


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def source():
    kb = load_knowledge(ROOT)
    return kb, compile_rules(kb), {case["id"]: case for case in load_cases(ROOT)}


def test_signature_respects_rational_ratios_and_merges_repeated_terms(source):
    kb, _, _ = source
    original = kb.reactions["rxn_hcl_naoh_neutralization"]["participants"]
    scaled = deepcopy(original)
    for item in scaled:
        item["coefficient"]["denominator"] *= 2
    assert reaction_signature(scaled) == reaction_signature(original)
    wrong_ratio = deepcopy(original)
    wrong_ratio[0]["coefficient"]["denominator"] *= 2
    assert reaction_signature(wrong_ratio) != reaction_signature(original)
    split = deepcopy(original)
    split[0]["coefficient"]["denominator"] *= 2
    split.append(deepcopy(split[0]))
    assert reaction_signature(split) == reaction_signature(original)
    assert reaction_signature(list(reversed(split))) == reaction_signature(original)


def test_repeated_reactant_identity_cannot_erase_phase_information(source):
    kb, plans, _ = source
    result = infer_case(kb, plans, {
        "id": "duplicate_input", "reactants": [
            {"target_id": "ent_substance_hcl", "phase": "aqueous"},
            {"target_id": "ent_substance_hcl", "phase": "gas"},
        ], "context": {"medium": "aqueous"},
    })
    assert result["status"] == "invalid"
    assert result["diagnostic"]["code"] == "duplicate_reactant"
    assert "candidate_key" not in result


@pytest.mark.parametrize("case_id", [
    "case_precipitation", "case_neutralization", "case_batch_a_hcl_khco3",
    "case_batch_a_hno3_k2co3", "case_batch_a_nh4_2so4_koh",
    "case_m21_hbr_k2so3", "case_m9_hcl_k2s2o3", "case_m10_mg_hcl",
])
def test_aqueous_families_reject_wrong_participant_phases(source, case_id):
    kb, plans, cases = source
    case = cases[case_id]
    assert infer_case(kb, plans, case)["status"] == "inferred"
    for index in range(len(case["reactants"])):
        wrong = deepcopy(case)
        wrong["reactants"][index]["phase"] = "gas"
        result = infer_case(kb, plans, wrong)
        assert result["status"] != "inferred"
        assert "candidate_key" not in result


@pytest.mark.parametrize("corruption", ["reaction", "form", "speciation", "composition", "charge", "facet"])
def test_invalid_canonical_chemistry_is_rejected_at_source_boundary(source, corruption):
    kb = deepcopy(source[0])
    entity = kb.entities["ent_substance_nacl"]
    reaction = kb.reactions["rxn_hcl_naoh_neutralization"]
    if corruption == "reaction":
        reaction["participants"][0]["coefficient"]["numerator"] += 1
    elif corruption == "form":
        reaction["forms"][0]["participants"][0]["coefficient"]["numerator"] += 1
    elif corruption == "speciation":
        entity["speciation_profiles"][0]["products"][0]["coefficient"]["numerator"] += 1
    elif corruption == "composition":
        entity["payload"]["composition"]["components"].append(
            deepcopy(entity["payload"]["composition"]["components"][0])
        )
    elif corruption == "charge":
        kb.entities["ent_species_na_plus"]["payload"]["composition"]["net_charge"] = 0
    else:
        entity["facet_assertions"].append({**entity["facet_assertions"][0], "value": False})
    with pytest.raises(SourceError):
        validate_references(kb)


def test_relation_target_cannot_hide_equal_specificity_contradiction(source):
    kb = deepcopy(source[0])
    zinc = kb.entities["ent_substance_elemental_zn"]
    base = {
        "relation_key": "metal.product_cation", "target_id": "ent_species_zn_2plus",
        "evidence_ids": ["ev_f2_reactions"],
    }
    zinc["relation_assertions"] = [
        {**base, "context": {"medium": "aqueous"}},
        {**base, "context": {"temperature_regime": "ambient"}, "truth": False},
    ]
    with pytest.raises(SourceError, match="ambiguous contextual relation"):
        kb.relation_assertions(zinc["id"], "metal.product_cation",
                               {"medium": "aqueous", "temperature_regime": "ambient"})


def test_unknown_path_is_not_reported_as_all_paths_blocked(source):
    kb, plans, cases = source
    plan = next(p for p in plans if p.rule_id == "rule_f2_strong_acid_base_neutralization")
    unknown = replace(plan, rule_id="rule_unknown", blockers=(replace(plan.blockers[0], key="missing"),))
    result = infer_case(kb, (plan, unknown), cases["case_blocked_frozen"])
    assert result["status"] == "indeterminate"
    assert result["diagnostic"]["code"] == "unknown_applicability"


def test_reactant_and_rule_order_do_not_change_results_or_proof_traces(source):
    kb, plans, cases = source
    for case in cases.values():
        reordered = {**case, "reactants": list(reversed(case["reactants"]))}
        assert infer_case(kb, plans, case) == infer_case(kb, tuple(reversed(plans)), reordered), case["id"]


@pytest.mark.parametrize("case_id", ["case_m10_zn_hcl", "case_m12_zn_cuso4"])
def test_multiple_supporting_assertions_do_not_make_one_product_ambiguous(source, case_id):
    kb, plans, cases = source
    kb = deepcopy(kb)
    relation_sources = [("ent_substance_elemental_zn", "metal.product_cation")]
    if case_id == "case_m12_zn_cuso4":
        relation_sources.append(("ent_species_cu_2plus", "ion.elemental_substance"))
    for entity_id, relation_key in relation_sources:
        assertions = kb.entities[entity_id]["relation_assertions"]
        original = next(item for item in assertions if item["relation_key"] == relation_key)
        original["context"] = {"medium": "aqueous"}
        assertions.append({
            **deepcopy(original),
            "context": {"temperature_regime": "ambient"},
            "evidence_ids": ["ev_f2_reactions"],
        })
    case = cases[case_id]
    result = infer_case(kb, plans, case)
    assert result["status"] == "inferred"
    assert result["validation"] == {"atoms": True, "charge": True}
    assert result["canonical_match"]["state"] == "exact"
    assert "ev_f2_reactions" in result["provenance"]["evidence_ids"]
    for entity_id, relation_key in relation_sources:
        proof = [item for item in result["provenance"]["relation_assertions"]
                 if item["source_id"] == entity_id and item["relation_key"] == relation_key]
        assert len(proof) == 2
        assert len({item["target_id"] for item in proof}) == 1
        kb.entities[entity_id]["relation_assertions"].reverse()
    assert infer_case(kb, plans, case) == result
