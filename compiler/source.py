from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml
from jsonschema import Draft202012Validator

from .canonical import sha256_hex


SOURCE_DIRS = ("knowledge/domain", "knowledge/rules")


class SourceError(ValueError):
    pass


class UniqueKeyLoader(yaml.SafeLoader):
    pass


def _construct_mapping(loader: UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False) -> dict[str, Any]:
    mapping: dict[str, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise SourceError(f"duplicate YAML key: {key!r}")
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
        raise SourceError(f"invalid YAML in {path}: {exc}") from exc


@dataclass(frozen=True)
class KnowledgeBase:
    records: tuple[dict[str, Any], ...]
    entities: dict[str, dict[str, Any]]
    reactions: dict[str, dict[str, Any]]
    rules: dict[str, dict[str, Any]]
    sources: dict[str, dict[str, Any]]
    evidence: dict[str, dict[str, Any]]
    source_digest: str

    def facet_state(self, entity_id: str, facet_key: str) -> tuple[str, Any]:
        entity = self.entities[entity_id]
        for assertion in entity.get("facet_assertions", []):
            if assertion["facet_key"] == facet_key:
                return assertion.get("value_state", "known"), assertion.get("value")
        return "unknown", None


def _validator(repo_root: Path) -> Draft202012Validator:
    import json

    schema_path = repo_root / "schemas" / "f2-record.schema.json"
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
            raise SourceError(f"{path} must contain a top-level records list")
        for record in doc["records"]:
            errors = sorted(validator.iter_errors(record), key=lambda e: list(e.absolute_path))
            if errors:
                error = errors[0]
                location = "/".join(str(part) for part in error.absolute_path)
                raise SourceError(f"schema validation failed at {path}:{location}: {error.message}")
            record_id = record["id"]
            if record_id in seen_ids:
                raise SourceError(f"duplicate durable id: {record_id}")
            seen_ids.add(record_id)
            records.append(record)

    records.sort(key=lambda record: (record["record_type"], record["id"]))
    by_type: dict[str, dict[str, dict[str, Any]]] = {
        kind: {} for kind in ("entity", "reaction", "rule", "source", "evidence")
    }
    for record in records:
        by_type[record["record_type"]][record["id"]] = record

    kb = KnowledgeBase(
        records=tuple(records),
        entities=by_type["entity"],
        reactions=by_type["reaction"],
        rules=by_type["rule"],
        sources=by_type["source"],
        evidence=by_type["evidence"],
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
                    raise SourceError(f"composition element ref does not resolve to element: {element_id}")
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
            _require(kb.entities, pattern["target_id"], "entity")
        for product in rule["products"]:
            _require(kb.entities, product["target_id"], "entity")
        for evidence_id in rule.get("evidence_ids", []):
            _require(kb.evidence, evidence_id, "evidence")


def _validate_participants(kb: KnowledgeBase, participants: list[dict[str, Any]], owner: str) -> None:
    for participant in participants:
        entity_id = participant["target_id"]
        entity = kb.entities.get(entity_id)
        if entity is None:
            raise SourceError(f"unresolved participant {entity_id} in {owner}")
        if participant.get("target_kind") != entity.get("entity_kind"):
            raise SourceError(f"participant target_kind mismatch for {entity_id} in {owner}")


def _require(index: dict[str, Any], key: str, kind: str) -> None:
    if key not in index:
        raise SourceError(f"unresolved {kind} ref: {key}")


def load_cases(repo_root: Path) -> list[dict[str, Any]]:
    import json

    doc = load_yaml(repo_root / "knowledge" / "fixtures" / "f2_cases.yaml")
    schema = json.loads((repo_root / "schemas" / "f2-case.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(doc), key=lambda e: list(e.absolute_path))
    if errors:
        error = errors[0]
        raise SourceError(f"case schema validation failed: {error.message}")
    return doc["cases"]
