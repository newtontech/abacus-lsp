from __future__ import annotations

from pathlib import Path

from abacus_lsp.agent import CAPABILITIES
from abacus_lsp.analyzer import analyze_case, parse_log

# ---------------------------------------------------------------------------
# parse_log unit tests
# ---------------------------------------------------------------------------


def test_log_parser_scf_not_converged(tmp_path: Path) -> None:
    """ABACUS301: SCF convergence failure."""
    log = tmp_path / "running.log"
    log.write_text("SCF iteration 1\nSCF is NOT converged!\n", encoding="utf-8")
    diags = parse_log(log)
    assert any(d.code == "ABACUS301" for d in diags)
    assert diags[0].severity == "error"
    assert "SCF" in diags[0].evidence[0]


def test_log_parser_scf_convergence_failed(tmp_path: Path) -> None:
    """ABACUS301: SCF convergence failure via 'CONVERGENCE FAILED'."""
    log = tmp_path / "running.log"
    log.write_text("SCF CONVERGENCE FAILED after 100 steps\n", encoding="utf-8")
    diags = parse_log(log)
    assert any(d.code == "ABACUS301" for d in diags)


def test_log_parser_geometry_not_converged(tmp_path: Path) -> None:
    """ABACUS302: Geometry optimization did not converge."""
    log = tmp_path / "running.log"
    log.write_text("GEOMETRY is NOT CONVERGED\n", encoding="utf-8")
    diags = parse_log(log)
    assert any(d.code == "ABACUS302" for d in diags)
    assert diags[0].severity == "error"


def test_log_parser_geometry_convergence_failed(tmp_path: Path) -> None:
    """ABACUS302: Geometry convergence failure via 'CONVERGENCE FAILED'."""
    log = tmp_path / "running.log"
    log.write_text("GEOMETRY CONVERGENCE FAILED\n", encoding="utf-8")
    diags = parse_log(log)
    assert any(d.code == "ABACUS302" for d in diags)


def test_log_parser_segfault(tmp_path: Path) -> None:
    """ABACUS303: Segfault detected."""
    log = tmp_path / "running.log"
    log.write_text("Segmentation fault at address 0x0\n", encoding="utf-8")
    diags = parse_log(log)
    assert any(d.code == "ABACUS303" for d in diags)
    assert diags[0].severity == "error"


def test_log_parser_segfault_one_word(tmp_path: Path) -> None:
    """ABACUS303: Segfault via 'SEGFAULT' keyword."""
    log = tmp_path / "running.log"
    log.write_text("Caught SEGFAULT signal\n", encoding="utf-8")
    diags = parse_log(log)
    assert any(d.code == "ABACUS303" for d in diags)


def test_log_parser_file_error_open(tmp_path: Path) -> None:
    """ABACUS304: File error with 'OPEN' keyword."""
    log = tmp_path / "running.log"
    log.write_text("ERROR: cannot open file pseudo.upf\n", encoding="utf-8")
    diags = parse_log(log)
    assert any(d.code == "ABACUS304" for d in diags)
    assert "pseudo.upf" in diags[0].message


def test_log_parser_file_error_file(tmp_path: Path) -> None:
    """ABACUS304: File error with 'FILE' keyword."""
    log = tmp_path / "running.log"
    log.write_text("ERROR: FILE not found orbital.orb\n", encoding="utf-8")
    diags = parse_log(log)
    assert any(d.code == "ABACUS304" for d in diags)


def test_log_parser_memory_allocation_error(tmp_path: Path) -> None:
    """ABACUS309: Memory allocation error."""
    log = tmp_path / "running.log"
    log.write_text("ALLOCATE ERROR: insufficient memory\n", encoding="utf-8")
    diags = parse_log(log)
    assert any(d.code == "ABACUS309" for d in diags)
    assert diags[0].severity == "error"


def test_log_parser_empty(tmp_path: Path) -> None:
    """No errors in a clean log."""
    log = tmp_path / "running.log"
    log.write_text("Everything fine\nCalculation completed\n", encoding="utf-8")
    diags = parse_log(log)
    assert diags == []


def test_log_parser_nonexistent(tmp_path: Path) -> None:
    """Non-existent log file returns empty diagnostics."""
    diags = parse_log(tmp_path / "nonexistent.log")
    assert diags == []


def test_log_parser_multiple_errors(tmp_path: Path) -> None:
    """Multiple error patterns in one log produce multiple diagnostics."""
    log = tmp_path / "running.log"
    log.write_text(
        "SCF is NOT converged!\n"
        "GEOMETRY is NOT CONVERGED\n"
        "Caught SEGFAULT signal\n"
        "ERROR: cannot open file test.upf\n"
        "ALLOCATE ERROR: out of memory\n",
        encoding="utf-8",
    )
    diags = parse_log(log)
    codes = {d.code for d in diags}
    assert "ABACUS301" in codes
    assert "ABACUS302" in codes
    assert "ABACUS303" in codes
    assert "ABACUS304" in codes
    assert "ABACUS309" in codes


# ---------------------------------------------------------------------------
# Integration: analyze_case picks up log errors
# ---------------------------------------------------------------------------


def test_analyze_case_geometry_not_converged(tmp_path: Path) -> None:
    """analyze_case detects geometry convergence failure via running.log."""
    (tmp_path / "INPUT").write_text("INPUT_PARAMETERS\ncalculation relax\n", encoding="utf-8")
    (tmp_path / "STRU").write_text("ATOMIC_POSITIONS\nDirect\n", encoding="utf-8")
    (tmp_path / "KPT").write_text("K_POINTS\n0\nGamma\n1 1 1 0 0 0\n", encoding="utf-8")
    (tmp_path / "running.log").write_text("GEOMETRY is NOT CONVERGED\n", encoding="utf-8")
    diagnostics = analyze_case(tmp_path)
    assert any(d.code == "ABACUS302" and d.severity == "error" for d in diagnostics), (
        f"Expected geometry not converged (ABACUS302), got: {[d.message for d in diagnostics]}"
    )


def test_analyze_case_segfault(tmp_path: Path) -> None:
    """analyze_case detects segfault via running.log."""
    (tmp_path / "INPUT").write_text("INPUT_PARAMETERS\ncalculation scf\n", encoding="utf-8")
    (tmp_path / "STRU").write_text("ATOMIC_POSITIONS\nDirect\n", encoding="utf-8")
    (tmp_path / "KPT").write_text("K_POINTS\n0\nGamma\n1 1 1 0 0 0\n", encoding="utf-8")
    (tmp_path / "running.log").write_text("SEGFAULT\n", encoding="utf-8")
    diagnostics = analyze_case(tmp_path)
    assert any(d.code == "ABACUS303" for d in diagnostics)


def test_analyze_case_file_error(tmp_path: Path) -> None:
    """analyze_case detects file error via running.log."""
    (tmp_path / "INPUT").write_text("INPUT_PARAMETERS\ncalculation scf\n", encoding="utf-8")
    (tmp_path / "STRU").write_text("ATOMIC_POSITIONS\nDirect\n", encoding="utf-8")
    (tmp_path / "KPT").write_text("K_POINTS\n0\nGamma\n1 1 1 0 0 0\n", encoding="utf-8")
    (tmp_path / "running.log").write_text("ERROR: cannot OPEN file missing.upf\n", encoding="utf-8")
    diagnostics = analyze_case(tmp_path)
    assert any(d.code == "ABACUS304" for d in diagnostics)


def test_analyze_case_memory_error(tmp_path: Path) -> None:
    """analyze_case detects memory allocation error via running.log."""
    (tmp_path / "INPUT").write_text("INPUT_PARAMETERS\ncalculation scf\n", encoding="utf-8")
    (tmp_path / "STRU").write_text("ATOMIC_POSITIONS\nDirect\n", encoding="utf-8")
    (tmp_path / "KPT").write_text("K_POINTS\n0\nGamma\n1 1 1 0 0 0\n", encoding="utf-8")
    (tmp_path / "running.log").write_text("ALLOCATE ERROR: out of memory\n", encoding="utf-8")
    diagnostics = analyze_case(tmp_path)
    assert any(d.code == "ABACUS309" for d in diagnostics)


# ---------------------------------------------------------------------------
# Capability contract
# ---------------------------------------------------------------------------


def test_log_parser_capability_registered() -> None:
    """log_parser capability is present in the agent CAPABILITIES registry."""
    assert "log_parser" in CAPABILITIES
    cap = CAPABILITIES["log_parser"]
    assert "scf_not_converged" in cap["patterns"]
    assert "geometry_not_converged" in cap["patterns"]
    assert "segfault" in cap["patterns"]
    assert "file_error" in cap["patterns"]
    assert "memory_allocation_error" in cap["patterns"]
    assert "running.log" in cap["log_paths"]


def test_log_parser_capability_patterns_cover_all_codes() -> None:
    """Each diagnostic code produced by parse_log maps to a capability pattern."""
    cap = CAPABILITIES["log_parser"]
    expected_patterns = [
        "scf_not_converged",
        "geometry_not_converged",
        "segfault",
        "file_error",
        "memory_allocation_error",
    ]
    for pattern in expected_patterns:
        assert pattern in cap["patterns"], f"Missing pattern: {pattern}"
