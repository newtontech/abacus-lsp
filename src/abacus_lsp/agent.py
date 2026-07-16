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
    "ABACUS206": {
        "summary": "NUMERICAL_ORBITAL count differs from ATOMIC_POSITIONS element count.",
        "next_action": "ensure each atomic species has a matching orbital file",
    },
    "ABACUS207": {
        "summary": "ATOMIC_SPECIES order differs from ATOMIC_POSITIONS order.",
        "next_action": "reorder ATOMIC_SPECIES to match ATOMIC_POSITIONS",
    },
    "ABACUS208": {
        "summary": "latname is set but STRU contains LATTICE_VECTORS.",
        "next_action": "remove latname or replace LATTICE_VECTORS with lattice name",
    },
    "ABACUS209": {
        "summary": "gamma_only overrides normal KPT sampling.",
        "next_action": "edit INPUT or KPT",
    },
    "ABACUS210": {
        "summary": "nscf calculation requires explicit K-point sampling.",
        "next_action": "set KPT mode to 'mp' with non-zero count",
    },
    "ABACUS211": {
        "summary": "Keyword is LCAO-only, ignored with basis_type=pw.",
        "next_action": "remove LCAO-only keyword or switch basis_type to lcao",
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
    "ABACUS305": {
        "summary": "Pseudopotential file not found during ABACUS execution.",
        "next_action": "check pseudo_dir path and ATOMIC_SPECIES pseudopotential filenames",
    },
    "ABACUS306": {
        "summary": "Numerical orbital file not found during ABACUS execution.",
        "next_action": "check orbital_dir path and NUMERICAL_ORBITAL filenames",
    },
    "ABACUS307": {
        "summary": "Illegal or out-of-range K-point encountered.",
        "next_action": "verify K-point definitions in KPT file",
    },
    "ABACUS309": {
        "summary": "Memory allocation failed during ABACUS execution.",
        "next_action": "reduce system size, lower ecutwfc, or increase available memory",
    },
    "ABACUS310": {
        "summary": "MPI or parallel execution error occurred.",
        "next_action": "check MPI configuration or reduce number of processes",
    },
    "ABACUS311": {
        "summary": "DFT+U self-consistency failed.",
        "next_action": "adjust Hubbard U parameters or orbital_corr settings",
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
    """Check if abacus-agent-tools is available as optional backend.

    LLM Wiki: wiki/concepts/Basis_Set_Types.md
    """
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
    """Apply a deterministic fix for a diagnostic code.

    Returns a DiagnosticEnvelope/v1-compatible repair preview or explicit
    refusal reasons for unsafe cases.

    LLM Wiki: wiki/concepts/Basis_Set_Types.md
    """
    # ABACUS205: Add NUMERICAL_ORBITAL section to STRU
    # Handle this case specially since the diagnostic is only generated
    # when NUMERICAL_ORBITAL is NOT present in STRU
    if code == "ABACUS205":
        stru = case_dir / "STRU"
        text = stru.read_text(encoding="utf-8") if stru.exists() else ""
        if "NUMERICAL_ORBITAL" in text:
            return {
                "ok": False,
                "changed": [],
                "code": code,
                "reason": "STRU already contains NUMERICAL_ORBITAL section",
                "diagnostic_envelope": "v1",
                "operation": "fix",
                "safe_to_apply": False,
            }
        if stru.exists():
            preview = (
                text.rstrip()
                + "\n\nNUMERICAL_ORBITAL\n"
                + "# Add orbital files matching ATOMIC_POSITIONS order\n"
            )
            return {
                "ok": True,
                "changed": [str(stru)],
                "code": code,
                "diagnostic_envelope": "v1",
                "operation": "fix",
                "safe_to_apply": True,
                "preview": {
                    "file": str(stru),
                    "action": "append_section",
                    "section": "NUMERICAL_ORBITAL",
                    "diff": (
                        "+ NUMERICAL_ORBITAL\n+ # Add orbital files matching ATOMIC_POSITIONS order"
                    ),
                },
                "applied_fix": {
                    "kind": "insert_section",
                    "file": "STRU",
                    "section": "NUMERICAL_ORBITAL",
                },
            }
        return {
            "ok": False,
            "changed": [],
            "code": code,
            "reason": "STRU file does not exist",
            "diagnostic_envelope": "v1",
            "operation": "fix",
            "safe_to_apply": False,
        }

    diagnostics = analyze_case(case_dir)
    target_diag = None
    for diag in diagnostics:
        if diag.code == code:
            target_diag = diag
            break

    if target_diag is None:
        return {
            "ok": False,
            "changed": [],
            "code": code,
            "reason": f"No diagnostic with code {code} found in case directory",
            "diagnostic_envelope": "v1",
            "operation": "fix",
            "safe_to_apply": False,
        }

    # ABACUS210: Set K-point mode to 'mp' for nscf
    if code == "ABACUS210":
        kpt = case_dir / "KPT"
        text = kpt.read_text(encoding="utf-8") if kpt.exists() else ""
        if kpt.exists():
            preview = "K_POINTS\n0\nmp\n8 8 8 0 0 0\n"
            return {
                "ok": True,
                "changed": [str(kpt)],
                "code": code,
                "diagnostic_envelope": "v1",
                "operation": "fix",
                "safe_to_apply": True,
                "preview": {
                    "file": str(kpt),
                    "action": "replace_content",
                    "content": preview,
                },
                "applied_fix": {
                    "kind": "set_kpoint_mode",
                    "file": "KPT",
                    "mode": "mp",
                },
            }
        return {
            "ok": False,
            "changed": [],
            "code": code,
            "reason": "KPT file does not exist",
            "diagnostic_envelope": "v1",
            "operation": "fix",
            "safe_to_apply": False,
        }

    # ABACUS211: Remove LCAO-only keyword
    if code == "ABACUS211":
        keyword = target_diag.suggested_fix.get("keyword") if target_diag.suggested_fix else None
        if keyword:
            inp = case_dir / "INPUT"
            if inp.exists():
                lines = inp.read_text(encoding="utf-8").splitlines()
                new_lines = [line for line in lines if not line.strip().lower().startswith(keyword)]
                preview = "\n".join(new_lines) + "\n"
                return {
                    "ok": True,
                    "changed": [str(inp)],
                    "code": code,
                    "diagnostic_envelope": "v1",
                    "operation": "fix",
                    "safe_to_apply": True,
                    "preview": {
                        "file": str(inp),
                        "action": "remove_keyword",
                        "keyword": keyword,
                        "lines_removed": len(lines) - len(new_lines),
                    },
                    "applied_fix": {
                        "kind": "remove_keyword",
                        "keyword": keyword,
                    },
                }
        return {
            "ok": False,
            "changed": [],
            "code": code,
            "reason": "Cannot determine keyword to remove",
            "diagnostic_envelope": "v1",
            "operation": "fix",
            "safe_to_apply": False,
        }

    # Runtime errors: provide guidance but refuse automatic fix
    if code.startswith("ABACUS3"):
        return {
            "ok": False,
            "changed": [],
            "code": code,
            "reason": (
                f"Runtime error {code} requires manual investigation. "
                "Check the log file for details and adjust INPUT parameters accordingly."
            ),
            "diagnostic_envelope": "v1",
            "operation": "fix",
            "safe_to_apply": False,
            "suggested_next_steps": EXPLANATIONS.get(code, {}).get("next_action", "inspect log"),
        }

    # Default: no safe automatic fix
    return {
        "ok": False,
        "changed": [],
        "code": code,
        "reason": "no safe automatic fix available for this diagnostic",
        "diagnostic_envelope": "v1",
        "operation": "fix",
        "safe_to_apply": False,
    }


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
