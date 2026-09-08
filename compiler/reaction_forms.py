from __future__ import annotations

from typing import Any, Iterable

from .source import KnowledgeBase, SourceError


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
    return {
        "reaction_id": reaction_id,
        "form_key": form["form_key"],
        "form_kind": form["form_kind"],
        "participants": form["participants"],
        "projection": {
            "method": form["projection"]["method"],
            "required_assumptions": sorted(form["projection"].get("required_assumptions", [])),
            "supplied_assumptions": sorted(supplied),
        },
    }
