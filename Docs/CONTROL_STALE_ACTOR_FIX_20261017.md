# 修复记录：被控 Actor 失效后的操纵态清理缺口

> **修订 2：** 2026-10-17（按《灯影山海_本轮修改审查意见.md》完成四项修正后更新）
> **依据：** 《灯影山海_审查意见总汇_修订版.md》第 5 节 + 本轮修改审查意见
> **性质：** 最小修复。只改状态清理与事件契约 + 防重复退出通知；未重构交互组件，未改谜题数值/容差/保持时间/15 Hz 等任何既有规则。

## 验收记录（按审查意见推荐格式）

| 字段 | 值 |
|---|---|
| Task / Revision | `M1-Control-StaleActorCleanup / Run2` |
| Git 状态（三类区分） | **本地已提交**：`master@dda43f2c`（M2 slice，2026-10-02）；**本地未提交**：本次修复的 2 改 3 新增文件（见 §2）；**已推送公开 GitHub**：无——本地仓库 `git remote -v` 为空（无远端），公开仓 `main@b5ed7c0` 与本地 `dda43f2c` 是两条不同提交线，**公开仓当前不含本次修复** |
| Engine / Toolchain | UE 5.8.3（`EngineAssociation: 5.8`），MSVC 14.51.36260（非首选版本告警，与仓库既有告警一致），Windows SDK 10.0.26100 |
| World / Map | 无地图依赖（瞬态游戏世界自动化测试） |
| Asset / Package | `NOT_PACKAGED`（未打包；Development/Shipping 包验收另行执行，不沿用旧包结果） |
| Test | `Automation RunTests DengYingShanHai`（**164 项全量，PASS**，日志 `FullRegression3.log`） |
| Result | **164/164 PASS**（161 项既有 + 3 项本次新增） |
| Evidence | `D:\DYS_Build\Saved\Logs\ControlTest7.log`（定向 3 项）、`FullRegression3.log`（全量 164 项）、`FullRegression2.log`（第 1 轮全量，暴露定时器测试缺陷） |
| Rollback | 还原 `DYInteractionComponent.h/.cpp` + 删除 2 个新测试文件即可完整回退；不影响任何资产与地图 |

## 1. 缺陷描述

`UDYInteractionComponent::EndActiveControl()` 在 `ActiveControlledActor.Get()` 返回空（被控 Actor 在操纵中被销毁，弱引用失效）时直接 `return`，**跳过** `OnControlStateChanged.Broadcast(actor, false)`。而 `ADYStageOperatorPawn::HandleControlStateChanged` 正是靠该广播调用 `ADYStagePlayerController::SetManipulationMode(false)` 切回探索模式。

后果：操纵中 Actor 被销毁后，Pawn 卡在操纵输入上下文——玩家按 E（重新请求操纵）只会反复失败，无法自行恢复探索态。`EndPlay`/复位路径能兜底清理，但常规游玩路径无出口。

## 2. 修复内容（精确文件与行为）

| 文件 | 改动 | 状态 |
|---|---|---|
| `Source/DengYingShanHai/Public/Interaction/DYInteractionComponent.h` | 新增私有成员 `bool bPendingControlExitNotify = false`；测试 seam 新增 `HasActiveFocusTimer` | 本地修改 |
| `Source/DengYingShanHai/Private/Interaction/DYInteractionComponent.cpp` | ① `EndActiveControl()`：无待通知即返回守卫；弱引用失效分支清理残留、广播 `(nullptr,false)` 恰好一次、恢复焦点；② `ToggleControl()`：进入控制置位标志；开放会话分支 `IsValid() || bPendingControlExitNotify`；③ `UpdateFocusedActor()`：定时器回调里自动收尾 | 本地修改 |
| `Source/DengYingShanHai/Private/Tests/DYControlStaleActorAutomationTests.cpp` | **新增** 3 个自动化测试（覆盖路径见 §3） | 本地新增（未提交） |
| `Source/DengYingShanHai/Private/Tests/DYControlExitRecorder.h` | **新增** 测试专用广播记录器 | 本地新增（未提交） |

契约要点：每次成功 `BeginControl` 恰好对应一次退出广播（正常退出用真实 Actor 指针；Actor 已销毁时用 `nullptr`）；重复 `EndActiveControl()` 不产生重复广播；`FocusDistance=700` 等全部数值不变。

## 3. 自动化测试与覆盖边界（如实标注）

| 测试 | 复现路径 | 覆盖的路径 | **不覆盖** |
|---|---|---|---|
| `StaleActorExitNotify` | 进入操纵 → 销毁被控 Actor → 再按 E（"再请求操纵"） | `ToggleControl` 触发的清理；重复结束不重复广播；清理后组件可用 | 不声称覆盖 `EndPlay`/复位生命周期 |
| `StaleActorDirectEnd` | 进入操纵 → 销毁 → 直接 `EndActiveControl()`（与 `EndPlay`/复位同形的调用） | 直接结束契约（null 参数、恰好一次） | **不等于**真实 `EndPlay` 已测 |
| `StaleActorTimerDrivenCleanup` | 进入操纵 → 销毁 → **不调用组件方法**，按引擎帧循环语义推进 `GFrameCounter` + `TimerManager::Tick`，让**真实定时器**观察失效会话 | 定时器驱动的自动收尾（`UpdateFocusedActor` 定时器分支）；后续帧不重复广播；清理后可再次操纵 | PIE/真人键鼠 |

**测试实现要点（供复核）：**

- 瞬态世界无 GameMode → `UWorld::BeginPlay()` 不分发 actor BeginPlay → 测试用引擎真实分发路径 `Actor::DispatchBeginPlay()`。
- 灯的 `LightControl::BeginPlay` 会沿轨道重定位灯（`SetNormalizedValue → SetActorLocation`）→ fixture 用灯的**实际 post-BeginPlay 位置**摆放操作者与相机。
- `FTimerManager::Tick` 有**同帧去重**（`HasBeenTickedThisFrame`，TimerManager.cpp:1136）→ 测试按生产帧循环语义先 `++GFrameCounter` 再 `Tick(0.2s)` × 6 帧（1.2 s，覆盖 0.1 s 定时器多个周期，含浮点余量）。
- seam 新增 `HasActiveFocusTimer` 作为前置断言，防"定时器未武装的空转通过"。

## 4. 订阅者空指针契约核查（`(nullptr, false)`）

| 订阅者 | 实现 | 结论 |
|---|---|---|
| `ADYStageOperatorPawn::HandleControlStateChanged` | 只读 `bIsControlling` → `SetManipulationMode`，不解引用 Actor | **安全** |
| `ADYInteractionHUD::HandleControlChanged` | 忽略参数，`RefreshInteraction()` 经 `IsControlling()` 重算 | **安全** |
| Blueprint 侧订阅（若有） | 绑定点为 UFUNCTION，蓝图可挂同名事件 | **需 UE 核验**：逐个检查主图/Dev 蓝图对 null 的处理 |

## 5. 构建与回归（按审查意见修正后的执行要求）

**构建路径结论（修正第 1 轮"必须在原中文路径构建"的表述）：**

- 原中文路径 `D:\灯影山海` 直接构建失败（MSVC c1xx 非 ASCII 路径 C1083）；junction 会被 UBT 解析回真实路径，同样失败。
- **现行方案（审查意见确认的方向）**：英文路径隔离副本 `D:\DYS_Build` = Source + Config + .uproject + **完整 Content（233 MB）**——本轮已补齐 Content，构成完整工程副本。
- 不为单一路径通过而改动全局编译器/SDK/引擎环境。中文路径兼容问题在完整副本验证之后另行决定是否处理。

**回归结果（真实数据，非预期值）：**

| 轮次 | 环境 | 结果 | 说明 |
|---|---|---|---|
| 第 1 轮 | 沙箱（缺 Content） | 163 项：157 PASS / 6 FAIL | 6 项失败均因资产加载为 null（`InputContract`/`ClassDefaults`/`OperatorComponents`/`MenuButtonFontConsistency`/`SavedBlueprint×2`）；当时**未**预设它们必然通过，仅作初步归因 |
| 第 2 轮（Run2） | **完整工程副本** | **164 项：164 PASS / 0 FAIL** | 第 1 轮 6 项全部转绿，初步归因得到证实；同时暴露并修复了第 1 轮新增定时器测试自身的两个缺陷（见 §6） |

命令：`Build.bat DengYingShanHaiEditor Win64 Development -project="D:/DYS_Build/DengYingShanHai.uproject" -WaitMutex -NoUBA` → `Result: Succeeded`；`UnrealEditor-Cmd.exe … -ExecCmds="Automation RunTests DengYingShanHai" -TestExit="Automation Test Queue Empty" … -NullRHI` → `164 tests performed`，0 FAIL。

## 6. 第 2 轮新增测试的开发过程（失败如实保留）

`StaleActorTimerDrivenCleanup` 首两轮**失败并被如实记录**（`FullRegression2.log` / `ControlTest2-4.log`），根因两个：

1. 瞬态世界无 GameMode，`World->BeginPlay()` 不分发 BeginPlay → 定时器未武装（用 `DispatchBeginPlay` 修复）；
2. `FTimerManager::Tick` 的同帧去重 + 0.1 s 浮点比较边界 → 定时器武装了但从未触发（用帧计数推进 + 0.2 s 步长修复）。

**教训**：与审查意见一致——"不预先把失败判定为必然通过"同样适用于新测试本身；诊断过程（NextTick 探针、WorldTime 输出）留存于 `ControlTest5/6.log`。

## 7. 仍待人工验收（NEEDS_HUMAN_REVIEW，不互相代签）

1. **UE PIE**：输入映射、镜头、准星、焦点与探索态恢复的实际表现。
2. **真人键鼠**：真实 E 键进入/退出、被控对象销毁场景下的玩家体验。
3. **Development / Shipping 包**：本轮 `NOT_PACKAGED`；打包验收须在新集成版本上执行。
4. **Git 同步**：本地修改是否提交、是否建立远端并推送——由作者决定；在此之前公开仓不含本修复。
