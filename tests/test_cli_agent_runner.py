from __future__ import annotations

import json
from pathlib import Path

from abacus_lsp.agent import apply_fix, export_context, query_diagnostics
from abacus_lsp.cli import _parse_tolerance, agent_main, schema_main
from abacus_lsp.cli import test_main as cli_test_main
from abacus_lsp.server import (
    code_actions,
    completion_items,
    document_symbols,
    find_references,
    folding_ranges,
    goto_definition,
    hover_text,
    publish_diagnostics,
    rename_symbol,
)
from abacus_lsp.test_runner import run_regression, run_smoke

FIXTURES = Path(__file__).parent / "fixtures"


def test_schema_cli_builds_json(tmp_path: Path) -> None:
    out = tmp_path / "schema.json"

    assert schema_main(["build", "--out", str(out), "--version", "test"]) == 0

    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["abacus_version"] == "test"
    assert any(item["name"] == "calculation" for item in payload["keywords"])


def test_agent_query_and_export_context(tmp_path: Path) -> None:
    case = FIXTURES / "valid" / "mgo_lcao"

    result = query_diagnostics(case)
    context = export_context(case, tmp_path / ".abacus-lsp")

    assert result["ok"] is True
    assert context["ok"] is True
    assert (tmp_path / ".abacus-lsp" / "diagnostics.json").exists()


def test_agent_apply_fix_for_lcao_missing_orbitals(tmp_path: Path) -> None:
    (tmp_path / "INPUT").write_text("INPUT_PARAMETERS\nbasis_type lcao\n", encoding="utf-8")
    (tmp_path / "STRU").write_text("ATOMIC_POSITIONS\nDirect\n", encoding="utf-8")
    (tmp_path / "KPT").write_text("K_POINTS\n0\nGamma\n1 1 1 0 0 0\n", encoding="utf-8")

    result = apply_fix(tmp_path, "ABACUS205")

    assert result["ok"] is True
    assert "NUMERICAL_ORBITAL" in (tmp_path / "STRU").read_text(encoding="utf-8")


def test_agent_cli_returns_nonzero_for_blocking_errors(tmp_path: Path, capsys) -> None:
    (tmp_path / "INPUT").write_text("INPUT_PARAMETERS\nbasis_type lcao\n", encoding="utf-8")
    (tmp_path / "STRU").write_text("ATOMIC_POSITIONS\nDirect\n", encoding="utf-8")
    (tmp_path / "KPT").write_text("K_POINTS\n0\nGamma\n1 1 1 0 0 0\n", encoding="utf-8")

    code = agent_main(["query-diagnostics", str(tmp_path)])

    assert code == 1
    assert "ABACUS205" in capsys.readouterr().out


def test_static_test_cli_and_missing_smoke_backend(capsys) -> None:
    assert cli_test_main(["static", str(FIXTURES / "valid" / "mgo_lcao"), "--json"]) == 0
    assert (
        cli_test_main(["smoke", str(FIXTURES / "valid" / "mgo_lcao"), "--backend", "pyabacus"]) == 1
    )
    assert "pyabacus backend is not installed" in capsys.readouterr().out


def test_regression_runner_compares_tolerances(tmp_path: Path) -> None:
    (tmp_path / "result.json").write_text('{"energy": 1.01}', encoding="utf-8")
    expect = tmp_path / "expected.json"
    expect.write_text('{"energy": 1.0}', encoding="utf-8")

    assert run_regression(tmp_path, expect, {"energy": 0.02})["ok"] is True
    assert run_regression(tmp_path, expect, {"energy": 0.001})["ok"] is False
    assert _parse_tolerance("energy=0.1,force=0.2") == {"energy": 0.1, "force": 0.2}


def test_server_helper_surfaces_language_features() -> None:
    text = "INPUT_PARAMETERS\ncalculation scf\n"

    assert "calculation" in completion_items("INPUT")
    assert hover_text("ecutwfc") and "Ry" in hover_text("ecutwfc")
    assert document_symbols("INPUT", text)[0]["name"] == "calculation"
    assert isinstance(code_actions(FIXTURES / "valid" / "mgo_lcao"), list)


def test_run_smoke_unknown_backend() -> None:
    result = run_smoke(FIXTURES / "valid" / "mgo_lcao", backend="unknown")

    assert result["ok"] is False
    assert "unknown smoke backend" in result["reason"]


def test_server_completion_covers_all_file_types() -> None:
    """Verify completion items are returned for INPUT, STRU, and KPT."""
    assert "calculation" in completion_items("INPUT")
    assert "ecutwfc" in completion_items("INPUT")
    assert "ATOMIC_SPECIES" in completion_items("STRU")
    assert "LATTICE_VECTORS" in completion_items("STRU")
    assert "Gamma" in completion_items("KPT")
    assert "MP" in completion_items("KPT")
    assert "Line" in completion_items("KPT")
    # Unknown file type returns empty
    assert completion_items("unknown.txt") == []


def test_hover_text_covers_keywords() -> None:
    """Hover returns documentation for known keywords and None for unknown."""
    text = hover_text("ecutwfc")
    assert text is not None
    assert "Ry" in text
    assert "Real" in text

    text = hover_text("calculation")
    assert text is not None
    assert "Enum" in text

    # Boolean keyword
    text = hover_text("gamma_only")
    assert text is not None
    assert "Boolean" in text

    # Unknown keyword returns None
    assert hover_text("not_a_keyword") is None


def test_document_symbols_input_and_stru() -> None:
    """Document symbols extracts parameters and sections."""
    input_text = "INPUT_PARAMETERS\ncalculation scf\necutwfc 100\n"
    syms = document_symbols("INPUT", input_text)
    names = [s["name"] for s in syms]
    assert "calculation" in names
    assert "ecutwfc" in names

    stru_text = "ATOMIC_SPECIES\nSi 28 Si.upf\n\nLATTICE_VECTORS\n1 0 0\n"
    syms = document_symbols("STRU", stru_text)
    names = [s["name"] for s in syms]
    assert "ATOMIC_SPECIES" in names
    assert "LATTICE_VECTORS" in names


def test_folding_ranges_stru() -> None:
    """Folding ranges for STRU sections."""
    stru_text = "ATOMIC_SPECIES\nSi 28 Si.upf\n\nLATTICE_VECTORS\n1 0 0\n0 1 0\n0 0 1\n"
    ranges = folding_ranges("STRU", stru_text)
    assert len(ranges) >= 1
    assert ranges[0]["startLine"] == 0


def test_code_actions_for_valid_fixture() -> None:
    """Code actions are a list (even if empty for valid case)."""
    actions = code_actions(FIXTURES / "valid" / "mgo_lcao")
    assert isinstance(actions, list)


def test_goto_definition_input_file_refs(tmp_path: Path) -> None:
    """Go-to-definition on stru_file and kpoint_file in INPUT."""
    (tmp_path / "INPUT").write_text(
        "INPUT_PARAMETERS\nstru_file STRU\nkpoint_file KPT\n", encoding="utf-8"
    )
    (tmp_path / "STRU").write_text("ATOMIC_POSITIONS\nDirect\n", encoding="utf-8")
    (tmp_path / "KPT").write_text("K_POINTS\n0\nGamma\n1 1 1 0 0 0\n", encoding="utf-8")

    input_text = (tmp_path / "INPUT").read_text(encoding="utf-8")

    # Go to definition on stru_file line
    defs = goto_definition("INPUT", input_text, 2, 1, tmp_path)
    assert len(defs) >= 1
    assert "STRU" in defs[0]["uri"]

    # Go to definition on kpoint_file line
    defs = goto_definition("INPUT", input_text, 3, 1, tmp_path)
    assert len(defs) >= 1
    assert "KPT" in defs[0]["uri"]


def test_goto_definition_stru_pseudo(tmp_path: Path) -> None:
    """Go-to-definition on pseudopotential filename in STRU."""
    (tmp_path / "INPUT").write_text("INPUT_PARAMETERS\npseudo_dir ./\n", encoding="utf-8")
    (tmp_path / "STRU").write_text(
        "ATOMIC_SPECIES\nSi 28.085 Si.upf\n\nATOMIC_POSITIONS\nDirect\n",
        encoding="utf-8",
    )
    (tmp_path / "Si.upf").write_text("pseudo\n", encoding="utf-8")

    stru_text = (tmp_path / "STRU").read_text(encoding="utf-8")
    defs = goto_definition("STRU", stru_text, 2, 1, tmp_path)
    assert len(defs) >= 1
    assert "Si.upf" in defs[0]["uri"]


def test_find_references_input_keyword(tmp_path: Path) -> None:
    """Find all references for a repeated keyword."""
    (tmp_path / "INPUT").write_text("INPUT_PARAMETERS\necutwfc 50\necutwfc 100\n", encoding="utf-8")
    input_text = (tmp_path / "INPUT").read_text(encoding="utf-8")
    refs = find_references("INPUT", input_text, 2, 1, tmp_path)
    assert len(refs) == 2
    lines = [r["line"] for r in refs]
    assert 2 in lines
    assert 3 in lines


def test_rename_input_keyword() -> None:
    """Rename produces workspace edits for all occurrences."""
    text = "INPUT_PARAMETERS\necutwfc 50\necutwfc 100\n"
    result = rename_symbol("INPUT", text, 2, 1, "ecutwfc_new")
    assert result is not None
    assert "changes" in result
    assert "INPUT" in result["changes"]
    edits = result["changes"]["INPUT"]
    assert len(edits) == 2
    assert all(e["newText"] == "ecutwfc_new" for e in edits)


def test_rename_returns_none_for_unsupported() -> None:
    """Rename returns None for unsupported files/positions."""
    result = rename_symbol("STRU", "ATOMIC_SPECIES\nSi 28 Si.upf\n", 1, 1, "new")
    assert result is None
    # Comment line
    result = rename_symbol("INPUT", "INPUT_PARAMETERS\n# comment\n", 2, 1, "new")
    assert result is None
    # Out of bounds
    result = rename_symbol("INPUT", "INPUT_PARAMETERS\necutwfc 50\n", 10, 1, "new")
    assert result is None


def test_publish_diagnostics(tmp_path: Path) -> None:
    """Publish diagnostics groups by file."""
    (tmp_path / "INPUT").write_text("INPUT_PARAMETERS\nbasis_type lcao\n", encoding="utf-8")
    (tmp_path / "STRU").write_text("ATOMIC_POSITIONS\nDirect\n", encoding="utf-8")
    (tmp_path / "KPT").write_text("K_POINTS\n0\nGamma\n1 1 1 0 0 0\n", encoding="utf-8")

    result = publish_diagnostics(tmp_path)
    assert isinstance(result, dict)
    # Should have diagnostics grouped by file path
    all_diags = []
    for file_diags in result.values():
        all_diags.extend(file_diags)
    assert len(all_diags) > 0


def test_goto_definition_out_of_bounds() -> None:
    """Go-to-definition with invalid line numbers returns empty."""
    text = "INPUT_PARAMETERS\necutwfc 50\n"
    assert goto_definition("INPUT", text, 0, 1) == []
    assert goto_definition("INPUT", text, 10, 1) == []
    # Comment line
    assert goto_definition("INPUT", "# comment\necutwfc 50\n", 1, 1) == []


def test_find_references_stru_section() -> None:
    """Find references for STRU section names."""
    text = "ATOMIC_SPECIES\nSi 28 Si.upf\n\nATOMIC_SPECIES\nO 16 O.upf\n"
    refs = find_references("STRU", text, 1, 1)
    assert len(refs) == 2


def test_find_references_out_of_bounds() -> None:
    """Find references with invalid positions returns empty."""
    text = "INPUT_PARAMETERS\necutwfc 50\n"
    assert find_references("INPUT", text, 0, 1) == []
    assert find_references("INPUT", text, 10, 1) == []
    assert find_references("INPUT", "# comment\necutwfc 50\n", 1, 1) == []


def test_goto_definition_no_case_dir_file_ref() -> None:
    """Go-to-definition on file-ref keywords without case_dir returns symbolic ref."""
    text = "INPUT_PARAMETERS\nstru_file my_stru\nkpoint_file my_kpt\n"
    defs = goto_definition("INPUT", text, 2, 1)
    assert len(defs) == 1
    assert defs[0]["uri"] == "my_stru"
    defs = goto_definition("INPUT", text, 3, 1)
    assert len(defs) == 1
    assert defs[0]["uri"] == "my_kpt"


def test_goto_definition_non_file_key() -> None:
    """Go-to-definition on a non-file keyword returns empty."""
    text = "INPUT_PARAMETERS\necutwfc 50\n"
    assert goto_definition("INPUT", text, 2, 1) == []


def test_goto_definition_stru_non_species_line(tmp_path: Path) -> None:
    """Go-to-definition on a non-species STRU line returns empty."""
    (tmp_path / "INPUT").write_text("INPUT_PARAMETERS\npseudo_dir ./\n", encoding="utf-8")
    stru_text = "ATOMIC_SPECIES\n# comment\n"
    defs = goto_definition("STRU", stru_text, 2, 1, tmp_path)
    assert defs == []


def test_find_references_input_header_line() -> None:
    """Find references on INPUT_PARAMETERS line treats it as a keyword."""
    text = "INPUT_PARAMETERS\necutwfc 50\n"
    refs = find_references("INPUT", text, 1, 1)
    # INPUT_PARAMETERS line is not a keyword, so treated as a comment-like header
    # It should still try to find refs for "input_parameters"
    assert isinstance(refs, list)


def test_rename_empty_line() -> None:
    """Rename on empty line returns None."""
    result = rename_symbol("INPUT", "INPUT_PARAMETERS\n   \necutwfc 50\n", 2, 1, "new")
    assert result is None


def test_goto_definition_stru_out_of_bounds() -> None:
    """Go-to-definition for STRU with invalid positions."""
    assert goto_definition("STRU", "ATOMIC_SPECIES\nSi 28 Si.upf\n", 0, 1) == []
    assert goto_definition("STRU", "ATOMIC_SPECIES\nSi 28 Si.upf\n", 10, 1) == []


def test_publish_diagnostics_valid_case() -> None:
    """Valid fixture should have diagnostics but no errors."""
    result = publish_diagnostics(FIXTURES / "valid" / "mgo_lcao")
    all_diags = []
    for file_diags in result.values():
        all_diags.extend(file_diags)
    # No errors
    assert all(d["severity"] != "error" for d in all_diags)


def test_hover_text_with_and_without_unit() -> None:
    """Hover text includes unit when present."""
    # Keyword with unit
    text = hover_text("ecutwfc")
    assert text is not None
    assert "(Ry)" in text
    # Keyword without unit
    text = hover_text("scf_thr")
    assert text is not None
    assert "(Ry)" not in text
    # Keyword with default
    text = hover_text("calculation")
    assert text is not None
    assert "Default: scf" in text


def test_uri_to_filename() -> None:
    """Test URI-to-filename conversion."""
    from abacus_lsp.server import _uri_to_filename

    # file:// URI
    assert _uri_to_filename("file:///home/user/project/INPUT") == "INPUT"
    assert _uri_to_filename("file:///home/user/project/STRU") == "STRU"
    # Plain path
    assert _uri_to_filename("INPUT") == "INPUT"
    # URI with encoded chars
    assert _uri_to_filename("file:///path%20with%20spaces/INPUT") == "INPUT"


def test_register_features_with_pygls() -> None:
    """Test that _register_features registers handlers without error."""
    from abacus_lsp.server import _register_features

    # Create a mock-like server object with a feature decorator
    class FakeServer:
        def __init__(self):
            self._features = {}

        def feature(self, *args, **kwargs):
            def decorator(func):
                self._features[func.__name__] = func
                return func

            return decorator

    fake = FakeServer()
    _register_features(fake)
    # Check that feature handlers were registered
    assert "completions" in fake._features
    assert "hover" in fake._features
    assert "symbols" in fake._features
    assert "folding" in fake._features
    assert "formatting" in fake._features


def test_register_features_no_lsprotocol(monkeypatch) -> None:
    """_register_features handles missing lsprotocol gracefully."""
    from abacus_lsp.server import _register_features

    class FakeServer:
        def feature(self, *args, **kwargs):
            return lambda func: func

    # Simulate lsprotocol not available by patching the import
    import builtins

    real_import = builtins.__import__

    def mock_import(name, *args, **kwargs):
        if name == "lsprotocol" or name.startswith("lsprotocol"):
            raise ImportError("no lsprotocol")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", mock_import)

    fake = FakeServer()
    # Should return without error
    _register_features(fake)
