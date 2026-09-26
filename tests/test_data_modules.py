import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from compiler.application import export_modules
from compiler.build import tree_digest
from compiler.canonical import canonical_json_bytes
from compiler.rules import compile_rules
from compiler.source import knowledge_from_records, load_knowledge


ROOT = Path(__file__).resolve().parents[1]


def test_three_modules_are_complete_disjoint_roots_with_valid_independent_dependencies(tmp_path):
    manifest = export_modules(ROOT, tmp_path / "first", "WORKTREE")
    export_modules(ROOT, tmp_path / "second", "WORKTREE")
    assert tree_digest(tmp_path / "first") == tree_digest(tmp_path / "second")
    schema = json.loads((tmp_path / "first/knowledge-record.schema.json").read_text(encoding="utf-8"))
    kb = load_knowledge(ROOT)
    expected = {
        "elements": {key for key, item in kb.entities.items() if item["entity_kind"] == "element"},
        "substances": {key for key, item in kb.entities.items() if item["entity_kind"] != "element"},
        "equations": set(kb.reactions) | set(kb.rules),
    }
    merged = {}
    for name, entry in manifest["modules"].items():
        path = tmp_path / "first" / entry["file"]
        raw = path.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == manifest["artifacts"][entry["file"]]
        data = json.loads(raw)
        assert set(data["root_ids"]) == expected[name]
        assert not (set(data["root_ids"]) & set(data["dependency_ids"]))
        assert set(data["root_ids"]) | set(data["dependency_ids"]) == {r["id"] for r in data["records"]}
        standalone = knowledge_from_records(((path, r) for r in data["records"]), Draft202012Validator(schema))
        assert standalone.source_digest == data["record_digest"]
        assert len(compile_rules(standalone)) == len(standalone.rules)
        assert entry["record_count"] == len(standalone.records)
        for record in data["records"]:
            encoded = canonical_json_bytes(record)
            assert merged.setdefault(record["id"], encoded) == encoded
    assert set().union(*expected.values()) <= set(merged)
    assert not any(json.loads(value)["record_type"] == "teaching_view" for value in merged.values())
