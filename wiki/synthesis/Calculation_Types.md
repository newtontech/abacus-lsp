# Calculation Types 计算类型

> 创建日期：2026-06-12
> 最后更新：2026-06-12
> 覆盖来源：3

## 核心论点

ABACUS 支持多种电子结构计算类型，通过 `calculation` 参数控制，每种类型有不同的参数需求和输出特性。

## 计算类型列表

### scf (Self-Consistent Field)
**描述**: 自洽场电子结构计算，最基本的计算类型

**典型用途**:
- 获取基态电子密度
- 为后续计算提供波函数初值
- 能量和力的收敛计算

**必需参数**:
- `basis_type`: pw 或 lcao
- `ecutwfc`: 平面波截断 (PW)
- `scf_thr`: 收敛阈值

**可选输出**:
- `out_dos`: 态密度

### relax (Geometry Optimization)
**描述**: 固定晶胞的原子位置优化

**典型用途**:
- 获取平衡几何结构
- 表面吸附构型优化
- 分子结构优化

**额外参数**:
- `relax_nmax`: 最大优化步数
- `force_thr_ev`: 力收敛阈值

### cell-relax (Variable Cell Optimization)
**描述**: 同时优化原子位置和晶胞参数

**典型用途**:
- 晶格常数优化
- 相变研究
- 压强-体积关系

**额外参数**:
- `relax_nmax`: 最大优化步数
- `press`: 目标压强

### md (Molecular Dynamics)
**描述**: 第一性原理分子动力学

**典型用途**:
- 有限温度性质
- 扩散系数
- 相变动力学

**必需参数** (诊断提示):
- `md_nstep`: MD 步数
- `md_dt`: 时间步长

**诊断**: ABACUS308 提示缺少 MD 参数

### nscf (Non-Self-Consistent Field)
**描述**: 基于已有电荷密度的非自洽计算

**典型用途**:
- 能带结构计算
- 精细态密度
- 光学性质计算

**典型输出**:
- `out_band`: 能带结构
- `out_dos`: 态密度

### get_wf (Get Wavefunction)
**描述**: 输出波函数

**典型用途**:
- 后处理分析
- 可视化

### get_pchg (Get Partial Charge)
**描述**: 输出分波电荷密度

**典型用途**:
- 键合分析
- 电荷转移分析

## 工作流建议

### 标准能带计算流程
1. scf: 获取收敛电荷密度
2. nscf + out_band: 计算能带

### 标准态密度流程
1. scf: 自洽计算
2. nscf + out_dos: 更密集 k 点网格的态密度

### 诊断支持
- `out_band=1` 但 KPT 非 Line 模式: ABACUS305
- `out_dos=1` 但非 scf/nscf: ABACUS306

## 相关来源
- `raw/assets/src/abacus_lsp/schema.py`
- `raw/assets/tests/fixtures/valid/`
- `raw/assets/src/abacus_lsp/analyzer.py`

## 来源列表
- KeywordSchema.calculation enum
- 测试夹具示例
- 工作流诊断规则
