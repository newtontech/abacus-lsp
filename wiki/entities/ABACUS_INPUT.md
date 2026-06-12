# ABACUS INPUT 文件

> 类型：文件格式 / File Format
> 创建日期：2026-06-12
> 最后更新：2026-06-12
> 来源数：8

## 简介

ABACUS `INPUT` 文件是电子结构计算的主要控制文件，包含计算参数、方法和输出选项。它是 ABACUS 软件包的核心输入格式。ABACUS 包含 400+ 个 INPUT 参数，覆盖从系统设置到高级功能的所有配置。

## 文件结构

### 必需头部
```
INPUT_PARAMETERS
```

### 参数格式
```
keyword  value  # optional comment
```

### 关键规则
- 所有参数必须在 `INPUT_PARAMETERS` 头部之后
- 使用 `#` 或 `/` 开始注释
- 参数名称不区分大小写
- 重复参数时，ABACUS 使用最后一个值
- 未知参数名导致程序停止并报错
- 文件名必须是 "INPUT"，不能更改
- 布尔参数支持: True/False, 1/0, T/F (不区分大小写)
- 行字符位置 150 之后的内容被忽略

### 内置帮助系统
```bash
abacus -h              # 通用帮助
abacus -s ecut         # 按关键词搜索参数
abacus -h ecutwfc      # 特定参数详细帮助
```
支持模糊匹配、大小写不敏感查找。

## 核心参数分类

### System / 系统参数
- `suffix`: 输出目录后缀 (默认: ABACUS)
- `calculation`: 计算类型 (scf, relax, cell-relax, md, nscf, get_wf, get_pchg, get_s, gen_bessel, gen_opt_abfs, test_memory, test_neighbour)
- `esolver_type`: 能量求解器 (ksdft, ofdft, sdft, lj, dp, ksdft_md)
- `symmetry`: 是否使用对称性 (默认: 1)
- `cal_force`: 是否计算力
- `cal_stress`: 是否计算应力
- `device`: 计算设备 (cpu/gpu)
- `precision`: 浮点精度 (double/single)
- `latname`: Bravais 晶格类型名

### Electronic Structure / 电子结构
- `basis_type`: 基组类型 (pw, lcao)
- `ecutwfc`: 平波能量截断 (Ry) (PW 默认 50, LCAO 默认 100)
- `scf_thr`: SCF 收敛阈值 (PW: Ry, LCAO: 无量纲; 推荐 PW=1e-9, LCAO=1e-7)
- `nspin`: 自旋极化模式 (1=无自旋, 2=共线, 4=非共线)
- `dft_functional`: 交换关联泛函
- `nbands`: 能带数
- `nelec`: 电子数
- `smearing_method`: 展宽方法 (gauss, fd, mp, mv)
- `smearing_sigma`: 展宽宽度 (Ry)
- `mixing_type`: 电荷混合方法 (pulay, plain, broyden, pulay-kerker)
- `mixing_beta`: 混合参数 (默认: 0.7)
- `lspinorb`: 自旋轨道耦合
- `noncolin`: 非共线磁性

### Input Files / 输入文件
- `pseudo_dir`: 赝势文件目录
- `orbital_dir`: 数值轨道文件目录 (LCAO)
- `stru_file`: 结构文件路径 (默认: STRU)
- `kpoint_file`: K 点文件路径 (默认: KPT)
- `read_file_dir`: 读取文件目录
- `restart_load`: 从先前计算加载

### Plane Wave / 平面波
- `ecutwfc`: 波函数截断 (Ry)
- `ecutrho`: 电荷密度截断 (Ry, 默认 4*ecutwfc)
- `nx/ny/nz`: FFT 网格维度
- `pw_diag_thr`: 对角化阈值
- `pw_diag_nmax`: 最大对角化迭代

### LCAO / 数值原子轨道
- `lcao_ecut`: LCAO 能量截断
- `search_radius`: 邻居搜索半径 (Bohr)
- `lmaxmax`: 最大角动量 (默认: 2)
- `bx/by/bz`: 网格分区

### K-points / K 点
- `gamma_only`: 使用 Gamma 单点计算
- `kspacing`: K 点间距 (1/Bohr)
- `koffset`: K 点偏移

### Geometry Relaxation / 几何优化
- `relax_method`: 优化方法 (cg, bfgs, sd, cg-bfgs)
- `relax_nmax`: 最大离子迭代步数
- `force_thr_ev`: 力收敛阈值 (eV/Angstrom)
- `stress_thr`: 应力收敛阈值 (kBar)
- `fixed_axes`: 固定轴

### Output / 输出
- `out_chg`: 电荷密度输出 (-1/0/1)
- `out_band`: 输出能带结构
- `out_dos`: 输出态密度
- `out_wfc_pw`: PW 波函数输出
- `out_wfc_lcao`: LCAO 波函数输出
- `out_pot`: 静电势输出
- `out_mat_hs`: 哈密顿/重叠矩阵输出
- `out_mul`: Mulliken 电荷分析
- `out_stru`: 结构输出
- `out_level`: 输出详细程度

### Molecular Dynamics / 分子动力学
- `md_type`: MD 类型 (0=NVT, 1=NPT, etc.)
- `md_nstep`: MD 步数
- `md_dt`: 时间步长 (fs)
- `md_thermostat`: 恒温器类型
- `md_tfirst/md_tlast`: 初始/最终温度 (K)

### DFT+U
- `dft_plus_u`: DFT+U 方法 (0=关, 1=简单, 2=高级)
- `orbital_corr`: 修正轨道 (-1=无, l 量子数)
- `hubbard_u`: Hubbard U 值 (eV)

### vdW 修正
- `vdw_method`: vdW 方法 (d2/d3/d3bj/d4/bbjk/kbd/none)

### Exact Exchange / 混合泛函
- `exx_fock_alpha`: 精确交换分数 (默认: 0.25)
- `exx_hybrid_step`: 混合泛函 SCF 步数

### SOC / 自旋轨道耦合
- `lspinorb`: 启用 SOC
- `noncolin`: 非共线磁性
- `soc_lambda`: SOC 强度缩放

## 参数类别统计

| 类别 | 参数数 |
|------|--------|
| 系统变量 | ~30 |
| 输入文件 | ~7 |
| 平面波 | ~18 |
| LCAO | ~11 |
| 电子结构 | ~37 |
| SDFT | ~9 |
| 几何优化 | ~19 |
| 输出控制 | ~32 |
| 分子动力学 | ~38 |
| DFT+U | ~9 |
| 自旋约束 DFT | ~10 |
| vdW 修正 | ~20 |
| RT-TDDFT | ~37 |
| 混合泛函 | ~28 |

## 相关来源
- `raw/assets/abacus-input-reference.md` - 完整 INPUT 参数参考
- `raw/assets/abacus-quickstart-inputs.md` - 输入文件快速入门
- `raw/assets/abacus-examples.md` - 计算示例
- `raw/assets/src/abacus_lsp/schema.py`
- `raw/assets/schemas/abacus-builtin.json`
- 官方文档: http://abacus.deepmodeling.com/en/latest/advanced/input_files/input-main.html

## 相关实体/概念
- [[ABACUS_STRU]]
- [[ABACUS_KPT]]
- [[ABACUS_File_Format]]
- [[KeywordSchema]]
- [[SchemaRegistry]]
- [[Calculation_Types]]

## 历史更新
- 2026-06-12: 初始创建，从源代码和文档提取参数列表
- 2026-06-12: 扩展为完整参数参考，新增 400+ 参数分类、内置帮助系统、ESolver 类型
