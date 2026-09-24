from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml

from compiler.predicates import compile_predicate, evaluate_predicate
from compiler.rules import compile_rules
from compiler.source import SourceError, load_knowledge


ROOT = Path(__file__).resolve().parents[1]


def _copy(tmp_path: Path) -> Path:
    work = tmp_path / "repo"
    shutil.copytree(ROOT, work, ignore=shutil.ignore_patterns(".git", "build", "__pycache__", ".pytest_cache"))
    return work


def _append_displacement_relation(work: Path, *, target_id: str = "ent_species_na_plus") -> None:
    path = work / "knowledge" / "domain" / "m10_metal_entities.yaml"
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    zinc = next(record for record in doc["records"] if record.get("id") == "ent_substance_elemental_zn")
    zinc.setdefault("relation_assertions", []).append(
        {
            "relation_key": "metal.displaces_cation",
            "target_id": target_id,
            "context": {"medium": "aqueous"},
            "evidence_ids": ["ev_f2_reactions"],
        }
    )
    path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")


def _relation_predicate(*, target_id: str = "ent_species_na_plus") -> dict:
    return {
        "operator": "equals",
        "subject": "relation",
        "binding": "metal",
        "key": "metal.displaces_cation",
        "target_id": target_id,
        "expected": True,
    }


def _append_rule(work: Path, predicate: dict) -> None:
    path = work / "knowledge" / "rules" / "m12_relation_fixture.yaml"
    path.write_text(
        yaml.safe_dump(
            {
                "records": [
                    {
                        "id": "rule_m12_relation_fixture",
                        "record_type": "rule",
                        "version": "1.0.0",
                        "decision_domain": "m12_relation_fixture",
                        "match": {
                            "reactants": [
                                {
                                    "bind": "metal",
                                    "target_id": "ent_substance_elemental_zn",
                                    "phase": "solid",
                                },
                                {
                                    "bind": "other",
                                    "target_id": "ent_substance_hcl",
                                    "phase": "aqueous",
                                },
                            ]
                        },
                        "context": {"medium": "aqueous"},
                        "predicates": [predicate],
                        "products": [{"target_id": "ent_substance_h2", "phase": "gas"}],
                        "validators": ["atoms_conserved", "charge_conserved"],
                        "evidence_ids": ["ev_f2_reactions"],
                    }
                ]
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )


def test_relation_predicate_lowers_exact_target_and_evaluates_known_true(tmp_path: Path) -> None:
    work = _copy(tmp_path)
    _append_displacement_relation(work)
    kb = load_knowledge(work)

    predicate = compile_predicate(_relation_predicate(), {"metal"})
    truth, fact = evaluate_predicate(
        predicate,
        kb,
        {"metal": "ent_substance_elemental_zn"},
        {"medium": "aqueous", "temperature_regime": "ambient"},
    )

    assert predicate.target_id == "ent_species_na_plus"
    assert truth.value == "TRUE"
    assert fact.state.value == "known"
    assert fact.value is True
    assert fact.origin == "contextual_relation"
    assert fact.context == (("medium", "aqueous"),)
    assert fact.evidence_ids == ("ev_f2_reactions",)
    assert fact.relation_assertions == (
        {
            "source_id": "ent_substance_elemental_zn",
            "relation_key": "metal.displaces_cation",
            "target_id": "ent_species_na_plus",
            "context": {"medium": "aqueous"},
            "evidence_ids": ["ev_f2_reactions"],
        },
    )


@pytest.mark.parametrize(
    ("target_id", "context"),
    [
        ("ent_species_h_plus", {"medium": "aqueous"}),
        ("ent_species_na_plus", {"medium": "gas"}),
    ],
)
def test_relation_predicate_absence_or_wrong_context_remains_unknown(
    tmp_path: Path,
    target_id: str,
    context: dict,
) -> None:
    work = _copy(tmp_path)
    _append_displacement_relation(work)
    kb = load_knowledge(work)
    predicate = compile_predicate(_relation_predicate(target_id=target_id), {"metal"})

    first = evaluate_predicate(predicate, kb, {"metal": "ent_substance_elemental_zn"}, context)
    second = evaluate_predicate(predicate, kb, {"metal": "ent_substance_elemental_zn"}, context)

    assert first == second
    truth, fact = first
    assert truth.value == "UNKNOWN"
    assert fact.state.value == "absent"
    assert fact.relation_assertions == ()


def test_relation_predicate_requires_one_valid_binding_one_target_source_and_true_equals() -> None:
    with pytest.raises(SourceError, match="requires one valid binding"):
        compile_predicate(_relation_predicate(), {"other"})
    with pytest.raises(SourceError, match="requires exactly one target_id or target_source"):
        compile_predicate({key: value for key, value in _relation_predicate().items() if key != "target_id"}, {"metal"})
    with pytest.raises(SourceError, match="requires exactly one target_id or target_source"):
        compile_predicate(
            {
                **_relation_predicate(),
                "target_source": {"kind": "exact_entity", "target_id": "ent_species_cu_2plus"},
            },
            {"metal"},
        )
    with pytest.raises(SourceError, match="supports only equals expected true"):
        compile_predicate({**_relation_predicate(), "expected": False}, {"metal"})
    with pytest.raises(SourceError, match="unsupported relation predicate key"):
        compile_predicate({**_relation_predicate(), "key": "fixture.invalid"}, {"metal"})


def test_rule_relation_predicate_target_must_resolve(tmp_path: Path) -> None:
    work = _copy(tmp_path)
    _append_rule(work, _relation_predicate(target_id="ent_missing_species"))

    with pytest.raises(SourceError) as exc:
        load_knowledge(work)

    assert exc.value.code == "reference_unresolved"
    assert exc.value.stage == "reference_validation"
    assert exc.value.details == {
        "relation_key": "metal.displaces_cation",
        "target_id": "ent_missing_species",
        "target_kind": "species",
    }


def test_rule_relation_predicate_compiles_to_typed_plan(tmp_path: Path) -> None:
    work = _copy(tmp_path)
    _append_displacement_relation(work)
    _append_rule(work, _relation_predicate())

    plan = next(plan for plan in compile_rules(load_knowledge(work)) if plan.rule_id == "rule_m12_relation_fixture")
    predicate = next(predicate for predicate in plan.predicates if predicate.subject == "relation")

    assert predicate.binding == "metal"
    assert predicate.key == "metal.displaces_cation"
    assert predicate.target_id == "ent_species_na_plus"
    assert predicate.expected is True
