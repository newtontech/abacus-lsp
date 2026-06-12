# ABACUS INPUT File Reference

> Source: http://abacus.deepmodeling.com/en/latest/advanced/input_files/input-main.html
> Fetched: 2026-06-12

## Overview

The INPUT file controls calculation type and settings. Starts with keyword `INPUT_PARAMETERS`.

### File Format Rules

- Must start with `INPUT_PARAMETERS` keyword
- Lines starting with `#` or `/` are ignored
- Format: `parameter_name value` (separated by spaces or tabs)
- Characters after position 150 on a line are ignored
- Parameters can be in any order
- Only one parameter per line
- Duplicate parameter names: last value wins
- Unknown parameter names cause program to stop with error
- Filename must be exactly "INPUT"
- Boolean values: `True/False`, `1/0`, `T/F`, `true/false` (case insensitive)

### Basic Example

```
INPUT_PARAMETERS
suffix                  MgO  # output in OUT.{suffix} directory
pseudo_dir              ./   # pseudopotential directory
orbital_dir             ./   # orbital file directory
ecutwfc                 100  # in Rydberg
scf_thr                 1e-6 # SCF convergence threshold
basis_type              lcao # lcao or pw
calculation             scf  # calculation type
out_chg                 0    # charge density output
```

### Built-in Help

```bash
abacus -h              # General help
abacus -s ecut         # Search parameters by keyword
abacus -h ecutwfc      # Detailed help for specific parameter
```

Parameter lookups are case-insensitive. Fuzzy matching suggests similar parameters for typos.

## Parameter Categories

### System Variables

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `suffix` | String | ABACUS | Name for output directory (OUT.{suffix}) |
| `ntype` | Integer | 0 | Number of different atom species |
| `calculation` | String | scf | Calculation type (see below) |
| `esolver_type` | String | ksdft | Energy solver type |
| `symmetry` | Integer | 1 | Whether to use symmetry |
| `symmetry_prec` | Real | 1e-5 | Precision for symmetry analysis |
| `symmetry_autoclose` | Boolean | True | Auto-close symmetry on failure |
| `cal_force` | Boolean | 0 | Whether to calculate forces |
| `kpar` | Integer | 1 | K-point parallelization |
| `bndpar` | Integer | 1 | Band parallelization |
| `latname` | String | none | Bravais lattice type name |
| `init_wfc` | String | atomic | Initial wavefunction method |
| `init_chg` | String | atomic | Initial charge density method |
| `init_vel` | Boolean | 0 | Whether to read initial velocity |
| `mem_saver` | Integer | 0 | Memory saving mode |
| `cal_stress` | Boolean | 0 | Whether to calculate stress |
| `diago_proc` | Integer | 0 | Number of procs for diagonalization |
| `nbspline` | Integer | -1 | B-spline interpolation |
| `kspacing` | Real | 0 | K-point spacing (in 1/Bohr) |
| `koffset` | Integer | 0 | K-point offset |
| `kmesh_type` | String | gamma | K-mesh type |
| `min_dist_coef` | Real | 0.2 | Minimum distance coefficient |
| `device` | String | cpu | Compute device (cpu/gpu) |
| `precision` | String | double | Floating point precision |
| `cell_factor` | Real | 1.2 | Cell factor for variable-cell |
| `chg_extrap` | String | atomic | Charge extrapolation method |

### Calculation Types

| Value | Description |
|-------|-------------|
| `scf` | Self-consistent electronic structure calculation |
| `nscf` | Non-self-consistent calculation (requires charge density file) |
| `relax` | Structure relaxation (atomic positions) |
| `cell-relax` | Cell relaxation (positions + lattice vectors) |
| `md` | Molecular dynamics simulation |
| `get_pchg` | Partial (band-decomposed) charge density (LCAO only) |
| `get_wf` | Real space wave functions (LCAO only) |
| `get_s` | Overlap matrix (LCAO with multiple k points) |
| `gen_bessel` | Generate Bessel projectors for DeePKS (LCAO only) |
| `gen_opt_abfs` | Generate optimized auxiliary basis functions |
| `test_memory` | Estimate memory consumption |
| `test_neighbour` | Neighboring atom information (LCAO only) |

### Energy Solver Types (esolver_type)

| Value | Description |
|-------|-------------|
| `ksdft` | Kohn-Sham DFT (default) |
| `ofdft` | Orbital-free DFT |
| `sdft` | Stochastic DFT |
| `lj` | Lennard-Jones potential |
| `dp` | Deep Potential (machine learning) |
| `ksdft_md` | Kohn-Sham DFT for molecular dynamics |

### Input Files

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `stru_file` | String | STRU | Structure file name |
| `kpoint_file` | String | KPT | K-point file name |
| `pseudo_dir` | String | ./ | Pseudopotential directory |
| `orbital_dir` | String | ./ | Orbital file directory |
| `read_file_dir` | String | OUT.suffix/ | Directory for reading files |
| `restart_load` | Boolean | False | Load from previous calculation |

### Plane Wave Variables

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ecutwfc` | Real | 50 (PW) / 100 (LCAO) | Plane-wave energy cutoff (Ry) |
| `ecutrho` | Real | 4*ecutwfc | Charge density cutoff (Ry) |
| `nx/ny/nz` | Integer | 0 | FFT grid dimensions |
| `pw_diag_thr` | Real | 1e-2 | Diagonalization threshold |
| `pw_diag_nmax` | Integer | 30 | Max diagonalization iterations |
| `fft_mode` | Integer | 0 | FFT mode selection |

### LCAO Variables

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lmaxmax` | Integer | 2 | Maximum angular momentum |
| `lcao_ecut` | Real | 0 | Energy cutoff for LCAO |
| `search_radius` | Real | -1 | Search radius for neighbors (Bohr) |
| `bx/by/bz` | Integer | 1 | Grid partition for LCAO |

### Electronic Structure

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `basis_type` | String | pw | Basis set: `pw` or `lcao` |
| `ks_solver` | String | default | Eigensolver method |
| `nbands` | Integer | 0 | Number of bands |
| `nelec` | Real | 0 | Number of electrons |
| `dft_functional` | String | default | Exchange-correlation functional |
| `nspin` | Integer | 1 | Spin polarization: 1, 2, or 4 |
| `smearing_method` | String | gauss | Smearing method |
| `smearing_sigma` | Real | 0.01 | Smearing width (Ry) |
| `mixing_type` | String | pulay | Charge mixing method |
| `mixing_beta` | Real | 0.7 | Mixing parameter |
| `gamma_only` | Integer | 0 | Gamma-only calculation |
| `scf_nmax` | Integer | 50 | Max SCF iterations |
| `scf_thr` | Real | 1e-9 (PW) / 1e-7 (LCAO) | SCF convergence threshold |
| `scf_ene_thr` | Real | -1 | Energy convergence threshold |
| `lspinorb` | Boolean | 0 | Spin-orbit coupling |
| `noncolin` | Boolean | 0 | Non-collinear magnetism |

### Smearing Methods

| Value | Description |
|-------|-------------|
| `gauss` | Gaussian smearing |
| `gaussian` | Gaussian (alias) |
| `fd` | Fermi-Dirac |
| `mp` | Methfessel-Paxton |
| `mp2` | Second-order Methfessel-Paxton |
| `mv` | Marzari-Vanderbilt (cold smearing) |

### Mixing Types

| Value | Description |
|-------|-------------|
| `plain` | Simple mixing |
| `pulay` | Pulay mixing (default) |
| `pulay-kerker` | Pulay with Kerker preconditioner |
| `broyden` | Broyden mixing |

### Geometry Relaxation

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `relax_method` | String | cg | Relaxation method |
| `relax_nmax` | Integer | 1 | Max ionic iterations |
| `force_thr` | Real | 0.025 | Force threshold (Ry/Bohr) |
| `force_thr_ev` | Real | 0.025 | Force threshold (eV/Angstrom) |
| `stress_thr` | Real | 0.5 | Stress threshold (kBar) |
| `relax_bfgs_w1` | Real | 0.01 | BFGS w1 parameter |
| `relax_bfgs_w2` | Real | 0.5 | BFGS w2 parameter |
| `fixed_axes` | String | None | Fixed axes during relaxation |
| `fixed_ibrav` | Boolean | False | Keep Bravais lattice type |
| `fixed_atoms` | Boolean | False | Fix all atoms |

### Relaxation Methods

| Value | Description |
|-------|-------------|
| `cg` | Conjugate gradient (default) |
| `bfgs` | BFGS quasi-Newton |
| `sd` | Steepest descent |
| `cg-bfgs` | Combined CG and BFGS |

### Output Control

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `out_chg` | Integer | 0 | Charge density output (-1/0/1) |
| `out_pot` | Integer | 0 | Electrostatic potential output |
| `out_wfc_pw` | Integer | 0 | PW wavefunction output |
| `out_wfc_lcao` | Integer | 0 | LCAO wavefunction output |
| `out_dos` | Integer | 0 | Density of states output |
| `out_band` | Integer | 0 | Band structure output |
| `out_stru` | Integer | 0 | Structure output |
| `out_mat_hs` | Integer | 0 | Hamiltonian/overlap matrix output |
| `out_mul` | Integer | 0 | Mulliken charge analysis |
| `out_level` | String | ie | Output verbosity level |
| `out_app_flag` | Boolean | True | Append to output files |
| `out_ndigits` | Integer | 8 | Output precision (decimal places) |
| `restart_save` | Boolean | False | Save restart files |

### Molecular Dynamics

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `md_type` | Integer | 0 | MD type (0=NVT, 1=NPT, etc.) |
| `md_nstep` | Integer | 10 | Number of MD steps |
| `md_dt` | Real | 1.0 | Time step (fs) |
| `md_thermostat` | String | nhc | Thermostat type |
| `md_tfirst` | Real | -1 | Initial temperature (K) |
| `md_tlast` | Real | -1 | Final temperature (K) |
| `md_restart` | Boolean | False | Restart MD |
| `md_dumpfreq` | Integer | 1 | Dump frequency |
| `md_seed` | Integer | -1 | Random seed |

### DFT+U Correction

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dft_plus_u` | Integer | 0 | DFT+U method (0=off, 1=simple, 2=advanced) |
| `orbital_corr` | Integer[] | -1 | Which orbitals to correct (-1=none, l quantum number) |
| `hubbard_u` | Real[] | 0.0 | Hubbard U values (eV) |
| `yukawa_potential` | Boolean | False | Use Yukawa potential |
| `yukawa_lambda` | Real | 0.0 | Yukawa screening parameter |
| `onsite_radius` | Real | 0.0 | Onsite radius (Bohr) |

### vdW Correction

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `vdw_method` | String | none | vdW method (d2/d3/d3bj/d4/bbjk/kbd/none) |
| `vdw_s6` | Real | default | Scaling parameter s6 |
| `vdw_s8` | Real | default | Scaling parameter s8 |
| `vdw_a1` | Real | default | Damping parameter a1 |
| `vdw_a2` | Real | default | Damping parameter a2 |
| `vdw_cutoff_radius` | Real | default | Cutoff radius |

### Electric Field

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `efield_flag` | Boolean | False | Apply electric field |
| `dip_cor_flag` | Boolean | False | Dipole correction |
| `efield_dir` | Integer | 2 | Field direction (0=x, 1=y, 2=z) |
| `efield_amp` | Real | 0 | Field amplitude (a.u.) |

### Exact Exchange (Hybrid Functionals)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `exx_fock_alpha` | Real | 0.25 | Fraction of exact exchange |
| `exx_hybrid_step` | Integer | 1 | Hybrid functional SCF steps |
| `exx_separate_loop` | Boolean | True | Separate EXX loop |

### Spin-Orbit Coupling

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lspinorb` | Boolean | False | Enable SOC |
| `noncolin` | Boolean | False | Non-collinear magnetism |
| `soc_lambda` | Real | 1.0 | SOC strength scaling |

### RT-TDDFT (Real-Time TDDFT)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `td_dt` | Real | 0.02 | Time step (a.u.) |
| `td_propagator` | String | midpoint | Propagation method |
| `td_vext` | Boolean | False | External field |
| `td_stype` | Integer | 0 | Field spatial type |
| `td_ttype` | String | none | Field temporal type |
| `out_dipole` | Boolean | False | Output dipole moment |
| `out_current` | Boolean | False | Output current |

### Implicit Solvation

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `imp_sol` | Boolean | False | Enable implicit solvation |
| `eb_k` | Real | 80 | Dielectric constant |
| `tau` | Real | 0.000182 | Effective surface tension parameter |
| `sigma_k` | Real | 0.6 | Width of dielectric function |
| `nc_k` | Real | 0.00037 | Density threshold |

### DeePKS (Machine Learning)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `deepks_scf` | Boolean | False | Enable DeePKS SCF |
| `deepks_model` | String | none | Model file path |
| `deepks_out_labels` | Boolean | False | Output training labels |
| `deepks_bandgap` | Boolean | False | Bandgap model |

### Berry Phase

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `berry_phase` | Boolean | False | Calculate Berry phase |
| `gdir` | Integer | 3 | Direction for polarization |
| `towannier90` | Boolean | False | Wannier90 interface |

## Parameter Count by Category

- System variables: ~30
- Input files: ~7
- Plane wave: ~18
- LCAO: ~11
- Electronic structure: ~37
- SDFT: ~9
- Geometry relaxation: ~19
- Output: ~32
- DOS: ~8
- NAOs: ~6
- DeePKS: ~17
- OFDFT: ~20
- ML-KEDF: ~32
- Electric field: ~7
- Gate field: ~6
- Exact Exchange: ~28
- Molecular dynamics: ~38
- DFT+U: ~9
- Spin-Constrained DFT: ~10
- vdW correction: ~20
- Berry phase: ~11
- RT-TDDFT: ~37
- Debug: ~10
- Electronic conductivities: ~9
- Implicit solvation: ~5
- QO analysis: ~5
- PEXSI: ~25
- LR-TDDFT: ~16
- RDMFT: ~2

Total: ~400+ parameters
