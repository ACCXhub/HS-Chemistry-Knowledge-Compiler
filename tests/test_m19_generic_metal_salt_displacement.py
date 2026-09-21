from __future__ import annotations

import copy
import json
from dataclasses import replace
from pathlib import Path

import pytest

from compiler.build import (
    ARTIFACT_FORMAT_VERSION,
    SUPPORTED_ARTIFACT_FORMAT_VERSIONS,
    artifact_versions,
    audit_repository,
    compile_repository,
    validate_artifact_manifest,
)
from compiler.engine import infer_case
from compiler.model import EntitySourcePlan
from compiler.reaction_forms import derive_aqueous_ionic_form
from compiler.rules import RULE_DSL_VERSION, RULE_PLAN_VERSION, compile_rules
from compiler.source import SOURCE_SCHEMA_VERSION, SourceError, load_knowledge, validate_references


ROOT = Path(__file__).resolve().parents[1]
RULE_ID = "rule_m19_generic_aqueous_metal_salt_displacement"


def _case(case_id: str, metal_id: str, salt_id: str) -> dict:
    return {
        "id": case_id,
        "reactants": [
            {"target_id": metal_id, "phase": "solid"},
            {"target_id": salt_id, "phase": "aqueous"},
        ],
        "context": {"medium": "aqueous", "temperature_regime": "ambient"},
    }


def test_generic_rule_lowers_dynamic_relation_target_and_source_derived_product() -> None:
    plan = next(plan for plan in compile_rules(load_knowledge(ROOT)) if plan.rule_id == RULE_ID)
    relation = next(predicate for predicate in plan.predicates if predicate.subject == "relation")
    displaced = plan.products[1]

    assert relation.target_id is None
    assert relation.target_source.kind == "speciation_ion"
    assert relation.target_source.binding == "salt"
    assert relation.target_source.charge_sign == "positive"
    assert displaced.constructor == "entity_source"
    assert displaced.entity_source.kind == "relation_target"
    assert displaced.entity_source.relation_key == "ion.elemental_substance"
    assert displaced.entity_source.source.kind == "speciation_ion"
    assert displaced.entity_source.source.binding == "salt"
    assert displaced.entity_source.source.charge_sign == "positive"


def test_nested_entity_source_in_predicate_trace_is_json_serializable() -> None:
    kb = load_knowledge(ROOT)
    plan = next(plan for plan in compile_rules(kb) if plan.rule_id == RULE_ID)
    predicates = tuple(
        replace(
            predicate,
            target_source=EntitySourcePlan(
                kind="relation_target",
                relation_key="metal.product_cation",
                source=EntitySourcePlan(kind="binding", binding="metal"),
            ),
        )
        if predicate.subject == "relation"
        else predicate
        for predicate in plan.predicates
    )
    synthetic = replace(plan, predicates=predicates)

    result = infer_case(
        kb,
        (synthetic,),
        _case("m19-nested-trace", "ent_substance_elemental_zn", "ent_substance_cuso4"),
    )

    assert result["status"] == "indeterminate"
    json.dumps(result, sort_keys=True)


def test_generic_rule_infers_zinc_copper_sulfate_from_dynamic_cation_source() -> None:
    kb = load_knowledge(ROOT)

    result = infer_case(
        kb,
        compile_rules(kb),
        _case("m19-zn-cuso4", "ent_substance_elemental_zn", "ent_substance_cuso4"),
    )

    assert result["status"] == "inferred"
    assert result["rule_id"] == RULE_ID
    assert result["canonical_match"]["reaction_ids"] == ["rxn_m12_zn_cuso4_displacement"]
    assert {
        (item["role"], item["target_id"], item["phase"], item["coefficient"]["numerator"])
        for item in result["participants"]
    } == {
        ("reactant", "ent_substance_elemental_zn", "solid", 1),
        ("reactant", "ent_substance_cuso4", "aqueous", 1),
        ("product", "ent_substance_znso4", "aqueous", 1),
        ("product", "ent_substance_elemental_cu", "solid", 1),
    }
    assert result["provenance"]["speciation_profiles"] == [
        {
            "target_id": "ent_substance_cuso4",
            "profile_key": "aqueous_complete_dissociation",
            "model": "strong_electrolyte_complete_dissociation",
            "evidence_ids": ["ev_m12_copper_sulfate_identity_and_speciation"],
        }
    ]
    assert [item["relation_key"] for item in result["provenance"]["relation_assertions"]] == [
        "ion.elemental_substance",
        "metal.displaces_cation",
        "metal.product_cation",
    ]


def test_canonical_rule_owner_is_one_generic_family() -> None:
    kb = load_knowledge(ROOT)

    assert RULE_ID in kb.rules
    assert "rule_m12_metal_copper_sulfate_displacement" not in kb.rules
    assert "rule_m13_metal_silver_nitrate_displacement" not in kb.rules
    plan = next(plan for plan in compile_rules(kb) if plan.rule_id == RULE_ID)
    patterns = {pattern.bind: pattern for pattern in plan.patterns}
    relation = next(predicate for predicate in plan.predicates if predicate.subject == "relation")

    assert patterns["metal"].target_id is None
    assert patterns["metal"].phase == "solid"
    assert patterns["metal"].required_facets == ("classification.metal",)
    assert patterns["salt"].target_id is None
    assert patterns["salt"].phase == "aqueous"
    assert patterns["salt"].required_facets == ("classification.salt",)
    assert relation.target_id is None
    assert relation.target_source.binding == "salt"
    assert relation.target_source.charge_sign == "positive"


@pytest.mark.parametrize(
    ("metal", "salt_id", "product_salt_id", "displaced_id", "reaction_id", "coefficients"),
    [
        (
            "zn",
            "ent_substance_cuso4",
            "ent_substance_znso4",
            "ent_substance_elemental_cu",
            "rxn_m12_zn_cuso4_displacement",
            [1, 1, 1, 1],
        ),
        (
            "mg",
            "ent_substance_cuso4",
            "ent_substance_mgso4",
            "ent_substance_elemental_cu",
            "rxn_m12_mg_cuso4_displacement",
            [1, 1, 1, 1],
        ),
        (
            "zn",
            "ent_substance_agno3",
            "ent_substance_zn_no3_2",
            "ent_substance_elemental_ag",
            "rxn_m13_zn_agno3_displacement",
            [1, 2, 1, 2],
        ),
        (
            "mg",
            "ent_substance_agno3",
            "ent_substance_mg_no3_2",
            "ent_substance_elemental_ag",
            "rxn_m13_mg_agno3_displacement",
            [1, 2, 1, 2],
        ),
        (
            "zn",
            "ent_substance_cucl2",
            "ent_substance_zncl2",
            "ent_substance_elemental_cu",
            "rxn_m19_zn_cucl2_displacement",
            [1, 1, 1, 1],
        ),
        (
            "mg",
            "ent_substance_cucl2",
            "ent_substance_mgcl2",
            "ent_substance_elemental_cu",
            "rxn_m19_mg_cucl2_displacement",
            [1, 1, 1, 1],
        ),
    ],
)
def test_one_generic_rule_infers_copper_sulfate_silver_nitrate_and_copper_chloride(
    metal: str,
    salt_id: str,
    product_salt_id: str,
    displaced_id: str,
    reaction_id: str,
    coefficients: list[int],
) -> None:
    kb = load_knowledge(ROOT)
    plans = compile_rules(kb)
    metal_id = f"ent_substance_elemental_{metal}"
    case = _case(f"m19-{metal}-{salt_id}", metal_id, salt_id)

    first = infer_case(kb, plans, case)
    second = infer_case(kb, plans, case)

    assert first == second
    assert first["status"] == "inferred"
    assert first["rule_id"] == RULE_ID
    assert first["canonical_match"]["state"] == "exact"
    assert first["canonical_match"]["reaction_ids"] == [reaction_id]
    assert first["validation"] == {"atoms": True, "charge": True}
    by_id = {item["target_id"]: item for item in first["participants"]}
    assert sorted(item["coefficient"]["numerator"] for item in first["participants"]) == sorted(coefficients)
    assert by_id[metal_id]["phase"] == "solid"
    assert by_id[salt_id]["phase"] == "aqueous"
    assert by_id[product_salt_id]["phase"] == "aqueous"
    assert by_id[displaced_id]["phase"] == "solid"
    profile = first["provenance"]["speciation_profiles"]
    assert [item["target_id"] for item in profile] == [salt_id]
    relations = first["provenance"]["relation_assertions"]
    assert {item["relation_key"] for item in relations} == {
        "metal.displaces_cation",
        "metal.product_cation",
        "ion.elemental_substance",
    }
    dynamic_event = next(
        item
        for item in first["proof_trace"]
        if item.get("event") == "predicate.eval"
        and item.get("rule_id") == RULE_ID
        and item.get("subject") == "relation"
    )
    assert dynamic_event["target_id"] in {"ent_species_cu_2plus", "ent_species_ag_plus"}
    assert dynamic_event["speciation_profiles"] == profile


def test_m19_versions_and_serialized_plan_track_dynamic_entity_sources(tmp_path: Path) -> None:
    assert SOURCE_SCHEMA_VERSION == "3.7.0"
    assert RULE_DSL_VERSION == "1.4.0"
    assert RULE_PLAN_VERSION == "1.4.0"
    assert ARTIFACT_FORMAT_VERSION == "1.5.0"
    assert artifact_versions() == {
        "source_schema": "3.7.0",
        "rule_dsl": "1.4.0",
        "rule_plan": "1.4.0",
        "artifact_format": "1.5.0",
    }
    assert SUPPORTED_ARTIFACT_FORMAT_VERSIONS == frozenset(
        {"1.0.0", "1.1.0", "1.2.0", "1.3.0", "1.4.0", "1.5.0"}
    )
    for historical in ("1.0.0", "1.1.0", "1.2.0", "1.3.0", "1.4.0"):
        validate_artifact_manifest({"versions": {"artifact_format": historical}})

    output = tmp_path / "compiled"
    manifest = compile_repository(ROOT, output, "m19-version-fixture")
    plans = json.loads((output / "compiled-rule-plans.json").read_text(encoding="utf-8"))
    rule = next(item for item in plans["rules"] if item["rule_id"] == RULE_ID)
    relation = next(item for item in rule["predicates"] if item["subject"] == "relation")

    assert manifest["versions"] == artifact_versions()
    assert plans["artifact_format_version"] == "1.5.0"
    assert plans["rule_plan_version"] == "1.4.0"
    assert relation["target_id"] is None
    assert relation["target_source"] == {
        "kind": "speciation_ion",
        "binding": "salt",
        "target_id": None,
        "charge_sign": "positive",
        "relation_key": None,
        "source": None,
    }
    displaced = rule["products"][1]
    assert displaced["constructor"] == "entity_source"
    assert displaced["entity_source"]["relation_key"] == "ion.elemental_substance"
    assert displaced["entity_source"]["source"]["kind"] == "speciation_ion"


@pytest.mark.parametrize(
    ("metal_id", "salt_id"),
    [
        ("ent_substance_elemental_cu", "ent_substance_cuso4"),
        ("ent_substance_elemental_ag", "ent_substance_agno3"),
        ("ent_substance_elemental_na", "ent_substance_cuso4"),
        ("ent_substance_elemental_k", "ent_substance_agno3"),
    ],
)
def test_unsupported_pairwise_displacement_remains_unknown(metal_id: str, salt_id: str) -> None:
    kb = load_knowledge(ROOT)
    result = infer_case(kb, compile_rules(kb), _case("unsupported", metal_id, salt_id))

    assert result["status"] == "indeterminate"
    assert result["diagnostic"]["code"] == "unknown_applicability"
    assert "candidate_key" not in result
    event = next(
        item
        for item in result["proof_trace"]
        if item.get("rule_id") == RULE_ID and item.get("subject") == "relation"
    )
    assert event["truth"] == "UNKNOWN"
    assert event["knowledge_state"] == "absent"


def test_missing_context_and_wrong_salt_phase_do_not_infer() -> None:
    kb = load_knowledge(ROOT)
    plans = compile_rules(kb)
    missing_context = _case(
        "missing-context",
        "ent_substance_elemental_zn",
        "ent_substance_cuso4",
    )
    missing_context["context"] = {"temperature_regime": "ambient"}
    wrong_phase = _case(
        "wrong-phase",
        "ent_substance_elemental_zn",
        "ent_substance_cuso4",
    )
    wrong_phase["reactants"][1]["phase"] = "solid"

    missing = infer_case(kb, plans, missing_context)
    wrong = infer_case(kb, plans, wrong_phase)

    assert missing["status"] == "indeterminate"
    assert missing["diagnostic"]["code"] == "unknown_applicability"
    assert "candidate_key" not in missing
    assert wrong["status"] in {"no_match", "indeterminate"}
    assert wrong.get("rule_id") != RULE_ID
    assert "candidate_key" not in wrong


def test_missing_salt_speciation_is_structured_unknown() -> None:
    kb = load_knowledge(ROOT)
    entities = copy.deepcopy(kb.entities)
    entities["ent_substance_cuso4"].pop("speciation_profiles")
    altered = replace(kb, entities=entities)

    result = infer_case(
        altered,
        compile_rules(altered),
        _case("missing-speciation", "ent_substance_elemental_zn", "ent_substance_cuso4"),
    )

    assert result["status"] == "indeterminate"
    event = next(
        item
        for item in result["proof_trace"]
        if item.get("rule_id") == RULE_ID and item.get("subject") == "relation"
    )
    assert event["truth"] == "UNKNOWN"
    assert event["target_source_diagnostic"]["code"] == "speciation_unavailable"
    assert event["target_source_diagnostic"]["stage"] == "aqueous_speciation"
    assert "candidate_key" not in result


@pytest.mark.parametrize(
    ("mutation", "expected_source_id", "expected_code"),
    [
        ("missing_product_cation", "ent_substance_elemental_zn", "relation_unavailable"),
        ("ambiguous_product_cation", "ent_substance_elemental_zn", "relation_ambiguous"),
        ("missing_elemental_mapping", "ent_species_cu_2plus", "relation_unavailable"),
        ("ambiguous_elemental_mapping", "ent_species_cu_2plus", "relation_ambiguous"),
    ],
)
def test_product_relation_resolution_never_guesses_or_mints(
    mutation: str,
    expected_source_id: str,
    expected_code: str,
) -> None:
    kb = load_knowledge(ROOT)
    entities = copy.deepcopy(kb.entities)
    zinc = entities["ent_substance_elemental_zn"]
    copper_ion = entities["ent_species_cu_2plus"]
    if mutation == "missing_product_cation":
        zinc["relation_assertions"] = [
            item for item in zinc["relation_assertions"] if item["relation_key"] != "metal.product_cation"
        ]
    elif mutation == "ambiguous_product_cation":
        zinc["relation_assertions"].append(
            {
                "relation_key": "metal.product_cation",
                "target_id": "ent_species_mg_2plus",
                "context": {"medium": "aqueous"},
                "evidence_ids": ["ev_m10_metal_hydrogen_activity"],
            }
        )
    elif mutation == "missing_elemental_mapping":
        copper_ion.pop("relation_assertions")
    else:
        copper_ion["relation_assertions"].append(
            {
                "relation_key": "ion.elemental_substance",
                "target_id": "ent_substance_elemental_ag",
                "context": {},
                "evidence_ids": ["ev_m13_metal_silver_displacement"],
            }
        )
    altered = replace(kb, entities=entities)

    result = infer_case(
        altered,
        compile_rules(altered),
        _case(mutation, "ent_substance_elemental_zn", "ent_substance_cuso4"),
    )

    assert result["status"] == "invalid"
    assert result["diagnostic"]["code"] == expected_code
    assert result["diagnostic"]["details"]["source_id"] == expected_source_id
    assert "candidate_key" not in result
    assert set(altered.entities) == set(kb.entities)


@pytest.mark.parametrize(
    ("source_id", "target_id"),
    [
        ("ent_species_cl_minus", "ent_substance_elemental_cu"),
        ("ent_species_cu_2plus", "ent_substance_cuso4"),
    ],
)
def test_ion_elemental_relation_contract_rejects_wrong_endpoints(
    source_id: str,
    target_id: str,
) -> None:
    kb = load_knowledge(ROOT)
    entities = copy.deepcopy(kb.entities)
    entities[source_id].setdefault("relation_assertions", []).append(
        {
            "relation_key": "ion.elemental_substance",
            "target_id": target_id,
            "context": {},
            "evidence_ids": ["ev_m12_metal_copper_displacement"],
        }
    )

    with pytest.raises(SourceError) as exc:
        validate_references(replace(kb, entities=entities))

    assert exc.value.code == "schema_invalid"
    assert exc.value.stage == "reference_validation"
    assert exc.value.details["relation_key"] == "ion.elemental_substance"


@pytest.mark.parametrize(
    ("metal", "cation_id", "product_salt_id", "reaction_id"),
    [
        ("zn", "ent_species_zn_2plus", "ent_substance_zncl2", "rxn_m19_zn_cucl2_displacement"),
        ("mg", "ent_species_mg_2plus", "ent_substance_mgcl2", "rxn_m19_mg_cucl2_displacement"),
    ],
)
def test_copper_chloride_forms_cancel_chloride_without_special_projector(
    metal: str,
    cation_id: str,
    product_salt_id: str,
    reaction_id: str,
) -> None:
    kb = load_knowledge(ROOT)
    context = {"medium": "aqueous", "temperature_regime": "ambient"}
    complete = derive_aqueous_ionic_form(kb, reaction_id, "complete_ionic", context)
    net = derive_aqueous_ionic_form(kb, reaction_id, "net_ionic", context)

    assert complete["status"] == "derived"
    assert complete["validation"] == {"atoms": True, "charge": True}
    assert {item["target_id"] for item in complete["derivation"]["speciation_profiles"]} == {
        "ent_substance_cucl2",
        product_salt_id,
    }
    assert net["status"] == "derived"
    assert net["validation"] == {"atoms": True, "charge": True}
    assert {
        (item["role"], item["target_id"], item["coefficient"]["numerator"])
        for item in net["participants"]
    } == {
        ("reactant", f"ent_substance_elemental_{metal}", 1),
        ("reactant", "ent_species_cu_2plus", 1),
        ("product", cation_id, 1),
        ("product", "ent_substance_elemental_cu", 1),
    }
    assert not any(item["target_id"] == "ent_species_cl_minus" for item in net["participants"])


def test_audit_fixture_and_teaching_ownership_include_copper_chloride(tmp_path: Path) -> None:
    kb = load_knowledge(ROOT)
    view = kb.teaching_views["view_f3b_hs_aqueous_core"]
    by_path = {node["path_key"]: set(node.get("members", [])) for node in view["nodes"]}
    new_reactions = {"rxn_m19_zn_cucl2_displacement", "rxn_m19_mg_cucl2_displacement"}
    assert new_reactions <= by_path["D03/reaction-types/single-displacement"]
    assert new_reactions <= by_path["D06/notation/ionic-equations"]

    audit = audit_repository(ROOT, tmp_path / "audit", "m19-fixture")
    results = {result["case_id"]: result for result in audit["results"]}
    expected = {
        "case_m12_zn_cuso4",
        "case_m12_mg_cuso4",
        "case_m13_zn_agno3",
        "case_m13_mg_agno3",
        "case_m19_zn_cucl2",
        "case_m19_mg_cucl2",
    }
    assert expected <= set(results)
    for case_id in expected:
        assert results[case_id]["status"] == "inferred"
        assert results[case_id]["rule_id"] == RULE_ID
        assert results[case_id]["canonical_match"]["state"] == "exact"
