from __future__ import annotations

from typing import Any

from .model import PredicatePlan, RulePlan, Truth
from .source import KnowledgeBase, SourceError


def compile_rules(kb: KnowledgeBase) -> tuple[RulePlan, ...]:
    plans: list[RulePlan] = []
    for rule_id in sorted(kb.rules):
        source = kb.rules[rule_id]
        bindings = tuple(
            (pattern["bind"], pattern["target_id"])
            for pattern in source["match"]["reactants"]
        )
        if len({name for name, _ in bindings}) != len(bindings):
            raise SourceError(f"duplicate binding in {rule_id}")
        predicates: list[PredicatePlan] = []
        for pattern in source["match"]["reactants"]:
            for facet_key in pattern.get("required_facets", []):
                predicates.append(
                    PredicatePlan(
                        operator="facet_true",
                        binding=pattern["bind"],
                        key=facet_key,
                        expected=True,
                    )
                )
        for key, expected in sorted(source.get("context", {}).items()):
            predicates.append(PredicatePlan(operator="context_equals", key=key, expected=expected))
        blockers = tuple(
            PredicatePlan(operator="context_equals", key=item["key"], expected=item["equals"])
            for item in source.get("blockers", [])
        )
        plans.append(
            RulePlan(
                rule_id=rule_id,
                version=source["version"],
                decision_domain=source["decision_domain"],
                bindings=bindings,
                predicates=tuple(predicates),
                blockers=blockers,
                products=tuple((item["target_id"], item["phase"]) for item in source["products"]),
                validators=tuple(source.get("validators", [])),
                evidence_ids=tuple(source.get("evidence_ids", [])),
            )
        )
    return tuple(plans)


def bind_rule(plan: RulePlan, reactant_ids: tuple[str, ...]) -> dict[str, str] | None:
    expected_ids = [entity_id for _, entity_id in plan.bindings]
    if sorted(expected_ids) != sorted(reactant_ids):
        return None
    remaining = list(reactant_ids)
    bound: dict[str, str] = {}
    for binding, expected_id in plan.bindings:
        index = remaining.index(expected_id)
        bound[binding] = remaining.pop(index)
    return bound


def evaluate_predicate(
    predicate: PredicatePlan,
    kb: KnowledgeBase,
    bindings: dict[str, str],
    context: dict[str, Any],
) -> tuple[Truth, str]:
    if predicate.operator == "context_equals":
        if predicate.key not in context:
            return Truth.UNKNOWN, "UNKNOWN"
        return (
            (Truth.TRUE, "KNOWN")
            if context[predicate.key] == predicate.expected
            else (Truth.FALSE, "KNOWN")
        )
    if predicate.operator == "facet_true":
        assert predicate.binding is not None and predicate.key is not None
        entity_id = bindings[predicate.binding]
        state, value = kb.facet_state(entity_id, predicate.key)
        if state == "unknown":
            return Truth.UNKNOWN, "UNKNOWN"
        if state == "not_applicable":
            return Truth.UNKNOWN, "NOT_APPLICABLE"
        return ((Truth.TRUE, "KNOWN") if value is True else (Truth.FALSE, "KNOWN"))
    raise SourceError(f"unknown predicate operator: {predicate.operator}")
