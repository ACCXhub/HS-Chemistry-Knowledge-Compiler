from __future__ import annotations

from typing import Any

from .aqueous import AqueousResolutionError, resolve_exchange, resolve_ionic_pair_from_bindings
from .model import ProductPlan
from .source import KnowledgeBase, SourceError


class ProductResolutionError(SourceError):
    pass


def _translate_aqueous_error(exc: AqueousResolutionError) -> ProductResolutionError:
    return ProductResolutionError(
        str(exc),
        code=exc.code,
        stage=exc.stage,
        details=exc.details,
    )


def resolve_product(
    kb: KnowledgeBase,
    plan: ProductPlan,
    bindings: dict[str, str] | None = None,
    context: dict[str, Any] | None = None,
) -> str:
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
        return plan.target_id
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
        return candidates[0]
    if plan.constructor == "ionic_pair":
        assert plan.cation_from is not None and plan.anion_from is not None
        try:
            return resolve_ionic_pair_from_bindings(
                kb,
                bindings,
                plan.cation_from,
                plan.anion_from,
                context,
            ).target_id
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
            return resolution.precipitate_id
        if plan.exchange_role == "counterproduct":
            assert resolution.counterproduct_id is not None
            return resolution.counterproduct_id
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


def resolve_products(
    kb: KnowledgeBase,
    plans: tuple[ProductPlan, ...],
    bindings: dict[str, str] | None = None,
    context: dict[str, Any] | None = None,
) -> tuple[tuple[str, str], ...]:
    return tuple((resolve_product(kb, plan, bindings, context), plan.phase) for plan in plans)
