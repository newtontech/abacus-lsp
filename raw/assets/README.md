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

