from __future__ import annotations

from fractions import Fraction
from functools import reduce
from math import gcd
from typing import Iterable

from .model import BalanceResult
from .source import KnowledgeBase, SourceError


class BalanceError(ValueError):
    pass


def _composition(kb: KnowledgeBase, entity_id: str) -> tuple[dict[str, int], int]:
    entity = kb.entities[entity_id]
    payload = entity.get("payload", {})
    composition = payload.get("composition")
    if not composition:
        raise BalanceError(f"missing exact composition for {entity_id}")
    values = {item["element_id"]: item["count"] for item in composition["components"]}
    charge = int(payload.get("formal_charge", composition.get("net_charge", 0)))
    return values, charge


def _rref(matrix: list[list[Fraction]]) -> tuple[list[list[Fraction]], list[int]]:
    if not matrix:
        return matrix, []
    rows = len(matrix)
    cols = len(matrix[0])
    pivot_cols: list[int] = []
    pivot_row = 0
    for col in range(cols):
        pivot = next((r for r in range(pivot_row, rows) if matrix[r][col] != 0), None)
        if pivot is None:
            continue
        matrix[pivot_row], matrix[pivot] = matrix[pivot], matrix[pivot_row]
        factor = matrix[pivot_row][col]
        matrix[pivot_row] = [value / factor for value in matrix[pivot_row]]
        for row in range(rows):
            if row == pivot_row:
                continue
            factor = matrix[row][col]
            if factor:
                matrix[row] = [
                    matrix[row][c] - factor * matrix[pivot_row][c]
                    for c in range(cols)
                ]
        pivot_cols.append(col)
        pivot_row += 1
        if pivot_row == rows:
            break
    return matrix, pivot_cols


def _lcm(a: int, b: int) -> int:
    return abs(a * b) // gcd(a, b) if a and b else 0


def balance(kb: KnowledgeBase, reactants: Iterable[str], products: Iterable[str]) -> BalanceResult:
    reactants = tuple(reactants)
    products = tuple(products)
    ids = reactants + products
    if not reactants or not products:
        raise BalanceError("balancing requires reactants and products")
    compositions = [_composition(kb, entity_id) for entity_id in ids]
    elements = sorted({element for comp, _ in compositions for element in comp})
    matrix: list[list[Fraction]] = []
    for element in elements:
        row: list[Fraction] = []
        for index, (comp, _) in enumerate(compositions):
            sign = 1 if index < len(reactants) else -1
            row.append(Fraction(sign * comp.get(element, 0)))
        matrix.append(row)
    if any(charge != 0 for _, charge in compositions):
        matrix.append([
            Fraction((1 if index < len(reactants) else -1) * charge)
            for index, (_, charge) in enumerate(compositions)
        ])

    reduced, pivot_cols = _rref([row[:] for row in matrix])
    free_cols = [col for col in range(len(ids)) if col not in pivot_cols]
    if len(free_cols) != 1:
        raise BalanceError(f"underdetermined balancing system: {len(free_cols)} free variables")
    free = free_cols[0]
    vector = [Fraction(0) for _ in ids]
    vector[free] = Fraction(1)
    for row_index, pivot_col in reversed(list(enumerate(pivot_cols))):
        vector[pivot_col] = -reduced[row_index][free]
    if any(value <= 0 for value in vector):
        raise BalanceError("no strictly positive balancing solution")

    common_denominator = reduce(_lcm, (value.denominator for value in vector), 1)
    ints = [int(value * common_denominator) for value in vector]
    common_gcd = reduce(gcd, ints)
    ints = [value // common_gcd for value in ints]
    return BalanceResult(coefficients=tuple(ints), reactant_count=len(reactants))


def validate_conservation(
    kb: KnowledgeBase,
    reactants: tuple[str, ...],
    products: tuple[str, ...],
    result: BalanceResult,
) -> tuple[bool, bool]:
    ids = reactants + products
    if len(ids) != len(result.coefficients):
        raise SourceError("balance coefficient count mismatch")
    element_totals: dict[str, int] = {}
    charge_total = 0
    for index, (entity_id, coefficient) in enumerate(zip(ids, result.coefficients, strict=True)):
        composition, charge = _composition(kb, entity_id)
        sign = 1 if index < result.reactant_count else -1
        for element, count in composition.items():
            element_totals[element] = element_totals.get(element, 0) + sign * coefficient * count
        charge_total += sign * coefficient * charge
    return all(total == 0 for total in element_totals.values()), charge_total == 0
