# ABACUS STRU 文件

> 类型：文件格式 / File Format
> 创建日期：2026-06-12
> 最后更新：2026-06-12
> 来源数：7

## 简介

ABACUS `STRU` 文件描述原子结构，包括晶格常数、晶格矢量、原子种类、原子位置、赝势和数值轨道信息。可通过 `stru_file` 参数自定义文件名。

## 文件结构

### 必需/可选节

#### ATOMIC_SPECIES (必需)
```
ATOMIC_SPECIES
Element  Mass  Pseudopotential_File  [Pseudo_Type]
```
- 每行一个元素
- 格式：元素名、原子质量、赝势文件名、赝势类型(可选)
- 赝势类型: `upf`, `upf201`, `vwr`, `blps`, `auto`(默认)
- 质量仅在 MD 中使用，电子结构计算中不重要
- 不同元素可用不同赝势类型，但 XC 泛函应一致
- `esolver_type=lj` 或 `dp` 时不需要赝势

#### NUMERICAL_ORBITAL (LCAO 必需)
```
NUMERICAL_ORBITAL
Element.orb
```
- 每行一个数值轨道文件
- 顺序必须与 ATOMIC_POSITIONS 中的元素顺序一致
- PW 计算时忽略此节
- 可从 ABACUS 官网下载，推荐 APNSv1.0 集

#### LATTICE_CONSTANT (必需)
```
LATTICE_CONSTANT
value
```
- 晶格常数标度因子 (单位: Bohr)
- 1 Angstrom = 1.889726125457828 Bohr

#### LATTICE_VECTORS 或 LATTICE_PARAMETERS
```
LATTICE_VECTORS
v1x v1y v1z
v2x v2y v2z
v3x v3y v3z
```
- 矢量按晶格常数缩放
- 使用 `latname` 时必须删除此节

使用 `latname` 时的 LATTICE_PARAMETERS:
| latname | 参数 | 说明 |
|---------|------|------|
| sc, fcc, bcc | 无 | 简单/面心/体心立方 |
| hexagonal | c/a | 六方 |
| trigonal | cos(gamma) | 三方 |
| st, bct | c/a | 简单/体心四方 |
| so, baco, fco, bco | b/a, c/a | 正交 |
| sm, bacm | b/a, c/a, cos(ab) | 单斜 |
| triclinic | b/a, c/a, cos(ab), cos(ac), cos(bc) | 三斜 |

#### ATOMIC_POSITIONS (必需)
```
ATOMIC_POSITIONS
Coordinate_Mode
Element
magnetic_moment
atom_count
x y z [keyword value ...]
...
```

**坐标模式**:
- `Direct`: 分数坐标
- `Cartesian`: 笛卡尔坐标 (LATTICE_CONSTANT 单位)
- `Cartesian_au`: 笛卡尔 (Bohr)
- `Cartesian_angstrom`: 笛卡尔 (Angstrom)
- `Cartesian_angstrom_center_xy/xz/yz/xyz`: 以指定 Direct 点为参考的 Angstrom 坐标

**每原子关键字** (坐标后，可任意顺序):
| 关键字 | 说明 | 示例 |
|--------|------|------|
| `m` (或无) | 移动标志 0/1 | `m 0 0 0` |
| `v`/`vel`/`velocity` | 初始速度 | `v 1.0 1.0 1.0` |
| `mag`/`magmom` | 起始磁化 | `mag 1.0` 或 `mag 0 0 1` |
| `angle1` | 极角 (度) | `angle1 90` |
| `angle2` | 方位角 (度) | `angle2 0` |
| `lambda` | 自旋约束 Lagrange 乘子 (eV) | `lambda 0.5` |
| `sc` | 自旋约束目标磁化 | `sc 1.0` |

**磁化默认**: nspin=2 无显式 mag 时自动设 1.0; nspin=4 时设 (1,1,1)

## 交叉文件验证规则

- `basis_type=lcao` 时必须有 NUMERICAL_ORBITAL
- NUMERICAL_ORBITAL 数量必须与 ATOMIC_POSITIONS 元素数量匹配
- ATOMIC_SPECIES 和 ATOMIC_POSITIONS 的元素顺序应一致
- `latname` 和 LATTICE_VECTORS 不应同时使用
- 不应在同一 STRU 文件中混用 Direct 和 Cartesian 坐标
- 原子数必须与实际坐标行数匹配

## 相关来源
- `raw/assets/abacus-stru-format.md` - 完整 STRU 格式文档
- `raw/assets/abacus-quickstart-inputs.md` - 输入文件入门
- `raw/assets/abacus-examples.md` - MgO 示例
- `raw/assets/tests/fixtures/valid/si_pw/STRU`
- `raw/assets/tests/fixtures/valid/mgo_lcao/STRU`
- 官方文档: http://abacus.deepmodeling.com/en/latest/advanced/input_files/stru.html

## 相关实体/概念
- [[ABACUS_INPUT]]
- [[ABACUS_KPT]]
- [[Cross_File_Diagnostics]]
- [[Pseudopotentials]]
- [[Numerical_Orbitals]]

## 历史更新
- 2026-06-12: 初始创建，从测试夹具和分析器提取结构
- 2026-06-12: 大幅扩展，新增完整节格式、坐标模式、每原子关键字、Bravais 晶格类型表
