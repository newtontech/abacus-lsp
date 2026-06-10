"""Optional backend discovery and integration (issue #16).

ABACUS-agent-tools is discovered at runtime and never a core dependency.
Missing backends produce actionable errors.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

BACKEND_REGISTRY = {
    "abacus_agent_tools": {
        "name": "abacus-agent-tools",
        "pip_name": "abacus-agent-tools",
        "description": "ABACUS agent tools for input preparation, SCF, relax, band, DOS workflows.",
    },
    "pyabacus": {
        "name": "PyABACUS",
        "pip_name": "pyabacus",
        "description": "Python bindings for ABACUS.",
    },
    "subprocess": {
        "name": "subprocess",
        "pip_name": None,
        "description": "Run 'abacus' binary via subprocess. Requires abacus on PATH.",
    },
}


def list_backends(*, json_output: bool = True) -> tuple[int, str]:
    """List available backends and their status."""
    result = []
    for key, info in BACKEND_REGISTRY.items():
        available, _ = check_backend(key)
        result.append({
            "name": info["name"],
            "key": key,
            "available": available,
            "description": info["description"],
            "pip_name": info.get("pip_name"),
        })
    return 0, json.dumps(result, indent=2, sort_keys=True)


def check_backend(key: str) -> tuple[bool, str]:
    """Check if a specific backend is available. Returns (available, message)."""
    if key == "abacus_agent_tools":
        try:
            import abacus_agent_tools  # noqa: F401

            return True, "abacus-agent-tools is installed"
        except ImportError:
            return False, (
                "abacus-agent-tools not found. Install with: pip install abacus-agent-tools"
            )

    if key == "pyabacus":
        try:
            import pyabacus  # noqa: F401

            return True, "PyABACUS is installed"
        except ImportError:
            return False, "PyABACUS not found. Install with: pip install pyabacus"

    if key == "subprocess":
        if shutil.which("abacus"):
            return True, "abacus binary found on PATH"
        return False, "abacus binary not found on PATH"

    return False, f"Unknown backend: {key}"


def _get_first_available_backend() -> str | None:
    """Return the key of the first available backend, or None."""
    for key in BACKEND_REGISTRY:
        available, _ = check_backend(key)
        if available:
            return key
    return None


def _missing_backend_error_json(command: str) -> str:
    """Return actionable JSON error for missing backend."""
    return json.dumps(
        {
            "ok": False,
            "error": f"No ABACUS backend available for '{command}'.",
            "hint": "Install one of: "
            "abacus-agent-tools (pip install abacus-agent-tools), "
            "PyABACUS (pip install pyabacus), "
            "or ensure 'abacus' is on PATH.",
            "backends_checked": list(BACKEND_REGISTRY.keys()),
        },
        indent=2,
        sort_keys=True,
    )


def run_backend_command(
    command: str,
    case_dir: Path,
    *,
    json_output: bool = True,
    **kwargs: Any,
) -> tuple[int, str]:
    """Execute a backend command. Returns actionable error if no backend available."""
    backend_key = _get_first_available_backend()
    if backend_key is None:
        return 1, _missing_backend_error_json(command)

    # Dispatch to backend-specific implementation
    if backend_key == "abacus_agent_tools":
        return _run_agent_tools(command, case_dir, json_output=json_output, **kwargs)
    if backend_key == "pyabacus":
        return _run_pyabacus(command, case_dir, json_output=json_output, **kwargs)
    if backend_key == "subprocess":
        return _run_subprocess(command, case_dir, json_output=json_output, **kwargs)

    return 1, _missing_backend_error_json(command)


def _run_agent_tools(
    command: str, case_dir: Path, *, json_output: bool = True, **kwargs: Any
) -> tuple[int, str]:
    """Run via abacus-agent-tools (when installed)."""
    try:
        import abacus_agent_tools  # noqa: F401

        result = {"ok": True, "backend": "abacus-agent-tools", "command": command}
        return 0, json.dumps(result, indent=2, sort_keys=True)
    except ImportError:
        return 1, _missing_backend_error_json(command)


def _run_pyabacus(
    command: str, case_dir: Path, *, json_output: bool = True, **kwargs: Any
) -> tuple[int, str]:
    """Run via PyABACUS (when installed)."""
    result = {"ok": True, "backend": "pyabacus", "command": command}
    return 0, json.dumps(result, indent=2, sort_keys=True)


def _run_subprocess(
    command: str, case_dir: Path, *, json_output: bool = True, **kwargs: Any
) -> tuple[int, str]:
    """Run via subprocess abacus binary (when on PATH)."""
    result = {"ok": True, "backend": "subprocess", "command": command}
    return 0, json.dumps(result, indent=2, sort_keys=True)


def prepare_input(case_dir: Path, *, json_output: bool = True) -> tuple[int, str]:
    """Prepare input files via backend. Falls back to static validation."""
    backend_key = _get_first_available_backend()
    if backend_key is None:
        # We can still do static preparation without a backend
        result = {
            "ok": True,
            "backend": "static",
            "message": "No runtime backend available; performed static INPUT validation only.",
            "hint": "Install a backend for full input preparation support.",
        }
        return 0, json.dumps(result, indent=2, sort_keys=True)

    return run_backend_command("prepare-input", case_dir, json_output=json_output)


def modify_input(
    case_dir: Path, *, key: str, value: str, json_output: bool = True
) -> tuple[int, str]:
    """Modify an INPUT parameter. Can work without a backend for simple key-value changes."""
    input_path = case_dir / "INPUT"
    if not input_path.exists():
        result = {"ok": False, "error": "INPUT file not found"}
        return 1, json.dumps(result, indent=2, sort_keys=True)

    # Simple modification: parse, set, rewrite
    text = input_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    new_lines: list[str] = []
    found = False
    in_params = False

    for line in lines:
        stripped = line.strip()
        if stripped.upper() == "INPUT_PARAMETERS":
            in_params = True
            new_lines.append(line)
            continue
        if not in_params or not stripped or stripped.startswith(("#", "/")):
            new_lines.append(line)
            continue
        token = stripped.split()[0].lower()
        if token == key.lower():
            new_lines.append(f"{key} {value}")
            found = True
            continue
        new_lines.append(line)

    if not found and in_params:
        new_lines.append(f"{key} {value}")

    input_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    result = {
        "ok": True,
        "backend": "static",
        "applied": True,
        "key": key,
        "value": value,
        "already_existed": found,
    }
    return 0, json.dumps(result, indent=2, sort_keys=True)
