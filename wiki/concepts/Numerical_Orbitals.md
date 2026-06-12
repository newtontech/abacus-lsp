# Numerical Orbitals 数值轨道

> 类型：概念 / Concept
> 学科/领域：电子结构计算 / Electronic Structure

## 定义

数值原子轨道是预计算的数值化原子轨道函数，用于 LCAO 基组中的波函数展开。

## ABACUS 实现

### STRU 文件指定
```
NUMERICAL_ORBITAL
Si.orb
O.orb
```

### INPUT 配置
```
basis_type  lcao
orbital_dir ./
```

## 轨道文件要求

### 顺序匹配
- NUMERICAL_ORBITAL 顺序必须与 ATOMIC_POSITIONS 元素顺序一致
- 不匹配时报告 ABACUS206 警告

### 数量匹配
- 轨道数量必须等于元素种类数
- 不匹配时报告 ABACUS206 警告

## 文件格式

### 内容
- 数值化的径向轨道函数
- 通常由原子计算生成
- 包含不同角动量通道 (s, p, d, f)

### 常见扩展名
- `.orb`: 数值轨道文件
- `.orb`: 标准 ABACUS 格式

## 交叉验证规则

### LCAO 必需性
```
if basis_type == "lcao" and "NUMERICAL_ORBITAL" not in stru_file.sections:
    diagnostics.append(ABACUS205)
```

### 文件存在性
```
for orbital in stru_file.orbitals:
    if not (orbital_dir / orbital).exists():
        diagnostics.append(ABACUS204)
```

### APNS 库存检查
```
for orbital in stru_file.orbitals:
    if orbital not in allowed_orbitals:
        diagnostics.append(ABACUS402)
```

## MatMaster 要求

### LCAO 显式轨道
```json
{
  "require_lcao_orbitals": true
}
```
- LCAO 作业必须显式指定轨道
- 违反时报告 ABACUS422 错误

## 轨道生成

### ABACUS 工具
- 通常使用 ABACUS 提供的工具生成
- 需要参考配置

### 质量考虑
- 轨道质量影响计算精度
- 截断半径影响计算效率
- 通常需要测试收敛性

## 相关概念
- [[Basis_Set_Types]]
- [[ABACUS_STRU]]
- [[Cross_File_Diagnostics]]
- [[LCAO]]

## 来源
- `raw/assets/src/abacus_lsp/analyzer.py`
- `raw/assets/tests/fixtures/valid/mgo_lcao/STRU`
