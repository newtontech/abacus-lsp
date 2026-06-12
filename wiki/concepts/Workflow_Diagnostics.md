# Workflow Diagnostics 工作流诊断

> 类型：概念 / Concept
> 学科/领域：计算材料学 / Computational Materials Science

## 定义

工作流诊断检查 ABACUS 计算工作流的语义合理性，确保输出选项与计算类型匹配，并检测潜在配置错误。

## 核心机制

### 检查类别

#### 能带结构输出验证
- `out_band=1` 启用时，KPT 应为 Line 或 Line_Cartesian 模式
- 否则报告 ABACUS305 信息

#### 态密度输出验证
- `out_dos=1` 通常应在 scf 或 nscf 计算中使用
- 在其他计算类型中报告 ABACUS306 提示

#### DFT+U 配置完整性
- `dft_plus_u=1` 启用时，需要配置 Hubbard U 参数
- 缺少 `hubbard_u` 或 `orbital_corr` 参数报告 ABACUS304 警告

#### 分子动力学参数
- `calculation=md` 时应设置 `md_nstep` 和 `md_dt`
- 缺失参数报告 ABACUS308 提示

## 应用场景

### 计算前验证
在提交 ABACUS 计算前验证工作流配置的合理性

### 自动化工作流
确保代理生成的输入文件具有一致的工作流设置

### 教学场景
帮助新手了解不同计算类型所需的参数配置

## 真值判断

辅助函数 `_truthy()` 判断布尔字符串：
- 接受: "1", "true", "t", "yes"
- 大小写不敏感
- 空字符串为 False

## 相关概念
- [[Cross_File_Diagnostics]]
- [[ABACUS_INPUT]]
- [[Calculation_Type]]

## 来源
- `raw/assets/src/abacus_lsp/analyzer.py`
