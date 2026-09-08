from __future__ import annotations

import copy
import shutil
from dataclasses import replace
from pathlib import Path

import pytest
import yaml

from compiler.build import audit_repository
from compiler.engine import infer_case
from compiler.reaction_forms import derive_aqueous_ionic_form
from compiler.rules import analyze_rule_overlaps, compile_rules
from compiler.source import load_knowledge


ROOT = Path(__file__).resolve().parents[1]
RULE_ID = "rule_m6_strong_acid_carbonate_gas_evolution"


def _atoms(entity: dict) -> dict[str, int]:
    return {
        component["element_id"]: component["count"]
        for component in entity["payload"]["composition"]["components"]
    }


def _case(case_id: str, acid_id: str, carbonate_id: str, *, include_medium: bool = True) -> dict:
    context = {"temperature_regime": "ambient"}
    if include_medium:
        context["medium"] = "aqueous"
    return {
        "id": case_id,
        "reactants": [
            {"target_id": acid_id, "phase": "aqueous"},
            {"target_id": carbonate_id, "phase": "aqueous"},
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


def test_carbonate_ion_has_canonical_divalent_charge_and_composition() -> None:
    carbonate = load_knowledge(ROOT).entities["ent_species_co3_2minus"]

    assert carbonate["entity_kind"] == "species"
    assert carbonate["payload"]["species_kind"] == "ion"
    assert carbonate["payload"]["formal_charge"] == -2
    assert carbonate["payload"]["composition"]["net_charge"] == -2
    assert _atoms(carbonate) == {"ent_element_c": 1, "ent_element_o": 3}


@pytest.mark.parametrize(
    ("substance_id", "cation_id", "element_id"),
    [
        ("ent_substance_na2co3", "ent_species_na_plus", "ent_element_na"),
        ("ent_substance_k2co3", "ent_species_k_plus", "ent_element_k"),
    ],
)
def test_soluble_carbonate_salts_have_exact_composition_and_speciation(
    substance_id: str,
    cation_id: str,
    element_id: str,
) -> None:
    kb = load_knowledge(ROOT)
    carbonate = kb.entities[substance_id]

    assert _atoms(carbonate) == {element_id: 2, "ent_element_c": 1, "ent_element_o": 3}
    assert carbonate["payload"]["composition"]["net_charge"] == 0
    assert kb.facet_fact(substance_id, "classification.salt").value is True
    assert kb.facet_fact(substance_id, "classification.carbonate").value is True
    assert kb.property_fact(substance_id, "electrolyte.strength", {"medium": "aqueous"}).value == "strong"
    assert kb.property_fact(substance_id, "solubility.class", {"medium": "aqueous"}).value == "soluble"

    profiles = kb.speciation_profiles(substance_id, {"medium": "aqueous"})
    assert len(profiles) == 1
    assert profiles[0]["model"] == "strong_electrolyte_complete_dissociation"
    assert profiles[0]["products"] == [
        {"target_id": cation_id, "coefficient": {"numerator": 2, "denominator": 1}},
        {
            "target_id": "ent_species_co3_2minus",
            "coefficient": {"numerator": 1, "denominator": 1},
        },
    ]
    assert profiles[0]["evidence_ids"] == ["ev_f3b_carbonate_acid"]


@pytest.mark.parametrize(
    ("acid_id", "carbonate_id", "salt_id", "reaction_id"),
    [
        (
            "ent_substance_hcl",
            "ent_substance_na2co3",
            "ent_substance_nacl",
            "rxn_m6_hcl_na2co3_gas_evolution",
        ),
        (
            "ent_substance_hno3",
            "ent_substance_na2co3",
            "ent_substance_nano3",
            "rxn_m6_hno3_na2co3_gas_evolution",
        ),
        (
            "ent_substance_hcl",
            "ent_substance_k2co3",
            "ent_substance_kcl",
            "rxn_m6_hcl_k2co3_gas_evolution",
        ),
    ],
)
def test_acid_and_cation_substitutions_reuse_one_carbonate_rule(
    acid_id: str,
    carbonate_id: str,
    salt_id: str,
    reaction_id: str,
) -> None:
    kb = load_knowledge(ROOT)
    result = infer_case(kb, compile_rules(kb), _case(reaction_id, acid_id, carbonate_id))

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
            ("reactant", carbonate_id, 1, 1),
            ("product", salt_id, 2, 1),
            ("product", "ent_substance_co2", 1, 1),
            ("product", "ent_substance_h2o", 1, 1),
        ]
    )
    profiles = result["provenance"]["speciation_profiles"]
    assert {item["target_id"] for item in profiles} == {acid_id, carbonate_id}
    assert all(item["profile_key"] == "aqueous_complete_dissociation" for item in profiles)
    assert all(item["model"] == "strong_electrolyte_complete_dissociation" for item in profiles)
    assert all(item["evidence_ids"] for item in profiles)


def test_carbonate_rule_is_generic_and_uses_existing_ionic_pair_constructor() -> None:
    plan = next(plan for plan in compile_rules(load_knowledge(ROOT)) if plan.rule_id == RULE_ID)

    assert all(pattern.target_id is None for pattern in plan.patterns)
    assert plan.patterns[1].required_facets == ("classification.carbonate", "classification.salt")
    assert plan.products[0].constructor == "ionic_pair"
    assert plan.products[0].cation_from == "carbonate"
    assert plan.products[0].anion_from == "acid"


def test_all_carbonate_examples_derive_one_conserved_net_ionic_chemistry() -> None:
    kb = load_knowledge(ROOT)
    expected = sorted(
        [
            ("reactant", "ent_species_h_plus", 2, 1),
            ("reactant", "ent_species_co3_2minus", 1, 1),
            ("product", "ent_substance_co2", 1, 1),
            ("product", "ent_substance_h2o", 1, 1),
        ]
    )
    for reaction_id in (
        "rxn_m6_hcl_na2co3_gas_evolution",
        "rxn_m6_hno3_na2co3_gas_evolution",
        "rxn_m6_hcl_k2co3_gas_evolution",
    ):
        complete = derive_aqueous_ionic_form(kb, reaction_id, "complete_ionic", {"medium": "aqueous"})
        net = derive_aqueous_ionic_form(kb, reaction_id, "net_ionic", {"medium": "aqueous"})
        golden = next(form for form in kb.reactions[reaction_id]["forms"] if form["form_kind"] == "net_ionic")

        assert complete["status"] == "derived"
        assert complete["validation"] == {"atoms": True, "charge": True}
        assert complete["derivation"]["operators"] == ["expand_approved_aqueous_speciation"]
        assert net["status"] == "derived"
        assert net["reaction_id"] == reaction_id
        assert net["derivation"]["source_reaction_id"] == reaction_id
        assert net["derivation"]["operators"] == [
            "expand_approved_aqueous_speciation",
            "cancel_identical_canonical_spectators",
        ]
        assert net["validation"] == {"atoms": True, "charge": True}
        assert _normalized(net["participants"]) == expected
        assert _normalized(net["participants"]) == _normalized(golden["participants"])
        assert net["derivation"]["speciation_profiles"]
        assert net["derivation"]["evidence_ids"]
        assert net["derivation"]["kind"] == "derived_reaction_form"
        assert reaction_id not in {form.get("id") for form in kb.reactions[reaction_id]["forms"]}


def test_missing_aqueous_context_keeps_carbonate_applicability_unknown() -> None:
    kb = load_knowledge(ROOT)
    result = infer_case(
        kb,
        compile_rules(kb),
        _case("missing-medium", "ent_substance_hcl", "ent_substance_na2co3", include_medium=False),
    )

    assert result["status"] == "indeterminate"
    assert result["diagnostic"]["code"] == "unknown_applicability"
    assert "candidate_key" not in result
    assert any(
        event["event"] == "predicate.eval"
        and event["rule_id"] == RULE_ID
        and event["subject"] == "context"
        and event["key"] == "medium"
        and event["truth"] == "UNKNOWN"
        for event in result["proof_trace"]
    )


def test_missing_acid_strength_keeps_carbonate_applicability_unknown(tmp_path: Path) -> None:
    work = tmp_path / "repo"
    shutil.copytree(ROOT, work)
    path = work / "knowledge" / "domain" / "f3b_aqueous_entities.yaml"
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    acid = next(record for record in document["records"] if record.get("id") == "ent_substance_hno3")
    acid["property_assertions"] = [
        assertion for assertion in acid["property_assertions"] if assertion["property_key"] != "acid.strength"
    ]
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")

    kb = load_knowledge(work)
    result = infer_case(
        kb,
        compile_rules(kb),
        _case("unknown-acid-strength", "ent_substance_hno3", "ent_substance_na2co3"),
    )

    assert result["status"] == "indeterminate"
    assert "candidate_key" not in result
    assert any(
        event["event"] == "predicate.eval"
        and event["rule_id"] == RULE_ID
        and event["binding"] == "acid"
        and event["key"] == "acid.strength"
        and event["truth"] == "UNKNOWN"
        for event in result["proof_trace"]
    )


def test_missing_carbonate_speciation_is_explicit_and_never_formula_guessed() -> None:
    kb = load_knowledge(ROOT)
    entities = copy.deepcopy(kb.entities)
    entities["ent_substance_na2co3"].pop("speciation_profiles")
    kb_without_profile = replace(kb, entities=entities)

    result = infer_case(
        kb_without_profile,
        compile_rules(kb_without_profile),
        _case("missing-speciation", "ent_substance_hcl", "ent_substance_na2co3"),
    )

    assert result["status"] == "invalid"
    assert result["diagnostic"]["code"] == "speciation_unavailable"
    assert result["diagnostic"]["details"]["target_id"] == "ent_substance_na2co3"
    assert "candidate_key" not in result


@pytest.mark.parametrize(("mode", "candidate_count"), [("unresolved", 0), ("ambiguous", 2)])
def test_non_fabricating_salt_resolution_is_explicit(mode: str, candidate_count: int) -> None:
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

    result = infer_case(
        altered,
        compile_rules(altered),
        _case(mode, "ent_substance_hcl", "ent_substance_na2co3"),
    )

    assert result["status"] == "invalid"
    assert result["diagnostic"]["code"] == "product_unresolved"
    assert len(result["diagnostic"]["details"]["candidates"]) == candidate_count
    assert "candidate_key" not in result


def test_carbonate_overlap_relationships_are_explicit_and_deterministic() -> None:
    overlaps = analyze_rule_overlaps(compile_rules(load_knowledge(ROOT)))
    by_pair = {frozenset(item["rule_ids"]): item for item in overlaps}

    assert by_pair[
        frozenset({RULE_ID, "rule_f2_strong_acid_base_neutralization"})
    ]["relationships"] == ["specializes"]
    assert by_pair[
        frozenset({RULE_ID, "rule_m5_strong_acid_hydrogen_carbonate_gas_evolution"})
    ]["relationships"] == ["mutually_exclusive_with"]
    assert frozenset({RULE_ID, "rule_f2_agcl_precipitation"}) not in by_pair


def test_existing_teaching_view_integrates_carbonate_entities_and_reactions() -> None:
    view = load_knowledge(ROOT).teaching_views["view_f3b_hs_aqueous_core"]
    by_path = {node["path_key"]: set(node.get("members", [])) for node in view["nodes"]}
    reaction_ids = {
        "rxn_m6_hcl_na2co3_gas_evolution",
        "rxn_m6_hno3_na2co3_gas_evolution",
        "rxn_m6_hcl_k2co3_gas_evolution",
    }

    assert {"ent_substance_na2co3", "ent_substance_k2co3"} <= by_path[
        "D02/electrolyte-solutions/strong-electrolytes"
    ]
    assert reaction_ids <= by_path["D03/reaction-types/gas-evolution"]
    assert reaction_ids <= by_path["D06/notation/ionic-equations"]
    assert {"ent_substance_na2co3", "ent_substance_k2co3"} <= by_path[
        "D08/substance-classification/salts"
    ]


def test_audit_executes_carbonate_positive_and_unknown_cases(tmp_path: Path) -> None:
    audit = audit_repository(ROOT, tmp_path / "audit", "m6-fixture")
    results = {result["case_id"]: result for result in audit["results"]}

    for case_id in (
        "case_m6_hcl_na2co3",
        "case_m6_hno3_na2co3",
        "case_m6_hcl_k2co3",
    ):
        assert results[case_id]["status"] == "inferred"
        assert results[case_id]["rule_id"] == RULE_ID
    assert results["case_m6_hcl_na2co3_unknown_medium"]["status"] == "indeterminate"
