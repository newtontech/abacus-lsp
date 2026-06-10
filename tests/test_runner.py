"""Tests for abacus-test CLI: static, smoke, regression (issue #14)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "abacus_lsp.cli", *args],
        capture_output=True,
        text=True,
    )


# ── Static tests ──────────────────────────────────────────────────────────────


class TestStaticCommand:
    """abacus-test static requires no ABACUS binary."""

    def _make_case(self, tmp_path: Path, *, input_text: str, stru_text: str, kpt_text: str) -> Path:
        (tmp_path / "INPUT").write_text(input_text, encoding="utf-8")
        (tmp_path / "STRU").write_text(stru_text, encoding="utf-8")
        (tmp_path / "KPT").write_text(kpt_text, encoding="utf-8")
        return tmp_path

    def test_static_clean_case_passes(self, tmp_path: Path) -> None:
        case = self._make_case(
            tmp_path,
            input_text=(
                "INPUT_PARAMETERS\ncalculation scf\n"
                "basis_type pw\necutwfc 50\n"
            ),
            stru_text=(
                "ATOMIC_SPECIES\nSi 28.085 Si.upf\n\n"
                "LATTICE_CONSTANT\n1.0\n\n"
                "ATOMIC_POSITIONS\nDirect\nSi\n0.0\n"
                "1\n0.0 0.0 0.0\n"
            ),
            kpt_text="K_POINTS\n0\nGamma\n1 1 1 0 0 0\n",
        )
        r = _run_cli("test", "static", str(case), "--json")
        assert r.returncode == 0, f"stdout={r.stdout}\nstderr={r.stderr}"
        data = json.loads(r.stdout)
        errors = [d for d in data if d["severity"] == "error"]
        assert errors == []

    def test_static_missing_input_returns_error(self, tmp_path: Path) -> None:
        (tmp_path / "STRU").write_text("ATOMIC_SPECIES\nSi 28 Si.upf\n", encoding="utf-8")
        (tmp_path / "KPT").write_text("K_POINTS\n0\nGamma\n1 1 1 0 0 0\n", encoding="utf-8")
        r = _run_cli("test", "static", str(tmp_path), "--json")
        assert r.returncode == 1
        data = json.loads(r.stdout)
        assert any(d["code"] == "ABACUS201" for d in data)

    def test_static_json_is_deterministic(self, tmp_path: Path) -> None:
        case = self._make_case(
            tmp_path,
            input_text="INPUT_PARAMETERS\necutwfc 50\n",
            stru_text="ATOMIC_SPECIES\nSi 28 Si.upf\n",
            kpt_text="K_POINTS\n0\nGamma\n1 1 1 0 0 0\n",
        )
        r1 = _run_cli("test", "static", str(case), "--json")
        r2 = _run_cli("test", "static", str(case), "--json")
        assert r1.stdout == r2.stdout

    def test_static_sarif_like_output(self, tmp_path: Path) -> None:
        """Static --sarif emits SARIF-like structure with $schema and results."""
        case = self._make_case(
            tmp_path,
            input_text="INPUT_PARAMETERS\necutwfc 50\n",
            stru_text="ATOMIC_SPECIES\nSi 28 Si.upf\n",
            kpt_text="K_POINTS\n0\nGamma\n1 1 1 0 0 0\n",
        )
        r = _run_cli("test", "static", str(case), "--sarif")
        assert r.returncode in (0, 1)
        sarif = json.loads(r.stdout)
        assert "$schema" in sarif
        assert "results" in sarif
        assert isinstance(sarif["results"], list)

    def test_static_github_annotation_output(self, tmp_path: Path) -> None:
        """Static --github emits GitHub Actions annotation format."""
        case = self._make_case(
            tmp_path,
            input_text="INPUT_PARAMETERS\necutwfc 50\n",
            stru_text="ATOMIC_SPECIES\nSi 28 Si.upf\n",
            kpt_text="K_POINTS\n0\nGamma\n1 1 1 0 0 0\n",
        )
        r = _run_cli("test", "static", str(case), "--github")
        assert r.returncode in (0, 1)
        # Each line should match ::LEVEL file=...,line=...::message or be empty
        for line in r.stdout.strip().splitlines():
            if line:
                assert line.startswith("::")


# ── Smoke tests (opt-in) ──────────────────────────────────────────────────────


class TestSmokeCommand:
    """abacus-test smoke is opt-in and errors cleanly without backend."""

    def test_smoke_without_backend_errors_actionably(self, tmp_path: Path) -> None:
        (tmp_path / "INPUT").write_text("INPUT_PARAMETERS\ncalculation scf\n", encoding="utf-8")
        r = _run_cli("test", "smoke", str(tmp_path), "--json")
        assert r.returncode != 0
        # Should produce actionable error about missing backend
        combined = r.stdout + r.stderr
        assert "backend" in combined.lower() or "abacus" in combined.lower()

    def test_smoke_subcommand_exists(self) -> None:
        r = _run_cli("test", "smoke", "--help")
        assert r.returncode == 0
        assert "smoke" in r.stdout.lower() or "timeout" in r.stdout.lower()


# ── Regression tests (opt-in) ─────────────────────────────────────────────────


class TestRegressionCommand:
    """abacus-test regression is opt-in and errors cleanly without backend."""

    def test_regression_without_backend_errors_actionably(self, tmp_path: Path) -> None:
        (tmp_path / "INPUT").write_text("INPUT_PARAMETERS\ncalculation scf\n", encoding="utf-8")
        r = _run_cli("test", "regression", str(tmp_path), "--json")
        assert r.returncode != 0
        combined = r.stdout + r.stderr
        assert "backend" in combined.lower() or "abacus" in combined.lower()

    def test_regression_subcommand_exists(self) -> None:
        r = _run_cli("test", "regression", "--help")
        assert r.returncode == 0
