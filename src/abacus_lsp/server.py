from __future__ import annotations

from pathlib import Path
from typing import Any

from .analyzer import analyze_case, parse_input
from .formatter import FormatOptions, format_file_text
from .schema import SchemaRegistry

# ---------------------------------------------------------------------------
# Completion
# ---------------------------------------------------------------------------


def completion_items(filename: str) -> list[str]:
    upper = filename.upper()
    if upper == "INPUT":
        return SchemaRegistry.builtin().names()
    if upper == "STRU":
        return [
            "ATOMIC_SPECIES",
            "NUMERICAL_ORBITAL",
            "LATTICE_CONSTANT",
            "LATTICE_VECTORS",
            "LATTICE_PARAMETERS",
            "ATOMIC_POSITIONS",
        ]
    if upper == "KPT":
        return ["Gamma", "MP", "Direct", "Cartesian", "Line", "Line_Cartesian"]
    return []


# ---------------------------------------------------------------------------
# Hover
# ---------------------------------------------------------------------------


def hover_text(keyword: str) -> str | None:
    item = SchemaRegistry.builtin().get(keyword)
    if item is None:
        return None
    unit = f" ({item.unit})" if item.unit else ""
    default = f" Default: {item.default}." if item.default is not None else ""
    return f"`{item.name}`: {item.type}{unit}. {item.description}{default}"


# ---------------------------------------------------------------------------
# Document symbols
# ---------------------------------------------------------------------------


def document_symbols(filename: str, text: str) -> list[dict[str, Any]]:
    symbols = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", "/")):
            continue
        if filename.upper() == "INPUT" and stripped.upper() != "INPUT_PARAMETERS":
            symbols.append({"name": stripped.split()[0], "line": line_no, "kind": "parameter"})
        elif stripped.upper() in completion_items(filename):
            symbols.append({"name": stripped.upper(), "line": line_no, "kind": "section"})
    return symbols


# ---------------------------------------------------------------------------
# Folding ranges
# ---------------------------------------------------------------------------


def folding_ranges(filename: str, text: str) -> list[dict[str, int]]:
    symbols = document_symbols(filename, text)
    ranges = []
    for index, symbol in enumerate(symbols):
        if symbol["kind"] != "section":
            continue
        start = int(symbol["line"]) - 1
        end = (
            int(symbols[index + 1]["line"]) - 2
            if index + 1 < len(symbols)
            else len(text.splitlines()) - 1
        )
        if end > start:
            ranges.append({"startLine": start, "endLine": end})
    return ranges


# ---------------------------------------------------------------------------
# Code actions
# ---------------------------------------------------------------------------


def code_actions(case_dir: Path) -> list[dict[str, Any]]:
    actions = []
    for diagnostic in analyze_case(case_dir):
        if diagnostic.suggested_fix:
            actions.append(
                {
                    "title": f"Fix {diagnostic.code}: {diagnostic.message}",
                    "code": diagnostic.code,
                    "kind": diagnostic.suggested_fix.get("kind"),
                    "file": diagnostic.file,
                }
            )
    return actions


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------


def format_document(filename: str, text: str, normalize: bool = False) -> str:
    return format_file_text(filename, text, FormatOptions(normalize=normalize))


# ---------------------------------------------------------------------------
# Navigation: go-to-definition
# ---------------------------------------------------------------------------


def goto_definition(
    filename: str,
    text: str,
    line: int,
    character: int,
    case_dir: Path | None = None,
) -> list[dict[str, Any]]:
    """Return definition locations for the symbol at *line*/*character*.

    Supports:
    - INPUT keyword whose value is a file path (stru_file, kpoint_file, pseudo_dir,
      orbital_dir, read_file_dir) → locates the referenced file.
    - STRU file reference (e.g. a pseudopotential filename) → cross-links.
    - KPT file referenced from INPUT → locates the KPT file.
    """
    upper = filename.upper()
    lines = text.splitlines()
    if line < 1 or line > len(lines):
        return []
    stripped = lines[line - 1].strip()
    if not stripped or stripped.startswith(("#", "/")):
        return []

    results: list[dict[str, Any]] = []

    if upper == "INPUT":
        parts = stripped.split(maxsplit=1)
        if not parts:
            return []
        key = parts[0].lower()
        value = parts[1].strip() if len(parts) > 1 else ""
        if key in _FILE_REF_KEYS and case_dir is not None:
            target = case_dir / value
            if target.exists():
                results.append({"uri": str(target), "line": 1, "character": 1})
        elif key in _FILE_REF_KEYS and value:
            # Without case_dir, still return a symbolic reference
            results.append({"uri": value, "line": 1, "character": 1})

    elif upper == "STRU":
        # In ATOMIC_SPECIES, the 3rd column is a pseudopotential filename
        if case_dir is not None:
            input_file = parse_input(case_dir / "INPUT")
            pseudo_dir = input_file.parameters.get("pseudo_dir", "./")
            parts = stripped.split()
            if len(parts) >= 3:
                # This looks like a species line: element mass pseudo_file
                try:
                    float(parts[1])  # mass is numeric
                    target = case_dir / pseudo_dir / parts[2]
                    if target.exists():
                        results.append({"uri": str(target), "line": 1, "character": 1})
                except ValueError:
                    pass

    return results


_FILE_REF_KEYS = {"stru_file", "kpoint_file", "pseudo_dir", "orbital_dir", "read_file_dir"}


# ---------------------------------------------------------------------------
# Navigation: references
# ---------------------------------------------------------------------------


def find_references(
    filename: str,
    text: str,
    line: int,
    character: int,
    case_dir: Path | None = None,
) -> list[dict[str, Any]]:
    """Return all reference locations for the symbol at *line*/*character*.

    For INPUT keywords, find all occurrences across INPUT, STRU, and KPT.
    For STRU section names, find all section references.
    """
    upper = filename.upper()
    lines = text.splitlines()
    if line < 1 or line > len(lines):
        return []
    stripped = lines[line - 1].strip()
    if not stripped or stripped.startswith(("#", "/")):
        return []

    results: list[dict[str, Any]] = []

    if upper == "INPUT":
        parts = stripped.split()
        if not parts:
            return []
        key = parts[0].lower()
        # Find all occurrences of this keyword in the INPUT file
        for ln, ln_text in enumerate(lines, start=1):
            s = ln_text.strip()
            if s and not s.startswith(("#", "/")) and s.split()[0].lower() == key:
                results.append({"uri": filename, "line": ln, "character": 1})
        # Cross-file: if keyword is stru_file/kpoint_file, reference the file itself
        if case_dir is not None:
            if key == "stru_file":
                stru_name = parts[1].strip() if len(parts) > 1 else "STRU"
                stru_path = case_dir / stru_name
                if stru_path.exists():
                    results.append({"uri": str(stru_path), "line": 1, "character": 1})
            elif key == "kpoint_file":
                kpt_name = parts[1].strip() if len(parts) > 1 else "KPT"
                kpt_path = case_dir / kpt_name
                if kpt_path.exists():
                    results.append({"uri": str(kpt_path), "line": 1, "character": 1})

    elif upper == "STRU":
        token = stripped.split()[0].upper()
        # Find all occurrences of this section name
        for ln, ln_text in enumerate(lines, start=1):
            s = ln_text.strip().upper()
            if s == token:
                results.append({"uri": filename, "line": ln, "character": 1})

    return results


# ---------------------------------------------------------------------------
# Rename
# ---------------------------------------------------------------------------


def rename_symbol(
    filename: str,
    text: str,
    line: int,
    character: int,
    new_name: str,
) -> dict[str, Any] | None:
    """Return a workspace edit that renames the symbol at *line*/*character*.

    Supports renaming INPUT keywords.
    Returns None if rename is not supported for the symbol.
    """
    upper = filename.upper()
    lines = text.splitlines()
    if line < 1 or line > len(lines):
        return None
    stripped = lines[line - 1].strip()
    if not stripped or stripped.startswith(("#", "/")):
        return None

    if upper == "INPUT":
        parts = stripped.split()
        if not parts:
            return None
        old_key = parts[0]
        changes: dict[str, list[dict[str, Any]]] = {}
        edits: list[dict[str, Any]] = []
        for ln, ln_text in enumerate(lines, start=1):
            s = ln_text.strip()
            if s and not s.startswith(("#", "/")) and s.split()[0] == old_key:
                col = ln_text.lower().find(old_key.lower())
                if col >= 0:
                    edits.append(
                        {
                            "line": ln,
                            "startChar": col + 1,
                            "endChar": col + 1 + len(old_key),
                            "newText": new_name,
                        }
                    )
        if edits:
            changes[filename] = edits
            return {"changes": changes}

    return None


# ---------------------------------------------------------------------------
# Diagnostics (LSP publish)
# ---------------------------------------------------------------------------


def publish_diagnostics(case_dir: Path) -> dict[str, list[dict[str, Any]]]:
    """Return diagnostics grouped by file URI for LSP publishDiagnostics."""
    diagnostics = analyze_case(case_dir)
    by_file: dict[str, list[dict[str, Any]]] = {}
    for d in diagnostics:
        by_file.setdefault(d.file, []).append(d.to_json())
    return by_file


# ---------------------------------------------------------------------------
# LSP Server entry point
# ---------------------------------------------------------------------------


def run_stdio() -> int:
    try:
        server = _create_server()
    except ImportError:
        raise SystemExit("Install abacus-lsp[lsp] to run the stdio language server") from None

    _register_features(server)
    server.start_io()
    return 0


def _create_server() -> Any:
    """Create a pygls server, supporting both pygls 1.x and 2.x APIs."""
    try:
        from pygls.server import LanguageServer

        return LanguageServer("abacus-lsp", "0.1.0")
    except (ImportError, AttributeError):
        pass
    # pygls 2.x fallback
    from pygls.protocol import JsonRPCProtocol
    from pygls.server import JsonRPCServer  # type: ignore[attr-defined]

    return JsonRPCServer(protocol_cls=JsonRPCProtocol, converter_factory=None)


def _register_features(server: Any) -> None:
    """Register LSP feature handlers on a pygls server instance."""
    try:
        from lsprotocol import types as _lsp
    except ImportError:

        class _FallbackLsp:
            TEXT_DOCUMENT_COMPLETION = "textDocument/completion"
            TEXT_DOCUMENT_HOVER = "textDocument/hover"
            TEXT_DOCUMENT_DOCUMENT_SYMBOL = "textDocument/documentSymbol"
            TEXT_DOCUMENT_FOLDING_RANGE = "textDocument/foldingRange"
            TEXT_DOCUMENT_FORMATTING = "textDocument/formatting"

        lsp: Any = _FallbackLsp()
    else:
        lsp = _lsp

    @server.feature(lsp.TEXT_DOCUMENT_COMPLETION)  # type: ignore[untyped-decorator]
    def completions(params: Any) -> Any:
        uri = params.text_document.uri
        filename = _uri_to_filename(uri)
        items = completion_items(filename)
        return [lsp.CompletionItem(label=item) for item in items]

    @server.feature(lsp.TEXT_DOCUMENT_HOVER)  # type: ignore[untyped-decorator]
    def hover(params: Any) -> Any:
        uri = params.text_document.uri
        doc = server.workspace.get_text_document(uri)
        line = params.position.line
        lines = doc.source.splitlines()
        if line >= len(lines):
            return None
        stripped = lines[line].strip()
        if not stripped or stripped.startswith(("#", "/")):
            return None
        token = stripped.split()[0] if stripped else ""
        text = hover_text(token)
        if text is None:
            return None
        return lsp.Hover(contents=lsp.MarkupContent(kind=lsp.MarkupKind.Markdown, value=text))

    @server.feature(lsp.TEXT_DOCUMENT_DOCUMENT_SYMBOL)  # type: ignore[untyped-decorator]
    def symbols(params: Any) -> Any:
        uri = params.text_document.uri
        filename = _uri_to_filename(uri)
        doc = server.workspace.get_text_document(uri)
        syms = document_symbols(filename, doc.source)
        return [
            lsp.DocumentSymbol(
                name=s["name"],
                kind=(
                    lsp.SymbolKind.Field if s["kind"] == "parameter" else lsp.SymbolKind.Namespace
                ),
                range=lsp.Range(
                    start=lsp.Position(line=s["line"] - 1, character=0),
                    end=lsp.Position(line=s["line"], character=0),
                ),
                selection_range=lsp.Range(
                    start=lsp.Position(line=s["line"] - 1, character=0),
                    end=lsp.Position(line=s["line"] - 1, character=len(s["name"])),
                ),
            )
            for s in syms
        ]

    @server.feature(lsp.TEXT_DOCUMENT_FOLDING_RANGE)  # type: ignore[untyped-decorator]
    def folding(params: Any) -> Any:
        uri = params.text_document.uri
        filename = _uri_to_filename(uri)
        doc = server.workspace.get_text_document(uri)
        ranges = folding_ranges(filename, doc.source)
        return [
            lsp.FoldingRange(
                start_line=r["startLine"],
                end_line=r["endLine"],
            )
            for r in ranges
        ]

    @server.feature(lsp.TEXT_DOCUMENT_FORMATTING)  # type: ignore[untyped-decorator]
    def formatting(params: Any) -> Any:
        uri = params.text_document.uri
        filename = _uri_to_filename(uri)
        doc = server.workspace.get_text_document(uri)
        formatted = format_document(filename, doc.source)
        if formatted == doc.source:
            return []
        lines_old = doc.source.splitlines()
        return [
            lsp.TextEdit(
                range=lsp.Range(
                    start=lsp.Position(line=0, character=0),
                    end=lsp.Position(line=len(lines_old), character=0),
                ),
                new_text=formatted,
            )
        ]


def _uri_to_filename(uri: str) -> str:
    """Extract filename from a file URI."""
    if "://" in uri:
        path = uri.split("://", 1)[1]
        # Remove authority (e.g. host) if present
        if "/" in path:
            path = path[path.index("/") :]
        from urllib.parse import unquote

        path = unquote(path)
        return Path(path).name
    return Path(uri).name
