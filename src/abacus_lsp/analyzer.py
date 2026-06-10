from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .diagnostics import Diagnostic

COMMENT_PREFIXES = ("#", "/")

KNOWN_INPUT_KEYWORDS = {
    "basis_type",
    "calculation",
    "dft_plus_u",
    "ecutwfc",
    "gamma_only",
    "kpoint_file",
    "latname",
    "nspin",
    "orbital_dir",
    "out_band",
    "out_dos",
    "pseudo_dir",
    "scf_thr",
    "stru_file",
    "suffix",
}

KNOWN_KPT_MODES = {"gamma", "mp", "direct", "cartesian", "line", "line_cartesian"}
KNOWN_STRU_SECTIONS = {
    "ATOMIC_SPECIES",
    "NUMERICAL_ORBITAL",
    "LATTICE_CONSTANT",
    "LATTICE_VECTORS",
    "LATTICE_PARAMETERS",
    "ATOMIC_POSITIONS",
}


@dataclass
class InputFile:
    path: Path
    parameters: dict[str, str] = field(default_factory=dict)
    parameter_lines: dict[str, list[int]] = field(default_factory=dict)
    diagnostics: list[Diagnostic] = field(default_factory=list)


@dataclass
class StruFile:
    path: Path
    sections: set[str] = field(default_factory=set)
    species: list[str] = field(default_factory=list)
    pseudopotentials: list[str] = field(default_factory=list)
    orbitals: list[str] = field(default_factory=list)
    position_elements: list[str] = field(default_factory=list)
    diagnostics: list[Diagnostic] = field(default_factory=list)


@dataclass
class KptFile:
    path: Path
    mode: str | None = None
    diagnostics: list[Diagnostic] = field(default_factory=list)


def analyze_case(case_dir: Path) -> list[Diagnostic]:
    case_dir = case_dir.resolve()
    input_file = parse_input(case_dir / "INPUT")
    stru_name = input_file.parameters.get("stru_file", "STRU")
    kpt_name = input_file.parameters.get("kpoint_file", "KPT")
    stru_file = parse_stru(case_dir / stru_name)
    kpt_file = parse_kpt(case_dir / kpt_name)

    diagnostics = [
        *input_file.diagnostics,
        *stru_file.diagnostics,
        *kpt_file.diagnostics,
    ]
    diagnostics.extend(_cross_file_diagnostics(input_file, stru_file, kpt_file, case_dir))
    return sorted(diagnostics, key=lambda item: (item.file, item.line, item.code))


def parse_input(path: Path) -> InputFile:
    result = InputFile(path=path)
    if not path.exists():
        result.diagnostics.append(
            Diagnostic("ABACUS201", "error", "INPUT file is missing", str(path), 1)
        )
        return result

    saw_header = False
    for line_no, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith(COMMENT_PREFIXES):
            continue
        if not saw_header:
            if stripped.upper() == "INPUT_PARAMETERS":
                saw_header = True
                continue
            continue
        token = stripped.split()[0].lower()
        value = stripped.split(maxsplit=1)[1] if len(stripped.split(maxsplit=1)) > 1 else ""
        result.parameter_lines.setdefault(token, []).append(line_no)
        result.parameters[token] = value
        if token not in KNOWN_INPUT_KEYWORDS:
            result.diagnostics.append(
                Diagnostic(
                    "ABACUS002",
                    "warning",
                    f"unknown INPUT keyword: {token}",
                    str(path),
                    line_no,
                    suggested_fix={"kind": "check_keyword_spelling", "keyword": token},
                    confidence=0.75,
                )
            )

    if not saw_header:
        result.diagnostics.append(
            Diagnostic("ABACUS001", "error", "INPUT_PARAMETERS header is missing", str(path), 1)
        )

    for keyword, lines in result.parameter_lines.items():
        if len(lines) > 1:
            result.diagnostics.append(
                Diagnostic(
                    "ABACUS007",
                    "warning",
                    f"{keyword} is repeated; ABACUS uses the last value",
                    str(path),
                    lines[-1],
                    evidence=[f"previous definitions on lines {', '.join(map(str, lines[:-1]))}"],
                )
            )
    return result


def parse_stru(path: Path) -> StruFile:
    result = StruFile(path=path)
    if not path.exists():
        result.diagnostics.append(
            Diagnostic("ABACUS201", "error", "STRU file is missing", str(path), 1)
        )
        return result

    lines = path.read_text(encoding="utf-8").splitlines()
    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        upper = stripped.upper()
        if not stripped or stripped.startswith(COMMENT_PREFIXES):
            index += 1
            continue
        if upper in KNOWN_STRU_SECTIONS:
            result.sections.add(upper)
            if upper == "ATOMIC_SPECIES":
                index = _parse_species(lines, index + 1, result)
                continue
            if upper == "NUMERICAL_ORBITAL":
                index = _parse_orbitals(lines, index + 1, result)
                continue
            if upper == "ATOMIC_POSITIONS":
                index = _parse_atomic_positions(lines, index + 1, result)
                continue
        index += 1
    return result


def parse_kpt(path: Path) -> KptFile:
    result = KptFile(path=path)
    if not path.exists():
        result.diagnostics.append(
            Diagnostic("ABACUS202", "error", "KPT file is missing", str(path), 1)
        )
        return result

    meaningful = [
        (line_no, line.strip())
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1)
        if line.strip() and not line.strip().startswith(COMMENT_PREFIXES)
    ]
    if not meaningful:
        result.diagnostics.append(
            Diagnostic("ABACUS004", "error", "KPT file is empty", str(path), 1)
        )
        return result
    if meaningful[0][1].upper() not in {"K_POINTS", "KPOINTS", "K"}:
        result.diagnostics.append(
            Diagnostic(
                "ABACUS004",
                "error",
                "KPT must start with K_POINTS, KPOINTS, or K",
                str(path),
                meaningful[0][0],
            )
        )
    if len(meaningful) >= 3:
        mode = meaningful[2][1].split()[0].lower()
        result.mode = mode
        if mode not in KNOWN_KPT_MODES:
            result.diagnostics.append(
                Diagnostic(
                    "ABACUS005",
                    "error",
                    f"unknown KPT mode: {mode}",
                    str(path),
                    meaningful[2][0],
                )
            )
    return result


def format_input_text(text: str) -> str:
    lines = text.splitlines()
    entries: list[tuple[str, str, str]] = []
    output: list[str] = []
    in_parameters = False
    for raw_line in lines:
        stripped = raw_line.strip()
        if stripped.upper() == "INPUT_PARAMETERS":
            output.append("INPUT_PARAMETERS")
            in_parameters = True
            continue
        if not in_parameters or not stripped or stripped.startswith(COMMENT_PREFIXES):
            output.append(raw_line.rstrip())
            continue
        body, sep, comment = raw_line.partition("#")
        parts = body.split(maxsplit=1)
        if not parts:
            output.append(raw_line.rstrip())
            continue
        key = parts[0]
        value = parts[1].strip() if len(parts) > 1 else ""
        entries.append((key, value, f"{sep}{comment}".rstrip()))

    if not entries:
        return "\n".join(output).rstrip() + "\n"

    width = max(len(key) for key, _value, _comment in entries)
    formatted_entries = []
    for key, value, comment in entries:
        base = f"{key:<{width}}  {value}".rstrip()
        if comment:
            base = f"{base}  {comment}"
        formatted_entries.append(base)

    formatted_iter = iter(formatted_entries)
    final: list[str] = []
    seen_header = False
    for raw_line in output:
        final.append(raw_line)
        if raw_line == "INPUT_PARAMETERS" and not seen_header:
            seen_header = True
            final.extend(formatted_iter)
            break
    return "\n".join(final).rstrip() + "\n"


def _parse_species(lines: list[str], index: int, result: StruFile) -> int:
    while index < len(lines):
        stripped = lines[index].strip()
        if not stripped or stripped.startswith(COMMENT_PREFIXES):
            index += 1
            continue
        if stripped.upper() in KNOWN_STRU_SECTIONS:
            return index
        parts = stripped.split()
        result.species.append(parts[0])
        if len(parts) >= 3:
            result.pseudopotentials.append(parts[2])
        index += 1
    return index


def _parse_orbitals(lines: list[str], index: int, result: StruFile) -> int:
    while index < len(lines):
        stripped = lines[index].strip()
        if not stripped or stripped.startswith(COMMENT_PREFIXES):
            index += 1
            continue
        if stripped.upper() in KNOWN_STRU_SECTIONS:
            return index
        result.orbitals.append(stripped.split()[0])
        index += 1
    return index


def _parse_atomic_positions(lines: list[str], index: int, result: StruFile) -> int:
    if index < len(lines):
        index += 1  # coordinate mode
    while index < len(lines):
        stripped = lines[index].strip()
        if not stripped or stripped.startswith(COMMENT_PREFIXES):
            index += 1
            continue
        if stripped.upper() in KNOWN_STRU_SECTIONS:
            return index
        element = stripped.split()[0]
        result.position_elements.append(element)
        if index + 2 >= len(lines):
            result.diagnostics.append(
                Diagnostic(
                    "ABACUS004",
                    "error",
                    "incomplete ATOMIC_POSITIONS element block",
                    str(result.path),
                    index + 1,
                )
            )
            return len(lines)
        count_line = lines[index + 2].strip()
        try:
            atom_count = int(count_line)
        except ValueError:
            result.diagnostics.append(
                Diagnostic(
                    "ABACUS006",
                    "error",
                    "atom count must be an integer",
                    str(result.path),
                    index + 3,
                )
            )
            return len(lines)
        first_atom_line = index + 3
        available = 0
        for row in lines[first_atom_line : first_atom_line + atom_count]:
            if row.strip() and not row.strip().startswith(COMMENT_PREFIXES):
                available += 1
        if available != atom_count:
            result.diagnostics.append(
                Diagnostic(
                    "ABACUS006",
                    "error",
                    "atom count does not match ATOMIC_POSITIONS rows",
                    str(result.path),
                    index + 3,
                    evidence=[f"expected {atom_count} rows, found {available}"],
                )
            )
        index = first_atom_line + atom_count
    return index


def _cross_file_diagnostics(
    input_file: InputFile, stru_file: StruFile, kpt_file: KptFile, case_dir: Path
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    basis_type = input_file.parameters.get("basis_type", "").lower()
    if basis_type == "lcao" and "NUMERICAL_ORBITAL" not in stru_file.sections:
        diagnostics.append(
            Diagnostic(
                "ABACUS205",
                "error",
                "basis_type=lcao requires NUMERICAL_ORBITAL entries in STRU",
                str(stru_file.path),
                1,
                evidence=["INPUT: basis_type lcao", "STRU: missing NUMERICAL_ORBITAL"],
                suggested_fix={
                    "kind": "insert_section",
                    "file": "STRU",
                    "section": "NUMERICAL_ORBITAL",
                },
                confidence=0.94,
            )
        )
    if (
        stru_file.species
        and stru_file.position_elements
        and stru_file.species != stru_file.position_elements
    ):
        diagnostics.append(
            Diagnostic(
                "ABACUS207",
                "warning",
                "ATOMIC_SPECIES order differs from ATOMIC_POSITIONS order",
                str(stru_file.path),
                1,
                evidence=[
                    f"ATOMIC_SPECIES: {', '.join(stru_file.species)}",
                    f"ATOMIC_POSITIONS: {', '.join(stru_file.position_elements)}",
                ],
            )
        )
    if "latname" in input_file.parameters and "LATTICE_VECTORS" in stru_file.sections:
        diagnostics.append(
            Diagnostic(
                "ABACUS208",
                "warning",
                "latname is set, but STRU contains LATTICE_VECTORS",
                str(stru_file.path),
                1,
            )
        )
    if input_file.parameters.get("gamma_only", "").lower() in {
        "1",
        "true",
        "t",
    } and kpt_file.mode not in {None, "gamma"}:
        diagnostics.append(
            Diagnostic(
                "ABACUS209",
                "warning",
                "gamma_only=1 will overwrite KPT; multi-k KPT is ignored",
                str(kpt_file.path),
                1,
            )
        )
    for directory_key, filenames in {
        "pseudo_dir": stru_file.pseudopotentials,
        "orbital_dir": stru_file.orbitals,
    }.items():
        if directory_key not in input_file.parameters:
            continue
        base_dir = case_dir / input_file.parameters[directory_key]
        for filename in filenames:
            if not (base_dir / filename).exists():
                diagnostics.append(
                    Diagnostic(
                        "ABACUS204",
                        "warning",
                        f"{directory_key} file does not exist: {filename}",
                        str(stru_file.path),
                        1,
                    )
                )
    return diagnostics
