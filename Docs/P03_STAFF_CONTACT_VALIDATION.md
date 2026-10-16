# P03 接触契约小步：A 端 / 叙事地线验收记录

日期：2026-10-03 开始，2026-10-04 跨日核验
状态：**接触契约小步已实现并通过技术验证（48 Success / 0 Failed、三目标编译成功、原 35 M2 / 20 UI / 18 M3 冷读通过）。可见 P03 因果演出、落杖动画、树形几何与 Finale 结束态仍未实现。**
负责人：项目负责人（技术实现与验收）；Codex 负责实现与独立验收；WorkBuddy 仅整理文档。
依据：`Saved/Audit-2026-10-03-P03Contact/Supervisor-Results.md`、`Execution-Contract.md`、
`Baseline.json`、`ProtectedHashes-ForWorkBuddy.json`、`Automation/index.json`、`Automation-Initial/index.json`，
以及 `Build-Editor.log`／`Build-Editor-Final.log`／`Build-GameDevelopment.log`／
`Build-GameDevelopment-Final.log`／`Build-GameShipping.log`／`Verify-M2DevSlice.log`／
`Verify-M2UI.log`／`Verify-P03GeometryProbe.log`，以及本轮新增/修改源码只读核对。

> **本文件不是第三幕验收，也不是竞赛作品验收。** 本轮不设 P03 目标与容差、落杖/生长/超时数字；
> 不接成林、Finale、Skip、整局重启或新输入。**未做 Cook / Stage / Package，未做 GUI 与人工验收，不代签。**

> *永远不要以牺牲架构设计为代价追求功能；永远不要基于猜测进行权衡——必须与我确认。*

---

## 0. 本轮结论（先读这一段）

| 项目 | 状态 |
|---|---|
| 用户确认 | **A 端 ＋ 幕上叙事地线**（本轮明确） |
| Resolve 起始表现快照 | **已实现**（只在 live Resolve 事件捕获） |
| 一次性 Token 守卫接触接口 | **已实现**（读真实当前 A 端，不接受自报坐标） |
| 默认关闭 | **已实现**（`bEnableStaffContactPresentation = false`，现有 M2/M3 资产均未打开） |
| 自动化回归 | **48 Success / 0 succeededWithWarnings / 0 failed / 0 notRun** |
| 三目标编译 | **Editor / GameDevelopment / GameShipping 全部 Succeeded** |
| 冷读回归 | **M2 35 PASS ＋ UI 20 PASS ＋ M3 18 PASS**，均 0 error / 0 warning |
| 文档交接前原文件改动范围 | **122 项基线中 119 一致、3 改变、0 缺失**（仅 Director.h 与 Presentation.h/.cpp）；文档交接后另计，不混写 |
| 保护哈希 | **98 / 98 完好**，WorkBuddy 未改动任何非 Docs 文件 |
| **落杖动画 / 树形几何 / 林影** | **未实现** |
| **P03 Definition / 目标值 / 容差** | **未创建** |
| **Finale 结束态 / Skip / 整局重启** | **未实现** |
| **Cook / Stage / Package** | **未做** |
| **GUI / PIE 人工验收** | **未做，不代签** |
| 地线实际坐标与时长 | **仍待样本确认** |

---

## 1. 类职责（只读源码核实，不按旧类名猜测）

| 类 / 文件 | 职责 | 是否读 World |
|---|---|---|
| `ADYPuzzleDirector` | 唯一体验事实源。本轮**只增** `GetLightRigActor()` / `GetPuppetActor()` 两个只读访问器（`DYPuzzleDirector.h:54,57`），读取实际作者引用。`Director.cpp` 与 Evaluator **未改** | 是（既有） |
| `FDYStageResolvedPresentationSnapshot` | Resolve 起始快照：`bHasSnapshot` / `Token` / `PuzzleId` / `Light` / `Puppet` / `Projection` / `GroundLine`。**只在 live Resolve 事件捕获** | 值快照 |
| `FDYNarrativeGroundLineSnapshot` | 幕上叙事地线：`bIsValid` / `WorldAnchor` / `ScreenLocalZ`。注释明确是**作者在接收面上的线，不是后台实体地面** | 值快照 |
| `FDYStaffContactPresentationSnapshot` | 一次性接触快照：`bHasContact` / `Token` / `PuzzleId` / `Projection` / `ContactWorldPosition` | 值快照 |
| `UDYStaffContactLibrary` | **纯数据几何**。`CaptureNarrativeGroundLine()` 校验锚点必须位于**朝发光点的幕布表面**且在局部 Y/Z 边界内；`IsStaffAOnNarrativeGround()` 判定 A 端是否落在该地线 | **不读 World、不读像素、不读判定器** |
| `ADYStagePresentation` | 表现层持有者。Transient 运行态归 Presentation，**不写 CDO / Definition / 存档** | 是（既有职责） |

新增三个结构体按值只读；`StaffProjectionScreen` 与 `NarrativeGroundLine` 均为
`EditInstanceOnly` 且带 `EditCondition = "bEnableStaffContactPresentation"`。

---

## 2. 值快照与 Token 去重（本轮核心）

### 2.1 起始快照只在 live Resolve 捕获

- `HandlePuzzleResolved()`（`DYStagePresentation.cpp:426-431`）**先**调用
  `CaptureResolvedStaffPresentation(PuzzleId)`，**再**调用既有的 `ApplyResolvedPresentation(...)`。
  快照因此在旧 `ReceivePuzzleResolved` hook 之前就绪。
- 捕获前校验：开关打开、运行生命周期有效、Director 有效且同 World、
  `GetResolvedPuzzleSnapshot()` 的 `bIsResolved` 为真、`PuzzleId` 匹配、
  `IsResolvedTokenCurrent(Resolved.Token)` 为真。
- **同 Token 不重复捕获**：
  `if (ResolvedStaffPresentation.bHasSnapshot && ...Token == Resolved.Token) { return; }`
  ——注释写明「绝不用后来的动画/重复事件重建初始姿态」。
- 捕获时另外校验灯与偶的 `GetActorTransform()` 与快照中的 `WorldTransform` 一致，
  防止捕获已移动的对象。
- **late sync 不重建**：`SynchronizeFromDirector()`（`:284`）只走既有 `ApplyResolvedPresentation` 路径，
  **不调用** `CaptureResolvedStaffPresentation` ——冷启动 late-sync 只恢复表现，
  不会把后来的动画当成初始构图，也**不重放**接触事实。

### 2.2 一次性 Token 守卫接触

`TryAcceptStaffContact(const FGuid& Token)` 的完整接受条件（源码逐条核实）：

1. `IsStaffPresentationTokenCurrent(Token)`：开关打开 + 运行态有效 + Director 有效同 World
   + Token 有效 + 起始快照存在 + Token 与快照一致 + `Director->IsResolvedTokenCurrent(Token)`；
2. `!StaffContactPresentation.bHasContact` ——**同一 Token 只接受一次**；
3. 起始快照的 `Projection.bHasGeometry` 与 `GroundLine.bIsValid` 均为真；
4. `StaffProjectionScreen` 与 `NarrativeGroundLine` 有效且同 World；
5. **重新捕获当前真实几何**（`CaptureStaffProjection`），不接受调用者自报坐标；
6. 发光点、接收面变换、接收面局部边界与初始值逐一 `Equals(..., UE_DOUBLE_SMALL_NUMBER)`；
7. 地线 Actor 当前位置与快照锚点一致 ——**主灯/接收面/地线不得偷偷换构图**；
8. `IsStaffAOnNarrativeGround()` 为真 ——A 端实际投影落在固定地线上。

任一条不满足即 `return false`，**不产生接触事实**。

### 2.3 回调与重入安全

- 接触快照**在通知任何监听者前就已保存**：`StaffContactPresentation = Accepted;` 写在
  `ReceiveStaffContactAccepted(Accepted)` **之前**（源码注释：先消费再回调）。
- `ReceiveStaffContactAccepted` 是 `BlueprintImplementableEvent`（表现 hook）；
  `OnStaffContactAccepted()` 是**原生** `DECLARE_MULTICAST_DELEGATE_OneParam` 观察信号。
- 广播前**再次**校验 `IsStaffPresentationTokenCurrent(Token)`；
  回调之后**不做任何 mutation**（源码注释：监听器里的复位/销毁/重启保持完整）。
- 全部使用**栈上值副本**传递；回调内复位或销毁后，外层不写回旧证据。

### 2.4 非触地不接受

`IsStaffAOnNarrativeGround()` 要求同时满足：

- `Projection.bHasGeometry`、`Projection.Staff.bIsValid`、`GroundLine.bIsValid`；
- `Projection.EndA.Status == EDYStaffProjectionStatus::OnScreen`；
- 坐标非 NaN、`GroundLine.ScreenLocalZ` 有限；
- **对当前接收面重新验证地线**（`CaptureNarrativeGroundLine` 再跑一次）；
- 重新验证结果与保存值一致，且 `EndA.ScreenLocalPosition.Z` 与地线 Z 一致（仅数值 epsilon）。

**`OnScreen` 不等于触地。** 仅有 `OnScreen` 而不落在地线上，一律不接受。

### 2.5 缺失表现不撤销成功

- 捕获与接受都是**表现层**操作，成功事实始终由 Evaluator / Director 决定；
- 开关关闭、未进入运行生命周期、Director/Token 无效或未观察到 live Resolve 时，
  `GetResolvedStaffPresentationSnapshot()` 返回空结构；
- **已观察到合法 Resolve、但幕布/灯偶几何或地线引用缺失时**，仍保留
  `bHasSnapshot=true`、成功 Token / PuzzleId / 灯偶控制值，只有
  `Projection.bHasGeometry` 或 `GroundLine.bIsValid` 为 false；**不是整份快照为空**。
  `DefaultOffAndMissingGeometry` 直接断言了这一行为；
- 上述两条都**不会撤销已成立的判定成功**；
- `TryAcceptStaffContact` 失败只返回 `false`，不改变谜题状态；
- 过期 / 跨 Director / 重复 / 销毁后的回调一律拒绝，**成功事实不撤销**。

### 2.6 默认关闭与地图未变

- `bEnableStaffContactPresentation = false`（`DYStagePresentation.h:159`），
  注释写明「现有 M1/M2 资产保持其已验收的表现行为」；
- **现有 M2 / M3 资产均未打开新接入**，因此既有冷读结果不受影响；
- 本轮**没有修改任何 `.uasset` / `.umap`**，`Dev/M2` 与 `Dev/M3` 地图保持原样。

---

## 3. 实测证据（逐日志核对，均已独立复算）

### 3.1 自动化 —— 48 Success / 0 失败

`Automation-Initial/index.json`（`15.54.38`）与 `Automation/index.json`（`15.59.30`）**两轮完全一致**：

```
succeeded 48 | succeededWithWarnings 0 | failed 0 | notRun 0 | inProcess 0
逐项 state 复核：48 项全部 Success
```

- **原 40 项按 `fullTestPath` 全部保留**（含 `P03.Geometry.*` 6 项与 `P03.Foundation.*` 4 项）。
- **新增 8 项** `DengYingShanHai.P03.Contact.*`，源码 `DYStaffContactAutomationTests.cpp`（358 行）逐项对应：

| 测试路径 | 覆盖内容 |
|---|---|
| `ActualResolveAndCopy` | 真实 Director/Evaluator 成功事件 + 起始快照按值副本 |
| `OnScreenIsNotContact` | **`OnScreen` 不构成接触** |
| `ActualAExactlyOnce` | 真实 A 端**只接受一次** |
| `TokenLifetimeAndTeardown` | Token 生命周期、跨 Director 与 Director / Presentation 销毁后拒绝 |
| `DefaultOffAndMissingGeometry` | **默认关闭**属性、跨世界几何引用拒绝、几何缺失保留成功身份 |
| `FrozenReceiverEmitterAndLine` | 发光点/接收面/地线**冻结**（不得换构图） |
| `LateSyncAndReentrantReset` | late sync 不重建 + 回调内重入复位；没有测试路径重命名 |
| `TransformedGroundAndInvalidData` | 旋转/非均匀缩放地线、退化与 NaN 输入 |

- 测试使用真实 World / Actor / Staff、真实 Director / Evaluator 成功事件；
  **仅夹具中的数字、零 hold 与 Staff 位移是测试数据，不是 P03 体验目标或落杖动画**。
- 纯几何用例另验证旋转、非均匀缩放、边界、退化、NaN 与非接触。
- **既有噪声仍在**：`Automation.log` 有 **13 条** `Condition failed` Error（本机既有本地化 smoke-test，非本轮引入）。
  **不得声称整份日志零错误。** 项目 48 用例本身均 Success、无用例内警告。
- 既有 MSVC preferred-version 与引擎 `GetMovementBase` 弃用警告仍在。

### 3.2 三目标编译

| 日志 | 结果 |
|---|---|
| `Build-Editor.log` | `Result: Succeeded` |
| `Build-Editor-Final.log` | `Result: Succeeded`（第二轮：补充跨世界/销毁/真实默认值断言后重编） |
| `Build-GameDevelopment.log` | `Result: Succeeded` |
| `Build-GameDevelopment-Final.log` | `Result: Succeeded`（**最终**，对应补充断言后的最新源码） |
| `Build-GameShipping.log` | `Result: Succeeded` |

**三目标编译成功不等于打包通过**：本轮未做 Cook / Stage / Package，旧包不含本轮 C++。

### 3.3 冷读回归

| 日志 | 结果 |
|---|---|
| `Verify-M2DevSlice.log` | **35 PASS**，`Success - 0 error(s), 0 warning(s)` |
| `Verify-M2UI.log` | **20 PASS**，`Success - 0 error(s), 0 warning(s)` |
| `Verify-P03GeometryProbe.log` | **18 PASS**，`Success - 0 error(s), 0 warning(s)` |

M3 仍为 **18 PASS**——本轮**未修改地图**，M3 冷读项数不变，这与「地图未变」一致。

### 3.4 文档交接前范围审计（非最终文件数）

`Baseline.json` 共 **122** 个 Source/Config/Content/Scripts/Docs 原文件：

```
same 119 | changed 3 | missing 0
  CHANGED Source/DengYingShanHai/Public/Puzzles/DYPuzzleDirector.h
  CHANGED Source/DengYingShanHai/Public/Stage/DYStagePresentation.h
  CHANGED Source/DengYingShanHai/Private/Stage/DYStagePresentation.cpp
```

- 与监督报告一致。**文档交接前仅 3 个原文件改变**（都在本轮修改白名单内）。
- **仅新增 4 个源码**：`DYStaffPresentationTypes.h`、`DYStaffContactLibrary.h/.cpp`、
  `DYStaffContactAutomationTests.cpp`。
- **无资产、配置、脚本修改**；Evaluator、Environment、`Config`、`Build.cs`、
  输入 / 镜头 / P02 参数 / 15 Hz 均未改；已有测试未改。

### 3.5 保护哈希核对（本文档独立复算）

`ProtectedHashes-ForWorkBuddy.json` 共 **98** 项非 Docs 原/新产品文件：

```
protected total 98 | intact 98 | changed 0 | missing 0
```

**WorkBuddy 未改动任何受保护文件。** 该清单**不含任何 `Docs/` 路径**，
因此本轮三份 Docs 的写入不与保护范围冲突。
最终范围审计由 Codex 在文档交接后另做——**不把 Docs 修改混称为零变化**。

Git 状态（Codex 记录）：HEAD `dda43f2c8970c10680173387b963d1c730649f06`，暂存区为空。
本轮未执行 Git 写操作、未 commit、未删除、未覆盖原未提交改动。

### 3.6 文档交接后最终范围（Codex 独立复核）

122 个原文件：**117 一致 / 5 改变 / 0 缺失**。五项变化为三份原源码
（Director.h、Presentation.h/.cpp）及两份原文档（P03 接入计划、几何验收记录）；
另新增 **4 个源码 + 本验收文档**。非 Docs 的 98 项保护文件仍 **98 完好 / 0 变化**。
最终文件 SHA256 与路径见 `Saved/Audit-2026-10-03-P03Contact/FinalScopeAudit.json`。

WorkBuddy 提交稿完整保留在本轮 `Backup/WorkBuddy-Submitted/`；Codex 已按实际源码修正
缺失几何时保留成功身份、测试覆盖归属、历史/当前统计和旧 M2 同步 hook 的表述，
没有借文档复核改变任何产品代码或批准新的玩法/演出参数。

---

## 4. 语义边界（不得被后续文档稀释）

1. **这里的「接触」是几何一致，不是实体碰撞。**
   它是「幕上中心射线预测点」与「作者配置的叙事地线」在局部 Z 上的一致，
   **不是**实体碰撞检测、**不是**阴影像素识别、**不是**真实阴影可见性证明。
2. **`OnScreen` 不等于触地、不等于可见性、不等于成功。**
   `P03.Contact.OnScreenIsNotContact` 专门锁定这一点。
3. **接触是纯表现事实，不参与谜题判定。**
   成功只由 Evaluator / Director 决定；接触失败或缺失**不撤销**成功。
4. **本轮没有落杖动画、没有生长、没有树形几何、没有林影。**
   接触被接受后，**没有任何可见演出被触发**——Blueprint hook 存在但未接入表现资产。
5. **地线是作者配置项，本轮未制作或保存关卡 Actor。**
   现有 Dev/M2、Dev/M3 资产未配置地线、未启用接入，因此本轮**没有交付可操作的接触演出关卡**；
   自动化中已在真实 World/Actor 的夹具内走通接口，不能把「未接关卡」说成「接口没有运行验证」。
6. **不设任何 P03 数字。** 本轮地线只使用 `UE_DOUBLE_SMALL_NUMBER` 数值 epsilon，
   **不是**新增谜题容差。
7. **幕后实体点与幕上投影点是两处位置，不能混用。**
   `ContactWorldPosition` = `Projection.EndA.WorldPosition`，是幕布接收表面上的投影点；
   实体杖尖在 `Projection.Staff.EndAWorld`。后续真实树形投影必须让树形几何置于灯与幕之间，
   用同一主灯将其根部投影到该幕上接触点；不能把幕上点直接当作幕后树形实体的生成位置。

---

## 5. 未完成 / 后续（不代签）

| # | 项目 | 状态 |
|---|---|---|
| U1 | **落杖动画** | **未实现** |
| U2 | **树形几何 / 林影** | **未实现**；无 Forest Actor |
| U3 | **地线 Actor 实例** | **未制作或保存**；正式地图无实例 |
| U4 | **P03 Definition / 目标值 / 容差** | **未创建**；本轮刻意不设任何数字 |
| U5 | **落杖 / 生长 / 超时节奏** | **未定**，仍待样本确认 |
| U6 | **Finale 结束态 / Skip / 整局重启** | **未实现**；`RestartExperience()` 未批准 |
| U7 | **两种新环境态**（`FinaleReady` / `ForestComplete`） | **未实现**；`EDYStageEnvironment` 仍为 3 态 |
| U8 | **Cook / Stage / Package** | **未做**；三目标编译不等于打包通过，旧包不含本轮 C++ |
| U9 | **GUI / PIE 人工验收、Shipping 实际运行** | **未做，不代签** |
| U10 | 音效、镜头、正式美术、干净目标机、其他机器兼容 | 未做 |
| U11 | 地线实际坐标 | **待样本确认**，不凭猜测定为正式配置 |

> **地线实际位置、P03 目标/容差、落杖/生长/超时节奏、Skip 与整体重启入口，
> 均不能凭猜测定为正式配置。** 下一步先在独立 `Dev/M3` 制作**可展示的落杖构图样本**，
> 核对实际 A 端从成功构图移动到幕上地线，再接**同一点**的真实树形投影。
> 先用样本让用户确认，**不要求用户盲填工程数字**。

---

## 6. 回退

- 回退**只按单文件恢复**本轮 `Backup/` 中的备份；
- **不** `reset`、**不** `checkout`、**不**清理工作树；
- 新增的 4 个源码文件**只有在用户明确要求回退时**才移除；
- 本轮未执行 Git 写操作，改动以文件与备份形式留存。

## 7. 风险

| 风险 | 说明 |
|---|---|
| 地线无关卡实例 | 当前 Dev 资产未配置地线/动画，因此尚无可操作演出；真实 Actor 自动化已验证接口，但不替代可见验收 |
| 表现与判定分离可能被误用 | 有人可能把 `TryAcceptStaffContact` 当成成功判定；源码注释与本文件 §4.3 已明确禁止 |
| 现有 M2 hook 语义 | 本轮**只**保证新快照在旧 `ReceivePuzzleResolved` 之前就绪；**未宣称全类所有旧 hook 已去重** |
| 数值 epsilon 被当容差 | 源码注释已标注 `UE_DOUBLE_SMALL_NUMBER` 不是谜题容差；正式容差仍待确认 |
| 三目标编译被当打包通过 | 旧包不含本轮 C++，不得替代新功能打包证明 |
| 13 条本地化 Error | 不得声称整份自动化日志零错误 |

## 8. 下一步（须先经用户确认，不自行决定）

1. 在独立 `Dev/M3` 制作**可展示的落杖构图样本**（这是下一步的**唯一**当前动作）；
2. 核对实际 A 端能否从成功构图移动到幕上地线，用**样本**请用户确认地线位置与接触构图；
3. 用户确认后再接**同一点**的真实树形投影（同灯真实林影）；
4. 之后才讨论 P03 目标/容差、落杖/生长/超时节奏与 Finale 结束态。

## 9. 状态

**部分完成**：A 端＋幕上叙事地线的**底层接触契约**已实现并通过技术验证；
落杖动画、树形几何、林影、P03 Definition、Finale 结束态、Cook/Stage/Package 与人工验收均未完成。
本文档不构成第三幕或竞赛作品验收，**未代签任何人工确认**。

AI 使用记录：Codex 负责源码实现、三目标编译、48 项自动化与冷读验收、范围与保护哈希审计；
WorkBuddy 本轮先只读核对证据，再按白名单整理本文档。**不冒充已完成赛事 AI 申报。**
