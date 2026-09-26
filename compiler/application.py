"""Versioned, self-contained data export and validated application inference."""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

from . import __version__
from .build import artifact_versions
from .canonical import sha256_hex, write_canonical_json
from .engine import infer_case
from .rules import compile_rules
from .source import SourceError, knowledge_from_records, load_knowledge


BUNDLE_FORMAT_VERSION = "1.0.0"
_FILES = ("knowledge.json", "knowledge-record.schema.json", "inference-request.schema.json")


def export_bundle(repo_root: Path, output_dir: Path, source_revision: str) -> dict[str, Any]:
    """Publish canonical records, not fixture-generated reaction candidates."""
    kb = load_knowledge(repo_root)
    plans = compile_rules(kb)
    schema = json.loads((repo_root / "schemas/knowledge-record.schema.json").read_text(encoding="utf-8"))
    cases_schema = json.loads((repo_root / "schemas/f2-case.schema.json").read_text(encoding="utf-8"))
    request_schema = deepcopy(cases_schema["properties"]["cases"]["items"])
    request_schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    request_schema["properties"]["reactants"]["maxItems"] = max(len(plan.patterns) for plan in plans)
    request_schema["properties"]["context"] = {
        "type": "object", "additionalProperties": False,
        "properties": {
            "medium": {"enum": ["aqueous"]},
            "temperature_regime": {"enum": ["ambient", "warmed", "heated", "frozen"]},
        },
    }
    artifacts = {
        "knowledge.json": write_canonical_json(output_dir / "knowledge.json", {"records": kb.records}),
        "knowledge-record.schema.json": write_canonical_json(output_dir / "knowledge-record.schema.json", schema),
        "inference-request.schema.json": write_canonical_json(output_dir / "inference-request.schema.json", request_schema),
    }
    manifest = {
        "bundle_format_version": BUNDLE_FORMAT_VERSION,
        "compiler": {"name": "hs-chem-compiler", "version": __version__},
        "versions": artifact_versions(),
        "source_revision": source_revision,
        "source_semantic_digest": kb.source_digest,
        "record_counts": {kind: sum(record["record_type"] == kind for record in kb.records)
                          for kind in sorted({record["record_type"] for record in kb.records})},
        "artifacts": artifacts,
    }
    manifest["release_id"] = "hschem_" + sha256_hex(manifest)
    write_canonical_json(output_dir / "manifest.json", manifest)
    return manifest


def _bundle_error(message: str) -> SourceError:
    return SourceError(message, code="bundle_invalid", stage="bundle_load")


class InferenceSession:
    """Load once per application worker; infer without filesystem or database reads."""

    def __init__(self, bundle_dir: Path):
        try:
            manifest = json.loads((bundle_dir / "manifest.json").read_text(encoding="utf-8"))
            if not isinstance(manifest, dict):
                raise _bundle_error("bundle manifest must be an object")
            if manifest.get("bundle_format_version") != BUNDLE_FORMAT_VERSION:
                raise _bundle_error("unsupported bundle format")
            if manifest.get("compiler") != {"name": "hs-chem-compiler", "version": __version__}:
                raise _bundle_error("bundle requires its exact compiler version")
            if manifest.get("versions") != artifact_versions():
                raise _bundle_error("incompatible source/DSL/plan/artifact versions")
            body = {key: value for key, value in manifest.items() if key != "release_id"}
            if manifest.get("release_id") != "hschem_" + sha256_hex(body):
                raise _bundle_error("release identity mismatch")
            if not isinstance(manifest.get("artifacts"), dict) or set(manifest["artifacts"]) != set(_FILES):
                raise _bundle_error("bundle artifact set mismatch")
            documents = {}
            for name in _FILES:
                raw = (bundle_dir / name).read_bytes()
                if hashlib.sha256(raw).hexdigest() != manifest["artifacts"][name]:
                    raise _bundle_error(f"artifact checksum mismatch: {name}")
                documents[name] = json.loads(raw)
        except (OSError, UnicodeError, json.JSONDecodeError, TypeError) as exc:
            raise _bundle_error(f"cannot read bundle: {exc}") from exc

        schema = documents["knowledge-record.schema.json"]
        request_schema = documents["inference-request.schema.json"]
        try:
            Draft202012Validator.check_schema(schema)
            Draft202012Validator.check_schema(request_schema)
        except SchemaError as exc:
            raise _bundle_error(f"invalid bundled schema: {exc.message}") from exc
        data = documents["knowledge.json"]
        if not isinstance(data, dict) or not isinstance(data.get("records"), list):
            raise _bundle_error("knowledge.json must contain a records list")
        self._kb = knowledge_from_records(
            ((bundle_dir / "knowledge.json", record) for record in data["records"]),
            Draft202012Validator(schema),
        )
        if self._kb.source_digest != manifest.get("source_semantic_digest"):
            raise _bundle_error("source semantic digest mismatch")
        counts = {kind: sum(record["record_type"] == kind for record in self._kb.records)
                  for kind in sorted({record["record_type"] for record in self._kb.records})}
        if counts != manifest.get("record_counts"):
            raise _bundle_error("record count mismatch")
        self._plans = compile_rules(self._kb)
        self._request_validator = Draft202012Validator(request_schema)
        self._manifest = manifest

    @property
    def manifest(self) -> dict[str, Any]:
        return deepcopy(self._manifest)

    def infer(self, request: dict[str, Any]) -> dict[str, Any]:
        """Malformed requests raise SourceError; chemistry outcomes retain their status."""
        error = next(self._request_validator.iter_errors(request), None)
        if error is not None:
            raise SourceError(error.message, code="request_invalid", stage="request_validation",
                              details={"location": "/".join(str(part) for part in error.absolute_path)})
        identifiers = [item["target_id"] for item in request["reactants"]]
        if len(identifiers) != len(set(identifiers)):
            raise SourceError("repeated reactant identities are not supported, including across phases",
                              code="request_invalid", stage="request_validation")
        return {
            "release_id": self._manifest["release_id"],
            "compiler_version": __version__,
            "source_semantic_digest": self._kb.source_digest,
            "result": infer_case(self._kb, self._plans, deepcopy(request)),
        }
