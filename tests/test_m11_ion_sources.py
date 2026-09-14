from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml

from compiler.build import (
    ARTIFACT_FORMAT_VERSION,
    SUPPORTED_ARTIFACT_FORMAT_VERSIONS,
    artifact_versions,
)
from compiler.products import resolve_product_detail
from compiler.rules import RULE_DSL_VERSION, RULE_PLAN_VERSION, compile_rules
from compiler.source import SOURCE_SCHEMA_VERSION, SourceError, load_knowledge


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_RULE_ID = "rule_fixture_exact_entity_ion_source"


def _copy(tmp_path: Path) -> Path:
    work = tmp_path / "repo"
    shutil.copytree(ROOT, work)
    return work


def _append_exact_ion_rule(work: Path, target_id: str = "ent_species_oh_minus") -> None:
    rule = {
        "id": FIXTURE_RULE_ID,
        "record_type": "rule",
        "version": "1.0.0",
        "decision_domain": "exact_entity_ion_source_fixture",
        "match": {
            "reactants": [
                {"bind": "salt", "target_id": "ent_substance_nacl"},
            ]
        },
        "products": [
            {
                "phase": "aqueous",
                "construct": {
                    "kind": "ionic_pair",
                    "cation_source": {"kind": "speciation", "binding": "salt"},
                    "anion_source": {"kind": "exact_entity", "target_id": target_id},
                },
            }
        ],
        "validators": ["atoms_conserved", "charge_conserved"],
        "evidence_ids": ["ev_f2_reactions"],
    }
    path = work / "knowledge" / "rules" / "m11_exact_ion_fixture.yaml"
    path.write_text(yaml.safe_dump({"records": [rule]}, sort_keys=False), encoding="utf-8")


def test_exact_entity_ion_source_lowers_and_reuses_canonical_ionic_pair_resolution(
    tmp_path: Path,
) -> None:
    work = _copy(tmp_path)
    _append_exact_ion_rule(work)
    kb = load_knowledge(work)
    plan = next(plan for plan in compile_rules(kb) if plan.rule_id == FIXTURE_RULE_ID)

    product = plan.products[0]
    assert product.cation_source.kind == "speciation"
    assert product.cation_source.binding == "salt"
    assert product.anion_source.kind == "exact_entity"
    assert product.anion_source.binding is None
    assert product.anion_source.target_id == "ent_species_oh_minus"

    resolved = resolve_product_detail(
        kb,
        product,
        {"salt": "ent_substance_nacl"},
        {"medium": "aqueous", "temperature_regime": "ambient"},
    )

    assert resolved.target_id == "ent_substance_naoh"
    assert resolved.speciation_profiles == (
        {
            "target_id": "ent_substance_nacl",
            "profile_key": "aqueous_complete_dissociation",
            "model": "strong_electrolyte_complete_dissociation",
            "evidence_ids": ["ev_f2_reactions"],
        },
    )
    assert resolved.relation_assertions == ()
    assert resolved.evidence_ids == ("ev_f2_reactions",)


@pytest.mark.parametrize(
    ("target_id", "expected_code"),
    [
        ("ent_species_missing", "reference_unresolved"),
        ("ent_substance_h2o", "schema_invalid"),
        ("ent_species_na_plus", "schema_invalid"),
    ],
)
def test_exact_entity_ion_source_rejects_unresolved_non_ion_and_wrong_sign_targets(
    tmp_path: Path,
    target_id: str,
    expected_code: str,
) -> None:
    work = _copy(tmp_path)
    _append_exact_ion_rule(work, target_id)

    with pytest.raises(SourceError) as exc:
        load_knowledge(work)

    assert exc.value.code == expected_code
    assert exc.value.stage == "reference_validation"
    assert exc.value.details["target_id"] == target_id
    assert exc.value.details["ion_position"] == "anion"


def test_m11_versions_track_each_exact_ion_source_contract_change() -> None:
    assert SOURCE_SCHEMA_VERSION == "3.4.0"
    assert RULE_DSL_VERSION == "1.3.0"
    assert RULE_PLAN_VERSION == "1.3.0"
    assert ARTIFACT_FORMAT_VERSION == "1.4.0"
    assert SUPPORTED_ARTIFACT_FORMAT_VERSIONS == frozenset(
        {"1.0.0", "1.1.0", "1.2.0", "1.3.0", "1.4.0"}
    )
    assert artifact_versions() == {
        "source_schema": "3.4.0",
        "rule_dsl": "1.3.0",
        "rule_plan": "1.3.0",
        "artifact_format": "1.4.0",
    }


def test_exact_ion_target_participates_in_rule_outcome_equivalence(tmp_path: Path) -> None:
    work = _copy(tmp_path)
    _append_exact_ion_rule(work)
    path = work / "knowledge" / "rules" / "m11_exact_ion_fixture.yaml"
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    chloride_rule = doc["records"][0].copy()
    chloride_rule["id"] = "rule_fixture_exact_chloride_ion_source"
    chloride_rule["products"] = [
        {
            "phase": "aqueous",
            "construct": {
                "kind": "ionic_pair",
                "cation_source": {"kind": "speciation", "binding": "salt"},
                "anion_source": {
                    "kind": "exact_entity",
                    "target_id": "ent_species_cl_minus",
                },
            },
        }
    ]
    doc["records"].append(chloride_rule)
    path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")

    with pytest.raises(SourceError) as exc:
        compile_rules(load_knowledge(work))

    assert exc.value.code == "rule_overlap_compile_error"
    assert exc.value.stage == "rule_overlap_analysis"
    assert exc.value.details["outcomes_equivalent"] is False
