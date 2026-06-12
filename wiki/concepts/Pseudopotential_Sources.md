# Pseudopotential Sources and Formats 赝势来源与格式

> 类型：概念 / Concept
> 创建日期：2026-06-12
> 来源数：3

## 定义

ABACUS 支持多种赝势格式和来源。赝势用有效势替代原子核和内层电子，减少计算量同时保持化学精度。

## 支持的格式

### 模守恒赝势 (Norm-Conserving, NCPP)
- UPF (.UPF 格式)
- UPF2 (新 .UPF 格式)
- VWR (.vwr 格式)
- BLPS (bulk-derived local pseudopotential)

### 超软赝势 (Ultrasoft, USPP)
- UPF
- UPF2

### STRU 中的赝势类型标识
- `upf` - 标准 UPF 格式
- `upf201` - 新 UPF 格式
- `vwr` - VWR 格式
- `blps` - BLPS 格式
- `auto` - 自动识别 (默认)

## SOC 赝势

### 识别方法
UPF 文件头部检查:
```xml
<PP_HEADER relativistic="full" has_so="T" />
```

### 使用规则
1. SOC 计算 (`lspinorb=1`): 必须使用全相对论赝势 (`has_so=true`)
2. 非 SOC 计算: 可用标量相对论或全相对论赝势
3. USPP 约束: 全相对论 USPP 必须配合 `lspinorb=true`

### 来源
- SG15_ONCV: quantum-simulation.org
- PseudoDOJO: pseudo-dojo.org
- ABACUS 官方: abacus.ustc.edu.cn

## 赝势下载来源

### 综合网站
| 来源 | URL | 说明 |
|------|-----|------|
| Quantum ESPRESSO | quantum-espresso.org | 大量赝势 |
| SSSP | materialscloud.org | 高质量，经过测试 |
| PWmat | pwmat.com | 含镧系 |
| ABACUS@USTC | abacus.ustc.edu.cn | 官方 |

### 模守恒集合
| 集合 | 说明 |
|------|------|
| SG15 | ABACUS 中广泛使用 |
| PseudoDOJO | 含镧系 (f 电子冻结) |
| Rappe group | 合金系统性能优 |

### 超软集合
| 集合 | 说明 |
|------|------|
| Vanderbilt | Vanderbilt 组生成 |
| GBRV | QE 社区最流行 |

## APNS 项目

ABACUS Pseudopotential-Numerical atomic orbital Square (APNS) 项目:
- 目标: 提供高质量赝势和数值轨道
- 推荐集: APNSv1.0
- 可通过 AIS square 网站获取

## 相关来源
- `raw/assets/abacus-pseudopotentials-orbitals.md`
- `raw/assets/abacus-stru-format.md`
- 官方文档: http://abacus.deepmodeling.com/en/latest/advanced/pp_orb.html

## 相关概念
- [[Pseudopotentials]]
- [[Numerical_Orbitals]]
- [[ABACUS_STRU]]
- [[Spin_Polarization]]
