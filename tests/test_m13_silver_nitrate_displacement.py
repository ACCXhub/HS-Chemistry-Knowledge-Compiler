from __future__ import annotations

from pathlib import Path

import pytest

from compiler.build import ARTIFACT_FORMAT_VERSION, artifact_versions, audit_repository
from compiler.engine import infer_case
from compiler.reaction_forms import derive_aqueous_ionic_form
from compiler.rules import RULE_DSL_VERSION, RULE_PLAN_VERSION, compile_rules
from compiler.source import SOURCE_SCHEMA_VERSION, load_knowledge


ROOT = Path(__file__).resolve().parents[1]
RULE_ID = "rule_m13_metal_silver_nitrate_displacement"
SILVER_EVIDENCE_ID = "ev_m13_silver_nitrate_identity_and_speciation"
DISPLACEMENT_EVIDENCE_ID = "ev_m13_metal_silver_displacement"


def _ids_for_semantic_key(kb, scheme: str, value: str) -> tuple[str, ...]:
    return kb.semantic_keys[(scheme, value)]


def _atoms(entity: dict) -> dict[str, int]:
    return {
        component["element_id"]: component["count"]
        for component in entity["payload"]["composition"]["components"]
    }


def _case(case_id: str, metal_id: str) -> dict:
    return {
        "id": case_id,
        "reactants": [
            {"target_id": metal_id, "phase": "solid"},
            {"target_id": "ent_substance_agno3", "phase": "aqueous"},
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


def test_m13_reuses_silver_identities_and_hardens_authoritative_evidence() -> None:
    kb = load_knowledge(ROOT)

    assert _ids_for_semantic_key(kb, "element.symbol", "Ag") == ("ent_element_ag",)
    assert _ids_for_semantic_key(kb, "formula.ion", "Ag+") == ("ent_species_ag_plus",)
    assert _ids_for_semantic_key(kb, "formula.unit", "AgNO3") == ("ent_substance_agno3",)
    assert kb.sources["src_f2_fixture"]["source_type"] == "fixture"
    assert "not a corpus authority" in kb.sources["src_f2_fixture"]["citation"]
    assert kb.evidence["ev_f2_reactions"]["source_id"] == "src_f2_fixture"

    authoritative = kb.evidence[SILVER_EVIDENCE_ID]
    assert authoritative["source_id"] == "src_openstax_chemistry_2e"
    for entity_id in ("ent_element_ag", "ent_species_ag_plus", "ent_substance_agno3"):
        assert SILVER_EVIDENCE_ID in kb.entities[entity_id]["evidence_ids"]

    silver_nitrate = kb.entities["ent_substance_agno3"]
    for assertion in silver_nitrate["facet_assertions"] + silver_nitrate["property_assertions"]:
        assert SILVER_EVIDENCE_ID in assertion["evidence_ids"]
    profile = kb.speciation_profiles("ent_substance_agno3", {"medium": "aqueous"})[0]
    assert profile["products"] == [
        {"target_id": "ent_species_ag_plus", "coefficient": {"numerator": 1, "denominator": 1}},
        {"target_id": "ent_species_no3_minus", "coefficient": {"numerator": 1, "denominator": 1}},
    ]
    assert SILVER_EVIDENCE_ID in profile["evidence_ids"]


def test_m13_elemental_silver_and_metal_nitrates_are_canonical_data() -> None:
    kb = load_knowledge(ROOT)

    silver = kb.entities["ent_substance_elemental_ag"]
    assert silver["entity_kind"] == "substance"
    assert silver["payload"]["substance_kind"] == "elemental"
    assert _atoms(silver) == {"ent_element_ag": 1}
    assert silver["payload"]["composition"]["net_charge"] == 0
    assert kb.facet_fact(silver["id"], "classification.metal").value is True
    assert "speciation_profiles" not in silver
    assert silver["id"] != "ent_element_ag"
    assert _ids_for_semantic_key(kb, "formula.elemental_basis", "Ag") == (silver["id"],)

    expected = {
        "ent_substance_zn_no3_2": ("Zn(NO3)2", "ent_element_zn", "ent_species_zn_2plus"),
        "ent_substance_mg_no3_2": ("Mg(NO3)2", "ent_element_mg", "ent_species_mg_2plus"),
    }
    for substance_id, (formula, metal_element_id, cation_id) in expected.items():
        assert _ids_for_semantic_key(kb, "formula.unit", formula) == (substance_id,)
        substance = kb.entities[substance_id]
        assert substance["payload"]["substance_kind"] == "pure_compound"
        assert _atoms(substance) == {
            metal_element_id: 1,
            "ent_element_n": 2,
            "ent_element_o": 6,
        }
        assert substance["payload"]["composition"]["net_charge"] == 0
        assert kb.facet_fact(substance_id, "classification.salt").value is True
        assert kb.facet_fact(substance_id, "classification.nitrate").value is True
        assert kb.property_fact(substance_id, "solubility.class", {"medium": "aqueous"}).value == "soluble"
        assert kb.property_fact(substance_id, "electrolyte.strength", {"medium": "aqueous"}).value == "strong"
        assert kb.speciation_profiles(substance_id, {"medium": "aqueous"})[0]["products"] == [
            {"target_id": cation_id, "coefficient": {"numerator": 1, "denominator": 1}},
            {"target_id": "ent_species_no3_minus", "coefficient": {"numerator": 2, "denominator": 1}},
        ]


def test_m13_zinc_and_magnesium_have_real_many_target_displacement_relations() -> None:
    kb = load_knowledge(ROOT)
    evidence = kb.evidence[DISPLACEMENT_EVIDENCE_ID]
    assert evidence["source_id"] == "src_openstax_chemistry_2e"

    for metal in ("zn", "mg"):
        metal_id = f"ent_substance_elemental_{metal}"
        assertions = kb.relation_assertions(
            metal_id,
            "metal.displaces_cation",
            {"medium": "aqueous", "temperature_regime": "ambient"},
        )
        assert [(item["target_id"], item["evidence_ids"]) for item in assertions] == [
            ("ent_species_ag_plus", [DISPLACEMENT_EVIDENCE_ID]),
            ("ent_species_cu_2plus", ["ev_m12_metal_copper_displacement"]),
        ]
        product_cations = kb.relation_assertions(
            metal_id,
            "metal.product_cation",
            {"medium": "aqueous", "temperature_regime": "ambient"},
        )
        assert len(product_cations) == 1


def test_m13_rule_is_agno3_bounded_and_reuses_m12_contracts() -> None:
    plan = next(plan for plan in compile_rules(load_knowledge(ROOT)) if plan.rule_id == RULE_ID)
    patterns = {pattern.bind: pattern for pattern in plan.patterns}
    relation = next(predicate for predicate in plan.predicates if predicate.subject == "relation")

    assert patterns["metal"].target_id is None
    assert patterns["metal"].entity_kind == "substance"
    assert patterns["metal"].phase == "solid"
    assert patterns["metal"].required_facets == ("classification.metal",)
    assert patterns["silver_nitrate"].target_id == "ent_substance_agno3"
    assert patterns["silver_nitrate"].phase == "aqueous"
    assert relation.binding == "metal"
    assert relation.key == "metal.displaces_cation"
    assert relation.target_id == "ent_species_ag_plus"
    assert relation.operator == "equals"
    assert relation.expected is True

    nitrate = plan.products[0]
    assert nitrate.constructor == "ionic_pair"
    assert nitrate.phase == "aqueous"
    assert nitrate.cation_source.kind == "relation_target"
    assert nitrate.cation_source.binding == "metal"
    assert nitrate.cation_source.relation_key == "metal.product_cation"
    assert nitrate.anion_source.kind == "speciation"
    assert nitrate.anion_source.binding == "silver_nitrate"
    assert [(product.constructor, product.target_id, product.phase) for product in plan.products[1:]] == [
        ("exact_entity", "ent_substance_elemental_ag", "solid")
    ]
    assert plan.decision_domain == "aqueous_silver_nitrate_displacement"


@pytest.mark.parametrize(
    ("metal", "cation_id", "nitrate_id", "reaction_id"),
    [
        ("zn", "ent_species_zn_2plus", "ent_substance_zn_no3_2", "rxn_m13_zn_agno3_displacement"),
        ("mg", "ent_species_mg_2plus", "ent_substance_mg_no3_2", "rxn_m13_mg_agno3_displacement"),
    ],
)
def test_m13_one_rule_infers_exact_balanced_reactions_with_full_provenance(
    metal: str,
    cation_id: str,
    nitrate_id: str,
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
            ("reactant", "ent_substance_agno3", "aqueous", 2, 1),
            ("product", nitrate_id, "aqueous", 1, 1),
            ("product", "ent_substance_elemental_ag", "solid", 2, 1),
        ]
    )
    assert first["provenance"]["relation_assertions"] == [
        {
            "source_id": metal_id,
            "relation_key": "metal.displaces_cation",
            "target_id": "ent_species_ag_plus",
            "context": {"medium": "aqueous"},
            "evidence_ids": [DISPLACEMENT_EVIDENCE_ID],
        },
        {
            "source_id": metal_id,
            "relation_key": "metal.product_cation",
            "target_id": cation_id,
            "context": {"medium": "aqueous"},
            "evidence_ids": ["ev_m10_metal_hydrogen_activity"],
        },
    ]
    assert first["provenance"]["speciation_profiles"] == [
        {
            "target_id": "ent_substance_agno3",
            "profile_key": "aqueous_complete_dissociation",
            "model": "strong_electrolyte_complete_dissociation",
            "evidence_ids": ["ev_f2_reactions", SILVER_EVIDENCE_ID],
        }
    ]
    relation_event = next(
        item
        for item in first["proof_trace"]
        if item.get("event") == "predicate.eval" and item.get("subject") == "relation"
    )
    assert relation_event["truth"] == "TRUE"
    assert relation_event["target_id"] == "ent_species_ag_plus"
    assert relation_event["relation_assertions"] == first["provenance"]["relation_assertions"][:1]


@pytest.mark.parametrize(
    ("metal", "cation_id", "reaction_id"),
    [
        ("zn", "ent_species_zn_2plus", "rxn_m13_zn_agno3_displacement"),
        ("mg", "ent_species_mg_2plus", "rxn_m13_mg_agno3_displacement"),
    ],
)
def test_m13_complete_and_net_ionic_forms_cancel_only_nitrate(
    metal: str,
    cation_id: str,
    reaction_id: str,
) -> None:
    kb = load_knowledge(ROOT)
    metal_id = f"ent_substance_elemental_{metal}"
    nitrate_id = f"ent_substance_{metal}_no3_2"
    context = {"medium": "aqueous", "temperature_regime": "ambient"}
    complete = derive_aqueous_ionic_form(kb, reaction_id, "complete_ionic", context)
    net = derive_aqueous_ionic_form(kb, reaction_id, "net_ionic", context)

    assert complete["status"] == "derived"
    assert complete["validation"] == {"atoms": True, "charge": True}
    assert _normalized(complete["participants"]) == sorted(
        [
            ("reactant", metal_id, "solid", 1, 1),
            ("reactant", "ent_species_ag_plus", "dissolved", 2, 1),
            ("reactant", "ent_species_no3_minus", "dissolved", 2, 1),
            ("product", cation_id, "dissolved", 1, 1),
            ("product", "ent_species_no3_minus", "dissolved", 2, 1),
            ("product", "ent_substance_elemental_ag", "solid", 2, 1),
        ]
    )
    assert {item["target_id"] for item in complete["derivation"]["speciation_profiles"]} == {
        "ent_substance_agno3",
        nitrate_id,
    }
    assert DISPLACEMENT_EVIDENCE_ID in complete["derivation"]["evidence_ids"]
    assert SILVER_EVIDENCE_ID in complete["derivation"]["evidence_ids"]

    assert net["status"] == "derived"
    assert net["validation"] == {"atoms": True, "charge": True}
    assert _normalized(net["participants"]) == sorted(
        [
            ("reactant", metal_id, "solid", 1, 1),
            ("reactant", "ent_species_ag_plus", "dissolved", 2, 1),
            ("product", cation_id, "dissolved", 1, 1),
            ("product", "ent_substance_elemental_ag", "solid", 2, 1),
        ]
    )
    assert not any(item["target_id"] == "ent_species_no3_minus" for item in net["participants"])


@pytest.mark.parametrize("metal", ["ag", "na", "k", "cu"])
def test_m13_missing_ag_displacement_knowledge_remains_open_world(metal: str) -> None:
    kb = load_knowledge(ROOT)
    metal_id = f"ent_substance_elemental_{metal}"
    assert not any(
        assertion["target_id"] == "ent_species_ag_plus"
        for assertion in kb.relation_assertions(
            metal_id,
            "metal.displaces_cation",
            {"medium": "aqueous", "temperature_regime": "ambient"},
        )
    )

    result = infer_case(kb, compile_rules(kb), _case(f"{metal}-agno3", metal_id))
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


def test_m13_compatibility_coordinates_remain_frozen() -> None:
    assert SOURCE_SCHEMA_VERSION == "3.5.0"
    assert RULE_DSL_VERSION == "1.3.0"
    assert RULE_PLAN_VERSION == "1.3.0"
    assert ARTIFACT_FORMAT_VERSION == "1.4.0"
    assert artifact_versions() == {
        "source_schema": "3.5.0",
        "rule_dsl": "1.3.0",
        "rule_plan": "1.3.0",
        "artifact_format": "1.4.0",
    }


def test_m13_teaching_fixture_and_prior_family_regressions(tmp_path: Path) -> None:
    kb = load_knowledge(ROOT)
    view = kb.teaching_views["view_f3b_hs_aqueous_core"]
    by_path = {node["path_key"]: set(node.get("members", [])) for node in view["nodes"]}
    reactions = {"rxn_m13_zn_agno3_displacement", "rxn_m13_mg_agno3_displacement"}
    assert reactions <= by_path["D03/reaction-types/single-displacement"]
    assert reactions <= by_path["D06/notation/ionic-equations"]
    assert {
        "ent_substance_agno3",
        "ent_substance_zn_no3_2",
        "ent_substance_mg_no3_2",
    } <= by_path["D08/substance-classification/salts"]
    assert "ent_substance_elemental_ag" in by_path["D08/substance-classification/metals"]
    assert {
        "ent_element_ag",
        "ent_species_ag_plus",
        "ent_substance_elemental_ag",
    } <= by_path["D10/elements-and-compounds/representative-elements"]

    audit = audit_repository(ROOT, tmp_path / "audit", "m13-fixture")
    results = {result["case_id"]: result for result in audit["results"]}
    for case_id in ("case_m13_zn_agno3", "case_m13_mg_agno3"):
        assert results[case_id]["status"] == "inferred"
        assert results[case_id]["rule_id"] == RULE_ID
        assert results[case_id]["canonical_match"]["state"] == "exact"
    for case_id in ("case_m13_ag_agno3", "case_m13_na_agno3", "case_m13_k_agno3", "case_m13_cu_agno3"):
        assert results[case_id]["status"] == "indeterminate"
        assert "candidate_key" not in results[case_id]

    expected_prior = {
        "case_m12_zn_cuso4": "rule_m12_metal_copper_sulfate_displacement",
        "case_m12_mg_cuso4": "rule_m12_metal_copper_sulfate_displacement",
        "case_m10_zn_hcl": "rule_m10_active_metal_non_oxidizing_acid_hydrogen",
        "case_m10_mg_hcl": "rule_m10_active_metal_non_oxidizing_acid_hydrogen",
        "case_m11_na_water": "rule_m11_water_reactive_metal_hydrogen",
        "case_m11_k_water": "rule_m11_water_reactive_metal_hydrogen",
    }
    for case_id, rule_id in expected_prior.items():
        assert results[case_id]["status"] == "inferred"
        assert results[case_id]["rule_id"] == rule_id
        assert results[case_id]["canonical_match"]["state"] == "exact"
    assert results["case_m12_cu_cuso4"]["status"] == "indeterminate"
