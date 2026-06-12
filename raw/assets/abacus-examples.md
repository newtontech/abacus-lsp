# ABACUS Quick Start Examples

> Source: http://abacus.deepmodeling.com/en/latest/quick_start/hands_on.html
> Fetched: 2026-06-12

## SCF Calculation - LCAO Example (FCC MgO)

### STRU file

```
#This is the atom file containing all the information
#about the lattice structure.

ATOMIC_SPECIES
Mg 24.305  Mg_ONCV_PBE-1.0.upf  # element name, atomic mass, pseudopotential file
O  15.999 O_ONCV_PBE-1.0.upf

NUMERICAL_ORBITAL
Mg_gga_8au_100Ry_4s2p1d.orb
O_gga_8au_100Ry_2s2p1d.orb

LATTICE_CONSTANT
1.8897259886 		# 1.8897259886 Bohr =  1.0 Angstrom

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
0.0  0.5  0.5  0 0 0    #x,y,z, move_x, move_y, move_z
0.5  0.0  0.5  0 0 0    #x,y,z, move_x, move_y, move_z
0.5  0.5  0.0  0 0 0    #x,y,z, move_x, move_y, move_z
O                       #Name of element
0.0                     #Magnetic for this element.
4                       #Number of atoms
0.5  0.0  0.0  0 0 0    #x,y,z, move_x, move_y, move_z
0.5  0.5  0.5  0 0 0    #x,y,z, move_x, move_y, move_z
0.0  0.0  0.5  0 0 0    #x,y,z, move_x, move_y, move_z
0.0  0.5  0.0  0 0 0    #x,y,z, move_x, move_y, move_z
```

### INPUT file (LCAO)

```
INPUT_PARAMETERS
suffix                  MgO
pseudo_dir              ./
orbital_dir		./
ecutwfc                 100             # Rydberg
scf_thr                 1e-6		    # SCF criterion
basis_type              lcao
calculation             scf		# this is the key parameter telling abacus to do a scf calculation
```

### KPT file

```
K_POINTS
0
Gamma
4 4 4 0 0 0
```

### Running

```bash
OMP_NUM_THREADS=1 mpirun -np 2 abacus
```

### Expected Output

Main output in `OUT.MgO/running_scf.log`:
```
!FINAL_ETOT_IS -7663.897267807250 eV
```

## SCF Calculation - PW Example (FCC MgO)

### INPUT file (PW)

```
INPUT_PARAMETERS
suffix                  MgO
pseudo_dir              ./
ecutwfc                 100             # Rydberg
scf_thr                 1e-6		    # SCF criterion
basis_type              pw              # changes the type of basis set
calculation             scf		# this is the key parameter telling abacus to do a scf calculation
```

### STRU file (PW)

Same as LCAO example but **without** the NUMERICAL_ORBITAL section:

```
ATOMIC_SPECIES
Mg 24.305  Mg_ONCV_PBE-1.0.upf
O  15.999 O_ONCV_PBE-1.0.upf

LATTICE_CONSTANT
1.8897259886

LATTICE_VECTORS
4.25648 0.00000 0.00000
0.00000 4.25648 0.00000
0.00000 0.00000 4.25648

ATOMIC_POSITIONS
Direct
Mg
0.0
4
0.0  0.0  0.0  0 0 0
0.0  0.5  0.5  0 0 0
0.5  0.0  0.5  0 0 0
0.5  0.5  0.0  0 0 0
O
0.0
4
0.5  0.0  0.0  0 0 0
0.5  0.5  0.5  0 0 0
0.0  0.0  0.5  0 0 0
0.0  0.5  0.0  0 0 0
```

### Expected Output

```
!FINAL_ETOT_IS -7665.688319476949 eV
```

## Geometry Optimization - LCAO Example

### INPUT file (cell-relax)

```
INPUT_PARAMETERS
suffix                  MgO
nelec                   0.0
pseudo_dir              ./
orbital_dir             ./
ecutwfc                 100             # Rydberg
scf_thr                 1e-6		# SCF criterion
basis_type              lcao
calculation             cell-relax	# optimization calculation
force_thr_ev		0.01		# force convergence threshold (eV/Angstrom)
stress_thr		5		# stress convergence threshold (kBar)
relax_nmax		100		# maximal ionic iteration steps
out_stru		1
```

Use same KPT, STRU, pseudopotential, and orbital files as SCF-LCAO example.
Output: `STRU_NOW.cif` and `OUT.MgO/running_cell-relax.log`

## Geometry Optimization - PW Example

### INPUT file (cell-relax, PW)

```
INPUT_PARAMETERS
suffix                  MgO
nelec                   0.0
pseudo_dir              ./
ecutwfc                 100             # Rydberg
scf_thr                 1e-6		# SCF criterion
basis_type              pw
calculation             cell-relax	# optimization calculation
force_thr_ev		0.01		# force convergence threshold (eV/Angstrom)
stress_thr		5		# stress convergence threshold (kBar)
relax_nmax		100		# maximal ionic iteration steps
out_stru		1
```

Use same KPT, STRU, and pseudopotential files as SCF-PW example.
Output: `STRU_NOW.cif` and `STRU_ION_D`

## Key Differences: LCAO vs PW

| Aspect | LCAO | PW |
|--------|------|-----|
| `basis_type` | lcao | pw |
| Orbital files | Required in STRU | Not needed |
| `ecutwfc` default | 100 Ry | 50 Ry |
| `scf_thr` recommended | 1e-7 | 1e-9 |
| Speed | Faster for large systems | Simpler setup |
| Accuracy | Systematic with basis size | Systematic with cutoff |
