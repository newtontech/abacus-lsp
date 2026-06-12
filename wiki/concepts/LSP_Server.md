# LSP Server 语言服务器

> 类型：组件 / Component
> 创建日期：2026-06-12
> 来源数：2

## 简介

`abacus-lsp` 实现了 Language Server Protocol，为编辑器提供 ABACUS 输入文件的智能编辑支持。

## 支持的 LSP 功能

### 基础功能
- **Diagnostics**: 实时语法和语义错误检测
- **Completion**: 关键字自动完成
- **Hover**: 关键字悬停提示
- **Symbols**: 文档符号导航
- **Folding**: 代码折叠

### 高级功能
- **Formatting**: 代码格式化
- **Code Actions**: 快速修复
- **Document Links**: 文件链接解析

## 启动方式

### 标准输入/输出
```bash
abacus-lsp --stdio
```

### TCP Socket (未来)
```bash
abacus-lsp --socket <port>
```

## 架构分层

### 1. 解析层
- INPUT/STRU/KPT 文件解析
- 错误容忍的词法分析

### 2. 模式层
- 关键字模式注册表
- 值类型验证

### 3. 诊断层
- 语法诊断
- 模式诊断
- 交叉文件诊断
- 工作流诊断

### 4. 协议层
- LSP 消息处理
- 位置映射
- 响应序列化

## 诊断输出格式

### 编辑器格式
标准 LSP Diagnostic 对象

### 代理格式 (JSON)
```json
{
  "code": "ABACUS001",
  "severity": "error",
  "category": "syntax",
  "confidence": 1.0,
  "source": "abacus-lsp",
  "range": {...},
  "software": "abacus",
  "file_type": "input",
  "path": "...",
  "fix_hints": [...],
  "blocking": true
}
```

## 工具命令

### check
```bash
abacus-lsp-tool check path/to/case --format json
```
运行完整诊断并输出 JSON

### context
```bash
abacus-lsp-tool context path/to/input --format json
```
获取文件上下文信息

### complete
```bash
abacus-lsp-tool complete path/to/input --format json
```
获取补全建议

## 相关来源
- `raw/assets/src/abacus_lsp/server.py`
- `raw/assets/docs/DIAGNOSTIC_ENGINE_V1.md`

## 相关实体/概念
- [[Diagnostic]]
- [[Diagnostic_Engine_v1]]
- [[SchemaRegistry]]

## 历史更新
- 2026-06-12: 初始创建，从服务器模块和文档提取
