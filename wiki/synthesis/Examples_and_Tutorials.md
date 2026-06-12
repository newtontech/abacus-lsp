# Examples and Tutorials 示例与教程

> 类型：综合页面 / Synthesis
> 创建日期：2026-06-12
> 来源数：5

## 核心论点

ABACUS 提供完整的 SCF、几何优化和分子动力学示例，支持 PW 和 LCAO 两种基组。官方文档站提供从入门到高级的完整教程体系。

## SCF 计算

### LCAO 示例 (FCC MgO)

**INPUT**:
```
INPUT_PARAMETERS
suffix          MgO
pseudo_dir      ./
orbital_dir     ./
ecutwfc         100    # Ry
scf_thr         1e-6
basis_type      lcao
calculation     scf
```

**KPT**:
```
K_POINTS
0
Gamma
4 4 4 0 0 0
```

**STRU**: MgO 面心立方，4 个 Mg + 4 个 O 原子

**运行**: `OMP_NUM_THREADS=1 mpirun -np 2 abacus`

**结果**: `!FINAL_ETOT_IS -7663.897267807250 eV`

### PW 示例 (FCC MgO)

与 LCAO 相同，仅改 `basis_type pw` 并移除 STRU 中 NUMERICAL_ORBITAL 节。

**结果**: `!FINAL_ETOT_IS -7665.688319476949 eV`

## 几何优化

### cell-relax (LCAO/PW)
```
INPUT_PARAMETERS
calculation     cell-relax
force_thr_ev    0.01     # eV/Angstrom
stress_thr      5        # kBar
relax_nmax      100
```

输出: `STRU_NOW.cif` 和 `OUT.MgO/running_cell-relax.log`

## LCAO vs PW 对比

| 方面 | LCAO | PW |
|------|------|-----|
| `basis_type` | lcao | pw |
| 轨道文件 | STRU 中需要 | 不需要 |
| `ecutwfc` 默认 | 100 Ry | 50 Ry |
| `scf_thr` 推荐 | 1e-7 | 1e-9 |
| 速度 | 大体系更快 | 设置更简单 |
| 精度 | 依赖轨道质量 | 系统性收敛 |

## 官方文档结构

```
Quick Start/
├── Easy Installation
├── Two Quick Examples
├── Input Files Introduction
└── Output Files Introduction

Advanced/
├── Running SCF (初始化/构建哈密顿/求解/收敛/加速/复杂环境/SOC)
├── Basis Set and Pseudopotentials
├── Geometry Optimization
├── Molecular Dynamics
├── Electronic Properties (能带/DOS/Mulliken/静电势/波函数/...)
├── Output Files (规范/running_scf.log/偶极矩)
├── Interfaces (PyABACUS/DeePKS/DP-GEN/DeepH/Phonopy/Wannier90/ASE/...)
└── Input Files (INPUT 关键字/STRU/KPT)
```

## 接口集成

| 接口 | 说明 |
|------|------|
| PyABACUS | Python 接口 |
| DeePKS | 深度学习 Kohn-Sham |
| DP-GEN | Deep Potential 生成器 |
| DeepH | 深度学习哈密顿 |
| DeePTB | 深度学习紧束缚 |
| Phonopy | 声子计算 |
| Wannier90 | Wannier 函数 |
| ASE | 原子模拟环境 |

## 相关来源
- `raw/assets/abacus-examples.md` - 完整计算示例
- `raw/assets/abacus-tutorials.md` - 教程资源汇总
- `raw/assets/abacus-quickstart-inputs.md` - 输入文件入门
- `raw/assets/abacus-readme.md` - GitHub README
- 官方文档: http://abacus.deepmodeling.com/

## 相关实体/概念
- [[ABACUS_INPUT]]
- [[ABACUS_STRU]]
- [[ABACUS_KPT]]
- [[Basis_Set_Types]]
- [[Calculation_Types]]
