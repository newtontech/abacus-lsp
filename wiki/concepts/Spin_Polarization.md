# Spin Polarization 自旋极化

> 类型：概念 / Concept
> 学科/领域：量子力学 / Quantum Mechanics

## 定义

自旋极化计算考虑电子自旋自由度，用于描述磁性体系和开壳层系统。

## ABACUS 实现

### nspin 参数
```
nspin  1  # 非极化
nspin  2  # 自旋极化
nspin  4  # 非共线自旋
```

### 模式详解

#### nspin = 1 (非极化)
- 每个轨道占据 2 个电子 (自旋向上和向下)
- 适合闭壳层体系
- 最小计算量

#### nspin = 2 (自旋极化)
- 分别处理自旋向上和向下电子
- 适合开壳层体系和磁性材料
- 需要初始磁矩设置

#### nspin = 4 (非共线自旋)
- 处理自旋轨道耦合
- 适合复杂磁性体系
- 计算量最大

## STRU 文件配置

### 磁矩设置
在 ATOMIC_POSITIONS 节中:
```
ATOMIC_POSITIONS
Direct
Fe
2.0    # 初始磁矩
1
0.0 0.0 0.0
```

## 典型应用

### 铁磁体
- Fe, Co, Ni 等过渡金属
- `nspin=2` + 初始磁矩

### 反铁磁体
- 需要仔细设置初始磁矩方向
- 可能需要超胞

### 自旋轨道耦合
- 重元素系统
- `nspin=4`

## 诊断支持

当前无特定诊断，但关键字模式包含 `nspin`:
```python
KeywordSchema(
    "nspin",
    "Integer",
    None,
    "1",
    "Spin",
    "Spin-polarization mode.",
    ["PW", "LCAO"],
    ["1", "2", "4"],
    "builtin",
)
```

## 相关概念
- [[Electronic_Structure]]
- [[Magnetic_Systems]]
- [[DFT_Plus_U]]

## 来源
- `raw/assets/src/abacus_lsp/schema.py`
