from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from typing import Any, Iterable

from .source import KnowledgeBase, SourceError


def _coefficient(source: dict[str, Any]) -> Fraction:
    return Fraction(source["numerator"], source["denominator"])


def _coefficient_dict(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def _entity_charge_and_atoms(kb: KnowledgeBase, entity_id: str) -> tuple[dict[str, int], int]:
    entity = kb.entities[entity_id]
    if entity.get("entity_kind") == "material_system":
        raise SourceError(
            f"material_system cannot enter exact ionic-form validation: {entity_id}",
            code="stoichiometric_basis_required",
            stage="reaction_form_projection",
            details={"target_id": entity_id},
        )
    payload = entity.get("payload", {})
    composition = payload.get("composition")
    if not composition:
        raise SourceError(
            f"missing exact composition for reaction-form participant: {entity_id}",
            code="projection_unavailable",
            stage="reaction_form_projection",
            details={"target_id": entity_id},
        )
    atoms = {item["element_id"]: item["count"] for item in composition["components"]}
    charge = int(payload.get("formal_charge", composition.get("net_charge", 0)))
    return atoms, charge


def _merge_participants(kb: KnowledgeBase, entries: list[tuple[str, str, str, Fraction]]) -> list[dict[str, Any]]:
    totals: dict[tuple[str, str, str], Fraction] = defaultdict(Fraction)
    for role, target_id, phase, coefficient in entries:
        totals[(role, target_id, phase)] += coefficient
    participants: list[dict[str, Any]] = []
    for (role, target_id, phase), coefficient in sorted(totals.items()):
        if coefficient <= 0:
            continue
        participants.append(
            {
                "target_id": target_id,
                "target_kind": kb.entities[target_id]["entity_kind"],
                "role": role,
                "coefficient": _coefficient_dict(coefficient),
                "phase": phase,
            }
        )
    return participants


def _cancel_spectators(kb: KnowledgeBase, participants: list[dict[str, Any]]) -> list[dict[str, Any]]:
    reactants: dict[tuple[str, str], Fraction] = defaultdict(Fraction)
    products: dict[tuple[str, str], Fraction] = defaultdict(Fraction)
    for participant in participants:
        key = (participant["target_id"], participant["phase"])
        target = reactants if participant["role"] == "reactant" else products
        target[key] += _coefficient(participant["coefficient"])
    for key in sorted(set(reactants) & set(products)):
        cancelled = min(reactants[key], products[key])
        reactants[key] -= cancelled
        products[key] -= cancelled
    entries: list[tuple[str, str, str, Fraction]] = []
    for (target_id, phase), coefficient in sorted(reactants.items()):
        if coefficient:
            entries.append(("reactant", target_id, phase, coefficient))
    for (target_id, phase), coefficient in sorted(products.items()):
        if coefficient:
            entries.append(("product", target_id, phase, coefficient))
    return _merge_participants(kb, entries)


def _validate_participant_conservation(kb: KnowledgeBase, participants: list[dict[str, Any]]) -> dict[str, bool]:
    atom_totals: dict[str, Fraction] = defaultdict(Fraction)
    charge_total = Fraction(0)
    for participant in participants:
        atoms, charge = _entity_charge_and_atoms(kb, participant["target_id"])
        coefficient = _coefficient(participant["coefficient"])
        sign = 1 if participant["role"] == "reactant" else -1
        for element_id, count in atoms.items():
            atom_totals[element_id] += sign * coefficient * count
        charge_total += sign * coefficient * charge
    return {
        "atoms": all(total == 0 for total in atom_totals.values()),
        "charge": charge_total == 0,
    }


def _unavailable(reaction_id: str, form_kind: str, code: str, message: str, **details: Any) -> dict[str, Any]:
    return {
        "status": "unavailable",
        "reaction_id": reaction_id,
        "form_kind": form_kind,
        "diagnostic": {
            "code": code,
            "stage": "reaction_form_projection",
            "message": message,
            "details": {key: details[key] for key in sorted(details)},
        },
    }


def derive_aqueous_ionic_form(
    kb: KnowledgeBase,
    reaction_id: str,
    form_kind: str,
    context: dict[str, Any],
) -> dict[str, Any]:
    if form_kind not in {"complete_ionic", "net_ionic"}:
        raise SourceError(
            f"unsupported derived aqueous form: {form_kind}",
            code="schema_invalid",
            stage="reaction_form_projection",
            details={"form_kind": form_kind},
        )
    reaction = kb.reactions.get(reaction_id)
    if reaction is None:
        raise SourceError(
            f"unknown reaction: {reaction_id}",
            code="reference_unresolved",
            stage="reaction_form_projection",
            details={"reaction_id": reaction_id},
        )

    entries: list[tuple[str, str, str, Fraction]] = []
    profile_trace: list[dict[str, Any]] = []
    evidence_ids: set[str] = set(reaction.get("evidence_ids", []))
    for participant in reaction["participants"]:
        coefficient = _coefficient(participant["coefficient"])
        if participant["phase"] != "aqueous":
            entries.append((participant["role"], participant["target_id"], participant["phase"], coefficient))
            continue
        profiles = kb.speciation_profiles(participant["target_id"], context)
        if not profiles:
            return _unavailable(
                reaction_id,
                form_kind,
                "speciation_unavailable",
                "aqueous participant has no approved speciation profile",
                target_id=participant["target_id"],
            )
        if len(profiles) != 1:
            return _unavailable(
                reaction_id,
                form_kind,
                "speciation_ambiguous",
                "aqueous participant resolves to multiple equally specific speciation profiles",
                target_id=participant["target_id"],
                profile_keys=sorted(profile["profile_key"] for profile in profiles),
            )
        profile = profiles[0]
        if profile["model"] != "strong_electrolyte_complete_dissociation":
            return _unavailable(
                reaction_id,
                form_kind,
                "speciation_model_unsupported",
                "bounded aqueous projector only expands approved complete-dissociation profiles",
                target_id=participant["target_id"],
                model=profile["model"],
            )
        evidence_ids.update(profile.get("evidence_ids", []))
        profile_trace.append(
            {
                "target_id": participant["target_id"],
                "profile_key": profile["profile_key"],
                "model": profile["model"],
                "evidence_ids": sorted(profile.get("evidence_ids", [])),
            }
        )
        for product in profile["products"]:
            entries.append(
                (
                    participant["role"],
                    product["target_id"],
                    "dissolved",
                    coefficient * _coefficient(product["coefficient"]),
                )
            )

    complete = _merge_participants(kb, entries)
    projected = complete if form_kind == "complete_ionic" else _cancel_spectators(kb, complete)
    validation = _validate_participant_conservation(kb, projected)
    if not validation["atoms"] or not validation["charge"]:
        return {
            "status": "invalid",
            "reaction_id": reaction_id,
            "form_kind": form_kind,
            "participants": projected,
            "validation": validation,
            "diagnostic": {
                "code": "projection_conservation_failure",
                "stage": "reaction_form_projection",
                "message": "derived ionic form failed mandatory atom or charge conservation",
            },
        }
    operators = ["expand_approved_aqueous_speciation"]
    if form_kind == "net_ionic":
        operators.append("cancel_identical_canonical_spectators")
    return {
        "status": "derived",
        "reaction_id": reaction_id,
        "form_kind": form_kind,
        "participants": projected,
        "validation": validation,
        "derivation": {
            "kind": "derived_reaction_form",
            "source_reaction_id": reaction_id,
            "context": {key: context[key] for key in sorted(context)},
            "speciation_profiles": sorted(profile_trace, key=lambda item: (item["target_id"], item["profile_key"])),
            "operators": operators,
            "evidence_ids": sorted(evidence_ids),
        },
    }


def project_reaction_form(
    kb: KnowledgeBase,
    reaction_id: str,
    form_kind: str,
    assumptions: Iterable[str],
) -> dict[str, Any] | None:
    reaction = kb.reactions.get(reaction_id)
    if reaction is None:
        raise SourceError(
            f"unknown reaction: {reaction_id}",
            code="reference_unresolved",
            stage="reaction_form_projection",
            details={"reaction_id": reaction_id},
        )
    supplied = frozenset(assumptions)
    matches: list[dict[str, Any]] = []
    for form in reaction.get("forms", []):
        if form["form_kind"] != form_kind:
            continue
        required = frozenset(form["projection"].get("required_assumptions", []))
        if required <= supplied:
            matches.append(form)
    if not matches:
        return None
    if len(matches) > 1:
        raise SourceError(
            f"ambiguous reaction form projection for {reaction_id}:{form_kind}",
            code="canonical_conflict",
            stage="reaction_form_projection",
            details={"reaction_id": reaction_id, "form_kind": form_kind},
        )
    form = matches[0]
    projection_meta = {
        "method": form["projection"]["method"],
        "lifecycle": form["projection"].get("lifecycle", "curated"),
        "required_assumptions": sorted(form["projection"].get("required_assumptions", [])),
        "supplied_assumptions": sorted(supplied),
    }
    if form_kind in {"complete_ionic", "net_ionic"}:
        context = {"medium": "aqueous"} if "aqueous_medium" in supplied else {}
        derived = derive_aqueous_ionic_form(kb, reaction_id, form_kind, context)
        if derived["status"] != "derived":
            return None
        return {
            **derived,
            "form_key": form["form_key"],
            "projection": projection_meta,
        }
    return {
        "reaction_id": reaction_id,
        "form_key": form["form_key"],
        "form_kind": form["form_kind"],
        "participants": form["participants"],
        "projection": projection_meta,
    }
