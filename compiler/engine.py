from __future__ import annotations

from math import gcd
from typing import Any

from .balance import BalanceError, balance, validate_conservation
from .canonical import sha256_hex
from .model import RulePlan, Truth
from .rules import bind_rule, evaluate_predicate
from .source import KnowledgeBase


def _normalize_coefficients(participants: list[dict[str, Any]]) -> list[dict[str, Any]]:
    coefficients = [item["coefficient"]["numerator"] for item in participants]
    common = 0
    for coefficient in coefficients:
        common = gcd(common, coefficient)
    common = common or 1
    normalized: list[dict[str, Any]] = []
    for item in participants:
        normalized.append(
            {
                "role": item["role"],
                "target_id": item["target_id"],
                "phase": item.get("phase", "unknown"),
                "coefficient": item["coefficient"]["numerator"] // common,
            }
        )
    return sorted(normalized, key=lambda item: (item["role"], item["target_id"], item["phase"]))


def reaction_signature(participants: list[dict[str, Any]]) -> str:
    return sha256_hex(_normalize_coefficients(participants))


def canonical_reaction_index(kb: KnowledgeBase) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    for reaction_id in sorted(kb.reactions):
        signature = reaction_signature(kb.reactions[reaction_id]["participants"])
        index.setdefault(signature, []).append(reaction_id)
    return index


def infer_case(kb: KnowledgeBase, plans: tuple[RulePlan, ...], case: dict[str, Any]) -> dict[str, Any]:
    normalized_reactants = sorted(case["reactants"], key=lambda item: (item["target_id"], item["phase"]))
    reactants = tuple(item["target_id"] for item in normalized_reactants)
    reactant_phases = {item["target_id"]: item["phase"] for item in normalized_reactants}
    context = case.get("context", {})
    trace: list[dict[str, Any]] = [
        {"event": "input.normalized", "reactants": normalized_reactants, "context": context},
        {"event": "refs.resolved", "resolved": all(entity_id in kb.entities for entity_id in reactants)},
    ]
    unresolved = [entity_id for entity_id in reactants if entity_id not in kb.entities]
    if unresolved:
        return _terminal(case, "invalid", trace, diagnostic="unresolved_inputs", details=unresolved)

    trace.append({"event": "knowledge.resolved", "entity_count": len(reactants)})
    compatible: list[tuple[RulePlan, dict[str, str]]] = []
    for plan in plans:
        bindings = bind_rule(plan, reactants)
        if bindings is not None:
            compatible.append((plan, bindings))
    if not compatible:
        trace.append({"event": "rule.match", "result": "none"})
        return _terminal(case, "no_match", trace)

    indeterminate = False
    for plan, bindings in compatible:
        trace.append({"event": "rule.match", "rule_id": plan.rule_id, "result": "candidate"})
        predicate_results: list[Truth] = []
        for predicate in plan.predicates:
            truth, state = evaluate_predicate(predicate, kb, bindings, context)
            predicate_results.append(truth)
            trace.append({
                "event": "predicate.eval",
                "rule_id": plan.rule_id,
                "operator": predicate.operator,
                "binding": predicate.binding,
                "key": predicate.key,
                "expected": predicate.expected,
                "truth": truth.value,
                "knowledge_state": state,
            })
        if Truth.FALSE in predicate_results:
            continue

        blocked = False
        blocker_unknown = False
        for blocker in plan.blockers:
            truth, state = evaluate_predicate(blocker, kb, bindings, context)
            trace.append({
                "event": "blocker.checked",
                "rule_id": plan.rule_id,
                "operator": blocker.operator,
                "key": blocker.key,
                "truth": truth.value,
                "knowledge_state": state,
            })
            if truth is Truth.TRUE:
                blocked = True
            elif truth is Truth.UNKNOWN:
                blocker_unknown = True
        if blocked:
            return _terminal(case, "blocked", trace, rule_id=plan.rule_id)
        if blocker_unknown or Truth.UNKNOWN in predicate_results:
            indeterminate = True
            continue
        return _construct_candidate(kb, plan, reactants, reactant_phases, context, trace, case)

    return _terminal(case, "indeterminate" if indeterminate else "no_match", trace)


def _construct_candidate(
    kb: KnowledgeBase,
    plan: RulePlan,
    reactants: tuple[str, ...],
    reactant_phases: dict[str, str],
    context: dict[str, Any],
    trace: list[dict[str, Any]],
    case: dict[str, Any],
) -> dict[str, Any]:
    product_specs = tuple(sorted(plan.products, key=lambda item: (item[0], item[1])))
    products = tuple(item[0] for item in product_specs)
    product_phases = {entity_id: phase for entity_id, phase in product_specs}
    trace.append({"event": "products.constructed", "rule_id": plan.rule_id, "products": [{"target_id": i, "phase": p} for i, p in product_specs]})
    missing = [entity_id for entity_id in products if entity_id not in kb.entities]
    trace.append({"event": "products.resolved", "resolved": not missing, "missing": missing})
    if missing:
        return _terminal(case, "invalid", trace, rule_id=plan.rule_id, diagnostic="unresolved_products")
    try:
        balanced = balance(kb, reactants, products)
    except BalanceError as exc:
        trace.append({"event": "balance.failed", "diagnostic": str(exc)})
        return _terminal(case, "invalid", trace, rule_id=plan.rule_id, diagnostic="balance_failed")

    trace.append({"event": "balance.completed", "coefficients": list(balanced.coefficients)})
    atoms_ok, charge_ok = validate_conservation(kb, reactants, products, balanced)
    trace.append({"event": "validation.atoms", "result": atoms_ok})
    trace.append({"event": "validation.charge", "result": charge_ok})
    if not atoms_ok or not charge_ok:
        return _terminal(case, "invalid", trace, rule_id=plan.rule_id, diagnostic="conservation_failed")

    participants: list[dict[str, Any]] = []
    ids = reactants + products
    for index, (entity_id, coefficient) in enumerate(zip(ids, balanced.coefficients, strict=True)):
        participants.append({
            "target_id": entity_id,
            "role": "reactant" if index < len(reactants) else "product",
            "phase": reactant_phases[entity_id] if index < len(reactants) else product_phases[entity_id],
            "coefficient": {"numerator": coefficient, "denominator": 1},
        })
    signature = reaction_signature(participants)
    matches = canonical_reaction_index(kb).get(signature, [])
    comparison_state = "exact" if len(matches) == 1 else "none" if not matches else "conflict"
    trace.append({"event": "canonical.compare", "state": comparison_state, "reaction_ids": matches})

    semantic_candidate = {
        "rule_id": plan.rule_id,
        "rule_version": plan.version,
        "inputs": list(reactants),
        "context": context,
        "participants": _normalize_coefficients(participants),
    }
    candidate_key = "cand_sha256_" + sha256_hex(semantic_candidate)
    trace.append({"event": "candidate.emitted", "candidate_key": candidate_key})
    return {
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
        "proof_trace": trace,
    }


def _terminal(
    case: dict[str, Any],
    status: str,
    trace: list[dict[str, Any]],
    **extra: Any,
) -> dict[str, Any]:
    result = {"case_id": case["id"], "status": status, "proof_trace": trace}
    result.update(extra)
    return result
