from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict
from fractions import Fraction
from typing import Any

from .balance import BalanceError, balance, primitive_coefficients, validate_conservation
from .canonical import sha256_hex
from .diagnostics import diagnostic
from .model import RulePlan, Truth
from .predicates import evaluate_predicate
from .products import ProductResolutionError, resolve_products_detailed
from .rules import bind_rule_candidates, resolve_applicable_rules
from .source import KnowledgeBase


def _normalize_coefficients(participants: list[dict[str, Any]]) -> list[dict[str, Any]]:
    totals: dict[tuple[str, str, str], Fraction] = defaultdict(Fraction)
    for item in participants:
        key = (item["role"], item["target_id"], item.get("phase", "unknown"))
        value = item["coefficient"]
        totals[key] += Fraction(value["numerator"], value["denominator"])
    keys = sorted(totals)
    coefficients = primitive_coefficients(totals[key] for key in keys)
    return [
        {"role": role, "target_id": target_id, "phase": phase, "coefficient": coefficient}
        for (role, target_id, phase), coefficient in zip(keys, coefficients, strict=True)
    ]


def reaction_signature(participants: list[dict[str, Any]]) -> str:
    return sha256_hex(_normalize_coefficients(participants))


def canonical_reaction_index(kb: KnowledgeBase) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    for reaction_id in sorted(kb.reactions):
        signature = reaction_signature(kb.reactions[reaction_id]["participants"])
        index.setdefault(signature, []).append(reaction_id)
    return index


def compare_canonical_reactions(
    kb: KnowledgeBase,
    participants: list[dict[str, Any]],
    context: dict[str, Any],
) -> dict[str, Any]:
    signature_matches = canonical_reaction_index(kb).get(reaction_signature(participants), [])
    compatible: list[str] = []
    compatibility: list[dict[str, Any]] = []
    condition_evidence_ids: set[str] = set()
    for reaction_id in signature_matches:
        reaction = kb.reactions[reaction_id]
        unsatisfied: list[dict[str, Any]] = []
        for condition in sorted(reaction.get("conditions", []), key=lambda item: item["key"]):
            key = condition["key"]
            actual = context.get(key)
            if actual != condition["value"]:
                unsatisfied.append(
                    {
                        "key": key,
                        "required": condition["value"],
                        "actual": actual,
                        "reason": "missing" if key not in context else "conflicting",
                        "evidence_ids": sorted(condition.get("evidence_ids", [])),
                    }
                )
        state = "incompatible" if unsatisfied else "compatible"
        compatibility.append(
            {
                "reaction_id": reaction_id,
                "state": state,
                "unsatisfied": unsatisfied,
            }
        )
        if not unsatisfied:
            compatible.append(reaction_id)
            for condition in reaction.get("conditions", []):
                condition_evidence_ids.update(condition.get("evidence_ids", []))
    return {
        "state": "exact" if len(compatible) == 1 else "none" if not compatible else "conflict",
        "reaction_ids": compatible,
        "condition_compatibility": compatibility,
        "condition_evidence_ids": sorted(condition_evidence_ids),
    }


def _trace_predicate(
    trace: list[dict[str, Any]],
    event: str,
    plan: RulePlan,
    predicate: Any,
    truth: Truth,
    fact: Any,
) -> None:
    item = {
        "event": event,
        "rule_id": plan.rule_id,
        "operator": predicate.operator,
        "subject": predicate.subject,
        "binding": predicate.binding,
        "bindings": list(predicate.bindings),
        "key": predicate.key,
        "expected": predicate.expected,
        "truth": truth.value,
        "knowledge_state": fact.state.value,
        "fact_origin": fact.origin,
        "fact_context": dict(fact.context),
        "evidence_ids": list(fact.evidence_ids),
    }
    if predicate.subject == "relation":
        item["target_id"] = fact.resolved_target_id or predicate.target_id
        item["target_source"] = None if predicate.target_source is None else asdict(predicate.target_source)
        item["relation_assertions"] = list(fact.relation_assertions)
        item["speciation_profiles"] = list(fact.speciation_profiles)
        if fact.diagnostic is not None:
            item["target_source_diagnostic"] = fact.diagnostic
    trace.append(item)


def infer_case(kb: KnowledgeBase, plans: tuple[RulePlan, ...], case: dict[str, Any]) -> dict[str, Any]:
    normalized_reactants = sorted(case["reactants"], key=lambda item: (item["target_id"], item["phase"]))
    reactants = tuple(item["target_id"] for item in normalized_reactants)
    reactant_phases = {item["target_id"]: item["phase"] for item in normalized_reactants}
    context = case.get("context", {})
    trace: list[dict[str, Any]] = [
        {"event": "input.normalized", "reactants": normalized_reactants, "context": context},
        {"event": "refs.resolved", "resolved": all(entity_id in kb.entities for entity_id in reactants)},
    ]
    unresolved = sorted(entity_id for entity_id in reactants if entity_id not in kb.entities)
    if unresolved:
        return _terminal(
            case,
            "invalid",
            trace,
            diagnostic_obj=diagnostic(
                "reference_unresolved",
                "input_resolution",
                "one or more input entities do not resolve",
                target_ids=unresolved,
            ),
        )

    trace.append({"event": "knowledge.resolved", "entity_count": len(reactants)})
    matched_any = False
    indeterminate = False
    blocked_rules: list[str] = []
    applicable: dict[str, dict[str, str]] = {}
    applicable_relation_assertions: dict[str, tuple[dict[str, Any], ...]] = {}
    applicable_speciation_profiles: dict[str, tuple[dict[str, Any], ...]] = {}
    applicable_predicate_evidence_ids: dict[str, tuple[str, ...]] = {}

    for plan in sorted(plans, key=lambda item: item.rule_id):
        binding_candidates = bind_rule_candidates(plan, reactants, kb, reactant_phases)
        if not binding_candidates:
            continue
        matched_any = True
        trace.append({"event": "rule.match", "rule_id": plan.rule_id, "result": "candidate"})

        plan_indeterminate = False
        plan_blocked = False
        for bindings in binding_candidates:
            predicate_results: list[Truth] = []
            predicate_relation_assertions: list[dict[str, Any]] = []
            predicate_speciation_profiles: list[dict[str, Any]] = []
            predicate_evidence_ids: set[str] = set()
            for predicate in plan.predicates:
                truth, fact = evaluate_predicate(predicate, kb, bindings, context)
                predicate_results.append(truth)
                predicate_relation_assertions.extend(fact.relation_assertions)
                predicate_speciation_profiles.extend(fact.speciation_profiles)
                predicate_evidence_ids.update(fact.evidence_ids)
                _trace_predicate(trace, "predicate.eval", plan, predicate, truth, fact)
            if Truth.FALSE in predicate_results:
                continue

            blocker_unknown = False
            blocked = False
            for blocker in plan.blockers:
                truth, fact = evaluate_predicate(blocker, kb, bindings, context)
                _trace_predicate(trace, "blocker.checked", plan, blocker, truth, fact)
                if truth is Truth.TRUE:
                    blocked = True
                elif truth is Truth.UNKNOWN:
                    blocker_unknown = True
            if blocked:
                plan_blocked = True
                continue
            if blocker_unknown or Truth.UNKNOWN in predicate_results:
                plan_indeterminate = True
                continue
            applicable.setdefault(plan.rule_id, bindings)
            applicable_relation_assertions.setdefault(
                plan.rule_id,
                tuple(predicate_relation_assertions),
            )
            applicable_speciation_profiles.setdefault(
                plan.rule_id,
                tuple(predicate_speciation_profiles),
            )
            applicable_predicate_evidence_ids.setdefault(
                plan.rule_id,
                tuple(sorted(predicate_evidence_ids)),
            )
            break

        if plan.rule_id not in applicable:
            if plan_blocked:
                blocked_rules.append(plan.rule_id)
            if plan_indeterminate:
                indeterminate = True

    if not matched_any:
        trace.append({"event": "rule.match", "result": "none"})
        return _terminal(
            case,
            "no_match",
            trace,
            diagnostic_obj=diagnostic("no_rule_match", "rule_match", "no rule participant pattern matched"),
        )

    if not applicable:
        if blocked_rules and not indeterminate:
            return _terminal(
                case,
                "blocked",
                trace,
                rule_id=sorted(blocked_rules)[0],
                diagnostic_obj=diagnostic(
                    "blocked",
                    "blocker_resolution",
                    "all otherwise-applicable rule paths were blocked",
                    rule_ids=sorted(blocked_rules),
                ),
            )
        if indeterminate:
            return _terminal(
                case,
                "indeterminate",
                trace,
                diagnostic_obj=diagnostic(
                    "unknown_applicability",
                    "predicate_evaluation",
                    "rule applicability depends on UNKNOWN or absent knowledge",
                ),
            )
        return _terminal(
            case,
            "no_match",
            trace,
            diagnostic_obj=diagnostic("no_rule_match", "rule_match", "matched patterns failed known predicates"),
        )

    selected_rule_id, resolution_error = resolve_applicable_rules(plans, set(applicable))
    trace.append(
        {
            "event": "rule.resolution",
            "applicable_rule_ids": sorted(applicable),
            "selected_rule_id": selected_rule_id,
        }
    )
    if selected_rule_id is None:
        return _terminal(case, "ambiguous", trace, diagnostic_obj=resolution_error)
    plan = next(plan for plan in plans if plan.rule_id == selected_rule_id)
    return _construct_candidate(
        kb,
        plan,
        applicable[selected_rule_id],
        reactants,
        reactant_phases,
        context,
        trace,
        case,
        applicable_relation_assertions.get(selected_rule_id, ()),
        applicable_speciation_profiles.get(selected_rule_id, ()),
        applicable_predicate_evidence_ids.get(selected_rule_id, ()),
    )


def _construct_candidate(
    kb: KnowledgeBase,
    plan: RulePlan,
    bindings: dict[str, str],
    reactants: tuple[str, ...],
    reactant_phases: dict[str, str],
    context: dict[str, Any],
    trace: list[dict[str, Any]],
    case: dict[str, Any],
    predicate_relation_assertions: tuple[dict[str, Any], ...],
    predicate_speciation_profiles: tuple[dict[str, Any], ...],
    predicate_evidence_ids: tuple[str, ...],
) -> dict[str, Any]:
    try:
        resolved_products = tuple(
            sorted(
                resolve_products_detailed(kb, plan.products, bindings, context),
                key=lambda item: (item.target_id, item.phase),
            )
        )
    except ProductResolutionError as exc:
        trace.append({"event": "products.resolved", "resolved": False, "diagnostic": exc.diagnostic})
        return _terminal(case, "invalid", trace, rule_id=plan.rule_id, diagnostic_obj=exc.diagnostic)

    products = tuple(item.target_id for item in resolved_products)
    product_phases = {item.target_id: item.phase for item in resolved_products}
    profile_index = {
        (profile["target_id"], profile["profile_key"]): profile
        for profile in (
            list(predicate_speciation_profiles)
            + [profile for product in resolved_products for profile in product.speciation_profiles]
        )
    }
    speciation_profiles = [profile_index[key] for key in sorted(profile_index)]
    relation_index = {
        (
            assertion["source_id"],
            assertion["relation_key"],
            assertion["target_id"],
            tuple(sorted(assertion["context"].items())),
            tuple(sorted(assertion["evidence_ids"])),
        ): assertion
        for assertion in (
            list(predicate_relation_assertions)
            + [
                assertion
                for product in resolved_products
                for assertion in product.relation_assertions
            ]
        )
    }
    relation_assertions = [relation_index[key] for key in sorted(relation_index)]
    product_evidence_ids = {
        evidence_id
        for product in resolved_products
        for evidence_id in product.evidence_ids
    }
    constructed_event = {
        "event": "products.constructed",
        "rule_id": plan.rule_id,
        "products": [{"target_id": item.target_id, "phase": item.phase} for item in resolved_products],
        "speciation_profiles": speciation_profiles,
    }
    if relation_assertions:
        constructed_event["relation_assertions"] = relation_assertions
    trace.append(constructed_event)
    trace.append({"event": "products.resolved", "resolved": True, "missing": []})
    try:
        balanced = balance(kb, reactants, products)
    except BalanceError as exc:
        diag = diagnostic("balance_failure", "balancing", str(exc), rule_id=plan.rule_id)
        trace.append({"event": "balance.failed", "diagnostic": diag})
        return _terminal(case, "invalid", trace, rule_id=plan.rule_id, diagnostic_obj=diag)

    trace.append({"event": "balance.completed", "coefficients": list(balanced.coefficients)})
    atoms_ok, charge_ok = validate_conservation(kb, reactants, products, balanced)
    trace.append({"event": "validation.atoms", "result": atoms_ok})
    trace.append({"event": "validation.charge", "result": charge_ok})
    if not atoms_ok:
        return _terminal(
            case,
            "invalid",
            trace,
            rule_id=plan.rule_id,
            diagnostic_obj=diagnostic("atom_validation_failure", "validation", "atom conservation failed"),
        )
    if not charge_ok:
        return _terminal(
            case,
            "invalid",
            trace,
            rule_id=plan.rule_id,
            diagnostic_obj=diagnostic("charge_validation_failure", "validation", "charge conservation failed"),
        )

    participants: list[dict[str, Any]] = []
    ids = reactants + products
    for index, (entity_id, coefficient) in enumerate(zip(ids, balanced.coefficients, strict=True)):
        participants.append(
            {
                "target_id": entity_id,
                "role": "reactant" if index < len(reactants) else "product",
                "phase": reactant_phases[entity_id] if index < len(reactants) else product_phases[entity_id],
                "coefficient": {"numerator": coefficient, "denominator": 1},
            }
        )
    comparison = compare_canonical_reactions(kb, participants, context)
    matches = comparison["reaction_ids"]
    comparison_state = comparison["state"]
    trace.append(
        {
            "event": "canonical.compare",
            "state": comparison_state,
            "reaction_ids": matches,
            "condition_compatibility": comparison["condition_compatibility"],
        }
    )

    semantic_candidate = {
        "rule_id": plan.rule_id,
        "rule_version": plan.version,
        "inputs": list(reactants),
        "context": context,
        "participants": _normalize_coefficients(participants),
    }
    candidate_key = "cand_sha256_" + sha256_hex(semantic_candidate)
    trace.append({"event": "candidate.emitted", "candidate_key": candidate_key})
    result = {
        "case_id": case["id"],
        "status": "inferred",
        "candidate_key": candidate_key,
        "rule_id": plan.rule_id,
        "rule_version": plan.version,
        "participants": participants,
        "validation": {"atoms": atoms_ok, "charge": charge_ok},
        "canonical_match": {
            "state": comparison_state,
            "reaction_ids": matches,
            "reaction_forms": {
                reaction_id: [form["form_key"] for form in kb.reactions[reaction_id].get("forms", [])]
                for reaction_id in matches
            },
        },
        "provenance": {
            "kind": "derived_reaction_candidate",
            "rule_id": plan.rule_id,
            "rule_version": plan.version,
            "evidence_ids": sorted(set(plan.evidence_ids) | product_evidence_ids | set(predicate_evidence_ids)),
            "speciation_profiles": speciation_profiles,
        },
        "proof_trace": trace,
    }
    if comparison["condition_evidence_ids"]:
        result["canonical_match"]["condition_evidence_ids"] = comparison["condition_evidence_ids"]
        result["provenance"]["condition_evidence_ids"] = comparison["condition_evidence_ids"]
    if relation_assertions:
        result["provenance"]["relation_assertions"] = relation_assertions
    if comparison_state == "none":
        result["diagnostics"] = [
            diagnostic("canonical_no_match", "canonical_comparison", "candidate has no canonical reaction match")
        ]
    elif comparison_state == "conflict":
        result["diagnostics"] = [
            diagnostic(
                "canonical_conflict",
                "canonical_comparison",
                "candidate matches multiple canonical reactions",
                reaction_ids=matches,
            )
        ]
    return result


def _terminal(
    case: dict[str, Any],
    status: str,
    trace: list[dict[str, Any]],
    *,
    diagnostic_obj: dict[str, Any] | None = None,
    **extra: Any,
) -> dict[str, Any]:
    result = {"case_id": case["id"], "status": status, "proof_trace": trace}
    if diagnostic_obj is not None:
        result["diagnostic"] = diagnostic_obj
    result.update(extra)
    return result
