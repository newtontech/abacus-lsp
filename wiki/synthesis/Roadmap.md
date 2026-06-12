# Roadmap 开发路线图

> 创建日期：2026-06-12
> 最后更新：2026-06-12
> 覆盖来源：1

## 核心论点

abacus-lsp 按六个里程碑组织开发，从基础研究和模式定义到完整的 LSP 服务器和测试运行器。

## 里程碑

### Milestone 0: Research and Schema
**状态**: 已完成

**目标**:
- 创建 ABACUS 输入模式生成器
- 创建测试夹具语料库

**交付物**:
- `schema.py`: 关键字模式系统
- `schemas/abacus-builtin.json`: 内置模式
- `tests/fixtures/`: 测试夹具

### Milestone 1: Parser
**状态**: 已完成

**目标**:
- 实现 INPUT 解析器
- 实现 STRU 解析器
- 实现 KPT 解析器

**交付物**:
- `analyzer.py` 中的解析函数
- `InputFile`, `StruFile`, `KptFile` 数据结构

### Milestone 2: Linter
**状态**: 已完成

**目标**:
- 实现语法和模式诊断
- 实现交叉文件诊断
- 实现物理和工作流规则

**交付物**:
- 完整诊断系统
- 20+ 诊断代码
- 日志解析器

### Milestone 3: Formatter
**状态**: 已完成

**目标**:
- 实现安全格式化器
- 实现标准化格式化器

**交付物**:
- `formatter.py`
- `abacus-fmt` CLI 工具

### Milestone 4: LSP
**状态**: 进行中

**目标**:
- 实现 LSP 服务器 MVP
- 实现代码操作
- 实现格式化提供器

**交付物**:
- `server.py`: LSP 服务器
- `abacus-lsp` CLI 工具

### Milestone 5: Test Runner and Agent Interfaces
**状态**: 计划中

**目标**:
- 实现 `abacus-test static/smoke/regression`
- 实现代理 JSON 协议
- 集成 ABACUS-agent-tools 作为可选后端

**交付物**:
- `test_runner.py` 扩展
- 代理工具接口
- 可选后端集成

## 设计原则

### 轻量级
- 不依赖 ABACUS 二进制文件进行核心功能
- 实时编辑操作不触发重型计算

### 确定性
- 代理工具输出稳定的 JSON
- 诊断结果可重复

### 分层架构
- 解析器 → 模式 → 诊断 → LSP → 后端
- 每层可独立测试和使用

## 未规划功能

### 不会包含
- 实时 ABACUS 计算执行
- Bohrium 提交 (仅接口)
- 重度工作流自动化

### 原因
- 这些功能应通过显式命令触发
- 避免编辑时产生意外开销

## 相关来源
- `raw/assets/docs/roadmap/ROADMAP.md`

## 来源列表
- 官方路线图文档
