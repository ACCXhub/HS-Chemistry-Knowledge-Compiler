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

