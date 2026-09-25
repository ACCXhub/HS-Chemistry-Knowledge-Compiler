from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .model import EntitySourcePlan
from .source import RELATION_CONTRACTS, SourceError


class EntitySourceResolutionError(SourceError):
    pass


@dataclass(frozen=True)
class EntityResolution:
    target_id: str
    speciation_profiles: tuple[dict[str, Any], ...] = ()
    relation_assertions: tuple[dict[str, Any], ...] = ()
    evidence_ids: tuple[str, ...] = ()


def compile_entity_source(
    source: dict[str, Any],
    bindings: set[str],
    *,
    allow_relation: bool = True,
) -> EntitySourcePlan:
    kind = source.get("kind")
    if kind == "exact_entity":
        target_id = source.get("target_id")
        if not isinstance(target_id, str) or not target_id:
            raise SourceError(
                "exact entity source requires target_id",
                code="schema_invalid",
                stage="rule_compile",
            )
        return EntitySourcePlan(kind=kind, target_id=target_id)
    if kind == "binding":
        binding = source.get("binding")
        if binding not in bindings:
            raise SourceError(
                f"entity source binding does not resolve: {binding}",
                code="reference_unresolved",
                stage="rule_compile",
                details={"binding": binding},
            )
        return EntitySourcePlan(kind=kind, binding=binding)
    if kind == "speciation_ion":
        binding = source.get("binding")
        if binding not in bindings:
            raise SourceError(
                f"entity source binding does not resolve: {binding}",
                code="reference_unresolved",
                stage="rule_compile",
                details={"binding": binding},
            )
        charge_sign = source.get("charge_sign")
        if charge_sign not in {"positive", "negative"}:
            raise SourceError(
                "speciation ion source requires positive or negative charge_sign",
                code="schema_invalid",
                stage="rule_compile",
            )
        return EntitySourcePlan(kind=kind, binding=binding, charge_sign=charge_sign)
    if kind == "relation_target":
        if not allow_relation:
            raise SourceError(
                "entity source permits at most one relation hop",
                code="schema_invalid",
                stage="rule_compile",
            )
        relation_key = source.get("relation_key")
        if relation_key not in RELATION_CONTRACTS:
            raise SourceError(
                f"unsupported entity-source relation key: {relation_key}",
                code="schema_invalid",
                stage="rule_compile",
                details={"relation_key": relation_key},
            )
        nested = source.get("source")
        if not isinstance(nested, dict):
            raise SourceError(
                "relation target source requires a typed source",
                code="schema_invalid",
                stage="rule_compile",
            )
        return EntitySourcePlan(
            kind=kind,
            relation_key=relation_key,
            source=compile_entity_source(nested, bindings, allow_relation=False),
        )
    raise SourceError(
        f"unknown entity source: {kind}",
        code="schema_invalid",
        stage="rule_compile",
        details={"entity_source": kind},
    )


def _charge(kb: Any, entity_id: str) -> int:
    entity = kb.entities.get(entity_id)
    payload = entity.get("payload", {}) if entity is not None else {}
    charge = payload.get("formal_charge")
    if (
        entity is None
        or entity.get("entity_kind") != "species"
        or payload.get("species_kind") != "ion"
        or not isinstance(charge, int)
        or isinstance(charge, bool)
    ):
        raise EntitySourceResolutionError(
            f"entity source target is not a canonical ion Species: {entity_id}",
            code="reference_unresolved" if entity is None else "schema_invalid",
            stage="entity_source_resolution",
            details={"target_id": entity_id},
        )
    return charge


def _profile_for(kb: Any, entity_id: str, context: dict[str, Any]) -> dict[str, Any]:
    profiles = kb.speciation_profiles(entity_id, context)
    if len(profiles) != 1:
        raise EntitySourceResolutionError(
            f"aqueous speciation is {'ambiguous' if profiles else 'unavailable'} for {entity_id}",
            code="speciation_ambiguous" if profiles else "speciation_unavailable",
            stage="aqueous_speciation",
            details={
                "target_id": entity_id,
                "profile_keys": sorted(profile["profile_key"] for profile in profiles),
            },
        )
    return profiles[0]


def _single_profile_ion(kb: Any, profile: dict[str, Any], charge_sign: str) -> str:
    candidates = [
        product["target_id"]
        for product in profile["products"]
        if (charge_sign == "positive" and _charge(kb, product["target_id"]) > 0)
        or (charge_sign == "negative" and _charge(kb, product["target_id"]) < 0)
    ]
    if len(candidates) != 1:
        raise EntitySourceResolutionError(
            f"speciation profile does not provide exactly one {charge_sign} ionic constituent",
            code="speciation_ambiguous",
            stage="aqueous_speciation",
            details={"profile_key": profile["profile_key"], "candidates": sorted(candidates)},
        )
    return candidates[0]


def resolve_entity_source(
    kb: Any,
    bindings: dict[str, str],
    source: EntitySourcePlan,
    context: dict[str, Any],
) -> EntityResolution:
    if source.kind == "exact_entity":
        assert source.target_id is not None
        entity = kb.entities.get(source.target_id)
        if entity is None:
            raise EntitySourceResolutionError(
                f"exact entity source target is unavailable: {source.target_id}",
                code="reference_unresolved",
                stage="entity_source_resolution",
                details={"target_id": source.target_id},
            )
        return EntityResolution(
            target_id=source.target_id,
            evidence_ids=tuple(sorted(entity.get("evidence_ids", []))),
        )
    if source.kind == "binding":
        assert source.binding is not None
        target_id = bindings[source.binding]
        if target_id not in kb.entities:
            raise EntitySourceResolutionError(
                f"bound entity source target is unavailable: {target_id}",
                code="reference_unresolved",
                stage="entity_source_resolution",
                details={"binding": source.binding, "target_id": target_id},
            )
        return EntityResolution(target_id=target_id)
    if source.kind == "speciation_ion":
        assert source.binding is not None and source.charge_sign is not None
        target_id = bindings[source.binding]
        profile = _profile_for(kb, target_id, context)
        ion_id = _single_profile_ion(kb, profile, source.charge_sign)
        provenance = {
            "target_id": target_id,
            "profile_key": profile["profile_key"],
            "model": profile["model"],
            "evidence_ids": sorted(profile.get("evidence_ids", [])),
        }
        return EntityResolution(
            target_id=ion_id,
            speciation_profiles=(provenance,),
            evidence_ids=tuple(provenance["evidence_ids"]),
        )
    if source.kind == "relation_target":
        assert source.source is not None and source.relation_key is not None
        resolved_source = resolve_entity_source(kb, bindings, source.source, context)
        assertions = kb.relation_assertions(resolved_source.target_id, source.relation_key, context)
        candidates = sorted({assertion["target_id"] for assertion in assertions})
        if len(candidates) != 1:
            raise EntitySourceResolutionError(
                f"relation target is {'ambiguous' if assertions else 'unavailable'} for "
                f"{resolved_source.target_id}:{source.relation_key}",
                code="relation_ambiguous" if assertions else "relation_unavailable",
                stage="relation_resolution",
                details={
                    "source_id": resolved_source.target_id,
                    "relation_key": source.relation_key,
                    "candidates": candidates,
                },
            )
        relation_assertions = tuple(
            sorted(
                resolved_source.relation_assertions + assertions,
                key=lambda item: (
                    item["source_id"],
                    item["relation_key"],
                    item["target_id"],
                    tuple(sorted(item["context"].items())),
                ),
            )
        )
        return EntityResolution(
            target_id=candidates[0],
            speciation_profiles=resolved_source.speciation_profiles,
            relation_assertions=relation_assertions,
            evidence_ids=tuple(
                sorted(set(resolved_source.evidence_ids) | {
                    evidence_id for assertion in assertions for evidence_id in assertion["evidence_ids"]
                })
            ),
        )
    raise EntitySourceResolutionError(
        f"unsupported entity source: {source.kind}",
        code="schema_invalid",
        stage="entity_source_resolution",
        details={"entity_source": source.kind},
    )
