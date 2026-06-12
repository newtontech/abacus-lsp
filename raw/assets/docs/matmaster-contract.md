# ABACUS MatMaster execution contracts

MatMaster workflows can opt into additional execution guards with a local
`.abacus-lsp/matmaster.json` file.

```json
{
  "enabled": true,
  "min_kpoint_grid": [2, 2, 2],
  "forbid_parent_paths": true,
  "require_lcao_orbitals": true
}
```

When enabled, `abacus-lsp` emits:

- `ABACUS420` when the automatic KPT grid is below `min_kpoint_grid`.
- `ABACUS421` when `pseudo_dir` or `orbital_dir` points outside the workspace.
- `ABACUS422` when an LCAO job omits explicit `NUMERICAL_ORBITAL` entries.

## APNS inventory checks

APNS-backed submissions can add `.abacus-lsp/apns.json`:

```json
{
  "pseudopotentials": ["Si_ONCV_PBE-1.2.upf"],
  "orbitals": ["Si_gga_8au_100Ry_2s2p1d.orb"]
}
```

The analyzer reports `ABACUS401` for pseudopotentials outside the configured
inventory and `ABACUS402` for orbital files outside the configured inventory.
