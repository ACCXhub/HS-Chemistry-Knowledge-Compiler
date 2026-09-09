from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from math import gcd
from typing import Any

from .model import FactValue, IonSourcePlan, KnowledgeState
from .source import KnowledgeBase, SourceError


class AqueousResolutionError(SourceError):
    pass


@dataclass(frozen=True)
class IonicPairResolution:
    target_id: str
    cation_id: str
    anion_id: str
    cation_coefficient: int
    anion_coefficient: int
    speciation_profiles: tuple[dict[str, Any], ...] = ()
    relation_assertions: tuple[dict[str, Any], ...] = ()
    evidence_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class ExchangeResolution:
    status: str
    products: tuple[IonicPairResolution, ...] = ()
    precipitate_id: str | None = None
    counterproduct_id: str | None = None
    evidence_ids: tuple[str, ...] = ()
    diagnostic: dict[str, Any] | None = None


def _charge(kb: KnowledgeBase, species_id: str) -> int:
    entity = kb.entities.get(species_id)
    if entity is None or entity.get("entity_kind") != "species":
        raise AqueousResolutionError(
            f"ionic constituent does not resolve to species: {species_id}",
            code="reference_unresolved",
            stage="aqueous_product_resolution",
            details={"target_id": species_id},
        )
    return int(entity.get("payload", {}).get("formal_charge", 0))


def _composition(kb: KnowledgeBase, entity_id: str) -> Counter[str]:
    entity = kb.entities[entity_id]
    composition = entity.get("payload", {}).get("composition")
    if not composition:
        raise AqueousResolutionError(
            f"missing exact composition for ionic constituent: {entity_id}",
            code="product_unresolved",
            stage="aqueous_product_resolution",
            details={"target_id": entity_id},
        )
    return Counter({item["element_id"]: item["count"] for item in composition["components"]})


def _scaled_composition(composition: Counter[str], coefficient: int) -> Counter[str]:
    if coefficient <= 0:
        raise ValueError("composition coefficient must be a positive integer")
    return Counter({element_id: count * coefficient for element_id, count in composition.items()})


def _profile_for(kb: KnowledgeBase, entity_id: str, context: dict[str, Any]) -> dict[str, Any]:
    profiles = kb.speciation_profiles(entity_id, context)
    if len(profiles) != 1:
        raise AqueousResolutionError(
            f"aqueous speciation is {'ambiguous' if profiles else 'unavailable'} for {entity_id}",
            code="speciation_ambiguous" if profiles else "speciation_unavailable",
            stage="aqueous_speciation",
            details={
                "target_id": entity_id,
                "profile_keys": sorted(profile["profile_key"] for profile in profiles),
            },
        )
    return profiles[0]


def _single_profile_ion(kb: KnowledgeBase, profile: dict[str, Any], sign: str) -> str:
    candidates: list[str] = []
    for product in profile["products"]:
        charge = _charge(kb, product["target_id"])
        if (sign == "positive" and charge > 0) or (sign == "negative" and charge < 0):
            candidates.append(product["target_id"])
    if len(candidates) != 1:
        raise AqueousResolutionError(
            f"speciation profile does not provide exactly one {sign} ionic constituent",
            code="speciation_ambiguous",
            stage="aqueous_speciation",
            details={"profile_key": profile["profile_key"], "candidates": sorted(candidates)},
        )
    return candidates[0]


def resolve_ionic_pair(kb: KnowledgeBase, cation_id: str, anion_id: str) -> IonicPairResolution:
    cation_charge = _charge(kb, cation_id)
    anion_charge = _charge(kb, anion_id)
    if cation_charge <= 0 or anion_charge >= 0:
        raise AqueousResolutionError(
            "ionic_pair requires a positive cation and negative anion",
            code="schema_invalid",
            stage="aqueous_product_resolution",
            details={"cation_id": cation_id, "anion_id": anion_id},
        )
    divisor = gcd(cation_charge, abs(anion_charge))
    cation_coefficient = abs(anion_charge) // divisor
    anion_coefficient = cation_charge // divisor
    expected = _scaled_composition(_composition(kb, cation_id), cation_coefficient)
    expected.update(_scaled_composition(_composition(kb, anion_id), anion_coefficient))

    candidates: list[str] = []
    for entity_id, entity in sorted(kb.entities.items()):
        if entity.get("entity_kind") != "substance":
            continue
        payload = entity.get("payload", {})
        composition = payload.get("composition")
        if not composition or int(composition.get("net_charge", 0)) != 0:
            continue
        actual = Counter({item["element_id"]: item["count"] for item in composition["components"]})
        if actual == expected:
            candidates.append(entity_id)
    if len(candidates) != 1:
        raise AqueousResolutionError(
            f"ionic product resolution is {'ambiguous' if candidates else 'unresolved'} for {cation_id} + {anion_id}",
            code="product_unresolved",
            stage="aqueous_product_resolution",
            details={"cation_id": cation_id, "anion_id": anion_id, "candidates": candidates},
        )
    return IonicPairResolution(
        target_id=candidates[0],
        cation_id=cation_id,
        anion_id=anion_id,
        cation_coefficient=cation_coefficient,
        anion_coefficient=anion_coefficient,
    )


def _resolve_ion_source(
    kb: KnowledgeBase,
    bindings: dict[str, str],
    source: IonSourcePlan,
    sign: str,
    context: dict[str, Any],
) -> tuple[str, tuple[dict[str, Any], ...], tuple[dict[str, Any], ...], tuple[str, ...]]:
    source_id = bindings[source.binding]
    if source.kind == "speciation":
        profile = _profile_for(kb, source_id, context)
        ion_id = _single_profile_ion(kb, profile, sign)
        provenance = {
            "target_id": source_id,
            "profile_key": profile["profile_key"],
            "model": profile["model"],
            "evidence_ids": sorted(profile.get("evidence_ids", [])),
        }
        return ion_id, (provenance,), (), tuple(provenance["evidence_ids"])
    if source.kind == "relation_target":
        assert source.relation_key is not None
        assertions = kb.relation_assertions(source_id, source.relation_key, context)
        if len(assertions) != 1:
            candidates = sorted(assertion["target_id"] for assertion in assertions)
            raise AqueousResolutionError(
                f"relation target is {'ambiguous' if assertions else 'unavailable'} for {source_id}:{source.relation_key}",
                code="relation_ambiguous" if assertions else "relation_unavailable",
                stage="relation_resolution",
                details={
                    "source_id": source_id,
                    "relation_key": source.relation_key,
                    "candidates": candidates,
                },
            )
        assertion = assertions[0]
        return (
            assertion["target_id"],
            (),
            (assertion,),
            tuple(assertion["evidence_ids"]),
        )
    raise AqueousResolutionError(
        f"unsupported ionic-pair ion source: {source.kind}",
        code="schema_invalid",
        stage="aqueous_product_resolution",
        details={"ion_source": source.kind},
    )


def resolve_ionic_pair_from_sources(
    kb: KnowledgeBase,
    bindings: dict[str, str],
    cation_source: IonSourcePlan,
    anion_source: IonSourcePlan,
    context: dict[str, Any],
) -> IonicPairResolution:
    cation, cation_profiles, cation_relations, cation_evidence = _resolve_ion_source(
        kb, bindings, cation_source, "positive", context
    )
    anion, anion_profiles, anion_relations, anion_evidence = _resolve_ion_source(
        kb, bindings, anion_source, "negative", context
    )
    resolved = resolve_ionic_pair(kb, cation, anion)
    profiles = tuple(
        sorted(cation_profiles + anion_profiles, key=lambda item: (item["target_id"], item["profile_key"]))
    )
    relations = tuple(
        sorted(
            cation_relations + anion_relations,
            key=lambda item: (
                item["source_id"],
                item["relation_key"],
                item["target_id"],
                tuple(sorted(item["context"].items())),
            ),
        )
    )
    evidence_ids = tuple(sorted(set(cation_evidence) | set(anion_evidence)))
    return IonicPairResolution(
        target_id=resolved.target_id,
        cation_id=resolved.cation_id,
        anion_id=resolved.anion_id,
        cation_coefficient=resolved.cation_coefficient,
        anion_coefficient=resolved.anion_coefficient,
        speciation_profiles=profiles,
        relation_assertions=relations,
        evidence_ids=evidence_ids,
    )


def resolve_ionic_pair_from_bindings(
    kb: KnowledgeBase,
    bindings: dict[str, str],
    cation_binding: str,
    anion_binding: str,
    context: dict[str, Any],
) -> IonicPairResolution:
    """Compatibility wrapper for the legacy speciation-only boundary."""
    return resolve_ionic_pair_from_sources(
        kb,
        bindings,
        IonSourcePlan(kind="speciation", binding=cation_binding),
        IonSourcePlan(kind="speciation", binding=anion_binding),
        context,
    )


def resolve_exchange(kb: KnowledgeBase, left_id: str, right_id: str, context: dict[str, Any]) -> ExchangeResolution:
    try:
        left_profile = _profile_for(kb, left_id, context)
        right_profile = _profile_for(kb, right_id, context)
        left_cation = _single_profile_ion(kb, left_profile, "positive")
        left_anion = _single_profile_ion(kb, left_profile, "negative")
        right_cation = _single_profile_ion(kb, right_profile, "positive")
        right_anion = _single_profile_ion(kb, right_profile, "negative")
        products = (
            resolve_ionic_pair(kb, left_cation, right_anion),
            resolve_ionic_pair(kb, right_cation, left_anion),
        )
    except AqueousResolutionError as exc:
        return ExchangeResolution(status="unknown", diagnostic=exc.diagnostic)

    classes: list[tuple[IonicPairResolution, FactValue]] = []
    evidence_ids: set[str] = set(left_profile.get("evidence_ids", [])) | set(right_profile.get("evidence_ids", []))
    for product in products:
        fact = kb.property_fact(product.target_id, "solubility.class", context)
        classes.append((product, fact))
        evidence_ids.update(fact.evidence_ids)
    if any(fact.state is not KnowledgeState.KNOWN for _, fact in classes):
        return ExchangeResolution(
            status="unknown",
            products=products,
            evidence_ids=tuple(sorted(evidence_ids)),
            diagnostic={
                "code": "solubility_unknown",
                "stage": "aqueous_driving_force",
                "message": "exchange product solubility is not fully known in the requested context",
                "details": {"products": sorted(product.target_id for product, _ in classes)},
            },
        )
    insoluble = [product for product, fact in classes if fact.value == "insoluble"]
    soluble = [product for product, fact in classes if fact.value == "soluble"]
    if len(insoluble) == 1 and len(soluble) == 1:
        return ExchangeResolution(
            status="precipitate",
            products=products,
            precipitate_id=insoluble[0].target_id,
            counterproduct_id=soluble[0].target_id,
            evidence_ids=tuple(sorted(evidence_ids)),
        )
    if not insoluble and len(soluble) == 2:
        return ExchangeResolution(
            status="none",
            products=products,
            evidence_ids=tuple(sorted(evidence_ids)),
        )
    return ExchangeResolution(
        status="unknown",
        products=products,
        evidence_ids=tuple(sorted(evidence_ids)),
        diagnostic={
            "code": "driving_force_ambiguous",
            "stage": "aqueous_driving_force",
            "message": "bounded precipitation model cannot select exactly one insoluble product",
            "details": {"products": sorted(product.target_id for product in products)},
        },
    )


def exchange_driving_force_fact(
    kb: KnowledgeBase,
    left_id: str,
    right_id: str,
    context: dict[str, Any],
) -> FactValue:
    resolution = resolve_exchange(kb, left_id, right_id, context)
    if resolution.status == "unknown":
        return FactValue(
            KnowledgeState.UNKNOWN,
            None,
            "derived",
            evidence_ids=resolution.evidence_ids,
        )
    return FactValue(
        KnowledgeState.KNOWN,
        resolution.status,
        "derived",
        evidence_ids=resolution.evidence_ids,
    )
