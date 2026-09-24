from __future__ import annotations

import copy
import json
import shutil
from dataclasses import replace
from pathlib import Path

import pytest
import yaml

from compiler.build import (
    ARTIFACT_FORMAT_VERSION,
    SUPPORTED_ARTIFACT_FORMAT_VERSIONS,
    artifact_versions,
    validate_artifact_manifest,
)
from compiler.engine import compare_canonical_reactions, infer_case
from compiler.rules import compile_rules
from compiler.source import SOURCE_SCHEMA_VERSION, SourceError, load_cases, load_knowledge


ROOT = Path(__file__).resolve().parents[1]


def _add_conditions(work: Path, conditions: list[dict]) -> str:
    path = work / "knowledge" / "domain" / "m6_carbonate_reactions.yaml"
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    reaction = document["records"][0]
    reaction["conditions"] = conditions
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    return reaction["id"]


def test_reaction_conditions_are_validated_embedded_values_and_old_records_remain_compatible(tmp_path: Path) -> None:
    work = tmp_path / "repo"
    shutil.copytree(ROOT, work, ignore=shutil.ignore_patterns(".git", "build", "__pycache__", ".pytest_cache"))
    reaction_id = _add_conditions(
        work,
        [
            {
                "key": "medium",
                "value": "aqueous",
                "evidence_ids": ["ev_f3b_carbonate_acid"],
            },
            {
                "key": "temperature_regime",
                "value": "warmed",
                "evidence_ids": ["ev_f3b_carbonate_acid"],
            },
        ],
    )

    kb = load_knowledge(work)

    assert SOURCE_SCHEMA_VERSION == "3.7.0"
    assert kb.reactions[reaction_id]["conditions"] == [
        {"key": "medium", "value": "aqueous", "evidence_ids": ["ev_f3b_carbonate_acid"]},
        {
            "key": "temperature_regime",
            "value": "warmed",
            "evidence_ids": ["ev_f3b_carbonate_acid"],
        },
    ]
    assert kb.reactions["rxn_m6_hno3_na2co3_gas_evolution"].get("conditions", []) == []


def test_duplicate_reaction_condition_keys_are_rejected(tmp_path: Path) -> None:
    work = tmp_path / "repo"
    shutil.copytree(ROOT, work, ignore=shutil.ignore_patterns(".git", "build", "__pycache__", ".pytest_cache"))
    _add_conditions(
        work,
        [
            {"key": "medium", "value": "aqueous", "evidence_ids": ["ev_f3b_carbonate_acid"]},
            {"key": "medium", "value": "aqueous", "evidence_ids": ["ev_f3b_carbonate_acid"]},
        ],
    )

    with pytest.raises(SourceError, match="duplicate reaction condition"):
        load_knowledge(work)


def test_reaction_condition_authoring_order_is_not_semantic(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    shutil.copytree(ROOT, first, ignore=shutil.ignore_patterns(".git", "build", "__pycache__", ".pytest_cache"))
    shutil.copytree(ROOT, second, ignore=shutil.ignore_patterns(".git", "build", "__pycache__", ".pytest_cache"))
    conditions = [
        {"key": "medium", "value": "aqueous", "evidence_ids": ["ev_f3b_carbonate_acid"]},
        {
            "key": "temperature_regime",
            "value": "warmed",
            "evidence_ids": ["ev_f3b_carbonate_acid"],
        },
    ]
    reaction_id = _add_conditions(first, conditions)
    _add_conditions(second, list(reversed(conditions)))

    first_kb = load_knowledge(first)
    second_kb = load_knowledge(second)

    assert first_kb.reactions[reaction_id]["conditions"] == second_kb.reactions[reaction_id]["conditions"]
    assert first_kb.source_digest == second_kb.source_digest


def _conditioned_neutralization_kb(*, duplicate: bool = False):
    kb = load_knowledge(ROOT)
    reactions = copy.deepcopy(kb.reactions)
    reaction = reactions["rxn_hcl_naoh_neutralization"]
    reaction["conditions"] = [
        {
            "key": "temperature_regime",
            "value": "warmed",
            "evidence_ids": ["ev_f3b_strong_acid_base"],
        }
    ]
    if duplicate:
        duplicate_reaction = copy.deepcopy(reaction)
        duplicate_reaction["id"] = "rxn_fixture_hcl_naoh_warmed_duplicate"
        reactions[duplicate_reaction["id"]] = duplicate_reaction
    return replace(kb, reactions=reactions)


def _neutralization_case(context: dict) -> dict:
    return {
        "id": "conditioned-neutralization",
        "reactants": [
            {"target_id": "ent_substance_hcl", "phase": "aqueous"},
            {"target_id": "ent_substance_naoh", "phase": "aqueous"},
        ],
        "context": context,
    }


def test_canonical_comparison_filters_by_required_conditions_and_accepts_extra_context() -> None:
    kb = _conditioned_neutralization_kb()

    compatible = infer_case(
        kb,
        compile_rules(kb),
        _neutralization_case(
            {"medium": "aqueous", "temperature_regime": "warmed", "lab_scale": "small"}
        ),
    )
    participants = kb.reactions["rxn_hcl_naoh_neutralization"]["participants"]
    missing = compare_canonical_reactions(kb, participants, {"medium": "aqueous"})
    conflicting = compare_canonical_reactions(
        kb,
        participants,
        {"medium": "aqueous", "temperature_regime": "ambient"},
    )

    assert compatible["canonical_match"]["state"] == "exact"
    assert compatible["canonical_match"]["reaction_ids"] == ["rxn_hcl_naoh_neutralization"]
    assert compatible["canonical_match"]["condition_evidence_ids"] == ["ev_f3b_strong_acid_base"]
    assert missing["state"] == "none"
    assert conflicting["state"] == "none"
    for comparison, reason in ((missing, "missing"), (conflicting, "conflicting")):
        assert comparison["condition_compatibility"] == [
            {
                "reaction_id": "rxn_hcl_naoh_neutralization",
                "state": "incompatible",
                "unsatisfied": [
                    {
                        "key": "temperature_regime",
                        "required": "warmed",
                        "actual": None if reason == "missing" else "ambient",
                        "reason": reason,
                        "evidence_ids": ["ev_f3b_strong_acid_base"],
                    }
                ],
            }
        ]


def test_multiple_condition_compatible_canonical_reactions_remain_conflict() -> None:
    kb = _conditioned_neutralization_kb(duplicate=True)
    base = kb.reactions["rxn_hcl_naoh_neutralization"]["participants"]

    comparison = compare_canonical_reactions(
        kb,
        base,
        {"medium": "aqueous", "temperature_regime": "warmed"},
    )

    assert comparison["state"] == "conflict"
    assert comparison["reaction_ids"] == [
        "rxn_fixture_hcl_naoh_warmed_duplicate",
        "rxn_hcl_naoh_neutralization",
    ]


def test_m7_condition_contract_remains_compatible_with_current_versions() -> None:
    assert artifact_versions() == {
        "source_schema": "3.7.0",
        "rule_dsl": "1.4.0",
        "rule_plan": "1.4.0",
        "artifact_format": "1.5.0",
    }
    assert ARTIFACT_FORMAT_VERSION == "1.5.0"
    assert SUPPORTED_ARTIFACT_FORMAT_VERSIONS == frozenset(
        {"1.0.0", "1.1.0", "1.2.0", "1.3.0", "1.4.0", "1.5.0"}
    )
    validate_artifact_manifest({"versions": {"artifact_format": "1.0.0"}})
    validate_artifact_manifest({"versions": {"artifact_format": "1.1.0"}})
    validate_artifact_manifest({"versions": {"artifact_format": "1.2.0"}})
    validate_artifact_manifest({"versions": {"artifact_format": "1.3.0"}})
    schema = json.loads((ROOT / "schemas" / "knowledge-record.schema.json").read_text(encoding="utf-8"))
    assert schema["x-source-schema-version"] == "3.7.0"
