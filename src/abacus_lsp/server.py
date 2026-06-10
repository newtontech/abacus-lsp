from __future__ import annotations

from pathlib import Path
from typing import Any

from .analyzer import analyze_case
from .formatter import FormatOptions, format_file_text
from .schema import SchemaRegistry


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


def hover_text(keyword: str) -> str | None:
    item = SchemaRegistry.builtin().get(keyword)
    if item is None:
        return None
    unit = f" ({item.unit})" if item.unit else ""
    default = f" Default: {item.default}." if item.default is not None else ""
    return f"`{item.name}`: {item.type}{unit}. {item.description}{default}"


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


def format_document(filename: str, text: str, normalize: bool = False) -> str:
    return format_file_text(filename, text, FormatOptions(normalize=normalize))


def run_stdio() -> int:
    try:
        from pygls.server import LanguageServer  # type: ignore[import-not-found]
    except ImportError:
        raise SystemExit("Install abacus-lsp[lsp] to run the stdio language server") from None

    server = LanguageServer("abacus-lsp", "0.1.0")
    server.start_io()
    return 0
