# Pseudopotentials 赝势

> 类型：概念 / Concept
> 学科/领域：电子结构计算 / Electronic Structure

## 定义

赝势是用有效势替代原子核和内层电子对价电子的作用，减少计算量的同时保持化学精度。

## ABACUS 实现

### 文件指定
在 STRU 文件的 ATOMIC_SPECIES 节中:
```
ATOMIC_SPECIES
Si 28.085 Si.upf
O  15.999 O.upf
```

### 目录配置
在 INPUT 文件中:
```
pseudo_dir  ./
```

## UPF 格式

### 文件扩展名
- `.upf`: UltraSoft Pseudopotential
- `.upf`: 标准 UPF 格式
- `.rec`: UPF 建议

### 内容包含
- 元素信息
- 赝势类型
- 局部和非局域分量
- 赝波函数

## 交叉文件验证

### 文件存在性检查
- 检查 `pseudo_dir` 中的赝势文件是否存在
- 缺失时报告 ABACUS204 警告

### 解析器行为
```python
for directory_key, filenames in {
    "pseudo_dir": stru_file.pseudopotentials,
}.items():
    base_dir = case_dir / input_file.parameters[directory_key]
    for filename in filenames:
        if not (base_dir / filename).exists():
            diagnostics.append(ABACUS204)
```

## APNS 集成

### 库存配置
`.abacus-lsp/apns.json`:
```json
{
  "pseudopotentials": [
    "Si.upf",
    "O.upf"
  ]
}
```

### 库存检查
- ABACUS401: 赝势不在 APNS 库存中
- 建议使用库存中的赝势

## 赝势类型

### 标准赝势 (NCPP)
- Norm-conserving
- 适合一般用途
- 格式: UPF, UPF2, VWR, BLPS

### 超软赝势 (USPP)
- Ultra-soft
- 减少截断能量需求
- 格式: UPF, UPF2
- 约束: 全相对论 USPP 必须配合 `lspinorb=true`

### SOC 赝势
- 必须为全相对论 (`relativistic="full"`, `has_so="T"`)
- SOC 计算 (`lspinorb=1`) 必须使用
- 来源: SG15_ONCV, PseudoDOJO, ABACUS 官方

### 下载来源
- SG15: ABACUS 广泛使用
- PseudoDOJO: 含镧系
- GBRV: 超软赝势，QE 社区流行
- APNS 项目: 官方推荐 (APNSv1.0)

## 相关概念
- [[Pseudopotential_Sources]] - 详细的赝势来源与格式
- [[ABACUS_STRU]]
- [[Cross_File_Diagnostics]]
- [[APNS]]

## 来源
- `raw/assets/src/abacus_lsp/analyzer.py`
