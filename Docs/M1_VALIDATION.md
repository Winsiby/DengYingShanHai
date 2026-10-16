# M1 VALIDATION｜“引日启幕”Dev 垂直切片验收

建立日期：2026-10-02  
工程：`DengYingShanHai`  
地图：`/Game/DengYingShanHai/Dev/Interaction/LV_InteractionLab`  
状态：**Accepted / Closed。黑屏与调试闪烁回归已修复；用户已完成 9 项人工 PIE 检查并确认全部正常，修复版独立包运行无问题；15 Hz 与 PC 键鼠基线已确认，可进入 M2。**

> 最高优先级限制：*永远不要以牺牲架构设计为代价追求功能；永远不要基于猜测进行权衡——必须与用户确认。*

## 1. 本里程碑只验证什么

M1 只验证第一次互动“发现规律”的最小完整链：玩家发现并聚焦主灯，进入操纵态，在受限轨道移动真实 UE 灯光，直接观察幕后灯/偶与幕上投影的因果关系，再由独立参数判定完成持续确认。

本阶段不实现互动二、互动三、正式夸父模型、最终戏台美术、正式声音、正式幕布材质或“弃杖化林”。基础形体、文字标签和橙色成功灯光都是 Dev 反馈，不得进入最终展示结论。

## 2. 当前实现结构

```text
ADYStageOperatorPawn
  → UDYInteractionComponent
    → IDYControllable
      → ADYLightRigActor
        → UDYLightControlComponent

ADYPuzzleDirector
  → UDYPuzzleDefinition（配置）
  → UDYPuzzleEvaluatorComponent（纯参数判定）
  → ADYLightRigActor（显式实例引用）
  ⇒ 发布 PuzzleActivated / EvaluationUpdated / Hold / Resolved

BP_DYStagePresentation
  → 显式引用 Director 与 ADYStageEnvironment
  → P01 Resolve 映射为 SunAwakened，复位映射为 Dormant
```

职责边界：

- Pawn 只绑定语义 Input Action，不保存谜题答案；
- InteractionComponent 负责聚焦、进入/退出、意图路由和上下文重置请求；
- LightRig 负责灯具表现、真实光照和可控能力，不知道目标区间；
- Evaluator 只处理区间、滞回、持续确认和成功边沿，不读取阴影像素；
- Director 是关卡流程事实源，以显式引用采样 LightRig 并发布语义事件；
- StagePresentation 只在 Director 更新谜题事实后消费事件，不复制判定；StageEnvironment 只被动接收语义状态，不读取 Director；
- Level Blueprint 不保存状态、不复制判定、不查找 Actor。

当前重置链为：

```text
操纵态 R
→ Pawn
→ InteractionComponent::ResetActiveControl
→ IDYControllable::ResetControlState
→ LightRig::OnResetRequested
→ Director::ResetCurrentPuzzle
```

这条链避免 Pawn 依赖 PuzzleDirector，也避免 `GetAllActorsOfClass`。禁用灯的 gameplay response 不会静默结束 InteractionComponent 持有的控制会话，输入上下文生命周期仍只有一个事实源。

## 3. Dev 输入与数据基线

以下物理键已确认为当前竞赛版本的 PC 键鼠基线；语义 Action 与 Mapping Context 仍保持可替换，不把物理键写入谜题逻辑：

| 状态 | 输入 | Dev 行为 |
|---|---|---|
| Explore | `W/A/S/D`、Mouse | 移动与观察 |
| Explore | `E` | 对准可控灯具时进入 Manipulate |
| Explore | `R` | 复位操作载体，保持 Phase1 语义 |
| Manipulate | `A/D` | 沿一维轨道移动主灯 |
| Manipulate | `R` | 重置当前 P01 灯位与判定 |
| Manipulate | `E` | 退出控制并恢复 Explore Context |

P01 当前 Dev 数据：

| 字段 | 数值 | 决策状态 |
|---|---:|---|
| Target | 0.680 | Dev 实验值 |
| EnterTolerance | 0.045 | Dev 实验值 |
| ExitTolerance | 0.085 | Dev 实验值 |
| RequiredHoldSeconds | 1.25 s | Dev 实验值 |
| EvaluationFrequency | 15 Hz | ADR-006 Accepted；竞赛版本统一逻辑采样基线 |

调试层显示 `Current / Target / Enter / Exit / Valid / Progress / Holding / State / ResolveCount / Hz`，并绘制灯轨与目标位置。它默认关闭，只有显式使用启动参数 `-DYDebug` 才启用；显示刷新与 15 Hz 谜题采样解耦，并限制为最高 4 Hz，避免高频文字闪烁。Shipping 构建不会显示 C++ 屏幕调试。

## 3.1 聚焦半径与相机射线长度分离（2026-10-02 修正）

监督复测发现并已修复一处 Dev 阻塞项：出生点原地对准灯具按 `E` 无响应，向前移动约 0.9 秒后同一操作成功，日志出现 `Entered Dev Manipulate input mode at priority 10`。碰撞、输入映射与状态链均正常。

根因不是资产、碰撞或输入，而是**角色交互半径与相机射线长度错误共用同一个 700 cm**：

- 角色到 M2 灯具约 515 cm，在 700 cm 半径内；
- 第三人称 SpringArm 臂长 360 cm，相机位于角色之后，相机到灯具超过 800 cm；
- 旧实现从相机视点发出长度恰为 700 cm 的射线，在到达灯具之前就已耗尽。

修复保持 `FocusDistance = 700 cm` 不变，语义为角色真实可交互半径：

- `ComputeFocusTraceLength()` 返回 `相机到角色偏移 + FocusDistance`，使射线不再提前耗尽；
- `IsWithinFocusDistance()` 在命中后按“候选对象到角色 <= 700 cm”二次门控，相机位置、后移距离与 FOV 均不能扩大角色半径；
- 仍只接受第一个 Visibility 阻挡物，遮挡语义不变；仍为 0.10 秒定时器刷新，无 Tick、无世界扫描；
- `OnFocusChanged`、`OnControlStateChanged` 与输入上下文生命周期未改动。

本项只修改 C++、自动化测试与文档，未触碰任何 `.uasset`、地图、灯位、PlayerStart、亮度、材质或 15 Hz 判定。聚焦距离语义的规范描述见 `TECH_SPEC.md` 的「聚焦距离语义」小节；本节与 `M2_VALIDATION.md` 第 0 节记录该缺陷的复测与修复过程。

### 3.2 本项的验证结果（2026-10-03）

- Editor Development 构建成功：`Build.bat -NoUBA`，最终增量 4/4 成功；
- 产物 `Binaries/Win64/UnrealEditor-DengYingShanHai.dll`，641,024 字节，时间 2026-10-03 02:08:43；
- 工具链实际为 MSVC 14.51.36260，高于 UE 5.8.3 首选的 14.50，Unreal Build Tool 给出非首选版本警告。
  该警告属本机既有环境提示，**不归因于本轮代码**；
- 全套自动化最终报告 `Saved/Automation/M2-Focus-FinalFull/index.json`：
  **16 succeeded / 0 failed / 0 warnings / 0 errors**。逐项 JSON 的 `state` 已逐一核对，未只依据进程退出码；
- 测试世界初始化曾导致 `RuntimeTrace` 失败：临时 World 缺少 `InitializeActorsForPlay`，
  表现为直接调用 `_Implementation` 返回 true 而 `Execute_` 分发返回 false。
  按 UE 5.8 官方 `ActorTestSpawner` 模式补齐 `AddToRoot` 与 `InitializeActorsForPlay` 后，
  单项报告 `Saved/Automation/M2-Focus-RuntimeWorldInit/index.json` 为 1 Success / 0 error / 0 warning；
- 两个关键基线保持不变，完整 SHA-256 为：
  - `Scripts/Create-M2DevSlice.py` = `2F434ADD735339F89C677C2C2EE6A2C0BB892C023D405C76506EFDBB7BAEBC5F`
  - `Content/DengYingShanHai/Dev/M2/Maps/LV_M2PuzzleLab.umap` = `8236EC5F3AD66BE9BF10C9D91E15AD5AA9771D6D11ADF3E55CC15D1842E759A4`
  Git 仍为 22 项改动，未 commit、未暂存、未清理；01:30 之后无任何 `.uasset`/`.umap` 写入。

### 3.3 恢复过程记录（据实记录）

修复过程中，`Source/DengYingShanHai/Private/Interaction/DYInteractionComponent.cpp`
曾因编辑工具误用覆盖重定向（`echo >`）在本地文件时间 01:41:05 变为 3 字节。
该事故由监督者发现。

恢复方式：**没有使用 Git 回退覆盖脏工作树**。先确认该文件原先不属于既有 19 项改动，
再以 HEAD 中的原始构造函数 + 9 个成员函数为基线，合入本轮已审计的聚焦改动重建文件。

恢复完整性由以下证据支撑：

- 最终函数清单包含原有构造函数、`BeginPlay`、`EndPlay`、`ToggleControl`、`EndActiveControl`、
  `ApplyPrimaryAxis`、`ResetActiveControl`、`UpdateFocusedActor`、`SetFocusedActor`、`GetOwnerPawn`，
  以及新增的 `EvaluateFocus`、`PublishFocusDebug`、`ComputeFocusTraceLength`、`IsWithinFocusDistance`；
- 其中 8 个原有函数体与 HEAD 逐字节一致；
- `git diff --check` 通过；
- 多次成功链接、`RuntimeTrace` 单项通过与 16/16 全套回归证明恢复后行为未丢失。

事故原因是编辑工具误操作，**不归因于 UBA 或构建环境**。

## 4. 已获得的证据

最终代码与保存资产回归已经获得：

- `DengYingShanHaiEditor Win64 Development` 编译成功；项目代码无编译错误；
- 全项目 C++ Automation 7/7：M1 3/3、Phase1 回归 4/4；Cook 依赖修复后的最新报告位于 `Saved/Automation/M1-CookFix/index.json`，修复前最终回归报告位于 `Saved/Automation/M1-Final/index.json`；
- M1 资产独立重载出现 `DY_M1_VERIFIED`，0 error / 0 warning；
- Phase1 资产回归出现 `DY_PHASE1_VERIFIED`，0 error / 0 warning；
- 真实 D3D12/SM6 的 `Project.Maps.PIE` 1/1，通过 11.38 秒地图启动/退出与交互帧率等待，报告位于 `Saved/Automation/M1-Final-MapsPIE/index.json`；
- Map Check 为 0 error / 0 warning；运行时 GameMode 为 `DYStageGameMode`，Explore Context 只应用一次；
- Manipulate Context 精确包含 `E/A/D/R` 四个 Dev 映射，`A` 只有一个 Negate，其他无 Modifier；
- Director 显式引用 LightRig 与 P01 Definition；`BP_DYStagePresentation` 显式引用 Director 与 StageEnvironment，并把 P01 Resolve 映射为 `SunAwakened`。Movable Spot Light、真实投影、手动曝光锁定和 Dormant 零强度均通过保存资产检查。
- 2026-10-02 M2-B 架构迁移后，M1 保存资产再次独立重载：6 个生成 Actor、`DY_M1_VERIFIED`、0 error / 0 warning；全项目 C++ Automation 11/11 通过；限定 `LV_InteractionLab` 的真实图形 PIE 1/1 通过，Map Check 0 error / 0 warning，未出现 Presentation 缺少引用错误。
- 2026-10-02 视觉回归修复后的全项目 C++ Automation 7/7，通过报告位于 `C:\UEBuildArtifacts\DengYingShanHai\Automation\M1-VisualFix-20261002\index.json`；独立资产重载为 0 error / 0 warning；
- 修复后的编辑器与独立包 D3D12 截图一致；临时编辑器曝光截图已在确认后清理，保留的交付证据位于第 7 节产物的 `DengYingShanHai/Saved/Screenshots/Windows/HighresScreenshot00000.png`。画面能辨认灯、偶、承影墙、地面和阴影，且没有屏幕调试文字、青色轨道、绿色目标球或被镜头裁切的世界空间标签。

Windows Development 封装包及独立启动证据已写入第 7 节。人工体验仍必须按第 5 节完成；自动化不能替代主观可读性与操作手感确认。

## 5. 人工 M1 PIE 验收单

打开 `LV_InteractionLab`，点击 Play。正常视觉验收保持默认调试关闭；只有诊断判定参数时才使用 `-DYDebug` 启动，按顺序检查：

- [ ] 开局能在合理视角内发现灯、固定皮影占位和承影墙；无需绕场寻找核心互动；
- [ ] 准星/视线对准灯具后按 `E` 能进入操纵态，未对准时不会误控其他 Actor；
- [ ] 操纵态中 Explore Context 已移除：`A/D` 只移动灯，不同时移动角色；
- [ ] 灯只沿可见调试轨道移动，0–1 两端受限，不越界、不漂移；
- [ ] 幕后灯具移动时，幕上真实 UE 阴影连续改变，固定皮影本体与幕上结果能同时读懂；
- [ ] 手动曝光保持稳定，不因灯位变化产生明显呼吸、过曝或把影子洗掉；
- [ ] `Current` 随灯位连续变化；`Target=0.680`、进入/退出容差和状态显示正确；
- [ ] 进入目标区后开始 Holding；小幅离开但未越过 ExitTolerance 时不抖动取消；越界后清零并回到 Searching；
- [ ] 保持约 1.25 秒后只 Resolve 一次，`ResolveCount` 保持 1，成功灯光变化清楚但不冒充正式演出；
- [ ] Resolve 后继续按 `A/D` 不会破坏结果；操纵态按 `R` 可回到初始灯位、清空判定并再次完成；
- [ ] 完成前按 `E` 退出后角色移动/观察恢复；再次聚焦进入不会出现双倍输入；
- [ ] 连续执行“进入 → 移动 → 退出 → 再进入 → 重置 → 完成”至少 3 轮，无卡死、空引用、重复委托或输入上下文残留；
- [ ] 幕后与幕上在同一操作视图内同时可读；若必须频繁转身才能理解因果，则记录为机位失败；
- [ ] 当前灰盒没有被误判为正式视觉质量；只评价机制、可读性、稳定性和镜头关系。

记录时补充：测试日期、操作者、分辨率、窗口模式、输入设备、平均/最低帧率观察、异常、截图或录像路径。

## 6. M1 关闭结论与进入 M2 的门槛

2026-10-02，用户确认上述 9 项人工 PIE 检查全部正常，随后确认修复版独立包运行无问题、键鼠映射无问题，并明确确认 15 Hz。由此：

1. ADR-006 接受 15 Hz；
2. ADR-010 接受当前 PC 键鼠基线；
3. M1 人工与独立包门槛已通过，允许进入 M2；
4. 语义 Action、互斥 Context 和可替换映射仍是架构边界；
5. 阴影、幕布和曝光的最终美术参数仍须在正式资产进入后重新做视觉回归，不随 M1 关闭自动固化。

进入 M2 不授权复制三套状态机、导入正式大包或把未确认的 `Dev/` 视觉实验迁入正式内容目录。

## 7. Windows Development 包证据

最终有效产物来自提交 `052d2c8`，项目版本为 `0.2.1-m1-visual-fix`：

```text
C:\UEBuildArtifacts\DengYingShanHai\M1-0.2.1-visual-fix-052d2c8\Archive\Windows
```

自动验证结论：

- UAT 的 Build、Cook、Stage、Package、Archive 全部完成，ExitCode=0，结尾为 `BUILD SUCCESSFUL`；
- Cook By the Book 以 `LV_InteractionLab` 为显式根，`IsCookAll=false`，501 个包进入最终 IoStore；
- IoStore 响应清单明确包含目标地图、Explore/Manipulate 两个 Mapping Context 和 6 个 Input Action；
- 归档目录启动 15 秒，bootstrap 与实际 Game 进程均持续响应；
- 运行时使用 D3D12/SM6，项目版本正确，`DYStageGameMode` 正确，目标地图完成加载；
- 日志出现 `Applied Explore input context once at priority 0.`，项目级错误/警告为 0；
- 唯一运行警告来自 NVIDIA 592.01 驱动：UE 自动禁用对 610.00 以下驱动不安全的 TSR 16-bit VALU 路径，不属于项目逻辑或资产缺陷；
- 运行证据日志位于 `Archive/Windows/DengYingShanHai/Saved/Logs/DengYingShanHai.log`；
- 分发文件（不含启动后生成的 `Saved`）共 48 个、1,021,632,492 bytes。当前是 Development 证据包，不代表最终 Shipping 包体目标。

主要产物 SHA-256：

| 相对 `Archive` 的路径 | Bytes | SHA-256 |
|---|---:|---|
| `Windows/DengYingShanHai.exe` | 171,520 | `46301cb8e69caaa5030c008cd2b989a51e72c8bb9507a3955d105118f750b9bb` |
| `Windows/DengYingShanHai/Binaries/Win64/DengYingShanHai.exe` | 332,055,552 | `d91b1b9a797d3623ef1ebbbcd1853f646418d6f66f7b9a4d38e03bcaa2016606` |
| `Windows/DengYingShanHai/Content/Paks/DengYingShanHai-Windows.pak` | 11,229,703 | `8be53bbc5d2daab9d7c11b5d490a3504430943f157fd0e945868f21aea78fe18` |
| `Windows/DengYingShanHai/Content/Paks/DengYingShanHai-Windows.ucas` | 199,947,696 | `8f73acd0bdeb000f328db8ea649660d6ba30e269bbc55ba07785311e933517fd` |
| `Windows/DengYingShanHai/Content/Paks/DengYingShanHai-Windows.utoc` | 189,847 | `0863fc5437bf590f0cdfb482cd12ee5353f217c10908faf3612a2cf6c6868e90` |
| `Windows/DengYingShanHai/Content/Paks/global.ucas` | 3,213,808 | `4cd3e20dcbd098b02d2af2aa14c85c1eb4c862876ee7004a3c4260ce86fbb92b` |
| `Windows/DengYingShanHai/Content/Paks/global.utoc` | 794 | `0401663e9673a47b22942c79fd5d1a235bf4792016018ae011ddb6271c58cc03` |

第一次从提交 `0d4de49` 生成的包成功加载地图，但封装日志发现输入资产未被 Cook。根因是 Pawn/Controller 对必需输入资产使用运行时软路径，没有形成 Cooker 可追踪的依赖。修复提交 `89b901b` 将这些小型、启动必需的资产改为 CDO 硬引用，同时保留 `EditDefaultsOnly` 替换能力，并增加 ClassDefaults 回归断言。失败包在问题与证据记录完成后已清理，不得分发或验收。

提交 `89b901b` 的 `0.2.0-m1-dev` 包随后在真实画面复查中暴露两项回归：手动曝光下基础照明过低导致首屏近黑，以及 Director/世界空间标签默认输出开发调试导致左上角文字和轨迹干扰。`052d2c8` 恢复可读的物理曝光与基础补光、提高 Dev 主灯/成功反馈可见度、移除 M1 世界文字、隐藏 Phase 1 遗留标签，并把 Director 调试改为显式启用和限频显示。因此 `0.2.0-m1-dev-89b901b` 已被废止并清理，不得继续用于展示或验收。

2026-10-02，用户从修复版独立包完成运行复查并确认“新版的运行无问题”。清理时删除两个废止构建目录、修复构建中与 `Archive` 重复的 `Stage` 目录及四张临时编辑器曝光截图，共释放 5,110,294,567 bytes；当前修复版 `Archive`、运行日志、包内截图和 Automation 7/7 报告均保留。

自动启动不能替代人工通关。当前仍须由用户从上述最终目录运行 `DengYingShanHai.exe`，按第 5 节完成一轮；未经这一步，不得宣称“独立包完整互动验收通过”。

## 8. 可重复命令

资产生成：

```powershell
& 'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe' `
  'C:\UEProjects\DengYingShanHai\DengYingShanHai.uproject' `
  -run=pythonscript `
  '-script=C:\UEProjects\DengYingShanHai\Scripts\Create-M1DevSlice.py' `
  -unattended -nop4 -nosplash -NullRHI -NoSound
```

独立资产验证：

```powershell
& 'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe' `
  'C:\UEProjects\DengYingShanHai\DengYingShanHai.uproject' `
  -run=pythonscript `
  '-script=C:\UEProjects\DengYingShanHai\Scripts\Verify-M1DevSlice.py' `
  -unattended -nop4 -nosplash -NullRHI -NoSound
```

成功必须以日志中的 `DY_M1_VERIFIED` 为准，不能只看进程退出码。

Windows Development Build/Cook/Stage/Package/Archive：

```powershell
& 'C:\Program Files\Epic Games\UE_5.8\Engine\Build\BatchFiles\RunUAT.bat' BuildCookRun `
  '-project=C:\UEProjects\DengYingShanHai\DengYingShanHai.uproject' `
  -noP4 -targetplatform=Win64 -clientconfig=Development `
  -build -cook -stage -package -archive -pak -iostore `
  '-map=/Game/DengYingShanHai/Dev/Interaction/LV_InteractionLab' `
  '-stagingdirectory=<unique-output>\Stage' `
  '-archivedirectory=<unique-output>\Archive' `
  -unattended -noxge '-UbtArgs=-NoUBA'
```

每次构建必须使用新的输出目录，并以源码提交短哈希命名；不得覆盖旧证据。成功后仍须检查封装日志中的项目级错误、Cook 清单和实际启动结果。
