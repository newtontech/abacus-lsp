#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "usage: $0 path/to/abacus_lsp-*.whl" >&2
  exit 2
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WHEEL="$1"
if [[ "$WHEEL" != /* ]]; then
  WHEEL="$(pwd)/$WHEEL"
fi
if [ ! -f "$WHEEL" ]; then
  echo "wheel not found: $WHEEL" >&2
  exit 2
fi

PYTHON_BIN="${PYTHON:-python3}"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

"$PYTHON_BIN" -m venv "$TMP_DIR/venv"
VENV_PYTHON="$TMP_DIR/venv/bin/python"
BIN="$TMP_DIR/venv/bin"
"$VENV_PYTHON" -m pip install --disable-pip-version-check "${WHEEL}[lsp]"

(
  cd "$TMP_DIR"
  # Server CLI: abacus-lsp --help
  "$BIN/abacus-lsp" --help >/dev/null
)

VALID="$REPO_ROOT/tests/fixtures/preflight/valid_pw"
INVALID="$REPO_ROOT/tests/fixtures/invalid/kpt_count"
LOG_CASE="$REPO_ROOT/tests/fixtures/log/geometry_not_converged"

# Agent CLI: abacus-lsp query-diagnostics
"$BIN/abacus-lsp" query-diagnostics "$VALID" >"$TMP_DIR/agent-valid.json"
# Diagnostic Engine CLI: abacus-lsp-tool check
"$BIN/abacus-lsp-tool" check "$VALID" --fail-on-blocking >"$TMP_DIR/valid.json"

if "$BIN/abacus-lsp-tool" check "$INVALID" --fail-on-blocking >"$TMP_DIR/invalid.json"; then
  echo "invalid fixture unexpectedly passed" >&2
  exit 1
fi

"$BIN/abacus-lsp-tool" check "$LOG_CASE" >"$TMP_DIR/log.json"

"$VENV_PYTHON" - "$TMP_DIR" <<'PY'
import importlib.metadata
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
assert importlib.metadata.version("abacus-lsp") == "0.1.1"

agent = json.loads((root / "agent-valid.json").read_text())
valid = json.loads((root / "valid.json").read_text())
invalid = json.loads((root / "invalid.json").read_text())
log = json.loads((root / "log.json").read_text())

assert agent["ok"] is True
assert valid["ok"] is True
assert invalid["ok"] is False
assert any(item["code"] == "ABACUS005" for item in invalid["diagnostics"])
assert any(item["code"] == "ABACUS302" for item in log["diagnostics"])
PY

echo "Fresh-wheel smoke passed: server CLI, agent CLI, valid/invalid/log fixtures"
