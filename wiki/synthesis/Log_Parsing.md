# Log Parsing 日志解析

> 创建日期：2026-06-12
> 最后更新：2026-06-12
> 覆盖来源：2

## 核心论点

abacus-lsp 可以解析 ABACUS 运行时日志文件，检测计算失败和错误模式，提供运行时反馈。

## 支持的日志文件

### 搜索顺序
1. `running.log`
2. `run.log`
3. `OUT.ABACUS/running_0.log`

### 解析触发
当案例目录中存在任一日志文件时自动解析

## 检测的错误模式

### SCF 收敛失败 (ABACUS301)
**检测模式**:
- "SCF" + ("NOT CONVERGED" | "CONVERGENCE FAILED" | "CONVERGENCE FAILURE")

**置信度**: 0.95

**修复建议**:
- kind: `increase_scf_steps_or_threshold`

**含义**:
- 自洽场迭代未收敛
- 可能需要增加 `scf_nmax` 或放宽 `scf_thr`

### 几何优化未收敛 (ABACUS302)
**检测模式**:
- "GEOMETRY" + ("NOT CONVERGED" | "CONVERGENCE FAILED")

**置信度**: 0.90

**修复建议**:
- kind: `increase_relax_steps_or_adjust_bfgs`

**含义**:
- 几何优化未达到收敛标准
- 可能需要增加 `relax_nmax` 或调整力收敛阈值

### 段错误 (ABACUS303)
**检测模式**:
- "SEGFAULT" | "SEGMENTATION FAULT"

**置信度**: 0.95

**修复建议**:
- kind: `check_input_or_reduce_system_size`

**含义**:
- 程序崩溃，可能是内存错误或输入问题

### 文件错误 (ABACUS304)
**检测模式**:
- "ERROR" + ("OPEN" | "FILE")

**置信度**: 0.85

**修复建议**:
- kind: `verify_file_paths_in_input`

**含义**:
- 无法打开所需文件
- 检查 `pseudo_dir`、`orbital_dir` 等路径

### 内存分配错误 (ABACUS309)
**检测模式**:
- "ALLOCATE" + "ERROR"

**置信度**: 0.90

**修复建议**:
- kind: `reduce_memory_usage_or_increase_resources`

**含义**:
- 内存不足或数组过大
- 减少系统规模或增加内存资源

## 解析实现

### 逐行扫描
```python
for line_no, line in enumerate(log_lines, start=1):
    upper = line.upper()
    # 检查各种错误模式
```

### 大小写不敏感
- 所有模式匹配使用大写比较
- 原始行保留在 evidence 中

### 行位置
- 报告的行号对应日志文件中的位置
- 帮助用户定位问题

## 诊断输出

### 证据包含
- 原始日志行内容
- 帮助用户在完整日志中查找

### 置信度
- 根据模式特异性设置
- 帮助代理判断严重程度

## 相关来源
- `raw/assets/src/abacus_lsp/analyzer.py`
- `raw/assets/tests/fixtures/invalid/scf_not_converged/`

## 来源列表
- parse_log 函数
- 测试夹具中的日志示例
