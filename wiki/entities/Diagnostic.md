# Diagnostic 诊断实体

> 类型：数据结构 / Data Structure
> 创建日期：2026-06-12
> 来源数：3

## 简介

`Diagnostic` 是 abacus-lsp 的核心诊断信息数据结构，用于表示 ABACUS 输入文件中的问题和警告。

## 数据结构

### 必需字段
```python
@dataclass
class Diagnostic:
    code: str           # 稳定的诊断代码 (如 "ABACUS001")
    severity: str       # "error", "warning", "information", "hint"
    message: str        # 人类可读的描述
    file: str           # 文件路径
    line: int           # 从 1 开始的行号
```

### 可选字段
```python
    column: int | None = None           # 列号
    end_line: int | None = None         # 范围结束行
    end_column: int | None = None       # 范围结束列
    suggested_fix: dict | None = None   # 建议的修复信息
    confidence: float | None = None     # 置信度 (0.0-1.0)
    evidence: list[str] | None = None  # 支持证据
```

## 诊断代码分类

### ABACUS001 系列：语法错误
- `ABACUS001`: INPUT_PARAMETERS 头部缺失
- `ABACUS002`: 未知的 INPUT 关键字
- `ABACUS004`: KPT 文件为空或格式错误
- `ABACUS005`: KPT 模式未知或参数错误
- `ABACUS006`: STRU 原子计数不匹配
- `ABACUS007`: INPUT 参数重复

### ABACUS101 系列：模式验证
- `ABACUS101`: 关键字值类型错误

### ABACUS201 系列：文件缺失
- `ABACUS201`: INPUT 文件缺失
- `ABACUS202`: KPT 文件缺失
- `ABACUS204`: 伪势或轨道文件不存在

### ABACUS205 系列：交叉文件
- `ABACUS205`: LCAO 基组缺少 NUMERICAL_ORBITAL
- `ABACUS206`: 轨道数量与元素数量不匹配
- `ABACUS207`: ATOMIC_SPECIES 与 ATOMIC_POSITIONS 顺序不一致
- `ABACUS208`: latname 与 LATTICE_VECTORS 冲突
- `ABACUS209`: gamma_only 覆盖 KPT 设置

### ABACUS301 系列：运行时错误
- `ABACUS301`: SCF 收敛失败
- `ABACUS302`: 几何优化未收敛
- `ABACUS303`: 段错误检测
- `ABACUS304`: 文件错误
- `ABACUS308`: MD 参数缺失
- `ABACUS309`: 内存分配错误

### ABACUS401 系列：第三方集成
- `ABACUS401`: APNS 伪势不在库存中
- `ABACUS402`: APNS 轨道不在库存中
- `ABACUS420`: KPT 网格低于 MatMaster 最小密度
- `ABACUS421`: 路径包含父目录引用
- `ABACUS422`: MatMaster LCAO 作业需要显式轨道

## 严重性策略

### error
- 高置信度的语法、模式、类型/值或引用问题
- 应阻止自动提交，因为上游运行时可能会拒绝输入

### warning
- 高风险或可疑输入，可能是有意的
- 应向代理显示，不自动阻止修复循环

### information / hint
- 样式、文档或可选优化信息

## 相关来源
- `raw/assets/src/abacus_lsp/diagnostics.py`
- `raw/assets/src/abacus_lsp/analyzer.py`
- `raw/assets/diagnostics/diagnostic-engine-v1.schema.json`

## 相关实体/概念
- [[Diagnostic_Engine_v1]]
- [[Rich_Diagnostic_Shape]]
- [[Severity_Policy]]

## 历史更新
- 2026-06-12: 初始创建，从诊断模块和分析器提取
