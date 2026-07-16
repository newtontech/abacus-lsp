# abacus-lsp

`abacus-lsp` is a Language Server Protocol and CLI toolkit for ABACUS `INPUT`,
`STRU`, and `KPT` files.

The project goal is to provide a fast, deterministic feedback layer for humans
and coding agents that write ABACUS inputs. The LSP should stay lightweight:
syntax, schema, cross-file checks, formatting, and explicit commands belong in
this repository; real ABACUS calculations, Bohrium submissions, and heavier
workflow automation should only run through explicit test or command entry
points.

## Initial CLI Surface

```bash
abacus-lsp --stdio
abacus-lint ./case --json
abacus-fmt -w INPUT STRU KPT
abacus-test static ./case
```

## Installation

Current release: `0.1.1`

Install the command-line and agent tools from PyPI:

```bash
pip install abacus-lsp
```

Install the stdio language server with its optional protocol dependencies:

```bash
pip install abacus-lsp[lsp]
abacus-lsp --stdio
```

The `abacus-lsp-tool` agent CLI exposes JSON capabilities, checks, context,
completion, hover, symbols, and non-destructive fix previews.

## Releases

Releases use PyPI Trusted Publishing: a pushed `v*` tag starts the release
workflow, which verifies that the tag matches `pyproject.toml`, builds and
checks the distribution, and installs the wheel into a fresh virtual
environment for CLI and fixture smoke tests. Only the protected `pypi`
environment receives `id-token: write`; no long-lived PyPI token is stored.

GitHub Release finalization is a sibling of PyPI publication: it consumes the
same verified `python-distributions` artifact, validates the tag checkout
against `GITHUB_SHA`, and can succeed even when PyPI trusted publishing is
temporarily unavailable.

For future versions, create the approved `v*` tag on the exact release
commit. Pull requests and ordinary branch pushes cannot publish, and rerunning a
completed tag does not create a duplicate GitHub Release.

The first committed version includes a small static analyzer and formatter
scaffold so roadmap work can start from a runnable baseline.

## Development

```bash
python -m pip install -e ".[dev]"
pytest
ruff check src tests
```

The runtime package intentionally has no hard dependency on ABACUS, PyABACUS,
or ABACUS-agent-tools. Those integrations are planned as optional backends.

## Roadmap

The roadmap is tracked in GitHub issues and summarized in
[docs/roadmap/ROADMAP.md](docs/roadmap/ROADMAP.md).
