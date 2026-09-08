from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml
from jsonschema import Draft202012Validator

from .canonical import sha256_hex
from .model import FactValue, KnowledgeState


SOURCE_DIRS = ("knowledge/domain", "knowledge/rules")
SOURCE_SCHEMA_VERSION = "3.0.0"


class SourceError(ValueError):
    def __init__(
        self,
        message: str,
        *,
        code: str = "source_error",
        stage: str = "source",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.stage = stage
        self.details = details or {}

    @property
    def diagnostic(self) -> dict[str, Any]:
        result: dict[str, Any] = {"code": self.code, "stage": self.stage, "message": str(self)}
        if self.details:
            result["details"] = {key: self.details[key] for key in sorted(self.details)}
        return result


class UniqueKeyLoader(yaml.SafeLoader):
    pass


def _construct_mapping(loader: UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False) -> dict[str, Any]:
    mapping: dict[str, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise SourceError(
                f"duplicate YAML key: {key!r}",
                code="schema_invalid",
                stage="source_load",
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_mapping,
)


def load_yaml(path: Path) -> Any:
    try:
        return yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueKeyLoader)
    except yaml.YAMLError as exc:
        raise SourceError(
            f"invalid YAML in {path}: {exc}",
            code="schema_invalid",
            stage="source_load",
            details={"path": path.as_posix()},
        ) from exc


@dataclass(frozen=True)
class KnowledgeBase:
    records: tuple[dict[str, Any], ...]
    entities: dict[str, dict[str, Any]]
    reactions: dict[str, dict[str, Any]]
    rules: dict[str, dict[str, Any]]
    sources: dict[str, dict[str, Any]]
    evidence: dict[str, dict[str, Any]]
    semantic_keys: dict[tuple[str, str], tuple[str, ...]]
    source_digest: str

    def facet_fact(self, entity_id: str, facet_key: str) -> FactValue:
        entity = self.entities[entity_id]
        for assertion in entity.get("facet_assertions", []):
            if assertion["facet_key"] == facet_key:
                state = KnowledgeState(assertion.get("value_state", "known"))
                return FactValue(
                    state=state,
                    value=assertion.get("value"),
                    origin=assertion.get("fact_kind", "intrinsic"),
                )
        return FactValue(KnowledgeState.ABSENT, None, "intrinsic")

    def facet_state(self, entity_id: str, facet_key: str) -> tuple[str, Any]:
        """Compatibility projection for F2 callers."""
        fact = self.facet_fact(entity_id, facet_key)
        legacy_state = "unknown" if fact.state is KnowledgeState.ABSENT else fact.state.value
        return legacy_state, fact.value

    def semantic_key_candidates(self, scheme: str, value: str) -> tuple[str, ...]:
        return self.semantic_keys.get((scheme, value), ())


def _validator(repo_root: Path) -> Draft202012Validator:
    import json

    schema_path = repo_root / "schemas" / "knowledge-record.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    return Draft202012Validator(schema)


def _iter_record_files(repo_root: Path) -> Iterable[Path]:
    paths: list[Path] = []
    for relative in SOURCE_DIRS:
        root = repo_root / relative
        if root.exists():
            paths.extend(root.glob("*.yaml"))
    return sorted(paths, key=lambda path: path.as_posix())


def load_knowledge(repo_root: Path) -> KnowledgeBase:
    validator = _validator(repo_root)
    records: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for path in _iter_record_files(repo_root):
        doc = load_yaml(path)
        if not isinstance(doc, dict) or not isinstance(doc.get("records"), list):
            raise SourceError(
                f"{path} must contain a top-level records list",
                code="schema_invalid",
                stage="source_load",
                details={"path": path.as_posix()},
            )
        for record in doc["records"]:
            errors = sorted(validator.iter_errors(record), key=lambda e: list(e.absolute_path))
            if errors:
                error = errors[0]
                location = "/".join(str(part) for part in error.absolute_path)
                raise SourceError(
                    f"schema validation failed at {path}:{location}: {error.message}",
                    code="schema_invalid",
                    stage="source_schema",
                    details={"path": path.as_posix(), "location": location},
                )
            record_id = record["id"]
            if record_id in seen_ids:
                raise SourceError(
                    f"duplicate durable id: {record_id}",
                    code="schema_invalid",
                    stage="source_load",
                    details={"id": record_id},
                )
            seen_ids.add(record_id)
            records.append(record)

    records.sort(key=lambda record: (record["record_type"], record["id"]))
    by_type: dict[str, dict[str, dict[str, Any]]] = {
        kind: {} for kind in ("entity", "reaction", "rule", "source", "evidence")
    }
    for record in records:
        by_type[record["record_type"]][record["id"]] = record

    semantic_index: dict[tuple[str, str], list[str]] = {}
    for entity_id, entity in by_type["entity"].items():
        for key in entity.get("semantic_keys", []):
            semantic_index.setdefault((key["scheme"], key["value"]), []).append(entity_id)

    kb = KnowledgeBase(
        records=tuple(records),
        entities=by_type["entity"],
        reactions=by_type["reaction"],
        rules=by_type["rule"],
        sources=by_type["source"],
        evidence=by_type["evidence"],
        semantic_keys={key: tuple(sorted(ids)) for key, ids in semantic_index.items()},
        source_digest=sha256_hex(records),
    )
    validate_references(kb)
    return kb


def validate_references(kb: KnowledgeBase) -> None:
    for entity in kb.entities.values():
        composition = entity.get("payload", {}).get("composition")
        if composition:
            for component in composition.get("components", []):
                element_id = component["element_id"]
                target = kb.entities.get(element_id)
                if not target or target.get("entity_kind") != "element":
                    raise SourceError(
                        f"composition element ref does not resolve to element: {element_id}",
                        code="reference_unresolved",
                        stage="reference_validation",
                        details={"target_id": element_id},
                    )
        for evidence_id in entity.get("evidence_ids", []):
            _require(kb.evidence, evidence_id, "evidence")

    for evidence in kb.evidence.values():
        _require(kb.sources, evidence["source_id"], "source")

    for reaction in kb.reactions.values():
        _validate_participants(kb, reaction.get("participants", []), reaction["id"])
        for form in reaction.get("forms", []):
            _validate_participants(kb, form.get("participants", []), f"{reaction['id']}:{form['form_key']}")
        for evidence_id in reaction.get("evidence_ids", []):
            _require(kb.evidence, evidence_id, "evidence")

    for rule in kb.rules.values():
        for pattern in rule["match"]["reactants"]:
            if "target_id" in pattern:
                _require(kb.entities, pattern["target_id"], "entity")
        for product in rule["products"]:
            if "target_id" in product:
                _require(kb.entities, product["target_id"], "entity")
        for evidence_id in rule.get("evidence_ids", []):
            _require(kb.evidence, evidence_id, "evidence")


def _validate_participants(kb: KnowledgeBase, participants: list[dict[str, Any]], owner: str) -> None:
    for participant in participants:
        entity_id = participant["target_id"]
        entity = kb.entities.get(entity_id)
        if entity is None:
            raise SourceError(
                f"unresolved participant {entity_id} in {owner}",
                code="reference_unresolved",
                stage="reference_validation",
                details={"owner": owner, "target_id": entity_id},
            )
        if participant.get("target_kind") != entity.get("entity_kind"):
            raise SourceError(
                f"participant target_kind mismatch for {entity_id} in {owner}",
                code="schema_invalid",
                stage="reference_validation",
                details={"owner": owner, "target_id": entity_id},
            )


def _require(index: dict[str, Any], key: str, kind: str) -> None:
    if key not in index:
        raise SourceError(
            f"unresolved {kind} ref: {key}",
            code="reference_unresolved",
            stage="reference_validation",
            details={"kind": kind, "target_id": key},
        )


def load_cases(repo_root: Path) -> list[dict[str, Any]]:
    import json

    doc = load_yaml(repo_root / "knowledge" / "fixtures" / "f2_cases.yaml")
    schema = json.loads((repo_root / "schemas" / "f2-case.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(doc), key=lambda e: list(e.absolute_path))
    if errors:
        error = errors[0]
        raise SourceError(
            f"case schema validation failed: {error.message}",
            code="schema_invalid",
            stage="case_schema",
        )
    return doc["cases"]
