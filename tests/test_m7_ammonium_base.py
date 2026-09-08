from __future__ import annotations

import copy
from dataclasses import replace
from pathlib import Path

import pytest

from compiler.build import audit_repository
from compiler.engine import infer_case
from compiler.reaction_forms import derive_aqueous_ionic_form, project_reaction_form
from compiler.rules import analyze_rule_overlaps, compile_rules
from compiler.source import load_knowledge


ROOT = Path(__file__).resolve().parents[1]
RULE_ID = "rule_m7_ammonium_strong_base_gas_evolution"


def _atoms(entity: dict) -> dict[str, int]:
    return {
        component["element_id"]: component["count"]
        for component in entity["payload"]["composition"]["components"]
    }


def test_ammonium_and_ammonia_have_exact_composition_and_charge() -> None:
    kb = load_knowledge(ROOT)

    ammonium = kb.entities["ent_species_nh4_plus"]
    ammonia = kb.entities["ent_substance_nh3"]

    assert ammonium["payload"]["formal_charge"] == 1
    assert ammonium["payload"]["composition"]["net_charge"] == 1
    assert _atoms(ammonium) == {"ent_element_n": 1, "ent_element_h": 4}
    assert ammonia["payload"]["composition"]["net_charge"] == 0
    assert _atoms(ammonia) == {"ent_element_n": 1, "ent_element_h": 3}


def test_ammonium_salts_have_exact_composition_and_aqueous_speciation() -> None:
    kb = load_knowledge(ROOT)

    ammonium_chloride = kb.entities["ent_substance_nh4cl"]
    ammonium_sulfate = kb.entities["ent_substance_nh4_2so4"]

    assert _atoms(ammonium_chloride) == {
        "ent_element_n": 1,
        "ent_element_h": 4,
        "ent_element_cl": 1,
    }
    assert _atoms(ammonium_sulfate) == {
        "ent_element_n": 2,
        "ent_element_h": 8,
        "ent_element_s": 1,
        "ent_element_o": 4,
    }
    assert kb.speciation_profiles("ent_substance_nh4cl", {"medium": "aqueous"})[0]["products"] == [
        {"target_id": "ent_species_nh4_plus", "coefficient": {"numerator": 1, "denominator": 1}},
        {"target_id": "ent_species_cl_minus", "coefficient": {"numerator": 1, "denominator": 1}},
    ]
    assert kb.speciation_profiles("ent_substance_nh4_2so4", {"medium": "aqueous"})[0]["products"] == [
        {"target_id": "ent_species_nh4_plus", "coefficient": {"numerator": 2, "denominator": 1}},
        {"target_id": "ent_species_so4_2minus", "coefficient": {"numerator": 1, "denominator": 1}},
    ]


def _case(
    case_id: str,
    ammonium_salt_id: str,
    base_id: str = "ent_substance_naoh",
    *,
    medium: bool = True,
    warmed: bool = True,
) -> dict:
    context = {}
    if medium:
        context["medium"] = "aqueous"
    if warmed:
        context["temperature_regime"] = "warmed"
    return {
        "id": case_id,
        "reactants": [
            {"target_id": ammonium_salt_id, "phase": "aqueous"},
            {"target_id": base_id, "phase": "aqueous"},
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


@pytest.mark.parametrize(
    ("ammonium_salt_id", "salt_id", "reaction_id", "coefficients"),
    [
        (
            "ent_substance_nh4cl",
            "ent_substance_nacl",
            "rxn_m7_nh4cl_naoh_ammonia_liberation",
            {"ent_substance_nh4cl": 1, "ent_substance_naoh": 1, "ent_substance_nacl": 1, "ent_substance_nh3": 1, "ent_substance_h2o": 1},
        ),
        (
            "ent_substance_nh4_2so4",
            "ent_substance_na2so4",
            "rxn_m7_nh4_2so4_naoh_ammonia_liberation",
            {"ent_substance_nh4_2so4": 1, "ent_substance_naoh": 2, "ent_substance_na2so4": 1, "ent_substance_nh3": 2, "ent_substance_h2o": 2},
        ),
    ],
)
def test_two_ammonium_cases_reuse_one_rule_and_exact_balancer(
    ammonium_salt_id: str,
    salt_id: str,
    reaction_id: str,
    coefficients: dict[str, int],
) -> None:
    kb = load_knowledge(ROOT)

    result = infer_case(kb, compile_rules(kb), _case(reaction_id, ammonium_salt_id))

    assert result["status"] == "inferred"
    assert result["rule_id"] == RULE_ID
    assert result["canonical_match"] == {
        "state": "exact",
        "reaction_ids": [reaction_id],
        "reaction_forms": {reaction_id: ["molecular", "complete_ionic", "net_ionic"]},
        "condition_evidence_ids": ["ev_m7_ammonia_warmed_test", "ev_m7_ammonium_hydroxide_aqueous"],
    }
    assert result["validation"] == {"atoms": True, "charge": True}
    assert {item["target_id"]: item["coefficient"]["numerator"] for item in result["participants"]} == coefficients
    assert next(item for item in result["participants"] if item["target_id"] == salt_id)["phase"] == "aqueous"
    assert next(item for item in result["participants"] if item["target_id"] == "ent_substance_nh3")["phase"] == "gas"
    assert {item["target_id"] for item in result["provenance"]["speciation_profiles"]} == {
        ammonium_salt_id,
        "ent_substance_naoh",
    }
    assert result["provenance"]["condition_evidence_ids"] == [
        "ev_m7_ammonia_warmed_test",
        "ev_m7_ammonium_hydroxide_aqueous",
    ]


def test_m7_rule_is_generic_conditioned_and_uses_ionic_pair() -> None:
    plan = next(plan for plan in compile_rules(load_knowledge(ROOT)) if plan.rule_id == RULE_ID)

    assert all(pattern.target_id is None for pattern in plan.patterns)
    assert plan.patterns[0].required_facets == ("classification.ammonium", "classification.salt")
    assert plan.patterns[1].required_facets == ("classification.base",)
    assert plan.products[0].constructor == "ionic_pair"
    assert plan.products[0].cation_from == "base"
    assert plan.products[0].anion_from == "ammonium_salt"
    context_predicates = {
        (predicate.key, predicate.expected)
        for predicate in plan.predicates
        if predicate.subject == "context"
    }
    assert context_predicates == {("medium", "aqueous"), ("temperature_regime", "warmed")}


def test_ammonium_examples_derive_same_condition_provenanced_net_ionic_form() -> None:
    kb = load_knowledge(ROOT)
    expected = sorted(
        [
            ("reactant", "ent_species_nh4_plus", "dissolved", 1, 1),
            ("reactant", "ent_species_oh_minus", "dissolved", 1, 1),
            ("product", "ent_substance_nh3", "gas", 1, 1),
            ("product", "ent_substance_h2o", "liquid", 1, 1),
        ]
    )
    for reaction_id in (
        "rxn_m7_nh4cl_naoh_ammonia_liberation",
        "rxn_m7_nh4_2so4_naoh_ammonia_liberation",
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
        assert net["derivation"]["reaction_conditions"] == [
            {"key": "medium", "value": "aqueous", "evidence_ids": ["ev_m7_ammonium_hydroxide_aqueous"]},
            {"key": "temperature_regime", "value": "warmed", "evidence_ids": ["ev_m7_ammonia_warmed_test"]},
        ]
        assert "ev_m7_ammonia_warmed_test" in net["derivation"]["evidence_ids"]


def test_condition_specific_gas_form_requires_warmed_projection_assumption() -> None:
    kb = load_knowledge(ROOT)
    reaction_id = "rxn_m7_nh4cl_naoh_ammonia_liberation"

    without_warming = project_reaction_form(
        kb,
        reaction_id,
        "net_ionic",
        {"aqueous_medium", "strong_electrolyte_dissociation"},
    )
    with_warming = project_reaction_form(
        kb,
        reaction_id,
        "net_ionic",
        {"aqueous_medium", "strong_electrolyte_dissociation", "warmed_ammonia_liberation"},
    )

    assert without_warming is None
    assert with_warming is not None
    assert with_warming["status"] == "derived"


@pytest.mark.parametrize(
    ("medium", "warmed", "expected_status"),
    [(False, True, "indeterminate"), (True, False, "indeterminate")],
)
def test_missing_required_m7_context_does_not_emit_gas_candidate(
    medium: bool,
    warmed: bool,
    expected_status: str,
) -> None:
    kb = load_knowledge(ROOT)
    result = infer_case(
        kb,
        compile_rules(kb),
        _case("missing-condition", "ent_substance_nh4cl", medium=medium, warmed=warmed),
    )

    assert result["status"] == expected_status
    assert "candidate_key" not in result


def test_missing_base_strength_remains_unknown() -> None:
    kb = load_knowledge(ROOT)
    entities = copy.deepcopy(kb.entities)
    entities["ent_substance_naoh"]["property_assertions"] = [
        item
        for item in entities["ent_substance_naoh"]["property_assertions"]
        if item["property_key"] != "base.strength"
    ]
    altered = replace(kb, entities=entities)

    result = infer_case(
        altered,
        compile_rules(altered),
        _case("missing-base-strength", "ent_substance_nh4cl"),
    )

    assert result["status"] == "indeterminate"
    assert "candidate_key" not in result


def test_missing_ammonium_speciation_is_explicit_and_no_formula_guessing_occurs() -> None:
    kb = load_knowledge(ROOT)
    entities = copy.deepcopy(kb.entities)
    entities["ent_substance_nh4cl"].pop("speciation_profiles")
    altered = replace(kb, entities=entities)

    result = infer_case(
        altered,
        compile_rules(altered),
        _case("missing-ammonium-speciation", "ent_substance_nh4cl"),
    )

    assert result["status"] == "invalid"
    assert result["diagnostic"]["code"] == "speciation_unavailable"
    assert result["diagnostic"]["details"]["target_id"] == "ent_substance_nh4cl"
    assert "candidate_key" not in result


def test_non_ammonium_salt_and_strong_base_do_not_fabricate_ammonia() -> None:
    kb = load_knowledge(ROOT)

    result = infer_case(kb, compile_rules(kb), _case("ordinary-salt", "ent_substance_nacl"))

    assert result["status"] == "indeterminate"
    assert "candidate_key" not in result


def test_m7_overlap_relationships_are_explicit_and_deterministic() -> None:
    overlaps = analyze_rule_overlaps(compile_rules(load_knowledge(ROOT)))
    by_pair = {frozenset(item["rule_ids"]): item for item in overlaps}

    assert by_pair[frozenset({RULE_ID, "rule_f2_strong_acid_base_neutralization"})]["relationships"] == [
        "mutually_exclusive_with"
    ]
    assert frozenset({RULE_ID, "rule_f2_agcl_precipitation"}) not in by_pair
    for acid_rule_id in (
        "rule_m5_strong_acid_hydrogen_carbonate_gas_evolution",
        "rule_m6_strong_acid_carbonate_gas_evolution",
    ):
        assert by_pair[frozenset({RULE_ID, acid_rule_id})]["relationships"] == ["mutually_exclusive_with"]


@pytest.mark.parametrize(("mode", "candidate_count"), [("unresolved", 0), ("ambiguous", 2)])
def test_m7_spectator_salt_resolution_never_fabricates_identity(mode: str, candidate_count: int) -> None:
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

    result = infer_case(altered, compile_rules(altered), _case(mode, "ent_substance_nh4cl"))

    assert result["status"] == "invalid"
    assert result["diagnostic"]["code"] == "product_unresolved"
    assert len(result["diagnostic"]["details"]["candidates"]) == candidate_count
    assert "candidate_key" not in result


def test_candidate_identity_includes_context_while_condition_match_allows_extra_context() -> None:
    kb = load_knowledge(ROOT)
    plans = compile_rules(kb)
    base = _case("base-context", "ent_substance_nh4cl")
    extra = copy.deepcopy(base)
    extra["id"] = "extra-context"
    extra["context"]["lab_scale"] = "small"

    first = infer_case(kb, plans, base)
    repeated = infer_case(kb, plans, base)
    with_extra = infer_case(kb, plans, extra)

    assert first["candidate_key"] == repeated["candidate_key"]
    assert first["candidate_key"] != with_extra["candidate_key"]
    assert first["canonical_match"]["state"] == "exact"
    assert with_extra["canonical_match"]["state"] == "exact"


def test_existing_teaching_view_maps_ammonium_chemistry_and_warmed_test() -> None:
    kb = load_knowledge(ROOT)
    view = kb.teaching_views["view_f3b_hs_aqueous_core"]
    by_path = {node["path_key"]: set(node.get("members", [])) for node in view["nodes"]}
    reactions = {
        "rxn_m7_nh4cl_naoh_ammonia_liberation",
        "rxn_m7_nh4_2so4_naoh_ammonia_liberation",
    }

    assert {"ent_substance_nh4cl", "ent_substance_nh4_2so4"} <= by_path[
        "D02/electrolyte-solutions/strong-electrolytes"
    ]
    assert reactions <= by_path["D03/reaction-types/gas-evolution"]
    assert reactions <= by_path["D05/chemical-experiments/ammonium-ion-identification"]
    assert reactions <= by_path["D06/notation/ionic-equations"]
    assert {"ent_substance_nh4cl", "ent_substance_nh4_2so4"} <= by_path[
        "D08/substance-classification/salts"
    ]
    assert {"ent_species_nh4_plus", "ent_substance_nh3"} <= by_path[
        "D10/elements-and-compounds/nitrogen-compounds"
    ]


def test_m7_does_not_create_ammonium_hydroxide_canonical_truth() -> None:
    kb = load_knowledge(ROOT)

    assert "ent_substance_nh4oh" not in kb.entities
    assert kb.semantic_key_candidates("formula.unit", "NH4OH") == ()


def test_audit_executes_m7_positive_unknown_and_contrast_cases(tmp_path: Path) -> None:
    audit = audit_repository(ROOT, tmp_path / "audit", "m7-fixture")
    results = {result["case_id"]: result for result in audit["results"]}

    for case_id in ("case_m7_nh4cl_naoh", "case_m7_nh4_2so4_naoh"):
        assert results[case_id]["status"] == "inferred"
        assert results[case_id]["rule_id"] == RULE_ID
        assert results[case_id]["canonical_match"]["state"] == "exact"
    assert results["case_m7_nh4cl_naoh_unknown_temperature"]["status"] == "indeterminate"
    assert "candidate_key" not in results["case_m7_nh4cl_naoh_unknown_temperature"]
    assert "candidate_key" not in results["case_m7_nacl_naoh_contrast"]
