from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

from compiler.balance import validate_conservation
from compiler.canonical import canonical_json_bytes
from compiler.engine import compare_canonical_reactions, reaction_signature
from compiler.model import BalanceResult
from compiler.reaction_forms import derive_aqueous_ionic_form
from compiler.source import KnowledgeBase, SourceError, load_knowledge

from .legacy_identity import DISPOSITIONS, reconcile_record, report_bytes


PHASES = {"s": "solid", "l": "liquid", "g": "gas", "aq": "aqueous"}
IONIC_PHASES = {**PHASES, "aq": "dissolved"}
CONDITIONS = {
    "高温": ("temperature_regime", "heated"),
    "加热": ("temperature_regime", "heated"),
    "加热可促进氨逸出": ("temperature_regime", "warmed"),
}


def _identity_policy(record: dict[str, Any], declared: dict[str, Any]) -> dict[str, Any] | None:
    if record.get("kind") == "ion":
        return {"intent": "reconcile"}
    if record.get("kind") != "substance":
        return None
    if declared:
        return {"intent": "reconcile", **declared}
    if record.get("category") == "simple_substance":
        return None
    return {
        "identity_profile": "strict_simple_substance_v1",
        "intent": "reconcile",
        "referent_shape": "simple_neutral_pure_compound",
    }


def _resolve_identity(
    legacy_id: str,
    identity_records: dict[str, dict[str, Any]],
    kb: KnowledgeBase,
    identity_policies: dict[str, dict[str, Any]],
) -> tuple[str | None, dict[str, Any]]:
    record = identity_records.get(legacy_id)
    if record is None:
        return None, {"legacy_id": legacy_id, "reason_code": "legacy_participant_record_missing"}
    family = record.get("kind")
    if family not in {"substance", "ion"}:
        return None, {"legacy_id": legacy_id, "reason_code": "unsupported_participant_family"}
    policy = _identity_policy(record, identity_policies.get(legacy_id, {}))
    if policy is None:
        return None, {
            "legacy_id": legacy_id,
            "reason_code": "participant_referent_shape_not_approved",
        }
    decision = reconcile_record(family, record, kb.entities, kb.evidence, kb.sources, policy)
    if decision["disposition"] != "mapped_existing":
        return None, {
            "legacy_id": legacy_id,
            "reason_code": "participant_identity_unresolved",
            "identity_disposition": decision["disposition"],
            "identity_reason_code": decision.get("reason_code"),
        }
    return decision["canonical_id"], {
        "legacy_id": legacy_id,
        "canonical_id": decision["canonical_id"],
        "identity_basis": decision["identity_basis"],
    }


def _normalize_context(record: dict[str, Any]) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    conditions = record.get("conditions")
    if not isinstance(conditions, list) or any(
        not isinstance(item, str) or not item for item in conditions
    ):
        return None, {"reason_code": "invalid_legacy_conditions"}
    context: dict[str, Any] = {}
    participants = record.get("reactants", []) + record.get("products", [])
    if any(item.get("phase") == "aq" for item in participants if isinstance(item, dict)):
        context["medium"] = "aqueous"
    normalized: list[dict[str, str]] = []
    for condition in sorted(conditions):
        mapped = CONDITIONS.get(condition)
        if mapped is None:
            return None, {"reason_code": "unsupported_condition", "legacy_condition": condition}
        key, value = mapped
        if key in context and context[key] != value:
            return None, {"reason_code": "conflicting_conditions", "condition_key": key}
        context[key] = value
        normalized.append({"legacy": condition, "key": key, "value": value})
    return context, {"context": context, "normalized_conditions": normalized}


def _validate_reaction_shape(record: dict[str, Any]) -> str | None:
    if not isinstance(record.get("id"), str) or record.get("kind") != "reaction":
        return "invalid_reaction_identity"
    if record.get("reversible") is not False:
        return "reversible_reaction_not_supported"
    for role_key in ("reactants", "products"):
        participants = record.get(role_key)
        if not isinstance(participants, list) or not participants:
            return "invalid_participant_collection"
        for participant in participants:
            if not isinstance(participant, dict) or not isinstance(
                participant.get("species_id"), str
            ):
                return "invalid_participant_shape"
            coefficient = participant.get("coefficient")
            if (
                isinstance(coefficient, bool)
                or not isinstance(coefficient, int)
                or coefficient <= 0
            ):
                return "invalid_coefficient"
            if participant.get("phase") not in PHASES:
                return "unsupported_phase"
    return None


def _resolve_participants(
    record: dict[str, Any],
    kb: KnowledgeBase,
    identity_records: dict[str, dict[str, Any]],
    identity_policies: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]] | None, list[dict[str, Any]], dict[str, Any] | None]:
    totals: dict[tuple[str, str, str], int] = defaultdict(int)
    mappings: list[dict[str, Any]] = []
    for role_key, role in (("reactants", "reactant"), ("products", "product")):
        for participant in record[role_key]:
            legacy_id = participant["species_id"]
            canonical_id, identity = _resolve_identity(
                legacy_id, identity_records, kb, identity_policies
            )
            if canonical_id is None:
                return None, mappings, identity
            phase = PHASES[participant["phase"]]
            coefficient = participant["coefficient"]
            totals[(role, canonical_id, phase)] += coefficient
            mappings.append(
                {
                    **identity,
                    "role": role,
                    "coefficient": coefficient,
                    "legacy_phase": participant["phase"],
                    "canonical_phase": phase,
                }
            )
    common = 0
    for coefficient in totals.values():
        common = math.gcd(common, coefficient)
    common = common or 1
    participants = [
        {
            "target_id": target_id,
            "target_kind": kb.entities[target_id]["entity_kind"],
            "role": role,
            "coefficient": {"numerator": coefficient // common, "denominator": 1},
            "phase": phase,
        }
        for (role, target_id, phase), coefficient in sorted(totals.items())
    ]
    return (
        participants,
        sorted(mappings, key=lambda item: (item["role"], item["legacy_id"])),
        None,
    )


def _conservation(kb: KnowledgeBase, participants: list[dict[str, Any]]) -> dict[str, bool]:
    ordered = sorted(
        participants,
        key=lambda item: (item["role"] != "reactant", item["target_id"], item["phase"]),
    )
    reactants = tuple(item["target_id"] for item in ordered if item["role"] == "reactant")
    products = tuple(item["target_id"] for item in ordered if item["role"] == "product")
    coefficients = tuple(item["coefficient"]["numerator"] for item in ordered)
    atoms, charge = validate_conservation(
        kb,
        reactants,
        products,
        BalanceResult(coefficients=coefficients, reactant_count=len(reactants)),
    )
    return {"atoms": atoms, "charge": charge}


def _reaction_form_diagnostic(
    record: dict[str, Any],
    canonical_id: str,
    context: dict[str, Any],
    kb: KnowledgeBase,
    identity_records: dict[str, dict[str, Any]],
    identity_policies: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    legacy_form = record.get("net_ionic")
    if legacy_form is None:
        return {"state": "unavailable", "reason_code": "legacy_net_ionic_absent"}
    if not isinstance(legacy_form, dict):
        return {"state": "unsupported_inconsistent", "reason_code": "invalid_legacy_net_ionic"}
    resolved: list[dict[str, Any]] = []
    for role_key, role in (("reactants", "reactant"), ("products", "product")):
        role_participants = legacy_form.get(role_key)
        if not isinstance(role_participants, list) or not role_participants:
            return {
                "state": "unsupported_inconsistent",
                "reason_code": "invalid_legacy_net_ionic",
            }
        for participant in role_participants:
            if not isinstance(participant, dict):
                return {
                    "state": "unsupported_inconsistent",
                    "reason_code": "invalid_legacy_net_ionic",
                }
            canonical_participant, detail = _resolve_identity(
                participant.get("species_id", ""), identity_records, kb, identity_policies
            )
            if canonical_participant is None:
                return {
                    "state": "unsupported_inconsistent",
                    "reason_code": "legacy_net_ionic_participant_unresolved",
                    "participant": detail,
                }
            phase = IONIC_PHASES.get(participant.get("phase"))
            coefficient = participant.get("coefficient")
            if (
                phase is None
                or isinstance(coefficient, bool)
                or not isinstance(coefficient, int)
                or coefficient <= 0
            ):
                return {
                    "state": "unsupported_inconsistent",
                    "reason_code": "invalid_legacy_net_ionic",
                }
            resolved.append(
                {
                    "target_id": canonical_participant,
                    "target_kind": kb.entities[canonical_participant]["entity_kind"],
                    "role": role,
                    "coefficient": {"numerator": coefficient, "denominator": 1},
                    "phase": phase,
                }
            )
    try:
        canonical_form = derive_aqueous_ionic_form(kb, canonical_id, "net_ionic", context)
    except SourceError as exc:
        return {"state": "unavailable", "reason_code": exc.code}
    if canonical_form.get("status") != "derived":
        return {"state": "unavailable", "reason_code": "canonical_net_ionic_unavailable"}
    compatible = reaction_signature(resolved) == reaction_signature(canonical_form["participants"])
    return {
        "state": "compatible" if compatible else "unsupported_inconsistent",
        "reason_code": None if compatible else "legacy_net_ionic_mismatch",
    }


def reconcile_reaction(
    record: dict[str, Any],
    kb: KnowledgeBase,
    identity_records: dict[str, dict[str, Any]],
    identity_policies: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    legacy_id = record.get("id")
    base = {"legacy_id": legacy_id, "record_family": "reaction"}
    invalid = _validate_reaction_shape(record)
    if invalid:
        return {**base, "disposition": "rejected_invalid", "reason_code": invalid}
    context, condition_detail = _normalize_context(record)
    if context is None:
        disposition = (
            "rejected_invalid"
            if condition_detail["reason_code"]
            in {"invalid_legacy_conditions", "conflicting_conditions"}
            else "skipped_unsupported"
        )
        return {**base, "disposition": disposition, **condition_detail}
    participants, mappings, unresolved = _resolve_participants(
        record, kb, identity_records, identity_policies or {}
    )
    if participants is None:
        return {
            **base,
            "disposition": "skipped_unsupported",
            "participant_mappings": mappings,
            "reason_code": "unresolved_participant",
            "unresolved_participant": unresolved,
        }
    try:
        conservation = _conservation(kb, participants)
    except (KeyError, SourceError, ValueError) as exc:
        return {
            **base,
            "disposition": "rejected_invalid",
            "reason_code": "conservation_unavailable",
            "diagnostic": str(exc),
        }
    if not all(conservation.values()):
        return {
            **base,
            "conservation": conservation,
            "disposition": "rejected_invalid",
            "normalized_participant_signature": participants,
            "participant_mappings": mappings,
            "reason_code": "conservation_failed",
        }
    comparison = compare_canonical_reactions(kb, participants, context)
    common = {
        **base,
        "condition_interpretation": condition_detail,
        "conservation": conservation,
        "normalized_participant_signature": participants,
        "participant_mappings": mappings,
        "reaction_signature": reaction_signature(participants),
    }
    if comparison["state"] == "conflict":
        return {
            **common,
            "candidate_ids": comparison["reaction_ids"],
            "disposition": "ambiguous",
            "reason_code": "multiple_compatible_canonical_reactions",
        }
    if comparison["state"] == "none":
        has_signature_match = bool(comparison["condition_compatibility"])
        return {
            **common,
            "disposition": "skipped_unsupported",
            "reason_code": (
                "incompatible_canonical_conditions"
                if has_signature_match
                else "canonical_reaction_no_match"
            ),
            "condition_compatibility": comparison["condition_compatibility"],
        }
    canonical_id = comparison["reaction_ids"][0]
    return {
        **common,
        "canonical_id": canonical_id,
        "canonical_match_basis": "normalized_participant_signature_and_controlled_conditions",
        "disposition": "mapped_existing",
        "reaction_form_comparison": _reaction_form_diagnostic(
            record,
            canonical_id,
            context,
            kb,
            identity_records,
            identity_policies or {},
        ),
    }


def build_report(
    records: Iterable[dict[str, Any]],
    cohort: Iterable[dict[str, Any]],
    kb: KnowledgeBase,
    identity_records: dict[str, dict[str, Any]],
    *,
    identity_policies: dict[str, dict[str, Any]] | None,
    legacy_revision: str,
    legacy_manifest: dict[str, Any],
    input_files: Iterable[str],
) -> dict[str, Any]:
    records = list(records)
    index = {record.get("id"): record for record in records}
    if None in index or len(index) != len(records):
        raise ValueError("invalid or duplicate legacy Reaction id")
    decisions: list[dict[str, Any]] = []
    selected: list[dict[str, Any]] = []
    for entry in sorted(cohort, key=lambda item: item["legacy_id"]):
        record = index.get(entry["legacy_id"])
        if record is None:
            decisions.append(
                {
                    "disposition": "rejected_invalid",
                    "legacy_id": entry["legacy_id"],
                    "reason_code": "selected_legacy_reaction_missing",
                    "record_family": "reaction",
                }
            )
            continue
        selected.append(record)
        decisions.append(reconcile_reaction(record, kb, identity_records, identity_policies))
    counts = {name: 0 for name in DISPOSITIONS}
    for decision in decisions:
        counts[decision["disposition"]] += 1
    digest = hashlib.sha256(
        canonical_json_bytes(sorted(selected, key=lambda item: item["id"]))
    ).hexdigest()
    return {
        "canonical_source_digest": kb.source_digest,
        "decisions": sorted(decisions, key=lambda item: item["legacy_id"]),
        "disposition_counts": counts,
        "input_summary": {
            "by_family": {"reaction": len(decisions)},
            "input_files": sorted(set(input_files)),
            "selected_count": len(decisions),
            "selected_records_sha256": digest,
        },
        "legacy_source": {
            "package": legacy_manifest.get("package"),
            "package_path": "packages/inorganic",
            "package_version": legacy_manifest.get("version"),
            "revision": legacy_revision,
        },
        "milestone": "M24",
        "report_version": "1.0.0",
    }


def _read_jsonl(package_root: Path, files: Iterable[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for logical_file in sorted(files):
        for line_number, line in enumerate(
            (package_root / logical_file).read_text(encoding="utf-8").splitlines(), 1
        ):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSONL in {logical_file}:{line_number}") from exc
    return records


def run_reaction_pilot(repo_root: Path, legacy_root: Path, cohort_path: Path) -> dict[str, Any]:
    cohort_doc = json.loads(cohort_path.read_text(encoding="utf-8"))
    revision = subprocess.run(
        ["git", "-C", str(legacy_root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if revision != cohort_doc["expected_legacy_revision"]:
        expected_revision = cohort_doc["expected_legacy_revision"]
        raise ValueError(
            f"legacy revision mismatch: expected {expected_revision}, got {revision}"
        )
    package_root = legacy_root / cohort_doc["legacy_package_path"]
    manifest = json.loads((package_root / "manifest.json").read_text(encoding="utf-8"))
    reaction_files = manifest["canonical_files"]["reactions"]
    identity_files = (
        manifest["canonical_files"]["ions"] + manifest["canonical_files"]["substances"]
    )
    reactions = _read_jsonl(package_root, reaction_files)
    identity_list = _read_jsonl(package_root, identity_files)
    identity_records = {record["id"]: record for record in identity_list}
    if len(identity_records) != len(identity_list):
        raise ValueError("duplicate legacy identity record")
    return build_report(
        reactions,
        cohort_doc["records"],
        load_knowledge(repo_root),
        identity_records,
        identity_policies=cohort_doc.get("identity_policies", {}),
        legacy_revision=revision,
        legacy_manifest=manifest,
        input_files=reaction_files,
    )


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Run the bounded M24 legacy Reaction pilot")
    result.add_argument("--repo-root", type=Path, default=Path.cwd())
    result.add_argument("--legacy-root", type=Path, required=True)
    result.add_argument("--cohort", type=Path)
    result.add_argument("--output", type=Path)
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    repo_root = args.repo_root.resolve()
    cohort = args.cohort or repo_root / "migration" / "m24_reaction_pilot_cohort.json"
    output = args.output or repo_root / "migration" / "reports" / "m24_reaction_pilot_report.json"
    report = run_reaction_pilot(repo_root, args.legacy_root.resolve(), cohort.resolve())
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(report_bytes(report))
    summary = {
        "output": output.as_posix(),
        "disposition_counts": report["disposition_counts"],
    }
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
