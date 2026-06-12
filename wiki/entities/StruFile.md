# StruFile 数据结构

> 类型：数据结构 / Data Structure
> 创建日期：2026-06-12
> 来源数：2

## 简介

`StruFile` 是 ABACUS STRU 文件的内存表示，包含解析后的节信息和元素列表。

## 数据结构

```python
@dataclass
class StruFile:
    path: Path                              # 文件路径
    sections: set[str]                      # 出现的节集合
    species: list[str]                      # ATOMIC_SPECIES 元素列表
    pseudopotentials: list[str]             # 赝势文件列表
    orbitals: list[str]                     # 数值轨道文件列表
    position_elements: list[str]           # ATOMIC_POSITIONS 元素列表
    diagnostics: list[Diagnostic]          # 诊断列表
```

## 已知节类型

```python
KNOWN_STRU_SECTIONS = {
    "ATOMIC_SPECIES",
    "NUMERICAL_ORBITAL",
    "LATTICE_CONSTANT",
    "LATTICE_VECTORS",
    "LATTICE_PARAMETERS",
    "ATOMIC_POSITIONS",
}
```

## 节解析规则

### ATOMIC_SPECIES
格式: `Element Mass Pseudopotential`
- 记录元素名和赝势文件名

### NUMERICAL_ORBITAL
格式: `Element.orb`
- 记录轨道文件名
- 必须与 ATOMIC_POSITIONS 元素数量匹配

### LATTICE_CONSTANT
格式: 单个数值
- 晶格常数标度因子

### LATTICE_VECTORS
格式: 三行三维向量
- 每行: `vx vy vz`

### LATTICE_PARAMETERS
格式: `a b c alpha beta gamma`
- 晶格参数和角度

### ATOMIC_POSITIONS
格式:
```
Coordinate_Mode  # Direct or Cartesian
Element
magnetic_moment
atom_count
x1 y1 z1
...
```
- 记录元素名
- 验证原子计数与行数匹配

## 解析器行为

- 节名不区分大小写
- 空行和注释行跳过
- 遇到未知节时跳过并继续
- 不完整元素块时产生诊断

## 相关来源
- `raw/assets/src/abacus_lsp/analyzer.py`
- `raw/assets/tests/fixtures/valid/`

## 相关实体/概念
- [[ABACUS_STRU]]
- [[InputFile]]
- [[KptFile]]

## 历史更新
- 2026-06-12: 初始创建，从分析器和测试夹具提取
