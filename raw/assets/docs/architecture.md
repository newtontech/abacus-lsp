# Architecture

`abacus-lsp` is designed as a layered toolkit:

1. Parser: loss-aware parsing for `INPUT`, `STRU`, and `KPT`.
2. Schema registry: ABACUS keyword metadata from bundled schemas, local
   `abacus -h` output, and optional project overrides.
3. Linter: syntax, schema, cross-file, physics/workflow, and agent-oriented
   diagnostics.
4. Formatter: safe formatting by default, explicit normalization when requested.
5. LSP server: diagnostics, completion, hover, symbols, folding, formatting, code
   actions, document links, and explicit workspace commands.
6. Test runner: static, smoke, regression, and agent JSON outputs.
7. Optional workflow backends: PyABACUS, ABACUS-agent-tools, Bohrium, or
   DPDispatcher integrations behind explicit commands.

Heavy calculations must not be triggered by ordinary editing, diagnostics, or
save events. Those operations belong behind explicit commands such as
`abacus-test smoke` or future workspace commands.

