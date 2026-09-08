from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class Truth(str, Enum):
    TRUE = "TRUE"
    FALSE = "FALSE"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class PredicatePlan:
    operator: str
    binding: str | None = None
    key: str | None = None
    expected: Any = None


@dataclass(frozen=True)
class RulePlan:
    rule_id: str
    version: str
    decision_domain: str
    bindings: tuple[tuple[str, str], ...]
    predicates: tuple[PredicatePlan, ...]
    blockers: tuple[PredicatePlan, ...]
    products: tuple[tuple[str, str], ...]
    validators: tuple[str, ...]
    evidence_ids: tuple[str, ...]


@dataclass(frozen=True)
class BalanceResult:
    coefficients: tuple[int, ...]
    reactant_count: int
