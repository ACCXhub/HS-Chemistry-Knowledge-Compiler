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


def _set_hcl_relations(work: Path, assertions: list[dict]) -> None:
    path = work / "knowledge" / "domain" / "f2_entities.yaml"
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    hcl = next(record for record in doc["records"] if record.get("id") == "ent_substance_hcl")
    hcl["relation_assertions"] = assertions
    path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")


def test_relation_lookup_uses_most_specific_context_and_preserves_provenance(tmp_path: Path) -> None:
    work = _copy(tmp_path)
    _set_hcl_relations(
        work,
        [
            {
                "relation_key": "metal.product_cation",
                "target_id": "ent_species_h_plus",
                "context": {},
                "evidence_ids": ["ev_f2_reactions"],
            },
            {
                "relation_key": "metal.product_cation",
                "target_id": "ent_species_na_plus",
                "context": {"medium": "aqueous"},
                "evidence_ids": ["ev_f2_reactions"],
            },
        ],
    )

    kb = load_knowledge(work)

    assert kb.relation_assertions(
        "ent_substance_hcl",
        "metal.product_cation",
        {"medium": "aqueous", "temperature_regime": "ambient"},
    ) == (
        {
            "source_id": "ent_substance_hcl",
            "relation_key": "metal.product_cation",
            "target_id": "ent_species_na_plus",
            "context": {"medium": "aqueous"},
            "evidence_ids": ["ev_f2_reactions"],
        },
    )


def test_relation_key_is_controlled_by_the_source_contract(tmp_path: Path) -> None:
    work = _copy(tmp_path)
    _set_hcl_relations(
        work,
        [
            {
                "relation_key": "fixture.uncontrolled_relation",
                "target_id": "ent_species_h_plus",
                "context": {"medium": "aqueous"},
                "evidence_ids": ["ev_f2_reactions"],
            }
        ],
    )

    with pytest.raises(SourceError) as exc:
        load_knowledge(work)

    assert exc.value.code == "schema_invalid"
    assert exc.value.stage == "source_schema"


def test_duplicate_or_contradictory_relation_assertions_in_one_context_are_rejected(tmp_path: Path) -> None:
    work = _copy(tmp_path)
    _set_hcl_relations(
        work,
        [
            {
                "relation_key": "metal.product_cation",
                "target_id": "ent_species_h_plus",
                "context": {"medium": "aqueous"},
                "evidence_ids": ["ev_f2_reactions"],
            },
            {
                "relation_key": "metal.product_cation",
                "target_id": "ent_species_na_plus",
                "context": {"medium": "aqueous"},
                "evidence_ids": ["ev_f2_reactions"],
            },
        ],
    )

    with pytest.raises(SourceError, match="duplicate contextual relation assertion") as exc:
        load_knowledge(work)

    assert exc.value.code == "schema_invalid"
    assert exc.value.stage == "source_load"


@pytest.mark.parametrize(
    ("target_id", "evidence_id", "expected_kind"),
    [
        ("ent_missing_species", "ev_f2_reactions", "species"),
        ("ent_substance_nacl", "ev_f2_reactions", "species"),
        ("ent_species_h_plus", "ev_missing_relation", "evidence"),
    ],
)
def test_relation_targets_and_evidence_must_resolve(
    tmp_path: Path,
    target_id: str,
    evidence_id: str,
    expected_kind: str,
) -> None:
    work = _copy(tmp_path)
    _set_hcl_relations(
        work,
        [
            {
                "relation_key": "metal.product_cation",
                "target_id": target_id,
                "context": {"medium": "aqueous"},
                "evidence_ids": [evidence_id],
            }
        ],
    )

    with pytest.raises(SourceError) as exc:
        load_knowledge(work)

    assert exc.value.code == "reference_unresolved"
    assert exc.value.stage == "reference_validation"
    assert expected_kind in str(exc.value)


def test_relation_lookup_exposes_zero_and_equal_specificity_candidates_deterministically(tmp_path: Path) -> None:
    work = _copy(tmp_path)
    _set_hcl_relations(
        work,
        [
            {
                "relation_key": "metal.product_cation",
                "target_id": "ent_species_h_plus",
                "context": {"medium": "aqueous"},
                "evidence_ids": ["ev_f2_reactions"],
            },
            {
                "relation_key": "metal.product_cation",
                "target_id": "ent_species_na_plus",
                "context": {"temperature_regime": "ambient"},
                "evidence_ids": ["ev_f2_reactions"],
            },
        ],
    )
    kb = load_knowledge(work)

    assert kb.relation_assertions("ent_substance_hcl", "metal.product_cation", {}) == ()
    matches = kb.relation_assertions(
        "ent_substance_hcl",
        "metal.product_cation",
        {"medium": "aqueous", "temperature_regime": "ambient"},
    )
    assert [match["target_id"] for match in matches] == ["ent_species_h_plus", "ent_species_na_plus"]
