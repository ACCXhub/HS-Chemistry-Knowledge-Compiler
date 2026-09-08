from __future__ import annotations

import copy
import shutil
from dataclasses import replace
from pathlib import Path

import pytest
import yaml

from compiler.build import artifact_versions, audit_repository
from compiler.engine import infer_case
from compiler.reaction_forms import derive_aqueous_ionic_form
from compiler.rules import analyze_rule_overlaps, compile_rules
from compiler.source import load_knowledge


ROOT = Path(__file__).resolve().parents[1]
RULE_ID = "rule_m8_strong_acid_sulfite_gas_evolution"


def _atoms(entity: dict) -> dict[str, int]:
    return {
        component["element_id"]: component["count"]
        for component in entity["payload"]["composition"]["components"]
    }


def _case(case_id: str, acid_id: str, sulfite_id: str, *, include_medium: bool = True) -> dict:
    context = {"temperature_regime": "ambient"}
    if include_medium:
        context["medium"] = "aqueous"
    return {
        "id": case_id,
        "reactants": [
            {"target_id": acid_id, "phase": "aqueous"},
            {"target_id": sulfite_id, "phase": "aqueous"},
        ],
        "context": context,
    }


def _normalized(participants: list[dict]) -> list[tuple[str, str, int, int]]:
    return sorted(
        (
            item["role"],
            item["target_id"],
            item["coefficient"]["numerator"],
            item["coefficient"]["denominator"],
        )
        for item in participants
    )


def test_sulfite_and_sulfur_dioxide_have_exact_canonical_composition() -> None:
    kb = load_knowledge(ROOT)
    sulfite = kb.entities["ent_species_so3_2minus"]
    sulfur_dioxide = kb.entities["ent_substance_so2"]

    assert sulfite["entity_kind"] == "species"
    assert sulfite["payload"]["species_kind"] == "ion"
    assert sulfite["payload"]["formal_charge"] == -2
    assert sulfite["payload"]["composition"]["net_charge"] == -2
    assert _atoms(sulfite) == {"ent_element_s": 1, "ent_element_o": 3}
    assert sulfur_dioxide["payload"]["composition"]["net_charge"] == 0
    assert _atoms(sulfur_dioxide) == {"ent_element_s": 1, "ent_element_o": 2}


@pytest.mark.parametrize(
    ("substance_id", "cation_id", "element_id"),
    [
        ("ent_substance_na2so3", "ent_species_na_plus", "ent_element_na"),
        ("ent_substance_k2so3", "ent_species_k_plus", "ent_element_k"),
    ],
)
def test_soluble_sulfite_salts_have_exact_composition_and_speciation(
    substance_id: str,
    cation_id: str,
    element_id: str,
) -> None:
    kb = load_knowledge(ROOT)
    sulfite = kb.entities[substance_id]

    assert _atoms(sulfite) == {element_id: 2, "ent_element_s": 1, "ent_element_o": 3}
    assert sulfite["payload"]["composition"]["net_charge"] == 0
    assert kb.facet_fact(substance_id, "classification.salt").value is True
    assert kb.facet_fact(substance_id, "classification.sulfite").value is True
    assert kb.property_fact(substance_id, "electrolyte.strength", {"medium": "aqueous"}).value == "strong"
    assert kb.property_fact(substance_id, "solubility.class", {"medium": "aqueous"}).value == "soluble"
    assert kb.speciation_profiles(substance_id, {"medium": "aqueous"})[0]["products"] == [
        {"target_id": cation_id, "coefficient": {"numerator": 2, "denominator": 1}},
        {
            "target_id": "ent_species_so3_2minus",
            "coefficient": {"numerator": 1, "denominator": 1},
        },
    ]


@pytest.mark.parametrize(
    ("acid_id", "sulfite_id", "salt_id", "reaction_id"),
    [
        (
            "ent_substance_hcl",
            "ent_substance_na2so3",
            "ent_substance_nacl",
            "rxn_m8_hcl_na2so3_gas_evolution",
        ),
        (
            "ent_substance_hno3",
            "ent_substance_na2so3",
            "ent_substance_nano3",
            "rxn_m8_hno3_na2so3_gas_evolution",
        ),
        (
            "ent_substance_hcl",
            "ent_substance_k2so3",
            "ent_substance_kcl",
            "rxn_m8_hcl_k2so3_gas_evolution",
        ),
    ],
)
def test_acid_and_cation_substitutions_reuse_one_sulfite_rule(
    acid_id: str,
    sulfite_id: str,
    salt_id: str,
    reaction_id: str,
) -> None:
    kb = load_knowledge(ROOT)
    result = infer_case(kb, compile_rules(kb), _case(reaction_id, acid_id, sulfite_id))

    assert result["status"] == "inferred"
    assert result["rule_id"] == RULE_ID
    assert result["canonical_match"] == {
        "state": "exact",
        "reaction_ids": [reaction_id],
        "reaction_forms": {reaction_id: ["molecular", "complete_ionic", "net_ionic"]},
    }
    assert result["validation"] == {"atoms": True, "charge": True}
    assert _normalized(result["participants"]) == sorted(
        [
            ("reactant", acid_id, 2, 1),
            ("reactant", sulfite_id, 1, 1),
            ("product", salt_id, 2, 1),
            ("product", "ent_substance_so2", 1, 1),
            ("product", "ent_substance_h2o", 1, 1),
        ]
    )
    profiles = result["provenance"]["speciation_profiles"]
    assert {item["target_id"] for item in profiles} == {acid_id, sulfite_id}
    assert all(item["evidence_ids"] for item in profiles)


def test_sulfite_rule_is_generic_and_reuses_ionic_pair() -> None:
    plan = next(plan for plan in compile_rules(load_knowledge(ROOT)) if plan.rule_id == RULE_ID)

    assert all(pattern.target_id is None for pattern in plan.patterns)
    assert plan.patterns[1].required_facets == ("classification.salt", "classification.sulfite")
    assert plan.products[0].constructor == "ionic_pair"
    assert plan.products[0].cation_from == "sulfite"
    assert plan.products[0].anion_from == "acid"


def test_all_sulfite_examples_derive_the_same_conserved_net_ionic_form() -> None:
    kb = load_knowledge(ROOT)
    expected = sorted(
        [
            ("reactant", "ent_species_h_plus", 2, 1),
            ("reactant", "ent_species_so3_2minus", 1, 1),
            ("product", "ent_substance_so2", 1, 1),
            ("product", "ent_substance_h2o", 1, 1),
        ]
    )
    for reaction_id in (
        "rxn_m8_hcl_na2so3_gas_evolution",
        "rxn_m8_hno3_na2so3_gas_evolution",
        "rxn_m8_hcl_k2so3_gas_evolution",
    ):
        complete = derive_aqueous_ionic_form(kb, reaction_id, "complete_ionic", {"medium": "aqueous"})
        net = derive_aqueous_ionic_form(kb, reaction_id, "net_ionic", {"medium": "aqueous"})
        golden = next(form for form in kb.reactions[reaction_id]["forms"] if form["form_kind"] == "net_ionic")

        assert complete["status"] == "derived"
        assert complete["validation"] == {"atoms": True, "charge": True}
        assert net["status"] == "derived"
        assert net["reaction_id"] == reaction_id
        assert net["validation"] == {"atoms": True, "charge": True}
        assert _normalized(net["participants"]) == expected
        assert _normalized(net["participants"]) == _normalized(golden["participants"])
        assert net["derivation"]["operators"] == [
            "expand_approved_aqueous_speciation",
            "cancel_identical_canonical_spectators",
        ]
        assert net["derivation"]["speciation_profiles"]
        assert "ev_m8_sulfite_acid" in net["derivation"]["evidence_ids"]


def test_sulfate_contrast_and_unrelated_pair_do_not_infer_sulfur_dioxide() -> None:
    kb = load_knowledge(ROOT)
    plans = compile_rules(kb)

    sulfate = infer_case(kb, plans, _case("sulfate-contrast", "ent_substance_hcl", "ent_substance_na2so4"))
    unrelated = infer_case(
        kb,
        plans,
        {
            "id": "unrelated",
            "reactants": [
                {"target_id": "ent_substance_nacl", "phase": "aqueous"},
                {"target_id": "ent_substance_naoh", "phase": "aqueous"},
            ],
            "context": {"medium": "aqueous", "temperature_regime": "ambient"},
        },
    )

    for result in (sulfate, unrelated):
        assert result["status"] == "indeterminate"
        assert "candidate_key" not in result


def test_missing_medium_and_acid_strength_remain_unknown(tmp_path: Path) -> None:
    kb = load_knowledge(ROOT)
    missing_medium = infer_case(
        kb,
        compile_rules(kb),
        _case("missing-medium", "ent_substance_hcl", "ent_substance_na2so3", include_medium=False),
    )
    assert missing_medium["status"] == "indeterminate"
    assert "candidate_key" not in missing_medium

    work = tmp_path / "repo"
    shutil.copytree(ROOT, work)
    path = work / "knowledge" / "domain" / "f3b_aqueous_entities.yaml"
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    acid = next(record for record in document["records"] if record.get("id") == "ent_substance_hno3")
    acid["property_assertions"] = [
        assertion for assertion in acid["property_assertions"] if assertion["property_key"] != "acid.strength"
    ]
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    altered = load_knowledge(work)
    missing_strength = infer_case(
        altered,
        compile_rules(altered),
        _case("missing-strength", "ent_substance_hno3", "ent_substance_na2so3"),
    )
    assert missing_strength["status"] == "indeterminate"
    assert "candidate_key" not in missing_strength


def test_missing_sulfite_speciation_is_explicit_and_never_formula_guessed() -> None:
    kb = load_knowledge(ROOT)
    entities = copy.deepcopy(kb.entities)
    entities["ent_substance_na2so3"].pop("speciation_profiles")
    altered = replace(kb, entities=entities)

    result = infer_case(
        altered,
        compile_rules(altered),
        _case("missing-speciation", "ent_substance_hcl", "ent_substance_na2so3"),
    )

    assert result["status"] == "invalid"
    assert result["diagnostic"]["code"] == "speciation_unavailable"
    assert result["diagnostic"]["details"]["target_id"] == "ent_substance_na2so3"
    assert "candidate_key" not in result


@pytest.mark.parametrize(("mode", "candidate_count"), [("unresolved", 0), ("ambiguous", 2)])
def test_sulfite_salt_resolution_never_fabricates_identity(mode: str, candidate_count: int) -> None:
    kb = load_knowledge(ROOT)
    entities = copy.deepcopy(kb.entities)
    if mode == "unresolved":
        entities.pop("ent_substance_nacl")
    else:
        duplicate = copy.deepcopy(entities["ent_substance_nacl"])
        duplicate["id"] = "ent_substance_nacl_duplicate"
        duplicate["semantic_keys"] = []
        entities[duplicate["id"]] = duplicate
    altered = replace(kb, entities=entities)
    result = infer_case(altered, compile_rules(altered), _case(mode, "ent_substance_hcl", "ent_substance_na2so3"))

    assert result["status"] == "invalid"
    assert result["diagnostic"]["code"] == "product_unresolved"
    assert len(result["diagnostic"]["details"]["candidates"]) == candidate_count
    assert "candidate_key" not in result


def test_sulfite_overlap_graph_is_explicit_and_deterministic() -> None:
    first = analyze_rule_overlaps(compile_rules(load_knowledge(ROOT)))
    second = analyze_rule_overlaps(compile_rules(load_knowledge(ROOT)))
    assert first == second
    by_pair = {frozenset(item["rule_ids"]): item for item in first}

    assert by_pair[frozenset({RULE_ID, "rule_f2_strong_acid_base_neutralization"})]["relationships"] == [
        "specializes"
    ]
    for sibling in (
        "rule_m5_strong_acid_hydrogen_carbonate_gas_evolution",
        "rule_m6_strong_acid_carbonate_gas_evolution",
    ):
        assert by_pair[frozenset({RULE_ID, sibling})]["relationships"] == ["mutually_exclusive_with"]
    assert by_pair[frozenset({RULE_ID, "rule_m7_ammonium_strong_base_gas_evolution"})]["relationships"] == [
        "mutually_exclusive_with"
    ]


def test_m7_warmed_condition_and_compatibility_versions_remain_unchanged() -> None:
    kb = load_knowledge(ROOT)
    plans = compile_rules(kb)
    missing_warming = infer_case(
        kb,
        plans,
        {
            "id": "m7-condition-regression",
            "reactants": [
                {"target_id": "ent_substance_nh4cl", "phase": "aqueous"},
                {"target_id": "ent_substance_naoh", "phase": "aqueous"},
            ],
            "context": {"medium": "aqueous"},
        },
    )

    assert missing_warming["status"] == "indeterminate"
    assert "candidate_key" not in missing_warming
    assert artifact_versions() == {
        "source_schema": "3.1.0",
        "rule_dsl": "1.0.0",
        "rule_plan": "1.0.0",
        "artifact_format": "1.1.0",
    }


def test_existing_teaching_view_integrates_sulfite_records() -> None:
    view = load_knowledge(ROOT).teaching_views["view_f3b_hs_aqueous_core"]
    by_path = {node["path_key"]: set(node.get("members", [])) for node in view["nodes"]}
    reaction_ids = {
        "rxn_m8_hcl_na2so3_gas_evolution",
        "rxn_m8_hno3_na2so3_gas_evolution",
        "rxn_m8_hcl_k2so3_gas_evolution",
    }

    assert {"ent_substance_na2so3", "ent_substance_k2so3"} <= by_path[
        "D02/electrolyte-solutions/strong-electrolytes"
    ]
    assert reaction_ids <= by_path["D03/reaction-types/gas-evolution"]
    assert reaction_ids <= by_path["D06/notation/ionic-equations"]
    assert {"ent_substance_na2so3", "ent_substance_k2so3"} <= by_path[
        "D08/substance-classification/salts"
    ]
    assert {"ent_species_so3_2minus", "ent_substance_so2"} <= by_path[
        "D10/elements-and-compounds/sulfur-compounds"
    ]


def test_audit_executes_sulfite_positive_unknown_and_contrast_cases(tmp_path: Path) -> None:
    audit = audit_repository(ROOT, tmp_path / "audit", "m8-fixture")
    results = {result["case_id"]: result for result in audit["results"]}

    for case_id in (
        "case_m8_hcl_na2so3",
        "case_m8_hno3_na2so3",
        "case_m8_hcl_k2so3",
    ):
        assert results[case_id]["status"] == "inferred"
        assert results[case_id]["rule_id"] == RULE_ID
        assert results[case_id]["canonical_match"]["state"] == "exact"
    assert results["case_m8_hcl_na2so3_unknown_medium"]["status"] == "indeterminate"
    assert "candidate_key" not in results["case_m8_hcl_na2so3_unknown_medium"]
    assert "candidate_key" not in results["case_m8_hcl_na2so4_contrast"]
