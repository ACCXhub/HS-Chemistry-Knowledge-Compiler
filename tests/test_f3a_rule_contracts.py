from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml

from compiler.build import ARTIFACT_FORMAT_VERSION, compile_repository, validate_artifact_manifest
from compiler.engine import infer_case
from compiler.predicates import compile_predicate, evaluate_predicate
from compiler.reaction_forms import project_reaction_form
from compiler.rules import analyze_rule_overlaps, compile_rules
from compiler.source import SourceError, load_knowledge


ROOT = Path(__file__).resolve().parents[1]


def _copy(tmp_path: Path) -> Path:
    work = tmp_path / "repo"
    shutil.copytree(ROOT, work)
    return work


def _append_rules(work: Path, records: list[dict]) -> None:
    path = work / "knowledge" / "rules" / "extra.yaml"
    path.write_text(yaml.safe_dump({"records": records}, sort_keys=False), encoding="utf-8")


def _rule(rule_id: str, *, required: list[str], product: str, **relations: object) -> dict:
    record = {
        "id": rule_id,
        "record_type": "rule",
        "version": "1.0.0",
        "decision_domain": "overlap_fixture",
        "match": {
            "reactants": [
                {"bind": "left", "entity_kind": "substance", "required_facets": required},
                {"bind": "right", "entity_kind": "substance"},
            ]
        },
        "context": {"medium": "aqueous"},
        "products": [{"target_id": product, "phase": "liquid" if product == "ent_substance_h2o" else "aqueous"}],
        "validators": ["atoms_conserved", "charge_conserved"],
        "evidence_ids": ["ev_f2_reactions"],
    }
    record.update(relations)
    return record


def test_generic_facet_based_participant_rule_matching() -> None:
    kb = load_knowledge(ROOT)
    plans = compile_rules(kb)
    plan = next(plan for plan in plans if plan.rule_id == "rule_f2_agcl_precipitation")
    assert all(pattern.target_id is None for pattern in plan.patterns)
    case = {
        "id": "generic_case",
        "reactants": [
            {"target_id": "ent_substance_agno3", "phase": "aqueous"},
            {"target_id": "ent_substance_nacl", "phase": "aqueous"},
        ],
        "context": {"medium": "aqueous", "temperature_regime": "ambient"},
    }
    result = infer_case(kb, plans, case)
    assert result["status"] == "inferred"
    assert result["candidate_key"]
    assert result["canonical_match"]["reaction_ids"] == ["rxn_agcl_precipitation"]


def test_unknown_predicate_behavior_distinguishes_absent() -> None:
    kb = load_knowledge(ROOT)
    predicate = compile_predicate(
        {"operator": "equals", "subject": "context", "key": "pressure", "expected": "high"}, set()
    )
    truth, fact = evaluate_predicate(predicate, kb, {}, {})
    assert truth.value == "UNKNOWN"
    assert fact.state.value == "absent"
    assert fact.origin == "contextual"


def test_typed_predicate_validation_and_invalid_argument_rejection() -> None:
    predicate = compile_predicate(
        {"operator": "in_set", "subject": "context", "key": "medium", "expected": ["aqueous", "gas"]}, set()
    )
    assert predicate.operator == "in_set"
    with pytest.raises(SourceError, match="requires scalar expected"):
        compile_predicate(
            {"operator": "equals", "subject": "context", "key": "medium", "expected": ["aqueous"]}, set()
        )
    with pytest.raises(SourceError, match="does not accept expected"):
        compile_predicate(
            {"operator": "is_known", "subject": "context", "key": "medium", "expected": True}, set()
        )


def test_overlap_detection_and_unresolved_overlap_is_compile_error(tmp_path: Path) -> None:
    work = _copy(tmp_path)
    _append_rules(
        work,
        [
            _rule("rule_overlap_general", required=[], product="ent_substance_h2o"),
            _rule("rule_overlap_specific", required=["acid.strong_in_water"], product="ent_substance_nacl"),
        ],
    )
    kb = load_knowledge(work)
    with pytest.raises(SourceError) as exc:
        compile_rules(kb)
    assert exc.value.code == "rule_overlap_compile_error"
    assert {"rule_overlap_general", "rule_overlap_specific"} <= set(str(exc.value).split()) or "rule_overlap_general" in str(exc.value)


def test_explicit_specialization_resolves_overlap(tmp_path: Path) -> None:
    work = _copy(tmp_path)
    _append_rules(
        work,
        [
            _rule("rule_overlap_general", required=[], product="ent_substance_h2o"),
            _rule(
                "rule_overlap_specific",
                required=["acid.strong_in_water"],
                product="ent_substance_nacl",
                specializes=["rule_overlap_general"],
            ),
        ],
    )
    plans = compile_rules(load_knowledge(work))
    overlaps = analyze_rule_overlaps(plans)
    item = next(item for item in overlaps if "rule_overlap_general" in item["rule_ids"])
    assert item["relationships"] == ["specializes"]


def test_resolution_cycle_rejected(tmp_path: Path) -> None:
    work = _copy(tmp_path)
    _append_rules(
        work,
        [
            _rule("rule_cycle_a", required=[], product="ent_substance_h2o", overrides=["rule_cycle_b"]),
            _rule("rule_cycle_b", required=["acid.strong_in_water"], product="ent_substance_nacl", overrides=["rule_cycle_a"]),
        ],
    )
    with pytest.raises(SourceError, match="resolution cycle") as exc:
        compile_rules(load_knowledge(work))
    assert exc.value.stage == "rule_resolution_graph"


def test_rule_file_order_independence(tmp_path: Path) -> None:
    work = _copy(tmp_path)
    original = compile_rules(load_knowledge(work))
    rule_file = work / "knowledge" / "rules" / "f2_rules.yaml"
    doc = yaml.safe_load(rule_file.read_text(encoding="utf-8"))
    doc["records"] = list(reversed(doc["records"]))
    rule_file.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
    reordered = compile_rules(load_knowledge(work))
    assert [plan.rule_id for plan in original] == [plan.rule_id for plan in reordered]
    assert original == reordered


def test_reaction_form_projection_preserves_identity_and_uses_assumptions() -> None:
    kb = load_knowledge(ROOT)
    required = {"aqueous_medium", "strong_electrolyte_dissociation", "insoluble_precipitate_intact"}
    projection = project_reaction_form(kb, "rxn_agcl_precipitation", "net_ionic", required)
    assert projection is not None
    assert projection["reaction_id"] == "rxn_agcl_precipitation"
    assert projection["form_key"] == "net_ionic"
    assert project_reaction_form(
        kb,
        "rxn_agcl_precipitation",
        "net_ionic",
        {"aqueous_medium", "strong_electrolyte_dissociation"},
    ) is None


def test_artifact_version_emitted_and_validated(tmp_path: Path) -> None:
    manifest = compile_repository(ROOT, tmp_path / "out", "fixture-revision")
    assert manifest["versions"] == {
        "source_schema": "3.1.0",
        "rule_dsl": "1.0.0",
        "rule_plan": "1.0.0",
        "artifact_format": ARTIFACT_FORMAT_VERSION,
    }
    validate_artifact_manifest(manifest)
    incompatible = {**manifest, "versions": {**manifest["versions"], "artifact_format": "999.0.0"}}
    with pytest.raises(ValueError, match="unsupported artifact format"):
        validate_artifact_manifest(incompatible)


def test_diagnostics_are_structured() -> None:
    kb = load_knowledge(ROOT)
    plans = compile_rules(kb)
    case = {
        "id": "unknown_input",
        "reactants": [{"target_id": "ent_missing", "phase": "aqueous"}],
        "context": {},
    }
    result = infer_case(kb, plans, case)
    assert result["diagnostic"]["code"] == "reference_unresolved"
    assert result["diagnostic"]["stage"] == "input_resolution"
    assert isinstance(result["diagnostic"]["message"], str)


def test_ordinary_new_rule_fixture_requires_no_engine_change(tmp_path: Path) -> None:
    work = _copy(tmp_path)
    engine_before = (work / "compiler" / "engine.py").read_bytes()
    _append_rules(
        work,
        [
            {
                "id": "rule_fixture_ionic_precipitation",
                "record_type": "rule",
                "version": "1.0.0",
                "decision_domain": "ionic_fixture",
                "match": {
                    "reactants": [
                        {"bind": "cation", "target_id": "ent_species_ag_plus", "species_kind": "ion"},
                        {"bind": "anion", "target_id": "ent_species_cl_minus", "species_kind": "ion"},
                    ]
                },
                "products": [{"target_id": "ent_substance_agcl", "phase": "solid"}],
                "validators": ["atoms_conserved", "charge_conserved"],
                "evidence_ids": ["ev_f2_reactions"],
            }
        ],
    )
    kb = load_knowledge(work)
    plans = compile_rules(kb)
    result = infer_case(
        kb,
        plans,
        {
            "id": "ionic_fixture",
            "reactants": [
                {"target_id": "ent_species_ag_plus", "phase": "dissolved"},
                {"target_id": "ent_species_cl_minus", "phase": "dissolved"},
            ],
            "context": {},
        },
    )
    assert result["status"] == "inferred"
    assert (work / "compiler" / "engine.py").read_bytes() == engine_before


def test_old_exact_case_semantics_survive_generic_pattern() -> None:
    kb = load_knowledge(ROOT)
    plans = compile_rules(kb)
    result = infer_case(
        kb,
        plans,
        {
            "id": "architecture_test",
            "reactants": [
                {"target_id": "ent_substance_nacl", "phase": "aqueous"},
                {"target_id": "ent_substance_agno3", "phase": "aqueous"},
            ],
            "context": {"medium": "aqueous", "temperature_regime": "ambient"},
        },
    )
    assert result["rule_id"] == "rule_f2_agcl_precipitation"
    assert result["canonical_match"]["reaction_ids"] == ["rxn_agcl_precipitation"]


def test_fact_states_distinguish_known_false_unknown_not_applicable_and_absent(tmp_path: Path) -> None:
    work = _copy(tmp_path)
    path = work / "knowledge" / "domain" / "f2_entities.yaml"
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    entity = next(record for record in doc["records"] if record.get("id") == "ent_substance_nacl")
    entity["facet_assertions"].extend(
        [
            {"facet_key": "fixture.false", "value_state": "known", "value": False, "fact_kind": "intrinsic"},
            {"facet_key": "fixture.unknown", "value_state": "unknown", "value": None, "fact_kind": "derived"},
            {"facet_key": "fixture.na", "value_state": "not_applicable", "value": None, "fact_kind": "intrinsic"},
        ]
    )
    path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
    kb = load_knowledge(work)
    assert kb.facet_fact("ent_substance_nacl", "fixture.false").value is False
    assert kb.facet_fact("ent_substance_nacl", "fixture.false").state.value == "known"
    assert kb.facet_fact("ent_substance_nacl", "fixture.unknown").state.value == "unknown"
    assert kb.facet_fact("ent_substance_nacl", "fixture.unknown").origin == "derived"
    assert kb.facet_fact("ent_substance_nacl", "fixture.na").state.value == "not_applicable"
    assert kb.facet_fact("ent_substance_nacl", "fixture.absent").state.value == "absent"


def test_simple_context_constraints_can_prove_rules_disjoint(tmp_path: Path) -> None:
    work = _copy(tmp_path)
    left = _rule("rule_context_a", required=[], product="ent_substance_h2o")
    right = _rule("rule_context_b", required=[], product="ent_substance_nacl")
    left["context"] = {"medium": "aqueous"}
    right["context"] = {"medium": "gas"}
    _append_rules(work, [left, right])
    plans = compile_rules(load_knowledge(work))
    assert not any(set(item["rule_ids"]) == {"rule_context_a", "rule_context_b"} for item in analyze_rule_overlaps(plans))
