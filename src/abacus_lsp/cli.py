from __future__ import annotations

import argparse
import json
from pathlib import Path

from .agent import apply_fix, explain_diagnostic, export_context, query_diagnostics
from .analyzer import analyze_case
from .formatter import FormatOptions, format_file_text
from .schema import build_schema
from .server import run_stdio
from .test_runner import run_regression, run_smoke, run_static


def schema_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="abacus-schema")
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("build")
    build.add_argument("--abacus-bin")
    build.add_argument("--docs-cache", type=Path)
    build.add_argument("--version", default="builtin")
    build.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "build":
        payload = build_schema(args.abacus_bin, args.docs_cache, args.version)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return 0
    return 2


def lsp_main(argv: list[str] | None = None) -> int:
    argv = list(argv) if argv is not None else None
    effective_argv = argv
    if effective_argv is None:
        import sys

        effective_argv = sys.argv[1:]
    subcommands = {
        "query-diagnostics",
        "explain-diagnostic",
        "apply-fix",
        "export-context",
    }
    if effective_argv and effective_argv[0] in subcommands:
        return agent_main(effective_argv)
    parser = argparse.ArgumentParser(prog="abacus-lsp")
    parser.add_argument("--stdio", action="store_true", help="start the LSP server on stdio")
    args = parser.parse_args(effective_argv)
    if not args.stdio:
        parser.error("use --stdio or an agent subcommand")
    return run_stdio()


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
    parser.add_argument("--normalize", action="store_true", help="canonicalize display order")
    parser.add_argument("--keyword-case", choices=["lower", "upper", "keep"], default="lower")
    parser.add_argument(
        "--bool-style",
        choices=["1/0", "true/false", "t/f", "yes/no", "keep"],
        default="keep",
    )
    parser.add_argument("files", nargs="+", type=Path)
    args = parser.parse_args(argv)
    for path in args.files:
        text = path.read_text(encoding="utf-8")
        formatted = format_file_text(
            path.name,
            text,
            FormatOptions(
                normalize=args.normalize,
                keyword_case=args.keyword_case,
                boolean_style=args.bool_style,
            ),
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
    smoke = subparsers.add_parser("smoke")
    smoke.add_argument("case", type=Path)
    smoke.add_argument("--backend", default="subprocess")
    smoke.add_argument("--timeout", type=int, default=120)
    smoke.add_argument("--nprocs", type=int, default=1)
    smoke.add_argument("--abacus-command", default="abacus")
    regression = subparsers.add_parser("regression")
    regression.add_argument("case", type=Path)
    regression.add_argument("--expect", type=Path, required=True)
    regression.add_argument("--tolerance", default="")
    args = parser.parse_args(argv)
    if args.command == "static":
        result = run_static(args.case)
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            for item in result["diagnostics"]:
                print(
                    f"{item['file']}:{item['line']}:{item['column']}: "
                    f"{item['severity']} {item['code']} {item['message']}"
                )
        return 0 if result["ok"] else 1
    if args.command == "smoke":
        result = run_smoke(args.case, args.backend, args.timeout, args.nprocs, args.abacus_command)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["ok"] else 1
    if args.command == "regression":
        tolerance = _parse_tolerance(args.tolerance)
        result = run_regression(args.case, args.expect, tolerance)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["ok"] else 1
    return 2


def agent_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="abacus-lsp")
    subparsers = parser.add_subparsers(dest="command", required=True)
    query = subparsers.add_parser("query-diagnostics")
    query.add_argument("case", type=Path)
    subparsers.add_parser("explain-diagnostic").add_argument("code")
    fix = subparsers.add_parser("apply-fix")
    fix.add_argument("case", type=Path)
    fix.add_argument("--code", required=True)
    export = subparsers.add_parser("export-context")
    export.add_argument("case", type=Path)
    export.add_argument("--for-agent", action="store_true")
    args = parser.parse_args(argv)
    if args.command == "query-diagnostics":
        result = query_diagnostics(args.case)
    elif args.command == "explain-diagnostic":
        result = explain_diagnostic(args.code)
    elif args.command == "apply-fix":
        result = apply_fix(args.case, args.code)
    elif args.command == "export-context":
        result = export_context(args.case)
    else:
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("ok", True) else 1


def _parse_tolerance(raw: str) -> dict[str, float]:
    result: dict[str, float] = {}
    for item in raw.split(","):
        if not item:
            continue
        key, value = item.split("=", 1)
        result[key] = float(value)
    return result
