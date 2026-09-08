from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from compiler.balance import balance, validate_conservation
from compiler.build import audit_repository, tree_digest, validate
from compiler.engine import infer_case
from compiler.rules import compile_rules
from compiler.source import SourceError, load_cases, load_knowledge


ROOT = Path(__file__).resolve().parents[1]


def _results() -> dict[str, dict]:
    kb = load_knowledge(ROOT)
    plans = compile_rules(kb)
    return {case["id"]: infer_case(kb, plans, case) for case in load_cases(ROOT)}


def test_schema_rejects_invalid_fixture(tmp_path: Path) -> None:
    work = tmp_path / "repo"
    shutil.copytree(ROOT, work)
    bad = work / "knowledge" / "domain" / "bad.yaml"
    bad.write_text("records:\n  - id: broken\n    record_type: entity\n", encoding="utf-8")
    with pytest.raises(SourceError, match="schema validation failed"):
        load_knowledge(work)


def test_reference_resolution_and_validation_summary() -> None:
    summary = validate(ROOT)
    assert summary["record_count"] > 0
    assert summary["rule_count"] == 6
    assert summary["case_count"] == 20


def test_three_valued_unknown_is_not_false() -> None:
    result = _results()["case_unknown_medium"]
    assert result["status"] == "indeterminate"
    predicate_events = [event for event in result["proof_trace"] if event["event"] == "predicate.eval"]
    assert any(event["truth"] == "UNKNOWN" for event in predicate_events)


def test_precipitation_inference_and_canonical_comparison() -> None:
    result = _results()["case_precipitation"]
    assert result["status"] == "inferred"
    assert result["canonical_match"]["state"] == "exact"
    assert result["canonical_match"]["reaction_ids"] == ["rxn_agcl_precipitation"]
    assert result["canonical_match"]["reaction_forms"]["rxn_agcl_precipitation"] == ["net_ionic"]


def test_acid_base_inference() -> None:
    result = _results()["case_neutralization"]
    assert result["status"] == "inferred"
    assert result["rule_id"] == "rule_f2_strong_acid_base_neutralization"
    assert result["canonical_match"]["reaction_ids"] == ["rxn_hcl_naoh_neutralization"]


def test_declared_blocker_is_explicit() -> None:
    result = _results()["case_blocked_frozen"]
    assert result["status"] == "blocked"
    assert any(
        event["event"] == "blocker.checked" and event["truth"] == "TRUE"
        for event in result["proof_trace"]
    )


def test_exact_balancing_for_molecular_and_ionic_cases() -> None:
    kb = load_knowledge(ROOT)
    molecular = balance(
        kb,
        ("ent_substance_nacl", "ent_substance_agno3"),
        ("ent_substance_agcl", "ent_substance_nano3"),
    )
    assert molecular.coefficients == (1, 1, 1, 1)
    ionic = balance(
        kb,
        ("ent_species_ag_plus", "ent_species_cl_minus"),
        ("ent_substance_agcl",),
    )
    assert ionic.coefficients == (1, 1, 1)


def test_atom_and_charge_conservation() -> None:
    kb = load_knowledge(ROOT)
    ionic = balance(
        kb,
        ("ent_species_ag_plus", "ent_species_cl_minus"),
        ("ent_substance_agcl",),
    )
    atoms_ok, charge_ok = validate_conservation(
        kb,
        ("ent_species_ag_plus", "ent_species_cl_minus"),
        ("ent_substance_agcl",),
        ionic,
    )
    assert atoms_ok is True
    assert charge_ok is True


def test_candidate_key_is_deterministic_and_has_no_review_uuid() -> None:
    first = _results()["case_precipitation"]
    second = _results()["case_precipitation"]
    assert first["candidate_key"] == second["candidate_key"]
    assert first["candidate_key"].startswith("cand_sha256_")
    assert "id" not in first


def test_repeated_audit_build_is_byte_stable(tmp_path: Path) -> None:
    out_a = tmp_path / "a"
    out_b = tmp_path / "b"
    audit_repository(ROOT, out_a, "eeff560b176b4d4b0cb45aec663413325ac39232")
    audit_repository(ROOT, out_b, "eeff560b176b4d4b0cb45aec663413325ac39232")
    assert tree_digest(out_a) == tree_digest(out_b)
    for name in ("reaction-candidates.json", "diagnostics.json", "manifest.json"):
        assert (out_a / name).read_bytes() == (out_b / name).read_bytes()


def test_proof_trace_contains_required_stages() -> None:
    result = _results()["case_precipitation"]
    events = [event["event"] for event in result["proof_trace"]]
    required = [
        "input.normalized",
        "refs.resolved",
        "knowledge.resolved",
        "rule.match",
        "predicate.eval",
        "blocker.checked",
        "products.constructed",
        "products.resolved",
        "balance.completed",
        "validation.atoms",
        "validation.charge",
        "canonical.compare",
        "candidate.emitted",
    ]
    for stage in required:
        assert stage in events


def test_file_traversal_order_does_not_change_semantic_output(tmp_path: Path) -> None:
    work = tmp_path / "repo"
    shutil.copytree(ROOT, work)
    original = audit_repository(ROOT, tmp_path / "original", "same-revision")
    domain = work / "knowledge" / "domain"
    (domain / "f2_entities.yaml").rename(domain / "z_entities.yaml")
    (domain / "f2_reactions.yaml").rename(domain / "a_reactions.yaml")
    reordered = audit_repository(work, tmp_path / "reordered", "same-revision")
    assert original["manifest"]["source_semantic_digest"] == reordered["manifest"]["source_semantic_digest"]
    assert (tmp_path / "original" / "reaction-candidates.json").read_bytes() == (
        tmp_path / "reordered" / "reaction-candidates.json"
    ).read_bytes()


def test_input_reactant_order_does_not_change_candidate() -> None:
    kb = load_knowledge(ROOT)
    plans = compile_rules(kb)
    case = next(case for case in load_cases(ROOT) if case["id"] == "case_precipitation")
    reversed_case = {**case, "reactants": list(reversed(case["reactants"]))}
    first = infer_case(kb, plans, case)
    second = infer_case(kb, plans, reversed_case)
    assert first["candidate_key"] == second["candidate_key"]
    assert first["participants"] == second["participants"]


def test_reaction_form_is_not_a_duplicate_reaction_identity() -> None:
    kb = load_knowledge(ROOT)
    reaction = kb.reactions["rxn_agcl_precipitation"]
    assert [form["form_key"] for form in reaction["forms"]] == ["net_ionic"]
    assert "id" not in reaction["forms"][0]
