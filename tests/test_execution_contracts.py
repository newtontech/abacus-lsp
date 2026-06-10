from __future__ import annotations

import json
from pathlib import Path

from abacus_lsp.analyzer import analyze_case


def _write_case(case: Path) -> None:
    case.mkdir(parents=True, exist_ok=True)
    (case / "INPUT").write_text(
        "INPUT_PARAMETERS\nbasis_type lcao\npseudo_dir ../pseudos\norbital_dir ./\n",
        encoding="utf-8",
    )
    (case / "STRU").write_text(
        """ATOMIC_SPECIES
Si 28.085 Si.bad.upf

NUMERICAL_ORBITAL
Si.bad.orb

ATOMIC_POSITIONS
Direct
Si
0.0
1
0.0 0.0 0.0
""",
        encoding="utf-8",
    )
    (case / "KPT").write_text("K_POINTS\n0\nGamma\n1 1 1 0 0 0\n", encoding="utf-8")


def test_apns_inventory_diagnostics(tmp_path: Path) -> None:
    _write_case(tmp_path)
    config_dir = tmp_path / ".abacus-lsp"
    config_dir.mkdir()
    (config_dir / "apns.json").write_text(
        json.dumps({"pseudopotentials": ["Si.good.upf"], "orbitals": ["Si.good.orb"]}),
        encoding="utf-8",
    )

    codes = {item.code for item in analyze_case(tmp_path)}

    assert {"ABACUS401", "ABACUS402"} <= codes


def test_matmaster_execution_contract_diagnostics(tmp_path: Path) -> None:
    _write_case(tmp_path)
    config_dir = tmp_path / ".abacus-lsp"
    config_dir.mkdir()
    (config_dir / "matmaster.json").write_text(
        json.dumps(
            {
                "enabled": True,
                "min_kpoint_grid": [2, 2, 2],
                "forbid_parent_paths": True,
                "require_lcao_orbitals": True,
            }
        ),
        encoding="utf-8",
    )

    codes = {item.code for item in analyze_case(tmp_path)}

    assert {"ABACUS420", "ABACUS421"} <= codes
