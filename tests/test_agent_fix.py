"""Tests for agent fix operations with DiagnosticEnvelope/v1 compatibility."""

from __future__ import annotations

from pathlib import Path

from abacus_lsp.agent import apply_fix, explain_diagnostic


def test_explain_diagnostic_returns_envelope_fields() -> None:
    """explain_diagnostic returns code, summary, next_action."""
    result = explain_diagnostic("ABACUS205")
    assert result["code"] == "ABACUS205"
    assert "summary" in result
    assert "next_action" in result


def test_explain_diagnostic_unknown_code() -> None:
    """explain_diagnostic handles unknown codes gracefully."""
    result = explain_diagnostic("UNKNOWN999")
    assert result["code"] == "UNKNOWN999"
    assert "No detailed explanation" in result["summary"]


def test_apply_fix_abacus205_returns_preview(tmp_path: Path) -> None:
    """apply_fix for ABACUS205 returns a repair preview with envelope fields."""
    (tmp_path / "INPUT").write_text(
        "INPUT_PARAMETERS\nbasis_type lcao\ncalculation scf\n",
        encoding="utf-8",
    )
    (tmp_path / "STRU").write_text(
        "ATOMIC_SPECIES\nSi 28.085 Si.upf\n\nATOMIC_POSITIONS\nDirect\nSi\n0.0\n1\n0.0 0.0 0.0\n",
        encoding="utf-8",
    )
    (tmp_path / "KPT").write_text("K_POINTS\n0\nGamma\n1 1 1 0 0 0\n", encoding="utf-8")

    result = apply_fix(tmp_path, "ABACUS205")

    assert result["ok"] is True
    assert result["code"] == "ABACUS205"
    assert result["diagnostic_envelope"] == "v1"
    assert result["operation"] == "fix"
    assert result["safe_to_apply"] is True
    assert "preview" in result
    assert "applied_fix" in result
    assert result["preview"]["section"] == "NUMERICAL_ORBITAL"


def test_apply_fix_abacus205_refuses_when_section_exists(tmp_path: Path) -> None:
    """apply_fix for ABACUS205 refuses when STRU already has NUMERICAL_ORBITAL."""
    (tmp_path / "INPUT").write_text(
        "INPUT_PARAMETERS\nbasis_type lcao\ncalculation scf\n",
        encoding="utf-8",
    )
    (tmp_path / "STRU").write_text(
        "ATOMIC_SPECIES\nSi 28.085 Si.upf\n\nNUMERICAL_ORBITAL\nSi.orb\n\n"
        "LATTICE_CONSTANT\n1.0\n\nATOMIC_POSITIONS\nDirect\nSi\n0.0\n1\n0.0 0.0 0.0\n",
        encoding="utf-8",
    )
    (tmp_path / "KPT").write_text("K_POINTS\n0\nGamma\n1 1 1 0 0 0\n", encoding="utf-8")

    result = apply_fix(tmp_path, "ABACUS205")

    assert result["ok"] is False
    assert result["diagnostic_envelope"] == "v1"
    assert result["safe_to_apply"] is False
    assert "already contains" in result["reason"]


def test_apply_fix_abacus210_returns_preview(tmp_path: Path) -> None:
    """apply_fix for ABACUS210 returns a repair preview."""
    (tmp_path / "INPUT").write_text(
        "INPUT_PARAMETERS\ncalculation nscf\nbasis_type pw\necutwfc 50\n",
        encoding="utf-8",
    )
    (tmp_path / "STRU").write_text(
        "ATOMIC_SPECIES\nSi 28.085 Si.upf\n\nLATTICE_CONSTANT\n1.0\n\n"
        "ATOMIC_POSITIONS\nDirect\nSi\n0.0\n1\n0.0 0.0 0.0\n",
        encoding="utf-8",
    )
    (tmp_path / "KPT").write_text("K_POINTS\n0\nGamma\n1 1 1 0 0 0\n", encoding="utf-8")

    result = apply_fix(tmp_path, "ABACUS210")

    assert result["ok"] is True
    assert result["code"] == "ABACUS210"
    assert result["diagnostic_envelope"] == "v1"
    assert result["safe_to_apply"] is True
    assert "preview" in result


def test_apply_fix_abacus211_returns_preview(tmp_path: Path) -> None:
    """apply_fix for ABACUS211 returns a repair preview."""
    (tmp_path / "INPUT").write_text(
        "INPUT_PARAMETERS\ncalculation scf\nbasis_type pw\necutwfc 50\ndmesh 0.01\n",
        encoding="utf-8",
    )
    (tmp_path / "STRU").write_text(
        "ATOMIC_SPECIES\nSi 28.085 Si.upf\n\nLATTICE_CONSTANT\n1.0\n\n"
        "ATOMIC_POSITIONS\nDirect\nSi\n0.0\n1\n0.0 0.0 0.0\n",
        encoding="utf-8",
    )
    (tmp_path / "KPT").write_text("K_POINTS\n0\nGamma\n1 1 1 0 0 0\n", encoding="utf-8")

    result = apply_fix(tmp_path, "ABACUS211")

    assert result["ok"] is True
    assert result["code"] == "ABACUS211"
    assert result["diagnostic_envelope"] == "v1"
    assert result["safe_to_apply"] is True
    assert "preview" in result
    assert result["preview"]["keyword"] == "dmesh"


def test_apply_fix_runtime_error_refuses(tmp_path: Path) -> None:
    """apply_fix for runtime errors (ABACUS3xx) refuses with guidance."""
    (tmp_path / "INPUT").write_text(
        "INPUT_PARAMETERS\ncalculation scf\n",
        encoding="utf-8",
    )
    (tmp_path / "STRU").write_text(
        "ATOMIC_SPECIES\nSi 28.085 Si.upf\n\nLATTICE_CONSTANT\n1.0\n\n"
        "ATOMIC_POSITIONS\nDirect\nSi\n0.0\n1\n0.0 0.0 0.0\n",
        encoding="utf-8",
    )
    (tmp_path / "KPT").write_text("K_POINTS\n0\nGamma\n1 1 1 0 0 0\n", encoding="utf-8")
    (tmp_path / "running.log").write_text("SCF is NOT converged!\n", encoding="utf-8")

    result = apply_fix(tmp_path, "ABACUS301")

    assert result["ok"] is False
    assert result["diagnostic_envelope"] == "v1"
    assert result["safe_to_apply"] is False
    assert "Runtime error" in result["reason"]
    assert "suggested_next_steps" in result


def test_apply_fix_unknown_code_refuses(tmp_path: Path) -> None:
    """apply_fix for unknown codes refuses gracefully."""
    (tmp_path / "INPUT").write_text(
        "INPUT_PARAMETERS\ncalculation scf\n",
        encoding="utf-8",
    )
    (tmp_path / "STRU").write_text("ATOMIC_POSITIONS\nDirect\n", encoding="utf-8")
    (tmp_path / "KPT").write_text("K_POINTS\n0\nGamma\n1 1 1 0 0 0\n", encoding="utf-8")

    result = apply_fix(tmp_path, "UNKNOWN999")

    assert result["ok"] is False
    assert result["diagnostic_envelope"] == "v1"
    assert result["safe_to_apply"] is False
    assert "No diagnostic" in result["reason"]
