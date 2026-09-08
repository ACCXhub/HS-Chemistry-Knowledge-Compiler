from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from . import __version__
from .canonical import write_canonical_json
from .engine import infer_case
from .rules import compile_rules
from .source import load_cases, load_knowledge


CONTRACT_VERSION = "f2.0"


def validate(repo_root: Path) -> dict[str, Any]:
    kb = load_knowledge(repo_root)
    cases = load_cases(repo_root)
    plans = compile_rules(kb)
    return {
        "source_digest": kb.source_digest,
        "record_count": len(kb.records),
        "rule_count": len(plans),
        "case_count": len(cases),
    }


def compile_repository(repo_root: Path, output_dir: Path, source_revision: str) -> dict[str, Any]:
    kb = load_knowledge(repo_root)
    plans = compile_rules(kb)
    plan_projection = [
        {
            "rule_id": plan.rule_id,
            "version": plan.version,
            "decision_domain": plan.decision_domain,
            "bindings": list(plan.bindings),
            "predicates": [predicate.__dict__ for predicate in plan.predicates],
            "blockers": [blocker.__dict__ for blocker in plan.blockers],
            "products": [list(product) for product in plan.products],
            "validators": list(plan.validators),
        }
        for plan in plans
    ]
    plan_hash = write_canonical_json(output_dir / "compiled-rule-plans.json", plan_projection)
    diagnostics = {
        "status": "ok",
        "record_count": len(kb.records),
        "rule_count": len(plans),
        "source_digest": kb.source_digest,
    }
    diagnostics_hash = write_canonical_json(output_dir / "diagnostics.json", diagnostics)
    manifest = {
        "compiler": {"name": "hs-chem-compiler", "version": __version__},
        "contract_version": CONTRACT_VERSION,
        "source_revision": source_revision,
        "source_semantic_digest": kb.source_digest,
        "artifacts": {
            "compiled-rule-plans.json": plan_hash,
            "diagnostics.json": diagnostics_hash,
        },
    }
    write_canonical_json(output_dir / "manifest.json", manifest)
    return manifest


def audit_repository(repo_root: Path, output_dir: Path, source_revision: str) -> dict[str, Any]:
    kb = load_knowledge(repo_root)
    plans = compile_rules(kb)
    cases = load_cases(repo_root)
    results = [infer_case(kb, plans, case) for case in sorted(cases, key=lambda item: item["id"])]
    candidate_hash = write_canonical_json(output_dir / "reaction-candidates.json", results)
    diagnostics = {
        "statuses": {
            status: sum(1 for result in results if result["status"] == status)
            for status in sorted({result["status"] for result in results})
        },
        "source_digest": kb.source_digest,
    }
    diagnostics_hash = write_canonical_json(output_dir / "diagnostics.json", diagnostics)
    manifest = {
        "compiler": {"name": "hs-chem-compiler", "version": __version__},
        "contract_version": CONTRACT_VERSION,
        "source_revision": source_revision,
        "source_semantic_digest": kb.source_digest,
        "artifacts": {
            "reaction-candidates.json": candidate_hash,
            "diagnostics.json": diagnostics_hash,
        },
    }
    manifest_hash = write_canonical_json(output_dir / "manifest.json", manifest)
    return {"manifest_hash": manifest_hash, "manifest": manifest, "results": results}


def tree_digest(path: Path) -> str:
    digest = hashlib.sha256()
    for file_path in sorted(path.glob("*.json"), key=lambda p: p.name):
        digest.update(file_path.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_path.read_bytes())
    return digest.hexdigest()
