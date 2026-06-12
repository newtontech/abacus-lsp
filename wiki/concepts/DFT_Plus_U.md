# DFT+U 方法

> 类型：概念 / Concept
> 学科/领域：密度泛函理论 / Density Functional Theory

## 定义

DFT+U 是对标准密度泛函理论的修正方法，用于改善对强关联电子系统（如 d 轨道和 f 轨道元素）的描述。

## ABACUS 实现

### 启用 DFT+U
在 INPUT 文件中设置：
```
dft_plus_u  1
```

### 所需参数

除了启用开关外，还需要配置：
- `hubbard_u`: 各元素的 Hubbard U 参数
- `orbital_corr`: 需要修正的轨道角动量

## 诊断规则

### 配置完整性检查
- `dft_plus_u=1` 但缺少 Hubbard U 详细参数时
- 报告 ABACUS304 警告
- 建议添加 `hubbard_u` 和 `orbital_corr` 参数

## 典型应用

### 过渡金属氧化物
- Fe, Co, Ni, Cu 等元素的氧化物
- 改善带隙和磁性质的描述

### 稀土化合物
- 镧系和锕系元素
- 4f 电子的局域化处理

### 典型元素
- 第一过渡金属系: Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn
- 部分镧系元素

## 相关概念
- [[Electronic_Structure]]
- [[Hubbard_U]]
- [[Strongly_Correlated_Systems]]

## 来源
- `raw/assets/src/abacus_lsp/analyzer.py`
