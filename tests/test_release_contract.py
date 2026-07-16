from __future__ import annotations

import json
import re
from pathlib import Path

import abacus_lsp

REPO_ROOT = Path(__file__).resolve().parents[1]
RELEASE_VERSION = "0.1.1"


def _project_version() -> str:
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    project = pyproject.split("[project]", 1)[1].split("\n[", 1)[0]
    match = re.search(r'^version = "([^"]+)"$', project, re.MULTILINE)
    assert match is not None
    return match.group(1)


def test_release_version_is_consistent() -> None:
    assert _project_version() == RELEASE_VERSION
    assert abacus_lsp.__version__ == RELEASE_VERSION
    assert (REPO_ROOT / "VERSION").read_text(encoding="utf-8").strip() == RELEASE_VERSION

    capabilities = json.loads((REPO_ROOT / "lsp-capabilities.json").read_text(encoding="utf-8"))
    assert capabilities["releaseVersion"] == RELEASE_VERSION
    assert capabilities["repository"] == "newtontech/abacus-lsp"


def test_release_notes_and_install_docs_cover_current_version() -> None:
    changelog = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert f"## [{RELEASE_VERSION}] - 2026-07-16" in changelog

    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert "pip install abacus-lsp[lsp]" in readme
    assert f"Current release: `{RELEASE_VERSION}`" in readme
    assert "Trusted Publishing" in readme


def test_release_workflow_uses_tag_only_oidc_trusted_publishing() -> None:
    workflow = (REPO_ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")

    assert re.search(r"push:\s*\n\s+tags:\s*\[?\"v\*\"\]?", workflow)
    assert "workflow_dispatch:" not in workflow
    assert "environment: pypi" in workflow
    assert "id-token: write" in workflow
    assert "pypa/gh-action-pypi-publish@release/v1" in workflow
    assert "python -m build" in workflow
    assert "python -m twine check dist/*" in workflow
    assert "scripts/smoke_wheel.sh dist/*.whl" in workflow
    assert "Tag version does not match pyproject.toml" in workflow


def test_fresh_wheel_smoke_covers_server_agent_and_fixture_classes() -> None:
    smoke = (REPO_ROOT / "scripts" / "smoke_wheel.sh").read_text(encoding="utf-8")
    for required in (
        "abacus-lsp --help",
        "abacus-lsp query-diagnostics",
        "abacus-lsp-tool check",
        "tests/fixtures/preflight/valid_pw",
        "tests/fixtures/invalid/kpt_count",
        "tests/fixtures/log/geometry_not_converged",
        "ABACUS005",
        "ABACUS302",
    ):
        assert required in smoke
