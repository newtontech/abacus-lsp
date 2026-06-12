# LLM Wiki 更新日志 / LLM Wiki Change Log

## 2026-06-12

### 初始化 / Initial Creation

**操作**: 创建 LLM Wiki 知识库结构

**来源路径**:
- `raw/assets/docs/` - 文档目录
- `raw/assets/README.md` - 项目说明
- `raw/assets/AGENTS.md` - 代理指南
- `raw/assets/pyproject.toml` - 项目配置
- `raw/assets/schemas/` - 模式文件
- `raw/assets/diagnostics/` - 诊断模式

**创建页面** (共 24 页):

**实体页面** (9):
- [[ABACUS_INPUT]] - INPUT 文件格式
- [[ABACUS_STRU]] - STRU 结构文件
- [[ABACUS_KPT]] - K 点文件
- [[Diagnostic]] - 诊断数据结构
- [[KeywordSchema]] - 关键字模式
- [[SchemaRegistry]] - 模式注册表
- [[InputFile]] - INPUT 内存表示
- [[StruFile]] - STRU 内存表示
- [[KptFile]] - KPT 内存表示

**概念页面** (9):
- [[Cross_File_Diagnostics]] - 交叉文件诊断
- [[Workflow_Diagnostics]] - 工作流诊断
- [[DFT_Plus_U]] - DFT+U 方法
- [[Basis_Set_Types]] - 基组类型
- [[Spin_Polarization]] - 自旋极化
- [[K_Point_Generation]] - K 点生成
- [[Pseudopotentials]] - 赝势
- [[Numerical_Orbitals]] - 数值轨道
- [[Formatter]] - 格式化器
- [[LSP_Server]] - 语言服务器

**综合页面** (5):
- [[Calculation_Types]] - 计算类型参考
- [[Diagnostic_Codes]] - 诊断代码参考
- [[CLI_Reference]] - 命令行接口参考
- [[Project_Configuration]] - 项目配置
- [[Log_Parsing]] - 日志解析
- [[Roadmap]] - 开发路线图

**导航文件**:
- [[index.md]] - 知识库导航
- [[log.md]] - 更新日志

**关键发现**:
1. ABACUS 支持 PW 和 LCAO 两种基组类型
2. 诊断代码分为 1xx (语法), 2xx (文件), 3xx (运行时), 4xx (第三方)
3. 项目支持 APNS 和 MatMaster 第三方集成
4. LSP 服务器提供完整的编辑器支持

**来源数**: 20+ 文件和模块

### ABACUS 文档收集与 Wiki 扩展

**操作**: 从 ABACUS 上游官方文档收集原始资料，更新和扩展 Wiki 页面

**来源路径** (新增 7 个原始文档):
- `raw/assets/abacus-readme.md` - GitHub 仓库 README (deepmodeling/abacus-develop)
- `raw/assets/abacus-input-reference.md` - 完整 INPUT 参数参考 (400+ 参数，30+ 类别)
- `raw/assets/abacus-stru-format.md` - STRU 文件格式规范 (完整节定义、Bravais 类型表、每原子关键字)
- `raw/assets/abacus-kpt-format.md` - KPT 文件格式规范 (Gamma/MP/显式/Line 模式)
- `raw/assets/abacus-pseudopotentials-orbitals.md` - 赝势与基组文档 (格式、SOC 要求、APNS 项目)
- `raw/assets/abacus-examples.md` - SCF 和几何优化完整示例 (MgO LCAO/PW)
- `raw/assets/abacus-quickstart-inputs.md` - 输入文件快速入门指南
- `raw/assets/abacus-tutorials.md` - 教程资源和学习材料汇总

**数据来源**:
- http://abacus.deepmodeling.com/ (官方文档站)
- https://github.com/deepmodeling/abacus-develop (上游仓库)
- http://abacus.deepmodeling.com/en/latest/advanced/input_files/input-main.html
- http://abacus.deepmodeling.com/en/latest/advanced/input_files/stru.html
- http://abacus.deepmodeling.com/en/latest/advanced/input_files/kpt.html
- http://abacus.deepmodeling.com/en/latest/advanced/pp_orb.html
- http://abacus.deepmodeling.com/en/latest/quick_start/hands_on.html
- http://abacus.deepmodeling.com/en/latest/quick_start/input.html

**更新页面** (3 个现有页面大幅扩展):
- [[ABACUS_INPUT]] - 新增 400+ 参数分类表、内置帮助系统、esolver 类型、混合泛函参数等
- [[ABACUS_STRU]] - 新增完整节格式、8 种坐标模式、每原子关键字 (m/v/mag/angle/lambda/sc)、14 种 Bravais 类型表
- [[ABACUS_KPT]] - 新增权重与对称性说明、Line 模式详细格式、Gamma-only 说明

**新增页面** (2 个):
- [[Pseudopotential_Sources]] (概念) - 赝势格式、SOC 要求、下载来源、APNS 项目
- [[Examples_and_Tutorials]] (综合) - SCF/优化示例、LCAO vs PW 对比、官方文档结构、接口集成

**更新导航** (2 个):
- [[index.md]] - 新增页面引用、Raw Assets 文档列表
- [[log.md]] - 本更新日志条目

**关键发现**:
1. ABACUS 包含 400+ 个 INPUT 参数，覆盖 30+ 个功能类别
2. 内置帮助系统支持模糊搜索和大小写不敏感查找 (`abacus -h`, `abacus -s`)
3. STRU 支持 14 种 Bravais 晶格类型通过 latname 自动生成
4. 赝势支持 NC 和 USPP，SOC 计算需要全相对论赝势
5. APNS 项目提供标准化赝势和轨道集 (推荐 APNSv1.0)
6. 支持 13+ 个外部软件接口 (DeePKS, DP-GEN, Phonopy, Wannier90, ASE 等)

**来源数**: 8 个上游文档页面

---

## 待补充 / Future Additions

### 计划中的实体
- Hubbard_U 参数
- Magnetic_Systems
- Band_Structure
- Density_of_States

### 计划中的概念
- SCF_Convergence
- Geometry_Optimization
- Molecular_Dynamics

### 计划中的综合页面
- 完整的 INPUT 参数参考
- STRU 格式详细说明
- 错误诊断和修复指南
