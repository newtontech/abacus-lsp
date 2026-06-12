# ABACUS INPUT 文件

> 类型：文件格式 / File Format
> 创建日期：2026-06-12
> 来源数：5

## 简介

ABACUS `INPUT` 文件是电子结构计算的主要控制文件，包含计算参数、方法和输出选项。它是 ABACUS 软件包的核心输入格式。

## 文件结构

### 必需头部
```
INPUT_PARAMETERS
```

### 参数格式
```
keyword  value  # optional comment
```

### 关键规则
- 所有参数必须在 `INPUT_PARAMETERS` 头部之后
- 使用 `#` 或 `/` 开始注释
- 参数名称不区分大小写
- 重复参数时，ABACUS 使用最后一个值

## 核心参数分类

### System / 系统参数
- `suffix`: 输出目录后缀
- `calculation`: 计算类型 (scf, relax, cell-relax, md, nscf, get_wf, get_pchg)

### Electronic Structure / 电子结构
- `basis_type`: 基组类型 (pw, lcao)
- `ecutwfc`: 平波能量截断 (Ry)
- `scf_thr`: SCF 收敛阈值
- `nspin`: 自旋极化模式 (1, 2, 4)
- `dft_plus_u`: 启用 DFT+U 修正

### Input Files / 输入文件
- `pseudo_dir`: 赝势文件目录
- `orbital_dir`: 数值轨道文件目录 (LCAO)
- `stru_file`: 结构文件路径 (默认: STRU)
- `kpoint_file`: K 点文件路径 (默认: KPT)

### K-points / K 点
- `gamma_only`: 使用 Gamma 单点计算

### Output / 输出
- `out_band`: 输出能带结构
- `out_dos`: 输出态密度

## 相关来源
- `raw/assets/docs/README.md`
- `raw/assets/src/abacus_lsp/schema.py`
- `raw/assets/schemas/abacus-builtin.json`

## 相关实体/概念
- [[ABACUS_STRU]]
- [[ABACUS_KPT]]
- [[ABACUS_File_Format]]
- [[KeywordSchema]]
- [[SchemaRegistry]]

## 历史更新
- 2026-06-12: 初始创建，从源代码和文档提取参数列表
