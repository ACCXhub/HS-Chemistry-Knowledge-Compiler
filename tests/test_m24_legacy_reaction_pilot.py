from __future__ import annotations

import copy
import json
from dataclasses import replace
from pathlib import Path

from compiler.source import load_knowledge
from migration.legacy_identity import reconcile_record, report_bytes
from migration.legacy_reaction import build_report, reconcile_reaction


ROOT = Path(__file__).resolve().parents[1]


def _substance(legacy_id: str, formula: str, composition: dict[str, int]) -> dict:
    return {
        "id": legacy_id,
        "kind": "substance",
        "name_en": legacy_id.removeprefix("substance:").replace("-", " "),
        "formula": formula,
        "composition": composition,
    }


def _neutralization_identities() -> dict[str, dict]:
    records = [
        _substance("substance:hydrogen-chloride", "HCl", {"H": 1, "Cl": 1}),
        _substance("substance:sodium-hydroxide", "NaOH", {"Na": 1, "O": 1, "H": 1}),
        _substance("substance:sodium-chloride", "NaCl", {"Na": 1, "Cl": 1}),
        _substance("substance:water", "H2O", {"H": 2, "O": 1}),
    ]
    return {record["id"]: record for record in records}


def _neutralization_record(*, scale: int = 1, legacy_id: str = "reaction:hcl-naoh-test") -> dict:
    return {
        "id": legacy_id,
        "kind": "reaction",
        "reactants": [
            {"species_id": "substance:hydrogen-chloride", "coefficient": scale, "phase": "aq"},
            {"species_id": "substance:sodium-hydroxide", "coefficient": scale, "phase": "aq"},
        ],
        "products": [
            {"species_id": "substance:sodium-chloride", "coefficient": scale, "phase": "aq"},
            {"species_id": "substance:water", "coefficient": scale, "phase": "l"},
        ],
        "conditions": [],
        "reversible": False,
    }


def _thermal_identities() -> dict[str, dict]:
    records = [
        _substance("substance:calcium-carbonate", "CaCO3", {"Ca": 1, "C": 1, "O": 3}),
        _substance("substance:calcium-oxide", "CaO", {"Ca": 1, "O": 1}),
        _substance("substance:carbon-dioxide", "CO2", {"C": 1, "O": 2}),
    ]
    return {record["id"]: record for record in records}


def _thermal_record(conditions: list[str]) -> dict:
    return {
        "id": "reaction:caco3-thermal-test",
        "kind": "reaction",
        "reactants": [
            {"species_id": "substance:calcium-carbonate", "coefficient": 1, "phase": "s"}
        ],
        "products": [
            {"species_id": "substance:calcium-oxide", "coefficient": 1, "phase": "s"},
            {"species_id": "substance:carbon-dioxide", "coefficient": 1, "phase": "g"},
        ],
        "conditions": conditions,
        "reversible": False,
    }


def _report() -> dict:
    return json.loads(
        (ROOT / "migration" / "reports" / "m24_reaction_pilot_report.json").read_text(
            encoding="utf-8"
        )
    )


def test_real_pilot_maps_multiple_families_without_creating_truth() -> None:
    report = _report()
    decisions = {item["legacy_id"]: item for item in report["decisions"]}

    assert report["milestone"] == "M24"
    assert report["input_summary"]["selected_count"] == 18
    assert report["disposition_counts"] == {
        "ambiguous": 0,
        "created_canonical": 0,
        "mapped_existing": 16,
        "rejected_invalid": 0,
        "skipped_unsupported": 2,
    }
    assert {
        decisions["reaction:hcl-naoh"]["canonical_id"],
        decisions["reaction:agno3-nacl"]["canonical_id"],
        decisions["reaction:sodium-bicarbonate-hcl"]["canonical_id"],
        decisions["reaction:na2so3-hcl"]["canonical_id"],
        decisions["reaction:nh4cl-naoh"]["canonical_id"],
        decisions["reaction:zinc-cuso4"]["canonical_id"],
        decisions["reaction:caco3-thermal"]["canonical_id"],
        decisions["reaction:nahco3-thermal"]["canonical_id"],
    } == {
        "rxn_hcl_naoh_neutralization",
        "rxn_agcl_precipitation",
        "rxn_f3b_hcl_nahco3_gas_evolution",
        "rxn_m8_hcl_na2so3_gas_evolution",
        "rxn_m7_nh4cl_naoh_ammonia_liberation",
        "rxn_m12_zn_cuso4_displacement",
        "rxn_m16_caco3_heated_decomposition",
        "rxn_m17_nahco3_heated_decomposition",
    }
    assert decisions["reaction:calcium-carbonate-hcl"]["reason_code"] == (
        "canonical_reaction_no_match"
    )
    assert decisions["reaction:ammonia-catalytic-oxidation"]["reason_code"] == (
        "unsupported_condition"
    )
    assert "C:\\" not in json.dumps(report)


def test_common_factor_normalizes_but_reverse_and_phase_mismatch_do_not() -> None:
    kb = load_knowledge(ROOT)
    identities = _neutralization_identities()

    scaled = reconcile_reaction(_neutralization_record(scale=2), kb, identities)
    assert scaled["disposition"] == "mapped_existing"
    assert scaled["canonical_id"] == "rxn_hcl_naoh_neutralization"
    assert {
        item["coefficient"]["numerator"]
        for item in scaled["normalized_participant_signature"]
    } == {1}

    reversed_record = _neutralization_record()
    reversed_record["reactants"], reversed_record["products"] = (
        reversed_record["products"],
        reversed_record["reactants"],
    )
    reversed_result = reconcile_reaction(reversed_record, kb, identities)
    assert reversed_result["disposition"] == "skipped_unsupported"
    assert reversed_result["reason_code"] == "canonical_reaction_no_match"

    wrong_phase = _neutralization_record()
    wrong_phase["products"][1]["phase"] = "g"
    phase_result = reconcile_reaction(wrong_phase, kb, identities)
    assert phase_result["disposition"] == "skipped_unsupported"
    assert phase_result["reason_code"] == "canonical_reaction_no_match"


def test_unresolved_invalid_and_unconserved_reactions_fail_closed() -> None:
    kb = load_knowledge(ROOT)
    identities = _neutralization_identities()

    unresolved_identities = dict(identities)
    unresolved_identities.pop("substance:sodium-hydroxide")
    unresolved = reconcile_reaction(_neutralization_record(), kb, unresolved_identities)
    assert unresolved["disposition"] == "skipped_unsupported"
    assert unresolved["reason_code"] == "unresolved_participant"

    malformed = _neutralization_record()
    malformed["reactants"][0]["coefficient"] = 0
    invalid = reconcile_reaction(malformed, kb, identities)
    assert invalid["disposition"] == "rejected_invalid"
    assert invalid["reason_code"] == "invalid_coefficient"

    unconserved_record = _neutralization_record()
    unconserved_record["products"][1]["coefficient"] = 2
    unconserved = reconcile_reaction(unconserved_record, kb, identities)
    assert unconserved["disposition"] == "rejected_invalid"
    assert unconserved["reason_code"] == "conservation_failed"


def test_required_controlled_condition_is_neither_omitted_nor_invented() -> None:
    kb = load_knowledge(ROOT)
    identities = _thermal_identities()

    heated = reconcile_reaction(_thermal_record(["高温"]), kb, identities)
    assert heated["disposition"] == "mapped_existing"
    assert heated["canonical_id"] == "rxn_m16_caco3_heated_decomposition"

    missing = reconcile_reaction(_thermal_record([]), kb, identities)
    assert missing["disposition"] == "skipped_unsupported"
    assert missing["reason_code"] == "incompatible_canonical_conditions"
    assert missing["condition_compatibility"][0]["unsatisfied"][0]["reason"] == "missing"

    incompatible = reconcile_reaction(_thermal_record(["加热可促进氨逸出"]), kb, identities)
    assert incompatible["disposition"] == "skipped_unsupported"
    assert incompatible["reason_code"] == "incompatible_canonical_conditions"
    assert incompatible["condition_compatibility"][0]["unsatisfied"][0]["reason"] == "conflicting"


def test_multiple_canonical_matches_are_ambiguous() -> None:
    kb = load_knowledge(ROOT)
    reactions = copy.deepcopy(kb.reactions)
    duplicate = copy.deepcopy(reactions["rxn_hcl_naoh_neutralization"])
    duplicate["id"] = "rxn_hcl_naoh_duplicate_for_test"
    reactions[duplicate["id"]] = duplicate
    ambiguous_kb = replace(kb, reactions=reactions)

    result = reconcile_reaction(
        _neutralization_record(), ambiguous_kb, _neutralization_identities()
    )
    assert result["disposition"] == "ambiguous"
    assert result["reason_code"] == "multiple_compatible_canonical_reactions"
    assert result["candidate_ids"] == [
        "rxn_hcl_naoh_duplicate_for_test",
        "rxn_hcl_naoh_neutralization",
    ]


def test_report_is_order_independent_generator_safe_and_idempotent() -> None:
    kb = load_knowledge(ROOT)
    identities = _neutralization_identities()
    records = [
        _neutralization_record(legacy_id="reaction:a"),
        _neutralization_record(scale=2, legacy_id="reaction:b"),
    ]
    cohort = [{"legacy_id": "reaction:a"}, {"legacy_id": "reaction:b"}]
    reactions_before = copy.deepcopy(kb.reactions)
    kwargs = {
        "identity_policies": {},
        "legacy_revision": "a" * 40,
        "legacy_manifest": {"package": "inorganic", "version": "test"},
        "input_files": ["data/reactions.jsonl"],
    }

    first = build_report((item for item in records), cohort, kb, identities, **kwargs)
    second = build_report(
        (item for item in reversed(records)), list(reversed(cohort)), kb, identities, **kwargs
    )

    assert report_bytes(first) == report_bytes(second)
    assert kb.reactions == reactions_before
    assert first["disposition_counts"]["created_canonical"] == 0


def test_elemental_identity_profile_is_explicit_and_formula_corroborated() -> None:
    kb = load_knowledge(ROOT)
    record = _substance("substance:zinc", "Zn", {"Zn": 1})
    policy = {
        "identity_profile": "strict_elemental_substance_v1",
        "intent": "reconcile",
        "referent_shape": "single_elemental_substance_referent",
    }

    mapped = reconcile_record(
        "substance", record, kb.entities, kb.evidence, kb.sources, policy
    )
    assert mapped["disposition"] == "mapped_existing"
    assert mapped["canonical_id"] == "ent_substance_elemental_zn"

    wrong_formula = {**record, "formula": "not-zinc"}
    skipped = reconcile_record(
        "substance", wrong_formula, kb.entities, kb.evidence, kb.sources, policy
    )
    assert skipped["disposition"] == "skipped_unsupported"
    assert skipped["reason_code"] == "no_verified_canonical_match"


def test_legacy_reaction_forms_are_diagnostics_only_and_runtime_isolated() -> None:
    mapped = [item for item in _report()["decisions"] if item["disposition"] == "mapped_existing"]
    states = {item["reaction_form_comparison"]["state"] for item in mapped}
    assert states == {"compatible", "unavailable", "unsupported_inconsistent"}
    assert not any("reaction_form" in item.get("canonical_match_basis", "") for item in mapped)

    malformed_form = _neutralization_record()
    malformed_form["net_ionic"] = {"reactants": "not-a-participant-list", "products": []}
    diagnostic = reconcile_reaction(
        malformed_form, load_knowledge(ROOT), _neutralization_identities()
    )
    assert diagnostic["disposition"] == "mapped_existing"
    assert diagnostic["reaction_form_comparison"] == {
        "state": "unsupported_inconsistent",
        "reason_code": "invalid_legacy_net_ionic",
    }

    for path in (ROOT / "compiler").glob("*.py"):
        source = path.read_text(encoding="utf-8")
        assert "from migration" not in source
        assert "import migration" not in source
