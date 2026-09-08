from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .aqueous import exchange_driving_force_fact
from .model import FactValue, KnowledgeState, PredicatePlan, Truth
from .source import KnowledgeBase, SourceError


_SCALAR_TYPES = (str, bool, int)


@dataclass(frozen=True)
class OperatorSpec:
    name: str
    allowed_subjects: frozenset[str]
    expected_shape: str
    input_types: tuple[str, ...]
    unknown_is_unknown: bool


_FACT_SUBJECTS = frozenset({"context", "facet", "property", "ionic_exchange"})
OPERATOR_REGISTRY: dict[str, OperatorSpec] = {
    "equals": OperatorSpec("equals", _FACT_SUBJECTS, "scalar", ("string", "boolean", "integer"), True),
    "not_equals": OperatorSpec("not_equals", _FACT_SUBJECTS, "scalar", ("string", "boolean", "integer"), True),
    "is_known": OperatorSpec("is_known", _FACT_SUBJECTS, "none", ("any_fact_state",), False),
    "in_set": OperatorSpec("in_set", frozenset({"context", "facet", "property"}), "scalar_list", ("string", "boolean", "integer"), True),
}


def compile_predicate(source: dict[str, Any], bindings: set[str]) -> PredicatePlan:
    operator = source.get("operator")
    if operator not in OPERATOR_REGISTRY:
        raise SourceError(
            f"unknown predicate operator: {operator}",
            code="schema_invalid",
            stage="rule_compile",
            details={"operator": operator},
        )
    spec = OPERATOR_REGISTRY[operator]
    subject = source.get("subject", "context")
    if subject not in spec.allowed_subjects:
        raise SourceError(
            f"operator {operator} does not support subject {subject}",
            code="schema_invalid",
            stage="rule_compile",
            details={"operator": operator, "subject": subject},
        )
    binding = source.get("binding")
    predicate_bindings = tuple(source.get("bindings", []))
    key = source.get("key")
    if not isinstance(key, str) or not key:
        raise SourceError("predicate key must be a non-empty string", code="schema_invalid", stage="rule_compile")

    if subject in {"facet", "property"}:
        if binding not in bindings:
            raise SourceError(
                f"predicate binding does not resolve: {binding}",
                code="reference_unresolved",
                stage="rule_compile",
                details={"binding": binding},
            )
        if predicate_bindings:
            raise SourceError(
                f"{subject} predicate cannot declare bindings",
                code="schema_invalid",
                stage="rule_compile",
            )
    elif subject == "context":
        if binding is not None or predicate_bindings:
            raise SourceError(
                "context predicate cannot declare participant bindings",
                code="schema_invalid",
                stage="rule_compile",
            )
    elif subject == "ionic_exchange":
        if binding is not None or len(predicate_bindings) != 2 or any(item not in bindings for item in predicate_bindings):
            raise SourceError(
                "ionic_exchange predicate requires exactly two valid bindings",
                code="schema_invalid",
                stage="rule_compile",
                details={"bindings": list(predicate_bindings)},
            )
        if key != "driving_force":
            raise SourceError(
                f"unsupported ionic_exchange predicate key: {key}",
                code="schema_invalid",
                stage="rule_compile",
                details={"key": key},
            )

    has_expected = "expected" in source
    expected = source.get("expected")
    if spec.expected_shape == "none":
        if has_expected:
            raise SourceError(
                f"operator {operator} does not accept expected",
                code="schema_invalid",
                stage="rule_compile",
            )
    elif spec.expected_shape == "scalar":
        if not has_expected or not isinstance(expected, _SCALAR_TYPES):
            raise SourceError(
                f"operator {operator} requires scalar expected",
                code="schema_invalid",
                stage="rule_compile",
                details={"operator": operator},
            )
    elif spec.expected_shape == "scalar_list":
        if (
            not has_expected
            or not isinstance(expected, list)
            or not expected
            or any(not isinstance(item, _SCALAR_TYPES) for item in expected)
        ):
            raise SourceError(
                f"operator {operator} requires non-empty scalar-list expected",
                code="schema_invalid",
                stage="rule_compile",
                details={"operator": operator},
            )
        expected_types = {type(item) for item in expected}
        if len(expected_types) != 1:
            raise SourceError(
                f"operator {operator} requires homogeneous expected values",
                code="schema_invalid",
                stage="rule_compile",
                details={"operator": operator},
            )
    return PredicatePlan(
        operator=operator,
        subject=subject,
        binding=binding,
        bindings=predicate_bindings,
        key=key,
        expected=expected,
    )


def _fact_for(
    predicate: PredicatePlan,
    kb: KnowledgeBase,
    bindings: dict[str, str],
    context: dict[str, Any],
) -> FactValue:
    assert predicate.key is not None
    if predicate.subject == "context":
        if predicate.key not in context:
            return FactValue(KnowledgeState.ABSENT, None, "contextual")
        return FactValue(
            KnowledgeState.KNOWN,
            context[predicate.key],
            "contextual",
            context=((predicate.key, context[predicate.key]),),
        )
    if predicate.subject == "facet":
        assert predicate.binding is not None
        return kb.facet_fact(bindings[predicate.binding], predicate.key)
    if predicate.subject == "property":
        assert predicate.binding is not None
        return kb.property_fact(bindings[predicate.binding], predicate.key, context)
    if predicate.subject == "ionic_exchange":
        left_binding, right_binding = predicate.bindings
        return exchange_driving_force_fact(kb, bindings[left_binding], bindings[right_binding], context)
    raise SourceError(f"unsupported predicate subject: {predicate.subject}")


def evaluate_predicate(
    predicate: PredicatePlan,
    kb: KnowledgeBase,
    bindings: dict[str, str],
    context: dict[str, Any],
) -> tuple[Truth, FactValue]:
    fact = _fact_for(predicate, kb, bindings, context)
    if predicate.operator == "is_known":
        return (Truth.TRUE if fact.state is KnowledgeState.KNOWN else Truth.FALSE), fact
    if fact.state is not KnowledgeState.KNOWN:
        return Truth.UNKNOWN, fact
    if predicate.operator == "equals":
        return (Truth.TRUE if fact.value == predicate.expected else Truth.FALSE), fact
    if predicate.operator == "not_equals":
        return (Truth.TRUE if fact.value != predicate.expected else Truth.FALSE), fact
    if predicate.operator == "in_set":
        return (Truth.TRUE if fact.value in predicate.expected else Truth.FALSE), fact
    raise SourceError(f"unknown predicate operator: {predicate.operator}")
