"""Agent JSON protocol for query-diagnostics, explain, apply-fix, export-context."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .analyzer import (
    KNOWN_INPUT_KEYWORDS,
    KNOWN_KPT_MODES,
    KNOWN_STRU_SECTIONS,
    analyze_case,
)

# ── Diagnostic explanations ───────────────────────────────────────────────────

DIAGNOSTIC_DATABASE: dict[str, dict[str, Any]] = {
    "ABACUS001": {
        "code": "ABACUS001",
        "severity": "error",
        "description": "INPUT file is missing the INPUT_PARAMETERS header.",
        "suggested_fix": {"kind": "add_header", "header": "INPUT_PARAMETERS"},
    },
    "ABACUS002": {
        "code": "ABACUS002",
        "severity": "warning",
        "description": "Unknown INPUT keyword. Check spelling against ABACUS documentation.",
        "suggested_fix": {"kind": "check_keyword_spelling"},
    },
    "ABACUS004": {
        "code": "ABACUS004",
        "severity": "error",
        "description": "KPT file format error.",
        "suggested_fix": {"kind": "fix_kpt_format"},
    },
    "ABACUS005": {
        "code": "ABACUS005",
        "severity": "error",
        "description": (
            "Unknown KPT mode. Must be one of: "
            "gamma, mp, direct, cartesian, line, line_cartesian."
        ),
        "suggested_fix": {"kind": "fix_kpt_mode"},
    },
    "ABACUS006": {
        "code": "ABACUS006",
        "severity": "error",
        "description": "STRU atom count mismatch.",
        "suggested_fix": {"kind": "fix_atom_count"},
    },
    "ABACUS007": {
        "code": "ABACUS007",
        "severity": "warning",
        "description": "Duplicate INPUT keyword. ABACUS uses the last value.",
        "suggested_fix": {"kind": "remove_duplicate"},
    },
    "ABACUS201": {
        "code": "ABACUS201",
        "severity": "error",
        "description": "INPUT file is missing.",
        "suggested_fix": {"kind": "create_file", "file": "INPUT"},
    },
    "ABACUS202": {
        "code": "ABACUS202",
        "severity": "error",
        "description": "KPT file is missing.",
        "suggested_fix": {"kind": "create_file", "file": "KPT"},
    },
    "ABACUS204": {
        "code": "ABACUS204",
        "severity": "warning",
        "description": "Referenced file (pseudo_dir or orbital_dir) does not exist.",
        "suggested_fix": {"kind": "check_file_path"},
    },
    "ABACUS205": {
        "code": "ABACUS205",
        "severity": "error",
        "description": "basis_type=lcao requires NUMERICAL_ORBITAL entries in STRU.",
        "suggested_fix": {
            "kind": "insert_section",
            "file": "STRU",
            "section": "NUMERICAL_ORBITAL",
            "after": "ATOMIC_SPECIES",
        },
    },
    "ABACUS207": {
        "code": "ABACUS207",
        "severity": "warning",
        "description": "ATOMIC_SPECIES order differs from ATOMIC_POSITIONS order.",
        "suggested_fix": {"kind": "reorder_species"},
    },
    "ABACUS208": {
        "code": "ABACUS208",
        "severity": "warning",
        "description": "latname is set but STRU contains LATTICE_VECTORS.",
        "suggested_fix": {"kind": "remove_latname_or_lattice_vectors"},
    },
    "ABACUS209": {
        "code": "ABACUS209",
        "severity": "warning",
        "description": "gamma_only=1 will overwrite KPT; multi-k KPT is ignored.",
        "suggested_fix": {"kind": "remove_gamma_only_or_fix_kpt"},
    },
}


def query_diagnostics(case_dir: Path, *, json_output: bool = True) -> tuple[int, str]:
    """Run diagnostics and return structured agent JSON.

    Returns (exit_code, json_text).
    JSON includes: ok, blocking_errors, next_action, diagnostics with suggested_fixes.
    """
    diagnostics = analyze_case(case_dir)
    raw = [d.to_json() for d in diagnostics]

    blocking = [d for d in diagnostics if d.severity == "error"]
    warnings = [d for d in diagnostics if d.severity != "error"]
    blocking_count = len(blocking)

    if blocking_count == 0 and not warnings:
        next_action = "proceed"
    elif blocking_count == 0:
        next_action = "review_warnings"
    else:
        next_action = "fix_errors"

    result = {
        "ok": blocking_count == 0,
        "blocking_errors": blocking_count,
        "warning_count": len(warnings),
        "next_action": next_action,
        "diagnostics": raw,
    }

    exit_code = 1 if blocking_count > 0 else 0
    return exit_code, json.dumps(result, indent=2, sort_keys=True)


def explain_diagnostic(code: str, *, json_output: bool = True) -> tuple[int, str]:
    """Explain a diagnostic code in structured JSON."""
    info = DIAGNOSTIC_DATABASE.get(code)
    if info is None:
        result = {"code": code, "known": False, "description": f"Unknown diagnostic code: {code}"}
    else:
        result = {"known": True, **info}

    return 0, json.dumps(result, indent=2, sort_keys=True)


def apply_fix(case_dir: Path, code: str, *, json_output: bool = True) -> tuple[int, str]:
    """Apply a suggested fix for the given diagnostic code.

    Currently supports ABACUS205 (insert NUMERICAL_ORBITAL section).
    """
    if code == "ABACUS205":
        return _apply_fix_205(case_dir, json_output=json_output)

    result = {
        "applied": False,
        "code": code,
        "error": f"No automated fix available for {code}",
        "changes": [],
    }
    return 1, json.dumps(result, indent=2, sort_keys=True)


def _apply_fix_205(case_dir: Path, *, json_output: bool = True) -> tuple[int, str]:
    """Fix ABACUS205: insert NUMERICAL_ORBITAL section into STRU after ATOMIC_SPECIES."""
    stru_path = case_dir / "STRU"
    if not stru_path.exists():
        result = {
            "applied": False,
            "code": "ABACUS205",
            "error": "STRU file not found",
            "changes": [],
        }
        return 1, json.dumps(result, indent=2, sort_keys=True)

    text = stru_path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    # Find ATOMIC_SPECIES section end
    new_lines: list[str] = []
    inserted = False
    i = 0
    while i < len(lines):
        new_lines.append(lines[i])
        stripped = lines[i].strip().upper()
        if stripped == "ATOMIC_SPECIES" and not inserted:
            # Read past species entries until we hit another section or blank+section
            i += 1
            while i < len(lines):
                s = lines[i].strip()
                if s.upper() in KNOWN_STRU_SECTIONS:
                    break
                new_lines.append(lines[i])
                i += 1
            # Insert NUMERICAL_ORBITAL placeholder
            new_lines.append("\n")
            new_lines.append("NUMERICAL_ORBITAL\n")
            new_lines.append("# Add orbital files here, e.g. Si_gga_8au_60Ry_2s2p1d.orb\n")
            inserted = True
            continue
        i += 1

    if not inserted:
        # Append at end
        new_lines.append("\nNUMERICAL_ORBITAL\n")
        new_lines.append("# Add orbital files here\n")
        inserted = True

    stru_path.write_text("".join(new_lines), encoding="utf-8")

    result = {
        "applied": True,
        "code": "ABACUS205",
        "changes": [
            {
                "file": "STRU",
                "action": "insert_section",
                "section": "NUMERICAL_ORBITAL",
            }
        ],
    }
    return 0, json.dumps(result, indent=2, sort_keys=True)


def export_context(case_dir: Path, *, for_agent: bool = True) -> tuple[int, str]:
    """Export context artifacts to .abacus-lsp/ directory.

    Creates: context.json, diagnostics.json, schema-used.json, files-index.json.
    """
    export_dir = case_dir / ".abacus-lsp"
    export_dir.mkdir(exist_ok=True)

    # Gather diagnostics
    diagnostics = analyze_case(case_dir)
    raw_diags = [d.to_json() for d in diagnostics]

    # Gather files index
    files_index = _build_files_index(case_dir)

    # Gather schema info
    schema = {
        "input_keywords": sorted(KNOWN_INPUT_KEYWORDS),
        "kpt_modes": sorted(KNOWN_KPT_MODES),
        "stru_sections": sorted(KNOWN_STRU_SECTIONS),
    }

    # Build context
    blocking_count = sum(1 for d in diagnostics if d.severity == "error")
    context = {
        "case_dir": str(case_dir.resolve()),
        "ok": blocking_count == 0,
        "blocking_errors": blocking_count,
        "warning_count": sum(1 for d in diagnostics if d.severity != "error"),
        "diagnostics": raw_diags,
        "files": [f["name"] for f in files_index],
        "schema": schema,
    }

    # Write artifacts
    (export_dir / "context.json").write_text(
        json.dumps(context, indent=2, sort_keys=True), encoding="utf-8"
    )
    (export_dir / "diagnostics.json").write_text(
        json.dumps(raw_diags, indent=2, sort_keys=True), encoding="utf-8"
    )
    (export_dir / "schema-used.json").write_text(
        json.dumps(schema, indent=2, sort_keys=True), encoding="utf-8"
    )
    (export_dir / "files-index.json").write_text(
        json.dumps(files_index, indent=2, sort_keys=True), encoding="utf-8"
    )

    return 0, json.dumps({"ok": True, "export_dir": str(export_dir)}, indent=2, sort_keys=True)


def _build_files_index(case_dir: Path) -> list[dict[str, Any]]:
    """Build a files index for the case directory."""
    known_files = ["INPUT", "STRU", "KPT"]
    index: list[dict[str, Any]] = []
    for name in known_files:
        path = case_dir / name
        if path.exists():
            stat = path.stat()
            index.append({
                "name": name,
                "path": str(path),
                "size": stat.st_size,
                "exists": True,
            })
        else:
            index.append({
                "name": name,
                "path": str(path),
                "exists": False,
            })
    return index
