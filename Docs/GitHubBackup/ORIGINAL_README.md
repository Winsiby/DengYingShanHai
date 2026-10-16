# 灯影山海：UE 5.8 C++ 竞赛工程

《灯影山海》是一款以中国皮影戏和《山海经》“夸父逐日”意象为核心的 UE5 实时光影交互叙事 Demo。玩家作为“复演者”进入一座久未开演的小型影戏剧场，在幕后“以灯为日、以影为夸父”，操纵灯具并调整皮影，让幕布上的实时影子依次完成“引日启幕—逐光成形—杖落成林”，把停在落杖之前的最后一出《逐日》重新演完。

本启动包描述一个范围受控、按里程碑推进的比赛版本：一个连续小剧场主地图、三次核心互动、一个高潮结尾、5–8 分钟完整体验。剧场包含入场短廊、幕后操作区、左右台翼、简化台前与不可探索远景，但不扩展成村落、多房间或第二关卡。开发周期不绑定固定天数；周期延长用于提高完成度、文化表达和验证质量，不自动扩大玩法与场景范围。

## 参赛背景

《灯影山海》拟参加 **2026 年第十四届全国大学生数字媒体科技作品及创意竞赛“虚幻引擎（UE）作品创作”赛项**，主要对应“基于 UE 的游戏与互动体验”方向，并体现实时渲染与交互探索能力。

作品以可运行的 Windows 游戏 Demo 为核心交付，不以静态渲染画面代替交互开发。项目将通过实时灯光与阴影、C++ 与 Blueprint 混合架构、稳定的谜题判定、Sequencer 演出和目标设备性能验证，回应赛项对引擎应用深度、系统完成度、交互逻辑、运行稳定性、实时渲染质量、性能优化和应用价值的关注。第三方模型、插件、素材和代码统一按 `Docs/LICENSES.md` 登记来源与授权。

## 核心方案

- 引擎：Unreal Engine 5
- 项目类型：最小 C++ 第三人称技术骨架；未导入完整 Third Person 模板、变体或共享角色大包
- 开发方式：C++ + Blueprint 混合
- 玩法：操纵光源与皮影的关系，使幕布影子满足目标
- 场景：单一连续小剧场；短廊、幕后、台翼、简化台前和不可探索远景
- 叙事：玩家作为“复演者”，把停在落杖前的最后一出《逐日》演完
- 表现：UE 实时灯光、阴影、材质、动画和 Sequencer
- 判定：独立的逻辑参数判定；不把实时阴影像素结果作为唯一成功条件
- 平台：Windows 演示与录屏版本优先

## 文件说明

```text
AGENTS.md              Codex 长期项目指令、边界和开发规则
README.md              启动与使用说明
Docs/
├─ PROJECT_BRIEF.md     项目定位、目标、范围和验收标准
├─ COMPETITION_BENCHMARK.md  竞赛评分、历届案例与优化依据
├─ ENVIRONMENT_SETUP.md 环境基线、安装步骤与验收标准
├─ ENVIRONMENT_VALIDATION.md 本机环境实测、路径修复与编译结果
├─ PHASE1_VALIDATION.md 第一阶段自动验收证据与人工复核清单
├─ GDD.md               当前竞赛版本的玩法、文化创意与体验流程
├─ INTERACTION_PRESENTATION_SPEC.md  三段学习曲线、落杖因果、双空间、声音与阴影规格
├─ ENVIRONMENT_NARRATIVE_SPEC.md  单地图剧场空间、环境状态与最小故事背景
├─ ARCHITECTURE_DESIGN.md 当前已确认的游戏模块、类职责、通信、状态机与实验边界
├─ ARCHITECTURE_DECISIONS.md 架构决定、确认状态、证据与回退记录
├─ TECH_SPEC.md         C++/Blueprint 架构、判定和测试方案
├─ DEVELOPMENT_PLAN.md  无固定天数的里程碑、分工、验收和止损点
├─ ASSET_LIST.md        美术、动画、音频和视频资产清单
└─ LICENSES.md          第三方资产与许可登记规则
```

## 如何使用

### 环境检查

本项目固定使用 UE 5.8.3、Visual Studio 2026、Windows SDK 26100 与 Git LFS。UE 5.8.3 首选 MSVC 14.50；本机当前只安装 14.51.36260，实测 Editor/Game Target 均能编译，但 UnrealBuildTool 会给出“非首选版本”警告。开始工作前阅读 `Docs/ENVIRONMENT_SETUP.md` 并运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\Scripts\Check-Environment.ps1
```

Required failures 为 0 才可继续；非零 warnings 必须阅读原因，不得将警告隐去。本机当前预期为 Required failures 0、warnings 1（MSVC 14.51 工具链风险提示）。

### 打开当前工程

1. 使用英文入口 `C:\UEProjects\DengYingShanHai\DengYingShanHai.uproject` 打开工程；该入口指向当前仓库，不是另一份副本。
2. 不再新建 Third Person 模板工程，也不把官方模板的变体、Mannequin 共享包、StateTree 或 AI 依赖整包导入。
3. 当前第一阶段包含单一 Runtime 模块、最小 `ACharacter` 操作载体、Spring Arm/Camera、Enhanced Input 和 `Dev/Interaction/LV_InteractionLab` 灰盒测试地图。
4. 编辑器专用 `PythonScriptPlugin` 被有意保留，用于可重复生成与独立验证 Phase 1 资产；`.uproject` 的 `TargetAllowList` 限制其不进入 Game Target。
5. 按 `Docs/DEVELOPMENT_PLAN.md` 从“灰盒戏台 + 第一次互动垂直切片”继续，不先做完整美术或可选 Mask 判定。

### 第一阶段复核命令

下面命令都从项目根目录运行，UE 相关路径必须使用英文入口：

```powershell
# 环境检查
powershell -ExecutionPolicy Bypass -File .\Scripts\Check-Environment.ps1

# Development Editor（-NoUBA 是当前机器已验证的稳定路径）
& 'C:\Program Files\Epic Games\UE_5.8\Engine\Build\BatchFiles\Build.bat' `
  DengYingShanHaiEditor Win64 Development `
  '-Project=C:\UEProjects\DengYingShanHai\DengYingShanHai.uproject' `
  -WaitMutex -NoHotReloadFromIDE -NoEngineChanges -NoUBA

# 从磁盘重载并验证地图、输入资产、GameMode 与镜头装配
& 'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe' `
  'C:\UEProjects\DengYingShanHai\DengYingShanHai.uproject' `
  -Unattended -NullRHI -NoSound -NoSplash `
  '-ExecutePythonScript=C:\UEProjects\DengYingShanHai\Scripts\Verify-Phase1Assets.py'
```

完整的 C++ Automation、PIE 和 Game Target 命令及已知限制见 `Docs/PHASE1_VALIDATION.md`。

### 接入已有项目

1. 先备份或提交已有项目。
2. 将本包的文件放入项目根目录；如果已有同名文件，应人工合并，不要直接覆盖。
3. 对照 `Docs/TECH_SPEC.md` 盘点现有类和 Blueprint，保留能服务最终范围的部分。
4. 将旧方案中不属于“单戏台、三互动、一个结尾”的功能移出当前里程碑，但不要在未确认前删除资产。

## 建议给 Codex 的第一条任务

```text
请先阅读 AGENTS.md、Docs/PROJECT_BRIEF.md、Docs/COMPETITION_BENCHMARK.md、
Docs/GDD.md、Docs/INTERACTION_PRESENTATION_SPEC.md、Docs/ENVIRONMENT_NARRATIVE_SPEC.md、
Docs/ARCHITECTURE_DESIGN.md、Docs/ARCHITECTURE_DECISIONS.md 和 Docs/TECH_SPEC.md。
检查当前 UE5 项目结构与引擎版本，然后给出 M1 垂直切片的实施清单。暂时不要创建可选 Render Target Mask 方案；先实现
可移动光源、皮影交互、参数区间判定、成功事件和调试显示。
```

## 首个垂直切片应出现的可玩结果

M1 里程碑结束前，灰盒场景中应该可以：

1. 走近并选中灯具；
2. 在受限轨道上移动或旋转灯具；
3. 看到幕布实时阴影随之变化；
4. 逻辑判定读取光源与皮影参数；
5. 参数进入容差并保持短暂时间后触发成功事件；
6. 在屏幕或场景中显示调试误差，便于快速调参。

达不到这六项时，不进入大规模美术替换。

## 当前竞赛版本的一句话完成标准

一个不了解项目的玩家，可以在没有开发者口头解释的情况下，于 5–8 分钟内进入一座连续、可信的小型影戏剧场，理解“未完逐日—玩家复演”的背景，完成三次逐步加深的光影互动，并看到从落杖接触点直接生长出来的高潮结尾。

## 资产与引用

- 开场《山海经》原典引用、文化研究来源、可直接使用的开放资源、Fab/Freesound 逐项审核规则及资产准入责任，见 `Docs/ASSET_SOURCES.md`。
- 已实际进入项目的第三方文件，必须同步登记到 `Docs/LICENSES.md`，并在 `Docs/ASSET_LIST.md` 关联项目内路径。
> 资产落地：夸父的原典/古图依据与模型规格见 [`Docs/KUAFU_VISUAL_RESEARCH.md`](Docs/KUAFU_VISUAL_RESEARCH.md)；免费/开放资产主选、零付费筛选顺序与 UE 5.8 验证要求见 [`Docs/ASSET_ACQUISITION_PLAN.md`](Docs/ASSET_ACQUISITION_PLAN.md)。
> **资产预算约束**：比赛版本全部使用团队自制或许可清晰的免费/开源资产，不采购任何模型、材质、音频、插件或模板。详见 `Docs/FREE_ASSET_POLICY.md`。
> **架构原则**：*永远不要以牺牲架构设计为代价追求功能；永远不要基于猜测进行权衡——必须与我确认。* 当前架构提案与待确认决策见 `Docs/ARCHITECTURE_DESIGN.md`、`Docs/ARCHITECTURE_DECISIONS.md`。
