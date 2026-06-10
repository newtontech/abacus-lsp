from __future__ import annotations

from pathlib import Path

from abacus_lsp.analyzer import analyze_case

FIXTURES = Path(__file__).parent / "fixtures"


def test_valid_fixture_has_no_errors() -> None:
    diagnostics = analyze_case(FIXTURES / "valid" / "mgo_lcao")

    assert [item for item in diagnostics if item.severity == "error"] == []


def test_kpt_count_mismatch_is_error() -> None:
    diagnostics = analyze_case(FIXTURES / "invalid" / "kpt_count")

    assert any(item.code == "ABACUS005" and item.severity == "error" for item in diagnostics)


def test_schema_type_and_enum_diagnostics(tmp_path: Path) -> None:
    (tmp_path / "INPUT").write_text(
        "INPUT_PARAMETERS\ncalculation invalid\ngamma_only maybe\necutwfc high\n",
        encoding="utf-8",
    )
    (tmp_path / "STRU").write_text("ATOMIC_POSITIONS\nDirect\n", encoding="utf-8")
    (tmp_path / "KPT").write_text("K_POINTS\n0\nGamma\n1 1 1 0 0 0\n", encoding="utf-8")

    diagnostics = analyze_case(tmp_path)

    assert sum(1 for item in diagnostics if item.code == "ABACUS101") == 3


def test_workflow_band_hint_requires_line_mode(tmp_path: Path) -> None:
    (tmp_path / "INPUT").write_text(
        "INPUT_PARAMETERS\ncalculation scf\nout_band 1\n",
        encoding="utf-8",
    )
    (tmp_path / "STRU").write_text("ATOMIC_POSITIONS\nDirect\n", encoding="utf-8")
    (tmp_path / "KPT").write_text("K_POINTS\n0\nGamma\n1 1 1 0 0 0\n", encoding="utf-8")

    diagnostics = analyze_case(tmp_path)

    assert any(item.code == "ABACUS305" for item in diagnostics)
