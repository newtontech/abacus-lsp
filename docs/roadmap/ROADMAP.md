# Roadmap

The plan is organized into six milestones. Each milestone is also represented as
GitHub issues.

## Milestone 0: Research and Schema

- Create ABACUS input schema generator.
- Create fixture corpus.

## Milestone 1: Parser

- Implement `INPUT` parser.
- Implement `STRU` parser.
- Implement `KPT` parser.

## Milestone 2: Linter

- Implement syntax and schema diagnostics.
- Implement cross-file diagnostics.
- Implement physics and workflow lint rules.

## Milestone 3: Formatter

- Implement safe formatter.
- Implement normalize formatter.

## Milestone 4: LSP

- Implement LSP server MVP.
- Implement code actions.
- Implement formatting provider.

## Milestone 5: Test Runner and Agent Interfaces

- Implement `abacus-test static/smoke/regression`.
- Implement agent JSON protocol.
- Integrate ABACUS-agent-tools as an optional backend.

