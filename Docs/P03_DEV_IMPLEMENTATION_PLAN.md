# P03「杖落成林」Dev 原型接入计划

日期：2026-10-03（接触契约小步跨日核验至 2026-10-04）
状态：**方案方向已确认；底层快照/令牌小步、几何前置小步、接触契约小步（B1）均已实现并通过技术验证。当前项目回归基线 48 Success / 0 Failed，三目标编译成功，原 35 M2 / 20 UI / 18 M3 冷读通过。** 用户已确认 **A 端 ＋ 幕上叙事地线**。**可见 P03 因果演出、落杖动画、树形几何与 Finale 结束态仍未实现；本计划整体不得写成完成。** 地线实际坐标、落杖/生长时长与 P03 参数仍待样本确认，不能把本文件的候选 API 当成现有接口。
2026-10-04 增量：**无时长构图预览已完成，用户已选择下一步 Dev 高位地线**（幕布底部以上 15%，本灰盒幕上世界 Z70）。同一实际玩家 POV 和主灯下生成起始/中途/接触六张原始 PIE 截图，两组原生接触与恢复检查通过。**仅确认 Dev 落点，不同时批准最终弃杖动作、落杖/生长时长或 P03 目标。** 所有临时地线与 Staff 位移仅存在未保存会话，现有 `.umap/.uasset` 与源码未修改；未新编译、Cook 或打包。详见 [`P03_DROP_COMPOSITION_PREVIEW.md`](P03_DROP_COMPOSITION_PREVIEW.md)。上段“地线实际坐标待确认”保留为 B1 历史状态；现阶段 Dev Z70 已确认，正式资产布局仍需接入后复核。

负责人：项目负责人（技术实现与验收）；Codex 负责实现与独立验收；WorkBuddy 仅整理文档。本轮交接审核因额度限制未完成，增量事实暂由 Codex 保留，不能称作 WorkBuddy 提交。
依据：根目录 `AGENTS.md`、`TECH_SPEC.md`、`ARCHITECTURE_DESIGN.md`、
`INTERACTION_PRESENTATION_SPEC.md`、`M2_VALIDATION.md`，以及
`Saved/Audit-2026-10-03-M2Closure/Supervisor-Results.md`、
`Saved/Audit-2026-10-03-P03Foundation/Supervisor-Results.md`、
`Saved/Audit-2026-10-03-P03Geometry/Supervisor-Results.md`、
`Saved/Audit-2026-10-03-P03Contact/Supervisor-Results.md`。

**已完成的分步验收记录：**

- 几何前置小步（40 Success 轮）：[`P03_GEOMETRY_VALIDATION.md`](P03_GEOMETRY_VALIDATION.md)
- 接触契约小步（48 Success 轮）：[`P03_STAFF_CONTACT_VALIDATION.md`](P03_STAFF_CONTACT_VALIDATION.md)
- 无时长构图预览（2026-10-04，真实 PIE 静态帧及 Dev 高位地线确认）：[`P03_DROP_COMPOSITION_PREVIEW.md`](P03_DROP_COMPOSITION_PREVIEW.md)

> **真实 API 提示**：本计划 §5 步骤一的 B1「起始/接触快照与守卫」**已实现**，
> 现有接口是 `GetResolvedStaffPresentationSnapshot` / `GetStaffContactPresentationSnapshot` /
> `TryAcceptStaffContact` / `ReceiveStaffContactAccepted`（+ 原生 `OnStaffContactAccepted`），
> **不是** `BeginForestGrowth` / `FinishFinale` ——后两者**仍不存在**。
> §3 候选架构与 §10 未决取舍不扩大范围；§5 只更新已实现与待实现的分步状态。

> *永远不要以牺牲架构设计为代价追求功能；永远不要基于猜测进行权衡——必须与我确认。*

---

## 0. 前置事实（已由用户签收）

- 用户已明确「中文 UI 正常」；
- 用户已针对完整 M2／P02 的 11 项人工清单答复「**11 项已逐项检查，全部正常**」
  （由 Codex 记录在 `M2_VALIDATION.md` §0.11、§5 与 UI 提案）；
- 本轮同会话两次配置均 **0 个产品哈希变化**，每次 **20 UI PASS + 35 M2 PASS**，
  84 个产品文件一致（`Saved/Audit-2026-10-03-M2Closure/`）。
- **M2Closure 当时的 30 项自动化、三目标编译、两个技术包属于更早的 M2UI 证据，当时未重跑。** 本轮接触契约已新跑 48 项与三目标编译，但未新打包。
- 用户随后明确选择 **「采用真实投影树形灰盒方案」**：实际杖尖的幕上投影落点 → 少量可投影树形灰盒展开 → 同一主灯真实林影；先不接正式美术、声音或新镜头。
- Codex 继续完成首个 C++ 契约小步（§5），最新项目 **34 Success / 0 Failed**（原 30 项全保留、新增 4 项），三目标编译和 20 UI / 35 M2 冷读通过，见 `Saved/Audit-2026-10-03-P03Foundation/`。
- 随后完成**独立几何前置小步**（`Dev/M3` 原生探针），最新项目 **40 Success / 0 succeededWithWarnings / 0 failed / 0 notRun**（原 34 项全保留、新增 6 项 `P03.Geometry.*`），三目标编译 Succeeded，原 **35 M2 / 20 UI** 冷读通过，**标签修正后 18 项 M3 冷读、隔离文件 Windows Cook 与有限桌面画面抽查均完成**。文档交接前 111 项原文件中 109 项一致、仅 `DYPuppetActor.h/.cpp` 改变；文档交接后本计划的批准状态更新成为第三项变化（108 相同/3 改变/0 缺失）。逐项核对见 `P03_GEOMETRY_VALIDATION.md`，证据在 `Saved/Audit-2026-10-03-P03Geometry/`。
- 该小步已实测确认：发光点取实际 SpotLight 位置（**X 恒为 −415、Z 恒为 310，只有 Y 在 −320…+280 变化，轨道沿世界 +Y**，`FVector::RightVector` 即 +Y，**不是 +X**）；接收面取近侧 **X925** 而非立方体中心 X950；杖尖 A/B 三组采样的 `OnScreen` 均为 status=4，但**投影 A 未触地**。
- **历史轮次保留**：34 Success 轮（`P03Foundation`）与 40 Success 轮（`P03Geometry`）的证据与结论均保留在各自审计目录与验收文档中，**不被本轮覆盖或擦去**。当时「A/B 未选择」是那两轮的**历史事实**。
- 用户随后明确确认 **「A 端 ＋ 幕上叙事地线」**；Codex 实现并技术验收**接触契约小步（B1）**：
  Resolve 起始表现快照 + 一次性 Token 守卫接触接口已实现，**默认关闭**（`bEnableStaffContactPresentation=false`，现有 M2/M3 资产均未打开）。
  最新 **48 Success / 0 succeededWithWarnings / 0 failed / 0 notRun**（原 40 项按 `fullTestPath` 全保留、新增 8 项 `P03.Contact.*`），
  三目标编译 Succeeded，**35 M2 / 20 UI / 18 M3** 冷读通过（本轮**未改地图**，M3 仍为 18 项）。
  **文档交接前** 122 项原文件基线 **119 一致 / 3 改变 / 0 缺失**（仅 `DYPuzzleDirector.h`、`DYStagePresentation.h/.cpp`），
  另新增 4 个源码；保护哈希 **98 / 98 完好**。逐项核对见 `P03_STAFF_CONTACT_VALIDATION.md`，证据在 `Saved/Audit-2026-10-03-P03Contact/`。
- **仍未完成/签收**：落杖动画、树形几何与林影、地线 Actor 实例、P03 Definition 与目标/容差、
  Finale 结束态、Skip、整局重启、两种新环境态、最终美术、音效、正式主地图、
  **Cook/Stage/Package**、**GUI 与人工验收**、其他机器兼容与完整竞赛三轮通关。
  本轮自动化整日志仍有本机既有 **13 条**本地化 smoke-test `Condition failed` Error，**不可写成零错误**。
  未测不统一写成“未开始”。

---

## 1. 玩家可见结果（目标，非承诺）

在隔离 `Dev/M3` 原型中复用既有灰盒场地布局，保留 `Dev/M2` 已通过的地图和资产；玩家完成第三段「杖落成林」时**应当**看到：

1. 复用前两段操纵语法，不新增解谜按键；Resolve 前局部复位沿用已有方式，Resolve 后必须遵守整局重启规格，不把 P02 可局部 R 的行为偷偷照搬至 Finale；
2. 灯与偶**同时**满足条件并保持足够时长后，谜题判定成立；
3. 玩家**当前实际摆出的**灯与偶姿态**被保留**，不被替换成预制构图；
4. 手杖落点与幕上投影接触点**一致**，成林从**该接触点**生长；
5. 成功后 `A`/`D` 不再移动对象（表现冻结）；
6. 出现「杖落成林」的**因果连续演出**，而不是成功后淡入一片树林。

**当前状态：可见 P03 因果演出未实现；既有成功锁与新数据快照已可验证。** 现有 P02 成功后仅应用作者配置的
`ResolvedEnvironmentState` 暖色，**没有落杖接触、没有生长、没有结束态**。

---

## 2. 实际缺口与源码路径（只读核实，不猜类名）

| 缺口 | 实际情况 | 源码路径 |
|---|---|---|
| 三幕队列 | **不存在**。Director 只有**一份** `PuzzleDefinition`，无序列、无索引、无「第几幕」 | `DYPuzzleDirector.h:113` |
| Token 机制 | 首步已有 Director 激活 FGuid、成功 Token 核验及失效；完整演出回调消费/Finale 状态机仍未接入 | `DYPuzzleDirector.h/.cpp` |
| 完整体验状态 | Director **已有当前谜题事实权威**，不是“无事实源”；完整三幕/Finale 状态机尚无。原成功事件第二参数仍为判定结果，签名未改 | `DYPuzzleDirector.h` |
| 判定快照的灯偶变换 | 原 `FDYEvaluationResult` 不含变换；**新增** `FDYResolvedPuzzleSnapshot` 包含判定结果及真实控制快照，原成功事件内可只读获取 | `DYResolvedPuzzleSnapshot.h`、`DYPuzzleDirector.cpp` |
| 控制快照 | **已存在**：`GetControlSnapshot()` 返回 `FDYControlSnapshot{ bIsValid, PrimaryNormalized, PoseId, WorldTransform }` | `DYControllable.h:39`、`DYControlTypes.h:54-73` |
| 恢复快照 API | **不存在**。`RestoreControlSnapshot` **只见于设计稿 `ARCHITECTURE_DESIGN.md:137`，源码无任何实现** | 全工程 grep 为 0 |
| 皮影类名 | 实际是 **`ADYPuppetActor`**，**不是**设计稿的 `ADYShadowPuppetActor` | `DYPuppetActor.h:17` |
| 手杖组件 | `Staff` 为**私有** `UStaticMeshComponent`，用 `CylinderMesh` 基本形状，相对位置 `(0,-45,25)`、缩放 `(0.06,0.06,1.55)`，随预设 Pose 改变 | `DYPuppetActor.h:55-57`、`.cpp:32-38,56` |
| 杖尖 Socket | **仍不存在**。全工程 `Socket` 命中仅为相机 SpringArm。几何小步改为**只读值快照** `GetStaffGeometrySnapshot()`：取 `Staff` 真实静态网格局部边界 + 组件世界变换，输出局部 **−Z/+Z** 两端 A/B，**不指定最终杖尖** | `DYStaffGeometryTypes.h`、`DYPuppetActor.cpp:78-97`；详见 `P03_GEOMETRY_VALIDATION.md` §2.1 |
| Environment 状态 | 枚举**只有 3 态**：`Dormant`／`SunAwakened`／`ChaseAwakened`。**`FinaleReady`／`ForestComplete` 尚未实现** | `DYStageEnvironment.h:11-16` |
| 接触底层／落杖动画与生长 | **底层接触接口已实现**：实际 A 端、地线值快照与一次性 Token 守卫；无已保存地线关卡实例、落杖动画、Forest Actor 或 `BeginGrowth`。旧几何采样未触地与新接口夹具验证是两种不同证据 | `DYStagePresentation.h:48`；`P03_STAFF_CONTACT_VALIDATION.md` |
| P03 收尾 | `ReceivePuzzleResolved` 与新增 `ReceiveStaffContactAccepted` 是 **Blueprint hook**；没有 Finale 结束态或完成回调消费 | `DYStagePresentation.h:102`、`DYStaffPresentationTypes.h` |

**结论**：设计稿与源码存在**已知偏差**（类名、缺失的恢复 API、缺失的环境态）。
本计划以**源码实际**为准，不以设计稿命名为准。

---

## 3. 类布局与唯一负责人

沿用**已接受**的基础架构（`ARCHITECTURE_DESIGN.md` §0、§2），不引入新层：

```text
ADYPuzzleDirector ──成功 Token + 只读快照──▶ ADYStagePresentation
   │  唯一体验事实                          │  表现快照 + 演出编排
   │  不读像素/幕布接触                     │  显式引用 Puppet / Forest / Environment
   ▼                                         ▼
UDYPuzzleEvaluatorComponent（不读视觉）  ADYForestGrowthActor（拟新增，只表现）
UDYPuzzleDefinition × 3（拟新增 P03）
```

- **新增 Subsystem：禁止**
- **世界扫描找 Actor：禁止**
- **新增按键：禁止**
- **第二张正式主地图：禁止**；独立 Dev/M3 是技术测试地图，不是第二正式场景。保留 P02，不向原 Dev/M2 写入第三幕资产。
- 唯一负责人：**项目负责人**；美术资产按既有分工，不在本计划内分配

---

## 4. 通信规则（不可违反）

1. **Director 发行 Token，并且是唯一体验事实来源。** 首步采用不透明 `FGuid` 激活身份，成功快照另带 `PuzzleId`；不依赖会归零的序号。B1 已在 Presentation 中实现**同一 Token 的接触消费一次**；完整 Finale 完成回调的消费协议仍未实现，不能把接触守卫当作体验结束权威。
2. **Evaluator 不读视觉。** 判定只依据参数区间与 Holding。
3. **Director 绝不读取幕布接触点、像素或投影来判断成功。**
   它可以在 Resolve 时**收集灯与偶的真实 `WorldTransform` 作为留证**，
   但缺失或不完美**不得撤销已经成立的判定成功**。
4. **手杖当前变换、杖尖候选点与幕上投影落点属于「表现快照」，由 Presentation 获取。**
   资产缺失时表现降级，**判定成功仍然成立**。
5. **Presentation 回调必须核验 Token**：过期 Token 一律丢弃，不推进流程。
6. **Forest 只做表现**，不回写谜题状态、不参与成功判定。
7. 新会话或整体重启**必须废弃全部旧 Token**。

---

## 5. 有序实施步骤

### 步骤一 A（已实现）：C++ 成功控制快照与 Token 身份契约

只改两个 Director 文件，新增 `Public/Puzzles/DYResolvedPuzzleSnapshot.h` 与 `Private/Tests/DYResolvedSnapshotAutomationTests.cpp`；逐文件备份及白名单见 `Saved/Audit-2026-10-03-P03Foundation/Execution-Contract.md`。

- `FDYResolvedPuzzleSnapshot`：只读值结构，含 `bIsResolved / PuzzleId / Token / Evaluation / Light / Puppet`，没有手杖组件或投影落点。
- `ADYPuzzleDirector::GetResolvedPuzzleSnapshot()`：返回独立副本，不重放事件、不移动 Actor；未成功/复位/EndPlay 后返回空快照。
- `ADYPuzzleDirector::IsResolvedTokenCurrent(const FGuid&)`：只读核验本 Director 当前成功身份；无效、旧激活或另一实例的 Token 被拒绝。不是 `FinishFinale`，不决定成功、不触发生长。
- 原 `OnPuzzleResolved` 签名保留，快照在原事件前已捕获；没有新增第二个成功广播。StopEvaluation 移到原成功通知前，避免监听者重启的新计时器被旧完成尾部清掉；激活/评估的同步回调若重启，则旧分支停止处理。
- 原 P01/P02 输入、15 Hz、参数、地图和局部 R 行为不变。P03 终章锁/统一重启**尚未接入**，不将本步宣称为已实现该规则。

实测：34 项全成功（原 30 保留 + 4 新增）；Editor/Game Development/Game Shipping 三目标 Succeeded；20 UI / 35 M2 冷读成功。**未新 Cook/打包、未新增 P03 画面**，旧 UI 独立包不包含本轮代码。

### 步骤一 B：**B1 已实现（起始/接触快照与守卫）／B2 仍待实现（结束态）**

**本步不含音效、不换相机、不采购或下载任何美术资产。**

#### B1 —— 已实现并通过技术验证（48 Success 轮）

以下接口**现已存在于源码**，不再是「拟新增」：

| 已存在 API | 位置 | 用途与已核实语义 |
|---|---|---|
| `FDYStageResolvedPresentationSnapshot` | `DYStaffPresentationTypes.h` | Resolve 起始快照：`Token` / `PuzzleId` / 灯与偶控制快照 / 投影捕获 / 叙事地线。**只在 live Resolve 事件捕获**，同 Token 不重复捕获 |
| `FDYNarrativeGroundLineSnapshot` | `DYStaffPresentationTypes.h` | 幕上叙事地线：`WorldAnchor` + `ScreenLocalZ`；是**作者在接收面上的线，不是后台实体地面** |
| `FDYStaffContactPresentationSnapshot` | `DYStaffPresentationTypes.h` | 一次性接触快照：`Token` / `PuzzleId` / 投影 / `ContactWorldPosition` |
| `GetResolvedStaffPresentationSnapshot()` | `ADYStagePresentation` | 只读返回**值副本**；开关关闭 / 无 live Resolve / Token 失效时返回空结构 |
| `GetStaffContactPresentationSnapshot()` | `ADYStagePresentation` | 只读返回接触值副本；仅在接触已成立且 Token 仍当前时返回 |
| `TryAcceptStaffContact(Token)` | `ADYStagePresentation` | **自行读取真实当前 A 端**（不接受调用者自报坐标）；校验 Token 一次性、发光点/接收面/地线未换构图、A 投影落在固定地线；**纯表现，不解决/不结束谜题** |
| `ReceiveStaffContactAccepted(Contact)` | `ADYStagePresentation` | `BlueprintImplementableEvent` 表现 hook；另有原生观察信号 `OnStaffContactAccepted()` |
| `UDYStaffContactLibrary::CaptureNarrativeGroundLine / IsStaffAOnNarrativeGround` | `DYStaffContactLibrary` | 纯数据几何，不读 World/像素/判定器；地线锚点必须在朝发光点的接收面且在局部 Y/Z 边界内 |
| `bEnableStaffContactPresentation` | `ADYStagePresentation` | **默认 `false`**；现有 M2/M3 资产均未打开 |
| `GetLightRigActor()` / `GetPuppetActor()` | `ADYPuzzleDirector` | 本轮**只增**的只读访问器，读取实际作者引用；`Director.cpp` 未改 |

**已核实语义**：接触是「幕上中心射线预测点与叙事地线的几何一致」，**不是**实体碰撞、
**不是**阴影像素识别、**不是**真实阴影可见性证明；`OnScreen` **不构成接触**（有专测 `OnScreenIsNotContact` 锁定）。
接触是**纯表现事实**，成功只由 Evaluator/Director 决定，**接触失败或缺失不撤销成功**。
`SynchronizeFromDirector()` **不重建**新起始快照，late sync 只恢复表现、不重放接触。
这里不宣称旧 M2 `ReceivePuzzleResolved` hook 已全面去重：既有同步路径仍会调用它，
后续 P03 图表必须检查新快照/接触事实，不能以旧 hook 的再次执行代替新接触。
`ContactWorldPosition` 是**幕上投影点**；后台实体杖尖是 `Projection.Staff.EndAWorld`。
后续树形几何应在灯与幕之间，从实体点建立根部，让同灯真实投影在幕上同点展开，不直接把幕上坐标当作实体生成点。
数值只用 `UE_DOUBLE_SMALL_NUMBER` epsilon，**不是**新增谜题容差。
逐项证据见 [`P03_STAFF_CONTACT_VALIDATION.md`](P03_STAFF_CONTACT_VALIDATION.md)。

#### B2 —— 仍待实现（以下**均为「拟新增」，不是现有接口**）

| 拟新增 | 位置 | 用途 |
|---|---|---|
| `FinishFinale(Token)` | `ADYPuzzleDirector` | 校验并消费当前终章回调，仅一次进入最终体验状态；名字/签名仍属候选，**源码中不存在** |
| `BeginForestGrowth(Token, ContactTransform)` | `ADYStagePresentation` | 消费接触同步点、核验身份并驱动 Forest；**源码中不存在**，名字亦非最终定名——本轮实际实现的是 `TryAcceptStaffContact`，它**不驱动任何 Forest** |
| `RestartExperience()` | `ADYPuzzleDirector`／`ADYStageGameMode` | 整体重启，废弃旧 Token；**未批准、未实现** |
| 落杖动画 / 树形几何 / 林影 | Dev/M3 灰盒资产 | **未制作**；`ADYForestGrowthActor` 仍不存在 |
| `FinaleReady` / `ForestComplete` 环境态 | `DYStageEnvironment` | 枚举仍只有 3 态，两态**未实现** |

> **接触被接受后当前不会触发任何可见演出**——Blueprint hook 存在但未接入表现资产。
> 杖尖读取已在几何小步以 `GetStaffGeometrySnapshot()`（局部 −Z/+Z 两端 A/B）实现，
> **不是**本表曾假设的 `GetStaffTipWorldTransform()`；用户已确认取 **A 端**。

**关键约束**：Resolve 之后**局部 `R` 不得偷偷复位**已成立的演出；
整体重启走统一的 `RestartExperience()` 路径（本轮**未实现**）。

### 步骤二：独立 Dev/M3 灰盒资产（保留 P02 通过基线）

- 新增 `Content/DengYingShanHai/Dev/M3/`，**不修改** `Dev/M2` 的既有资产；
- 放置：接触锚点 Actor、Forest 表现 Actor、题签；
- **落杖动画与生长优先用 Blueprint / Sequencer**，**不在 Evaluator 或 Director 内写动画**；
- **最小降级路径**：若 Sequencer 不可用，必须**从实际接触落点生长真实几何剪影**，
  不得用屏幕空间贴图或全屏渐变假装成林；**主灯实时投影必须保持**。

### 步骤三：P03-only 验证通过后，才接三幕连续顺序

前两步未通过验收前，**不新增 `UDYPuzzleDefinition` 序列、不改 M2 地图、不动 `Config`**。

---

## 6. 状态与生命周期

- 完整体验状态沿用已接受方案 `PuzzleActive / PuzzleConfirming / PuzzleResolved / FinaleLocked / ExperienceComplete`，不另发明平行体验状态机；Evaluator 的 `Searching / Holding / Resolved` 仍是判定状态，两者不是同一个层级；后两种体验状态目前未实现；
- 状态由 Director 持有，Presentation **只读并消费**；
- **不联网、不复制、不存档**：Director 持有的是当前世界的体验事实，Presentation 持有表现运行态；不是把全部事实称为纯表现信息。
  不入 Data Asset／CDO，不做联机同步，不写存档；
- **最终集成目标**：冷启动 late-sync 只恢复表现快照，不重放成功事件、碰撞声或演出。本轮新 Staff 路径不重建起始快照、不重放接触；旧 M2 `ReceivePuzzleResolved` 同步 hook 保持原语义，全面演出去重须在后续 P03 接入时落实；
- 过期 Token、重复回调、卸载中的 Actor 一律安全丢弃。

---

## 7. 资产目录与软硬依赖

**表现资源可降级，授权/几何正确性不可省略**：缺失音效/VFX 不撤销成功，也不阻塞逻辑结束；但杖尖、幕布平面与接触落点是可见因果原型的必要作者配置，交付前必须验证有效，不能“没有森林只显示成功”仍称 P03 演出通过。

这里的可降级不是指已经实现 `TSoftObjectPtr`；World Actor 一对一关系采用显式引用。不编造当前资产的软引用加载行为。

**硬依赖（必须有，否则本步不做）**：Director Token 与冻结；
Presentation 显式引用；Forest 只做表现。

新增依赖模块：**无**。不引入插件、不采购或下载美术资产。

---

## 8. 文件白名单候选与逐文件备份回退

> 以下为**候选**，实施前须逐文件确认并单独备份。

| 动作 | 文件 |
|---|---|
| 修改 | `Public/Puzzles/DYPuzzleTypes.h`、`Public/Puzzles/DYPuzzleDirector.h`、`Private/Puzzles/DYPuzzleDirector.cpp` |
| 修改（后续候选） | `Public/Interaction/DYPuppetActor.h`、`Private/Interaction/DYPuppetActor.cpp`（只读杖尖/Staff 表现锚点；不改 P02 操纵逻辑） |
| 修改（后续候选） | `Public/Stage/DYStageEnvironment.h`、`Private/Stage/DYStageEnvironment.cpp`（追加两个新态并实现表现；不重排现有序号） |
| 修改 | `Public/Stage/DYStagePresentation.h`、`Private/Stage/DYStagePresentation.cpp`（显式引用 + Token 核验） |
| 新增 | `Public/Stage/DYForestGrowthActor.h`、`Private/Stage/DYForestGrowthActor.cpp`（只表现） |
| 新增 | `Content/DengYingShanHai/Dev/M3/…`（灰盒资产） |
| 修改 | `Source/.../DengYingShanHai.Build.cs`（**仅在真实需要时**） |
| 测试 | `Private/Tests/` 新增 P03 用例；**不删除**既有测试 |

**回退**：实施前把每个待改文件完整复制到本轮 `Saved` 备份目录并记录 SHA-256；
回退时**只按明确单文件恢复**，**不 reset 全仓、不 git checkout 未提交改动、不清理脏工作树**。

---

## 9. 验收

| 项 | 通过标准 |
|---|---|
| 重复成功 | 同一 Token 重复回调不产生二次成功、不重播演出 |
| 过期 Token | 旧会话／重启后的 Token 全部被丢弃 |
| Resolve 冻结 | 成功后 `A`／`D` 不再移动灯与偶 |
| 非接触不生长 | **正常播放**没有幕上杖尖接触同步点就不得启动生长；Skip/中断走统一最终状态，是明确的收尾例外，不伪造接触声或重播成功 |
| 接触仅一次 | 同一接触点只触发一次生长 |
| `R` 与整体重启 | 局部 `R` 不偷偷复位已成立演出；整体重启走统一路径且废弃旧 Token |
| Skip／中断一致终态 | 跳过与中断都收敛到同一结束态，不重播成功 |
| 失焦 | 窗口失焦再返回不残留输入上下文、不卡死 |
| 既有回归 | **20 UI PASS + 35 M2 PASS** 保持；P02 通过基线不被破坏 |
| 自动化 | 当前 **48 项** Automation 全部保持 Success，后续演出/收尾再增加测试；原 40 项完整保留（包含更早的 30/34 基线） |
| 冷读 | 新增资产只读检查 **0 error / 0 warning** |
| Windows 打包 | 显式 Cook P03 测试地图后，独立包进程验证中文 UI 存在、开发参数仍不存在 |

---

## 10. 风险与需要用户确认的取舍

### 必须由用户确认（我不自行决定）

| # | 待确认 |
|---|---|
| **Q1** | **P03 目标值与容差**：目前**没有任何已确认数值**。需真实几何与可玩性验证后确定，**不编造默认值** |
| **Q2** | **落杖时长**：**未确定**。需按实际动画节奏确认 |
| **Q3** | **生长时长／超时阈值**：**未确定**。需按实机观感确认 |
| **Q4** | **跳过/整体重启测试入口**：既有操纵键鼠已经确认，不重复询问；任何新 Skip 入口或将 R 改为重启都须另列影响，不能悄悄改映射 |
| **Q5** | **测试重启路径**：走 `RestartExperience()` 还是关卡重载，**尚未批准** |
| **执行顺序** | 独立 Dev/M3 的 P03-only 验证先于三幕整合，是保护已签收基线的技术安排，不要求用户重复批准既有三幕架构；不先扩建标题/新镜头/声音 |

### 已知风险

- **设计与源码偏差**：设计稿的 `ADYShadowPuppetActor` 与 `RestoreControlSnapshot` **源码不存在**，
  若照设计稿实现会引入不存在的引用；
- **资产缺失不得撤销成功**：表现降级路径必须先定，否则容易出现「看起来失败」的歧义；
- **首步即上演出风险高**：建议严格按步骤一 → 二 → 三，不合并；
- `Staff` 私有且无杖尖 Socket，接触点方案直接影响步骤一实现方式；
- Environment 缺 `FinaleReady`／`ForestComplete`，若步骤一强行使用会与现有 3 态枚举冲突。

> **几何小步已部分消解 Staff 访问风险**：`Staff` 仍私有、无 Socket，但已提供只读值快照
> （局部 −Z/+Z 两端 A/B），**接触点方案不再被「取不到杖尖」阻塞**。
> **该风险现已进一步消解**：用户已确认取 **A 端**。
>
> **接触契约小步已消解「落杖接触点从哪来」**：现有 `TryAcceptStaffContact(Token)`
> 读取真实当前 A 端并与作者配置的幕上地线比对，由一次性 Token 守卫。
> **但地线 Actor 尚未制作、落杖动画与树形几何尚未实现**——
> 见 `P03_STAFF_CONTACT_VALIDATION.md` §5 U1/U2/U3。
> Environment 缺两态的风险**未消解**，仍适用于 B2。

---

## 11. 状态

**部分完成（本计划整体未完成）**。已完成的分步，逐轮证据均保留、不被后续轮次覆盖：

| 分步 | 回归基线 | 验收文档 |
|---|---|---|
| 首个 C++ 契约小步（步骤一 A） | 34 Success | `Saved/Audit-2026-10-03-P03Foundation/` |
| 几何前置小步 | 40 Success ／ 18 项 M3 冷读 ／ 独立 Cook | [`P03_GEOMETRY_VALIDATION.md`](P03_GEOMETRY_VALIDATION.md) |
| **接触契约小步（步骤一 B1）** | **48 Success** | [`P03_STAFF_CONTACT_VALIDATION.md`](P03_STAFF_CONTACT_VALIDATION.md) |
| **无时长构图预览（2026-10-04）** | 两组真实 PIE，0%/50% 非接触、100% 一次接触及完整变换恢复；未重跑旧 48 项 | [`P03_DROP_COMPOSITION_PREVIEW.md`](P03_DROP_COMPOSITION_PREVIEW.md) |

- 用户已确认真实投影树形灰盒方向，**并已确认 A 端 ＋ 幕上叙事地线**。
- WorkBuddy 初稿中把 Director 本身也称为“无唯一体验事实”、混写 `UDYPuzzleDirector`/`ADYPuzzleEvaluator`、令牌仅序号、`Dev/M2` 与 `Dev/M3` 范围矛盾等描述，由 Codex 按实际源码与最新用户选择更正；初稿保留在对应 Backup。
- 几何小步：新增只读杖尖值快照与中心射线投影库、`Dev/M3` 原生探针。
- 接触小步：Resolve 起始快照 + 一次性 Token 守卫接触接口，**默认关闭**，地图与既有资产未改。

**仍未实现**：落杖动画、树形几何与林影、地线 Actor 实例、P03 Definition 与目标/容差、
`FinishFinale` 与 Finale 结束态、`RestartExperience()`、Skip、两种新环境态、
Cook/Stage/Package、GUI 与人工验收。**本计划不得写成完成。**

§10 未决数字不会阻塞无需演出时间的底层契约；也不会因该契约完成而自动获得批准。
下一步在独立 `Dev/M3` 制作**可展示的落杖构图样本**，核对实际 A 端从成功构图移动到幕上地线，
再接同一点的真实树形投影；地线位置与节奏值用**样本**请用户确认，不要求用户盲填工程数字。
**当前 `OnScreen` 只是中心射线几何预测，不是可见性、触地或通关；
本轮「接触」也只是几何一致，不是实体碰撞或阴影识别。**

### 2026-10-04 后续事实与下一步

- **上述“待制作落杖构图样本”现已完成其无时长静态预览部分**：脚本从继承 P02 沙盒的真实 Resolve 起点，仅平移实际 Staff，保留灯/偶根、幕布、真实投影和原有玩家 POV。它不是正式连续动画或 P03 通关。
- 第一组 5% 低地线虽被原生几何接受，但幕上世界 Z=-10 被后台地板遮挡，视觉不通过；后续改比较 15%（Z70）与 10%（Z30），保留全部失败/比较证据，没有改主灯、镜头或 M2。
- 用户已回复 **“高位地线（推荐）”**；下一步 Dev 样本采用 15% / Z70，**不再把该 Dev 选择列为未决**。最终弃杖动作、时长、P03 参数与正式资产尺度仍未确认。
- **下一步**：从该构图的真实实体 A 端继续制作同点树形几何投影样本，保留同一主灯；归一化展开可以先比较构图，不偷偷绑定正式生长时长。幕上接触点不是后台生成位置，不能混用。
- **当前暂缓的执行**：权限审核服务因额度限制未能完成 WorkBuddy 文档交接审核，粘贴未执行。为保留事实，本轮增量由 Codex 记录；WorkBuddy 并未提交本轮文档。不绕过审核继续启动 UE 或操作桌面，源码/森林实现与验收待审核服务恢复后推进。

### 2026-10-04 同根真实投影样本增量（最新；以上全文保留为历史）

- **技术取证通过、构图待优化，正式 P03 演出仍未完成。** 用户已确认 A 端与高位幕上地线15% / 本灰盒Z70，不再要求选择地线。
- 从既有P02夹具真实Resolve继续：实际Staff平移到原生接触点后，10个Engine Cylinder枝段从实体A形成单根连通图，由同一Movable主灯真实投影。没有材质林影或成功后换构图；仍只是无时长静态样本。
- Run2与最终Run4分别完成6张1600×900实际PIE原图、24次枝段实体验证（48个端点检查）、1次接受接触、重复拒绝、完整Staff变换恢复及旧Token拒绝。原0.72 / 0.80 / Hold1.25s / 15Hz为P02夹具，不是P03参数。
- 幕上点 `(925,-11.156213,70)` 不能充当幕后根；实际实体根 `(600,18.713764,128.208955)` 来源为Contact.Projection.Staff.EndAWorld。实际灯/偶根、幕、Staff旋转缩放、POV和FOV保持；正式节奏/容差未批准。
- 最终Run4读取枝段实际材质为 `/Engine/EngineMaterials/DefaultMaterial.DefaultMaterial`，不是此前预检猜测的BasicShapeMaterial；未换材质。树投影关闭对照只改CastShadow，不重写几何变换。Run1 GUID比较与Run3材质名称假设失败均安全退出，证据保留。
- 全日志仍有13条既有Condition failed Error与1条TSR Warning；本轮没有新增C++ Automation、编译/Cook/Package或性能验收，旧48 Success仍是历史证据。
- 视觉不足：中央主干/上枝与夸父重叠，裸枝稀疏，实体和影子双线及影边锯齿。**先做“同根早分叉、两侧展开、中央留空”的对照样本仅为建议，待用户确认，未实施。** 不为此擅自移动灯/偶/幕/镜头或隐藏实体。
- 上文“额度审核阻塞”是前轮历史，当前独立UE正常启动；本轮WorkBuddy交接初次因数据披露审核被拒，用户明确授权该负载后正常通过并实际交付，没有绕过审核。
- WorkBuddy整理3份文档，Codex复核并纠正跨轮Token误读、实际材质、字段出处和历史段落覆盖。WorkBuddy原稿在本轮审计WorkBuddy-Output保留；旧历史完整前缀由逐文件备份恢复，本轮最新状态只追加。
- 详见 [`P03_FOREST_PROJECTION_PREVIEW.md`](P03_FOREST_PROJECTION_PREVIEW.md) 与 `Saved/Audit-2026-10-04-P03ForestPreview/Verification-Run4.json`。
- 仍未实现：保存的地线/Forest表现资产、连续落杖生长、P03 Definition及参数、Finale、三幕队列、Skip/整体重启、两新环境态、正式美术声音、玩家人工通关、新Windows包。旧Start-M3Geometry入口不包含本样本。

### 2026-10-04 中央留空同根构图对照增量（最新；以上全文保留为历史）

- 用户回复**「按照你的想法来」**，批准上一轮建议的**同根更早分叉、两侧展开、中央留空**未保存 Dev 对照。**仅确认这一步未保存的 Dev 构图**；**未批准**正式连续动画、正式美术、P03 参数与容差、任何秒数、Skip 或整体重启。**本计划整体仍未完成。**
- Run2 实测：6 张 1600×900 无 HUD 真实 PIE 原图；**23 次枝实体验证（5+9+9）、46 个实际中心线端点、184 个实际 Cylinder bounds 投影角检查**——**不是 23 个 Automation 测试**；1 次真实原生接触、1 次完整 Staff 变换恢复与旧 Token 拒绝；`Completed(error = null)`、Editor 正常退出。
- **本 Run2 Token `5DB65B1C49D07D57CF6E9B96E93C6CC8` 只对本 Run2 的接触/Resolve 有效**，contact 与 resolve 同值、`native_token_current = true`；**不与旧 Run4 或本 Run1 混写**。
- 拓扑为 **9 边单根连通**（短根→低位左右→两侧上行→四个枝尖），`no_central_upright = true`；半展开 5 段、全展开 9 段、投影关闭对照 9 段。实体 A 物理根 `(600, 18.713764, 128.208955)` 与幕上根 `(925, -11.156213, 70)` **不等同、不可互换**，树根取 `EndAWorld`。
- 角色保护框取**真实 Torso/Head 各 8 角**共 16 角投影，诊断 padding 仅局部 Y/Z 各 2.0，`gameplay_tolerance_changed = false`。**体积理想射线包络留空不等于 VSM 像素/半影/POV 遮挡已全部解决。** `sample_width_fraction = .48` 是构图坐标基准，**不是实测树宽 48%**。
- 视觉：中央重叠**减少**、角色轮廓更清楚、低位同根连接可追溯；但**U 形框/支架感、裸枝稀疏、实体影子双线、锯齿仍在**，后台灰盒与反光地板仍非正式美术。**技术与对照通过，画面局部改善；不是最终成林构图，不是用户视觉验收，不是 P03 可玩完成。**
- Run1 在**进入 PIE 前**被输出路径守卫拒绝（`RuntimeError: Evidence output must stay within this composition audit`）；**未放宽守卫**，只修正 Saved 启动脚本输出路径，失败日志保留。
- 灯/幕/偶根/Staff 旋转缩放/POV/FOV/曝光/材质均不改；P02 夹具 `0.72/0.80`、Hold `1.25s`、`15 Hz` **仍是夹具**（`invented_p03_parameters = false`）。**本轮未编译、未 Cook/Stage/Package、无新 C++ Automation**；历史 48 Success 仅为历史基线。日志仍有 **13 条**既有 Error 与 **1 条** TSR Warning——**不等于整日志零 Error**；**无性能与打包结论**。
- 资产沿用**已登记**的 Engine Cylinder 与实际 DefaultMaterial，**未下载新资产、未付费**，无新的许可条目必要。
- 详见 [`P03_FOREST_COMPOSITION_COMPARISON.md`](P03_FOREST_COMPOSITION_COMPARISON.md)；证据在 `Saved/Audit-2026-10-04-P03ForestComposition/`。最终全文件保护哈希由 Codex 在本文档交付后复核，**本节不预写最终文件数量**。

### 2026-10-04 低位转折与分段外展枝形对照增量（最新；以上全文保留为历史）

- 用户回复**「继续按照你的想法来进行」**，批准上一轮建议：在 Dev 无时长样本中用**分段渐缩、转折与侧枝轮廓**减轻 U 形框。**仅批准这一步未保存的 Dev 对照**；**未自动批准**正式美术、演出秒数、P03 目标/容差、Skip、整局重启、相机/输入或三幕整合。**本计划整体仍未完成。**
- 本轮 **Run1 成功**，6 张 1600×900 无 HUD 真实 PIE 原图，无编辑合成。**本轮没有失败的 UE Run，不混入上一轮 Run1 的路径失败。**
- 拓扑为 **15 边 16 节点单根连通**（`branch_count=15`、`node_count=16`、`single_root=true`、`parent_before_child=true`、`thickness_nonincreasing=true`）：实际 A → 极短 fork；左右 near → exit 低位逃逸；exit → lower → upper → tip 弯折上行；lower/upper 侧枝错位展开（`asymmetry_is_diagnostic=true`）。
- **41 枝实例检查（11+15+15）／82 个实际中心端点／328 个实际 Cylinder bounds 投影角**——**不是 41 项 Automation 测试**；`new_automation_suite=false`。
- 分段直径因子 `1/.80/.72/.68/.58/.46`、侧枝 `.42`，**原末梢 `.42` 保守保持**；**分段减细不是平滑连续 taper，也不是真实生物桃树**（`stepped_diameters_not_smooth_taper=true`、`biological_model_claim=false`）。
- **低位连接仍必需**（`low_connection_retained=true`），**保护框不放宽**；真实 Torso/Head 每次 identity 锁网格/bounds/组件变换（16 角）；枝干每次布置核验端点与 8 角；持续身份守卫 Actor 变换/hidden/`CastShadow`；`gameplay_tolerance_changed=false`。
- **本 Run1 Token `E897B2094D231613DF7D85BB3FDCD62D` 只同本轮 Resolve/Contact 相等，不跨旧 Run2/Run4。** `ContactAccepted` **是 Python 审计标签**，反映原生 `TryAcceptStaffContact` 接受与真实 Contact 快照，**不是原生事件名称**。
- 实体 A 根 `(600, 18.713764, 128.208955)` 与幕上根 `(925, -11.156213, 70)` **不等同、不可互换**；树根取 `EndAWorld`；根射线倍率 `1.3201970443349753`。
- 三个字段口径：中心节点局部包络 `[-29.9332743728, 30.6333910876, -35, 16.119]` 是**节点范围**，**不是实际树体积或阴影像素宽度**；`.48/.62` 是**坐标基准，不是实测总宽**；`low_clearance=0.6347455647` 是**预扣半径的低位预算，不是全树最小实际净距**。
- 05/06 对照**只改树 `CastShadow`**，**实体不隐藏**、15 枝变换与端点**完全保持**，关投影**仅供诊断**。**原生射线投影与实际 8 角留空 ≠ VSM 像素/半影/POV 无遮挡。**
- 视觉：**U 形近垂直双柱与直角托架感减轻**，改为外展 V 形/浅弧 + 错位侧枝，**中央留空保持**；但**必要的短横根仍存在且可见**（不能声称 U 框完全消除）、**裸枝稀疏**、**双线增加**、**锯齿明显**，分段折线与直径台阶仍是灰盒。**技术与对照有效，轮廓局部改善；不是参赛高质量林相，不是正式连续演出，不是用户视觉验收，不是 P03 可玩完成。**
- **无 Source / 资产 / Config / `.uproject` / 旧启动器变化**；旧 Composition 脚本**仅默认保持 hook**，旧 9 段入口**未重跑实机**（只做 AST/导入/拓扑/语法比较）。主灯/幕/偶根/Staff 旋转缩放/POV/FOV/曝光均不改；P02 夹具 `0.72/0.80`、Hold `1.25s`、`15 Hz` **不等于 P03 参数**，`no_new_time_parameters=true`。
- 日志仍有 **13 条**既有 Error 与 **1 条** TSR Warning——**诊断成功 ≠ 全日志 0 Error**；**无新 C++ Automation、无编译 / Cook / Package、无性能结论**，历史 48 Success **不是本轮重跑**。资产只用已登记 Engine Cylinder 与实际 `DefaultMaterial`，**未下载、未付费**，**不改 `LICENSES.md`**。
- 本轮由 Codex **启动一次**完整 Editor 进入 PIE 取证，**不混写上一轮两次启动**。旧 `Start-M3Geometry.cmd` **不包含本样本**，新 Python 是自动取证入口，**不是双击即可手动可玩的第三幕**。
- 详见 [`P03_BRANCH_REFINEMENT_PREVIEW.md`](P03_BRANCH_REFINEMENT_PREVIEW.md)；证据在 `Saved/Audit-2026-10-04-P03BranchRefinement/`。最终全文件哈希由 Codex 在本文档交付后复核，**本节不预写最终文件数量**。

### 2026-10-04 独立 Dev 连续预览增量（最新；以上全文保留为历史）

- 用户明确确认制作**独立 Dev 连续预览入口**：从真实 Resolve 起点连续落杖，**A 端接触已确认 Z70 地线后**才展开既有真实投影枝形。**速度仅用于比较，正式演出时长未确认。** 本段之前的「尚无连续动画」是**当时的历史事实**；现已实现 **Editor-only 连续样本**，但**不是正式 P03**。**本计划整体仍未完成。**
- 新增 3 个入口：`Scripts/Preview-P03Continuous.py`、`Scripts/Start-M3Continuous.ps1`、根 `Start-M3Continuous.cmd`；旧四脚本**只导入派生、不编辑**。**无新 Actor 类、无 Subsystem、无 Tick 世界扫描、无生产资产**。Director 保持谜题事实与 Token 权威，Presentation 保持原生一次性接触消费，**新脚本只驱动临时表现**。
- 实际连续顺序：等待真实 P02 夹具 Resolve → 保留 Staff/灯/偶/幕/主灯/曝光/POV → 按**经过时间连续平移** → **精确到终点后一次**原生 `TryAcceptStaffContact` → 核验同 Token 快照并做一次重复拒绝 → 才从**实际实体 A** 反算既有 **15 边 16 节点**并连续展开。**起点截图完成后才开落杖时钟，接触核验后重新开生长时钟，不把前阶段积压时间带进生长；中途无截图停顿。**
- 参数仅进程级：临时默认 **Drop2/Growth6/FinalHold6**（**只为方便观察的预览占位，绝不写入 Definition/Blueprint/Sequencer**），Run3 为 **4/12/4**；可用 `-DropSeconds` / `-GrowthSeconds` / `-FinalHoldSeconds` 调整。**2/6 与 4/12 都只是候选，不替用户选正式节奏。速度改变不改变 P02 的 Hold 1.25s 与 15Hz；真实 Resolve 仍来自既有 P02 夹具，不是已完成的 P03 谜题。**
- **三次真实 Editor 启动**：**Run1 失败**（PID 26456，在导入旧 ForestProjection 输出守卫时被拒绝，**未进入 PIE、无截图、无 MotionFrame**，日志保留；根因为 PowerShell `SetEnvironmentVariable(name,$null)` 传出空字符串，改为 Env Provider 删除并按原存在/缺失分支恢复，**旧守卫不放宽**；另有 2 次启动器干跑修正，**未修改执行策略**）。**Run2 成功**（PID 35776，占位 2/6/6，481 MotionFrame ＝ 起始 1 + 落杖 120 + 生长 360，**3406 枝体布置 / 6812 中心端点 / 27248 bounds 角**）。**Run3 成功**（PID 6484，经新根 cmd，4/12/4，961 MotionFrame ＝ 1 + 240 + 720，**6810 / 13620 / 54480**；**3406 不是 Run3 计数，不得混用**）。两次成功各 `Completed(error=null)`、**共 4 张 1600×900 首尾原图**、**无中间视频**。**以上计数均不是 Automation 项。**
- 两次成功**各 1 次接受、1 次重复拒绝**；Token **同轮相等但互不通用**：Run2 `A89ABCE14F15ACE7312BB5ABE507B041`、Run3 `22B2FF154539C6274B15D4BC6E3D56F7`。**接触前无树**，展开后仍为**同根 15 枝 16 节点**且从实际 A 反算；**主灯/幕/偶根/POV/FOV/曝光/Staff 旋转缩放**均保持。
- **真假验证边界**：真实 bounds 与变换**由 UE 读取**、投影**调用原生库**、原生 `TryAcceptStaffContact` 真实接受与拒绝；**8 角/端点诊断 assert 由 Python 执行——不是新增 C++ 体积契约，不是像素可见性证明**；**逻辑/Launcher mock 不启动 UE，不冒称原生故障或包装验证**。测试夹具修正（首轮 mock 计数 script 作用域不正确，已改为共享对象后通过）**如实记录，不隐瞒**。
- **恢复完整 Staff 变换 + 旧 Token 拒绝 + 临时对象销毁属于 Dev 退出清理，不是游戏 Skip/中断统一终态。** 最大回调间隔 `drop 31ms / growth 32ms` **仅本机诊断记录，不是 GPU/FPS/多帧率通过**。
- 用户使用：**先关闭其他 UE 实例**，再双击根 `Start-M3Continuous.cmd`，**保持鼠标键盘不动**，自动结束后恢复并退出。**这不是按 E 可玩的第三幕**；**旧 `Start-M3Geometry.cmd` 不含新样本**；**只在 Editor 可用，现有打包版本不含**（Python 是 Editor-only）。
- 两次成功各 **13 条**既有本地化 smoke-test `Error` 与 **3 条 `Warning`**（1 条 NVIDIA/TSR 驱动兼容、2 条 HTTP 退出告警）。**不写零 Error，也不把 Warning 据猜测归因为画面问题**；账号/遥测标识不向文档转录。**无本轮 C++ Automation、编译、Cook、Stage、Package 或性能测试；历史 48 项不是本轮重跑。**
- 画面仍是原**裸枝 V 形/浅弧灰盒**：低位横向根、双线、阴影锯齿仍在，**无叶片/林层/桃林语义**，场地与地板仍占位。**不是参赛高质量林相，不是正式连续演出，不是用户视觉或节奏验收，不是 P03 可玩完成。**
- 仍**没有**生产 Forest/Blueprint/Sequencer 演出、Finale/整体重启/三幕队列/P03Definition/正式美术声音；未测焦点切换/多帧率/中途 Token 原生故障注入；**Development 包验证未做**——正式接入仍需 Blueprint/Sequencer 表现接口并在 Development 包验证，**这不是本次已完成项**。
- 文档交接前 **140 个原产品 SHA 全相同、新增 3 个入口共 143**；`Source`/`Config`/`Content`/`.uproject`/旧启动器/其他 Docs 不改，**无 Git 写入/删除/提交**，Computer Use 的 `STOP` 仍保持。**最终数量待交付后由 Codex 审计，本文不预写最终全哈希结论。**
- 详见 [`P03_CONTINUOUS_PREVIEW.md`](P03_CONTINUOUS_PREVIEW.md)；证据在 `Saved/Audit-2026-10-04-P03ContinuousPreview/`。

### 2026-10-04 原生成林几何接口增量（最新；以上全文保留为历史）

- 用户测试独立连续 Dev 预览后表示**「勉强达到效果，可以继续下一步」**——记录为**连续因果基本可读、视觉仍须提升**。**这不是正式美术、完整 P03、秒数或目标参数签收；后续视觉提升目标明确保留，正式 Q1–Q5 仍待确认。** 本段之前的「树形几何未实现」是**当时的历史事实**；现已实现**无状态几何库**，但**尚未挂接表现入口，不是正式 P03**。**本计划整体仍未完成。**
- 本轮**仅新增 3 个源码**：`Public/Stage/DYForestGeometryLibrary.h`、`Private/Stage/DYForestGeometryLibrary.cpp`、`Private/Tests/DYForestGeometryAutomationTests.cpp`。**不改 M2、地图、主灯、镜头、曝光、输入、15Hz 或旧预览入口；不新增 Actor、模块或插件。**
- `UDYForestGeometryLibrary` 为**无状态** Blueprint Function Library：**无 World、无 Actor 引用、无时钟、无资源加载、无输入、无委托、无 Tick、无持久状态**；**不生长 Actor、不推进谜题/Finale、不消费 Token**；**不硬编码** 15 枝、Z70、正式林相或演出时长。两个入口：`IsForestLayoutValid` 与 `SampleForestGeometry`。
- **坐标单位口径**：枝段 `StartScreenOffset`／`EndScreenOffset` 是**接收面局部 `+Y`/`+Z` 单位**，**不是 UV、也不是世界厘米**；`DiameterWorld` 是 A 端源深度的物理直径（cm），**不隐含默认美术尺寸**；`GrowthBegin`／`GrowthEnd` 是**归一化表现进度**，**绝不是秒数或谜题阈值**。输出 `MeshWorldTransform` 是**网格组件的世界变换，不是其 owner Actor 的变换**。
- 实现要点：由 Staff **自身实际 bounds 与组件变换重建 A/B 两端**并复核；**物理根取 `Staff.EndAWorld`、幕上根取接触投影**，按**实际 `ScreenTransform` 与重算 `RayParameter`** 逆解到**同一源深度**；网格**以局部 Z 为成长轴**，**偏心 bounds 用完整中心补偿**使实际两端精确落在计划起点与当前终点；`MakeFromZ` **传单位轴**以避免极短萌发枝被安全归一化阈值清成零基；零长度枝段**只输出隐藏标志 + 未应用的单位变换**，不生成可见零长度网格。
- **失败闭合**：7 态 `EDYForestGeometryStatus`（`InvalidContactGeometry`／`InvalidLayout`／`InvalidMeshBounds`／`InvalidProgress`／`OutsideScreen`／`InvalidComputedGeometry`／`Valid`）。布局校验拒绝空数组、根不唯一、父索引越界、连接点不匹配、`GrowthEnd ≤ GrowthBegin`、直径非正、**向梢增粗**、**重复终点**、**回到根**。**失败返回空枝数组，不泄漏早先结果。**
- **授权边界（不得弱化）**：`ContactToken` **只是诊断身份副本**；**合法非空随机身份也能得到数学 `Valid`**（测试明确证明该边界）。**未来调用方必须经 Presentation 接受并再次核对当前接触/Resolve 身份；`TryAccept` 返回 true 后仍可能被同步回调复位。** 本库**不构成身份授权**。
- **实编与自动化**：三目标实编通过（`DengYingShanHaiEditor` Win64 Development、`DengYingShanHai` Win64 Development、`DengYingShanHai` Win64 Shipping，均退出码 0 / `Result: Succeeded`；本机 UE 5.8.3、英文 junction、`-NoUBA -WaitMutex`、Windows SDK 10.0.26100.0、MSVC 14.51.36260；保留非首选编译器与 Engine `Character.h` 既有弃用警告，**不改引擎或环境**）。**最终 Automation 58 Success / 0 Failed**（`UnrealEditor-Cmd -NullRHI -unattended`、正常 `TestExit`、0 ensure）＝ **10 项新测试 + 48 原有**。**Game 编译不是 Cook/Package/运行成功证据。**
- **首轮 56 不是最终**：首轮仅 8 项新测试时全 56 Success；审查发现 `MakeFromZ` 默认 `GetSafeNormal` 的**长度平方阈值可能把微小萌发 Direction 清成零**，**已改为传 `Direction`／`Length` 且不改变可见 epsilon**，随后补测极小根/子枝、Staff 自身旋转/负缩放、反向接收面、首段有效但后段角体积失败等用例，再复编全 58 Success；**初轮日志留存，不把首轮通过冒称已覆盖微小生长。**
- 10 项新测试前缀 `DengYingShanHai.P03.ForestGeometry`：`PhysicalRootAndInverseProjection`、`RotatedScaledReceiver`、`ActualAndOffCenterMeshBounds`、`NormalizedParentBeforeChild`、`InvalidTopologyAndAuthoring`、`InvalidInputFailsClosed`、`EightCornerEnvelopeAndReceiverLimits`、`ValuePurityAndAuthorityBoundary`、`TinyEmergenceKeepsValidAxis`、`TransformedStaffAndOppositeReceiverFace`。独立代理只读审查；**源码修改/构建/验收均由 Codex 负责。**
- **八角包络的边界**：**不是像素、半影、遮挡或视觉质量验收**；**`Valid` 仅指当前进度样本**；**隐藏枝段只检查完整中心线，不检查未来全部进度的八角体积**。
- **真实 Engine Cylinder 只在自动化测试中被加载**（`ActualAndOffCenterMeshBounds`），**不是新运行库的硬资产依赖**；本库为纯代码库、不加载资产；**未下载新资产、未付费**，本轮**不新增许可条目**。
- **本步未做**：无新增 GUI/阴影画面验证、**无 Cook、无 Stage、无 Package、无性能测量、无本轮人工第三幕检查**；**旧包不含新接口**；**现有 Python 连续预览仍是旧实现，未改为调用本库**。**打包验证程序未执行。**
- **下一技术小步（本轮未实现、未开启）**：在 `Dev/M3` 用**显式 Presentation 调用**接入**仅负责枝段显示/归一化进度/清理**的表现 Actor，复用本库，**继续保留真实同主灯投影**；**具体 Actor 生命周期与中断清理需列出后再实现**。**新库尚未挂接 Blueprint，Forest Actor 不存在。** 正式目标/容差、落杖与成林秒数/超时、Skip/R 与整局重启**仍按 Q1–Q5 逐项确认**；**视觉廉价感仍需正式免费合规美术、林相与剧场材质层改善，不以几何库验收替代。**
- 文档前哈希：**144 个原产品 SHA 全相同、0 缺失**，新增 3 源码；`Source`（新增 3 个除外）/`Content`/`Config`/`Scripts`/`.uproject`/启动器未写入，**无 Git 写入/删除/提交**。**最终五项产品白名单、原 Plan 完整字节前缀、HEAD 与空 index 由 Codex 在本文档交付后检查，本文不预写最终全哈希结论。**
- 详见 [`P03_NATIVE_FOREST_GEOMETRY.md`](P03_NATIVE_FOREST_GEOMETRY.md)；证据在 `Saved/Audit-2026-10-04-P03NativeForest/`。

### 2026-10-04 原生成林表现 Actor 增量（最新；以上全文保留为历史）

上一段「Forest Actor 不存在」是**当时的历史事实**；本段更新为：表现 Actor 已实现，但**不是正式第三幕演出**。本计划整体仍未完成。

- **工程已迁移**：物理根 `D:\灯影山海`，英文 junction `C:\UEProjects\DengYingShanHai` 指向同一目录；旧 C 工作区仅保留兼容目录与根文件副本。**给用户的启动地址一律使用 D 盘。** `P03_NATIVE_FOREST_GEOMETRY.md` 保留为历史步报告，其「当步未接入」事实不被覆盖。
- `ADYForestPresentationActor` 只管理枝形 StaticMeshComponents、冻结 authoring 内容、归一化进度与清理。**无 Tick、无 timer、无世界扫描、无 Director 读取、无输入、无谜题评分、无演出秒数、无完成游戏权力、不硬编码美术默认资源。**
- mesh/material/layout 由外部作者配置；运行会话用内容副本与真实 mesh bounds；**mesh 局部 Z 为生长轴**；**库输出组件 world transform，不重复乘 Actor 变换**；Movable、NoCollision、visible 时 cast shadow；失败与清理**先隐藏关投影再 DestroyComponent**。
- Actor 侧 Begin/Apply/Clear **私有**，`friend ADYStagePresentation` 才能调用，绑定 weak owner 与 token。Presentation 新增 `BeginForestPresentation(Token)` / `SetForestNormalizedGrowth(Token, p)` / `ClearForestPresentation(Token)` 与显式可空 `ForestPresentationActor` 引用。**必须真实 Resolve、真实 A 接触、当前同一 token**；Begin/Set 再捕获实际灯/Staff/幕布/地线几何，**变化时拒绝，更新失败清除旧树，不撤销谜题成功**。活动期间重复 Begin、外来 owner/token、跨 World **只拒绝，不抹掉当前会话**。
- **授权边界**：几何库中的 Guid **只是诊断值，不是授权**；**数学 Valid 不是阴影像素、遮挡、半影、美术或 FPS 证明**。Clear 后若仍是真实当前接触可显式重建 Dev 资源，**这不是正式 Skip、R、RestartExperience 或 FinishFinale 的决定**。
- **接口说明**：真实 Resolve/A 接触/当前同一 token 是 Begin/Set 的前提；Clear 只匹配所属会话的有效 token，不再要求接触条件。失效通知与拆卸能够释放资源，不代表完成游戏权限。
- Director 新增 native resolved-invalidation 通知：**先清事实再通知旧 token**；**serial 防重入覆盖，EndPlay 禁止复活**；Reset 的两处控制复位在广播后再查 serial；Presentation **只清与旧 token 匹配的会话，延迟旧通知不能抹掉新 Resolve**。
- **成功测试**：最终 Editor 自动化 **68 Success / 0 Failed / 0 NotRun**（58 旧 + 10 新 ForestPresentation）；三目标 Editor Development / Game Development / Game Shipping 均 Succeeded、exit 0（保留 MSVC 非首选警告与引擎 `Character.h` C4996，**不说零警告**；Shipping 只编译，**未生成新 Shipping 包**）。Run1 实际渲染预览 4/12/20 秒（临时）Completed，单次 contact/重复拒绝、15 枝、drop 240 + growth 721 = **961 motion callbacks**、**31339 次实际组件检查**、全释放/Staff 恢复/旧 token 拒绝、未 save 资产；**未以回调频率冒充 FPS**。
- **失败测试**：首编参数 `Owner` 遮蔽 `AActor::Owner` 致 C4458改名 `PresentationOwner` 后解决，**失败日志保留、不说一次成功**；首轮自动化 67 Success/0 Failed，补场景守卫与真可见前置断言后为 68。**原始日志存在既有错误、警告与新 InvalidActivation 的预期错误；测试通过不等于原始日志零错误。** 10 项新测试含 `InvalidActivationStillClears`、`SharedActorCannotBeHijacked`、`InvalidationReentryPreservesNewSession`、`InvalidationDestroyCannotResurrect`、`CurrentSceneMustMatchAcceptedContact`（分别移动实际灯/幕/地线/Staff 后拒绝更新与重建并清旧枝）；前三类主体 teardown 测试**先证可见与投影存在再证清理，避免真空通过**。
- **包验证（NullRHI，不是成林画面验收）**：新隔离 DevelopmentPackage Cook 根明确 `/Game/DengYingShanHai/Dev/M3/Maps/LV_M3GeometryProbe`，**非 cookall、不覆盖旧包**；BuildCookRun exit 0，Cook/Stage/Pak/IoStore/Archive 成功。第二个 `DevelopmentPackage-Verified` 同样完成打包并保留完整 `Package-UAT-Verified.log`；脱离 Editor/Python 从该包 exe 以 `-NullRHI` 执行 ForestPresentation，**10 Success / 0 Failed / 0 NotRun、exit 0**——**证明包中原生资源/几何/授权/生命周期代码与 cooked Cube/Cylinder 可执行；无图形渲染，不证明包中连续成林镜头。** 既有地图文件未修改，新 Actor 与接线只在未保存夹具中生成，**不含一个已接线的正式 P03 演出**；**双击包 exe 不会自动播放新成林预览，不交付该包为正式游戏入口**。
- 新入口 **`D:\灯影山海\Start-M3NativeForest.cmd`**（在文件资源管理器双击，不在 Codex 点开读代码）。需先关闭 UE、不要操作鼠标键盘、自动结束。**默认 2s 落杖 / 6s 生长 / 6s 留帧，仅临时比较值**，可从新 PS 参数调整，**正式时长未定**。预览脚本 `Preview-P03NativeForest.py` 派生旧连续预览但替换枝段管理，复用真实 P02 Resolve 夹具、实际 Staff A、已确认 Z70 地线、15 枝 16 节点、旧主灯/曝光/POV/保护区；**Python 不直接变换 branch 网格**；**15 个枝形的实体根是实际后台 A，不是幕面接触点**。新 launcher 只允许 D 根或英文 alias，拒绝已有 UE 与证据覆盖，使用新 output env 并恢复旧 env；**旧 C 根老 continuous launcher 可能报 junction workspace mismatch，本轮未改**。
- 临时原生 Actor 与地线**只在独立 Editor/PIE 内生成，不保存地图/BP/资产**。**未新增或保存 Blueprint 子类，但接口已可供 BP 调用且已由真实 Python 反射验证。** 首尾 HighResShot：`Run1\01-Start.png` 与 `02-ForestComplete.png`，1600x900 无 UI 叠层。Codex 已查看终帧：**细直枝、灰盒舞台、环境与形象仍有廉价感，未签正式美术/文化或用户视觉验收。**
- 范围：4 个原源码改动 + 3 个新源码 + 新 py/ps1/cmd 三入口 + 新文档与本追加，**共 12 个产品文件**；**零 `.uasset`/`.umap`、零 Config、零旧脚本或启动器修改**；实编更新本机二进制与缓存，Cook 自动更新两份未跟踪 `Build/Windows/FileOpenOrder` 生成日志，**单列而不冒称整个 Build 未变**。无 Git 写/commit/删除，无付费或新资产下载；Engine 免费灰盒沿用既有许可登记，**不把引擎内容叫开源**。细分计数与最终范围哈希由 Codex 终审。
- **协作约定**：**WorkBuddy 输入框存在限制，后续交接只发送短摘要与本地任务路径；具体上限未测。**
- **入口实测补记**：根 `.cmd → Windows PowerShell 5.1` 链路已真实运行；无 BOM 中文路径误读已修正，不改执行策略。Run2/Run3 清理均成功，Computer Use 看到了 Run3 前台林影终帧；没有代签用户或正式美术验收。长提示移到本地，284 字符短提示已成功发送；该长度不是最大上限。
- **未完成**：正式 P03 target/tolerance/hold、落杖与成林秒数及超时、Skip/R/全局重启**按 Q1–Q5 逐项确认**；免费合规美术与剧场质感、声音、完整三幕、5–8 分钟、性能、人工 PIE 与现场包视觉验收仍待后续。**本步只完成表现 Actor 资源层与独立 Dev 入口，不自行开启下一功能。** 用户前次「勉强达到效果」保留为「旧预览因果可读、视觉仍需提升」，**不可用本轮自动化替代用户新画面确认**。
- 详见 [`P03_NATIVE_FOREST_ACTOR.md`](P03_NATIVE_FOREST_ACTOR.md)；证据在 `Saved/Audit-2026-10-04-P03NativeActor/`。

### 2026-10-04 成林 Dev 资源持久化增量（最新；以上全文保留为历史）

上一段「未新增或保存 Blueprint 子类」是**当步历史事实**；本段更新为：**Dev 数据型 Blueprint 已保存、冷读并通过隔离包加载验证**，但**不是正式美术、正式时长或正式第三幕**。本计划整体仍未完成。

- 用户本轮「没问题，进入下一步」是**上一版原生成林 Dev 预览的人工确认**，**不是**正式 P03 艺术/时长/整局/现场包画面或性能签收。**本步保存资源不会自动改善灰盒质感。**
- 新资产 `Content\DengYingShanHai\Dev\M3\Forest\BP_DYForestPresentation_Dev.uasset`（28,558 B），父类 `ADYForestPresentationActor`，保存从**真实 Resolve / A 接触**采集的 **15 枝 authoring**；Engine Cylinder `/Engine/BasicShapes/Cylinder.Cylinder`，material override = NULL、实际 fallback `/Engine/EngineMaterials/DefaultMaterial.DefaultMaterial`。**Engine 灰盒形状只属 Dev 灰盒，不是最终高质量树林美术。**
- 蓝图**只保存 authoring**：mesh、null material override、15 个 branch definitions（**normalized intervals，不是秒数**）。**不保存**运行 token/contact/session、动态组件、演出秒数。**未新增可执行图表链路。** 实际 Editor 测试 AddInfo：`status=3`（BS_UpToDate）、UbergraphPages=1、FunctionGraphs=1、recursive graphs=2、**nodes=4、exec pins=4、exec links=0** —— 正确表述是**「没有连接的执行逻辑」，不是「没有图表/节点」**。
- 完整链路：新进程真实 Capture → 另一进程单独创建/保存 → 冷读已保存类实例 → Presentation 用真实 Resolve 与 A 接触授权 → C++ 原生组件/变换/真实投影 → Clear/Reset/EndPlay 释放。**不绕过授权，不动态重写已保存类的布局。** 三阶段证据：`CaptureRun1/Capture.log`（原始 P02 fixture **不是正式 P03 谜题数据**）、`Asset-Save.log`（只保存这一个新 BP，文件存在检测拒绝覆盖）、`Preview-Run1.log` 与 `Preview-Run2.log`（新进程加载已保存 GeneratedClass，只校验 15 枝与同一真实接触样本一致）。
- 预览实况：Run1 临时 4/12/30 秒、**54,402** 次重复组件检查；Run2 临时 2/6/6 秒、**19,210** 次；两次均 `Completed(error=null)`、全部组件已释放。Run2 补强终态断言（15 枝布局不变、CDO 会话与组件为空、CDO mesh 仍 Cylinder、material override 仍 NULL）。两次均为 **Editor/Python 驱动的未保存地图 Dev 自动连续预览，不是独立打包的连续演出，不是正式秒数或游戏 Restart 策略**。Codex 在 Run1 用官方 Computer Use 看到同版灰盒末态，**未代签用户对新运行或正式美术/性能的验收**。
- 构建与测试：首次 Editor 编译 **exit6**（测试 3 处 `FArrayProperty::Identical` 缺 `PortFlags`，仅补第三参 0 后重编，**失败日志保留**）；Editor 最终 / Game Development / Game Shipping 均 `Result: Succeeded`、exit0（**Shipping 只编译，未生成新 Shipping 包**）。**全量 Editor 自动化 70 succeeded / 0 failed / 0 warnings / 0 notRun / 0 inProcess**；旧 68 项集合全部保留且再次成功，只新增两项 ForestAsset；**旧 10 项 ForestPresentation RunTest 正文与 Before 逐字符相等**。
- **Cook 与包**：Windows Development Cook/Stage/IoStore/Archive **UAT exit0**，完整成功 markers，真实 Cook 命令含狭窄 Forest CookDir。**独立包 Runtime 自动化 11 succeeded / 0 failed / 0 warnings / 0 notRun / 0 inProcess**（＝原 ForestPresentation 10 项 + 新 ForestAsset 运行测试 1 项；**图表测试为 Editor-only，不应声称包内跑了图表测试**）。旧地图**没有持久引用**新 BP，故 Cook 显式指定 `/Game/DengYingShanHai/Dev/M3/Maps/LV_M3GeometryProbe` 并加额外实体目录 `Content/DengYingShanHai/Dev/M3/Forest`；**不改 Config、不 CookAll、不宣称地图单独能带入该资产**。最终包 exe 与本步 Game Development exe 的 SHA256 均为 `69CC74710775F91B90F1048F7D68F83118588197C29D81CA1E2019E81F58C8A7`。
- **NullRHI 的局限**：包用 NullRHI、不依赖 Editor/Python，**证明类/资源/几何/清理可以加载运行**；**不证明屏幕渲染、森林画面、FPS 或正式 P03 流程**。**本步包是 NullRHI 类加载/资源验收，不作成林图形验收，也不作正式可玩第三幕。** 自动化报告的 0 失败**不等于整份 UE 日志零 Error/Warning**（EditorTests 13、PackagedTests 1、Preview-Run1/2 各 13、Package-UAT 0；Ensure 统计各为 0；Preview 各 3 条 Warning，其余上述日志 Warning 0）。编译器 14.51.36260 高于 UE preferred 14.50.35717，**保留环境警告，不改工具链**。
- 启动地址 **`D:\灯影山海\Start-M3ForestAsset.cmd`**：在文件资源管理器双击，先关闭 UE；它调用 Windows PowerShell 5.1 再启动本机 UE 预览，自动运行/恢复/退出，默认 2/6/6 秒仅为预览值。脚本为 ASCII，检查英文 junction 指向 D 物理目录、已有输出拒绝覆盖，环境变量仅对子进程临时设置后还原。**Codex 链接可能打开源代码，不要把「看到代码」当执行成功，不要双击 PS1 期待执行。旧入口未改。此入口仍需本机 UE，不是独立游戏包。** 本步包 runtime exe 仅作资源验收，不提供正式第三幕通关入口。
- 本轮范围：8 个产品文件（测试 cpp 修改；新增 BP、`Create-P03ForestDevAsset.py`、`Preview-P03ForestAsset.py`、`Start-M3ForestAsset.ps1`、根 CMD、本文档；Plan 仅追加）。两份 Build/FileOpenOrder 工具日志列入生成物白名单，实测仅 `EditorOpenOrder.log` 哈希变化、`CookerOpenOrder.log` 不变，不冒称整个 Build 目录未变化。Codex 实际核验：191 基线中2产品修改、1工具日志变化、其余188哈希不变，新增6产品，共197文件，无越界/缺失；Plan 原60,237字节完整保留；HEAD不变、index为空、原86项dirty全部保留、当前91项。未Git提交或清理用户文件。首次结果 `FinalEvidence.json` 保留，文档数量口径修订后的复核另存 `FinalEvidence-Reviewed.json`。
- 回退：Before 保留 cpp 与 Plan 完整基线（`Saved\Audit-2026-10-04-P03ForestAsset\Before\`）。回退仅恢复本轮增量或移出本轮 6 个新增产品并重新构建，**必须先确认，不执行删除/reset/checkout**；不动原 86 项 dirty，不 reset/checkout/commit，不删用户文件。
- 协作约定：WorkBuddy 输入框有限制、**上限未知**，后续一律短摘要加本地脱敏任务文件，**不把长报告粘入输入框**。
- **未完成**：Q1 正式 target/tolerance/hold、Q2 落杖秒数、Q3 成林秒数/超时、Q4 Skip/R、Q5 整局重启方式**逐项确认**；正式皮影/林影/剧场免费合规美术与声音、完整三幕 5–8 分钟、性能、**包内图形**与现场人工验收仍待后续。**不得自行把灰盒当正式艺术成果，团队美术负责人不变。不自行开启下一功能。**
- 详见 [`P03_FOREST_DEV_ASSET.md`](P03_FOREST_DEV_ASSET.md)；证据在 `Saved/Audit-2026-10-04-P03ForestAsset/`。

- Codex 终审补记：本步资源持久化完成，不等于整体 P03 计划完成。包内日志的 1 条 Error 是 AutomationController 无法加载 HTML test-report template；HTML 报告未生成，`PackagedTests/index.json` 实际存在并记录 11 项成功。编辑器 13 条初始化自测 Error 不对应项目测试名失败。保留 WorkBuddy 原输出在本轮审计 `WorkBuddy-Output/`，本补记不更改前述历史字节。

### 2026-10-05 双变量候选校准增量（最新；以上全文保留为历史）

- 用户已确认**「直接双变量组合，先做 Dev 候选样本」**：**不新增**先锁灯/再调偶阶段，**不新增姿态按键**。本轮实际完成的是 **Dev 候选构图校准**，**不是玩家可玩样本、不是正式 P03 全流程、不是人工通关、不是新打包版本**，**本轮没有新游戏启动器**。**用户仅确认结构，不能据此推导具体目标或时长也已获批准。**
- 已保存的 `BP_DYForestPresentation_Dev` **仍是原 15 枝灰盒**，布局/网格/材质/CDO **未改**。角色仍灰盒、薄枝仍偏 V/U 枝形、剧场黑盒、地面偏亮，**不能称正式高质量美术通过**。
- 新诊断仅在本审计 `Calibrate-P03.py`；独立未保存 Editor PIE 临时演员与 Transient package 中未保存的诊断 Definition（**不是 RF_Transient flag**）。**只使用现有 C++ 调用，不改 C++。**
- 每采样把实际灯/偶读回值与实际当前 pose 设为诊断目标，**两个参数都启用、exact 0 容差、Hold=0**；`StartCurrentPuzzle` 产生真实 Resolve/Token。随后实际 Staff **仅平移**，A 端**真正投影**到已确认 Z70 高位地线，再经**当前身份**的原生接触授权接 Forest。**Hold=0 仅加速几何校准：不验证保持难度、不改变 15 Hz、不代表用户完成谜题。** 完整几何在显示生长前预检，用实际 Cylinder bounds 与当前接触，按实际 Torso/Head **16 角**投影加幕尺寸 **2% padding** 建保护框；**检查是真实几何/包围框，不是阴影像素识别，不证明全部连续参数空间。**
- **Run4 冷启动 50 组**成功（39 数值安全、11 预计边界不可用）；**Run5 冷启动 75 组**成功，**前 50 组选定几何/姿态/接触/结果字段与 Run4 逐项完全一致**。Run5 分组：Domain（灯/偶各 `{0,.25,.5,.75,1}`，25 组）14 Clear + 10 原生 Forest Begin 拒绝（actual pure initial geometry status 均 **OutsideScreen**，端点越幕）+ 1 Resolve 初始 A 已在幕外；LocalReference（灯 `{.63.. .81}` × 偶 `{.71.. .89}`）25/25 Clear；ReachCandidateProbe（灯同上 × 偶 `{.76.. .94}`）25/25 Clear 且全部 `P02_StrideReach`。**那 10 组不是程序异常或测试失败，而是几何上预计不可用的边界；LocalReference 是旧 P02 周边参考，不等于推荐 P03 目标。**
- 合计 **75 组：64 数值安全、74 次真实接触**；安全组每组验证 15 个实际枝组件，**合计 960 个组件样本验证（不是 960 个运行 Actor）**；**10 张 1600×900 原始 UE 截图**，**不包含完整 HUD，不能代替中文 UI/输入/保持/复位/现场人工检查**。每次在截图前后核验身份、灯偶根变换、幕与地线、Staff 接触变换、Forest token/实际组件与 POV；会话末恢复原 Definition/Staff 与 Editor 引用、释放原生枝资源、拒绝旧 Token、退出 PIE，**CDO 没有运行会话**。**该清理是诊断复位，不是游戏的 R 策略。**
- **本轮没有 Build / Cook / 新包**；**不能把上轮 Editor 70/0 与包内 NullRHI 11/0 当成本轮玩家 P03 通过**。Run4/Run5 各仍有 **13 条** `LogAutomationTest: Error: Condition failed` 初始化错误、**3 warnings**、**0 Ensure/Unhandled/Fatal**，本次诊断自身无 error，**不声称整份日志零错误**。
- 保留全部失败：Run1 参数拼接未加分组被 PowerShell 解析成 **9 个**片段（正确应 5）、无样本；两处新脚本反射/字段错误（非反射 inline getter、`ScreenLocalZ` 字段名）在 **Run2 前**修正且**不改产品 C++**；Run2 50 组 0 诊断异常但**尚无增强身份检查、不作最终证据**；Run3 在初期 POV 一致性检查中断、**0 样本**，后加入诊断出生稳定等待并沿用原数值比较方式，Run4/5 通过。**不推断已证明 Run3 的唯一物理根因，不修改相机设置。**
- 设计结论：**灯是一个连续量**；偶的位置与姿态挡位由**同一个 A/D 连续量联动**；**第三幕是两个已学控制量的组合，不是三个独立自由度**。旧参考偶 `.80 ± .09` **跨 `.75` 现有姿态边界**，所以「位置仍在退出区间」**不保证 RequiredPose 仍通过**——这是 P03 候选设计需规避的边界，**不判定已验收的 M2 有 Bug**。
- **待用户确认的 Dev 候选（尚未获批准）**：灯目标 `.72`、偶目标 `.85`；进入 `.05`、退出 `.09`、保持 `1.25s`；偶退出区间 `.76–.94` **不跨姿态边界**。已采样区域支持该提案，但**尚未实测玩家 Holding 或连续区间**；保持与容差拟与 M2 相同，**不通过增加精度制造第三幕难度**。另建议下一步 Dev **暂沿用**旧连续预览落杖 `2s`、成林 `6s`，**未确认任何正式演出秒数**。**若整理期间未收到 Codex 追加指示，以上仍标待确认。**
- 仍未确认：Q1 正式 target/tolerance/hold、Q2 drop 秒数、Q3 growth/timeout、Q4 Skip/R、Q5 整局重启、演出输入策略、正式资产。**只有此次结构选择已批准。** 之后唯一实现责任人为 Codex，队友负责正式免费合规美术/视频。
- 范围核验：基线保护 **195 个文件**，BeforeWorkBuddy 检查 **0 修改 / 0 新产品 / 0 缺失 / 0 意外变更**（本审计目录不计产品）；Git **121 dirty 均已有**，HEAD 未变、index 为空、**无 Git 写操作**，未清理其余未提交内容。**新文档与本节追加是本次唯一允许的产品变更**；最终 scope/Git 复核由 Codex 在本文档输出后执行。
- 用户可直接打开：`Saved\Audit-2026-10-05-P03InteractionCalibration\Run5\ReachCandidateProbe-L0.720-P0.850-Forest.png`（推荐候选中心图）、同目录 `ReachCandidateProbe-L0.630-P0.760-Forest.png` 与 `ReachCandidateProbe-L0.810-P0.940-Forest.png`（边界图）、`Results.json` 与 `Events.jsonl`（全部结果）。
- 详见 [`P03_INTERACTION_CALIBRATION.md`](P03_INTERACTION_CALIBRATION.md)；证据在 `Saved/Audit-2026-10-05-P03InteractionCalibration/`。

- Codex 本轮终审：75 组是采样执行完成，64 组数值安全、11 组边界不可用，不是 75 组构图全通过。AfterWorkBuddy 复核仅 Plan 末尾追加及新校准文档；原 67,878 字节历史前缀完整保留，其他旧文件、M2、Source/Config/Content/旧 Scripts/Tools/旧启动器不变；原 121 项 dirty 保留、当前 122、HEAD 不变、index 为空。最终修订复核另存 `D:\灯影山海\Saved\Audit-2026-10-05-P03InteractionCalibration\Evidence-Final.json`。本轮校准完成，整体 P03 仍未完成；Dev 具体候选仍待用户确认。
- 直接打开文件：中心图 `D:\灯影山海\Saved\Audit-2026-10-05-P03InteractionCalibration\Run5\ReachCandidateProbe-L0.720-P0.850-Forest.png`；最新说明 `D:\灯影山海\Docs\P03_INTERACTION_CALIBRATION.md`。本轮无新启动器；旧 `D:\灯影山海\Start-M3ForestAsset.cmd` 仅此前固定终态资源预览，不是双变量可玩样本。WorkBuddy 短提示本轮实际 292 字，完整显示且被接收；输入上限仍未知，继续用短摘要加本地任务文件，禁止贴长报告。

### 2026-10-05 双变量 Dev 可玩候选增量（最新；以上历史保留）

- 用户随后“确认”“继续任务”批准本次 **Dev 候选**：灯 .72、偶 .85、两项进入 .05 / 退出 .09、保持 1.25 秒、现有 Reach；落杖暂 2 秒、生长暂 6 秒。上一节“候选未批准”为当时历史；**本次批准不等于正式 Q1–Q5、输入锁、Skip/全局重启或美术定稿**。
- 新入口 `D:\灯影山海\Start-M3Candidate.cmd` 默认实际玩家操纵，无自动答案；只新增 Play / 独立 Verify / PS1 / CMD / 说明文档，本文仅追加。原 C++、M2、地图、Content、Config、旧 Scripts、Tools、旧启动器不改，无 Git 写操作。
- 最小 Editor-only 适配：transient-package Definition 接既有原生 15 Hz Director；真实成功后从本次 Staff 姿态开始纯位移；实际 A 接触原高位地线（世界 Z70）后，原 Presentation 授权保存的 15 枝 BP 实例，完整边界预检后真实投影生长。原生控制、POV 所有权和 R 上下文不改，复位仅恢复脚本负责的位移、不覆盖新姿态；没有世界 Tick 扫描或新核心判定。
- 最终 **Run9 / Run10 各 12 项诊断检查通过、0 失败**，各一次完整成林；Run10 是补强 CDO mesh/material 检查的最终代码。不是 C++ Automation 新增 12 项，不是 24 项不同检查。保留 Run1–8 失败，完整明细见新文档。诊断用已有 setter 和 E/R 同语义接口，**不冒充真人按键**。
- 真实 hold 约 1.267 秒；Run10 接触 `[925,9.96694,70]`、drop 约 2.000074 秒；局部地线 -35 对应世界 Z70。完整 15 组件/真实阴影可见，仍是细枝与占位偶的灰盒；**不代表消除廉价感或正式艺术验收**。
- 不新增或打包 runtime 演出：Python Slate cue 只在 Editor/未保存 PIE 中运行。**无 Build/Cook/新包，物理键鼠、中文 UI、新构图、操作手感待用户四项人工检查。** 通过候选后，正式 Blueprint/Sequencer 接入仍需独立批准、实现与包验收。
- Run10 全日志仍有 13 条初始化 Automation Error、3 warnings、0 Ensure/Unhandled/Fatal；本次诊断 error=null，不声称全日志零错误。Windows 双零线程/句柄的已退出进程对象曾阻止入口，现新启动器只忽略双零对象，活/未知 UE 仍拒绝启动，绝不结束他人进程。
- 本轮电脑操作初始化连续超时，因此没有发送 WorkBuddy 或桌面 HUD 验收；Codex 整理文档，保留 WorkBuddy 短提示规则，未虚构协作结果。负责人仍 Codex，队友后续负责免费合规正式美术/视频。
- 说明：`D:\灯影山海\Docs\P03_DEV_PLAYABLE_CANDIDATE.md`；证据：`D:\灯影山海\Saved\Audit-2026-10-05-P03PlayableCandidate\Run10\Events.jsonl`；终帧：同目录 `ForestComplete.png`。请在资源管理器双击启动文件，聊天链接可能只预览代码。

- Codex 最终增量：Run11 关闭 local import 前的缓存写入后，原 12 项再次通过；唯一新增缓存已移动至审计目录可恢复留存，未触碰旧缓存。Run12 最终 **13 项诊断检查 / 0 失败**，新增“E 同语义放开后的第三幕成功文案保持正确”，只纠正当前 TextBlock、不改 CDO/判定/输入。最新证据 `D:\灯影山海\Saved\Audit-2026-10-05-P03PlayableCandidate\Run12\Events.jsonl`、`Result.json`、`ForestComplete.png`；`Finished(error=null)`、15 实组件验证、实际接触世界 Z70。首份 scope 报告因自动缓存未归档而失败，保留；最终范围以 `Evidence-FinalReviewed.json` 为准，文档旧 75,073 字节前缀需完整保留。人工四项、正式 runtime/美术/完整三幕/包仍未完成。

### 2026-10-05 入口检测后：运行时落杖数学基础（最新增量，以上历史字节保留）

- 入口已单独修复：默认可见 Play / Ready 与退出监控、HUD 后请求 GameOnly/游戏焦点、停止 PIE 后清理而保留编辑器。Run19 可见中文与退出留存；最终 Run20 诊断 13/0，启动协议模拟 6/0。证据 `D:\灯影山海\Saved\Audit-2026-10-05-P03LaunchFix\`。旧文“停止 PIE 自动结束编辑器”已过时；不要保存临时地图，重试应正常关闭并从根 CMD 重新启动。
- 用户回复“检测完毕直接开始下一步”，登记为当前入口检测完成及后续开发授权；不虚构未逐项描述的人工细项。下一技术方向是候选向可打包运行时迁移，本步只先完成既定 C++ 可测试底层，未实施 Blueprint 执行图、地图接线、正式参数或新的最终状态。
- 新增 `UDYStaffDropLibrary::SampleStaffDrop` / `FDYStaffDropSample` 与 8 项独立自动化。纯函数从真实局部 bounds、固定 Resolve 组件变换、原射线与原地线计算平移；保持 Staff rotation/signed scale、幕局部 X/Y，只向原地线 Z 下落。输出端点按最终变换重新捕获，终点再复核原接触与横向位置；无效输入/无法表示的数值结果失败闭合。
- **纯数学 Valid 不是当前 Token 授权、接触接受或游戏完成**。GUID 只复制；没有 World/Actor/CDO 写入、资源加载、计时/秒数、Timeline、输入或 POV。B 可在幕外，不新增第二端接触要求，不放宽地线 epsilon。当前 Python 候选未接入新库，因此本步没有新画面。
- **最终 Editor 自动化 78 Success / 0 Failed / 0 Warnings / 0 NotRun / 0 InProcess**，退出码 0；原 70 项完整保留且再次成功，新 8 项含因果终点、纯值/旋转/镜像/偏心bounds、完整receiver变换、大坐标失败闭合、进度边界、无效快照、缓存复核、地线/高度与运行时反射。新测试为 EditorContext，不能声称包内已跑 8 项。Editor Development / Game Development / Game Shipping 三目标编译均 Succeeded、exit 0；不把 Game 编译当 Cook/Stage/Package/Deploy/Run。
- 原始测试日志仍有 13 条既有初始化 Error，0 ensure/Unhandled/Fatal；保留非 preferred MSVC 与引擎 Character.h 弃用警告，不修改引擎/环境、不声称整份日志零错误。没有 Cook/新包，没有新的渲染/性能或正式艺术验收。
- 范围：新增3源码+新迁移说明，修改候选说明、本文仅末尾追加；不改任何旧源码、Config、Content、已有 Scripts/启动器、M2、15 Hz或已保存15枝BP。Before保护200文件与127项dirty；最终6产品白名单、用户保存地图、本文原字节前缀和Git状态由Codex终审。无Git写操作、删除、下载资产或新增付费/插件依赖。
- 后续 Blueprint 表现时间线、真实接触后的重入复核、完整15枝最终bounds与Torso/Head保护区预检、局部复位/EndPlay清理及独立Development包仍未接入。正式Q1–Q5、输入锁、Skip/R、整局重启、三幕队列、正式免费合规美术/声音、5–8分钟与现场图形验收不因本步通过而定稿。
- 负责人 Codex；本步未发送 WorkBuddy，短摘要+本地文件的输入限制约定不变。说明：`D:\灯影山海\Docs\P03_RUNTIME_DEV_MIGRATION.md`；证据：`D:\灯影山海\Saved\Audit-2026-10-05-P03RuntimePreparation\`。当前运行文件仍为 `D:\灯影山海\Start-M3Candidate.cmd`，在资源管理器双击，不是点击聊天链接预览代码。

### 2026-10-06 已保存运行时接线与独立包（最新增量；以上历史字节保留）

- 用户继续既定任务。本轮已新增纯 ForestPreflight、Stage 最小只读资源 getter/真实旧身份失效 BP hook、2 张保存的 Blueprint Timeline、6 个 Runtime 资产及独立 `LV_M3RuntimeCandidate` 副本；包内落杖/接触/生长不再依赖 Editor Python。负责人 Codex；队友后续正式免费合规美术/视频职责不变。WorkBuddy 本轮未收发任务，短提示规则保留。
- 候选 .72/.85、.05/.09、保持 1.25、Reach、15 Hz、暂用 2/6 秒、A/Z70/15 枝均不变。原生 Director 判定、Stage 接触/授权、纯库数学、Blueprint 表现时间分层；本次真实成功 Staff 位移接地后同点成林，不瞬移/换镜头。不是正式 Q1–Q5、Skip/R 新语义、输入锁、整局结束态或三幕队列。
- 新纯预检包含最终 15 枝 bounds、Torso/Head 16 角与 2% padding；无 Actor/World/time/token 授权。实际 Begin p0 隐藏资源不替代最终预检。相同 Resolve 同步不重启；旧失效回调不清新身份；Reset 只恢复所属 Staff 平移、停 Timeline、释放枝网格。完成保持不是 FinishFinale。
- Editor 集合 **87/0**，三个编译目标成功；自然 PIE Run2 9 阶段、补强后 Run3 10 阶段通过。新增 live-map ClientContext 单独覆盖三阶段复位、旧回调隔离与完成态 Director EndPlay；未独立覆盖活动 Stage/World EndPlay或真人键鼠。
- UAT Run1 Cook 成功但输出末级不符 Stage；Run2 Zen IPv6 请求遭代理502。通过正常参数补 Windows 末级及仅子进程 localhost NO_PROXY，Run3/Run4 完成 Cook/Stage/Pak/IoStore/Package/Archive；不改全局代理、Config、引擎或旧包。证据 `D:\灯影山海\Saved\Audit-2026-10-06-P03RuntimeWiring\`。
- 诚实保留失败：Run3 包逻辑12/0；Run4 补强后 NullRHI **11/1**，一次实际组件变换与样本差异未解释，epsilon 未放宽，现已增加失败数值记录；成功 PIE 的15枝全可见/Portion=1并不能解释该失败。默认 D3D12 图形首帧两次 GPUCrash，一次正常流程通过，不称稳定。
- 图形隔离：`-d3ddebug` 有真实起点/成林图但因截图 BackBuffer barrier 错误报告11/1；仅 `-norhithread` 12/0；保留正常线程、仅 VSM OnePassProjection=0 的 Run6 **12/0** 并取得含中文 UI 真实图。后两者只是候选诊断，性能开销未测，**须用户确认后才可进入新 Dev 默认入口**。未降画质、关闭阴影、换DX11、修改注册表或驱动。
- 同上审计目录 `PackagedGraphics-Run6-Captures\UnsolvedStartup.png` / `CompletedHolding.png`；结果 `PackagedGraphics-Run6\index.json`；失败 `PackagedTests-Final2\index.json`。独立包 `D:\灯影山海\Builds\M3Runtime-20261006-Run4\Windows\` 必须显式带新地图，裸 exe 可能加载旧默认地图。本轮尚未交付稳定新默认启动器；旧 `Start-M3Candidate.cmd` 完全不改。
- 已有204文件/131dirty基线保持，旧产品修改白名单只有 Stage h/cpp 与 Migration/Plan（本文仅追加）；新产品均 Dev，新资产复用原免费许可并实查容器中字体/Forest/BP/地图、OFL随包。8个新注释节点GUID警告、初始化错误、包HTML模板缺失、非preferred工具链及旧驱动TSR警告保留。无Git写操作、删除或覆盖旧资产；最终范围与历史前缀由Codex终审。
- 下一步先定位严格变换失败、确认新Dev投影候选，再制作入口、测性能与实际键鼠/中文/重进/关闭。正式美术、声音、三幕连续体验、5–8分钟与目标机三轮完整Development/Shipping仍未完成。当前主说明以 `D:\灯影山海\Docs\P03_RUNTIME_DEV_MIGRATION.md` 的10月6日段为准；10月5日“尚未接线/打包”保留为历史，不代表当前。

- Codex 范围终审通过：4旧产品修改、13新产品、0缺失/越界；原 Plan 82,342 字节前缀完整，217产品，131原dirty全保留、182当前dirty（含2独立包生成物），HEAD不变/index空。IoStore实际也含未改默认LV_InteractionLab和Engine Entry，不能称只Cook一图；不是CookAll。8关键包文件SHA/大小和测试版本见 `Package-Run4-Artifact.json`，最新失败日志增强已三目标编译但未重封Run4。`PrecisionProbe-Run1` 编辑器二进制 -game/NullRHI 的1/0不是包证据，也不解释原严格失败。默认启动候选仍待用户确认，没有静默设置投影开关。

- 最新精度诊断补充与措辞纠正：旧 Run4 的失败原本是包含可见性/投影/TF 的组合断言，无原始值时不能直接归为变换。当前 Editor `-game / -NullRHI` 的 `PrecisionProbe-Run2` **0/1** 才实际抓到 Branch0 visible=1、shadow=1、Portion=1、仅 Z 残差 `-6.4902002264943803e-5 cm`；`Run3` **0/1** 再抓到重演最终保持 Phase4 的 Z 残差 `-1.6279472532687578e-5 cm`。最后两次诊断观测的实际位置保留不变、目标落在 UE `1e-4` 近似区间，符合源码默认小位移不更新的机制；不是紧邻 Setter 的前后观测，也不回写旧包失败的未记录值。
- 当前新测试文件内增加 Editor-only `EngineMicroTransformObservation`，独立 transient world、真实注册/no collision/no physics 组件：普通 Setter 保留 `5e-5 cm`，公开 NoPhysics 接口候选在保持/改变缩放两种情况下都通过原 `1e-8` 全TF；不改真实Forest。最新 Editor **88/0/0 warnings/notrun/inprocess**；最新 Editor/GameDevelopment/GameShipping 均实编成功，未重封Run4。原 LiveMap 严格终态仍失败，不把机制诊断通过当作产品通过。
- 新增只读末段观测和诊断版本 `20261006-MicroSetterProbe`；失败后不再同帧 Reset/Destroy，保留现场原值。新旧日志、报告及两张正常Run6包内截图均已检查，未放宽epsilon、改引擎/缓存、关闭投影或伪造物理按键。
- 两项待确认独立保留：①仅额外修改旧 `DYForestPresentationActor.cpp`，为目前无物理的林枝接公开 NoPhysics 候选，再严格验证实际15枝/重演/拆卸并重打独立包；②仅新Dev启动入口临时用 VSM OnePassProjection=0，真实阴影/D3D12/正常线程保留，但性能需测。均未静默实施；本轮产品范围仍4旧修改+13新产品，原Forest源码、旧资产/地图、M2、输入、镜头、15Hz和旧启动器不变。详情以Migration文档最新段为准。
