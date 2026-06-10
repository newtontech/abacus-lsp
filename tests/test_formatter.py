"""Tests for safe and normalize formatters (issues #9 and #10)."""
from __future__ import annotations

from pathlib import Path

import pytest

from abacus_lsp.formatter import (
    normalize_format_input,
    safe_format_input,
    safe_format_kpt,
    safe_format_stru,
)

# ---------------------------------------------------------------------------
# Safe INPUT formatter tests (issue #9)
# ---------------------------------------------------------------------------


class TestSafeInput:
    """Safe formatter for INPUT files."""

    def test_aligns_columns(self) -> None:
        """Keys and inline comments are aligned across entries."""
        text = "INPUT_PARAMETERS\nsuffix MgO\necutwfc 100 # Ry\n"
        result = safe_format_input(text)
        # max_key=7, max_val_with_comment=3
        assert result == "INPUT_PARAMETERS\nsuffix   MgO\necutwfc  100  # Ry\n"

    def test_aligns_columns_multi(self) -> None:
        """All three columns aligned when multiple inline comments exist."""
        text = "INPUT_PARAMETERS\necutwfc 100 # energy cutoff\nscf_thr 1e-6 # convergence\n"
        result = safe_format_input(text)
        assert "ecutwfc  100   # energy cutoff\n" in result
        assert "scf_thr  1e-6  # convergence\n" in result

    def test_preserves_comments(self) -> None:
        """Standalone comment lines are preserved in their original positions."""
        text = "INPUT_PARAMETERS\n# important comment\necutwfc 100\n"
        result = safe_format_input(text)
        assert "# important comment" in result
        lines = result.splitlines()
        assert lines[1] == "# important comment"
        assert lines[2].startswith("ecutwfc")

    def test_preserves_inline_comments(self) -> None:
        """Inline comments after values are preserved and aligned."""
        text = "INPUT_PARAMETERS\necutwfc 100 # cutoff\nbasis_type lcao\n"
        result = safe_format_input(text)
        assert "# cutoff" in result

    def test_preserves_duplicate_keys(self) -> None:
        """Duplicate key-value pairs are preserved in order."""
        text = "INPUT_PARAMETERS\necutwfc 50\necutwfc 100\n"
        result = safe_format_input(text)
        lines = [
            ln for ln in result.splitlines()
            if ln.strip() and not ln.strip().startswith("#")
        ]
        param_lines = [ln for ln in lines if ln != "INPUT_PARAMETERS"]
        assert len(param_lines) == 2
        assert "50" in param_lines[0]
        assert "100" in param_lines[1]

    def test_preserves_order(self) -> None:
        """Parameter order is unchanged after formatting."""
        text = "INPUT_PARAMETERS\ncalculation scf\necutwfc 100\nbasis_type lcao\n"
        result = safe_format_input(text)
        param_lines = [
            ln for ln in result.splitlines()
            if ln.strip() and ln.strip() != "INPUT_PARAMETERS"
            and not ln.strip().startswith("#")
        ]
        keys = [ln.split()[0] for ln in param_lines]
        assert keys == ["calculation", "ecutwfc", "basis_type"]

    def test_ensures_trailing_newline(self) -> None:
        """Output always ends with exactly one newline."""
        assert safe_format_input("INPUT_PARAMETERS\necutwfc 100").endswith("\n")
        assert safe_format_input("INPUT_PARAMETERS\necutwfc 100\n").endswith("\n")
        assert not safe_format_input("INPUT_PARAMETERS\necutwfc 100\n").endswith("\n\n")

    def test_idempotent(self) -> None:
        """Formatting already-formatted text produces identical output."""
        text = (
            "INPUT_PARAMETERS\n"
            "suffix   MgO\n"
            "ecutwfc  100  # Ry\n"
            "calculation  scf\n"
            "\n"
            "# a comment\n"
            "basis_type   lcao\n"
        )
        once = safe_format_input(text)
        twice = safe_format_input(once)
        assert once == twice

    def test_idempotent_complex(self) -> None:
        """Idempotent with duplicates, comments, and blank lines."""
        text = (
            "INPUT_PARAMETERS\n"
            "ecutwfc 50\n"
            "ecutwfc 100  # effective\n"
            "# mid comment\n"
            "scf_thr 1e-6\n"
            "\n"
            "basis_type lcao\n"
        )
        once = safe_format_input(text)
        twice = safe_format_input(once)
        assert once == twice

    def test_preserves_blank_lines(self) -> None:
        """Blank lines within the parameter block are preserved."""
        text = "INPUT_PARAMETERS\necutwfc 100\n\nbasis_type lcao\n"
        result = safe_format_input(text)
        assert "\n\n" in result

    def test_no_header(self) -> None:
        """Files without INPUT_PARAMETERS header are preserved."""
        text = "some random text\nmore text\n"
        result = safe_format_input(text)
        assert "some random text" in result
        assert result.endswith("\n")

    def test_empty_file(self) -> None:
        """Empty files produce a single newline."""
        assert safe_format_input("") == "\n"

    def test_header_only(self) -> None:
        """Files with only the INPUT_PARAMETERS header."""
        result = safe_format_input("INPUT_PARAMETERS\n")
        assert result == "INPUT_PARAMETERS\n"

    def test_preserves_pre_header_content(self) -> None:
        """Content before INPUT_PARAMETERS header is preserved."""
        text = "# comment before header\nINPUT_PARAMETERS\necutwfc 100\n"
        result = safe_format_input(text)
        assert result.startswith("# comment before header\n")


# ---------------------------------------------------------------------------
# Safe STRU formatter tests (issue #9)
# ---------------------------------------------------------------------------


class TestSafeStru:
    """Safe formatter for STRU files."""

    def test_preserves_sections(self) -> None:
        """All sections and their content are preserved."""
        text = (
            "ATOMIC_SPECIES\n"
            "Si 28.085 Si.upf\n"
            "\n"
            "LATTICE_CONSTANT\n"
            "10.2\n"
            "\n"
            "LATTICE_VECTORS\n"
            "1.0 0.0 0.0\n"
            "0.0 1.0 0.0\n"
            "0.0 0.0 1.0\n"
        )
        result = safe_format_stru(text)
        assert "ATOMIC_SPECIES" in result
        assert "LATTICE_CONSTANT" in result
        assert "LATTICE_VECTORS" in result

    def test_preserves_comments(self) -> None:
        """Comments within STRU are preserved."""
        text = "ATOMIC_SPECIES\n# a comment\nSi 28.085 Si.upf\n"
        result = safe_format_stru(text)
        assert "# a comment" in result

    def test_normalizes_whitespace(self) -> None:
        """Internal whitespace in data lines is normalized."""
        text = "ATOMIC_SPECIES\nSi   28.085   Si.upf\n"
        result = safe_format_stru(text)
        # Should normalize multiple spaces to one
        assert "Si 28.085 Si.upf" in result

    def test_idempotent(self) -> None:
        """Formatting already-formatted STRU produces identical output."""
        text = (
            "ATOMIC_SPECIES\n"
            "Si 28.085 Si.upf\n"
            "O 15.999 O.upf\n"
            "\n"
            "LATTICE_CONSTANT\n"
            "10.2\n"
            "\n"
            "LATTICE_VECTORS\n"
            "1.0 0.0 0.0\n"
            "0.0 1.0 0.0\n"
            "0.0 0.0 1.0\n"
        )
        once = safe_format_stru(text)
        twice = safe_format_stru(once)
        assert once == twice

    def test_ensures_trailing_newline(self) -> None:
        """Output always ends with exactly one newline."""
        assert safe_format_stru("ATOMIC_SPECIES\nSi 28 Si.upf").endswith("\n")
        assert not safe_format_stru("ATOMIC_SPECIES\nSi 28 Si.upf\n").endswith("\n\n")

    def test_preserves_order(self) -> None:
        """Section order is preserved."""
        text = (
            "LATTICE_CONSTANT\n10.2\n\nATOMIC_SPECIES\nSi 28 Si.upf\n"
        )
        result = safe_format_stru(text)
        lattice_pos = result.index("LATTICE_CONSTANT")
        species_pos = result.index("ATOMIC_SPECIES")
        assert lattice_pos < species_pos

    def test_preserves_atomic_positions(self) -> None:
        """ATOMIC_POSITIONS section content is preserved."""
        text = (
            "ATOMIC_POSITIONS\n"
            "Direct\n"
            "Si\n"
            "0.0\n"
            "1\n"
            "0.0 0.0 0.0\n"
        )
        result = safe_format_stru(text)
        assert "Direct" in result
        assert "0.0 0.0 0.0" in result


# ---------------------------------------------------------------------------
# Safe KPT formatter tests (issue #9)
# ---------------------------------------------------------------------------


class TestSafeKpt:
    """Safe formatter for KPT files."""

    def test_preserves_content(self) -> None:
        """KPT content is preserved."""
        text = "K_POINTS\n0\nGamma\n1 1 1 0 0 0\n"
        result = safe_format_kpt(text)
        assert "K_POINTS" in result
        assert "Gamma" in result
        assert "1 1 1 0 0 0" in result

    def test_normalizes_whitespace(self) -> None:
        """Internal whitespace is normalized."""
        text = "K_POINTS\n0\nGamma\n1   1   1   0   0   0\n"
        result = safe_format_kpt(text)
        assert "1 1 1 0 0 0" in result

    def test_idempotent(self) -> None:
        """Formatting already-formatted KPT produces identical output."""
        text = "K_POINTS\n0\nGamma\n1 1 1 0 0 0\n"
        once = safe_format_kpt(text)
        twice = safe_format_kpt(once)
        assert once == twice

    def test_ensures_trailing_newline(self) -> None:
        """Output always ends with exactly one newline."""
        assert safe_format_kpt("K_POINTS\n0\nGamma\n1 1 1 0 0 0").endswith("\n")
        assert not safe_format_kpt("K_POINTS\n0\nGamma\n1 1 1 0 0 0\n").endswith("\n\n")

    def test_preserves_comments(self) -> None:
        """Comments in KPT are preserved."""
        text = "K_POINTS\n0\n# a comment\nGamma\n1 1 1 0 0 0\n"
        result = safe_format_kpt(text)
        assert "# a comment" in result

    def test_handles_mp_mode(self) -> None:
        """Handles Monkhurst-Pack mode KPT."""
        text = "K_POINTS\n0\nMP\n4 4 4 0 0 0\n"
        result = safe_format_kpt(text)
        assert "MP" in result
        assert "4 4 4 0 0 0" in result


# ---------------------------------------------------------------------------
# Normalize INPUT formatter tests (issue #10)
# ---------------------------------------------------------------------------


class TestNormalizeInput:
    """Normalize formatter for INPUT files."""

    def test_groups_by_category(self) -> None:
        """Keywords are grouped by category with comment headers."""
        text = "INPUT_PARAMETERS\necutwfc 100\ncalculation scf\n"
        result = normalize_format_input(text)
        # Calculation Control should come before Planewave Basis
        calc_cat = result.index("Calculation Control")
        pw_cat = result.index("Planewave Basis")
        assert calc_cat < pw_cat
        # calculation should be under Calculation Control
        calc_kw = result.index("calculation")
        assert calc_kw > calc_cat
        # ecutwfc should be under Planewave Basis
        ecut_kw = result.index("ecutwfc")
        assert ecut_kw > pw_cat

    def test_comments_duplicates(self) -> None:
        """Earlier duplicate values are turned into comments with [dup] marker."""
        text = "INPUT_PARAMETERS\necutwfc 50\necutwfc 100\n"
        result = normalize_format_input(text)
        # Should have one active ecutwfc and one commented duplicate
        assert "# [dup] ecutwfc 50" in result
        # The last value should be the active one
        lines = result.splitlines()
        active = [
            ln for ln in lines
            if ln.strip().startswith("ecutwfc") and not ln.strip().startswith("#")
        ]
        assert len(active) == 1
        assert "100" in active[0]

    def test_idempotent(self) -> None:
        """Normalizing already-normalized text produces identical output."""
        text = "INPUT_PARAMETERS\necutwfc 100\ncalculation scf\nbasis_type lcao\n"
        once = normalize_format_input(text)
        twice = normalize_format_input(once)
        assert once == twice

    def test_idempotent_with_duplicates(self) -> None:
        """Normalize with duplicates is idempotent."""
        text = "INPUT_PARAMETERS\necutwfc 50\necutwfc 100\ncalculation scf\n"
        once = normalize_format_input(text)
        twice = normalize_format_input(once)
        assert once == twice

    def test_keyword_casing_lower(self) -> None:
        """Keywords are lowercased by default."""
        text = "INPUT_PARAMETERS\nECUTWFC 100\nCalculation scf\n"
        result = normalize_format_input(text)
        assert "ecutwfc" in result
        assert "calculation" in result

    def test_keyword_casing_keep(self) -> None:
        """keyword_case='keep' preserves original casing."""
        text = "INPUT_PARAMETERS\nECUTWFC 100\n"
        result = normalize_format_input(text, keyword_case="keep")
        assert "ECUTWFC" in result

    def test_boolean_style_true_false(self) -> None:
        """Boolean values can be normalized to true/false."""
        text = "INPUT_PARAMETERS\nout_band 1\ngamma_only 0\n"
        result = normalize_format_input(text, bool_style="true/false")
        assert "true" in result
        assert "false" in result

    def test_boolean_style_keep(self) -> None:
        """bool_style='keep' preserves original values."""
        text = "INPUT_PARAMETERS\nout_band 1\n"
        result = normalize_format_input(text, bool_style="keep")
        assert "1" in result

    def test_not_default(self) -> None:
        """Normalize mode produces different output than safe mode."""
        text = "INPUT_PARAMETERS\necutwfc 100\ncalculation scf\n"
        safe_result = safe_format_input(text)
        norm_result = normalize_format_input(text)
        # Normalize reorders by category, safe preserves original order
        assert safe_result != norm_result

    def test_unknown_keywords_in_other(self) -> None:
        """Unknown keywords go into an Other section."""
        text = "INPUT_PARAMETERS\nmy_custom_param 42\n"
        result = normalize_format_input(text)
        assert "Other" in result or "my_custom_param" in result

    def test_category_headers_format(self) -> None:
        """Category headers use the # --- <name> --- format."""
        text = "INPUT_PARAMETERS\ncalculation scf\n"
        result = normalize_format_input(text)
        assert "# --- Calculation Control ---" in result


# ---------------------------------------------------------------------------
# CLI tests for abacus-fmt (issues #9 and #10)
# ---------------------------------------------------------------------------


class TestFmtCli:
    """Tests for the abacus-fmt command-line interface."""

    def test_stdout(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        """Without -w, formatted output goes to stdout."""
        from abacus_lsp.cli import fmt_main
        infile = tmp_path / "INPUT"
        infile.write_text("INPUT_PARAMETERS\necutwfc 100 # Ry\n", encoding="utf-8")
        fmt_main([str(infile)])
        captured = capsys.readouterr()
        assert "ecutwfc" in captured.out
        assert "# Ry" in captured.out

    def test_write_in_place(self, tmp_path: Path) -> None:
        """With -w, files are written in place."""
        from abacus_lsp.cli import fmt_main
        infile = tmp_path / "INPUT"
        infile.write_text("INPUT_PARAMETERS\necutwfc 100\n", encoding="utf-8")
        fmt_main(["-w", str(infile)])
        result = infile.read_text(encoding="utf-8")
        assert result != "INPUT_PARAMETERS\necutwfc 100\n"
        assert "ecutwfc" in result

    def test_write_stru(self, tmp_path: Path) -> None:
        """STRU files are formatted with -w."""
        from abacus_lsp.cli import fmt_main
        infile = tmp_path / "STRU"
        infile.write_text("ATOMIC_SPECIES\nSi   28.085   Si.upf\n", encoding="utf-8")
        fmt_main(["-w", str(infile)])
        result = infile.read_text(encoding="utf-8")
        assert "Si 28.085 Si.upf" in result

    def test_normalize_flag(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        """--normalize activates normalize mode."""
        from abacus_lsp.cli import fmt_main
        infile = tmp_path / "INPUT"
        infile.write_text("INPUT_PARAMETERS\necutwfc 100\ncalculation scf\n", encoding="utf-8")
        fmt_main(["--normalize", str(infile)])
        captured = capsys.readouterr()
        assert "# ---" in captured.out

    def test_multiple_files(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        """Multiple files can be formatted in one invocation."""
        from abacus_lsp.cli import fmt_main
        infile = tmp_path / "INPUT"
        infile.write_text("INPUT_PARAMETERS\necutwfc 100\n", encoding="utf-8")
        kptfile = tmp_path / "KPT"
        kptfile.write_text("K_POINTS\n0\nGamma\n1   1   1   0   0   0\n", encoding="utf-8")
        fmt_main([str(infile), str(kptfile)])
        captured = capsys.readouterr()
        assert "ecutwfc" in captured.out
        assert "Gamma" in captured.out

    def test_normalize_not_default_without_flag(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Without --normalize, output uses safe mode (no category headers)."""
        from abacus_lsp.cli import fmt_main

        infile = tmp_path / "INPUT"
        infile.write_text(
            "INPUT_PARAMETERS\necutwfc 100\ncalculation scf\n", encoding="utf-8"
        )
        fmt_main([str(infile)])
        captured = capsys.readouterr()
        # Safe mode does NOT add category headers
        assert "# ---" not in captured.out
