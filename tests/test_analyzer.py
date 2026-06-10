from __future__ import annotations

from pathlib import Path

from abacus_lsp.analyzer import analyze_case, format_input_text


def test_cross_file_lcao_requires_numerical_orbital(tmp_path: Path) -> None:
    (tmp_path / "INPUT").write_text(
        "INPUT_PARAMETERS\nbasis_type lcao\ncalculation scf\n",
        encoding="utf-8",
    )
    (tmp_path / "STRU").write_text(
        """ATOMIC_SPECIES
Si 28.085 Si.upf

LATTICE_CONSTANT
1.0

ATOMIC_POSITIONS
Direct
Si
0.0
1
0.0 0.0 0.0
""",
        encoding="utf-8",
    )
    (tmp_path / "KPT").write_text("K_POINTS\n0\nGamma\n1 1 1 0 0 0\n", encoding="utf-8")

    diagnostics = analyze_case(tmp_path)

    assert any(item.code == "ABACUS205" for item in diagnostics)


def test_duplicate_input_keyword_is_warning(tmp_path: Path) -> None:
    (tmp_path / "INPUT").write_text(
        "INPUT_PARAMETERS\necutwfc 50\necutwfc 100\n",
        encoding="utf-8",
    )
    (tmp_path / "STRU").write_text("ATOMIC_POSITIONS\nDirect\n", encoding="utf-8")
    (tmp_path / "KPT").write_text("K_POINTS\n0\nGamma\n1 1 1 0 0 0\n", encoding="utf-8")

    diagnostics = analyze_case(tmp_path)

    assert any(item.code == "ABACUS007" and item.severity == "warning" for item in diagnostics)


def test_safe_input_formatter_aligns_entries() -> None:
    formatted = format_input_text("INPUT_PARAMETERS\nsuffix MgO\necutwfc 100 # Ry\n")

    assert formatted == "INPUT_PARAMETERS\nsuffix   MgO\necutwfc  100  # Ry\n"

