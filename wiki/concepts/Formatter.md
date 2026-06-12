# Formatter 格式化器

> 类型：组件 / Component
> 创建日期：2026-06-12
> 来源数：2

## 简介

abacus-lsp 提供 INPUT 文件格式化功能，支持安全格式化和显式规范化两种模式。

## 命令行使用

```bash
# 格式化文件 (原地修改)
abacus-fmt -w INPUT STRU KPT

# 标准化格式
abacus-fmt --normalize INPUT
```

## 格式化规则

### INPUT 文件

#### 安全格式化
1. 保留所有原始内容
2. 对齐关键字和值
3. 保留注释
4. 保留 INPUT_PARAMETERS 头部

#### 标准化格式
1. 删除重复参数 (保留最后一个)
2. 按字母顺序排序关键字 (可选)
3. 统一大小写 (关键字转小写)
4. 规范化空格和缩进

### 对齐规则

```
# 格式化前
calculation scf
ecutwfc 50
basis_type pw

# 格式化后
calculation  scf
basis_type  pw
ecutwfc     50
```

## LSP 集成

### Formatting Provider
LSP 服务器提供标准格式化接口:
- `textDocument/formatting`
- `textDocument/rangeFormatting`

### 选项
```typescript
{
  "insertSpaces": true,
  "tabSize": 2,
  "normalize": false  // 是否启用规范化
}
```

## 实现细节

### 格式化流程
1. 解析原始文本为 `InputFile`
2. 按列宽对齐条目
3. 重构格式化文本
4. 验证格式化结果

### 列宽计算
```python
width = max(len(key) for key, _value, _comment in entries)
```

### 注释处理
- 保留行内注释位置
- 保留独立注释行
- 注释符号对齐

## 兼容性

### 保留的语义
- 所有关键字值完全保留
- 所有注释保留
- 物理意义不变

### 可能的变化
- 空格和缩进
- 关键字顺序 (规范化模式)
- 重复参数 (规范化模式)

## 相关来源
- `raw/assets/src/abacus_lsp/formatter.py`
- `raw/assets/src/abacus_lsp/cli.py`

## 相关实体/概念
- [[ABACUS_INPUT]]
- [[LSP_Server]]

## 历史更新
- 2026-06-12: 初始创建，从格式化器模块提取
