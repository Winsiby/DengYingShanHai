# TECH SPEC｜技术方案

> 人员事实更新（2026-10-09）：本项目由用户独立完成，用户是唯一人类作者与负责人。Codex/WorkBuddy 仅作辅助工具，不是制作成员；当前责任与署名见 `SOLO_PRODUCTION.md`。历史验证不追溯伪改。

> 本文定义技术原则、判定方案和验收目标；当前已确认的类级职责、依赖方向、状态机和最小实现顺序见 [`ARCHITECTURE_DESIGN.md`](ARCHITECTURE_DESIGN.md)，决策状态见 [`ARCHITECTURE_DECISIONS.md`](ARCHITECTURE_DECISIONS.md)。当前架构统一采用 `ADYPuzzleDirector` + `UDYPuzzleDefinition` Data Asset + Evaluator + Token 化表现桥。发生冲突时停止实现并与用户确认，不在代码中静默选择。

三段学习曲线、落杖到成林的演出因果、双空间镜头、声音状态和调试验收见 [`INTERACTION_PRESENTATION_SPEC.md`](INTERACTION_PRESENTATION_SPEC.md)。

单地图剧场尺度、玩家路径、环境状态、最小故事和环境资产边界见 [`ENVIRONMENT_NARRATIVE_SPEC.md`](ENVIRONMENT_NARRATIVE_SPEC.md)。

## 1. 技术目标

在 UE5 中用最小、可调、可测试的架构支撑一个连续小剧场主地图中的四幕演出；每幕复用三步光影互动。视觉层提供实时灯光、阴影、剧场环境状态和戏剧表现；玩法层使用独立逻辑参数稳定判定。任何单一渲染特性或周边环境资产都不能成为通关前提。

环境基线固定为 UE 5.8.x 正式版、Visual Studio 2026 与 Windows SDK 10.0.26100；UE 5.8.3 首选 MSVC 14.50.35717。本机当前实际使用 MSVC 14.51.36260，Editor/Game 实编译通过但保留 UnrealBuildTool 非首选版本警告。开始实现前，应记录实际 UE 热修复版本、引擎路径、编译器、目标电脑 GPU 与打包配置；当前竞赛版本开发中不无故升级 UE 小版本。完整安装与验收见 `ENVIRONMENT_SETUP.md`。

> 当前实现事实（2026-10-31，基线 Run176）：四幕分别呈现夸父、精卫、刑天、烛龙，仍共用一套输入、参数区间判定和单一主地图。后续章节中的最初三段方案与旧版本验收记录属于历史；当前构建与证据以最新交接记录为准。

## 2. 总体结构

```text
Enhanced Input
      │
      ▼
Player Character ── UDYInteractionComponent
      │                         │
      │                    IDYInteractable
      │                         │
      ├────────── ADYMovableLightActor
      └────────── ADYShadowPuppetActor
                                │
                                ▼
                     ADYPuzzleDirector
                                │
                    F/DY Puzzle Definition
                                │
                 ┌──────────────┴──────────────┐
                 ▼                             ▼
      参数区间逻辑判定                 Blueprint/Sequencer 事件
                 │                             │
                 └──────────────┬──────────────┘
                                ▼
                       BP_DYStagePresentation
                         │             │
                         ▼             ▼
              BP_DYStageEnvironment   实时光影/叙事演出
```

## 3. 核心类建议

命名可根据项目模块名调整，但职责边界应保持稳定。

### `UDYInteractionComponent`

职责：

- 通过短距离 Trace 或候选列表寻找可交互物；
- 管理聚焦、进入操纵、调整、取消和重置输入意图；
- 将输入值传给当前对象，不直接实现灯或皮影逻辑；
- 向 UI/Blueprint 广播提示和状态。

关键要求：一次只能有一个明确的 Active Interactable；丢失引用或对象被禁用时必须安全退出。

#### 聚焦距离语义（2026-10-02 修正）

`FocusDistance` 只表示**角色到交互物的真实最大可交互半径**，不表示相机射线长度。两者必须分开：

- 第三人称相机的 SpringArm 位于角色之后，相机到角色存在固定偏移；
- 可见性射线仍从相机视点发出，因此射线长度为
  `相机到角色偏移 + FocusDistance`，由 `ComputeFocusTraceLength()` 计算；
- 该长度是三角不等式给出的安全上界：角色半径球内任意点到相机的距离都不超过它，不会漏掉合法候选；
- 命中后必须再经过 `IsWithinFocusDistance()` 门控，即**候选对象到角色的距离不得超过 `FocusDistance`**；
- 射线只负责遮挡语义（仍然只接受第一个 Visibility 阻挡物，禁止穿墙），门控只负责半径语义，两者职责不合并；
- 相机位置、后移距离或 FOV 变化都不得改变角色的可交互半径；
- 聚焦仍由 0.10 秒定时器驱动，不使用 Tick、世界扫描或 `GetAllActorsOfClass`。

#### 聚焦诊断（Development-only）

聚焦管线提供一个只读诊断层，用于在真实 PIE 中定位「看不见 / 看得见但不易识别 / 看得见但无法聚焦」这类问题：

- 仅在显式 `-DYDebug` 启动参数下启用，复用 Puzzle Director 的同一开关；默认关闭；
- 整段实现位于 `#if !UE_BUILD_SHIPPING` 内，Shipping 编译期完全剔除，
  不保留任何可开启调试的属性、反射结构或 Blueprint 函数；
- 可观察内容：`ViewLocation`、`PawnLocation`、`TraceLength`、实际 `HitActor`、
  是否实现 `DYControllable`、`Pawn→Candidate` 距离、`WithinReach`、
  `CanBeginControl`、最终 `FocusedActor` 与 `RejectReason`；
- `RejectReason` 取值：`NoHit`（射线未命中任何物）、`BlockedByNonControllable`
  （首个 Visibility 阻挡物不是可控对象，即遮挡）、`BeyondOperatorReach`
  （可见但超出角色半径）、`CanBeginControlRefused`（候选拒绝控制）、`None`（已接受）；
- 绘制真实 `ViewLocation → TraceEnd` 的单条非持久射线，寿命略大于一个刷新间隔，
  避免陈旧射线被误读为当前状态；
- 日志只在 `HitActor`、`RejectReason` 或 `FocusedActor` 变化时输出，
  连续相同状态只记录一次，不按 0.10 秒无条件刷屏；
- 诊断只观察，不参与判定；开关打开与关闭时判定路径完全一致。

聚焦相关验证的分工必须保持清晰，不得互相替代：

- `M1.Focus.NoTickLifecycleContract` 只证明聚焦更新由定时器驱动、组件不 Tick，
  **不涉及任何遮挡结论**；
- 命中、遮挡（首个 Visibility 阻挡物拦截聚焦）与超出角色半径被拒绝，
  由 `M1.Focus.RuntimeTrace` 在真实世界的真实碰撞中证明；
- `-DYDebug` 运行日志只提供观察证据，单独一条日志不能替代上述自动化结论；
- 自动化不能替代人工验收。`M1.Focus.RuntimeTrace` 证明的是生产判定路径；
  站立不动、准星瞄准后按 `E` 的真实体验已在 `-game` 独立运行（非 PIE）中验证，
  但**全 M2 人工验收单尚未逐项执行**。

#### Development HUD（仅非 Shipping）

`ADYDevInteractionHUD` 提供最低限度的交互状态可见性，由 `DYStageGameMode` 在
`#if !UE_BUILD_SHIPPING` 下设为 `HUDClass`，正式美术 UI 后续替换：

- 既有准星／交互提示层只读取 `UDYInteractionComponent::GetFocusedActor()` 与 `IsControlling()`；
- 本步新增的 **Dev 状态行**另外订阅 Presentation 的离散提示快照，详见下文「Dev 状态文字反馈的最小事件链」；
- 画面中心准星：**白色 = 未聚焦**，**绿色 = 可操作**；
- 提示为简短 ASCII 英文字串（`Aim at the lamp` / `[E]  interact` /
  `A / D  adjust  E  release  R  reset`），因为本构建的 Dev 字体未验证中文字形；
- 不做世界扫描、不复制聚焦判定、不控制 POV、不改相机/地图/灯位/交互半径/判定频率，
  不依赖任何项目资产或插件；
- 绘制使用 `AHUD` 的 `DrawRect` / `DrawText` / `GetTextSize`，无需额外 Canvas 资源。

#### 输入诊断的职责划分

交互相关日志分两层，都受 `!UE_BUILD_SHIPPING` 与 `-DYDebug` 双重门控，且都按事件输出：

- `ADYStageOperatorPawn::HandleInteractInput`（绑定 `ETriggerEvent::Started`）输出
  `InputDebug InteractStarted=...`，用于判断**按键是否真的送达游戏**；
- `UDYInteractionComponent::ToggleControl` 输出
  `InteractDebug ControlToggle requested action=...`，用于判断**聚焦门控是否接受**。
  该函数不一定只由物理 E 调用，故文案不声称收到物理按键。

**规则**：不得由 `Entered Dev Manipulate` 缺失推断「用户没有按 E」。
必须先用 `InputDebug` 确认输入到达，再看 `InteractDebug` 的 `reason`
（`NoFocusCandidate` / `BlockedByNonControllable` / `BeyondOperatorReach` /
`CanBeginControlRefused`）判断拒绝原因。

### `IDYInteractable`

建议接口：

- `CanInteract`
- `BeginFocus` / `EndFocus`
- `BeginInteraction` / `EndInteraction`
- `ApplyPrimaryAdjustment`
- `ApplySecondaryAdjustment`
- `ResetInteraction`
- `GetInteractionPrompt`

接口表达“玩家意图”，不暴露具体键位。

### `ADYMovableLightActor`

职责：

- 管理灯具根节点、可移动光源、可视网格与交互碰撞；
- 沿受限轴、轨道或角度范围调整；
- 提供 0–1 归一化位置/角度给谜题系统；
- 暴露 Blueprint 表现事件；
- 支持锁定、软吸附和重置。

优先用约束参数驱动 Transform，不使用无约束物理模拟。灯光组件 Mobility 和阴影设置在关卡实例中显式检查。

### `ADYShadowPuppetActor`

职责：

- 管理皮影网格/骨骼网格与投影位置；
- 提供受限位置、朝向和 `PoseId`；
- 由 Blueprint/Animation Blueprint 播放预设姿态；
- 向谜题系统提供归一化逻辑参数。

当前竞赛版本不提供自由拖拽骨骼。姿态数量应少且轮廓差异明显。

### `ADYPuzzleTargetActor`（可选可视辅助）

职责：

- 在编辑器中显示目标构图范围、参考点或调试 Gizmo；
- 可向 Blueprint 提供幕布上的目标提示位置；
- Shipping 构建中隐藏纯调试可视内容。

它不负责核心状态机，避免每个目标各自维护流程。

### `ADYPuzzleDirector`

职责：

- 保存三个谜题的顺序与状态；
- 定期读取灯具和皮影的逻辑参数；
- 计算误差、进入/离开容差和保持时间；
- 广播进度、成功和全部完成事件；
- 管理已完成状态与局部重置；
- 提供开发调试显示。

建议状态：

```text
Locked → Available → Active → Holding → Resolved
                         ↑         │
                         └─────────┘  超出容差
```

只允许 Director 推进全局谜题顺序。Blueprint 不应绕过 Director 私自把多个谜题标为完成。

### `BP_DYStagePresentation`

职责：

- 监听 Puzzle Director 事件；
- 播放短过渡、Sequencer、音频、材质变化和高潮结尾；
- 直接调用唯一的 `BP_DYStageEnvironment`，把既有流程映射为五个环境表现状态；
- 在演出期间锁定/恢复恰当输入；
- 提供跳过或开发快速测试入口。

当前竞赛版本直接使用放置在主关卡中的专用 Blueprint Actor，不把核心流程放入 Level Blueprint。它只编排表现，不复制 Puzzle Director 的判定或完成状态，也不提前扩建复杂叙事框架。所有异步表现通过 Director 发出的 Token 开始，并用同一 Token 回调完成；过期回调不得推进当前流程。

当前 Dev 实现使用 `ADYStagePresentation` 作为 `BP_DYStagePresentation` 的稳定 C++ 基类：BeginPlay 以显式 Director 引用绑定动态委托，EndPlay 解绑，迟到时查询 Director 当前状态同步。基类只把已确认的谜题事实映射到 Environment，并将 15 Hz 采样去重为有限 Feedback 变化；具体镜头、动画、音频和 VFX 仍由 Blueprint 事件实现。

#### Dev 状态文字反馈的最小事件链

Presentation 除既有 Blueprint 事件外，另维护一个**不含答案数据的表现快照**与
一个**原生（非 Blueprint）multicast**，供 Dev HUD 读取：

```text
ADYPuzzleDirector（既有 multicast）
   → ADYStagePresentation：有限 Feedback 变化 → 提示状态 + 快照
        └→ 原生 multicast OnFeedbackDisplayChanged
             → ADYDevInteractionHUD：缓存快照并在 DrawHUD 绘制
```

- **GameMode 弱注册通知**：`ADYStageGameMode` 以 `TWeakObjectPtr` 持有本世界的
  Presentation，并提供注册／注销通知。注册时校验非空、`IsValid` 且同 World；
  注销按身份比对，**旧 Actor 结束不能清除新 Actor 的绑定**。不遍历世界。
- **HUD 迟到读取快照**：HUD 在 `BeginPlay` 绑定 GameMode 通知并读取当前已注册引用，
  两种 BeginPlay 顺序都成立；随后只读 `GetFeedbackDisplay()` 快照，
  **不调用** `SynchronizeFromDirector()`，因此不会重放演出事件或重置环境。
  切换、注销与 `EndPlay` 都会清旧绑定并隐藏状态行。
- **统一去重**：所有显示变化经单一入口，仅在状态实际改变时通知；
  重复的取消事件不重复广播、也不延长中断显示。
- **单个中断计时器**：由 Presentation 拥有，不是每个监听者各持一个。
  中断期间 `Far`/`Near` 采样只更新恢复基线，到期恢复**最新**基线；
  新的 Holding、Resolve、Activate 与 `EndPlay` 都会清理旧计时器，
  避免旧到期回调覆盖新状态。中断显示时长是可替换的 Dev 占位值，不是最终节奏决定。
- **不显示答案**：HUD 不读取归一化位置、target、容差、Progress 或 Holding 数值，
  只消费离散状态枚举。
- **旧 Dev 读取口的门控**：仅在非 Shipping 构建且 Dev 内容树内启用，判断依据是世界包名前缀
  `/Game/DengYingShanHai/Dev/`。真实 PIE 只在 map 短名前增加 `UEDPIE_0_`，
  目录结构保留；不使用任意 `Contains` 或伪造整路径前缀来放宽门控。
> **（迁移前历史，2026-10-03 之前）** 本段描述的是**只有 Dev HUD 反馈**的阶段。
> 当时 Shipping 下默认 GameMode 不挂载 Dev HUD、反馈注册与采样入口关闭、中断计时器不启动。
> **该描述已被 2026-10-03 的公共玩家层取代**：现在公共玩家提示与
> **那一个 Interrupted 单次计时器在 Shipping 与非 Dev 地图下仍然有效并被复用**，
> 原 GameMode 在 Shipping 不挂载旧 Dev HUD，旧 Dev getter/通知也保持关闭；不是从二进制删除该类。公共玩家层不受这两个 Dev 条件限制。

**验收现状注记（2026-10-03）**：上述事件链已由 Codex 在真实 PIE 中完成客观复测
（灯单条件、偶单条件、组合 Holding、中断、统一复位、单次完成与失焦返回均有实测证据）。

**当时的阻塞原因**：目标侧幕后皮影与操杆偏暗、前方大块几何遮挡构图。
后续只读定位确认根因是**实心 Phase1 测试夹具挡住主灯到目标皮影／幕的光路**，
**不是亮度不足**——提高强度无法打通被实心几何阻断的路径。

**本轮处置（用户批准并已实施）**：在 `Dev/M2/Maps/LV_M2PuzzleLab` 内**只迁移三项夹具位置**
（`DEV_CameraWall`、`DEV_InnerCornerA`、`DEV_InnerCornerB` 移至侧翼），保留其材质、尺寸与碰撞，
不删除夹具；**未新增补光、未改曝光／镜头／输入／判定／主灯**，无 C++ 改动。
正常与调试 PIE 中灯、偶与幕上投影均可见，**基本双空间可见性已恢复**。

**用户有限签收（2026-10-03）**：布局修复后用户答复「看清了，操作正常」，
**仅签收 Dev/M2 的主观可读性与操作手感**，不等于 `M2_VALIDATION.md` §5 的 11 项
逐项人工检查通过，也不等于 M2 完整完成。

**中文 UI 方案（已批准并实现，ADR-013 Accepted 2026-10-03）**：

[`M2_UI_IMPLEMENTATION_PLAN.md`](M2_UI_IMPLEMENTATION_PLAN.md) 的方案 B 已由用户确认并由 Codex 实施：
薄 `AHUD` 适配器 + 原生 UMG 中文视图。**架构边界如下**：

- **Presentation 仍是唯一所有者**：离散玩家提示状态、恢复基线与**唯一 Interrupted 单次计时器**
  仍归 `ADYStagePresentation`，不在 Widget 或新蓝图里复制保持／打断判定。
  向 Widget **不传** Target、Tolerance、Current 或精确 Progress。
- **公共玩家口与旧 Dev 口分离（门控按源码只读核实）**：
  - `GetPlayerFeedbackDisplay()` / `OnPlayerFeedbackDisplayChanged()` /
    `GetPlayerStagePresentation()`：**无任何门控**，Shipping 与非 Dev 地图均可用；
  - 旧 Dev 口 `GetFeedbackDisplay()` / `GetStagePresentation()`：
    **仅在 `!UE_BUILD_SHIPPING` 且 Dev 包名前缀成立时可读**（Shipping 或非 Dev 地图返回 `Hidden`／空），
    **源码中并无 `FParse`／`-DYDebug` 判断**；
  - **开发数值、轨道与目标球**另需 `-DYDebug`（`!Shipping`）；
    Dev HUD 类本身在 Shipping 下不挂载，但**不能声称**其类与文案已从二进制剔除。
- **适配器订阅 PC／Pawn／Presentation**：`ADYInteractionHUD` 以 `AHUD` 与当前本地
  `OwningPlayerController` 关系存在，订阅 Interaction 的聚焦／操纵事件与同世界 GameMode
  显式注册的 Presentation；**不另建玩家控制权**，不改 Enhanced Input Context、不调用 `SetViewTarget`。
- **UMG 仅显示**：`UDYInteractionHUDWidget` 的原生 UMG 树只负责题签、中心准星与底部提示行；
  WBP 原型**仅配置字体／题签／颜色等默认样式**，不是手工 Designer 节点图，也不臆测蓝图节点。
- **解绑（按源码实际行为区分）**：
  - `Pawn` 更换时先从旧 Interaction 解绑再绑新 Pawn；`Presentation` 更换先解绑旧实例；
    旧 Actor 卸载不能清除新绑定；
  - Widget `NativeDestruct`（经 `OnNativeDestruct` 委托 → `HandleWidgetDestruct`）
    清理 **PC／Pawn／GameMode／Presentation 的订阅**并重置这些弱引用，
    **但 `View` 强引用保留**；
  - 只有 HUD `EndPlay` 才`RemoveFromParent()` 并把 `View` 置 `nullptr`。
- **无新增轮询**：无 UI Tick、无世界扫描、无属性轮询绑定、无新增输入或 POV 所有者。

上文 Dev HUD 段中「反馈入口关闭且计时器不启动」已是**迁移前历史**；
Dev HUD 的准星、聚焦只读与不操控 POV 等规则**仍然有效**，未被本小步改变。
中文 UI 是在其之上分离出的公共玩家层。

最新证据见 `Saved/Audit-2026-10-03-M2UI/Supervisor-Results.md`。
本注记只记录当前状态与门控事实；上文标注为迁移前历史的段落不再适用。

**后续签收更新（2026-10-03）**：用户明确「中文 UI 正常」，又针对 `M2_VALIDATION.md` §5 完整清单答复「11 项已逐项检查，全部正常」。P02 灰盒机制及 UI 切片现已签收；前述仅有限签收/等待勾选描述为历史。整个 M2 三互动里程碑与竞赛作品仍未完成。

收尾补验：同一真实 GUI Editor 会话二次运行 UI 配置，各次零产品文件 SHA256 变化、20 UI + 35 M2 PASS；外部比对 84 个产品文件未变。证据见 `Saved/Audit-2026-10-03-M2Closure/Supervisor-Results.md`，不扩大为其他机器兼容或完整流程验收。本轮没有修改 C++ 或重新编译打包。

**P03 初始审查缺口**：原 `OnPuzzleResolved` 携带的 `FDYEvaluationResult` 仅是判定结果，不是完整 Transform 冻结包；`FDYControlSnapshot` 已含 Actor WorldTransform，但不含手杖组件/投影落点。初始 Director 无 Token、三幕顺序或完整体验状态；StageEnvironment 实际枚举仅前三态。

**后续首步实现（2026-10-03）**：用户选择真实投影树形灰盒方案。新增 `FDYResolvedPuzzleSnapshot`，Director 在成功时一次捕获真实灯/偶控制快照并发行不透明 `FGuid` 身份；`GetResolvedPuzzleSnapshot()` 返回独立副本，`IsResolvedTokenCurrent()` 只读核验当前成功身份。原成功事件签名、P01/P02、15 Hz、地图与输入不改。复位、重新激活、EndPlay 和跨实例旧身份拒绝已有测试；**接触/完整演出回调消费、FinaleLocked、三幕顺序、手杖/幕布表现快照及成林仍未实现**。主判定仍不依赖锚点/像素。

本轮首步 34 Success / 0 Failed（原 30 保留 + 4 新增）、Editor/Game Development/Game Shipping 编译、20 UI / 35 M2 冷读通过；未新 Cook/打包或生成 P03 可见画面，旧 UI 包不含新代码。执行合同及证据见 `Saved/Audit-2026-10-03-P03Foundation/`，后续接入规格见 [`P03_DEV_IMPLEMENTATION_PLAN.md`](P03_DEV_IMPLEMENTATION_PLAN.md)。未决参数/演出时长须确认，不据此改变输入或整局复位规则。

### `BP_DYStageEnvironment`

职责：

- 收拢同一剧场中需要随流程变化的环境强调灯、材质、题签、幔帐、台翼和远景表现引用；
- 接受 Stage Presentation 的显式状态调用，应用 Dormant、SunAwakened、ChaseAwakened、FinaleReady 与 ForestComplete；
- 状态应用可重复安全调用，重开时能恢复 Dormant；
- 动态材质实例在 BeginPlay/显式初始化中创建并缓存；
- 使用一次性事件、Timeline、材质动画或 Sequencer，不以 Tick 扫描世界。

它不读取 Puzzle Director、不自行推进状态、不切换输入/相机，也不包含环境解谜。主地图只有一个稳定实例，由 Stage Presentation 直接引用，不使用 `Get All Actors of Class`、Subsystem 或全局消息总线发现。

## 4. 数据定义

三幕统一使用 `UDYPuzzleDefinition : UPrimaryDataAsset` 保存不可变定义；Director 只保存对三份定义的引用和独立运行状态。Data Asset 不保存当前幕次、Holding 时间、完成标志或 Actor 引用。该决定已经确认，不再使用 Director/Manager 内复制的三组配置数组。

建议最小结构：

```cpp
UENUM(BlueprintType)
enum class EDYPuzzleState : uint8
{
    Locked,
    Available,
    Active,
    Holding,
    Resolved
};

USTRUCT(BlueprintType)
struct FDYTargetRange
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    float Target = 0.5f;

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    float EnterTolerance = 0.08f;

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    float ExitTolerance = 0.10f;

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    float Weight = 1.0f;
};

USTRUCT(BlueprintType)
struct FDYPuzzleDefinition
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    FDYTargetRange LightPosition;

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    FDYTargetRange LightRotation;

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    FDYTargetRange PuppetPosition;

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    FDYTargetRange PuppetRotation;

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    FName RequiredPoseId;

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    float RequiredHoldSeconds = 1.0f;
};
```

并非每个谜题都启用全部字段。用显式布尔值或条件列表说明哪些条件生效，不要让未启用字段意外参与评分。`ExitTolerance` 应不小于 `EnterTolerance`，以滞回保护刚刚进入正确区间的条件。

## 5. 主判定方案：参数区间

### 输入参数

- 灯具轨道位置 `LPos`，归一化为 0–1；
- 灯具角度 `LRot`，按约束范围归一化；
- 皮影位置 `PPos`；
- 皮影朝向 `PRot`；
- 皮影预设姿态 `PoseId`；
- 可选的谜题阶段/对象启用状态。

### 单条件误差

对连续参数可使用：

```text
NormalizedError = abs(Current - Target) / max(Tolerance, SmallNumber)
```

`NormalizedError <= 1` 表示进入容差；离开时改用 `ExitTolerance`。角度必须使用最短角差，避免 0°/360° 跳变。

### 总体进度

用于提示的进度可以是加权误差的平滑映射；用于成功的条件应保持明确：所有启用的必要条件均在容差内，且姿态匹配。

```text
AllRequiredConditionsValid
        +
ContinuousHoldTime >= RequiredHoldSeconds
        ↓
Resolve Puzzle
```

对进度值做插值以稳定 UI/音效，但不要对成功条件做过长延迟。进入与离开容差可以使用少量滞回，防止边界抖动。

### 为什么这是主方案

- 与阴影分辨率、抗锯齿、渲染比例和灯光质量解耦；
- 可以在 C++ 纯逻辑测试中验证；
- 调参快速，能给玩家稳定容差；
- 同一套系统可配置三个谜题；
- 打包和换电脑后更可控。

## 6. 可选升级：Render Target Mask

仅当主流程已跑通、打包稳定且计划有余量时尝试。它必须通过独立接口提供相似度分数，并可一键关闭回退到参数判定。

可选流程：

```text
SceneCapture / CustomDepth
        ↓
低分辨率二值或灰度 Mask
        ↓
与目标 Mask 计算重叠 / 差异
        ↓
输出 0–1 相似度
        ↓
作为辅助条件或表现信号
```

限制：

- 不在 M2 三互动灰盒闭环通过前进入关键路径；
- 不要求每帧高分辨率读取 GPU 数据到 CPU；
- 不允许因画质设置变化而使谜题不可完成；
- 失败时保留参数判定和预设目标；
- 不为该功能修改引擎源码。

## 7. 视觉阴影与灯光方案

### 7.1 渲染基线

当前 Windows Demo 优先采用 Deferred Renderer、一盏 Movable 主灯和 Virtual Shadow Maps。Lumen GI/Reflections 可用于环境反弹与材质质感，但不参与玩法判定；单主灯灰盒阶段默认不启用 MegaLights，只有目标机 GPU 测量证明其有明确收益时才评估。

主灯优先使用与灯具造型和照射范围相符的 Spot Light 或 Point Light：

- 开启动态阴影，让玩家移动灯时幕上轮廓连续变化；
- 使用 Candela 或 Lumens 时记录逆平方衰减、灯到幕布距离、Source Radius 和曝光；
- Attenuation Radius 只作为影响范围，不用来补亮；
- Source Radius 增大将使影子更软，应从能辨认关节和杖尖的较小值开始逐步调节；
- 互动阶段采用固定曝光或窄范围受控曝光，防止灯具运动引起亮度泵动；
- 灯光参数必须与目标显示器、实际机位和目标画质档一起验收，不孤立记录一个强度数字。

### 7.2 幕布与关键投影

- 幕布材质必须在主要观察侧清楚表现主灯产生的真实阴影，并通过实际前后机位测试；
- 夸父、手杖和必要操杆明确 Cast Shadow，非关键装饰根据性能关闭阴影；
- 关键轮廓必须由玩家正在操纵的主灯与皮影产生；
- Light Function、材质投影、预制林影和 Niagara 只能增强提示或高潮，不能冒充主交互阴影；
- 目标提示与实时影子使用可辨别的材质、线型或动画语言；
- 录屏版和现场版保留同一主灯/主阴影路径，降级时优先删除次要灯、粒子、景深和环境阴影。

### 7.3 诊断与验收

灯光问题按以下顺序诊断：关闭干扰后处理 → 锁定曝光 → 检查材质/法线 → HDR/Eye Adaptation → Lumen Overview/Surface Cache → Shadow/VSM → Light Complexity/影响范围 → 目标机 GPU 时间。不得通过随意提高曝光补偿掩盖主灯或幕布问题。

验收必须同时满足：主要机位轮廓清楚、无明显曝光泵动；关键阴影可随玩家操作连续变化；降低非关键画质后逻辑仍能完成；目标机达到记录的帧率/帧时间预算。

### 7.4 剧场环境灯光状态

灯光按“关键主灯—环境底光—演出强调灯”分层：主灯负责实时阴影和太阳意象；底光只保证短廊、幕后路径和交互对象可读；强调灯随环境状态照亮题签、台翼、锣鼓角和简化观演区。

- 灰盒阶段先用 Manual Exposure 建立主灯/底光关系，再决定最终固定或窄范围受控曝光；
- Dormant 到 ForestComplete 不通过自动曝光把各阶段拉回同一亮度；
- 环境苏醒优先复用局部灯和材质参数，不为每个状态新增一批灯；
- 环境局部灯使用最小有效 Attenuation Radius，避免和主灯在幕布区域重叠；
- 远山卡片、长凳、台翼装饰和非关键木构默认不投动态阴影；
- 用同一机位截图和目标机 GPU 帧时间验证五个状态的可区分性与成本。

## 8. Blueprint 事件边界

建议从 C++ 暴露：

- `OnFocusChanged`
- `OnInteractionStarted` / `OnInteractionEnded`
- `OnNormalizedValueChanged`
- `OnPuzzleActivated`
- `OnEvaluationUpdated`（C++ 采样事件；Presentation 去重后才向 Blueprint 发布有限 Feedback 变化）
- `OnPuzzleHoldStarted` / `OnPuzzleHoldCancelled`
- `OnPuzzleResolved`（携带 `PuzzleId` 和冻结的 Resolved Snapshot）
- `OnAllPuzzlesResolved`

Blueprint 响应事件完成：提示、音效、材质参数、灯光变化、动画与 Sequencer。事件应能重复安全调用或有明确一次性保护。

P03 Resolve 后，Stage Presentation 必须从玩家当前可见状态继续落杖，使用皮影杖尖的骨骼 Socket/Scene Component 与幕布接触锚点建立表现落点。接触同步点才调用幂等的 `BeginGrowth`；Director 不依赖杖尖锚点、声音、VFX 或 Sequencer 才能判定成功。

声音事件按状态而不是按帧驱动：Progress 先离散为“远/近/有效”并加滞回与冷却；Holding 控制可持续进入/退出的节奏层；Resolve 只触发一次重音；脚步和杖尖接触使用 Animation Notify 或 Sequencer 明确同步点。

## 9. 输入与镜头

### 9.1 输入

- 使用 Enhanced Input；
- 区分角色移动 Context 与对象操纵 Context；
- 进入操纵时降低输入歧义，离开时可靠恢复；
- 键鼠为首要验收输入，其他设备放入有余量项。

### 9.2 相机所有权

- Explore：角色 Camera Component/Spring Arm 拥有基础 POV；
- Manipulate：本地 PlayerController 使用 `Set View Target with Blend` 切换到 `BP_DYStageCameraRig`；
- Transition/Finale：带 Camera Cut Track 的 Level Sequence 暂时接管；
- 任一时刻只有一个系统写最终 POV，不使用 UE 5.8 Experimental Gameplay Camera System；
- Stage Presentation 在播放前记录/推导当前有效 View Target、输入模式与 UI 状态；完成、跳过、中断和 Sequence 销毁都走同一个恢复函数；
- 恢复目标必须是当前仍有效的角色或舞台相机，不缓存已经销毁的陈旧 Actor。

### 9.3 构图与验收

舞台操纵镜头采用幕后三分之四构图：幕布是主要阅读区，灯、皮影或操杆至少保留一项在前/侧景。先固定机位、目标、遮挡和基础 FOV，再考虑轻微过渡、Shake 或后处理。强景深、持续抖动和相机 Lag 不得降低影子可读性，Shake 强度必须允许降为零。

Finale 至少包含一个连续镜头展示“玩家最终影形 → 杖尖接触 → 林影生长”。用正常结束、跳过、中断、重启、低/高帧率和常用画面比例验证相机交接。

完整空间只需要四个镜头任务：Explore 介绍短廊/台翼/幕后纵深；Manipulate 证明实时因果；Finale Cause Shot 不切镜证明落杖成林；Audience Reveal 在因果已成立后展示台前全景。台前主要是镜头空间，不要求玩家绕行或新增导航任务。

## 10. 调试工具

Development 构建至少提供：

- 当前谜题 ID、学习阶段与状态；
- 各启用参数的 Current / Target / Enter Tolerance / Exit Tolerance / Valid；
- 当前/目标 `PoseId` 和 Enabled Control Mask；
- 是否处于 Holding 以及剩余保持时间；
- 当前交互对象；
- 最近状态迁移、Resolve 触发次数；
- P03 冻结 Snapshot、杖尖和幕布接触锚点有效性；
- 当前 View Target、Sequencer 接管状态；
- 当前 Stage Environment 状态、最近一次状态应用与关键表现引用有效性；
- 主灯动态阴影状态、画质档和帧时间摘要；
- 快速重置当前谜题；
- 开发专用的激活/跳转下一阶段方式；
- 关键状态变化日志。

世界调试图形可显示受限轨道、目标区间、幕布接触点和杖尖锚点。Shipping 构建关闭屏幕调试、世界调试图形和开发跳关入口；调试开关只改变可视化，不能改变谜题结果。

## 11. 性能与打包目标

- 以目标演示电脑的 1080p 实际表现为准；
- 目标是稳定 60 FPS，若硬件与视觉目标冲突，最低验收是稳定且无明显卡顿的 30 FPS 以上，并记录测试配置；
- 避免每帧全场景昂贵捕获、频繁创建动态材质实例或无边界 Tick；
- 主地图不启用 World Partition/Level Streaming；不可探索远山优先使用卡片、平面、雾层和低成本材质；
- 台前长凳与台翼道具模块化复用，大多数装饰不需要碰撞和动态阴影；
- 不需要每帧计算的判定可采用较低频率更新；
- 从 M1 起每个里程碑至少生成并验证一份可运行 Development 包，M5/M6 同时验证 Shipping；
- 打包前检查 Map 列表、默认 GameMode、输入配置、重定向器、缺失引用与插件依赖。

## 12. 最小测试矩阵

| 类别 | 测试 |
|---|---|
| 交互 | 聚焦、进入、调整、取消、切换对象、对象失效 |
| 约束 | 到达边界、快速输入、低帧率、重置后参数正确 |
| 判定 | 容差内/外、角度跨 360°、姿态错误、保持中断、只触发一次 |
| 流程 | 三谜题顺序、已完成不回退、过场期间输入锁定、结束状态 |
| 恢复 | 当前谜题重置、重新开始、意外离开互动区 |
| 因果 | P03 保留最终 Transform、杖尖接触与成林首帧同步、跳过后最终状态一致 |
| 镜头 | 双空间可读、POV 单一所有者、结束/跳过/中断后正确恢复 |
| 音频 | Progress 不连发、Holding 可回落、Resolve 只重音一次、静音仍可通关 |
| 环境 | 五状态顺序/幂等/重开、环境灯不削弱幕布、无 Director 反向依赖、无世界扫描 Tick |
| 空间 | 入场 20 秒内看懂路径；短廊/台翼相机不穿模；台前/远景不可误入且不增加任务 |
| 打包 | 无编辑器依赖、字体/音频/Sequencer 被 Cook、默认地图正确 |
| 性能 | 三次互动与高潮的帧率、GPU 帧时间、阴影质量、显存与卡顿观察 |

## 13. 降级顺序

当进度或性能不足时，按以下顺序止损：

1. 关闭 Mask 相似度升级，仅保留参数判定；
2. 删除观众剪影、窗外天气、次要远景层和装饰微动；
3. 减少环境动态阴影、粒子和次要灯光，保留连续剧场壳体；
4. 将自由拖动改为轨道/分段位置，将连续姿态改为预设姿态；
5. 缩短过渡镜头和次要动画；
6. 替换次要道具为剪影或平面美术；
7. 保留三次互动的结构，但简化每次的对象数量。

不得通过删除高潮结尾或破坏三次递进来掩盖延期。

## 14. 推荐开发顺序

1. 灰盒连续小剧场：短廊、幕后、台翼、幕布、简化台前和远景面；
2. 幕布、主灯、单个皮影与三分之四操纵机位；
3. Interaction 接口与灯具约束；
4. 参数判定、保持确认和调试显示；
5. 第一互动完整垂直切片与 Dormant/SunAwakened 环境状态；
6. 复用结构配置互动二、三并补齐五个环境状态；
7. 接入最终美术、动画、音频和 Sequencer；
8. 性能、打包、盲测与录屏；
9. 只有仍有余量，才评估 Mask 升级。

## 15. 竞赛可验证性与技术证据

最终演示不能只展示完成画面，还要能证明作品的实时性、工程性与个人实际贡献，区分第三方资源和 AI 辅助。以下证据与开发同步生成，不在最后一天补拍：

| 需要证明 | 实现/记录方式 | 对外展示方式 |
|---|---|---|
| 光影由玩家实时驱动 | 固定测试机位同时拍到幕后灯/偶与幕上结果；保留连续输入过程 | 10–20 秒无切镜操作片段 |
| 判定稳定且与渲染解耦 | Development 调试层显示 Current、Target、Tolerance、Holding 与状态迁移 | 技术说明中的前后台对照截图或短录屏 |
| 三次互动复用统一框架 | 三个 `UDYPuzzleDefinition` 配置同一 Director，不复制三套状态机 | 架构图 + 三组配置对照 |
| C++ 与 Blueprint 分工清楚 | 保留核心类关系、公开事件、Blueprint 接线与 Sequencer 触发图 | 一页技术流程图，现场可快速说明 |
| 运行性能与兼容性可靠 | 从 M1 起每个里程碑记录包版本、电脑配置、分辨率、平均/最低帧率、显存观察和已知问题 | 性能表 + 最终包运行录像 |
| 作品可复现 | 记录 UE 小版本、插件版本、打包设置、默认地图、运行说明和校验信息 | `README`/运行说明 + 干净路径复测记录 |

### 演示模式

- Shipping 包保持纯净，不出现开发信息；
- 单独保留 Development 演示包或受控调试开关，用于答辩时显示判定参数、状态和帧率；
- 调试开关不得改变谜题结果，只改变可视化；
- 准备“正常演示—调试证据—恢复正常”的 30 秒以内操作流程；
- 若现场设备性能下降，优先降低次要阴影、粒子和后处理，不改变逻辑容差与剧情结果。

### 证据留存规则

- 每次里程碑至少保存一段短视频、一张带版本号的截图和一条测试结论；
- 重要优化同时保存“优化前/后”的相同机位或同一场景数据；
- 盲测记录包含测试者是否首次接触、完成时长、卡点、提示介入和修改结果，不只写“体验良好”；
- AI 辅助产生的文本、代码、图像或音频按竞赛要求记录工具/模型、用途、输入来源、人工修改与最终采用情况；
- 第三方代码、插件、模型、纹理、字体和音频继续按 `LICENSES.md` 登记，不把许可不明内容带入 Demo、视频或答辩材料。
> **第三方依赖约束（2026-10-01）**：正式版本不得依赖任何付费资产、付费插件、付费代码或付费生成服务。引入免费/开源内容前必须审查许可、版本兼容、打包条件和署名义务；无法留存授权证据的依赖不准进入正式目录。详见 `Docs/FREE_ASSET_POLICY.md`。
> **最高优先级架构约束（2026-10-01）**：*永远不要以牺牲架构设计为代价追求功能；永远不要基于猜测进行权衡——必须与我确认。* 详细职责、依赖方向、状态机、测试边界和待确认事项见 `Docs/ARCHITECTURE_DESIGN.md` 与 `Docs/ARCHITECTURE_DECISIONS.md`。
> **架构确认状态（2026-10-01）**：基础架构已经确认；阴影、幕布、判定频率和整局复位仅获准在 `Content/DengYingShanHai/Dev/` 中实验，实验结论仍需用户二次确认后才能进入正式地图。不得预设最终输入按键。

## 16. 独立 Dev 开始—三幕—结束—重演（2026-10-09）

本节记录用户已批准并实际实现的隔离闭环，不把上文历史阶段描述误认为当前完整实现，也不自动接入正式地图。

- 精确新地图为 `/Game/DengYingShanHai/Dev/EntryLoop/Maps/LV_EntryLoopDev`。Director 增加实例级 `bAutoStartOnBeginPlay`，默认 true 保留原单幕/三幕行为；新地图置 false。在初始 Inactive 下不启动采样计时器或生成首个 Activation Token，普通开始/复位口不能绕过。
- 独立 `ADYDevEntryPlayerController` 经既有 GameMode 注册链显式读取同世界 Stage。初次开始仅通过原生私有可信边界，由 Director 验证世界、引用、生命周期、序列和就绪后接受一次；UI 不直接访问该边界，不拥有第二套幕次/成功状态。
- `UDYDevEntryWidget` 只负责原生 UMG 视图与按钮意图，字体复用既有 OFL 中文资产；不持有 Director、目标/容差、精确进度或判定。菜单 UIOnly、鼠标与焦点由本地控制器拥有；开始后清旧按键状态并恢复 GameOnly。原 E/A/D/R 及 Explore/Manipulate Context 不修改。
- 最终题签和菜单等待真实林形完成经 Director 校验后的 Complete，不在第三幕参数刚 Resolve 时出现。第三幕保持既有最终状态连续落杖，A 端、Z70、15 Hz、2 秒题签和 1.25 秒 Dev 保持等原参数未改。
- 重演只允许当前真实 Complete，消耗一次请求，退出操纵后下一帧 OpenLevel 精确同地图。EndPlay 清理计时器、注册/显示委托及 Widget，不缓存旧 World 进度或重新伪造林形；旅行失败保留原终态并恢复菜单，失败分支尚未动态故障注入。
- 菜单仅在精确 Dev 世界及非 Shipping 下激活。这里的 Development 样本不能用作 Shipping 菜单已完成的证据。不添加暂停、Skip、存档、新 POV、Subsystem、扫描 Tick 或插件。

证据：原生 110/0；可见 37 项、两轮三幕、一次实际同地图重载及两次真实成林，实际退出 0；独立新包首帧/正常退出与四项启动 DryRun 通过。可见脚本使用真实 OnClicked 委托和公开参数请求，不验证物理鼠标/键盘。包内真人全流程、退出按钮、5–8 分钟、正式美术/声音、不同显示比例和 Shipping 仍待验收。

启动为 `D:\灯影山海\Start-EntryLoopDev.cmd`；合同及分层证据见 `DEV_ENTRY_LOOP_PLAN.md`、`DEV_ENTRY_LOOP_VALIDATION.md`。旧入口、旧包和原资产保留。未修改 Config，Cook 中附带旧默认 InteractionLab/Engine Entry 的事实单独记录，不把 Dev 副本算作新增竞赛场景。

## 17. 独立 Dev 灯速与就位反馈（2026-10-10）

用户已接受“灯速约降低 25%、灯／偶分别就位提示、保持进度条”的方案。新样本为 `/Game/DengYingShanHai/Dev/AlignmentFeedback/Maps/LV_AlignmentFeedbackLab`，仅一个开发验证副本，不增加竞赛场景。旧 EntryLoop、Readability 地图、启动文件和已归档包保留。

- 新地图灯组件实例速度由实际冷读基线 `0.35` 改为 `0.2625` 归一化单位／秒（75%），偶仍为实际基线 `0.28`；不是全局输入倍率，不改键位、Input Action、镜头、惯性或目标附近吸附。
- `ADYStagePresentation` 新增默认关闭的实例 opt-in。它将现有 `FDYEvaluationResult` 投影为 `FDYPlayerAlignmentDisplay`，只含必要／就位标志与原保持时钟的比例。LightReady 来自已有带滞回的有效标志；PuppetReady 同时满足已启用的位置与姿态。P01 未启用的偶条件不显示为“就位”。
- 同一 Near 内就位状态变更、同一 Holding 内时钟推进都更新只读快照；不能被原有限状态去重吞掉。公共 Native delegate 仍走显式 Stage → HUD adapter → UMG，无 UI Tick、世界扫描或第二判定器。
- 本节经用户授权放宽历史玩家视图“无任何 Holding 数值”的限制，仅允许 `HoldElapsedSeconds / HoldRequiredSeconds` 的进度条。它不传 Current、Target、Tolerance、PoseId 或 `Progress`，不声称像素重合率，不拥有独立成功时钟；第三幕 Resolve 也不显示“复演已成”。
- 单独灯或偶到位时显示下一步建议；双方到位提示松开 A／D，并在原底部区域显示细保持条。打断沿用原单次 Interrupted 计时器，进度归零并隐藏；复位、换幕、非 Playing、EndPlay 和重演清理快照及订阅。旧地图 opt-in=false，旧 HUD 文案不变。
- 15 Hz、目标与容差、约 1.25 秒保持、2 秒 Dev 题签、A 端＋Z70、真实阴影／真实树形和原 Drop → Contact → Forest → Complete 因果链均不修改。

启动文件为 `D:\灯影山海\Start-AlignmentDev.cmd`。编译／自动化、可见脚本、打包首帧与人类体验分层记录见 `ALIGNMENT_FEEDBACK_VALIDATION.md`；不得把 native seam 或参数驱动脚本记作物理键鼠／盲测签收。

## 18. 第二幕身形提示校准（2026-10-10）

用户反馈上一版可操作且体验良好，但第二幕幕上框与偶影不贴合。本次只在现有 AlignmentFeedback Dev 地图校准第二幕被动视觉参考，不修改判定或演出规则。

- 旧框以头部＋躯干包围范围再加单变量容差位移余量构成，既不是躯干参考，也不是整只偶（不含手杖）的完整轮廓；导致角标过大、视觉语义不清。
- 使用实际目标 `.72/.80`、`P02_StrideReach`，从生产投影函数、实际主灯发射点和实际幕布接收面测量当前躯干 Cube 的 8 个真实顶点。身形角标按这组投影包围范围加固定 8 cm 留白；不把判定容差画成像素轮廓。
- 新建独立 `Dev/AlignmentFeedback/Guides/MI_DY_P02BodyFit`，仅修改 `BodyY / BodyZ / BodyHalfWidth / BodyHalfHeight` 四项标量；当前地图只替换 `GuideP02` 材质槽 0。头部弧线、共享父材质、原 Readability 实例、P01/P03 参考、Actor Transform、碰撞及投影设置保持不变。
- 角标是目标躯干的构图参考：头影配弧、身影配角标，杖影不需要进入身体框。所有容差内合法状态不保证逐像素贴框；底部灯／偶“已就位”与原保持进度仍是权威反馈。视觉异常不会改变逻辑判定。
- 15 Hz、灯速 `.2625`、偶速 `.28`、目标／容差／保持时长、E/A/D/R、镜头、三幕复位与重演、A 端＋Z70 和实际落杖成林全部冻结。未修改原生源码、Config、DataAsset 或 Blueprint 图。

原启动地址不变，打开新版固定 `AlignmentDev-20261010-Run2`；旧 Run1 包仍归档，但其专用比较启动文件已于 2026-10-19 清理。范围、测量值、失败工具记录及分层验收见 `P02_GUIDE_FIT_VALIDATION.md`。这不代表正式美术、5–8 分钟盲测、其他分辨率或 Shipping 已验收。

## 19. 基础演出声音 Dev（2026-10-10）

用户已反馈第二幕身形提示“效果可以，进入下一步”。本步在同一 AlignmentFeedback Dev 地图增加一个显式引用 Stage 的 `ADYStageAudioPresentationActor`；唯一人类负责人仍为用户，Codex 辅助实现与核查。三次互动、输入、相机、判定、幕次和落杖成林时序全部冻结。

- Audio Actor 默认 opt-in=false，无 Tick、世界扫描、Director 依赖、目标／容差读取或成功判定。仅消费 Stage 的已成立只读演出事实与事件；不建新 Subsystem、时钟或流程控制器。
- 开始后的有效演出播放低音量风声；既有 Playing＋Holding 时播放轻碰节奏循环，打断／复位／换幕立即停止，不由 15 Hz 保持比例更新重新启动。P01/P02 AwaitingTransition 各播放一次木击；P03 Resolve 不播放落杖声。
- 落杖木击只由真实 Stage 接受的杖尖接触事件触发，验证当前 Activation Token 并去重；枝叶循环只在实际 Sequence Complete 后启动，不以 Holding、Resolve 或预估秒数代替。
- 五个独立 `UAudioComponent` 随当前 World 归属，初始不自动播放；同图重演重新建立实例。Stage 单独 EndPlay、引用失效、Audio Actor EndPlay 都解绑并停声；不缓存旧世界 Actor 或接触身份。晚加入只同步循环需求，不补播已成立的单次声。
- Dev 静音入口为子进程 `-DYAudioMuted`，不写全局设置；静音不改变任何玩法状态，解除静音只恢复当前需求循环，不补播历史木击。没有新增玩家键位或设置菜单。
- 五个 SoundWave 均为本轮明确 CC0 来源的本地派生 PCM，Dev 非空间化混音；不是正式锣鼓曲牌、吟唱或史实声景。源音、许可证据、处理参数与哈希见 `AUDIO_DEV_SOURCES.md` 及新审计 AudioSources；本轮不读取或改写既有许可登记文件。

独立入口 `D:\灯影山海\Start-AudioDev.cmd` 固定选择本轮声音包；原 `Start-AlignmentDev.cmd` 和旧包保持无声比较用途。当前源码地图已增加声音 Actor，因此旧入口的显式 EditorGame 回退使用的是当前工程，不能称为历史无声源码。契约、实际验证与尚未验收项见 `AUDIO_DEV_PLAN.md`、`AUDIO_DEV_VALIDATION.md`。播放请求／组件 IsPlaying／游戏混音波形与系统扬声器、人工试听、包内物理键鼠、首次玩家盲测严格分层。

## 20. 人物脚步、可闻度与空剧院声学 Dev（2026-10-10）

用户反馈“没有听到任何声音”，要求人物行走有脚步并考虑空荡大型剧院。一次只读 Windows 默认端点查询实际为静音、主音量 0；只描述查询当刻，不能回溯断言此前体验状态。Codex 不改变系统／其他应用音量。旧游戏主混音 RMS 约 -51.16 dBFS，也存在可闻度不足的独立风险。此轮为单人项目内的声音修复，不扩大物理剧场或可探索范围。

- 新建七条许可明确 CC0 的增益／脚步候选 SoundWave 于 `Dev/TheatreAudio/Sounds`；五条源只提升有限增益约 12–16 dB，时长、保持脉冲节拍和循环交叉不变。旧五声音资产、旧包均保留。音色仍不是正式锣鼓或吟唱；A/B 脚步不是已认证木地板／真实左右脚录音。
- 新 `ADYTheatreOperatorPawn` 只创建 `UDYFootstepAudioComponent`，继承原操作载体全部输入、移动、相机和复位。独立 Dev Pawn／GameMode BP 配置两段 SoundWave；只把当前 AlignmentFeedback 地图 GameMode 指向该变体，不改原 Pawn、PlayerController、输入资产或共享 GameMode。
- 脚步能力只监听真实 `OnCharacterMovementUpdated`、MovementModeChanged 和既有 OnOperatorReset。按实际地面水平位移累计，候选步距 150 cm；原 360 cm/s 速度下约 2.4 次／秒。停住、撞墙无位移、空中、传送、复位和长卡顿不积攒补发声；一轮移动更新最多一声。无 Tick、Timer、世界扫描、Director 依赖或新增按键。
- 当前灰盒没有骨骼步行动画，因此采用实际位移触发，不伪称已有 AnimNotify。正式角色／步行动画接入后可用实际足落地 Notify 提供同类声源事件；本轮不搭建未使用的大型材质／动画路由。
- 原 StageAudioActor 统一激活引擎内置混响。2.4 秒 Decay、35 ms 早反射延迟是空大剧院的算法音色候选，不是实测 RT60 或按几何声线还原。脚步、接触发送高于风与保持声，干声清晰度优先。声音仍为 2D、无距离衰减；允许读取 AttenuationOverride，关闭实际 Spatialize，开启 Manual ReverbSend，不误以为仅 Activate 就有尾音。
- Actor 使用唯一 Tag、UPROPERTY 持有运行时 ReverbEffect、原设备 Handle；从引擎实际 `GetActiveReverb()` 确认登记，诊断不是自行设定成功。Stage／Actor EndPlay 或静音时只移除自己的原生 Tag；即使 World 已禁用音频播放，仍从原设备清理，不删除其他效果。重演不继承旧脚步积累或历史木击。
- 原生混响保留有限尾音；停源／移除 Tag 不等于瞬间混音全零。静音启动无新播放请求；静音重演的数值验证在旧尾音衰减窗口后采集。实际干／湿 A/B 要证明源停止之后的有限能量尾巴；人耳舒适度与最终扬声器输出单列，不以计数替代。

入口仍为 `D:\灯影山海\Start-AudioDev.cmd`，本轮更新为固定 `AudioDev-20261010-Run2`，不随意选最新包。按键、灯速 `.2625`、偶速 `.28`、15 Hz、目标／容差／保持、第二幕身形参考、镜头、A 端／Z70、真实落杖成林与开始—结束—重演均不变。过程、来源和验证见 `THEATRE_AUDIO_PLAN.md`、`THEATRE_AUDIO_SOURCES.md`、`THEATRE_AUDIO_VALIDATION.md`。

## 21. 脚步与实际移动起停同步修复（2026-10-10）

用户反馈脚步与人物移动不同步。本节替代 §20 中将 150 cm 同时用于首次起步的旧相位契约；§20 的来源、房间声学、架构和冻结边界继续有效。只修复脚步 C++ 组件及其测试，不改任何 Content、Config、输入、人物速度、镜头或谜题参数。

- 首次起步从实际贴地运动的锚点产生 2 cm **净水平位移**后提交一声，后续每行走 150 cm 提交一声。尚未确认起步时不累计往返碰撞抖动；跨阈值的余量保留，不因首帧分割丢失。正常直线路程 D 的步数为 D<2 时 0，否则 `1+floor((D-2)/150)`；低帧仍最多一声、不补发积压声。
- 真实零位移停止后，组件清空起步／步幅状态，并停止自己拥有的直接脚步声源；不在正常跨步之间的无新声回调里误停。松开输入后的原生减速仍可移动，不能以松键替代实际停步。既有房间混响保持自然衰减，不被当作新脚步。
- 增加只读实际移动状态、起步／停止计数和原生世界时间诊断。首次 onset 与 Play 请求同一移动更新发生；计数／世界时间不代表 AudioThread callback、Windows 端点或人耳响应时间。
- 传送、空中、复位、长卡顿、静音和销毁沿用原清理；无 Tick、Timer、输入监听、世界扫描或新资产。当前操作载体没有骨骼步行动画，本次是位移起停同步，不伪称动画足落地 Notify 同步。

原入口 `D:\灯影山海\Start-AudioDev.cmd` 固定更新到独立 `AudioDev-20261010-Run3`；Run2 及更早归档保留。原生、实际行走／录音、完整三幕回归、打包首帧和人类听感分别记录于 `FOOTSTEP_SYNC_VALIDATION.md` 及 `Saved/Audit-2026-10-10-FootstepSync`。唯一人类负责人为用户，Codex 为实现与验证辅助。

## 22. 五态被动环境 Dev 合同（2026-10-11）

在已验收灰盒闭环内补齐 `Dormant → SunAwakened → ChaseAwakened → FinaleReady → ForestComplete`，不扩展空间、玩法或体验时间。本轮仍是两盏既有环境灯的对照样本，不代表正式戏台美术完成。唯一人类负责人为用户，Codex 辅助实现与验证。

- `StagePresentation` 持有环境显式引用，映射已成立的三幕序列事实；Environment 只接受状态并呈现，无 Director 依赖、Tick、扫描、判定或新流程时钟。前三态枚举值与光照原值不变。
- `bEnableFiveStateDevEnvironment` 默认关闭，只有新 `Dev/EnvironmentStates/Maps/LV_EnvironmentStatesLab` 的 Stage 实例开启。原地图、旧入口与旧包不自动升级。
- 第一幕 Playing 为 Dormant，成功题签为 SunAwakened；第二幕 Playing 为 SunAwakened，成功题签为 ChaseAwakened；第三幕 Playing 为 ChaseAwakened。真实 P03 Resolve 后序列 AwaitingFinale 才为 FinaleReady；真实树形完全生长且原流程接受完成后 Complete 才为 ForestComplete。接触、开始长树或部分生长本身不提前宣告完成。
- 当前幕复位回到该幕 Playing 对应状态；OpenLevel 重演重新建立 Dormant；迟到同步只恢复当前终态，不重放落杖、林影或单次声音。环境引用必须有效且同世界；环境广播后复核原激活身份，避免回调内复位被旧显示覆盖。
- 沿用两盏不投影的 Movable PointLight。五态光通量对为 `0/0、5000/0、3500/4500、1750/1125、5000/4500 lm`，后两态仅为 Dev 候选；不调主投影灯、曝光、阴影、位置、衰减或颜色。以同一真实最终 POV 截图对比，不把参数存在当作画面通过。
- E/A/D/R、玩家移动、脚步同步与大厅尾音、灯／偶速度、15 Hz、目标／容差／保持、题签秒数、镜头、第二幕身形参考、A 端／Z70 和 Drop → Contact → Forest → Complete 均冻结。

独立入口 `D:\灯影山海\Start-EnvironmentDev.cmd`。范围与验收分层见 `ENVIRONMENT_STATES_DEV_PLAN.md`、`ENVIRONMENT_STATES_VALIDATION.md`。参数驱动 PIE、数值混音、首帧与物理键鼠、人工听感、5–8 分钟盲测、Shipping 验收分别记录；不得互相替代。

## 23. 新幕开始时退出上一幕操纵（2026-10-11）

用户明确要求：进入下一幕后刷新操纵状态，取消上一幕按 E 建立的操纵关系，其他不变。修复只属于输入会话清理，不改变谜题、演出或复位含义。

- `ADYDevEntryPlayerController` 复用当前 Stage 的已绑定幕次事件；重新读取同世界 Director 与 Stage 的一致当前快照，只在有效 Playing 幕索引前进时，对当前拥有 Pawn 的交互组件调用既有 `EndActiveControl()`。
- 该既有路径结束灯／偶的 under-control 状态，清空 ActiveControlledActor，并经 Pawn 原回调移除 Manipulate Mapping Context、恢复 Explore。无需切镜、传送、角色复位、改灯偶参数或新增世界扫描／监听。
- 首次进入第一幕、同幕 R、Holding／打断、成功题签等待、第三幕落杖／成林／结束、重复显示同步均不额外释放。幕索引在可重入结束操纵回调前消费；新 Stage 挂接只建立该来源的真实基线，解绑／EndPlay 清除旧观察索引。
- 新幕需要玩家重新对准并按一次 E。Director 新幕 Playing 通知发生在重新启用对象之前，因此原 0.10 秒聚焦刷新可以短暂尚无焦点；不改变启用顺序或新增计时器。持续 A/D 退出操纵后沿用原 Explore 轴映射，不新增按键屏蔽、Flush 或重映射。
- 场景、资产、相机、移动与脚步、声音、五态光照、15 Hz、目标／容差／保持、题签时长、A 端／Z70 和真实落杖成林链全部不变。

当前入口仍为 `D:\灯影山海\Start-EnvironmentDev.cmd`，固定更新到独立 `EnvironmentDev-20261011-Run2`，Run1 与所有更早包保留。原声音／其他旧入口继续固定历史包，不把它们宣称为本修复版本。源码、实际 E 语义操纵与两轮完整回归、打包及保护证据见 `ACT_ENTRY_CONTROL_RESET_VALIDATION.md` 与 `Saved/Audit-2026-10-11-ActEntryControlReset`；纯 policy 自动化不代替实际 LocalPlayer／交互会话验证。

## 24. 首个免费木地板 Dev 材质样本（2026-10-11）

用户已确认 §23 的跨幕操纵修复正常。本步进入同一剧场的美术集成，先用有据可查的免费表面材质替换灰盒地面，不同时扩建空间、替换幕布或更改机制。唯一人类负责人为用户，Codex 辅助实现与验证。

- 同一 `LV_EnvironmentStatesLab` 只替换 `DEV_Floor` 的材质槽 0；Engine Cube、24×18 m 几何、BlockAll、Transform、阴影属性、全部其他 Actor 与游戏合同保持原值。原 `Start-EnvironmentDev.cmd` 固定 Run2 包仍是灰盒比较基线，不自动升级。
- 新增 `Dev/WoodFloor` 内三张 2K 纹理、一个仅供地面使用的父材质和一个常量实例。来源为 Poly Haven `Old Wooden Floor 02`，CC0；原始 PNG、API 元数据、获取哈希和许可文本保留在 `Assets/Sources/PolyHaven/old_wooden_floor_02`，详见 `WOOD_FLOOR_SOURCES.md`。
- 实际 `r.Substrate=0`，使用当前标准 PBR 输出，不启用或迁移 Substrate。BaseColor 为 sRGB/Color，NormalDX 为线性/NormalMap，ARM 为线性/Masks；RGB→BaseColor、RGB→Normal、G→Roughness、R→AO；Metallic=0、Specular=.5 对应非金属 F0=.04。冷读需检查实际节点、输出通道、父材质与地面槽，不能只凭编译成功判定画面正确。
- UV0 的 TilingU=12、TilingV=9 为 Dev 候选平铺，未认证 Cube 顶面轴向与真实板宽，不宣称物理精确 2 m。无发光、位移、WPO、透明层、材质层、MPC、运行时实例修改或新插件；不搭建尚未使用的通用大材质系统。
- 本轮不改变 C++、Blueprint 事件图、15 Hz、谜题、E/A/D/R、移动与脚步、空剧院声场、镜头、灯位/曝光/阴影、演出时长、A 端/Z70 或 Drop→Contact→Forest→Complete。

独立新入口 `D:\灯影山海\Start-WoodFloorDev.cmd`，固定 WoodFloorDev-20261011-Run1。流程、真实材质画面、源码/旧包保护、失败记录与分层验收见 `WOOD_FLOOR_DEV_PLAN.md`、`WOOD_FLOOR_VALIDATION.md` 和 `Saved/Audit-2026-10-11-WoodFloor`。该样本不代表完整剧场、正式夸父形象、美术质量认可、5–8 分钟盲测或 Shipping 验收已完成。

## 25. 免费原尺寸台翼屏风 Dev 样本（2026-10-11）

本步只增加同一 Env Dev 地图的右台翼陈设，不追加地图、谜题或通用环境框架。唯一人类作者仍为用户，Codex 辅助实现与验证。原木地板入口及固定包保留。

- Poly Haven Chinese Screen Panels（Kirill Sannikov，CC0）作为后台陈设候选；保留原作孔雀花卉图案，不声称山海经纹样、皮影专属器物或历史复原。不把网页标称1.6米屏风非等比扩成8米幕框；完整幕框与正式建筑样式仍未完成。
- 新增 `Dev/StageWings` 六包：一个静态网格、三张2K纹理、一个标准PBR父材质和一个常量实例。FBX实际单位、bounds、轴向、LOD/UV及导入配置由工具读取留证，不用网页三角数代替实际网格观察。
- 仅一个原生 `StaticMeshActor`：`DEV_WingScreen_Right`，Static/无Tick，无碰撞且各通道Ignore、无阴影、无动态间接光或距离场光照影响；不实现Controllable，不绑定Director/Stage/环境事件。原32Actor的对象路径、变换、灯组件、轨道和森林配置单独冻结。
- 材质保持实际 `r.Substrate=0`、Opaque/DefaultLit、原UV0平铺1×1；Base RGB、NormalDX RGB、ARM G→Roughness/R→AO/B→Metallic，Specular=.5。只替换本模型材质，不改原木地板、幕布和照明。位置由真实导入bounds对齐地面后冻结，核心投影域外还需实际同机位和行走验证。
- C++、蓝图逻辑、E/A/D/R、15 Hz、相机、声音/脚步、跨幕解除、目标/容差/保持、A端/Z70与落杖成林因果不变；不把NoCollision或无阴影当作画面不遮挡的充分证据。

详细范围、素材与实际结果见 `STAGE_WINGS_DEV_PLAN.md`、`STAGE_WINGS_SOURCES.md`、`STAGE_WINGS_VALIDATION.md`。仅发布门槛通过后交付独立 `Start-StageWingsDev.cmd`。软件回归不代勾作者审美、物理键鼠、听感、首次玩家、完整剧场或Shipping。

## 26. 幕框/帷幕免费资产准入与下一结构方案（2026-10-11）

本轮接用户“继续下一步”，先执行真实来源与文件准入，不把未经检查的成品场景塞入关卡。唯一人类作者仍为用户，Codex辅助；本轮只有文档与隔离审计变化，没有Content/Source/Config/启动器或新包变化。

- 实际隔离下载3DAssets.dev CC0 Stage Leg/Border两个GLB及API/许可。离线解码geometry/indices/节点TRS，面数1384/4400、顶点2926/9826与发布方一致；两模型的所有primitive无TEXCOORD，images/textures均0，仅材质常量。PASS是文件检查成功，直接近景资产决策为REJECT，不是UE导入或画质通过；AI来源如实披露。
- 官网西式Proscenium净口7.2×5.2m不容纳当前Dev9×8m接收体，且装饰风格不适配，排除直接使用。人工CC0木构候选网页有UV声明但浏览器下载页429，未取得模型；不登录、不支付、不绕限制。
- 下一结构路线为木构承托框与布质侧幕分离，精选免费构件后独立适配；优先一个通过真实尺寸/UV/材质检查的最小样本，不预建新大型框架或空启动器。不把1.6m家具拉大充幕框，不自动改变接收体/主灯/POV来迁就资源。
- 静态陈设使用原生StaticMeshActor；确需固定组合才考虑一个仅持SMComponents的表现Actor/BP。无Director依赖、Tick、世界发现、谜题或第二流程时钟；将来状态表现仍由既有StagePresentation→StageEnvironment明确驱动。
- 标准PBR/r.Substrate=0、材质族与原UV实测、现有曝光/五态灯值和真实投影保持。原33Actor、控制/复位/声音/成林合同冻结；旧灰盒结构不能被顺便移动、隐藏或删除。全建筑风格与正式尺度迁移不在本次自动定稿。

实际来源和排除证据见 `STAGE_FRAME_ASSET_REVIEW.md`，下一样本选型、文件边界、材质/光照/生命周期与验证步骤见 `STAGE_FRAME_NEXT_PLAN.md`。当前运行入口仍是固定 `Start-StageWingsDev.cmd`；没有本轮新的玩法、音频、首帧、性能或Shipping验收。

## 27. 单柱免费资产与材质方向准入（2026-10-12）

接 §26 的下一最小构件任务，已取得 VVayToyek 免费 CC0 原始亭台 ZIP，离线仅提取“檐柱1”；不导入整亭、不改主地图。§26 的下载429是前一阶段真实记录，保留原审计，本次追加正常匿名下载成功记录。唯一人类作者仍为用户，Codex辅助实现/核查。

- 派生 FBX 保留 Geometry/Normal/UV 原属性字节、单位、轴向与缩放；只删去无关对象/连接、重置该 Model 原场景平移、更新对象计数。独立96项源数据核对通过。不把下载页“复原”宣传作为历史依据。
- 实际 UE 檐柱尺寸285.278×285.278×2036.122cm（Z向上），252三角面、384渲染顶点、UV0、两个原槽。源高度20.36m真实保留，不臆改为毫米或自动等比适配现有8m接收体；当前只是未摆放的 Dev 资产。
- 七份新资产只在 `/Game/DengYingShanHai/Dev/FramePostAsset/`：一 StaticMesh、三份2K纹理、一 Surface/Opaque/DefaultLit 单面标准PBR父材质和两个常量MI。Mesh→MI→父材质→纹理，无Director/Stage事件、Actor、Tick、Subsystem或状态职责。没有自动碰撞、Nanite、世界映射、WPO、MPC或新增渲染路径。
- Dark Wood 采用官方 CC0 2K Diffuse/NormalDX/ARM，实际字节数与官方MD5一致。BaseColor=sRGB，NormalDX=线性/NormalMap，ARM=线性/Masks、R=AO/G=Roughness/B=Metallic，Specular=.5。先查实际图与UV；Wood Table 原图有拼板接缝，仅保留来源对照、不导入。
- 源柱侧面长轴对应V，纹理顺纹对应U；木柱槽0采用 `(V,1-U)`，切线法线同步变换 `(-Ny,Nx,Nz)`，基座槽1保留UV0。`UVQuarterTurn`只支持实例端点0/1，不作为连续旋转控件。1×1采样只用于方向检查，物理纹理密度、端面/柱脚、近中远与主场景光照未定稿。
- 创建前两轮节点/检查器失败均未保存资产；Run3确实保存七份。真实D3D12/SM6冷读1395项检查通过、退出0、未保存；查看器真实纹理采样与纵向木纹已留图。1490/1395是审计断言数，包含文件保护，不是新增游戏单元测试数。启动时既有13条smoke通用断言仍留证，不宣布日志零错误。

新 `Start-FramePostAssetReview.cmd` 仅打开 UE 原生静态网格查看器，不是游戏入口或新包；当前可玩仍打开 `Start-StageWingsDev.cmd`。来源、失败记录、原生API边界、图形会话与后续比例/摆放门槛见 `FRAME_POST_ASSET_SOURCES.md`、`FRAME_POST_ASSET_VALIDATION.md`。不关闭完整幕框、帷幕、夸父造型、正式画质、性能、盲测或Shipping里程碑。

## 28. 单柱独立可玩 Dev 构图样本（2026-10-12）

接 §27 资产准入，用户明确选择“完整可玩样本：追加精确路径及测试”。负责人仍为用户独立制作，Codex辅助实现与验证；不依赖队友或WorkBuddy。本次是同一既有剧场的独立Dev比较样本，不增加竞赛版本的场景数量。

- 新地图仅为 `/Game/DengYingShanHai/Dev/FramePostPlacement/Maps/LV_FramePostPlacementLab`。由原EnvironmentStatesLab模板生成，保留原33个Actor的已列举变换、组件、灯/轨道、流程、音频与成林合同，再增加一原生StaticMeshActor。仅在 `DYDevEntryPlayerController.cpp` 增加该地图的精确身份分支，在 `DYEntryLoopAutomationTests.cpp` 增加对应独立测试；不放宽目录/前缀匹配，不改变旧四地图与Shipping边界。
- `DEV_FramePost_Right` 复用上一阶段已验证的七资产。20.3612m原柱等比缩放至8m候选高度，XYZ统一比例约 .39290377，位置约 `(950,540,0)`cm、旋转0；底座世界宽约112.09cm。核心保护盒Y上界470cm，底座最近Y约483.9566cm，保留约13.96cm间隙。8m只是获准制作的Dev构图候选，不是正式建筑尺度、玩家阻挡或整体幕框定稿。
- 新柱仅承担被动陈设：Static、Actor/组件Tick关闭，组件与BodyInstance均NoCollision、公开八通道Ignore、Overlap关闭，不实现DYControllable；不投影、不影响动态间接光/距离场光照。Actor总碰撞开关保持true，以免遮掩组件规则。无新Blueprint、Director引用、谜题条件或世界扫描；这些标志不保证所有屏幕空间/GI路径零影响。
- 材质保留原两MI与UV方向约定：柱槽 `(V,1-U)` 及切线法线 `(-Ny,Nx,Nz)`，基座原UV。未修改幕布、主灯/曝光、操纵POV、旧木地板/台翼、输入、15Hz、谜题参数、声音/脚步、跨幕取消操纵和真实杖落成林。固定POV的五态画面已检查，但纹理物理密度、近景端面、接缝和最终画质仍待独立验收。
- 实际Editor Development构建退出0；原生项目自动化155成功/0失败，新精确地图测试成功。冷读是真实D3D12/SM6、未保存，1468项为审计断言而非155之外的游戏测试。完整PIE分别通过65流程、35环境、41实际控制断言及10次独立柱合同观察，包含两次真实成林、一次OpenLevel重演与跨幕会话清理；语义输入不等于物理键盘盲测。控制探针为聚焦临时调整过视线，不冒充同POV证据；同POV由另组五态截图证明。
- 独立Windows Development包真实UAT退出0。首次检查器错误要求Zen Cook生成松散umap，保留该FAIL；不重跑UAT，改用UE原生只读IoStore目录与全部payload哈希校验：41条冻结必需依赖、主容器2027个chunk和global 1个chunk通过。包身份和50个归档文件保持固定，首帧验证另存补充记录，不追改旧身份字段。
- 新固定可玩入口为 `D:\灯影山海\Start-FramePostDev.cmd`，默认只启动 `Builds\FramePostDev-20261012-Run1\Windows`，不会选最新目录或默默退回编辑器。显式EditorGame只作诊断。三次真实CMD→Windows PowerShell 5 DryRun通过；曾出现的PS7/PS5模块路径问题仅用CMD子进程局部环境隔离修复，没有改全局环境。真实打包窗口的中文开始菜单、点击“开始复演”后的场景/柱/实时偶影已核查，正常关闭后游戏和CMD退出均0；没有把首帧称为完整打包通关或人类审美验收。

创建探针、首次WorldMemoryLeaks、原生容器参数检查器失败和原启动smoke断言均保留原证据；不读受保护getter、不覆盖失败结果、不因后续通过宣称日志零错误。历史 §27 的资产查看入口仍是查看器，旧 `Start-StageWingsDev.cmd` 与旧包保持原字节。本步具体文件范围、许可来源指向、实际失败与待验项目见 `FRAME_POST_DEV_VALIDATION.md`；最终保护以 `Saved/Audit-2026-10-12-FramePostPlacementDev/FINAL.json` 为准。

## 29. 同源横梁资产准入与布质侧幕复查（2026-10-12）

接 §28 单柱可玩样本，按下一最小构件准入范围推进。用户仍为唯一人类作者，Codex辅助；本步只新增一个未摆放的Dev StaticMesh及其独立查看入口，不改C++、Config、地图、玩法、镜头/灯光、声音或旧包，不把一个梁构件称为完整幕框。

- 从已取得的VVayToyek CC0亭台中选择真实“额枋1”Model824772630→Geometry512851073→Material450385832，非横放柱子或重新造型。只移除无关对象/连接、将Model场景平移置零、调整定义计数；原Geometry/法线/UV/材质、Header/Footer、轴/单位与局部枢轴保留。独立扫描器逐256节点比原属性字节，不执行主提取脚本作证；其初版数量断言错误FAIL保留，Run2通过。
- 唯一新包 `/Game/DengYingShanHai/Dev/FrameBeamAsset/Meshes/SM_DY_FrameBeam_Source`。原生FBX导入scale=1/场景单位转换/ImportNormals，未自动生成材质、纹理、碰撞、Lightmap UV或Nanite，未导入整亭。实际UE尺寸2630.546631×111.114189×142.727215cm，长轴X、局部origin Z28.636393cm、28tri/48render vertices/1UV/1section；源16vertices是拆分前数据，不声称额外建模。源26.31m不是正式尺度，不自动缩放或按pivot猜接合。
- 原单槽“额枋”显式复用已冻结 `MI_DY_FramePost_Wood`→`M_DY_FramePost_Master`→三张Dark Wood纹理。8条源长边实读沿UV V，沿用实例QuarterTurn=1的 `(V,1-U)` 与 `(-Ny,Nx,Nz)` 法线逆基底，旧五依赖和原七柱资产字节不改。不搭新Master/动态MI/MPC/全局渲染路径；仍Surface/Opaque/DefaultLit/单面、r.Substrate=0。1×1只是方向比较，近景端头、纹理物理密度、接缝及GPU尚未验收。
- 本步没有Actor、BP、状态、Tick、Director通信或第二流程所有者。依赖仅新SM→旧常量MI→旧父材质→旧三纹理。尚无地图引用/Cook范围变化；今后摆放才采用被动原生StaticMeshActor，需单独冻结world bounds/碰撞/投影，复测完整流程与独立包，不提前创建运行框架。
- 实际probe1447检查/保存0、create1464/仅保存1新mesh、真实D3D12/SM6 cold1457/保存0，原生退出均0；这些是资产/文件审计断言，不是新增游戏测试。原生网格查看器确实显示长向木纹和完整梁形，查看器背景为引擎内置预览环境，不是游戏空间；跨轮Esc停止Computer Use的记录保留，窗口正常退出是否通过以实际非null EXIT及补充关闭记录为准。
- 新 `D:\灯影山海\Start-FrameBeamAssetReview.cmd` 只看网格，不开游戏、不改尺度/保存/重导入。入口绑定1新mesh+精确唯一5旧依赖、各SHA与最终清单；发布前补上仅检查count=5的缺口。WindowsPS5 UTF8 BOM、子进程模块路径、立即保持Handle与拒绝null退出码沿用已验证方式，不改全局设置。普通入口DryRun与预发布GUI会话分开记录，不互相替代。
- 布质侧幕新一轮实际文件检查：Innerscene CC0纱帘GLB有47mesh/实际UV与法线/2材质/3嵌图，但透光家居用途不适配厚台翼；Blender Studio Cube Diorama官方CC0 ZIP已取得，只有Zstandard封装.blend与目录表，本机未找到现有Blender CLI，未解码场景，不猜packed纹理；MZiemys Curtain需登录，未取得、不绕限制。既有无UV的3DAssets帷幕不重新准入。

来源与派生见 `FRAME_BEAM_ASSET_SOURCES.md`，实际验收/失败/入口见 `FRAME_BEAM_ASSET_VALIDATION.md`，布料排除与候选见 `CURTAIN_ASSET_REVIEW.md`。最终产品/旧包/来源保护以 `Saved/Audit-2026-10-12-FrameBeamAsset/FINAL.json` 为准。可玩仍用 `Start-FramePostDev.cmd`；正式比例、幕框接合、布质台翼、全场景质感、5–8分钟盲测、性能与Shipping未关闭。

## 30. 梁柱真实接合切面与纹理频率依据（2026-10-12）

本轮只做离线 Dev 构图依据，新增 `FRAME_BEAM_PLACEMENT_PLAN.md`；没有改地图、C++、Config、资产、入口、包或运行UE。用户仍是唯一人类作者，Codex辅助，不依赖手工建模或其他成员。

- 从实际 native 冷读及两份派生 FBX 重新扫描梁底 polygon9、柱顶32边 polygon30。柱8m等比 `.39290377163557627` 时梁长1033.552cm。居中梁的整件AABB虽与右柱侧界重叠16.066cm，真正最低底面仍离柱顶最近点11.301cm、平面交集0；因此不能以bounds接触宣布接合。
- 只推荐比较同源同等比、Yaw90、Location `(950,23.22415363604682,816.7876838516025)`cm 的局部接缝候选，不改旧柱、不补左柱。梁world bounds X[928.171408,971.828592]、Y[-493.551693,540]、Z[800,856.078061]；距幕顶50cm/核心盒顶30cm。实际两源几何平面交集421.829cm²不是榫接、UE物理接触、承重或画质认证；当前无左支撑，不能称完整幕框。梁顶齐柱顶的源相对高度侵入核心盒26.078cm，应排除。
- 另比较梁自身等比长1080cm/1158.581cm的候选，均不拉伸截面，但相对柱源比例分别改变4.494%/12.097%；未确定正式尺度或编写地图。AABB分离不推导最终POV、主灯光锥或所有GI/反射隔离。
- 方向沿用UV0→QuarterTurn1 `(V,1-U)`、Normal `(-Ny,Nx,Nz)`；实际轴向采样不一致：当前柱约259.60源texel/m，同柱scale的梁顶约140.11、两侧/底约198.15。2K源采样覆盖不是实际mip、屏幕pixel或美术目标。现有父材质没有Tiling参数，不能仅新建MI假称可修；先保留共享旧材质做实际近中远对照，确需密度修订才单列有界Dev父材质副本，不覆盖旧资产或换渲染路线。
- 下一实际样本仅一个原生被动StaticMeshActor与唯一组件，在独立新Dev图由World拥有；无Director/Controllable/Stage绑定、Tick/Timer/扫描/网络/存档。本轮没有新引用或Cook。五态同POV、真实控制/复位/跨幕/两轮三幕/成林/音频及固定Development包必须另行实际验证，不重称旧155/65/35/41为本轮测试。

保护与失败见新方案及 `Saved/Audit-2026-10-12-FrameBeamPlacementPlan/FINAL.json`；原326产品仅两文档原字节前缀追加、一新方案，旧926归档/15来源/24隔离来源保持。六项平面裁剪sanity与精确输入哈希只作数值证据，无受限登记读取、Git写入或文件清理。可玩仍 `Start-FramePostDev.cmd`，正式美术/建筑尺度/完整框/帷幕/盲测/GPU/Shipping未关闭。

## 31. 横梁与右柱独立可玩 Dev 接缝样本（2026-10-13 完成记录）

接 §30 离线接合依据，用户继续下一步；唯一人类作者和负责人仍为用户，Codex辅助实现/验证，不依赖队友、WorkBuddy或手工建模。本次只有一个新独立Dev比较地图，不改变竞赛单主地图、三次互动和体验时长边界。

- 新地图精确身份 `/Game/DengYingShanHai/Dev/FrameBeamPlacement/Maps/LV_FrameBeamPlacementLab`，从既有单柱地图模板生成；保留旧34Actor已列举合同，只加原生StaticMeshActor `DEV_FrameBeam_RightJoint`，实际35Actor。现有C++入口只追加这一精确身份，测试只追加对应独立用例；旧五图、上下文拒绝与Shipping边界不变，没有Dev目录/前缀宽泛放行。
- 梁Location `(950,23.22415363604682,816.7876838516025)`cm、Pitch0/Yaw90/Roll0、XYZ等比 `.39290377163557627`；与旧柱同源同比，梁底Z800、顶Z856.078061，距幕顶50cm/核心盒顶30cm。真实源底面/柱顶约421.829cm²交集候选落实为实际Actor变换与bounds，不把整件AABB重叠当榫接/物理/承重或正式尺度。未加左柱，左端未支撑，不称完整幕框。
- World拥有唯一被动Actor/SMComponent，Static、无Tick/Timer/世界扫描/复制/存档、无Controllable/Director/Stage通信。Actor总碰撞true，组件与BodyInstance NoCollision、公开八通道Ignore、Overlapfalse；投影/HiddenShadow/动态间接/距离场false。这不是玩法光影所有者，也不代表全部渲染路径零影响。依赖仅旧梁SM→旧常量MI→旧Master→三纹理，无新BP/材质，旧资产字节冻结。
- 保留原木材方向/Normal基底、旧木地板/屏风/幕布/灯光/曝光/POV、E/A/D/R、15Hz、谜题/保持/提示、脚步/声音、跨幕取消与杖落成林。本步不修共享UV密度：柱259.60、梁顶140.11、侧/底198.15源texel/m只是采样依据，现有父材质无Tiling参数，近中远/实际mip/画质目标另验。
- 实际Editor Development构建退出0，156原生项目测试成功/0失败/0未执行，新 `FrameBeamExactMapIdentityAndContexts` 成功。probe1476/旧34、create2242/新35/只保存新图、真实D3D12冷读1498/保存0；这些是审计断言，不是上千游戏单元测试。没有执行Shipping。
- `VisiblePlay-Run2` 完整65流程/35环境、两次真实成林/一次OpenLevel重演，旧柱10/新梁10独立五态观察；第一轮五态实际最终POV读回完全一致，无相机写入。两cycle Master Mix WAV导出完整，静音流程保留；不代签Windows输出/耳朵听感。独立 `ControlProbe-Run1` 41项通过、两次成林/一次重演、真实位移和EndPlay清理；其临时聚焦视线调整不是固定POV组，也未录混音，不称物理键鼠测试。
- `VisiblePlay-Run1` 四前态POV相同、结束时PC朝向变化使严格五态阈值失败，实际输入来源未知；保留FAIL，不归因镜头延迟、不改产品或判据、不强制复位相机，再按原条件Run2通过。正常原生退出0不等于观察器PASS。旧smoke与其它历史失败仍留存，不宣称日志零错误。

- 一次实际UAT退出0；`Package-Run1/RESULT` 因错误要求“Cooked地图仅一张”仍保留FAIL。独立Recovery实读本机UE Cook源码与两级Config，确认精确三图为显式新梁图＋项目GameDefaultMap Interaction＋继承ServerDefaultMap Entry，没有NoDefaultMaps参数；后两图不提供选择。Recovery只读恢复精确UFS门控，不改Config、不重UAT、不覆失败，不宣称包内只有一图。
- 原生IoStore列表/主payload/global三次实际exit0，2029主chunk＋1global全哈希、299312275/3224104B读入、42核心＋2默认共44指定export通过；生成固定包身份后封存50文件/1070522460B。身份FirstFrame/Gameplay/PackageAudio/HumanVisual/Shipping false原样，后续首帧另外留证，不追改历史字段。未要求Zen松散umap或脚本读取ProjectStore替代原生校验。
- 原PS5隔离试验的JSON顶层数组包装兼容失败留存，发布前仅两处改为直接ConvertFrom-Json。实际launcher SHA D24E5E00050F25FCCD68A5945DE7163ADEABAB473DCCC459B9B83EBF93821A6E，PS5解析0；真实谓词fixture隔离29案例（4正exit0/25负exit1对应门控）全匹配，没有启动UE/游戏或写D。此反例测试不是实际包首帧或真实CMD验证。

- 发布入口默认Package/显式Package/显式EditorGame三次真实CMD/PS5 DryRun均实际exit0，没有启动游戏/UE或创建game Run。实际PackageFirstFrame-Run2由官方Computer Use观察中文菜单、点击开始、留含梁场景截图并只对精确游戏窗口正常Alt+F4，NativePID37448/Window3277942；真实Game0/CMD0、日志新图LoadMap与Exiting绑定，不称全日志零警告。
- 首帧后审计检查器 `[int]Run` 与本地 `$run` 大小写不敏感冲突报Int32转换，原RESULT FAIL保留，不是游戏/产品失败。只修审计变量，独立补充实读331产品/50封存SHA、PID/地图/截图/真实exit0，SUPPLEMENTARY-RESULT首帧PASS；不重游戏、不改产品/原FAIL/历史包身份。FullGameplay/PackageAudio/HumanVisual仍false，首帧不是包内两轮通关。

新 `D:\灯影山海\Start-FrameBeamDev.cmd` 只绑定 `Builds\FrameBeamDev-20261012-Run1\Windows`，无最新目录/静默Editor回退；旧 `Start-FramePostDev.cmd` 保持。2026-10-13完成记录不改旧20261012审计/包身份。最终发布合同332产品/四旧变更/五新，实际集合与旧926归档/来源/Git保护以本轮 `FINAL.json` 为准，不提前宣称最终PASS；分层结果见 `FRAME_BEAM_DEV_VALIDATION.md`。正式完整框/侧幕/近中远接缝画质/尺度/GPU/盲测/包内三轮与Shipping未关闭。

## 32. 梁柱接缝与木纹：只读原生实图诊断（2026-10-13）

接 §31，用户继续下一步；负责人和唯一人类作者仍为用户，Codex辅助。本轮只拍现有独立梁图，不新增资产/地图/C++/玩法/输入/声音/包，不改旧共享材质、主灯/曝光或游戏POV，不补左柱或确定正式尺度。

- 专用Editor加载精确 `LV_FrameBeamPlacementLab`，原生D3D12/SM6、Lit、非PIE、无pilot；同活动key水平FOV实际90°、只读，不调用FOVsetter。Editor诊断视口近2.562m/中9m/远22m同目标/方向/分辨率，仅距离变化；底面2.607m、斜端2.982m另组。五张1920×1080原始PNG逐图Task/文件头/尺寸/字节/SHA/机位记录，未提亮或重绘，不冒充玩家位置/最终POV。
- 每图前后实际35Actor冷契约、原柱/梁完整契约一致；只临时移动Editor viewport，native highres暂切GameView后恢复，无CameraActor/Controller/地图或资产保存。结束恢复原位置/旋转、FOV90/GameViewfalse，NativePID6672/Exit0非null。原生highres FinishLoading并禁用ScreenPercentage，因此不能认证运行时mip/性能/实际游戏分辨率、活动nearclip或正式美术。
- 独立源面复扫确认底面比尖端退进27.367484cm，柱顶共面交集421.828972cm²/8.754%。实图梁侧横纹/柱纵纹可辨，削角端与柱顶外露；构造感仍偏局部搭接。柱顶/端面暗近黑，不能据此认定空气缝、穿模、端纹缺失或normal错误，接合/暗面美术不验收。
- 旧QuarterTurn1/NormalDX基底保持；柱259.60、梁顶140.11、侧/底198.15源texel/m仅采样依据，同MI不等密度，父材质无Tiling参数。没有仅建MI假修、独立Master或全局渲染变化。
- 未实施Y平移候选：+43.551693cm在整梁外框仍横跨幕宽时达到48.212%柱顶交集，底面仍短左幕27.367484cm；+66.657861cm使柱顶Y全包达到67.098%，整梁却短左幕23.106168cm，底面短50.473652cm。窄X使任意Y平移不能全包柱顶；材质不能补面积。只建议原样与保幕宽候选独立对照，不自动实施取舍、非等比加粗/补柱/托件或改幕。
- `Render-Run1` native0但审计重入FAIL/0合格图保留：native先ToggleGameView再FinishLoading/BindTask，加载泵Slate递归settle误检查临时状态。只给审计脚本BUSY/DONE/requesting防护，保持全部阈值；3s warmup不作为startup根因。Run2真实5图成功；日志初始化Condition failed及TSR警告仍存在，不说日志零错误。本轮未RunTests/编译/UAT/包通关/声音/Shipping，前轮156/65/35/41只作历史。

交付 `D:\灯影山海\Docs\FRAME_BEAM_JOINT_REVIEW.html`（资源管理器双击看图）与MD报告；只向两现有Docs追加原字节前缀保留，其余产品/976包文件/15来源/24隔离来源/Git保护以当前Audit `FINAL.json` 为准。无受限登记读取或删除。可玩入口仍 `Start-FrameBeamDev.cmd`，不是本轮新包。最终接合/暗面/完整框、布质台翼、正式比例、GPU、盲测/包内三轮和Shipping未关闭。

## 33. 梁柱保外轮廓幕宽候选：未保存的A/B实图实验（2026-10-13）

接 §32，继续工程下一最小对照；用户为唯一人类作者和负责人，Codex辅助。只在专用Editor内存里移动既有梁ActorY，拍图后恢复，不新增／保存地图或资产，不改C++、Config、玩法／输入／声音、材质、灯光／曝光或游戏POV，不补左柱／托件或非等比加粗。

- A原Y23.22415363604682，B仅+Y43.55169272790636cm→66.77584636395318。X950/Z816.787683852/Yaw90/XYZ等比.39290377163557627与35Actor不变。World仍拥有原被动StaticMeshActor，无新框架／BP／Tick／Director通信。
- B真实柱顶共面覆盖2323.173235cm²/48.212%（A421.828972/8.754%）；全梁Y[-450,583.551693]仍跨900cm幕宽，但底面[-422.632516,556.184209]左短27.367484cm，未全包柱顶／梁底幕宽，非承重或榫卯合格。+66.657861大移位本轮未试，不能因面积最大自动采用。
- 三固定机位（近／底面／整体）A/B各一，真实D3D12/SM6、Lit、同active key/FOV90°/1920×1080，取景不追随梁移动、FOV只读；无PIE／CameraActor／Controller／Sequencer写入，非玩家位置。六张Run2原图未提亮／裁切／重绘，均有Task/头/尺寸/字节/SHA/机位。
- 新工具仅复制旧beam字段reader的AST原生读数部分，不执行旧author/verify/protect或改旧断言；完整Cold契约只放行7个明确Y标量，各只接受精确delta与1e-7cm误差，其余键／值／列表严格相同。每图前后全Actor/原柱/灯／流程／玩家CDO等既有合同未变；最后用原捕获Transform恢复，全部Cold一致，原视口恢复、FOV90/GameViewfalse，dirty map/content全程0且不清flag。磁盘保护另验。
- 实图B跨更多柱顶、局部接合更容易读懂；整体显示左端余量被消耗。只建议B进入下一独立可玩Dev候选，不作为正式采用；暗面仍不能证明无缝、穿模、端纹／normal正确，仍非完整幕框／消除廉价感。旧MI/Master/UV QuarterTurn/Normal基底冻结，源texel/m不当游戏mip；不新材质或shader参数变体。
- Run1正常六图/恢复/native0保留，不伪改FAIL；独立审查随后发现其Actor恢复guard异常可能跳过view。仅审计工具拆双try、汇总errors/pending Task；四离线mock案例通过，非UE／游戏回归。新Run2 native0/六图/恢复通过。Highres强制加载／禁ScreenPercentage，不认证实时mip/GPU/nearclip；日志错误／警告保留，不说零错误。本轮未编译/RunTests/PIE/UAT/Cook/声音／包通关／Shipping，前轮结果仍历史。

交付 `D:\灯影山海\Docs\FRAME_BEAM_JOINT_AB.html` 与MD，只两Docs追加／两新报告，334→336产品，其余332产品、976归档／15源／24隔离源/Git以本轮Audit `FINAL.json`保护。实现只留Saved、无运行依赖，不读受限登记／不删除。可玩仍 `Start-FrameBeamDev.cmd`，没有新包。下一独立可玩候选需精确图身份／文件白名单及原流程/镜头/控制/成林/重演/声音与Development包实际回归，不据照片关闭正式构图／暗面／完整框／尺度/GPU/盲测／包三轮／Shipping。


## 34. B 摆放独立可玩 Dev 候选（2026-10-13）

接 §33 实图 A/B，用户继续下一步。唯一人类作者和负责人为用户，Codex 辅助。只把保全梁外轮廓幕宽的 B 摆放序列化为独立 Dev 比较图，不覆盖 A 图／入口／包，不改变单主地图、三互动、体验时长或分工；不是正式美术采用。

- 精确新图 `/Game/DengYingShanHai/Dev/FrameBeamCandidate/Maps/LV_FrameBeamCandidateLab` 复制既有 `LV_FrameBeamPlacementLab`，仍 35 Actor，无增加／删除。只将 `DEV_FrameBeam_RightJoint` Y 从 23.22415363604682 加 43.55169272790636 cm 到 66.77584636395318；X950／Z816.7876838516025／Yaw90／XYZ 等比 .39290377163557627 固定。归一化新旧包名后，只准 7 个明确 Y 标量，各只接受精确 delta、1e-7 cm 浮点误差；其他全部键／值／列表冷读严格保持，创建和另进程冷读分开，不把内存图当保存图。
- World 拥有同一被动原生 StaticMeshActor／组件；Static、无 Tick／Timer／扫描／网络／存档、无 Controllable／Director／Stage 通信，Actor 碰撞总开关 true，组件与 BodyInstance NoCollision／八通道 Ignore／Overlap false，投影／HiddenShadow／动态间接／距离场标志 false。已有 Stage → Environment 显式引用和 Director 事实所有权、菜单／最终 POV 所有者与 OpenLevel 生命周期不改。没有新类、BP、状态或通用框架，不能据这些标志宣称全部 GI／反射／GPU 零影响。
- 依赖仍为旧梁 SM → 旧常量 MI → 旧 Master → 三木纹图；不新增模型／材质／纹理／音频／字体／插件／付费资源，不重写共享 UV／Normal 基底。旧柱、幕／地面／屏风、主灯／曝光／游戏 POV、E/A/D/R、速度／15 Hz／目标／容差／保持、第二幕提示、声音／脚步、跨幕取消与 A 端／Z70／真实落杖成林链冻结。
- C++ 仅在现有入口白名单追加本精确图身份、对应测试追加一个独立用例；旧六图、上下文拒绝与 Shipping 门控保留，不放宽 Dev 目录或前缀。实际 Editor Development 构建 0，原生 157 成功／0 失败／0 未执行。probe3772／create9035／cold6025 是审计断言，35 Actor、只保存新图已实读；不是数千游戏测试。PLACEMENT 初版 Label 缺项仅在静态运行识别后补元数据，原稿保留，不伪称原生 FAIL 或产品修复。
- 本轮 `VisiblePlay-Run1` 实际 native0／65 流程／35 环境，旧柱10／B梁10五态观察、两次真实成林／一次 OpenLevel 重演、两 cycle UE Master Mix 导出；五态实际同 PlayerCameraManager、位置(-1260,-155,178.1500015258789)／rot0／FOV70。原图实际查看，为含开发界面的 Editor viewport，非 standalone／正式高质量定稿。`ControlProbe-Run1` native0／41项，真实语义聚焦操纵／R／步行／跨幕释放／两次林／一次重演／EndPlay清理；其临时聚焦视线调整另组，不充当固定 POV，语义与混音不代物理键鼠／Windows输出／耳朵听感。整个原生回归338产品 SHA／集合不变，旧结果不重称当前。
- 实际 UAT-Run1 native0，严格三图为显式 B 图＋未改 Config 的项目 Interaction／引擎 Entry 默认图；后两图不提供玩家选择。三个原生 IoStore 实际 exit0，2029主chunk／1global全部payload哈希、299312275／3224104B、42核心＋2默认export实查；固定包50文件／1070536087B。身份生成时 FirstFrame／Gameplay／PackageAudio／HumanVisual／Shipping false 保留，后续只另写补充，不覆历史。未 cookall／宽泛 AlwaysCook／松散补包。实际 MSVC14.51.36260（目录14.51.36231）／SDK10.0.26100.0与UE非首选警告保留，不改环境、不宣称零警告。
- 入口两文件发布阶段340产品；原生PS5.1.26100.9444解析0／Run2隔离31例(4正27负)实际非null退出与门控全匹配，launcher SHA2118791870CE2E2A691EC2182A2304E215488F4D238E692F0A74307273D7B018。三种真实 CMD／PS5 DryRun（默认Package／显式Package／显式EditorGame）实际均0，无 UE／game启动。首轮29例与PS5作者编码／Package静态encoding／EOL工具FAIL原样保留，只修工具、未改产品。
- 官方CU首帧初因Windows防火墙许可弹窗PENDING，未操作安全弹窗／修改权限，交用户手动处理。用户反馈关闭后只读核发现同PID10892仍活、同窗口591026最小化，不将先前反馈当已验证退出；只激活现有窗口，系统弹窗已消失。中文菜单完整观察→实际click开始→B梁场景→只对该窗口官方Alt_L+F4正常关闭，实际Game0／CMD0，`PackageFirstFrame-Run1/RESULT`为PASS-PUBLIC-PACKAGE-MENU-START-FIRSTFRAME-NORMAL-EXIT，Identity／Products unchanged true。无重复启动／Run2／重建包，UAT仅一次；早先PENDING保留。Menu／Started原生JPEG保留，PNG仅转封装且全1922×1248 decoded32bpp逐像素一致、未裁剪／提亮／改色，非原生PNG。UAT0／DryRun／fixture 不代首帧，当前首帧也不代包内全通关／包音频／人工美术／Shipping，FullGameplay／PackageAudio仍false，固定身份历史字段不改。
- 同PID实际Session log绑定精确候选图LoadMap带?Name=Player、Win RequestExit及Exiting；不只凭画面／窗口消失推定退出。首次JPEG包装工具MIME guard失败在任何文件写入前，后续保留JPEG／逐像素PNG包装验证，非游戏FAIL，不改包／产品。

新入口 `D:\灯影山海\Start-FrameBeamCandidate.cmd` 固定 `Builds\FrameBeamCandidate-20261013-Run1\Windows`，不选最新／静默 Editor 回退；本轮分层结果见 `FRAME_BEAM_CANDIDATE_DEV.md`／HTML。旧 `Start-FrameBeamDev.cmd` 保留最小运行回退。336→338 创建／340入口阶段实录，最终六新／四旧改、342 集合与 332 旧产品／976 旧归档／15 源／24 隔离源／Git 保护以当前 Audit FINAL 为准，未在文档提前声称FINAL已生成，受限登记不读／哈希，失败与旧身份不覆／不删。

B 柱顶共面覆盖约 48.212%，但梁底左短幕 27.367484 cm、未全包 cap／全宽；不是完整幕框、承重、榫卯或历史尺度。正式采用、暗面／端纹／normal／无缝／穿模、运行时 mip／GPU、左支撑／布幕／空间、5–8 分钟盲测、包内三轮和 Shipping 仍待验。文化创新仍为灯／影／夸父与玩家直接落杖成林，木构服务演出，不用装饰代替机制。

## 35. 实际B木构近景与源UV/Normal诊断（2026-10-13）

接 §34，只读实际保存的 FrameBeamCandidate 图，不在A内临时模拟B。完整图册/方案为 `Docs/FRAME_BEAM_MATERIAL_REVIEW.md`／HTML；负责人唯一用户，Codex辅助。本步不保存地图/资产，不改Actor、Master、输入、15Hz、谜题、灯/曝光、玩家POV、音频或包，不自动采纳B或补左支撑。

原生D3D12/SM6 Editor Lit Run2 PID36236真实退出0，5张1920×1080PNG：接缝2.562m/9m/22m同目标方向FOV90（不写FOV），另梁底2.607m、随B端部Y位移的斜端2.982m。逐图前后35 Actor/梁/旧柱冷合同与dirty列表不变，原视口/旋转/GameView实际恢复，199条审计断言非UE游戏用例。highres强制加载/禁ScreenPercentage，不代实际mip/GPU/玩家机位/人工美术。源法线和暗接触不可相互代证；Session仍有Condition failed/TSR警告，不称零错误。

独立读真实原/派生FBX全部角点、梁10面28fan三角/柱98面252fan三角，逐面物理UV Jacobian而非bounds估计；两Geometry（含UV/Normal）原属性字节同、七输入SHA同。2K与等比0.39290377163557627下：梁侧/底轴/横约198.15源texel/m，顶轴140.114/横198.152（约1.414倍），部分斜端轴99.013/横198.152，轴投影U/V不统一；柱木槽轴259.602/横546.787–773.274（2.106–2.979倍）。这些不是正式物理木纹/mip标准。全局平铺不改各向异性；1.310115对齐梁侧与柱轴仅令顶轴183.566，不算完整修复。源最大法线偏差梁0.00006782°/柱0.00003502°，无反向/退化，但不认证UE拆三角/切线/NormalDX/接触阴影。

保持旧有界木族Surface/Opaque/DefaultLit/单面、UV0 QuarterTurn1与NormalDX逆基底、三纹理sRGB/线性合同；旧父无Tiling，本轮没有新Master/MI/开关/Layers/WPO/RVT/MPC或Shader/GPU测量。材料/灯光/镜头技能用于区分UV、源法线、曝光/阴影与诊断POV，不通过补光遮缺口。

收敛的未实施下一候选为“仅梁顶面UV独立校准资产”：保持几何/法线/槽/单位与旧原件，复用旧MI，梁侧198.152仅作局部实验参考、长向候选倍率约1.414214，横向不同时放大；斜端/柱/正式密度不自动修订。必须先验证UV索引/seam、native导入切线和同条件图，不将独立资产比较充当游戏集成验收，后续可玩图/包另有边界。未从诊断推定UV重写或B正式采用许可。

摄影Run1空参数工具缺陷留证：PowerShell `$args`误绑定，UE PID35060仅空窗口，无项目/图/Result；精确匹配证据后正常CloseMainWindow、真实Exit0不计摄影通过。改明确argument变量及启动前非空门控，Run2另存。独立工具首轮ByPolygon假设不适用真实梁AllSame[0]，仅映射支持修正，原产品不动。仅新增两报告、向§35/计划§27追加；旧文档前缀/备份保留，342→344/340旧产品不变、1026包/15源/24隔离源以本Audit FINAL核实，受限登记不读/哈希、无删除/Git写。



## 36. 梁顶 UV 独立校准资产与同条件摄影（2026-10-13）

用户明确接受 §35 的有限方案。唯一人类作者及负责人为用户，Codex辅助实现与验收；当前只交付独立 Dev 梁资产，不把它写入原 B 地图，不改旧入口／包，也不作为正式美术采用。详细图册为 `D:\灯影山海\Docs\FRAME_BEAM_TOP_UV.html`／MD。

- 新资产仅 `/Game/DengYingShanHai/Dev/FrameBeamTopUV/Meshes/SM_DY_FrameBeam_TopUV`。从原派生 FBX 制作独立源文件，顶面是源 Y=max 的 polygon 0。UV minV=.030432701110839844 为既有共享边锚点，只将两个顶面独享 UV 对的 V（double 索引47／51）按 1.4142131281943933 拉开，maxV→.999912420356238；全38个U／48角UV索引及其他9面UV不改。源长向140.114→198.152源2K texel/m，横向198.152保持；仅以梁侧为局部实验参考，非正式物理木纹或运行时mip标准。序列化容器偏移可变化，不误称整个FBX仅两个原始字节改变。
- 16控制点／10源面／28三角、法线／单位／轴／槽／连接／材质保持；独立树扫描256节点，仅UV属性改变，8568离线断言通过。首轮mapping LF内容哈希与实际CRLF文件哈希不一致留证，元数据澄清及独立Run2分别核验；不是产品几何失败。新FBX SHA9D67085097B6EA5D18E098BFD5002D74148943F681182E2C17598EDC7835F999。
- 复用原木族MI／Master及三2K纹理，不改图、UV QuarterTurn1、NormalDX逆基底、Surface/Opaque/DefaultLit/单面或采样Wrap／sRGB/线性合同。probe前两轮32px代理门控失败保留，安装源证实异步默认纹理可返回32px；完成既有资产编译后实读2048，不降级2K门槛、不改图／纹理属性，也不宣称mip升级。
- 原生D3D12/SM6 probe-Run3／create-Run1／另进程verify-Run1全部真实退出0，分别5766／6284／6280审计断言（非游戏测试）。只保存一新uasset；渲染48顶点／28三角／UV0、MeshDescription16顶点／84三角实例／28三角保持；原生推导坐标(sourceX,sourceZ,sourceY)、V翻转，原全精度UV=false及half存储设置保持。仅两个render V和三个三角实例V变化，48法线／切线精确一致，所有非顶UV／导入／Build／section／bounds／材质参数保持。冷读0保存，实例不是源48角，数量不可混淆。
- 实际B图35Actor原合同，只临时切换同组件mesh拍摄再恢复；唯一允许的两处mesh引用变为新资产，其余字段全比较。原／候选同顶目标方向、近3.516513m／中9m／远22m，FOV90只读，Lit／Unlit共12原生1920×1080PNG；native0、63341合同断言、零dirty／地图保存／Actor变换／游戏POV／灯或曝光写入，原mesh和诊断视口恢复。追加两独立进程各6图同样native0／恢复；两variant各三Unlit图与原Run1字节完全一致，115项只读PNG复核通过。
- 初次默认high预览疑似黑背景，后磁盘像素及original-detail全12图复核排除：Near Unlit背景y800..1080新旧差异0，疑似黑图不是实际摄影FAIL，也没有证明UE缓存故障或“复拍修复UE”。保留所有原PNG、原native结果及复拍，不改图。近景顶纹更密、侧／背景稳定；中远景与暗光差异有限，不称全面消除廉价感。Lit EV未冻结、不作像素差纯UV定量因果；highres强制加载／禁ScreenPercentage，不认证游戏机位、实时mip/GPU、normal最终质量或人工采用。

新增可复现原生导入工具 `Scripts\Create-FrameBeamTopUVAsset.py`，只处理本资产／阶段白名单，依赖Saved审计证据且不是游戏运行依赖；未新增类／BP／Tick／Director通信或通用框架。新图／左支撑／斜端／柱／正式密度／全框／NormalDX细化不自动扩项。没有编译／RunTests／PIE／Cook／UAT／新可玩包，本步不能用历史157或旧包首帧充当新资产集成验收。

脚本是冻结批次实施记录，BEFORE包含原文档；发布后直接重跑会因精确旧基线改变而拒绝，且不允许覆盖已存在新asset。这是有意保护，不将它当通用一键重导入器；后续必须另建明确冻结基线，不跳过guard或把历史结果称为新验收。

本轮预期344→348：四新产品（mesh／工具／两报告），只向TECH_SPEC／DEVELOPMENT_PLAN两旧文档追加，旧字节前缀／备份保留；其余342旧产品、1026封存文件／15旧源／24隔离源及Git身份的最终实核见本Audit `FINAL.json`，不提前伪称结果文件已生成。受限许可登记不读／哈希，无付费或新来源下载、无删除／提交／旧包覆盖。现有可玩仍 `D:\灯影山海\Start-FrameBeamCandidate.cmd`，旧梁仍是最小回退；新资产未被任何新保存地图采用。

后续先结合原图评估这个局部候选，再在独立Dev样本验证；当前不改玩法、15Hz、E/A/D/R、主灯、曝光、声音、玩家POV或真实落杖成林。柱接合、端纹／NormalDX、左支撑、剧场空间、5–8分钟盲测、包内三轮、Shipping与正式美术标准仍待验，木构服务“灯为日、影为夸父、玩家弃杖化林”，不表述为历史结构复原。

## 37. 梁顶 UV 候选进入独立可玩 Dev（2026-10-14）

负责人和唯一人类作者为用户，Codex 辅助实施与验证。新精确地图 `/Game/DengYingShanHai/Dev/FrameBeamTopUV/Maps/LV_FrameBeamTopUVLab` 从已保存 B 地图复制，仍 35 Actor；只将既有被动 `DEV_FrameBeam_RightJoint` 的静态网格引用换为 `SM_DY_FrameBeam_TopUV`。位置 `(950,66.77584636395318,816.7876838516025)` cm、Yaw90、等比 `.39290377163557627`、原 MI／Master／三纹理和所有旧场景合同保持。新地图内两个合同 mesh 字段反映同一替换，不是修改两个 Actor。

现有两个 C++ 文件只追加新图精确身份和对应独立测试；旧七图、Game／PIE 上下文、Dev 路径拒绝与 Shipping 边界保持，没有目录／前缀宽泛放行。Director 拥有谜题事实，Stage 驱动 Environment，原 EntryController 继续负责菜单与 OpenLevel 重演；被动梁不读流程、不拥有输入或 POV。E/A/D/R、15 Hz、跨幕取消、脚步和同起点杖落成林沿用。

本批次实际 Editor Development 构建退出0，158项目原生测试成功／0失败／0未执行。probe-Run2 8533与create-Run1 19749审计检查通过，只有一个新图保存；verify-Run1独立冷读实际退出0、13168检查、35Actor、零保存，精确差异只有两个合同mesh字段。首次probe将35Actor误与37合同键要求相等的工具FAIL保留，另两个键为_pawn／_flow，只修审计计数再跑，未改产品判据。数千审计断言不是项目游戏测试。

VisiblePlay-Run1真实D3D12/native0，65流程／35环境、旧柱10／候选梁10五态观察通过，两次实际成林／一次OpenLevel重演；同最终POV五图已按原图查看，仍含Editor界面、不是打包首帧或美术采纳。两cycle UE Master Mix导出及静音流程通过，不代签Windows输出或耳朵。ControlProbe-Run1 native0／41项控制、两次成林／一次重演与EndPlay清理通过；其临时聚焦视线另组，不冒充固定POV或物理键鼠。350阶段产品不变。

独立UAT-Run1实际退出0，Config保持，实际Cook精确三图为显式TopUV＋既有项目Interaction＋引擎Entry，入口不提供地图选择。PackageContainer-Run1三个原生操作实际exit0、2029主chunk＋1global全payload哈希、299312266／3224104B、42核心＋2默认export通过；50封存文件／1070559651B，身份生成时FullGameplay／PackageAudio／Shipping等历史字段保持。新启动器原生PS5解析0与隔离33案例（4正／29拒）通过，发布后阶段352产品；公开CMD经Windows PowerShell 5.1执行默认Package、显式Package及EditorGame三个真实DryRun，均实际退出0。不把fixture或DryRun称为实际包内完整运行。

官方Computer Use已观察本轮实际包的中文菜单，实际click开始并看到场景，PackageFirstFrame-Run1保存Menu.jpg／Started.jpg及逐像素一致封装PNG；用户随后physical Escape中止Computer Use，未再启动窗口。只读复核同一GameRun1（PID26204）的原生日志与退出记录，精确LoadMap为TopUV，UGameEngine::Tick.ViewportClosed触发RequestExitWithStatus(0,0)，随后Exiting，游戏实际Exit0、公开CMD Exit0。原首帧RESULT因缺VISUAL.json记FAIL并原样保留；COMPLETION-REVIEW.json补充两幅图像哈希、日志、实际退出及352产品／构建身份保护。NormalCloseRequestedByCodex=false，不推断关窗者。技术样本的包内菜单／开始画面及原生正常退出已核实，未代包内全流程、包内声音或真人验收；最终发布保护仍以FINAL.json实际结果为准。

本轮固定入口 `D:\灯影山海\Start-FrameBeamTopUV.cmd` 绑定 `Builds\FrameBeamTopUV-20261013-Run1\Windows`，旧 `Start-FrameBeamCandidate.cmd` 与旧包保留。目录／包沿用冻结20261013身份，进展日期记录2026-10-14。局部UV候选不代正式艺术、木纹尺寸／实际mip／GPU、建筑尺度、包内三轮或Shipping；文化因果仍“灯为日、影为夸父、玩家杖落成林”。10月21日前提交的下一步优先解决正式入口与可投影夸父形象，暂停局部UV打磨。最终原产品保护与追加文档前缀以本Audit FINAL.json实核为准。
