from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .aqueous import AqueousResolutionError, resolve_exchange, resolve_ionic_pair_from_sources
from .model import ProductPlan
from .source import KnowledgeBase, SourceError


class ProductResolutionError(SourceError):
    pass


@dataclass(frozen=True)
class ResolvedProduct:
    target_id: str
    phase: str
    speciation_profiles: tuple[dict[str, Any], ...] = ()
    relation_assertions: tuple[dict[str, Any], ...] = ()
    evidence_ids: tuple[str, ...] = ()


def _translate_aqueous_error(exc: AqueousResolutionError) -> ProductResolutionError:
    return ProductResolutionError(
        str(exc),
        code=exc.code,
        stage=exc.stage,
        details=exc.details,
    )


def resolve_product_detail(
    kb: KnowledgeBase,
    plan: ProductPlan,
    bindings: dict[str, str] | None = None,
    context: dict[str, Any] | None = None,
) -> ResolvedProduct:
    bindings = bindings or {}
    context = context or {}
    if plan.constructor == "exact_entity":
        assert plan.target_id is not None
        if plan.target_id not in kb.entities:
            raise ProductResolutionError(
                f"canonical product does not resolve: {plan.target_id}",
                code="product_unresolved",
                stage="product_resolution",
                details={"target_id": plan.target_id},
            )
        return ResolvedProduct(plan.target_id, plan.phase)
    if plan.constructor == "semantic_key":
        assert plan.scheme is not None and plan.value is not None
        candidates = kb.semantic_key_candidates(plan.scheme, plan.value)
        if len(candidates) != 1:
            raise ProductResolutionError(
                f"semantic product resolution is {'ambiguous' if candidates else 'unresolved'}: {plan.scheme}={plan.value}",
                code="product_unresolved",
                stage="product_resolution",
                details={
                    "scheme": plan.scheme,
                    "value": plan.value,
                    "candidates": list(candidates),
                },
            )
        return ResolvedProduct(candidates[0], plan.phase)
    if plan.constructor == "ionic_pair":
        assert plan.cation_source is not None and plan.anion_source is not None
        try:
            resolution = resolve_ionic_pair_from_sources(
                kb,
                bindings,
                plan.cation_source,
                plan.anion_source,
                context,
            )
            return ResolvedProduct(
                target_id=resolution.target_id,
                phase=plan.phase,
                speciation_profiles=resolution.speciation_profiles,
                relation_assertions=resolution.relation_assertions,
                evidence_ids=resolution.evidence_ids,
            )
        except AqueousResolutionError as exc:
            raise _translate_aqueous_error(exc) from exc
    if plan.constructor == "exchange_product":
        assert plan.left_binding is not None and plan.right_binding is not None and plan.exchange_role is not None
        resolution = resolve_exchange(kb, bindings[plan.left_binding], bindings[plan.right_binding], context)
        if resolution.status != "precipitate":
            diagnostic = resolution.diagnostic or {
                "code": "product_unresolved",
                "stage": "product_resolution",
                "message": "exchange product requested without a unique precipitation driving force",
                "details": {"status": resolution.status},
            }
            raise ProductResolutionError(
                diagnostic["message"],
                code=diagnostic["code"],
                stage=diagnostic["stage"],
                details=diagnostic.get("details", {}),
            )
        if plan.exchange_role == "precipitate":
            assert resolution.precipitate_id is not None
            return ResolvedProduct(resolution.precipitate_id, plan.phase, evidence_ids=resolution.evidence_ids)
        if plan.exchange_role == "counterproduct":
            assert resolution.counterproduct_id is not None
            return ResolvedProduct(resolution.counterproduct_id, plan.phase, evidence_ids=resolution.evidence_ids)
        raise ProductResolutionError(
            f"unknown exchange product role: {plan.exchange_role}",
            code="schema_invalid",
            stage="product_resolution",
        )
    raise ProductResolutionError(
        f"unknown product constructor: {plan.constructor}",
        code="schema_invalid",
        stage="product_resolution",
    )


def resolve_product(
    kb: KnowledgeBase,
    plan: ProductPlan,
    bindings: dict[str, str] | None = None,
    context: dict[str, Any] | None = None,
) -> str:
    return resolve_product_detail(kb, plan, bindings, context).target_id


def resolve_products_detailed(
    kb: KnowledgeBase,
    plans: tuple[ProductPlan, ...],
    bindings: dict[str, str] | None = None,
    context: dict[str, Any] | None = None,
) -> tuple[ResolvedProduct, ...]:
    return tuple(resolve_product_detail(kb, plan, bindings, context) for plan in plans)


def resolve_products(
    kb: KnowledgeBase,
    plans: tuple[ProductPlan, ...],
    bindings: dict[str, str] | None = None,
    context: dict[str, Any] | None = None,
) -> tuple[tuple[str, str], ...]:
    return tuple(
        (resolved.target_id, resolved.phase)
        for resolved in resolve_products_detailed(kb, plans, bindings, context)
    )
