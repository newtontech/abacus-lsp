from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .analyzer import analyze_case
from .formatter import format_file


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
    parser.add_argument(
        "--normalize", action="store_true",
        help="apply normalize formatter (reorder by category, collapse duplicates)",
    )
    parser.add_argument(
        "--keyword-case", choices=["lower", "upper", "keep"], default="lower",
        help="keyword casing for normalize mode (default: lower)",
    )
    parser.add_argument(
        "--bool-style", choices=["1/0", "true/false", "t/f", "yes/no", "keep"],
        default="keep",
        help="boolean value style for normalize mode (default: keep)",
    )
    parser.add_argument("files", nargs="+", type=Path)
    args = parser.parse_args(argv)
    for path in args.files:
        text = path.read_text(encoding="utf-8")
        formatted = format_file(
            text,
            path.name,
            normalize=args.normalize,
            keyword_case=args.keyword_case,
            bool_style=args.bool_style,
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
