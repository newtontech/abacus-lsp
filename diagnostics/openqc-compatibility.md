# OpenQC Compatibility Report — abacus-lsp

> Generated: 2026-06-15
> Capability manifest: `lsp-capabilities.json`
> Provenance manifest: `raw/assets/manifest.json`
> Coordinator gate: `lsp:check-family`

This document records the executable evidence that `abacus-lsp` is wired into
the OpenQC scientific LSP fleet. It is intentionally machine-readable in
structure so the coordinator can verify each claim from the repo without
running the LSP server.

## 1. Language and file detection

| Field | Value | Evidence |
|-------|-------|----------|
| `software` | ABACUS | `lsp-capabilities.json` |
| `file_types_supported` | INPUT, KPT, STRU | `lsp-capabilities.json` |
| `operations` | check, context, complete, hover, symbols, fix | `lsp-capabilities.json` |

## 2. Configured executable

| Field | Value |
|-------|-------|
| `agentCli.command` | `abacus-lsp-tool` |
| `openqc.cli_smoke_test` | `scripts/openqc_smoke.sh` |
| `openqc.lsp_check_family` | true |

## 3. Agent CLI availability

`abacus-lsp-tool` answers the fleet-standard operations:

```bash
abacus-lsp-tool capabilities
abacus-lsp-tool check <path> [--fail-on-blocking]
abacus-lsp-tool preflight <path> [--fail-on-blocking]
abacus-lsp-tool manifest [path]
abacus-lsp-tool context <path> [--line N --character N]
abacus-lsp-tool complete <path> [--line N --character N]
abacus-lsp-tool hover <path> [--line N --character N]
abacus-lsp-tool symbols <path>
abacus-lsp-tool fix <path> [--line N --character N]
```

Every operation returns stable `DiagnosticEnvelope/v1` JSON.

## 4. Closed-loop fixture evidence

| Fixture | Expected outcome | Verified by |
|---------|------------------|-------------|
| `tests/fixtures/preflight/valid_pw` | clean gate (`ok=true`, no blocking) | `tests/test_closed_loop_fixtures.py` |
| `tests/fixtures/valid/si_pw` | no blocking errors | `tests/test_closed_loop_fixtures.py` |
| `tests/fixtures/invalid/kpt_count` | `ABACUS005` blocking error | `tests/test_closed_loop_fixtures.py` |
| `tests/fixtures/preflight/low_ecutwfc` | `ABACUS607` non-blocking warning | `tests/test_closed_loop_fixtures.py` |
| `tests/fixtures/invalid/unknown_keyword` | `ABACUS002` non-blocking warning | `tests/test_closed_loop_fixtures.py` |
| `tests/fixtures/log/geometry_not_converged/running.log` | `ABACUS302` runtime log error | `tests/test_closed_loop_fixtures.py` |

## 5. Source provenance summary

Official ABACUS documentation anchors are captured under `raw/assets/` with
checksums in `raw/assets/manifest.json`. Runtime preflight diagnostics
(`ABACUS601`–`ABACUS610`) carry structured `source_provenance` fields.
Legacy analyzer codes (`ABACUS001`–`ABACUS422`) are mapped in
`lsp-capabilities.json` `sourceProvenance` entries.

## 6. Blocking policy (representative codes)

| Code | Severity | Blocks run-gate? |
|------|----------|------------------|
| ABACUS005 (KPT count mismatch) | error | yes |
| ABACUS101 (schema type/enum) | error | yes |
| ABACUS603 (missing lattice) | error | yes |
| ABACUS002 (unknown keyword) | warning | no |
| ABACUS607 (low ecutwfc) | warning | no |
| ABACUS302 (geometry not converged) | error | yes (runtime log) |

## 7. Output/log diagnostic support

| Layer | Status |
|-------|--------|
| INPUT/KPT/STRU parser rules | implemented (analyzer + schema registry) |
| Preflight cross-file checks | implemented (`ABACUS601`–`ABACUS610`) |
| Runtime log parser | implemented for SCF/geometry/segfault/file/memory patterns |
| Version-aware keyword scope | implemented via `.abacus-lsp/intent.json` |

Grammar coverage is **partial** by design: only documented INPUT keywords and
common runtime log patterns are enforced. Full ABACUS 3.8 keyword coverage
remains tracked in issue #64.

## 8. Verification commands

```bash
# Closed-loop fixture gate
PYTHONPATH=src python3 -m pytest tests/test_closed_loop_fixtures.py -v

# OpenQC smoke script
bash scripts/openqc_smoke.sh

# Full test suite
make test
```
