from copy import deepcopy
from pathlib import Path

from compiler.engine import infer_case
from compiler.reaction_forms import derive_aqueous_ionic_form
from compiler.rules import compile_rules
from compiler.source import load_cases, load_knowledge


ROOT = Path(__file__).resolve().parents[1]


def test_aluminate_dissolution_and_net_ionic_form():
    kb = load_knowledge(ROOT)
    plans = compile_rules(kb)
    case = next(c for c in load_cases(ROOT) if c["id"] == "case_curriculum_aluminium_hydroxide_naoh")
    result = infer_case(kb, plans, case)
    assert result["status"] == "inferred"
    assert result["canonical_match"]["reaction_ids"] == ["rxn_curriculum_aluminium_hydroxide_naoh"]
    assert result["validation"] == {"atoms": True, "charge": True}
    ionic = derive_aqueous_ionic_form(kb, "rxn_curriculum_aluminium_hydroxide_naoh", "net_ionic", case["context"])
    assert ionic["status"] == "derived"
    assert ionic["validation"] == {"atoms": True, "charge": True}
    assert {(p["role"], p["target_id"], p["phase"]): p["coefficient"] for p in ionic["participants"]} == {
        ("reactant", "ent_substance_al_oh_3", "solid"): {"numerator": 1, "denominator": 1},
        ("reactant", "ent_species_oh_minus", "dissolved"): {"numerator": 1, "denominator": 1},
        ("product", "ent_species_al_oh_4_minus", "dissolved"): {"numerator": 1, "denominator": 1},
    }
    independent = deepcopy(kb)
    independent.reactions.clear()
    assert infer_case(independent, plans, case)["status"] == "inferred"
    for key in ["medium", "temperature_regime"]:
        missing = deepcopy(case)
        del missing["context"][key]
        assert infer_case(kb, plans, missing)["status"] == "indeterminate"
    absent_solid = deepcopy(case)
    absent_solid["reactants"][0] = {"target_id": "ent_substance_alcl3", "phase": "aqueous"}
    assert infer_case(kb, plans, absent_solid)["status"] != "inferred"
    assert kb.semantic_key_candidates("formula.ion", "AlO2-") == ()


def test_aluminium_and_alumina_base_paths_require_explicit_water_and_balance():
    kb = load_knowledge(ROOT)
    plans = compile_rules(kb)
    cases = {case["id"]: case for case in load_cases(ROOT)}
    expected = {
        "case_curriculum_aluminium_naoh": (
            "rule_curriculum_aluminium_naoh",
            "rxn_curriculum_aluminium_naoh",
            {"ent_substance_elemental_al": 2, "ent_substance_naoh": 2,
             "ent_substance_h2o": 6, "ent_substance_na_al_oh_4": 2,
             "ent_substance_h2": 3},
        ),
        "case_curriculum_alumina_naoh": (
            "rule_curriculum_alumina_naoh",
            "rxn_curriculum_alumina_naoh",
            {"ent_substance_al2o3": 1, "ent_substance_naoh": 2,
             "ent_substance_h2o": 3, "ent_substance_na_al_oh_4": 2},
        ),
    }
    for case_id, (rule_id, reaction_id, coefficients) in expected.items():
        result = infer_case(kb, plans, deepcopy(cases[case_id]))
        assert result["status"] == "inferred"
        assert result["rule_id"] == rule_id
        assert result["canonical_match"]["reaction_ids"] == [reaction_id]
        assert result["validation"] == {"atoms": True, "charge": True}
        assert {item["target_id"]: item["coefficient"] for item in result["participants"]} == {
            target_id: {"numerator": coefficient, "denominator": 1}
            for target_id, coefficient in coefficients.items()
        }

        reordered = deepcopy(cases[case_id])
        reordered["reactants"].reverse()
        assert infer_case(kb, plans, reordered) == result

        missing_water = deepcopy(cases[case_id])
        missing_water["reactants"] = [
            item for item in missing_water["reactants"]
            if item["target_id"] != "ent_substance_h2o"
        ]
        assert infer_case(kb, plans, missing_water)["status"] != "inferred"

        missing_temperature = deepcopy(cases[case_id])
        del missing_temperature["context"]["temperature_regime"]
        assert infer_case(kb, plans, missing_temperature)["status"] == "indeterminate"

    independent = deepcopy(kb)
    independent.reactions.clear()
    for case_id in expected:
        assert infer_case(independent, plans, cases[case_id])["status"] == "inferred"

