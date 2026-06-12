"""Tests for Capability #39 – Completion.

Covers:
- completion_items: keyword suggestions per file type
- completion_values: enum/boolean value suggestions
- completion_file_hints: file-aware path suggestions
"""

from __future__ import annotations

from pathlib import Path

from abacus_lsp.server import completion_file_hints, completion_items, completion_values

# ---------------------------------------------------------------------------
# completion_items
# ---------------------------------------------------------------------------


def test_completion_includes_all_schema_keywords() -> None:
    """All registered schema keywords appear in INPUT completions."""
    items = completion_items("INPUT")
    # Core keywords from the builtin schema
    assert "calculation" in items
    assert "ecutwfc" in items
    assert "basis_type" in items
    assert "scf_thr" in items
    assert "nspin" in items
    assert "suffix" in items
    assert "pseudo_dir" in items
    assert "orbital_dir" in items
    assert "stru_file" in items
    assert "kpoint_file" in items
    assert "gamma_only" in items
    assert "latname" in items
    assert "out_band" in items
    assert "out_dos" in items
    assert "dft_plus_u" in items


def test_completion_input_case_insensitive() -> None:
    """Filename matching is case-insensitive."""
    assert completion_items("input") == completion_items("INPUT")


def test_completion_stru_sections() -> None:
    """STRU completion returns known section names."""
    items = completion_items("STRU")
    assert "ATOMIC_SPECIES" in items
    assert "NUMERICAL_ORBITAL" in items
    assert "LATTICE_CONSTANT" in items
    assert "LATTICE_VECTORS" in items
    assert "LATTICE_PARAMETERS" in items
    assert "ATOMIC_POSITIONS" in items


def test_completion_kpt_modes() -> None:
    """KPT completion returns known K-point modes."""
    items = completion_items("KPT")
    assert "Gamma" in items
    assert "MP" in items
    assert "Direct" in items
    assert "Cartesian" in items
    assert "Line" in items
    assert "Line_Cartesian" in items


def test_completion_unknown_file_empty() -> None:
    """Unknown file types return empty completion list."""
    assert completion_items("random.txt") == []


# ---------------------------------------------------------------------------
# completion_values
# ---------------------------------------------------------------------------


def test_completion_values_calculation_enum() -> None:
    """calculation keyword returns all enum values."""
    values = completion_values("calculation")
    assert "scf" in values
    assert "nscf" in values
    assert "relax" in values
    assert "md" in values
    assert "cell-relax" in values
    assert "get_wf" in values
    assert "get_pchg" in values


def test_completion_values_basis_type_enum() -> None:
    """basis_type keyword returns pw and lcao."""
    values = completion_values("basis_type")
    assert values == ["pw", "lcao"]


def test_completion_values_nspin_enum() -> None:
    """nspin keyword returns stringified integer enum values."""
    values = completion_values("nspin")
    assert "1" in values
    assert "2" in values
    assert "4" in values


def test_completion_values_boolean() -> None:
    """Boolean keywords return common boolean representations."""
    values = completion_values("gamma_only")
    assert "0" in values
    assert "1" in values
    assert "true" in values
    assert "false" in values


def test_completion_values_boolean_out_band() -> None:
    """out_band is a Boolean keyword."""
    values = completion_values("out_band")
    assert "0" in values
    assert "1" in values


def test_completion_values_real_type_empty() -> None:
    """Real-type keywords have no canned value suggestions."""
    assert completion_values("ecutwfc") == []


def test_completion_values_path_type_empty() -> None:
    """Path-type keywords have no canned value suggestions."""
    assert completion_values("stru_file") == []


def test_completion_values_unknown_keyword_empty() -> None:
    """Unknown keywords return empty list."""
    assert completion_values("nonexistent_keyword") == []


def test_completion_values_case_insensitive() -> None:
    """Keyword lookup is case-insensitive."""
    assert completion_values("Calculation") == completion_values("calculation")
    assert completion_values("ECUTWFC") == completion_values("ecutwfc")


# ---------------------------------------------------------------------------
# completion_file_hints
# ---------------------------------------------------------------------------


def test_file_hints_stru_file(tmp_path: Path) -> None:
    """stru_file hints suggest existing STRU files in case directory."""
    (tmp_path / "STRU").write_text("ATOMIC_POSITIONS\nDirect\n", encoding="utf-8")
    (tmp_path / "my_structure.stru").write_text("content", encoding="utf-8")
    (tmp_path / "unrelated.txt").write_text("content", encoding="utf-8")

    hints = completion_file_hints("stru_file", tmp_path)
    assert "STRU" in hints
    assert "my_structure.stru" in hints
    assert "unrelated.txt" not in hints


def test_file_hints_kpoint_file(tmp_path: Path) -> None:
    """kpoint_file hints suggest existing KPT files in case directory."""
    (tmp_path / "KPT").write_text("K_POINTS\n0\nGamma\n1 1 1 0 0 0\n", encoding="utf-8")
    (tmp_path / "my_kpts.kpt").write_text("content", encoding="utf-8")
    (tmp_path / "unrelated.txt").write_text("content", encoding="utf-8")

    hints = completion_file_hints("kpoint_file", tmp_path)
    assert "KPT" in hints
    assert "my_kpts.kpt" in hints
    assert "unrelated.txt" not in hints


def test_file_hints_directory_keywords(tmp_path: Path) -> None:
    """Directory keywords (pseudo_dir, orbital_dir) suggest subdirectories."""
    (tmp_path / "pseudo").mkdir()
    (tmp_path / "orbitals").mkdir()
    (tmp_path / "some_file.txt").write_text("content", encoding="utf-8")

    hints = completion_file_hints("pseudo_dir", tmp_path)
    assert "pseudo/" in hints
    assert "orbitals/" in hints
    assert "some_file.txt" not in hints

    hints_orbital = completion_file_hints("orbital_dir", tmp_path)
    assert "pseudo/" in hints_orbital


def test_file_hints_read_file_dir(tmp_path: Path) -> None:
    """read_file_dir also suggests subdirectories."""
    (tmp_path / "data").mkdir()
    hints = completion_file_hints("read_file_dir", tmp_path)
    assert "data/" in hints


def test_file_hints_non_path_keyword_empty(tmp_path: Path) -> None:
    """Non-path keywords return empty hints."""
    assert completion_file_hints("calculation", tmp_path) == []
    assert completion_file_hints("ecutwfc", tmp_path) == []


def test_file_hints_nonexistent_dir_empty() -> None:
    """Non-existent directory returns empty hints."""
    hints = completion_file_hints("stru_file", Path("/nonexistent/path"))
    assert hints == []


def test_file_hints_empty_dir(tmp_path: Path) -> None:
    """Empty directory returns no stru_file hints."""
    hints = completion_file_hints("stru_file", tmp_path)
    assert hints == []


def test_file_hints_case_insensitive_keyword(tmp_path: Path) -> None:
    """Keyword lookup is case-insensitive."""
    (tmp_path / "STRU").write_text("content", encoding="utf-8")
    assert completion_file_hints("STRU_FILE", tmp_path) == completion_file_hints(
        "stru_file", tmp_path
    )


# ---------------------------------------------------------------------------
# Capability contract fixture existence
# ---------------------------------------------------------------------------


def test_capability_fixture_exists() -> None:
    """The completion capability contract fixture exists."""
    fixture = Path(__file__).parent / "fixtures" / "capabilities" / "completion.json"
    assert fixture.exists(), f"Capability fixture missing: {fixture}"


def test_capability_fixture_valid_json() -> None:
    """The completion capability contract fixture is valid JSON with required fields."""
    import json

    fixture = Path(__file__).parent / "fixtures" / "capabilities" / "completion.json"
    data = json.loads(fixture.read_text(encoding="utf-8"))
    assert data["capability_id"] == "completion"
    assert "INPUT" in data["file_types"]
    assert data["provides_keywords"] is True
    assert data["provides_values"] is True
    assert data["provides_file_hints"] is True
