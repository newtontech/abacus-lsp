from __future__ import annotations

import json
from pathlib import Path

from abacus_lsp.agent import apply_fix, export_context, query_diagnostics
from abacus_lsp.cli import _parse_tolerance, agent_main, schema_main
from abacus_lsp.cli import test_main as cli_test_main
from abacus_lsp.server import code_actions, completion_items, document_symbols, hover_text
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
        cli_test_main(["smoke", str(FIXTURES / "valid" / "mgo_lcao"), "--backend", "pyabacus"])
        == 1
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
