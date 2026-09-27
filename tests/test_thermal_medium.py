"""A phase match cannot establish the surrounding reaction medium."""
from copy import deepcopy
from pathlib import Path

import pytest

from compiler.engine import infer_case
from compiler.rules import compile_rules
from compiler.source import load_cases, load_knowledge


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("case_id", [
    "case_m16_caco3_heated",
    "case_m17_nahco3_heated",
    "case_m18_magnesium_steam_heated",
])
def test_thermal_medium_is_required_independently_of_phase(case_id):
    kb = load_knowledge(ROOT)
    plans = compile_rules(kb)
    case = deepcopy(next(c for c in load_cases(ROOT) if c["id"] == case_id))
    positive = infer_case(kb, plans, case)
    assert positive["status"] == "inferred"
    assert positive["canonical_match"]["state"] == "exact"
    rule_id = positive["rule_id"]
    assert kb.rules[rule_id]["version"] == "1.1.0"

    for medium, status, truth in [(None, "indeterminate", "UNKNOWN"), ("aqueous", "no_match", "FALSE")]:
        if medium is None:
            case["context"].pop("medium")
        else:
            case["context"]["medium"] = medium
        result = infer_case(kb, plans, case)
        assert result["status"] == status
        assert "candidate_key" not in result
        assert any(item.get("rule_id") == rule_id and item.get("key") == "medium"
                   and item.get("truth") == truth for item in result["proof_trace"])
