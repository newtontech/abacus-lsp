from __future__ import annotations

import json
from pathlib import Path

from abacus_lsp.schema import SchemaRegistry, build_schema, validate_keyword_value


def test_build_schema_is_deterministic() -> None:
    first = build_schema(version="test")
    second = build_schema(version="test")

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["schema_version"] == "abacus-lsp-schema-v1"
    assert any(item["name"] == "ecutwfc" and item["unit"] == "Ry" for item in first["keywords"])


def test_project_override_updates_keyword(tmp_path: Path) -> None:
    override_dir = tmp_path / ".abacus-lsp"
    override_dir.mkdir()
    (override_dir / "schema.override.json").write_text(
        json.dumps(
            {
                "keywords": {
                    "ecutwfc": {
                        "default": "80",
                        "description": "Project default cutoff",
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    registry = SchemaRegistry.builtin().with_project_overrides(tmp_path)

    assert registry.get("ecutwfc") is not None
    assert registry.get("ecutwfc").default == "80"  # type: ignore[union-attr]
    assert registry.get("ecutwfc").description == "Project default cutoff"  # type: ignore[union-attr]


def test_schema_validation_covers_types_and_enums() -> None:
    registry = SchemaRegistry.builtin()

    assert validate_keyword_value(registry.get("ecutwfc"), "not-real")  # type: ignore[arg-type]
    assert validate_keyword_value(registry.get("gamma_only"), "maybe")  # type: ignore[arg-type]
    assert validate_keyword_value(registry.get("calculation"), "unknown")  # type: ignore[arg-type]
    assert validate_keyword_value(registry.get("calculation"), "scf") is None  # type: ignore[arg-type]
