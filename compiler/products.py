from __future__ import annotations

from .model import ProductPlan
from .source import KnowledgeBase, SourceError


class ProductResolutionError(SourceError):
    pass


def resolve_product(kb: KnowledgeBase, plan: ProductPlan) -> str:
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
    raise ProductResolutionError(
        f"unknown product constructor: {plan.constructor}",
        code="schema_invalid",
        stage="product_resolution",
    )


def resolve_products(kb: KnowledgeBase, plans: tuple[ProductPlan, ...]) -> tuple[tuple[str, str], ...]:
    return tuple((resolve_product(kb, plan), plan.phase) for plan in plans)
