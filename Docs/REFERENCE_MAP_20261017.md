# P02/P03 正式入口引用链追踪（阶段 1 交付物）

> **日期：** 2026-10-17
> **执行者：** Codex（只读追踪，本轮未修改任何资产、地图或 Blueprint）
> **本地版本：** `main@dda43f2c8970c10680173387b963d1c730649f06`
> **方法：** `.umap`/`.uasset` 二进制内嵌字符串扫描（UE 保存态会内嵌被引用对象的完整路径）+ C++ `ConstructorHelpers` 硬编码路径枚举 + `Config/DefaultEngine.ini`。
> **方法边界（务必先读）：** 字符串扫描**能证明**「主图保存态中存在对该资产的引用记录」；**不能证明**该引用在 Blueprint 节点图中如何接线、运行时是否实际生效。凡涉及节点接线的结论一律标注 **需 UE 核验**。

## 1. 版本与入口身份

| 项 | 值 | 来源 |
|---|---|---|
| 正式主图 | `/Game/DengYingShanHai/Maps/L_DY_Main` | `Config/DefaultEngine.ini` `GameDefaultMap` + `DYReleaseEntryPlayerController.cpp:7` |
| 正式 GameMode | `BP_DYReleaseGameMode`（继承 C++ `DYStageGameMode`） | 主图引用扫描 |
| 编辑器启动图 | `LV_InteractionLab`（Dev） | `DefaultEngine.ini` `EditorStartupMap` |
| Dev 菜单可达地图 | EntryLoop / Readability / Alignment / Environment / FramePost / FrameBeam ×3 | `DYDevEntryPlayerController.cpp:18-25` |

## 2. `L_DY_Main` 直接引用清单（保存态字符串扫描）

```
/Game/DengYingShanHai/Core/BP_DYReleaseGameMode          ← 正式 GameMode
/Game/DengYingShanHai/Stage/BP_DYStageEnvironment        ← 三幕环境表现
/Game/DengYingShanHai/Dev/AlignmentFeedback/Guides/MI_DY_P02BodyFit   ← P02 目标提示材质（旧 Cube 校准）
/Game/DengYingShanHai/Dev/Readability/Guides/MI_DYReadability_P01
/Game/DengYingShanHai/Dev/Readability/Guides/MI_DYReadability_P03
/Game/DengYingShanHai/Dev/Readability/Stage/BP_DYReadabilityPresentation
/Game/DengYingShanHai/Dev/M1/Data/DA_DY_P01_SunAwakening ← P01 谜题数据
/Game/DengYingShanHai/Dev/M2/Data/DA_DY_P02_ChaseForm    ← P02 谜题数据
/Game/DengYingShanHai/Dev/M3/Forest/BP_DYForestPresentation_Dev  ← P03 森林（Dev 版）
/Game/DengYingShanHai/Dev/TheatreAudio/Sounds/SFX_DevForestLeaves
/Game/DengYingShanHai/Dev/WoodFloor/Materials/MI_DY_WoodFloor_Dev
/Game/DengYingShanHai/Dev/StageWings/Meshes/SM_DY_WingScreen
/Game/DengYingShanHai/Dev/FramePostAsset/Meshes/SM_DY_FramePost_Source
/Game/DengYingShanHai/Dev/FramePostAsset/Materials/MI_DY_FramePost_Base
/Game/DengYingShanHai/Dev/FramePostAsset/Materials/MI_DY_FramePost_Wood
/Game/DengYingShanHai/Dev/FrameBeamTopUV/Meshes/SM_DY_FrameBeam_TopUV
```

主图内关键 Actor 对象名：`PuppetActor`（C++ `DYPuppetActor`）、`M2_Puppet_P02_Controlled`、`ForestPresentationActor`、`ForestRoot`、`GuideP01/P02/P03`、`Readability_GuideP01/P02/P03`。

## 3. P02 引用链结论

```
L_DY_Main
├─ PuppetActor / M2_Puppet_P02_Controlled   ← C++ 灰盒 ADYPuppetActor（Cube/Sphere/Cylinder 基础形状）
├─ DA_DY_P02_ChaseForm                      ← 判定数据（目标/容差/姿态/保持时间）
├─ MI_DY_P02BodyFit                         ← 身形提示材质（旧 Engine Cube 躯干八顶点校准）
└─ GuideP02 / Readability_GuideP02
```

**静态确认（措辞按证据边界收紧）：**

1. **本次保存态字符串扫描未发现**新夸父偶 `BP_DYKuafuPuppet_Fitted` 的主图直接引用；**是否存在间接引用、动态加载或运行时替换，仍需 UE 资产引用检查（Reference Viewer / Size Map）及实际运行验证**。该 Blueprint 引用 `SK_DY_Kuafu_Refined`、`SM_DY_Kuafu_Staff`、`MI_DY_Kuafu_Staff_Wood` 与三个姿态动画（Reach/StrideBack/StrideMid），目前仅见于 `Dev/KuafuAppearance/Presentation/`。
2. 主图 P02 目标提示材质的引用记录指向 `MI_DY_P02BodyFit`——其记录中的校准依据是旧 Cube 躯干；实例参数与运行时实际效果需 UE 核验。
3. `DA_DY_P02_ChaseForm` 自身不引用其他资产（纯数据）。

**印证审查意见：** "旧 BodyFit 几何校准依据已经不能自动代表新皮影的可见身形"——本次扫描在保存态引用层面与之相容，但最终确认需 UE 核验实例接线。

**需 UE 核验：**
- 主图 `PuppetActor` 实例上是 C++ 默认组件布局还是 Blueprint 覆盖；`M2_Puppet_P02_Controlled` 的类与组件。
- `GuideP02` 的网格、材质槽是否确实使用 `MI_DY_P02BodyFit`，以及 Guide 开/关由哪个节点驱动。
- `BP_DYKuafuPuppet_Fitted` 内部旧 Torso 隐藏代理与新骨骼网格的层级（审查意见已指出存在，需保存态确认）。

## 4. P03 引用链结论

```
L_DY_Main
├─ ForestPresentationActor / ForestRoot
│   └─ BP_DYForestPresentation_Dev → C++ ADYForestPresentationActor
├─ SFX_DevForestLeaves
└─ DA 无（P03 判定数据在主图内联或需 UE 核验）
```

**静态确认：**

1. 主图引用的是 **Dev 版森林** `BP_DYForestPresentation_Dev`；它只继承 C++ `ADYForestPresentationActor`，自身不引用任何枝叶网格——枝叶资产由 C++ 布局在运行时生成（`DYForestPresentationActor.cpp`）。
2. 两套已通过技术验证的叶簇候选 `BP_DYForestCanopy_Leafed`（窄叶）与 `BP_DYForestCanopy_WideLeaf`（宽叶）**均未进入主图**。
3. `BP_DYP03RuntimePresentation`（引用 `WBP_DYP03RuntimeCue`）属于 `Dev/M3/Runtime` 候选链，同样**不在主图引用清单**。

**印证审查意见：** 森林候选"未自动进入正式入口与最新游戏包"；2.4 倍直径实验失败未采纳——与主图现状一致。

**需 UE 核验：**
- 主图 `ForestPresentationActor` 实例的 BranchLayout/接触 opt-in/授权参数默认值。
- C++ `TryAcceptStaffContact → BeginForestPresentation → SetForestNormalizedGrowth → SubmitForestFinaleCompletion` 四接口在主图语境下的实际触发节点（不可静态证明）。
- ForestCanopy 两个候选蓝图与 `SM_DY_ForestBranch_Leafed/WideLeaf` 的网格参数，作为阶段 3 隔离候选的基础。

## 5. 主图当前使用的 Dev 资产汇总（阶段 4 集成清单基础）

正式主图当前是 **Dev 资产混合体**，以下 Dev 目录资产已进入主图：

| 资产 | 目录 | 状态 |
|---|---|---|
| `MI_DY_WoodFloor_Dev` | WoodFloor | 已入主图 |
| `SM_DY_WingScreen` | StageWings | 已入主图 |
| `SM_DY_FramePost_Source` + 2 材质 | FramePostAsset | 已入主图 |
| `SM_DY_FrameBeam_TopUV` | FrameBeamTopUV | 已入主图 |
| `BP_DYForestPresentation_Dev` | M3/Forest | 已入主图 |
| `MI_DY_P02BodyFit` | AlignmentFeedback | 已入主图 |
| `MI_DYReadability_P01/P03` | Readability | 已入主图 |
| `SFX_DevForestLeaves` | TheatreAudio | 已入主图 |

**未入主图的新候选**（集成时的优先考察对象）：

- `BP_DYKuafuPuppet_Fitted`（新夸父，含骨骼网格与三姿态）
- `BP_DYForestCanopy_Leafed` / `BP_DYForestCanopy_WideLeaf`（两套叶簇）
- `BP_DYP03RuntimePresentation`（P03 Runtime HUD/Cue 链）

## 6. 变更候选白名单建议（供阶段 2-4 立项）

| 阶段 | 候选变更 | 约束 |
|---|---|---|
| 2 | `MI_DY_P02BodyFit` 的隔离副本校准（新材质实例，不动原件） | 只在 Dev 隔离图验收 |
| 2 | 主图 `PuppetActor` 替换为 `BP_DYKuafuPuppet_Fitted` 的候选 | 待 UE 核验接线后单独批准 |
| 3 | 主图森林从 `BP_DYForestPresentation_Dev` 换为叶簇候选 | 须先通过同机位五态视觉验收 |
| 4 | 主图 Dev 材质升级为正式版 | 逐资产列出，保留回退点 |

## 7. 本轮未做

- 未修改任何 `.umap`/`.uasset`/`.cpp`（代码修复见 `DYInteractionComponent` 缺口修复记录，另行交付）。
- 未运行 UE 编辑器/PIE；未触发任何资产保存。
- 无法静态证明的节点接线已全部列入"需 UE 核验"，未凭命名猜测。
