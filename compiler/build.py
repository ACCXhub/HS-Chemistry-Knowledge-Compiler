from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from . import __version__
from .canonical import write_canonical_json
from .engine import infer_case
from .reaction_forms import derive_aqueous_ionic_form
from .rules import RULE_DSL_VERSION, RULE_PLAN_VERSION, analyze_rule_overlaps, compile_rules
from .source import SOURCE_SCHEMA_VERSION, KnowledgeBase, load_cases, load_knowledge


ARTIFACT_FORMAT_VERSION = "1.2.0"
SUPPORTED_ARTIFACT_FORMAT_VERSIONS = frozenset({"1.0.0", "1.1.0", ARTIFACT_FORMAT_VERSION})


def artifact_versions() -> dict[str, str]:
    return {
        "source_schema": SOURCE_SCHEMA_VERSION,
        "rule_dsl": RULE_DSL_VERSION,
        "rule_plan": RULE_PLAN_VERSION,
        "artifact_format": ARTIFACT_FORMAT_VERSION,
    }


def validate_artifact_manifest(manifest: dict[str, Any]) -> None:
    versions = manifest.get("versions")
    if not isinstance(versions, dict):
        raise ValueError("artifact manifest is missing versions")
    version = versions.get("artifact_format")
    if version not in SUPPORTED_ARTIFACT_FORMAT_VERSIONS:
        raise ValueError(f"unsupported artifact format version: {version}")


def validate(repo_root: Path) -> dict[str, Any]:
    kb = load_knowledge(repo_root)
    cases = load_cases(repo_root)
    plans = compile_rules(kb)
    return {
        "source_digest": kb.source_digest,
        "record_count": len(kb.records),
        "rule_count": len(plans),
        "case_count": len(cases),
        "teaching_view_count": len(kb.teaching_views),
        "speciation_profile_count": sum(len(entity.get("speciation_profiles", [])) for entity in kb.entities.values()),
        "versions": artifact_versions(),
        "potential_overlap_count": len(analyze_rule_overlaps(plans)),
    }


def _plan_projection(plans: tuple[Any, ...]) -> dict[str, Any]:
    rules: list[dict[str, Any]] = []
    for plan in plans:
        rules.append(
            {
                "rule_id": plan.rule_id,
                "version": plan.version,
                "decision_domain": plan.decision_domain,
                "patterns": [pattern.__dict__ for pattern in plan.patterns],
                "predicates": [predicate.__dict__ for predicate in plan.predicates],
                "blockers": [blocker.__dict__ for blocker in plan.blockers],
                "products": [
                    {
                        "constructor": product.constructor,
                        "phase": product.phase,
                        "target_id": product.target_id,
                        "scheme": product.scheme,
                        "value": product.value,
                        "cation_source": None
                        if product.cation_source is None
                        else product.cation_source.__dict__,
                        "anion_source": None
                        if product.anion_source is None
                        else product.anion_source.__dict__,
                        "left_binding": product.left_binding,
                        "right_binding": product.right_binding,
                        "exchange_role": product.exchange_role,
                    }
                    for product in plan.products
                ],
                "validators": list(plan.validators),
                "relations": plan.relations.__dict__,
            }
        )
    return {
        "artifact_format_version": ARTIFACT_FORMAT_VERSION,
        "rule_plan_version": RULE_PLAN_VERSION,
        "rules": rules,
    }


def _teaching_projection(kb: KnowledgeBase) -> dict[str, Any]:
    return {
        "artifact_format_version": ARTIFACT_FORMAT_VERSION,
        "views": [kb.teaching_views[view_id] for view_id in sorted(kb.teaching_views)],
    }


def _speciation_projection(kb: KnowledgeBase) -> dict[str, Any]:
    entities: list[dict[str, Any]] = []
    for entity_id in sorted(kb.entities):
        profiles = kb.entities[entity_id].get("speciation_profiles", [])
        if not profiles:
            continue
        entities.append(
            {
                "entity_id": entity_id,
                "profiles": sorted(profiles, key=lambda profile: (profile["profile_key"], sorted(profile["context"].items()))),
            }
        )
    return {
        "artifact_format_version": ARTIFACT_FORMAT_VERSION,
        "entities": entities,
    }


def _derived_form_projection(kb: KnowledgeBase) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    for reaction_id in sorted(kb.reactions):
        form_kinds = sorted(
            {
                form["form_kind"]
                for form in kb.reactions[reaction_id].get("forms", [])
                if form["form_kind"] in {"complete_ionic", "net_ionic"}
                and form["projection"].get("lifecycle", "curated") == "golden"
            }
        )
        for form_kind in form_kinds:
            results.append(derive_aqueous_ionic_form(kb, reaction_id, form_kind, {"medium": "aqueous"}))
    return {
        "artifact_format_version": ARTIFACT_FORMAT_VERSION,
        "forms": results,
    }


def _write_compiled_knowledge_artifacts(kb: KnowledgeBase, output_dir: Path) -> dict[str, str]:
    return {
        "teaching-views.json": write_canonical_json(output_dir / "teaching-views.json", _teaching_projection(kb)),
        "aqueous-speciation.json": write_canonical_json(output_dir / "aqueous-speciation.json", _speciation_projection(kb)),
        "derived-reaction-forms.json": write_canonical_json(
            output_dir / "derived-reaction-forms.json", _derived_form_projection(kb)
        ),
    }


def compile_repository(repo_root: Path, output_dir: Path, source_revision: str) -> dict[str, Any]:
    kb = load_knowledge(repo_root)
    plans = compile_rules(kb)
    plan_hash = write_canonical_json(output_dir / "compiled-rule-plans.json", _plan_projection(plans))
    compiled_knowledge = _write_compiled_knowledge_artifacts(kb, output_dir)
    overlap_diagnostics = list(analyze_rule_overlaps(plans))
    diagnostics = {
        "artifact_format_version": ARTIFACT_FORMAT_VERSION,
        "status": "ok",
        "record_count": len(kb.records),
        "rule_count": len(plans),
        "teaching_view_count": len(kb.teaching_views),
        "source_digest": kb.source_digest,
        "potential_overlaps": overlap_diagnostics,
    }
    diagnostics_hash = write_canonical_json(output_dir / "diagnostics.json", diagnostics)
    manifest = {
        "compiler": {"name": "hs-chem-compiler", "version": __version__},
        "versions": artifact_versions(),
        "source_revision": source_revision,
        "source_semantic_digest": kb.source_digest,
        "artifacts": {
            "compiled-rule-plans.json": plan_hash,
            **compiled_knowledge,
            "diagnostics.json": diagnostics_hash,
        },
    }
    write_canonical_json(output_dir / "manifest.json", manifest)
    validate_artifact_manifest(manifest)
    return manifest


def audit_repository(repo_root: Path, output_dir: Path, source_revision: str) -> dict[str, Any]:
    kb = load_knowledge(repo_root)
    plans = compile_rules(kb)
    cases = load_cases(repo_root)
    results = [infer_case(kb, plans, case) for case in sorted(cases, key=lambda item: item["id"])]
    candidate_hash = write_canonical_json(
        output_dir / "reaction-candidates.json",
        {
            "artifact_format_version": ARTIFACT_FORMAT_VERSION,
            "results": results,
        },
    )
    compiled_knowledge = _write_compiled_knowledge_artifacts(kb, output_dir)
    diagnostics = {
        "artifact_format_version": ARTIFACT_FORMAT_VERSION,
        "statuses": {
            status: sum(1 for result in results if result["status"] == status)
            for status in sorted({result["status"] for result in results})
        },
        "source_digest": kb.source_digest,
    }
    diagnostics_hash = write_canonical_json(output_dir / "diagnostics.json", diagnostics)
    manifest = {
        "compiler": {"name": "hs-chem-compiler", "version": __version__},
        "versions": artifact_versions(),
        "source_revision": source_revision,
        "source_semantic_digest": kb.source_digest,
        "artifacts": {
            "reaction-candidates.json": candidate_hash,
            **compiled_knowledge,
            "diagnostics.json": diagnostics_hash,
        },
    }
    manifest_hash = write_canonical_json(output_dir / "manifest.json", manifest)
    validate_artifact_manifest(manifest)
    return {"manifest_hash": manifest_hash, "manifest": manifest, "results": results}


def tree_digest(path: Path) -> str:
    digest = hashlib.sha256()
    for file_path in sorted(path.glob("*.json"), key=lambda p: p.name):
        digest.update(file_path.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_path.read_bytes())
    return digest.hexdigest()
