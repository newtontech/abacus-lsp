from __future__ import annotations

from dataclasses import dataclass

from .analyzer import COMMENT_PREFIXES
from .schema import SchemaRegistry

STRU_SECTIONS = {
    "ATOMIC_SPECIES",
    "NUMERICAL_ORBITAL",
    "LATTICE_CONSTANT",
    "LATTICE_VECTORS",
    "LATTICE_PARAMETERS",
    "ATOMIC_POSITIONS",
}


@dataclass(frozen=True)
class FormatOptions:
    normalize: bool = False
    keyword_case: str = "lower"
    boolean_style: str = "numeric"


def format_file_text(filename: str, text: str, options: FormatOptions | None = None) -> str:
    options = options or FormatOptions()
    upper = filename.upper()
    if upper == "INPUT":
        return format_input_text(text, options)
    if upper == "STRU" or filename.lower().endswith(".stru"):
        return format_stru_text(text)
    if upper == "KPT" or filename.lower().endswith(".kpt"):
        return format_kpt_text(text)
    return text.rstrip() + "\n"


def format_input_text(text: str, options: FormatOptions | None = None) -> str:
    options = options or FormatOptions()
    entries, prefix, suffix = _split_input_entries(text)
    if not entries:
        return "\n".join(prefix + suffix).rstrip() + "\n"
    if options.normalize:
        entries = _normalize_input_entries(entries, options)
        prefix = ["INPUT_PARAMETERS"]
        suffix = []
    width = max(len(entry[0]) for entry in entries if not entry[0].startswith("#"))
    formatted = []
    for key, value, comment in entries:
        if key.startswith("#"):
            formatted.append(key)
            continue
        rendered_key = _case_keyword(key, options)
        base = f"{rendered_key:<{width}}  {value}".rstrip()
        if comment:
            base = f"{base}  {comment}"
        formatted.append(base)
    return "\n".join([*prefix, *formatted, *suffix]).rstrip() + "\n"


def format_stru_text(text: str) -> str:
    lines = [line.rstrip() for line in text.splitlines()]
    output: list[str] = []
    previous_was_section = False
    for line in lines:
        stripped = line.strip()
        upper = stripped.upper()
        if not stripped:
            continue
        if upper in STRU_SECTIONS:
            if output and not previous_was_section:
                output.append("")
            output.append(upper)
            previous_was_section = True
            continue
        previous_was_section = False
        parts = stripped.split()
        output.append(" ".join(parts) if parts else stripped)
    return "\n".join(output).rstrip() + "\n"


def format_kpt_text(text: str) -> str:
    output = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(COMMENT_PREFIXES):
            output.append(stripped)
        else:
            output.append(" ".join(stripped.split()))
    return "\n".join(output).rstrip() + "\n"


def _split_input_entries(text: str) -> tuple[list[tuple[str, str, str]], list[str], list[str]]:
    prefix: list[str] = []
    suffix: list[str] = []
    entries: list[tuple[str, str, str]] = []
    in_parameters = False
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if stripped.upper() == "INPUT_PARAMETERS":
            prefix.append("INPUT_PARAMETERS")
            in_parameters = True
            continue
        if not in_parameters:
            prefix.append(raw_line.rstrip())
            continue
        if not stripped or stripped.startswith(COMMENT_PREFIXES):
            suffix.append(raw_line.rstrip())
            continue
        body, sep, comment = raw_line.partition("#")
        parts = body.split(maxsplit=1)
        if not parts:
            suffix.append(raw_line.rstrip())
            continue
        key = parts[0]
        value = parts[1].strip() if len(parts) > 1 else ""
        entries.append((key, value, f"{sep}{comment}".rstrip()))
    return entries, prefix, suffix


def _normalize_input_entries(
    entries: list[tuple[str, str, str]], options: FormatOptions
) -> list[tuple[str, str, str]]:
    registry = SchemaRegistry.builtin()
    effective: dict[str, tuple[str, str, str]] = {}
    duplicates: list[tuple[str, str, str]] = []
    for key, value, comment in entries:
        normalized = key.lower()
        if normalized in effective:
            old_key, old_value, old_comment = effective[normalized]
            old = f"# duplicate ignored: {old_key} {old_value}".rstrip()
            if old_comment:
                old = f"{old} {old_comment}"
            duplicates.append((old, "", ""))
        effective[normalized] = (normalized, _normalize_value(normalized, value, options), comment)
    grouped = sorted(
        effective.values(),
        key=lambda item: (
            registry.get(item[0]).category if registry.get(item[0]) else "zzz",
            item[0],
        ),
    )
    return [*duplicates, *grouped]


def _normalize_value(key: str, value: str, options: FormatOptions) -> str:
    if options.boolean_style == "text" and value.lower() in {"1", "0", "true", "false", "t", "f"}:
        return "true" if value.lower() in {"1", "true", "t"} else "false"
    if options.boolean_style == "numeric" and value.lower() in {"true", "false", "t", "f"}:
        return "1" if value.lower() in {"true", "t"} else "0"
    return value


def _case_keyword(key: str, options: FormatOptions) -> str:
    if key.startswith("#"):
        return key
    if options.keyword_case == "upper":
        return key.upper()
    return key.lower()
