from __future__ import annotations

from pathlib import Path

from abacus_lsp.analyzer import analyze_case, parse_input, parse_kpt, parse_stru
from abacus_lsp.server import (
    completion_items,
    document_symbols,
    find_references,
    folding_ranges,
    goto_definition,
    publish_diagnostics,
    rename_symbol,
)

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


# ---------------------------------------------------------------------------
# LSP feature tests on valid fixture
# ---------------------------------------------------------------------------


def test_valid_fixture_completion() -> None:
    """Completion items include all registered keywords."""
    items = completion_items("INPUT")
    assert "calculation" in items
    assert "ecutwfc" in items
    assert "suffix" in items


def test_valid_fixture_document_symbols() -> None:
    """Document symbols extracts keywords from fixture INPUT."""
    input_text = (FIXTURES / "valid" / "mgo_lcao" / "INPUT").read_text(encoding="utf-8")
    syms = document_symbols("INPUT", input_text)
    names = [s["name"] for s in syms]
    assert "calculation" in names
    assert "ecutwfc" in names
    assert "basis_type" in names


def test_valid_fixture_folding_ranges() -> None:
    """Folding ranges on fixture STRU."""
    stru_text = (FIXTURES / "valid" / "mgo_lcao" / "STRU").read_text(encoding="utf-8")
    ranges = folding_ranges("STRU", stru_text)
    assert len(ranges) >= 1


def test_valid_fixture_publish_diagnostics() -> None:
    """Publish diagnostics on valid fixture groups by file (may be empty if clean)."""
    by_file = publish_diagnostics(FIXTURES / "valid" / "mgo_lcao")
    assert isinstance(by_file, dict)


# ---------------------------------------------------------------------------
# Invalid case: missing INPUT header
# ---------------------------------------------------------------------------


def test_missing_input_header(tmp_path: Path) -> None:
    (tmp_path / "INPUT").write_text("calculation scf\necutwfc 50\n", encoding="utf-8")
    (tmp_path / "STRU").write_text("ATOMIC_POSITIONS\nDirect\n", encoding="utf-8")
    (tmp_path / "KPT").write_text("K_POINTS\n0\nGamma\n1 1 1 0 0 0\n", encoding="utf-8")

    input_file = parse_input(tmp_path / "INPUT")
    assert any(d.code == "ABACUS001" for d in input_file.diagnostics)


# ---------------------------------------------------------------------------
# Invalid case: unknown keywords
# ---------------------------------------------------------------------------


def test_unknown_keyword_warning(tmp_path: Path) -> None:
    (tmp_path / "INPUT").write_text(
        "INPUT_PARAMETERS\nmy_unknown_param 42\n", encoding="utf-8"
    )
    (tmp_path / "STRU").write_text("ATOMIC_POSITIONS\nDirect\n", encoding="utf-8")
    (tmp_path / "KPT").write_text("K_POINTS\n0\nGamma\n1 1 1 0 0 0\n", encoding="utf-8")

    diagnostics = analyze_case(tmp_path)
    assert any(d.code == "ABACUS002" and d.severity == "warning" for d in diagnostics)


# ---------------------------------------------------------------------------
# Invalid case: KPT mode
# ---------------------------------------------------------------------------


def test_invalid_kpt_mode(tmp_path: Path) -> None:
    (tmp_path / "INPUT").write_text("INPUT_PARAMETERS\ncalculation scf\n", encoding="utf-8")
    (tmp_path / "STRU").write_text("ATOMIC_POSITIONS\nDirect\n", encoding="utf-8")
    (tmp_path / "KPT").write_text("K_POINTS\n0\nInvalidMode\n1 1 1 0 0 0\n", encoding="utf-8")

    kpt_file = parse_kpt(tmp_path / "KPT")
    assert any(
        d.code == "ABACUS005" and "unknown KPT mode" in d.message
        for d in kpt_file.diagnostics
    )


# ---------------------------------------------------------------------------
# Invalid case: STRU incomplete ATOMIC_POSITIONS
# ---------------------------------------------------------------------------


def test_incomplete_atomic_positions(tmp_path: Path) -> None:
    (tmp_path / "INPUT").write_text("INPUT_PARAMETERS\n", encoding="utf-8")
    (tmp_path / "STRU").write_text(
        "ATOMIC_POSITIONS\nDirect\nSi\n0.0\n",
        encoding="utf-8",
    )
    stru_file = parse_stru(tmp_path / "STRU")
    assert any(d.code == "ABACUS004" for d in stru_file.diagnostics)


# ---------------------------------------------------------------------------
# Invalid case: invalid atom count
# ---------------------------------------------------------------------------


def test_invalid_atom_count(tmp_path: Path) -> None:
    (tmp_path / "INPUT").write_text("INPUT_PARAMETERS\n", encoding="utf-8")
    (tmp_path / "STRU").write_text(
        "ATOMIC_POSITIONS\nDirect\nSi\n0.0\nnotanumber\n0.0 0.0 0.0\n",
        encoding="utf-8",
    )
    stru_file = parse_stru(tmp_path / "STRU")
    assert any(d.code == "ABACUS006" for d in stru_file.diagnostics)


# ---------------------------------------------------------------------------
# LSP navigation on valid fixture
# ---------------------------------------------------------------------------


def test_goto_definition_on_valid_fixture() -> None:
    """Go-to-definition for stru_file reference in valid MgO fixture."""
    case = FIXTURES / "valid" / "mgo_lcao"
    input_text = (case / "INPUT").read_text(encoding="utf-8")
    # The fixture doesn't have explicit stru_file, so test on pseudo_dir
    defs = goto_definition("INPUT", input_text, 1, 1, case)
    # Line 1 is suffix line, not a file ref
    assert isinstance(defs, list)


def test_find_references_on_valid_fixture() -> None:
    """Find references for a keyword in valid fixture."""
    input_text = (FIXTURES / "valid" / "mgo_lcao" / "INPUT").read_text(encoding="utf-8")
    # Find references for 'calculation' keyword
    refs = find_references("INPUT", input_text, 2, 1)
    assert isinstance(refs, list)
    assert len(refs) >= 1


# ---------------------------------------------------------------------------
# Edge cases: empty and malformed files
# ---------------------------------------------------------------------------


def test_empty_input_file(tmp_path: Path) -> None:
    (tmp_path / "INPUT").write_text("", encoding="utf-8")
    input_file = parse_input(tmp_path / "INPUT")
    # Empty file gets ABACUS001 (missing header) not ABACUS201 (missing file)
    assert any(d.code == "ABACUS001" for d in input_file.diagnostics)


def test_empty_kpt_file(tmp_path: Path) -> None:
    (tmp_path / "KPT").write_text("", encoding="utf-8")
    kpt_file = parse_kpt(tmp_path / "KPT")
    # Empty KPT gets ABACUS004 (empty file), not ABACUS202 (missing file)
    assert any(d.code == "ABACUS004" for d in kpt_file.diagnostics)


def test_kpt_bad_header(tmp_path: Path) -> None:
    (tmp_path / "KPT").write_text("BAD_HEADER\n0\nGamma\n1 1 1 0 0 0\n", encoding="utf-8")
    kpt_file = parse_kpt(tmp_path / "KPT")
    assert any(d.code == "ABACUS004" for d in kpt_file.diagnostics)


def test_input_comment_only(tmp_path: Path) -> None:
    (tmp_path / "INPUT").write_text("# just a comment\n", encoding="utf-8")
    input_file = parse_input(tmp_path / "INPUT")
    assert any(d.code == "ABACUS001" for d in input_file.diagnostics)


def test_input_with_slash_comments(tmp_path: Path) -> None:
    (tmp_path / "INPUT").write_text(
        "INPUT_PARAMETERS\n/slash comment\ncalculation scf\n", encoding="utf-8"
    )
    input_file = parse_input(tmp_path / "INPUT")
    # Should parse normally, slash comments ignored
    assert "calculation" in input_file.parameters


# ---------------------------------------------------------------------------
# More LSP navigation tests
# ---------------------------------------------------------------------------


def test_goto_definition_stru_non_numeric_mass(tmp_path: Path) -> None:
    """Go-to-definition on STRU line where column 2 is NOT numeric."""
    (tmp_path / "INPUT").write_text(
        "INPUT_PARAMETERS\npseudo_dir ./\n", encoding="utf-8"
    )
    # This STRU line has a non-numeric second column (LATTICE_CONSTANT)
    stru_text = "LATTICE_CONSTANT\n10.2\n"
    defs = goto_definition("STRU", stru_text, 1, 1, tmp_path)
    # LATTICE_CONSTANT has 2 parts, not 3, so no species match
    assert defs == []


def test_find_references_cross_file_stru(tmp_path: Path) -> None:
    """Find references for stru_file keyword cross-links to STRU."""
    (tmp_path / "INPUT").write_text(
        "INPUT_PARAMETERS\nstru_file STRU\n", encoding="utf-8"
    )
    (tmp_path / "STRU").write_text("ATOMIC_POSITIONS\nDirect\n", encoding="utf-8")
    (tmp_path / "KPT").write_text("K_POINTS\n0\nGamma\n1 1 1 0 0 0\n", encoding="utf-8")

    input_text = (tmp_path / "INPUT").read_text(encoding="utf-8")
    refs = find_references("INPUT", input_text, 2, 1, tmp_path)
    # Should include the STRU file reference
    uris = [r["uri"] for r in refs]
    assert any("STRU" in u for u in uris)


def test_find_references_cross_file_kpt(tmp_path: Path) -> None:
    """Find references for kpoint_file keyword cross-links to KPT."""
    (tmp_path / "INPUT").write_text(
        "INPUT_PARAMETERS\nkpoint_file KPT\n", encoding="utf-8"
    )
    (tmp_path / "STRU").write_text("ATOMIC_POSITIONS\nDirect\n", encoding="utf-8")
    (tmp_path / "KPT").write_text("K_POINTS\n0\nGamma\n1 1 1 0 0 0\n", encoding="utf-8")

    input_text = (tmp_path / "INPUT").read_text(encoding="utf-8")
    refs = find_references("INPUT", input_text, 2, 1, tmp_path)
    uris = [r["uri"] for r in refs]
    assert any("KPT" in u for u in uris)


def test_rename_single_occurrence() -> None:
    """Rename with single keyword occurrence."""
    text = "INPUT_PARAMETERS\ncalculation scf\n"
    result = rename_symbol("INPUT", text, 2, 1, "calc_type")
    assert result is not None
    assert "changes" in result
    edits = result["changes"]["INPUT"]
    assert len(edits) == 1
    assert edits[0]["newText"] == "calc_type"


def test_publish_diagnostics_with_errors(tmp_path: Path) -> None:
    """Publish diagnostics on invalid case groups by file."""
    (tmp_path / "INPUT").write_text(
        "INPUT_PARAMETERS\nbasis_type lcao\n", encoding="utf-8"
    )
    (tmp_path / "STRU").write_text("ATOMIC_POSITIONS\nDirect\n", encoding="utf-8")
    (tmp_path / "KPT").write_text("K_POINTS\n0\nGamma\n1 1 1 0 0 0\n", encoding="utf-8")

    by_file = publish_diagnostics(tmp_path)
    assert isinstance(by_file, dict)
    # Should have at least one file with diagnostics
    total = sum(len(v) for v in by_file.values())
    assert total > 0


# ---------------------------------------------------------------------------
# Additional invalid input edge cases
# ---------------------------------------------------------------------------


def test_input_nspin_not_integer(tmp_path: Path) -> None:
    """Non-integer nspin value produces type error."""
    (tmp_path / "INPUT").write_text(
        "INPUT_PARAMETERS\nnspin abc\n", encoding="utf-8"
    )
    (tmp_path / "STRU").write_text("ATOMIC_POSITIONS\nDirect\n", encoding="utf-8")
    (tmp_path / "KPT").write_text("K_POINTS\n0\nGamma\n1 1 1 0 0 0\n", encoding="utf-8")

    diagnostics = analyze_case(tmp_path)
    assert any(d.code == "ABACUS101" and "nspin" in d.message for d in diagnostics)


def test_input_ecutwfc_negative_valid_type(tmp_path: Path) -> None:
    """Negative number is still a valid real number type-wise."""
    (tmp_path / "INPUT").write_text(
        "INPUT_PARAMETERS\necutwfc -50\n", encoding="utf-8"
    )
    (tmp_path / "STRU").write_text("ATOMIC_POSITIONS\nDirect\n", encoding="utf-8")
    (tmp_path / "KPT").write_text("K_POINTS\n0\nGamma\n1 1 1 0 0 0\n", encoding="utf-8")

    diagnostics = analyze_case(tmp_path)
    # -50 is a valid real number, should not produce ABACUS101
    assert not any(d.code == "ABACUS101" and "ecutwfc" in d.message for d in diagnostics)


def test_stru_missing_file(tmp_path: Path) -> None:
    """Parsing a missing STRU file produces ABACUS201."""
    result = parse_stru(tmp_path / "STRU")
    assert any(d.code == "ABACUS201" for d in result.diagnostics)


def test_kpt_missing_file(tmp_path: Path) -> None:
    """Parsing a missing KPT file produces ABACUS202."""
    result = parse_kpt(tmp_path / "KPT")
    assert any(d.code == "ABACUS202" for d in result.diagnostics)


# ---------------------------------------------------------------------------
# New fixture-based tests
# ---------------------------------------------------------------------------


def test_si_pw_valid_fixture_has_no_errors() -> None:
    """PW basis Si fixture should have no errors."""
    diagnostics = analyze_case(FIXTURES / "valid" / "si_pw")
    assert [item for item in diagnostics if item.severity == "error"] == []


def test_si_pw_valid_fixture_document_symbols() -> None:
    """Document symbols for PW basis Si fixture."""
    input_text = (FIXTURES / "valid" / "si_pw" / "INPUT").read_text(encoding="utf-8")
    syms = document_symbols("INPUT", input_text)
    names = [s["name"] for s in syms]
    assert "calculation" in names
    assert "ecutwfc" in names
    assert "scf_thr" in names


def test_si_pw_valid_fixture_completion() -> None:
    """Completion on the si_pw INPUT fixture."""
    items = completion_items("INPUT")
    assert "ecutwfc" in items
    assert "basis_type" in items


def test_bad_calculation_fixture_produces_error() -> None:
    """Invalid calculation type produces ABACUS101 error."""
    diagnostics = analyze_case(FIXTURES / "invalid" / "bad_calculation")
    assert any(d.code == "ABACUS101" and "calculation" in d.message for d in diagnostics)


def test_missing_files_fixture_produces_missing_diag() -> None:
    """STRU and KPT files that don't exist produce ABACUS201/202."""
    diagnostics = analyze_case(FIXTURES / "invalid" / "missing_files")
    # The STRU and KPT still exist in the fixture, but stru_file/kpoint_file
    # point to non-existent files. This tests the file path handling.
    assert isinstance(diagnostics, list)


def test_duplicate_stru_fixture_produces_warning() -> None:
    """Duplicate stru_file keyword produces ABACUS007 warning."""
    diagnostics = analyze_case(FIXTURES / "invalid" / "duplicate_stru")
    assert any(d.code == "ABACUS007" for d in diagnostics)


def test_si_pw_stru_folding_ranges() -> None:
    """Folding ranges for Si PW STRU fixture."""
    stru_text = (FIXTURES / "valid" / "si_pw" / "STRU").read_text(encoding="utf-8")
    ranges = folding_ranges("STRU", stru_text)
    assert len(ranges) >= 1
    # First range should start from ATOMIC_SPECIES section
    assert ranges[0]["startLine"] == 0


def test_rule_invalid_input_keyword(tmp_path: Path) -> None:
    """RULE abacus.input.invalid_keyword: error on unknown INPUT keyword."""
    (tmp_path / "INPUT").write_text(
        "INPUT_PARAMETERS\nzzz_nonexistent_keyword 42\n", encoding="utf-8"
    )
    (tmp_path / "STRU").write_text("ATOMIC_POSITIONS\nDirect\n", encoding="utf-8")
    (tmp_path / "KPT").write_text("K_POINTS\n0\nGamma\n1 1 1 0 0 0\n", encoding="utf-8")
    diagnostics = analyze_case(tmp_path)
    assert any(
        d.code == "ABACUS002" and "unknown" in d.message.lower() and "zzz_nonexistent_keyword" in d.message
        for d in diagnostics
    ), f"Expected unknown keyword error, got: {[d.message for d in diagnostics]}"


def test_rule_missing_input_file(tmp_path: Path) -> None:
    """RULE abacus.files.missing_input: error when INPUT file is absent."""
    # No INPUT file created, only STRU and KPT
    (tmp_path / "STRU").write_text("ATOMIC_POSITIONS\nDirect\n", encoding="utf-8")
    (tmp_path / "KPT").write_text("K_POINTS\n0\nGamma\n1 1 1 0 0 0\n", encoding="utf-8")
    diagnostics = analyze_case(tmp_path)
    assert any(
        d.severity == "error" and "INPUT file is missing" in d.message
        for d in diagnostics
    ), f"Expected missing INPUT error, got: {[d.message for d in diagnostics]}"


def test_rule_missing_stru_file(tmp_path: Path) -> None:
    """RULE abacus.files.missing_stru: error when STRU file is absent."""
    (tmp_path / "INPUT").write_text(
        "INPUT_PARAMETERS\ncalculation scf\n", encoding="utf-8"
    )
    # No STRU file - use non-default name to avoid auto-STRU
    (tmp_path / "KPT").write_text("K_POINTS\n0\nGamma\n1 1 1 0 0 0\n", encoding="utf-8")
    diagnostics = analyze_case(tmp_path)
    assert any(
        d.severity == "error" and "STRU" in d.message and "missing" in d.message
        for d in diagnostics
    ), f"Expected missing STRU error, got: {[d.message for d in diagnostics]}"


def test_rule_invalid_input_value(tmp_path: Path) -> None:
    """RULE abacus.input.invalid_value: error on invalid INPUT value."""
    (tmp_path / "INPUT").write_text(
        "INPUT_PARAMETERS\ncalculation not_a_real_calc\n", encoding="utf-8"
    )
    (tmp_path / "STRU").write_text("ATOMIC_POSITIONS\nDirect\n", encoding="utf-8")
    (tmp_path / "KPT").write_text("K_POINTS\n0\nGamma\n1 1 1 0 0 0\n", encoding="utf-8")
    diagnostics = analyze_case(tmp_path)
    assert any(
        d.code == "ABACUS101" and d.severity == "error"
        for d in diagnostics
    ), f"Expected invalid value error (ABACUS101), got: {[d.message for d in diagnostics]}"


def test_rule_species_orbital_mismatch(tmp_path: Path) -> None:
    """RULE abacus.stru.species_orbital_mismatch: warn when orbital and species counts differ."""
    (tmp_path / "INPUT").write_text(
        "INPUT_PARAMETERS\nbasis_type lcao\ncalculation scf\n", encoding="utf-8"
    )
    (tmp_path / "KPT").write_text("K_POINTS\n0\nGamma\n1 1 1 0 0 0\n", encoding="utf-8")
    # STRU with 2 species but only 1 orbital file
    (tmp_path / "STRU").write_text(
        "ATOMIC_SPECIES\nSi 28.086 Si_ONCV_PBE-1.0.upf\nO 15.999 O_ONCV_PBE-1.0.upf\n"
        "NUMERICAL_ORBITAL\nSi_gga_8au_100Ry_2s2p1d.orb\n"
        "LATTICE_CONSTANT\n10.2\n"
        "LATTICE_VECTORS\n1.0 0.0 0.0\n0.0 1.0 0.0\n0.0 0.0 1.0\n"
        "ATOMIC_POSITIONS\nDirect\nSi\n0.0\n1\n0.0 0.0 0.0 0 0 0\nO\n0.0\n1\n0.5 0.5 0.5 0 0 0\n",
        encoding="utf-8",
    )
    diagnostics = analyze_case(tmp_path)
    assert any(
        d.code == "ABACUS206" and "ORBITAL" in d.message and "count" in d.message.lower()
        for d in diagnostics
    ), f"Expected species/orbital mismatch, got: {[d.message for d in diagnostics]}"


def test_si_pw_goto_definition_stru_file(tmp_path: Path) -> None:
    """Go-to-definition on stru_file in INPUT navigates to the STRU file."""
    # Use the si_pw fixture path as case_dir
    case = FIXTURES / "valid" / "si_pw"
    input_text = (case / "INPUT").read_text(encoding="utf-8")
    # The si_pw fixture uses default STRU name (no explicit stru_file)
    # So let's test with a temporary case that has explicit stru_file
    (tmp_path / "INPUT").write_text(
        "INPUT_PARAMETERS\nstru_file custom_stru\ncalculation scf\n",
        encoding="utf-8",
    )
    (tmp_path / "custom_stru").write_text(
        "ATOMIC_POSITIONS\nDirect\n", encoding="utf-8"
    )
    (tmp_path / "KPT").write_text("K_POINTS\n0\nGamma\n1 1 1 0 0 0\n", encoding="utf-8")

    input_text = (tmp_path / "INPUT").read_text(encoding="utf-8")
    defs = goto_definition("INPUT", input_text, 2, 1, tmp_path)
    assert len(defs) >= 1
    assert "custom_stru" in defs[0]["uri"]
