# 阶段 A 机器核验总结：`BP_DYKuafuPuppet_Fitted` 装配与动画机制

> **日期：** 2026-10-17
> **方法：** ① UE 5.8.3 PythonScriptPlugin 属性探针（确认 UBlueprint 反射边界）；② `.uasset` name table 全量提取（列出蓝图引用的全部标识符，非关键词猜测）。
> **只读声明：** 未保存任何资产，未修改任何文件。
> **证据文件：** `D:/DYS_Build/Saved/Verification/UE_VERIFY_V5_SCS.json` + 本文本的提取清单。

## 1. Python 探针结论（确定性硬边界）

UBlueprint 在 UE 5.8 Python 中**只暴露极少成员**。探针逐一尝试 8 个成员，仅 `status` 可读（`BS_UP_TO_DATE`），以下全部"Failed to find property"：

```
simple_construction_script / inherited_components / construction_script /
ubergraph_pages / function_graphs / blueprint_type / parent_class
```

**结论：蓝图图数据（SCS 节点树、图页）不在 Python 反射面上。** 上轮"属性名可能不对"的假设被探针否定。节点级核验只能走图形界面。

## 2. Name table 全量提取的节点符号级发现

对 `BP_DYKuafuPuppet_Fitted.uasset`（162 KB）提取全部标识符后，装配与动画机制的结构清晰浮现：

### 2.1 SCS 新增组件：`KuafuMesh`

- `KuafuMesh` + `KuafuMesh_GEN_VARIABLE`（_GEN_VARIABLE 后缀 = **SCS 生成的组件变量**）
- `SkeletalMeshComponent`、`SK_DY_Kuafu_Refined`
- `ComponentClass` / `ComponentTemplate` / `BlueprintComponents`（SCS 节点序列化符号）

**回答阶段 A"Components 面板"项**：蓝图通过 SCS 新增名为 **KuafuMesh** 的骨骼网格组件（CDO 组件列表里没有它是因为 SCS 组件在实例化时创建）。

### 2.2 动画机制：AnimationSingleNode + 姿态切换

```
EAnimationMode::AnimationSingleNode + AnimationMode + AnimToPlay + AnimationData
SetAnimation + PlayRate
ApplyKuafuPose（自定义事件）+ GetPoseId + GetNormalizedValue
K2Node_CustomEvent_NormalizedValue / K2Node_CustomEvent_PoseId
OnControlChanged（委托）+ K2Node_AddDelegate / K2Node_RemoveDelegate / CreateDelegate
A_DY_Kuafu_Poses_Armature_A_DY_Kuafu_Reach / StrideBack / StrideMid（三姿态）
```

**回答阶段 A"三个姿态动画"项**：

1. **目标组件**：`KuafuMesh`（SkeletalMeshComponent）
2. **播放模式**：`AnimationSingleNode`（单动画节点模式），通过 `SetAnimation(AnimToPlay)` 切换
3. **播放条件**：Event Graph 里存在自定义事件 **`ApplyKuafuPose`**，参数为 `NormalizedValue` 与 `PoseId`，绑定到父类 `DYPuppetControlComponent` 的 **`OnControlChanged`** 委托（AddDelegate/CreateDelegate 符号在场，另有 RemoveDelegate 对应解绑）
4. **结束处理**：`PlayRate` 与 `ReceiveEndPlay` 符号在场；停止/结束的节点级细节仍需图形核验

### 2.3 显隐与投影

- `SetVisibility`、`SetCastShadow`、`AttachParent`、`RelativeLocation`
- `DYPuppetActor:Torso` / `DYPuppetActor:Head`（父类灰盒组件引用）

与上一轮发现互相印证：新旧组件的显隐/投影切换存在，具体互斥关系需图形核验。

### 2.4 Event Graph 事件面

`ReceiveBeginPlay` / `ReceiveEndPlay` / `ReceiveTick` / `ReceiveActorBeginOverlap`、`K2Node_IfThenElse`、`K2Node_VariableGet/Set`、`ExecuteUbergraph_BP_DYKuafuPuppet_Fitted`（Ubergraph 存在）。

**注意**：`ReceiveTick` 符号在场意味着 Event Graph 可能订阅了 Tick 事件——虽然 C++ 侧 `DYPuppetActor` 禁用了 Actor Tick（`bCanEverTick=false`），但 BP 的 ReceiveTick 是否实际连接节点需图形核验（空连接不产生开销）。

## 3. 阶段 A 清单的更新状态

| 阶段 A 清单项 | 本轮结果 |
|---|---|
| Components 面板组件层级 | **符号级回答**：SCS 新增 `KuafuMesh`（SkeletalMeshComponent）；与父类 Torso/Head 的附着关系待图形核验 |
| CS 创建/赋值/位置/显隐 | **符号级确认存在**（SetVisibility/SetCastShadow/RelativeLocation/AttachParent）；节点顺序待图形核验 |
| Event Graph 是否覆盖装配结果 | EG 存在（ExecuteUbergraph），含 SetVisibility 符号；是否覆盖待图形核验 |
| 三个姿态动画 | **符号级回答**：KuafuMesh + AnimationSingleNode + SetAnimation，由 OnControlChanged → ApplyKuafuPose(PoseId) 驱动 |
| 手杖与身形对齐 | 待 PIE/图形 |
| 重建/重开一致性 | 待 PIE/图形 |

## 4. 剩余图形核验清单（聚焦化）

1. 打开 BP 的 SCS 面板：确认 KuafuMesh 的附着父级与 Transform。
2. 打开 CS 图：确认 SetVisibility 的目标（隐藏 Torso/Head？还是显示 KuafuMesh？）与执行顺序。
3. 打开 Event Graph：确认 ApplyKuafuPose 的 PoseId→动画映射分支、SetVisibility 是否在运行时再次调用。
4. PIE 隔离关卡：真身可见、灰盒隐藏、姿态切换、手杖对齐。

以上 4 项完成后，阶段 A 的通过标准（`下一步执行安排.md` 阶段 A 五项）即可判定。

## 7. 第三轮机器核验（v6：SCS 模板路径 / Guide 初始显隐 / Timeline 实证）

方法：按 name table 证据以完整子对象路径加载 SCS 模板；主图加载态直接 introspect Guide actor 的初始显隐；TimelineComponent 实例枚举。原始数据：`UE_VERIFY_V6_TEMPLATES.json`。

### 7.1 B1 默认状态安全性——已实证

主图三个 Guide（StaticMeshActor_13/15/16）保存态 **`hidden_in_scene = true`（全部默认隐藏）**，组件层 visible=true（组件可见性与 Actor 隐藏独立）。**进入游戏时不会错误显示任何 Guide**——初始状态安全，运行时由 `ApplyReadabilityGuides` 按幕开启。阶段 B 清单"默认状态是否安全"项**实证通过**。

### 7.2 Timeline 实证（C3 的名称与长度项）

Stage 表现 actor 上有两个 TimelineComponent 实例：

| 组件名 | 长度（秒） | 加载态播放 |
|---|---|---|
| `时间轴` | 2.0 | false |
| `时间轴_0` | 6.0 | false |

与 name table 注释 "Dev-only linear timelines, **fixed-length 2/6 seconds**" 完全对应。推断（需图形核验确认归因）：2 秒对应杖落/接触表现（`ApplyDrop`），6 秒对应成林生长（`ApplyGrowth`）。加载态均未播放，符合"事件驱动启动"的预期。

### 7.3 SCS 模板子对象不可按名加载

`KuafuMesh_GEN_VARIABLE` / `DefaultSceneRoot_GEN_VARIABLE` 按 CDO 子对象路径加载返回 null——SCS 模板序列化位置与猜测不符（或为独立 package 内对象）。**Python 路径下 SCS 模板属性不可达**，`KuafuMesh` 的 Transform/可见性/动画模式具体数值归入图形核验（Components 面板 Details 一目了然）。此为 Python 侧第二个硬边界，与 §1 的反射边界一并定案。

### 7.4 更新后的剩余图形核验清单（聚焦到具体数值）

1. KuafuMesh 的 Details 面板：Skeletal Mesh 赋值、Relative Location/Rotation/Scale、Visibility/CastShadow、Animation Mode（预期 AnimationSingleNode）与 AnimToPlay 占位。
2. CS 图：SetVisibility/SetCastShadow 的目标组件与布尔值；执行顺序。
3. Event Graph：ApplyKuafuPose 的 PoseId 分支；"时间轴"/"时间轴_0" 分别由哪个事件启动（2s/6s 归因）、输出如何进 `SetForestNormalizedGrowth`。
4. PIE：阶段 A/B 通过标准判定。

## 8. 本文件结论

三轮机器核验（实例 introspect / name table / 模板与初始状态）已把 Python 只读路径推进到 API 硬边界（两处：蓝图图反射面、SCS 模板子对象），取得：装配与动画机制符号级全景、Stage 载体与全部配置、P03 调用链调用者、Guide 显隐控制者、Timeline 长度、Guide 默认安全。**剩余全部为图形核验（清单见 §7.4）与 PIE/人工验收。**

方法边界附注：

- Name table 提取列出的是**蓝图引用过的标识符集合**，不是执行顺序；"存在 SetAnimation 调用符号"不等于"运行时一定以预期参数调用"。
- SCS 变量命名（KuafuMesh）与 _GEN_VARIABLE 后缀是 UE 序列化惯例，可信度高但仍属保存态证据。
- 全部结论与既有约束一致：不据此修改任何资产，不把字符串级证据写成节点执行证据。

---

## 9. 阶段 B 机器核验：`BP_DYReadabilityPresentation` 的 Guide 显隐与 P03 调用链

方法：同 §2 的 name table 全量提取，对象为主图 Stage 表现载体 `BP_DYReadabilityPresentation.uasset`（957 KB——显著大于夸父 BP，含森林/杖/幕全部表现逻辑）。只读，未写任何资产。

### 9.1 Guide 显隐控制者确认（回答阶段 B 第一项）

- **`GuideP01` / `GuideP02` / `GuideP03` 三个变量存在**（对应主图三个共位 StaticMeshActor）
- **显隐逻辑集中在单一函数 `ApplyReadabilityGuides`**（`K2Node_FunctionEntry` 符号表明是一个函数图，非分散在 Event Graph 多处）
- `SetActorHiddenInGame` 在场——切换手段是隐藏而非移动
- `Act Index` / `ActCount` / `ActTitle` / `ShowActGuidance` / `ReceivePuzzleActivated` / `ReceivePuzzleResolved` 在场——**按幕序列状态驱动**，与 C++ 侧 `DYActSequenceSnapshot` 对接

**符号级结论**：三个共位 Guide 由 `ApplyReadabilityGuides` 统一按幕状态显隐（`SetActorHiddenInGame`），符合"按幕切换显示"的预期设计；共位本身有合理机制。节点级互斥正确性（是否漏显/漏隐）仍需图形核验 + PIE。

### 9.2 P03 调用链在 Event Graph 中完整在场（回答阶段 D 载体项）

四接口调用与 Token 校验符号**全部在该 BP 的 Event Graph 中**：

```
CallFunc_TryAcceptStaffContact_ReturnValue
CallFunc_BeginForestPresentation_ReturnValue
CallFunc_SetForestNormalizedGrowth_ReturnValue
CallFunc_SubmitForestFinaleCompletion_ReturnValue
CallFunc_IsResolvedTokenCurrent_ReturnValue / OwnsToken / UsedToken / CueToken
ReceiveStaffPresentationInvalidated（失效回调）+ ReceivePuzzleResolved
ApplyDrop / ApplyGrowth / CompleteGrowth / CheckForestSilhouette / CaptureStaffProjection / SampleStaffDrop
```

其中注释字符串 "Accept ONLY the original live native capture. Same UsedToken" 表明 BP 对重复/旧 Token 有显式防护逻辑——与 C++ 侧 Token 契约在 BP 层配合。**调用者是谁的问题已解决**：就是这个 BP 的 Event Graph。

**边界**：调用的执行顺序与条件分支仍需图形核验；边界行为（错误位置、旧 Token、Reset）需 PIE。

### 9.3 新注意事项：Event Graph 使用 Timeline

`K2Node_Timeline` / `GetTimelineLength` / `GetPlaybackPosition` / `SetNewTime` 在场。**若成林生长进度由 BP Timeline 驱动而非直接透传 Director 事件**，需要核验 Timeline 的推进与 `SetForestNormalizedGrowth` 的调用关系是否符合"Authored normalized progress"契约（C++ 注释明示 Progress 是作者 authored 值，不含谜题判断）。此项列为图形核验重点。

### 9.4 阶段 B 清单更新状态

| 阶段 B 清单项 | 本轮结果 |
|---|---|
| 定位三 Guide 显隐控制节点 | **符号级完成**：`ApplyReadabilityGuides` 函数 + `SetActorHiddenInGame` + 幕序列状态输入 |
| 切幕时只有预期 Guide 显示 | 待 PIE |
| 失败/Reset/重演/退出恢复 | 待 PIE（`ReceiveStaffPresentationInvalidated` 失效回调在场） |
| P02 Guide 网格/材质/参数 | **已确认**（§2.2：Cube + `MI_DY_P02BodyFit`） |
| 基于真实身形校准 | 依赖阶段 A 图形核验完成 |
| 隔离关卡验收 | 待人工 |

### 9.5 阶段 D 清单更新状态

| 阶段 D 清单项 | 本轮结果 |
|---|---|
| 定位真实接触入口及调用者 | **符号级完成**：`BP_DYReadabilityPresentation` Event Graph（§6.2） |
| Token 生成/传递/校验/失效 | 符号在场（IsResolvedTokenCurrent/OwnsToken/UsedToken/CueToken/Invalidated 回调）；运行时行为待 PIE |
| 四接口调用顺序与边界 | 待 PIE（节点在场已确认） |
