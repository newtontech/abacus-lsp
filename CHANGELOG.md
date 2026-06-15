# Changelog

All notable changes to this project are documented in this file.

## [0.1.0] - 2026-06-15

### Added

- Closed-loop fixture gate (`tests/test_closed_loop_fixtures.py`) for OpenQC
  `lsp:check-family` verification.
- OpenQC compatibility report (`diagnostics/openqc-compatibility.md`).
- `fixturePaths` and provenance manifest linkage in `lsp-capabilities.json`.
- `capabilities` agent CLI operation returning `lsp-capabilities.json`.
- `VERSION` file aligned with `pyproject.toml`.

### Fixed

- `scripts/test.sh` now sets `PYTHONPATH=src` so local worktrees run against
  the checkout under test instead of a globally installed package.
