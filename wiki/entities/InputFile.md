# InputFile 数据结构

> 类型：数据结构 / Data Structure
> 创建日期：2026-06-12
> 来源数：2

## 简介

`InputFile` 是 ABACUS INPUT 文件的内存表示，包含解析后的参数、条目和诊断信息。

## 数据结构

```python
@dataclass
class InputFile:
    path: Path                              # 文件路径
    entries: list[InputEntry]               # 关键字条目列表
    parameters: dict[str, str]              # 参数名到值的映射
    parameter_lines: dict[str, list[int]]   # 参数名到行号的映射
    diagnostics: list[Diagnostic]           # 诊断列表
```

## InputEntry 条目结构

```python
@dataclass
class InputEntry:
    name: str      # 关键字名称 (小写)
    value: str     # 原始值字符串
    comment: str   # 注释内容
    line: int      # 行号 (从 1 开始)
    column: int    # 列号 (从 1 开始)
    raw: str       # 原始行内容
```

## 解析规则

### 注略规则
- 以 `#` 或 `/` 开头的行视为注释
- 行内注释以 `#` 分隔

### 头部识别
- `INPUT_PARAMETERS` 头部必须出现
- 头部前的任何非空内容会被忽略

### 参数解析
- 关键字不区分大小写 (转换为小写存储)
- 关键字和值以空格分隔
- 值可以是多词 (取第一个词用于类型检查)

### 重复处理
- 重复参数保留最后一个值
- 重复行会记录在 `parameter_lines` 中

## 典型用法

```python
# 解析 INPUT 文件
input_file = parse_input(case_dir / "INPUT", registry)

# 访问参数
calculation = input_file.parameters.get("calculation", "scf")
ecutwfc = input_file.parameters.get("ecutwfc", "50")

# 获取参数位置
lines = input_file.parameter_lines.get("calculation", [1])

# 检查诊断
if input_file.diagnostics:
    for diag in input_file.diagnostics:
        print(f"{diag.code}: {diag.message}")
```

## 相关来源
- `raw/assets/src/abacus_lsp/analyzer.py`

## 相关实体/概念
- [[ABACUS_INPUT]]
- [[StruFile]]
- [[KptFile]]
- [[InputEntry]]

## 历史更新
- 2026-06-12: 初始创建，从分析器模块提取
