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
RULE_ID = "rule_m11_water_reactive_metal_hydrogen"


def _case(
    case_id: str,
    metal_id: str,
    *,
    water_phase: str = "liquid",
    include_temperature: bool = True,
) -> dict:
    context = {"medium": "aqueous"}
    if include_temperature:
        context["temperature_regime"] = "ambient"
    return {
        "id": case_id,
        "reactants": [
            {"target_id": metal_id, "phase": "solid"},
            {"target_id": "ent_substance_h2o", "phase": water_phase},
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


def test_na_and_k_elemental_substances_are_distinct_contextual_and_relation_backed() -> None:
    kb = load_knowledge(ROOT)
    expected = {
        "na": ("ent_species_na_plus", 11),
        "k": ("ent_species_k_plus", 19),
    }

    for symbol, (ion_id, atomic_number) in expected.items():
        element = kb.entities[f"ent_element_{symbol}"]
        metal = kb.entities[f"ent_substance_elemental_{symbol}"]
        assert element["entity_kind"] == "element"
        assert element["payload"]["atomic_number"] == atomic_number
        assert metal["entity_kind"] == "substance"
        assert metal["payload"]["substance_kind"] == "elemental"
        assert metal["id"] != element["id"]
        assert metal["payload"]["composition"] == {
            "components": [{"element_id": element["id"], "count": 1}],
            "net_charge": 0,
        }
        assert "speciation_profiles" not in metal
        assert kb.facet_fact(metal["id"], "classification.metal").value is True

        reactivity = kb.property_fact(
            metal["id"],
            "metal.water_reactivity",
            {"medium": "aqueous", "temperature_regime": "ambient"},
        )
        assert reactivity.state is KnowledgeState.KNOWN
        assert reactivity.value == "reacts"
        assert reactivity.context == (("temperature_regime", "ambient"),)
        assert reactivity.evidence_ids == ("ev_m11_alkali_metal_water_reactivity",)

        relations = kb.relation_assertions(
            metal["id"],
            "metal.product_cation",
            {"medium": "aqueous", "temperature_regime": "ambient"},
        )
        assert relations == (
            {
                "source_id": metal["id"],
                "relation_key": "metal.product_cation",
                "target_id": ion_id,
                "context": {},
                "evidence_ids": ["ev_m11_alkali_metal_identity_and_cations"],
            },
        )


def test_m11_rule_is_generic_phase_bounded_and_uses_relation_plus_exact_ion() -> None:
    plan = next(plan for plan in compile_rules(load_knowledge(ROOT)) if plan.rule_id == RULE_ID)
    patterns = {pattern.bind: pattern for pattern in plan.patterns}
    predicates = {(item.subject, item.binding, item.key, item.expected) for item in plan.predicates}

    assert patterns["metal"].target_id is None
    assert patterns["metal"].entity_kind == "substance"
    assert patterns["metal"].phase == "solid"
    assert patterns["metal"].required_facets == ("classification.metal",)
    assert patterns["water"].target_id == "ent_substance_h2o"
    assert patterns["water"].phase == "liquid"
    assert ("context", None, "temperature_regime", "ambient") in predicates
    assert ("property", "metal", "metal.water_reactivity", "reacts") in predicates

    hydroxide = plan.products[0]
    assert hydroxide.constructor == "ionic_pair"
    assert hydroxide.phase == "aqueous"
    assert hydroxide.cation_source.kind == "relation_target"
    assert hydroxide.cation_source.binding == "metal"
    assert hydroxide.cation_source.relation_key == "metal.product_cation"
    assert hydroxide.anion_source.kind == "exact_entity"
    assert hydroxide.anion_source.binding is None
    assert hydroxide.anion_source.target_id == "ent_species_oh_minus"
    assert [(item.constructor, item.target_id, item.phase) for item in plan.products[1:]] == [
        ("exact_entity", "ent_substance_h2", "gas")
    ]
    assert plan.decision_domain == "metal_liquid_water_hydrogen"
    assert plan.relations.overrides == ()
    assert plan.relations.specializes == ()
    assert plan.relations.mutually_exclusive_with == ()


@pytest.mark.parametrize(
    ("symbol", "ion_id", "hydroxide_id", "reaction_id"),
    [
        ("na", "ent_species_na_plus", "ent_substance_naoh", "rxn_m11_na_water_hydrogen"),
        ("k", "ent_species_k_plus", "ent_substance_koh", "rxn_m11_k_water_hydrogen"),
    ],
)
def test_na_and_k_reuse_one_rule_exact_balancer_and_canonical_identity(
    symbol: str,
    ion_id: str,
    hydroxide_id: str,
    reaction_id: str,
) -> None:
    kb = load_knowledge(ROOT)
    metal_id = f"ent_substance_elemental_{symbol}"
    plans = compile_rules(kb)
    first = infer_case(kb, plans, _case(reaction_id, metal_id))
    second = infer_case(kb, plans, _case(reaction_id, metal_id))

    assert first == second
    assert first["status"] == "inferred"
    assert first["rule_id"] == RULE_ID
    assert first["canonical_match"] == {
        "state": "exact",
        "reaction_ids": [reaction_id],
        "reaction_forms": {reaction_id: ["molecular", "complete_ionic", "net_ionic"]},
        "condition_evidence_ids": ["ev_m11_alkali_metal_water_reactivity"],
    }
    assert first["validation"] == {"atoms": True, "charge": True}
    assert _normalized(first["participants"]) == sorted(
        [
            ("reactant", metal_id, "solid", 2, 1),
            ("reactant", "ent_substance_h2o", "liquid", 2, 1),
            ("product", hydroxide_id, "aqueous", 2, 1),
            ("product", "ent_substance_h2", "gas", 1, 1),
        ]
    )
    assert first["provenance"]["relation_assertions"] == [
        {
            "source_id": metal_id,
            "relation_key": "metal.product_cation",
            "target_id": ion_id,
            "context": {},
            "evidence_ids": ["ev_m11_alkali_metal_identity_and_cations"],
        }
    ]
    assert first["provenance"]["speciation_profiles"] == []
    assert {
        "ev_f2_reactions",
        "ev_m11_alkali_metal_identity_and_cations",
        "ev_m11_alkali_metal_water_reactivity",
    } <= set(first["provenance"]["evidence_ids"])


@pytest.mark.parametrize(
    ("symbol", "ion_id", "hydroxide_id", "reaction_id", "profile_evidence_id"),
    [
        (
            "na",
            "ent_species_na_plus",
            "ent_substance_naoh",
            "rxn_m11_na_water_hydrogen",
            "ev_f2_reactions",
        ),
        (
            "k",
            "ent_species_k_plus",
            "ent_substance_koh",
            "rxn_m11_k_water_hydrogen",
            "ev_f3b_strong_acid_base",
        ),
    ],
)
def test_m11_complete_and_net_ionic_forms_are_equal_without_fake_water_speciation(
    symbol: str,
    ion_id: str,
    hydroxide_id: str,
    reaction_id: str,
    profile_evidence_id: str,
) -> None:
    kb = load_knowledge(ROOT)
    metal_id = f"ent_substance_elemental_{symbol}"
    context = {"medium": "aqueous", "temperature_regime": "ambient"}
    complete = derive_aqueous_ionic_form(kb, reaction_id, "complete_ionic", context)
    net = derive_aqueous_ionic_form(kb, reaction_id, "net_ionic", context)
    expected = sorted(
        [
            ("reactant", metal_id, "solid", 2, 1),
            ("reactant", "ent_substance_h2o", "liquid", 2, 1),
            ("product", ion_id, "dissolved", 2, 1),
            ("product", "ent_species_oh_minus", "dissolved", 2, 1),
            ("product", "ent_substance_h2", "gas", 1, 1),
        ]
    )

    for form in (complete, net):
        assert form["status"] == "derived"
        assert form["reaction_id"] == reaction_id
        assert form["validation"] == {"atoms": True, "charge": True}
        assert _normalized(form["participants"]) == expected
        assert form["derivation"]["speciation_profiles"] == [
            {
                "target_id": hydroxide_id,
                "profile_key": "aqueous_complete_dissociation",
                "model": "strong_electrolyte_complete_dissociation",
                "evidence_ids": [profile_evidence_id],
            }
        ]
        assert "ent_substance_h2o" not in {
            item["target_id"] for item in form["derivation"]["speciation_profiles"]
        }
        assert "ev_m11_alkali_metal_water_reactivity" in form["derivation"]["evidence_ids"]
    assert _normalized(complete["participants"]) == _normalized(net["participants"])


@pytest.mark.parametrize("symbol", ["cu", "zn", "mg"])
def test_cu_zn_and_mg_water_cases_remain_unknown_without_authored_reactivity(
    symbol: str,
) -> None:
    kb = load_knowledge(ROOT)
    metal_id = f"ent_substance_elemental_{symbol}"
    fact = kb.property_fact(
        metal_id,
        "metal.water_reactivity",
        {"medium": "aqueous", "temperature_regime": "ambient"},
    )
    result = infer_case(kb, compile_rules(kb), _case(f"{symbol}-water", metal_id))

    assert fact.state is KnowledgeState.ABSENT
    assert result["status"] == "indeterminate"
    assert result["diagnostic"]["code"] == "unknown_applicability"
    assert "candidate_key" not in result
    evaluations = [
        item
        for item in result["proof_trace"]
        if item.get("rule_id") == RULE_ID and item.get("key") == "metal.water_reactivity"
    ]
    assert len(evaluations) == 1
    assert evaluations[0]["truth"] == "UNKNOWN"
    assert evaluations[0]["knowledge_state"] == "absent"


def test_missing_temperature_or_non_liquid_water_does_not_infer_m11() -> None:
    kb = load_knowledge(ROOT)
    plans = compile_rules(kb)
    missing_temperature = infer_case(
        kb,
        plans,
        _case("na-water-no-temperature", "ent_substance_elemental_na", include_temperature=False),
    )
    steam = infer_case(
        kb,
        plans,
        _case("na-steam", "ent_substance_elemental_na", water_phase="gas"),
    )

    assert missing_temperature["status"] == "indeterminate"
    assert missing_temperature["diagnostic"]["code"] == "unknown_applicability"
    assert not any(
        item.get("event") == "rule.match" and item.get("rule_id") == RULE_ID
        for item in steam["proof_trace"]
    )
    assert steam["status"] in {"no_match", "indeterminate"}
    assert "candidate_key" not in steam


def test_missing_water_reactivity_and_missing_product_cation_stay_explicit() -> None:
    kb = load_knowledge(ROOT)
    entities = copy.deepcopy(kb.entities)
    sodium = entities["ent_substance_elemental_na"]
    sodium["property_assertions"] = [
        item
        for item in sodium["property_assertions"]
        if item["property_key"] != "metal.water_reactivity"
    ]
    missing_fact_kb = replace(kb, entities=entities)
    missing_fact = infer_case(
        missing_fact_kb,
        compile_rules(missing_fact_kb),
        _case("missing-water-reactivity", "ent_substance_elemental_na"),
    )
    assert missing_fact["status"] == "indeterminate"
    assert missing_fact["diagnostic"]["code"] == "unknown_applicability"

    entities = copy.deepcopy(kb.entities)
    entities["ent_substance_elemental_na"].pop("relation_assertions")
    missing_relation_kb = replace(kb, entities=entities)
    missing_relation = infer_case(
        missing_relation_kb,
        compile_rules(missing_relation_kb),
        _case("missing-product-cation", "ent_substance_elemental_na"),
    )
    assert missing_relation["status"] == "invalid"
    assert missing_relation["diagnostic"]["code"] == "relation_unavailable"
    assert missing_relation["diagnostic"]["stage"] == "relation_resolution"


def test_missing_exact_hydroxide_ion_is_an_explicit_reference_failure() -> None:
    kb = load_knowledge(ROOT)
    entities = copy.deepcopy(kb.entities)
    entities.pop("ent_species_oh_minus")
    altered = replace(kb, entities=entities)
    result = infer_case(
        altered,
        compile_rules(altered),
        _case("missing-hydroxide-ion", "ent_substance_elemental_na"),
    )

    assert result["status"] == "invalid"
    assert result["diagnostic"]["code"] == "reference_unresolved"
    assert result["diagnostic"]["stage"] == "ion_source_resolution"
    assert result["diagnostic"]["details"] == {
        "ion_position": "anion",
        "target_id": "ent_species_oh_minus",
    }


@pytest.mark.parametrize(("mode", "candidate_count"), [("unresolved", 0), ("ambiguous", 2)])
def test_m11_hydroxide_resolution_never_fabricates_identity(
    mode: str,
    candidate_count: int,
) -> None:
    kb = load_knowledge(ROOT)
    entities = copy.deepcopy(kb.entities)
    if mode == "unresolved":
        entities.pop("ent_substance_naoh")
    else:
        duplicate = copy.deepcopy(entities["ent_substance_naoh"])
        duplicate["id"] = "ent_substance_naoh_duplicate"
        duplicate["semantic_keys"] = []
        entities[duplicate["id"]] = duplicate
    altered = replace(kb, entities=entities)
    result = infer_case(
        altered,
        compile_rules(altered),
        _case(mode, "ent_substance_elemental_na"),
    )

    assert result["status"] == "invalid"
    assert result["diagnostic"]["code"] == "product_unresolved"
    assert len(result["diagnostic"]["details"]["candidates"]) == candidate_count
    assert "candidate_key" not in result


def test_m11_overlap_teaching_and_audit_integration_are_deterministic(tmp_path: Path) -> None:
    kb = load_knowledge(ROOT)
    plans = compile_rules(kb)
    first = analyze_rule_overlaps(plans)
    second = analyze_rule_overlaps(compile_rules(load_knowledge(ROOT)))
    assert first == second
    assert not any(RULE_ID in item["rule_ids"] for item in first)

    view = kb.teaching_views["view_f3b_hs_aqueous_core"]
    by_path = {node["path_key"]: set(node.get("members", [])) for node in view["nodes"]}
    reactions = {"rxn_m11_na_water_hydrogen", "rxn_m11_k_water_hydrogen"}
    assert reactions <= by_path["D03/reaction-types/single-displacement"]
    assert reactions <= by_path["D06/notation/ionic-equations"]
    assert {"ent_substance_elemental_na", "ent_substance_elemental_k"} <= by_path[
        "D08/substance-classification/metals"
    ]
    assert {"ent_element_na", "ent_element_k"} <= by_path[
        "D10/elements-and-compounds/representative-elements"
    ]

    audit = audit_repository(ROOT, tmp_path / "audit", "m11-fixture")
    results = {result["case_id"]: result for result in audit["results"]}
    for case_id in ("case_m11_na_water", "case_m11_k_water"):
        assert results[case_id]["status"] == "inferred"
        assert results[case_id]["rule_id"] == RULE_ID
        assert results[case_id]["canonical_match"]["state"] == "exact"
    for case_id in ("case_m11_cu_water", "case_m11_zn_water", "case_m11_mg_water"):
        assert results[case_id]["status"] == "indeterminate"
        assert "candidate_key" not in results[case_id]
