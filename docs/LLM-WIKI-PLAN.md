# LLM Wiki 知识库计划 / LLM Wiki Knowledge Base Plan

> 项目：abacus-lsp
> 创建日期：2026-06-12
> 状态：已完成

## 目标 / Objective

为 abacus-lsp 项目创建 Andrej Karpathy 风格的 LLM Wiki 知识库，保存 ABACUS 量子化学域的源证据和合成知识。

## 知识库结构 / Structure

```
abacus-lsp/
├── raw/
│   └── assets/          # 源证据文件 (只读)
│       ├── docs/        # 项目文档
│       ├── schemas/     # 模式文件
│       ├── diagnostics/ # 诊断模式
│       ├── README.md    # 项目说明
│       ├── AGENTS.md    # 代理指南
│       └── pyproject.toml
├── wiki/
│   ├── entities/        # 实体页面 (9 页)
│   ├── concepts/        # 概念页面 (10 页)
│   └── synthesis/       # 综合页面 (6 页)
├── index.md             # 导航中心
└── log.md               # 变更日志
```

## 已创建内容 / Created Content

### 实体页面 / Entity Pages (9)

1. **ABACUS_INPUT** - INPUT 文件格式
   - 参数分类和类型
   - 必需和可选参数
   - 交叉文件引用

2. **ABACUS_STRU** - STRU 结构文件
   - 节结构说明
   - 交叉验证规则
   - 测试夹具示例

3. **ABACUS_KPT** - K 点文件
   - K 点模式
   - 网格生成
   - 能带路径

4. **Diagnostic** - 诊断数据结构
   - 字段定义
   - 诊断代码分类
   - 严重性策略

5. **KeywordSchema** - 关键字模式
   - 模式结构
   - 内置关键字列表
   - 值验证规则

6. **SchemaRegistry** - 模式注册表
   - 模式来源优先级
   - 项目覆盖机制
   - JSON 序列化

7. **InputFile** - INPUT 内存表示
   - 数据结构
   - 解析规则
   - 重复处理

8. **StruFile** - STRU 内存表示
   - 节解析
   - 元素列表
   - 验证规则

9. **KptFile** - KPT 内存表示
   - 模式存储
   - 点计数验证
   - 网格解析

### 概念页面 / Concept Pages (10)

1. **Cross_File_Diagnostics** - 交叉文件诊断
   - 分析流程
   - 检查规则
   - MatMaster 集成

2. **Workflow_Diagnostics** - 工作流诊断
   - 工作流检查
   - 输出验证
   - 参数完整性

3. **DFT_Plus_U** - DFT+U 方法
   - ABACUS 实现
   - 所需参数
   - 典型应用

4. **Basis_Set_Types** - 基组类型
   - PW vs LCAO
   - 选择建议
   - 交叉验证

5. **Spin_Polarization** - 自旋极化
   - nspin 参数
   - 磁矩设置
   - 典型应用

6. **K_Point_Generation** - K 点生成
   - 生成模式
   - 网格密度建议
   - MatMaster 检查

7. **Pseudopotentials** - 赝势
   - UPF 格式
   - 文件指定
   - APNS 集成

8. **Numerical_Orbitals** - 数值轨道
   - LCAO 要求
   - 顺序和数量验证
   - MatMaster 规则

9. **Formatter** - 格式化器
   - 格式化规则
   - LSP 集成
   - 兼容性

10. **LSP_Server** - 语言服务器
    - 支持的功能
    - 启动方式
    - 工具命令

### 综合页面 / Synthesis Pages (6)

1. **Calculation_Types** - 计算类型参考
   - 所有计算类型
   - 参数需求
   - 工作流建议

2. **Diagnostic_Codes** - 诊断代码参考
   - 完整代码列表
   - 分类和修复建议
   - 置信度说明

3. **CLI_Reference** - 命令行接口参考
   - 所有命令
   - 选项和参数
   - 配置文件

4. **Project_Configuration** - 项目配置
   - 配置文件格式
   - APNS 集成
   - MatMaster 集成

5. **Log_Parsing** - 日志解析
   - 支持的日志文件
   - 错误模式检测
   - 解析实现

6. **Roadmap** - 开发路线图
   - 六个里程碑
   - 设计原则
   - 未规划功能

## 使用指南 / Usage Guide

### 导航
- 从 `index.md` 开始浏览
- 使用 Obsidian 风格链接 `[[Page_Name]]` 跳转
- 查看 `log.md` 了解更新历史

### 查询
- 实体页面查找具体的 ABACUS 概念
- 概念页面理解跨域知识
- 综合页面获取完整参考

### 扩展
- 在 `raw/assets/` 添加新源文件
- 在 `wiki/` 创建新页面
- 更新 `index.md` 和 `log.md`

## 技术细节 / Technical Details

### 格式约定
- 双语格式：中文标题 + 英文术语
- Obsidian 风格链接
- 来源路径使用 `raw/assets/` 前缀
- 不确定性明确标注

### 页面模板
- 实体页面：类型、创建日期、来源数
- 概念页面：类型、学科/领域
- 综合页面：创建日期、最后更新、覆盖来源

## 验收标准 / Acceptance Criteria

- [x] 创建 20+ wiki 文件
- [x] 双语格式 (中文标题，英文术语)
- [x] 覆盖 ABACUS 特定域知识
- [x] 包含文件格式、数据结构、概念和参考
- [x] 创建导航中心和变更日志
- [x] 所有页面包含来源引用

## 后续计划 / Future Plans

1. 扩展实体页面 (Hubbard_U, Magnetic_Systems 等)
2. 添加更多概念页面 (SCF 收敛、几何优化等)
3. 创建错误诊断和修复指南
4. 集成更多 ABACUS 文档

---

*此计划于 2026-06-12 完成，创建了 25 页知识库内容。*
