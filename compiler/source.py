from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml
from jsonschema import Draft202012Validator

from .canonical import sha256_hex
from .model import FactValue, KnowledgeState


SOURCE_DIRS = ("knowledge/domain", "knowledge/rules", "knowledge/teaching")
SOURCE_SCHEMA_VERSION = "3.2.0"
RELATION_CONTRACTS = {
    "metal.product_cation": {
        "source_entity_kind": "substance",
        "source_substance_kind": "elemental",
        "source_required_facet": "classification.metal",
        "target_entity_kind": "species",
        "target_species_kind": "ion",
        "target_charge_sign": "positive",
    }
}


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


def _context_tuple(context: dict[str, Any] | None) -> tuple[tuple[str, Any], ...]:
    return tuple(sorted((context or {}).items()))


def _context_matches(assertion_context: dict[str, Any] | None, requested: dict[str, Any]) -> bool:
    return all(requested.get(key) == value for key, value in (assertion_context or {}).items())


@dataclass(frozen=True)
class KnowledgeBase:
    records: tuple[dict[str, Any], ...]
    entities: dict[str, dict[str, Any]]
    reactions: dict[str, dict[str, Any]]
    rules: dict[str, dict[str, Any]]
    sources: dict[str, dict[str, Any]]
    evidence: dict[str, dict[str, Any]]
    teaching_views: dict[str, dict[str, Any]]
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
                    evidence_ids=tuple(sorted(assertion.get("evidence_ids", []))),
                )
        return FactValue(KnowledgeState.ABSENT, None, "intrinsic")

    def property_fact(self, entity_id: str, property_key: str, context: dict[str, Any]) -> FactValue:
        entity = self.entities[entity_id]
        matches = [
            assertion
            for assertion in entity.get("property_assertions", [])
            if assertion["property_key"] == property_key and _context_matches(assertion.get("context"), context)
        ]
        if not matches:
            return FactValue(KnowledgeState.ABSENT, None, "contextual")
        specificity = max(len(assertion.get("context", {})) for assertion in matches)
        matches = [assertion for assertion in matches if len(assertion.get("context", {})) == specificity]
        signatures = {
            (
                assertion.get("value_state", "known"),
                repr(assertion.get("value")),
                assertion.get("fact_kind", "contextual"),
                _context_tuple(assertion.get("context")),
            )
            for assertion in matches
        }
        if len(signatures) != 1:
            raise SourceError(
                f"ambiguous contextual property fact: {entity_id}:{property_key}",
                code="contextual_fact_ambiguous",
                stage="fact_resolution",
                details={"entity_id": entity_id, "property_key": property_key},
            )
        assertion = sorted(matches, key=lambda item: _context_tuple(item.get("context")))[0]
        return FactValue(
            state=KnowledgeState(assertion.get("value_state", "known")),
            value=assertion.get("value"),
            origin=assertion.get("fact_kind", "contextual"),
            context=_context_tuple(assertion.get("context")),
            evidence_ids=tuple(sorted(assertion.get("evidence_ids", []))),
        )

    def relation_assertions(
        self,
        entity_id: str,
        relation_key: str,
        context: dict[str, Any],
    ) -> tuple[dict[str, Any], ...]:
        entity = self.entities[entity_id]
        matches = [
            assertion
            for assertion in entity.get("relation_assertions", [])
            if assertion["relation_key"] == relation_key
            and _context_matches(assertion.get("context"), context)
        ]
        if not matches:
            return ()
        specificity = max(len(assertion.get("context", {})) for assertion in matches)
        most_specific = [
            assertion
            for assertion in matches
            if len(assertion.get("context", {})) == specificity
        ]
        return tuple(
            {
                "source_id": entity_id,
                "relation_key": assertion["relation_key"],
                "target_id": assertion["target_id"],
                "context": dict(sorted(assertion.get("context", {}).items())),
                "evidence_ids": sorted(assertion.get("evidence_ids", [])),
            }
            for assertion in sorted(
                most_specific,
                key=lambda item: (
                    item["target_id"],
                    _context_tuple(item.get("context")),
                    tuple(sorted(item.get("evidence_ids", []))),
                ),
            )
        )

    def speciation_profiles(self, entity_id: str, context: dict[str, Any]) -> tuple[dict[str, Any], ...]:
        entity = self.entities[entity_id]
        matches = [
            profile
            for profile in entity.get("speciation_profiles", [])
            if _context_matches(profile.get("context"), context)
        ]
        if not matches:
            return ()
        specificity = max(len(profile.get("context", {})) for profile in matches)
        return tuple(
            sorted(
                (profile for profile in matches if len(profile.get("context", {})) == specificity),
                key=lambda profile: (profile["profile_key"], _context_tuple(profile.get("context"))),
            )
        )

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


def _validate_assertion_uniqueness(record: dict[str, Any]) -> None:
    property_keys: set[tuple[str, tuple[tuple[str, Any], ...]]] = set()
    for assertion in record.get("property_assertions", []):
        key = (assertion["property_key"], _context_tuple(assertion.get("context")))
        if key in property_keys:
            raise SourceError(
                f"duplicate contextual property assertion: {record['id']}:{assertion['property_key']}",
                code="schema_invalid",
                stage="source_load",
                details={"entity_id": record["id"], "property_key": assertion["property_key"]},
            )
        property_keys.add(key)

    relation_keys: set[tuple[str, tuple[tuple[str, Any], ...]]] = set()
    for assertion in record.get("relation_assertions", []):
        key = (assertion["relation_key"], _context_tuple(assertion.get("context")))
        if key in relation_keys:
            raise SourceError(
                f"duplicate contextual relation assertion: {record['id']}:{assertion['relation_key']}",
                code="schema_invalid",
                stage="source_load",
                details={"entity_id": record["id"], "relation_key": assertion["relation_key"]},
            )
        relation_keys.add(key)

    profile_keys: set[tuple[str, tuple[tuple[str, Any], ...]]] = set()
    for profile in record.get("speciation_profiles", []):
        key = (profile["profile_key"], _context_tuple(profile.get("context")))
        if key in profile_keys:
            raise SourceError(
                f"duplicate speciation profile: {record['id']}:{profile['profile_key']}",
                code="schema_invalid",
                stage="source_load",
                details={"entity_id": record["id"], "profile_key": profile["profile_key"]},
            )
        profile_keys.add(key)


def _validate_reaction_condition_uniqueness(record: dict[str, Any]) -> None:
    condition_keys: set[str] = set()
    for condition in record.get("conditions", []):
        key = condition["key"]
        if key in condition_keys:
            raise SourceError(
                f"duplicate reaction condition: {record['id']}:{key}",
                code="schema_invalid",
                stage="source_load",
                details={"reaction_id": record["id"], "condition_key": key},
            )
        condition_keys.add(key)


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
            if record.get("record_type") == "entity":
                _validate_assertion_uniqueness(record)
            if record.get("record_type") == "reaction":
                _validate_reaction_condition_uniqueness(record)
                if "conditions" in record:
                    record["conditions"] = sorted(
                        record["conditions"],
                        key=lambda condition: (condition["key"], condition["value"]),
                    )
            seen_ids.add(record_id)
            records.append(record)

    records.sort(key=lambda record: (record["record_type"], record["id"]))
    by_type: dict[str, dict[str, dict[str, Any]]] = {
        kind: {} for kind in ("entity", "reaction", "rule", "source", "evidence", "teaching_view")
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
        teaching_views=by_type["teaching_view"],
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
        for assertion in entity.get("facet_assertions", []):
            for evidence_id in assertion.get("evidence_ids", []):
                _require(kb.evidence, evidence_id, "evidence")
        for assertion in entity.get("property_assertions", []):
            for evidence_id in assertion.get("evidence_ids", []):
                _require(kb.evidence, evidence_id, "evidence")
        for assertion in entity.get("relation_assertions", []):
            relation_key = assertion["relation_key"]
            contract = RELATION_CONTRACTS[relation_key]
            source_payload = entity.get("payload", {})
            required_facet = contract["source_required_facet"]
            has_required_facet = any(
                item["facet_key"] == required_facet
                and item.get("value_state", "known") == "known"
                and item.get("value") is True
                for item in entity.get("facet_assertions", [])
            )
            if (
                entity.get("entity_kind") != contract["source_entity_kind"]
                or source_payload.get("substance_kind") != contract["source_substance_kind"]
                or not has_required_facet
            ):
                raise SourceError(
                    f"relation source does not satisfy {relation_key} contract: {entity['id']}",
                    code="schema_invalid",
                    stage="reference_validation",
                    details={
                        "relation_key": relation_key,
                        "source_id": entity["id"],
                        "source_entity_kind": contract["source_entity_kind"],
                        "source_required_facet": required_facet,
                        "source_substance_kind": contract["source_substance_kind"],
                    },
                )
            expected_kind = contract["target_entity_kind"]
            target_id = assertion["target_id"]
            target = kb.entities.get(target_id)
            if not target or target.get("entity_kind") != expected_kind:
                raise SourceError(
                    f"relation target does not resolve to {expected_kind}: {target_id}",
                    code="reference_unresolved",
                    stage="reference_validation",
                    details={
                        "relation_key": relation_key,
                        "source_id": entity["id"],
                        "target_id": target_id,
                        "target_kind": expected_kind,
                    },
                )
            target_payload = target.get("payload", {})
            formal_charge = target_payload.get("formal_charge")
            if (
                target_payload.get("species_kind") != contract["target_species_kind"]
                or not isinstance(formal_charge, int)
                or isinstance(formal_charge, bool)
                or formal_charge <= 0
            ):
                raise SourceError(
                    f"relation target does not satisfy {relation_key} positive-ion contract: {target_id}",
                    code="schema_invalid",
                    stage="reference_validation",
                    details={
                        "relation_key": relation_key,
                        "source_id": entity["id"],
                        "target_charge_sign": contract["target_charge_sign"],
                        "target_id": target_id,
                        "target_species_kind": contract["target_species_kind"],
                    },
                )
            for evidence_id in assertion.get("evidence_ids", []):
                _require(kb.evidence, evidence_id, "evidence")
        for profile in entity.get("speciation_profiles", []):
            for product in profile["products"]:
                target = kb.entities.get(product["target_id"])
                if not target or target.get("entity_kind") != "species":
                    raise SourceError(
                        f"speciation product does not resolve to species: {product['target_id']}",
                        code="reference_unresolved",
                        stage="reference_validation",
                        details={"target_id": product["target_id"]},
                    )
            for evidence_id in profile.get("evidence_ids", []):
                _require(kb.evidence, evidence_id, "evidence")
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
        for condition in reaction.get("conditions", []):
            for evidence_id in condition.get("evidence_ids", []):
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

    resolvable_members = set(kb.entities) | set(kb.reactions)
    for view in kb.teaching_views.values():
        path_keys: set[str] = set()
        for node in view["nodes"]:
            if node["path_key"] in path_keys:
                raise SourceError(
                    f"duplicate teaching path in {view['id']}: {node['path_key']}",
                    code="schema_invalid",
                    stage="reference_validation",
                    details={"view_id": view["id"], "path_key": node["path_key"]},
                )
            path_keys.add(node["path_key"])
            for member in node.get("members", []):
                if member not in resolvable_members:
                    raise SourceError(
                        f"unresolved teaching view member: {member}",
                        code="reference_unresolved",
                        stage="reference_validation",
                        details={"view_id": view["id"], "target_id": member},
                    )


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
        if entity.get("entity_kind") == "material_system":
            raise SourceError(
                f"material_system requires an explicit stoichiometric projection basis: {entity_id}",
                code="stoichiometric_basis_required",
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
