from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .analyzer import analyze_case
from .diagnostics import Diagnostic
from .schema import SchemaRegistry

EXPLANATIONS = {
    "ABACUS205": {
        "summary": "LCAO basis calculations require NUMERICAL_ORBITAL entries in STRU.",
        "next_action": "edit STRU",
    },
    "ABACUS209": {
        "summary": "gamma_only overrides normal KPT sampling.",
        "next_action": "edit INPUT or KPT",
    },
    "ABACUS301": {
        "summary": "SCF convergence failed during the self-consistent field iteration.",
        "next_action": "increase scf_nmax or relax scf_thr in INPUT",
    },
    "ABACUS302": {
        "summary": "Geometry optimization did not converge within the allowed steps.",
        "next_action": "increase relax_nstep or adjust BFGS parameters",
    },
    "ABACUS303": {
        "summary": "A segmentation fault occurred during ABACUS execution.",
        "next_action": "check INPUT parameters or reduce system size",
    },
    "ABACUS304": {
        "summary": "A file error was detected in the runtime log.",
        "next_action": "verify all file paths in INPUT (pseudo_dir, orbital_dir, etc.)",
    },
    "ABACUS309": {
        "summary": "Memory allocation failed during ABACUS execution.",
        "next_action": "reduce system size, lower ecutwfc, or increase available memory",
    },
}

CAPABILITIES = {
    "log_parser": {
        "patterns": [
            "scf_not_converged",
            "geometry_not_converged",
            "segfault",
            "file_error",
            "memory_allocation_error",
        ],
        "log_paths": ["running.log", "run.log", "OUT.ABACUS/running_0.log"],
    },
    "agent_tools_backend": {
        "optional": True,
        "description": "ABACUS-agent-tools for advanced validation and execution",
    },
}


def get_agent_tools_status() -> dict[str, Any]:
    """Check if abacus-agent-tools is available as optional backend."""
    try:
        import abacus_agent_tools  # noqa: F401

        return {"available": True, "backend": "abacus-agent-tools"}
    except ImportError:
        return {"available": False, "backend": None}


def query_diagnostics(case_dir: Path) -> dict[str, Any]:
    diagnostics = analyze_case(case_dir)
    blocking = [item for item in diagnostics if item.severity == "error"]
    return {
        "ok": not blocking,
        "blocking_errors": [item.to_json() for item in blocking],
        "diagnostics": [item.to_json() for item in diagnostics],
        "next_action": _next_action(blocking),
    }


def explain_diagnostic(code: str) -> dict[str, Any]:
    return {
        "code": code,
        **EXPLANATIONS.get(
            code,
            {
                "summary": "No detailed explanation is available for this diagnostic yet.",
                "next_action": "inspect diagnostic evidence",
            },
        ),
    }


def apply_fix(case_dir: Path, code: str) -> dict[str, Any]:
    if code == "ABACUS205":
        stru = case_dir / "STRU"
        text = stru.read_text(encoding="utf-8") if stru.exists() else ""
        if "NUMERICAL_ORBITAL" not in text:
            stru.write_text(
                text.rstrip()
                + "\n\nNUMERICAL_ORBITAL\n"
                + "# Add orbital files matching ATOMIC_POSITIONS order\n",
                encoding="utf-8",
            )
            return {"ok": True, "changed": [str(stru)], "code": code}
    return {"ok": False, "changed": [], "code": code, "reason": "no safe automatic fix"}


def export_context(case_dir: Path, out_dir: Path | None = None) -> dict[str, Any]:
    out_dir = out_dir or case_dir / ".abacus-lsp"
    out_dir.mkdir(parents=True, exist_ok=True)
    diagnostics = query_diagnostics(case_dir)
    schema = SchemaRegistry.builtin().with_project_overrides(case_dir).to_json()
    files = sorted(
        str(path.relative_to(case_dir))
        for path in case_dir.rglob("*")
        if path.is_file() and ".abacus-lsp" not in path.parts
    )
    artifacts = {
        "diagnostics": out_dir / "diagnostics.json",
        "schema": out_dir / "schema-used.json",
        "files": out_dir / "files-index.json",
        "context": out_dir / "context.json",
    }
    artifacts["diagnostics"].write_text(
        json.dumps(diagnostics, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    artifacts["schema"].write_text(json.dumps(schema, indent=2, sort_keys=True), encoding="utf-8")
    artifacts["files"].write_text(json.dumps(files, indent=2, sort_keys=True), encoding="utf-8")
    context = {
        "case_dir": str(case_dir),
        "ok": diagnostics["ok"],
        "diagnostic_count": len(diagnostics["diagnostics"]),
        "artifacts": {key: str(value) for key, value in artifacts.items()},
    }
    artifacts["context"].write_text(json.dumps(context, indent=2, sort_keys=True), encoding="utf-8")
    return context


def _next_action(blocking: list[Diagnostic]) -> str:
    if not blocking:
        return "none"
    if blocking[0].suggested_fix:
        return str(blocking[0].suggested_fix.get("kind", "edit input files"))
    return "edit input files"
