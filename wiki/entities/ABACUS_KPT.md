# ABACUS KPT 文件

> 类型：文件格式 / File Format
> 创建日期：2026-06-12
> 来源数：4

## 简介

ABACUS `KPT` 文件定义 K 点采样网格，用于布里渊区积分。支持多种生成模式和显式 K 点列表。

## 文件结构

### 必需头部
```
K_POINTS
```
或
```
KPOINTS
K
```

### 格式
```
K_POINTS
nk  # K 点数量，0 表示自动生成
mode  # 生成模式
...
```

## K 点模式

### Gamma (自动网格)
```
K_POINTS
0
Gamma
nkx nky nkz 0 0 0
```
- 使用 Monkhorst-Pack 网格原点偏移

### MP (Monkhorst-Pack)
```
K_POINTS
0
mp
nkx nky nkz 0 0 0
```

### Direct / Cartesian (显式列表)
```
K_POINTS
nk
direct  # 或 cartesian
kx1 ky1 kz1 weight1
...
```
- 必须指定 nk > 0
- 行数必须与 nk 匹配

### Line / Line_Cartesian (能带路径)
```
K_POINTS
nk
line
kx1 ky1 kz1
kx2 ky2 kz2
...
```
- 用于能带结构计算
- 需要与 `out_band=1` 配合使用

## 验证规则

- K 点数量必须与点行数匹配 (非自动模式)
- 自动网格模式需要一行网格参数
- `gamma_only=1` 会覆盖 KPT 文件设置

## 相关来源
- `raw/assets/tests/fixtures/valid/si_pw/KPT`
- `raw/assets/src/abacus_lsp/analyzer.py`

## 相关实体/概念
- [[ABACUS_INPUT]]
- [[ABACUS_STRU]]
- [[Band_Structure]]

## 历史更新
- 2026-06-12: 初始创建，从测试夹具和分析器提取
