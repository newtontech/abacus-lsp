from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .agent import apply_fix, explain_diagnostic, export_context, query_diagnostics
from .analyzer import analyze_case, format_input_text
from .backends import (
    list_backends,
    modify_input,
    prepare_input,
    run_backend_command,
)
from .testrunner import run_regression, run_smoke, run_static


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

    # static
    static = subparsers.add_parser("static", help="run static parser/linter checks")
    static.add_argument("case", type=Path)
    static.add_argument("--json", action="store_true")
    static.add_argument("--sarif", action="store_true", help="emit SARIF-like output")
    static.add_argument("--github", action="store_true", help="emit GitHub Actions annotations")

    # smoke
    smoke = subparsers.add_parser(
        "smoke", help="run a tiny ABACUS job (requires backend)"
    )
    smoke.add_argument("case", type=Path)
    smoke.add_argument("--json", action="store_true")
    smoke.add_argument("--timeout", type=int, default=120, help="timeout in seconds")
    smoke.add_argument("--nprocs", type=int, default=1, help="number of MPI processes")

    # regression
    regression = subparsers.add_parser(
        "regression", help="compare converged results with tolerances (requires backend)"
    )
    regression.add_argument("case", type=Path)
    regression.add_argument("--json", action="store_true")
    regression.add_argument("--expect", type=str, default=None, help="expected results JSON file")
    regression.add_argument("--tolerance", type=float, default=1e-6, help="numerical tolerance")

    args = parser.parse_args(argv)

    if args.command == "static":
        fmt = "json"
        if args.sarif:
            fmt = "sarif"
        elif args.github:
            fmt = "github"
        code, output = run_static(args.case, output_format=fmt)
        print(output)
        return code

    if args.command == "smoke":
        code, output = run_smoke(
            args.case, timeout=args.timeout, nprocs=args.nprocs, json_output=args.json
        )
        print(output)
        return code

    if args.command == "regression":
        code, output = run_regression(
            args.case,
            expect_file=args.expect,
            tolerance=args.tolerance,
            json_output=args.json,
        )
        print(output)
        return code

    return 2


# ── Agent JSON protocol commands (issue #15) ──────────────────────────────────


def agent_main(argv: list[str] | None = None) -> int:
    """CLI entry point for agent-facing commands."""
    parser = argparse.ArgumentParser(prog="abacus-lsp")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # query-diagnostics
    qd = subparsers.add_parser("query-diagnostics", help="query diagnostics for a case")
    qd.add_argument("case", type=Path)
    qd.add_argument("--json", action="store_true", help="emit structured JSON")

    # explain-diagnostic
    ed = subparsers.add_parser("explain-diagnostic", help="explain a diagnostic code")
    ed.add_argument("code", type=str, help="diagnostic code e.g. ABACUS205")
    ed.add_argument("--json", action="store_true")

    # apply-fix
    af = subparsers.add_parser("apply-fix", help="apply a suggested fix")
    af.add_argument("case", type=Path)
    af.add_argument("--code", type=str, required=True, help="diagnostic code to fix")
    af.add_argument("--json", action="store_true")

    # export-context
    ec = subparsers.add_parser("export-context", help="export context artifacts")
    ec.add_argument("case", type=Path)
    ec.add_argument("--for-agent", action="store_true", help="export for agent consumption")

    # backend (issue #16)
    be = subparsers.add_parser("backend", help="optional backend commands")
    be_sub = be.add_subparsers(dest="backend_command", required=True)

    be_list = be_sub.add_parser("list", help="list available backends")
    be_list.add_argument("--json", action="store_true")

    be_run = be_sub.add_parser("run-scf", help="run SCF calculation via backend")
    be_run.add_argument("case", type=Path)
    be_run.add_argument("--json", action="store_true")

    be_relax = be_sub.add_parser("run-relax", help="run relaxation via backend")
    be_relax.add_argument("case", type=Path)
    be_relax.add_argument("--json", action="store_true")

    be_band = be_sub.add_parser("run-band", help="run band structure via backend")
    be_band.add_argument("case", type=Path)
    be_band.add_argument("--json", action="store_true")

    be_dos = be_sub.add_parser("run-dos", help="run DOS via backend")
    be_dos.add_argument("case", type=Path)
    be_dos.add_argument("--json", action="store_true")

    be_prep = be_sub.add_parser("prepare-input", help="prepare input via backend")
    be_prep.add_argument("case", type=Path)
    be_prep.add_argument("--json", action="store_true")

    be_mod = be_sub.add_parser("modify-input", help="modify an INPUT parameter")
    be_mod.add_argument("case", type=Path)
    be_mod.add_argument("--key", type=str, required=True)
    be_mod.add_argument("--value", type=str, required=True)
    be_mod.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)

    if args.command == "query-diagnostics":
        code, output = query_diagnostics(args.case, json_output=args.json)
        print(output)
        return code

    if args.command == "explain-diagnostic":
        code, output = explain_diagnostic(args.code, json_output=args.json)
        print(output)
        return code

    if args.command == "apply-fix":
        code, output = apply_fix(args.case, args.code, json_output=args.json)
        print(output)
        return code

    if args.command == "export-context":
        code, output = export_context(args.case, for_agent=args.for_agent)
        print(output)
        return code

    if args.command == "backend":
        return _handle_backend(args)

    return 2


def _handle_backend(args: argparse.Namespace) -> int:
    bc = args.backend_command

    if bc == "list":
        code, output = list_backends(json_output=args.json)
        print(output)
        return code

    if bc == "prepare-input":
        code, output = prepare_input(args.case, json_output=args.json)
        print(output)
        return code

    if bc == "modify-input":
        code, output = modify_input(
            args.case, key=args.key, value=args.value, json_output=args.json
        )
        print(output)
        return code

    # All other backend commands require a real backend
    command_map = {
        "run-scf": "run-scf",
        "run-relax": "run-relax",
        "run-band": "run-band",
        "run-dos": "run-dos",
    }
    cmd_name = command_map.get(bc, bc)
    code, output = run_backend_command(cmd_name, args.case, json_output=getattr(args, "json", True))
    print(output)
    return code


if __name__ == "__main__":
    # Allow running as `python -m abacus_lsp.cli`
    # Dispatch based on first positional arg
    _raw_args = sys.argv[1:]

    _agent_commands = {
        "query-diagnostics", "explain-diagnostic", "apply-fix",
        "export-context", "backend",
    }
    _test_commands = {"static", "smoke", "regression"}
    _test_prefix = {"test"}  # e.g. `test static ...`
    _lint_commands = {"lint"}
    _fmt_commands = {"fmt"}

    if _raw_args and _raw_args[0] in _agent_commands:
        sys.exit(agent_main(_raw_args))
    elif _raw_args and _raw_args[0] in _test_commands:
        sys.exit(test_main(_raw_args))
    elif _raw_args and _raw_args[0] in _test_prefix:
        # `test static ...` -> strip "test" and dispatch to test_main
        sys.exit(test_main(_raw_args[1:]))
    elif _raw_args and _raw_args[0] in _lint_commands:
        sys.exit(lint_main(_raw_args[1:]))
    elif _raw_args and _raw_args[0] in _fmt_commands:
        sys.exit(fmt_main(_raw_args[1:]))
    elif _raw_args and _raw_args[0] in {"--stdio"}:
        sys.exit(lsp_main(_raw_args))
    elif _raw_args and _raw_args[0] in {"--help", "-h"}:
        print("Usage: python -m abacus_lsp.cli <command> [options]")
        print("Commands: query-diagnostics, explain-diagnostic, apply-fix, export-context,")
        print("          backend, static, smoke, regression, lint, fmt, --stdio")
        sys.exit(0)
    else:
        # Default to agent_main which has its own argparse
        sys.exit(agent_main(_raw_args))
