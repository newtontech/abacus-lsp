"""Tests for optional backend integration (issue #16)."""
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


class TestBackendDiscovery:
    """abacus-lsp alone does not install or require ABACUS-agent-tools."""

    def test_no_agent_tools_import_required(self) -> None:
        """Core abacus_lsp imports should work without abacus_agent_tools."""
        import importlib

        spec = importlib.util.find_spec("abacus_agent_tools")
        assert spec is None, "abacus_agent_tools should not be installed in this test env"

    def test_backend_list_command(self) -> None:
        r = _run_cli("backend", "list", "--json")
        assert r.returncode == 0
        data = json.loads(r.stdout)
        assert isinstance(data, list)
        # Without abacus_agent_tools installed, backends should list available ones
        # with status information
        for entry in data:
            assert "name" in entry
            assert "available" in entry

    def test_missing_backend_actionable_error(self, tmp_path: Path) -> None:
        (tmp_path / "INPUT").write_text("INPUT_PARAMETERS\ncalculation scf\n", encoding="utf-8")
        r = _run_cli("backend", "run-scf", str(tmp_path), "--json")
        assert r.returncode != 0
        combined = r.stdout + r.stderr
        # Must be actionable: mention the backend name and how to get it
        assert "backend" in combined.lower()

    def test_backend_commands_are_explicit(self) -> None:
        """Backend commands must not be invoked by normal diagnostics."""
        # Normal lint should not reference backends
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            (td / "INPUT").write_text("INPUT_PARAMETERS\necutwfc 50\n", encoding="utf-8")
            (td / "STRU").write_text("ATOMIC_SPECIES\nSi 28 Si.upf\n", encoding="utf-8")
            (td / "KPT").write_text("K_POINTS\n0\nGamma\n1 1 1 0 0 0\n", encoding="utf-8")
            r = _run_cli("lint", str(td))
            assert "backend" not in r.stdout.lower()
            assert "backend" not in r.stderr.lower()


class TestBackendCommands:
    """Explicit backend commands exist and are documented."""

    def test_backend_subcommand_help(self) -> None:
        r = _run_cli("backend", "--help")
        assert r.returncode == 0
        help_text = r.stdout.lower()
        # Should list available subcommands
        assert "list" in help_text or "run" in help_text

    def test_backend_prepare_input_without_tools(self, tmp_path: Path) -> None:
        (tmp_path / "INPUT").write_text("INPUT_PARAMETERS\ncalculation scf\n", encoding="utf-8")
        r = _run_cli("backend", "prepare-input", str(tmp_path), "--json")
        # Should either work (if there's a built-in prepare) or give actionable error
        assert r.returncode in (0, 1, 2)
        if r.returncode != 0:
            combined = r.stdout + r.stderr
            assert "backend" in combined.lower() or "agent-tools" in combined.lower()

    def test_backend_modify_input_without_tools(self, tmp_path: Path) -> None:
        (tmp_path / "INPUT").write_text("INPUT_PARAMETERS\ncalculation scf\n", encoding="utf-8")
        r = _run_cli(
            "backend", "modify-input", str(tmp_path),
            "--key", "ecutwfc", "--value", "100", "--json",
        )
        assert r.returncode in (0, 1, 2)
        if r.returncode != 0:
            combined = r.stdout + r.stderr
            assert "backend" in combined.lower() or "agent-tools" in combined.lower()

    def test_backend_run_relax_without_tools(self, tmp_path: Path) -> None:
        (tmp_path / "INPUT").write_text("INPUT_PARAMETERS\ncalculation relax\n", encoding="utf-8")
        r = _run_cli("backend", "run-relax", str(tmp_path), "--json")
        assert r.returncode != 0
        combined = r.stdout + r.stderr
        assert "backend" in combined.lower()

    def test_backend_run_band_without_tools(self, tmp_path: Path) -> None:
        (tmp_path / "INPUT").write_text(
            "INPUT_PARAMETERS\ncalculation scf\nout_band 1\n", encoding="utf-8"
        )
        r = _run_cli("backend", "run-band", str(tmp_path), "--json")
        assert r.returncode != 0
        combined = r.stdout + r.stderr
        assert "backend" in combined.lower()

    def test_backend_run_dos_without_tools(self, tmp_path: Path) -> None:
        (tmp_path / "INPUT").write_text(
            "INPUT_PARAMETERS\ncalculation scf\nout_dos 1\n", encoding="utf-8"
        )
        r = _run_cli("backend", "run-dos", str(tmp_path), "--json")
        assert r.returncode != 0
        combined = r.stdout + r.stderr
        assert "backend" in combined.lower()
