"""Safe and normalize formatters for ABACUS input files (issues #9, #10)."""
from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass

COMMENT_PREFIXES = ("#", "/")

# ---------------------------------------------------------------------------
# INPUT keyword categories for normalize mode (issue #10)
# ---------------------------------------------------------------------------

INPUT_CATEGORIES: list[tuple[str, list[str]]] = [
    ("Calculation Control", [
        "calculation", "suffix", "esolver_type", "nbands", "nupdown",
        "ntype", "nspin", "nelec", "nelec_delta", "lmaxmax",
    ]),
    ("Planewave Basis", [
        "ecutwfc", "ecutrho", "pw_diag_thr", "pw_diag_nmax",
        "gamma_only", "gamma_only_local",
    ]),
    ("Numerical Atomic Orbitals", [
        "basis_type", "lcao_ecut", "lcao_dk", "lcao_dr", "lcao_rmax",
        "lmax", "lmaxall", "search_radius", "search_pbc",
    ]),
    ("K-points", [
        "kpoint_file", "kpar", "kspacing", "nupdown",
    ]),
    ("SCF", [
        "scf_thr", "scf_thr_type", "scf_nmax", "dft_plus_u",
        "charge_extrap", "out_mul", "symmetry", "init_chg",
        "chg_extrap", "efield_flag", "dip_cor_flag",
    ]),
    ("Structure", [
        "stru_file", "latname", "cell_factor",
    ]),
    ("Files and Paths", [
        "pseudo_dir", "orbital_dir", "read_file_dir",
    ]),
    ("Output", [
        "out_band", "out_dos", "out_stru", "out_chg", "out_pot",
        "out_wfc_pw", "out_wfc_r", "out_cube", "out_alllog",
        "out_app_flag", "out_ndigits", "out_level",
    ]),
    ("Smearing", [
        "smearing_method", "smearing_sigma", "smearing_temp",
    ]),
    ("Charge Mixing", [
        "mixing_type", "mixing_beta", "mixing_ndim", "mixing_gg0",
        "mixing_gg0_coef", "mixing_tau", "mixing_dftu",
    ]),
    ("Relaxation", [
        "force_thr", "force_thr_ev", "relax_method", "relax_bfgs_w1",
        "relax_bfgs_w2", "relax_cg_beta", "bfgs_w1", "bfgs_w2",
        "cal_force", "relax_new", "out_level", "fixed_axes", "fixed_ibrav",
        "fixed_atoms",
    ]),
    ("Molecular Dynamics", [
        "md_type", "md_nstep", "md_dt", "md_tauthermo", "md_taubaro",
        "md_restart", "md_enssolver", "md_thermostat", "md_temp",
        "md_press", "md_pmode", "md_pcouple",
    ]),
]

# Build reverse map: keyword -> category index
_KEYWORD_TO_CATEGORY: dict[str, int] = {}
for _idx, (_cat_name, _keywords) in enumerate(INPUT_CATEGORIES):
    for _kw in _keywords:
        if _kw not in _KEYWORD_TO_CATEGORY:
            _KEYWORD_TO_CATEGORY[_kw] = _idx

# Category names by index
_CATEGORY_NAMES = [name for name, _ in INPUT_CATEGORIES]

# Boolean value sets
_TRUE_VALUES = frozenset({"1", "true", "t", "yes", "on"})
_FALSE_VALUES = frozenset({"0", "false", "f", "no", "off"})
_BOOLEAN_VALUES = _TRUE_VALUES | _FALSE_VALUES

DUP_MARKER = "# [dup]"


@dataclass(frozen=True)
class FormatOptions:
    normalize: bool = False
    keyword_case: str = "lower"
    boolean_style: str = "keep"


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


@dataclass
class _InputLine:
    """Parsed line in an INPUT file."""
    kind: str  # "pre_header", "header", "blank", "comment", "entry", "dup_marker"
    raw: str
    key: str = ""
    value: str = ""
    inline_comment: str = ""  # includes leading "#" or "/"


def _is_boolean(value: str) -> bool:
    return value.lower() in _BOOLEAN_VALUES


def _normalize_boolean(value: str, style: str) -> str:
    if style == "keep":
        return value
    is_true = value.lower() in _TRUE_VALUES
    if style == "1/0":
        return "1" if is_true else "0"
    elif style == "true/false":
        return "true" if is_true else "false"
    elif style == "t/f":
        return "t" if is_true else "f"
    elif style == "yes/no":
        return "yes" if is_true else "no"
    return value


def _detect_file_type(filename: str) -> str:
    """Detect ABACUS file type from filename."""
    name = filename.upper()
    if name == "INPUT":
        return "input"
    elif name == "STRU":
        return "stru"
    elif name in ("KPT", "KPOINTS"):
        return "kpt"
    else:
        # Default to kpt for unknown files
        return "kpt"


# ---------------------------------------------------------------------------
# INPUT parsing helpers
# ---------------------------------------------------------------------------


def _parse_input_lines(text: str) -> list[_InputLine]:
    """Parse INPUT file text into structured lines."""
    lines = text.splitlines()
    result: list[_InputLine] = []
    saw_header = False

    for raw_line in lines:
        stripped = raw_line.strip()

        if not saw_header:
            if stripped.upper() == "INPUT_PARAMETERS":
                result.append(_InputLine(kind="header", raw=raw_line))
                saw_header = True
            else:
                result.append(_InputLine(kind="pre_header", raw=raw_line))
            continue

        if not stripped:
            result.append(_InputLine(kind="blank", raw=raw_line))
            continue

        if stripped.startswith(COMMENT_PREFIXES):
            # Check for dup marker
            if stripped.startswith(DUP_MARKER):
                rest = stripped[len(DUP_MARKER):].strip()
                parts = rest.split(maxsplit=1)
                if parts:
                    key = parts[0]
                    value = parts[1] if len(parts) > 1 else ""
                    result.append(_InputLine(
                        kind="dup_marker", raw=raw_line,
                        key=key, value=value,
                    ))
                    continue
            result.append(_InputLine(kind="comment", raw=raw_line))
            continue

        # Key-value entry: only split on "#" for inline comments
        # (not "/" since it appears in file paths)
        body, sep, comment = stripped.partition("#")
        parts = body.split(maxsplit=1)
        if not parts:
            result.append(_InputLine(kind="comment", raw=raw_line))
            continue

        key = parts[0]
        value = parts[1].strip() if len(parts) > 1 else ""
        inline_comment = f"{sep}{comment}" if sep else ""

        result.append(_InputLine(
            kind="entry", raw=raw_line,
            key=key, value=value, inline_comment=inline_comment,
        ))

    return result


# ---------------------------------------------------------------------------
# Safe formatters (issue #9)
# ---------------------------------------------------------------------------


def safe_format_input(text: str) -> str:
    """Safe formatter for INPUT files.

    Preserves order, comments, duplicate parameters, and trailing newline.
    Aligns keyword/value/comment columns.
    Idempotent.
    """
    parsed = _parse_input_lines(text)

    # Find all entries to determine column widths
    entries = [line for line in parsed if line.kind == "entry"]

    if not entries:
        # No entries: just normalize trailing whitespace and ensure newline
        return "\n".join(line.raw.rstrip() for line in parsed).rstrip() + "\n"

    max_key_len = max(len(e.key) for e in entries)
    # Only consider values from entries that have inline comments
    # for comment column alignment
    max_val_len = max(
        (len(e.value) for e in entries if e.inline_comment),
        default=0,
    )

    # Build output
    formatted: list[str] = []
    for line in parsed:
        if line.kind == "entry":
            if line.inline_comment and max_val_len > 0:
                formatted.append(
                    f"{line.key:<{max_key_len}}  {line.value:<{max_val_len}}  "
                    f"{line.inline_comment}".rstrip()
                )
            else:
                formatted.append(
                    f"{line.key:<{max_key_len}}  {line.value}".rstrip()
                )
        elif line.kind == "header":
            formatted.append("INPUT_PARAMETERS")
        else:
            formatted.append(line.raw.rstrip())

    return "\n".join(formatted).rstrip() + "\n"


def safe_format_stru(text: str) -> str:
    """Safe formatter for STRU files.

    Preserves section order, comments, and trailing newline.
    Normalizes internal whitespace in data lines.
    Idempotent.
    """
    lines = text.splitlines()
    formatted: list[str] = []
    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped:
            formatted.append("")
            continue
        if stripped.startswith(COMMENT_PREFIXES):
            formatted.append(stripped)
            continue
        # Data line: normalize internal whitespace
        parts = stripped.split()
        formatted.append(" ".join(parts))

    return "\n".join(formatted).rstrip() + "\n"


def safe_format_kpt(text: str) -> str:
    """Safe formatter for KPT files.

    Preserves content and comments.
    Normalizes internal whitespace in data lines.
    Idempotent.
    """
    lines = text.splitlines()
    formatted: list[str] = []
    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped:
            formatted.append("")
            continue
        if stripped.startswith(COMMENT_PREFIXES):
            formatted.append(stripped)
            continue
        # Data line: normalize internal whitespace
        parts = stripped.split()
        formatted.append(" ".join(parts))

    return "\n".join(formatted).rstrip() + "\n"


# ---------------------------------------------------------------------------
# Normalize formatters (issue #10)
# ---------------------------------------------------------------------------


def normalize_format_input(
    text: str,
    *,
    keyword_case: str = "lower",
    bool_style: str = "keep",
) -> str:
    """Normalize formatter for INPUT files.

    Groups keywords by category, comments out earlier duplicate values,
    supports configurable keyword casing and boolean style.
    Never the default behavior.
    Idempotent.
    """
    parsed = _parse_input_lines(text)

    # Collect active entries and dup markers
    entries: list[_InputLine] = []
    dup_markers: list[_InputLine] = []

    for line in parsed:
        if line.kind == "entry":
            entries.append(line)
        elif line.kind == "dup_marker":
            dup_markers.append(line)

    if not entries:
        return "INPUT_PARAMETERS\n"

    # Handle active duplicates: keep only the last value for each key
    seen: dict[str, int] = {}  # key -> index in final_entries
    final_entries: list[_InputLine] = []
    new_dups: list[_InputLine] = list(dup_markers)

    for entry in entries:
        if entry.key in seen:
            # Convert earlier entry to dup marker
            old = final_entries[seen[entry.key]]
            new_dups.append(_InputLine(
                kind="dup_marker", raw="",
                key=old.key, value=old.value,
            ))
            # Replace with the later entry
            final_entries[seen[entry.key]] = entry
        else:
            seen[entry.key] = len(final_entries)
            final_entries.append(entry)

    # Group by category (preserve original order within each category)
    category_entries: OrderedDict[int, list[_InputLine]] = OrderedDict()
    other_entries: list[_InputLine] = []

    for entry in final_entries:
        cat_idx = _KEYWORD_TO_CATEGORY.get(entry.key.lower())
        if cat_idx is not None:
            if cat_idx not in category_entries:
                category_entries[cat_idx] = []
            category_entries[cat_idx].append(entry)
        else:
            other_entries.append(entry)

    # Sort categories by their defined order
    sorted_cats = sorted(category_entries.items())

    # Collect all entries for column alignment
    all_norm_entries: list[_InputLine] = []
    for _, cat_entries in sorted_cats:
        all_norm_entries.extend(cat_entries)
    if other_entries:
        all_norm_entries.extend(other_entries)

    # Determine column widths
    max_key_len = max(len(e.key) for e in all_norm_entries)

    # Group dup markers by key
    dups_by_key: dict[str, list[str]] = {}
    for d in new_dups:
        dups_by_key.setdefault(d.key, []).append(d.value)

    # Build output
    output_lines: list[str] = ["INPUT_PARAMETERS"]

    for cat_idx, cat_entries in sorted_cats:
        output_lines.append("")
        output_lines.append(f"# --- {_CATEGORY_NAMES[cat_idx]} ---")
        for entry in cat_entries:
            # Add dup markers before active entry
            for dup_val in dups_by_key.get(entry.key, []):
                output_lines.append(f"{DUP_MARKER} {entry.key} {dup_val}")
            # Remove from dups_by_key so they're not output again
            if entry.key in dups_by_key:
                del dups_by_key[entry.key]

            # Normalize keyword case
            nkey = entry.key
            if keyword_case == "lower":
                nkey = entry.key.lower()
            elif keyword_case == "upper":
                nkey = entry.key.upper()
            # else "keep"

            # Normalize boolean
            nvalue = entry.value
            if bool_style != "keep" and _is_boolean(entry.value):
                nvalue = _normalize_boolean(entry.value, bool_style)

            output_lines.append(f"{nkey:<{max_key_len}}  {nvalue}")

    # Other category
    if other_entries:
        output_lines.append("")
        output_lines.append("# --- Other ---")
        for entry in other_entries:
            for dup_val in dups_by_key.get(entry.key, []):
                output_lines.append(f"{DUP_MARKER} {entry.key} {dup_val}")
            if entry.key in dups_by_key:
                del dups_by_key[entry.key]

            nkey = entry.key
            if keyword_case == "lower":
                nkey = entry.key.lower()
            elif keyword_case == "upper":
                nkey = entry.key.upper()

            nvalue = entry.value
            if bool_style != "keep" and _is_boolean(entry.value):
                nvalue = _normalize_boolean(entry.value, bool_style)

            output_lines.append(f"{nkey:<{max_key_len}}  {nvalue}")

    return "\n".join(output_lines).rstrip() + "\n"


def normalize_format_stru(text: str) -> str:
    """Normalize formatter for STRU files.

    Ensures blank lines between sections.
    Idempotent.
    """
    lines = text.splitlines()
    formatted: list[str] = []
    KNOWN_SECTIONS = {
        "ATOMIC_SPECIES", "NUMERICAL_ORBITAL", "LATTICE_CONSTANT",
        "LATTICE_VECTORS", "LATTICE_PARAMETERS", "ATOMIC_POSITIONS",
    }

    prev_was_section = False
    for raw_line in lines:
        stripped = raw_line.strip()
        is_section = stripped.upper() in KNOWN_SECTIONS

        if is_section and formatted and prev_was_section is False:
            # Ensure blank line before section (but not if we just had one)
            if formatted and formatted[-1] != "":
                formatted.append("")

        if not stripped:
            formatted.append("")
        elif stripped.startswith(COMMENT_PREFIXES):
            formatted.append(stripped)
        else:
            parts = stripped.split()
            formatted.append(" ".join(parts))

        prev_was_section = is_section or (not stripped and prev_was_section)

    return "\n".join(formatted).rstrip() + "\n"


def normalize_format_kpt(text: str) -> str:
    """Normalize formatter for KPT files. Same as safe for now."""
    return safe_format_kpt(text)


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------


def format_file(
    text: str,
    filename: str,
    *,
    normalize: bool = False,
    keyword_case: str = "lower",
    bool_style: str = "keep",
) -> str:
    """Format file content based on file type and mode."""
    ft = _detect_file_type(filename)
    if normalize:
        if ft == "input":
            return normalize_format_input(text, keyword_case=keyword_case, bool_style=bool_style)
        elif ft == "stru":
            return normalize_format_stru(text)
        else:
            return normalize_format_kpt(text)
    else:
        if ft == "input":
            return safe_format_input(text)
        elif ft == "stru":
            return safe_format_stru(text)
        else:
            return safe_format_kpt(text)


def format_file_text(filename: str, text: str, options: FormatOptions | None = None) -> str:
    options = options or FormatOptions()
    return format_file(
        text,
        filename,
        normalize=options.normalize,
        keyword_case=options.keyword_case,
        bool_style=_bool_style_for_worker(options.boolean_style),
    )


def format_input_text(text: str, options: FormatOptions | None = None) -> str:
    return format_file_text("INPUT", text, options)


def format_stru_text(text: str) -> str:
    return safe_format_stru(text)


def format_kpt_text(text: str) -> str:
    return safe_format_kpt(text)


def _bool_style_for_worker(style: str) -> str:
    if style == "numeric":
        return "1/0"
    if style == "text":
        return "true/false"
    return style
