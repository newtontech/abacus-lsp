# ABACUS STRU 文件

> 类型：文件格式 / File Format
> 创建日期：2026-06-12
> 来源数：4

## 简介

ABACUS `STRU` 文件描述原子结构，包括晶格常数、晶格矢量、原子种类、原子位置和数值轨道信息。

## 文件结构

### 必需/可选节

#### ATOMIC_SPECIES (必需)
```
ATOMIC_SPECIES
Element  Mass  Pseudopotential_File
```
- 每行一个元素
- 格式：元素名、原子质量、赝势文件名

#### NUMERICAL_ORBITAL (LCAO 必需)
```
NUMERICAL_ORBITAL
Element.orb
```
- 每行一个数值轨道文件
- 顺序必须与 ATOMIC_POSITIONS 中的元素顺序一致

#### LATTICE_CONSTANT (必需)
```
LATTICE_CONSTANT
value
```
- 晶格常数标度因子

#### LATTICE_VECTORS 或 LATTICE_PARAMETERS
```
LATTICE_VECTORS
v1x v1y v1z
v2x v2y v2z
v3x v3y v3z
```
或
```
LATTICE_PARAMETERS
a b c alpha beta gamma
```

#### ATOMIC_POSITIONS (必需)
```
ATOMIC_POSITIONS
Coordinate_Mode  # Direct or Cartesian
Element
magnetic_moment
atom_count
x1 y1 z1
...
```

## 交叉文件验证规则

- `basis_type=lcao` 时必须有 NUMERICAL_ORBITAL
- NUMERICAL_ORBITAL 数量必须与 ATOMIC_POSITIONS 元素数量匹配
- ATOMIC_SPECIES 和 ATOMIC_POSITIONS 的元素顺序应一致
- `latname` 和 LATTICE_VECTORS 不应同时使用

## 相关来源
- `raw/assets/tests/fixtures/valid/si_pw/STRU`
- `raw/assets/tests/fixtures/valid/mgo_lcao/STRU`
- `raw/assets/src/abacus_lsp/analyzer.py`

## 相关实体/概念
- [[ABACUS_INPUT]]
- [[ABACUS_KPT]]
- [[Cross_File_Diagnostics]]

## 历史更新
- 2026-06-12: 初始创建，从测试夹具和分析器提取结构
