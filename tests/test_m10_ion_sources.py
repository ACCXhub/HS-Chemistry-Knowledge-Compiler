from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
import yaml

from compiler.build import (
    ARTIFACT_FORMAT_VERSION,
    SUPPORTED_ARTIFACT_FORMAT_VERSIONS,
    artifact_versions,
    compile_repository,
)
from compiler.products import ProductResolutionError, resolve_product_detail
from compiler.rules import RULE_DSL_VERSION, RULE_PLAN_VERSION, compile_rules
from compiler.source import SOURCE_SCHEMA_VERSION, load_knowledge


ROOT = Path(__file__).resolve().parents[1]


def _copy(tmp_path: Path) -> Path:
    work = tmp_path / "repo"
    shutil.copytree(ROOT, work)
    return work


def _set_source_relations(work: Path, assertions: list[dict]) -> None:
    path = work / "knowledge" / "domain" / "m9_thiosulfate_entities.yaml"
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    source = next(record for record in doc["records"] if record.get("id") == "ent_substance_na2s2o3")
    source["relation_assertions"] = assertions
    path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")


def _append_typed_rule(work: Path) -> None:
    rule = {
        "id": "rule_fixture_relation_ionic_pair",
        "record_type": "rule",
        "version": "1.0.0",
        "decision_domain": "relation_ionic_pair_fixture",
        "match": {
            "reactants": [
                {"bind": "metal", "target_id": "ent_substance_na2s2o3"},
                {"bind": "acid", "target_id": "ent_substance_hcl"},
            ]
        },
        "products": [
            {
                "phase": "aqueous",
                "construct": {
                    "kind": "ionic_pair",
                    "cation_source": {
                        "kind": "relation_target",
                        "binding": "metal",
                        "relation_key": "metal.product_cation",
                    },
                    "anion_source": {"kind": "speciation", "binding": "acid"},
                },
            }
        ],
        "validators": ["atoms_conserved", "charge_conserved"],
        "evidence_ids": ["ev_f2_reactions"],
    }
    path = work / "knowledge" / "rules" / "m10_relation_fixture.yaml"
    path.write_text(yaml.safe_dump({"records": [rule]}, sort_keys=False), encoding="utf-8")


def _fixture_plan(work: Path):
    plans = compile_rules(load_knowledge(work))
    return next(plan for plan in plans if plan.rule_id == "rule_fixture_relation_ionic_pair")


def test_typed_ion_sources_lower_and_legacy_ionic_pair_syntax_stays_compatible(tmp_path: Path) -> None:
    work = _copy(tmp_path)
    _append_typed_rule(work)

    typed = _fixture_plan(work).products[0]
    assert typed.cation_source.kind == "relation_target"
    assert typed.cation_source.binding == "metal"
    assert typed.cation_source.relation_key == "metal.product_cation"
    assert typed.anion_source.kind == "speciation"
    assert typed.anion_source.binding == "acid"
    assert typed.cation_from is None
    assert typed.anion_from == "acid"

    legacy = next(
        plan for plan in compile_rules(load_knowledge(work))
        if plan.rule_id == "rule_m9_acid_thiosulfate_decomposition"
    ).products[0]
    assert legacy.cation_source.kind == "speciation"
    assert legacy.cation_source.binding == "thiosulfate"
    assert legacy.anion_source.kind == "speciation"
    assert legacy.anion_source.binding == "acid"
    assert legacy.cation_from == "thiosulfate"
    assert legacy.anion_from == "acid"


def test_relation_cation_and_speciation_anion_reuse_neutral_ionic_pair_resolution(tmp_path: Path) -> None:
    work = _copy(tmp_path)
    _set_source_relations(
        work,
        [
            {
                "relation_key": "metal.product_cation",
                "target_id": "ent_species_na_plus",
                "context": {"medium": "aqueous"},
                "evidence_ids": ["ev_f2_reactions"],
            }
        ],
    )
    _append_typed_rule(work)
    kb = load_knowledge(work)

    resolved = resolve_product_detail(
        kb,
        _fixture_plan(work).products[0],
        {"metal": "ent_substance_na2s2o3", "acid": "ent_substance_hcl"},
        {"medium": "aqueous", "temperature_regime": "ambient"},
    )

    assert resolved.target_id == "ent_substance_nacl"
    assert resolved.speciation_profiles == (
        {
            "target_id": "ent_substance_hcl",
            "profile_key": "aqueous_complete_dissociation",
            "model": "strong_electrolyte_complete_dissociation",
            "evidence_ids": ["ev_f2_reactions"],
        },
    )
    assert resolved.relation_assertions == (
        {
            "source_id": "ent_substance_na2s2o3",
            "relation_key": "metal.product_cation",
            "target_id": "ent_species_na_plus",
            "context": {"medium": "aqueous"},
            "evidence_ids": ["ev_f2_reactions"],
        },
    )
    assert resolved.evidence_ids == ("ev_f2_reactions",)


@pytest.mark.parametrize(
    ("assertions", "expected_code", "expected_candidates"),
    [
        ([], "relation_unavailable", []),
        (
            [
                {
                    "relation_key": "metal.product_cation",
                    "target_id": "ent_species_na_plus",
                    "context": {"medium": "aqueous"},
                    "evidence_ids": ["ev_f2_reactions"],
                },
                {
                    "relation_key": "metal.product_cation",
                    "target_id": "ent_species_k_plus",
                    "context": {"temperature_regime": "ambient"},
                    "evidence_ids": ["ev_f2_reactions"],
                },
            ],
            "relation_ambiguous",
            ["ent_species_k_plus", "ent_species_na_plus"],
        ),
    ],
)
def test_relation_ion_source_zero_and_multiple_targets_are_explicit(
    tmp_path: Path,
    assertions: list[dict],
    expected_code: str,
    expected_candidates: list[str],
) -> None:
    work = _copy(tmp_path)
    _set_source_relations(work, assertions)
    _append_typed_rule(work)
    kb = load_knowledge(work)

    with pytest.raises(ProductResolutionError) as exc:
        resolve_product_detail(
            kb,
            _fixture_plan(work).products[0],
            {"metal": "ent_substance_na2s2o3", "acid": "ent_substance_hcl"},
            {"medium": "aqueous", "temperature_regime": "ambient"},
        )

    assert exc.value.code == expected_code
    assert exc.value.stage == "relation_resolution"
    assert exc.value.details["source_id"] == "ent_substance_na2s2o3"
    assert exc.value.details["relation_key"] == "metal.product_cation"
    assert exc.value.details["candidates"] == expected_candidates


def test_m10_versions_track_source_dsl_plan_and_external_artifact_changes(tmp_path: Path) -> None:
    assert SOURCE_SCHEMA_VERSION == "3.2.0"
    assert RULE_DSL_VERSION == "1.1.0"
    assert RULE_PLAN_VERSION == "1.1.0"
    assert ARTIFACT_FORMAT_VERSION == "1.2.0"
    assert SUPPORTED_ARTIFACT_FORMAT_VERSIONS == frozenset({"1.0.0", "1.1.0", "1.2.0"})
    assert artifact_versions() == {
        "source_schema": "3.2.0",
        "rule_dsl": "1.1.0",
        "rule_plan": "1.1.0",
        "artifact_format": "1.2.0",
    }

    output = tmp_path / "compiled"
    compile_repository(ROOT, output, "m10-version-fixture")
    payload = json.loads((output / "compiled-rule-plans.json").read_text(encoding="utf-8"))
    m10 = next(
        rule for rule in payload["rules"]
        if rule["rule_id"] == "rule_m10_active_metal_non_oxidizing_acid_hydrogen"
    )["products"][0]
    assert m10["cation_source"] == {
        "kind": "relation_target",
        "binding": "metal",
        "relation_key": "metal.product_cation",
    }
    assert m10["anion_source"] == {
        "kind": "speciation",
        "binding": "acid",
        "relation_key": None,
    }
    legacy = next(
        rule for rule in payload["rules"]
        if rule["rule_id"] == "rule_m9_acid_thiosulfate_decomposition"
    )["products"][0]
    assert legacy["cation_source"] == {
        "kind": "speciation",
        "binding": "thiosulfate",
        "relation_key": None,
    }
    assert legacy["anion_source"] == {
        "kind": "speciation",
        "binding": "acid",
        "relation_key": None,
    }
