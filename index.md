# ABACUS LSP 知识库导航 / ABACUS LSP Knowledge Base Index

> 创建日期：2026-06-12
> 最后更新：2026-06-12

## 简介 / Introduction

本知识库基于 Andrej Karpathy 的 LLM Wiki 模式，为 abacus-lsp 项目维护一个 markdown 优先的知识系统。

**原始证据存储于 `raw/` 目录** - 不修改源文件
**代理维护的合成知识存储于 `wiki/` 目录** - 可持续更新

---

## 快速导航 / Quick Navigation

### 核心实体 / Core Entities
- [[ABACUS_INPUT]] - INPUT 文件格式和参数
- [[ABACUS_STRU]] - STRU 结构文件
- [[ABACUS_KPT]] - K 点文件
- [[Diagnostic]] - 诊断数据结构
- [[KeywordSchema]] - 关键字模式
- [[SchemaRegistry]] - 模式注册表
- [[InputFile]] - INPUT 内存表示
- [[StruFile]] - STRU 内存表示
- [[KptFile]] - KPT 内存表示

### 概念 / Concepts
- [[Cross_File_Diagnostics]] - 交叉文件诊断
- [[Workflow_Diagnostics]] - 工作流诊断
- [[DFT_Plus_U]] - DFT+U 方法
- [[Basis_Set_Types]] - 基组类型 (PW/LCAO)
- [[Spin_Polarization]] - 自旋极化
- [[K_Point_Generation]] - K 点生成
- [[Pseudopotentials]] - 赝势
- [[Numerical_Orbitals]] - 数值轨道
- [[Formatter]] - 格式化器
- [[LSP_Server]] - 语言服务器

### 综合页面 / Synthesis
- [[Calculation_Types]] - 计算类型参考
- [[Diagnostic_Codes]] - 诊断代码参考
- [[CLI_Reference]] - 命令行接口参考
- [[Project_Configuration]] - 项目配置
- [[Log_Parsing]] - 日志解析
- [[Roadmap]] - 开发路线图

---

## 按主题浏览 / By Topic

### 文件格式 / File Formats
- INPUT: [[ABACUS_INPUT]] | [[InputFile]]
- STRU: [[ABACUS_STRU]] | [[StruFile]]
- KPT: [[ABACUS_KPT]] | [[KptFile]]

### 数据结构 / Data Structures
- [[Diagnostic]] | [[KeywordSchema]] | [[SchemaRegistry]]
- [[InputFile]] | [[StruFile]] | [[KptFile]]

### 诊断系统 / Diagnostics
- [[Cross_File_Diagnostics]] | [[Workflow_Diagnostics]]
- [[Diagnostic_Codes]] | [[Log_Parsing]]

### 电子结构概念 / Electronic Structure
- [[Basis_Set_Types]] | [[DFT_Plus_U]] | [[Spin_Polarization]]
- [[K_Point_Generation]] | [[Pseudopotentials]] | [[Numerical_Orbitals]]

### 工具和接口 / Tools & Interfaces
- [[LSP_Server]] | [[Formatter]] | [[CLI_Reference]]

### 项目管理 / Project Management
- [[Project_Configuration]] | [[Roadmap]]

---

## 最近更新 / Recent Updates

查看 [[log.md]] 获取完整更新历史。

---

## 贡献指南 / Contributing

知识库由代理维护，人类通过以下方式贡献：

1. 提供原始文档和代码到 `raw/assets/`
2. 报告缺失或不准确的页面
3. 建议新的实体或概念

---

## 技术说明 / Technical Notes

- 使用 Obsidian 风格链接 `[[Page_Name]]`
- 来源路径使用 `raw/assets/` 前缀
- 不确定性明确标注而非推测
