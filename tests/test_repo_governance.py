"""Repository governance and docs asset checks."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_governance_guidance_files_exist() -> None:
    required = (
        "AGENTS.md",
        "CONTRIBUTING.md",
        ".governance-kit.yml",
        ".github/PULL_REQUEST_TEMPLATE.md",
        "docs/LLM-WIKI-PLAN.md",
    )
    missing = [path for path in required if not (REPO_ROOT / path).is_file()]
    assert not missing, f"Missing governance files: {', '.join(missing)}"


def test_pr_contract_fetch_has_merge_base() -> None:
    workflow = (REPO_ROOT / ".github" / "workflows" / "pr-contract.yml").read_text(encoding="utf-8")
    assert 'git fetch origin "$BASE_REF" --depth=1' not in workflow
