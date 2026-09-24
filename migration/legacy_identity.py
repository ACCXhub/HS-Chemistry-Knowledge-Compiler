from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Iterable

from compiler.source import KnowledgeBase, load_knowledge


DISPOSITIONS = (
    "mapped_existing",
    "created_canonical",
    "skipped_unsupported",
    "ambiguous",
    "rejected_invalid",
)
FAMILY_FILE_KEYS = {
    "element_scope": "element_scope",
    "ion": "ions",
    "substance": "substances",
}


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def report_bytes(report: dict[str, Any]) -> bytes:
    return _canonical_json(report) + b"\n"


def _legacy_composition(record: dict[str, Any]) -> tuple[tuple[str, int], ...]:
    composition = record.get("composition")
    if not isinstance(composition, dict) or not composition:
        raise ValueError("composition must be a non-empty object")
    normalized: list[tuple[str, int]] = []
    for symbol, count in composition.items():
        if not isinstance(symbol, str) or not symbol:
            raise ValueError("composition symbols must be non-empty strings")
        if isinstance(count, bool) or not isinstance(count, int) or count <= 0:
            raise ValueError("composition counts must be positive integers")
        normalized.append((symbol, count))
    return tuple(sorted(normalized))


def _validate_legacy_record(record_family: str, record: dict[str, Any]) -> None:
    legacy_id = record.get("id")
    if not isinstance(legacy_id, str) or not legacy_id:
        raise ValueError("id must be a non-empty string")
    expected_kind = {"element_scope": "element_scope", "ion": "ion", "substance": "substance"}.get(
        record_family
    )
    if expected_kind is None or record.get("kind") != expected_kind:
        raise ValueError(f"kind must be {expected_kind!r}")
    if record_family == "element_scope":
        symbol = record.get("symbol")
        atomic_number = record.get("atomic_number")
        if not isinstance(symbol, str) or not symbol:
            raise ValueError("element symbol must be a non-empty string")
        if isinstance(atomic_number, bool) or not isinstance(atomic_number, int) or atomic_number <= 0:
            raise ValueError("atomic_number must be a positive integer")
        return

    composition = _legacy_composition(record)
    if record_family == "ion":
        charge = record.get("charge")
        if isinstance(charge, bool) or not isinstance(charge, int) or charge == 0:
            raise ValueError("ion charge must be a non-zero integer")
        if record.get("ion_type") != "monatomic" or len(composition) != 1 or composition[0][1] != 1:
            raise ValueError("M22 supports only one-atom monatomic ions")


def _canonical_composition(
    entity: dict[str, Any], entities: dict[str, dict[str, Any]]
) -> tuple[tuple[str, int], ...] | None:
    components = entity.get("payload", {}).get("composition", {}).get("components")
    if not isinstance(components, list) or not components:
        return None
    normalized: list[tuple[str, int]] = []
    for component in components:
        element = entities.get(component.get("element_id"))
        symbol = (element or {}).get("payload", {}).get("symbol")
        count = component.get("count")
        if not isinstance(symbol, str) or isinstance(count, bool) or not isinstance(count, int):
            return None
        normalized.append((symbol, count))
    return tuple(sorted(normalized))


def _verified_candidates(
    record_family: str,
    record: dict[str, Any],
    entities: dict[str, dict[str, Any]],
    policy: dict[str, Any],
) -> tuple[list[str], dict[str, Any]]:
    if record_family == "element_scope":
        symbol = record["symbol"]
        atomic_number = record["atomic_number"]
        candidates = [
            entity_id
            for entity_id, entity in entities.items()
            if entity.get("entity_kind") == "element"
            and entity.get("payload", {}).get("symbol") == symbol
            and entity.get("payload", {}).get("atomic_number") == atomic_number
        ]
        facts = {"atomic_number": atomic_number, "entity_kind": "element", "symbol": symbol}
    else:
        composition = _legacy_composition(record)
        if record_family == "ion":
            charge = record["charge"]
            candidates = [
                entity_id
                for entity_id, entity in entities.items()
                if entity.get("entity_kind") == "species"
                and entity.get("payload", {}).get("species_kind") == "ion"
                and entity.get("payload", {}).get("formal_charge") == charge
                and entity.get("payload", {}).get("composition", {}).get("net_charge") == charge
                and _canonical_composition(entity, entities) == composition
            ]
            facts = {
                "composition": [[symbol, count] for symbol, count in composition],
                "entity_kind": "species",
                "formal_charge": charge,
                "species_kind": "ion",
            }
        else:
            candidates = [
                entity_id
                for entity_id, entity in entities.items()
                if entity.get("entity_kind") == "substance"
                and entity.get("payload", {}).get("substance_kind") == "pure_compound"
                and entity.get("payload", {}).get("composition", {}).get("net_charge") == 0
                and _canonical_composition(entity, entities) == composition
            ]
            facts = {
                "composition": [[symbol, count] for symbol, count in composition],
                "entity_kind": "substance",
                "net_charge": 0,
                "substance_kind": "pure_compound",
            }
            if policy.get("identity_profile") == "strict_simple_substance_v1":
                referent_shape = policy.get("referent_shape")
                if referent_shape != "simple_neutral_pure_compound":
                    raise ValueError("strict substance reconciliation requires an explicit referent shape gate")
                formula = record.get("formula")
                if not isinstance(formula, str) or not formula:
                    raise ValueError("strict substance reconciliation requires a formula lookup signal")
                candidates = [
                    entity_id
                    for entity_id in candidates
                    if any(
                        key.get("scheme") in {"formula.molecular", "formula.unit"}
                        and key.get("value") == formula
                        for key in entities[entity_id].get("semantic_keys", [])
                    )
                ]
                facts["formula_semantic_key"] = formula
                facts["referent_shape_gate"] = referent_shape
    return sorted(candidates), facts


def _identity_basis(record: dict[str, Any], facts: dict[str, Any]) -> dict[str, Any]:
    signals = {
        key: record[key]
        for key in ("formula", "name_en", "symbol")
        if isinstance(record.get(key), str) and record[key]
    }
    return {"lookup_signals": signals, "verified_facts": facts}


def _created_evidence_basis(
    canonical_id: str,
    evidence_ids: Iterable[str],
    entities: dict[str, dict[str, Any]],
    evidence: dict[str, dict[str, Any]],
    sources: dict[str, dict[str, Any]],
) -> list[dict[str, str]] | None:
    entity = entities.get(canonical_id)
    if entity is None:
        return None
    entity_evidence = set(entity.get("evidence_ids", []))
    result: list[dict[str, str]] = []
    for evidence_id in sorted(evidence_ids):
        item = evidence.get(evidence_id)
        source = sources.get((item or {}).get("source_id"))
        if (
            item is None
            or source is None
            or evidence_id not in entity_evidence
            or source.get("source_type") == "fixture"
        ):
            return None
        result.append({"evidence_id": evidence_id, "source_id": item["source_id"]})
    return result or None


def reconcile_record(
    record_family: str,
    record: dict[str, Any],
    entities: dict[str, dict[str, Any]],
    evidence: dict[str, dict[str, Any]],
    sources: dict[str, dict[str, Any]],
    policy: dict[str, Any],
) -> dict[str, Any]:
    base = {"legacy_id": record.get("id"), "record_family": record_family}
    try:
        _validate_legacy_record(record_family, record)
        candidates, facts = _verified_candidates(record_family, record, entities, policy)
    except (KeyError, ValueError) as exc:
        return {
            **base,
            "disposition": "rejected_invalid",
            "reason_code": "invalid_legacy_record",
            "diagnostic": str(exc),
        }

    basis = _identity_basis(record, facts)
    intent = policy.get("intent")
    if intent == "skip":
        return {
            **base,
            "disposition": "skipped_unsupported",
            "identity_basis": basis,
            "reason_code": policy["reason_code"],
        }
    if len(candidates) > 1:
        return {
            **base,
            "candidate_ids": candidates,
            "disposition": "ambiguous",
            "identity_basis": basis,
            "reason_code": "multiple_verified_canonical_matches",
        }
    if not candidates:
        return {
            **base,
            "disposition": "skipped_unsupported",
            "identity_basis": basis,
            "reason_code": "no_verified_canonical_match",
        }

    canonical_id = candidates[0]
    if intent == "reconcile":
        return {
            **base,
            "canonical_id": canonical_id,
            "disposition": "mapped_existing",
            "identity_basis": basis,
        }
    if intent == "create_canonical":
        if canonical_id != policy.get("canonical_id"):
            return {
                **base,
                "candidate_ids": candidates,
                "disposition": "ambiguous",
                "identity_basis": basis,
                "reason_code": "verified_match_differs_from_declared_creation",
            }
        evidence_basis = _created_evidence_basis(
            canonical_id,
            policy.get("evidence_ids", []),
            entities,
            evidence,
            sources,
        )
        if evidence_basis is None:
            return {
                **base,
                "disposition": "rejected_invalid",
                "identity_basis": basis,
                "reason_code": "canonical_creation_evidence_gate_failed",
            }
        return {
            **base,
            "canonical_id": canonical_id,
            "disposition": "created_canonical",
            "evidence_basis": evidence_basis,
            "identity_basis": basis,
        }
    return {
        **base,
        "disposition": "rejected_invalid",
        "identity_basis": basis,
        "reason_code": "invalid_cohort_policy",
    }


def build_report(
    records: Iterable[dict[str, Any]],
    cohort: Iterable[dict[str, Any]],
    kb: KnowledgeBase,
    *,
    legacy_revision: str,
    legacy_manifest: dict[str, Any],
    input_files: Iterable[str],
    milestone: str = "M22",
    report_version: str = "1.0.0",
    legacy_package_path: str = "packages/inorganic",
) -> dict[str, Any]:
    index: dict[str, dict[str, Any]] = {}
    for record in records:
        legacy_id = record.get("id")
        if not isinstance(legacy_id, str) or legacy_id in index:
            raise ValueError(f"invalid or duplicate legacy id: {legacy_id!r}")
        index[legacy_id] = record

    decisions: list[dict[str, Any]] = []
    selected_records: list[dict[str, Any]] = []
    family_counts: dict[str, int] = {}
    for policy in sorted(cohort, key=lambda item: item["legacy_id"]):
        legacy_id = policy["legacy_id"]
        record = index.get(legacy_id)
        if record is None:
            decisions.append(
                {
                    "disposition": "rejected_invalid",
                    "legacy_id": legacy_id,
                    "reason_code": "selected_legacy_record_missing",
                    "record_family": policy["record_family"],
                }
            )
            continue
        family = policy["record_family"]
        selected_records.append(record)
        family_counts[family] = family_counts.get(family, 0) + 1
        decisions.append(
            reconcile_record(family, record, kb.entities, kb.evidence, kb.sources, policy)
        )

    disposition_counts = {name: 0 for name in DISPOSITIONS}
    for decision in decisions:
        disposition_counts[decision["disposition"]] += 1
    selected_digest = hashlib.sha256(
        _canonical_json(sorted(selected_records, key=lambda item: item["id"]))
    ).hexdigest()
    return {
        "canonical_source_digest": kb.source_digest,
        "decisions": sorted(decisions, key=lambda item: item["legacy_id"]),
        "disposition_counts": disposition_counts,
        "input_summary": {
            "by_family": {key: family_counts[key] for key in sorted(family_counts)},
            "input_files": sorted(set(input_files)),
            "selected_count": len(decisions),
            "selected_records_sha256": selected_digest,
        },
        "legacy_source": {
            "package": legacy_manifest.get("package"),
            "package_path": legacy_package_path,
            "package_version": legacy_manifest.get("version"),
            "revision": legacy_revision,
        },
        "milestone": milestone,
        "report_version": report_version,
    }


def _git_revision(root: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _load_real_inputs(
    legacy_root: Path, cohort_doc: dict[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, Any], list[str]]:
    package_path = cohort_doc["legacy_package_path"]
    package_root = legacy_root / Path(package_path)
    manifest = json.loads((package_root / "manifest.json").read_text(encoding="utf-8"))
    selected_families = {item["record_family"] for item in cohort_doc["records"]}
    logical_files = sorted(
        {
            file_name
            for family in selected_families
            for file_name in manifest["canonical_files"][FAMILY_FILE_KEYS[family]]
        }
    )
    records: list[dict[str, Any]] = []
    for logical_file in logical_files:
        path = package_root / Path(logical_file)
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if line.strip():
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise ValueError(f"invalid JSONL in {logical_file}:{line_number}") from exc
    return records, manifest, logical_files


def run_identity_batch(repo_root: Path, legacy_root: Path, cohort_path: Path) -> dict[str, Any]:
    cohort_doc = json.loads(cohort_path.read_text(encoding="utf-8"))
    revision = _git_revision(legacy_root)
    expected_revision = cohort_doc["expected_legacy_revision"]
    if revision != expected_revision:
        raise ValueError(f"legacy revision mismatch: expected {expected_revision}, got {revision}")
    records, manifest, logical_files = _load_real_inputs(legacy_root, cohort_doc)
    kb = load_knowledge(repo_root)
    return build_report(
        records,
        cohort_doc["records"],
        kb,
        legacy_revision=revision,
        legacy_manifest=manifest,
        input_files=logical_files,
        milestone=cohort_doc.get("milestone", "M22"),
        report_version=cohort_doc.get("report_version", "1.0.0"),
        legacy_package_path=cohort_doc["legacy_package_path"],
    )


run_pilot = run_identity_batch


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Run a bounded legacy identity migration batch")
    result.add_argument("--repo-root", type=Path, default=Path.cwd())
    result.add_argument("--legacy-root", type=Path, required=True)
    result.add_argument("--cohort", type=Path)
    result.add_argument("--output", type=Path)
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    repo_root = args.repo_root.resolve()
    cohort_path = args.cohort or repo_root / "migration" / "m22_pilot_cohort.json"
    cohort_doc = json.loads(cohort_path.read_text(encoding="utf-8"))
    output = args.output or repo_root / cohort_doc.get(
        "report_path", "migration/reports/m22_pilot_report.json"
    )
    report = run_identity_batch(repo_root, args.legacy_root.resolve(), cohort_path.resolve())
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(report_bytes(report))
    print(json.dumps({"output": output.as_posix(), "disposition_counts": report["disposition_counts"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
