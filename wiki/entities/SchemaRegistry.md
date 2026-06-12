# SchemaRegistry 模式注册表

> 类型：组件 / Component
> 创建日期：2026-06-12
> 来源数：2

## 简介

`SchemaRegistry` 管理 ABACUS 关键字模式集合，支持内置模式、运行时模式和项目级覆盖。

## 核心功能

### 构造方法
```python
registry = SchemaRegistry(keywords: dict[str, KeywordSchema] | None = None)
```

### 类方法
```python
# 创建内置模式注册表
registry = SchemaRegistry.builtin()

# 从 JSON 文件加载
registry = SchemaRegistry.from_file(path: Path)
```

### 实例方法
```python
# 获取单个关键字模式
keyword = registry.get(name: str) -> KeywordSchema | None

# 获取所有关键字名称
names = registry.names() -> list[str]

# 导出为 JSON
payload = registry.to_json(version: str) -> dict[str, Any]

# 写入 JSON 文件
registry.write_json(path: Path, version: str)

# 应用项目级覆盖
registry = registry.with_project_overrides(project_dir: Path)
```

## 模式来源优先级

1. **内置模式** (`BUILTIN_KEYWORDS`)
2. **运行时模式** (`abacus -h` 输出)
3. **项目覆盖** (`.abacus-lsp/schema.override.json`)

## 项目覆盖格式

`.abacus-lsp/schema.override.json`:
```json
{
  "keywords": {
    "ecutwfc": {
      "default": "100",
      "description": "Project-specific higher cutoff"
    }
  }
}
```

或简化格式：
```json
{
  "keywords": [
    {
      "name": "ecutwfc",
      "default": "100"
    }
  ]
}
```

## JSON 序列化格式

```json
{
  "schema_version": "abacus-lsp-schema-v1",
  "abacus_version": "builtin",
  "keywords": [
    {
      "name": "calculation",
      "type": "Enum",
      "unit": null,
      "default": "scf",
      "category": "System",
      "description": "Calculation type.",
      "availability": ["PW", "LCAO"],
      "enum": ["scf", "relax", "cell-relax", "md", "nscf", "get_wf", "get_pchg"],
      "source": "builtin"
    }
  ]
}
```

## 运行时模式收集

`_collect_runtime_keywords()` 通过运行 `abacus -h` 收集运行时关键字：
- 超时: 20 秒
- 仅收集已知关键字的模式更新
- 忽略非字母数字令牌

## 相关来源
- `raw/assets/src/abacus_lsp/schema.py`

## 相关实体/概念
- [[KeywordSchema]]
- [[ABACUS_INPUT]]
- [[Project_Overrides]]

## 历史更新
- 2026-06-12: 初始创建，从 schema.py 提取
