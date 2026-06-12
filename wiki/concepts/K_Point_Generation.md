# K Point Generation K 点生成

> 类型：概念 / Concept
> 学科/领域：固体物理 / Solid State Physics

## 定义

K 点采样用于在布里渊区内进行积分，近似表示周期性体系的电子性质。

## ABACUS 实现

### KPT 文件控制
通过 KPT 文件或 INPUT 参数控制 K 点采样

### 生成模式

#### Gamma 单点
```
K_POINTS
0
Gamma
4 4 4 0 0 0
```
- 仅在 Gamma 点计算
- 适合大胞或分子

#### MP 网格
```
K_POINTS
0
mp
4 4 4 0 0 0
```
- Monkhorst-Pack 网格
- 位移由最后三个数字控制
- 0 0 0: 包含 Gamma 点
- 0.5 0.5 0.5: 不包含 Gamma 点

#### 显式坐标
```
K_POINTS
nk
direct
kx1 ky1 kz1 w1
kx2 ky2 kz2 w2
...
```
- 完全控制 K 点位置
- 适合特定路径计算

#### 能带路径
```
K_POINTS
nk
line
G 0 0 0
X 0.5 0 0
...
```
- 用于能带结构计算
- 需要高对称点坐标

## INPUT 参数覆盖

### gamma_only
```
gamma_only  1
```
- 覆盖 KPT 文件设置
- 强制使用 Gamma 单点
- 诊断 ABACUS209 警告

## 网格密度建议

### 简单立方
- 金属: 12×12×12 或更高
- 半导体: 8×8×8
- 绝缘体: 4×4×4

### 大胞
- 当胞内原子数 > 50，可减少网格
- 分子可用 Gamma 单点

## MatMaster 集成

### 最小密度检查
`.abacus-lsp/matmaster.json`:
```json
{
  "min_kpoint_grid": [4, 4, 4]
}
```
- 低于最小值报告 ABACUS420 警告

## 相关概念
- [[ABACUS_KPT]]
- [[Brillouin_Zone]]
- [[Band_Structure]]

## 来源
- `raw/assets/src/abacus_lsp/analyzer.py`
- `raw/assets/tests/fixtures/valid/`
