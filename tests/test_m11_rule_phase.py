from __future__ import annotations

import shutil
from pathlib import Path

import yaml

from compiler.rules import bind_rule_candidates, compile_rules
from compiler.source import load_knowledge


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_RULE_ID = "rule_fixture_liquid_water_phase"


def test_reactant_pattern_phase_is_lowered_and_rejects_a_different_input_phase(
    tmp_path: Path,
) -> None:
    work = tmp_path / "repo"
    shutil.copytree(ROOT, work, ignore=shutil.ignore_patterns(".git", "build", "__pycache__", ".pytest_cache"))
    rule = {
        "id": FIXTURE_RULE_ID,
        "record_type": "rule",
        "version": "1.0.0",
        "decision_domain": "reactant_phase_fixture",
        "match": {
            "reactants": [
                {
                    "bind": "water",
                    "target_id": "ent_substance_h2o",
                    "phase": "liquid",
                }
            ]
        },
        "products": [{"target_id": "ent_substance_h2o", "phase": "liquid"}],
        "validators": ["atoms_conserved", "charge_conserved"],
        "evidence_ids": ["ev_f2_reactions"],
    }
    path = work / "knowledge" / "rules" / "m11_phase_fixture.yaml"
    path.write_text(yaml.safe_dump({"records": [rule]}, sort_keys=False), encoding="utf-8")

    kb = load_knowledge(work)
    plan = next(plan for plan in compile_rules(kb) if plan.rule_id == FIXTURE_RULE_ID)

    assert plan.patterns[0].phase == "liquid"
    assert bind_rule_candidates(
        plan,
        ("ent_substance_h2o",),
        kb,
        {"ent_substance_h2o": "liquid"},
    ) == ({"water": "ent_substance_h2o"},)
    assert bind_rule_candidates(
        plan,
        ("ent_substance_h2o",),
        kb,
        {"ent_substance_h2o": "gas"},
    ) == ()
