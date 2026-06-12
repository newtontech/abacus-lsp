# CLI Reference 命令行接口参考

> 创建日期：2026-06-12
> 最后更新：2026-06-12
> 覆盖来源：2

## 核心论点

abacus-lsp 提供多个命令行工具，分别用于不同的功能：LSP 服务器、代码检查、格式化和测试。

## 命令列表

### abacus-lsp (LSP 服务器)

**启动 LSP 服务器**
```bash
abacus-lsp --stdio
```

**描述**: 通过标准输入/输出与编辑器通信

**用途**: VS Code、Vim/Neovim、Emacs 等编辑器集成

### abacus-lint (代码检查器)

**检查计算案例**
```bash
abacus-lint ./case
abacus-lint ./case --json
```

**描述**: 对 ABACUS 计算案例运行完整诊断

**输出格式**:
- 默认: 人类可读文本
- `--json`: JSON 格式，适合自动化

**检查内容**:
- INPUT 语法和模式
- STRU 结构
- KPT K 点设置
- 交叉文件一致性
- 运行时日志解析 (如果存在)

### abacus-fmt (格式化器)

**格式化输入文件**
```bash
abacus-fmt -w INPUT STRU KPT
abacus-fmt --normalize INPUT
```

**选项**:
- `-w`: 原地写入文件
- `--normalize`: 标准化格式 (更强的规范化)

**格式化规则**:
- 关键字对齐
- 注释保留
- INPUT_PARAMETERS 头部保证

### abacus-test (测试运行器)

**运行测试**
```bash
abacus-test static ./case
abacus-test smoke ./case
abacus-test regression ./case
```

**描述**: 不同层次的测试验证

**测试类型**:
- `static`: 静态分析 (语法、模式、交叉文件)
- `smoke`: 烟雾测试 (快速运行检查)
- `regression`: 回归测试 (完整计算验证)

### abacus-schema (模式工具)

**生成/查看模式**
```bash
abacus-schema
abacus-schema --output schema.json
abacus-schema --abacus /path/to/abacus
```

**描述**: 导出 ABACUS 关键字模式

**选项**:
- `--output`: 输出到文件
- `--abacus`: 从 ABACUS 二进制收集运行时模式

### abacus-lsp-tool (代理工具)

**诊断工具**
```bash
abacus-lsp-tool check path/to/case --format json
abacus-lsp-tool context path/to/input --format json
abacus-lsp-tool complete path/to/input --format json
abacus-lsp-tool hover path/to/input --format json
abacus-lsp-tool symbols path/to/input --format json
abacus-lsp-tool fix path/to/input --format json
```

**描述**: 确定性 JSON 输出的 LSP 操作

**用途**: 代理集成和自动化工作流

## 配置文件

### 项目级配置

`.abacus-lsp/schema.override.json`: 关键字模式覆盖
`.abacus-lsp/apns.json`: APNS 材料库配置
`.abacus-lsp/matmaster.json`: MatMaster 集成配置

## 相关来源
- `raw/assets/pyproject.toml`
- `raw/assets/src/abacus_lsp/cli.py`

## 来源列表
- pyproject.toml 中的脚本定义
- CLI 模块实现
