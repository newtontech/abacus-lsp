# ABACUS KPT 文件

> 类型：文件格式 / File Format
> 创建日期：2026-06-12
> 最后更新：2026-06-12
> 来源数：6

## 简介

ABACUS `KPT` 文件定义 K 点采样网格，用于布里渊区积分。支持自动生成 (Monkhorst-Pack)、显式列表和能带路径模式。可通过 `kpoint_file` 参数自定义文件名。

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
- Gamma 居中 Monkhorst-Pack 网格
- 前 3 个数字: 倒格子方向分割数
- 后 3 个数字: 网格偏移 (0 0 0 = 无偏移)

### MP (Monkhorst-Pack)
```
K_POINTS
0
MP
nkx nky nkz 0 0 0
```
- 标准 Monkhorst-Pack 网格
- 可能不包含 Gamma 点

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
- 每行 4 个数字: kx ky kz weight

#### K 点权重与对称性
- 自定义权重在对称性约化到 IBZ 时被保留
- MP 网格: 均匀权重 (1/N)
- 显式列表: 自定义权重在等效点合并时正确组合
- 权重归一化: 总和等于 degspin (非自旋=2, 自旋=1)

### Line / Line_Cartesian (能带路径)
```
K_POINTS
nk
Line
kx1 ky1 kz1 nk_between
kx2 ky2 kz2 nk_between
...
```
- 用于能带结构计算
- `Line` = Direct 坐标, `Line_Cartesian` = 笛卡尔坐标
- 第 4 个数字: 当前高对称点到下一点之间的 K 点数
- 需要与 `out_band=1` 配合使用

## Gamma-only 计算

设置 INPUT 中 `gamma_only=1` 启用 (仅 LCAO)。KPT 文件设置将被覆盖。多 K 点计算时确保关闭。

## 验证规则

- K 点数量必须与点行数匹配 (非自动模式)
- 自动网格模式需要一行网格参数
- `gamma_only=1` 会覆盖 KPT 文件设置
- 自定义权重应与晶体对称性一致

## 相关来源
- `raw/assets/abacus-kpt-format.md` - 完整 KPT 格式文档
- `raw/assets/abacus-quickstart-inputs.md` - 输入文件入门
- `raw/assets/tests/fixtures/valid/si_pw/KPT`
- 官方文档: http://abacus.deepmodeling.com/en/latest/advanced/input_files/kpt.html

## 相关实体/概念
- [[ABACUS_INPUT]]
- [[ABACUS_STRU]]
- [[K_Point_Generation]]
- [[Calculation_Types]]

## 历史更新
- 2026-06-12: 初始创建，从测试夹具和分析器提取
- 2026-06-12: 扩展为完整 KPT 格式参考，新增权重/对称性说明、Line 模式、Gamma-only 说明
