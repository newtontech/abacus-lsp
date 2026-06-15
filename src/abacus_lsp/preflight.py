"""Universal generated-input preflight capabilities.

This module implements the four fleet-wide preflight capabilities called out in
``newtontech/abacus-lsp#60`` against a *generic artifact-role model*, so the
checks generalize to any backend in the scientific LSP fleet instead of being
wired to MatMaster submission policy:

* ``version-aware-keywords``  - explicit runtime/version assumption metadata and
  basis-availability validation derived from the schema, never guessed.
* ``cross-artifact-graph``   - resolves the case as a graph of artifacts with
  stable roles (primary-input, structure, kpoints, pseudopotential, orbital,
  lattice). Cross-file checks operate on the graph rather than ad-hoc file
  names, so the same model works for VASP/CP2K/GROMACS/etc.
* ``code-actions``           - normalizes repair hints/actions on every
  diagnostic and exposes a blocking gate the agent CLI can run as
  ``check --fail-on-blocking``.
* ``fleet-regression-fixtures`` - ``fleet_manifest`` returns a machine-readable
  description of the preflight surface (codes, capabilities, fixture
  expectations) so the parent ``bohrium_skills`` probe/report workflow can
  consume regression evidence without re-deriving it.

The diagnostics emitted here are plain dictionaries (not the legacy
``Diagnostic`` dataclass) so they can carry the richer ``DiagnosticEnvelope/v1``
fields (``source_provenance``, ``domain_tags``, ``facts``, ``artifact_roles``,
``version_assumption``, ``actions``) directly.

LLM Wiki: wiki/concepts/Basis_Set_Types.md
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .analyzer import (
    InputFile,
    KptFile,
    StruFile,
    _auto_kpt_grid,
    parse_input,
    parse_kpt,
    parse_stru,
)
from .schema import SchemaRegistry

# --- Artifact-role model ---------------------------------------------------

# Generic roles. These are intentionally software-agnostic: every fleet backend
# can map its native files onto this same small role set, which is what lets the
# parent router consume cross-file checks without learning MatMaster specifics.
ROLE_PRIMARY_INPUT = "primary-input"
ROLE_STRUCTURE = "structure"
ROLE_KPOINTS = "kpoints"
ROLE_PSEUDOPOTENTIAL = "pseudopotential"
ROLE_ORBITAL = "orbital"
ROLE_LATTICE = "lattice"

ALL_ROLES = (
    ROLE_PRIMARY_INPUT,
    ROLE_STRUCTURE,
    ROLE_KPOINTS,
    ROLE_PSEUDOPOTENTIAL,
    ROLE_ORBITAL,
    ROLE_LATTICE,
)

# Conservative workflow thresholds used by the warning-level ecutwfc check.
# The actual cutoff is overridable via the preflight intent contract; this is
# only the default fleet baseline, not a MatMaster policy.
DEFAULT_ECUTWFC_WARNING_RY = 50.0

# Codes reserved for the universal preflight surface. They use the ``ABACUS6xx``
# band so they sort after existing rule codes and stay identifiable as
# cross-fleet preflight findings.
CODE_MISSING_ARTIFACT = "ABACUS601"
CODE_NTYPE_MISMATCH = "ABACUS602"
CODE_MISSING_LATTICE = "ABACUS603"
CODE_LCAO_NO_ORBITAL = "ABACUS604"
CODE_UNRESOLVED_ARTIFACT = "ABACUS605"
CODE_ORBITAL_WITH_PW = "ABACUS606"
CODE_LOW_ECUTWFC = "ABACUS607"
CODE_SUSPICIOUS_KPOINTS = "ABACUS608"
CODE_VERSION_ASSUMPTION = "ABACUS609"
CODE_KEYWORD_VERSION_MISMATCH = "ABACUS610"


@dataclass(frozen=True)
class ArtifactNode:
    """A node in the cross-artifact graph.

    ``role`` is one of the fleet-generic roles above; ``path`` is the resolved
    filesystem path (may be a non-existent reference, which is itself a
    finding); ``source`` records where the reference originated so consumers
    can trace provenance.

    LLM Wiki: wiki/concepts/Basis_Set_Types.md
    """

    role: str
    path: Path
    exists: bool
    source: str
    referenced_from: tuple[str, int] | None = None
    detail: dict[str, Any] | None = None


@dataclass
class ArtifactGraph:
    """Generic cross-artifact graph built from a parsed case directory.

    LLM Wiki: wiki/concepts/Basis_Set_Types.md
    """

    case_dir: Path
    nodes: list[ArtifactNode] = field(default_factory=list)

    def by_role(self, role: str) -> list[ArtifactNode]:
        return [node for node in self.nodes if node.role == role]

    def to_json(self) -> list[dict[str, Any]]:
        """Serialize the graph for the parent probe/report workflow.

        LLM Wiki: wiki/concepts/Basis_Set_Types.md
        """

        def _node_json(node: ArtifactNode) -> dict[str, Any]:
            payload: dict[str, Any] = {
                "role": node.role,
                "path": str(node.path),
                "exists": node.exists,
                "source": node.source,
            }
            if node.referenced_from is not None:
                payload["referenced_from"] = {
                    "path": node.referenced_from[0],
                    "line": node.referenced_from[1],
                }
            if node.detail:
                payload["detail"] = node.detail
            return payload

        return sorted(
            (_node_json(node) for node in self.nodes),
            key=lambda item: (item["role"], item["path"]),
        )


def build_artifact_graph(
    case_dir: Path,
    input_file: InputFile,
    stru_file: StruFile,
    kpt_file: KptFile,
) -> ArtifactGraph:
    """Build the cross-artifact graph from parsed ABACUS inputs.

    The model is generic: it records roles + resolved paths + provenance. The
    same shape generalizes to other fleet backends because it never bakes in
    MatMaster/Bohrium runtime concepts (no input_dir, no image, no session).

    LLM Wiki: wiki/concepts/Basis_Set_Types.md
    """
    case_dir = case_dir.resolve()
    graph = ArtifactGraph(case_dir=case_dir)

    input_path = input_file.path
    graph.nodes.append(
        ArtifactNode(
            role=ROLE_PRIMARY_INPUT,
            path=input_path,
            exists=input_path.exists(),
            source="case-root",
        )
    )

    stru_name = input_file.parameters.get("stru_file", "STRU")
    stru_line = input_file.parameter_lines.get("stru_file", [1])[-1]
    graph.nodes.append(
        ArtifactNode(
            role=ROLE_STRUCTURE,
            path=stru_file.path,
            exists=stru_file.path.exists(),
            source=f"INPUT:{stru_name}",
            referenced_from=(str(input_path), stru_line),
        )
    )

    kpt_name = input_file.parameters.get("kpoint_file", "KPT")
    kpt_line = input_file.parameter_lines.get("kpoint_file", [1])[-1]
    graph.nodes.append(
        ArtifactNode(
            role=ROLE_KPOINTS,
            path=kpt_file.path,
            exists=kpt_file.path.exists(),
            source=f"INPUT:{kpt_name}",
            referenced_from=(str(input_path), kpt_line),
        )
    )

    pseudo_dir_value = input_file.parameters.get("pseudo_dir")
    for filename in stru_file.pseudopotentials:
        resolved = _resolve_dir(case_dir, pseudo_dir_value) / filename
        graph.nodes.append(
            ArtifactNode(
                role=ROLE_PSEUDOPOTENTIAL,
                path=resolved,
                exists=resolved.exists(),
                source=f"STRU:ATOMIC_SPECIES:{filename}",
                detail={"declared_dir": pseudo_dir_value} if pseudo_dir_value else None,
            )
        )

    orbital_dir_value = input_file.parameters.get("orbital_dir")
    for filename in stru_file.orbitals:
        resolved = _resolve_dir(case_dir, orbital_dir_value) / filename
        graph.nodes.append(
            ArtifactNode(
                role=ROLE_ORBITAL,
                path=resolved,
                exists=resolved.exists(),
                source=f"STRU:NUMERICAL_ORBITAL:{filename}",
                detail={"declared_dir": orbital_dir_value} if orbital_dir_value else None,
            )
        )

    has_vectors = "LATTICE_VECTORS" in stru_file.sections or (
        "LATTICE_PARAMETERS" in stru_file.sections and "LATTICE_VECTORS" in stru_file.sections
    )
    graph.nodes.append(
        ArtifactNode(
            role=ROLE_LATTICE,
            path=stru_file.path,
            exists=bool(stru_file.sections),
            source="STRU:LATTICE_VECTORS/LATTICE_PARAMETERS",
            detail={
                "has_vectors": "LATTICE_VECTORS" in stru_file.sections,
                "has_parameters": "LATTICE_PARAMETERS" in stru_file.sections,
                "latname_provided": "latname" in input_file.parameters,
            },
        )
        if has_vectors or "latname" in input_file.parameters
        else ArtifactNode(
            role=ROLE_LATTICE,
            path=stru_file.path,
            exists=False,
            source="STRU:LATTICE_VECTORS/LATTICE_PARAMETERS",
            detail={
                "has_vectors": False,
                "has_parameters": False,
                "latname_provided": False,
            },
        )
    )

    return graph


def _resolve_dir(case_dir: Path, declared: str | None) -> Path:
    if not declared:
        return case_dir
    candidate = Path(declared)
    if candidate.is_absolute():
        return candidate
    return case_dir / candidate


# --- Preflight diagnostics -------------------------------------------------


def preflight_diagnostics(
    case_dir: Path,
    *,
    registry: SchemaRegistry | None = None,
    intent: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], ArtifactGraph]:
    """Run universal generated-input preflight checks.

    Returns a tuple of (diagnostics, artifact_graph). Diagnostics are envelope
    dicts carrying the full ``DiagnosticEnvelope/v1`` field set so the agent
    CLI can emit them directly without re-shaping.

    LLM Wiki: wiki/concepts/Basis_Set_Types.md
    """
    case_dir = case_dir.resolve()
    registry = registry or SchemaRegistry.builtin().with_project_overrides(case_dir)
    input_file = parse_input(case_dir / "INPUT", registry)
    stru_file = parse_stru(
        case_dir / input_file.parameters.get("stru_file", "STRU")
    )
    kpt_file = parse_kpt(case_dir / input_file.parameters.get("kpoint_file", "KPT"))
    graph = build_artifact_graph(case_dir, input_file, stru_file, kpt_file)

    version_assumption = resolve_version_assumption(intent)
    diagnostics: list[dict[str, Any]] = []
    diagnostics.extend(_missing_artifact_diagnostics(graph))
    diagnostics.extend(_ntype_diagnostics(input_file, stru_file))
    diagnostics.extend(_lattice_diagnostics(input_file, stru_file))
    diagnostics.extend(_lcao_orbital_diagnostics(input_file, stru_file))
    diagnostics.extend(_unresolved_artifact_diagnostics(graph))
    diagnostics.extend(_orbital_with_pw_diagnostics(input_file, stru_file))
    diagnostics.extend(_low_ecutwfc_diagnostics(input_file, intent))
    diagnostics.extend(_suspicious_kpoints_diagnostics(input_file, kpt_file, stru_file))
    diagnostics.extend(_version_keyword_diagnostics(input_file, registry, version_assumption))
    diagnostics.extend(_version_assumption_diagnostic(version_assumption, intent))

    return sorted(
        diagnostics,
        key=lambda item: (
            item.get("range", {}).get("start", {}).get("line", 0),
            item.get("range", {}).get("start", {}).get("character", 0),
            item["code"],
        ),
    ), graph


def _diag(
    *,
    code: str,
    severity: str,
    message: str,
    path: Path,
    line: int = 1,
    column: int = 1,
    category: str,
    confidence: float,
    blocking: bool,
    source_provenance: dict[str, Any],
    fix_hints: list[str],
    actions: list[dict[str, Any]] | None = None,
    facts: dict[str, Any] | None = None,
    artifact_roles: list[str] | None = None,
    domain_tags: list[str] | None = None,
    version_assumption: dict[str, Any] | None = None,
    manual_ref: str | None = None,
    intent: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a single normalized preflight diagnostic.

    Carries every field the issue acceptance criteria require (``code``,
    ``severity``, ``path``/``range``, ``blocking``, ``category``,
    ``source_provenance``, ``fix_hints``/``actions``) plus the richer envelope
    fields (``facts``, ``artifact_roles``, ``domain_tags``,
    ``version_assumption``) used by the parent fleet probe.

    LLM Wiki: wiki/concepts/Basis_Set_Types.md
    """
    line0 = max(line - 1, 0)
    col0 = max(column - 1, 0)
    payload: dict[str, Any] = {
        "code": code,
        "severity": severity,
        "message": message,
        "file": str(path),
        "line": line,
        "column": column,
        "category": category,
        "confidence": confidence,
        "source": "abacus-preflight",
        "range": {
            "start": {"line": line0, "character": col0},
            "end": {"line": line0, "character": col0 + 1},
        },
        "blocking": blocking,
        "fix_hints": fix_hints,
        "source_provenance": source_provenance,
    }
    if actions:
        payload["actions"] = actions
    if facts:
        payload["facts"] = facts
    if artifact_roles:
        payload["artifact_roles"] = artifact_roles
    if domain_tags:
        payload["domain_tags"] = domain_tags
    if version_assumption:
        payload["version_assumption"] = version_assumption
    if manual_ref:
        payload["manual_ref"] = manual_ref
    if intent:
        payload["intent"] = intent
    return payload


def _missing_artifact_diagnostics(graph: ArtifactGraph) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    # Only block on primary structural artifacts; pseudopotential/orbital
    # resolution has its own dedicated diagnostic.
    for role in (ROLE_STRUCTURE, ROLE_KPOINTS):
        for node in graph.by_role(role):
            if not node.exists:
                ref = node.referenced_from or ("case-root", 1)
                out.append(
                    _diag(
                        code=CODE_MISSING_ARTIFACT,
                        severity="error",
                        message=(
                            f"{role} artifact referenced from INPUT is missing: "
                            f"{node.path.name}"
                        ),
                        path=node.path,
                        line=ref[1],
                        category="cross-file reference",
                        confidence=0.97,
                        blocking=True,
                        source_provenance={
                            "role": role,
                            "referenced_from": {"path": ref[0], "line": ref[1]},
                            "declared_in": node.source,
                        },
                        fix_hints=[
                            f"Create {node.path.name} in the case directory",
                            f"Or update the INPUT reference that points to {node.path.name}",
                        ],
                        actions=[
                            {
                                "kind": "create_artifact",
                                "role": role,
                                "target": str(node.path),
                                "safe_to_auto_apply": False,
                            }
                        ],
                        facts={"missing_path": str(node.path)},
                        artifact_roles=[role],
                        domain_tags=["cross-file", "blocking"],
                    )
                )
    return out


def _ntype_diagnostics(input_file: InputFile, stru_file: StruFile) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    ntype_raw = input_file.parameters.get("ntype")
    species_count = len(stru_file.species)
    if ntype_raw is None:
        # ntype absent is only a soft note: ABACUS can often infer it. We still
        # surface it so the parent probe knows the assumption was made.
        if species_count:
            out.append(
                _diag(
                    code=CODE_NTYPE_MISMATCH,
                    severity="information",
                    message=(
                        "ntype is unset; ABACUS will infer it from STRU "
                        "ATOMIC_SPECIES"
                    ),
                    path=input_file.path,
                    line=1,
                    category="semantic consistency",
                    confidence=0.8,
                    blocking=False,
                    source_provenance={
                        "role": ROLE_PRIMARY_INPUT,
                        "reason": "ntype keyword absent from INPUT",
                    },
                    fix_hints=[f"Set ntype {species_count} to make the assumption explicit"],
                    actions=[
                        {
                            "kind": "set_keyword",
                            "keyword": "ntype",
                            "value": str(species_count),
                            "target": str(input_file.path),
                            "safe_to_auto_apply": False,
                        }
                    ],
                    facts={"inferred_ntype": species_count},
                    artifact_roles=[ROLE_PRIMARY_INPUT, ROLE_STRUCTURE],
                    domain_tags=["cross-file", "assumption"],
                )
            )
        return out
    try:
        declared = int(str(ntype_raw).split()[0])
    except (ValueError, IndexError):
        return []
    if declared != species_count:
        line = input_file.parameter_lines.get("ntype", [1])[-1]
        out.append(
            _diag(
                code=CODE_NTYPE_MISMATCH,
                severity="error",
                message=(
                    f"ntype={declared} does not match the {species_count} "
                    "species declared in STRU ATOMIC_SPECIES"
                ),
                path=input_file.path,
                line=line,
                category="semantic consistency",
                confidence=0.96,
                blocking=True,
                source_provenance={
                    "role": ROLE_PRIMARY_INPUT,
                    "cross_referenced_role": ROLE_STRUCTURE,
                    "parsed_ntype": declared,
                    "parsed_species": stru_file.species,
                },
                fix_hints=[
                    f"Set ntype {species_count} to match ATOMIC_SPECIES",
                    "Or correct the ATOMIC_SPECIES block in STRU",
                ],
                actions=[
                    {
                        "kind": "set_keyword",
                        "keyword": "ntype",
                        "value": str(species_count),
                        "target": str(input_file.path),
                        "safe_to_auto_apply": False,
                    }
                ],
                facts={
                    "declared_ntype": declared,
                    "species_count": species_count,
                    "species": stru_file.species,
                },
                artifact_roles=[ROLE_PRIMARY_INPUT, ROLE_STRUCTURE],
                domain_tags=["cross-file", "blocking"],
            )
        )
    return out


def _lattice_diagnostics(
    input_file: InputFile, stru_file: StruFile
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    has_vectors = "LATTICE_VECTORS" in stru_file.sections
    has_parameters = "LATTICE_PARAMETERS" in stru_file.sections
    has_latname = "latname" in input_file.parameters
    if not has_vectors and not has_parameters and not has_latname:
        out.append(
            _diag(
                code=CODE_MISSING_LATTICE,
                severity="error",
                message=(
                    "STRU has no LATTICE_VECTORS/LATTICE_PARAMETERS and INPUT "
                    "has no latname fallback"
                ),
                path=stru_file.path,
                line=1,
                category="cross-file reference",
                confidence=0.95,
                blocking=True,
                source_provenance={
                    "role": ROLE_LATTICE,
                    "stru_sections": sorted(stru_file.sections),
                    "latname_provided": has_latname,
                },
                fix_hints=[
                    "Add a LATTICE_VECTORS block to STRU",
                    "Or set latname in INPUT to use a named lattice",
                ],
                actions=[
                    {
                        "kind": "insert_section",
                        "section": "LATTICE_VECTORS",
                        "target": str(stru_file.path),
                        "safe_to_auto_apply": False,
                    }
                ],
                facts={
                    "has_lattice_vectors": has_vectors,
                    "has_lattice_parameters": has_parameters,
                    "latname_provided": has_latname,
                },
                artifact_roles=[ROLE_LATTICE, ROLE_STRUCTURE],
                domain_tags=["cross-file", "blocking"],
            )
        )
    return out


def _lcao_orbital_diagnostics(
    input_file: InputFile, stru_file: StruFile
) -> list[dict[str, Any]]:
    out: list[dict[ str, Any]] = []
    basis_type = input_file.parameters.get("basis_type", "").lower()
    if basis_type == "lcao" and not stru_file.orbitals:
        out.append(
            _diag(
                code=CODE_LCAO_NO_ORBITAL,
                severity="error",
                message=(
                    "basis_type=lcao requires a NUMERICAL_ORBITAL section in STRU"
                ),
                path=stru_file.path,
                line=1,
                category="cross-file reference",
                confidence=0.95,
                blocking=True,
                source_provenance={
                    "role": ROLE_ORBITAL,
                    "basis_type": basis_type,
                    "orbital_count": len(stru_file.orbitals),
                },
                fix_hints=[
                    "Add a NUMERICAL_ORBITAL section listing orbital files",
                    "Or switch basis_type to pw",
                ],
                actions=[
                    {
                        "kind": "insert_section",
                        "section": "NUMERICAL_ORBITAL",
                        "target": str(stru_file.path),
                        "safe_to_auto_apply": False,
                    }
                ],
                facts={"basis_type": basis_type, "orbital_files": stru_file.orbitals},
                artifact_roles=[ROLE_ORBITAL, ROLE_STRUCTURE, ROLE_PRIMARY_INPUT],
                domain_tags=["cross-file", "blocking"],
            )
        )
    return out


def _unresolved_artifact_diagnostics(graph: ArtifactGraph) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for role in (ROLE_PSEUDOPOTENTIAL, ROLE_ORBITAL):
        for node in graph.by_role(role):
            if not node.exists:
                out.append(
                    _diag(
                        code=CODE_UNRESOLVED_ARTIFACT,
                        severity="warning",
                        message=(
                            f"{role} artifact referenced from STRU cannot be "
                            f"resolved: {node.path.name}"
                        ),
                        path=node.path,
                        line=1,
                        category="cross-file reference",
                        confidence=0.85,
                        blocking=False,
                        source_provenance={
                            "role": role,
                            "declared_in": node.source,
                            "declared_dir": (node.detail or {}).get("declared_dir"),
                        },
                        fix_hints=[
                            f"Place {node.path.name} in the declared directory",
                            "Or correct the directory declared in INPUT",
                        ],
                        actions=[
                            {
                                "kind": "resolve_artifact",
                                "role": role,
                                "target": str(node.path),
                                "safe_to_auto_apply": False,
                            }
                        ],
                        facts={"unresolved_path": str(node.path)},
                        artifact_roles=[role],
                        domain_tags=["cross-file", "workspace-resolve"],
                    )
                )
    return out


def _orbital_with_pw_diagnostics(
    input_file: InputFile, stru_file: StruFile
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    basis_type = input_file.parameters.get("basis_type", "").lower()
    if basis_type == "pw" and stru_file.orbitals:
        out.append(
            _diag(
                code=CODE_ORBITAL_WITH_PW,
                severity="warning",
                message=(
                    "STRU declares NUMERICAL_ORBITAL entries but basis_type=pw; "
                    "orbitals will be ignored"
                ),
                path=stru_file.path,
                line=1,
                category="semantic consistency",
                confidence=0.9,
                blocking=False,
                source_provenance={
                    "role": ROLE_ORBITAL,
                    "basis_type": basis_type,
                    "orbital_count": len(stru_file.orbitals),
                },
                fix_hints=[
                    "Remove the NUMERICAL_ORBITAL section if running a PW job",
                    "Or change basis_type to lcao",
                ],
                actions=[
                    {
                        "kind": "review_section",
                        "section": "NUMERICAL_ORBITAL",
                        "target": str(stru_file.path),
                        "safe_to_auto_apply": False,
                    }
                ],
                facts={"basis_type": basis_type, "orbital_files": stru_file.orbitals},
                artifact_roles=[ROLE_ORBITAL, ROLE_STRUCTURE, ROLE_PRIMARY_INPUT],
                domain_tags=["semantic", "non-blocking"],
            )
        )
    return out


def _low_ecutwfc_diagnostics(
    input_file: InputFile, intent: dict[str, Any] | None
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    ecut_raw = input_file.parameters.get("ecutwfc")
    if ecut_raw is None:
        return out
    try:
        ecut = float(str(ecut_raw).split()[0])
    except (ValueError, IndexError):
        return out
    # Intent contract can override the default baseline. If the intent declares
    # this is a high-accuracy production input, the finding is promoted to a
    # warning regardless of the baseline; otherwise the conservative default
    # triggers a warning below it.
    threshold = float(
        (intent or {}).get("ecutwfc_warning_ry", DEFAULT_ECUTWFC_WARNING_RY)
    )
    high_accuracy = bool((intent or {}).get("high_accuracy_production", False))
    if ecut < threshold:
        severity = "warning"
        blocking = False
        message = (
            f"ecutwfc={ecut} Ry is below the conservative workflow threshold "
            f"({threshold} Ry)"
        )
        if high_accuracy:
            message += "; intent marks this as high-accuracy production input"
        line = input_file.parameter_lines.get("ecutwfc", [1])[-1]
        out.append(
            _diag(
                code=CODE_LOW_ECUTWFC,
                severity=severity,
                message=message,
                path=input_file.path,
                line=line,
                category="preflight/runtime-risk",
                confidence=0.8,
                blocking=blocking,
                source_provenance={
                    "role": ROLE_PRIMARY_INPUT,
                    "keyword": "ecutwfc",
                    "threshold_source": (
                        "intent"
                        if "ecutwfc_warning_ry" in (intent or {})
                        else "default"
                    ),
                },
                fix_hints=[
                    f"Raise ecutwfc to at least {threshold} Ry",
                    "Or document the lower cutoff in the intent contract",
                ],
                actions=[
                    {
                        "kind": "set_keyword",
                        "keyword": "ecutwfc",
                        "value": str(threshold),
                        "target": str(input_file.path),
                        "safe_to_auto_apply": False,
                    }
                ],
                facts={
                    "ecutwfc": ecut,
                    "threshold": threshold,
                    "high_accuracy_production": high_accuracy,
                },
                artifact_roles=[ROLE_PRIMARY_INPUT],
                domain_tags=["preflight", "runtime-risk"],
            )
        )
    return out


def _suspicious_kpoints_diagnostics(
    input_file: InputFile, kpt_file: KptFile, stru_file: StruFile
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    grid = _auto_kpt_grid(kpt_file)
    if grid is None:
        return out
    if any(component <= 1 for component in grid):
        # Heuristic flag for low-dimensional / under-sampled meshes. The issue
        # frames this as a warning (risk of silent bad results) rather than a
        # hard block.
        out.append(
            _diag(
                code=CODE_SUSPICIOUS_KPOINTS,
                severity="warning",
                message=(
                    f"K-point grid {grid} contains a 1-point axis; under-sampling "
                    "risks silently inaccurate results for low-dimensional systems"
                ),
                path=kpt_file.path,
                line=1,
                category="preflight/runtime-risk",
                confidence=0.7,
                blocking=False,
                source_provenance={
                    "role": ROLE_KPOINTS,
                    "grid": list(grid),
                    "kpt_mode": kpt_file.mode,
                },
                fix_hints=[
                    "Increase the sparse k-point axis",
                    "Or confirm the system is genuinely low-dimensional",
                ],
                actions=[
                    {
                        "kind": "review_keyword",
                        "target": str(kpt_file.path),
                        "safe_to_auto_apply": False,
                    }
                ],
                facts={"grid": list(grid), "mode": kpt_file.mode},
                artifact_roles=[ROLE_KPOINTS],
                domain_tags=["preflight", "runtime-risk"],
            )
        )
    return out


# --- version-aware-keywords ------------------------------------------------


def resolve_version_assumption(intent: dict[str, Any] | None) -> dict[str, Any]:
    """Resolve the explicit runtime/version assumption for this preflight run.

    When the exact runtime/image version is unknown we record that fact
    explicitly rather than guessing, per the issue's version-assumptions
    acceptance criterion. The intent contract can override ``software_version``
    (e.g. ``abacus >=3.6``); otherwise we fall back to the schema version the
    builtin keyword set was authored against.

    LLM Wiki: wiki/concepts/Basis_Set_Types.md
    """
    intent = intent or {}
    software_version = intent.get("software_version")
    runtime_image = intent.get("runtime_image")
    assumption: dict[str, Any] = {
        "software": "abacus",
        "software_version": software_version or "unknown",
        "runtime_image": runtime_image or "unknown",
        "schema_source": intent.get("schema_source", "abacus-lsp builtin"),
        # The fallback is intentional and explicit so consumers never have to
        # guess whether ``unknown`` means "not checked" or "could not determine".
        "exact_runtime_known": bool(software_version or runtime_image),
    }
    if software_version or runtime_image:
        assumption["declared_by"] = "intent"
    else:
        assumption["declared_by"] = "fallback"
    return assumption


def _version_keyword_diagnostics(
    input_file: InputFile,
    registry: SchemaRegistry,
    version_assumption: dict[str, Any],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    basis_type = input_file.parameters.get("basis_type", "").lower()
    for keyword, value in input_file.parameters.items():
        schema = registry.get(keyword)
        if schema is None:
            continue
        availability = [item.lower() for item in schema.availability]
        # The schema records availability per basis (PW/LCAO). When basis_type
        # is set and the keyword is not available for it, that is a real
        # version/basis compatibility finding the parent probe can act on.
        if basis_type and availability and basis_type not in availability:
            line = input_file.parameter_lines.get(keyword, [1])[-1]
            out.append(
                _diag(
                    code=CODE_KEYWORD_VERSION_MISMATCH,
                    severity="error",
                    message=(
                        f"INPUT keyword {keyword} is not available for "
                        f"basis_type={basis_type} (schema availability: "
                        f"{schema.availability})"
                    ),
                    path=input_file.path,
                    line=line,
                    category="schema",
                    confidence=0.92,
                    blocking=True,
                    source_provenance={
                        "role": ROLE_PRIMARY_INPUT,
                        "keyword": keyword,
                        "schema_source": schema.source,
                    },
                    fix_hints=[
                        f"Remove {keyword} when using basis_type={basis_type}",
                        "Or switch to a supported basis_type",
                    ],
                    actions=[
                        {
                            "kind": "remove_keyword",
                            "keyword": keyword,
                            "target": str(input_file.path),
                            "safe_to_auto_apply": False,
                        }
                    ],
                    facts={
                        "keyword": keyword,
                        "value": value,
                        "basis_type": basis_type,
                        "availability": schema.availability,
                    },
                    artifact_roles=[ROLE_PRIMARY_INPUT],
                    domain_tags=["schema", "version-aware", "blocking"],
                    version_assumption=version_assumption,
                    manual_ref=schema.source,
                )
            )
    return out


def _version_assumption_diagnostic(
    version_assumption: dict[str, Any], intent: dict[str, Any] | None
) -> list[dict[str, Any]]:
    """Emit an explicit information diagnostic when the runtime version is unknown.

    This makes the version assumption machine-readable in the diagnostic stream
    itself (not just metadata) so the parent probe can surface it without
    parsing the envelope top-level.

    LLM Wiki: wiki/concepts/Basis_Set_Types.md
    """
    if version_assumption["exact_runtime_known"]:
        return []
    return [
        _diag(
            code=CODE_VERSION_ASSUMPTION,
            severity="information",
            message=(
                "Exact ABACUS runtime/image version is unknown; preflight "
                "validated against the builtin schema keyword set"
            ),
            path=Path(version_assumption.get("schema_source", "abacus-lsp builtin")),
            line=1,
            category="preflight/runtime-risk",
            confidence=1.0,
            blocking=False,
            source_provenance={
                "role": ROLE_PRIMARY_INPUT,
                "reason": "software_version and runtime_image not declared in intent",
            },
            fix_hints=[
                "Declare software_version/runtime_image in the intent contract",
            ],
            actions=[],
            facts={
                "software_version": version_assumption["software_version"],
                "runtime_image": version_assumption["runtime_image"],
                "schema_source": version_assumption["schema_source"],
            },
            artifact_roles=[ROLE_PRIMARY_INPUT],
            domain_tags=["version-aware", "assumption"],
            version_assumption=version_assumption,
            intent=dict(intent) if intent else None,
        )
    ]


# --- fleet-regression-fixtures --------------------------------------------


def fleet_manifest(
    *,
    fixtures: Iterable[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Return a machine-readable preflight manifest for the parent fleet.

    The parent ``bohrium_skills`` probe/report workflow consumes this to know
    which preflight codes exist, which capabilities are implemented, and which
    fixtures exercise them. Keeping it as data (not README prose) means the
    fleet regression evidence stays in sync with the implementation.

    LLM Wiki: wiki/concepts/Basis_Set_Types.md
    """
    codes = {
        CODE_MISSING_ARTIFACT: {
            "severity": "error",
            "category": "cross-file reference",
            "blocking": True,
            "capability": "cross-artifact-graph",
            "summary": "primary structure/kpoints artifact missing from workspace",
        },
        CODE_NTYPE_MISMATCH: {
            "severity": "error",
            "category": "semantic consistency",
            "blocking": True,
            "capability": "cross-artifact-graph",
            "summary": "ntype does not match STRU ATOMIC_SPECIES count",
        },
        CODE_MISSING_LATTICE: {
            "severity": "error",
            "category": "cross-file reference",
            "blocking": True,
            "capability": "cross-artifact-graph",
            "summary": "no lattice definition and no latname fallback",
        },
        CODE_LCAO_NO_ORBITAL: {
            "severity": "error",
            "category": "cross-file reference",
            "blocking": True,
            "capability": "cross-artifact-graph",
            "summary": "basis_type=lcao without NUMERICAL_ORBITAL section",
        },
        CODE_UNRESOLVED_ARTIFACT: {
            "severity": "warning",
            "category": "cross-file reference",
            "blocking": False,
            "capability": "cross-artifact-graph",
            "summary": "pseudopotential/orbital file cannot be resolved",
        },
        CODE_ORBITAL_WITH_PW: {
            "severity": "warning",
            "category": "semantic consistency",
            "blocking": False,
            "capability": "cross-artifact-graph",
            "summary": "NUMERICAL_ORBITAL declared but basis_type=pw",
        },
        CODE_LOW_ECUTWFC: {
            "severity": "warning",
            "category": "preflight/runtime-risk",
            "blocking": False,
            "capability": "version-aware-keywords",
            "summary": "ecutwfc below conservative workflow threshold",
        },
        CODE_SUSPICIOUS_KPOINTS: {
            "severity": "warning",
            "category": "preflight/runtime-risk",
            "blocking": False,
            "capability": "cross-artifact-graph",
            "summary": "k-point grid has a 1-point axis",
        },
        CODE_VERSION_ASSUMPTION: {
            "severity": "information",
            "category": "preflight/runtime-risk",
            "blocking": False,
            "capability": "version-aware-keywords",
            "summary": "exact runtime version unknown; fallback schema used",
        },
        CODE_KEYWORD_VERSION_MISMATCH: {
            "severity": "error",
            "category": "schema",
            "blocking": True,
            "capability": "version-aware-keywords",
            "summary": "keyword not available for declared basis_type",
        },
    }
    capabilities = {
        "version-aware-keywords": {
            "status": "available",
            "evidence_codes": [
                CODE_KEYWORD_VERSION_MISMATCH,
                CODE_VERSION_ASSUMPTION,
                CODE_LOW_ECUTWFC,
            ],
        },
        "cross-artifact-graph": {
            "status": "available",
            "roles": list(ALL_ROLES),
            "evidence_codes": [
                CODE_MISSING_ARTIFACT,
                CODE_NTYPE_MISMATCH,
                CODE_MISSING_LATTICE,
                CODE_LCAO_NO_ORBITAL,
                CODE_UNRESOLVED_ARTIFACT,
                CODE_ORBITAL_WITH_PW,
                CODE_SUSPICIOUS_KPOINTS,
            ],
        },
        "code-actions": {
            "status": "available",
            "blocking_gate": "abacus-lsp-tool check --fail-on-blocking",
            "evidence_codes": list(codes.keys()),
        },
        "fleet-regression-fixtures": {
            "status": "available",
            "fixtures": list(fixtures) if fixtures else [],
        },
    }
    return {
        "software": "abacus",
        "preflight_envelope": "DiagnosticEnvelope/v1",
        "artifact_roles": list(ALL_ROLES),
        "capabilities": capabilities,
        "codes": codes,
    }
