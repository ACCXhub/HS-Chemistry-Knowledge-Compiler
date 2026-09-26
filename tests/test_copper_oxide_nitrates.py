from pathlib import Path

import pytest

from compiler.engine import infer_case
from compiler.reaction_forms import derive_aqueous_ionic_form
from compiler.rules import compile_rules
from compiler.source import load_cases, load_knowledge


ROOT = Path(__file__).resolve().parents[1]
PATHS = ["cuo_hcl", "cuo_hno3", "cao_hno3", "caco3_hno3", "zinc_copper_nitrate",
         "magnesium_copper_nitrate", "copper_nitrate_naoh", "copper_nitrate_koh"]


@pytest.fixture(scope="module")
def source():
    kb = load_knowledge(ROOT)
    return kb, compile_rules(kb), {case["id"]: case for case in load_cases(ROOT)}


@pytest.mark.parametrize("path", PATHS)
def test_missing_product_identities_unlock_existing_chemistry_paths(source, path):
    kb, plans, cases = source
    result = infer_case(kb, plans, cases["case_curriculum_" + path])
    assert result["status"] == "inferred"
    assert result["validation"] == {"atoms": True, "charge": True}
    assert result["canonical_match"]["reaction_ids"] == ["rxn_curriculum_" + path]
    assert result["rule_id"] in {
        "rule_basic_oxide_cuo_acid", "rule_basic_oxide_cao_acid", "rule_solid_calcium_carbonate_acid",
        "rule_m19_generic_aqueous_metal_salt_displacement", "rule_m15_hydroxide_precipitation",
    }
    form = derive_aqueous_ionic_form(kb, "rxn_curriculum_" + path, "net_ionic", cases["case_curriculum_" + path]["context"])
    assert form["status"] == "derived"
    assert form["validation"] == {"atoms": True, "charge": True}


def test_nitrate_salt_reuse_does_not_make_nitric_acid_non_oxidizing(source):
    kb, plans, cases = source
    result = infer_case(kb, plans, cases["case_curriculum_iron_nitric_unknown"])
    assert "candidate_key" not in result
    assert any(event.get("key") == "acid.redox_character" and event.get("truth") == "UNKNOWN"
               for event in result["proof_trace"])
    for path in ["cuo_hcl", "cuo_hno3"]:
        result = infer_case(kb, plans, cases["case_curriculum_" + path])
        assert {item["target_id"]: item["coefficient"]["numerator"] for item in result["participants"]
                if item["role"] == "reactant"} == {
            "ent_substance_cuo": 1, "ent_substance_" + path.split("_")[1]: 2,
        }
