# M2 VALIDATION｜“逐光成形”协同控制 Dev 切片

建立日期：2026-10-02  
负责人：项目负责人  
地图：`/Game/DengYingShanHai/Dev/M2/Maps/LV_M2PuzzleLab`  
数据：`/Game/DengYingShanHai/Dev/M2/Data/DA_DY_P02_ChaseForm`  
状态：**M2-A 协同判定与 M2-B 最小表现边界已完成；聚焦射线长度缺陷已修复；Dev 状态文字反馈小步已实现并通过独立验收（Editor Development 构建成功、全项目 Automation 25/25、Shipping 目标编译 7/7、普通 `-game` 真实键鼠五状态闭环与成功后 R 复位均已验证）；Dev/M2 可读性布局小步已由用户批准并实施（见 §0.8），实心挡光夹具已迁移、基本双空间可见性恢复；用户已于 2026-10-03 就该布局给出**有限签收**「看清了，操作正常」（见 §0.9），**不等于 §5 的 11 项逐项人工检查通过**。中文 UI 方案 B **已批准并实施，技术验收完成**（见 §0.10，30/30 项目测试、20 UI 冷读、35 地图冷读、三目标编译、Development 与 Shipping 完整技术包、真实 RHI 键鼠闭环），**等待用户签收 UI 布局与措辞**。正式美术、最终主地图接入、音效节奏、首次玩家盲测与 §5 的 11 项人工验收**仍未完成**。**

> 最高优先级限制：*永远不要以牺牲架构设计为代价追求功能；永远不要基于猜测进行权衡——必须与用户确认。*

## 0. 聚焦可发现性阻塞项修复（2026-10-02）

监督复测确认：出生点原地对准灯具按 `E` 无响应；向前约 0.9 秒后成功，日志出现 `Entered Dev Manipulate input mode at priority 10`。`D` 移灯与操纵态 `R` 复位均正常，故碰撞、输入与状态链无缺陷。

根因是 `FocusDistance` 同时被当作角色半径和相机射线长度：角色距灯约 515 cm（< 700），但相机经 360 cm 臂长后移，相机到灯超过 800 cm，700 cm 的射线提前耗尽。

修复只分离两项语义，`FocusDistance` 仍为 700 cm 角色真实半径：射线长度改为「相机到角色偏移 + `FocusDistance`」，命中后再以「候选到角色 <= `FocusDistance`」门控。只改 C++、自动化测试与文档，**未触碰任何 `.uasset`、地图、灯位、PlayerStart、亮度、材质与 15 Hz 判定**。

实现要点：

- 唯一的聚焦判定实现在私有 `UDYInteractionComponent::EvaluateFocus`，顺序为
  trace → 接口检查 → 半径门控 → `CanBeginControl` → `SetFocusedActor`；`UpdateFocusedActor` 取得视点后调用它；
- 自动化测试通过 `FDYFocusAutomationSeam` 友元访问该私有函数，并用组件自身的
  `GetFocusedActor()` 断言结果，不新增任何 public、UFUNCTION 或 BlueprintCallable 入口；
- 聚焦诊断只在 `-DYDebug` 下启用，整段位于 `#if !UE_BUILD_SHIPPING` 内，Shipping 编译期完全剔除。
  规范描述见 `TECH_SPEC.md` 的「聚焦诊断」小节。

### 0.1 本项的验证结果（2026-10-03）

- Editor Development 构建成功：`Build.bat -NoUBA`，最终增量 4/4 成功；
  产物 `Binaries/Win64/UnrealEditor-DengYingShanHai.dll`，641,024 字节，时间 2026-10-03 02:08:43；
- MSVC 14.51.36260 高于 UE 5.8.3 首选 14.50，Unreal Build Tool 给出非首选版本警告，
  属本机既有环境提示，不归因于本轮代码；
- 全套自动化最终报告 `Saved/Automation/M2-Focus-FinalFull/index.json`：
  **16 succeeded / 0 failed / 0 warnings / 0 errors**，逐项 JSON 的 `state` 已逐一核对，
  未只依据进程退出码；
- `RuntimeTrace` 曾因测试 World 缺少 `InitializeActorsForPlay` 而失败，表现为直接调用
  `_Implementation` 为 true 而 `Execute_` 分发为 false。按 UE 5.8 官方 `ActorTestSpawner`
  模式补齐后，单项报告 `Saved/Automation/M2-Focus-RuntimeWorldInit/index.json`
  为 1 Success / 0 error / 0 warning；
- 该测试在真实世界的真实碰撞中证明三件事：相机后移时仍能聚焦 700 cm 内的灯、
  前方存在 Visibility 遮挡物时不能聚焦、可见但距角色超过 700 cm 时被半径门控拒绝。

### 0.2 `-DYDebug` 运行观察

以 `-game -DYDebug` 加载 `/Game/DengYingShanHai/Dev/M2/Maps/LV_M2PuzzleLab` 成功进入 Play，
无输入首帧日志样例：

```text
FocusDebug ViewLocation=(-900.0,-210.0,98.2) PawnLocation=(-900.0,-210.0,98.2) TraceLength=700.0 HitActor=None Controllable=0 PawnToCandidate=0.0 WithinReach=0 CanBeginControl=0 FocusedActor=None RejectReason=NoHit
```

该样例为无输入首帧，`HitActor=None`，**不构成「出生点对准灯按 `E`」的人工验证**。
命中、遮挡与超距三种结果由 `RuntimeTrace` 证明；人工 PIE 复核仍未完成，见第 5 节。

### 0.3 Shipping 编译期剔除验证（2026-10-03，监督最新复验）

监督以**最新代码**实际编译 Win64 Shipping：

```text
Build.bat DengYingShanHai Win64 Shipping -Project=... -NoUBA -WaitMutex
  → 7/7 Succeeded，退出码 0
  → 证据：Saved/Audit-2026-10-03-M2Flow/Supervisor-Shipping.log
```

产物 `Binaries/Win64/DengYingShanHai-Win64-Shipping.exe`：

| 项 | 值 |
|---|---|
| 大小 | 165,980,160 B |
| 时间 | 2026-10-03 12:14:13 |
| SHA-256 | `BCD53D5636BD319B5590D0D4DECD16BE85885108A4F32512C707068EDD3A1A29` |

**UTF-16 二进制字符串核验**：

| 字符串前缀 | Development DLL | Shipping EXE |
|---|:---:|:---:|
| `FocusDebug ViewLocation=` | 有 | **无** |
| `InteractDebug ControlToggle` | 有（4 处） | **无** |
| `InputDebug InteractStarted` | 有 | **无** |
| `Aim at the lamp`（HUD 文案） | 有 | **有** |
| `ADYDevInteractionHUD` | 有 | **有** |

**结论（准确表述）**：

- 三类**调试诊断**已确认在 Shipping 编译期完全剔除；
- **不能据此说「HUD 类整体剔除」**：`Aim at the lamp` 与 `ADYDevInteractionHUD`
  字符串在 Shipping EXE 中**仍然存在**。这是因为 `HUDClass` 的赋值位于
  `#if !UE_BUILD_SHIPPING` 内，Shipping 下**默认 GameMode 不挂载该 HUD**，
  但类与文案本身仍被链接进二进制。
  因此只能说：**默认 GameMode 不挂载 Development HUD**，不能说 HUD 已被整体剔除。

**边界**：以上仅为 **Shipping 目标编译验证**，**不是 Cook、不是 Stage、不是可分发打包**，
也不代表 M2 Windows Development 包已Cook 或打包。正式打包仍需等待人工验收通过后执行。

### 0.4 Development HUD 与真实按键验证（2026-10-03）

新增 `ADYDevInteractionHUD`（`Public/UI` + `Private/UI`），并由 `DYStageGameMode` 在
`#if !UE_BUILD_SHIPPING` 下设置 `HUDClass`。它只读取
`UDYInteractionComponent::GetFocusedActor()` 与 `IsControlling()`：

- 画面中心准星：**白色 = 未聚焦**，**绿色 = 可操作**；
- 简短提示：`Aim at the lamp` / `[E]  interact` / `A / D  adjust   E  release   R  reset`；
- **提示暂用 ASCII 英文字串**：本构建的 Dev 字体未验证中文字形，正式美术 UI 后续替换；
- HUD 不做世界扫描、不复制判定、不控制 POV、不改相机/地图/灯位/700 cm/15 Hz，不加插件、不依赖任何 `.uasset`。

按键级诊断同样受 `!UE_BUILD_SHIPPING` + `-DYDebug` 双重门控：

- `ADYStageOperatorPawn::HandleInteractInput`（`ETriggerEvent::Started`，即真实输入触发）输出
  `InputDebug InteractStarted=1 FocusedActor=%s IsControlling=%d`；
- `UDYInteractionComponent::ToggleControl` 输出
  `InteractDebug ControlToggle requested action=...`。该函数不一定只由物理 E 调用，
  因此文案为 `ControlToggle requested`，不声称收到物理按键。

**独立 `-game` 实测（非 PIE）**，证据 `Saved/Audit-2026-10-03-InputE/Supervisor-HUD-Final.log`：

```text
未瞄准：InputDebug InteractStarted=1 FocusedActor=None IsControlling=0
        InteractDebug ControlToggle requested action=Rejected reason=NoFocusCandidate
瞄准灯：InputDebug InteractStarted=1 FocusedActor=DYLightRigActor_1 IsControlling=0
        Entered Dev Manipulate input mode at priority 10.
        InteractDebug ControlToggle requested action=EnterManipulate Candidate=DYLightRigActor_1
释放：  InputDebug InteractStarted=1 FocusedActor=None IsControlling=1
        InteractDebug ControlToggle requested action=Release FocusBefore=None ActiveAfter=0
```

- 站立不动、**无需角色前进**，准星瞄准灯后按 E 即进入操纵；
- 监督者另行观察：`D` 使灯位`Current` 由 `0.150` 变为 `0.470`，`R` 复位回 `0.150`，`E` 正常释放。
  该组数值来自监督者的独立观察，未在上述日志中逐行记录；
- 由此确立区分：**输入是否送达**由 `InputDebug` 判断，**是否被聚焦门控接受**由
  `InteractDebug` 的 `reason` 判断。不得由 `Entered Dev Manipulate` 缺失推断「用户没按 E」。

**无 `-DYDebug` 的普通模式实测**（证明诊断门控有效，正常启动不刷调试日志）：

证据 `Saved/Audit-2026-10-03-InputE/Supervisor-HUD-Normal.log`（未使用 `-DYDebug`，
日志中 `InteractDebug` 与 `FocusDebug` 均为 0 次）：

```text
Entered Dev Manipulate input mode at priority 10.        （E 进入操纵）
Puzzle P02_ChaseForm reset to its authored Dev baseline.  （R 复位谜题）
Restored Explore input mode.                              （E 释放操纵）
```

画面证据（截图目录
`C:/Users/lenovo/.codex/visualizations/2026/09/30/01a0f245-1d70-7ba1-9b69-e6db6a9b7948/`）：

| 截图 | 证明内容 |
|---|---|
| `HUD_Normal_Green.png` | 画面中心**绿色**准星 + `[E] interact`，灯具可见 |
| `HUD_Normal_Control.png` | 操纵态**白色**准星 + `A/D adjust  E release  R reset` |
| `HUD_D_adjust.png` | `D` 调整灯位 |
| `HUD_R_reset.png` | `R` 复位灯位 |

**构建与回归**：Editor Development 构建退出 0；
`Saved/Automation/M2-HUD-Final/index.json` 为 **16 succeeded / 0 failed / 0 warnings**，
逐项 `state` 均为 `Success`。

**仍未完成**：全 M2 人工验收单（含幕布因果、 Holding、ChaseAwakened 可读性、
静音可完成、结束界面等）尚未逐项执行；Windows Development 包（Cook/打包）未开始。

### 0.5 独立只读重载与P02 协同链路实测（2026-10-03）

**独立只读重载**（非脚本推导）：

```text
UnrealEditor-Cmd -run=pythonscript -script=Scripts/Verify-M2DevSlice.py
  → 退出码 0，DY_M2_VERIFIED，33 项断言全 PASS / 0 FAIL
  → 证据：Saved/Audit-2026-10-03-M2Flow/ReadOnlyReload-M2.log
```

无写操作证明：执行前后 6 个文件 SHA-256逐一比对完全一致
（`LV_M2PuzzleLab.umap`= `8236ec5f…`、`DA_DY_P02_ChaseForm.uasset`=`ac88a48d…`、
`BP_DYStagePresentation.uasset`=`245ffb02…`、`BP_DYStageEnvironment.uasset`=`3159cd2f…`、
`Verify-M2DevSlice.py`=`e7a0b4cc…`、`Create-M2DevSlice.py`=`2f434add…`）；
git 仍 28 项、HEAD `dda43f2`、暂存 0；今日 uasset/umap 写入 0。
重载脚本仅调用 `load_asset` / `load_class` / `get_editor_subsystem` / `log`，无写操作。

**P02 协同链路实玩实测**（`-game` 独立运行，证据
`Saved/Audit-2026-10-03-M2Flow/Supervisor-Flow.log` 与同批截图）：

| 阶段 | 实测结果 |
|---|---|
| 仅灯到位 | 灯 `0.714` 有效，偶 `0.150` → Holding 0、State=Searching（**不误完成**） |
| 走近皮影 | 玩家 `W` 走到 `(184.4, -390.5, 98.2)`，瞄准躯干后 `HitActor=DYPuppetActor_1`、`WithinReach=1`、`CanBegin=1`，真实按 E 成功进入 |
| 进入Holding | 偶 `0.782`、灯 `0.714` → Holding 0.13 / 1.25 |
| Holding 中断 | 偶退到 `0.597`（StrideMid）→ 重回 Searching、Holding 0 |
| Resolve | 灯 `0.714`、偶 `0.794` → State=Resolved、ResolveCount=1、Holding 1.27；日志 `Puzzle P02_ChaseForm resolved exactly once.` **全文仅 1 次** |
| 完成后锁定 | 操纵**偶**时继续按 `D`，**偶不再移动** |
| 统一复位 | 操纵偶时按 `R` → 灯与偶均回 `0.150`、Back Searching、Holding 0、Resolve 0，环境暖色撤销 |
| 仅偶到位 | 偶 `0.798` 有效、灯 `0.150` → 仍 Searching（**不误完成**） |
| 连续复位 | 连续 3 次 `R` 无卡死；`E` 释放后按 `R` 角色回出生点 |
| 焦点返回 | 操纵灯时切到 `W/B` 再返回，`D` 使灯 `0.150 → 0.272`，偶仍 `0.150`；`R`/`E` 正常（截图 `M2_FocusReturn.png`）——**仅覆盖「无按键保持的失焦恢复」，未测「按住键时失焦」的压力场景** |

上述实测**证明既有关卡在实玩中可达且协同判定正确**：灯与偶必须同时到位才会 Resolve。

**仍未验证**：PIE 路径、幕上构图的实时可读性、`ChaseAwakened` 呈现效果、
静音可完成、结束界面。上述均属主观可读性或未执行项，**不因本表通过而视为完成**。

### 0.6 Dev 状态文字反馈（2026-10-03，已实现并独立验收）

普通模式缺少「近 / 有效 / Holding 中 / 被打断 / 完成」状态反馈的问题已解决。
实现采用既有架构表现依赖，不新增判定、不显示答案数值。

**事件链**：Director 发布谜题事实 → `ADYStagePresentation` 转换为离散提示状态
→ `ADYStageGameMode` 弱注册通知 → `ADYDevInteractionHUD` 缓存并绘制。

提示六态：`Hidden` / `Adjust` / `Near` / `Holding` / `Interrupted` / `Complete`，
普通模式使用 ASCII 占位文案：`Keep adjusting` / `Getting closer` / `Hold steady` /
`Interrupted - try again` / `Complete`。

**硬性约束均已满足**：

- **不显示答案数值** —— HUD 不读取 `Current`、target、tolerance、Progress 或 Holding 数值；
- **不新增世界扫描**，不新增 Tick 轮询谜题；
- **不直接读取 Puzzle Director**，只消费 Presentation 发布的离散状态；
- HUD 迟到时只读 `GetFeedbackDisplay()` 快照，**不调用** `SynchronizeFromDirector()`，
  因此不会重放演出事件或重置环境；
- 既有准星与 `E` 交互提示行为不变。

**统一去重与中断计时器**：所有显示变化经单一入口，仅在状态实际改变时通知；
重复取消事件不重复广播、也不延长中断；`Far`/`Near` 采样在中断期间只更新恢复基线，
到期恢复**最新**基线；新的 Holding、Resolve、Activate 与 EndPlay 都会清理旧计时器，
避免旧到期回调覆盖新状态。中断显示默认 1.2 秒，为**可替换的 Dev 占位值**，不是最终节奏决定。

**Dev / Shipping 门控**：Dev 检查使用世界包名前缀 `/Game/DengYingShanHai/Dev/`；
真实 PIE 包名只在 map 短名前增加 `UEDPIE_0_`（如
`/Game/DengYingShanHai/Dev/M2/Maps/UEDPIE_0_LV_M2PuzzleLab`），目录保留。
Shipping 下默认 GameMode 不挂载 Dev HUD，反馈注册与采样入口关闭、中断计时器不启动；
但**不能声称** HUD 类、枚举与文案已全部从 Shipping 二进制剔除。

**改动范围**：8 个源码／测试文件（6 个既有文件修改 + 2 个新增），零资产改动。
不改地图、灯位、PlayerStart、镜头、输入、R 语义、判定目标／容差、15 Hz、材质与模型。

**自动化新增 9 项**（`DengYingShanHai.M2.Feedback.*`，全部 Success）：
`DisplayMapping`、`NoDuplicateNotifications`、`DevIsolation`、
`HUD.RegistrationOrderAndTeardown`、`Timer.RestoresLatestBaseline`、
`Timer.HoldCancels`、`Timer.ResolveCancels`、`Timer.ActivateCancels`、
`Timer.DuplicateCancelDoesNotExtend`。

其中 5 项计时器测试使用**真实 `FTimerManager`**：首次 Tick 激活后，通过 Automation
潜伏命令等待实际引擎帧推进，再 Tick 到期／取消；测试不直接调用到期回调冒充计时器，
不修改 `GFrameCounter`，不添加公开作弊入口。`HUD.RegistrationOrderAndTeardown`
调用与 `BeginPlay` 相同的生产绑定函数，但**不是完整 PIE 生命周期录像**。

**证据路径**：

- 验收事实源：`Saved/Audit-2026-10-03-M2Feedback/Supervisor-Results.md`
- 自动化报告（**独立目录**）：`Saved/Automation/M2Feedback-Codex/index.json`
  （25/0/0，逐项 `state` 全为 Success）
- 构建与测试日志根目录（**`Saved/Audit-2026-10-03-M2Feedback/`，不是上面的 Automation 报告目录**）：
  - `Supervisor-EditorBuild.log` / `Supervisor-EditorBuild.json`
  - `Supervisor-Automation.log`
  - `Supervisor-Shipping.log` / `Supervisor-Shipping.json`
  - `Supervisor-Normal2.log`（有效闭环）、`Supervisor-Normal.log`（前一轮路线试验，不作成功证据）
- 哈希对照：同目录 `Supervisor-BaselineHashes.json` / `Supervisor-VerifiedHashes.json`
- 回退证据：同目录 `backup/`

**普通模式真实键鼠验收**（真实 D3D12/SM6 窗口，无 `-DYDebug`，非 PIE、非打包程序；
只通过 E/A/D/W/R 与鼠标，不注入 Target、不直接改 Transform、不用 console 强制成功）：

| 证据 | 实际可见结果 |
|---|---|
| `Feedback_Start.png` | 初始 `Keep adjusting` |
| `Feedback_FreshReady.png` | 皮影绿色 E 聚焦，`Getting closer` |
| `Feedback_Holding.png` | `Hold steady` |
| `Feedback_Interrupted.png` | `Interrupted - try again` |
| `Feedback_InterruptExpired.png` | 到期恢复 `Getting closer` |
| `Feedback_Complete.png` | `Complete` + 原有暖色成功环境 |
| `Feedback_ResetFromComplete.png` | R 后 `Keep adjusting`，成功环境回到基线 |

日志 `Supervisor-Normal2.log` 在 06:06:05 UTC 记录 `Puzzle P02_ChaseForm resolved exactly once.`，
随后记录 `reset to its authored Dev baseline.`。截图根目录：
`C:\Users\lenovo\.codex\visualizations\2026\09\30\01a0f245-1d70-7ba1-9b69-e6db6a9b7948\`。

**当前风险**：

- 提示为**可替换的 Dev 占位**，不是正式中文 UI；本构建默认字体的中文覆盖**未验证**；
- 中断 1.2 秒为占位节奏，不是最终演出决定；
- 真实键鼠证明的是第 5 节之外的补充闭环，**不等于**第 5 节整套人工 PIE 验收通过；
- 边界项（中断期间新激活清理、Hold/Resolve 抢占、重复取消不延期）由自动化证明，
  **不混写为全套人工 PIE**；
- 未 Cook、未 Stage、未打包，Shipping 编译通过**不代表**运行包验证通过。

### 0.7 真实 PIE 客观复测（2026-10-03，Codex 执行）

唯一事实源：`Saved/Audit-2026-10-03-M2Acceptance/Supervisor-Results.md`。
本节由该文件同步，**不是人工签收**；§5 清单仍全部未勾选。

**本轮执行**：

1. `Verify-M2DevSlice.py` 只读重载：退出 0、`DY_M2_VERIFIED`、0 error / 0 warning（`AssetReload.log`）；
2. `Project.Maps.PIE` 限定 `LV_M2PuzzleLab`，真实 D3D12/SM6：1 succeeded / 0 failed，Map Check 0 error / 0 warning
   （`PIE-Automation.log`）。**该测试只证明启停，不操作谜题**；
3. 交互 PIE（PID 18920，带 `-DYDebug`，编辑器真实 Selected Viewport）；
4. 正常 PIE（PID 24844，不带 `-DYDebug`）：出生点不移动，瞄准后 `E` 控灯、`D` 调整、`R` 复位、`E` 释放；
   画面无调试字段／轨道／目标球，`LogDengYingShanHai` 的 FocusDebug/InteractDebug/InputDebug **共 0 行**；
5. 两个交互会话经 `Esc` 正常结束并正常关闭本轮启动的编辑器，无强杀、无 Save All、无地图保存。

**客观证据（PID 18920 同时证明灯单条件与偶单条件）**：

| 场景 | 观测值 |
|---|---|
| 灯单条件 | 灯 `.710` Valid=true，偶 `.150` Valid=false → Searching、ResolveCount 0 |
| 偶单条件 | 偶 `.799/StrideReach` Valid=true，灯 `.150` Valid=false → Searching、ResolveCount 0 |
| 组合 Holding | `.716/.780` → Holding 0.13 / 1.25；`A` 退到 `.589` 使 Holding 归 0 |
| 完成 | 再次 `D` 后 Complete，日志 UTC 06:50:35 `resolved exactly once` **全文仅 1 行** |
| 统一复位 | 控灯 `R` 与控偶完成后 `R` 均回 `.150/.150`、StrideBack、Searching、Holding 0、Resolve 0，环境回基线 |
| 调试链路截图 | `Holding` → `Interrupted` → `InterruptExpired` → `Complete` → `PuppetReset`，提示依次为 `Hold steady` / `Interrupted - try again` / `Getting closer` / `Complete` / `Keep adjusting` |

共 **18 张**截图，保存于 `Saved/Audit-2026-10-03-M2Acceptance/Screenshots/`，
使用 `Acceptance_PIE_` 前缀，不覆盖上一轮 `Feedback_` 截图。
证据隔离：上一轮 `-game`（PID 36876，`M2Feedback/Supervisor-Normal2.log`）与本轮 **不是同一个 PID**，
两者不混用；`M2Feedback/Supervisor-Normal.log` 为路线试验，不作成功证据。

**可读性未签收**：移动灯到目标侧后，幕后灰盒皮影及操杆偏暗，白色大块幕／遮挡几何与角色占位体
干扰观看，**尚不能清楚表现预期的双重空间**。灰盒几何姿态改变是可观察事实，
但**不等于「逐日」文化形象成立或可读性达标**。

**启动期 13 条错误已定位，但整份 GUI 启动日志并非零错误**：

GUI 编辑器进入 PIE **之前**出现 13 条 `LogAutomationTest: Error: Condition failed`，
提高日志详细度后确认属**引擎自带三项 Core SmokeFilter 测试**：

| 引擎测试 | 条数 |
|---|---:|
| `FUnifiedErrorTest_CreateErrorMessage` | 7 |
| `FUnifiedErrorTest_CreateErrorMessageWithContext` | 4 |
| `FStructuredLogFormatTest` | 2 |

证据 `PIE-Normal.log`（UTC 06:54:25；真实 PIE 于 06:54:33 开始）。
UnifiedError 测试对**格式化后的英文文案**做直接比较，而本次日志输出中文；
**本机语言格式相关是有依据的疑点，不声称已做语言 A/B 复验**。
项目 25 项测试标记 `EngineFilter`，**未标记** `SmokeFilter`。
本轮两份交互日志中 `LogDengYingShanHai` 无 Error/Warning，但**整份启动日志并非零错误**。
**不更换编辑器语言、不安装驱动、不改引擎、不「吞掉」错误。**
另有 D3D12 下 NVIDIA 驱动禁用 TSR 16-bit VALU 的引擎警告；未崩溃，
**不因此宣称性能通过或自行更新驱动**。

**无产品写入证明**：`BaselineHashes.json` 中 Source/Content/Config/Scripts 共 70 文件，
测试后 SHA256 **70 compared / 0 changed**；
`LV_M2PuzzleLab.umap` = `8236EC5F…759A4`、`Create-M2DevSlice.py` = `2F434ADD…EBC5F` 均未变。
HEAD 仍 `dda43f2`，暂存为空。

**本轮未执行**：用户人工签收、主观可读性签收、Dev 可读性修复小步、长时间刷新稳定性、
语言 A/B 复验、手柄／分屏／打包进程、Windows Development 包、第三幕、正式 UI 与美术。
**本轮未再次执行 25 项自动化**（25/25 为上一轮结果）。

### 0.8 Dev/M2 可读性布局小步（2026-10-03，用户批准并已实施）

事实源：`Saved/Audit-2026-10-03-M2Readability/Supervisor-Results.md`（Codex 修复与复验）。
本节由该文件同步，**不构成用户主观签收**；§5 清单仍全部未勾选。

**根因不是亮度不足，而是实心测试夹具挡住了光路。** `DEV_CameraWall` 实心范围
x[-122.5,-77.5]、y[-150,150]、z[0,340]；主灯目标位（灯 .72）与皮影目标位（偶 .80）
连线在 x=-100 处约 y82.2、z279，正落在该墙内——**提高强度无法打通被实心几何阻断的路径**。
`DEV_InnerCornerB` 位于偶与幕之间并占据观察构图。

**修复方式：只迁移三项 Phase1 夹具的位置，保留材质、尺寸与碰撞，不删除任何夹具**（单位 cm）：

| Actor | 旧位置 | 新位置 |
|---|---|---|
| `DEV_CameraWall` | (-100, 0, 170) | (-100, **-650**, 170) |
| `DEV_InnerCornerA` | (420, -520, 150) | (420, **-750**, 150) |
| `DEV_InnerCornerB` | (690, -250, 150) | (690, **-660**, 150) |

新位置留在原地板边界内的侧翼，避开主灯到目标皮影／幕的路径。M1 技术实验地图保留原布局。

**幂等配置工具**：`Scripts/Configure-M2Readability.py`（新增）。显式 M2 世界检查、
三标签唯一性与类型预检，**只调用位置 setter**。全部正确时为 **NOOP 且不保存地图**；
不修改旧 `Create-M2DevSlice.py`、不重建谜题 Actor。

**调用顺序与幂等验证**：
`读取并备份 → 仅配置 M2 夹具 → 独立磁盘重载 Verify 脚本 → 对比 70 文件仅地图变化
（新增工具单列） → 真实 RHI 正常／调试模式复测 → 保留失败尝试与截图`。
`Configure-Idempotent.log` 记录重复运行为三项 NOOP、退出 0，地图 SHA-256 保持不变。

**备份与回退**：`Backup/LV_M2PuzzleLab.before.umap`，SHA-256
`8236EC5F3AD66BE9BF10C9D91E15AD5AA9771D6D11ADF3E55CC15D1842E759A4`（与修复前源一致）。
修复后地图 SHA-256 为 `273EEE61596E6D34004B2CD1796798EBBCDBC7648706BFB00CA2D07580E413B0`。
回退方式：**退出使用该地图的 UE 进程后，仅以该备份恢复这一个明确地图**，
不恢复整个工作区、不 git checkout 未提交的用户改动。

**本轮不变量**：**无任何 C++ 改动，未重新编译**。未新增灯、未修改曝光／主灯／相机、
未删除 Actor、未改输入或判定、未改共享 Stage Blueprint 与 M1 地图。
Source／Config／其他 Content／原 Scripts 均未变；70 个既有产品文件中**仅 M2 地图哈希变化**，
新增配置脚本单列。

**自动化与磁盘检查**：

- `Verify-M2.log`：退出 0、`DY_M2_VERIFIED`、`DY M2 Verify: PASS` 计数 **35**、
  FAIL 0；15 Hz、灯目标 .72、偶目标 .80、1.25 s、姿态与显式引用、默认关闭调试均不变。
  初稿曾手计为 36，后按日志逐行计数**校正为 35**，**检查均通过，不是检查失败**；
- `Configure.log`：commandlet 0 error / 0 warning，退出 0；
- `Inspect-Before2.log` / `Inspect-After.log`：独立磁盘加载各 25 个已保存 Actor，
  过滤 Struct／Object 地址后**仅三项夹具不同**，且改变的只是 Actor 及其 mesh 的世界位置；
  已记录的 scale、rotation、shadow、mesh 类型、灯光与曝光值一致
  （**不是**对全部未导出资产属性的二进制语义审查）；
- 首次 `Inspect-Before.log` 因只读辅助脚本调用不存在的 `is_hidden` API 失败，
  已修正为属性读取；**失败记录保留，不是产品运行失败**。

**真实编辑器 PIE（UE5.8.3 真实 Selected Viewport，D3D12 RHI，非 `-game` 冒充、非 NullRHI）**：

| 检查 | 观察结果 |
|---|---|
| 出生点灯交互 | 不前进、瞄准灯按 `E` 成功；正常模式仅已有准星与 ASCII 状态，无开发参数／轨道 |
| 仅灯到位 | Debug 灯 `.716` 有效、偶 `.150` 无效，Searching／Holding 0／Hz 15；**灯、偶与幕上投影均可见** |
| 偶聚焦／控制 | 沿原路线靠近、绿准星按 `E`；同机位可见占位皮影及其**头／身／杖投影** |
| 组合 Holding | 灯 `.716`、偶 `.785`、Reach 有效，Holding .20/1.25、Hz 15；正常模式 `Hold steady` |
| 打断 | `A` 退出到偶 `.539`、Mid 无效，Searching／Holding 0、灯仍有效；`Interrupted` 出现后恢复 `Getting closer` |
| 再尝试成功 | `D` 回有效范围、等待后 Complete；同画面暖色强调与影子保留；每个 PIE 日志 `resolved exactly once` **仅 1 次** |
| 成功后 `R` | 灯／偶均回 `.150`、Back 无效、Searching／Holding 0／ResolveCount 0、Hz 15；暖色撤回、投影仍可见 |
| 仅偶到位 | 成功复位后仅调偶、等候 >1.25 s，偶有效／灯 `.150` 无效，**仍 Searching**，无再次完成 |
| `E` 释放／退出 | 操纵退出恢复 Explore；正常停止 PIE 后关闭本轮自启编辑器，**未保存运行状态** |

**项目测试**：25 项 `DengYingShanHai` 测试逐项 `Result={Success}`、**失败 0**、进程退出 0
（`Automation.log`）。此为**旧二进制的回归**——本轮无 C++ 改动，**未重新编译**。

**与引擎自检的区别**：正常 PIE、调试 PIE 及 Automation 启动阶段**仍各出现既有 13 条**
`LogAutomationTest: Error: Condition failed`；此前审计定位于引擎 Core SmokeTests 的
格式／本地化断言，**根因未经语言 A/B 确认，本轮未修引擎**。
**25 项项目测试全部成功与这些引擎自检是不同结果，不能说整份日志零错误。**
原 NVIDIA／TSR 警告不在本小步处理范围。

**证据目录**：`Saved/Audit-2026-10-03-M2Readability/`，其中
`Screenshots/` 共 **19 张**：`Readability_Normal*.png` **8 张**、`Readability_Debug*.png` **9 张**、
`Before_*.png` **2 张**（本轮 A/B 用的历史图副本）。
**上一轮 §0.7 的 18 张 `Acceptance_PIE_*` 原始证据未被覆盖或改动。**
现场 A/B 见 `Before_NormalLampOnly.png` 与 `Readability_NormalLampOnly.png`、
`Before_DebugHolding.png` 与 `Readability_Debug_Holding.png`；
**不是完全相同像素机位的定量亮度实验**。

**（历史记录）本小步实施后仍待用户签收**：灰盒仍有球头、矩形躯干、细杖、角色占位体、硬边幕／侧墙及既有强调灯光斑。
这些**不构成正式夸父形象或高质量皮影美术**，文化形象、中文正式 UI、音效、盲测、
性能门槛、完整 5–8 分钟、P03 与结尾**均未完成**。当时要求用户确认当前画面是否已足够清楚
用于技术验收；**该签收已于 2026-10-03 给出，见 §0.9**。第 5 节人工清单始终不代勾。

### 0.9 用户有限签收（2026-10-03，当时记录；最新签收见 §0.11）

用户本轮明确答复：**「看清了，操作正常」**。

**签收范围（有限）**：仅签收 §0.8 布局修复后的 **Dev/M2 主观可读性与操作手感**，
即当前灰盒画面是否已足够清楚可用于技术验收，以及 `E`／`A`／`D`／`R` 操作是否正常。

**该签收不代表**：

- §5 的 **11 项独立人工检查全部通过** —— §5 清单**全部保持未勾选**；
- **M2 完整完成** —— 正式中文 UI、音效节奏、最终美术、首次玩家盲测、
  性能门槛、完整 5–8 分钟、Windows Development 包与 P03 **均未完成**；
- 灰盒的球头、矩形躯干、细杖与角色占位体已成为**正式夸父形象或最终美术**。

因此本节**不改动 §5 任何一个 checkbox 的文本或勾选状态**，只在其说明段中区分
「有限签收」与「逐项人工检查」两件事，避免把两者混为一次结论。

**后续方向**：中文 UI 方案 B 已按用户批准实施并通过技术验收（见 §0.10）。
本节签收范围不因该实现而扩大；**下一步是用户签收 UI 布局与措辞**，
以及 §5 其余人工项的逐项确认，不再是请求方案确认。

### 0.10 中文 UI 方案 B 实施与技术验收（2026-10-03，当时记录；后续签收及补验见 §0.11）

事实源：`Saved/Audit-2026-10-03-M2UI/Supervisor-Results.md`（Codex 实现与独立验收）
执行合同：`Saved/Audit-2026-10-03-M2UI/Execution-Contract.md`
架构决定：`ARCHITECTURE_DECISIONS.md` **ADR-013（Accepted，2026-10-03）**

用户已批准「采用方案B且允许」。本小步**技术验证完成，等待用户签收 UI 布局与措辞**；
**不是整个 M2 或竞赛 Demo 完成**。

#### 本轮 0.10 证据（区分类型，不混写）

| 核验 | 结果 | 证据类型 |
|---|---|---|
| 实施前项目自动化 | 25 Success / 0 Failed | 回归基线 |
| **实施后项目自动化** | **30 Success / 0 Failed**，退出码 0；新增文案、绑定、非 Dev 真实计时器、EndPlay 清理测试；**未删旧测试** | 自动化 |
| **UI 冷读** | **20 PASS**，commandlet 0 error / 0 warning | 只读资产检查 |
| **M2 原玩法／保存约束冷读** | **35 PASS**，commandlet 0 error / 0 warning | 只读资产检查 |
| Editor / Game Development / Game Shipping 编译 | **三者 Succeeded** | 编译 |
| **M2 Development 与 Shipping 完整 Cook / Stage / Package / Archive** | 两者 **BUILD SUCCESSFUL**、退出码 0；Cook summary 0 error / 0 warning | **完整技术包** |
| Font cmap | 45 个实际文案字符（含全角空格 U+3000）均无缺字 | 只读解析 + 实拍独立验证 |
| Editor 真实 PIE | `E`/`A`/`D`/`R` 与反馈闭环可见 | 真实 RHI 键鼠 |
| **Shipping 独立包键鼠闭环** | 灯单条件只到 Near、灯偶组合 Holding、打断／到期恢复 Near、再试 Complete、`R` 回 Adjust | **真实独立包** |
| Development 独立包 | 1920×1080 中文与同一键鼠闭环正常，**无开发画面** | 独立包 |
| Development 调试模式 | `-DYDebug` 显示目标参数／轨道／15 Hz，**中文玩家 UI 仍存在** | 独立包 |

**分辨率如实记录**：720 高客户端实测 **1279×720**（DPI 舍入，**不写成精确 1280×720**）；
1080 为 **1920×1080**。

#### 已知失败与处置（不掩盖）

1. `FontFileImportFactory` 在 NullRHI commandlet 无 Slate 应用时断言；改为真实 Editor GUI 导入，无额外插件。
2. **第一份 Shipping 虽 Cook 成功，但命令行地图被引擎 Shipping 默认忽略，启动进入 M1**；
   `M2UI-Shipping-20261003` **不交付为 UI 通过版本**。引擎 `GameInstance.cpp` 621–645 默认
   `UE_ALLOW_MAP_OVERRIDE_IN_SHIPPING=0`。
3. 正确包来自 `Saved/PackagingProject` **隔离构建副本**，只在副本 Config 把 `GameDefaultMap` 设为 M2；
   **原工程 Target 宏与全局 Config 未改**（原 `DefaultEngine.ini` SHA-256 `909F1328…6533` 保持）。
4. 最初名为 `ShippingM2_720_Initial` 的截图**实际是 1920×1080**，不能凭文件名认定分辨率；
   后续原图从真实客户端矩形捕获。
5. Development 首次批量探针把移鼠与 `E` 放在同一步、未等待聚焦刷新，因此未进入控制；
   `DevelopmentM2_1080_*` 第一组**不作为闭环成功证据**；重启后分开聚焦与 `E`，用
   `DevelopmentM2_Retry_*` 验证。**产品输入逻辑未修改。**
6. Windows 防火墙网络访问询问曾抢焦点；安全守卫拒绝发键后核实 `PickerHost`，按 `Esc` 取消，
   **未打开公共／专用网络许可**。此离线 Demo 无需批准联网。

#### 交付与启动

优先直接双击（Shipping，**无需打开 UE；必须保留整个 Windows 文件夹，不能只复制 exe**）：

```text
C:/Users/lenovo/.codex/visualizations/2026/09/30/01a0f245-1d70-7ba1-9b69-e6db6a9b7948/M2UI-Shipping-M2-20261003/Windows/DengYingShanHai.exe
```

Development 对照包：同根下 `M2UI-Development-M2-20261003/Windows/DengYingShanHai.exe`。

**Dev／Ship 技术包不是完整竞赛作品**：不含正式美术、最终主地图接入、音效与 P03。

#### 保留风险

- 未做 GUI 配置脚本**重复执行的二进制幂等性实测**，不能把「脚本有相等检查」写成已通过幂等验收；
- **未测**其他机器兼容、FPS、首玩时长、音效与完整三轮竞赛流程；
- 既有引擎 smoke-test 本地化 Error、MSVC 版本建议与 RHI `TSR 16-bit VALU` 警告**均保留**；
  **不声称整份运行日志零警告**（Shipping 默认关闭日志亦不能据此声称零警告）；
- 项目 30 项 Success **不等于**整份 Automation 日志零错误。

**本节是技术验收，不是用户逐项签收**；§5 的 **11 项人工清单仍全部未勾选**。

### 0.11 P02 与中文 UI 用户签收、重复配置补验（2026-10-03）

用户先答复 **「中文 UI 正常，继续下一步」**，随后针对本文件 §5 完整清单明确答复 **「11 项已逐项检查，全部正常」**。§5 现按用户实际报告逐项勾选，原检查文本不变；不再要求用户重复提交这 11 项。§0.9–0.10 当时的待签收结论属于历史，已由本节更新。

Codex 另在同一次真实 GUI Editor 会话连续运行两次 UI 配置：各次均 0 个产品文件 SHA256 变化、20 UI PASS、35 M2 PASS。外部复核 84 个 Source/Content/Config/Scripts/LICENSES 文件未变且无新增。详见 `Saved/Audit-2026-10-03-M2Closure/Supervisor-Results.md`。这是本机同会话重复配置证据，不是所有环境幂等承诺。

**关闭范围**：P02「逐光成形」灰盒机制与中文 UI 切片。**仍未完成**：P03 连续落杖成林、三幕整体流程、正式美术/声音/主地图、首次玩家盲测、5–8 分钟、性能与其他机器兼容、完整竞赛三轮通关。M2 是“三互动灰盒闭环”整体里程碑，不能因此标为整体完成。用户“继续下一步”允许进入第三幕准备，实际未决参数和演出取舍仍须确认。

### 0.12 第三幕首个底层契约小步（2026-10-03，不扩大 P02 签收）

用户选择「采用真实投影树形灰盒方案」。Codex 已新增成功控制快照及 Director Token 身份契约，只改两个 Director 文件、新增快照头与测试文件；M1/P02 资产、输入、镜头、灯光、15 Hz 与参数均未变。最新项目 34 Success / 0 Failed（原 30 项全保留 + 新增 4 项），Editor/Game Development/Game Shipping 编译、20 UI 与 35 M2 冷读通过。

这是后续真实落杖演出的数据基础，不是可见 P03：手杖/幕布表现快照、接触/生长、完整终章锁/结束态/回调消费均未接入，未新 Cook/Stage/Package，旧 UI 包不含本轮代码。用户已签收的 §5 不重置或重复要求检查；新小步证据独立保留在 `Saved/Audit-2026-10-03-P03Foundation/`。

## 1. 玩家可见结果

玩家沿用 M1 已学会的输入，不增加新按键：

1. 对准灯具按 `E` 进入控制，用 `A/D` 改变灯位，再按 `E` 退出；
2. 对准皮影按 `E` 进入控制，同样用 `A/D` 改变偶位；
3. 皮影沿轨道移动时经过少量预设姿态档位，形成稳定 `PoseId`；
4. 只有灯位、偶位和指定姿态同时处于目标条件并保持 1.25 秒，第二幕才 Resolve；
5. `R` 通过当前受控对象发出统一的谜题复位请求，同时恢复灯、偶和判定状态。

这使第二次互动成为“在两个可控对象之间切换并协同控制”，而不是为第二幕开发另一套输入或判定系统。

## 2. 实现结构

```text
ADYStageOperatorPawn
  → UDYInteractionComponent
    → IDYControllable
      ├─ ADYLightRigActor → UDYLightControlComponent
      └─ ADYPuppetActor   → UDYPuppetControlComponent

ADYPuzzleDirector
  → 显式 LightRig / PuppetActor 引用
  → UDYPuzzleDefinition（灯位、偶位、RequiredPoseId、Holding）
  → UDYPuzzleEvaluatorComponent（统一滞回、进度、Holding、一次性 Resolve）
  ⇒ OnPuzzleActivated / OnEvaluationUpdated / OnHoldStarted / OnHoldCanceled
  ⇒ OnPuzzleResolved(PuzzleId, ResolvedSnapshot)

BP_DYStagePresentation（ADYStagePresentation 基类）
  → 显式 PuzzleDirector / StageEnvironment 引用
  → P02 Resolve 映射为 ChaseAwakened
  → 只在有限 Feedback 状态改变时向 Blueprint 发布表现事件

BP_DYStageEnvironment（ADYStageEnvironment 基类）
  → Dormant / SunAwakened / ChaseAwakened
  → 不读取 Director、不判定流程、不 Tick
```

关键边界：

- `UDYPuppetControlComponent` 是可复用能力组件，不读取谜题答案；
- 灯和偶都消费相同 `FDYControlIntent::PrimaryAxis`；
- P01 的 Puppet 条件默认关闭，皮影控制组件也默认禁用，因此 M2 扩展不会让第一幕皮影意外可控；
- `UDYPuzzleEvaluatorComponent` 在同一个状态机中组合条件，不新增 P02 专用 Blueprint 判定；
- Director 只发布谜题事实，已移除对 StageEnvironment 的引用和直接调用；
- `ADYStagePresentation` 在 BeginPlay 一次绑定 Director 委托，EndPlay 解绑，并通过当前状态查询处理 Actor BeginPlay 顺序不确定性；
- 15 Hz `OnEvaluationUpdated` 只在 C++ 中更新轻量状态，Blueprint 只接收 Far / Near / InsideTarget / Holding / Resolved 等离散变化，不会按采样频率连发音效；
- 真实 UE 阴影只负责视觉，灯位、偶位、PoseId 和持续时间才是唯一主判定；
- 屏幕调试仍默认关闭，只在显式 `-DYDebug` 时以最高 4 Hz 展示，而逻辑统一以已确认的 15 Hz 采样。

## 3. 当前 P02 Dev 配置

| 条件 | Target | Enter | Exit | 备注 |
|---|---:|---:|---:|---|
| LightPosition | 0.72 | 0.05 | 0.09 | 归一化灯轨 |
| PuppetPosition | 0.80 | 0.05 | 0.09 | 归一化操偶轨 |
| PuppetPoseId | `P02_StrideReach` | — | — | 离散姿态条件 |
| RequiredHoldSeconds | 1.25 s | — | — | 使用真实世界时间累计 |
| EvaluationFrequency | 15 Hz | — | — | ADR-006 Accepted |

这些目标值属于 Dev 调试配置，可在不改变架构的前提下调节；任何会改变输入语法、控制对象数量或第二幕体验结构的调整仍须与用户确认。

## 4. 已完成证据

- `DengYingShanHaiEditor Win64 Development` 编译成功；
- 全项目 C++ Automation 11/11 通过：Phase 1 4 项、M1 3 项、M2 4 项
  （**初始 M2 切片的历史数字**；最新全项目结果为 25/25，见 §0.6）；
- M2 测试覆盖组合条件、任一条件丢失后取消 Holding、偶位独立滞回、P01 固定偶的默认禁用，以及 Presentation/Environment 无 Tick 默认值；
- 独立 UE 进程从磁盘重载地图与 Data Asset，输出 `DY_M2_VERIFIED`，0 error / 0 warning；
- Map Check 为 0 error / 0 warning；
- 显式限制到 `LV_M2PuzzleLab` 的真实 D3D12/SM6 `Project.Maps.PIE` 1/1 通过，地图正常进入和退出 PIE，Map Check 0 error / 0 warning，运行时使用 `DYStageGameMode` 且 Explore Context 只应用一次；
- 保存资产验证确认 Director 只显式引用 LightRig、PuppetActor 与 P02 Definition；`BP_DYStagePresentation` 显式引用 Director 和 StageEnvironment，并把 P02 Resolve 映射为 `ChaseAwakened`；
- `BP_DYStageEnvironment` 使用无 Tick 的 `ADYStageEnvironment` 基类，现有两个可移动 Dev 强调灯，保存时均为 Dormant 零强度；
- 皮影占位体的三个部件继续投射真实 UE 阴影；
- P02 数据和地图只写入 `Dev/M2`；两个共享薄 Blueprint 位于 `Content/DengYingShanHai/Stage`，源 M1 地图保持独立。

自动化报告：

```text
C:\UEProjects\DengYingShanHai\Saved\Automation\M2B-Core\index.json
C:\UEProjects\DengYingShanHai\Saved\Automation\M2B-Map-PIE\index.json
```

## 5. 人工 PIE 检查

在 Content Browser 打开 `DengYingShanHai/Dev/M2/Maps/LV_M2PuzzleLab` 后运行 PIE：

> **用户已逐项签收，2026-10-03**：在明确列出本清单范围的询问中答复「11 项已逐项检查，全部正常」。以下勾选依据是用户实际报告，不是 Codex 用自动化或先前「看清了，操作正常」替代人工检查。项目最新历史自动化为 30/30；这仍是独立证据类型，不扩大为完整作品签收。

- [x] 默认画面无屏幕调试文字、轨道或目标球闪烁；
- [x] 对准灯按 `E` 可进入控制，`A/D` 只移动灯，再按 `E` 可退出；
- [x] 对准皮影按 `E` 可进入控制，`A/D` 移动皮影且灰盒姿态可见变化，再按 `E` 可退出；
- [x] 灯和皮影使用相同按键，但同一时刻只有当前选中对象响应；
- [x] 在 `-DYDebug` 下可同时看到 Light、Puppet、Pose、Holding、State 与 15 Hz，显示刷新不闪烁；
- [x] 只满足灯位或只满足偶位/姿态时不会误完成；
- [x] 全部条件满足并保持 1.25 秒后只 Resolve 一次；
- [x] Resolve 后台翼级暖色扩展明显不同于 P01，且不覆盖主灯投影的因果可读性；
- [x] 控制灯或偶时按 `R` 都能复位灯位、偶位、姿态、Holding 与 Resolve 状态，环境同时回到 Dormant；
- [x] 移动灯和偶时幕上阴影实时变化，视觉异常不会改变参数判定；
- [x] 退出控制、窗口失焦、重新进入和连续复位不会残留输入上下文或卡死。

本轮只评价协同机制、稳定性、阴影因果和调试可证性。基础几何皮影、轨道映射姿态和现有成功灯光仍是 Dev 占位，不代表正式视觉质量。

## 6. 已知限制与下一段工作

当前已完成 Director → Presentation → Environment 边界、`ChaseAwakened` Dev 表现，
以及 §0.6 的 Dev 状态文字反馈。`BP_DYStagePresentation` 当前是无自定义事件图的最小
Blueprint 子类：绑定、迟到同步、有限状态去重、提示快照与环境映射由可测试的 C++ 基类保证，
Blueprint 事件留给后续视听编排。

**已完成**：Dev 状态文字反馈（Keep adjusting / Getting closer / Hold steady /
Interrupted - try again / Complete）、Editor Development 构建、Automation 25/25
（**上一轮结果**）、Shipping 目标编译、普通 `-game` 真实键鼠五状态闭环，
以及 §0.7 的**本轮真实 PIE 客观复测**。

**原阻塞已处理**：§0.7 记录的「实心挡光夹具导致目标侧偏暗、前方大块几何遮挡」，
其根因是**实心 Phase1 夹具挡住主灯到目标皮影／幕的光路**，不是亮度不足。
该布局小步**已由用户批准并实施**（见 §0.8）：三项夹具迁移到侧翼，正常与调试 PIE 中
灯、偶与幕上投影均可见，**基本双空间可见性已恢复**。

**可读性与操作手感已获有限签收**：§0.8 布局修复后，用户于 2026-10-03 答复
**「看清了，操作正常」**（见 §0.9）。该签收仅覆盖主观可读性与操作手感，
**不等于 §5 的 11 项逐项人工检查通过**；灰盒的球头、矩形躯干、细杖与占位体
**不代表正式夸父形象或最终美术**。

**（历史，指 §0.8 夹具布局小步）** 该小步未新增补光、未改曝光／镜头／输入／判定、未改主灯，
且**仅该布局小步**没有 C++ 改动。
**本轮（§0.10 中文 UI）确有 C++ 修改**，并已完成 Editor／Game Development／Game Shipping **三目标编译**。

**中文 UI 已实施**：方案 B（薄 C++ 绑定适配器 + UMG 中文视图，公共玩家提示与 Dev 诊断分离）
已由用户批准并由 Codex 实施，**技术验收完成**（见 §0.10）：
30/30 项目测试、20 项 UI 冷读、35 项地图冷读、Editor／Game Development／Game Shipping 三目标编译、
Development 与 Shipping **完整 Cook／Stage／Package 技术包**、以及真实 RHI 键鼠闭环。
架构决定见 `ARCHITECTURE_DECISIONS.md` **ADR-013（Accepted，2026-10-03）**。

**当前下一步：P02 与 UI 已签收，进入 P03「杖落成林」Dev 连续因果原型准备。** 以下未决配置由第三幕提案列明，不自行确定。

1. 审查真实变换冻结快照、Director 发出 Token、P03 控制锁与落杖/接触/成林/统一收尾接口；
2. 在隔离 Dev 测试资产中验证玩家最终状态 → 落杖 → 同落点生长，保留 M1/P02 资产；
3. 正式美术与最终主地图接入、音效节奏与视觉引导；
4. 首次玩家盲测、性能门槛与完整 5–8 分钟；
5. 其他机器兼容与完整三轮竞赛流程仍未测；本机同会话 GUI 配置二次幂等已补验，不夸大为跨环境结论；
6. P03 原型与三幕整体接通、上述整体退出条件完成后，才关闭 M2 三互动里程碑。

**（迁移前历史，2026-10-03 之前）** 以下为方案 B 实施前的旧清单，
其中「用户确认中文 UI 提案」与「再生成 M2 Windows Development 包」两项**已由 §0.10 取代**
（方案 B 已获用户批准并实施，Development／Shipping 完整技术包已构建）：

1. 用户确认中文 UI 提案（是否接受方案 B）后，再实施中文提示与字体验证；
2. 正式 UI 之后接入音效节奏、视觉引导与最终美术，以及静音可完成性复核；
3. 首次玩家盲测（完成时长、卡点、提示介入、能否复述「未完逐日—自己复演」）；
4. §5 的 11 项逐项人工检查按项确认；
5. 上述完成后再生成 M2 Windows Development 包（Cook / Stage / Package）；
6. M2 完整验收通过后才进入第三幕综合条件与「杖落成林」连续因果原型。

**不宣称 M2 完整完成**，也不把 `LV_M2PuzzleLab` 当作最终单主地图；
P02 主观可读性、操作、中文 UI 和 11 项人工检查现均获用户明确签收；**不等于整个 M2 三互动里程碑或竞赛版本完成**。

## 7. 可重复命令

生成：

```powershell
& 'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe' `
  'C:\UEProjects\DengYingShanHai\DengYingShanHai.uproject' `
  -run=pythonscript `
  '-script=C:\UEProjects\DengYingShanHai\Scripts\Create-M2DevSlice.py' `
  -unattended -nop4 -nosplash -NullRHI -NoSound
```

独立重载验证：

```powershell
& 'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe' `
  'C:\UEProjects\DengYingShanHai\DengYingShanHai.uproject' `
  -run=pythonscript `
  '-script=C:\UEProjects\DengYingShanHai\Scripts\Verify-M2DevSlice.py' `
  -unattended -nop4 -nosplash -NullRHI -NoSound
```
