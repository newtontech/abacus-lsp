#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Issue:
    title: str
    milestone: str
    labels: tuple[str, ...]
    body: str


MILESTONES = {
    "Milestone 0: Research and Schema": "ABACUS keyword metadata, schemas, and fixtures.",
    "Milestone 1: Parser": "Loss-aware INPUT, STRU, and KPT parsing.",
    "Milestone 2: Linter": "Syntax, schema, cross-file, and workflow diagnostics.",
    "Milestone 3: Formatter": "Safe and normalized formatting modes.",
    "Milestone 4: LSP": "Editor-facing language server features.",
    "Milestone 5: Test Runner and Agent Interfaces": "Static/smoke/regression tests and agent JSON protocol.",
}

LABELS = {
    "roadmap": ("6f42c1", "Imported from the initial ABACUS LSP roadmap."),
    "schema": ("0052cc", "Schema and metadata work."),
    "fixtures": ("0e8a16", "Test fixture and corpus work."),
    "parser": ("1d76db", "Parser and source mapping work."),
    "linter": ("d93f0b", "Diagnostics and lint rules."),
    "formatter": ("fbca04", "Formatting work."),
    "lsp": ("5319e7", "Language Server Protocol features."),
    "test-runner": ("c2e0c6", "Static, smoke, and regression test commands."),
    "agent": ("bfdadc", "Agent-facing JSON and deterministic feedback."),
    "optional-backend": ("ededed", "Optional integration with external workflow backends."),
}


ISSUES = [
    Issue(
        title="Create ABACUS input schema generator",
        milestone="Milestone 0: Research and Schema",
        labels=("roadmap", "schema"),
        body="""## Problem

ABACUS `INPUT` has many versioned keywords. Handwritten metadata will drift and will not be enough for hover, completion, type checks, or agent diagnostics.

## Scope

- Build `abacus-schema build`.
- Collect keyword name, type, unit, default, category, description, availability, enum, and source.
- Support bundled static schemas, runtime refresh from local `abacus -h` / `abacus -s`, and project overrides in `.abacus-lsp/schema.override.json`.
- Emit `schemas/abacus-<version>.json`.

## Acceptance criteria

- Schema generation is deterministic for the same ABACUS binary/docs input.
- Generated schema can power unknown-keyword, type, enum, hover, and completion metadata.
- Source provenance is recorded per keyword.
""",
    ),
    Issue(
        title="Create ABACUS fixture corpus",
        milestone="Milestone 0: Research and Schema",
        labels=("roadmap", "fixtures"),
        body="""## Problem

Parser, formatter, linter, LSP, and test-runner behavior needs stable fixtures before feature work scales.

## Scope

- Add official or minimal MgO, Si, and H2O-style cases.
- Cover `INPUT`, `STRU`, and `KPT`.
- Include KPT auto mesh, explicit points, and band line mode.
- Include negative fixtures for malformed input.

## Acceptance criteria

- Fixtures are small enough for CI.
- Every fixture has expected diagnostics or expected no-diagnostic snapshots.
- Heavy ABACUS execution is opt-in and not required for ordinary PR checks.
""",
    ),
    Issue(
        title="Implement INPUT parser",
        milestone="Milestone 1: Parser",
        labels=("roadmap", "parser"),
        body="""## Problem

`INPUT` needs a parser that preserves enough source information for diagnostics, formatting, code actions, and agent output.

## Scope

- Recognize `INPUT_PARAMETERS`.
- Ignore preamble before the header.
- Support comment lines beginning with `#` or `/`.
- Parse one parameter per line.
- Preserve source ranges, comments, original text, duplicate keys, and final effective value.
- Treat parameter names case-insensitively.

## Acceptance criteria

- Parser returns CST/AST-style structures with line and column ranges.
- Duplicate parameters are represented without losing earlier definitions.
- Parser does not crash on partial edits or malformed lines.
""",
    ),
    Issue(
        title="Implement STRU parser",
        milestone="Milestone 1: Parser",
        labels=("roadmap", "parser"),
        body="""## Problem

`STRU` is section-based and includes nested `ATOMIC_POSITIONS` element blocks that require a state machine rather than simple key-value parsing.

## Scope

- Parse `ATOMIC_SPECIES`, `NUMERICAL_ORBITAL`, `LATTICE_CONSTANT`, `LATTICE_VECTORS`, `LATTICE_PARAMETERS`, and `ATOMIC_POSITIONS`.
- Track section ranges and source text.
- Parse element label, magnetization line, atom count, and coordinate rows inside `ATOMIC_POSITIONS`.
- Preserve pseudopotential and orbital filenames.

## Acceptance criteria

- Atom-count mismatches are detectable from the parse result.
- Section order and missing-block diagnostics have enough location data.
- Partial or malformed `ATOMIC_POSITIONS` blocks produce diagnostics instead of crashes.
""",
    ),
    Issue(
        title="Implement KPT parser",
        milestone="Milestone 1: Parser",
        labels=("roadmap", "parser"),
        body="""## Problem

K-point files have multiple modes and count conventions that should be validated consistently.

## Scope

- Accept `K_POINTS`, `KPOINTS`, or `K`.
- Parse automatic mesh, explicit `Direct` / `Cartesian`, `Line`, and `Line_Cartesian` forms.
- Preserve point rows, weights, path counts, and source ranges.

## Acceptance criteria

- Point-count and row-count mismatches are reported.
- Unknown modes produce precise diagnostics.
- The parser supports both complete files and half-written editor buffers.
""",
    ),
    Issue(
        title="Implement syntax and schema diagnostics",
        milestone="Milestone 2: Linter",
        labels=("roadmap", "linter", "schema"),
        body="""## Problem

Users and agents need immediate deterministic feedback for syntax mistakes and schema mismatches.

## Scope

- Implement diagnostics for missing `INPUT_PARAMETERS`, unknown keywords, invalid value types, malformed STRU sections, KPT count mismatch, and atom count mismatch.
- Add schema-backed checks for numeric, boolean, enum, and keyword spelling.
- Include ABACUS-style fuzzy suggestions where available.

## Acceptance criteria

- Diagnostics have stable codes such as `ABACUS001` and `ABACUS101`.
- Diagnostics include severity, message, file, range, and machine-readable metadata.
- Snapshot tests cover positive and negative fixtures.
""",
    ),
    Issue(
        title="Implement cross-file diagnostics",
        milestone="Milestone 2: Linter",
        labels=("roadmap", "linter"),
        body="""## Problem

Many ABACUS failures come from relationships between `INPUT`, `STRU`, `KPT`, and referenced files, not from a single file in isolation.

## Scope

- Check `stru_file` and `kpoint_file` existence.
- Check `pseudo_dir` plus pseudopotential filenames.
- Check `orbital_dir` plus numerical orbital filenames.
- Check `basis_type=lcao` requires `NUMERICAL_ORBITAL`.
- Check orbital/species/position ordering.
- Check `latname` conflicts with `LATTICE_VECTORS`.
- Check `gamma_only=1` will override multi-k KPT files.

## Acceptance criteria

- Cross-file diagnostics work from a case directory.
- Missing files include resolved path evidence.
- Each diagnostic includes suggested fix metadata where feasible.
""",
    ),
    Issue(
        title="Implement physics and workflow lint rules",
        milestone="Milestone 2: Linter",
        labels=("roadmap", "linter"),
        body="""## Problem

ABACUS inputs can be syntactically valid while still encoding likely workflow mistakes.

## Scope

- Add non-blocking checks for suspicious `scf_thr`, relax/cell-relax output settings, spin-orbit/noncollinear combinations, DFT+U completeness, band/DOS KPT modes, smearing values, and MD settings.
- Split severity into error, warning, info, and hint.
- Keep physics/workflow rules configurable so they do not become noisy.

## Acceptance criteria

- Rules are documented with rationale and examples.
- Defaults are conservative.
- Users can suppress or downgrade noisy rules.
""",
    ),
    Issue(
        title="Implement safe formatter",
        milestone="Milestone 3: Formatter",
        labels=("roadmap", "formatter"),
        body="""## Problem

Formatting should improve readability without changing ABACUS semantics.

## Scope

- Preserve parameter and section order.
- Preserve comments.
- Preserve duplicate parameters while warning that the last value wins.
- Align keyword/value/comment columns.
- Normalize spacing and section blank lines.
- Ensure trailing newline.

## Acceptance criteria

- Formatting is idempotent.
- Safe mode never removes data or reorders effective semantics.
- Tests cover `INPUT`, `STRU`, and `KPT`.
""",
    ),
    Issue(
        title="Implement normalize formatter",
        milestone="Milestone 3: Formatter",
        labels=("roadmap", "formatter"),
        body="""## Problem

Some users need canonical project style that may reorder presentation or collapse duplicate definitions, but this must be explicit.

## Scope

- Add `abacus-fmt --normalize`.
- Group `INPUT` keywords by official category.
- Optionally keep only the final effective duplicate value and turn previous definitions into comments.
- Support configurable keyword casing and boolean style.

## Acceptance criteria

- Normalize mode is never the default.
- Output is idempotent.
- Semantic changes are documented in a preview or diff-friendly form.
""",
    ),
    Issue(
        title="Implement LSP server MVP",
        milestone="Milestone 4: LSP",
        labels=("roadmap", "lsp"),
        body="""## Problem

The project needs an editor-facing language server that exposes the parser, schema, linter, and formatter capabilities.

## Scope

- Implement `abacus-lsp --stdio`.
- Publish diagnostics for `INPUT`, `STRU`, and `KPT`.
- Add completion for `INPUT` keywords, enum values, file paths, STRU sections, and KPT modes.
- Add hover metadata from schema.
- Add document symbols and folding ranges.

## Acceptance criteria

- The server follows LSP JSON-RPC lifecycle expectations.
- Tests cover initialization, didOpen/didChange diagnostics, hover, completion, symbols, and folding.
- The server does not crash on malformed or partial documents.
""",
    ),
    Issue(
        title="Implement code actions",
        milestone="Milestone 4: LSP",
        labels=("roadmap", "lsp"),
        body="""## Problem

Many ABACUS diagnostics can be repaired mechanically and should expose quick fixes for editors and agents.

## Scope

- Quick-fix keyword typos.
- Insert missing `NUMERICAL_ORBITAL` section skeletons.
- Fix KPT point counts where unambiguous.
- Convert duplicate parameter definitions into comments or keep only the effective value in normalize mode.
- Surface suggested fixes from diagnostic metadata.

## Acceptance criteria

- Each code action is tied to a diagnostic code.
- Ambiguous fixes are offered as commands or hints, not applied silently.
- Edits preserve comments and unrelated file contents.
""",
    ),
    Issue(
        title="Implement formatting provider",
        milestone="Milestone 4: LSP",
        labels=("roadmap", "lsp", "formatter"),
        body="""## Problem

Editor users need document and range formatting wired to the same formatter as the CLI.

## Scope

- Implement `textDocument/formatting`.
- Implement `textDocument/rangeFormatting` where safe.
- Reuse safe formatter by default.
- Expose normalize formatting only through an explicit command or setting.

## Acceptance criteria

- LSP formatting output matches `abacus-fmt`.
- Range formatting does not corrupt multi-line STRU or KPT constructs.
- Formatter tests include CLI/LSP parity.
""",
    ),
    Issue(
        title="Implement abacus-test static, smoke, and regression",
        milestone="Milestone 5: Test Runner and Agent Interfaces",
        labels=("roadmap", "test-runner"),
        body="""## Problem

The project needs command-line checks that agents and CI can use without coupling normal editing to real ABACUS runs.

## Scope

- `abacus-test static ./case`: parse, schema-check, cross-file-check, and emit JSON/SARIF/GitHub annotations.
- `abacus-test smoke ./case --timeout 120 --nprocs 1`: run a tiny ABACUS job through PyABACUS, subprocess, or optional backend.
- `abacus-test regression tests/fixtures --expect energy.json --tolerance ...`: compare converged results with tolerances.

## Acceptance criteria

- Static tests require no ABACUS binary.
- Smoke and regression are opt-in.
- Outputs are deterministic and suitable for CI annotations.
""",
    ),
    Issue(
        title="Implement agent JSON protocol",
        milestone="Milestone 5: Test Runner and Agent Interfaces",
        labels=("roadmap", "agent"),
        body="""## Problem

Coding agents need compact, structured outputs rather than editor-oriented prose.

## Scope

- Add `abacus-lsp query-diagnostics ./case --json`.
- Add `abacus-lsp explain-diagnostic ABACUS205 --json`.
- Add `abacus-lsp apply-fix ./case --code ABACUS205`.
- Add `abacus-lsp export-context ./case --for-agent`.
- Emit `.abacus-lsp/context.json`, diagnostics, schema-used, and files-index artifacts.

## Acceptance criteria

- Agent JSON includes `ok`, `blocking_errors`, `next_action`, and structured suggested fixes.
- Outputs avoid nondeterministic wording.
- CLI exits distinguish blocking errors from warnings.
""",
    ),
    Issue(
        title="Integrate ABACUS-agent-tools as optional backend",
        milestone="Milestone 5: Test Runner and Agent Interfaces",
        labels=("roadmap", "agent", "optional-backend"),
        body="""## Problem

ABACUS-agent-tools already owns input preparation, workflow execution, and domain workflows. `abacus-lsp` should reuse it without making it a core dependency.

## Scope

- Add optional backend discovery for ABACUS-agent-tools.
- Expose explicit commands for prepare input, modify input, run SCF, relax, band, DOS, and related workflows.
- Keep backend commands out of ordinary diagnostics and formatting.
- Document how PyABACUS, subprocess, ABACUS-agent-tools, Bohrium, or DPDispatcher are selected.

## Acceptance criteria

- Installing `abacus-lsp` alone does not install or require ABACUS-agent-tools.
- Missing backend produces actionable errors.
- Heavy or remote workflows require explicit user command invocation.
""",
    ),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default="newtontech/abacus-lsp")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        for issue in ISSUES:
            print(f"[dry-run] {issue.milestone}: {issue.title}")
        return 0

    ensure_labels(args.repo)
    ensure_milestones(args.repo)
    existing_titles = set(read_existing_issue_titles(args.repo))
    created: list[str] = []
    skipped: list[str] = []

    for issue in ISSUES:
        if issue.title in existing_titles:
            skipped.append(issue.title)
            continue
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as body_file:
            body_file.write(issue.body.rstrip() + "\n")
            body_path = Path(body_file.name)
        try:
            cmd = [
                "gh",
                "issue",
                "create",
                "--repo",
                args.repo,
                "--title",
                issue.title,
                "--body-file",
                str(body_path),
                "--milestone",
                issue.milestone,
            ]
            for label in issue.labels:
                cmd.extend(["--label", label])
            result = subprocess.run(cmd, check=True, text=True, capture_output=True)
            created.append(result.stdout.strip())
        finally:
            body_path.unlink(missing_ok=True)

    for url in created:
        print(f"created {url}")
    for title in skipped:
        print(f"skipped existing issue: {title}")
    return 0


def ensure_labels(repo: str) -> None:
    for label, (color, description) in LABELS.items():
        subprocess.run(
            [
                "gh",
                "label",
                "create",
                label,
                "--repo",
                repo,
                "--color",
                color,
                "--description",
                description,
                "--force",
            ],
            check=True,
        )


def ensure_milestones(repo: str) -> None:
    existing = subprocess.run(
        ["gh", "api", f"repos/{repo}/milestones", "--paginate", "--jq", ".[].title"],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.splitlines()
    for title, description in MILESTONES.items():
        if title in existing:
            continue
        subprocess.run(
            [
                "gh",
                "api",
                f"repos/{repo}/milestones",
                "-f",
                f"title={title}",
                "-f",
                f"description={description}",
            ],
            check=True,
        )


def read_existing_issue_titles(repo: str) -> list[str]:
    result = subprocess.run(
        [
            "gh",
            "issue",
            "list",
            "--repo",
            repo,
            "--state",
            "all",
            "--limit",
            "200",
            "--json",
            "title",
            "--jq",
            ".[].title",
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout.splitlines()


if __name__ == "__main__":
    raise SystemExit(main())

