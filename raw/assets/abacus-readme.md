# ABACUS GitHub Repository README

> Source: https://github.com/deepmodeling/abacus-develop
> Fetched: 2026-06-12

## About ABACUS

ABACUS (**A**tomic-orbital **B**ased **A**b-initio **C**omputation at **US**tc) is an open-source package based on density functional theory (DFT). The package utilizes both plane wave and numerical atomic basis sets with the usage of pseudopotentials to describe the interactions between nuclear ions and valence electrons.

## Key Features

- Supports LDA, GGA, meta-GGA, and hybrid functionals
- Single-point calculations, geometry optimizations, and ab-initio molecular dynamics with various ensembles
- Advanced functionalities: DFT+U, VdW corrections, implicit solvation model
- General infrastructure for machine-learning-assisted DFT methods (DeePKS, DP-GEN, DeepH, DeePTB etc.)

## Repository Structure

```
abacus-develop/
├── cmake/          # CMake build configuration
├── conda/          # Conda package recipes
├── docs/           # Documentation sources
├── doxygen/        # Doxygen API documentation
├── examples/       # Example calculations
├── interfaces/     # Interfaces to other software
├── python/pyabacus/# Python interface
├── source/         # C++ source code
├── tests/          # Test suite
├── toolchain/      # Build toolchain
├── tools/          # Utility tools
├── CMakeLists.txt  # Build system
├── Dockerfile.gnu  # Docker (GNU)
├── Dockerfile.intel# Docker (Intel)
├── Dockerfile.cuda # Docker (CUDA)
```

## Languages

- C++ 88.5%
- Python 4.0%
- CUDA 3.3%
- Shell 2.6%
- CMake 1.1%
- C 0.4%

## License

LGPL-3.0

## Latest Release

v3.11.0-beta.2 (May 15, 2026), 94 total releases.

## Topics

dft, openmp, mpi, cuda, molecular-dynamics, density-functional-theory, ab-initio, electronic-structure, orbital-free-dft, real-time-tddft

## Online Documentation

- Main docs: http://abacus.deepmodeling.com/
- GitHub Pages tutorials and developer guides
