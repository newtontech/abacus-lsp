from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from abacus_lsp.agent import apply_fix, explain_diagnostic
from abacus_lsp.analyzer import analyze_case, parse_input, parse_kpt, parse_stru
from abacus_lsp.cli import fmt_main, lint_main, lsp_main
from abacus_lsp.formatter import FormatOptions, format_file_text
from abacus_lsp.schema import SchemaRegistry, build_schema
from abacus_lsp.server import folding_ranges, format_document
from abacus_lsp.test_runner import run_regression, run_smoke


def test_missing_and_malformed_files_cover_error_paths(tmp_path: Path) -> None:
    assert parse_input(tmp_path / "INPUT").diagnostics[0].code == "ABACUS201"
    assert parse_stru(tmp_path / "STRU").diagnostics[0].code == "ABACUS201"
    assert parse_kpt(tmp_path / "KPT").diagnostics[0].code == "ABACUS202"

    (tmp_path / "INPUT").write_text("no header\n", encoding="utf-8")
    (tmp_path / "KPT").write_text("BAD\nx\nNope\n", encoding="utf-8")
    diagnostics = [
        item.code
        for item in [
            *parse_input(tmp_path / "INPUT").diagnostics,
            *parse_kpt(tmp_path / "KPT").diagnostics,
        ]
    ]

    assert "ABACUS001" in diagnostics
    assert "ABACUS004" in diagnostics
    assert "ABACUS005" in diagnostics


def test_stru_atom_count_and_order_diagnostics(tmp_path: Path) -> None:
    (tmp_path / "INPUT").write_text(
        "INPUT_PARAMETERS\nbasis_type lcao\npseudo_dir ./\norbital_dir ./\n",
        encoding="utf-8",
    )
    (tmp_path / "STRU").write_text(
        """ATOMIC_SPECIES
O 15.999 missing.upf
Si 28.085 Si.upf

NUMERICAL_ORBITAL
Si.orb

ATOMIC_POSITIONS
Direct
Si
0.0
2
0.0 0.0 0.0
""",
        encoding="utf-8",
    )
    (tmp_path / "KPT").write_text("K_POINTS\n0\nGamma\n1 1 1 0 0 0\n", encoding="utf-8")

    codes = {item.code for item in analyze_case(tmp_path)}

    assert {"ABACUS006", "ABACUS204", "ABACUS207"} <= codes

    second = tmp_path / "orbital-count"
    second.mkdir()
    (second / "INPUT").write_text(
        "INPUT_PARAMETERS\nbasis_type lcao\norbital_dir ./\n",
        encoding="utf-8",
    )
    (second / "STRU").write_text(
        """ATOMIC_SPECIES
Si 28.085 Si.upf
O 15.999 O.upf

NUMERICAL_ORBITAL
Si.orb

ATOMIC_POSITIONS
Direct
Si
0.0
1
0.0 0.0 0.0
O
0.0
1
0.5 0.5 0.5
""",
        encoding="utf-8",
    )
    (second / "KPT").write_text("K_POINTS\n0\nGamma\n1 1 1 0 0 0\n", encoding="utf-8")

    assert any(item.code == "ABACUS206" for item in analyze_case(second))


def test_workflow_rules_for_dft_u_md_and_dos(tmp_path: Path) -> None:
    (tmp_path / "INPUT").write_text(
        "INPUT_PARAMETERS\ncalculation md\ndft_plus_u 1\nout_dos 1\n",
        encoding="utf-8",
    )
    (tmp_path / "STRU").write_text("ATOMIC_POSITIONS\nDirect\n", encoding="utf-8")
    (tmp_path / "KPT").write_text("K_POINTS\n0\nGamma\n1 1 1 0 0 0\n", encoding="utf-8")

    codes = {item.code for item in analyze_case(tmp_path)}

    assert {"ABACUS304", "ABACUS306", "ABACUS308"} <= codes


def test_schema_file_roundtrip_and_runtime_fallback(tmp_path: Path) -> None:
    path = tmp_path / "schema.json"
    SchemaRegistry.builtin().write_json(path)

    registry = SchemaRegistry.from_file(path)
    payload = build_schema(abacus_bin="/does/not/exist")

    assert registry.get("calculation") is not None
    assert payload["keywords"]


def test_format_cli_write_and_lint_plain_output(tmp_path: Path, capsys) -> None:
    input_path = tmp_path / "INPUT"
    input_path.write_text("INPUT_PARAMETERS\nsuffix x\n", encoding="utf-8")
    (tmp_path / "STRU").write_text("ATOMIC_POSITIONS\nDirect\n", encoding="utf-8")
    (tmp_path / "KPT").write_text("K_POINTS\n0\nGamma\n1 1 1 0 0 0\n", encoding="utf-8")

    assert fmt_main(["-w", str(input_path)]) == 0
    assert lint_main([str(tmp_path)]) == 0
    assert "suffix" in input_path.read_text(encoding="utf-8")
    assert capsys.readouterr().out == ""


def test_lsp_entry_reports_stdio_errors(monkeypatch) -> None:
    monkeypatch.setattr(
        "abacus_lsp.cli.run_stdio",
        lambda: (_ for _ in ()).throw(SystemExit("Install abacus-lsp[lsp]")),
    )
    with pytest.raises(SystemExit) as exc:
        lsp_main(["--stdio"])

    assert "abacus-lsp[lsp]" in str(exc.value)


def test_server_format_and_folding_helpers() -> None:
    stru = "ATOMIC_SPECIES\nSi 28 Si.upf\nATOMIC_POSITIONS\nDirect\n"

    assert format_document("STRU", stru).endswith("\n")
    assert folding_ranges("STRU", stru)
    assert format_file_text(
        "INPUT",
        "INPUT_PARAMETERS\nGAMMA_ONLY false\n",
        FormatOptions(keyword_case="upper"),
    )


def test_agent_explain_and_unavailable_fix(tmp_path: Path) -> None:
    assert explain_diagnostic("ABACUS205")["next_action"] == "edit STRU"
    assert explain_diagnostic("UNKNOWN")["next_action"] == "inspect diagnostic evidence"
    assert apply_fix(tmp_path, "UNKNOWN")["ok"] is False


def test_regression_missing_result_and_subprocess_smoke(monkeypatch, tmp_path: Path) -> None:
    expect = tmp_path / "expected.json"
    expect.write_text(json.dumps({"energy": 1.0}), encoding="utf-8")
    assert run_regression(tmp_path, expect, {"energy": 0.1})["ok"] is False

    monkeypatch.setattr("shutil.which", lambda _command: "/bin/true")

    class FakeResult:
        returncode = 0
        stdout = "ok"
        stderr = ""

    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: FakeResult())
    assert run_smoke(tmp_path)["ok"] is True
