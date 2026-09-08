from __future__ import annotations

import argparse
import json
from pathlib import Path

from .build import audit_repository, compile_repository, validate


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(prog="hs-chem-compiler")
    result.add_argument("--repo-root", type=Path, default=Path.cwd())
    sub = result.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    compile_cmd = sub.add_parser("compile")
    compile_cmd.add_argument("--output", type=Path, default=Path("build/f2-compile"))
    compile_cmd.add_argument("--source-revision", default="WORKTREE")
    audit_cmd = sub.add_parser("audit")
    audit_cmd.add_argument("--output", type=Path, default=Path("build/f2-audit"))
    audit_cmd.add_argument("--source-revision", default="WORKTREE")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    root = args.repo_root.resolve()
    if args.command == "validate":
        print(json.dumps(validate(root), ensure_ascii=False, sort_keys=True))
        return 0
    output = args.output
    if not output.is_absolute():
        output = root / output
    if args.command == "compile":
        result = compile_repository(root, output, args.source_revision)
    else:
        result = audit_repository(root, output, args.source_revision)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
