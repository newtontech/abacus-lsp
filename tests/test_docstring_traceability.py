from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPORT_PATH = Path("reports/docstring-wiki-raw-traceability.json")


def _load_report(repo_root: Path) -> dict:
    report_file = repo_root / REPORT_PATH
    assert report_file.is_file(), f"Report not found at {REPORT_PATH}"
    return json.loads(report_file.read_text(encoding="utf-8"))


def _run_checker(repo_root: Path, *, strict: bool = False) -> subprocess.CompletedProcess:
    cmd = [
        sys.executable,
        str(repo_root / "scripts" / "check_docstring_traceability.py"),
        "--root",
        str(repo_root),
        "--write-report",
    ]
    if strict:
        cmd.append("--strict")
    return subprocess.run(cmd, cwd=repo_root, check=False, capture_output=True, text=True)


def test_docstring_wiki_raw_traceability_is_complete() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = _run_checker(repo_root, strict=True)
    assert result.returncode == 0, result.stdout + result.stderr


def test_v1_schema_version() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = _load_report(repo_root)
    assert report["schemaVersion"] == "openqc.lsp.traceability.v1"


def test_v1_required_top_level_fields() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = _load_report(repo_root)
    required = [
        "schemaVersion",
        "serverId",
        "repository",
        "languageId",
        "generatedAt",
        "summary",
        "docstrings",
        "wikiSources",
        "ruleIds",
        "sourceUrls",
        "rawManifest",
    ]
    for field in required:
        assert field in report, f"Missing required top-level field: {field}"


def test_v1_server_and_language() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = _load_report(repo_root)
    assert report["serverId"] == "abacus-lsp"
    assert report["languageId"] == "ABACUS"
    assert report["repository"] == "newtontech/abacus-lsp"


def test_v1_summary_zero_failures() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = _load_report(repo_root)
    summary = report["summary"]
    assert summary["docstringsLinked"] == summary["docstringsTotal"]
    assert summary["brokenWikiLinks"] == 0
    assert summary["wikiSourcesWithoutRaw"] == 0
    assert summary["rawManifestFailures"] == 0


def test_v1_rule_id_format() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = _load_report(repo_root)
    pattern = re.compile(r"^ABACUS-[A-Z_]+-[A-Z_]+-\d{3}$")
    for rule in report["ruleIds"]:
        assert "code" in rule, f"Rule missing 'code': {rule}"
        assert pattern.match(rule["code"]), f"Invalid rule ID format: {rule['code']}"


def test_v1_no_absolute_paths() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = _load_report(repo_root)
    report_text = json.dumps(report)
    assert "/Users/" not in report_text, "Report contains absolute /Users/ paths"
    assert "/home/" not in report_text, "Report contains absolute /home/ paths"


def test_v1_docstrings_array_populated() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = _load_report(repo_root)
    assert isinstance(report["docstrings"], list)
    assert len(report["docstrings"]) > 0
    for doc in report["docstrings"]:
        assert "path" in doc
        assert "wikiPath" in doc
        assert "symbol" in doc
        assert doc["wikiPath"].startswith("wiki/")
        assert not doc["path"].startswith("/"), f"Absolute path: {doc['path']}"
        assert "linked" in doc
        assert not doc["file"].startswith("/"), f"Absolute path: {doc['file']}"


def test_v1_wiki_sources_array_populated() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = _load_report(repo_root)
    assert isinstance(report["wikiSources"], list)
    assert len(report["wikiSources"]) > 0
    for ws in report["wikiSources"]:
        assert "wikiPath" in ws
        assert "rawPath" in ws
        assert "sourceUrl" in ws
        assert ws["wikiPath"].startswith("wiki/")
        assert ws["rawPath"].startswith("raw/")
        assert ws["sourceUrl"]


def test_v1_source_urls_are_repository_relative() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = _load_report(repo_root)
    for entry in report["sourceUrls"]:
        assert "rawPath" in entry
        assert "url" in entry
        assert entry["rawPath"].startswith("raw/")
        assert entry["url"].startswith(("http://", "https://"))


def test_v1_raw_manifest_populated() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = _load_report(repo_root)
    assert isinstance(report["rawManifest"], dict)
    assert report["rawManifest"]["path"] == "raw/assets/manifest.json"
    assert report["rawManifest"]["ok"] is True
    assert len(report["rawManifest"]["entries"]) > 0
