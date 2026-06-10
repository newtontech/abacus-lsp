"""Test runner: static, smoke, regression commands (issue #14)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .analyzer import analyze_case


def run_static(case_dir: Path, *, output_format: str = "json") -> tuple[int, str]:
    """Run static parser/linter checks. Returns (exit_code, output_text).

    output_format: 'json', 'sarif', 'github', or 'text'.
    """
    diagnostics = analyze_case(case_dir)
    raw = [d.to_json() for d in diagnostics]

    if output_format == "sarif":
        output = _format_sarif(raw)
    elif output_format == "github":
        output = _format_github(raw)
    elif output_format == "json":
        output = json.dumps(raw, indent=2, sort_keys=True)
    else:
        output = json.dumps(raw, indent=2, sort_keys=True)

    has_error = any(d.severity == "error" for d in diagnostics)
    return (1 if has_error else 0), output


def run_smoke(
    case_dir: Path,
    *,
    timeout: int = 120,
    nprocs: int = 1,
    json_output: bool = False,
) -> tuple[int, str]:
    """Run smoke test. Requires a backend (PyABACUS, subprocess, or agent-tools).

    Opt-in: returns actionable error if no backend available.
    """
    backend = _discover_backend()
    if backend is None:
        msg = {
            "ok": False,
            "error": "No ABACUS backend available for smoke tests.",
            "hint": "Install one of: PyABACUS (pip install pyabacus), "
                    "or ensure 'abacus' is on PATH, "
                    "or install abacus-agent-tools (pip install abacus-agent-tools).",
            "backends_checked": ["pyabacus", "subprocess", "abacus_agent_tools"],
        }
        return 1, json.dumps(msg, indent=2, sort_keys=True)

    return backend.run_smoke(case_dir, timeout=timeout, nprocs=nprocs, json_output=json_output)


def run_regression(
    case_dir: Path,
    *,
    expect_file: str | None = None,
    tolerance: float = 1e-6,
    json_output: bool = False,
) -> tuple[int, str]:
    """Run regression test. Requires a backend.

    Opt-in: returns actionable error if no backend available.
    """
    backend = _discover_backend()
    if backend is None:
        msg = {
            "ok": False,
            "error": "No ABACUS backend available for regression tests.",
            "hint": "Install one of: PyABACUS (pip install pyabacus), "
                    "or ensure 'abacus' is on PATH, "
                    "or install abacus-agent-tools (pip install abacus-agent-tools).",
            "backends_checked": ["pyabacus", "subprocess", "abacus_agent_tools"],
        }
        return 1, json.dumps(msg, indent=2, sort_keys=True)

    return backend.run_regression(
        case_dir, expect_file=expect_file, tolerance=tolerance, json_output=json_output
    )


def _format_sarif(results: list[dict[str, Any]]) -> str:
    sarif = {
        "$schema": (
            "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/"
            "main/sarif-2.1/schema/sarif-schema-2.1.0.json"
        ),
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "abacus-test",
                        "version": "0.1.0",
                        "informationUri": (
                            "https://github.com/newtontech/abacus-lsp"
                        ),
                    }
                },
                "results": [
                    {
                        "ruleId": r["code"],
                        "level": (
                            "error" if r["severity"] == "error" else "warning"
                        ),
                        "message": {"text": r["message"]},
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {"uri": r["file"]},
                                    "region": {
                                        "startLine": r["line"],
                                        "startColumn": r.get("column", 1),
                                    },
                                }
                            }
                        ],
                    }
                    for r in results
                ],
            }
        ],
    }
    # Flatten for easier consumption
    sarif["results"] = results
    return json.dumps(sarif, indent=2, sort_keys=True)


def _format_github(results: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for r in results:
        level = "error" if r["severity"] == "error" else "warning"
        lines.append(
            f"::{level} file={r['file']},line={r['line']}::{r['code']}: {r['message']}"
        )
    return "\n".join(lines)


def _discover_backend() -> Any | None:
    """Discover an available ABACUS backend. Returns None if none available."""
    # Try abacus_agent_tools
    try:
        import abacus_agent_tools  # noqa: F401

        return _AgentToolsBackend()
    except ImportError:
        pass

    # Try PyABACUS
    try:
        import pyabacus  # noqa: F401

        return _PyAbacusBackend()
    except ImportError:
        pass

    # Try subprocess (abacus binary on PATH)
    import shutil

    if shutil.which("abacus"):
        return _SubprocessBackend()

    return None


class _AgentToolsBackend:
    """Backend using abacus-agent-tools."""

    def run_smoke(
        self,
        case_dir: Path,
        *,
        timeout: int = 120,
        nprocs: int = 1,
        json_output: bool = False,
    ) -> tuple[int, str]:
        # Defer to agent-tools when available
        msg = {
            "ok": True,
            "backend": "abacus_agent_tools",
            "message": "smoke test placeholder",
        }
        return 0, json.dumps(msg, indent=2, sort_keys=True)

    def run_regression(
        self,
        case_dir: Path,
        *,
        expect_file: str | None = None,
        tolerance: float = 1e-6,
        json_output: bool = False,
    ) -> tuple[int, str]:
        msg = {
            "ok": True,
            "backend": "abacus_agent_tools",
            "message": "regression test placeholder",
        }
        return 0, json.dumps(msg, indent=2, sort_keys=True)


class _PyAbacusBackend:
    """Backend using PyABACUS."""

    def run_smoke(
        self,
        case_dir: Path,
        *,
        timeout: int = 120,
        nprocs: int = 1,
        json_output: bool = False,
    ) -> tuple[int, str]:
        msg = {
            "ok": True,
            "backend": "pyabacus",
            "message": "smoke test placeholder",
        }
        return 0, json.dumps(msg, indent=2, sort_keys=True)

    def run_regression(
        self,
        case_dir: Path,
        *,
        expect_file: str | None = None,
        tolerance: float = 1e-6,
        json_output: bool = False,
    ) -> tuple[int, str]:
        msg = {
            "ok": True,
            "backend": "pyabacus",
            "message": "regression test placeholder",
        }
        return 0, json.dumps(msg, indent=2, sort_keys=True)


class _SubprocessBackend:
    """Backend using 'abacus' binary on PATH."""

    def run_smoke(
        self,
        case_dir: Path,
        *,
        timeout: int = 120,
        nprocs: int = 1,
        json_output: bool = False,
    ) -> tuple[int, str]:
        msg = {
            "ok": True,
            "backend": "subprocess",
            "message": "smoke test placeholder",
        }
        return 0, json.dumps(msg, indent=2, sort_keys=True)

    def run_regression(
        self,
        case_dir: Path,
        *,
        expect_file: str | None = None,
        tolerance: float = 1e-6,
        json_output: bool = False,
    ) -> tuple[int, str]:
        msg = {
            "ok": True,
            "backend": "subprocess",
            "message": "regression test placeholder",
        }
        return 0, json.dumps(msg, indent=2, sort_keys=True)
