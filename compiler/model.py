from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class Truth(str, Enum):
    TRUE = "TRUE"
    FALSE = "FALSE"
    UNKNOWN = "UNKNOWN"


class KnowledgeState(str, Enum):
    KNOWN = "known"
    UNKNOWN = "unknown"
    NOT_APPLICABLE = "not_applicable"
    ABSENT = "absent"


@dataclass(frozen=True)
class FactValue:
    state: KnowledgeState
    value: Any = None
    origin: str = "intrinsic"
    context: tuple[tuple[str, Any], ...] = ()
    evidence_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class PredicatePlan:
    operator: str
    subject: str = "context"
    binding: str | None = None
    bindings: tuple[str, ...] = ()
    key: str | None = None
    expected: Any = None


@dataclass(frozen=True)
class ParticipantPatternPlan:
    bind: str
    target_id: str | None = None
    entity_kind: str | None = None
    species_kind: str | None = None
    required_facets: tuple[str, ...] = ()
    forbidden_facets: tuple[str, ...] = ()


@dataclass(frozen=True)
class IonSourcePlan:
    kind: str
    binding: str
    relation_key: str | None = None


@dataclass(frozen=True)
class ProductPlan:
    constructor: str
    phase: str
    target_id: str | None = None
    scheme: str | None = None
    value: str | None = None
    cation_source: IonSourcePlan | None = None
    anion_source: IonSourcePlan | None = None
    left_binding: str | None = None
    right_binding: str | None = None
    exchange_role: str | None = None

    @property
    def cation_from(self) -> str | None:
        if self.cation_source is not None and self.cation_source.kind == "speciation":
            return self.cation_source.binding
        return None

    @property
    def anion_from(self) -> str | None:
        if self.anion_source is not None and self.anion_source.kind == "speciation":
            return self.anion_source.binding
        return None


@dataclass(frozen=True)
class RuleRelations:
    overrides: tuple[str, ...] = ()
    specializes: tuple[str, ...] = ()
    fallback_for: tuple[str, ...] = ()
    equivalent_to: tuple[str, ...] = ()
    mutually_exclusive_with: tuple[str, ...] = ()


@dataclass(frozen=True)
class RulePlan:
    rule_id: str
    version: str
    decision_domain: str
    patterns: tuple[ParticipantPatternPlan, ...]
    predicates: tuple[PredicatePlan, ...]
    blockers: tuple[PredicatePlan, ...]
    products: tuple[ProductPlan, ...]
    validators: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    relations: RuleRelations = RuleRelations()

    @property
    def bindings(self) -> tuple[tuple[str, str | None], ...]:
        """F2 compatibility projection; generic patterns may have no exact target id."""
        return tuple((pattern.bind, pattern.target_id) for pattern in self.patterns)


@dataclass(frozen=True)
class BalanceResult:
    coefficients: tuple[int, ...]
    reactant_count: int
