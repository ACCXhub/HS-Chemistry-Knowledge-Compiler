from __future__ import annotations

import copy
from dataclasses import replace
from pathlib import Path

import pytest

from compiler.build import audit_repository
from compiler.engine import infer_case
from compiler.reaction_forms import derive_aqueous_ionic_form
from compiler.rules import analyze_rule_overlaps, compile_rules
from compiler.source import load_knowledge


ROOT = Path(__file__).resolve().parents[1]
RULE_ID = "rule_m10_active_metal_non_oxidizing_acid_hydrogen"


def _atoms(entity: dict) -> dict[str, int]:
    return {
        component["element_id"]: component["count"]
        for component in entity["payload"]["composition"]["components"]
    }


def _case(
    case_id: str,
    metal_id: str,
    acid_id: str = "ent_substance_hcl",
    *,
    include_medium: bool = True,
) -> dict:
    context = {"temperature_regime": "ambient"}
    if include_medium:
        context["medium"] = "aqueous"
    return {
        "id": case_id,
        "reactants": [
            {"target_id": metal_id, "phase": "solid"},
            {"target_id": acid_id, "phase": "aqueous"},
        ],
        "context": context,
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


def test_metal_elements_and_elemental_substances_are_distinct_without_fake_speciation() -> None:
    kb = load_knowledge(ROOT)
    expected = {
        "zn": (30, "above"),
        "mg": (12, "above"),
        "cu": (29, "below"),
    }

    for symbol, (atomic_number, activity) in expected.items():
        element = kb.entities[f"ent_element_{symbol}"]
        substance = kb.entities[f"ent_substance_elemental_{symbol}"]
        assert element["entity_kind"] == "element"
        assert element["payload"]["atomic_number"] == atomic_number
        assert substance["entity_kind"] == "substance"
        assert substance["payload"]["substance_kind"] == "elemental"
        assert substance["id"] != element["id"]
        assert _atoms(substance) == {element["id"]: 1}
        assert substance["payload"]["composition"]["net_charge"] == 0
        assert "speciation_profiles" not in substance
        assert kb.facet_fact(substance["id"], "classification.metal").value is True
        fact = kb.property_fact(
            substance["id"],
            "metal.activity.relative_to_hydrogen",
            {"medium": "aqueous"},
        )
        assert fact.state.value == "known"
        assert fact.value == activity
        assert fact.evidence_ids == ("ev_m10_metal_hydrogen_activity",)

    assert kb.relation_assertions(
        "ent_substance_elemental_zn", "metal.product_cation", {"medium": "aqueous"}
    )[0]["target_id"] == "ent_species_zn_2plus"
    assert kb.relation_assertions(
        "ent_substance_elemental_mg", "metal.product_cation", {"medium": "aqueous"}
    )[0]["target_id"] == "ent_species_mg_2plus"
    assert kb.relation_assertions(
        "ent_substance_elemental_cu", "metal.product_cation", {"medium": "aqueous"}
    ) == ()


def test_m10_product_ions_hydrogen_and_metal_chlorides_have_exact_canonical_data() -> None:
    kb = load_knowledge(ROOT)

    for symbol in ("zn", "mg"):
        element_id = f"ent_element_{symbol}"
        ion_id = f"ent_species_{symbol}_2plus"
        chloride_id = f"ent_substance_{symbol}cl2"
        ion = kb.entities[ion_id]
        chloride = kb.entities[chloride_id]
        assert ion["entity_kind"] == "species"
        assert ion["payload"]["species_kind"] == "ion"
        assert ion["payload"]["formal_charge"] == 2
        assert ion["payload"]["composition"]["net_charge"] == 2
        assert _atoms(ion) == {element_id: 1}
        assert _atoms(chloride) == {element_id: 1, "ent_element_cl": 2}
        assert chloride["payload"]["composition"]["net_charge"] == 0
        assert kb.property_fact(chloride_id, "electrolyte.strength", {"medium": "aqueous"}).value == "strong"
        assert kb.property_fact(chloride_id, "solubility.class", {"medium": "aqueous"}).value == "soluble"
        assert kb.speciation_profiles(chloride_id, {"medium": "aqueous"})[0]["products"] == [
            {"target_id": ion_id, "coefficient": {"numerator": 1, "denominator": 1}},
            {
                "target_id": "ent_species_cl_minus",
                "coefficient": {"numerator": 2, "denominator": 1},
            },
        ]

    hydrogen = kb.entities["ent_substance_h2"]
    assert hydrogen["entity_kind"] == "substance"
    assert hydrogen["payload"]["substance_kind"] == "elemental"
    assert hydrogen["id"] != "ent_element_h"
    assert _atoms(hydrogen) == {"ent_element_h": 2}
    assert hydrogen["payload"]["composition"]["net_charge"] == 0


def test_m10_rule_is_generic_and_uses_relation_plus_speciation_ion_sources() -> None:
    plan = next(plan for plan in compile_rules(load_knowledge(ROOT)) if plan.rule_id == RULE_ID)
    patterns = {pattern.bind: pattern for pattern in plan.patterns}
    predicates = {(item.binding, item.key, item.expected) for item in plan.predicates}

    assert all(pattern.target_id is None for pattern in plan.patterns)
    assert patterns["metal"].required_facets == ("classification.metal",)
    assert patterns["acid"].required_facets == ("classification.acid",)
    assert ("metal", "metal.activity.relative_to_hydrogen", "above") in predicates
    assert ("acid", "acid.strength", "strong") in predicates
    assert ("acid", "electrolyte.strength", "strong") in predicates
    assert ("acid", "acid.redox_character", "non_oxidizing") in predicates
    salt = plan.products[0]
    assert salt.constructor == "ionic_pair"
    assert salt.cation_source.kind == "relation_target"
    assert salt.cation_source.binding == "metal"
    assert salt.cation_source.relation_key == "metal.product_cation"
    assert salt.anion_source.kind == "speciation"
    assert salt.anion_source.binding == "acid"
    assert [(item.constructor, item.target_id, item.phase) for item in plan.products[1:]] == [
        ("exact_entity", "ent_substance_h2", "gas")
    ]
    assert plan.relations.overrides == ()
    assert plan.relations.specializes == ()
    assert plan.relations.mutually_exclusive_with == ()


@pytest.mark.parametrize(
    ("metal_id", "ion_id", "salt_id", "reaction_id"),
    [
        (
            "ent_substance_elemental_zn",
            "ent_species_zn_2plus",
            "ent_substance_zncl2",
            "rxn_m10_zn_hcl_hydrogen",
        ),
        (
            "ent_substance_elemental_mg",
            "ent_species_mg_2plus",
            "ent_substance_mgcl2",
            "rxn_m10_mg_hcl_hydrogen",
        ),
    ],
)
def test_zinc_and_magnesium_reuse_one_rule_exact_balancer_and_relation_provenance(
    metal_id: str,
    ion_id: str,
    salt_id: str,
    reaction_id: str,
) -> None:
    kb = load_knowledge(ROOT)
    plans = compile_rules(kb)
    case = _case(reaction_id, metal_id)

    first = infer_case(kb, plans, case)
    second = infer_case(kb, plans, case)

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
            ("reactant", "ent_substance_hcl", "aqueous", 2, 1),
            ("product", salt_id, "aqueous", 1, 1),
            ("product", "ent_substance_h2", "gas", 1, 1),
        ]
    )
    assert first["provenance"]["relation_assertions"] == [
        {
            "source_id": metal_id,
            "relation_key": "metal.product_cation",
            "target_id": ion_id,
            "context": {"medium": "aqueous"},
            "evidence_ids": ["ev_m10_metal_hydrogen_activity"],
        }
    ]
    assert {item["target_id"] for item in first["provenance"]["speciation_profiles"]} == {
        "ent_substance_hcl"
    }
    assert "ev_m10_metal_hydrogen_activity" in first["provenance"]["evidence_ids"]
    constructed = next(item for item in first["proof_trace"] if item["event"] == "products.constructed")
    assert constructed["relation_assertions"] == first["provenance"]["relation_assertions"]
    compared = next(item for item in first["proof_trace"] if item["event"] == "canonical.compare")
    assert compared["condition_compatibility"] == [
        {"reaction_id": reaction_id, "state": "compatible", "unsatisfied": []}
    ]


@pytest.mark.parametrize(
    ("metal", "ion", "reaction_id"),
    [
        ("zn", "ent_species_zn_2plus", "rxn_m10_zn_hcl_hydrogen"),
        ("mg", "ent_species_mg_2plus", "rxn_m10_mg_hcl_hydrogen"),
    ],
)
def test_m10_complete_and_net_ionic_forms_preserve_solid_metal_and_hydrogen_gas(
    metal: str,
    ion: str,
    reaction_id: str,
) -> None:
    kb = load_knowledge(ROOT)
    metal_id = f"ent_substance_elemental_{metal}"
    complete = derive_aqueous_ionic_form(kb, reaction_id, "complete_ionic", {"medium": "aqueous"})
    net = derive_aqueous_ionic_form(kb, reaction_id, "net_ionic", {"medium": "aqueous"})

    assert complete["status"] == "derived"
    assert complete["validation"] == {"atoms": True, "charge": True}
    assert _normalized(complete["participants"]) == sorted(
        [
            ("reactant", metal_id, "solid", 1, 1),
            ("reactant", "ent_species_h_plus", "dissolved", 2, 1),
            ("reactant", "ent_species_cl_minus", "dissolved", 2, 1),
            ("product", ion, "dissolved", 1, 1),
            ("product", "ent_species_cl_minus", "dissolved", 2, 1),
            ("product", "ent_substance_h2", "gas", 1, 1),
        ]
    )
    assert net["status"] == "derived"
    assert net["reaction_id"] == reaction_id
    assert net["validation"] == {"atoms": True, "charge": True}
    assert _normalized(net["participants"]) == sorted(
        [
            ("reactant", metal_id, "solid", 1, 1),
            ("reactant", "ent_species_h_plus", "dissolved", 2, 1),
            ("product", ion, "dissolved", 1, 1),
            ("product", "ent_substance_h2", "gas", 1, 1),
        ]
    )
    assert net["derivation"]["operators"] == [
        "expand_approved_aqueous_speciation",
        "cancel_identical_canonical_spectators",
    ]
    assert {item["target_id"] for item in net["derivation"]["speciation_profiles"]} == {
        "ent_substance_hcl",
        f"ent_substance_{metal}cl2",
    }
    assert "ev_m10_metal_hydrogen_activity" in net["derivation"]["evidence_ids"]


def test_copper_known_failure_and_nitric_acid_or_missing_medium_remain_unknown() -> None:
    kb = load_knowledge(ROOT)
    plans = compile_rules(kb)
    copper = infer_case(kb, plans, _case("cu-hcl", "ent_substance_elemental_cu"))
    nitric = infer_case(
        kb,
        plans,
        _case("zn-hno3", "ent_substance_elemental_zn", "ent_substance_hno3"),
    )
    missing_medium = infer_case(
        kb,
        plans,
        _case("zn-hcl-no-medium", "ent_substance_elemental_zn", include_medium=False),
    )

    assert copper["status"] == "indeterminate"
    assert copper["diagnostic"]["code"] == "unknown_applicability"
    assert "candidate_key" not in copper
    activity = [
        item
        for item in copper["proof_trace"]
        if item.get("rule_id") == RULE_ID and item.get("key") == "metal.activity.relative_to_hydrogen"
        and item.get("knowledge_state") == "known"
    ]
    assert len(activity) == 1
    assert activity[0]["truth"] == "FALSE"
    assert activity[0]["knowledge_state"] == "known"

    for result in (nitric, missing_medium):
        assert result["status"] == "indeterminate"
        assert result["diagnostic"]["code"] == "unknown_applicability"
        assert "candidate_key" not in result
    redox = [
        item
        for item in nitric["proof_trace"]
        if item.get("rule_id") == RULE_ID and item.get("key") == "acid.redox_character"
    ]
    assert redox
    assert all(item["truth"] == "UNKNOWN" for item in redox)
    assert all(item["knowledge_state"] == "absent" for item in redox)


def test_missing_activity_and_missing_or_ambiguous_product_cation_stay_explicit() -> None:
    kb = load_knowledge(ROOT)

    entities = copy.deepcopy(kb.entities)
    zinc = entities["ent_substance_elemental_zn"]
    zinc["property_assertions"] = [
        item
        for item in zinc["property_assertions"]
        if item["property_key"] != "metal.activity.relative_to_hydrogen"
    ]
    missing_activity_kb = replace(kb, entities=entities)
    missing_activity = infer_case(
        missing_activity_kb,
        compile_rules(missing_activity_kb),
        _case("missing-activity", "ent_substance_elemental_zn"),
    )
    assert missing_activity["status"] == "indeterminate"
    assert missing_activity["diagnostic"]["code"] == "unknown_applicability"

    entities = copy.deepcopy(kb.entities)
    entities["ent_substance_elemental_zn"].pop("relation_assertions")
    missing_relation_kb = replace(kb, entities=entities)
    missing_relation = infer_case(
        missing_relation_kb,
        compile_rules(missing_relation_kb),
        _case("missing-relation", "ent_substance_elemental_zn"),
    )
    assert missing_relation["status"] == "invalid"
    assert missing_relation["diagnostic"]["code"] == "relation_unavailable"
    assert missing_relation["diagnostic"]["stage"] == "relation_resolution"

    entities = copy.deepcopy(kb.entities)
    entities["ent_substance_elemental_zn"]["relation_assertions"].append(
        {
            "relation_key": "metal.product_cation",
            "target_id": "ent_species_mg_2plus",
            "context": {"temperature_regime": "ambient"},
            "evidence_ids": ["ev_m10_metal_hydrogen_activity"],
        }
    )
    ambiguous_relation_kb = replace(kb, entities=entities)
    ambiguous = infer_case(
        ambiguous_relation_kb,
        compile_rules(ambiguous_relation_kb),
        _case("ambiguous-relation", "ent_substance_elemental_zn"),
    )
    assert ambiguous["status"] == "invalid"
    assert ambiguous["diagnostic"]["code"] == "relation_ambiguous"
    assert ambiguous["diagnostic"]["details"]["candidates"] == [
        "ent_species_mg_2plus",
        "ent_species_zn_2plus",
    ]


@pytest.mark.parametrize(("mode", "candidate_count"), [("unresolved", 0), ("ambiguous", 2)])
def test_metal_chloride_resolution_never_fabricates_identity(mode: str, candidate_count: int) -> None:
    kb = load_knowledge(ROOT)
    entities = copy.deepcopy(kb.entities)
    if mode == "unresolved":
        entities.pop("ent_substance_zncl2")
    else:
        duplicate = copy.deepcopy(entities["ent_substance_zncl2"])
        duplicate["id"] = "ent_substance_zncl2_duplicate"
        duplicate["semantic_keys"] = []
        entities[duplicate["id"]] = duplicate
    altered = replace(kb, entities=entities)

    result = infer_case(
        altered,
        compile_rules(altered),
        _case(mode, "ent_substance_elemental_zn"),
    )

    assert result["status"] == "invalid"
    assert result["diagnostic"]["code"] == "product_unresolved"
    assert len(result["diagnostic"]["details"]["candidates"]) == candidate_count
    assert "candidate_key" not in result


def test_m10_rule_is_structurally_disjoint_and_overlap_output_is_deterministic() -> None:
    plans = compile_rules(load_knowledge(ROOT))
    assert RULE_ID in {plan.rule_id for plan in plans}
    first = analyze_rule_overlaps(plans)
    second = analyze_rule_overlaps(compile_rules(load_knowledge(ROOT)))

    assert first == second
    assert not any(RULE_ID in item["rule_ids"] for item in first)


def test_relation_provenance_is_emitted_only_when_product_resolution_uses_it() -> None:
    kb = load_knowledge(ROOT)
    plans = compile_rules(kb)
    legacy = infer_case(
        kb,
        plans,
        {
            "id": "legacy-hydrogen-carbonate",
            "reactants": [
                {"target_id": "ent_substance_hcl", "phase": "aqueous"},
                {"target_id": "ent_substance_nahco3", "phase": "aqueous"},
            ],
            "context": {"medium": "aqueous", "temperature_regime": "ambient"},
        },
    )

    assert legacy["status"] == "inferred"
    assert "relation_assertions" not in legacy["provenance"]
    constructed = next(item for item in legacy["proof_trace"] if item["event"] == "products.constructed")
    assert "relation_assertions" not in constructed


def test_existing_teaching_view_integrates_m10_records() -> None:
    view = load_knowledge(ROOT).teaching_views["view_f3b_hs_aqueous_core"]
    by_path = {node["path_key"]: set(node.get("members", [])) for node in view["nodes"]}
    reactions = {"rxn_m10_zn_hcl_hydrogen", "rxn_m10_mg_hcl_hydrogen"}

    assert {"ent_substance_zncl2", "ent_substance_mgcl2"} <= by_path[
        "D02/electrolyte-solutions/strong-electrolytes"
    ]
    assert reactions <= by_path["D03/reaction-types/single-displacement"]
    assert reactions <= by_path["D06/notation/ionic-equations"]
    assert {"ent_substance_zncl2", "ent_substance_mgcl2"} <= by_path[
        "D08/substance-classification/salts"
    ]
    assert {
        "ent_substance_elemental_zn",
        "ent_substance_elemental_mg",
        "ent_substance_elemental_cu",
    } <= by_path["D08/substance-classification/metals"]
    assert {"ent_element_zn", "ent_element_mg", "ent_element_cu"} <= by_path[
        "D10/elements-and-compounds/representative-elements"
    ]


def test_audit_executes_m10_positive_negative_and_unknown_cases(tmp_path: Path) -> None:
    audit = audit_repository(ROOT, tmp_path / "audit", "m10-fixture")
    results = {result["case_id"]: result for result in audit["results"]}

    for case_id in ("case_m10_zn_hcl", "case_m10_mg_hcl"):
        assert results[case_id]["status"] == "inferred"
        assert results[case_id]["rule_id"] == RULE_ID
        assert results[case_id]["canonical_match"]["state"] == "exact"
    assert results["case_m10_cu_hcl"]["status"] == "indeterminate"
    assert "candidate_key" not in results["case_m10_cu_hcl"]
    assert results["case_m10_zn_hno3_unknown_redox"]["status"] == "indeterminate"
    assert results["case_m10_zn_hcl_unknown_medium"]["status"] == "indeterminate"
