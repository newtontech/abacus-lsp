from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from .agent import query_diagnostics


def run_static(case_dir: Path) -> dict[str, Any]:
    return query_diagnostics(case_dir)


def run_smoke(
    case_dir: Path,
    backend: str = "subprocess",
    timeout: int = 120,
    nprocs: int = 1,
    abacus_command: str = "abacus",
) -> dict[str, Any]:
    if backend == "pyabacus":
        try:
            import pyabacus  # type: ignore[import-not-found]  # pragma: no cover
        except ImportError:
            return {"ok": False, "reason": "pyabacus backend is not installed"}
        return {"ok": bool(pyabacus), "backend": backend}  # pragma: no cover
    if backend == "agent-tools":
        if not _has_agent_tools():
            return {"ok": False, "reason": "ABACUS-agent-tools backend is not installed"}
        return {"ok": False, "reason": "agent-tools execution adapter is not configured"}
    if backend != "subprocess":
        return {"ok": False, "reason": f"unknown smoke backend: {backend}"}
    if shutil.which(abacus_command) is None:
        return {"ok": False, "reason": f"ABACUS command not found: {abacus_command}"}
    result = subprocess.run(
        [abacus_command],
        cwd=case_dir,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
        env={"OMP_NUM_THREADS": str(nprocs)},
    )
    return {
        "ok": result.returncode == 0,
        "backend": backend,
        "returncode": result.returncode,
        "stdout": result.stdout[-4000:],
        "stderr": result.stderr[-4000:],
    }


def run_regression(
    case_dir: Path,
    expect_path: Path,
    tolerance: dict[str, float],
) -> dict[str, Any]:
    expected = json.loads(expect_path.read_text(encoding="utf-8"))
    actual_path = case_dir / "result.json"
    if not actual_path.exists():
        return {"ok": False, "reason": f"missing result file: {actual_path}"}
    actual = json.loads(actual_path.read_text(encoding="utf-8"))
    failures = []
    for key, expected_value in expected.items():
        actual_value = actual.get(key)
        limit = tolerance.get(key, 0.0)
        if isinstance(expected_value, (int, float)) and isinstance(actual_value, (int, float)):
            if abs(actual_value - expected_value) > limit:
                failures.append({"key": key, "expected": expected_value, "actual": actual_value})
        elif actual_value != expected_value:
            failures.append({"key": key, "expected": expected_value, "actual": actual_value})
    return {"ok": not failures, "failures": failures}


def _has_agent_tools() -> bool:
    try:
        import abacus_agent_tools  # pragma: no cover
    except ImportError:
        return False
    return bool(abacus_agent_tools)  # pragma: no cover
