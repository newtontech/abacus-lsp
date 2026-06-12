# KeywordSchema 关键字模式

> 类型：数据结构 / Data Structure
> 创建日期：2026-06-12
> 来源数：2

## 简介

`KeywordSchema` 是 ABACUS INPUT 关键字的元数据描述，包含类型、单位、默认值、可用性和枚举值等信息。

## 数据结构

### 字段定义
```python
@dataclass(frozen=True)
class KeywordSchema:
    name: str                    # 关键字名称 (小写)
    type: str                     # 数据类型: String, Real, Integer, Boolean, Enum, Path
    unit: str | None              # 物理单位 (如 "Ry")
    default: str | None           # 默认值
    category: str                 # 分类: System, Electronic structure, Plane wave, ...
    description: str             # 人类可读描述
    availability: list[str]       # 可用性: ["PW"], ["LCAO"], ["PW", "LCAO"]
    enum: list[str] | None        # 枚举值 (仅 Enum 类型)
    source: str                   # 来源: "builtin", "abacus -h", ...
```

## 内置关键字

### System / 系统
- `suffix`: 输出目录命名后缀
- `calculation`: 计算类型 (枚举: scf, relax, cell-relax, md, nscf, get_wf, get_pchg)

### Electronic Structure / 电子结构
- `basis_type`: 基组类型 (枚举: pw, lcao)
- `nspin`: 自旋极化模式 (枚举: 1, 2, 4)
- `dft_plus_u`: 启用 DFT+U 修正

### Plane Wave / 平面波
- `ecutwfc`: 平面波函数能量截断 (单位: Ry)

### Input Files / 输入文件
- `pseudo_dir`: 赝势文件目录
- `orbital_dir`: 数值轨道文件目录 (仅 LCAO)
- `stru_file`: 结构文件路径
- `kpoint_file`: K 点文件路径

### K-points / K 点
- `gamma_only`: 使用 Gamma 单点计算

### Output / 输出
- `out_band`: 写入能带结构输出
- `out_dos`: 写入态密度输出

## 模式注册表

`SchemaRegistry` 管理关键字模式集合：

```python
class SchemaRegistry:
    def __init__(self, keywords: dict[str, KeywordSchema] | None = None)
    def get(self, name: str) -> KeywordSchema | None
    def names(self) -> list[str]
    def to_json(self, version: str) -> dict[str, Any]
```

### 项目级覆盖
`.abacus-lsp/schema.override.json` 可覆盖内置模式：
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

## 值验证

`validate_keyword_value()` 根据模式类型验证值：
- `Real`: 必须是有效浮点数
- `Integer`: 必须是有效整数
- `Boolean`: 必须是 true/false, t/f, 1/0
- `Enum`: 必须在枚举列表中

## 相关来源
- `raw/assets/src/abacus_lsp/schema.py`
- `raw/assets/schemas/abacus-builtin.json`

## 相关实体/概念
- [[SchemaRegistry]]
- [[ABACUS_INPUT]]
- [[Type_Value_Diagnostics]]

## 历史更新
- 2026-06-12: 初始创建，从 schema.py 提取
