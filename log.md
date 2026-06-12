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
