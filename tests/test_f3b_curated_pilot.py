from __future__ import annotations

from collections import Counter
from pathlib import Path

from compiler.balance import balance, validate_conservation
from compiler.engine import infer_case
from compiler.rules import compile_rules
from compiler.source import load_knowledge


ROOT = Path(__file__).resolve().parents[1]
F3B_REACTIONS = (
    "rxn_f3b_baso4_precipitation",
    "rxn_f3b_hno3_koh_neutralization",
    "rxn_f3b_hcl_nahco3_gas_evolution",
)


def _composition_and_charge(kb, entity_id: str) -> tuple[dict[str, int], int]:
    payload = kb.entities[entity_id]["payload"]
    composition = payload.get("composition")
    assert composition is not None, entity_id
    atoms = {item["element_id"]: item["count"] for item in composition["components"]}
    charge = int(payload.get("formal_charge", composition["net_charge"]))
    return atoms, charge


def _authored_conservation(kb, participants: list[dict]) -> tuple[dict[str, int], int]:
    totals: Counter[str] = Counter()
    charge = 0
    for participant in participants:
        atoms, entity_charge = _composition_and_charge(kb, participant["target_id"])
        coefficient = participant["coefficient"]["numerator"]
        sign = 1 if participant["role"] == "reactant" else -1
        for element_id, count in atoms.items():
            totals[element_id] += sign * coefficient * count
        charge += sign * coefficient * entity_charge
    return dict(totals), charge


def _case(case_id: str, reactants: list[tuple[str, str]]) -> dict:
    return {
        "id": case_id,
        "reactants": [{"target_id": target_id, "phase": phase} for target_id, phase in reactants],
        "context": {"medium": "aqueous", "temperature_regime": "ambient"},
    }


def test_f3b_identity_levels_are_distinct_and_resolve() -> None:
    kb = load_knowledge(ROOT)
    assert kb.entities["ent_species_hcl_molecule"]["entity_kind"] == "species"
    assert kb.entities["ent_substance_hcl"]["entity_kind"] == "substance"
    assert kb.entities["ent_material_hydrochloric_acid_aqueous"]["entity_kind"] == "material_system"


def test_f3b_ion_composition_matches_formal_charge() -> None:
    kb = load_knowledge(ROOT)
    ion_ids = [
        "ent_species_na_plus",
        "ent_species_k_plus",
        "ent_species_ba_2plus",
        "ent_species_no3_minus",
        "ent_species_so4_2minus",
        "ent_species_hco3_minus",
    ]
    for entity_id in ion_ids:
        payload = kb.entities[entity_id]["payload"]
        assert payload["species_kind"] == "ion"
        assert payload["formal_charge"] == payload["composition"]["net_charge"]


def test_f3b_key_formula_compositions() -> None:
    kb = load_knowledge(ROOT)
    expected = {
        "ent_substance_bacl2": {"ent_element_ba": 1, "ent_element_cl": 2},
        "ent_substance_na2so4": {"ent_element_na": 2, "ent_element_s": 1, "ent_element_o": 4},
        "ent_substance_baso4": {"ent_element_ba": 1, "ent_element_s": 1, "ent_element_o": 4},
        "ent_substance_hno3": {"ent_element_h": 1, "ent_element_n": 1, "ent_element_o": 3},
        "ent_substance_koh": {"ent_element_k": 1, "ent_element_o": 1, "ent_element_h": 1},
        "ent_substance_kno3": {"ent_element_k": 1, "ent_element_n": 1, "ent_element_o": 3},
        "ent_substance_nahco3": {"ent_element_na": 1, "ent_element_h": 1, "ent_element_c": 1, "ent_element_o": 3},
        "ent_substance_co2": {"ent_element_c": 1, "ent_element_o": 2},
    }
    for entity_id, expected_atoms in expected.items():
        actual, charge = _composition_and_charge(kb, entity_id)
        assert actual == expected_atoms
        assert charge == 0


def test_f3b_canonical_reactions_balance_and_conserve() -> None:
    kb = load_knowledge(ROOT)
    for reaction_id in F3B_REACTIONS:
        reaction = kb.reactions[reaction_id]
        reactants = tuple(p["target_id"] for p in reaction["participants"] if p["role"] == "reactant")
        products = tuple(p["target_id"] for p in reaction["participants"] if p["role"] == "product")
        authored = tuple(p["coefficient"]["numerator"] for p in reaction["participants"])
        result = balance(kb, reactants, products)
        assert result.coefficients == authored
        atoms_ok, charge_ok = validate_conservation(kb, reactants, products, result)
        assert atoms_ok is True
        assert charge_ok is True


def test_f3b_reaction_forms_conserve_atoms_and_charge() -> None:
    kb = load_knowledge(ROOT)
    for reaction_id in F3B_REACTIONS:
        for form in kb.reactions[reaction_id]["forms"]:
            atom_totals, charge_total = _authored_conservation(kb, form["participants"])
            assert all(total == 0 for total in atom_totals.values()), (reaction_id, form["form_key"], atom_totals)
            assert charge_total == 0, (reaction_id, form["form_key"], charge_total)


def test_f3b_has_no_duplicate_semantic_keys() -> None:
    kb = load_knowledge(ROOT)
    seen: dict[tuple[str, str], str] = {}
    for entity_id, entity in sorted(kb.entities.items()):
        for key in entity.get("semantic_keys", []):
            semantic_key = (key["scheme"], key["value"])
            assert semantic_key not in seen, (semantic_key, seen[semantic_key], entity_id)
            seen[semantic_key] = entity_id


def test_f3b_all_authored_evidence_refs_resolve() -> None:
    kb = load_knowledge(ROOT)
    f3b_records = [
        record for record in kb.records
        if record["id"].startswith(("ent_", "rxn_f3b_", "ev_f3b_", "src_openstax"))
    ]
    for record in f3b_records:
        for evidence_id in record.get("evidence_ids", []):
            assert evidence_id in kb.evidence
        for assertion in record.get("facet_assertions", []):
            for evidence_id in assertion.get("evidence_ids", []):
                assert evidence_id in kb.evidence
        for assertion in record.get("property_assertions", []):
            for evidence_id in assertion.get("evidence_ids", []):
                assert evidence_id in kb.evidence
        for profile in record.get("speciation_profiles", []):
            for evidence_id in profile.get("evidence_ids", []):
                assert evidence_id in kb.evidence


def test_f3b_teaching_view_members_resolve_without_owning_identity() -> None:
    kb = load_knowledge(ROOT)
    view = kb.teaching_views["view_f3b_hs_aqueous_core"]
    resolvable = set(kb.entities) | set(kb.reactions)
    members: list[str] = []
    for node in view["nodes"]:
        members.extend(node.get("members", []))
    assert members
    assert all(member in resolvable for member in members)
    assert len(set(members)) < len(members)


def test_f3b_inference_coverage_audit_executes_against_converged_rules() -> None:
    kb = load_knowledge(ROOT)
    plans = compile_rules(kb)
    cases = [
        _case("f3b_existing_agcl", [("ent_substance_nacl", "aqueous"), ("ent_substance_agno3", "aqueous")]),
        _case("f3b_existing_neutralization", [("ent_substance_hcl", "aqueous"), ("ent_substance_naoh", "aqueous")]),
        _case("f3b_baso4", [("ent_substance_bacl2", "aqueous"), ("ent_substance_na2so4", "aqueous")]),
        _case("f3b_hno3_koh", [("ent_substance_hno3", "aqueous"), ("ent_substance_koh", "aqueous")]),
        _case("f3b_hcl_nahco3", [("ent_substance_hcl", "aqueous"), ("ent_substance_nahco3", "aqueous")]),
        _case("f3b_no_net_contrast", [("ent_substance_nacl", "aqueous"), ("ent_substance_kno3", "aqueous")]),
    ]
    results = {case["id"]: infer_case(kb, plans, case) for case in cases}
    assert results["f3b_existing_agcl"]["status"] == "inferred"
    assert results["f3b_existing_agcl"]["canonical_match"]["reaction_ids"] == ["rxn_agcl_precipitation"]
    assert results["f3b_existing_neutralization"]["status"] == "inferred"
    assert results["f3b_existing_neutralization"]["canonical_match"]["reaction_ids"] == ["rxn_hcl_naoh_neutralization"]
    assert results["f3b_baso4"]["status"] == "inferred"
    assert results["f3b_baso4"]["canonical_match"]["reaction_ids"] == ["rxn_f3b_baso4_precipitation"]
    assert results["f3b_hno3_koh"]["status"] == "inferred"
    assert results["f3b_hno3_koh"]["canonical_match"]["reaction_ids"] == ["rxn_f3b_hno3_koh_neutralization"]
    assert results["f3b_hcl_nahco3"]["status"] == "no_match"
    assert results["f3b_no_net_contrast"]["status"] == "no_match"


def test_f3b_generated_candidates_do_not_become_canonical_records() -> None:
    kb = load_knowledge(ROOT)
    plans = compile_rules(kb)
    case = _case("f3b_existing_agcl", [("ent_substance_nacl", "aqueous"), ("ent_substance_agno3", "aqueous")])
    result = infer_case(kb, plans, case)
    assert result["status"] == "inferred"
    assert result["candidate_key"].startswith("cand_sha256_")
    assert "id" not in result
    assert result["candidate_key"] not in kb.reactions
    assert result["provenance"]["kind"] == "derived_reaction_candidate"
