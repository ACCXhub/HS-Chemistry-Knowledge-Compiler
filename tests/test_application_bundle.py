from pathlib import Path

import pytest

from compiler.application import InferenceSession, export_bundle
from compiler.build import tree_digest
from compiler.canonical import sha256_hex, write_canonical_json
from compiler.engine import infer_case
from compiler.rules import compile_rules
from compiler.source import SourceError, load_cases, load_knowledge


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def bundle(tmp_path_factory):
    folder = tmp_path_factory.mktemp("bundle")
    export_bundle(ROOT, folder, "WORKTREE")
    return folder, InferenceSession(folder)


def test_portable_bundle_roundtrip_preserves_every_fixture_outcome(bundle, tmp_path):
    folder, session = bundle
    kb = load_knowledge(ROOT)
    plans = compile_rules(kb)
    export_bundle(ROOT, tmp_path, "WORKTREE")
    assert tree_digest(folder) == tree_digest(tmp_path)
    for case in load_cases(ROOT):
        result = session.infer(case)
        assert result["result"] == infer_case(kb, plans, case), case["id"]
        assert result["source_semantic_digest"] == kb.source_digest
        assert result["release_id"] == session.manifest["release_id"]


@pytest.mark.parametrize("change", ["phase", "duplicate", "quantity", "concentration", "temperature", "extra", "empty", "many"])
def test_public_request_rejects_unsupported_or_lossy_input(bundle, change):
    _, session = bundle
    request = {"id": "api_example", "reactants": [
        {"target_id": "ent_substance_hcl", "phase": "aqueous"},
        {"target_id": "ent_substance_naoh", "phase": "aqueous"},
    ], "context": {"medium": "aqueous"}}
    if change == "phase":
        request["reactants"][0]["phase"] = "aq"
    elif change == "duplicate":
        request["reactants"][1] = {"target_id": "ent_substance_hcl", "phase": "gas"}
    elif change == "quantity":
        request["reactants"][0]["amount"] = 1
    elif change == "concentration":
        request["context"]["concentration"] = "concentrated"
    elif change == "temperature":
        request["context"]["temperature_regime"] = 25
    elif change == "extra":
        request["products"] = []
    elif change == "empty":
        request["reactants"] = []
    else:
        request["reactants"] *= 2
    with pytest.raises(SourceError) as caught:
        session.infer(request)
    assert caught.value.code == "request_invalid"


def test_caller_cannot_mutate_session_via_input_or_output(bundle):
    _, session = bundle
    request = next(case for case in load_cases(ROOT) if case["id"] == "case_hbr_na2s2o3_unstored")
    expected = session.infer(request)
    result = session.infer(request)
    result["result"]["participants"].clear()
    result["result"]["proof_trace"].clear()
    session.manifest["artifacts"].clear()
    assert session.infer(request) == expected
    request["context"]["medium"] = "mutated"
    assert expected["result"]["proof_trace"][0]["context"]["medium"] == "aqueous"


@pytest.mark.parametrize("change", ["checksum", "compiler", "versions", "digest", "references"])
def test_loader_rejects_corrupt_or_incompatible_release(bundle, tmp_path, change):
    folder, session = bundle
    for path in folder.glob("*.json"):
        (tmp_path / path.name).write_bytes(path.read_bytes())
    manifest = session.manifest
    if change == "checksum":
        with (tmp_path / "knowledge.json").open("ab") as stream:
            stream.write(b" ")
    elif change == "compiler":
        manifest["compiler"]["version"] = "0.0.0"
    elif change == "versions":
        manifest["versions"]["rule_dsl"] = "99.0.0"
    elif change == "digest":
        manifest["source_semantic_digest"] = "0" * 64
    else:
        import json
        data = json.loads((tmp_path / "knowledge.json").read_text(encoding="utf-8"))
        data["records"] = [record for record in data["records"] if record["id"] != "ent_substance_hcl"]
        manifest["artifacts"]["knowledge.json"] = write_canonical_json(tmp_path / "knowledge.json", data)
    manifest["release_id"] = "hschem_" + sha256_hex({key: value for key, value in manifest.items() if key != "release_id"})
    write_canonical_json(tmp_path / "manifest.json", manifest)
    with pytest.raises(SourceError):
        InferenceSession(tmp_path)
