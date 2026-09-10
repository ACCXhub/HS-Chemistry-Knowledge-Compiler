from __future__ import annotations

import copy
from dataclasses import replace
from pathlib import Path

import pytest

from compiler.build import artifact_versions, audit_repository
from compiler.engine import infer_case
from compiler.reaction_forms import derive_aqueous_ionic_form
from compiler.rules import analyze_rule_overlaps, compile_rules
from compiler.source import load_cases, load_knowledge


ROOT = Path(__file__).resolve().parents[1]
RULE_ID = "rule_m9_acid_thiosulfate_decomposition"


def _atoms(entity: dict) -> dict[str, int]:
    return {
        component["element_id"]: component["count"]
        for component in entity["payload"]["composition"]["components"]
    }


def _case(
    case_id: str,
    acid_id: str,
    thiosulfate_id: str,
    *,
    include_medium: bool = True,
) -> dict:
    context = {"temperature_regime": "ambient"}
    if include_medium:
        context["medium"] = "aqueous"
    return {
        "id": case_id,
        "reactants": [
            {"target_id": acid_id, "phase": "aqueous"},
            {"target_id": thiosulfate_id, "phase": "aqueous"},
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


def test_thiosulfate_ion_has_exact_composition_and_charge() -> None:
    kb = load_knowledge(ROOT)

    assert "ent_species_s2o3_2minus" in kb.entities
    thiosulfate = kb.entities["ent_species_s2o3_2minus"]
    assert thiosulfate["entity_kind"] == "species"
    assert thiosulfate["payload"]["species_kind"] == "ion"
    assert thiosulfate["payload"]["formal_charge"] == -2
    assert thiosulfate["payload"]["composition"]["net_charge"] == -2
    assert _atoms(thiosulfate) == {"ent_element_s": 2, "ent_element_o": 3}


def test_elemental_sulfur_is_a_substance_with_a_stoichiometric_basis() -> None:
    kb = load_knowledge(ROOT)

    assert "ent_substance_elemental_sulfur" in kb.entities
    sulfur = kb.entities["ent_substance_elemental_sulfur"]
    assert sulfur["entity_kind"] == "substance"
    assert sulfur["payload"]["substance_kind"] == "elemental"
    assert sulfur["id"] != "ent_element_s"
    assert sulfur["payload"]["composition"]["net_charge"] == 0
    assert _atoms(sulfur) == {"ent_element_s": 1}


@pytest.mark.parametrize(
    ("substance_id", "cation_id", "element_id"),
    [
        ("ent_substance_na2s2o3", "ent_species_na_plus", "ent_element_na"),
        ("ent_substance_k2s2o3", "ent_species_k_plus", "ent_element_k"),
    ],
)
def test_soluble_thiosulfate_salts_have_exact_composition_and_speciation(
    substance_id: str,
    cation_id: str,
    element_id: str,
) -> None:
    kb = load_knowledge(ROOT)

    assert substance_id in kb.entities
    salt = kb.entities[substance_id]
    assert _atoms(salt) == {element_id: 2, "ent_element_s": 2, "ent_element_o": 3}
    assert salt["payload"]["composition"]["net_charge"] == 0
    assert kb.facet_fact(substance_id, "classification.salt").value is True
    assert kb.facet_fact(substance_id, "classification.thiosulfate").value is True
    assert kb.property_fact(substance_id, "electrolyte.strength", {"medium": "aqueous"}).value == "strong"
    assert kb.property_fact(substance_id, "solubility.class", {"medium": "aqueous"}).value == "soluble"
    assert kb.speciation_profiles(substance_id, {"medium": "aqueous"})[0]["products"] == [
        {"target_id": cation_id, "coefficient": {"numerator": 2, "denominator": 1}},
        {
            "target_id": "ent_species_s2o3_2minus",
            "coefficient": {"numerator": 1, "denominator": 1},
        },
    ]


def test_hydrochloric_acid_has_evidence_backed_non_oxidizing_aqueous_character() -> None:
    fact = load_knowledge(ROOT).property_fact(
        "ent_substance_hcl",
        "acid.redox_character",
        {"medium": "aqueous"},
    )

    assert fact.state.value == "known"
    assert fact.value == "non_oxidizing"
    assert fact.origin == "contextual"
    assert fact.context == (("medium", "aqueous"),)
    assert fact.evidence_ids == ("ev_m9_hcl_redox_compatibility",)


def test_m9_rule_is_generic_and_composes_existing_product_primitives() -> None:
    plans = compile_rules(load_knowledge(ROOT))

    assert RULE_ID in {plan.rule_id for plan in plans}
    plan = next(plan for plan in plans if plan.rule_id == RULE_ID)
    patterns = {pattern.bind: pattern for pattern in plan.patterns}
    assert all(pattern.target_id is None for pattern in plan.patterns)
    assert patterns["acid"].required_facets == ("classification.acid",)
    assert patterns["thiosulfate"].required_facets == (
        "classification.salt",
        "classification.thiosulfate",
    )
    assert plan.products[0].constructor == "ionic_pair"
    assert plan.products[0].cation_from == "thiosulfate"
    assert plan.products[0].anion_from == "acid"
    assert [
        (product.constructor, product.target_id, product.phase)
        for product in plan.products[1:]
    ] == [
        ("exact_entity", "ent_substance_so2", "gas"),
        ("exact_entity", "ent_substance_elemental_sulfur", "solid"),
        ("exact_entity", "ent_substance_h2o", "liquid"),
    ]


@pytest.mark.parametrize(
    ("thiosulfate_id", "salt_id", "reaction_id"),
    [
        (
            "ent_substance_na2s2o3",
            "ent_substance_nacl",
            "rxn_m9_hcl_na2s2o3_decomposition",
        ),
        (
            "ent_substance_k2s2o3",
            "ent_substance_kcl",
            "rxn_m9_hcl_k2s2o3_decomposition",
        ),
    ],
)
def test_two_cation_cases_reuse_m9_rule_and_exact_balancer(
    thiosulfate_id: str,
    salt_id: str,
    reaction_id: str,
) -> None:
    kb = load_knowledge(ROOT)
    result = infer_case(
        kb,
        compile_rules(kb),
        _case(reaction_id, "ent_substance_hcl", thiosulfate_id),
    )

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
            ("reactant", "ent_substance_hcl", "aqueous", 2, 1),
            ("reactant", thiosulfate_id, "aqueous", 1, 1),
            ("product", salt_id, "aqueous", 2, 1),
            ("product", "ent_substance_so2", "gas", 1, 1),
            ("product", "ent_substance_elemental_sulfur", "solid", 1, 1),
            ("product", "ent_substance_h2o", "liquid", 1, 1),
        ]
    )
    profiles = result["provenance"]["speciation_profiles"]
    assert {item["target_id"] for item in profiles} == {
        "ent_substance_hcl",
        thiosulfate_id,
    }
    redox_events = [
        event
        for event in result["proof_trace"]
        if event.get("rule_id") == RULE_ID and event.get("key") == "acid.redox_character"
    ]
    assert len(redox_events) == 1
    assert redox_events[0]["truth"] == "TRUE"
    assert redox_events[0]["evidence_ids"] == ["ev_m9_hcl_redox_compatibility"]


def test_both_m9_reactions_derive_the_same_mixed_phase_net_ionic_form() -> None:
    kb = load_knowledge(ROOT)
    expected_net = sorted(
        [
            ("reactant", "ent_species_h_plus", "dissolved", 2, 1),
            ("reactant", "ent_species_s2o3_2minus", "dissolved", 1, 1),
            ("product", "ent_substance_so2", "gas", 1, 1),
            ("product", "ent_substance_elemental_sulfur", "solid", 1, 1),
            ("product", "ent_substance_h2o", "liquid", 1, 1),
        ]
    )

    for reaction_id in (
        "rxn_m9_hcl_na2s2o3_decomposition",
        "rxn_m9_hcl_k2s2o3_decomposition",
    ):
        complete = derive_aqueous_ionic_form(
            kb,
            reaction_id,
            "complete_ionic",
            {"medium": "aqueous"},
        )
        net = derive_aqueous_ionic_form(
            kb,
            reaction_id,
            "net_ionic",
            {"medium": "aqueous"},
        )
        golden = next(
            form
            for form in kb.reactions[reaction_id]["forms"]
            if form["form_kind"] == "net_ionic"
        )

        assert complete["status"] == "derived"
        assert complete["validation"] == {"atoms": True, "charge": True}
        assert {
            (item["target_id"], item["phase"])
            for item in complete["participants"]
            if item["role"] == "product"
        } >= {
            ("ent_substance_so2", "gas"),
            ("ent_substance_elemental_sulfur", "solid"),
            ("ent_substance_h2o", "liquid"),
        }
        assert net["status"] == "derived"
        assert net["reaction_id"] == reaction_id
        assert net["validation"] == {"atoms": True, "charge": True}
        assert _normalized(net["participants"]) == expected_net
        assert _normalized(net["participants"]) == _normalized(golden["participants"])
        assert net["derivation"]["operators"] == [
            "expand_approved_aqueous_speciation",
            "cancel_identical_canonical_spectators",
        ]
        assert net["derivation"]["reaction_conditions"] == []
        assert net["derivation"]["speciation_profiles"]
        assert "ev_m9_thiosulfate_hcl_decomposition" in net["derivation"]["evidence_ids"]


def test_hno3_redox_boundary_and_missing_medium_remain_unknown() -> None:
    kb = load_knowledge(ROOT)
    plans = compile_rules(kb)
    nitric = infer_case(
        kb,
        plans,
        _case("hno3-pressure", "ent_substance_hno3", "ent_substance_na2s2o3"),
    )
    missing_medium = infer_case(
        kb,
        plans,
        _case(
            "missing-medium",
            "ent_substance_hcl",
            "ent_substance_na2s2o3",
            include_medium=False,
        ),
    )

    for result in (nitric, missing_medium):
        assert result["status"] == "indeterminate"
        assert result["diagnostic"]["code"] == "unknown_applicability"
        assert "candidate_key" not in result
    redox_events = [
        event
        for event in nitric["proof_trace"]
        if event.get("rule_id") == RULE_ID and event.get("key") == "acid.redox_character"
    ]
    assert redox_events
    assert all(event["truth"] == "UNKNOWN" for event in redox_events)
    assert all(event["knowledge_state"] == "absent" for event in redox_events)


def test_sulfate_and_sulfite_are_not_misclassified_as_thiosulfate() -> None:
    kb = load_knowledge(ROOT)
    plans = compile_rules(kb)
    sulfate = infer_case(
        kb,
        plans,
        _case("sulfate-contrast", "ent_substance_hcl", "ent_substance_na2so4"),
    )
    sulfite = infer_case(
        kb,
        plans,
        _case("sulfite-contrast", "ent_substance_hcl", "ent_substance_na2so3"),
    )

    assert sulfate["status"] == "indeterminate"
    assert "candidate_key" not in sulfate
    assert sulfite["status"] == "inferred"
    assert sulfite["rule_id"] == "rule_m8_strong_acid_sulfite_gas_evolution"
    assert all(
        participant["target_id"] != "ent_substance_elemental_sulfur"
        for participant in sulfite["participants"]
    )


def test_missing_thiosulfate_speciation_is_explicit_and_never_formula_guessed() -> None:
    kb = load_knowledge(ROOT)
    entities = copy.deepcopy(kb.entities)
    entities["ent_substance_na2s2o3"].pop("speciation_profiles")
    altered = replace(kb, entities=entities)

    result = infer_case(
        altered,
        compile_rules(altered),
        _case("missing-speciation", "ent_substance_hcl", "ent_substance_na2s2o3"),
    )

    assert result["status"] == "invalid"
    assert result["diagnostic"]["code"] == "speciation_unavailable"
    assert result["diagnostic"]["details"]["target_id"] == "ent_substance_na2s2o3"
    assert "candidate_key" not in result


@pytest.mark.parametrize(("mode", "candidate_count"), [("unresolved", 0), ("ambiguous", 2)])
def test_thiosulfate_spectator_salt_resolution_never_fabricates_identity(
    mode: str,
    candidate_count: int,
) -> None:
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
        _case(mode, "ent_substance_hcl", "ent_substance_na2s2o3"),
    )

    assert result["status"] == "invalid"
    assert result["diagnostic"]["code"] == "product_unresolved"
    assert len(result["diagnostic"]["details"]["candidates"]) == candidate_count
    assert "candidate_key" not in result


def test_m9_overlap_graph_is_explicit_and_deterministic() -> None:
    first = analyze_rule_overlaps(compile_rules(load_knowledge(ROOT)))
    second = analyze_rule_overlaps(compile_rules(load_knowledge(ROOT)))

    assert first == second
    by_pair = {frozenset(item["rule_ids"]): item for item in first}
    assert by_pair[
        frozenset({RULE_ID, "rule_f2_strong_acid_base_neutralization"})
    ]["relationships"] == ["specializes"]
    for sibling in (
        "rule_m5_strong_acid_hydrogen_carbonate_gas_evolution",
        "rule_m6_strong_acid_carbonate_gas_evolution",
        "rule_m7_ammonium_strong_base_gas_evolution",
        "rule_m8_strong_acid_sulfite_gas_evolution",
    ):
        assert by_pair[frozenset({RULE_ID, sibling})]["relationships"] == [
            "mutually_exclusive_with"
        ]


def test_existing_teaching_view_integrates_m9_without_a_d05_experiment_mapping() -> None:
    view = load_knowledge(ROOT).teaching_views["view_f3b_hs_aqueous_core"]
    by_path = {node["path_key"]: set(node.get("members", [])) for node in view["nodes"]}
    reaction_ids = {
        "rxn_m9_hcl_na2s2o3_decomposition",
        "rxn_m9_hcl_k2s2o3_decomposition",
    }

    assert {"ent_substance_na2s2o3", "ent_substance_k2s2o3"} <= by_path[
        "D02/electrolyte-solutions/strong-electrolytes"
    ]
    assert reaction_ids <= by_path["D03/reaction-types/gas-evolution"]
    assert reaction_ids <= by_path["D06/notation/ionic-equations"]
    assert {"ent_substance_na2s2o3", "ent_substance_k2s2o3"} <= by_path[
        "D08/substance-classification/salts"
    ]
    assert {
        "ent_species_s2o3_2minus",
        "ent_substance_na2s2o3",
        "ent_substance_k2s2o3",
    } <= by_path["D10/elements-and-compounds/sulfur-compounds"]
    assert "ent_substance_elemental_sulfur" in by_path[
        "D10/elements-and-compounds/representative-elements"
    ]
    assert not any(
        reaction_ids & members
        for path, members in by_path.items()
        if path.startswith("D05/")
    )


def test_audit_executes_m9_positive_unknown_and_contrast_cases(tmp_path: Path) -> None:
    audit = audit_repository(ROOT, tmp_path / "audit", "m9-fixture")
    results = {result["case_id"]: result for result in audit["results"]}

    for case_id in ("case_m9_hcl_na2s2o3", "case_m9_hcl_k2s2o3"):
        assert case_id in results
        assert results[case_id]["status"] == "inferred"
        assert results[case_id]["rule_id"] == RULE_ID
        assert results[case_id]["canonical_match"]["state"] == "exact"
    for case_id in (
        "case_m9_hno3_na2s2o3_unknown_redox",
        "case_m9_hcl_na2s2o3_unknown_medium",
        "case_m9_hcl_na2so4_contrast",
    ):
        assert case_id in results
        assert results[case_id]["status"] == "indeterminate"
        assert "candidate_key" not in results[case_id]


def test_m7_condition_semantics_remain_unchanged_with_current_versions() -> None:
    kb = load_knowledge(ROOT)
    result = infer_case(
        kb,
        compile_rules(kb),
        {
            "id": "m7-condition-regression",
            "reactants": [
                {"target_id": "ent_substance_nh4cl", "phase": "aqueous"},
                {"target_id": "ent_substance_naoh", "phase": "aqueous"},
            ],
            "context": {"medium": "aqueous"},
        },
    )

    assert result["status"] == "indeterminate"
    assert "candidate_key" not in result
    assert artifact_versions() == {
        "source_schema": "3.2.0",
        "rule_dsl": "1.1.0",
        "rule_plan": "1.1.0",
        "artifact_format": "1.2.0",
    }


def test_m4_through_m9_candidate_keys_remain_stable() -> None:
    expected = {
        "case_precipitation": "cand_sha256_e748d5055726020bd5eb9741a030c6dd359e9aee5e5552fe28a45423f63a0f86",
        "case_neutralization": "cand_sha256_8248f1b224137d2853abdba56150875a42783d486307d90dbe757e2b89149866",
        "case_m5_hcl_nahco3": "cand_sha256_d4c18d6ea879b428fec9ff50a2fa18660f4661fb66bfe580760ea703ecb517aa",
        "case_m5_hno3_nahco3": "cand_sha256_d31b943663545568c02a91dc3a586756f3974618965af933c78c0d6bd3b42b41",
        "case_m6_hcl_na2co3": "cand_sha256_1275f47bf8ff2af169b7e20e0885ccbe5ae459c55e62ba913b238f14e3313899",
        "case_m6_hno3_na2co3": "cand_sha256_425918981aa1a6d0d44e5e944c20bf7b09f344875c3a6350db60fe40625a72a7",
        "case_m6_hcl_k2co3": "cand_sha256_15b4a7190b84f017e53824d27fa14d5ddca1456a4ecd62ce96edf837cbc8c6fd",
        "case_m7_nh4cl_naoh": "cand_sha256_1c1a6fc2bbe6318d0b9ef95a9bd5db7ba0c803cb0323b687bdee697cab916891",
        "case_m7_nh4_2so4_naoh": "cand_sha256_3a6887b9420c7e44d478b32d1846b8156f40a2cebc9181a0cd7f318109c472de",
        "case_m8_hcl_na2so3": "cand_sha256_70bcdc14447a9f306546a0cf8301e889ac12dd0ef7d0acddbbf38b285d63a378",
        "case_m8_hno3_na2so3": "cand_sha256_75ead4d58201fd52dca019459d689a4479a708b70449882ea616163839142d1d",
        "case_m8_hcl_k2so3": "cand_sha256_96c707940e3848579f8828b8247d46a84d179c63986bbbeddb44ac7e0bf22e85",
        "case_m9_hcl_na2s2o3": "cand_sha256_27fda74a000a136188f60cc6d8b6addb929dd8950a35f3796a2b3405b2c09f5f",
        "case_m9_hcl_k2s2o3": "cand_sha256_a1267ef389ad852b453746fd7da4f5f232ceb885ddbc3f7dc664ef2c0b299138",
    }
    kb = load_knowledge(ROOT)
    plans = compile_rules(kb)
    cases = {case["id"]: case for case in load_cases(ROOT)}

    actual = {
        case_id: infer_case(kb, plans, cases[case_id])["candidate_key"]
        for case_id in expected
    }

    assert actual == expected
