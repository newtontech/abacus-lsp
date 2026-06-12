# Project Configuration 项目配置

> 创建日期：2026-06-12
> 最后更新：2026-06-12
> 覆盖来源：2

## 核心论点

abacus-lsp 支持项目级配置，允许在 `.abacus-lsp/` 目录中覆盖默认行为和集成第三方服务。

## 配置目录结构

```
case_directory/
├── INPUT
├── STRU
├── KPT
└── .abacus-lsp/
    ├── schema.override.json    # 关键字模式覆盖
    ├── apns.json               # APNS 材料库配置
    └── matmaster.json          # MatMaster 集成配置
```

## schema.override.json

### 用途
覆盖或扩展内置关键字模式

### 格式
```json
{
  "keywords": {
    "ecutwfc": {
      "default": "100",
      "description": "Project-specific higher cutoff"
    },
    "custom_keyword": {
      "type": "Real",
      "category": "Custom",
      "description": "Project-specific parameter"
    }
  }
}
```

### 应用时机
- 加载 SchemaRegistry 时自动应用
- 与内置模式和运行时模式合并

## apns.json

### 用途
配置 APNS (Abacus Pseudopotential and Numerical Orbital Set) 材料库集成

### 格式
```json
{
  "pseudopotentials": [
    "Si.upf",
    "O.upf",
    "Fe.upf"
  ],
  "orbitals": [
    "Si.orb",
    "O.orb",
    "Fe.orb"
  ]
}
```

### 诊断规则
- ABACUS401: 伪势不在库存中
- ABACUS402: 轨道不在库存中

## matmaster.json

### 用途
配置 MatMaster/Bohrium 材料计算平台集成

### 格式
```json
{
  "enabled": true,
  "min_kpoint_grid": [8, 8, 8],
  "forbid_parent_paths": true,
  "require_lcao_orbitals": true
}
```

### 配置项详解

#### enabled
- 启用 MatMaster 集成检查

#### min_kpoint_grid
- 最小 K 点网格密度 [nkx, nky, nkz]
- 低于此值报告 ABACUS420

#### forbid_parent_paths
- 禁止 `..` 或绝对路径
- 确保工作区可移植性
- 违反时报告 ABACUS421

#### require_lcao_orbitals
- LCAO 作业必须显式指定轨道
- 违反时报告 ABACUS422

## 配置加载顺序

1. 内置模式 (`BUILTIN_KEYWORDS`)
2. 运行时模式 (`abacus -h`)
3. 项目覆盖 (`.abacus-lsp/schema.override.json`)

## 诊断配置加载

```python
def _load_lsp_config(case_dir: Path, filename: str) -> dict[str, Any]:
    path = case_dir / ".abacus-lsp" / filename
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))
```

## 相关来源
- `raw/assets/src/abacus_lsp/schema.py`
- `raw/assets/src/abacus_lsp/analyzer.py`

## 来源列表
- SchemaRegistry.with_project_overrides
- APNS 诊断函数
- MatMaster 诊断函数
