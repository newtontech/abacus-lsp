from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "abacus-lsp-schema-v1"


@dataclass(frozen=True)
class KeywordSchema:
    name: str
    type: str
    unit: str | None
    default: str | None
    category: str
    description: str
    availability: list[str]
    enum: list[str] | None
    source: str

    def to_json(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_json(cls, payload: dict[str, Any]) -> KeywordSchema:
        return cls(
            name=str(payload["name"]).lower(),
            type=str(payload.get("type", "String")),
            unit=payload.get("unit"),
            default=payload.get("default"),
            category=str(payload.get("category", "Uncategorized")),
            description=str(payload.get("description", "")),
            availability=list(payload.get("availability", [])),
            enum=list(payload["enum"]) if payload.get("enum") is not None else None,
            source=str(payload.get("source", "unknown")),
        )


BUILTIN_KEYWORDS: dict[str, KeywordSchema] = {
    item.name: item
    for item in [
        KeywordSchema(
            "suffix",
            "String",
            None,
            None,
            "System",
            "Suffix used for output directory naming.",
            ["PW", "LCAO"],
            None,
            "builtin",
        ),
        KeywordSchema(
            "calculation",
            "Enum",
            None,
            "scf",
            "System",
            "Calculation type.",
            ["PW", "LCAO"],
            ["scf", "relax", "cell-relax", "md", "nscf", "get_wf", "get_pchg"],
            "builtin",
        ),
        KeywordSchema(
            "basis_type",
            "Enum",
            None,
            "pw",
            "Electronic structure",
            "Basis set type.",
            ["PW", "LCAO"],
            ["pw", "lcao"],
            "builtin",
        ),
        KeywordSchema(
            "ecutwfc",
            "Real",
            "Ry",
            "50",
            "Plane wave",
            "Energy cutoff for plane wave functions.",
            ["PW", "LCAO"],
            None,
            "builtin",
        ),
        KeywordSchema(
            "scf_thr",
            "Real",
            None,
            "1e-7",
            "Electronic structure",
            "SCF convergence threshold.",
            ["PW", "LCAO"],
            None,
            "builtin",
        ),
        KeywordSchema(
            "pseudo_dir",
            "Path",
            None,
            "./",
            "Input files",
            "Directory containing pseudopotential files.",
            ["PW", "LCAO"],
            None,
            "builtin",
        ),
        KeywordSchema(
            "orbital_dir",
            "Path",
            None,
            "./",
            "Input files",
            "Directory containing numerical orbital files.",
            ["LCAO"],
            None,
            "builtin",
        ),
        KeywordSchema(
            "stru_file",
            "Path",
            None,
            "STRU",
            "Input files",
            "Structure file path.",
            ["PW", "LCAO"],
            None,
            "builtin",
        ),
        KeywordSchema(
            "kpoint_file",
            "Path",
            None,
            "KPT",
            "Input files",
            "K-point file path.",
            ["PW", "LCAO"],
            None,
            "builtin",
        ),
        KeywordSchema(
            "gamma_only",
            "Boolean",
            None,
            "0",
            "K-points",
            "Use gamma-only calculation, overriding normal KPT sampling.",
            ["PW", "LCAO"],
            None,
            "builtin",
        ),
        KeywordSchema(
            "latname",
            "String",
            None,
            None,
            "Structure",
            "Named lattice setting that should not be combined with LATTICE_VECTORS.",
            ["PW", "LCAO"],
            None,
            "builtin",
        ),
        KeywordSchema(
            "out_band",
            "Boolean",
            None,
            "0",
            "Output",
            "Write band structure output.",
            ["PW", "LCAO"],
            None,
            "builtin",
        ),
        KeywordSchema(
            "out_dos",
            "Boolean",
            None,
            "0",
            "Output",
            "Write density of states output.",
            ["PW", "LCAO"],
            None,
            "builtin",
        ),
        KeywordSchema(
            "nspin",
            "Integer",
            None,
            "1",
            "Spin",
            "Spin-polarization mode.",
            ["PW", "LCAO"],
            ["1", "2", "4"],
            "builtin",
        ),
        KeywordSchema(
            "dft_plus_u",
            "Boolean",
            None,
            "0",
            "DFT+U",
            "Enable DFT+U corrections.",
            ["PW", "LCAO"],
            None,
            "builtin",
        ),
    ]
}


class SchemaRegistry:
    def __init__(self, keywords: dict[str, KeywordSchema] | None = None) -> None:
        self.keywords = dict(keywords or BUILTIN_KEYWORDS)

    @classmethod
    def builtin(cls) -> SchemaRegistry:
        return cls(BUILTIN_KEYWORDS)

    @classmethod
    def from_file(cls, path: Path) -> SchemaRegistry:
        payload = json.loads(path.read_text(encoding="utf-8"))
        keywords = {
            item["name"].lower(): KeywordSchema.from_json(item)
            for item in payload.get("keywords", [])
        }
        return cls(keywords)

    def with_project_overrides(self, project_dir: Path) -> SchemaRegistry:
        override_path = project_dir / ".abacus-lsp" / "schema.override.json"
        if not override_path.exists():
            return self
        payload = json.loads(override_path.read_text(encoding="utf-8"))
        merged = dict(self.keywords)
        raw_keywords = payload.get("keywords", {})
        if isinstance(raw_keywords, dict):
            iterator: Any = raw_keywords.items()
        else:
            iterator = ((item["name"], item) for item in raw_keywords)
        for name, override in iterator:
            key = str(name).lower()
            base = merged.get(key, KeywordSchema.from_json({"name": key}))
            updates = {field: value for field, value in dict(override).items() if field != "name"}
            merged[key] = replace(base, **updates)
        return SchemaRegistry(merged)

    def get(self, name: str) -> KeywordSchema | None:
        return self.keywords.get(name.lower())

    def names(self) -> list[str]:
        return sorted(self.keywords)

    def to_json(self, version: str = "builtin") -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "abacus_version": version,
            "keywords": [self.keywords[name].to_json() for name in self.names()],
        }

    def write_json(self, path: Path, version: str = "builtin") -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(self.to_json(version), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


def build_schema(
    abacus_bin: str | None = None,
    docs_cache: Path | None = None,
    version: str = "builtin",
) -> dict[str, Any]:
    registry = SchemaRegistry.builtin()
    runtime = _collect_runtime_keywords(abacus_bin)
    if runtime:
        merged = dict(registry.keywords)
        merged.update(runtime)
        registry = SchemaRegistry(merged)
    payload = registry.to_json(version=version)
    if docs_cache is not None:
        payload["docs_cache"] = str(docs_cache)
    return payload


def _collect_runtime_keywords(abacus_bin: str | None) -> dict[str, KeywordSchema]:
    if not abacus_bin:
        return {}
    try:
        result = subprocess.run(
            [abacus_bin, "-h"],
            text=True,
            capture_output=True,
            check=False,
            timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired):
        return {}
    if result.returncode != 0:
        return {}
    found: dict[str, KeywordSchema] = {}
    for line in result.stdout.splitlines():
        token = line.strip().split(maxsplit=1)[0].lower() if line.strip() else ""
        if not token or not token.replace("_", "").isalnum():
            continue
        if token in BUILTIN_KEYWORDS:
            found[token] = replace(BUILTIN_KEYWORDS[token], source=f"{abacus_bin} -h")
    return found


def validate_keyword_value(keyword: KeywordSchema, value: str) -> str | None:
    first = value.split()[0] if value.split() else ""
    if keyword.type == "Real":
        try:
            float(first)
        except ValueError:
            return f"{keyword.name} expects a real number"
    elif keyword.type == "Integer":
        try:
            int(first)
        except ValueError:
            return f"{keyword.name} expects an integer"
    elif keyword.type == "Boolean":
        if first.lower() not in {"true", "false", "t", "f", "1", "0"}:
            return f"{keyword.name} expects a boolean value"
    elif keyword.type == "Enum" and keyword.enum:
        if first.lower() not in {item.lower() for item in keyword.enum}:
            return f"{keyword.name} expects one of: {', '.join(keyword.enum)}"
    return None
