# ABACUS Input Files Quick Introduction

> Source: http://abacus.deepmodeling.com/en/latest/quick_start/input.html
> Fetched: 2026-06-12

## Overview

ABACUS requires three central input files before execution:
1. **INPUT** - Calculation parameters
2. **STRU** - Structure/geometry information
3. **KPT** - K-point grid settings

Plus supporting files:
- Pseudopotential files (UPF format)
- Numerical orbital files (LCAO only)

## INPUT File

Contains parameters controlling calculation type and settings.

### Format Rules

- Starts with `INPUT_PARAMETERS` keyword
- Lines starting with `#` or `/` are comments
- Format: `parameter_name value` (space or tab separated)
- Characters after position 150 ignored
- Values can be integer, real, or string
- Parameters in any order, one per line
- Duplicate names: last value wins
- Unknown names cause error and stop
- Filename must be "INPUT"

### Example INPUT

```
INPUT_PARAMETERS
suffix                  MgO  # output in OUT.{suffix} directory
pseudo_dir              ./   # pseudopotential directory
orbital_dir             ./   # orbital file directory
ecutwfc                 100  # in Rydberg
scf_thr                 1e-6 # SCF convergence
basis_type              lcao # lcao or pw
calculation             scf  # calculation type
out_chg                 0    # charge density output
```

### Key Parameters

| Parameter | Description |
|-----------|-------------|
| `suffix` | System name, output in OUT.{suffix} |
| `pseudo_dir` | Pseudopotential file directory |
| `orbital_dir` | Orbital file directory |
| `ecutwfc` | Energy cutoff for wave functions (Ry) |
| `scf_thr` | SCF convergence (Ry for PW, dimensionless for LCAO) |
| `basis_type` | `lcao` or `pw` |
| `calculation` | Calculation type (scf, nscf, relax, cell-relax, md, etc.) |
| `out_chg` | Charge output: -1=no, 0=binary, 1=binary+cube |

### Boolean Values

Boolean parameters accept: True/False, 1/0, T/F, true/false, TRUE/FALSE, t/f (case insensitive)

For `out_chg`: also supports `-1` to turn off checkpoint files.
Some output parameters accept a second option for precision, e.g., `out_chg 1 8` for 8 decimal digits.

### Built-in Help

```bash
abacus -h              # General help
abacus -s ecut         # Search parameters
abacus -h ecutwfc      # Detailed parameter help
```

## STRU File

Contains structural information: lattice constant, vectors, atomic positions.

### Example STRU

```
#This is the atom file containing all the information
#about the lattice structure.

ATOMIC_SPECIES
Mg 24.305  Mg_ONCV_PBE-1.0.upf  # element, mass, pseudopotential
O  15.999 O_ONCV_PBE-1.0.upf

NUMERICAL_ORBITAL
Mg_gga_8au_100Ry_4s2p1d.orb
O_gga_8au_100Ry_2s2p1d.orb

LATTICE_CONSTANT
1.889726126 # 1.0 Ang = 1/0.529177210544 Bohr

LATTICE_VECTORS
4.25648 0.00000 0.00000
0.00000 4.25648 0.00000
0.00000 0.00000 4.25648

ATOMIC_POSITIONS
Direct                  #Cartesian(Unit is LATTICE_CONSTANT)
Mg                      #Name of element
0.0                     #Magnetic for this element.
4                       #Number of atoms
0.0  0.0  0.0  0 0 0    #x,y,z, move_x, move_y, move_z
0.0  0.5  0.5  0 0 0
0.5  0.0  0.5  0 0 0
0.5  0.5  0.0  0 0 0
O                       #Name of element
0.0                     #Magnetic for this element.
4                       #Number of atoms
0.5  0.0  0.0  0 0 0
0.5  0.5  0.5  0 0 0
0.0  0.0  0.5  0 0 0
0.0  0.5  0.0  0 0 0
```

Notes:
- Custom STRU filename via `stru_file` keyword
- Pseudopotential and orbital order must match ATOMIC_POSITIONS order

## KPT File

K-point grid for Brillouin zone sampling.

### Example KPT

```
K_POINTS
0
Gamma
4 4 4 0 0 0
```

Custom KPT filename via `kpoint_file` keyword.

## Pseudopotential Files

- Norm-conserving pseudopotentials in UPF format
- Specified per element in STRU file
- Directory set by `pseudo_dir` in INPUT (default "./")
- Download from ABACUS website

## Numerical Orbital Files

- Only required for LCAO calculations
- Specified per element in STRU file
- Directory set by `orbital_dir` in INPUT (default "./")
- Download from ABACUS website
