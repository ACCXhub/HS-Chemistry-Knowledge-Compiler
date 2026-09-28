from copy import deepcopy
from pathlib import Path

import pytest

from compiler.application import InferenceSession, export_bundle
from compiler.reaction_forms import derive_aqueous_ionic_form
from compiler.source import SourceError, load_knowledge


@pytest.fixture(scope="module")
def session(tmp_path_factory):
    path = tmp_path_factory.mktemp("endpoints")
    export_bundle(Path(__file__).resolve().parents[1], path, "WORKTREE")
    return InferenceSession(path)


def request(regime):
    return {"id": "endpoint_request", "reactants": [
        {"target_id": "ent_substance_alcl3", "phase": "aqueous"},
        {"target_id": "ent_substance_naoh", "phase": "aqueous"}],
        "context": {"medium": "aqueous", "temperature_regime": "ambient",
                    "alkali_regime": regime}}


@pytest.mark.parametrize("regime,n,product", [
    ("precipitation_endpoint", 3, "ent_substance_al_oh_3"),
    ("excess", 4, "ent_species_al_oh_4_minus"),
])
def test_public_endpoint_selection_and_ionic_equation(session, regime, n, product):
    case = request(regime)
    result = session.infer(case)["result"]
    reaction = "rxn_alcl3_naoh_" + regime
    assert result["status"] == "inferred"
    assert result["canonical_match"]["reaction_ids"] == [reaction]
    kb = load_knowledge(Path(__file__).resolve().parents[1])
    form = derive_aqueous_ionic_form(kb, reaction, "net_ionic", case["context"])
    assert form["status"] == "derived"
    assert {p["target_id"]: p["coefficient"] for p in form["participants"]} == {
        "ent_species_al_3plus": {"numerator": 1, "denominator": 1},
        "ent_species_oh_minus": {"numerator": n, "denominator": 1},
        product: {"numerator": 1, "denominator": 1},
    }
    assert form["validation"] == {"atoms": True, "charge": True}
    for key in case["context"]:
        missing = deepcopy(case)
        del missing["context"][key]
        assert session.infer(missing)["result"]["status"] == "indeterminate"


def test_unsupported_amount_label_rejected(session):
    with pytest.raises(SourceError) as exc:
        session.infer(request("a_little"))
    assert exc.value.code == "request_invalid"
