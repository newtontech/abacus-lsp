# Cross File Diagnostics 交叉文件诊断

> 类型：概念 / Concept
> 学科/领域：电子结构计算 / Electronic Structure

## 定义

交叉文件诊断分析 ABACUS 计算案例的多个输入文件之间的一致性和依赖关系，确保 INPUT、STRU 和 KPT 文件的配置相互匹配。

## 核心机制

### 分析流程
1. 解析 INPUT 文件获取参数
2. 根据 INPUT 中的 `stru_file` 和 `kpoint_file` 参数解析 STRU 和 KPT
3. 检查跨文件依赖和一致性

### 检查规则

#### LCAO 基组验证
- `basis_type=lcao` 时，STRU 必须包含 NUMERICAL_ORBITAL 节
- 否则报告 ABACUS205 错误

#### 元素一致性
- ATOMIC_SPECIES 和 ATOMIC_POSITIONS 的元素顺序应一致
- 否则报告 ABACUS207 警告

#### 轨道数量匹配
- NUMERICAL_ORBITAL 数量必须与 ATOMIC_POSITIONS 元素数量匹配
- 否则报告 ABACUS206 警告

#### 晶格参数冲突
- `latname` 和 LATTICE_VECTORS 不应同时使用
- 否则报告 ABACUS208 警告

#### Gamma 覆盖
- `gamma_only=1` 会忽略 KPT 文件的多 K 点设置
- 报告 ABACUS209 警告

#### 文件存在性
- 检查 `pseudo_dir` 中的赝势文件是否存在
- 检查 `orbital_dir` 中的轨道文件是否存在
- 缺失文件报告 ABACUS204 警告

## 应用场景

### 静态分析
```bash
abacus-lint ./case --json
```
对计算案例进行完整的交叉文件验证

### LSP 诊断
编辑器中实时显示跨文件问题

### MatMaster 集成
额外的材料计算平台验证规则：
- KPT 网格密度最小值 (ABACUS420)
- 禁止父目录路径引用 (ABACUS421)
- LCAO 作业需要显式轨道 (ABACUS422)

## 相关概念
- [[Workflow_Diagnostics]]
- [[ABACUS_INPUT]]
- [[ABACUS_STRU]]
- [[ABACUS_KPT]]

## 来源
- `raw/assets/src/abacus_lsp/analyzer.py`
