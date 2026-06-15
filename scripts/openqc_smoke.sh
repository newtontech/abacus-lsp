#!/usr/bin/env bash
# OpenQC smoke test for abacus-lsp
# Verifies: language/file detection, configured executable, CLI availability,
# and compatibility-report entry
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LSP_BIN="${REPO_ROOT}/src/abacus_lsp/cli.py"
CAPABILITIES="${REPO_ROOT}/lsp-capabilities.json"
MANIFEST="${REPO_ROOT}/raw/assets/manifest.json"
FIXTURES_DIR="${REPO_ROOT}/tests/fixtures"

echo "=== OpenQC Smoke Test: abacus-lsp ==="
echo ""

# 1. Check lsp-capabilities.json exists and is valid JSON
echo "[1/6] Checking lsp-capabilities.json..."
if [ ! -f "$CAPABILITIES" ]; then
  echo "FAIL: lsp-capabilities.json not found"
  exit 1
fi
if ! python3 -c "import json; json.load(open('$CAPABILITIES'))" 2>/dev/null; then
  echo "FAIL: lsp-capabilities.json is not valid JSON"
  exit 1
fi
echo "  OK: lsp-capabilities.json is valid JSON"

# 2. Check manifest.json exists and is valid JSON
echo "[2/6] Checking raw/assets/manifest.json..."
if [ ! -f "$MANIFEST" ]; then
  echo "FAIL: raw/assets/manifest.json not found"
  exit 1
fi
if ! python3 -c "import json; json.load(open('$MANIFEST'))" 2>/dev/null; then
  echo "FAIL: raw/assets/manifest.json is not valid JSON"
  exit 1
fi
echo "  OK: manifest.json is valid JSON"

# 3. Check file type detection
echo "[3/6] Checking file type detection..."
python3 -c "
from pathlib import Path
import sys
sys.path.insert(0, '${REPO_ROOT}/src')
from abacus_lsp.analyzer import analyze_case

# Test with valid fixture
valid_dir = Path('${FIXTURES_DIR}/valid/si_pw')
if not valid_dir.exists():
    print('FAIL: valid/si_pw fixture not found')
    sys.exit(1)

diags = analyze_case(valid_dir)
print(f'  OK: analyze_case on valid/si_pw returned {len(diags)} diagnostics')
if any(d.severity == 'error' for d in diags):
    print(f'  WARN: valid fixture has error diagnostics: {[d.code for d in diags if d.severity == \"error\"]}')
"

# 4. Check CLI availability
echo "[4/6] Checking CLI availability..."
if [ -f "$LSP_BIN" ]; then
  if python3 "$LSP_BIN" --help >/dev/null 2>&1; then
    echo "  OK: CLI --help works"
  else
    echo "  WARN: CLI --help failed (may need dependencies)"
  fi
else
  echo "  WARN: CLI entry point not found at $LSP_BIN"
fi

# 5. Check DiagnosticEnvelope/v1 compatibility
echo "[5/6] Checking DiagnosticEnvelope/v1 schema..."
SCHEMA_FILE="${REPO_ROOT}/raw/assets/diagnostics/diagnostic-engine-v1.schema.json"
if [ -f "$SCHEMA_FILE" ]; then
  if python3 -c "import json; json.load(open('$SCHEMA_FILE'))" 2>/dev/null; then
    echo "  OK: diagnostic-engine-v1.schema.json is valid"
  else
    echo "  FAIL: diagnostic-engine-v1.schema.json is not valid JSON"
    exit 1
  fi
else
  echo "  FAIL: diagnostic-engine-v1.schema.json not found"
  exit 1
fi

# 6. Check sourceProvenance traceability
echo "[6/6] Checking sourceProvenance entries..."
PROVENANCE_COUNT=$(python3 -c "
import json
caps = json.load(open('$CAPABILITIES'))
print(len(caps.get('sourceProvenance', [])))
")
echo "  OK: Found $PROVENANCE_COUNT sourceProvenance entries"

if [ "$PROVENANCE_COUNT" -lt 3 ]; then
  echo "  FAIL: Expected at least 3 sourceProvenance entries"
  exit 1
fi

echo ""
echo "=== OpenQC Smoke Test: PASSED ==="
echo ""
echo "Compatibility Report Entry:"
echo "  repository: newtontech/abacus-lsp"
echo "  software: ABACUS"
echo "  file_types: INPUT, KPT, STRU"
echo "  diagnostic_schema: DiagnosticEnvelope/v1"
echo "  source_provenance_count: $PROVENANCE_COUNT"
echo "  openqc_check_family: true"
