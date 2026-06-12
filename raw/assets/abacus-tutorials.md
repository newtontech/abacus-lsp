# ABACUS Tutorial Materials and Learning Resources

> Sources: Multiple (see below)
> Fetched: 2026-06-12

## Official Documentation

### Main Documentation Site
- URL: http://abacus.deepmodeling.com/
- Full documentation for ABACUS including installation, quick start, advanced topics

### Quick Start Guide
- URL: http://abacus.deepmodeling.com/en/latest/quick_start/hands_on.html
- Two quick examples: SCF calculation and geometry optimization
- Both LCAO and PW basis sets demonstrated

### Input Files Introduction
- URL: http://abacus.deepmodeling.com/en/latest/quick_start/input.html
- Explanation of INPUT, STRU, and KPT files
- Built-in help system documentation

### Full INPUT Keyword Reference
- URL: http://abacus.deepmodeling.com/en/latest/advanced/input_files/input-main.html
- Complete list of 400+ INPUT parameters with types, defaults, descriptions

### STRU File Documentation
- URL: http://abacus.deepmodeling.com/en/latest/advanced/input_files/stru.html
- Complete STRU file format specification

### KPT File Documentation
- URL: http://abacus.deepmodeling.com/en/latest/advanced/input_files/kpt.html
- K-point file format including auto-generation and explicit settings

### Basis Sets and Pseudopotentials
- URL: http://abacus.deepmodeling.com/en/latest/advanced/pp_orb.html
- Pseudopotential formats, SOC requirements, download sources, APNS project

## Documentation Structure

```
Quick Start
├── Easy Installation
├── Two Quick Examples
├── Brief Introduction of Input Files
└── Brief Introduction of Output Files

Advanced
├── Advanced Installation Options
├── Running SCF
│   ├── Initializing SCF
│   ├── Constructing the Hamiltonian
│   ├── Solving the Hamiltonian
│   ├── Converging SCF
│   ├── Accelerating the Calculation
│   ├── SCF in Complex Environments
│   └── Spin-polarization and SOC
├── Basis Set and Pseudopotentials
├── Geometry Optimization
├── Molecular Dynamics
├── Accelerate Performance
│   └── CUDA GPU Implementations
├── Electronic Properties and Outputs
│   ├── Extracting Band Structure
│   ├── Calculating DOS and PDOS
│   ├── Mulliken Charge Analysis
│   ├── Extracting Electrostatic Potential
│   ├── Extracting Wave Functions
│   ├── Extracting Charge Density
│   ├── Extracting Hamiltonian and Overlap Matrices
│   ├── Extracting Density Matrices
│   └── Berry Phase Calculation
├── Detailed Output Files
│   ├── ABACUS Output File Specification
│   ├── The running_scf.log file
│   └── Outputting Dipole Moment
├── Interfaces to Other Software
│   ├── PyABACUS
│   ├── DeePKS
│   ├── DP-GEN
│   ├── DeepH
│   ├── DeePTB
│   ├── Hefei-NAMD
│   ├── Phonopy
│   ├── Wannier90
│   ├── ASE
│   ├── PYATB
│   ├── ShengBTE
│   ├── CANDELA
│   └── TB2J
└── Detailed Input Files
    ├── Full List of INPUT Keywords
    ├── The STRU file
    └── The KPT file
```

## External Tutorials

### ABACUS+DPGEN Usage Tutorial
- URL: https://mcresearch.github.io/abacus-user-guide/abacus-dpgen.html
- Chinese-language tutorial for using ABACUS with DP-GEN
- Covers automated workflow generation

### DeepModeling Tutorials
- URL: https://tutorials.deepmodeling.com/
- General DeepModeling ecosystem tutorials
- Covers DeePMD-kit, DP-GEN, and related tools

## Interfaces to Other Software

| Interface | Description |
|-----------|-------------|
| PyABACUS | Python interface to ABACUS |
| DeePKS | Deep learning-based Kohn-Sham |
| DP-GEN | Deep Potential generator |
| DeepH | Deep learning Hamiltonian |
| DeePTB | Deep learning tight-binding |
| Hefei-NAMD | Non-adiabatic molecular dynamics |
| Phonopy | Phonon calculations |
| Wannier90 | Maximally localized Wannier functions |
| ASE | Atomic Simulation Environment |
| PYATB | Anisotropic tight-binding |
| ShengBTE | Phonon transport |
| CANDELA | Light-matter interactions |
| TB2J | Magnetic exchange parameters |

## ABACUS Research Paper

- Title: "ABACUS: An Electronic Structure Analysis Package for the AI Era"
- arXiv: https://arxiv.org/html/2501.08697v3
- Discusses PW and NAO basis sets, DFT methods, and ML integration

## Built-in Help System

ABACUS includes command-line parameter lookup:

```bash
abacus -h              # General help and common parameters
abacus -s ecut         # Search for parameters by keyword
abacus -h ecutwfc      # Detailed help for specific parameter
```

Features:
- Case-insensitive parameter names
- Fuzzy matching for typos
- Shows type, default, category, unit, and description

## Installation

- conda-forge: `conda install -c conda-forge abacus`
- Source build with CMake
- Docker images available (GNU, Intel, CUDA)
- Windows via WSL2 + conda-forge

## ABACUS Website

- Official site: http://abacus.ustc.edu.cn/
- Download pseudopotentials and orbitals
- Benchmark results
