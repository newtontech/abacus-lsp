# ABACUS KPT File Format

> Source: http://abacus.deepmodeling.com/en/latest/advanced/input_files/kpt.html
> Fetched: 2026-06-12

## Overview

The KPT file contains k-point grid settings for Brillouin zone sampling. ABACUS uses periodic boundary conditions for both crystals and finite systems.

## Gamma-only Calculations

Set `gamma_only` to 1 in INPUT for LCAO basis. The KPT file will be overwritten. Ensure `gamma_only` is off for multi-k calculations.

## Auto-Generated k-mesh (Monkhorst-Pack)

```
K_POINTS // keyword for start
0        // total number of k-points, 0 = generate automatically
Gamma    // Monkhorst-Pack method: 'Gamma' or 'MP'
2 2 2 0 0 0 // subdivisions along reciprocal vectors, then shift
```

- First line: keyword (`K_POINTS`, `KPOINTS`, or `K`)
- Second line: `0` means auto-generate using Monkhorst-Pack
- Third line: `Gamma` (Gamma-centered) or `MP` (offset)
- Fourth line: first 3 integers = k-grid dimensions, last 3 = offset

`Gamma` = Gamma-centered Monkhorst-Pack (includes Gamma point)
`MP` = Standard Monkhorst-Pack (may not include Gamma point)

## Explicit k-points

```
K_POINTS // keyword for start
8        // total number of k-points
Direct   // 'Direct' or 'Cartesian' coordinate
0.0 0.0 0.0 0.125 // coordinates and weights
0.5 0.0 0.0 0.125
0.0 0.5 0.0 0.125
0.5 0.5 0.0 0.125
0.0 0.0 0.5 0.125
0.5 0.0 0.5 0.125
0.0 0.5 0.5 0.125
0.5 0.5 0.5 0.125
```

### K-point Weights and Symmetry

- Custom weights are preserved during symmetry reduction
- For Monkhorst-Pack grids: uniform weights (1/N)
- For explicit lists: custom weights preserved during IBZ reduction
- Weight normalization: sum equals `degspin` (2 non-spin, 1 spin-polarized)

Example with custom weights:
```
K_POINTS
5
Direct
0.0 0.0 0.0   0.1   // Gamma with weight 0.1
0.5 0.0 0.0   0.2   // X point with weight 0.2
0.0 0.5 0.0   0.3   // Y point with weight 0.3
0.5 0.5 0.0   0.2   // M point with weight 0.2
0.0 0.0 0.5   0.2   // Z point with weight 0.2
```

## Band Structure (Line Mode)

```
K_POINTS // keyword for start
6        // number of high symmetry lines
Line     // line-mode ('Line' = Direct, 'Line_Cartesian' = Cartesian)
0.5 0.0 0.5 20 // X
0.0 0.0 0.0 20 // Gamma
0.5 0.5 0.5 20 // L
0.5 0.25 0.75 20 // W
0.375 0.375 0.75 20 // K
0.0 0.0 0.0 1 // Gamma
```

Fourth line and following: special k-point coordinates and number of k-points between this and the next special point.

## Quick Start Example

```
K_POINTS
0
Gamma
4 4 4 0 0 0
```

This creates a standard 4x4x4 Gamma-centered k-mesh with no offset.
