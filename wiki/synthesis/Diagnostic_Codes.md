# Diagnostic Codes Reference 诊断代码参考

> 创建日期：2026-06-12
> 最后更新：2026-06-12
> 覆盖来源：2

## 核心论点

abacus-lsp 使用结构化的诊断代码系统，每个代码对应特定的检查规则，支持自动修复和代理集成。

## 代码分类

### 1xx 系列：INPUT 文件语法

| 代码 | 严重性 | 描述 | 修复建议 |
|------|--------|------|----------|
| ABACUS001 | error | INPUT_PARAMETERS 头部缺失 | 添加 INPUT_PARAMETERS 头 |
| ABACUS002 | warning | 未知的 INPUT 关键字 | 检查拼写或查阅文档 |
| ABACUS007 | warning | 参数重复 | 保留最后一个值 |

### 1xx 系列：模式验证

| 代码 | 严重性 | 描述 | 修复建议 |
|------|--------|------|----------|
| ABACUS101 | error | 关键字值类型错误 | 修正为正确类型 |

### 2xx 系列：文件存在性

| 代码 | 严重性 | 描述 | 修复建议 |
|------|--------|------|----------|
| ABACUS201 | error | INPUT 文件缺失 | 创建 INPUT 文件 |
| ABACUS202 | error | KPT 文件缺失 | 创建 KPT 文件 |
| ABACUS204 | warning | 伪势/轨道文件不存在 | 检查路径或提供文件 |

### 2xx 系列：STRU 文件

| 代码 | 严重性 | 描述 | 修复建议 |
|------|--------|------|----------|
| ABACUS004 | error | KPT 文件为空 | 添加 K 点数据 |
| ABACUS005 | error | KPT 模式/参数错误 | 修正模式或参数 |
| ABACUS006 | error | 原子计数不匹配 | 检查计数和行数 |

### 2xx 系列：交叉文件

| 代码 | 严重性 | 描述 | 修复建议 |
|------|--------|------|----------|
| ABACUS205 | error | LCAO 缺少 NUMERICAL_ORBITAL | 添加轨道节 |
| ABACUS206 | warning | 轨道与元素数量不匹配 | 检查轨道列表 |
| ABACUS207 | warning | ATOMIC_SPECIES/POSITIONS 顺序不一致 | 统一顺序 |
| ABACUS208 | warning | latname 与 LATTICE_VECTORS 冲突 | 选择一种方式 |
| ABACUS209 | warning | gamma_only 覆盖 KPT | 确认意图 |

### 3xx 系列：运行时诊断

| 代码 | 严重性 | 描述 | 修复建议 |
|------|--------|------|----------|
| ABACUS301 | error | SCF 收敛失败 | 增加步数或放宽阈值 |
| ABACUS302 | error | 几何优化未收敛 | 增加步数或调整 BFGS |
| ABACUS303 | error | 段错误检测 | 检查输入或减少系统规模 |
| ABACUS304 | error/warning | 文件错误 / DFT+U 不完整 | 检查路径 / 添加 Hubbard U |
| ABACUS308 | hint | MD 参数缺失 | 添加 md_nstep, md_dt |
| ABACUS309 | error | 内存分配错误 | 减少内存使用或增加资源 |

### 4xx 系列：第三方集成

| 代码 | 严重性 | 描述 | 修复建议 |
|------|--------|------|----------|
| ABACUS401 | warning | APNS 伪势不在库存 | 选择库存伪势 |
| ABACUS402 | warning | APNS 轨道不在库存 | 选择库存轨道 |
| ABACUS420 | warning | KPT 网格低于最小值 | 增加网格密度 |
| ABACUS421 | warning | 路径包含父目录引用 | 使用相对路径 |
| ABACUS422 | error | MatMaster LCAO 需要轨道 | 添加 NUMERICAL_ORBITAL |

## 修复建议类型

### kind 字段值
- `check_keyword_spelling`: 检查关键字拼写
- `replace_value`: 替换值
- `insert_section`: 插入节
- `increase_scf_steps_or_threshold`: 增加 SCF 步数或阈值
- `increase_relax_steps_or_adjust_bfgs`: 增加弛豫步数或调整 BFGS
- `check_input_or_reduce_system_size`: 检查输入或减少规模
- `verify_file_paths_in_input`: 验证文件路径
- `reduce_memory_usage_or_increase_resources`: 减少内存或增加资源
- `choose_apns_pseudopotential`: 选择 APNS 伪势
- `choose_apns_orbital`: 选择 APNS 轨道
- `increase_kpt_grid`: 增加 KPT 网格

## 相关来源
- `raw/assets/src/abacus_lsp/analyzer.py`
- `raw/assets/src/abacus_lsp/diagnostics.py`

## 来源列表
- 解析器诊断规则
- 交叉文件检查
- 日志解析器
