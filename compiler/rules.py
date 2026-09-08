from __future__ import annotations

from itertools import permutations
from typing import Any, Iterable

from .model import ParticipantPatternPlan, PredicatePlan, ProductPlan, RulePlan, RuleRelations
from .predicates import compile_predicate
from .source import KnowledgeBase, SourceError


RULE_DSL_VERSION = "1.0.0"
RULE_PLAN_VERSION = "1.0.0"
_RELATION_FIELDS = (
    "overrides",
    "specializes",
    "fallback_for",
    "equivalent_to",
    "mutually_exclusive_with",
)


def _legacy_context_predicate(key: str, expected: Any) -> dict[str, Any]:
    return {"operator": "equals", "subject": "context", "key": key, "expected": expected}


def _compile_blocker(source: dict[str, Any], bindings: set[str]) -> PredicatePlan:
    if "operator" in source:
        return compile_predicate(source, bindings)
    return compile_predicate(
        {
            "operator": "equals",
            "subject": "context",
            "key": source["key"],
            "expected": source["equals"],
        },
        bindings,
    )


def _compile_product(source: dict[str, Any]) -> ProductPlan:
    phase = source["phase"]
    if "target_id" in source:
        return ProductPlan(constructor="exact_entity", phase=phase, target_id=source["target_id"])
    construction = source["construct"]
    kind = construction["kind"]
    if kind == "semantic_key":
        return ProductPlan(
            constructor="semantic_key",
            phase=phase,
            scheme=construction["scheme"],
            value=construction["value"],
        )
    raise SourceError(
        f"unknown product constructor: {kind}",
        code="schema_invalid",
        stage="rule_compile",
        details={"constructor": kind},
    )


def compile_rules(kb: KnowledgeBase) -> tuple[RulePlan, ...]:
    plans: list[RulePlan] = []
    for rule_id in sorted(kb.rules):
        source = kb.rules[rule_id]
        patterns = tuple(
            ParticipantPatternPlan(
                bind=pattern["bind"],
                target_id=pattern.get("target_id"),
                entity_kind=pattern.get("entity_kind"),
                species_kind=pattern.get("species_kind"),
                required_facets=tuple(sorted(pattern.get("required_facets", []))),
                forbidden_facets=tuple(sorted(pattern.get("forbidden_facets", []))),
            )
            for pattern in source["match"]["reactants"]
        )
        bindings = {pattern.bind for pattern in patterns}
        if len(bindings) != len(patterns):
            raise SourceError(
                f"duplicate binding in {rule_id}",
                code="schema_invalid",
                stage="rule_compile",
                details={"rule_id": rule_id},
            )

        predicates: list[PredicatePlan] = []
        for pattern in patterns:
            for facet_key in pattern.required_facets:
                predicates.append(
                    compile_predicate(
                        {
                            "operator": "equals",
                            "subject": "facet",
                            "binding": pattern.bind,
                            "key": facet_key,
                            "expected": True,
                        },
                        bindings,
                    )
                )
            for facet_key in pattern.forbidden_facets:
                predicates.append(
                    compile_predicate(
                        {
                            "operator": "not_equals",
                            "subject": "facet",
                            "binding": pattern.bind,
                            "key": facet_key,
                            "expected": True,
                        },
                        bindings,
                    )
                )
        for key, expected in sorted(source.get("context", {}).items()):
            predicates.append(compile_predicate(_legacy_context_predicate(key, expected), bindings))
        for predicate_source in source.get("predicates", []):
            predicates.append(compile_predicate(predicate_source, bindings))

        relations = RuleRelations(
            overrides=tuple(sorted(source.get("overrides", []))),
            specializes=tuple(sorted(source.get("specializes", []))),
            fallback_for=tuple(sorted(source.get("fallback_for", []))),
            equivalent_to=tuple(sorted(source.get("equivalent_to", []))),
            mutually_exclusive_with=tuple(sorted(source.get("mutually_exclusive_with", []))),
        )
        plans.append(
            RulePlan(
                rule_id=rule_id,
                version=source["version"],
                decision_domain=source["decision_domain"],
                patterns=patterns,
                predicates=tuple(predicates),
                blockers=tuple(_compile_blocker(item, bindings) for item in source.get("blockers", [])),
                products=tuple(_compile_product(item) for item in source["products"]),
                validators=tuple(source.get("validators", [])),
                evidence_ids=tuple(source.get("evidence_ids", [])),
                relations=relations,
            )
        )
    compiled = tuple(plans)
    validate_rule_relationships(compiled)
    validate_rule_overlaps(compiled)
    return compiled


def _pattern_structural_match(pattern: ParticipantPatternPlan, entity: dict[str, Any], entity_id: str) -> bool:
    if pattern.target_id is not None and pattern.target_id != entity_id:
        return False
    if pattern.entity_kind is not None and pattern.entity_kind != entity.get("entity_kind"):
        return False
    if pattern.species_kind is not None and pattern.species_kind != entity.get("payload", {}).get("species_kind"):
        return False
    return True


def bind_rule_candidates(
    plan: RulePlan,
    reactant_ids: tuple[str, ...],
    kb: KnowledgeBase,
) -> tuple[dict[str, str], ...]:
    if len(plan.patterns) != len(reactant_ids):
        return ()
    candidates: list[dict[str, str]] = []
    for ordered_ids in permutations(sorted(reactant_ids)):
        bound: dict[str, str] = {}
        valid = True
        for pattern, entity_id in zip(plan.patterns, ordered_ids, strict=True):
            entity = kb.entities.get(entity_id)
            if entity is None or not _pattern_structural_match(pattern, entity, entity_id):
                valid = False
                break
            bound[pattern.bind] = entity_id
        if valid and bound not in candidates:
            candidates.append(bound)
    return tuple(candidates)


def bind_rule(
    plan: RulePlan,
    reactant_ids: tuple[str, ...],
    kb: KnowledgeBase | None = None,
) -> dict[str, str] | None:
    """Compatibility helper returning the first deterministic binding candidate."""
    if kb is None:
        expected_ids = [pattern.target_id for pattern in plan.patterns]
        if any(entity_id is None for entity_id in expected_ids):
            return None
        if sorted(expected_ids) != sorted(reactant_ids):
            return None
        remaining = list(reactant_ids)
        bound: dict[str, str] = {}
        for pattern in plan.patterns:
            assert pattern.target_id is not None
            index = remaining.index(pattern.target_id)
            bound[pattern.bind] = remaining.pop(index)
        return bound
    candidates = bind_rule_candidates(plan, reactant_ids, kb)
    return candidates[0] if candidates else None


def _patterns_compatible(a: ParticipantPatternPlan, b: ParticipantPatternPlan) -> bool:
    if a.target_id is not None and b.target_id is not None and a.target_id != b.target_id:
        return False
    if a.entity_kind is not None and b.entity_kind is not None and a.entity_kind != b.entity_kind:
        return False
    if a.species_kind is not None and b.species_kind is not None and a.species_kind != b.species_kind:
        return False
    if set(a.required_facets) & set(b.forbidden_facets):
        return False
    if set(b.required_facets) & set(a.forbidden_facets):
        return False
    return True


def _context_equals_constraints(plan: RulePlan) -> dict[str, Any]:
    constraints: dict[str, Any] = {}
    for predicate in plan.predicates:
        if predicate.subject == "context" and predicate.operator == "equals" and predicate.key is not None:
            constraints[predicate.key] = predicate.expected
    return constraints


def _participant_overlap(a: RulePlan, b: RulePlan) -> tuple[bool, str]:
    if len(a.patterns) != len(b.patterns):
        return False, "participant_count_disjoint"
    left_context = _context_equals_constraints(a)
    right_context = _context_equals_constraints(b)
    for key in sorted(set(left_context) & set(right_context)):
        if left_context[key] != right_context[key]:
            return False, f"context_disjoint:{key}"
    for permuted in permutations(b.patterns):
        if all(_patterns_compatible(left, right) for left, right in zip(a.patterns, permuted, strict=True)):
            signature = ";".join(
                f"{left.bind}<->{right.bind}"
                for left, right in zip(a.patterns, permuted, strict=True)
            )
            return True, f"potential_overlap:{signature}"
    return False, "participant_constraints_disjoint"


def _outcome_signature(plan: RulePlan) -> tuple[Any, ...]:
    products = tuple(
        sorted(
            (
                product.constructor,
                product.target_id,
                product.scheme,
                product.value,
                product.phase,
            )
            for product in plan.products
        )
    )
    return products, tuple(sorted(plan.validators))


def _relation_targets(plan: RulePlan) -> dict[str, set[str]]:
    return {field: set(getattr(plan.relations, field)) for field in _RELATION_FIELDS}


def _direct_relationships(a: RulePlan, b: RulePlan) -> set[str]:
    relationships: set[str] = set()
    for field in _RELATION_FIELDS:
        if b.rule_id in getattr(a.relations, field) or a.rule_id in getattr(b.relations, field):
            relationships.add(field)
    return relationships


def precedence_edges(plans: Iterable[RulePlan]) -> set[tuple[str, str]]:
    edges: set[tuple[str, str]] = set()
    for plan in plans:
        for target in plan.relations.overrides:
            edges.add((plan.rule_id, target))
        for target in plan.relations.specializes:
            edges.add((plan.rule_id, target))
        for target in plan.relations.fallback_for:
            edges.add((target, plan.rule_id))
    return edges


def validate_rule_relationships(plans: tuple[RulePlan, ...]) -> None:
    by_id = {plan.rule_id: plan for plan in plans}
    for plan in plans:
        targets = _relation_targets(plan)
        for field, refs in targets.items():
            for target in refs:
                if target not in by_id:
                    raise SourceError(
                        f"unknown rule relationship ref: {plan.rule_id} {field} {target}",
                        code="reference_unresolved",
                        stage="rule_resolution_graph",
                        details={"rule_id": plan.rule_id, "relation": field, "target_rule_id": target},
                    )
                if target == plan.rule_id:
                    raise SourceError(
                        f"self rule relationship is invalid: {plan.rule_id} {field}",
                        code="schema_invalid",
                        stage="rule_resolution_graph",
                        details={"rule_id": plan.rule_id, "relation": field},
                    )
                if field == "equivalent_to" and _outcome_signature(plan) != _outcome_signature(by_id[target]):
                    raise SourceError(
                        f"equivalent_to rules have non-equivalent outcomes: {plan.rule_id}, {target}",
                        code="schema_invalid",
                        stage="rule_resolution_graph",
                        details={"rule_id": plan.rule_id, "target_rule_id": target},
                    )
        for target in by_id:
            active = {field for field, refs in targets.items() if target in refs}
            if "equivalent_to" in active and active & {"overrides", "specializes", "fallback_for", "mutually_exclusive_with"}:
                raise SourceError(
                    f"contradictory rule relationships: {plan.rule_id} -> {target}: {sorted(active)}",
                    code="schema_invalid",
                    stage="rule_resolution_graph",
                    details={"rule_id": plan.rule_id, "target_rule_id": target, "relations": sorted(active)},
                )

    edges = precedence_edges(plans)
    graph: dict[str, set[str]] = {rule_id: set() for rule_id in by_id}
    for winner, loser in edges:
        graph[winner].add(loser)
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(rule_id: str, path: list[str]) -> None:
        if rule_id in visiting:
            cycle_start = path.index(rule_id)
            cycle = path[cycle_start:] + [rule_id]
            raise SourceError(
                f"rule resolution cycle: {' -> '.join(cycle)}",
                code="schema_invalid",
                stage="rule_resolution_graph",
                details={"cycle": cycle},
            )
        if rule_id in visited:
            return
        visiting.add(rule_id)
        for child in sorted(graph[rule_id]):
            visit(child, path + [child])
        visiting.remove(rule_id)
        visited.add(rule_id)

    for rule_id in sorted(graph):
        visit(rule_id, [rule_id])


def analyze_rule_overlaps(plans: tuple[RulePlan, ...]) -> tuple[dict[str, Any], ...]:
    diagnostics: list[dict[str, Any]] = []
    for index, left in enumerate(plans):
        for right in plans[index + 1 :]:
            if left.decision_domain != right.decision_domain:
                continue
            overlaps, reason = _participant_overlap(left, right)
            if not overlaps:
                continue
            diagnostics.append(
                {
                    "rule_ids": [left.rule_id, right.rule_id],
                    "decision_domain": left.decision_domain,
                    "reason": reason,
                    "outcomes_equivalent": _outcome_signature(left) == _outcome_signature(right),
                    "relationships": sorted(_direct_relationships(left, right)),
                }
            )
    return tuple(diagnostics)


def validate_rule_overlaps(plans: tuple[RulePlan, ...]) -> None:
    for item in analyze_rule_overlaps(plans):
        left_id, right_id = item["rule_ids"]
        left = next(plan for plan in plans if plan.rule_id == left_id)
        right = next(plan for plan in plans if plan.rule_id == right_id)
        relationships = set(item["relationships"])
        if "equivalent_to" in relationships and not item["outcomes_equivalent"]:
            raise SourceError(
                f"equivalent_to rules have non-equivalent outcomes: {left_id}, {right_id}",
                code="rule_overlap_compile_error",
                stage="rule_overlap_analysis",
                details=item,
            )
        if item["outcomes_equivalent"]:
            continue
        if not relationships & {"overrides", "specializes", "fallback_for", "mutually_exclusive_with"}:
            raise SourceError(
                f"unresolved rule overlap: {left_id} vs {right_id} ({item['reason']})",
                code="rule_overlap_compile_error",
                stage="rule_overlap_analysis",
                details=item,
            )


def resolve_applicable_rules(
    plans: tuple[RulePlan, ...],
    applicable_rule_ids: set[str],
) -> tuple[str | None, dict[str, Any] | None]:
    if not applicable_rule_ids:
        return None, None
    if len(applicable_rule_ids) == 1:
        return next(iter(applicable_rule_ids)), None
    by_id = {plan.rule_id: plan for plan in plans}

    for rule_id in sorted(applicable_rule_ids):
        declared = set(by_id[rule_id].relations.mutually_exclusive_with)
        conflict = sorted(declared & applicable_rule_ids)
        if conflict:
            return None, {
                "code": "ambiguous_rule_resolution",
                "stage": "rule_resolution",
                "message": "mutually exclusive rules both became applicable",
                "details": {"rule_ids": sorted({rule_id, *conflict})},
            }

    edges = precedence_edges(plans)
    graph: dict[str, set[str]] = {rule_id: set() for rule_id in by_id}
    for winner, loser in edges:
        graph[winner].add(loser)

    def reaches(winner: str, loser: str) -> bool:
        stack = list(graph[winner])
        seen: set[str] = set()
        while stack:
            current = stack.pop()
            if current == loser:
                return True
            if current in seen:
                continue
            seen.add(current)
            stack.extend(graph[current])
        return False

    dominated = {
        loser
        for loser in applicable_rule_ids
        if any(winner != loser and reaches(winner, loser) for winner in applicable_rule_ids)
    }
    winners = sorted(applicable_rule_ids - dominated)
    if len(winners) == 1:
        return winners[0], None

    signatures = {_outcome_signature(by_id[rule_id]) for rule_id in winners}
    if len(signatures) == 1:
        return winners[0], None
    return None, {
        "code": "ambiguous_rule_resolution",
        "stage": "rule_resolution",
        "message": "multiple applicable rules have no unique explicit winner",
        "details": {"rule_ids": winners},
    }
