"""Tests for agent JSON protocol (issue #15)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

DEFAULT_INPUT = "INPUT_PARAMETERS\ncalculation scf\nbasis_type pw\necutwfc 50\n"
DEFAULT_STRU = (
    "ATOMIC_SPECIES\nSi 28.085 Si.upf\n\n"
    "LATTICE_CONSTANT\n1.0\n\n"
    "ATOMIC_POSITIONS\nDirect\nSi\n0.0\n1\n0.0 0.0 0.0\n"
)
DEFAULT_KPT = "K_POINTS\n0\nGamma\n1 1 1 0 0 0\n"


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "abacus_lsp.cli", *args],
        capture_output=True,
        text=True,
    )


def _make_case(
    tmp_path: Path,
    *,
    input_text: str = DEFAULT_INPUT,
    stru_text: str = DEFAULT_STRU,
    kpt_text: str = DEFAULT_KPT,
) -> Path:
    (tmp_path / "INPUT").write_text(input_text, encoding="utf-8")
    (tmp_path / "STRU").write_text(stru_text, encoding="utf-8")
    (tmp_path / "KPT").write_text(kpt_text, encoding="utf-8")
    return tmp_path


# ── query-diagnostics ─────────────────────────────────────────────────────────


class TestQueryDiagnostics:
    def test_query_diagnostics_json_structure(self, tmp_path: Path) -> None:
        case = _make_case(tmp_path)
        r = _run_cli("query-diagnostics", str(case), "--json")
        assert r.returncode in (0, 1), f"stderr={r.stderr}"
        data = json.loads(r.stdout)
        assert "ok" in data
        assert "blocking_errors" in data
        assert "next_action" in data
        assert isinstance(data["blocking_errors"], int)

    def test_query_diagnostics_clean_case(self, tmp_path: Path) -> None:
        case = _make_case(tmp_path)
        r = _run_cli("query-diagnostics", str(case), "--json")
        data = json.loads(r.stdout)
        assert data["ok"] is True
        assert data["blocking_errors"] == 0

    def test_query_diagnostics_with_errors(self, tmp_path: Path) -> None:
        # Missing INPUT file triggers ABACUS201 error
        (tmp_path / "STRU").write_text("ATOMIC_SPECIES\nSi 28 Si.upf\n", encoding="utf-8")
        (tmp_path / "KPT").write_text("K_POINTS\n0\nGamma\n1 1 1 0 0 0\n", encoding="utf-8")
        r = _run_cli("query-diagnostics", str(tmp_path), "--json")
        data = json.loads(r.stdout)
        assert data["ok"] is False
        assert data["blocking_errors"] >= 1

    def test_query_diagnostics_includes_suggested_fixes(self, tmp_path: Path) -> None:
        """When errors have suggested_fix, it should appear in the output."""
        case = _make_case(
            tmp_path,
            input_text=(
                "INPUT_PARAMETERS\nbasis_type lcao\n"
                "calculation scf\necutwfc 50\n"
            ),
        )
        r = _run_cli("query-diagnostics", str(case), "--json")
        data = json.loads(r.stdout)
        # ABACUS205 should be in there with a suggested_fix
        diag_205 = [d for d in data.get("diagnostics", []) if d.get("code") == "ABACUS205"]
        assert len(diag_205) == 1
        assert diag_205[0].get("suggested_fix") is not None

    def test_query_diagnostics_exit_code_distinction(self, tmp_path: Path) -> None:
        """Exit 0 for warnings-only, 1 for blocking errors."""
        # Case with only warnings: unknown keyword
        case_warn = _make_case(
            tmp_path,
            input_text="INPUT_PARAMETERS\necutwfc 50\nunknown_kw val\n",
        )
        r = _run_cli("query-diagnostics", str(case_warn), "--json")
        data = json.loads(r.stdout)
        if data["blocking_errors"] == 0:
            assert r.returncode == 0
        else:
            assert r.returncode == 1


# ── explain-diagnostic ────────────────────────────────────────────────────────


class TestExplainDiagnostic:
    def test_explain_known_code(self) -> None:
        r = _run_cli("explain-diagnostic", "ABACUS205", "--json")
        assert r.returncode == 0
        data = json.loads(r.stdout)
        assert data["code"] == "ABACUS205"
        assert "description" in data
        assert "severity" in data
        assert "suggested_fix" in data

    def test_explain_unknown_code(self) -> None:
        r = _run_cli("explain-diagnostic", "ABACUS999", "--json")
        assert r.returncode == 0
        data = json.loads(r.stdout)
        assert data["code"] == "ABACUS999"
        assert data["known"] is False

    def test_explain_output_deterministic(self) -> None:
        r1 = _run_cli("explain-diagnostic", "ABACUS205", "--json")
        r2 = _run_cli("explain-diagnostic", "ABACUS205", "--json")
        assert r1.stdout == r2.stdout


# ── apply-fix ──────────────────────────────────────────────────────────────────


class TestApplyFix:
    def test_apply_fix_adds_numerical_orbital_section(self, tmp_path: Path) -> None:
        """Applying fix for ABACUS205 should modify STRU to add NUMERICAL_ORBITAL."""
        case = _make_case(
            tmp_path,
            input_text=(
                "INPUT_PARAMETERS\nbasis_type lcao\n"
                "calculation scf\necutwfc 50\n"
            ),
        )
        r = _run_cli("apply-fix", str(case), "--code", "ABACUS205", "--json")
        assert r.returncode == 0
        stru_text = (case / "STRU").read_text(encoding="utf-8")
        assert "NUMERICAL_ORBITAL" in stru_text

    def test_apply_fix_reports_json(self, tmp_path: Path) -> None:
        case = _make_case(
            tmp_path,
            input_text=(
                "INPUT_PARAMETERS\nbasis_type lcao\n"
                "calculation scf\necutwfc 50\n"
            ),
        )
        r = _run_cli("apply-fix", str(case), "--code", "ABACUS205", "--json")
        data = json.loads(r.stdout)
        assert data["applied"] is True
        assert "changes" in data


# ── export-context ─────────────────────────────────────────────────────────────


class TestExportContext:
    def test_export_context_creates_abacus_lsp_dir(self, tmp_path: Path) -> None:
        case = _make_case(tmp_path)
        r = _run_cli("export-context", str(case), "--for-agent")
        assert r.returncode == 0
        export_dir = case / ".abacus-lsp"
        assert export_dir.is_dir()

    def test_export_context_artifacts(self, tmp_path: Path) -> None:
        case = _make_case(tmp_path)
        _run_cli("export-context", str(case), "--for-agent")
        export_dir = case / ".abacus-lsp"
        assert (export_dir / "context.json").exists()
        assert (export_dir / "diagnostics.json").exists()
        assert (export_dir / "schema-used.json").exists()
        assert (export_dir / "files-index.json").exists()

    def test_export_context_json_valid(self, tmp_path: Path) -> None:
        case = _make_case(tmp_path)
        _run_cli("export-context", str(case), "--for-agent")
        ctx = json.loads((case / ".abacus-lsp" / "context.json").read_text(encoding="utf-8"))
        assert "case_dir" in ctx
        assert "diagnostics" in ctx

    def test_export_context_files_index(self, tmp_path: Path) -> None:
        case = _make_case(tmp_path)
        _run_cli("export-context", str(case), "--for-agent")
        idx = json.loads((case / ".abacus-lsp" / "files-index.json").read_text(encoding="utf-8"))
        assert isinstance(idx, list)
        names = [f["name"] for f in idx]
        assert "INPUT" in names
        assert "STRU" in names
        assert "KPT" in names

    def test_export_context_schema_used(self, tmp_path: Path) -> None:
        case = _make_case(tmp_path)
        _run_cli("export-context", str(case), "--for-agent")
        schema = json.loads(
            (case / ".abacus-lsp" / "schema-used.json").read_text(encoding="utf-8")
        )
        assert isinstance(schema, dict)
        assert "input_keywords" in schema
