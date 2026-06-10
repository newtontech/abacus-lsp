from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .analyzer import analyze_case, format_input_text


def lsp_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="abacus-lsp")
    parser.add_argument("--stdio", action="store_true", help="start the LSP server on stdio")
    args = parser.parse_args(argv)
    if not args.stdio:
        parser.error("only --stdio is currently supported")
    print(
        "abacus-lsp server scaffold: LSP protocol implementation is tracked in roadmap issues",
        file=sys.stderr,
    )
    return 0


def lint_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="abacus-lint")
    parser.add_argument("case", type=Path, help="ABACUS case directory containing INPUT/STRU/KPT")
    parser.add_argument("--json", action="store_true", help="emit JSON diagnostics")
    args = parser.parse_args(argv)
    diagnostics = analyze_case(args.case)
    if args.json:
        print(json.dumps([item.to_json() for item in diagnostics], indent=2, sort_keys=True))
    else:
        for item in diagnostics:
            print(
                f"{item.file}:{item.line}:{item.column}: "
                f"{item.severity} {item.code} {item.message}"
            )
    return 1 if any(item.severity == "error" for item in diagnostics) else 0


def fmt_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="abacus-fmt")
    parser.add_argument("-w", "--write", action="store_true", help="write files in place")
    parser.add_argument("files", nargs="+", type=Path)
    args = parser.parse_args(argv)
    for path in args.files:
        text = path.read_text(encoding="utf-8")
        formatted = (
            format_input_text(text) if path.name.upper() == "INPUT" else text.rstrip() + "\n"
        )
        if args.write:
            path.write_text(formatted, encoding="utf-8")
        else:
            print(formatted, end="")
    return 0


def test_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="abacus-test")
    subparsers = parser.add_subparsers(dest="command", required=True)
    static = subparsers.add_parser("static", help="run static parser/linter checks")
    static.add_argument("case", type=Path)
    static.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if args.command == "static":
        return lint_main([str(args.case), *(["--json"] if args.json else [])])
    return 2
