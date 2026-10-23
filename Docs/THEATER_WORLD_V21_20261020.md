# 灯影山海 · V2.1 剧场世界重构执行记录（2026-10-20）

> 依据：`C:\Users\lenovo\Downloads\灯影山海_V2.1_剧场世界重构_GitHub资源与DSH执行总案.md`
> 规格链：`specs/001-theater-world-v21/{spec,plan,tasks}.md` + `.specify/memory/constitution.md`
> 结论：V2.1 的 P0（剧场外壳、山海外景、菜单成为正式入口、P03→外景复绿、重新打包）已全部实现并在 Development 真机与 Shipping 包内验证；外景美术仍是 blockout 级。

## 1. 与 plan.md 的一处偏离（已知并接受）

plan.md 要求"先在隔离预览图 `LV_DY_TheaterWorld_Preview` 里搭外壳，再合回主图"。
实际执行改为**直接在 `L_DY_Main` 内脚本化搭建**，原因：

1. 外壳必须贴合既有幕布/台框（X≈900–950）与观众席 mockup（X=1350），复制整个舞台到预览图成本高、易漂移；
2. 全部新 Actor 带 tag `DYTheater`、label 前缀 `DYTheater_`，构建脚本幂等（先删后建），可随时整体重建；
3. 改前已备份 `Saved/Audit-2026-10-20-V21/backup/L_DY_Main.umap` 并记录 SHA256。

## 2. 剧场外壳（`DYTheater_` 共 211 个 Actor，另加 `DYSky_Dome`）

| 组 | 数量 | 说明 |
|---|---:|---|
| Floor / FloorApron | 1 / 1 | 主体地板 4000×2600，台前副台 |
| Wall / Wainscot / Pilaster | 2 / 2 / 16 | 侧墙 Y=±1300、护墙板、8 对壁柱 |
| RearWall / GatePost / GateLintel / GateStep | 3 / 2 / 1 / 1 | 后墙留门洞 Y∈[-510,90]、Z∈[0,900]，对齐后台走廊 Y=-210 |
| FrontWall / FrontGateDoor | 3 / 1 | 前门（观众席背后），本轮不作为进线 |
| Beam / Rafter / Roof | 4 / 8 / 3 | 顶梁 Z=1750、椽条 Z=1820、瓦顶 Z=1900；Roof_A/B/C 之间在 X∈[500,1150] **不铺瓦**，给主灯投影留天空通路 |
| Proc / Curtain | 4 / 2 | 台口柱 Y=±820、台口梁、台口冠、两侧垂幕 Y=±1180 |
| Riser / AudienceRail / RailPost | 3 / 1 / 5 | 观众席三级踏步 + 栏板 |
| Lantern / LanternCord / LanternLight | 14 / 14 / 14 | 吊灯笼（球体 + 发光材质）与暖光点光 |
| Sconce / SconceLight / HallBounce | 6 / 6 / 1 | 观众席壁灯与大厅反弹光 |
| Sun | 1 | DirectionalLight，100000 lux，Rotator(-38,145,0)，色 (255,238,214)，ForwardShadingPriority=1 |
| ExtGround / ExtPath | 1 / 1 | 外景地面 14000×14000、石板路 4000×500（门洞对齐 Y=-210） |
| PathLantern / PathLamp / PathLight | 12 / 12 / 12 | 石板路两侧石柱、灯头与点光 |
| DeadTree / DeadCanopy | 14 / 14 | 枯树，tag `DYExterior_DeadTree`；树冠另带 `DYExterior_Canopy`（P03 复绿用） |
| Rock / Mountain | 10 / 16 | 散石（|Y|≥1500，避开进门视线）、B/C 环远景山锥（半径 9000–14000） |

关键空间量级：主体约 40 m(X) × 26 m(Y) × 19 m(Z)；台口 X≈880；后门 X=-1800；外景石板路从 X=-5600 延伸到门口。

### 显式隐藏（物体不动）
`DEV_LeftBoundary`、`DEV_RightBoundary`、`DEV_CameraWall`、`DEV_InnerCornerA/B`、`DEV_LowCeiling`、`DEV_LowCeilingPostA/B` —— 旧灰盒隔墙在外壳内会被看到，进游戏时隐藏，演出坐标零改动。

### 天空与外景照度
- `DYSky_Dome`：半径 130 m 的 StaticMesh 球，材质 `MI_DY_SkyDome`（父材质 `M_DY_SkyDome`：SkyColor × SkyIntensity → Emissive，**Unlit + TwoSided**）。第 2 轮把它从 Lit 改 Unlit，因为 Lit 材质的内表面被 100000 lux 太阳打亮成白墙。
- **必须 NoCollision**：球体半径 130 m，若保留 BlockAll，玩家传送/出生到球内会被"反穿插"弹到 130 m 外，表现为画面全黑（这一坑排查了 4 轮，见 §6）。
- 主图后处理是 `AEM_MANUAL`、bias 3.5 的固定曝光（`M2_PostProcess_ExposureLock` 已 unbound），所以室外只有真实日照量级（100000 lux）能被看见；5000 lux 及以下全黑。这是当前"室外偏夜、室内靠灯"的原因，也是后续美术要统一的地方。

## 3. 菜单成为正式入口

| 改动 | 文件 |
|---|---|
| 主图开局用 `ADYReleaseEntryPlayerController`（按地图身份而不是配置节） | `Source/DengYingShanHai/Private/Core/DYStageGameMode.cpp`（`InitGame` 里 `UWorld::RemovePIEPrefix(MapName)` 含 `L_DY_Main` 时替换 `PlayerControllerClass`）、`Public/Core/DYStageGameMode.h` |
| 菜单资产进 Cook 范围 | `Config/DefaultGame.ini` 增加 `+DirectoriesToAlwaysCook=(Path="/Game/DengYingShanHai/UI/Menu")` |

六牌匾闭环（Development 与 Shipping 包均已验证）：

| 项 | 行为 |
|---|---|
| 开始游戏 | `Director->StartManualSequence()`，进 P01 引日启幕 |
| 继续游戏 | 仅对**内存中的暂停会话**开放；冷启动为禁用态（深灰底 + 浅字，可读） |
| 演出篇章 | 只读列出三幕题签 + "后续篇章：制作中"，不跳关 |
| 游戏说明 | 按键与三次互动说明 |
| 设置 | 主音量 / 窗口模式 / 分辨率，改即预览；15 秒未确认自动还原；"确认设置"写 `UGameUserSettings` |
| 退出游戏 | `RequestQuitExperience()` |
| Esc | Play 态暂停回菜单，再按继续；菜单态 Esc 由 Widget 处理，不到 PlayerController（0.35 s 去抖防一次按键触发暂停+继续） |

禁用态实现教训：`SButton` 的 Disabled 分支 + 禁用纹理在本机表现为"灰板无字"；最终改为**恒 enabled、只换禁用样式（`MakePlaqueBrush` 的 tint 生效）+ 文字色改浅宣纸色**。另修掉 `MakePlaqueBrush` 传纹理时丢弃 Fallback 颜色的老 bug。

## 4. P03 杖落成林 → 外景复绿（V2.1 唯一世界联动）

- 实现：`Source/DengYingShanHai/Private/Stage/DYStageEnvironment.cpp`
  - `ApplyState(ForestComplete)` → `TriggerExteriorGreening()`；回到 `Dormant` → `ResetExteriorGreening()`；
  - 扫描一次带 `DYExterior_DeadTree` + `DYExterior_Canopy` 的 StaticMeshActor，建 14 个 MID，`ExteriorDeadTint(0.26,0.22,0.17) → ExteriorAliveTint(0.07,0.50,0.10)`，4 秒渐变（World TimerManager，不用 Tick，因为 BP 子类 `bCanEverTick=false`）；
  - 同时 2D 播放风声 + 树叶/鸟声并 3 秒淡入（`SFX_DevWind`、`SFX_DevForestLeaves`）；
  - 不读 Puzzle Director、不逐帧扫描世界，符合 AGENTS.md 第 19 条。
- Shipping 兼容：`GetActorLabel()` 在 `WITH_EDITOR=0` 不可用（曾 `error C2039`），改为判 Actor 标签。
- 开发验证命令（仅非 Shipping）：`dy.ForceForestComplete` 每 6 秒重推 `ForestComplete`、96 秒自停；否则 `DYStagePresentation::ApplyFiveStateEnvironment()` 会用导演快照（Act0/Dormant）把它打回。
- 证据：`Saved/Audit-2026-10-20-V21/p03-before-green.png`、`p03-after-green.png`（14 棵树冠由褐转绿，树干/灯笼/山体不变），日志 `[DYExterior] greening 14 canopies over 4.0s` → `greening complete tint=(0.07,0.50,0.10) mids=14`。

## 5. 构建与复现

- 世界搭建（幂等）：GUI 编辑器 + 环境变量 `DY_SCRIPT=C:\dy_build\build_all.py`（内部依次跑 `build_theater.py` 与 `add_sky.py`），项目级钩子 `Content/Python/init_unreal.py` 在约 240 tick 后执行并打印 `DY_SCRIPT DONE`；跑前先 `Stop-Process UnrealEditor`，否则保存报 `Error moving file ... (Error Code 32)`。
- C++：`Stop-Process UnrealEditor` → 拷 `Source` 到 `C:\dy_build\Source` → `cmd /c C:\dy_build\rebuild.cmd`（看 `C:\dy_build\build5.log` 的 `Result: Succeeded`）→ 回拷 `UnrealEditor-DengYingShanHai.dll` 与 `UnrealEditor.modules` 到 `D:\灯影山海\Binaries\Win64\`。
- 真机机位：`ADYDevEntryPlayerController::ApplyDebugReviewView()`，`DY_DEBUG_VIEW=1..8` 选起始机位，游戏内 `PageDown/PageUp` 循环（**不要用 F1–F8**，那是引擎的视图模式热键，F5 会把画面切成 ShaderComplexity）。
  1 门外接近 / 2 门厅 / 3 后排看台口 / 4 台上回看观众席 / 5 外景树林 / 6 外景大全景 / 7 观众席后全景 / 8 侧廊。
- 截图：`C:\dy_build\cap6.ps1 <pid> <png>`（DPI 感知 + 客户区，唯一可信）；按键注入 `C:\dy_build\keys.ps1 <pid> "<hex VK 列表>"`；鼠标合成点击在本机始终无效，UI 自动化走 `dy.MenuAutoTest` / `DY_MENU_AUTOTEST`。

## 6. 本轮踩坑（下次直接跳过）

1. `UnrealEditor-Cmd.exe -run=pythonscript` 日志报成功但**没有执行**脚本 → 一律走 GUI 编辑器 + `init_unreal.py` 钩子。
2. 天空穹顶球体保留 BlockAll → 玩家被弹到 130 m 外，画面全黑（`trace pawn` 才看出来的）。必须 `set_collision_profile_name('NoCollision')`。
3. 穹顶材质是 Lit + 默认 0.5 BaseColor → 被 100000 lux 太阳打亮成白墙；改 Unlit 后正常。
4. `SetActorTickEnabled(true)` 对 `bCanEverTick=false` 的 BP 子类无效；渐变要用 Timer。
5. `GetActorLabel()` 在 Shipping 编译不过，判标签。
6. F1–F8 在 game viewport 里被引擎当视图模式热键。
7. 旧灰盒隔墙在外壳内仍可见，需 `set_actor_hidden_in_game(True)`。

## 7. 仍未完成（交接给下一步）

- 外景美术仍是 blockout：树冠是球、山是锥、地面是纯色；V2.1 §外景 C 环远景（雾、云、山影剪影）未做。
- 曝光冲突未解：室内固定手动曝光适合灯火，室外被压成夜。若要做"白天山海"，需要给外景单独的 PostProcessVolume 曝光或引入自动曝光分区。
- "真实通关到 P03"的端到端复绿仍未在真机跑通：逻辑链路由自动化覆盖（172/172，含 "Only accepted proof establishes ForestComplete"、"Resolve is FinaleReady, never ForestComplete"），视觉渐变由 `dy.ForceForestComplete` 证明；真实通关需完整三幕操作，尚未执行。
- 外景资源候选（R01 KayKit 等）未下载、未登记许可；本轮全部为程序化自建，无第三方资产。

## 8. 外景美术 pass5（Run4，2026-10-20 04:5x）

在 `C:\dy_build\build_theater.py` 里把外景从"完全相同的一套复制品"改成有变化的夜景：

- **树形变化**：`trunk_h=620+(seed%4)*90`、`trunk_w=62+(seed%3)*10`、`canopy_d=380+(seed*53%5)*46`、`jitter=((seed*37)%7-3)*14`（`seed=i*3+k`），树冠 Z 抬到 `trunk_h + canopy_d*0.30`，高度压扁到 `canopy_d*0.72`。
- **月亮**：`M_DY_MoonGlow`（Unlit+emissive）→ `MI_DY_Moon`，球体 `DYTheater_Moon` 在 `(-7600, 5200, 6400)`，直径 900。
- **中景山脊**：10 座 `DYTheater_Ridge_*`，`ang2=i*36+12`、`rad2=5200+(i%3)*900`、尺寸 `(3600,3600,1200+(i%5)*420)`，补上远景与近景之间的层次。
- **天穹**：`DYSky_Dome` Unlit、`NoCollision`，`SkyColor=(0.05,0.08,0.14)`、`SkyIntensity=2.0`。

结果：`DYTheater_*` 222 个，地图 665,725 字节 / SHA256 `98043673…9B31`，重建日志 `Saved/Logs/BuildAll4.log`（`CREATED 222` / `SAVED MAP` / `SKY OK`）。机位证据 `Saved/Audit-2026-10-20-V21/pass5-05-grove.png`、`pass5-06-wide.png`。包：Run4（见 `Docs/FORMAL_SHIPPING_20261020.md`）。

仍未解决：外景整体仍偏暗（手动曝光锁 3.5，室外只有 100000 lux 太阳与月亮可见）；树林区有几条细白斜条未查明来源（疑似灯具自发光面片在斜视角下的高光）。
## 9. 外景起步：从山海走进戏台（Run6，2026-10-20）

> 用户原话（m04598）：「玩家点开始游戏后，不是直接出现在戏台前，而是在戏场外（在山海世界），随着指引去往戏台的」。

### 9.1 空间

- `PlayerStart` 从 `(-900,-210,120)` 迁到外景 **`(-4600,-210,60)`、Yaw=0**，正对后门；全场只有这一个 PlayerStart。
- 路线：外景灯径（石板路 X∈[-5600,-1880]、Y=-210）→ 后门 `X=-1800`（门洞 Y∈[-510,90]、Z∈[0,900]）→ 40 cm 门槛（`StaticMeshActor_86`）→ 大厅地板 Z=0。门内外高差 40 cm 小于 `MaxStepHeight` 45，可直接走过去，不需要跳跃或交互。
- 步行距离约 28 m，正常 W 前进 8 秒左右进门；外景与大厅共用一台固定手动曝光，所以室外是夜、室内是灯火。

### 9.2 只照"往哪走"的四盏灯

外景原本只有月亮与远景灯柱，玩家出生点附近没有地面照度。`C:\dy_build\entry_walk.py` 除挪 PlayerStart 外，幂等补四盏无阴影暖光（tag `DYTheater`，算进 226）：

| Actor | 位置 | 强度 / 半径 |
|---|---|---|
| `DYTheater_EntryLamp_L` | `(-4460, 90, 320)` | 2600 / 1000 |
| `DYTheater_EntryLamp_R` | `(-4460, -510, 320)` | 2600 / 1000 |
| `DYTheater_GateLamp_L` | `(-2020, 120, 470)` | 5200 / 1300 |
| `DYTheater_GateLamp_R` | `(-2020, -540, 470)` | 5200 / 1300 |

效果：石板路被两对暖光"分段点亮"，一直指到门里发亮的幕布，形成天然的路径引导，不额外加箭头或 UI 标记。

### 9.3 引导与 HUD 分层（C++）

- `ADYDevEntryPlayerController::BeginEntryWalkGuidance()`（菜单"开始游戏"被接受后调用）：
  - `Hud->SetStageHudVisible(false)`：隐藏题签、提示底板、准星、状态/就绪/保持进度；菜单与引导句保留；
  - `ShowTransientHint(UDYInteractionHUDWidget::GetEntryWalkHint(), 10.0f)` → 中央「沿灯径向灯火深处走去，入戏台」；
  - `EntryWalkHandle` 每 0.25 s 跑 `HandleEntryWalkCheck()`，`EntryWalkTimeoutHandle` 60 s 兜底调 `RestoreStageHud()`。
- `HandleEntryWalkCheck()`：`ControlledPawn->GetActorLocation().X > -1700` 即判定入戏台 → 清两个 timer、`SetStageHudVisible(true)`、`ShowTransientHint("入戏台", 4.0f)`，并记 `Entry walk: player crossed into the theater at ...`。
- `EndPlay` 清 `EntryWalkTimeoutHandle`，避免换图后定时器回调到已销毁对象。
- HUD 侧：`UDYInteractionHUDWidget::SetStageHudVisible(bool)` 只切舞台专属元素（`TitleText`/`PromptBack`/`Crosshair` 用 `HitTestInvisible`↔`Collapsed`，`Status`/`Readiness`/`HoldProgress` 再与 `bStageHudVisible` 取与）；`ADYInteractionHUD` 转发。

### 9.4 验证

| 场景 | 证据 | 结果 |
|---|---|---|
| Shipping 冷启动 → 开始游戏 | `Saved/Audit-2026-10-20-V21/run6-outside.png` | 站在外景石板路上，前方是亮灯的后门与门内幕布；中央引导句；舞台 HUD 全隐 |
| 走进大厅 | `run6-hall.png` | 题签「引日启幕」、准星、右下状态框恢复，「入戏台」回执弹出 |
| 编辑器 -game 连拍 | `C:\dy_build\shots\ew4-1-spawn.png`、`ew4-2-path.png`、`ew4-3-hall.png` | 同上；日志 `Entry walk: player crossed into the theater at V(X=-1679.07, Y=-210.00, Z=97.93)` |

### 9.5 已知偏差与坑

1. 外景阶段左上角仍有 Blueprint 给的「操纵灯，用 A / D 将头部影子送入浅色缺口…」。该句由 `BP_DYThreeActPresentation` / `BP_DYReadabilityPresentation` 在运行时喂给 WBP，C++ 拿不到句柄（关卡里的 presentation actor 没有 WidgetComponent），本轮**不处理**，需要在 Blueprint 里按"演出是否开始"控制可见性。
2. `PlayerStart` 改位后，任何依赖出生点 `(-900,-210,120)` 的调试机位/脚本都要重新看一遍；`ApplyDebugReviewView()` 的 8 个机位是绝对坐标，不受影响。
3. 打包版 `-abslog` 指向含中文的路径会被吞掉，运行期拿不到日志；排查用编辑器 -game 或改成 ASCII 路径。

## 10. 结束态（复演已成）菜单一致性（Run7 追加）

### 10.1 现象与根因

`DYFormalCaptureDir` 的三幕通关截帧里，结束面板左列出现的是「章节选择」+ 图标版旧菜单，与现行「演出篇章」版矛盾。
根因不是隐藏了某个 Widget，而是**底图原画自带一列菜单**：`T_MenuBackground` 画的就是 V2.2 参考稿，左列六项（开始游戏 / 继续游戏 / 章节选择 / 游戏说明 / 设置 / 退出游戏）与右下「游戏说明」纸卡都烤在贴图里。Slate 牌匾平时正好把它们盖住，而 `UDYDevEntryWidget::RefreshView()` 在 `End`/`Reloading` 面板把 `MenuColumn` 与 `GuidePanel` 设成 `Collapsed`，原画旧列就露出来了。

### 10.2 修法

1. `MenuColumn`、`GuidePanel` **不再随结束态收起**（始终 `SelfHitTestInvisible`），由 Slate 盖住原画旧列；
2. 结束卡里的独立按钮改为 `Collapsed`，把"重新复演"落在**菜单列首牌位**（`PrimaryLabel`）上：
   - `IsMenuItemAvailable(0)` → `bStartPanel || CurrentPanel == EDYDevEntryPanel::End`；
   - `HandleMenuSelection(0)` → `End` 面板调 `RequestReplayExperience()`；
   - `HandlePrimaryClick()` 允许 `End`；`SetWidgetToFocus(PrimaryButton)` 保证 Enter 可直接重演；
3. 结束语缩短为一行（原句会把结束卡撑宽、压到右下引导卡上）。

### 10.3 验证

| 项 | 证据 | 结论 |
|---|---|---|
| 结束面板（编辑器 -game，`DY_MENU_PANEL=end`） | `Saved/Audit-2026-10-20-V21/run7-ending-panel.png` | 左列首牌「重新复演」为可用态并盖住原画旧列，其余五项禁用；结束卡不再压到右下引导卡 |
| 自动化 | `Saved/Logs/AutomationV21f.log` | 172/172 Success |
| Shipping 回归 | `run7-menu.png` / `run7-outside.png` / `run7-hall.png` / `run7-pause.png` | 四点与 Run6 一致，结束态改动不影响开局面板 |

`DY_MENU_PANEL=end` 是**仅非 Shipping** 的调试开关（`bPreviewEnding`，`#if !UE_BUILD_SHIPPING` 包住），Shipping 二进制不含。

## 11. V2.3 四幕剧场（Run19–Run85，2026-10-20 → 2026-10-21）

用户下达 V2.3 总指令（四幕独立可玩、共用一座戏台、四幕连演有真结局）后，本日把「三幕一戏」升级为「四幕连演」，并把演出篇章做成真正的章节入口。

### 11.1 四幕 = 四个「三步」章节，而不是改状态机

Director 的既有语义是「恰好三幕」（`ValidateActSequence` 写死 `ActSequence.Num() != 3` 即失败，`ThreeAct.*` 自动化断言也依赖它）。V2.3 不推翻这套机器，而是把它复用四次：

| 章 | 幕名 | 三步来源 | 定义资产 |
|---|---|---|---|
| 第 1 章 | 夸父逐日 | 地图实例里现成的 `ActSequence`（引日启幕 / 逐光成形 / 杖落成林） | `DA_DY_P01_SunAwakening`、`DA_DY_P02_ChaseForm`、`DA_P03RuntimeCandidate`（Dev 路径，原样沿用） |
| 第 2 章 | 精卫填海 | `EnsureCampaignChapters()` 运行时 `NewObject<UDYPuzzleDefinition>` 现造 | `P04_Jingwei_01..03`（内存对象，不落 .uasset） |
| 第 3 章 | 刑天舞干戚 | 同上 | `P05_Xingtian_01..03` |
| 第 4 章 | 烛龙昼夜 | 同上 | `P06_Zhulong_01..03` |

- 数据结构：`DYActSequenceTypes.h` 新增 `FDYChapterEntry{ FText ChapterTitle; FText ChapterSubtitle; TArray<FDYActSequenceEntry> Steps; }`；`FDYActSequenceSnapshot` 增加 `ChapterIndex / ChapterCount / ChapterTitle`。
- 开关：`DYPuzzleDirector.h` 的 `UPROPERTY(EditInstanceOnly) bool bFourActCampaign = false`。默认 false ⇒ 所有自动化 fixture 行为不变；主图实例已置 true（编辑器 Python 里蛇形名 `four_act_campaign`，`bFourActCampaign` 会抛属性错误）。
- 切换：`StartCampaignChapter(Index, Requester)` 把 `ActSequence` 换成该章的 3 条，再把 `CurrentActIndex` 归位并走原有 `StartCurrentPuzzle()`。因此 `Num()==3` 永远成立。

### 11.2 章节推进：BP 提交优先，C++ 兜底

1. `AcceptFinaleCompletion()` 若发现「本幕是终幕且还有下一章」→ `AdvanceCampaignChapter()`（换章 + 起下一章第一步），否则才 `SetSequencePhase(Complete)`。
2. 兜底定时器：进入 `AwaitingFinale` 后 `ScheduleCampaignChapterFallback()`，第 1 章等 40 s、其后每章 8 s；到点仍在 `AwaitingFinale` 就强制推进。这样即使 BP 演出因为「只认识三幕」不提交，连演也不会卡死。
3. 只有第四幕落幕才会 `Complete`，菜单回到 `End` 面板（「复演已成」+ 首牌「重新复演」）。

### 11.3 每幕调色板（`DYPuzzleDirector.cpp` 的 `DYCampaign::GetPalette`）

`ApplyChapterPalette()` 在 `BeginPlay` 与每次 `StartCurrentPuzzle()` 调用，做两件事：给名字含 `Sky_Dome` 的 `AStaticMeshActor` 建 `UMaterialInstanceDynamic` 并写 `Horizon` / `Zenith` / `SkyIntensity`；给名字含 `ExtFog` 的 `AExponentialHeightFog` 写 `SetFogDensity`。不改资产、不存盘。

| 章 / 步 | Horizon | Zenith | SkyIntensity | FogDensity |
|---|---|---|---|---|
| 第 1 章 夸父（默认） | (0.10, 0.14, 0.24) | (0.05, 0.08, 0.16) | 60 | 0.008 |
| 第 2 章 精卫 | (0.05, 0.26, 0.32) | (0.02, 0.10, 0.22) | 66 | 0.022 |
| 第 3 章 刑天 | (0.36, 0.12, 0.07) | (0.14, 0.04, 0.04) | 58 | 0.014 |
| 第 4 章 烛龙 · 第 1 步（夜） | (0.02, 0.03, 0.07) | (0.01, 0.02, 0.05) | 26 | 0.010 |
| 第 4 章 烛龙 · 第 2 步起（昼） | (0.80, 0.70, 0.52) | (0.36, 0.52, 0.70) | 115 | 0.004 |

（第一版数字偏保守，Run20 外景几乎看不出差别；Run21 把第 2/3 章各拉大一档。）

### 11.4 菜单：演出篇章成为真正的章节入口

- `BuildOverlay()` 的行循环从 3 行改 4 行，行标题取 `ADYPuzzleDirector::GetCampaignChapterTitles()`；章节态点行 = `StartChapterFromOverlay(Index)` → `ADYDevEntryPlayerController::RequestChapterExperience(Index)`。
- 进浮层即把键盘焦点放到第一行（否则 Esc 关闭后 Enter 只会重开浮层——Run19 截图里就是这么暴露的），Up/Down + Enter 可选幕。
- 说明页按 V2.3 指定文案改写，并补两行非遗内容：锣鼓与器乐（声音只作氛围，谜题不依赖听觉）、四偶图鉴（剧终后影偶留在戏台上）。
- 结束语改为四幕版：「四幕演尽，夸父、精卫、刑天与烛龙的影子都已落定。选「重新复演」或按 Enter 从头再看。」
- 评审钩子：`DY_CHAPTER=N`（Shipping 也生效）让「开始游戏」直接进第 N 幕，用于逐幕视觉验证；不设则从第一幕起。

### 11.5 外景：月亮入画 + 外墙不再死黑

| 项 | 值 / 做法 |
|---|---|
| 月亮位置 | `DYTheater_Moon` 移到 `(781, 739, 2825)`、scale 4.5；从出生眼位 `(-4600,-210,160)` 看是 az≈10°、el≈26°，1920×1200 下位于画面顶部中央且整圆可见 |
| 月亮材质 | `MI_DY_Moon` 的 `Glow` 抬到 (40, 38, 34)、`BaseColor` (1, 1, 0.98) |
| 夜空 | `M_DY_SkyGradient` 改 `two_sided`（球体内表面剔除会让整个天空变黑）+ `MSM_UNLIT`；`MI_DY_SkyDome` 的 `SkyIntensity` 从 2.0 抬到 60（手动曝光 bias 3.5 是给 100000 lux 日光准备的，低亮度夜空会被压成纯黑） |
| 外墙补光 | `DYExt16_FacadeLamp_L/R`：PointLight @ `(-1885, -1180, 780)` / `(-1885, 700, 780)`，intensity 2600、attenuation 1100、MOVABLE、投影。x=-1885 是按地图实测外墙面（`DYTheater_RearWall_Head` minX=-1825）外移 60 cm 定位的——之前 x=-1755 的灯埋在墙体内，所以"看不见" |

### 11.6 「三幕→四幕」是资产级修法（重要）

BP 表现层把提示句照着自己的「三幕」认知写死，C++ 拿不到句柄：

1. 第一版在 `SetEntryIntroCueVisible()` 的文本循环里做 `三幕→四幕` 的 `SetText`；Run22 又加了 0.5 s 定时器兜底 —— 真机仍然显示「依次复演三幕」，说明 BP 每帧/每次状态变化都会重写这句，运行时改字会被覆盖。
2. 最终生效的是**等长 UTF-16 字节替换**：`依次复演三幕` → `依次复演四幕`（6 字 → 6 字，UTF-16 字节数不变，`FString` 的长度前缀不用动，包内其它偏移也不受影响）。落点：
   - `Content/DengYingShanHai/Dev/Readability/Stage/BP_DYReadabilityPresentation.uasset`（2 处）
   - `Content/DengYingShanHai/Dev/ThreeAct/Stage/BP_DYThreeActPresentation.uasset`（2 处）
   - `Content/DengYingShanHai/Dev/ThreeAct/UI/WBP_DYThreeActCue.uasset`（1 处）
   原始文件备份在 `C:\dy_build\asset_backup\`。Run23 真机 `Run23-ch1-hall.png` 已显示「依次复演四幕 · 操作沿用 E / A / D」。
3. ⚠ 这是二进制补丁：一旦在编辑器里重新导入/重存这三个资产，文字会退回「三幕」，需要重打。C++ 里原先那处 0.5 s 定时器规范化（`ADYDevEntryPlayerController::NormalizeCampaignWording`）**已删除**：它把所有 UTextBlock 里的「三幕」无差别替换成「四幕」，把「第三幕 · 刑天舞干戚」也改成了「第四幕 · 刑天舞干戚」（Run28 真机截图暴露）。删除后由资产补丁负责，Run30 起四行标题正确。

### 11.7 验证矩阵（全部为打包 Shipping 版真机截图，1920×1200，`Saved/Audit-2026-10-20-V21/`）

| 画面 | 证据 | 结论 |
|---|---|---|
| 主菜单 | `Run23-menu.png` | 六牌位、副标题、聚焦「演出篇章」正常 |
| 演出篇章 | `Run19-chapters.png` | 四幕清单 + 四行可点 + 提示 + 返回；背景压暗 |
| 外景（第一幕） | `Run23-outside-1s.png` | 夜空、完整圆月、树冠剪影、灯柱纵深、两盏壁灯、门洞灯火 |
| 外景（第二幕） | `Run23-ch1-outside-1s.png` | 天青偏青绿（第 2 幕后调色板真机可见） |
| 大厅（第一幕第一步） | `Run23-hall.png` | 题签「引日启幕」、BP 引导句、幕布/皮影/灯具、底部三行状态、准星 |
| 大厅（第二幕第一步） | `Run23-ch1-hall.png` | 题签「衔石入海」、底部「偶已就位」、左上文案已是「四幕」 |
| 大厅（第四幕第一步） | `Run21-ch3-hall.png` | 题签「夜伏」、底部「灯已就位 · 偶待调整」 |
| 暂停 | `Run23-pause.png` | Esc 暂停面板与继续/重演闭环 |
| 四幕连演→真结局 | `Run25-campaign-087s.png`、`Run27-campaign-087s.png` | 探针 12 步走完四幕（`phase=4 chapter=4/4`），End 面板「复演已成」+ 影偶图鉴四行 +「重新复演」 |
| 外景（Run38 定稿） | `Run38-outside-1s.png` | 入口提示条 + 金线、暖光门脸、18 格窗、月与山影、无重复叠光 |
| 演出篇章（Run38） | `Run38-chapters.png` | 第一/二/**三**/四幕标题正确（验证「第四幕」误替换已修） |
| 第三幕配色 | `Run38-campaign-012s.png` | 主灯转赤，屏面偏暖红 |
| 外景（Run43） | `Run43-outside-1s.png` | 与 Run38 同一版外景，验证该包未回退 |
| 图鉴详情（Run44） | `Run44-codex.png` | 加背景乐后重打包，图鉴仍为「影偶图鉴 · 夸父逐日」 |
| 外景灯柱（Run46） | `Run46-outside-1s.png` | pass31/32 后：灌木缩回真实尺寸、灯柱变瘦柱 + 球灯 + 木灯帽，入口提示条与金线仍在 |
| 帧率探针（Run47） | `Run47-PerfProbe.log` / `Run47-PerfProbe-1920x1200.log`（各 108 行） | `DY_PERF_PROBE=1` 打包实测：1280×720 平均 157.4 FPS；1920×1200 平均 166.5 FPS，均为四幕连演全程 |
| 外景与入口提示（Run47） | `Run47-outside-1s.png` | 灯柱成排带灯帽、门脸暖光、入口提示条 + 金色横线可见 |
| 图鉴详情（Run47） | `Run47-codex.png` | 与 Run44 一致：「影偶图鉴 · 夸父逐日」造型/操演/七步/四条 |
| 锣鼓提示音（Run48） | `SfxProbe.log`（`%LOCALAPPDATA%\DengYingShanHai\Saved`） | `DY_SFX_PROBE=1` 打包实测 9 条：鼓 4（每章开场）、结算音 4（每章第三幕落定）、锣 1（剧终 t=75.5） |
| 设置持久化（Run51） | `Run51-settings-committed.png` / `Run51-settings-persisted.png` + `%LOCALAPPDATA%\DengYingShanHai\Saved\Config\Windows\GameUserSettings.ini` | 提交后 `[DengYingShanHai] VolumeStep=9`；新进程 `probe-loaded t=2.0 vol=9`，设置页显示 9/10 |
| 四幕连演（Run51） | `CampaignProbe.log` / `SfxProbe.log` / `Run51-campaign-087s.png` | `verify_sfx.ps1 -Attempt Run51` 12 步到 `phase=4 chapter=4/4 act=3`；锣鼓 9 条（t=14.9/23.1/31.1/38.7/46.7/54.0/62.0/69.6/75.6）；End 面板含图鉴四行与「退出游戏」 |
| 章节直开（Run52） | `Run52-chapters.png` / `Run52-chapter-hall.png` / `Run52-chapter-act.png` + `SfxProbe.log` | 菜单 Down×2 + Enter 开「演出篇章」，再 Down×2 + Enter 选第三幕；进场标题为「断首犹立」，`cue=1 chapter=2 phase=0` 记到章切换；直开模式不写 `CampaignProbe.log`（该探针只在连演时记录） |
| 退出游戏（Run52） | `Run52-ending.png` + 进程退出 | 结束面板 5×Down + Enter 点「退出游戏」，`WaitForExit(12s)` 返回 True，进程正常退出 |
| 外景树冠与远山（Run53） | `Run53-outside-1s.png` | pass33/34 后：104 个树冠球各补 2 个偏移小冠（共 208 个），路侧轮廓由单球变簇；远山裙 8 座补地平线 |
| 门前修形与四幕影偶（Run55） | `Run55-gate-mid.png` / `Run55-gate-front.png` / `Run55-gate-hall.png` | pass35 删掉 92 个冗余 actor（含 14 块悬空石板），`DYTheater_GateStep` 压到地面；路面连续、门口只剩门楼 + 两侧灯柱 + 门内灯径 |
| 门厅四幕影偶陈列（Run55，已在 Run68 撤回，见 §11.19） | `C:/dy_build/shots35/hall_leftd.png`（左墙夸父/精卫）、`hall_rightd.png`（右墙刑天/烛龙） | 220 × 250 cm 木背板 + 板前 6 cm 的 157 cm 剪影偶（墨色 + 朱红道具 + 铜钩）+ 一盏 900 cd 暖光；编辑器离屏捕获，打包版受构图所限未单独取景 |
| 复演闭环（Run52 / Run53 复测） | `Run52-replay1.png` / `Run52-replay3.png`、`Run53-replay1.png` / `Run53-replay3.png` + `CampaignProbe.log` | `verify_replay.ps1 -Attempt Run52/Run53`：Enter 复演后探针均追加 25 行，从 `chapter=1/4 act=1` 重演到 `phase=4 chapter=4/4 act=3`；第二遍结束面板仍是「复演已成」 |
| 设置 15 s 回滚（Run50） | `SettingsProbe.log` + `Run50-settings-dirty.png` / `Run50-settings-reverted.png` | `DY_SETTINGS_PROBE=1` 打包实测：`probe-dirty t=1.8 vol=9` → `probe-after-timeout t=20.0 vol=10`；截图 9/10 + 「预览中：5 秒…」 → 10/10 + 提示复位 |
| 图鉴复核（Run48） | `Run48-codex.png` | 加锣鼓后重打包，图鉴详情页未回退 |
| 图鉴复核（Run53） | `Run53-codex.png` / `Run53-ending.png` | 外景 pass33/34 后重打包：结束面板仍是「复演已成」+ 图鉴四行，图鉴详情页「影偶图鉴 · 夸父逐日」未回退 |
| 入口提示与章节（Run51） | `Run51-outside-1s.png` / `Run51-chapters.png` | 提示条 + 金线仍在；章节浮层四行依次为第一/二/三/四幕 |
| 入口提示与章节（Run48） | `Run48-outside-1s.png` / `Run48-chapters.png` | 提示条 + 金线仍在；章节浮层四行依次为第一/二/三/四幕 |
| 演出篇章（Run43） | `Run43-chapters.png` | 四行标题正确（浮层不再被进场替换污染） |
| 影偶图鉴页 | `Run43-codex.png` | 结束面板 →「游戏说明」→「影偶图鉴 · 夸父逐日」：造型/操演/制作七步/四条影偶 |
| 图鉴返回 | `Run43-codex-back.png` | Esc 关闭浮层，焦点回「重新复演」 |
| 门厅四偶·墙板（Run64） | 编辑器离屏 `C:/dy_build/shots35/hall_leftd.png` / `hall_rightd.png` | pass36 四块 220×250 cm 木背板 + 板前 6 cm 剪影偶（39 部件）；贴墙 y=±1252，偶面法线朝 ±Y，玩家沿 X 直行只看到侧棱 → 真机不可见 |
| 门厅四偶·立偶（Run65） | `Run65-hall-*.png` | pass37 改门厅两侧独立立偶（48 部件 + 4 灯），位置 (-1450,±620)/(-860,±620)；仍在走廊墙后 |
| 四偶射灯过曝（Run66） | `Run66-outside-1s.png` | 1400 cd 射灯把偶打成白矩形；同包 C++ 把到达时的两条牌匾合成一条 |
| 四偶降亮后消失（Run67） | `Run67-step01..14.png` | 230 cd / 2.1 m 后 0 可见像素；`verify_steps.ps1` 逐秒走查，到达时只剩一块牌匾 |
| 四偶陈列撤回（Run68） | `Run68-campaign-*.png` / `Run68-ending.png` / `Run68-replay*.png` | pass43 删 108 个影偶/标定演员（`left=0`）；四幕影偶只走影偶图鉴 UI；四幕连演 25 行到 `phase=4`、锣鼓 9 条、复演追加 25 行 |
| 入口灯型统一（Run72，前一包） | `Run72-step01..05.png` | 灯径只剩一套「瘦石柱 + 球灯 + 黄铜灯帽 + 宝顶」（12 根）；pass35 补的 8 组矮灯（方块灯身 + 米色锥顶，32 演员）已删，灯的光源全留（`FORMAL_SHIPPING_20261020.md` §9.16） |
| 标题面板可续演（Run73，前一包） | `Run73-fresh-menu.png` / `Run73-continue-menu.png`（+ `-crop3` 对比） | 六牌匾第二块「继续游戏」：无进度时灰底禁用，走过一段后重启变奶油可用态，选中即从上次那一幕续演；进度只记章节（`Saved/DYProgress.txt`），终章落幕后自动清零（`FORMAL_SHIPPING_20261020.md` §9.17） |
| 章节已演标记（Run74，前一包） | `Run74-chapterlist.png`（+ 编辑器 `ChapSeed-2-list.png`） | 「演出篇章」行尾标「（已演）」：`Saved/DYProgress.txt` 增 `PlayedMask` 一位一幕，`MarkChapterPlayed()` 在下一幕开始时记上一幕、剧终记最后一幕；提示行同步说明（`FORMAL_SHIPPING_20261020.md` §9.18） |
| 已演标记的十六进制读回（Run75，前一包） | `Run75-hexchapters.png` / `Run75-hex0a-chapters.png` | 种 `PlayedMask=0f` 四行全标；种 `0a` 只标第二、第四幕（bit1/bit3）。Run74 用 `Atoi` 读 `%02x` 写出的值，`0f`→0 导致四幕演完后重启标记全消失（`FORMAL_SHIPPING_20261020.md` §9.19） |
| 叠加层蓝框与菜单焦点（Run76 / Run77） | `Run77-endfull.png` / `Run77-codexfull1.png` / `Run76-pause.png` / `Run76-chapters2.png`（Shipping 2134×1333）+ 编辑器 `Edchk5-menu-zoom.png` / `Edchk5-pause-zoom.png` | ① 方向键移动后不再有 1 px 蓝色 Slate 焦点框（`NativeTick` 镜像块改 `ClearKeyboardFocus(SetDirectly)` + `SetKeyboardFocus()`）；② 菜单六块牌有键盘焦点可见（琥珀牌面 + 标签前「◆」）；③ 结束面板主牌回到「重新复演」（Run76 曾把它盖成「开始游戏」）；④ 图鉴文案改「录入图鉴」（`FORMAL_SHIPPING_20261020.md` §9.20） |
| 第一幕容差放宽（Run78） | `Run78-campaign-087s.png`（通关后 End 面板「◆ 重新复演」）、`Run78-replay0..3.png`、`Run78-pause.png`（Shipping 2134×1333） | 只改三份第一幕数据资产的 Enter/Exit（0.075 / 0.115）：连演 25 行到 `phase=4 chapter=4/4 act=3 晦明同光`、`SfxProbe.log` 9 条（鼓 15.9/32.1/47.6/63.4、结算 24.1/39.6/55.4/70.9、锣 76.9）、复演 `REACHED_PHASE4=True` / `VERIFY-REPLAY-DONE`；exe 与 Run77 相同，map `BB0AE8F5…30C11F`（`FORMAL_SHIPPING_20261020.md` §9.22） |
| 站位提示（Run79） | `Run79-reach-final.png`（Shipping 2134×1333，底部牌匾「走近灯架，灯要够得到才推得动」+「灯：待调整」） | 玩家在戏台内够不到灯连续 6 s 时给一句走位指导、6 s 后还原、每幕最多一次；`EntryWalkProbe.log` 打出 `ShowHint text=走近灯架…`；判据与交互共用 `IsWithinFocusDistance`/`FocusDistance=700`，不参与判定；需偶版文案由新增自动化直测（`FORMAL_SHIPPING_20261020.md` §9.23） |
| 图鉴补锣鼓器乐（Run82，当前包） | `Run82-codex0.png` / `Run82-end.png`（Shipping 2134×1333） | 影偶图鉴正文新增「锣鼓与器乐」一段（四幕各一句），与造型/操演/制作七步并列，非遗五项齐全；正文抽成 `UDYDevEntryWidget::MakeCodexEntry()` 纯函数并加 1 项自动化（`DengYingShanHai.M1.UI.CodexCopy`）。只改 `DYDevEntryWidget.h/.cpp` 与测试，地图与判定未动（`FORMAL_SHIPPING_20261020.md` §9.25；美术缺口清单 `ART_BACKLOG_20261021.md`） |
| 章内携带上一步值（Run81） | `Run81-carry-002s…082s.png` / `Run81-replay0..3.png` / `Run81-pause.png` | 同一幕第 2、3 步不再把两轴重置到 0.15，而是从上一步定义里的 Target 起（`Saved/CarryProbe.log` **12 行**：每幕首步 `light=0.150 puppet=0.150 carried=0`、第 2/3 步 `carried=1`；Run81 与 Run80 只差这个探针）；配套把 `DA_P03RuntimeCandidate` 偶目标 0.85 → 0.92（窗口 0.845–0.995）；自动演出每步都直接写 Target、证明不了携带；四幕纯按键 45.6 s → 约 **24.1 s**（`FORMAL_SHIPPING_20261020.md` §9.24、`ACT_PLAYABILITY_20261021.md` 第 10 节） |
| 外景占位材质清理（Run71，前一包） | `Run71-step01..05.png`（Shipping 2134×1333） | 入口灯柱的顶板/顶珠不再挂引擎默认材质；树冠不再是等半径圆；近景山锥退出直行构图（`FORMAL_SHIPPING_20261020.md` §9.15） |
| 叠加层焦点可见（Run70，前一包） | `Run70-chapterlist.png` / `Run70-settings.png`（Shipping 2134×1333） | 「演出篇章」「设置」里键盘光标所在行画成朱红底 + 暖金字；`ApplyOverlayRowFocus()` + `NativeTick` 镜像 `FSlateApplication` 真实焦点（5.8 的 `FButtonStyle` 没有 focused 画刷，见 FORMAL §9.14） |
| 禁用牌匾可读（Run69，前一包） | `Run69-menu.png` / `Run69-menu-crop.png`（Shipping 首屏 2400×1350） | 第二块牌「继续游戏」不再空白：`RefreshView()` 按可用性重设标签颜色（禁用 `.80,.75,.66`）；四幕连演与复演在 Run69 上复跑通过（`Run69-campaign-087s.png` / `Run69-replay1..3.png`） |

脚本：`C:\dy_build\verify_run20.ps1 -Attempt <Run> [-Chapter N]`（PS1 必须 UTF-8 **带 BOM**；每一步按键前都跑 `foreground_game.ps1` 确认游戏窗口在前台，否则合成按键会打进用户的前台窗口）。

### 11.8 仍未完成 / 已知缺口

1. ~~入口提示不显示~~ → Run30 起已解决：UMG 那条路（独立 Hint 浮框 880×56、复用底部提示框 `bHintOverride`）都拿到 `size=0x0`，最终改在 `ADYInteractionHUD::DrawHUD()` 里直接用 `AHUD::DrawText`/`DrawRect` 画（`SetEntryWalkGuide(bool,const FText&)` 由控制器下发，字号 1.60、半透明底条 + 金色横线，位置居中偏下 132 px）。真机 `Run30-outside-1s.png`、`Run38-outside-1s.png`、`Run43-outside-1s.png` 均可见。
2. ~~四幕连演未走通~~ → Run25/Run27 已用 `DY_CAMPAIGN_AUTOPLAY=1` 在打包 Shipping 中跑通 12 步到真结局（探针 + 截图），但**真人手动**全程通关仍只有前作三幕记录，四幕手动可解性待验收。
3. 图鉴目前是 End 面板里的四行文字（夸父/精卫/刑天/烛龙），没有独立页面、四偶立绘与非遗图文；P1 策划的「影偶文化图鉴」仅达最小形态。
4. 外部山海仍是 blockout（树=柱+球、山=锥），只有剪影层面的氛围。Run32–Run38 做了 pass22–pass30 的美术迭代（对称格窗 18 个、右侧远山、瓦檐、石径、巨石、门侧灯笼、单套泛光），详见 §11.10；建模级升级（真山体/真树）未做。
5. 第 2/3/4 章的谜题参数由 C++ 现造，尚未经过真人可解性验证（容差 0.11/0.12，保持 1.0–1.25 s）。

### 11.9 回归与全程自检钩子（Run24 起）

- 四幕改动后自动化回归 **172/172 Success**（`C:\dy_build\AutomationV23.log`，`TEST COMPLETE. EXIT CODE: 0`；命令见 `C:\dy_build\ci_run13.ps1`）。注意：该脚本必须 UTF-8 **带 BOM**，并且项目路径用 ASCII 的 `C:\UEProjects\DengYingShanHai\DengYingShanHai.uproject`（Junction），否则命令行里的中文会变成 `D:/鐏奖灞辨捣/...` 而直接失败。
- 新增**验证用自检钩子** `DY_CAMPAIGN_AUTOPLAY=1`：`ADYPuzzleDirector` 每 0.2 s 把灯位与影偶位直接写到当前幕作者的 Target 上，让人不在键盘前也能把四幕走完。它**只写控制值**，判定、保持计时、转场提交、终幕森林仍由 Evaluator 与 Presentation 各自负责，不跳过任何判定。
- 由此发现的**参数一致性 bug**：影偶的「姿态」不是独立字段，而是由归一化位置反推的（`UDYPuppetControlComponent::GetPoseIndexForNormalizedValue` = round(value × (PoseIds-1))，三条 → value ≥ 0.75 才是 `P02_StrideReach`）。原先第 2/3/4 章里有几步把 `RequiredPuppetPoseId` 写成 `P02_StrideReach` 却把 `PuppetPosition.Target` 给成 0.14/0.18/0.30/0.50，**几何上永远无法同时满足**。已把这几步的偶位目标改到 0.84/0.86/0.88（原有三幕的 0.80/0.85 就是同一规律的正确示范，探针 `C:\dy_build\probe_acts.py` 已 dump 出前作的完整参数表可对照）。

### 11.10 外景美术 pass22–pass30 与四幕主灯配色（Run31–Run38）

| pass | 进包包号 | 做法 |
|---|---|---|
| pass22 | Run31 | 泛光改为 `Rotator(0,-62,0)`（yaw 0 朝 +X 朝墙，之前朝玩家所以墙面死黑）；5 盏 SpotLight @ x=-2015、y=(-1060,-560,60,660,1100)、z=60、42,000 cd、attenuation 3400、内 20°/外 52°、色 (255,186,126)、不投影；格窗改成 x=-1834 的竖缝 |
| pass23 | Run32 | 格窗改**对称网格** 6 列 y=(-730,-900,-1070,310,480,650) × 3 行 z=(1010,1220,1430) 共 18 个 `DYExt23_Lattice_*`（8 条竖缝读起来像百叶窗）；新增 4 个右远山 `DYExt23_RidgeRightFar_*`（x 2400–3960、y 2800–4240、h 2600–3500）补画面右侧空洞 |
| pass24–27 | Run32–Run36 | 瓦檐、石径、巨石、门侧大灯笼、雾；**试错**：加墙面洗光 → 更冷更白（Run33）；改几何发光条 → 材质是受光材质、不是自发光，几乎不亮（Run34）；42,000 cd 泛光叠多套 → 3 处白斑（根因见下） |
| pass29–30 | Run37–Run38 | 清掉重复 actor 后单套重建：发光条前移 `(-1892,-40,1940)`、檐灯 `(-1884,y,1886)`、格窗 `x=-1866`、`DYExt16_FacadeLamp` 降到 1,100 cd |
| pass33–34 | Run53 | 树冠簇化：检测 `Sphere` + `MI_DY_TreeDead` 的 actor（104 个，含旧 pass7 树冠与 pass31 灌木），每个补 2 个偏移小冠（0.56× / 0.44×，带 ±0.5d 偏移）；远山裙 8 座宽锥（半径 1,800–3,000 cm、高 700–1,200 cm）落在 x 2,200–5,000 |
| pass35 | Run54 / Run55 | 门前清场：删 14 块 `DYExt30_Slab_*`（悬空石板「梯子」）、20 立石、18 格心、16 个重复外侧路径灯等共 92 个 actor；`DYTheater_GateStep` 改 loc(-1800,-210,-10)、scale(1.4,7,0.2) 压到地面；新增门厅四幕影偶陈列（4 背板 + 39 部件 + 4 暖光）、8 石灯笼、6 远山、8 枯树。Run55 补 pass35d/e/f：偶从背板内抬到板前 6 cm、重贴 ink/朱红材质 |

### 11.11 影偶图鉴与「键盘焦点」的三个坑（Run39–Run43）

- **图鉴页**：`EDYMenuOverlay` 增加 `Codex`；结束面板里「游戏说明」牌位改为打开图鉴（`HandleMenuSelection` 按 `CurrentPanel == End` 分流），`RefreshOverlay()` 的 Codex 分支列出四具影偶（夸父逐日/精卫填海/刑天舞干戚/烛龙昼夜），每条含造型、操演、制作七步；行点击走 `ShowCodexEntry(N)`，Esc 返回。
- **坑 1（「第三幕」→「第四幕」第二次复发）**：`SetEntryIntroCueVisible()` 用 `TObjectIterator<UUserWidget>` 扫**全部** UTextBlock 做 `Replace("三幕","四幕")`，进场后连菜单浮层一起改。现在只处理类名含 `ThreeActHUD`/`ThreeActCue` 的演出控件。
- **坑 2（焦点游标）**：`UButton::HasKeyboardFocus()` 在焦点位于内层 `SButton` 时返回 false，导航把它当成「没有当前项」，每按一次 Down 都回到第一块可用牌位。改为自持 `NavFocusIndex`：`NativeOnKeyDown` 里推进、`CloseOverlay()` 与结束面板刷新时归零。
- **坑 3（验证脚本自己把焦点重置了）**：`keys.ps1` 每次调用都会 `SetForegroundWindow`，而 UE 在窗口激活时重置 Slate 焦点 —— 所以「下、下、Enter」必须**在同一次 keys 调用**里发出（`28,28,28,0D` 这种一串），否则永远停在第一块牌位。Run39–Run42 的三次误判都源于此。

- **四幕主灯配色**（Run35 起）：`DYPuzzleDirector::ApplyChapterPalette()` 末尾按 `FMath::Clamp(CurrentChapterIndex,0,3)` 给 `ADYLightRigActor::GetKeyLightComponent()` 设色 —— 夸父暖金 (1.00,0.86,0.66)×1.00、精卫青 (0.55,0.86,0.92)×0.92、刑天赤 (1.00,0.55,0.38)×1.10、烛龙月蓝 (0.58,0.66,1.00)×0.82。判定只读归一化值，颜色纯表现。
- **重要教训（actor 只增不删）**：`ext_v23`–`ext_v27` 的清理写成 `label.startswith(('DYExt21_', …))`（元组），UE Python 抛 `TypeError` 被同一 try 吞掉 → 每个 pass 只加不删。累计 925 个 DYExt actor、5 套 42,000 cd 泛光重叠，地图 1.3→2.9 MB，真机整面墙过曝。修法：独立脚本 `C:\dy_build\ext_clean.py` 用单字符串 `startswith('DYExt2')` + 统计输出，删 1,021 个，再单套重建。**以后任何批量删除都必须独立成脚本并打印 found/destroyed/remaining。**
- **材质认知**：`MI_DY_PathLantern` 是受光材质，几何体本身不发光；外景里那些「亮着的橙色方块」是被 `DYExt12_PathLight` 照亮的。想发光要么换 Unlit/自发光材质，要么补灯。
### 11.12 外景 pass31/pass32：一颗被放大 100 倍的灌木与一组石墩灯柱

- **根因**：pass7 生成 `DYExt7_Bush_*` 时把「米」当成了「缩放倍数」，14 颗灌木球的 `scale` 落在 450–2250 之间，实际包围盒半径 120–225 **米**，把整条进场路和戏台立面都罩在几个巨大的暗色球里。此前的截图之所以「看着还行」，是因为这些球被手动曝光压成近乎全黑的剪影，反而被误认成远山。
- **修法**（`C:\dy_build\ext_v31.py`）：按标签序号重算比例，把 14 颗球压回 3.4–5.05 的球径（约 3.4–5 m 冠幅），并把球心抬到 `30×scale` 让底部贴地；同时在坡脚补 12 丛灌木与 8 块卧石（`DYExt31_Shrub_*` / `DYExt31_Boulder_*`），避免压回真实尺寸后地面显得空。
- **灯柱**（`C:\dy_build\ext_v32.py`）：进场道两侧 6 对 `DYTheater_PathLantern_*` 原是 60 cm 见方的石墩 + 46 cm 发光立方体，读起来像一排水泥隔离墩。改成 34 cm 瘦柱（高度 2.5–2.86 m 有变化）+ 30 cm 球形灯 + 木灯帽 + 宝顶（`DYExt32_Cap_*` / `DYExt32_Finial_*`，共 24 个柱头件），灯的光源点未改动，所以原有亮度关系不变。
- **验证**：`Run46-outside-1s.png` / `Run46-outside-6s.png` 中灯柱成排有灯头与灯帽、灌木不再吞噬画面，入口提示条与金色横线仍在；`verify_campaign.ps1 -Attempt Run46` 连演 12 步到 `phase=4`，说明改美术没有碰谜题。
### 11.13 帧率探针（Run47）

- 动机：`-ExecCmds="stat fps"` + `-abslog` 在 Shipping 下完全失效（`NO_LOGGING` 让日志文件不生成，覆盖层也拍不到），性能证据一直是空的。
- 做法：`ADYDevEntryPlayerController::StartPerformanceProbe()` 在 `BeginPlay` 读 `DY_PERF_PROBE=1`，用 0.25 s 重复 Timer 采样 `FApp::GetDeltaTime()` 的倒数，做 0.25 系数指数滑动平均，每 4 次追加一行到 `Saved/PerfProbe.log`（`t=秒 fps=平滑 min=最低 max=最高 frames=样本数`）。探针默认关闭，不影响正常游玩。
- 实测：`C:\dy_build\verify_perf.ps1 -Attempt Run47` 与 `C:\dy_build\verify_perf_1920.ps1` 在打包 Shipping 里同时开 `DY_CAMPAIGN_AUTOPLAY=1` 与 `DY_PERF_PROBE=1`，四幕连演全程各 108 s 采样：**1280×720 平均 157.4 FPS（147.6–170.0）**、**1920×1200 平均 166.5 FPS（148.9–177.2）**；`CampaignProbe.log` 两次都落到 `phase=4 chapter=4/4 act=3`。
- 注意：数值取自窗口模式（非独占全屏）；真实演示机仍需在演示前采一次。
### 11.14 锣鼓提示音（Run48）

- 动机：四幕连演只有画面变化，章与幕的界限全靠题签读；V2.3 要求「锣鼓与器乐氛围」，但又不能变成通关提示通道。
- 素材：`C:\dy_build\make_sfx.py` 纯合成三件（无第三方采样）——锣 3.4 s（98 Hz 非谐分音 + 噪声起振）、鼓 1.0 s（76 Hz 下滑鼓皮 + 低通噪声）、结算音 2.2 s（523/784/1046/1318 Hz 叠音 + 弱锣），导入 `/Game/DengYingShanHai/Dev/Audio/SFX`。
- 接线：`ADYDevEntryPlayerController::PlaySequenceCue()` 在 `HandleActDisplay()`（`OnPlayerActDisplayChanged` 回调）里判定——`Playing` 且章号变化 → 鼓；`AwaitingFinale` 且相位变化 → 结算音；`Complete` 且相位变化 → 锣。只在状态跳变时响，不按帧、不按进度（`AGENTS.md` 第 16 条）。`DY_MUTE_SFX=1` 静音后谜题仍可完成。
- 可验证性：Shipping 的 `NO_LOGGING` 会剥掉 `UE_LOG`，所以另开 `DY_SFX_PROBE=1` 把 `cue=/t=/chapter=/phase=` 追加到 `Saved/SfxProbe.log`；开发包仍能在 `LogTemp` 看到 `DY SFX: cue=`。
- 实测（`C:\dy_build\verify_sfx.ps1 -Attempt Run48`）：连演 12 步到 `phase=4`，`SfxProbe.log` 9 条——鼓 t=14.9/31.1/46.6/62.0，结算音 t=23.1/38.6/54.0/69.5，锣 t=75.5；`Run48-codex.png` 复核图鉴页未回退。
- 未验收：音量平衡与音色听感需要人耳；当前锣/结算音 0.45、鼓 0.30。
### 11.15 设置页 15 s 回滚与持久化（Run50 / Run51）

- 需求出处：V2.2 主菜单重构要求「设置改动立即预览，15 s 内不确认自动还原」。
- 代码：`Private/UI/DYDevEntryWidget.cpp` 的 `HandleOverlayRow0/1/2Click` 改值后置 `bSettingsDirty` 并写 `SettingsDeadlineSeconds = FPlatformTime::Seconds() + 15.0`；`NativeTick → TickSettingsCountdown()` 每秒更新 `OverlayHint`（「预览中：%d 秒内不确认将自动还原。」），超时 `RevertSettings()` 恢复 `SavedVolumeStep/SavedWindowModeIndex/SavedResolutionIndex`；`CommitSettings()` 调 `ConfirmVideoMode()` 清 dirty；`CloseOverlay()` 在 dirty 时也回滚。
- 验证中的两个坑：
  1. 内置自测 `TickAutoTest()` 被 `#if !UE_BUILD_SHIPPING` 包住，**Shipping 里不存在**——Run49 用 `DY_MENU_AUTOTEST=4` 打进 Shipping 后完全没反应。
  2. 编辑器 `-game` 只能证明代码路径（`dirty t=9.0 vol=9` → `after-timeout t=25.0 vol=10`），不能说打包版也这样，因为 Shipping 的 `UGameUserSettings` 与窗口状态不同。
- 修法：新增与 `DY_CHAPTER`/`DY_CAMPAIGN_AUTOPLAY` 同级的 `DY_SETTINGS_PROBE=1`（`TickSettingsProbe()`，编译进所有配置），只走真实 UI 入口（`OpenOverlay(Settings)` → `HandleOverlayRow0Click()`），用 `WriteSettingsProbe()` 写 `Saved/SettingsProbe.log`。
- 实测（Run50，`C:\dy_build\verify_settings.ps1 -Attempt Run50`）：`probe-dirty t=1.8 vol=9 mode=1 res=2` → `probe-after-timeout t=20.0 vol=10 mode=1 res=2`；`Run50-settings-dirty.png` 主音量 9/10 + 倒计时提示，`Run50-settings-reverted.png` 主音量 10/10 + 提示恢复默认文案。
- 持久化（Run51）：`CommitSettings()` 增加 `GConfig->SetInt(TEXT("DengYingShanHai"), TEXT("VolumeStep"), VolumeStep, GGameUserSettingsIni)` + `Flush`，首次开设置页 `GConfig->GetInt` 读回；`Settings->SaveSettings()` 一并落盘窗口/分辨率。
  - 实测：mode 3 提交 `probe-committed t=3.0 vol=9`，ini 出现 `VolumeStep=9`；随后**新进程** mode 2 读出 `probe-loaded t=2.0 vol=9`，设置页截图显示「主音量 9 / 10」。
  - 坑：探针脚本原先带 `-nowrite`，该参数禁止配置落盘，导致第一次读回 10；去掉后通过。
  - Run51 回归：`verify_sfx.ps1 -Attempt Run51` 连演 12 步到 `phase=4`，`SfxProbe.log` 9 条（t=14.9/23.1/31.1/38.7/46.7/54.0/62.0/69.6/75.6）；`Run51-chapters.png` 四行正确；Run51 源码自动化 172/172。
  - 启动器编码：`Scripts/Start-FormalShipping.ps1` 必须保持 UTF-8 BOM（首三字节 `EF BB BF`），编辑工具会丢 BOM 导致中文路径乱码并把「identity is missing」误报出来。
- 仍未覆盖：设置页「分辨率」行显示预设值，自定义窗口尺寸（如 1920×1200）不在预设表里会回退到最后一档，属显示映射的小问题。

### 11.16 「重新复演」闭环（Run52）

- 需求：结束面板首牌「重新复演」应让玩家无需再点一次「开始游戏」就重新看四幕。
- 修法：`PerformReplay()` 在 `UGameplayStatics::OpenLevel(同一张 L_DY_Main)` 之前置位命名空间静态变量 `DYEntryReplay::bPending`；重载后的控制器 `BeginPlay()` 消费该标志并启动 0.6 s 周期 Timer，`TryAutoStartAfterReplay()` 等 Director 绑定、`GetEntryPanel()==Start`、无请求在飞时调用 `RequestStartExperience()`；最多 12 次（约 7 s）后放弃并记 Warning；正常启动不会触发（标志只在复演路径置位）。
- 验证（`C:\dy_build\verify_replay.ps1 -Attempt Run52`）：连演到 `phase=4` → Enter → `CampaignProbe.log` 追加 25 行，从 `chapter=1/4 act=1 引日启幕` 重演，经 `chapter=2/4`、`3/4`，再次到达 `phase=4 chapter=4/4 act=3 晦明同光`；截图 `Run52-replay1.png`（复演瞬间）与 `Run52-replay3.png`（第二遍结束面板）。
- 失败对照：Run51 同一脚本 `REPLAY_NEW_LINES=0`，`Run51-replay1.png` 停在主菜单「开始游戏」态——证明问题出在重载后停在菜单，而不是复演按钮无响应。
- 说明：Shipping 的 `NO_LOGGING` 剥掉 `Replay: new run started automatically` 日志，行为以探针文件与截图为准；开发包可见该行。

### 11.17 外景 pass33/34：树冠簇化与远山裙（Run53）

- 动机：pass31/32 之后树冠仍是「一根杆顶一个球」，远山是孤立锥体，远看仍像灰盒。
- 做法：不重建整套外景，只在既有树上加小冠——按「网格 = `Sphere`、材质名含 `TreeDead`、半径 1.5–9 m」识别出 104 个树冠球，每个补 2 个偏移小冠（0.56× / 0.44× 原直径，水平偏移 ±0.6d / ±0.4d、垂直 ∓0.1d，随机朝向），共 208 个；另加 8 座宽锥远山（半径 1,800–3,000 cm、高 700–1,200 cm）落在 x 2,200–5,000，补地平线缺口。
- 教训：第一次按 `DYExt22_Lobe_` 标签找，命中 0 个——标签集已被 pass24–30 重建；改按网格+材质识别后稳定命中。
- 证据：`Run53-outside-1s.png` 里路侧轮廓由单球变 2–3 个小冠组成的簇；性能 156.3 FPS 与 Run48 持平（见 §11.13）。

### 11.18 门前修形与四幕影偶陈列（Run55）

用户 m11176 指出「剧场前的梯子穿模、门口太多、戏台人偶没设置」。查下来：

- 那架「梯子」是 14 块 `DYExt30_Slab_*`（54–56 × 106 × 13 cm、z=22、比路面高 29 cm、彼此斜插），不是楼梯模型；`DYTheater_GateStep` 本身也是悬空的 80 × 350 × 15 台阶。两者叠加就成了门口那段「浮空歪梯子」。
- 门口冗余：20 块立石 `DYExt30_Stele_*`、18 片格心 `DYExt30_Lattice_*`、16 个外侧重复的 `DYExt12_PathLantern/PathLamp/PathLight_*`，再加多余灌木/石块/檐灯，共 92 个 actor 一起删。
- 台上可操纵皮影仍只有夸父（`BP_DYKuafuPuppet_Fitted_C`）——换偶会动阴影与判定，不改。新增门厅两侧「四幕影偶陈列」：左墙 x=-425 夸父、x=125 精卫；右墙 x=-425 刑天、x=125 烛龙。背板 `DYExt35_ActPanel_i` 贴在 y=±1252 的墙上（厚 12 cm），剪影偶 39 个部件在 y=±1240（板前 6 cm）。**这个 6 cm 是踩坑点**：第一次把偶放在 y=±1249，正好落在 12 cm 厚的背板体内，只露出头部和一条缝，看起来像「空展板」。
- 材质：墨色剪影 `MI_DY_Ink`（body/head/legs）+ 朱红道具 `MI_DY_LacquerOxBlood`（arms 与每幕专属部件 x0..x4）+ 铜钩 `MI_DY_AgedBrass`；每具一盏 `DYExt35_ActLamp_i`（±929/700、900 cd、520 半径、色 255,208,150）。
- 外景同一 pass：8 座石灯笼（4 盏 700 cd 点光）、6 座远山（半径 6,400–7,600 cm）、8 组枯树（3,400–4,600 cm）。
- 证据：`Run55-gate-front.png`（路面连续、门前清爽）、`Run55-gate-hall.png`（门洞到台面一路无遮挡）、`Run55-settings.png`（分辨率行带「当前」）、`C:/dy_build/shots35/hall_leftd.png`（左墙两具剪影）。
- 分辨率行：Run56 改读视口后备缓冲、Run57 改读 Win32 `GetClientRect`，同一台机器上都返回 1423 × 889，而窗口截图是 2134 × 1333——该 Shipping 进程在 DPI 虚拟化下拿到的就是逻辑客户区，真实上屏像素 = 1.5 倍；已记为已知限制，不再改。四具偶仍是基本体剪影；`DY_DEBUG_VIEW` 在打包版可用，但需关掉菜单才能取景。

### 11.19 四幕影偶陈列的撤回（Run64 → Run68）

§11.18 里摆在门厅两侧的四具影偶，真机走查证明读不到，最终在 pass43 全部删除。结论是**几何决定的**，不是美术没做完，写下来避免重复投入。

**根因**：入场走廊由 `M05_EntryWall_Left`(-930,-515) 与 `M05_EntryWall_Right`(-930,+95) 两堵 ext(250,15,200) 的木墙夹成，净宽 **610 cm**、中线 y≈-210；玩家沿 +X 直行，任何 |y|≥370 的侧向物体都在墙后。用金色标定柱（`DYCAL_*`，x=300，y 从 -1120 到 +1120 共 7 根）实测，画面里只有 y=0 那根出现。

**四次尝试**：
1. pass36 / Run64：门厅两侧墙上 4 块木背板 + 板前 6 cm 的 157 cm 剪影偶（39 部件）——贴墙 ⇒ 偶面法线朝 ±Y，玩家只看到 90° 侧棱。
2. pass37 / Run65：改成门厅两侧独立立偶（48 部件 + 4 灯），位置 (-1450,±620)/(-860,±620)——仍在走廊墙后。
3. pass38 / Run66：走廊内 48 演员、yaw=-90（剪影正对来向）、1400 cd 射灯——真机过曝成白矩形。
4. pass39 / Run67：射灯 230 cd / 2.1 m——完全看不见；pass40（yaw=180，侧看成一条线）、pass41（y=±740/±1120）同样 0 可见像素。

**处置（pass43 / Run68）**：删除 `DYExt35_Act*`、`DYExt37_Act*`、`DYExt38_Act*`、`DYExt40_Act*`、`DYExt41_Act*`、`DYCAL_*` 共 108 个演员（复核 `left=0`）并保存地图；四幕影偶由**影偶图鉴页**承载（结束面板 → 游戏说明 → 四条影偶，含造型/操演/制作七步）。若将来有正式皮影资产，正确位置是**戏台主光路**（与可操纵偶共面、同侧光），而不是门厅侧墙。

**同期修正**：「入戏台」与到达提示原先是两条牌匾，Run66 合为一条（`verify_steps.ps1 -Attempt Run67 -Steps 14 -WalkMs 1000 -Delay 22` 逐秒截图只留一块）。

**Run68 证据**：`verify_sfx.ps1 -Attempt Run68` 四幕连演到 `phase=4 chapter=4/4 act=3`（`CampaignProbe.log` 25 行）、`SfxProbe.log` 9 条（鼓 4 / 结算 4 / 锣 1，t=16.0…76.6）；`verify_replay.ps1 -Attempt Run68` 复演后追加 25 行；启动器 `-DryRun` = `PASS-PREFLIGHT-ONLY`（31 产物 / 757,838,316 字节）。

### 11.20 键盘焦点的可见性（Run70）

- 四幕菜单的叠加层（演出篇章 / 设置 / 影偶图鉴）原本用 `UButton` 列表实现，方向键由 Slate 默认导航移动焦点，但 5.8 的 `FButtonStyle` 只有 Normal/Hovered/Pressed/Disabled 四个画刷，没有 focused 画刷，于是「选中的是哪一幕」对玩家不可见。
- Run70 起由 `ApplyOverlayRowFocus()` 用朱红底 + 暖金字重画当前行，光标在 `NativeTick` 里从 `FSlateApplication::Get().GetKeyboardFocusedWidget()` 同步，Shipping 截图 `Run70-chapterlist.png` / `Run70-settings.png` 为证据。
- 这条改动只在 UI 层：地图哈希仍是 `0C833856…6E02053`，四幕连演 25 行、锣鼓 9 条、复演 `REPLAY_NEW_LINES=25`、自动化 173/173 全部与 Run69 相同。

### 11.21 外景美术的当前状态（Run71）

- 这一版解决的是三件具体的事：① 24 个灯柱顶板/顶珠还挂着 `WorldGridMaterial` / `DefaultMaterial`（后期批次漏设材质的残留，玩家抬头即见灰格）；② 328 个树冠是等比球，轮廓过规整；③ `DYExt30_Spire_*` 贴灯径两侧，直行时像帐篷压住门脸。修法与数据见 `FORMAL_SHIPPING_20261020.md` §9.15。
- 失败试验同样记录：给山锥加肩/峰合成两层山形（24 演员）变成灰色帐篷；把远景山脉放在 |y|=5400–6900 又没有雾参与，侧看是贴天的黑色锯齿；石板路太亮太大。三组全部删除。**没有体积雾时，远景只能做暗剪影。**
- 尚未解决：建筑与植被仍是基本体拼装（山=锥、树=球/柱、地=平面）。这属于「外景美术未完成」，不属本轮缺陷修复范围。

### 11.22 入口灯径的两套灯（Run72）

- 走到门口时先看到的是灯径。Run71 的走查图里，同一条线上并排着高灯柱（250–286 cm，球灯 + 黄铜帽 + 宝顶，12 根）和 pass35 补的矮灯（约 184 cm，方块灯身 + 米色锥顶，8 组）。矮灯在夜间剪影上就是小房子/小帐篷，与「门口尽量简洁」的目标相反。
- 处理原则：**统一灯型时只删几何，不删灯**。矮灯那 4 盏 700 cd 点光源在步道中线上方、本来就不可见，删掉会让路面变暗，所以全部保留。Run72 的 `Run72-step05.png` 与 Run71 同机位亮度一致，只有灯的数量从两套变一套。
- 现状：入口一共 12 根灯柱、12 盏 1500 cd 点光源，两侧仍是基本体树木/山锥（外景美术未完成，见 §11.21）。

### 11.23 标题面板的续演入口（Run73）

- 菜单六块牌里，「继续游戏」是唯一一块在标题面板**永远灰着**的牌；V2.2 定稿的牌匾语义没有覆盖「冷启动续演」，实现上它只是暂停面板的解暂停动作。
- V2.3 的四幕是可以逐幕开的（`演出篇章`），但评审最常用的路径仍是「开始/继续」两块牌；一块常灰的牌会被读成未完成。
- Run73 起：进度以章节为粒度记在 `Saved/DYProgress.txt`，`Playing` 写「章号+1」、`Complete` 写 0；标题面板据此决定这块牌是否可用，选中后走 `RequestChapterExperience(章号-1)`。
- 设计边界：不做幕内进度（灯/偶数值不存档）、不新增存档资产、dev 实验地图不写进度；删掉该文件即回到首次启动状态。

### 11.24 章节列表要能说出「哪一幕演过」（Run74）

- Run73 之前，「演出篇章」是四行静态幕名加两行说明；连演三遍之后打开它，看到的仍是同样的四行。四幕结构在菜单里只剩一句文案。
- Run74 起四行可以带「（已演）」。判定不取「进入过这一幕」——从该页可以直接开第四幕，那样会把前三幕误标；而是取「下一幕已经开始」，剧终时再补最后一幕。
- 这条状态与「继续游戏」共用同一份 `Saved/DYProgress.txt`（`ProgressChapter` + `PlayedMask`），因此「有一幕演过」与「可以续演」在界面上不会互相矛盾。
- 复演（结束面板 → 重新复演）不改已演标记：演过的幕就是演过，去掉标记反而会让评审以为进度丢了。

### 11.25 写读格式成对：PlayedMask 的 0f 事故（Run75）

- Run74 把四个「（已演）」位写成 `%02x`，读时却用了十进制 `Atoi`。`03`、`05` 这类纯数字掩码看不出问题；`0a`–`0f` 在第一个字母处截断，全部读成 0。四幕全部演完的终态恰好是 `0f`。
- 只在「四幕全演完 → 重启 → 打开演出篇章」这一条路径上暴露：单幕试玩、章节页直接开演、自动化断言都不会碰到它。
- Run75 改成 `Strtoi(..., 16)`，并用 `0a` 做区分性用例（第二、第四幕）而不是只用 `0f`：`0f` 只能证明「不为 0」，`0a` 才能证明「真按 16 进制」。

### 11.26 焦点的「可见」由成因决定，不由有无焦点决定（Run76 / Run77）

- UE 5.8 的 `FSlateApplication` 只在 `InCause == EFocusCause::Navigation` 时画焦点框（`SlateApplication.cpp:3099`）。叠加层条目本来是靠方向键让 Slate 自己导航的，于是每按一次方向键就带出一圈 1 px 蓝框；我们写在 `NativeOnKeyDown` 里的清理逻辑根本收不到那些键（已被 Slate 消费）。
- 真正的落点是 `NativeTick` 里镜像真实焦点的那一段：命中新行后先 `ClearKeyboardFocus(EFocusCause::SetDirectly)` 再 `SetKeyboardFocus()`，焦点还在同一行、键盘继续可用，但成因变了，框不再画。`ShowFocus` 是实时读取的，不需要刷新布局。
- 菜单六块牌不能用同一招：它们没有 overlay 那样的红底，`FButtonStyle` 也没有 focused 画刷。两次失败——借用半透明 hover 红底会透出背景美术里烘焙好的牌匾字，形成两层字；把首行 Collapse 掉会让整列上移，露出美术里烘焙好的第 6 块牌。**菜单列必须与 `T_MenuBackground` 烘焙的六格严格对齐。**
- 最终用「琥珀牌面 + 标签前「◆」」：`Normal.TintColor = Hovered.TintColor = (1.0, 0.84, 0.5)`，标签 `FText::Format(「◆ {0}」, BaseLabel)`。禁用项仍是灰牌 + 浅色标签（Run69 的修法）。
- 回归教训：焦点文本循环把 0 号牌改写成了静态名「开始游戏」，而结束面板本该是「重新复演」。修法是把 0 号牌改成 `GetPrimaryLabel(CurrentPanel)`——凡「按面板变化」的文案，不能混用静态基础名。这个问题是下一张结束面板截图抓到的（Run76 → Run77）。

### 11.27 四幕的输入行程与第一幕容差（Run78）

- 序列模式下每一步都由 `StartCurrentPuzzle()` 把两轴重置到 0.15（`DYPuzzleDirector.cpp:205`/`:207`），所以「上一步调到哪」不影响下一步的起点；灯轨 600 cm / 0.262 每秒、偶轨 320 cm / 0.28 每秒（关卡实例覆盖类默认 0.35），每步纯按键时长 = (目标 − 0.15) ÷ 速度。
- 四幕三步合计：第一幕 11.20 s、第二幕 10.04 s、第三幕 11.03 s、**第四幕 13.37 s**；单步最长是第四幕「睁眼为昼」5.25 s（灯 2.71 s + 偶 2.54 s）。整段 12 步只用方向键，合计约 45.6 s。
- 姿态门不增加操作：`GetPoseIndexForNormalizedValue()` 用 `RoundToInt(v × 2)`，三档姿态下 `P02_StrideReach` 需要偶位 ≥ 0.75；所有带姿态要求的目标都 ≥ 0.80，因此姿态只把可接受下沿抬到 0.75。第一幕「逐光成形」原本正好贴边（0.80 ± 0.05），放宽后离开贴边。
- 站位：两具操纵物相距约 1065 cm，而聚焦半径 `FocusDistance=700` cm。50 cm 网格上「视线 + 距离」判定，693 个采样点里只有 **76 个**能同时够到并看见两具，最近点 (50,-50,170) 到灯 530 cm、到偶 552 cm；站到 x ≤ -250 或 y ≤ -550 就要在两具之间走 3–7 m，而目前没有提示。这一条尚未修（属于 HUD 文案/引导，不是数值）。
- Run78 只改了第一幕三份数据资产的容差：Enter 0.045–0.05 → **0.075**、Exit 0.085–0.09 → **0.115**，可容忍按错 0.17–0.19 s → **±0.29 s**（灯 ±45 cm、偶 ±24 cm），约为后三幕的 65%；目标、保持 1.25 s、姿态、`bEnabled` 全部未动，后三幕（0.11/0.17、0.12/0.18）也未动。
- 因为改的是数据资产而不是 C++，Run78 的 exe 与 Run77 完全相同（`5C4700B9…A3747628`），但地图被重存（`774694AC…F571CCC` → `BB0AE8F5…30C11F`）、pak/ucas/utoc 三件哈希全变——「exe 没变」不能当成「包没变」，容器条目也要核。
- 完整表与站位二次判定见 `Docs/ACT_PLAYABILITY_20261021.md`（第 8 节为本次改动后的窗口），打包与回归见 `Docs/FORMAL_SHIPPING_20261020.md` §9.22。


### 11.28 够不到时给一句走位指导（Run79）

- 站位那条「76/693」的结论（§11.27）在 Run79 补了提示：玩家在戏台内、且离本幕需要的操纵物超过聚焦半径 `FocusDistance`（默认 700 cm）连续 **6 s**，底部牌匾给一句走位话，6 s 后自动还原，每幕最多一次。
- 判据与交互共用同一套语义：`UDYInteractionComponent::IsWithinFocusDistance` + `GetFocusDistance()`，提示本身不参与 Evaluator/相位/快照，改 `ReachHintDelaySeconds=0` 即整体关闭。
- 两句文案来自纯函数 `ADYPuzzleDirector::MakeReachHint`：需要偶「往灯与偶中间站，两件都够得到再动手」，只要灯「走近灯架，灯要够得到才推得动」，两件都够得到时返回空文本。
- 只在戏台内计时：`TheaterThresholdX = -1700` 现在放在 `Public/Core/DYEntryWalkTypes.h`，由入口引导与站位提示共用，避免两处各写一个数字；走廊阶段底部牌匾仍归「沿灯径向灯火深处走去，入戏台」。
- Shipping 真机（`Run79-reach-final.png` + `EntryWalkProbe.log` 的 `ShowHint text=走近灯架…`）证明通道与灯版文案；需偶版由新增自动化 `DengYingShanHai.M1.Puzzle.ReachHintCopy` 直测。包身份与回归见 `Docs/FORMAL_SHIPPING_20261020.md` §9.23。

### 11.29 章内携带上一步的目标值（Run81）

- §11.27 的前提「每一步都从 0.15 起」现在只对**每幕第一步**成立：同一幕内换步时，`AcceptActTransition()` 在 `++CurrentActIndex;` 之前置一次性标志 `bCarryEntryValuesOnNextStart`，`StartCurrentPuzzle()` 消费它，把上一步定义里 `bEnabled` 的轴设成**上一步的 Target**（不是玩家松手时的实际读数），跳过 `ResetToInitialValue()`。每幕第一步、`ResetCurrentPuzzle()`（重试）与 `StartCampaignChapter()` 都会清标志，仍从 0.15 起；开关 `bCarryControlValuesAcrossActs` 关掉即回到旧行为。
- 为什么携带 Target 而不是实际值：实际值可能停在上一步 Enter 窗边缘（如 0.875），下一步窗口会直接命中，玩家零输入就过关；Target 之间的差值是固定的（如杖落成林偶 0.80 → 0.92），每步至少一轴必须动。
- 配套把 `Content/DengYingShanHai/Dev/M3/Runtime/DA_P03RuntimeCandidate` 的偶目标 0.85 → **0.92**（`puppet_position.target`，Enter 0.075 / Exit 0.115 不变），窗口 0.845 – 0.995：上沿 ≤ 1.0，下沿仍高于姿态门 0.75；否则换步瞬间 0.05 < 0.075 会直接过关。
- 携带后纯按键量：第一幕 4.92 s、第二幕 7.39 s、第三幕 5.10 s、第四幕 6.69 s，**合计约 24.1 s**（改前 45.6 s）。最吃操作的是第二幕衔石入海的灯（306 cm / 1.95 s）、第一幕逐光成形的偶（208 cm / 2.32 s）、第四幕夜伏的偶（227 cm / 2.54 s）。
- 真机取证不能靠自动演出：`HandleCampaignAutoPlayTick()` 每步都直接 `SetNormalizedValue(Target)`，携带与否都会跑完。改由文件探针 `DY_CARRY_PROBE=1` 写 `Saved/CarryProbe.log`：Run81 12 行，每幕首步 `carried=0` 且两轴 0.150，第 2、3 步 `carried=1` 且等于上一步 Target；同轮 `CampaignProbe.log` 仍到 `phase=4 chapter=4/4 act=3 title=晦明同光`。
- 表与边界见 `Docs/ACT_PLAYABILITY_20261021.md` 第 10 节；包身份与回归见 `Docs/FORMAL_SHIPPING_20261020.md` §9.24。

### 11.30 影偶图鉴补「锣鼓与器乐」（Run82）

- V2.3 的非遗清单是五项：皮影造型、幕后操偶、制作七步、**锣鼓器乐**、通关后影偶文化图鉴。前四项里图鉴原本只覆盖前三项——造型与操演两段、制作七步一行，**锣鼓/器乐一个字都没有**，通关后玩家能读到「无锣鼓不开台」这类说法的地方为零。Run82 补的是这一处单点缺口。
- 正文从 `RefreshOverlay()` 的内联拼装抽成 `UDYDevEntryWidget::MakeCodexEntry(int32 Index)`（public static 纯函数，无世界访问），四段 `CodexDetails`（原有造型/操演）之后接四段新增 `CodexDrums`：夸父「开场三通鼓催幕，杖落一击大锣定音；鼓点跟着影偶的步幅走。」、精卫「小锣点水、鼓边碎击作浪，翅影掠过时钹合一声。」、刑天「堂鼓连击，钹分合应盾与斧；两影重合处改一记闷鼓。」、烛龙「大锣开昼、闷鼓收夜，昼夜交替只在两声之间。」，再接制作七步与「制作七步之外，锣鼓与器乐是影戏的另一半：无锣鼓不开台。」
- 索引用 `FMath::Clamp(Index, 0, 3)` 收敛：`MakeCodexEntry(9) == MakeCodexEntry(3)`，由自动化断言，避免图鉴条目数量变化时越界读到未初始化文案。
- 取证边界：图鉴只可能在四幕剧终后打开（`IsCodexUnlocked()`），所以真机截图必须走完一次完整连演（`verify_codex.ps1` 用 `DY_CAMPAIGN_AUTOPLAY=1` 跑到 `phase=4` 再按 D 两次跳过禁用牌、Enter 打开图鉴）；文案覆盖度本身由 175 项自动化里的 `M1.UI.CodexCopy` 直测，比只截一张图更能防止以后改文案时漏项。
- 没有做：没加锣鼓音效（既有 9 条状态触发已覆盖鼓/结算/锣）、没做器乐可视化、没改图鉴解锁条件、没动菜单与判定、没碰地图。
- 教训：像「非遗五项是否都讲到」这种**文案覆盖度**需求，靠人眼看截图会漏；把文案拼装抽成纯函数再加一条断言，改文案时 CI 会直接报出来。

### 11.31 换幕要有一个看得见的交代：幕间题签（Run83 / Run84）

- **问题**：四幕连演时标题行每一步都在换步骤名（引日启幕 → 逐光成形 → 杖落成林），但「现在是第几幕」只出现在「演出篇章」菜单里。玩家从走廊走到幕前，第一幕如何结束、第二幕何时开始，屏幕上没有一句话。
- **做法**：每幕第一次进入 HUD 时，把标题行换成放大的「第X幕 · 幕名」显示 **2.8 s**，随后回落到当前步骤题。判据是纯函数 `ShouldShowChapterCard()`（序列开启 / `ChapterCount > 1` / 索引有效 / 与上次显示不同 / 幕名非空）+ `MakeChapterCardText()`（单幕返回空）；计时用 `FTimerDelegate`，字号由 `BodyFontSize + 2` 提到 `+ 8`，下方状态行仍走步骤题。
- **到达门控（Run84 修的就是这条）**：首版在事件到达时就点亮，真机取证看到第一幕题签在自动演出开场约 2 s 就被计时消耗——那时玩家还在走廊、入口引导还没发出。Run84 把显示条件收紧为「舞台 HUD 可见 + 入口引导已收起 + `IsStageReached()`」，其中 `IsStageReached()` 读 `Pawn->GetActorLocation().X > DYEntryWalk::TheaterThresholdX`，与入口引导、站位提示共用 `Core/DYEntryWalkTypes.h` 的同一个 `-1700`。题签因此会**挂起等到玩家进戏台**，菜单直选一幕也不会在走廊里被耗掉。
- **取证**：`Run83-card-007s.png` 顶部是放大的「第四幕 · 烛龙昼夜」、`Run83-card-008s.png` 已回落「睁眼为昼」；Run84 的 `EntryWalkProbe.log` 记 4 条 `ChapterCard` + 3 条 `ChapterCardHidden`（第一幕 `walk=0` 未起计时，后三幕 `walk=1` 各显示满 2.8 s）。连拍每帧约 2.4 s，抓不到 2.8 s 的窗口，所以 Run84 的可见性以 Run83 那张截图为准。
- **边界**：题签只是 HUD 文案，不参与判定；没有音效、没有幕副标题、没改步骤题与保持时长、没动地图与 Director。自动化 `M1.UI.ChapterCard` 覆盖首次/重复/换幕/单幕/未开启/非法索引/空幕名七种输入，`ci_run13.ps1` 176 项全绿（13:18 Run83 / 13:33 Run84）。
- **教训**：任何「限时提示」都要先问「出现这一刻玩家在场吗」——只按事件点亮、按时长熄灭，在自动演出和菜单直选两条路径上都会在玩家看不见时把时长耗掉。

### 11.32 幕前的一条开发标定线（Run85）

- 建模盘点按材质扫了一遍 803 个 actor：场上只剩两处引擎默认材质——`DEV_BackScreen`（影窗幕面，等 A1 网格）与 `M3_RuntimeGroundLineMarker`（0.2 × 900 × 2 cm 的 Cube，`WorldGridMaterial`，贴在幕面前 0.2 cm，坐标 (924.8, 0, 70)），后者是 `Scripts/Create-P03RuntimeDev.py` 留下的目视标定条。
- 它不参与任何判定：真正被 `ADYStagePresentation::NarrativeGroundLine` 引用的是同脚本生成的 `M3_RuntimeNarrativeGroundLine`（TargetPoint）。所以直接删掉标定条、保留锚点：803 → 802，重载复验 `markerGoneAfterReload=true` / `anchorAfterReload=true`。
- 包：Run85 的 exe 与 Run84 相同（只改地图）、map 变 `F37EC39A…DA1B41`、31 文件 758,005,996 字节。回归：连演到 `phase=4 chapter=4/4 act=3`、锣鼓 9 条（16.0/32.1/47.5/62.8、24.1/39.5/54.8/70.3、76.3）、复演闭环通过；176 项自动化全绿。
- 教训：地图脚本生成的「只给开发看」的物体不会自己消失，落盘时就要 `HiddenInGame`；检查开发痕迹要按材质扫，不要只数 actor。
### 11.33 影窗终于是一块布：幕面、框，与一直挡在它前面的三块远山（Run86 → Run88）

- **为什么先做这一处**：整座戏台的表现都收在 900 × 800 cm 的幕面上——以灯为日、以影为夸父，全部发生在这块布。它此前只是一块 2 mm 薄 Cube 挂引擎默认材质，Run86 起更是整块全黑；玩家站在操偶位看到的是「一个黑洞」，而 HUD 还在说「灯已就位、影形已合」。
- **幕面**：`DEV_BackScreen` 2 mm 薄 Cube、正面 x = 925、900 × 800、不投影；材质 `M_DY_Cloth` + 实例 `MI_DY_ScreenCloth`，贴图是 PIL 现生成的 2048² 布纹（底 (238, 222, 194)、4 px 织纹、低频斑驳）。框料按 A1 概念图：上下 16 × 924 × 12 朱漆、左右 16 × 12 × 800 深木、上卷杆 Ø12 / 配重杆 Ø10 带黄铜端帽与朱漆环、四角 44 × 44 黄铜角花；框料正面比布面凸 3 cm（概念图「框深 16、布面距框后 3」）。
- **两根杆的方向**：圆柱默认沿 Z，UE Python 的 `Rotator` 顺序是 (roll, pitch, yaw) —— `Rotator(0, 90, 0)` 会让杆竖起来扎进地里（bounds z[350, 1290]），必须 `Rotator(90, 0, 0)` 才横过来（z[814, 826] / [17, 27]）。
- **黑幕的真凶**：三块 `DYExt30_RidgeBehind_*` 背景山横在相机 (-1595, -155, 178) 与幕布 (925, 0, 424) 之间（dist 1203 / 1213 / 1349）。它们是 **NoCollision**，所以视线射线一路穿过去命中幕布——这正是前几轮把问题误判成材质 / 灯光的原因。外景润色把共享的 `MI_DY_Mountain` 母材质换成深色 `M_DY_ExtInkWash` 后，这三块山在室内就是一块黑；Run83 时代它们还是灰盒亮色，看着像「被打亮的墙」，所以老截图显得正常。
- **处置**：山脊整体 +3200 X（近边 x = 2800 / 2810 / 2945，落在戏台后部之外），不删；临时点光、洋红 tag 材质、探针立方体清掉。三块旧「可读性引导面片」原本贴幕前 1.1–1.5 cm、正好 900 × 800 全覆盖，是首要嫌疑但 A/B 已排除；它们不带分幕语义（四幕共用 P01/P02 形状，且 `M_DY_Target_Sun` 是不透明 unlit 整板），现移到幕布后方并 `HiddenInGame`。
- **取证**：新加 `DY_ART_PROBE`（每秒一行写 `Saved/ArtProbe.log`：pawn / 相机坐标、正前方 6000 cm 射线命中的 actor / 网格 / 材质、最近 4 盏灯），第一件事就纠正了前提——复演者步速约 270 cm/s，走到操偶位要 21–22 秒，之前那些「黑幕」截图其实都还在走廊里。真机画面见 `Saved/Audit-2026-10-20-V21/ship88-w04.png`（第四幕：浅色布面 + 刑天紫红影子 + 木框与黄铜角花）。
- **包与回归**：Run88，exe `1710A30A…72D9A8E4`（探针是唯一 C++ 改动）、map `765D584F…AD9475`、31 文件 758,738,895 字节；176 项自动化全绿；连演到 `phase=4 chapter=4/4 act=3`、锣鼓 9 条、复演闭环通过。
- **教训**：看不见的问题要用渲染证据（隐藏 / 换色 / 换材质 A/B）证伪，碰撞证据会说谎（NoCollision 装饰物）；共享材质被外景调暗，代价可能出现在完全另一处（戏台幕前）；没有坐标探针时，「玩家没到场」和「幕布没渲染」会长得一模一样。
### 11.34 台口有了础与斗拱，路灯变成纸灯（A2 + A5 / Run89 → Run90）

- **台口**：柱子原来只是两根 120² 的方柱直接立在台板上。按 A2 概念图补了柱础（168² 基座 20 高 + 144² 础身 40 高，石材）、柱头（132² 托 26 高，朱漆）、三层斗拱（144 / 168 / 192 见方、各 18 厚，木 / 朱漆 / 木，累计出跳 36，顶到横梁底 z = 1375）、额枋（8×1520×40 朱漆 + 8 厚黄铜带）、柱梁交接黄铜板与两侧挂幕杆。共 20 个 actor，全部复用现成材质实例；柱础 60 高含在原有 1400 柱包络内，柱位与净宽 1520 未动。
- **路灯**：原来 34² 石柱顶上一颗 Ø30 发光球，中间空 34 cm。现在每根柱顶四件套——底圈 38×38×4（深木）、纸身 30×30×30（新材质 `MI_DY_LanternPaper`）、顶盖 40×40×6（深木）、顶饰 Ø5×7（黄铜）；12 根柱全部换装，旧球 12 个 `set_actor_hidden_in_game(True)` 保留（门楼 / 檐口灯还共用那个材质）。
- **纸灯材质**：`M_DY_LanternPaper` = 纸纹 BaseColor（TextureSampleParameter2D × Tint）+ Emissive（EmissiveTex × Glow 2.6）+ Roughness 0.62 / Specular 0.15，two-sided；两张 1024² 贴图用 PIL 现生成（暖纸底 + 128 px 竹骨 + 上下木圈；Emissive 中心暖光渐隐、骨架压黑）后导入 `Dev/WorldV2/Textures`。
- **观察**：纸灯身在真机里偏白、顶面接近过曝，Glow 2.6 偏高，下一轮与台口一起调（降到 1.6–1.8 并把 Tint 压暖）。
- **包与回归**：Run89（仅 A2）map `EC842582…39E9E`、31 文件 758,738,895（字节数与 Run88 相同，必须看 map 哈希）；Run90（A2 + A5）exe `1710A30A…72D9A8E4`、map `4073DED0…CB2EF12`、31 文件 **759,152,417** 字节（+413,522 是两张贴图）；176 项自动化全绿；连演 25 行到 `phase=4 chapter=4/4 act=3`、锣鼓 9 条（15.7 / 31.8 / 47.3 / 62.9、23.8 / 39.3 / 54.9 / 70.3、76.3）、复演闭环 50 行 2 条 phase=4。
- **教训**：路灯缺的是过渡构件而不是材质；台口构件在第三人称机位里被裁掉，先落尺寸等正面机位；编辑器导贴图会占 GPU，别和真机截图并行。
### 11.35 门楼终于有屋面：A4 的屋面、匾额与走廊墙帽（Run91）

- 先量后改：门楼 `GatePost_L/R`（80² × 920，柱心距 660、净宽 580）、`GateLintel`（z 905–995）、`GateStep`（140 × 700 × 20，顶面 z = 0），走廊 `M05_EntryWall_L/R`（500 × 30 × 400，墙心距 610）、`M05_EntryRoof`（500 × 680 × 18，z 420–438）、`M05_EntryPost_*`、`M05_EntryBeam_*` —— 与 A4 概念图几乎逐项相同，因此**不改槽位**，只补构件：屋面两块 92 × 792 × 10 斜面（绕 Y ±16°）、脊座与脊帽、两端翘头；匾额 10 × 320 × 76 + 黄铜框（预留空白）；楹联朱漆板 8 × 58 × 300 两块；黄铜雀替与门楣金线。
- 走廊：墙脚石材柱础条 500 × 44 × 24、墙顶木墙帽 500 × 46 × 16、内侧面每侧 3 根壁柱 24 × 10 × 380；顶棚加屋脊 520 × 26 × 18 与 4 条瓦垄 520 × 26 × 6。共 33 个构件。
- 新材质 `MI_DY_RoofTileTeal`（父材质 `M_DY_WorldBlockout`，青绿 (0.055, 0.135, 0.125) 线性）用于两坡、脊帽与瓦垄。工厂 `initial_parent` 属性不存在，必须 `create_asset` 后 `set_editor_property('parent', ...)`。
- 包与回归：Run91 map `760A09A2…34312C1`、31 文件 759,152,417 字节（字节数与 Run90 相同、hash 不同）；176 项自动化全绿；连演 25 行到 `phase=4 chapter=4/4 act=3`、锣鼓 9 条（15.9 / 32.0 / 47.8 / 63.4、24.0 / 39.8 / 55.4 / 70.9、76.9）、复演 25 行闭环。真机 `ext91b-approach.png` / `ext91b-walk.png`。
- 观察：门楼屋面在 50 m 外只有十几像素，游戏距离几乎读不出来；已记为待办，等 A3 墙体做立面浮雕时一并复核近景
### 11.36 观众厅终于有「构造」：A3 的墙裙、壁柱与栏杆，A6 的拼板地面（Run96）

- 先量后改：侧墙 `DYTheater_Wall_L/R` 4000 × 50 × 1900（y = ±1300）、壁柱 16 根 70² × 1900（中心 y = ±1240、间距 500）、观众栏杆 x = 1200、台前墙 x = 2200、台后墙 x = −1800、台阶 `DEV_Step_1..3` 90 × 150 × 25 —— 槽位与净宽全部不动，只在表面加层次。
- A3（82 个）每侧墙四件：石墙裙（z 0–150）、米白墙面（z 150–1580）、黄铜压条（z 1584）、朱漆上带（z 1580–1700）；16 根壁柱各加黄铜团花（Ø24 凸出 1.5）、柱头箍与石柱脚；栏杆补下横枋与 5 个黄铜柱头；台前 / 台后墙内表面各加石墙裙、米白墙板与朱漆带（台前左右各 1020 宽，避开 560 宽门洞）；台阶改石。新材质 `MI_DY_PlasterCream`（线性 (0.82, 0.78, 0.70)）。
- A6 地面：PIL 生成的 2048² 拼板贴图（板宽 40 cm、板长 160–480 随机、缝 0.8、错缝）→ `M_DY_WoodFloorPlank` / `MI_DY_WoodFloorPlank`，指派给 `DEV_Floor`、`M06_AudienceApron`、`DYTheater_Floor`、`DYTheater_FloorApron`；**只换材质不抬行走面**。真机 `s96-w04.png` 里地面已能看到拼板缝与错缝。
- 两个坑：侧墙贴片的 y 偏移符号写反 → 面板埋进墙里、画面零变化；`save_current_level()` 返回 True 不等于写盘（Run93/95 因此是空转包），必须再调 `EditorLevelLibrary.save_current_level()` 并重载复验。
- 包与回归：Run96 map `E47D94B5…13C355560E`、31 文件 **751,121,991** 字节（旧地面材质与贴图不再 Cook，比 Run91 少 8 MB）；自动化 176 / 0；`verify_sfx` 与 `verify_replay` 双绿。
- 观察：厅内第三人称机位下，墙面分层与壁柱团花都能读到；地面拼板缝在台前近距离很清楚，远景退化为整体暖色 —— 正是贴图方案想要的。
- 待办：A5 纸灯 Glow 2.6 偏高（降到 1.6–1.8）；门楼 / 檐口 / 屋面三颗球灯仍是发光球；B1–B3 与 C1–C3 未开始。机位。
### 11.37 一次诚实的失败：三层山体剪影与程序化枯树没成，回退到原树冠（Run97 → Run100）

- 做之前的目标很清楚：概念图 B1 给了「近 / 中 / 远」三层山（H1800 / 1200 / 800，宽 2600 / 3600 / 4800），B2 给了枯树的分件规格（主干 62² × 620、枝冠包络 417 × 374 × 310），这两组是外景最有观感收益的部分。
- 实现方式：山体用 **Unlit + Masked 剪影面片**（三张 PIL 现生成的 alpha 贴图 + `M_DY_MountainSilhouette`，6 块平面，前后各一组）；枯树用**圆柱段程序化分枝**（四级递归、pitch 由方向向量反解），8 棵沿灯径 + 10 棵在旧树冠位，共 290 个 actor；同时隐藏旧的球形树冠。
- 真机结果（`s99-w01.png`）：三层山读成戏台上方**一条青灰平板**——Unlit 不接雾、也不被场景压暗，等于贴在天空上的色块；程序化分枝读成**一排尖刺**；旧树冠一隐藏，地面反而更空。三件事同时变差。
- 处置：576 个 `ART_B1_*` / `ART_B2_*` 全部 `set_actor_hidden_in_game(True)`，328 个球形树冠/灌木恢复显示；语义上保留这些 actor 与三张贴图材质，等真正的网格方案到位再替换，不重新造一遍。
- 留下的正面结果：A5 纸灯的 `Glow` 从 2.6 降到 **1.7**（纸身不再过曝、暖光仍透竹骨），这条进了最终包。
- 教训：用引擎基本体拼不出概念图那种绘画型剪影；剪影要成立，面片必须**接雾、参与光照**（或干脆把远景交给天幕贴图）；枯树必须是真分枝网格，圆柱段在 20 m 外只会读成尖刺。本机没有 Blender，这两组要么等外部建模，要么改用「挂枝 alpha 卡片」，已记入 `ART_BACKLOG_20261021.md`。
- 包与回归：Run100 map `67B5E713…621C3449`、31 文件 **751,237,006** 字节（比 Run96 多 26,648：隐藏但仍存在的 B1/B2 actor 与贴图）；自动化 176 / 0，`verify_sfx` 与 `verify_replay` 双绿。
### 11.38 外景观感总补：贴图、枯枝剪影、壁柱、山石、锣鼓道具与月光补光（Run101）

- 这一轮把「外景是黑球 + 一整片竖向条纹橙墙 + 无纹理平地黄地」这件事正面解决掉，手段分三类：**给大面积物件上世界坐标 UV 贴图**、**把球冠换成枯枝剪影网格**、**补建筑与道具的层次**。
- 贴图（PIL 现生成，1024²，树皮 512×1024）：土、石板路、竖板墙、石膏、树皮、岩石共 6 张，走 5 个「世界坐标 UV + TileU/TileV 参数」的母材质与实例（引擎 Python 里没有 WorldAlignedTexture 节点，UV 用手搓的 WorldPosition/ComponentMask/Interpolate 拼出来）。
- 剪影：322 个 `MI_DY_TreeDead` 球冠换成 `SM_DY_BranchCrown_A/B_Unit100`（对方代理交付的枯枝网格，复用而不是重做），`scale = 原 extent / 50`，Z 旋转用标签字符和保证可复现。
- 层次：外墙壁柱 18 件（后墙 5 + 侧墙 7 根壁柱，配石墙裙、木带、檐口）、B3 山石 17 块（按 20% 埋深，沿路缘与林下分布）、C2 锣鼓与戏班道具 27 件（戏箱、案桌、堂鼓、大锣架 + Ø90 锣、小锣、钹一对、鼓槌）。全部为装饰件，**不参与判定、不改任何槽位**。
- 光照：门楼灯 2600/650 → 600/380 cd、月亮轮廓光 35 → 700、天光 0.8 → 1.35、外景雾 0.008 → 0.018，另加一盏无阴影的月光补光（pitch -38 / yaw 165，150 lux）与 3 个道具点光。曝光没有被自动曝光拖累——实测后处理卷是手动曝光、bias 3.5，改区间画面几乎不变，缺的就是光。
- 观感结果：入场从「看不清的两团黑 + 一条土路」变成「石径铺装 + 枯枝剪影 + 石膏墙木壁柱 + 门洞暖光同轴」；编辑器对照图 `Saved/Audit-2026-10-22-ArtPolishFinal/`、真机 `s101-w01/w03/w05.png`。
- 包与回归：Run101 map `0846A10E…B3B61D99`、31 文件 **752,992,875** 字节；自动化 176 / 0（`AutomationV32.log`），`verify_sfx` 9 条锣鼓与 `verify_replay` 25 行复演双绿。
- 待办：B1 山体还是 91 个 Cone；C1 三具影偶与 C3 图鉴版式未做；山石机位要换到树冠外再拍；门楼两侧柱在近景仍偏亮一点。

### 11.39 山是黑的，不是因为材质没换（B1 三层剪影定稿 / Run102）

- 现象：91 个山体 Cone 在夜里是一排匀齐的纯黑三角。前四轮都在「换材质」——世界坐标 UV 采岩石贴图、按 Z 做墨色梯度、加自发光——**一张图都没变**，连把自发光从 0.22 提到 1.6 都没有任何像素变化。
- 三个实验把问题钉死：① 把这 92 个 actor 全部 `set_actor_hidden_in_game(True)`，黑三角全消失 → 黑块就是它们，不是天幕也不是远景面片；② 把材质全换成纯红 unlit，它们变成**暗红锥** → 材质链路、指派、渲染都正常，夜里也确实有微弱环境光；③ 在五代 `M_DY_MountainLayer` 材质上分别调 tint 与 emissive，黑块没有变化 → 问题不在材质参数，在**光的量级**与**自发光里乘了贴图**。
- 两个真正的原因：这些山离所有灯源 6–17 km，夜里只剩极弱天光；而材质 BaseColor 的 tint 只有 0.05–0.15，乘下来落进 8-bit 的 0–2。另外自发光链是「贴图 × 梯度」，岩石贴图本身约 0.1，一乘自发光就被吃光——**自发光不能乘贴图**。
- 定稿做法：新建 `M_DY_MountainFlat`（BaseColor = 纯色 tint，Emissive = tint × Glow，无贴图、无世界坐标链），三个实例按 X 分近/中/远（tint 0.075 / 0.105 / 0.150，Glow 0.7 / 0.9 / 1.2），92 件统一改派；再把半径 <5000 的 36 个近场尖峰隐藏（它们贴着立面读成「牙」，与概念图「近景仅入画边缘」矛盾），剩下 43 件按 label 哈希做确定性随机缩放与绕 Z 旋转，打散「一排等高牙」的节奏。
- 6 块 `ART_B1_Mountain_*` 面片确认是引擎 Plane、无剪影 alpha，永久隐藏（启用只会挡住远景）。
- 结果：天空线高低错落，月侧锥面能读出受光折线，背光侧保持墨色。**形体仍是 Cone**——形式接近概念图，几何不合格，这条如实留在待办里（要真山形必须外部建模，或改成带 alpha 的剪影卡片）。
- 包与回归：Run102 map `61905D31…528B8C27`、31 文件 **752,977,826** 字节；自动化 176 / 0（`AutomationV33.log`）、`verify_sfx` 9 条、`verify_replay` 25 行双绿；真机 `s102-w01…w05.png`。
- 教训：查「为什么黑」按 **隐藏 → 染色 → 扫亮度** 三步走；只改材质会连改五版都看不出区别。


## §11.40 影偶图鉴页：概念图进了 UI（Run103）

- C1 三维实体化已放弃并清理（`pass191_c1.py` 建 93 件 primitive 影偶挂在北墙，真机读成"乐高小人"；`pass194_c1revert.py` 删 96 件，actor 总数回 1651）。
- 改为把 C1+C3 落成结束页的影偶图鉴：四张概念图裁切贴导入 `/Game/DengYingShanHai/UI/Codex/`（夸父 465×694、精卫 962×607、刑天 798×724、烛龙 424×737），`DYDevEntryWidget` 新增插图槽（左插图 / 右正文）。
- 图鉴页的红色游标跟随 `CodexIndex`；卡片改成固定 1040×1000 + ScaleToFit，插图 + 四行 + 页脚不再顶出屏幕。
- Run103：31 文件 / 756,354,646 字节、exe `7B86DA79…B62DE3`、map `2CA716ED…476551`；自动化 176/0；`verify_sfx` 到 `phase=4 晦明同光`（9 条 cue）；`verify_replay` `VERIFY-REPLAY-DONE`。
- 待办：夸父页插图顶部还残留概念图标题带半截字（裁切 y0 0.147 → 0.175 可修）；七步格的图版尚未接进页面（目前是正文一行"制作七步：…"）。

### §11.41 夸父插图重裁（Run104）
夸父页插图重裁为绝对像素框 `(300,255)-(898,898)`（598×643，含款识牌与全身、切掉右侧面板与底部标签），打包 Run104：31 文件 / 756,465,286 字节，exe 与 map 哈希同 Run103（只换贴图）；自动化 176/0，`verify_sfx` 到 `phase=4 晦明同光`，`verify_replay` 收尾。七步格图版因卡片空间不足暂不接入，理由记在 FORMAL §9.36。


### §11.42 树干树皮与墙面灰泥（Run105）
- 树干从纯色 `MI_DY_TreeTrunk` 换成世界坐标 UV 贴图 `MI_DY_TrunkTex`（母材质 `M_DY_TrunkTex`：WorldPosition→ComponentMask→Divide(220)→TextureSample→×Tint→BaseColor；Roughness 0.92），覆盖 **632 个树干**；贴图 `T_DY_BarkTex_BaseColor` 512×1024，自 `Assets/Sources/DengYingArt/Textures/` 导入（PIL 程序化生成，非照片）。
- 灰泥 `MI_DY_PlasterTex` 的 TileU/TileV 130→**95**、Tint→(0.62,0.575,0.515)：原来重复过密像细网格，改后远看是整片灰泥。
- B1 三层剪影卡片（近/中/远三张 2048×1024 墨色卡片，Unlit+Translucent）在 8.2–16 km 上完全看不见；把 Tint 改饱和红才看到纯黑锯齿剪影，证明是远景雾+自发光链路问题，**已回退**并删除 24 张卡片，actor 回 1651。回退时把近场尖峰也放出来了，改由 `pass210_hidenear.py` 按距离 <5200 隐藏 39 座、保留 47 座、6 块 `ART_B1_Mountain*` 平面永久隐藏。
- 复核图 `Saved/Audit-2026-10-22-Bark2/`（Entry/Gate/Hall）；Run105 = 31 文件 / 756,607,536 字节、map `BFA91095…5AE95D24`，自动化 176/0，`verify_sfx` 到 `phase=4 晦明同光`，`verify_replay` 收尾。

### §11.43 B3 山石改真棱面几何 + 枝冠压暗（Run106）
- B3 山石不再是球：Node 生成的 4 个 `SM_DY_Rock_{A..D}.obj`（二十面体细分 + 顶点随机位移 + 每面摊平做硬棱，900–3600 三角），`AssetImportTask` 导入后按 `get_bounds().box_extent` 反算缩放，**49 个石构件**（17 个 `ART_B3_Rock_*` + 32 个 `DYTheater_Rock_*`）全部替换，并按 label 哈希给 yaw 变化。无 DCC 也能出真几何 —— OBJ 是纯文本，顶点/面在脚本里算就行。
- 322 个枝冠的 `MI_DY_BranchBark` BaseColor 从 (0.18,0.12,0.075) 压到 (0.09,0.065,0.045)：原来在 600 cd 门脸灯下过曝成奶油色珊瑚，现在读成深色枯枝剪影。
- 程序化枯树（`SM_DY_BranchTree_A/B/C`，7.7k 三角/棵，主枝递归 3 层）替换过 592 个树干 Cylinder，四机位复看后判定**更差**（暗巷里细黑刺、失去体量），已整批回退并按公式还原柱心/柱高；actor 仍 1651。教训：批量隐藏的判据不要和同脚本刚写入的新网格前缀重叠，否则会把刚建的森林一起藏掉（`pass226_fix.py` 已修）。
- Run106 = 31 文件 / 756,683,136 字节、map `C2DE39A2…4CF34FB5`，自动化 176/0，`verify_sfx` 到 `phase=4 晦明同光`，`verify_replay` `VERIFY-REPLAY-DONE`。

### §11.44 山墙六盏壁灯（Run107）
- 门楣以上 10×20 m 的山墙原本全黑。现按 `DYExt30_GateLamp_0` 的灯笼模板在 x=-1795 / z=1140 挂 6 盏 `ART_EXT_WallLamp_00..05`（y=-1215/-905/-615/175/485/775，避开两根门柱），各配一根 34×5×5 cm 的 `ART_EXT_WallBracket_*` 横担，另加 4 盏 380 cd / 1000 半径的 `ART_LGT_WallFill_*` 暖点光。`MI_DY_LanternPaper.Glow` 1.7 → 3.06 让灯纸自发光。
- 坑：`PointLightComponent.light_color` 是 FColor（**B,G,R,A**），按 RGB 写会变蓝灯；`unreal.Rotator` 构造是 **(roll, pitch, yaw)**，手算视角必须改用 `find_look_at_rotation`。
- Run107 = 31 文件 / 756,685,184 字节、map `EA92785E…7C54`，自动化 176/0、SFX 9 cue 到 `phase=4`、REPLAY 通过。

### §11.45 门前黑锥清理与 C2 黄铜（Run108）
- `DYExt30_Snag_00..15` 16 根细锥在入场机位切过门楣，读成黑色尖刺，已整体隐藏（枝冠树群已足够表达枯枝）。门脸檐下六盏壁灯成为唯一焦点。
- `MI_DY_AgedBrass` 的基色参数是 **`Pigment`**、金属度 **`Metallic`**、粗糙度 **`RoughnessLevel`/`RoughnessDetail`**；复制出 `MI_DY_AgedBrassProp`（Metallic 0.6 / RoughnessLevel 0.52 / RoughnessDetail 0.34 / Pigment (0.78,0.58,0.26)）并覆盖大锣、小锣、两副钹 4 件，另加 2 盏 260–320 cd 暖点光。锣从"黑板"变成可读的黄铜盘。
- Run108 = 31 文件 / 756,687,507 字节、map `3FFF3414…1046A`，自动化 176/0、SFX 9 cue、REPLAY 通过。

### §11.46 近场金字塔清理（Run109）
- 64 座 `DYExt30_Ridge*/RidgeRight*/RidgeMid*/Spire*/RidgeEast* + DYExt33_Skirt* + DYTheater_Ridge*`（label 命中 Mountain/Ridge/Spire/Cliff/Skirt/Snag 且距 (200,0) < 5600）全部 `set_actor_hidden_in_game(True)`，保留 43 座 5.6–17 km 远景锥。入场帧里不再有三角切边。
- 关键验收教训：`set_actor_hidden_in_game` 只影响运行时，编辑器视口截图照样渲染；此类改动只能拿 Shipping 实机帧（`run_art_shipping2.ps1` → `s109-w01..w05.png`）验收。
- 另：编辑器截图落盘是异步的，两帧之间要留 ~9 s；`unreal.Vector((x,y,z))` 传元组会抛异常且静默终止 tick 链。
- Run109 = 31 文件 / 756,687,507 字节、map `84EEE6BE…6920`（与 Run108 同字节数，只有 map 哈希能证明真改了），自动化 176/0、SFX 9 cue、REPLAY 通过。

## 11.47 观众厅吊灯、内顶与图鉴七步（Run110）

- **吊灯亮度定稿**：`ART_LGT_HallLantern_*` 7 盏 → 2600 cd / 1400 cm；`ART_LGT_HallWall_*` 6 盏 → 1200 cd / 900 cm，仍然 `cast_shadows=False`、暖色 (1.0,0.72,0.42)。第一次只抬到 560/300 时抬头拍 `Saved/Audit-2026-10-22-HallLamp2/Up.png` 只有灯自身亮、望板仍黑，说明问题不是灯不够而是**没有可照的内表面**。
- **内顶望板**：`ART_A6_HallCeiling`（Plane 42×27 m，z=1865）、`ART_A6_HallCeiling_Stage`（14×13 m，z=1830），`Rotator(180,0,0)` 法线朝下，材质 `MI_DY_HallCeiling`（父 `M_DY_PlasterTex`，Tint (1.10,0.96,0.80)）。屋顶 `DYTheater_Roof_A/B/C` 是瓦面材质，朝内那面本来就吃不到光；补一层望板后，从 `Up` 机位看梁架之间是暖褐色木顶，`Overlook` 俯看影窗时画面成立。
- **图鉴七步页**：C3 七格工艺图版（01 选皮 … 07 装杆 + 材料示例）落在 `/Game/DengYingShanHai/UI/Codex/T_DY_Codex_Steps`（1990×1085，UI 组、sRGB），图鉴第 5 行切换。插图框改成"宽定高"（`ArtWidth=Clamp(WantHeight*Aspect,200,520)`、`ArtHeight=ArtWidth/Aspect`），宽图不再被压扁。
- **保存 API 教训**：`unreal.EditorLoadingAndSavingUtils.save_current_level()` 返回 True 但新增 actor 不落盘（重载即消失）；必须 `unreal.EditorLevelLibrary.save_current_level()` 且**重载复核**。本轮 `pass265` 丢了两块望板、`pass267` 才真正写入。
- 回归与包体见 `Docs/FORMAL_SHIPPING_20261020.md` §9.42：Run110 = 31 文件 / 760,801,003 字节、`SourceMapSHA256=3B2B1FE8…C588F4C2`、AutomationV41 176/0、sfx 9 cue 到 `phase=4 晦明同光`、replay 通过、Shipping 帧 `Saved/Audit-2026-10-20-V21/s110-w01..w05.png`。

## 11.48 入场路面「白斑」调查与 specular 归零（Run111）

- **现象**：Shipping 实机帧里入场石板路中线偏左有一排淡色矩形块（像斑马线），编辑器视口与俯视图都看不到。
- **排除线**：走廊 843 actor 全量导出无平面/光带；入口段（-7600<x<-4400）仅 24 actor 全是灯柱与点光；全图默认材质 0 个；像素统计 s109/s110/s111 同区域近白像素 683/693/443 且都落在灯点上 → 早就存在、不是本轮回归。全关卡 **无 ISM、无 Decal**（pass284 全量枚举），所以白带不可能是关卡内容。
- **改动**：x<-1500 的 34 盏点光 `specular_scale` 置 0（`pass274_spec.py`），重打包后实机帧白块依旧 → 高光假说排除；改动无害保留。
- **路面本体**：单个 Cube `DYTheater_ExtPath` (-3600,-210,-40) scale (40,5,0.4) + `MI_DY_StonePathTex`（Tile 170 / Roughness 0.82 / Specular 0.05）。
- 结论：列为已知观感瑕疵；后续若要根治，按"编辑器 -game 同机位对齐 → 逐盏关灯二分"定位，不要再在地图 actor 里找。
- 包体与回归见 `Docs/FORMAL_SHIPPING_20261020.md` §9.43：Run111 = 31 文件 / 760,801,003 字节、`SourceMapSHA256=9D610077…6ADE0B`、AutomationV42 176/0、SFX 9 cue、REPLAY 通过。

## 11.49 外景冷色灯修正（Run112）

- **现象**：入场帧门脸上两团青蓝光斑 + 树丛里一块冷白高光。
- **定位**：dump 74 盏灯的 intensity / light_color / attenuation / cast_shadows，只有 7 盏 B>R：`DYExt16_FacadeLamp_L/R` = (132,196,255)、`DYExt30_Uplight_00..04` = (104,164,255)。
- **根因**：`FColor` 与 `PointLightComponent.light_color` 都是 **B,G,R,A** 顺序，当初按 RGB 写 `unreal.Color(255,196,132,255)` 就成了蓝灯（§9.39 同一坑的遗留）。
- **修法**：`pass286_warm.py` → FacadeLamp (1.0,0.72,0.42)、Uplight (1.0,0.60,0.26) 且 7200→5200；`pass287` 重载复核 (255,221,173) / (255,203,139) 已落盘。
- **结果**：`s112-w02/w05.png` 门脸统一暖光，青蓝斑消失；包体 31 文件 / 760,801,003 与 Run108 起同字节数，map `A6BBB53E…EE7357`，AutomationV43 176/0。
- 详见 `Docs/FORMAL_SHIPPING_20261020.md` §9.44。

## 11.50 B1 山脊网格第二次尝试（Run113）与回退（Run114）

- **目标**：把远景 43 座可见 Cone（高度 2.1–5.7 m、距离 5.6–17.2 m 之外的远景层）换成有山脊轮廓的真几何剪影。
- **做法**：`gen_ridges.py` 生成 6 个归一化山脊网格 `SM_DY_Ridge_A..F`（0.5 单位、672–1056 三角、逐三角硬棱），`pass288_ridges2.py` 摆 20 个 `ART_B1_Ridge2_*`：三层环 R 8600/12500/17500、W 26000/34000/42000、H 2400/3200/4200、z=-300、yaw=deg+90，材质沿用 `MI_DY_MtnFlat_Near/Mid/Far`，同时隐藏 d≥5600 的 43 座 Cone。
- **失败现象**：Run113 打包后 `s113-w02.png` 里山脊网格变成头顶巨大白色碎片/白刃——朝向与尺度都不对，且被灯光打成过曝白，画面不可用。
- **回退**：`pass290_revert.py` 删 20 个 Ridge2；`pass291_restore.py` 按规则无条件重设可见性（d≥5600 的 43 座 Cone 可见、d<5600 的 64 座隐藏）；`pass292_clean.py` 清采集相机；重新打包 **Run114**（31 文件 / 760,801,003 字节、map `801F9618…4C8B16`），`s114-w02.png` 复归 Run112 观感。
- **判定**：B1 山脊网格方向两次失败（卡片板、真网格），**停止**。远景保留 Cone + 分层墨色 + 随距隐藏；这是当前无 DCC 条件下最稳定的做法。
- **两个可复用的坑**：`is_hidden_ed()` 读不到 `set_actor_hidden_in_game()` 的状态（回退必须按规则重设）；`run_py.ps1` 是"WaitFile 一出现就 Stop-Process"，截图脚本要在最后一张落盘后才写 JSON。
- 详见 `Docs/FORMAL_SHIPPING_20261020.md` §9.45。
## 11.51 入场面光衰减（Run118）与路面引导光带归因（Run115–Run117）

- **动机**：`s114-w02.png` 门楣与山墙被 5200 cd 门灯 + 5 盏 5200 cd 上照灯打成白橙一片，灰泥与斗拱投影不可读。
- **定稿**：`DYTheater_GateLamp_L/R` 5200→**3000**、`DYExt30_Uplight_00..04`（SpotLightComponent）5200→**3600**、`DYExt16_FacadeLamp_L` 600→**480**；脚本 `pass303_dim.py` + `EditorLevelLibrary.save_current_level()`。`s118-w02.png` 纹理与投影恢复、灯池仍在。
- **路面淡色带三条排除线**：① mobility STATIC→MOVABLE（Run115 `pass296`）→ 无变化，排除 lightmap 假高光，已还原；② 走廊 36 盏灯 intensity 全 0（Run116 `pass299`，原值存 `pass299_lights_off.json`）→ 全场漆黑而淡色带**自行发亮** → 是自发光而非这些灯照亮；③ 组件级扫描（`pass301` 网格、`pass302` 光组件 37 个）与全关卡 ISM/HISM/Decal 计数 0 → 关卡内没有这条几何。
- **结论**：淡色带是**运行时生成的引导光带**，与 HUD「沿灯径向灯火深处走去，入戏台」一致，**接受为有意引导**，停止排查；Run117 已复原 36 盏灯（`{"restored":36,"missing":[]}`）。
- **可复用判据**：这类"画面里有、场景里没有"的东西，只能靠关灯/改 mobility 的**功能实验**定位；`get_all_level_actors()` 的清点结果不能用来证明"不存在"。
- 详见 `Docs/FORMAL_SHIPPING_20261020.md` §9.46。

## 11.52 门外「燈影」匾额（Run119→Run120）

### 11.52.1 门脸的构件坐标（实测）
`-1900 < x < -1600`、`600 < z < 2000` 区间共 74 个 actor，关键构件：

| actor | 位置 | scale | 实际尺寸 |
| --- | --- | --- | --- |
| `DYTheater_RearWall_Head` | (-1800,-210,1400) | (0.5,6,10) | 50 cm 厚 / 600 宽 / 1000 高（z 900–1900）|
| `DYTheater_GateLintel` | (-1800,-210,950) | (0.9,7.2,0.9) | 90 高门楣，外凸 40 cm |
| `ART_EXT_RearBand` | (-1828,0,1150) | (0.3,24.6,0.42) | 横贯门脸的木带，外凸 18 cm |
| `ART_EXT_RearCornice` | (-1830,0,1620) | — | 檐下第二道线脚 |
| `ART_A4_Plaque` | (-1744,-210,946) | (0.1,3.2,0.76) | **门内侧**的匾，不是室外匾 |
| `ART_EXT_WallLamp_00..05` | x=-1795, z=1140 | — | y=-1215/-905/-615/175/485/775，半嵌进墙、探出约 9 cm |

### 11.52.2 匾额资产
- 贴图 `T_DY_PlaqueBoard` 1024×320：深漆木渐变底 + 只做压暗的木纹 + 双线金框与四角饰 + 196 px 金字「燈影」；字体为菜单系统已在用的 Noto Serif SC Bold（OFL）。
- 材质 `M_DY_PlaqueBoard`：`BaseTex` × `Tint` → BaseColor，贴图 × `Glow` → Emissive，Roughness 0.45、Metallic 0.2；实例 `MI_DY_PlaqueBoard` = Tint (1.0,0.93,0.80) / Glow 0.45。夜里靠自发光把金字顶出来，是这块匾能被读到的唯一原因。

### 11.52.3 摆位结论
- 匾身 `ART_A4_GatePlaqueOuter`：(-1846,-210,1130)、scale (0.06,4.2,1.3) = **420×130 cm**，挂在 `ART_EXT_RearBand` 前面（外凸 3 cm，不穿墙）。
- 铜框四条 `ART_A4_GatePlaqueTrimT/B/L/R`：x=-1852，上下各 z±68、左右各 y±215，scale 保证各 6 cm 边。
- 失败的第一次：z=1330 落进檐影里，Shipping 帧上只剩顶部一条暗板（Run119 作废）。**门脸这类多层构件必须先枚举坐标再摆位。**

### 11.52.4 验证
- `pass308_plaque_check.json`：total **1723 actor**，5 件匾额部件俱在，材质正确。
- Run120：`SourceMapSHA256=25F3907B3B4D31AEB6082DDF6349989E75483BA96D8DC6F08268C1FB0E6906CD`、31 文件 / 760,838,795 B；`s120-w03.png` 为验收帧。
- 回归：`AutomationV46.log` 176/0、sfx 9 cue、replay `REACHED_PHASE4=True`。

## 11.53 入场路面改成不规则青石板（Run121/Run122）

### 11.53.1 问题
`DYTheater_ExtPath` 是单个 Cube（scale 40,5,0.4 → 4000×500×40 cm，`/Engine/BasicShapes/Cube`，`MI_DY_StonePathTex`）。原贴图是等宽错缝砖，`TileU/TileV=170` 意味着纹理每 170 cm 重复一次，屏幕上就是「20 cm 的碎砖连成棋盘」。

### 11.53.2 做法
- 贴图 `T_DY_StonePathTex_BaseColor` 用 `C:/dy_build/gen_stone_v2.py` 重生成（1024²）：行高 84–142 px、板宽 96–236 px 随机、缝 4 px、板色 64–96、板内 8 级渐变、45% 磨角、26 条发丝裂纹、冷灰偏色 (×0.965/×1.0/×1.045)。
- `pass312_stone.py` 覆盖导入同名资产（sRGB + `TEXTUREGROUP_WORLD`），并把 `TileU/TileV` 170 → **250**（单块板约 30 cm）。
- `pass313_stone_tint.py`：`Tint` (1.05,1.02,0.98) → **(0.80,0.80,0.78)**，把放大后变亮的路面压回暗青石。

### 11.53.3 结论与数字
- Run121 = 贴图 + Tile 250（`s121-w02/w03.png`，石板成形但偏亮）；Run122 = 再压 Tint（`s122-w03.png`，暗青石成立）。
- Run122：31 文件 / **760,814,219** B、`SourceMapSHA256=25F3907B…0E6906CD`（与 Run120 同，改的都不是 map）；`AutomationV47` 176/0、sfx 9 cue、replay `REACHED_PHASE4=True`。
- 材质实例仍是 `MI_DY_StonePathTex`（父 `M_DY_StonePathTex`：`WorldPosition→ComponentMask→Divide(Tile)→TextureSampleParameter2D(BaseTex)→×Tint→BaseColor`，Roughness 0.82、Specular 0.05），路径与参数名不变，只改贴图内容和两个数值。

## 11.54 门脸木格窗（Run123）

- 坐标依据：墙前表面 x=-1825；`ART_EXT_RearBand` z=1150、壁灯 z=1140、匾额 z=1130、`ART_EXT_RearCornice` z=1620 → 窗只能落在 **1200 以上、1620 以下**。
- 落地：26 件 `ART_EXT_Lattice_{L,R}_{Top,Bot,Left,Right,M1..M7,H0,H1}`，x=-1818（外凸 7 cm），窗框 z **1250–1560**，左跨 y -1180…-280、右跨 y 280…1180；截面 24×14（框）/16×5（棂），材质 `MI_DY_FramePost_Wood`。
- actor 总数 1723 → **1749**；Run123 map `031100C3646CF4DED15C5FB6F7B0BF5331F5B080FE1365A13FF1F3020E697295`、31 文件 / 760,814,219 B。
- 验收帧 `s123-w02.png`：右窗网格清晰、左窗被枯枝部分遮挡；`AutomationV48` 176/0、sfx 9 cue、replay `REACHED_PHASE4=True`。

## 11.55 入口灯径嵌石：把运行时白色占位片换成真石板（Run124）

### 11.55.1 现象与定性
入场路面正中一串 7–8 片奶油白矩形，**只在 `-game` / Shipping 出现，编辑器视口同机位看不到**。四条排查把嫌疑面逐层收干：`BP_DYReadabilityPresentation_C` 无静态网格；全场 1749 actor 类普查无 ISM/HISM/Landscape；地面平板只有 ExtPath/ExtGround/GateStep/risers，包围盒求交 26 个 actor 里没有淡色板；编辑器 `-game` 可复现 → 运行时逻辑。

### 11.55.2 PIE 运行时枚举（关键手段）
`unreal.EditorLevelLibrary.editor_play_simulate()` → `get_game_world()` → `GameplayStatics.get_all_actors_of_class` 拿到运行时 1767 个 actor（比编辑器多 18，全是 Pawn/GameMode/HUD 类）。`BP_DYStageEnvironment_C` 包围盒是 x -4610…-2150、y -267…-152、z -16 的扁长条；逐组件 dump 出 **8 个 `StaticMeshComponent`，`/Engine/BasicShapes/Plane`、`MID_BasicShapeMaterial_0`、x=-4500 起每 320 cm 一片**；CDO 上只有 SceneRoot + 两个灯 → 运行时 C++ 生成。

### 11.55.3 真凶
`Source\DengYingShanHai\Private\Stage\DYStageEnvironment.cpp` 的 `LayReadableEntry()`（:60-110，`BeginPlay` 末尾调用）：沿 y=-210 打 8 条竖 `LineTraceSingleByChannel`，每次命中在路面 +4 cm 造一片 `Plane`，缩放 (2.2,1.15,1)=220×115 cm；材质是 `/Engine/BasicShapes/BasicShapeMaterial` 的 MID，并把参数 `Color` 设成 (0.46,0.32,0.18) 想做成深棕引导石——但该材质没有 `Color` 参数，**设置静默失败**，成品是引擎默认白/奶油色。

### 11.55.4 重写（:65-110）
- `Plane` → `/Engine/BasicShapes/Cube.Cube`（有厚度、有边缘光）；
- 材质 → `MI_DY_StonePathTex` 的 MID（与路面同一套 world-aligned 石板贴图；该 MI 已被 `DYTheater_ExtPath` 引用，字符串 `LoadObject` 能 cook），参数 `Tint` **(1.46,1.34,1.12)**、`Roughness` **0.94**、`Specular` **0.02**；
- 尺寸 224–236 × 114–119 × **2 cm**，`SetWorldLocation(Hit.ImpactPoint + (0,0,1.1))` 几乎与路面平齐（去掉 5 cm 侧面形成的黑框），`FRandomStream(20261022)` 给每片石板固定抖动；位置与 320 cm 间距不变，无碰撞/不投影；
- 函数后半段（:94-109）原有的「近白 + 强度>12000 + X<-1000 的路灯压到 4000 cd 并转暖」保留。

### 11.55.5 结论与数字
- Run124：31 文件 / **760,814,219** B、`SourceMapSHA256=031100C3…E697295`（与 Run123 同，只改 C++）、`NativeExeSHA256=C47EB577…E53E2867`（自 Run110 首次变动）。
- `s124-w02.png`：白矩形消失，代之以一条淡砂岩嵌石带，与路面同向的板缝；编辑器 `-game` 帧 `slab2-w02.png` 与真机一致。
- 回归：`AutomationV49` 176/0、sfx 9 cue（cue1 16.4/32.4/47.9/63.4，cue2 24.5/39.9/55.4/70.8，cue0 76.9）、replay `REACHED_PHASE4=True` + `VERIFY-REPLAY-DONE`。
- 教训：编辑器截图只反映编辑器世界；「只有打包版有」的画面问题必须先 `-game` 复现。`SetVectorParameterValue` 参数名错是静默失败——改引擎基本材质前先核参数表。
## 11.56 后台锣鼓道具换成曲面网格（Run125）

### 11.56.1 背景
后台 zone（y≈-1000/-1090 的戏箱·堂鼓·大锣架，y≈+1050 的案桌·小锣·钹）自 `pass156_props.py` 起一直是引擎基本体拼装：堂鼓是立圆柱、大锣是 Ø90 薄片、戏箱与案桌是直角方块。玩家从堂中走到台翼会近距离经过它们，体块感（无收腰、无卷边、无包角）直接暴露「未完成」。

### 11.56.2 网格（`C:/dy_build/gen_props_c2.py` → 11 个 OBJ → `pass325_c2props.py` 导入）
| 网格 | 尺寸（cm） | 结构 |
| --- | --- | --- |
| `SM_DY_C2_drum_body` | Ø62–67 × 56 | 桶形收腰，28 段 |
| `SM_DY_C2_drum_heads` | Ø62 | 浅锥双面鼓皮 |
| `SM_DY_C2_drum_studs` | Ø68 | 3 圈 × 20 颗黄铜钉 |
| `SM_DY_C2_drum_stand` | 底 ±13 / 顶 74 | 4 条外撇腿 + 2 横枨 |
| `SM_DY_C2_gong_large` | Ø75 × 3 | 卷边（rim 折起 3 cm） |
| `SM_DY_C2_gong_stand` | 跨 104 × 高 196 | 两柱 + 横梁 |
| `SM_DY_C2_gong_small` | Ø24 | 平锣 |
| `SM_DY_C2_cymbal` | Ø34 × 2.6 | 锥面 |
| `SM_DY_C2_prop_chest` | 92×56×54 | 带盖戏箱 |
| `SM_DY_C2_prop_chest_bands` | 92×56×54 | 四角 + 口沿包铜 |
| `SM_DY_C2_prop_table` | 124×62×79 | 案桌 + 牙板 |

### 11.56.3 材质与摆位
- 朱漆 `MI_DY_LacquerVermilion`、木 `MI_DY_M03_FrameWood`、黄铜 `MI_DY_AgedBrass` 全部复用既有资产；鼓皮新做 `MI_DY_C2_DrumHead`（父 `M_DY_PlasterTex`，Tint **0.62/0.52/0.38**、Rough **0.9**），因为白灰泥在灯笼光下过曝。
- 堂鼓 z=90（底 62 落在 74 高鼓架里）、yaw 25°；大锣架 yaw 90°（两柱沿 X、锣面朝 ±Y），锣心 z=145，梁下两根 Ø2 × 11.5 cm 绳；案桌顶 z=79.2，小锣 z=81.4、钹 z=81.8/83.2 各带 11–14° 倾角；4 根竹签横躺桌面 z=80.9。
- 删 23 件旧灰盒、加 14 件（12 道具 + 2 锣绳）：actor 总数 1749 → **1740**。

### 11.56.4 结论与数字
- Run125：31 文件 / **760,983,728** B（+169,509 B 全为新网格）、`SourceMapSHA256=7A34D128…3BB0B299`、`NativeExeSHA256=C47EB577…E53E2867`（未变，只改内容）。
- 验收帧：`Saved/Audit-2026-10-22-C2Props/{c2_drum2,c2_gong2,c2_table3,c2_wide3}.png`；灰盒对照 `wide.png`。
- 回归：`AutomationV50` 176/0、sfx 9 cue（16.3/32.4/47.8/63.5 + 24.4/39.8/55.4/71.1 + 77.1）、replay `REPLAY_NEW_LINES=25` + `REACHED_PHASE4`；真机帧 `s125-w01..w05.png`。
- 教训：批量导入必记材质解析结果（`load_asset` 失败只返回 None，`if mat is not None` 会静默留灰）；≤2 cm 薄片必须离面 2–3 cm 并倾斜，否则在斜俯视里是贴花。


## 11.57 影窗绢面与厅内灰泥（Run126）

### 11.57.1 影窗的承载物与材质链
- 幕面 actor：`DEV_BackScreen`（`StaticMeshActor`，网格 `/Engine/BasicShapes/Cube`，中心 **(925, 0, 424)**、半长 **(0.1, 450, 400)**）→ 实际 **9 m 宽 × 8 m 高**、位于 **x≈925**、屏面朝 **-X**；观众侧 x<900，幕后/操作侧 x>925（`M06_AudienceApron` x=1350、`DYTheater_FloorApron` x=2400）。
- 材质：`MI_DY_ScreenCloth`（`/Game/DengYingShanHai/Dev/WorldV2/Materials`）→ 父 `M_DY_Cloth`（`BLEND_OPAQUE`、`MSM_DEFAULT_LIT`、`two_sided=False`，节点链仅「`BaseColorTex` × `Tint` → BaseColor」）。参数：`BaseColorTex` = `T_DY_ScreenCloth_BaseColor`、`Tint` **(0.93, 0.88, 0.80)**。
- 同材质只被幕面使用（`find_package_referencers_for_asset` 结果：贴图 → `MI_DY_ScreenCloth` + `M_DY_Cloth`；MI → `L_DY_Main` 与历史候选关卡 `L_B2Wall_Candidate`），因此换贴图不影响其它布料件。

### 11.57.2 新绢面贴图
- 生成器 `C:/dy_build/gen_screen_tex.py` → `C:/dy_build/tex/screen/screen_cloth.png`，**2048 × 1820**（= 900 : 800）。
- 内容：暖米底 (0.955,0.905,0.828) + 两组低频噪声（18×16 / 80×64，幅 0.026 / 0.011）+ **5 幅竖缝**（正弦 wobble ±2.6 px，模糊 2.6 px，压暗 34/255，旁侧 blur 9 px 微高光）+ 幅内鼓起（压暗 0.020 / 中心高光 0.016）+ 顶部两道折痕（压暗 0.020）+ 16 个模糊污渍（半径 90–280 px、模糊 56 px、压暗 40/255）。
- 导入：`C:/dy_build/pass338_screentex.py`，`AssetImportTask` 覆盖同名资产（`replace_existing=True`）+ `srgb=True` + `lod_group=TEXTUREGROUP_WORLD`；验收帧 `Saved/Audit-2026-10-22-HallSurvey/screen_soft.png`。
- 机位：相机 (150,-420,330) → 看向 (900,0,430)、FOV 72、1920×1200。

### 11.57.3 厅内灰泥
- `MI_DY_PlasterTex`：`TileU/TileV` **95 → 240**（0.95 m → 0.24 m 重复周期），`Roughness` 0.9 / `Specular` 0.02 / `Tint` (0.62,0.575,0.515) 不变；脚本 `C:/dy_build/pass333_plastertile.py`，对照帧 `Saved/Audit-2026-10-22-BandTest/plast-w02.png`。

### 11.57.4 结论与数字
- Run126：31 文件 / **760,539,025** B（比 Run125 少 444,703 B，贴图低频化后块压缩更省，文件数与 CookedMaps 不变）、`SourceMapSHA256=7A34D128…3BB0B299`（与 Run125 同，未动 actor）、`NativeExeSHA256=C47EB577…E53E2867`（未变）。
- 回归：`AutomationV51` 176/0、sfx 9 cue（16.4/32.4/47.8/63.5 + 24.6/40.0/55.7/71.2 + 77.2）、replay `REPLAY_NEW_LINES=25` + `BEFORE_LEN=1093 / AFTER_LEN=2187` + `REACHED_PHASE4=True`；真机帧 `s126-w01..w05.png`（PROBE 98）。
- 教训：9 m 级大面留不住毫米细节（mip 一平均即无），可读的是缝 / 皱 / 污渍三类宏观痕迹；缝线的数量与软硬决定「布」还是「板」（12 幅硬缝读作彩钢板，5 幅软缝才读作绢）。

## 11.58 观众厅侧墙的影偶图鉴挂屏（Run127）

### 11.58.1 为什么是挂屏
观众厅左右墙 = `DYTheater_Wall_L/R`（Cube，中心 (200,∓1300,950)，半长 2000/25/950 → 40 m × 19 m）+ 贴面 `ART_A3_Plaster_L/R`（y=∓1273.5，半长 2000/1.5/715，`MI_DY_PlasterTex`）。这是全场最长的连续表面，而玩家在厅内转身时必然经过它。墙面本身没有可依的东西，所以补的是**陈设**而不是新墙。

### 11.58.2 资产
| 件 | 路径/做法 | 关键参数 |
| --- | --- | --- |
| 框网格 | `C:/dy_build/gen_frame.py` → `C:/dy_build/obj/frame/sm_dy_puppetframe.obj` → `SM_DY_PuppetFrame` | 外框 160×230 cm、框条 12 cm、深 8 cm、**无背板**；`box_extent`=(80,4,115) |
| 框材质 | `MI_DY_M03_FrameWood` | 沿用既有木材质 |
| 画面材质 | 4× `MI_DY_HallFrame_{Kuafu,Jingwei,Xingtian,Zhulong}`（父 `M_DY_PlaqueBoard`） | `BaseTex`=图鉴贴图、`Tint`=(1.0,0.95,0.86)、`Glow`=0.20 |
| 画面几何 | `/Engine/BasicShapes/Cube` 薄板 | scale (1.36, 0.03, 2.06) → 136×3×206 cm，双面可见 |

### 11.58.3 摆位
- x = **-1430 / -900 / -370 / 150**（壁柱 `ART_A3_PilasterFoot_L/R` 的中点：-1437 / -912 / -387 / 137），z = **820**。
- 左墙 y = **-1269**（yaw 0）、右墙 y = **+1269**（yaw 180）；画面中心 y = ∓1264.4（在框前 1.6 cm 的内凹位）。
- 每屏一盏 `PointLight` 在墙面外 62 cm：**120 cd / 半径 340 / cast_shadows=False / 暖色 (1.0,0.78,0.50)**，MOVABLE；框与画面 STATIC 且 `cast_shadow=True`。
- actor 名：`ART_HALL_Frame_{L,R}_0..3` / `ART_HALL_Art_{L,R}_0..3` / `ART_LGT_HallFrame_{L,R}_0..3`；脚本 `C:/dy_build/pass347_frames3.py` 每次重跑先按前缀删除旧 actor。
- map actor 总数 1740 → **1764**。

### 11.58.4 结论与数字
- Run127：31 文件 / **760,544,163** B（比 Run126 多 5,138 B，全部是 map）；`SourceMapSHA256=6E50B224C0E112FB6D0F1B2B68DC898874D611599DE4E248FDE439DF6A5EAFE1`；`NativeExeSHA256=C47EB577…E53E2867`（未变）。
- 回归：`AutomationV52` 176/0；sfx 9 cue（16.0/32.0/47.4/63.3 + 24.0/39.4/55.3/70.8 + 76.8）；replay `REPLAY_NEW_LINES=25` / `REACHED_PHASE4=True`；真机帧 `s127-w01..w05.png`（PROBE 98）。
- 验证帧：`Saved/Audit-2026-10-22-DisplayFrames/frame_wall.png`（侧墙挂屏）与 `frame_aud.png`（主观众机位不受影响）。
- 教训：空心框 + 实心背板 = 木牌；画面不能用 `unreal.Plane`（roll 轴序不稳、背面剔除后整片消失），薄 Cube 天生双面可见。挂屏高度按玩家视线定（z=980 不入画，z=820 才读成陈设）。

## 11.59 观众席木长凳：让 40×26 m 的大厅读成小戏台（Run128）

### 11.59.1 问题
观众厅地面从 `x=-1700`（门）一直铺到 `x≈925`（影窗），宽 `y∈[-1300,1300]`，但观众区一件陈设都没有。从门内看进去是一整片空木地板，读不出「这里坐过人」；剧场该有座位，而座位又必须让开中央走道（玩家要从门走到幕前、且互动区在 `x>800`）。

### 11.59.2 几何与摆位
- 网格：`C:/dy_build/gen_bench.py` → `sm_dy_audbench.obj`（`verts 64 / faces 48`）。沿 **Y 长 420 cm**、深 **40 cm**、座面 z = 40–46 cm、背靠两段斜靠板（z 52–74 / 72–94）、4 组侧腿 + 下枨。导入为 `SM_DY_AudBench`（`/Game/DengYingShanHai/Dev/ArtPolish_20261022/Meshes`，`box_extent` = **(23, 210, 47)**）。
- 摆位：4 排 × 2 侧 = **8 条**，`x = 250 / 90 / -70 / -230`（排距 160 cm），`y = ±560`；中央 `|y| < 350` 留作走道。材质 `MI_DY_M03_FrameWood`。
- 坐垫：每条凳一块薄 Cube，scale (0.38, 4.05, 0.055) → 380 × 405 × 5.5 cm，`z = 52`，材质 `MI_DY_LacquerVermilion`（朱漆），让长凳在暖光下有一条明确的红色水平线。
- 座位灯：`ART_LGT_AudSeat_{0..3}_{L,R}` 共 8 盏，`z = 260`，**320 cd / 半径 620 / cast_shadows=False / (1.0,0.80,0.56)**。原来这一片只有 5 盏灯，长凳在暗处读作黑块。
- 命名 `ART_AUD_Bench_{0..3}_{L,R}` / `ART_AUD_SeatCushion_{0..3}_{L,R}` / `ART_LGT_AudSeat_{0..3}_{L,R}`；脚本先删同前缀，可反复重跑。

### 11.59.3 两个坑
- **`set_actor_label()` 只改 label**：清理与统计必须按 `a.get_actor_label()` 匹配，按 `a.get_name()` 永远是 `StaticMeshActor_N`。
- **材质路径必须核实**：`MI_DY_LacquerOxBlood` 在 `Dev/WorldV2/Materials` 下**不存在**，`load_asset` 返回 None 而 `if mat is not None:` 静默跳过，8 块坐垫全留默认灰；改 `MI_DY_LacquerVermilion`（该目录唯一朱漆）才对。

### 11.59.4 结论与数字
- map actor **1764 → 1788**（8 凳 + 8 坐垫 + 8 灯）。
- 验证帧：`Saved/Audit-2026-10-22-Audience/aud_hall.png`、`aud_seat2.png`（从门内看：中央走道两侧各四排长凳、凳面一道朱红，尽头是亮着的影窗与「逐日」匾）。
- Run128：31 文件 / **760,556,929** B（比 Run127 多 12,766 B：新网格 + map）；`SourceMapSHA256=A9A581AC69C42077F7300745DA3B813BE56931E076BC51769A2787EE71052FAD`；`NativeExeSHA256=C47EB577…E53E2867`（未变）。
- 回归：`AutomationV53` 176/0；sfx 9 cue（16.4/32.7/48.2/63.6 + 24.7/40.2/55.6/71.5 + 77.5）；replay `REPLAY_NEW_LINES=25` / `REACHED_PHASE4=True`；真机帧 `s128-w01..w05.png`（PROBE 98）。
- 教训：空大空间先用「重复件」填（一条 64 顶点长凳复制 8 次），比改建筑便宜两个数量级；陈设先让开玩法动线（中央走道 |y|<350）；暗环境家具要么读作剪影、要么自带一盏小瓦数无阴影点光。

## 11.60 自制网格的 UV 补齐（Run129）

### 11.60.1 问题
`SM_DY_AudBench`（观众席长凳，Run128）、`SM_DY_PuppetFrame`（影偶挂屏框，Run127）、11 件 `SM_DY_C2_*`（后台锣鼓，Run125）都是脚本生成的 OBJ。生成器只输出顶点与面，没有 `vt`；UE 导入后 UV0 为空，材质贴图被采样成单一颜色 → 长凳在实机里读作浅银色金属条，戏箱是一块无细节的红方块。

### 11.60.2 做法
- `C:/dy_build/obj/uv/` 下 13 个 OBJ 全部补盒式投影 UV（按面法线主轴投影，1 UV = 1 m）。
- `pass362_uv.py` 用 `AssetImportTask`（`replace_existing`）原地覆盖同名资产，actor 引用与摆位完全不动。

### 11.60.3 资产与材质对照
| 资产 | 材质 | UV 之后读到的内容 |
| --- | --- | --- |
| `SM_DY_AudBench` | `MI_DY_M03_FrameWood` | 凳面板缝、靠板木纹、腿的竖纹，朱红坐垫读作漆布 |
| `SM_DY_PuppetFrame` | `MI_DY_M03_FrameWood` | 框条木纹连续，不再是一根棕色条 |
| `SM_DY_C2_drum_body` | `MI_DY_LacquerVermilion` | 桶身竖木条 + 漆面亮度变化 |
| `SM_DY_C2_drum_stand` / `gong_stand` | `MI_DY_M03_FrameWood` | 架腿木纹 |
| `SM_DY_C2_prop_chest` / `_bands` | `MI_DY_LacquerVermilion` / `MI_DY_AgedBrass` | 箱盖缝与箱箍分层 |
| `SM_DY_C2_gong_large` / `cymbal` | `MI_DY_AgedBrass` | 锣面中心高光与边缘暗环 |

### 11.60.4 验证与数字
- 编辑器验收帧：`Saved/Audit-2026-10-22-HallFront/hall_front.png`（相机 (-1700,-170,330)→(900,0,380)）、`Saved/Audit-2026-10-22-C2UV/c2_uv.png`（相机 (-1180,-760,190)→(-1480,-1030,110)）。
- Run129：31 文件 / **760,556,929** B；`SourceMapSHA256=5500DF0C61344F35A240EC338C8633460F8E4E4E1264D3BAAAE9375711D4ED5F`；`NativeExeSHA256=C47EB577…E53E2867`（未变）。
- 回归：`AutomationV54` 176/0；sfx 9 cue（16.4/32.4/47.8/63.3 + 24.4/39.8/55.3/70.8 + 76.8）；replay `REPLAY_NEW_LINES=25` / `REACHED_PHASE4=True`；真机帧 `s129-w01..w05.png`（PROBE 98）。
- 注意：`ArtifactBytes` 与 Run128 相同是块对齐巧合，`.ucas` 的 SHA-256 不同，内容确实变了。
## 11.61 观众厅中央地毡（Run130）

### 11.61.1 资产
- 贴图 `T_DY_CarpetCrimson`（512² 无缝深红织纹，`/Game/DengYingShanHai/Dev/ArtPolish_20261022/Textures/`），生成脚本为内联 Node PNG 编码器（8 px 经纬交织、三档值噪声、微斑点、暗格线）。
- 材质实例 `MI_DY_AisleCarpet`：父 `M_DY_GroundTex`（世界坐标 UV），`BaseColorTex`=新贴图、`TileU=TileV=110`、`Roughness 0.95`、`Specular 0.02`、`Tint (1.0,0.94,0.90)`。

### 11.61.2 摆位
| Actor | 位置 | 尺寸 | 材质 |
| --- | --- | --- | --- |
| `ART_HALL_Carpet` | (-460,-105,1.0) | 2560×300×2 cm（顶面 z=2） | `MI_DY_AisleCarpet` |
| `ART_HALL_Carpet_TrimL` | (-460,-253,1.15) | 2560×6×2.3 cm | `MI_DY_AgedBrass` |
| `ART_HALL_Carpet_TrimR` | (-460,43,1.15) | 2560×6×2.3 cm | `MI_DY_AgedBrass` |

- 走向：从门内 x=-1740 直通台口前 x=820；中心线 y=-105（门在 y=-210、影窗在 y=0，走线落在两者之间）。
- 让位：中央走道 |y|<45 上沿留 28 cm 避开 `ART_A4_WallPlinth_R`（y 73–117）的凸出；与长凳（|y|≥350）、台口柱（x=880）不冲突。

### 11.61.3 结果
- 验收帧 `Saved/Audit-2026-10-22-HallFront/hall_front.png`：朱红地毡沿中轴直通影窗，两条金线收边。actor **1788 → 1791**。
- Run130：31 文件 / **760,647,802** B；`SourceMapSHA256=B74471609AEE7A9C4803BB2982E471CAA489798FE09D7596CC7A425BBD683CE3`；`NativeExeSHA256=C47EB577…E53E2867`（未变）。
- 回归：`AutomationV55` 176/0；sfx 9 cue（16.3/32.4/47.8/63.7 + 24.4/39.8/55.7/71.4 + 77.4）；replay `REPLAY_NEW_LINES=25` / `REACHED_PHASE4=True`；真机帧 `s130-w01..w05.png`（PROBE 98）。
- 坑：`MaterialInstanceConstant` 无 `update_material_instance()` / `post_edit_change()`，设完参数直接 `save_loaded_asset` 并重新 `load_asset` 读回验证。
## 11.62 入口石路与全台木纹（Run131）

### 11.62.1 石路贴图
- `T_DY_StonePathTex_BaseColor` 重画（1024²，`gen_stone_v3.py`）：板色 76–90（原 64–96）、裂纹 12 条（原 26）、倒角代替磨角、32×32 低频漂移 ±6、冷灰偏色 [0.985,1.0,1.030]。
- `MI_DY_StonePathTex` 不变：`TileU/TileV=250`、`Tint (0.80,0.80,0.78)`、`Roughness 0.82`、`Specular 0.05`。

### 11.62.2 路缘石
| Actor | 位置 | 尺寸 | 材质 |
| --- | --- | --- | --- |
| `ART_EXT_PathKerb_L` | (-3690,-471,-15) | 3720×22×10 cm | `MI_DY_RockTex` |
| `ART_EXT_PathKerb_R` | (-3690,51,-15) | 3720×22×10 cm | `MI_DY_RockTex` |

### 11.62.3 门内壁灯
- `ART_EXT_WallLamp_00..05` 由 x=-1795 移到 **x=-1762**（原位置在后墙厚度 x∈[-1825,-1775] 内，一半埋墙）；z=1140、y 不变。
- 新增 `ART_LGT_RearWallLamp_00..05`：(-1738, y, 1100)，**110 cd / 半径 420 / cast_shadows=False / 暖色 (1.0,0.78,0.52)**。

### 11.62.4 木纹贴图
- `T_DY_FramePost_BaseColor` 32²→**512²**（深色红木，竖向木纹 + 3 个木节 + 低频漂移），`T_DY_FramePost_NormalDX` 32²→**512²**（由高度场 Sobel 生成，DX 约定，strength 3.2）；`ARM` 保持 32²。
- 材质 `M_DY_FramePost_Master` / `MI_DY_M03_FrameWood` 未改，引用该材质的全部构件一并更新：门罩、影窗框与卷轴、台口、长凳、锣架/案桌/戏箱。

### 11.62.5 结果
- actor **1791 → 1799**；Run131 = 31 文件 / **754,078,426** B（`.ucas` 少 6,567,936 B，`.utoc` -1,440）；`SourceMapSHA256=7D22DC2E…FC977AF6`；exe 未变。
- 回归：`AutomationV56` 176/0；sfx 9 cue（16.3/32.4/48.0/63.5 + 24.4/40.0/55.5/71.2 + 77.2）；replay `REPLAY_NEW_LINES=25` / `REACHED_PHASE4=True`；真机帧 `s131-w01..w05.png`（PROBE 98）。
## 11.63 入口灯径补两对灯柱（Run132）

### 11.63.1 现状与问题
- 灯柱 6 对，x = -2200 / -2700 / -3200 / -3700 / -4200 / -4700，间距 500 cm；左列 y=**-560**、右列 y=**+140**（对称轴是石路中心 y=-210）。
- 石路从 x=-5600 起，玩家起点 x=-6900，最近灯柱到路头还有 900–1200 cm 无光 → 首帧前景全黑。

### 11.63.2 新增构件
| 组 | x | 左列 y | 右列 y | 件数 |
| --- | --- | --- | --- | --- |
| `_6_0` / `_6_1` | -5200 | -560 | +140 | 9 + 9 |
| `_7_0` / `_7_1` | -5700 | -560 | +140 | 9 + 9 |

- 每套 9 件：柱身（`DYTheater_PathLantern`，34×34×250，`MI_DY_RockTex`）、木托、灯纸盒（30³，`MI_DY_LanternPaper`）、灯芯（Sphere，`MI_DY_PathLantern`）、木顶、宝顶、铜帽（52×52×10）、铜顶珠、PointLight（**1500 cd / 1300 cm / 暖色 / 无阴影**）。

### 11.63.3 结果
- actor **1799 → 1835**。
- Run132 = 31 文件 / **754,080,474** B、map `32628AD34FB953F3DED678AF7388BA68E4A44DD118F97BCD09B0AA398C158081`、exe 未变；`AutomationV57` 176/0；sfx 9 cue（16.4/24.7/32.6/40.3/48.3/56.0/64.0/71.5/77.5）；replay `REACHED_PHASE4=True`；真机帧 `s132-w01..w05.png`。


## 11.64 门脸格窗的否定结论（Run133 / Run134）

### 11.64.1 现象与根因
- `ART_EXT_Lattice_*` 26 件挂在门脸上墙（x≈-1818），材质是 `WorldGridMaterial`——引擎默认网格，等于没上材质。
- x=-1818 落在 `DYTheater_Wall`（x∈[-1825,-1775]）体内，26 件只有 5 cm 露在墙外，所以远看只是「淡淡方格」，不构成窗。

### 11.64.2 三次尝试与结果
| 轮次 | 做法 | 结果 |
| --- | --- | --- |
| Run133 | 26 件外移 x=-1834，换 `MI_DY_M03_FrameWood`，加两块 2×900×310 cm 纸面 `MI_DY_LatticePaper` | 木格条在暖光下读成**亮金属网格/铁丝网** |
| Run133 二次 | 每侧删 3 根格条、格子改 `MI_DY_TrunkTex`、纸面调暗 | 变成**纯黑方洞**，更差 |
| Run134 | 删掉全部内部格条（12 件），只留四边框；纸面 `Tint (1.0,0.86,0.66)`、`Glow 1.0` | 编辑器近景「木框 + 微亮装板」尚可；真机 `facade_crop134.png` 仍是**两条近黑横带** |

### 11.64.3 结论
- `pass408_tree.py` 删掉全部 10 件 `ART_EXT_Lattice_*`，恢复到**整面灰泥**（actor 1819 → 1809）。
- **规则**：门脸上墙区域没有专属光源。细格 → 金属丝；暗板 → 洞；自发光 → 被暗部吃掉。此区域只做整面材质，不做格窗、不做装板。

## 11.65 树干竖直化与树冠回滚（Run135 / Run136 / Run137）

### 11.65.1 树干
- 普查 633 个树相关 actor 后发现 **21 根树干 pitch 在 ±21°~±86°**（`DYTheater_DeadTree_0..13`、`DYExt12_Trunk_0..7`），这是「夜空横切黑梁」的根因；crown 的 z 值证明原本按竖直设计。
- `pass411_assign.py`：46 个树干统一换 `SM_DY_Trunk_Unit100`（收尖锥形，97 v / 156 f，`box_extent (34.7,32.1,50.2)`），|pitch|>8 的 21 个改为确定性抖动 ±6、roll=0。

### 11.65.2 树冠：三次重建全部失败
| 版本 | 生成脚本 | tris | 读感 |
| --- | --- | --- | --- |
| 原版 | `build_branch_crowns.py`（源 OBJ 在 `Assets/Sources/DengYingArt/B2-TreePolish-20261022/`） | — | 细枝鹿角，远看是枯树 |
| v1 | `gen_crown.py` | 1092 | 海胆/绒球 |
| v2 | `gen_crown2.py` | 512 | 脚手架硬杆/十字 |
| v3 | `gen_crown3.py` | 2172 | 编辑器尚可，真机成团黑海星（`s136-w01.png`） |

- 回滚：`pass421_restore.py` 用源 OBJ `replace_existing` 重导入，`box_extent` 回到 `(50,50,50)`；截图 `crown_restored.png` 与改冠前 `tree_fix2.png` 字节完全相同（1,444,762 B）。
- **规则**：覆盖自建网格前先找 `Assets/Sources/DengYingArt/<批次>/` 源 OBJ；没有源文件的资产不要覆盖。

### 11.65.3 远山三档
- 92 个山体 actor 只用三个 MI：`MI_DY_MtnFlat_Near/Mid/Far`（父 `M_DY_MountainFlat`，参数 `Glow` + `Tint`）。
- 调暗为 Near (0.050,0.058,0.078) / Mid (0.040,0.048,0.068) / Far (0.034,0.042,0.062)，`Glow` 0.02/0.05/0.08；原值分别是 (0.075,0.095,0.115)、(0.105,0.130,0.160)、(0.150,0.185,0.220)。
- 夜里山体从「白蓝金字塔」退回暗剪影（`s137-w01.png`）。


## 11.66 门口石灯：纸罩暖光与去悬空宝顶（Run138）

### 11.66.1 每根灯柱的真实层级
| z | Actor | 网格/材质 |
| --- | --- | --- |
| 125–143 | `DYTheater_PathLantern_i_j` | Cube，`MI_DY_RockTex`（柱身） |
| 270 | `ART_A5_LanternBase_i_j` | Cube，`MI_DY_FramePost_Wood`（木托） |
| 284 | `DYTheater_PathLamp_i_j` | Sphere，`MI_DY_PathLantern`（发光核心） |
| 287 | `ART_A5_LanternPaper_i_j` | Cube，`MI_DY_LanternPaper`（灯纸） |
| 300 | `DYTheater_PathLight_i_j` | PointLight 1500 cd / 1300 cm |
| 305 | `ART_A5_LanternRoof_i_j` | Cube，`MI_DY_FramePost_Wood`（木顶） |
| 306 | `DYExt32_Cap_i_j` | Cube，`MI_DY_AgedBrass`（铜帽） |
| 311.5 | `ART_A5_LanternFinial_i_j` | Sphere，`MI_DY_AgedBrass`（铜宝顶） |
| ~~324~~ | ~~`DYExt32_Finial_i_j`~~ | Sphere，`MI_DY_PathLantern` —— **Run138 删除** |

### 11.66.2 结论
- `DYExt32_Finial_*` 16 件是**多余的发光宝顶**，比铜宝顶还高 12.5 cm，悬在灯帽之上；删除后 actor 1809 → 1793。
- `MI_DY_LanternPaper`：`Tint` (1.0,0.95,0.88) → **(1.0,0.70,0.40)**、`Glow` 3.06 → **3.9**，纸罩从「白灰块」变成暖琥珀灯罩。
- 真机 `s138-w02.png` 与近景 `C:/dy_build/shots/lamp_warm.png` 对照确认；地图 `SourceMapSHA256=0C86EB7F…3DDDE27B`。


## 11.67 门脸台基改灰石（Run139）

- 三件台基：`ART_A3_RearPlinth_L`/`R`（Cube，z=75）、`ART_EXT_RearBase`（Cube，z=65），原本共用 `MI_DY_RockTex`（与 49 块山石同一实例）→ 夜景读成发绿霉的混凝土横带。
- 新增 `/Game/DengYingShanHai/Dev/ArtPolish_20261022/Materials/MI_DY_PlinthStone`：父 `M_DY_RockTex`，`Tint` (0.86,0.83,0.76)、`TileU/TileV` 90、`Roughness` 0.96、`Specular` 0.05，赋给上述三件。
- 失败备选：`MI_DY_PlinthTex`（父 `M_DY_GroundTex` + `T_DY_StonePathTex_BaseColor`，`Tile` 110）在 4–10 m 长构件上把石板拉成竖条，读作木板墙，未采用（资产保留）。
- 真机 `s139-w02.png` 裁切 `C:/dy_build/crop_base139.png` 确认：绿霉消失，台基为中性暖灰石基；地图 `SourceMapSHA256=69B02ADB…F09998C9`。


## 11.68 门内后墙两幅挂屏（Run140）

- 后墙（x=-1800，内表面 x=-1775）门洞两侧各 4 m 空白；侧墙已有 4 幅 `ART_HALL_Art_L/R_0..3`（Cube、`MI_DY_HallFrame_Kuafu/Xingtian`、scale (1.36,0.03,2.06)、z=820）。
- 新增 `ART_A3_RearHangPanel_0/1`（画心，x=-1760，y=∓620，z=880，scale (0.03,1.36,2.06)）+ `ART_A3_RearHangFrame_0/1`（木框板，x=-1762，scale (0.02,1.46,2.22)，`MI_DY_M03_FrameWood`），共 4 件；actor 1793→1797。
- 试过并回滚：4 根竖向木筋 `ART_A3_RearBatten_0..3`（读成悬空细棍）、一根通长上梁 `ART_A3_RearBeam_Top`（被天花板吃掉）。
- 真机 `s140-w01..w05.png` 与编辑器图 `C:/dy_build/shots/rearpanel2.png`；地图 `SourceMapSHA256=97A1E870…4A9FB127`。


## 11.69 檐口封板与檐木材质（Run141）

- 屋顶结构：`DYTheater_Roof_A/B/C` 三块平板在 z=1900（厚 40 cm）；墙头 `DYTheater_RearWall_Head` 顶面 z=1900；檐板 `DYExt30_Eave_00/01/02` 在 x=-1848/-1855/-1862、z=1946/1974/2002（外挑、逐层升高），翘角 `DYExt30_EaveTip_0/1` 在 z=2016；发光条 `DYExt30_EaveGlowStrip` 在 (-1892,-40,1940)。
- 修复：5 件檐木材质 `MI_DY_RockTex` → `MI_DY_M03_FrameWood`；新增封檐板 `ART_A6_EaveFascia_Front`（Cube (-1846,-210,1920)，scale (0.30,28.6,0.55)）与 `ART_A6_EaveFascia_In`（Cube (-1798,-210,1920)，scale (0.12,26.2,0.45)），均不投影；actor 1797→1799。
- 编辑器验证图 `C:/dy_build/shots/eave.png`（修复前，可见亮蓝天缝）与 `eave2.png`（修复后）；地图 `SourceMapSHA256=B4E8D883…77E212B`。


## 11.70 门脸壁灯补实体（Run142）

- 普查（`C:/dy_build/pass454_lights.py` → `pass454.json`，58 条灯光）：室外侧有 6 盏只发光、无实体的补光灯——`ART_LGT_WallFill_00..03`（x=-1880，y=-1030/-700/330/660，z=1120，380 cd / 1000 cm）与 `DYExt16_FacadeLamp_L/R`（x=-1885，y=-1180/700，z=780，480/380 cd / 1100 cm）。
- 修复（`C:/dy_build/pass455_facadelamp.py`）：以 `ART_EXT_WallLamp_00` 为模板复制 6 盏 `ART_EXT_FacadeWallLamp_00..05`（`SM_DY_LanternFamily_Unit100`，scale 0.72，无阴影，STATIC），位置 = 对应灯光 + x 47 cm（朝墙侧），使灯罩正好位于光斑中心。actor 1799 → 1805。
- 验证图 `C:/dy_build/shots/facade_lamp.png`；真机对比 `s141-w02.png`（光斑无灯）→ `s142-w02.png`（两对挂牌壁灯 + 下方一对）。
- 地图 `SourceMapSHA256=7F26FCF6…AC308173`。


## 11.71 入口石路石材试验与回退（Run143）

- 试验：`C:/dy_build/gen_stone_v4.py` 生成 2048² 交错石板贴图 → 覆盖 `T_DY_StonePathTex_BaseColor` → 图 `C:/dy_build/shots/path_v4.png`、`path_v4b.png`（再把 Tile 250→520、Tint 压到 0.72）。
- 判定：夜景里路面过亮、视觉重心从门脸转移到地面，且放大 Tile 没能有效放大石板 → **判负并回退**。
- 回退：`C:/dy_build/pass459_revert.py` 重导 `C:/dy_build/T_DY_StonePathTex_BaseColor_v3.png`，并把 `MI_DY_StonePathTex` 参数钉死为 TileU/TileV 250、Tint (0.80,0.80,0.78)、Roughness 0.94、Specular 0.02；图 `C:/dy_build/shots/path_rev.png`。
- 结论：入口路面保持**暗灰、低对比**是最稳的夜景做法；不要再往「更精细更亮」方向改。
