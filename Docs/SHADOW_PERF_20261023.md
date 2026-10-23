# 动态皮影演出系统（2026-10-23）

对应需求：@D:\DYS_SHADOW_PUPPET_GAMEPLAY_UPGRADE_20261023.md。目标是把"静态影偶 + 解谜判定"升级成"解谜成功 → 幕布上真的动起来演神话 → 再推进流程"，并且不破坏既有判定、可跳过、打包可用。

## 1. 系统构成

| 层 | 资产 / 类型 | 说明 |
| --- | --- | --- |
| 数据 | `UDYPuppetPerformanceData`（`/Game/DengYingShanHai/Puppets/DA_DYPuppetPerformance`），**只通过影偶实例上的 `PerformanceData` 显式挂接**（关卡里 `M2_Puppet_P02_Controlled` 的 Performance 组件） | 四幕（`FDYActPerformance`），每幕 5 个段落 + 1 条即时反馈；段落字段 `Animation`（UAnimSequence 软引用）、`Seconds`、`Caption`、`bLoop` |
| 运行时 | `UDYPuppetPerformanceComponent`（挂在 `ADYPuppetActor`） | `StartChapterPerformance` / `SkipPerformance` / `TriggerFeedback` / `IsPerforming`；逐段 `PlayAnimation` + `SetPosition(0)`，段末换段，结束 `RestorePose`（回到当前 pose） |
| 导演 | `ADYPuzzleDirector` | 本章**最后一幕**解谜成功 → 先播整幕演出，把 `OnPuzzleResolved` 延迟到演出结束（播完/跳过）后发布一次；非最后一幕只按 Progress 0.85 / 0.6 / 0.35 分桶触发 1.2 s 关节反馈 |
| 输入 | `ADYDevEntryPlayerController` | `BindKey(SpaceBar)` → `SkipAnyPerformanceInWorld`，Development / Shipping 都生效 |
| 字幕 | `UDYInteractionHUDWidget::ShowHint` | 每段一句幕间字幕，统一追加"空格可跳过演出"以保证可发现性 |

新文件（`Source/DengYingShanHai/`）：

- `Public/Puppets/DYPuppetPerformanceTypes.h`、`Private/Puppets/DYPuppetPerformanceTypes.cpp`
- `Public/Puppets/DYPuppetPerformanceComponent.h`、`Private/Puppets/DYPuppetPerformanceComponent.cpp`

改动文件：`Public/Interaction/DYPuppetActor.h`、`Private/Interaction/DYPuppetActor.cpp`、`Public/Puzzles/DYPuzzleDirector.h`、`Private/Puzzles/DYPuzzleDirector.cpp`、`Public/Core/DYDevEntryPlayerController.h`、`Private/Core/DYDevEntryPlayerController.cpp`。

## 2. 四幕编排

| 幕 | 时长 | 段落（每段 2.2–2.6 s） | 即时反馈 |
| --- | --- | --- | --- |
| 第一幕·夸父逐日 | 12.0 s | Run 追光 → Reach 举杖向烈日 → Stagger 热浪踉跄 → Fall 单膝落地 → Slump 弃杖化林 | Reach |
| 第二幕·精卫填海 | 12.4 s | Flap → Dive 掷石入海 → Hover → Dive → Flap 填海不止 | Flap |
| 第三幕·刑天舞干戚 | 12.2 s | AxeRaise 举斧 → AxeSwing 横挥 → Guard 盾挡 → Stomp 顿足 → Roar 咆哮 | AxeRaise |
| 第四幕·烛龙昼夜 | 12.6 s | Coil 盘身 → HeadRise 昂首睁眼 → Swim → HeadRise → Settle 昼夜既定 | HeadRise |

动画源在 Blender 侧生成（`Assets/Sources/DengYingArt/ThreePuppets-20261022/perf_clips.json` + `build_perf_anim.py`，Run5），导入到 `/Game/DengYingShanHai/Puppets/Animations/A_DY_<角色>_Perf_*`（17 条）：

- 夸父 6：`Perf_Run/Reach/Stagger/Fall/Slump/Rise`
- 精卫 4：`Perf_Flap/Dive/Hover/Land`
- 刑天 5：`Perf_AxeRaise/AxeSwing/Guard/Stomp/Roar`（无 Head 骨）
- 烛龙 4：`Perf_Coil/HeadRise/Swim/Settle`

平面内关节动作统一绕**世界 X 轴**四元数旋转：`m = pb.bone.matrix_local.to_3x3(); a = (m.inverted() @ Vector((1,0,0))).normalized(); pb.rotation_quaternion = Quaternion(a, radians(deg))`。

## 3. 时间语义（关键设计）

一"幕"（chapter）含三场"次幕"（act）。按需求文档，**整幕演出只在本章最后一幕解谜成功时播放**；前两场只播 1–3 s 的关节反馈。这样既满足"关键操作 1–3 s 内有可见动作"，又满足"幕完成才播 12–20 s 连续演出"。

```
DYPuzzleDirector.cpp（解谜成功块）
const bool bChapterFinaleShow = IsActSequenceEnabled() && IsFinalSequenceAct();
if (bChapterFinaleShow && Performance->StartChapterPerformance(CurrentChapterIndex)) { 延迟 OnPuzzleResolved }
else { ScheduleCampaignChapterFallback(); OnPuzzleResolved.Broadcast(...); }
```

演出结束（自然播完或空格跳过）都会走 `PublishResolvedSequence()`：校验 ActivationToken → 计时 fallback → 广播一次 → 章节推进照旧。因此**跳过与播完对流程等价**。

## 4. 验证证据

### 4.1 打包运行日志（Development RunD10）

`Builds/FormalMain-Development-20261023-RunD10/Windows/DengYingShanHai/Saved/Logs/`（UE 每次启动会把上一次日志改名为 `DengYingShanHai-backup-*.log`；归档副本 `Saved/Audit-2026-10-23-Performance/Packaged/RunD10-performance-fullplay.log` 与 `RunD10-performance-skip.log`）：

| 场景 | 关键日志（UTC） |
| --- | --- |
| 第一幕播完 | 09.23.04 `chapter 0 starts: 5 segments, 12.00 s, mesh=KuafuMesh` → 09.23.16 `chapter 0 finished skipped=0 at 12.02/12.00 s` → 同刻 `Puzzle P03_DevPlayableCandidate resolved exactly once` |
| 第二幕接续 | 09.24.03 `chapter 1 starts: 5 segments, 12.40 s, mesh=DYChapterCastMesh` → 09.24.16 `chapter 1 finished skipped=0 at 12.42/12.40 s` → `P04_Jingwei_03 resolved exactly once` |
| 第三幕接续 | 09.24.24 起 `chapter 2 feedback beat 0`（同一轮运行里连续三章都进入演出） |
| 空格跳过 | 09.24.51 `chapter 0 starts` → 3.79 s 时 `chapter 0 finished skipped=1 at 3.79/12.00 s` → 同帧 `P03 resolved exactly once` + `[PuppetPerformance] skipped by player.` |
| 即时反馈 | 每幕解谜过程中 `chapter N feedback beat 0` 反复出现（每次 1.2 s 关节动作后回位）；`P01`/`P02` 等非最后一幕只播反馈、立即发 resolve |
| 字幕与可发现性 | 帧证据 `Packaged/RunD10-Captions.png`：五段字幕依次出现，每段尾缀「空格可跳过演出」 |

### 4.2 幕布取样（UE 编辑器内，真实骨骼动作）

脚本 `Content/Python/perf_capture_ue.py`：逐幕切换影偶与题签，把每个段落的动画分别采 2 帧（25% / 75%），观众机位 (−980,−80,250) → (760,−80,250) FOV 62，1280×800。产物：

- `Saved/Audit-2026-10-23-Performance/PerfUE-Act1.png`（夸父：跑 / 伸手 / 踉跄 / 前扑 / 蹲伏）
- `.../PerfUE-Act2.png`（精卫：振翅 / 俯冲 / 悬停）
- `.../PerfUE-Act3.png`（刑天：举斧 / 横挥 / 盾挡 / 顿足 / 咆哮）
- `.../PerfUE-Act4.png`（烛龙：盘身 / 昂首 / 游动 / 收势）
- 逐帧原图 40 张在 `.../Performance/UE/Act<幕>-seg<段>-f<帧>.png`，报告 `perf-ue-capture.json`（ok=true，0 错误）

### 4.3 数据与 cook

`Content/Python/import_perf_ue.py` 报告 `perf-import.json`：4 幕、152 项断言、0 错误；RunD9 的 `DengYingShanHai-Windows.utoc` 里 `DA_DYPuppetPerformance` 与 17 条 `A_DY_*_Perf_*` 全部在包内（上一包 767 → 本包 785 个 cooked package）。

### 4.4 自动化回归

`AutomationV71.log`：EXIT 0，**180 Success / 0 Fail / 0 Warning**（`DengYingShanHai` 全部测试）。

修复前 `AutomationV70.log` 为 172 / 8 Fail，8 个失败全部来自"组件固定路径回落加载 DA"导致夹具里的 `OnPuzzleResolved` 被延迟（见第 7 节）。改为影偶实例显式挂接后恢复。

### 4.5 Shipping Run145（公开候选包）

`Builds/FormalMain-Shipping-20261023-Run145`：BUILD SUCCESSFUL，Packages Cooked 785，32 文件 / 856,413,975 B；`DengYingShanHai-Windows.utoc` 291,597 B 内含 `DA_DYPuppetPerformance`、17 条 `A_DY_*_Perf_*`、`SK_DY_Xingtian`、`MI_DY_TitleGlyph_Act4`。

Shipping 配置不写日志文件（`bUseLoggingInShipping`），因此用帧证据（`C:\dy_build\frames\s145c`、`s145d`，PostMessage 驱动、不抢前台）：

| 证据图 | 内容 |
| --- | --- |
| `Packaged/Shipping145-Captions.png` | 单轮运行里五段字幕依次出现：追日 → 伸手 → 踉跄 → 单膝落地 → 弃杖化林（尾缀"空格可跳过演出"） |
| `Packaged/Shipping145-PerfFrame.png` | 演出中整帧（幕面 + 字幕 + 顶部阶段提示） |
| `Packaged/Shipping145-Skip.png` | 12.7 s 时按空格：字幕立即回落到常规提示"对准灯具或皮影／影形已合，静待杖落成林"，后四段不再出现 → 跳过与恢复在 Shipping 同效 |

exe：`Windows/DengYingShanHai/Binaries/Win64/DengYingShanHai-Win64-Shipping.exe`，166,376,960 B，SHA256 `4148b55b35c2268c1e1551f8d874a19d2114d99290533d3114e6e014ae2ec1d2`。

### 4.6 公开入口切到 Run147

因为影偶实例挂接 DA 需要保存 `L_DY_Main`，地图哈希从 `E325713B…` 变为 `F03F9E32…`，此前指向 Run146 的正式入口预检会失败。于是用同一份 Shipping 编译产物重打一版并重新签名：

- 归档：`Builds/FormalMain-Shipping-20261023-Run147`，31 文件 / 856,412,694 B（Development 对照：RunD10 56 文件 / 1,215,421,639 B），exe 同 SHA256（与 Run145 同一二进制）
- 身份：`Windows/RELEASE-ENTRY-BUILD.json`，`SourceMapSHA256 = F03F9E320570CF84D7A5B854CC669480D490A80B9989C2EC34E607F788B082A3`
- 入口：`Scripts/Start-FormalShipping.ps1` 改指 Run147，`-DryRun` = `PASS-PREFLIGHT-ONLY`（31 文件 / 856,412,694 B）
- Run147 实机：`Packaged/Shipping147-Captions.png`（字幕依次出现：追日 → 伸手 → 踉跄 → 单膝落地），utoc 内 `DA_DYPuppetPerformance`、17 条 Perf 动画、三具影偶、题签材质齐全
- 回退点：Run146（31 文件 / 856,338,919 B，入场墙修复版，无演出系统）目录与身份文件都未改动

## 5. 需求验收对照（A01–A10）

| 编号 | 要求 | 结果 | 证据 |
| --- | --- | --- | --- |
| A01 | 关键操作 1–3 s 内明显动作，且不重复 | 达成 | Progress 分桶 0.85/0.6/0.35 触发 `feedback beat`，每幕固定一条 1.2 s 反馈镜头 |
| A02 | 完成谜题后播放完整神话演出（追日→力竭→化林） | 达成 | PerfUE-Act1.png 五段动作 + RunD10 日志 12.00 s 播完 + Shipping145-Captions.png |
| A03 | 演出可跳过，且提示可发现 | 达成 | 每段字幕尾附"空格可跳过演出"；日志 `skipped by player` |
| A04 | 正常结束（播完/跳过）后输入、相机、UI 全部恢复 | 达成 | `Finish` → `RestorePose` → 发布 → 章节推进；跳过与播完走同一收尾 |
| A05 | 跳过与播完对流程等价 | 达成 | 两种路径都只发一次 `resolved exactly once`，随后进入下一幕 |
| A06 | 快速反复触发不重入 | 达成 | `StartChapterPerformance` 在 `bPerforming` 时直接返回 false；`StartCurrentPuzzle` 先 `SkipPerformance` 再绑新演出 |
| A07 | 同角色造型/比例/关节一致 | 达成 | 动画与影偶共用 Run4 骨架；取样图剪影与四幕成片一致 |
| A08 | 不破坏既有解谜判定 | 达成 | 判定逻辑未改；演出只在判定成功后接管通知 |
| A09 | 四幕都能演 | 达成 | 四份 PerfUE-Act*.png + DA 四幕各 5 段 |
| A10 | 打包可用 | 达成 | RunD10（Development）日志复现整章演出与跳过；Run145（Shipping）帧证据复现同一演出，utoc 含全部动画与 DA |

## 6. 复现方式

```powershell
# 1) 生成动画（Blender，Run5）
python prepare_meshes.py Run4 ; blender -b --python build_perf_anim.py -- Kuafu   # 四个角色各跑一次
# 2) 导入 UE + 建 DA
powershell -File C:\dy_build\run_ue_script.ps1 -Script D:\灯影山海\Content\Python\import_perf_ue.py
# 3) 幕布取样
powershell -File C:\dy_build\run_ue_script.ps1 -Script D:\灯影山海\Content\Python\perf_capture_ue.py
# 4) 打包
RunUAT.bat BuildCookRun -project='D:\灯影山海\DengYingShanHai.uproject' -noP4 -platform=Win64 -clientconfig=Development -cook -stage -pak -archive -archivedirectory='D:\灯影山海\Builds\FormalMain-Development-20261023-RunD10'
# 5) Shipping（先单独编 Shipping exe，再 cook，不带 -build）
RunUAT.bat BuildCookRun ... -clientconfig=Shipping -cook -stage -pak -archive ^
  -archivedirectory='D:\灯影山海\Builds\FormalMain-Shipping-20261023-Run145'
```

运行期可用环境变量做无人工验证：`DY_CAMPAIGN_AUTOPLAY=1`（自动把灯/偶推到目标值解谜）、`DY_CHAPTER=N`（从菜单直接开第 N+1 幕）、`DY_DEBUG_VIEW=7`（观众席全景机位）、`DY_MUTE_BGM=1`。外部输入可以用 `C:\dy_build\sendkey_msg.ps1 -TargetPid <窗口进程> -Vk 0D` 以 PostMessage 送到非前台窗口（本机实测有效，不必抢焦点）。

## 6.5 交付包

`Assets/Sources/DengYingArt/ThreePuppets-20261022/DY_Performance_20261023.zip`：131 文件 + `MANIFEST.json`，38,118,228 B，SHA256 `8E965B75371D564BAAAB80BD55301B5991132E1972D606D7F97C6E78D216EFDD`，CRC 全通过。

| 目录 | 内容 |
| --- | --- |
| `Source/` | `perf_clips.json`（四角色片段规格）、`build_perf_anim.py`、四个新 C++ 文件（Types/Component 的 .h/.cpp） |
| `Animations/<角色>/` | 20 个 FBX + `perf_anim_report.json` + 预览帧（Run5） |
| `Tools/` | `import_perf_ue.py`、`perf_capture_ue.py`、`bind_perf_data.py` |
| `Evidence/` | 4 张 ClipSheet、4 张 PerfUE-Act、`perf-import.json`、`perf-bind.json`、`Packaged/`（RunD10 日志 + 字幕帧 + Shipping 字幕/跳过帧） |
| `Docs/` | 本文件 |

## 7. 已知边界与未做项

- 只在 `bFourActCampaign` 且影偶实例显式挂了 DA 时启用；自动化夹具（临时世界、默认 Actor）没有这个挂接，因此完全走旧路径。
- 早期版本在组件里写了"固定路径回落加载 DA"，结果自动化夹具也捡到了这份资产，把 `OnPuzzleResolved` 延迟掉，导致 8 个流程测试失败（`AutomationV70.log`）。改为"显式挂接"后恢复（`AutomationV71.log`）。这条经验保留在代码注释里。
- P1 未做：分段锣鼓/配音、每幕一次三维世界呼应、固定观演机位切换（当前沿用玩家视角）。
- P2 明确不做：物理布偶、写实过场、真实投影方案 B。
- 演出期间按 Esc 仍可回菜单（未额外加锁）。
- Shipping 不落日志，因此 Shipping 侧验收只能依赖帧证据（无 `skipped=1` 文本行）；语义等价性由 Development 日志 + Shipping 字幕/恢复帧共同证明。
- Run145 目录是 10:46 那次入场墙修复包的旧名，本轮第一版 Shipping cook 覆盖了它；对外入口用的是 Run147，Run145 只作过程目录，不再引用。
- 打包内菜单的"演出篇章"面板需要 Slate 真实点击才能开演（PostMessage 鼠标只改选中），自动验证统一走 `DY_CAMPAIGN_AUTOPLAY=1` + `DY_CHAPTER=N` 路径。

## 8. 第一幕「弃杖化林」修复（2026-10-23 晚）

### 8.1 两个独立缺陷

1. **通知令牌丢失（逻辑层）**：最后一幕的 `OnPuzzleResolved` 被推迟到演出结束后才广播，但 `PuzzleNotificationToken` 的作用域只覆盖评估函数栈，广播时令牌已失效，`ADYStagePresentation::HandlePuzzleResolved` 直接 return，接触点从未被捕获。修复：`ADYPuzzleDirector::PublishResolvedSequence()` 内补 `TGuardValue<FGuid> NotificationScope(PuzzleNotificationToken, NotifiedToken)`。
2. **接触比播报晚 2 秒（时序）**：BP 在 resolve 后 +2.0 s 才接受杖尖接触，旧逻辑在那一刻立即判定 `contact=0` 并放弃。修复：`PlayCampaignForestFinale` 改为等待 `StaffContactAccepted`（6 s 超时），接受后再延迟 0.25 s 启动成长——BP 在接触节点之后会同步清一次森林，提前启动会被清掉。
3. **树长在幕布面上（视觉层）**：林影长在叙事地线 `M3_RuntimeNarrativeGroundLine`（X=925.0），而幕布 `DEV_BackScreen` 在 X=925.1，几何体一半埋在幕布里，观众只看到几根细线。修复：`ADYForestPresentationActor` 增加 `WorldOffset`（默认零，几何测试不变），地图实例设为 (-40, 0, 0)，整片林向观众侧前移 40 cm。

### 8.2 证据

| 证据 | 文件 |
| --- | --- |
| 成长日志（接触→成长→满） | Development 日志：`[StaffContact] accepted` → `[CampaignForest] growing over 2.60 s.` → `full growth reached.` |
| 打包内林影成片（Run150） | `Saved/Audit-2026-10-23-Performance/Run150-Forest-Stages.png` |
| 打包内整幕（Run149/150） | `Run149-Forest-Audience.png`、`Run149-Forest-Zoom.png` |
| 地图挂接报告 | `forest-offset-bind.json`（before 0,0,0 → after -40,0,0，saved=true） |
| 自动化回归 | `Saved/Logs/AutomationV72.log`：186 Success / 0 Fail / EXIT 0 |

### 8.3 入口

公开入口脚本 `Scripts/Start-FormalShipping.ps1` 指向 **Run150**（31 文件 / 857,104,982 B，Shipping exe SHA256 `1797E9BF…`，地图 SHA256 `A048066A…`）。`-DryRun` = `PASS-PREFLIGHT-ONLY`。Run149（含逻辑修复、不含林影前移）与 Run148（入场墙修复版）保留作回退。

## 9. 密林美术尝试与回退（2026-10-23 深夜）

### 9.1 目标与做法

用户在 Run150 观察到成林只有 15 枝、约 100 cm 高的小树，「要茂密森林，优化美术」（m05228）。做法：把 15 枝布局换成 120 枝 / 56 个树冠簇的多层密林（7 棵树、高矮两档、地下横生根、中段侧枝、深墨绿剪影材质 `MI_DY_ForestCanopyInk`），并给 `ADYForestPresentationActor` 增加 `CanopyScales`（逐簇缩放）与 `CanopyMaterial`（统一树冠材质）两个 UPROPERTY。

### 9.2 失败现象与根因

- **Run151–Run153**：接触后约 1.3 s 出现 BP 文案「Dev 表现中止 · 使用当前操纵对象 R 复位」，幕布上没有任何树影。
- **Run160–Run162 诊断**：把日志写进文件（Shipping 不落日志，只能在自建文件里追加），确认接触被接受、`BeginSession` 被调用、`BS stage sample-ok / branches-done / canopies-done` 全部通过，但 `TryBegin` 尾部的生长启动行从未出现——组件、采样、树冠都建好了，失败发生在「启动生长 → BP 表现」这一段。
- **Run165 对照**：换成 12 枝 / 5 冠的极简布局，仍是同样的「Dev 表现中止」、仍无树影。说明**不是密林布局越界**，而是本轮改动（重编译/重保存 `BP_DYForestPresentation_Dev` 或 C++ 会话启动路径）整体破坏了第一幕这条链路；Run150 的同一逻辑用 15 枝是正常的。
- Run164 曾把生长启动前移到 `BeginForestPresentation`，日志能打全，画面仍无树 → 说明上游逻辑通了，断点在 BP 侧的接收/渲染。

### 9.3 回退决策（用户指令）

User said (m06658): "弄不出来就停，功能正常就行"。因此停止密林迭代，把地图森林数据恢复为 Run150 的 15 枝布局（`Content/Python/apply_restore_forest.py`：`branch_layout` 15 条 / `canopy_branches` [9,10,11,12,13] / `canopy_world_scale` 0.9 / `canopy_material` 空 / `canopy_scales` 空 / `world_offset` (-40,0,0)），移除全部 `DYForestDebugLog` 插桩，重编 Editor + Shipping，重 cook 出 **Run167**。

### 9.4 证据（Run167）

| 证据 | 位置 |
| --- | --- |
| 恢复报告 | `Saved/Audit-2026-10-23-Performance/forest-restore-run150.json`（ok=true，0 failed checks） |
| 打包内成林帧 | `C:/dy_build/frames/run167/`（v022/v023「林影已成」，无 Dev 中止）、`run167b/`（w029–w031 同上） |
| 成片拼图 | `C:/dy_build/frames/run167-sheet.png`、`run167b-sheet.png` |
| 自动化回归 | `Saved/Logs/AutomationV74.log`：186 Success / 0 Fail / EXIT 0（回退后源码） |
| 打包身份 | `Builds/FormalMain-Shipping-20261023-Run167/Windows/RELEASE-ENTRY-BUILD.json`（Shipping exe SHA256 `B6804EF4…`，地图 SHA256 `B27CAF41…`，31 文件 / 857,111,126 B） |
| 入口脚本 | `Scripts/Start-FormalShipping.ps1` 指向 Run167，`-DryRun` = `PASS-PREFLIGHT-ONLY`（ArtifactCount 31 / ArtifactBytes 857,111,126） |

### 9.5 结论与遗留

- 第一幕「弃杖化林」恢复为 Run150 的可用版本：小树成林、章节推进、无「Dev 表现中止」。密林（120 枝）在几何与采样层已验证通过（`dense-forest-apply5.json` ok=true），但在 BP 表现层无法落地，作为**已知未完成的美术目标**记录在此。
- `CanopyScales` / `CanopyMaterial` 两个 C++ 属性保留在代码里（默认空/空 = 旧行为，不影响 Run167），供后续重做密林时直接使用。
- 后续若重启该目标，第一步应是：用 Development 或编辑器内 PIE 复现「接触 → BeginSession → 生长」这一段，在 BP `BP_DYForestPresentation_Dev` 里检查 `BeginSession` 之后是否有节点重置/隐藏森林；不要先动布局数据。
- 四幕完整人工通关与观感验收仍是人工项。
