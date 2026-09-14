from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml

from compiler.source import SourceError, load_knowledge


ROOT = Path(__file__).resolve().parents[1]


def _copy(tmp_path: Path) -> Path:
    work = tmp_path / "repo"
    shutil.copytree(ROOT, work)
    return work


def _set_entity_relations(work: Path, entity_id: str, assertions: list[dict]) -> None:
    for path in sorted((work / "knowledge" / "domain").glob("*.yaml")):
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        entity = next((record for record in doc["records"] if record.get("id") == entity_id), None)
        if entity is None:
            continue
        entity["relation_assertions"] = assertions
        path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
        return
    raise AssertionError(f"fixture entity not found: {entity_id}")


def _assertion(
    target_id: str,
    *,
    relation_key: str = "metal.displaces_cation",
    evidence_id: str = "ev_f2_reactions",
) -> dict:
    return {
        "relation_key": relation_key,
        "target_id": target_id,
        "context": {"medium": "aqueous"},
        "evidence_ids": [evidence_id],
    }


def test_displacement_relation_allows_distinct_targets_in_one_context(tmp_path: Path) -> None:
    work = _copy(tmp_path)
    _set_entity_relations(
        work,
        "ent_substance_elemental_zn",
        [_assertion("ent_species_h_plus"), _assertion("ent_species_na_plus")],
    )

    kb = load_knowledge(work)

    assert [
        assertion["target_id"]
        for assertion in kb.relation_assertions(
            "ent_substance_elemental_zn",
            "metal.displaces_cation",
            {"medium": "aqueous"},
        )
    ] == ["ent_species_h_plus", "ent_species_na_plus"]


def test_product_cation_still_rejects_distinct_targets_in_one_context(tmp_path: Path) -> None:
    work = _copy(tmp_path)
    _set_entity_relations(
        work,
        "ent_substance_elemental_zn",
        [
            _assertion("ent_species_h_plus", relation_key="metal.product_cation"),
            _assertion("ent_species_na_plus", relation_key="metal.product_cation"),
        ],
    )

    with pytest.raises(SourceError, match="duplicate contextual relation assertion") as exc:
        load_knowledge(work)

    assert exc.value.code == "schema_invalid"
    assert exc.value.stage == "source_load"


def test_exact_duplicate_displacement_assertion_is_rejected(tmp_path: Path) -> None:
    work = _copy(tmp_path)
    assertion = _assertion("ent_species_na_plus")
    _set_entity_relations(work, "ent_substance_elemental_zn", [assertion, assertion.copy()])

    with pytest.raises(SourceError, match="duplicate contextual relation assertion") as exc:
        load_knowledge(work)

    assert exc.value.code == "schema_invalid"
    assert exc.value.stage == "source_load"


@pytest.mark.parametrize(
    ("target_id", "expected_code"),
    [
        ("ent_missing_species", "reference_unresolved"),
        ("ent_species_hcl_molecule", "schema_invalid"),
        ("ent_species_cl_minus", "schema_invalid"),
    ],
)
def test_displacement_target_must_resolve_to_a_positive_ion(
    tmp_path: Path,
    target_id: str,
    expected_code: str,
) -> None:
    work = _copy(tmp_path)
    _set_entity_relations(work, "ent_substance_elemental_zn", [_assertion(target_id)])

    with pytest.raises(SourceError) as exc:
        load_knowledge(work)

    assert exc.value.code == expected_code
    assert exc.value.stage == "reference_validation"
    assert exc.value.details["relation_key"] == "metal.displaces_cation"
    assert exc.value.details["source_id"] == "ent_substance_elemental_zn"
    assert exc.value.details["target_id"] == target_id


@pytest.mark.parametrize(
    "source_id",
    [
        "ent_element_zn",
        "ent_substance_hcl",
        "ent_substance_elemental_sulfur",
    ],
)
def test_displacement_source_must_be_an_elemental_metal_substance(
    tmp_path: Path,
    source_id: str,
) -> None:
    work = _copy(tmp_path)
    _set_entity_relations(work, source_id, [_assertion("ent_species_na_plus")])

    with pytest.raises(SourceError) as exc:
        load_knowledge(work)

    assert exc.value.code == "schema_invalid"
    assert exc.value.stage == "reference_validation"
    assert exc.value.details["relation_key"] == "metal.displaces_cation"
    assert exc.value.details["source_id"] == source_id


def test_displacement_relation_evidence_must_resolve(tmp_path: Path) -> None:
    work = _copy(tmp_path)
    _set_entity_relations(
        work,
        "ent_substance_elemental_zn",
        [_assertion("ent_species_na_plus", evidence_id="ev_missing_relation")],
    )

    with pytest.raises(SourceError) as exc:
        load_knowledge(work)

    assert exc.value.code == "reference_unresolved"
    assert exc.value.stage == "reference_validation"
    assert exc.value.details == {"kind": "evidence", "target_id": "ev_missing_relation"}
