# ABACUS OpenQC integration contract

OpenQC integrations should treat an ABACUS case directory as the unit of
discovery. The default files are `INPUT`, `STRU`, and `KPT`; integrations must
respect `stru_file` and `kpoint_file` when those parameters are present in
`INPUT`.

## Discovery

1. Locate `INPUT` in the submitted case directory.
2. Resolve `STRU` and `KPT` from `stru_file` and `kpoint_file`, falling back to
   the default filenames.
3. Run static diagnostics before scheduling any expensive workflow.

## Commands

OpenQC can consume deterministic diagnostics through:

```sh
abacus-lsp query-diagnostics ./case --json
abacus-test static ./case --json
abacus-lsp export-context ./case --for-agent
```

The diagnostic JSON is stable enough to use as deterministic reward evidence
for review agents. Heavy ABACUS workflows must remain an explicit execution
choice and should not be triggered by diagnostic discovery alone.
