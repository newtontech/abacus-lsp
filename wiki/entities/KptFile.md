# KptFile 数据结构

> 类型：数据结构 / Data Structure
> 创建日期：2026-06-12
> 来源数：2

## 简介

`KptFile` 是 ABACUS KPT 文件的内存表示，包含 K 点模式、数量和坐标列表。

## 数据结构

```python
@dataclass
class KptFile:
    path: Path                           # 文件路径
    mode: str | None                     # K 点生成模式
    count: int | None                    # K 点数量
    rows: list[tuple[int, str]]          # K 点行 (行号, 内容)
    diagnostics: list[Diagnostic]        # 诊断列表
```

## 已知模式

```python
KNOWN_KPT_MODES = {
    "gamma",           # Gamma 单点
    "mp",              # Monkhorst-Pack 自动网格
    "direct",          # 倒空间显式坐标
    "cartesian",       # 实空间显式坐标
    "line",            # 倒空间能线路径
    "line_cartesian",  # 实空间能线路径
}
```

## 文件格式

### 头部
三种形式均可:
```
K_POINTS
KPOINTS
K
```

### 内容结构
```
K_POINTS
nk          # K 点数量，0 表示自动生成
mode        # 生成模式
...         # 根据 mode 的不同格式
```

### 模式详解

#### Gamma / MP (自动网格)
```
nk = 0
mode = Gamma or mp
一行: nkx nky nkz 0 0 0
```

#### Direct / Cartesian (显式列表)
```
nk > 0
mode = direct or cartesian
nk 行: kx ky kz weight
```

#### Line / Line_Cartesian (能带路径)
```
nk > 0
mode = line or line_cartesian
2*nk 行: 路径点的起点和终点
```

## 验证规则

### 必需验证
- 文件不能为空
- 头部必须是 K_POINTS/KPOINTS/K
- 点数量必须是整数
- 模式必须在 KNOWN_KPT_MODES 中

### 一致性验证
- 当 nk > 0 且模式为显式坐标时，行数必须与 nk 匹配
- 当 nk = 0 且模式为自动网格时，必须有一行网格参数

## 解析器行为

- 忽略空行和注释行
- 模式名称不区分大小写
- 无效格式产生诊断但不中断解析

## 相关来源
- `raw/assets/src/abacus_lsp/analyzer.py`
- `raw/assets/tests/fixtures/valid/`

## 相关实体/概念
- [[ABACUS_KPT]]
- [[InputFile]]
- [[StruFile]]
- [[K_Point_Generation]]

## 历史更新
- 2026-06-12: 初始创建，从分析器和测试夹具提取
