# ABACUS STRU File Format

> Source: http://abacus.deepmodeling.com/en/latest/advanced/input_files/stru.html
> Fetched: 2026-06-12

## Overview

The `STRU` file contains information about:
- Lattice geometry
- Names/locations of pseudopotential and numerical orbital files
- Structural information about the system (atomic positions)

## Example (No latname)

```
ATOMIC_SPECIES
Si 28.00 Si_ONCV_PBE-1.0.upf upf201 // label; mass; pseudo_file; pseudo_type

NUMERICAL_ORBITAL
Si_gga_8au_60Ry_2s2p1d.orb //numerical_orbital_file

LATTICE_CONSTANT
10.2 // lattice scaling factor (Bohr)

LATTICE_VECTORS
0.5 0.5 0.0 // latvec1
0.5 0.0 0.5 // latvec2
0.0 0.5 0.5 // latvec3

ATOMIC_POSITIONS
Direct //Cartesian or Direct coordinate.
Si // Element type
0.0 // magnetism
2 // number of atoms
0.00 0.00 0.00 0 0 0
0.25 0.25 0.25 1 1 1
```

## Example (latname fcc)

When `latname="fcc"` is set in INPUT, LATTICE_VECTORS section is removed:

```
ATOMIC_SPECIES
Si 28.00 Si_ONCV_PBE-1.0.upf // label; mass; pseudo_file

NUMERICAL_ORBITAL
Si_gga_8au_60Ry_2s2p1d.orb //numerical_orbital_file

LATTICE_CONSTANT
10.2 // lattice scaling factor (Bohr)

ATOMIC_POSITIONS
Direct //Cartesian or Direct coordinate.
Si // Element type
0.0 // magnetism
2 // number of atoms
0.00 0.00 0.00 0 0 0
0.25 0.25 0.25 1 1 1
```

## Sections

### ATOMIC_SPECIES

Each line defines one element type:
- Name (label)
- Mass (only used in MD; for electronic structure, value is not important)
- Pseudopotential file name
- Pseudopotential type (optional): `upf`, `upf201`, `vwr`, `blps`, `auto` (default)

Format: `label mass pseudo_file [pseudo_type]`

Example: `Si 28.00 Si_ONCV_PBE-1.0.upf upf201`

When `esolver_type` is `lj` or `dp`, pseudo_file and pseudo_type are not needed.

Common pseudopotential sources:
1. Quantum ESPRESSO
2. SG15-ONCV
3. DOJO
4. BLPS

### NUMERICAL_ORBITAL

Only needed for LCAO calculations. Specifies numerical orbital files per element.

Format: `orbital_file_name`

Example: `Si_gga_8au_60Ry_2s2p1d.orb`

### LATTICE_CONSTANT

The lattice constant of the system in units of Bohr.

### LATTICE_VECTORS

3x3 matrix written in 3 lines. Vectors are scaled by the lattice constant.
Must be removed if `latname` is specified in INPUT.

### LATTICE_PARAMETERS

Only used when `latname` is set. Contains parameters for Bravais lattice types:

| latname | Parameters | Description |
|---------|-----------|-------------|
| sc | none | Simple cubic |
| fcc | none | Face-centered cubic |
| bcc | none | Body-centered cubic |
| hexagonal | c/a ratio | Hexagonal |
| trigonal | cos(gamma) | Trigonal |
| st | c/a ratio | Simple tetragonal |
| bct | c/a ratio | Body-centered tetragonal |
| so | b/a, c/a | Simple orthorhombic |
| baco | b/a, c/a | Base-centered orthorhombic |
| fco | b/a, c/a | Face-centered orthorhombic |
| bco | b/a, c/a | Body-centered orthorhombic |
| sm | b/a, c/a, cos(ab) | Simple monoclinic |
| bacm | b/a, c/a, cos(ab) | Base-centered monoclinic |
| triclinic | b/a, c/a, cos(ab), cos(ac), cos(bc) | Triclinic |

### ATOMIC_POSITIONS

Specifies positions and other information of individual atoms.

**First line** - coordinate system:
- `Direct` - fractional coordinates
- `Cartesian` - Cartesian in units of LATTICE_CONSTANT
- `Cartesian_au` - Cartesian in Bohr (same as Cartesian with LATTICE_CONSTANT = 1.0)
- `Cartesian_angstrom` - Cartesian in Angstrom
- `Cartesian_angstrom_center_xy` - Angstrom, centered at (0.5, 0.5, 0.0) in Direct
- `Cartesian_angstrom_center_xz` - Angstrom, centered at (0.5, 0.0, 0.5) in Direct
- `Cartesian_angstrom_center_yz` - Angstrom, centered at (0.0, 0.5, 0.5) in Direct
- `Cartesian_angstrom_center_xyz` - Angstrom, centered at (0.5, 0.5, 0.5) in Direct

**Per element block:**
1. Element name (e.g., `Si`)
2. Initial magnetic moment (e.g., `0.0` or `1.0`)
3. Number of atoms (e.g., `2`)
4. One line per atom: `x y z [keyword value ...]`

### Per-atom Keywords

After atomic coordinates, the following keywords can appear in any order:

| Keyword | Description | Example |
|---------|-------------|---------|
| `m` (or no keyword) | Movement flags (0/1 for x,y,z) | `m 0 0 0` or `1 1 1` |
| `v` / `vel` / `velocity` | Initial velocity components | `v 1.0 1.0 1.0` |
| `mag` / `magmom` | Start magnetization per atom | `mag 1.0` or `mag 0.0 0.0 1.0` |
| `angle1` | Polar angle (z-axis to spin) in degrees | `angle1 90` |
| `angle2` | Azimuthal angle (x-axis in xy-plane) in degrees | `angle2 0` |
| `lambda` | Lagrange multiplier for spin constraint (eV) | `lambda 0.5` or `lambda 0.1 0.2 0.3` |
| `sc` | Spin constraint target magnetization | `sc 1.0` or `sc 0.5 0.5 1.0` |

**Magnetization defaults:**
- For `nspin==2` without explicit mag: auto-set to 1.0
- For `nspin==4` without explicit mag: auto-set to (1,1,1)
- Auto-set is invalidated if any atom has explicit magnetic moment

### Important Notes

1. Do not mix Direct and Cartesian coordinates in the same STRU file
2. Number of atoms must match actual coordinate lines
3. Angles are in degrees, not radians
4. Each keyword should appear only once per atom
5. Keywords can appear in any order after coordinates
