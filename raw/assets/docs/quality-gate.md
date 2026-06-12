# newtontech LSP quality gate

`abacus-lsp` follows the shared newtontech LSP quality gate for every pull
request.

## Required checks

- `ruff check src tests scripts`
- `pytest`
- `python -m compileall src tests scripts`

The pytest suite enforces a minimum total coverage threshold of 80%. Feature
work that adds parser, diagnostic, formatter, CLI, or agent behavior must add
targeted tests for the new paths before implementation code is accepted.

## Runtime support

The supported package metadata targets Python 3.9 and newer. CI validates the
current baseline on Python 3.9 and the latest stable Python runner available to
the project.

## Heavy execution

Static diagnostics, schema validation, formatting, and agent context export are
safe default checks. Real ABACUS execution remains opt-in and must be selected
explicitly by a caller or workflow.
