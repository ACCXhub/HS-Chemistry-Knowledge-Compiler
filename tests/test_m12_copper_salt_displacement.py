from __future__ import annotations

import copy
from dataclasses import replace
from pathlib import Path

import pytest

from compiler.build import audit_repository
from compiler.engine import infer_case
from compiler.model import KnowledgeState
from compiler.reaction_forms import derive_aqueous_ionic_form
from compiler.rules import analyze_rule_overlaps, compile_rules
from compiler.source import load_knowledge


ROOT = Path(__file__).resolve().parents[1]
RULE_ID = "rule_m19_generic_aqueous_metal_salt_displacement"


def _atoms(entity: dict) -> dict[str, int]:
    return {
        component["element_id"]: component["count"]
        for component in entity["payload"]["composition"]["components"]
    }


def _case(case_id: str, metal_id: str, salt_id: str = "ent_substance_cuso4") -> dict:
    return {
        "id": case_id,
        "reactants": [
            {"target_id": metal_id, "phase": "solid"},
            {"target_id": salt_id, "phase": "aqueous"},
        ],
        "context": {"medium": "aqueous", "temperature_regime": "ambient"},
    }


def _normalized(participants: list[dict]) -> list[tuple[str, str, str, int, int]]:
    return sorted(
        (
            item["role"],
            item["target_id"],
            item["phase"],
            item["coefficient"]["numerator"],
            item["coefficient"]["denominator"],
        )
        for item in participants
    )


def test_m12_copper_ion_and_sulfate_salts_are_exact_canonical_data() -> None:
    kb = load_knowledge(ROOT)
    copper_ion = kb.entities["ent_species_cu_2plus"]
    assert copper_ion["entity_kind"] == "species"
    assert copper_ion["payload"]["species_kind"] == "ion"
    assert copper_ion["payload"]["formal_charge"] == 2
    assert copper_ion["payload"]["composition"]["net_charge"] == 2
    assert _atoms(copper_ion) == {"ent_element_cu": 1}

    expected = {
        "ent_substance_cuso4": ("ent_element_cu", "ent_species_cu_2plus"),
        "ent_substance_znso4": ("ent_element_zn", "ent_species_zn_2plus"),
        "ent_substance_mgso4": ("ent_element_mg", "ent_species_mg_2plus"),
    }
    for substance_id, (metal_element_id, cation_id) in expected.items():
        substance = kb.entities[substance_id]
        assert substance["entity_kind"] == "substance"
        assert substance["payload"]["substance_kind"] == "pure_compound"
        assert _atoms(substance) == {
            metal_element_id: 1,
            "ent_element_s": 1,
            "ent_element_o": 4,
        }
        assert substance["payload"]["composition"]["net_charge"] == 0
        assert kb.facet_fact(substance_id, "classification.salt").value is True
        assert kb.facet_fact(substance_id, "classification.sulfate").value is True
        assert kb.property_fact(substance_id, "solubility.class", {"medium": "aqueous"}).value == "soluble"
        assert kb.property_fact(substance_id, "electrolyte.strength", {"medium": "aqueous"}).value == "strong"
        assert kb.speciation_profiles(substance_id, {"medium": "aqueous"})[0]["products"] == [
            {"target_id": cation_id, "coefficient": {"numerator": 1, "denominator": 1}},
            {
                "target_id": "ent_species_so4_2minus",
                "coefficient": {"numerator": 1, "denominator": 1},
            },
        ]


def test_zinc_and_magnesium_own_evidence_backed_aqueous_displacement_relations() -> None:
    kb = load_knowledge(ROOT)
    for metal in ("zn", "mg"):
        metal_id = f"ent_substance_elemental_{metal}"
        assert "speciation_profiles" not in kb.entities[metal_id]
        assert kb.relation_assertions(
            metal_id,
            "metal.displaces_cation",
            {"medium": "aqueous", "temperature_regime": "ambient"},
        ) == (
            {
                "source_id": metal_id,
                "relation_key": "metal.displaces_cation",
                "target_id": "ent_species_ag_plus",
                "context": {"medium": "aqueous"},
                "evidence_ids": ["ev_m13_metal_silver_displacement"],
            },
            {
                "source_id": metal_id,
                "relation_key": "metal.displaces_cation",
                "target_id": "ent_species_cu_2plus",
                "context": {"medium": "aqueous"},
                "evidence_ids": ["ev_m12_metal_copper_displacement"],
            },
        )


def test_m12_regression_uses_generic_salt_rule_and_existing_constructors() -> None:
    plan = next(plan for plan in compile_rules(load_knowledge(ROOT)) if plan.rule_id == RULE_ID)
    patterns = {pattern.bind: pattern for pattern in plan.patterns}
    relation = next(predicate for predicate in plan.predicates if predicate.subject == "relation")

    assert patterns["metal"].target_id is None
    assert patterns["metal"].entity_kind == "substance"
    assert patterns["metal"].phase == "solid"
    assert patterns["metal"].required_facets == ("classification.metal",)
    assert patterns["salt"].target_id is None
    assert patterns["salt"].phase == "aqueous"
    assert patterns["salt"].required_facets == ("classification.salt",)
    assert relation.binding == "metal"
    assert relation.key == "metal.displaces_cation"
    assert relation.target_id is None
    assert relation.target_source.kind == "speciation_ion"
    assert relation.target_source.binding == "salt"
    assert relation.target_source.charge_sign == "positive"
    assert relation.operator == "equals"
    assert relation.expected is True

    sulfate = plan.products[0]
    assert sulfate.constructor == "ionic_pair"
    assert sulfate.phase == "aqueous"
    assert sulfate.cation_source.kind == "relation_target"
    assert sulfate.cation_source.binding == "metal"
    assert sulfate.cation_source.relation_key == "metal.product_cation"
    assert sulfate.anion_source.kind == "speciation"
    assert sulfate.anion_source.binding == "salt"
    displaced = plan.products[1]
    assert displaced.constructor == "entity_source"
    assert displaced.entity_source.kind == "relation_target"
    assert displaced.entity_source.relation_key == "ion.elemental_substance"
    assert displaced.entity_source.source.kind == "speciation_ion"
    assert displaced.entity_source.source.binding == "salt"
    assert displaced.phase == "solid"
    assert plan.decision_domain == "aqueous_metal_salt_displacement"
    assert plan.relations.overrides == ()
    assert plan.relations.specializes == ()
    assert plan.relations.mutually_exclusive_with == ()


@pytest.mark.parametrize(
    ("metal", "cation_id", "sulfate_id", "reaction_id"),
    [
        ("zn", "ent_species_zn_2plus", "ent_substance_znso4", "rxn_m12_zn_cuso4_displacement"),
        ("mg", "ent_species_mg_2plus", "ent_substance_mgso4", "rxn_m12_mg_cuso4_displacement"),
    ],
)
def test_zinc_and_magnesium_use_one_rule_exact_balancing_and_auditable_relations(
    metal: str,
    cation_id: str,
    sulfate_id: str,
    reaction_id: str,
) -> None:
    kb = load_knowledge(ROOT)
    metal_id = f"ent_substance_elemental_{metal}"
    first = infer_case(kb, compile_rules(kb), _case(reaction_id, metal_id))
    second = infer_case(kb, compile_rules(kb), _case(reaction_id, metal_id))

    assert first == second
    assert first["status"] == "inferred"
    assert first["rule_id"] == RULE_ID
    assert first["canonical_match"] == {
        "state": "exact",
        "reaction_ids": [reaction_id],
        "reaction_forms": {reaction_id: ["molecular", "complete_ionic", "net_ionic"]},
    }
    assert first["validation"] == {"atoms": True, "charge": True}
    assert _normalized(first["participants"]) == sorted(
        [
            ("reactant", metal_id, "solid", 1, 1),
            ("reactant", "ent_substance_cuso4", "aqueous", 1, 1),
            ("product", sulfate_id, "aqueous", 1, 1),
            ("product", "ent_substance_elemental_cu", "solid", 1, 1),
        ]
    )
    assert first["provenance"]["relation_assertions"] == [
        {
            "source_id": "ent_species_cu_2plus",
            "relation_key": "ion.elemental_substance",
            "target_id": "ent_substance_elemental_cu",
            "context": {},
            "evidence_ids": ["ev_m12_metal_copper_displacement"],
        },
        {
            "source_id": metal_id,
            "relation_key": "metal.displaces_cation",
            "target_id": "ent_species_cu_2plus",
            "context": {"medium": "aqueous"},
            "evidence_ids": ["ev_m12_metal_copper_displacement"],
        },
        {
            "source_id": metal_id,
            "relation_key": "metal.product_cation",
            "target_id": cation_id,
            "context": {"medium": "aqueous"},
            "evidence_ids": ["ev_m10_metal_hydrogen_activity"],
        },
    ]
    assert {item["target_id"] for item in first["provenance"]["speciation_profiles"]} == {
        "ent_substance_cuso4"
    }
    relation_event = next(
        item
        for item in first["proof_trace"]
        if item.get("event") == "predicate.eval" and item.get("subject") == "relation"
    )
    assert relation_event["target_id"] == "ent_species_cu_2plus"
    assert relation_event["truth"] == "TRUE"
    assert relation_event["relation_assertions"] == first["provenance"]["relation_assertions"][1:2]


@pytest.mark.parametrize(
    ("metal", "cation_id", "sulfate_id", "reaction_id"),
    [
        ("zn", "ent_species_zn_2plus", "ent_substance_znso4", "rxn_m12_zn_cuso4_displacement"),
        ("mg", "ent_species_mg_2plus", "ent_substance_mgso4", "rxn_m12_mg_cuso4_displacement"),
    ],
)
def test_m12_complete_and_net_ionic_forms_cancel_only_sulfate(
    metal: str,
    cation_id: str,
    sulfate_id: str,
    reaction_id: str,
) -> None:
    kb = load_knowledge(ROOT)
    metal_id = f"ent_substance_elemental_{metal}"
    context = {"medium": "aqueous", "temperature_regime": "ambient"}
    complete = derive_aqueous_ionic_form(kb, reaction_id, "complete_ionic", context)
    net = derive_aqueous_ionic_form(kb, reaction_id, "net_ionic", context)

    assert complete["status"] == "derived"
    assert complete["validation"] == {"atoms": True, "charge": True}
    assert _normalized(complete["participants"]) == sorted(
        [
            ("reactant", metal_id, "solid", 1, 1),
            ("reactant", "ent_species_cu_2plus", "dissolved", 1, 1),
            ("reactant", "ent_species_so4_2minus", "dissolved", 1, 1),
            ("product", cation_id, "dissolved", 1, 1),
            ("product", "ent_species_so4_2minus", "dissolved", 1, 1),
            ("product", "ent_substance_elemental_cu", "solid", 1, 1),
        ]
    )
    assert {item["target_id"] for item in complete["derivation"]["speciation_profiles"]} == {
        "ent_substance_cuso4",
        sulfate_id,
    }
    assert net["status"] == "derived"
    assert net["validation"] == {"atoms": True, "charge": True}
    assert _normalized(net["participants"]) == sorted(
        [
            ("reactant", metal_id, "solid", 1, 1),
            ("reactant", "ent_species_cu_2plus", "dissolved", 1, 1),
            ("product", cation_id, "dissolved", 1, 1),
            ("product", "ent_substance_elemental_cu", "solid", 1, 1),
        ]
    )


@pytest.mark.parametrize("metal", ["cu", "na", "k"])
def test_absent_displacement_relation_does_not_infer_cuso4_path(metal: str) -> None:
    kb = load_knowledge(ROOT)
    metal_id = f"ent_substance_elemental_{metal}"
    result = infer_case(kb, compile_rules(kb), _case(f"{metal}-cuso4", metal_id))

    assert result["status"] == "indeterminate"
    assert result["diagnostic"]["code"] == "unknown_applicability"
    assert result.get("rule_id") != RULE_ID
    assert "candidate_key" not in result
    relation_event = next(
        item
        for item in result["proof_trace"]
        if item.get("rule_id") == RULE_ID and item.get("subject") == "relation"
    )
    assert relation_event["truth"] == "UNKNOWN"
    assert relation_event["knowledge_state"] == "absent"


def test_copper_with_zinc_sulfate_does_not_trigger_generic_reverse_path() -> None:
    kb = load_knowledge(ROOT)
    result = infer_case(
        kb,
        compile_rules(kb),
        _case("cu-znso4", "ent_substance_elemental_cu", "ent_substance_znso4"),
    )

    assert result["status"] == "no_match"
    assert result.get("rule_id") != RULE_ID
    assert "candidate_key" not in result
    relation_event = next(
        item
        for item in result["proof_trace"]
        if item.get("rule_id") == RULE_ID and item.get("subject") == "relation"
    )
    assert relation_event["target_id"] == "ent_species_zn_2plus"
    assert relation_event["truth"] == "FALSE"
    assert relation_event["knowledge_state"] == "known"
    assert relation_event["relation_assertions"][0]["truth"] is False


def test_missing_product_sulfate_is_explicit_and_never_fabricated() -> None:
    kb = load_knowledge(ROOT)
    entities = copy.deepcopy(kb.entities)
    entities.pop("ent_substance_znso4")
    altered = replace(kb, entities=entities)
    result = infer_case(
        altered,
        compile_rules(altered),
        _case("missing-zinc-sulfate", "ent_substance_elemental_zn"),
    )

    assert result["status"] == "invalid"
    assert result["diagnostic"]["code"] == "product_unresolved"
    assert result["diagnostic"]["details"]["candidates"] == []
    assert "candidate_key" not in result


def test_m12_overlap_teaching_and_audit_integration_are_deterministic(tmp_path: Path) -> None:
    kb = load_knowledge(ROOT)
    plans = compile_rules(kb)
    first = analyze_rule_overlaps(plans)
    second = analyze_rule_overlaps(compile_rules(load_knowledge(ROOT)))
    assert first == second
    assert not any(RULE_ID in item["rule_ids"] for item in first)

    view = kb.teaching_views["view_f3b_hs_aqueous_core"]
    by_path = {node["path_key"]: set(node.get("members", [])) for node in view["nodes"]}
    reactions = {"rxn_m12_zn_cuso4_displacement", "rxn_m12_mg_cuso4_displacement"}
    assert reactions <= by_path["D03/reaction-types/single-displacement"]
    assert reactions <= by_path["D06/notation/ionic-equations"]
    assert {"ent_substance_cuso4", "ent_substance_znso4", "ent_substance_mgso4"} <= by_path[
        "D08/substance-classification/salts"
    ]
    assert "ent_species_cu_2plus" in by_path["D10/elements-and-compounds/representative-elements"]

    audit = audit_repository(ROOT, tmp_path / "audit", "m12-fixture")
    results = {result["case_id"]: result for result in audit["results"]}
    for case_id in ("case_m12_zn_cuso4", "case_m12_mg_cuso4"):
        assert results[case_id]["status"] == "inferred"
        assert results[case_id]["rule_id"] == RULE_ID
        assert results[case_id]["canonical_match"]["state"] == "exact"
    for case_id in ("case_m12_cu_cuso4", "case_m12_na_cuso4", "case_m12_k_cuso4"):
        assert results[case_id]["status"] == "indeterminate"
        assert "candidate_key" not in results[case_id]
    assert "candidate_key" not in results["case_m12_cu_znso4"]
