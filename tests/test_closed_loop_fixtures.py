"""Closed-loop fixture tests for abacus-lsp.

These tests exercise the canonical fixture directories declared in
``lsp-capabilities.json`` through the agent CLI surface
(``abacus-lsp-tool check`` / log parser). They are the single-command gate
that OpenQC's ``lsp:check-family`` coordinator consumes.

Issues addressed:
- #65 closed-loop fixtures, repair previews, output diagnostics, OpenQC smoke
- #64 DiagnosticEnvelope/v1 with rule IDs, severity, blocking, source
       provenance, and version scope
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = REPO_ROOT / "tests" / "fixtures"
VALID_DIRS = (
    FIXTURES / "valid",
    FIXTURES / "preflight" / "valid_pw",
)
INVALID_DIR = FIXTURES / "invalid"
LOG_DIR = FIXTURES / "log"


def _run_tool(*args: str) -> dict:
    """Run ``abacus-lsp-tool`` and return its parsed JSON payload."""
    cmd = [sys.executable, "-m", "abacus_lsp.tool", *args]
    proc = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        env={**os.environ, "PYTHONPATH": str(REPO_ROOT / "src")},
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert proc.returncode in (0, 1), proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["diagnostic_envelope"] == "v1", payload
    assert payload["software"] == "abacus", payload
    return payload


def test_canonical_fixture_directories_exist() -> None:
    """The canonical paths advertised in lsp-capabilities.json must exist."""
    for path in (*VALID_DIRS, INVALID_DIR, LOG_DIR):
        assert path.is_dir(), f"missing canonical fixture dir: {path}"
    assert any((FIXTURES / "valid").iterdir())
    assert any(INVALID_DIR.iterdir())
    assert any(LOG_DIR.iterdir())


def test_valid_preflight_fixture_has_no_blocking_errors() -> None:
    """Canonical valid workspace: no blocking diagnostics (ok=true)."""
    payload = _run_tool("check", str(FIXTURES / "preflight" / "valid_pw"))
    assert payload["ok"] is True, payload
    blocking = [d for d in payload["diagnostics"] if d.get("blocking")]
    assert blocking == [], payload["diagnostics"]


@pytest.mark.parametrize(
    "case",
    sorted(p.name for p in (FIXTURES / "valid").iterdir() if p.is_dir()),
)
def test_valid_case_directories_have_no_blocking_errors(case: str) -> None:
    """Valid multi-file cases must not emit blocking errors."""
    payload = _run_tool("check", str(FIXTURES / "valid" / case))
    blocking = [d for d in payload["diagnostics"] if d.get("blocking")]
    assert not blocking, payload["diagnostics"]


def test_kpt_count_is_blocking_error() -> None:
    """Invalid fixture: ABACUS005 blocking KPT count mismatch."""
    payload = _run_tool("check", str(INVALID_DIR / "kpt_count"))
    assert payload["ok"] is False
    errors = [d for d in payload["diagnostics"] if d["code"] == "ABACUS005"]
    assert errors, payload["diagnostics"]
    diag = errors[0]
    assert diag["severity"] == "error"
    assert diag["blocking"] is True


def test_low_ecutwfc_is_non_blocking_warning() -> None:
    """Preflight fixture: ABACUS607 warning that does NOT block the gate."""
    payload = _run_tool("check", str(FIXTURES / "preflight" / "low_ecutwfc"))
    warnings = [d for d in payload["diagnostics"] if d["code"] == "ABACUS607"]
    assert warnings, payload["diagnostics"]
    assert all(d["severity"] == "warning" for d in warnings)
    assert all(d["blocking"] is False for d in warnings)
    assert payload["ok"] is True, payload
    for diag in warnings:
        assert diag.get("source_provenance"), diag


def test_unknown_keyword_emits_warning() -> None:
    """Invalid fixture: ABACUS002 warning for unknown INPUT keyword."""
    payload = _run_tool("check", str(INVALID_DIR / "unknown_keyword"))
    warnings = [d for d in payload["diagnostics"] if d["code"] == "ABACUS002"]
    assert warnings, payload["diagnostics"]
    diag = warnings[0]
    assert diag["severity"] == "warning"
    assert diag["blocking"] is False


def test_fix_operation_returns_action_plan() -> None:
    """``fix`` returns a preview patch / action plan, not a destructive edit."""
    payload = _run_tool("fix", str(INVALID_DIR / "kpt_count"))
    assert payload["operation"] == "fix"
    assert "diagnostics" in payload


def test_log_fixture_emits_runtime_diagnostic() -> None:
    """Runtime log fixture yields ABACUS302 geometry convergence diagnostic."""
    from abacus_lsp.analyzer import parse_log

    diagnostics = parse_log(LOG_DIR / "geometry_not_converged" / "running.log")
    assert diagnostics, "expected at least one log diagnostic"
    diag = diagnostics[0]
    assert diag.code == "ABACUS302"
    assert diag.severity == "error"


def test_capabilities_payload_advertises_canonical_fixture_paths() -> None:
    """lsp-capabilities.json must advertise the canonical fixture dirs."""
    capabilities = json.loads((REPO_ROOT / "lsp-capabilities.json").read_text())
    fixture_paths = capabilities["fixturePaths"]
    assert "tests/fixtures/valid" in fixture_paths["valid"]
    assert "tests/fixtures/preflight/valid_pw" in fixture_paths["valid"]
    assert "tests/fixtures/invalid" in fixture_paths["invalid"]
    assert "tests/fixtures/log" in fixture_paths["logs"]


def test_provenance_manifest_exists_and_links_wiki() -> None:
    """raw/assets/manifest.json records official doc anchors with checksums."""
    manifest_path = REPO_ROOT / "raw" / "assets" / "manifest.json"
    assert manifest_path.is_file(), "missing raw/assets/manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest.get("schema_version") == "provenance-manifest-v1"
    anchors = manifest.get("official_source_anchors", [])
    assert anchors, "manifest must list official_source_anchors"
    assert any(a.get("url", "").startswith("https://abacus.deepmodeling.com") for a in anchors)
    entries = manifest.get("entries", [])
    assert len(entries) >= 5, "manifest should cover core captured docs"


def test_openqc_compatibility_report_exists_and_references_fixtures() -> None:
    """The OpenQC compatibility report must be present and up-to-date."""
    report = REPO_ROOT / "diagnostics" / "openqc-compatibility.md"
    assert report.is_file(), "missing diagnostics/openqc-compatibility.md"
    text = report.read_text(encoding="utf-8")
    for fixture in (
        "tests/fixtures/preflight/valid_pw",
        "tests/fixtures/invalid/kpt_count",
        "tests/fixtures/preflight/low_ecutwfc",
        "tests/fixtures/log/geometry_not_converged/running.log",
    ):
        assert fixture in text, f"openqc report missing reference: {fixture}"
    assert "ABACUS005" in text
    assert "ABACUS607" in text
