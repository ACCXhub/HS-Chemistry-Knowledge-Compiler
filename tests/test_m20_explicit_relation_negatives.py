from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml

from compiler.build import ARTIFACT_FORMAT_VERSION, SUPPORTED_ARTIFACT_FORMAT_VERSIONS
from compiler.engine import infer_case
from compiler.rules import RULE_DSL_VERSION, RULE_PLAN_VERSION, compile_rules
from compiler.source import SOURCE_SCHEMA_VERSION, SourceError, load_knowledge


ROOT = Path(__file__).resolve().parents[1]
RULE_ID = "rule_m19_generic_aqueous_metal_salt_displacement"


def _copy(tmp_path: Path) -> Path:
    work = tmp_path / "repo"
    shutil.copytree(ROOT, work, ignore=shutil.ignore_patterns(".git", "build", "__pycache__", ".pytest_cache"))
    return work


def _entity(work: Path, entity_id: str) -> tuple[Path, dict, dict]:
    for path in sorted((work / "knowledge" / "domain").glob("*.yaml")):
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        entity = next((item for item in doc["records"] if item.get("id") == entity_id), None)
        if entity is not None:
            return path, doc, entity
    raise AssertionError(f"fixture entity not found: {entity_id}")


def _write(path: Path, doc: dict) -> None:
    path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")


def _assertion(target_id: str, truth: bool) -> dict:
    return {
        "relation_key": "metal.displaces_cation",
        "target_id": target_id,
        "truth": truth,
        "context": {"medium": "aqueous"},
        "evidence_ids": ["ev_f2_reactions"],
    }


def _case(case_id: str, metal_id: str, salt_id: str) -> dict:
    return {
        "id": case_id,
        "reactants": [
            {"target_id": metal_id, "phase": "solid"},
            {"target_id": salt_id, "phase": "aqueous"},
        ],
        "context": {"medium": "aqueous", "temperature_regime": "ambient"},
    }


def test_relation_truth_contract_resolves_true_false_and_absent(tmp_path: Path) -> None:
    work = _copy(tmp_path)
    path, doc, copper = _entity(work, "ent_substance_elemental_cu")
    copper["relation_assertions"] = [
        _assertion("ent_species_zn_2plus", False),
        _assertion("ent_species_ag_plus", True),
    ]
    _write(path, doc)

    kb = load_knowledge(work)
    known_false = kb.relation_fact(
        "ent_substance_elemental_cu",
        "metal.displaces_cation",
        "ent_species_zn_2plus",
        {"medium": "aqueous"},
    )
    known_true = kb.relation_fact(
        "ent_substance_elemental_cu",
        "metal.displaces_cation",
        "ent_species_ag_plus",
        {"medium": "aqueous"},
    )
    absent = kb.relation_fact(
        "ent_substance_elemental_cu",
        "metal.displaces_cation",
        "ent_species_mg_2plus",
        {"medium": "aqueous"},
    )

    assert (known_true.state.value, known_true.value) == ("known", True)
    assert (known_false.state.value, known_false.value) == ("known", False)
    assert known_false.relation_assertions[0]["truth"] is False
    assert (absent.state.value, absent.value) == ("absent", None)


def test_positive_target_resolution_excludes_explicit_negatives(tmp_path: Path) -> None:
    work = _copy(tmp_path)
    path, doc, zinc = _entity(work, "ent_substance_elemental_zn")
    zinc["relation_assertions"] = [
        _assertion("ent_species_na_plus", False),
        _assertion("ent_species_h_plus", False),
        {
            "relation_key": "metal.product_cation",
            "target_id": "ent_species_zn_2plus",
            "context": {"medium": "aqueous"},
            "evidence_ids": ["ev_f2_reactions"],
        },
    ]
    _write(path, doc)

    kb = load_knowledge(work)

    assert kb.relation_assertions(
        "ent_substance_elemental_zn",
        "metal.displaces_cation",
        {"medium": "aqueous"},
    ) == ()


def test_equal_context_positive_negative_contradiction_is_rejected(tmp_path: Path) -> None:
    work = _copy(tmp_path)
    path, doc, copper = _entity(work, "ent_substance_elemental_cu")
    copper["relation_assertions"] = [
        _assertion("ent_species_zn_2plus", True),
        _assertion("ent_species_zn_2plus", False),
    ]
    _write(path, doc)

    with pytest.raises(SourceError, match="contradictory contextual relation assertion") as exc:
        load_knowledge(work)

    assert exc.value.code == "schema_invalid"
    assert exc.value.stage == "source_load"


def test_duplicate_negative_is_rejected_but_one_target_cardinality_ignores_rejections(
    tmp_path: Path,
) -> None:
    duplicate_work = _copy(tmp_path / "duplicate")
    path, doc, copper = _entity(duplicate_work, "ent_substance_elemental_cu")
    copper["relation_assertions"] = [
        _assertion("ent_species_zn_2plus", False),
        _assertion("ent_species_zn_2plus", False),
    ]
    _write(path, doc)
    with pytest.raises(SourceError, match="duplicate contextual relation assertion"):
        load_knowledge(duplicate_work)

    cardinality_work = _copy(tmp_path / "cardinality")
    path, doc, zinc = _entity(cardinality_work, "ent_substance_elemental_zn")
    zinc["relation_assertions"] = [
        {
            **_assertion("ent_species_zn_2plus", True),
            "relation_key": "metal.product_cation",
        },
        {
            **_assertion("ent_species_na_plus", False),
            "relation_key": "metal.product_cation",
        },
        {
            **_assertion("ent_species_h_plus", False),
            "relation_key": "metal.product_cation",
        },
    ]
    _write(path, doc)

    kb = load_knowledge(cardinality_work)
    assert [
        item["target_id"]
        for item in kb.relation_assertions(
            "ent_substance_elemental_zn",
            "metal.product_cation",
            {"medium": "aqueous"},
        )
    ] == ["ent_species_zn_2plus"]


def test_dynamic_m19_target_distinguishes_false_from_unknown() -> None:
    kb = load_knowledge(ROOT)
    plans = compile_rules(kb)

    known_false = infer_case(
        kb,
        plans,
        _case(
            "m20-cu-znso4",
            "ent_substance_elemental_cu",
            "ent_substance_znso4",
        ),
    )
    unknown = infer_case(
        kb,
        plans,
        _case(
            "m20-cu-mgso4",
            "ent_substance_elemental_cu",
            "ent_substance_mgso4",
        ),
    )

    false_event = next(
        item
        for item in known_false["proof_trace"]
        if item.get("rule_id") == RULE_ID and item.get("subject") == "relation"
    )
    unknown_event = next(
        item
        for item in unknown["proof_trace"]
        if item.get("rule_id") == RULE_ID and item.get("subject") == "relation"
    )
    assert known_false["status"] == "no_match"
    assert known_false["diagnostic"]["code"] == "no_rule_match"
    assert "candidate_key" not in known_false
    assert false_event["truth"] == "FALSE"
    assert false_event["knowledge_state"] == "known"
    assert false_event["target_id"] == "ent_species_zn_2plus"
    assert false_event["relation_assertions"][0]["truth"] is False
    assert "ev_m20_copper_zinc_non_displacement" in false_event["evidence_ids"]

    assert unknown["status"] == "indeterminate"
    assert unknown_event["truth"] == "UNKNOWN"
    assert unknown_event["knowledge_state"] == "absent"
    assert unknown_event["relation_assertions"] == []


def test_m20_source_version_only_advances_source_contract() -> None:
    assert SOURCE_SCHEMA_VERSION == "3.7.0"
    assert RULE_DSL_VERSION == "1.4.0"
    assert RULE_PLAN_VERSION == "1.4.0"
    assert ARTIFACT_FORMAT_VERSION == "1.5.0"
    assert SUPPORTED_ARTIFACT_FORMAT_VERSIONS == frozenset(
        {"1.0.0", "1.1.0", "1.2.0", "1.3.0", "1.4.0", "1.5.0"}
    )
