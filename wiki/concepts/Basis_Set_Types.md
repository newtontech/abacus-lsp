# Basis Set Types 基组类型

> 类型：概念 / Concept
> 学科/领域：电子结构计算 / Electronic Structure

## 定义

ABACUS 支持两种基组类型：平面波 (PW) 和数值原子轨道 (LCAO)，通过 `basis_type` 参数选择。

## 基组类型

### PW (Plane Wave)
**描述**: 使用平面波展开波函数

**特点**:
- 系统性收敛：通过增加 `ecutwfc` 提高精度
- 无基组叠加误差
- 适合周期性体系

**必需参数**:
- `ecutwfc`: 平面波截断能量 (Ry)

**优势**:
- 精度可控
- 易于并行
- 适合金属和绝缘体

**劣势**:
- 计算量大，特别是第一性原理 MD
- 空心区域需要大量平面波

### LCAO (Numerical Atomic Orbitals)
**描述**: 使用数值原子轨道展开波函数

**特点**:
- 基组大小固定，不随系统尺寸增加
- 适合大体系

**必需参数**:
- `orbital_dir`: 轨道文件目录
- STRU 中的 NUMERICAL_ORBITAL 节

**优势**:
- 效率高，适合大体系
- 适合数千原子系统
- MD 模拟速度快

**劣势**:
- 精度依赖轨道质量
- 可能有基组叠加误差

## 交叉验证规则

### LCAO 诊断
- `basis_type=lcao` 时 STRU 必须有 NUMERICAL_ORBITAL
- 否则报告 ABACUS205 错误

### 轨道文件检查
- NUMERICAL_ORBITAL 数量必须与 ATOMIC_POSITIONS 元素数量匹配
- 否则报告 ABACUS206 警告

## 选择建议

### 使用 PW 当
- 需要高精度
- 系统较小 (< 100 原子)
- 需要系统性收敛研究
- 金属体系

### 使用 LCAO 当
- 系统较大 (> 200 原子)
- 进行 MD 模拟
- 几何优化迭代
- 资源有限

## 典型计算类型

### PW 适合
- 精确能带结构
- 小分子精确计算
- 表面能计算

### LCAO 适合
- 大分子几何优化
- 长时间 MD
- 高通量筛选

## 相关概念
- [[ABACUS_INPUT]]
- [[NUMERICAL_ORBITAL]]
- [[Cross_File_Diagnostics]]
- [[ecutwfc]]

## 来源
- `raw/assets/src/abacus_lsp/schema.py`
- `raw/assets/src/abacus_lsp/analyzer.py`
