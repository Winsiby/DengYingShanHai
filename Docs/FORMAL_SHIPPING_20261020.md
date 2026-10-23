# 灯影山海 · Shipping 重打包记录（2026-10-20 → 2026-10-22 / 当前包 Run143，历史各包见 §9 与 Docs/BASELINE-V21.md）

> 触发原因：Run6 之后修了**结束态（复演已成）露出背景图里烤死的旧菜单列**——"章节选择"、图标与灰底文字在原画里，结束面板一收起自家菜单列就把它露了出来。该修动的是入口 C++，因此重打包为 Run7。Run1–Run4 为迭代中间产物，Run5 因打包期间改源码而**作废**，Run6 为外景起步版，**Run7 是与当前源码/地图一致的正式包**。

## 1. 产物

| 项 | 值 |
|---|---|
| 归档目录 | `D:\灯影山海\Builds\FormalMain-Shipping-20261020-Run7\Windows` |
| 构建审计 | `D:\灯影山海\Saved\Audit-2026-10-20-V21\Package-Run7` |
| 配置 / 平台 / 目标 | Shipping / Win64 / Game |
| 地图 | `/Game/DengYingShanHai/Maps/L_DY_Main` |
| 产物数量 | 31（另有身份文件 `RELEASE-ENTRY-BUILD.json`，归档内共 32 个文件） |
| 总字节 | 756,892,370 |
| `NativeExeSHA256` | `58B8631A1F9BB3FAC6F393903C955A37C922756B40E8FF04C29832BBCA47C1C6` |
| `SourceMapSHA256` | `5512ABA3BDFB32529484688E1507D169D01A305613DBB3BB713B7CB653F6B800` |
| 源地图大小 | 668,368 字节（含 226 个 `DYTheater_*` actor，本包地图与 Run6 相同） |
| CookedMaps | `L_DY_Main.umap`、`Engine/Content/Maps/Entry.umap` |
| UAT 结果 | `BUILD SUCCESSFUL` / `ExitCode=0 (Success)` / `BuildCookRun time: 115.18 s` |

身份文件 `RELEASE-ENTRY-BUILD.json`（归档根）、`ARTIFACTS.json` / `RESULT.json`（审计目录）由 `C:\dy_build\finalize_package.ps1` 在 UAT 后写盘，其中 `UATActualExit=0`。

## 2. 本轮改动（进了这个包的）

### 2.1 结束态菜单一致性（Run7 的唯一功能变更）

- 根因：`T_MenuBackground` 原画里**自带一列菜单**（开始游戏 / 继续游戏 / **章节选择** / 游戏说明 / 设置 / 退出游戏，带图标）和右下"游戏说明"纸卡。Slate 牌匾平时正好盖住它们，但 `UDYDevEntryWidget::RefreshView()` 在 `End`/`Reloading` 面板把 `MenuColumn` 与 `GuidePanel` 设成 `Collapsed`，原画里的旧列就露出来了，与"演出篇章"版本自相矛盾。
- 修法：两块**始终保持 `SelfHitTestInvisible`**（结束态不再收起），把原画旧列盖住；结束卡的独立"重新复演"按钮改成 `Collapsed`，让**菜单列首牌位**（`PrimaryLabel`）在结束态就是"重新复演"这唯一的 CTA：
  - `IsMenuItemAvailable(0)` → `bStartPanel || CurrentPanel == EDYDevEntryPanel::End`；
  - `HandleMenuSelection(0)` → 结束态走 `RequestReplayExperience()`，其余态仍走 `RequestStartExperience()`；
  - `HandlePrimaryClick()` 允许 `End`（`SetWidgetToFocus(PrimaryButton)` 保证 Enter 可直接重演）；
  - 结束语改成「杖落成林，未完的戏终于演到此刻。选「重新复演」或按 Enter 重新载入。」（原句过长会把结束卡撑宽、压到右下引导卡上）。
- 只影响结束态外观与入口；三幕判定、舞台相机、Director 未动。
- 新增**仅非 Shipping**的调试开关 `bPreviewEnding`（环境变量 `DY_MENU_PANEL=end`），用于在编辑器 -game 里直接看结束面板；`#if !UE_BUILD_SHIPPING` 包住，Shipping 二进制不含它。

### 2.2 外景起步（用户要求：不在戏台前直接开场）

- `PlayerStart` 从 `(-900,-210,120)` 移到外景 **`(-4600,-210,60)`、Yaw=0**（正对后门），改由 `C:\dy_build\entry_walk.py` 一次性写入地图；
- 同脚本补四盏仅照门径的暖光：`DYTheater_EntryLamp_L/R` 在 `X=-4460, Z=320`、`DYTheater_GateLamp_L/R` 在 `X=-2020, Z=470`（强度 2600 / 5200，无阴影），保证夜里能看清"往哪走"；
- 点「开始游戏」后 `ADYDevEntryPlayerController::BeginEntryWalkGuidance()` 接管：隐藏舞台 HUD、显示中央引导句「沿灯径向灯火深处走去，入戏台」10 s，每 0.25 s 检查玩家 X，越过 `X > -1700`（门内侧）就算入戏台 → 恢复 HUD、显示「入戏台」4 s，并写日志 `Entry walk: player crossed into the theater at ...`；**60 s 兜底**也会恢复 HUD。

### 2.3 舞台 HUD 外景分层

- `UDYInteractionHUDWidget::SetStageHudVisible(bool)`：只控制舞台专属元素（题签、提示底板、准星、状态/就绪/保持进度），外景仍保留菜单与引导句；
- `ADYInteractionHUD::SetStageHudVisible` 转发；控制器 `EndPlay` 清掉两个计时器。

### 2.4 字体与音频 cook

- `FF_MenuSerif_Font` / `FF_MenuSerifBold_Font` 实际不存在（`FF_MenuSerif.uasset` 是 FontFace），原 `FObjectFinder` 让 CDO 在打包版刷 `Failed to find object` 报错；改为 `LoadObject<UFont>(... LOAD_NoWarn | LOAD_Quiet)` 静默回退，并删掉两个空资产；
- `Config/DefaultGame.ini` 增 `+DirectoriesToAlwaysCook=(Path="/Game/DengYingShanHai/Dev/Audio")`，C++ 里的 soft path 音频不再漏 cook。

## 3. 包装脚本的假阴性（已修）

`Package-Shipping.ps1` 用 `Start-Process -Wait -PassThru` 调 `cmd /c RunUAT.bat`，本机拿不到 `$dyProcess.ExitCode`（恒为 null），UAT 成功也会抛 `UAT failed with exit `。
判据已改为读 `UAT-stdout.log` 的 `AutomationTool exiting with ExitCode=0`：`$dyExit` 为 null 时按该判据回填 0/-1，再决定是否抛错。Run5 就是被这条旧逻辑误杀（UAT 其实成功），Run6/Run7 均一次跑通并把身份文件写全。

## 4. 机器验证（Run7 包内，1920×1200）

| 步骤 | 证据 | 结论 |
|---|---|---|
| 冷启动 | `Saved/Audit-2026-10-20-V21/run7-menu.png` | 六牌匾齐全、CJK 正常；「继续游戏」禁用，「开始游戏」红匾高亮 |
| 按 Enter | `run7-outside.png` | **开局在外景灯径上**，正前是亮着灯的后门与门内幕布；中央显示「沿灯径向灯火深处走去，入戏台」；题签/准星/状态框全部隐藏 |
| W 前进过门 | `run7-hall.png` | 进入大厅：题签「引日启幕」、准星、右下状态框恢复 |
| 按 Esc | `run7-pause.png` | 回菜单，「开始游戏」转禁用、「继续游戏」转可用 → 暂停会话语义成立 |
| 结束面板 | `run7-ending-panel.png` | 编辑器 -game + `DY_MENU_PANEL=end` 直出：左列「重新复演」为可用态并压住原画旧列，其余五个牌匾为禁用态；结束卡只有标题与一行正文，不再压到右下引导卡 |
| 结束面板（打包版真实通关） | `run7-ending-panel-packaged.png` | Development D2 包三轮程序化通关的第 1 轮成林结束态（1600×900 截帧）：首牌「重新复演」可用、其余五项禁用，原画旧列被完全盖住 |

启动器预检 `-DryRun`：`Status=PASS-PREFLIGHT-ONLY`、`ArtifactCount=31`、`ArtifactBytes=756892370`、exit 0（两个 SHA 都与当前地图/二进制一致）。
包内运行日志仍未落地（`-abslog` 指向含中文的路径时被吞），运行期证据以四张截图为准；外景起步的行为另有编辑器 -game 日志 `Entry walk: player crossed into the theater at V(X=-1679.07, Y=-210.00, Z=97.93)`。
本轮真机运行是**直接起包内 exe**（`-windowed -ResX=1920 -ResY=1200 -nosplash`，与启动器同一份可执行文件与工作目录）：从本会话嵌套起 `Start-FormalShipping.ps1` 时子 PowerShell 丢了 `PSModulePath`，`Get-FileHash` 找不到，属工具环境问题，不是启动器缺陷——`-DryRun` 与本地直接执行均通过。

## 5. 自动化回归

- 命令：`UnrealEditor-Cmd.exe <uproject> -ExecCmds="Automation RunTests DengYingShanHai;Quit" -TestExit="Automation Test Queue Empty" -unattended -nosplash -nullrhi -nopause -log -abslog=...`
- 日志：`D:\灯影山海\Saved\Logs\AutomationV21f.log`（改动结束态后重跑）
- 结果：**172 个测试全部 Success，Fail=0，`TEST COMPLETE. EXIT CODE: 0`**

另有一条"打包版三幕真实通关"验证（Development 包 `Builds/FormalMain-Development-20261020-D1`，测试 `DengYingShanHai.FormalMain.PackagedThreeActsAndReplay`）：三轮完整流程 + 三轮同图重演全部 PASS，日志 `Saved/Logs/FormalFlowD1.log`，截帧在 `Saved/Audit-2026-10-20-V21/FormalFlow/`。

Run7 之后又重打了一次 Development 包并复跑同一条测试，用来验**结束态在打包版真实通关里**的样子：

- 打包：`powershell -File D:\灯影山海\Saved\Audit-2026-10-20-V21\Package-Development.ps1 -Attempt D2` → `BUILD SUCCESSFUL` / `ExitCode=0 (Success)` / `BuildCookRun time: 116.25 s`；产物 `Builds/FormalMain-Development-20261020-D2`（49 文件 / 1,115,149,287 字节），身份文件 `DEVELOPMENT-BUILD.json`。
- 复跑：`C:\dy_build\run_flow_d2.ps1`（1600×900、`-unattended`、`-DYFormalCaptureDir=Saved/Audit-2026-10-20-V21/FormalFlow-D2`）。
- 结果：`DY_FORMAL_PACKAGED cycle=3 PASS ThreeCompleteFlowsAndThreeSameMapReplays; programmatic interfaces only`、`Test Completed. Result={Success}`、`TEST COMPLETE. EXIT CODE: 0`，进程退出 0；日志 `Saved/Logs/FormalFlowD2.log`。
- 截帧：`FormalFlow-D2/00_Title.png`、`99_ReplayTitle.png`、`Cycle0{1,2,3}_{P02,ForestComplete}.png`；其中 `Cycle01_ForestComplete.png` 已复制为 `Saved/Audit-2026-10-20-V21/run7-ending-panel-packaged.png`，即上表最后一行。
- 包内资产缺口的复查：这份 D2 日志里没有 `Failed to find` / `Failed to load` 资产报错（只有 `aqProf.dll`、`VtuneApi.dll` 这类性能工具可选库的正常失败），说明字体静默回退与 `SFX_DevWind` 的 cook 修复在打包版里都成立。

- 自动化：Run47 / Run48 / Run51 / Run52 / Run53 源码上均 172/172 Success、0 Fail、`TEST COMPLETE. EXIT CODE: 0`（`C:\dy_build\AutomationV23.log`）。

## 6. 包内资产抽查（`UnrealPak -List`，共 2210 个 IoStore 条目，Run6 抽查结论沿用——Run7 只改 C++，资产与地图未变）

| 资产 | 结论 |
|---|---|
| `Content/DengYingShanHai/Maps/L_DY_Main.umap` | 在包内 |
| `UI/Menu/T_Plq{Normal,Hover,Pressed,Disabled}.uasset` | 四张牌匾底图齐全 |
| `UI/Menu/T_MenuBackground.uasset` | 在包内（结束态要盖住的旧列就在这张原画里） |
| `UI/Menu/Fonts/FF_MenuSerif.uasset`、`FF_MenuSerifBold.uasset` | 在包内（8.7 MB / 8.8 MB，Oodle） |
| `Dev/Audio/Sounds/SFX_DevWind.uasset` + `.ubulk` | 已补齐（此前打包版外景无声） |
| `Dev/TheatreAudio/Sounds/SFX_Dev{FootstepA,FootstepB,StaffContact,ForestLeaves,Resolve,HoldingPulse}.uasset` | 在包内 |
| `Dev/WorldV2/Materials/M_DY_SkyDome.uasset` | 在包内（Unlit） |

## 7. 包演化

| 包 | 地图 SHA256 | 产物数 | 字节数 | 说明 |
|---|---|---:|---:|---|
| `20261019-Run3` | `8E998DEC…9258` | 31 | 733,971,876 | V2.1 之前的基线 |
| `20261020-Run1` | `6ECB12E3…016C` | 31 | 756,729,073 | 外壳第一版（无天穹、无路灯笼） |
| `20261020-Run2` | `510286F3…3DC9` | 31 | 756,736,329 | 含后门/路灯笼/材质修正，但二进制仍带 Tick 覆盖 |
| `20261020-Run3` | `510286F3…3DC9` | 31 | 756,736,329 | 与源码一致（Tick 已删），天空纯黑、树为圆柱+球 |
| `20261020-Run4` | `98043673…9B31` | 31 | 756,742,959 | 外景 pass5：树形变化、月亮、中景山脊、Unlit 天穹 |
| ~~`20261020-Run5`~~ | — | — | — | **作废**：打包期间改了源码，包内不含 HUD 分层；见 `Package-Run5/VOIDED.md` |
| `20261020-Run6` | `5512ABA3…B800` | 31 | 756,900,562 | 外景起步 + HUD 分层 + 音频 cook + 字体静默回退；`DYTheater_*`=226 |
| **`20261020-Run7`（当前）** | `5512ABA3…B800` | 31 | 756,892,370 | 结束态菜单一致性（旧列遮盖 + 首牌位即重演）；其余同 Run6 |

`Scripts/Start-FormalShipping.ps1` 的 `$dyArchive`/`$dyAudit` 指向 Run7 / `Package-Run7`；Run1–Run6 与 19 日包保留可回滚。脚本必须带 UTF-8 BOM（PS 5.1 否则按 ANSI 读中文路径）。

## 8. 风险与未覆盖项

- Shipping 包内是"冷启动 → 外景 → 进门 → 暂停"四点验证，**没有在 Shipping 里手动打穿三幕**；完整三幕 + 结束面板已由 Development D2 包的打包版程序化通关复验（`run7-ending-panel-packaged.png`），仍未合并成一次 Shipping 人工通关。
- 仓库里那段左上角引导句「操纵灯，用 A / D 将头部影子送入浅色缺口…」由 Blueprint 在运行时喂给 WBP，C++ 拿不到句柄，所以**外景阶段它仍然可见**——与"外景只留一句"的预期有偏差，属已知外观问题。
- 外景仍是 blockout 级美术（树=柱+球、山=锥、地面单色），靠四盏门径灯提供可读性；固定手动曝光让室外呈夜景。
- 设置页写 `GameUserSettings` 的持久化未在 Shipping 下验证。
- 打包版 `-abslog` 走中文路径会失败，运行期日志目前拿不到，只能靠截图。
- 性能复测：Development D2 包 1080p/18,000 帧 CSV 显示稳定态 143.36 FPS、GPU 6.202 ms、P99 8.103 ms（`Docs/FORMAL_PERFORMANCE_20261020.md`）；Shipping 侧外部采样与真人通关性能仍未覆盖。

## 9. V2.3 四幕版本（Run19 → Run27）

V2.3 总案要求「四幕独立可玩、共用一座戏台、四幕连演有真结局」。C++ 与菜单改动、外景美术改动都在当天下午连续进了 9 个包，Run27 是这一轮结束时的正式包；最新正式包见 §9.4（Run51）。

| 包 | NativeExeSHA256 | SourceMapSHA256 | 产物 | 主要内容 |
|---|---|---|---|---|
| Run19 | `8A1FE8E8…3717B` | `94676387…C8755` | 31 / 757,064,790 | 四幕 C++（章节数据结构、Director 章节 API、章节选择 4 行、每幕调色板、兜底推进）首进包 |
| Run20 | `B099D072…6BA23` | `94676387…C8755` | 31 / 757,070,934 | `DY_CHAPTER` 直入第 N 幕钩子；进浮层时焦点落到第一行；底部提示框改造 |
| Run21 | `D48A9A39…E87F` | `853596AF…B8980` | 31 / 757,071,446 | 月亮移到 `(781,739,2825)` scale 4.5 并入画；每幕调色板加强；`DY_CHAPTER` 真机验证 |
| Run22 | `AD8CD7F4…884C2` | `853596AF…B8980` | 31 / 757,080,662 | BP HUD 文案「三幕」的运行时规范化（后证明会被 BP 覆盖）+ 非遗说明页扩写 |
| Run23 | `AD8CD7F4…884C2` | `853596AF…B8980` | 31 / 757,080,662 | 三份演示资产里的「依次复演三幕」字节级替换为「四幕」（真机确认显示「依次复演四幕 · 操作沿用 E / A / D」） |
| Run24 | `AAB9BE10…ED687` | `853596AF…B8980` | 31 / 757,081,174 | `DY_CAMPAIGN_AUTOPLAY` 自检钩子 + 探针 `CampaignProbe.log`；修正第 2/3/4 章影偶姿态带冲突（StrideReach 要求偶位 ≥ 0.75）；末幕兜底仍缺 |
| Run25 | `A1C6E0E5…44D1B` | `853596AF…B8980` | 31 / 757,082,710 | 末幕兜底修复（最后一章 6 s 后 `SetSequencePhase(Complete)`，四幕闭环）；**第一个跑通四幕连演→真结局面板的包** |
| Run26 | `7019359B…F974D` | `853596AF…B8980` | 31 / 757,090,902 | End 面板放开「退出游戏」 |
| **Run27** | **`055C0EF19440DBD5BD04497E960FBCF7C93596F6937346C8FFDE7286900BC85A`** | **`853596AFC4321D517852D21163BB970FBC7C640E505FAE3069318A39B59B8980`** | **31 / 757,091,414** | End 面板加「影偶图鉴」四行（夸父/精卫/刑天/烛龙），与 Run26 的退出可用性合并交付 |

- 归档：`D:\灯影山海\Builds\FormalMain-Shipping-20261020-Run27\Windows`；审计：`Saved\Audit-2026-10-20-V21\Package-Run27`；UAT `ExitCode=0` / `BUILD SUCCESSFUL`。
- 源地图：`L_DY_Main.umap` 827,084 字节，`SourceMapSHA256=853596AF…B8980`（与 Run21 之后一致；Run19/Run20 的包对应旧地图）。
- Run22 与 Run23 的 exe 与地图哈希相同，字节数也相同：差异只在 cooked 资产内容（三份 BP/WBP 里的提示句），因此 `SourceMapSHA256` 不能区分这两个包，需要时看 `ARTIFACTS.json` 的逐文件 SHA256。
- 启动器 `Scripts/Start-FormalShipping.ps1` 已指向 Run27，`-DryRun` 返回 `PASS-PREFLIGHT-ONLY`（31 产物 / 757,091,414 字节）。

### 9.1 本版新增的真机证据（1920×1200，打包 Shipping）

`Run23-menu.png`、`Run19-chapters.png`（四幕清单）、`Run23-outside-1s.png`（完整圆月 + 壁灯）、`Run23-ch1-outside-1s.png`（第 2 幕天青）、`Run23-hall.png`（第一幕第一步）、`Run23-ch1-hall.png`（第二幕「衔石入海」+「依次复演四幕」）、`Run21-ch3-hall.png`（第四幕「夜伏」）、`Run23-pause.png`。

### 9.3 四幕连演（Run25/Run27，`DY_CAMPAIGN_AUTOPLAY=1`）

`C:\dy_build\verify_campaign.ps1 -Attempt <Run> -Seconds 90 -Interval 5` 以打包 Shipping 启动、进游戏后 W 走 18 s 进厅，每 5 s 连拍一次并读取 `%LOCALAPPDATA%\DengYingShanHai\Saved\CampaignProbe.log`。

- Run25 探针 12 步全记录：第 1 幕 引日启幕→逐光成形→杖落成林；第 2 幕 衔石入海→石影连途→填海成洲；第 3 幕 断首犹立→举盾成影→舞干戚；第 4 幕 夜伏→睁眼为昼→晦明同光；末尾 `phase=4 chapter=4/4 act=3`（Complete）。
- `Run25-campaign-087s.png`：主菜单进入 End 态，首牌「重新复演」、浮层标题「复演已成」、正文「四幕演尽…」。即四幕连演→真结局面板闭环。
- 自检钩子只写灯位/偶位目标，不跳过 Evaluator 判定、保持计时、转场提交与终幕；`CampaignProbe.log` 只在 `DY_CAMPAIGN_AUTOPLAY=1` 时写。
- 172 项自动化在四幕改动后仍全绿（`C:\dy_build\AutomationV23.log`，`TEST COMPLETE. EXIT CODE: 0`）。

### 9.2 复打包时必须复现的三件事

1. **地图保存要双写**：`UnrealEditor` 的 `save_current_level()` 返回 True 也可能不落盘，必须再调 `unreal.EditorAssetLibrary.save_asset(MAP, False)` 并 `load_map` 复核（月亮那次就是只调前者，白跑两轮）。
2. **资产字节补丁**：`BP_DYReadabilityPresentation` / `BP_DYThreeActPresentation` / `WBP_DYThreeActCue` 里的「依次复演三幕」是等长 UTF-16 替换；重新导入资产会还原，需要重打（备份在 `C:\dy_build\asset_backup\`）。
3. **DLL 回拷**：`cmd /c C:\dy_build\rebuild.cmd` 成功后必须把 `C:\dy_build\Binaries\Win64\UnrealEditor-DengYingShanHai.dll` 与 `UnrealEditor.modules` 复制回 `D:\灯影山海\Binaries\Win64\`，否则「改了没效果」。
4. **PS1 保留 BOM**：编辑 `Scripts/*.ps1`、`C:\dy_build\*.ps1` 后要确认首三字节是 `EF BB BF`，否则中文路径会乱码并触发误报。

### 9.4 Run28 → Run84：入口提示、外景美术、四幕配色、影偶图鉴、自制背景乐/锣鼓、帧率探针、设置回滚/持久化、复演闭环、门前修形、影偶陈列取舍、禁用牌匾可读性、叠加层焦点高亮、外景占位材质清理、入口灯型统一、标题面板可续演、章节已演标记与十六进制读回、焦点环与菜单焦点可见、第一幕容差放宽、HUD 站位提示、章内携带上一步值、图鉴补锣鼓器乐、幕间题签（当前包 Run84）

Run27 之后又连续重打包 57 次（Run28 → Run84；Run29、Run40 因打包途中改源码作废，Run80 被 Run81 取代，Run83 被 Run84 取代），都是为了把「入口提示看不见」「外景太像灰盒」「四幕看起来一样」「图鉴只能用鼠标点」「换幕没有交代」五件事修掉。当前正式包为 **Run84**（Run84 = Run83 + 幕间题签改为「玩家到场后才出现」，从菜单直选一幕时不会在走廊里把题签耗掉，见 §9.26；Run83 = Run82 + 四幕每幕开场在标题行显示 2.8 s 的「第X幕 · 幕名」大字，再回落到步骤题；Run82 = Run81 + 影偶图鉴补「锣鼓与器乐」段落、并把图鉴正文抽成可单测的 `UDYDevEntryWidget::MakeCodexEntry()`，见 §9.25；Run81 = Run80 + 给携带逻辑补 `DY_CARRY_PROBE` 文件探针；Run80 = Run79 + 章内携带上一步目标值、并把第一幕第三步偶目标 0.85 → 0.92（pass60 重存地图），见 §9.24；Run79 = Run78 + HUD 站位提示，见 §9.23；Run78 = Run77 + 把第一幕三步的 Enter/Exit 容差从 0.045–0.05 / 0.085–0.09 放宽到 0.075 / 0.115（只改三份数据资产，exe 未变），见 §9.22；Run77 = Run76 + 修结束面板主牌标签被焦点文本覆盖：End 面板本应写「重新复演」，焦点标记把标签改成了「开始游戏」，现按面板取 `GetPrimaryLabel(CurrentPanel)`，见 §9.20；Run76 = Run75 + 叠加层方向键移动后残留的 1 px 蓝色 Slate 焦点框被清掉、菜单六块牌补上键盘焦点可见（琥珀色牌面 + 标签前「◆」），见 §9.20；Run75 = Run74 + 修「（已演）」标记在四幕全演完后重启消失：`PlayedMask` 用 `%02x` 写却用 `FCString::Atoi` 按十进制读回，`0f` 被读成 0，现改为 `FCString::Strtoi(..., 16)`，见 §9.19；Run74 = Run73 + 「演出篇章」把演完过的幕标成「（已演）」，进度文件从一行扩成 `ProgressChapter` + `PlayedMask` 两行，见 §9.18；Run73 = Run72 + 标题面板的「继续游戏」可以续演上次停下的那一幕，见 §9.17；Run72 = Run71 + 入口灯径上并存的 8 组矮灯（32 个演员）被删掉，只留 12 根高灯柱这一套灯型，见 §9.16；Run70 = Run69 + 演出版面/设置/图鉴条目的键盘焦点高亮，见 §9.14；Run69 = Run68 + 修「继续游戏」禁用牌匾无字，见 §9.13；Run68 = Run67 + 移除门厅四幕影偶陈列的 108 个演员，四幕影偶只走影偶图鉴 UI，理由见 §9.12；Run66 把到达戏台时的两条牌匾合成一条，Run64/Run65 是门厅四偶的两次失败陈列，见 §9.12；Run57 = Run55 + 设置页分辨率行改用 Win32 客户区读数，Run56 为中间包；Run55 回应用户 m11176 的五项：拆掉门前的浮空石板「梯子」、精简门口陈设、补四幕影偶陈列、外景再加石灯笼/远山裙/枯树、设置页分辨率行附注当前窗口尺寸；Run54 是同一批地图改动的首包，Run53 加地图侧外景 pass33/34：树冠簇化与远山裙；Run52 加「重新复演」自动重开四幕，Run51 加设置持久化与探针模式，Run50 加设置回滚探针，Run48 加自制锣鼓提示音见 §9.8，Run47 加帧率探针见 §9.7，Run44 加自制背景乐，Run45/Run46 修外景：巨型灌木缩放与灯柱造型）。

| 包 | NativeExeSHA256 | SourceMapSHA256 | 31 产物字节 | 进包的主改动 |
|---|---|---|---|---|
| Run28 | `B0DDBD19…CD404DA` | `1524DCF5…2C93393` | 757,104,214 | 外景 pass21（崖柱/山脊/檐灯/雾）+ 入口提示改 Canvas；包内仍是旧 DLL，提示未显示 |
| Run30 | `0256BD7F…AF27D` | `A5FEF4AD…4F08034` | 757,098,582 | Canvas DrawHUD 进包：入口提示**可见**；同包修掉「第三幕」被运行时替换成「第四幕」的 bug |
| Run31 | `11938D5F…9AED5BA` | `AA8ABA71…53A4EE0C` | 757,103,202 | 外景 pass22（泛光转向 +X、格窗竖缝）+ DrawHUD 金色横线 |
| Run32 | `11938D5F…9AED5BA` | `53063ED7…5ADF2EE7F` | 757,105,262 | 外景 pass23/24（对称格窗 18 个、右侧远山、瓦檐、石径、巨石、门侧大灯笼） |
| Run33 | `11938D5F…9AED5BA` | `CDE35C3F…9127A8` | 757,113,466 | pass25 试加墙面洗光，真机发冷发白，废弃 |
| Run34 | `11938D5F…9AED5BA` | `FA4011CB…307EA8` | 757,121,670 | pass26 用几何发光条替代洗光（材质非自发光，实际效果有限） |
| Run35 | `2B7C3067…C1CA50` | `FA4011CB…307EA8` | 757,106,310 | 四幕主灯配色（夸父暖金 / 精卫青 / 刑天赤 / 烛龙月蓝） |
| Run36 | `2B7C3067…C1CA50` | `E3819D21…510E3769E` | 757,112,478 | pass27 把 42,000 cd 泛光降到 7,200 cd（去掉过曝白斑） |
| Run37 | `2B7C3067…C1CA50` | `65C6751D…8A5C293E` | 757,085,794 | **去重**：地图里累计了 5 套外景 actor（原因见下），清空后只留一套 |
| Run38 | `2B7C3067…C1CA50` | `293B9D72…556E0C4` | 757,085,794 | pass28/29/30：单套外景 + 发光条/檐灯位置前移 + 门侧灯降亮 |
| Run39 | `3FA4E9AC…E360B5E` | `293B9D72…556E0C4` | 757,102,690 | 影偶图鉴页首次进包；暴露「第三幕→第四幕」残留替换与图鉴键位达不到 |
| Run41 | `74FA08EA…1A04B9B` | `293B9D72…556E0C4` | 757,111,906 | 只替换演出类控件的「三幕→四幕」+ 显式 Up/Down 导航 |
| Run42 | `0574B150…23CCAE1D` | `293B9D72…556E0C4` | 757,111,906 | 结束面板把焦点钉回首牌；键位仍被窗口激活重置 |
| Run43 | `8CF9817EA98A0FF26E7AB54901900D3E19460B5DF552425F3CD1A15CCD3AD184` | `293B9D72…556E0C4` | 757,120,098 | 导航游标自持（`NavFocusIndex`）+ 图鉴真机验证通过 |
| Run44 | `CC899777…5E10A6E6` | `293B9D72…556E0C4` | 757,668,586 | 自制五声音阶背景乐进包（`StartTheatreAmbience` + `BGM_DY_MountainSea`） |
| Run45 | `CC899777…5E10A6E6` | `B944DF51…465ABA8` | 757,670,634 | 外景 pass31：把 pass7 误放大 100 倍的 14 颗灌木球缩回真实尺寸，补 20 个坡脚灌木/石块 |
| Run46 | `CC899777…5E10A6E6` | `6C8C3478…BFFC53E` | 757,670,634 | 外景 pass32：灯柱由 60 cm 石墩改成 34 cm 瘦柱 + 球灯 + 木灯帽/宝顶，24 个柱头重建 |
| Run47 | `B20EC39E…C34E8062` | `6C8C3478…BFFC53E` | 757,679,850 | 帧率探针 `DY_PERF_PROBE=1`（`Saved/PerfProbe.log`，每秒一行）；包体较 Run46 +9,216 字节 |
| Run48 | `59179CE6…4637BEA` | `6C8C3478…BFFC53E` | 757,742,036 | 自研锣/鼓/结算音（`SFX_DY_Gong/Drum/Resolve`）按章、幕、剧终状态各响一次；`DY_SFX_PROBE=1` 写 `Saved/SfxProbe.log` |
| Run49 | `4B20A341…916DE` | `6C8C3478…BFFC53E` | 757,743,572 | 设置回滚探针（开发包 `DY_MENU_AUTOTEST=4`）；Shipping 里该自测被 `#if !UE_BUILD_SHIPPING` 剥掉，故另加 `DY_SETTINGS_PROBE=1` 并重打 Run50 |
| Run50 | `DA0432FA1F586CAFF3CD684EF0E66CA4E82212CF870A7C018DA80B669D227DCE` | `6C8C3478…BFFC53E` | 757,752,788 | 设置页 15 s 未确认自动回滚在 Shipping 真机可证（`SettingsProbe.log` + 两张截图）；其余同 Run48 |
| Run51 | `598DBACAEB01C4FB8D530770B50675F35EC8BBC9B51B7ED516F26C3A08ACEFB0` | `6C8C3478…BFFC53E` | 757,738,452 | 主音量写入 `GameUserSettings.ini` 的 `[DengYingShanHai] VolumeStep`（`CommitSettings()` 落盘、首次开设置页读回）；`DY_SETTINGS_PROBE=1/2/3` 分别测回滚/读回/提交 |
| Run52 | `41B8708634D52CDC1F2BAA71914780BAF2B636F24F6EB80C394C7045CFEC55AF` | `6C8C3478…BFFC53E` | 757,752,788 | 结束面板按「重新复演」后自动重开第一幕（`DYEntryReplay::bPending` + 重载地图后 0.6 s 轮询启动）；四幕→复演→四幕真机闭环 |
| Run53 | `41B8708634D52CDC1F2BAA71914780BAF2B636F24F6EB80C394C7045CFEC55AF` | `AE761B87…CE4D0D21` | 757,767,148 | 外景 pass33/34：104 个树冠球各补 2 个偏移小冠（208 个）成簇，远山裙 8 座；纯地图资产变更，exe 与 Run52 同哈希 |
| Run54 | `246F30F946098622D3A0636436D2FB91446D26954C34B0F0695BB7B29C55CFC2` | `60E6F37E…21510D` | 757,776,396 | 外景/门厅 pass35：删掉 92 个冗余 actor（14 块浮空石板、20 立石、18 格心、16 个重复路径灯等），`DYTheater_GateStep` 压平到地面；新增四幕影偶陈列（49 个 actor）+ 8 座石灯笼 + 6 座远山 + 8 组枯树；exe 还不含设置页与调试视角两处 C++ 修补 |
| Run55 | `4BE267E701378791B1EAC3E522C356D14AD3A8D0C1C1E207B5C83493D4A792C1` | `D71485BD…F09486` | 757,776,396 | pass35d/e/f：影偶从背板里抬到板前 6 cm、改按 ink 剪影 + 朱红道具重贴材质；C++ 设置页分辨率行附注「当前」、`DY_DEBUG_VIEW` 解除 Shipping 限制 |
| Run56 | `226C9996074138389D79438CCBD5387923397FBB6BCE13E6BD6FE2A81803BC28` | 同上 | 757,776,396 | 设置页改用视口后备缓冲像素尺寸（结果与 Run55 相同，说明 UE 视口接口本身返回 DPI 缩放值） |
| Run57 | `07F0A248374F8A56361231BB9D3EC383E5673D24E28A516F6F064D0CFBE400B1` | `D71485BD…F09486` | 757,776,908 | 设置页改读 Win32 窗口客户区（`GetClientRect`）；同一台机器上仍显示 1423 × 889，即窗口的逻辑尺寸，实际上屏 2134 × 1333（DPI 虚拟化），见 §9.11 已知限制 |
| Run58–Run63 | `AB1D12D9…` → `DBA4AC4C…` | `D71485BD…F09486`（六包同图） | 757,847,052 → 757,864,972 | 同一张地图上的 C++ 中间包，不作交付：入口牌匾/提示行与门厅取景的连续微调，最终并入 Run64 的 exe |
| Run64 | `DBA4AC4C835450D7AC42EF2E51F65064DCBA3557BA4F024DDC6868128C1A03C8` | `E4AF1F47…40AA7B` | 757,860,888 | pass36：门厅左右墙「四幕影偶」陈列（39 部件，贴墙 y=±1252）；真机走查发现贴墙 90° 的四具在直行画面外 |
| Run65 | 同上 | `D3FEDF1C…966DCA54` | 757,860,888 | pass37：改成门厅两侧独立立偶（48 部件 + 4 盏灯），撤离墙板 |
| Run66 | `F7B5E39270DCCC09A87040BC2AFD2F5E8411F04AB72BC945572145C8580A686D` | `C8475F00…F13D50` | 757,842,456 | C++：到达戏台时「入戏台」与到达提示两条牌匾合成一条；地图：pass38 入口走廊立偶（48 演员）+ 1400 cd 射灯 → 真机过曝成白矩形 |
| Run67 | 同上 | `254E7DF2…007DCF` | 757,842,456 | pass39：四偶射灯降到 230 cd / 2.1 m；真机四偶仍完全不可见（走廊净宽 610，见 §9.12） |
| Run68 | `F7B5E39270DCCC09A87040BC2AFD2F5E8411F04AB72BC945572145C8580A686D` | `0C833856…6E02053` | 757,838,316 | pass43：删掉 108 个影偶/标定演员（`DYExt35_Act*`、`DYExt37/38/40/41_Act*`、`DYCAL_*`），四幕影偶只保留影偶图鉴 UI 路径 |
| Run69 | `D1BB390420525F4F7344B32DF39A3A572AB6247D75E810CFA3584EC103AD2091` | 同上 | 757,847,020 | 禁用牌匾「继续游戏」不再是空白灰牌：`RefreshView()` 按可用性重设标签颜色（禁用用 `.80,.75,.66`，见 §9.13）；纯 C++、地图未变 |
| Run70 | `D835A7A0974EF181A5CC52EB60B8729833732F60B5660BE6F20F59C2C9FB84F5` | 同上 | 757,848,556 | 叠加层条目的键盘焦点由 `ApplyOverlayRowFocus()` 画成朱红底 + 暖金字，`NativeTick` 用 `FSlateApplication::Get().GetKeyboardFocusedWidget()` 镜像真实焦点（FButtonStyle 在 5.8 没有 focused 画刷，见 §9.14）；新增 `Slate` 模块依赖；纯 C++、地图未变 |
| Run71 | `D835A7A0974EF181A5CC52EB60B8729833732F60B5660BE6F20F59C2C9FB84F5` | `A84ABF05F32D92875C471D7133D74A81C3C902392E12C65713CEADA7A5F65E16` | 757,854,716 | pass44–pass50：外景美术补做（12 处 `WorldGridMaterial`/`DefaultMaterial` 占位材质换成黄铜/灯纸、328 处树冠球体做非等比抖动、近景 12 座山锥外推并缩尺）；两次失败试验（叠加肩锥、远景锯齿山脉 + 石板路）已全部删除，见 §9.15 |
| Run72 | `D835A7A0974EF181A5CC52EB60B8729833732F60B5660BE6F20F59C2C9FB84F5` | `774694ACFB6185904D230D79B8347CF184912F2F572E8A74C60022F42F571CCC` | 757,852,668 | pass52：入口灯径上两套灯型并排（12 根高灯柱 + 8 组「方块灯身 + 米色锥顶」矮灯），删掉矮灯的 32 个演员只留高灯柱，灯的光源全部保留故亮度不变，见 §9.16；Run72 时曾是当前包 |
| Run73 | `09FED426EEDE2BA3DBBB45FE23B7D22F26FC604EE61F7A00441499B4B7DA2368` | `774694ACFB6185904D230D79B8347CF184912F2F572E8A74C60022F42F571CCC`（同 Run72） | 757,862,012 | 标题面板的「继续游戏」原本恒灰，现在可续演上次停下的那一幕：新增章节级进度 `Saved/DYProgress.txt`，`UpdateContinueProgress()` 在 `HandleActDisplay` 里随快照写入（Playing → 章号+1，Complete → 0），见 §9.17；Run73 时曾是当前包 |
| Run74 | `5EA33D6FD81EF8A1F7C79691CA9583A36332837A3ABE34DB2F4498D9E6C21FBE` | `774694ACFB6185904D230D79B8347CF184912F2F572E8A74C60022F42F571CCC`（同 Run72/Run73） | 757,880,556 | 「演出篇章」把演完过的幕行尾标「（已演）」：`Saved/DYProgress.txt` 新增 `PlayedMask`（每幕一位），`MarkChapterPlayed()` 在下一幕开始时记上一幕、剧终时记最后一幕，改一幕标题不误标，见 §9.18；Run74 时曾是当前包（见 §9.19） |
| **Run75** | **`9EA71D9C37DE73D1484126F3BEA0931D0EC8BF41E6CD49BD63F136B7025C7F09`** | `774694ACFB6185904D230D79B8347CF184912F2F572E8A74C60022F42F571CCC`（同 Run72–Run74） | **757,880,556**（与 Run74 同字节：只换了一处调用，代码段被对齐吸收） | `PlayedMask` 以 `%02x` 写入却用 `FCString::Atoi` 按十进制读回，`0f` 读成 0——四幕全演完后重启「（已演）」全部消失；改用 `ReadHex()` = `FCString::Strtoi(..., 16)`，见 §9.19 |
| Run76 | `1FC864722B54EE8200C37308F7D4D538D21A93F357AFA668EA8D8BD981280518` | `774694ACFB6185904D230D79B8347CF184912F2F572E8A74C60022F42F571CCC`（同 Run72–Run75） | 757,882,092 | 叠加层 1 px 蓝焦点框消失 + 菜单牌「◆」焦点标记首版；同轮把结束面板主牌改坏（见 §9.20），地图未变 |
| Run77 | `5C4700B9C452BF03107A41178933BDB7432A593810F7BB79F23AFE91A3747628` | 同上（同 Run72–Run76） | 757,890,796 | 结束面板 0 号牌改取 `GetPrimaryLabel(CurrentPanel)`，修掉 Run76 的「◆ 开始游戏」回归；纯 C++、地图未变，见 §9.20 |
| Run78 | `5C4700B9C452BF03107A41178933BDB7432A593810F7BB79F23AFE91A3747628`（与 Run77 同 exe） | `BB0AE8F5EB29BB05FCE6C2680DA594FEC3A68F1ADFCBC1642C510FF38230C11F` | 757,890,796（与 Run77 同字节：只改三份数据资产里的浮点容差，被 pak 对齐吸收） | 第一幕三步 Enter 容差 0.045–0.05 → 0.075、Exit 0.085–0.09 → 0.115，见 §9.22 |
| Run79 | `EDD2FC47F2197C782F3EF6F94703E668DF4554D974A66ED132C62FAF777EEBF0`（有 C++ 改动） | `BB0AE8F5EB29BB05FCE6C2680DA594FEC3A68F1ADFCBC1642C510FF38230C11F`（同 Run78） | 757,953,260（+62,464 B） | HUD 站位提示：够不到灯（或灯与偶）时底部牌匾给一句走位指导，每幕最多一次，见 §9.23 |
| Run80 | `7F9D0719509F920F16ACFDE8C721DC7E8AABDCCEC24B9AE2E0CF6875D908651F`（有 C++ 改动） | `2DA372A32870D82B9BAC2F718CA81BBB9C5EA2DA1E67A4A631EF36DD7BB33165`（pass60 重存地图） | 757,945,068（−8,192 B：去掉了站位提示那一轮的构建中间态，见说明） | 章内携带上一步目标值（②）+ 第一幕第三步偶目标 0.85 → 0.92；**没有文件探针**，当天即被 Run81 取代，未做回归 |
| Run81 | `BC5D5FF36B2819B6D7AA46E4CB043463FA19494AD52A70B86249D24E5ED69333`（有 C++ 改动） | `2DA372A32870D82B9BAC2F718CA81BBB9C5EA2DA1E67A4A631EF36DD7BB33165`（同 Run80） | 757,955,308（比 Run80 +10,240 B） | Run80 + `DY_CARRY_PROBE` 文件探针：换步时把上一步的 Target 写进 `Saved/CarryProbe.log`，否则自动演出无法证明携带生效，见 §9.24 |
| Run82 | `001F16A7A7FD793B251C3831E27E46EE58097E7FB457EFC40A6F8C4ABB197908`（有 C++ 改动） | `2DA372A32870D82B9BAC2F718CA81BBB9C5EA2DA1E67A4A631EF36DD7BB33165`（同 Run80/Run81） | 757,978,860（比 Run81 +23,552 B） | Run81 + 影偶图鉴补「锣鼓与器乐」段（非遗五项齐）、图鉴正文抽成纯函数 `UDYDevEntryWidget::MakeCodexEntry()` 并加 1 项自动化，见 §9.25 |
| Run83 | `7204F52EAA81B4B09253011F8B0737759BA8999B9106ACFFAEB60EEBF3761AD3`（有 C++ 改动） | `2DA372A32870D82B9BAC2F718CA81BBB9C5EA2DA1E67A4A631EF36DD7BB33165`（同 Run80–Run82） | 758,014,188（比 Run82 +35,328 B） | 幕间题签首版：每幕开场标题行放大显示 2.8 s「第X幕 · 幕名」；真机发现第一幕题签在自动演出开场 2 s 就被计时消耗（当时入口引导还没发出），当天被 Run84 取代 |
| **Run84** | **`73E969A2581B7A726DEEA9FB16E59B1961B5BB401AAE2787788B0D8814FD4CB9`**（有 C++ 改动） | `2DA372A32870D82B9BAC2F718CA81BBB9C5EA2DA1E67A4A631EF36DD7BB33165`（同 Run80–Run83） | **758,005,996**（比 Run82 +27,136 B；比 Run83 −8,192 B，去掉了首版构建的中间态） | Run83 + 题签到达门控 `IsStageReached()`（`Pawn->GetActorLocation().X > DYEntryWalk::TheaterThresholdX`）：题签只在玩家进戏台后出现，走廊与菜单直选一幕都不会把它耗掉；新增 `M1.UI.ChapterCard` 自动化，见 §9.26；**当前交付包** |

- 历史归档（Run43）：`Builds\FormalMain-Shipping-20261020-Run43\Windows`（**2026-10-20 20:35 磁盘清理时删除**，只保留身份哈希与审计）；审计：`Saved\Audit-2026-10-20-V21\Package-Run43`；UAT `ExitCode=0`。
- **当前交付包 Run84**：`NativeExeSHA256=73E969A2581B7A726DEEA9FB16E59B1961B5BB401AAE2787788B0D8814FD4CB9`（本轮有 C++ 改动：幕间题签 + 到达门控）、`SourceMapSHA256=2DA372A32870D82B9BAC2F718CA81BBB9C5EA2DA1E67A4A631EF36DD7BB33165`（与 Run80–Run83 同图，只改 C++）、31 文件 / **758,005,996** 字节（比 Run82 +27,136 B）；归档 `Builds/FormalMain-Shipping-20261020-Run84/Windows`；审计 `Saved/Audit-2026-10-20-V21/Package-Run84`；`PASS-BUILD-COOK-STAGE-ARCHIVE`、UAT `ExitCode=0`。
- 前一包 Run83：`7204F52E…3761AD3` / `2DA372A3…7BB33165` / 758,014,188（幕间题签首版，题签会被走廊里的自动演出计时消耗，见 §9.26）；再前一包 Run82：`001F16A7…4B197908` / `2DA372A3…7BB33165` / 757,978,860（图鉴补锣鼓段 + `MakeCodexEntry`，见 §9.25）；再前一包 Run81：`BC5D5FF3…24E5ED69333` / `2DA372A3…7BB33165` / 757,955,308（章内携带上一步目标值 + `DY_CARRY_PROBE` 探针，见 §9.24）；再前一包 Run80：`7F9D0719…D908651F` / `2DA372A3…7BB33165` / 757,945,068（只装 carry、没有探针，被 Run81 取代，未做回归）；再前一包 Run79：`EDD2FC47…777EEBF0` / `BB0AE8F5…30C11F` / 757,953,260（HUD 站位提示，见 §9.23）；再前一包 Run78：`5C4700B9…A3747628`（与 Run77 同 exe）/ `BB0AE8F5…30C11F` / 757,890,796（第一幕容差放宽，见 §9.22）；再前一包 Run77：`5C4700B9…A3747628` / `774694AC…F571CCC` / 757,890,796（结束面板主牌文案回归修复，见 §9.20）；再前一包 Run76：`1FC86472…81280518` / 同 map / 757,882,092（焦点环与「◆」焦点标记首版，结束面板主牌标签被覆盖的缺陷在 Run77 修掉）；审计 `Package-Run78` / `Package-Run77` / `Package-Run76`。
- 再前一包 Run75：`9EA71D9C…05C7F09` / 同 map / 757,880,556（「（已演）」十六进制读回修复，见 §9.19）；再前一包 Run74：`5EA33D6F…6C21FBE` / 同 map / 757,880,556（「（已演）」首版）；审计 `Package-Run74`。
- 再前一包 Run73：`09FED426…7DA2368` / 同 map / 757,862,012（标题面板「继续游戏」可续演，见 §9.17）；再前一包 Run72：757,852,668（入口灯径删矮灯，见 §9.16）；再前一包 Run71：757,854,716（外景美术，见 §9.15）；再前一包 Run70：757,848,556（叠加层焦点，见 §9.14）。
- 再前一包 Run71：`D835A7A0…FB84F5` / `A84ABF05…A5F65E16` / 757,854,716（pass44–pass50 外景美术）；再前一包 Run70：`D835A7A0…FB84F5` / `0C833856…6E02053` / 757,848,556（只改叠加层焦点，地图不变）；再前一包 Run69：`D1BB3904…AD2091` / 同 map / 757,847,020（只改禁用牌匾标签色）。
- 再前一包 Run68：`F7B5E392…A686D` / 同 map / 757,838,316；再前一包 Run67：同 exe / `254E7DF2…007DCF` / 757,842,456；再前一包 Run65：`DBA4AC4C…1A03C8` / `D3FEDF1C…966DCA54` / 757,860,888。Run66–Run68 的 exe 完全相同（只有到达牌匾去重那一次 C++ 改动），字节差全部来自地图：pass38 加 48 个演员 → pass39 只改灯光参数 → pass43 删 108 个演员（757,842,456 → 757,838,316）。
- 真机证据：`Run43-outside-1s.png`（入口提示条 + 金线、暖光门脸、18 格窗、月与山影）、`Run43-chapters.png`（第一/二/**三**/四幕正确）、`Run43-campaign-087s.png`（End 面板含影偶图鉴四行与「退出游戏」）、`Run43-codex.png`（**影偶图鉴 · 夸父逐日**：造型/操演/制作七步/四行条目）、`Run43-codex-back.png`（Esc 返回菜单）。
- 探针：Run43 四幕连演 12 步全记录，末行 `phase=4 chapter=4/4 act=3 title=晦明同光`。
- 172 项自动化在 Run48 / Run51 / Run52 / Run53 资产状态下均全绿（`C:\dy_build\AutomationV23.log`：172 个 `Result={Success}`、0 个 `Fail`、`TEST COMPLETE. EXIT CODE: 0`）。
- **174 项自动化在 Run79 上全绿**（2026-10-21 12:11，`C:\dy_build\AutomationV23.log`：174 个 `Result={Success}`、0 个 `Fail`、`TEST COMPLETE. EXIT CODE: 0`）：在原有 173 项之外新增 `DengYingShanHai.M1.Puzzle.ReachHintCopy`，直测 `ADYPuzzleDirector::MakeReachHint` 的四组文案（灯可达且无偶→空、灯不可达且无偶→只提灯、两件都可达→空、需偶且缺一或都缺→「往灯与偶中间站」且不等于灯版）。
- **174 项自动化在 Run80 / Run81 上复跑全绿**（2026-10-21 12:26，`C:\dy_build\AutomationV23.log`：174 个 `Result={Success}`、0 个 `Fail`、`TEST COMPLETE. EXIT CODE: 0`）：本轮改的是携带语义与一条断言所在的 `DYFormalMainAutomationTests`（它要求 cooked Game、只在打包后跑，Shipping 的 `WITH_DEV_AUTOMATION_TESTS=0` 跑不了，本轮只做编译验证），Dev 三幕夹具的 `bFourActCampaign=false`，`0.15` 基线的既有断言全部保持。
- **176 项自动化在 Run83 / Run84 上全绿**（2026-10-21 13:18 / 13:33，`C:\dy_build\AutomationV23.log`：176 个 `Result={Success}`、0 个 `Fail`、`TEST COMPLETE. EXIT CODE: 0`）：在 175 项之外新增 `DengYingShanHai.M1.UI.ChapterCard`，直测两个纯函数——`ShouldShowChapterCard()`（首次看到某幕→true、同幕重复→false、下一幕→true、单幕 `ChapterCount=1`→false、`bSequenceEnabled=false`/`ChapterIndex=-1`/空幕名各→false）与 `MakeChapterCardText()`（单幕返回空、多幕返回幕名）。
- **175 项自动化在 Run82 上全绿**（2026-10-21 12:51，`C:\dy_build\AutomationV23.log`：175 个 `Result={Success}`、0 个 `Fail`、`TEST COMPLETE. EXIT CODE: 0`）：在 174 项之外新增 `DengYingShanHai.M1.UI.CodexCopy`，对四个索引直测 `UDYDevEntryWidget::MakeCodexEntry()` 的正文——造型/操演/制作七步/锣鼓/图鉴五个词齐全、各自带专属字（杖/翅/盾/蛇），越界索引（9）必须收敛到第三项；`M1.Puzzle.ReachHintCopy` 同轮仍绿。
- **173 项自动化在 Run68 / Run69 / Run70 / Run72 / Run73 / Run74 / Run75 / Run77 / Run78 上复跑全绿**（2026-10-21 03:05 / 03:12 / 03:49 / 04:24 / 08:25 / 08:41 / 10:42 / 11:31 / 11:56，`C:\dy_build\AutomationV23.log`：173 个 `Result={Success}`、0 个 `Fail`、`TEST COMPLETE. EXIT CODE: 0`）；Run66 的到达牌匾去重、Run69 的禁用牌匾配色、Run70 的叠加层焦点、Run72 的入口删灯都只改表现层/地图，未触碰任何断言。
- **Run68 证据**：四幕连演 25 行到 `phase=4 chapter=4/4 act=3 title=晦明同光`、`SfxProbe.log` 9 条（鼓 4 / 结算 4 / 锣 1，t=16.0…76.6）、复演后 `CampaignProbe.log` 再追加 25 行（`REPLAY_NEW_LINES=25`）；影偶陈列撤回的几何依据见 §9.12。
- **Run79 证据（③ 站位提示）**：`verify_reach.ps1 -Attempt Run79`（Shipping，`DY_ENTRY_PROBE=1`，按键从 PlayerStart 走进戏台、在够不到的位置停住）在 `EntryWalkProbe.log` 打出 `ShowHint text=走近灯架，灯要够得到才推得动 back=3 status=3 world=1 size=253x152 at=749,808 font=FF_DYSourceHanSansSC_Font`，截图 `Run79-reach-final.png`（底部牌匾提示 + 「灯：待调整」，上一行仍是幕内操作提示「操纵灯，用 A / D 将头部影子送入浅色缺口；影形渐合后保持。」）。该次真机只走到第一幕第一步（只要灯、不要偶），所以出现的是灯版文案；需偶版的「往灯与偶中间站，两件都够得到再动手」由新增自动化直测，未做第二次真人走位。回归：`verify_sfx.ps1 -Attempt Run79` 25 行到 `phase=4 chapter=4/4 act=3 title=晦明同光`、`SfxProbe.log` 9 条（鼓 15.9/32.1/47.5/63.2，结算 24.1/39.5/55.2/70.6，锣 76.6）；`verify_replay.ps1 -Attempt Run79` `REACHED_PHASE4=True`、`REPLAY_NEW_LINES=25`、`VERIFY-REPLAY-DONE`。
- **Run83 / Run84 证据（幕间题签）**：`verify_card.ps1 -Attempt Run83`（Shipping，`DY_CAMPAIGN_AUTOPLAY=1` + `DY_ENTRY_PROBE=1`，逐秒截图）→ `Saved/EntryWalkProbe.log` 出现 4 条 `ChapterCard text=… chapter=N/4` 与 4 条 `ChapterCardHidden`；截图 `Run83-card-007s.png` 顶部是放大的 **「第四幕 · 烛龙昼夜」**，`Run83-card-008s.png` 已回落到步骤题「睁眼为昼」——题签可见、2.8 s 后自回落。首版缺陷也在同一次取证里暴露：第一条探针是 `chapter=0/4 stage=1 walk=0`，即第一幕题签在自动演出开场约 2 s 就起计时（当时入口引导还没发、玩家还在走廊），到玩家进戏台时早就消失。Run84 因此加到达门控：同脚本 `verify_card2.ps1 -Attempt Run84`（Enter 后 W 走 18 s 进戏台）得到 4 条 `ChapterCard` 与 **3 条** `ChapterCardHidden`——第一幕题签（`walk=0`，玩家还没到场）**没有起计时**，第二/三/四幕（`walk=1`）各自显示满 2.8 s 后 `ChapterCardHidden`；截图为连拍间隔（每帧约 2.4 s，含前台校验与截图开销）所限没抓到那一帧，题签可见性以 Run83 的 `Run83-card-007s.png` 为准，Run84 证据是探针里的 3 次成功倒计时 + 上述自动化。
- **Run81 证据（② 章内携带）**：`verify_carry.ps1 -Attempt Run81`（Shipping，`DY_CAMPAIGN_AUTOPLAY=1` + `DY_CARRY_PROBE=1`）→ `Saved/CarryProbe.log` **12 行**：每幕第 1 步都是 `light=0.150 puppet=0.150 carried=0`，第 2、3 步 `carried=1` 且等于上一步定义里的 Target（`act=2 chapter=1/4 light=0.680 puppet=0.150`（P01 偶未启用→回 0.15）、`act=3 chapter=1/4 light=0.720 puppet=0.800`、`act=2 chapter=2/4 light=0.660 puppet=0.380`、`act=3 chapter=2/4 light=0.340 puppet=0.600`、`act=2 chapter=3/4 light=0.380 puppet=0.500`、`act=3 chapter=3/4 light=0.500 puppet=0.840`、`act=2 chapter=4/4 light=0.580 puppet=0.860`、`act=3 chapter=4/4 light=0.860 puppet=0.860`），同轮 `CampaignProbe.log` 25 行到 `phase=4 chapter=4/4 act=3 title=晦明同光`，截图 `Run81-carry-002s…082s.png`；`verify_sfx.ps1 -Attempt Run81` 同样 25 行到 `phase=4 …晦明同光`、`SfxProbe.log` **9 条**（鼓 15.9/32.1/47.6/63.0，结算 24.1/39.6/55.0/70.5，锣 76.5）；`verify_replay.ps1 -Attempt Run81` `REACHED_PHASE4=True`、`REPLAY_NEW_LINES=25`（`BEFORE_LEN=1093` → `AFTER_LEN=2187`）、`VERIFY-REPLAY-DONE`，截图 `Run81-replay0..3.png`、`Run81-pause.png`。**自动演出证明不了携带**：`HandleCampaignAutoPlayTick()` 每步都直接 `SetNormalizedValue(Target)`，所以必须靠上面这个文件探针。
- **Run77 证据**：`Run77-endfull.png`（结束面板：主牌是「◆ 重新复演」，不是被覆盖的「开始游戏」；末行两条提示「选「重新复演」或按 Enter 从头再看。」+「「游戏说明」打开影偶图鉴。」）；`Run77-codexfull1.png`（图鉴正文改「四幕剧终后，四具影偶录入图鉴，可在此回顾造型与操演。」，聚焦行朱红底 + 暖金字、**没有 1 px 蓝框**）；`Run76-pause.png`（暂停面板「◆ 继续游戏」琥珀牌面、顶部「开始游戏」仍为禁用灰牌且六格与背景美术对齐）；`Run76-chapters2.png`（「演出篇章」第二行红底 + 暖金字、无蓝框、四行「（已演）」）；编辑器同机位 `Edchk5-menu-zoom.png` / `Edchk5-pause-zoom.png`。`verify_sfx.ps1 -Attempt Run77` 25 行到 `phase=4 chapter=4/4 act=3 title=晦明同光` + `SfxProbe.log` 9 条（鼓 15.8/32.1/47.6/63.0，结算 24.1/39.6/55.0/70.7，锣 76.7）；`verify_replay.ps1 -Attempt Run77` `VERIFY-REPLAY-DONE`。
- **Run75 证据**：修前反证——在用 `0f` 种入 `%LOCALAPPDATA%\DengYingShanHai\Saved\DYProgress.txt` 的 Run74 Shipping 上打开「演出篇章」，四行**都没有**「（已演）」；修后 Run75 同一文件出现四行全标（`Run75-hexchapters.png`），换成 `PlayedMask=0a` 则只标第二、第四幕（`Run75-hex0a-chapters.png`，bit1/bit3），证明是按十六进制解析而不是碰巧；编辑器同验证 `Ed-hexread2-1.png`。`verify_sfx.ps1 -Attempt Run75` 25 行到 `phase=4 chapter=4/4 act=3 title=晦明同光` + `SfxProbe.log` 9 条（鼓 16.0/32.3/47.8/63.2，结算 24.3/39.8/55.2/70.7，锣 76.7）；`verify_replay.ps1 -Attempt Run75` `REACHED_PHASE4=True` / `VERIFY-REPLAY-DONE`。
- **Run74 证据**：Shipping 种入 `ProgressChapter=2` + `PlayedMask=03` 后 `Run74-chapterlist.png`（「演出篇章」第一、二行行尾是「（已演）」、第三四行不带标记、焦点在第一行；提示行变成「（已演）表示这一幕演完过」；主菜单「继续游戏」同时为可用态）；编辑器 `-game` 同机位 `ChapSeed-2-list.png`；`DY_CAMPAIGN_AUTOPLAY=1` 跑完四幕后进度文件为 `ProgressChapter=0` / `PlayedMask=0f`；`verify_sfx.ps1 -Attempt Run74` 25 行到 `phase=4 chapter=4/4 act=3 title=晦明同光` 且 `SfxProbe.log` 9 条（鼓 t=16.0/32.0/47.9/63.6，结算 t=24.0/39.9/55.6/71.2，锣 t=77.2）；`verify_replay.ps1 -Attempt Run74` `REACHED_PHASE4=True` / `VERIFY-REPLAY-DONE`。
- **Run73 证据**：真机首启（无进度文件）`Run73-fresh-menu.png` 里第二块牌是灰底禁用态；按 Enter 走完一段后 `%LOCALAPPDATA%\DengYingShanHai\Saved\DYProgress.txt` 变成 `ProgressChapter=1`，重启后 `Run73-continue-menu.png` 里该牌变奶油可用态（裁切 `Run73-fresh-menu-crop3.png` / `Run73-continue-menu-crop3.png` 对比）；编辑器 `-game` 用 `ProgressChapter=2` 复验日志 `progress loaded chapter=2` → `continue chapter=2 resumed=1`，画面为第二幕的冷蓝调（`ContE-1-menu.png` / `ContE-2-open.png`）。
- **Run72 证据**：`Run72-step01..05.png`（真机入口走查：灯径只剩一套「瘦石柱 + 球灯 + 黄铜灯帽 + 宝顶」，矮灯的小房子轮廓消失，路面亮度与 Run71 一致）；`verify_sfx.ps1 -Attempt Run72` 25 行到 `phase=4 chapter=4/4 act=3 title=晦明同光` 且 `SfxProbe.log` 9 条（鼓 t=16.0/32.0/47.5/63.2，结算 t=24.0/39.5/55.2/71.0，锣 t=77.0）；`verify_replay.ps1 -Attempt Run72` 后 `CampaignProbe.log` 由 25 行增至 50 行（`REPLAY_NEW_LINES=25`）。
- **Run71 证据**：`Run71-step01..05.png`（真机入口走查：近景山锥已退出构图、树冠不再是等半径圆、12 根灯柱顶端不再出现灰格材质）；`verify_sfx.ps1 -Attempt Run71` 25 行到 `phase=4 chapter=4/4 act=3 title=晦明同光` 且 `SfxProbe.log` 9 条（鼓 t=15.9/32.0/47.5/62.9，结算 t=24.0/39.5/54.9/70.2，锣 t=76.2）；`verify_replay.ps1 -Attempt Run71` 后 `CampaignProbe.log` 由 25 行增至 50 行（`REPLAY_NEW_LINES=25`）。
- **Run70 证据**：`Run70-chapterlist.png`（「演出篇章」第一行朱红底 + 暖金字）、`Run70-settings.png`（「主音量 10 / 10」同款高亮）、`Run70-menu.png`、`Run70-campaign-002s…087s.png`、`Run70-replay0..3.png`；`verify_sfx.ps1 -Attempt Run70` 25 行到 `phase=4 chapter=4/4 act=3 title=晦明同光` 且 `SfxProbe.log` 9 条（鼓 4 / 结算 4 / 锣 1，t=16.x…77.4）；`verify_replay.ps1 -Attempt Run70` `REPLAY_NEW_LINES=25`。

## 10. 编辑事故与 Run 台账（2026-10-22 重建）

> **事故**：2026-10-22 12:13，一次「读整文件再写回」的编辑把本文档从 **241,216 字节**写成 **55,097 字节**——`read` 对超大文件有输出上限，读到的是截断内容，写回即覆盖掉原 §8–§9.53。原文件未纳入 git，无副本可恢复。
> **处置**：§1–§7 与残存的 §9.2 / §9.4 段落原样保留；§8 台账改为**直接由 `Saved/Audit-2026-10-20-V21/Package-Run*/RESULT.json` 生成**（每个包的真实产物字段，比散文更可靠）；§9.45–§9.54 是我仍能逐条复述的近轮细节；更早各轮的一句话摘要以 `Docs/BASELINE-V21.md`（打包基线逐包条目）与 `Docs/GDD.md` 附录 A 为准。
> **教训**：大文件不要走 `read` → `write` 往返。读用 `fs.readFileSync`、写用 `fs.writeFileSync`（或 `edit` 打补丁），永远不要用「读到的内容」当整文件的新内容。

### 10.1 台账（124 个已归档包，全部 `PASS-BUILD-COOK-STAGE-ARCHIVE` / `UATExit=0`）

完整哈希见各 `Package-RunNN/RESULT.json`；下表给 map / exe 哈希前缀便于对照。**Run5 / Run29 / Run40 / Run94 无归档**（作废或未落盘）。

| Run | 产物 | 字节 | map 前缀 | exe 前缀 |
|---|---|---|---|---|
| 1 | — | — | `6ECB12E3DBF1` | `80FD37EE541E` |
| 2 | — | — | `510286F386DE` | `80FD37EE541E` |
| 3 | — | — | `510286F386DE` | `74B0CBDA0538` |
| 4 | — | — | `98043673DEB3` | `74B0CBDA0538` |
| 6 | 31 | 756,900,562 | `5512ABA3BDFB` | `87565BA963BC` |
| 7 | — | — | `5512ABA3BDFB` | `58B8631A1F9B` |
| 8 | 31 | 756,904,154 | `9A486646EE23` | `3EDB7B62176C` |
| 9 | 31 | 756,912,858 | `A1B45456F8AB` | `D2545A8A4E50` |
| 10 | 31 | 756,912,858 | `838BC836D443` | `D2545A8A4E50` |
| 11 | 31 | 756,912,858 | `10DF4A72C898` | `D2545A8A4E50` |
| 12 | 31 | 756,912,870 | `DB92357F1099` | `B9F91979E40A` |
| 13 | 31 | 756,929,766 | `DB92357F1099` | `EB28DFFAAA06` |
| 14 | 31 | 756,931,302 | `DB92357F1099` | `675989983916` |
| 15 | 31 | 756,931,302 | `22B77CD96996` | `675989983916` |
| 16 | 31 | 756,940,518 | `24808F6957A3` | `F38BEAF79261` |
| 17 | 31 | 756,923,622 | `24808F6957A3` | `F244082AEDA9` |
| 18 | 31 | 756,923,622 | `E0E6B9FD7186` | `F244082AEDA9` |
| 19 | 31 | 757,064,790 | `94676387E291` | `8A1FE8E81192` |
| 20 | 31 | 757,070,934 | `94676387E291` | `B099D072D781` |
| 21 | 31 | 757,071,446 | `853596AFC432` | `D48A9A390DBF` |
| 22 | 31 | 757,080,662 | `853596AFC432` | `AD8CD7F4B7B0` |
| 23 | 31 | 757,080,662 | `853596AFC432` | `AD8CD7F4B7B0` |
| 24 | 31 | 757,081,174 | `853596AFC432` | `AAB9BE10FD98` |
| 25 | 31 | 757,082,710 | `853596AFC432` | `A1C6E0E5C1A5` |
| 26 | 31 | 757,090,902 | `853596AFC432` | `7019359BCF82` |
| 27 | 31 | 757,091,414 | `853596AFC432` | `055C0EF19440` |
| 28 | 31 | 757,104,214 | `1524DCF59755` | `B0DDBD190FF1` |
| 30 | 31 | 757,098,582 | `A5FEF4AD529B` | `0256BD7FC429` |
| 31 | 31 | 757,103,202 | `AA8ABA712B72` | `11938D5FF4DA` |
| 32 | 31 | 757,105,262 | `53063ED7C1D5` | `11938D5FF4DA` |
| 33 | 31 | 757,113,466 | `CDE35C3FDC5B` | `11938D5FF4DA` |
| 34 | 31 | 757,121,670 | `FA4011CB03C2` | `11938D5FF4DA` |
| 35 | 31 | 757,106,310 | `FA4011CB03C2` | `2B7C3067C80B` |
| 36 | 31 | 757,112,478 | `E3819D2134F5` | `2B7C3067C80B` |
| 37 | 31 | 757,085,794 | `65C6751D37BC` | `2B7C3067C80B` |
| 38 | 31 | 757,085,794 | `293B9D727755` | `2B7C3067C80B` |
| 39 | 31 | 757,102,690 | `293B9D727755` | `3FA4E9AC2664` |
| 41 | 31 | 757,111,906 | `293B9D727755` | `74FA08EAF903` |
| 42 | 31 | 757,111,906 | `293B9D727755` | `0574B15048DC` |
| 43 | 31 | 757,120,098 | `293B9D727755` | `8CF9817EA98A` |
| 44 | 31 | 757,668,586 | `293B9D727755` | `CC899777B42F` |
| 45 | 31 | 757,670,634 | `B944DF51976E` | `CC899777B42F` |
| 46 | 31 | 757,670,634 | `6C8C34783105` | `CC899777B42F` |
| 47 | 31 | 757,679,850 | `6C8C34783105` | `B20EC39EE122` |
| 48 | 31 | 757,742,036 | `6C8C34783105` | `59179CE623CF` |
| 49 | 31 | 757,743,572 | `6C8C34783105` | `4B20A341C6B9` |
| 50 | 31 | 757,752,788 | `6C8C34783105` | `DA0432FA1F58` |
| 51 | 31 | 757,738,452 | `6C8C34783105` | `598DBACAEB01` |
| 52 | 31 | 757,752,788 | `6C8C34783105` | `41B8708634D5` |
| 53 | 31 | 757,767,148 | `AE761B87C4AF` | `41B8708634D5` |
| 54 | 31 | 757,776,396 | `60E6F37E4827` | `246F30F94609` |
| 55 | 31 | 757,776,396 | `D71485BD6186` | `4BE267E70137` |
| 56 | 31 | 757,776,396 | `D71485BD6186` | `226C99960741` |
| 57 | 31 | 757,776,908 | `D71485BD6186` | `07F0A248374F` |
| 58 | 31 | 757,847,052 | `D71485BD6186` | `AB1D12D999C7` |
| 59 | 31 | 757,848,588 | `D71485BD6186` | `5D03C8A2F021` |
| 60 | 31 | 757,857,292 | `D71485BD6186` | `8E41056DDA5C` |
| 61 | 31 | 757,857,292 | `D71485BD6186` | `E9A6D6F71522` |
| 62 | 31 | 757,857,804 | `D71485BD6186` | `DF9E41E0C086` |
| 63 | 31 | 757,864,972 | `D71485BD6186` | `DBA4AC4C8354` |
| 64 | 31 | 757,860,888 | `E4AF1F47D073` | `DBA4AC4C8354` |
| 65 | 31 | 757,860,888 | `D3FEDF1CB537` | `DBA4AC4C8354` |
| 66 | 31 | 757,842,456 | `C8475F005887` | `F7B5E39270DC` |
| 67 | 31 | 757,842,456 | `254E7DF23CF5` | `F7B5E39270DC` |
| 68 | 31 | 757,838,316 | `0C833856E9DE` | `F7B5E39270DC` |
| 69 | 31 | 757,847,020 | `0C833856E9DE` | `D1BB39042052` |
| 70 | 31 | 757,848,556 | `0C833856E9DE` | `D835A7A0974E` |
| 71 | 31 | 757,854,716 | `A84ABF05F32D` | `D835A7A0974E` |
| 72 | 31 | 757,852,668 | `774694ACFB61` | `D835A7A0974E` |
| 73 | 31 | 757,862,012 | `774694ACFB61` | `09FED426EEDE` |
| 74 | 31 | 757,880,556 | `774694ACFB61` | `5EA33D6FD81E` |
| 75 | 31 | 757,880,556 | `774694ACFB61` | `9EA71D9C37DE` |
| 76 | 31 | 757,882,092 | `774694ACFB61` | `1FC864722B54` |
| 77 | 31 | 757,890,796 | `774694ACFB61` | `5C4700B9C452` |
| 78 | 31 | 757,890,796 | `BB0AE8F5EB29` | `5C4700B9C452` |
| 79 | 31 | 757,953,260 | `BB0AE8F5EB29` | `EDD2FC47F219` |
| 80 | 31 | 757,945,068 | `2DA372A32870` | `7F9D0719509F` |
| 81 | 31 | 757,955,308 | `2DA372A32870` | `BC5D5FF36B28` |
| 82 | 31 | 757,978,860 | `2DA372A32870` | `001F16A7A7FD` |
| 83 | 31 | 758,014,188 | `2DA372A32870` | `7204F52EAA81` |
| 84 | 31 | 758,005,996 | `2DA372A32870` | `73E969A2581B` |
| 85 | 31 | 758,005,996 | `F37EC39A5151` | `73E969A2581B` |
| 86 | 31 | 758,718,927 | `6BC569635BC2` | `73E969A2581B` |
| 87 | 31 | 758,718,927 | `BF0DC7D452EA` | `73E969A2581B` |
| 88 | 31 | 758,738,895 | `765D584F3EAA` | `1710A30AD8FC` |
| 89 | 31 | 758,738,895 | `EC8425823DF3` | `1710A30AD8FC` |
| 90 | 31 | 759,152,417 | `4073DED0FA6A` | `1710A30AD8FC` |
| 91 | 31 | 759,152,417 | `760A09A21A58` | `1710A30AD8FC` |
| 92 | 31 | 759,156,791 | `975B4444D86D` | `1710A30AD8FC` |
| 93 | 31 | 759,156,791 | `975B4444D86D` | `1710A30AD8FC` |
| 95 | 31 | 759,156,791 | `C78298F25650` | `1710A30AD8FC` |
| 96 | 31 | 751,121,991 | `E47D94B53BD2` | `1710A30AD8FC` |
| 97 | 31 | 751,210,358 | `63C9E82A67F3` | `1710A30AD8FC` |
| 98 | 31 | 751,237,006 | `6E09FE6F0D1D` | `1710A30AD8FC` |
| 99 | 31 | 751,237,006 | `D6BA10E91FB1` | `1710A30AD8FC` |
| 100 | 31 | 751,237,006 | `67B5E713693E` | `1710A30AD8FC` |
| 101 | 31 | 752,992,875 | `0846A10E6974` | `1710A30AD8FC` |
| 102 | 31 | 752,977,826 | `61905D310C2B` | `1710A30AD8FC` |
| 103 | 31 | 756,354,646 | `2CA716ED373E` | `7B86DA7926B3` |
| 104 | 31 | 756,465,286 | `2CA716ED373E` | `7B86DA7926B3` |
| 105 | 31 | 756,607,536 | `BFA9109555A8` | `7B86DA7926B3` |
| 106 | 31 | 756,683,136 | `C2DE39A21995` | `7B86DA7926B3` |
| 107 | 31 | 756,685,184 | `EA92785E5937` | `7B86DA7926B3` |
| 108 | 31 | 756,687,507 | `3FFF3414BC3A` | `7B86DA7926B3` |
| 109 | 31 | 756,687,507 | `84EEE6BEE7E1` | `7B86DA7926B3` |
| 110 | 31 | 760,801,003 | `3B2B1FE813AE` | `1B0B6A4FD5C3` |
| 111 | 31 | 760,801,003 | `9D610077E9C8` | `1B0B6A4FD5C3` |
| 112 | 31 | 760,801,003 | `A6BBB53EAE5C` | `1B0B6A4FD5C3` |
| 113 | 31 | 761,094,213 | `CAA128C0F073` | `1B0B6A4FD5C3` |
| 114 | 31 | 760,801,003 | `801F9618464D` | `1B0B6A4FD5C3` |
| 115 | 31 | 760,801,003 | `DE43A33A797B` | `1B0B6A4FD5C3` |
| 116 | 31 | 760,801,003 | `73380BF746E1` | `1B0B6A4FD5C3` |
| 117 | 31 | 760,801,003 | `2E7DD38681DE` | `1B0B6A4FD5C3` |
| 118 | 31 | 760,801,003 | `AEF5A6F96A9D` | `1B0B6A4FD5C3` |
| 119 | 31 | 760,838,795 | `6FA942421ED5` | `1B0B6A4FD5C3` |
| 120 | 31 | 760,838,795 | `25F3907B3B4D` | `1B0B6A4FD5C3` |
| 121 | 31 | 760,814,219 | `25F3907B3B4D` | `1B0B6A4FD5C3` |
| 122 | 31 | 760,814,219 | `25F3907B3B4D` | `1B0B6A4FD5C3` |
| 123 | 31 | 760,814,219 | `031100C3646C` | `1B0B6A4FD5C3` |
| 124 | 31 | 760,814,219 | `031100C3646C` | `C47EB57726E7` |
| 125 | 31 | 760,983,728 | `7A34D1287118` | `C47EB57726E7` |
| 126 | 31 | 760,539,025 | `7A34D1287118` | `C47EB57726E7` |
| 127 | 31 | 760,544,163 | `6E50B224C0E1` | `C47EB57726E7` |
| 128 | 31 | 760,556,929 | `A9A581AC69C4` | `C47EB57726E7` |

### 10.2 阶段划分
- **Run1–Run27**：V2.3 四幕连演从首轮包到稳定（Run5 作废）。
- **Run28–Run84**：入口提示、外景美术、四幕配色、影偶图鉴、自制背景乐与锣鼓、帧率探针、设置回滚/持久化、复演闭环、门前修形、标题面板续演、章节已演标记、焦点环、HUD 站位提示、幕间题签。
- **Run85–Run114**：外景全量美术补（世界坐标 UV 材质、322 个枝冠、外墙壁柱、B3 山石、C2 锣鼓、月光补光）、B1 山体剪影定稿、图鉴「制作七步」、观众厅吊灯与内顶望板、两次山脊网格尝试失败回退。
- **Run115–Run128**：入口灯径白色占位片归因与改嵌石（Run124）、后台锣鼓曲面网格（Run125）、影窗绢面与灰泥细化（Run126）、观众厅影偶挂屏（Run127）、观众席木长凳（Run128）。

## 11. 近轮改动详解（对应旧 §9.45–§9.53）

### 11.1（旧 §9.45）B1 山脊网格第二次尝试：失败回退（Run113 作废 / Run114 复归）
`SM_DY_Ridge_A..F` + `M_DY_RidgeMat` + `MI_DY_Ridge_*` 在编辑器视图里是可接受的山脊，进 Shipping 后变成巨大的白楔子/白刃（`s113-w02.png`），Run113 全包作废；`pass290_revert` / `pass291_restore` / `pass292_clean` 回退并删资产，Run114 复归 Run112 的观感。结论：**远景山体只保留 43 座锥体 + `M_DY_MountainFlat` 墨色分层 + 距离隐藏**，不再试网格化。

### 11.2（旧 §9.46）入场面光衰减与「路面引导光带」（Run115–Run118）
`DYTheater_GateLamp_L/R` 5200→3000、`DYExt30_Uplight_00..04` 5200→3600、`DYExt16_FacadeLamp_L` 600→480（Run118 定稿）。同期三次内部诊断包不入基线：Run115（路面 movable 试验）、Run116（36 盏灯全关）、Run117（灯复原）。Run118 实测 **AVG 145.3 fps / MIN 128.4 / MAX 160.8**（`perf_shot.ps1`）。

### 11.3（旧 §9.47）门外「燈影」匾（Run120 定稿；Run119 作废）
`gen_plaque.py` 用 `Assets/Sources/UI/MenuV2/Fonts/NotoSerifSC-Bold.ttf` 生成 1024×320 匾面（深漆木底 + 压暗木纹 + 双线金框 + 196 px 金字）；材质 `M_DY_PlaqueBoard`（`BaseTex`×`Tint`→BaseColor、tex×`Glow`→Emissive、Rough 0.45 / Metal 0.2）+ `MI_DY_PlaqueBoard` Glow 0.45；匾身 `ART_A4_GatePlaqueOuter` (-1846,-210,1130) scale (0.06,4.2,1.3) = 420×130 cm，挂在 `ART_EXT_RearBand` 前 3 cm，4 根 `MI_DY_AgedBrassProp` 框条在 x=-1852。Run119 曾放 z=1330 被屋檐压成暗板 → 作废。

### 11.4（旧 §9.48）入口路面青石板（Run121→Run122）
`gen_stone_v2.py` 生成 1024² 不规则石板（行高 84–142、板宽 96–236、缝 4 px、板色 64–96、45% 磨角、26 条裂纹、冷灰偏色）；`pass312_stone.py` 覆盖导入同名 `T_DY_StonePathTex_BaseColor` 并把 `MI_DY_StonePathTex` 的 `TileU/TileV` 170→**250**；`pass313_stone_tint.py` 把 `Tint` 调 **(0.80,0.80,0.78)**（Run121 放大后偏亮，Run122 压回暗青石）。

### 11.5（旧 §9.49）门脸木格窗（Run123）
`pass314_lattice.py` 生成 26 件 `ART_EXT_Lattice_{L,R}_{Top,Bot,Left,Right,M1..M7,H0,H1}`：x=-1818、z 1250–1560、左跨 y -1180…-280 / 右跨 y 280…1180、框 24×14 cm / 棂 16×5 cm，材质 `MI_DY_FramePost_Wood`；actor 1723→**1749**。Run123 与 Run122 字节相同（760,814,219），只有 map 变。

### 11.6（旧 §9.50）入口灯径：白色占位片换成嵌石（Run124）
**真凶**：不是关卡资产、不是 BP、不是灯光或后处理，而是 C++ `ADYStageEnvironment::BeginPlay()` 里 `LayReadableEntry()` 在运行时造的 8 片 `/Engine/BasicShapes/Plane`，材质是 `BasicShapeMaterial` 的 MID（纯白奶油色），4 cm 浮在路面上、间距 320 cm，x 从 -4500 起、y=-210。排除路线：843 个走廊 actor 普查无平面光带/无 ISM/无 Decal；路面 `DYTheater_ExtPath` 是单 Cube + `MI_DY_StonePathTex`；PIE Simulate 里运行时世界 1767 actor（比编辑器多 18 个全是 Pawn/GameMode/HUD 类）却**没有任何新增石板几何**；`M2_StageEnvironment` 的包围盒是一条 x -4610…-2150、y ±57.5、z=-16 的扁平长条 → 直指该 Actor，逐组件 dump 出 8 个 `Cube/Plane` 组件才定位。
**修法**（`Source/DengYingShanHai/Private/Stage/DYStageEnvironment.cpp` 的 `LayReadableEntry()`）：`Plane`→`Cube`；材质换成 `/Game/DengYingShanHai/Dev/ArtPolish_20261022/Materials/MI_DY_StonePathTex` 的 MID（`Tint` (1.46,1.34,1.12)、`Roughness` 0.94、`Specular` 0.02）；尺寸 224–236×114–119×**2 cm**；`SetWorldLocation(Hit.ImpactPoint + FVector(0,0,1.1))`（原来 +4 cm、5 cm 厚会形成黑侧框）；`FRandomStream InlayJitter(20261022)` 抖动。
**结果**：`s124-w02.png` 里白矩形消失，代之以淡砂岩嵌石带（板缝与路面同向）；Run124 exe 哈希自 Run110 以来首次变动（`C47EB577…`）。

### 11.7（旧 §9.51）后台锣鼓道具：方块体换成曲面网格（Run125）
27 件 `ART_C2_*` 原本全是引擎基本体（Cube/Cylinder/Sphere）。`gen_props_c2.py` 生成 11 个 OBJ（1 unit = 1 cm）：`sm_dy_drum_body`（Ø62–67 × 高 56 桶形）、`drum_heads`、`drum_studs`（3 圈 × 20 颗）、`drum_stand`、`gong_large`（Ø75 卷边）、`gong_stand`、`gong_small`（Ø24）、`cymbal`（Ø34）、`prop_chest`（92×56×54）、`prop_chest_bands`、`prop_table`（124×62×76）；`pass325_c2props.py` 导入为 `SM_DY_C2_*` 并重摆，`pass327_c2mats.py` 赋材质，`pass328_c2detail.py` 补鼓绳/竹签/抬锣，`pass329_c2tweak.py` 微调钹倾角。
材质真实路径（重要）：朱漆 `/Game/DengYingShanHai/Dev/WorldV2/Materials/MI_DY_LacquerVermilion`、木 `/Game/DengYingShanHai/Dev/StageFrameM03/Materials/MI_DY_M03_FrameWood`、黄铜 `/Game/DengYingShanHai/Dev/KuafuAppearance/Materials/MI_DY_AgedBrass`、鼓皮新建 `MI_DY_C2_DrumHead`（父 `M_DY_PlasterTex`，`Tint` (0.62,0.52,0.38)、Rough 0.9、Specular 0.05）。actor 1749→**1740**。

### 11.8（旧 §9.52）影窗绢面与厅内灰泥（Run126）
影窗幕面 actor 是 `DEV_BackScreen`（Cube，中心 (925,0,424)、半长 (0.1,450,400) → 9×8 m，屏面朝 -X），材质 `MI_DY_ScreenCloth`（父 `M_DY_Cloth`：`BLEND_OPAQUE` / `MSM_DEFAULT_LIT`）。新贴图 `gen_screen_tex.py` → **2048×1820**：暖米底 (0.955,0.905,0.828) + 两组低频噪声 + **5 幅软竖缝**（wobble ±2.6 px、模糊 2.6 px、压暗 34/255）+ 幅内鼓起 + 顶部两道折痕 + 16 个模糊污渍；`pass338_screentex.py` 覆盖导入。**12 幅硬直缝版本失败**——整面读作彩钢板（等距硬线 = 板材语言），改软缝后才读作绢。灰泥 `MI_DY_PlasterTex` 的 `TileU/TileV` 95→**240**（`pass333_plastertile.py`）。Run126 字节 760,539,025（比 Run125 少 444,703：低频贴图压缩更省），map 与 Run125 相同。

### 11.9（旧 §9.53）观众厅侧墙：影偶图鉴挂屏（Run127）
观众厅两墙是 `DYTheater_Wall_L/R` 外面贴的 `ART_A3_Plaster_L/R`（`MI_DY_PlasterTex`），从观众席转身看是 40 m 长空白灰泥。做法：复用菜单「影偶图鉴」的四张插画（`/Game/DengYingShanHai/UI/Codex/T_DY_Codex_{Kuafu,Jingwei,Xingtian,Zhulong}`）。
- 框：`gen_frame.py` → `SM_DY_PuppetFrame`（160×230 cm、框条 12 cm、深 8 cm、**无背板**，`box_extent` (80,4,115)），材质 `MI_DY_M03_FrameWood`。
- 画面：`MI_DY_HallFrame_{Kuafu,Jingwei,Xingtian,Zhulong}`（父 `M_DY_PlaqueBoard`，参数 = 标量 `Glow`/`Roughness`/`Metallic` + 向量 `Tint` + 贴图 `BaseTex`），`Glow` **0.20**、`Tint` (1.0,0.95,0.86)；几何用**薄 Cube**（scale (1.36,0.03,2.06)）。
- 摆位（`pass347_frames3.py`）：x = **-1430 / -900 / -370 / 150**、z = **820**、左墙 y=-1269 yaw 0 / 右墙 y=+1269 yaw 180；每屏一盏 `PointLight` 墙外 62 cm、**120 cd / 半径 340 / cast_shadows=False / (1.0,0.78,0.50)**。actor 1740→**1764**。
- 两个坑：**框不能有背板**（否则只剩木板）；**画面不要用 `unreal.Plane`**（朝向取决于 `unreal.Rotator` 轴序，背面剔除后整片消失）。

## 12. 观众席：两列木长凳（Run128）

### 12.1 动机
观众厅是 **40 × 26 m** 的大空间，地面从 `x=-1700`（门）一直铺到 `x≈925`（影窗），但整个观众区一件陈设都没有——从门内看向影窗是一整片空木地板，读不出「这里坐过人」。剧场该有座位，而座位又必须让开中央走道（玩家要从门走到幕前，且不能挡住互动区）。

### 12.2 做法：一条程序化长凳，成对复制
- **网格**：`C:/dy_build/gen_bench.py` 生成 `C:/dy_build/obj/bench/sm_dy_audbench.obj`（`BENCH-OK {'verts': 64, 'faces': 48, 'bytes': 2535}`）：沿 **Y 长 420 cm**、深 **40 cm**、座面 z = 40–46 cm、背靠两段斜靠板（z 52–74 / 72–94）、4 组侧腿 + 下枨。导入为 `SM_DY_AudBench`（`/Game/DengYingShanHai/Dev/ArtPolish_20261022/Meshes`，`box_extent` = (23, 210, 47)）。
- **摆位**（`C:/dy_build/pass350_bench.py` + `pass354_seat.py`）：4 排 × 2 侧 = **8 条长凳**，x = **250 / 90 / -70 / -230**（排距 160 cm），y = **±560**；中央 |y| < 350 留作走道。凳材质 `MI_DY_M03_FrameWood`。
- **坐垫**：每条凳一块薄 Cube（scale (0.38, 4.05, 0.055) → 380 × 405 × 5.5 cm，z = 52），材质 `MI_DY_LacquerVermilion`（朱漆），让长凳在暖光下有一条明确的红色水平线，与暗木地面分开。
- **座位灯**：每排两侧各一盏 `PointLight`（`ART_LGT_AudSeat_{0..3}_{L,R}`，z = 260），**320 cd / 半径 620 / cast_shadows=False / 暖色 (1.0,0.80,0.56)**。原来这一片只有 5 盏灯，长凳在暗处读作黑块；加灯后座面与靠背的转折能读出来。
- 命名 `ART_AUD_Bench_{0..3}_{L,R}` / `ART_AUD_SeatCushion_{0..3}_{L,R}` / `ART_LGT_AudSeat_{0..3}_{L,R}`，脚本可反复重跑（先删同前缀）。

### 12.3 两个坑
- **`set_actor_label()` 只改 label，不改对象名**：清理/统计时要按 `a.get_actor_label()` 匹配；按 `a.get_name()` 前缀永远匹配不到（对象名仍是 `StaticMeshActor_N`），第一版清理逻辑因此全空。
- **材质路径必须逐个核实**：第一版给坐垫写的是 `MI_DY_LacquerOxBlood`，该资产在 `Dev/WorldV2/Materials` 里**不存在**，`load_asset` 返回 None 后 `if mat is not None: set_material(...)` 静默跳过，8 块坐垫全留默认灰材质。改成 `MI_DY_LacquerVermilion`（该目录下唯一的朱漆 MI）后才对。

### 12.4 结果
- map actor **1764 → 1788**（8 凳 + 8 坐垫 + 8 灯）。
- `Saved/Audit-2026-10-22-Audience/aud_hall.png` / `aud_seat2.png`：从门内看进去，中央走道两侧各四排长凳、凳面一道朱红坐垫，尽头是亮着的影窗与「逐日」匾；大厅从「空地板」变成「小戏台」。
- 打包：`Package-Shipping.ps1 -Attempt Run128` → `Status=PASS-BUILD-COOK-STAGE-ARCHIVE`、`UATExit=0`、31 文件 / **760,556,929** B（比 Run127 多 12,766 B：新网格 + map）、`NativeExeSHA256=C47EB57726E7DE069C2730ED97A01AF312E579EBBF5BCEC89926AC85E53E2867`（同 Run124–Run127）、`SourceMapSHA256=A9A581AC69C42077F7300745DA3B813BE56931E076BC51769A2787EE71052FAD`。
- 回归：`AutomationV53.log` **176 tests / 0 fail**；`verify_sfx -Attempt Run128` 9 cue（cue1 16.4/32.7/48.2/63.6、cue2 24.7/40.2/55.6/71.5、cue0 77.5，phase 链到 `phase=4 chapter=4/4 act=3 title=晦明同光`）；`verify_replay -Attempt Run128` → `REPLAY_NEW_LINES=25`、`REACHED_PHASE4=True`、`VERIFY-REPLAY-DONE`；真机帧 `Saved/Audit-2026-10-20-V21/s128-w01..w05.png`、`PROBE 98`。

### 12.5 教训
- **空大空间先用「重复件」填，不要造新结构**：一条 64 顶点长凳复制 8 次，比改建筑便宜两个数量级，而且立刻把「空地板」变成「戏台」。
- **陈设必须让开玩法动线**：先定中央走道（|y| < 350），再摆家具；否则玩家从门走到幕后会被自家陈设挡住。
- **暗环境里的家具要不就是剪影、要不就要有自己的光**：这一次选择给每排加一盏小瓦数无阴影点光，比调高环境光更省（环境光会把整间大厅洗平）。

## 13 自制网格补 UV：让木纹与漆面真正读出来（Run129）

### 13.1 现象
上几轮用 OBJ 自制了三个批次的网格（`SM_DY_AudBench` 观众席长凳、`SM_DY_PuppetFrame` 影偶挂屏框、11 件 `SM_DY_C2_*` 后台锣鼓道具），几何正确、材质也指向了正确的 `MI_DY_*`，但实机里长凳读作**浅银色金属条**、戏箱是一块没有细节的红方块。

### 13.2 定位
生成器（`C:/dy_build/gen_bench.py`、`gen_frame.py`、`gen_props_c2.py`）只写 `v` 与 `f`，**没有 `vt`**。UE 导入后网格没有 UV0，所有顶点采样同一 texel，材质里的木纹/漆纹等于被平均成一个颜色；颜色偏浅是因为采样点落在贴图的高光区。

### 13.3 做法
- `C:/dy_build/obj/uv/*.obj`：对每个 OBJ 做**盒式投影 UV**（按面法线取主轴，投影到对应两轴，单位取米 = cm/100），逐面写 `vt` 与 `f v/vt`。
- `C:/dy_build/pass362_uv.py`：`AssetImportTask`（`automated`/`replace_existing`/`save`）把 13 个网格重新导入到 `/Game/DengYingShanHai/Dev/ArtPolish_20261022/Meshes`，覆盖同名资产；actor 引用不变，无需重摆。
- UV 尺度：1 个 UV 单位 = 1 m，长凳 4.2 m 对应 4.2 UV，木纹密度与场内木地板/梁柱接近。

### 13.4 结果
- 长凳：木纹与板缝出现，座面朱红坐垫读作漆布；`Saved/Audit-2026-10-22-HallFront/hall_front.png` 里观众侧八排长凳的凳面、靠板、腿都能分辨。
- 后台道具：堂鼓桶身出现竖木条纹理、鼓架腿有了木纹、戏箱盖缝与箱箍分层；`Saved/Audit-2026-10-22-C2UV/c2_uv.png`。
- `Package-Shipping.ps1 -Attempt Run129`：`PASS-BUILD-COOK-STAGE-ARCHIVE`、`UATExit=0`、31 文件 / **760,556,929** B（与 Run128 同字节数属巧合：`DengYingShanHai-Windows.ucas` 的 SHA-256 前 16 位 `3ffcdca407d369fd` 与 Run128 的 `58c97682ada10f27` 不同，内容确实变了）、`SourceMapSHA256=5500DF0C61344F35A240EC338C8633460F8E4E4E1264D3BAAAE9375711D4ED5F`、`NativeExeSHA256=C47EB57726E7DE069C2730ED97A01AF312E579EBBF5BCEC89926AC85E53E2867`（未变，纯内容改动）。
- 回归：`AutomationV54.log` **176 tests / 0 fail**；`verify_sfx -Attempt Run129` 9 cue（cue1 16.4/32.4/47.8/63.3、cue2 24.4/39.8/55.3/70.8、cue0 76.8，phase 链到 `phase=4 chapter=4/4 act=3 title=晦明同光`）；`verify_replay -Attempt Run129`：`BEFORE_LEN=1093 AFTER_LEN=2187`、`REPLAY_NEW_LINES=25`、`REACHED_PHASE4=True`、`VERIFY-REPLAY-DONE`；真机帧 `Saved/Audit-2026-10-20-V21/s129-w01..w05.png`、`PROBE 98`。

### 13.5 教训
- **自制网格必须带 UV**：只要材质上有贴图，缺 UV0 就等于「单色塑料」；盒式投影 30 行代码即可，比重做材质便宜。
- 打包体积相同**不代表内容相同**：`ArtifactBytes` 只统计按块对齐后的文件尺寸，小改动会被块对齐吞掉；判断是否真的换了内容要哈希 `.ucas`。
- 覆盖导入后 actor 引用保持不变（`replace_existing` 是原地替换资产），所以可以先摆位、后补 UV，不必重摆。
## 14 观众厅中央地毡（Run130）

### 14.1 动机
入厅后（x=-1800 门 → x≈925 影窗）有约 26 m 的空地板。Run128 补了四排长凳，但中央走道仍是一条没有指向性的木地板，玩家进门后缺少「往哪里走」的视觉引导；戏台观众席通常有一条直通台口的地毡。

### 14.2 做法
- 新贴图 `C:/dy_build/tex/carpet/carpet_crimson.png`（512²，无缝深红织纹：8 px 经纬交织 + 三档值噪声 + 微斑点 + 8 px 暗格线），由 `C:/dy_build` 内联 Node PNG 编码器写出（无第三方依赖）。
- 导入为 `/Game/DengYingShanHai/Dev/ArtPolish_20261022/Textures/T_DY_CarpetCrimson`（`srgb=True`、`TEXTUREGROUP_WORLD`）。
- 新材质实例 `MI_DY_AisleCarpet`：父 `M_DY_GroundTex`（世界坐标 UV 材质），参数 `BaseColorTex`=`T_DY_CarpetCrimson`、`TileU=TileV=110`（每 1.1 m 一个循环）、`Roughness=0.95`、`Specular=0.02`、`Tint=(1.0,0.94,0.90)`。世界坐标 UV 意味着 26 m 长的地毯不会拉伸。
- 几何：`ART_HALL_Carpet` 一个 Cube，位置 **(-460,-105,1.0)**、scale **(25.6,3.0,0.02)**（2560×300×2 cm），顶部 z=2.0（厅内地面顶面 z=0）；`cast_shadow=False`、mobility STATIC。
- 收边：`ART_HALL_Carpet_TrimL/R` 各一条 Cube，y=-253 / +43、scale (25.6,0.06,0.023)，材质 `MI_DY_AgedBrass`，读作两条金线压边。
- 让位检查：走廊带 y∈[-300,90]、x∈[-1800,900]、离地 1–60 cm 的 actor 只有 `ART_A4_WallPlinth_R`（y 73–117）→ 地毯上沿 45 cm，留 28 cm 间隙；未与长凳（|y|≥350）、台口柱（x=880）冲突。

### 14.3 结果
- 验收帧 `Saved/Audit-2026-10-22-HallFront/hall_front.png`：从入口看进去，朱红地毡沿中轴直通影窗，两条金线收边，观众席长凳分列两侧。actor **1788 → 1791**。
- `Package-Shipping.ps1 -Attempt Run130`：`PASS-BUILD-COOK-STAGE-ARCHIVE`、`UATExit=0`、31 文件 / **760,647,802** B（比 Run129 多 90,873 B：新贴图 + 材质 + map）、`SourceMapSHA256=B74471609AEE7A9C4803BB2982E471CAA489798FE09D7596CC7A425BBD683CE3`、`NativeExeSHA256=C47EB577…E53E2867`（未变）。
- 回归：`AutomationV55.log` **176 tests / 0 fail**；`verify_sfx -Attempt Run130` 9 cue（cue1 16.3/32.4/47.8/63.7、cue2 24.4/39.8/55.7/71.4、cue0 77.4）；`verify_replay -Attempt Run130`：`BEFORE_LEN=1093 AFTER_LEN=2187`、`REPLAY_NEW_LINES=25`、`REACHED_PHASE4=True`、`VERIFY-REPLAY-DONE`；真机帧 `Saved/Audit-2026-10-20-V21/s130-w01..w05.png`、`PROBE 98`。

### 14.4 教训
- **长条形大件用世界坐标 UV 材质**：一个 Cube 拉 26 m 时，普通 UV 材质的贴图会被拉成条纹；`M_DY_GroundTex` 这类世界坐标材质改一个 `Tile` 参数就解决。
- `MaterialInstanceConstant` 在本版本 Python 里**没有** `update_material_instance()` / `post_edit_change()`；设完参数直接 `EditorAssetLibrary.save_loaded_asset(mi)` 即可，重新 `load_asset` 读回参数能验证生效（本次 `Tint` 与 `BaseColorTex` 均读回正确）。
- 摆长条构件前先做**走廊带占用检查**（离地高度 + 包围盒与目标带宽求交），比事后看穿模快得多。
## 15 入口石路与全台木纹（Run131）

### 15.1 动机
- Run131 的起点是两张真机帧：`s130-w01` / `s130-w03` 里入口石板路读作**高对比棋盘格**，而门罩、台口柱、长凳等所有木构件读作**浅灰米色板材**。前者是贴图对比度过大；后者追到根因 —— `M_DY_FramePost_Master` 的 BaseColor / NormalDX / ARM 三张图全是 **32×32**，木纹根本不存在，只剩光照形成的浅灰色块。

### 15.2 石路：降低对比度（重画贴图）
- 旧图 `T_DY_StonePathTex_BaseColor`（`gen_stone_v2.py`）板色 64–96、26 条裂纹、磨角 0.90 → 在暖光下形成明显的明暗拼块。
- 新图 `C:/dy_build/gen_stone_v3.py` → `T_DY_StonePathTex_BaseColor_v3.png`（1024²）：板色收紧到 **76–90**、顶边 +4 / 底边 -3 的倒角代替磨角、裂纹 26→**12** 且强度 0.30→0.20、加 32×32 低频色调漂移 ±6、最终 0.9 px 模糊 + 1.6 噪声；冷灰偏色 [0.985, 1.0, 1.030]。
- 导入覆盖同名资产（`/Game/DengYingShanHai/Dev/ArtPolish_20261022/Textures/`，`srgb=True`、`TEXTUREGROUP_WORLD`）；`MI_DY_StonePathTex` 参数不动（`TileU/TileV=250`、`Tint (0.80,0.80,0.78)`，读回复核一致）。
- 验收帧 `Saved/Audit-2026-10-22-PathTex/entry_after.png`（相机 (-6000,-250,200)→(-1900,-210,700)）：石板读作连续灰石面，不再有明暗拼块。

### 15.3 石路：加两道路缘石
- 两个 `Cube`：`ART_EXT_PathKerb_L/R` 位置 **(-3690, -471 / +51, -15)**、scale **(37.2, 0.22, 0.10)**（3720×22×10 cm），顶面比路面高 10 cm；材质 `MI_DY_RockTex`、`cast_shadow=False`、mobility STATIC。
- 作用：石路与暗土路的交界由一条硬边收住，避免路缘糊进黑暗；在 `kerb_after.png` 里表现为一条细暗线。

### 15.4 门内六盏壁灯（原来半埋在墙里）
- 体检发现 `ART_EXT_WallLamp_00..05`（z=1140，y=-1215/-905/-615/175/485/775）在 x=-1795，而后墙实体是 x∈[-1825,-1775] → 灯笼一半埋在墙体内，只剩一块浅色方块露在**厅内侧**。
- 处理：六盏灯平移到 **x=-1762**（向厅内露出 13 cm，成为正常的壁挂灯），并新增六盏灯源 `ART_LGT_RearWallLamp_00..05` 在 (-1738, y, 1100)，**110 cd / 半径 420 / cast_shadows=False / 暖色 (1.0,0.78,0.52)**。
- 验收帧 `Saved/Audit-2026-10-22-HallBack/back_wide2.png`（相机 (500,-200,340)→(-1850,-210,560)）：后墙出现一排暖色灯与六个光斑，浅色方块消失。

### 15.5 木构件：32² 占位木纹换成 512² 真木纹
- 生成 `C:/dy_build/gen_wood_frame.py`：512² 深色红木 —— 竖向木纹（正弦 + 低频扰动，freq 2π/7.6）、径向木节 3 个、低频色漂、脊部微高光；同时由高度场求 Sobel 生成 **DX 法线图**（strength 3.2）。
- 覆盖导入 `T_DY_FramePost_BaseColor`（512²、`srgb=True`、`TC_DEFAULT`、`TEXTUREGROUP_WORLD`）与 `T_DY_FramePost_NormalDX`（512²、`srgb=False`、`TC_NORMALMAP`、`TEXTUREGROUP_WORLD_NORMAL_MAP`），路径 `/Game/DengYingShanHai/Dev/FramePostAsset/Textures/`。
- 只改贴图、不改材质与摆位：`M_DY_FramePost_Master` 与 `MI_DY_M03_FrameWood` 参数（`UVQuarterTurn=0`）保持不变，所有使用该材质的构件一并变暖：门罩（`DYTheater_GatePost_L/R`、`DYTheater_GateLintel`、`ART_A4_GateRoof_Front/Rear`、`ART_A4_GateEaveTip_L/R`）、影窗框（`ART_A1_Frame*`、`M03_Frame*`、卷轴）、台口（`ART_A2_*`）、长凳（`SM_DY_AudBench`）、锣架/案桌/戏箱（`SM_DY_C2_*`）。
- 验收帧：`Saved/Audit-2026-10-22-WoodTex/wx_gate.png`（门罩变暖红木，和墙面、灯池统一）、`wx_hall.png`（观众厅）、`wx_c2.png`（锣鼓道具）、`wx_back.png`（后墙）。

### 15.6 结果与数字
- actor **1791 → 1799**（+2 路缘石 +6 壁灯灯源）。
- `Package-Shipping.ps1 -Attempt Run131`：`PASS-BUILD-COOK-STAGE-ARCHIVE`、`UATExit=0`、31 文件 / **754,078,426** B（比 Run130 少 6,567,936 B）、`SourceMapSHA256=7D22DC2EED4E49A0DD8332ED9F60F72FDD9F758853ABA3F1433DB2FDFC977AF6`、`NativeExeSHA256=C47EB577…E53E2867`（未变）。
- 字节变小的位置已定位：差异全部在 `DengYingShanHai-Windows.ucas`（284,399,072 → 277,831,136），`.utoc` 仅 -1,440，文件数仍为 31、`CookedMaps` 仍为两张；重贴图后压缩结果变化，未删除任何资产，真机帧里新木纹与新石纹均已生效。
- 回归：`AutomationV56.log` **176 tests / 0 fail**；`verify_sfx -Attempt Run131` 9 cue（cue1 16.3/32.4/48.0/63.5、cue2 24.4/40.0/55.5/71.2、cue0 77.2，phase 链到 `phase=4 chapter=4/4 act=3 title=晦明同光`）；`verify_replay -Attempt Run131` → `BEFORE_LEN=1093 AFTER_LEN=2187`、`REPLAY_NEW_LINES=25`、`REACHED_PHASE4=True`、`VERIFY-REPLAY-DONE`；真机帧 `Saved/Audit-2026-10-20-V21/s131-w01..w05.png`、`PROBE 98`、`ART2-DONE`。

### 15.7 教训
- **贴图尺寸要查**：构件发灰、发糊时先看 BaseColor 的实际尺寸。32×32 的贴图铺在 4 m 长的梁上等于没有木纹，改材质参数永远救不回来。
- 一张共享贴图的覆盖式替换，比逐个 actor 换材质安全得多：改完 `M_DY_FramePost_Master` 的整条引用链一起更新，不需要动任何摆位。
- 大对比度贴图在暖光下会被放大成拼块；石材这类大面积铺装应把板色区间收窄（±8 以内），靠缝隙、倒角和低频漂移提供信息量。
- 半埋构件是隐蔽缺陷：位置落在墙体厚度区间内时，渲染结果只是一块浅色方块，从两侧看都不像灯。体检时要把墙的包围盒和构件位置一起看。
## 16 入口灯径：补两对灯柱（Run132）

### 16.1 动机
- Run131 的真机首帧 `s131-w01` 里，玩家起点 (-6900,-210) 到最近一盏路灯之间还有 **1200 cm** 完全无光的暗段：灯柱只排到 x=-4700，而石路从 x=-5600 就开始了。
- 结果是入场第一眼的前景是一整块黑地面，石路像从黑暗里突然飘出来；灯柱阵列的节奏在起点位置断掉了。

### 16.2 做法：照抄现有灯柱组件
- 原有灯柱是 9 件一套（6 对，x = -2200/-2700/-3200/-3700/-4200/-4700，y = **-560 / +140**，即石路中心 y=-210 两侧各 350 cm）：
  - `DYTheater_PathLantern_N_M`：Cube，34×34×250 cm 柱身，`MI_DY_RockTex`
  - `ART_A5_LanternBase_N_M`：38×38×4 cm 木托，`MI_DY_FramePost_Wood`
  - `ART_A5_LanternPaper_N_M`：30³ cm 灯纸盒，`MI_DY_LanternPaper`
  - `DYTheater_PathLamp_N_M`：Sphere 灯芯，`MI_DY_PathLantern`
  - `ART_A5_LanternRoof_N_M`：40×40×6 cm 木顶
  - `ART_A5_LanternFinial_N_M`：金属宝顶
  - `DYExt32_Cap_N_M`：52×52×10 cm 铜帽
  - `DYExt32_Finial_N_M`：铜顶珠
  - `DYTheater_PathLight_N_M`：PointLight **1500 cd / 半径 1300 / 暖色 / 无阴影**
- `C:/dy_build/pass391_moreposts.py` + `pass393_side2.py` 以 x=-4700 那一对为模板，逐件复制（StaticMesh + 材质 + 缩放 + `cast_shadow` 原样拷贝，PointLight 拷强度/半径/颜色并强制 `cast_shadows=False`），新增两组：**x=-5200、x=-5700**，两侧各一。
- 命名沿用 `_N_M` 规则：新增 `_6_0/_6_1`（-5200）与 `_7_0/_7_1`（-5700），共 **4 根柱 + 36 个 actor**。

### 16.3 一个必须记住的坐标事实
- 灯柱**不是**对称于 y=0，而是对称于石路中心线 **y=-210**：左列 y=**-560**，右列 y=**+140**。
- 第一次复制时按 `y<0 / y>0` 分边，只复制出左侧（18 件）；第二次按标签后缀 `_5_0/_5_1` 取模板、只平移 x 才补齐（actor 1817 → 1835）。

### 16.4 结果与数字
- actor **1799 → 1835**（+4 柱、+36 组件；其中 4 盏灯）。
- `Package-Shipping.ps1 -Attempt Run132`：`PASS-BUILD-COOK-STAGE-ARCHIVE`、`UATExit=0`、31 文件 / **754,080,474** B（比 Run131 多 2,048 B）、`SourceMapSHA256=32628AD34FB953F3DED678AF7388BA68E4A44DD118F97BCD09B0AA398C158081`、`NativeExeSHA256=C47EB577…E53E2867`（未变）。
- 回归：`AutomationV57.log` **176 tests / 0 fail**；`verify_sfx -Attempt Run132` 9 cue（cue1 16.4/32.6/48.3/64.0、cue2 24.7/40.3/56.0/71.5、cue0 77.5）；`verify_replay -Attempt Run132` → `BEFORE_LEN=1093 AFTER_LEN=2187`、`REPLAY_NEW_LINES=25`、`REACHED_PHASE4=True`、`VERIFY-REPLAY-DONE`。
- 真机帧 `Saved/Audit-2026-10-20-V21/s132-w01..w05.png`（`PROBE 98`）：首帧 `s132-w01.png` 中起点两侧各有一盏灯罩住前景，入场由「从黑暗走向灯」变成「走在灯径上」。

### 16.5 教训
- 复制现成组件比重新设计安全：形状、比例、材质、亮度全部沿用关卡里已经被验证过的那一套，只改位置，观感不会跑偏。
- 复制时**不要用轴心符号判断左右**，要用标签后缀或原坐标；这套灯柱的对称轴是 y=-210，不是 y=0。
- 逐件复制必须同时拷贝 `cast_shadow`：路灯不投影，否则 4 盏新灯会在石路上打出一排硬阴影。


## 17. Run133–Run137：门脸格窗的否定结论、树干竖直化与树冠回滚（2026-10-22）

### 17.1 门脸格窗：三次改进后判定删除（Run133 / Run134）
- **起因**：`ART_EXT_Lattice_*` 26 件的材质是 `WorldGridMaterial`（默认网格），且 x=-1818 整块落在后墙体内（墙体 x∈[-1825,-1775]），只有 5 cm 露在外面，远看是「淡淡方格」。
- 三次尝试：① 26 件外移到 x=-1834 + 换 `MI_DY_M03_FrameWood`，新增两块纸面 `ART_EXT_Lattice_L_Paper/_R_Paper`（2×900×310 cm，`MI_DY_LatticePaper`）→ 木格条在暖光下读成**亮金属网格/铁丝网**；② 删掉每侧 3 根格条、格子改 `MI_DY_TrunkTex`、纸面调暗 → 变成**纯黑方洞**（更差）；③ 删掉全部内部格条（12 件），只留四边框 → 变成「带木框的深色装板」，编辑器近景可接受，但真机 `facade_crop133/134.png` 里仍是**两条近黑横带**，像缺面而不是灯窗。
- **结论**：`pass408_tree.py` 删除全部 10 件 `ART_EXT_Lattice_*`，门脸上墙恢复**整面灰泥**（actor 1819 → 1809）。
- **教训（写死）**：门脸上墙区域**没有光源**。该区域任何细格都会读成「金属丝」，任何暗板都会读成「洞」，连自发光（Glow 1.0）也会被暗部吃掉。这块保持整面灰泥，不要再试细格。

### 17.2 树干竖直化（Run135，唯一有效的一步）
- `C:/dy_build/pass408_tree.py` 普查 633 个树相关 actor（输出 `C:/dy_build/pass408.json`）：**21 根树干被随机 pitch 到 ±21°~±86°**（`DYTheater_DeadTree_0..13`、`DYExt12_Trunk_0..7`），在夜空里读成**横向黑梁**——这就是此前多张截图里横切天空的「大黑斜杆」的根因。crown 的 z（如 1059 = 树干 754 高 + 冠半高）证明原作者本就按竖直设计。
- `C:/dy_build/pass411_assign.py`：46 个树干 actor（DeadTree 14 + `DYExt12_Trunk` 8 + `DYExt35_TreeTrunk` 8 + `DYExt36_Trunk00..15` 16）统一换 `SM_DY_Trunk_Unit100`；|pitch|>8 的 21 个改为 pitch=确定性抖动 ±6、roll=0，yaw 保留。actor 仍 1809。
- 树干网格：`C:/dy_build/gen_trunk.py` → `C:/dy_build/obj/tree/sm_dy_trunk.obj`（rings z=-50 r34 / -44 r30 / -10 r27 / 18 r22 / 40 r15 / 50 r4，顶部 50.4 收尖，附 2 根断枝 stub；97 v / 156 f），导入 `/Game/DengYingShanHai/Dev/ArtPolish_20261022/Meshes/SM_DY_Trunk_Unit100`，`box_extent ≈ (34.7, 32.1, 50.2)`。

### 17.3 树冠三次重建全部失败，最终回滚（Run136 → Run137）
- 原 `SM_DY_BranchCrown_A/B_Unit100`（`/Game/DengYingShanHai/Dev/B2WallPolish_20261022/Meshes/`）被三次覆盖，全部**不如原版**：
  1. `gen_crown.py` 径向细枝（1092 tris）→ 读成「海胆/绒球」；
  2. `gen_crown2.py` 鹿角式分叉（512 tris）→ 读成「脚手架硬杆/十字」；
  3. `gen_crown3.py` 细密灌木（2172 tris，r0 4.0→1.3，depth 3）→ 编辑器尚可，Run136 真机 `s136-w01.png` 里是**成团黑海星**，明显差于 Run135 的 `s135-w01.png`。
- **回滚方法（重要）**：原始 OBJ 一直留着——`D:/灯影山海/Assets/Sources/DengYingArt/B2-TreePolish-20261022/SM_DY_B2_BranchCrown_A_Unit100_v01.obj` 与 `_B_`（同目录还有 `build_branch_crowns.py` / `.mtl` / `_ortho.png`）。`C:/dy_build/pass421_restore.py` 用 `replace_existing` 重导入同名资产 → `box_extent` 回到 `(50,50,50)`；截图 `C:/dy_build/shots/crown_restored.png` 与改冠之前那张 `tree_fix2.png` **字节完全相同（1,444,762 B）**，这就是回滚成功的机器证据。
- **教训**：覆盖任何自建网格之前，先找 `Assets/Sources/DengYingArt/<批次>/` 里的原始 OBJ；`Content` 下的 `.uasset` 不是唯一副本，本项目所有自建网格都有源文件留档。

### 17.4 远山三档调暗（Run137）
- 普查 92 个山体/山脊 actor 的材质，实际只有三个材质实例：`MI_DY_MtnFlat_Near/Mid/Far`（父材质 `M_DY_MountainFlat`，参数 `Glow`(标量) + `Tint`(向量)）。
- 原值偏亮，夜里读成「白蓝色金字塔」。`C:/dy_build/pass425_mtnset.py` 统一压暗（保留远/中/近三档层次）：
  - Near：`Tint` (0.075,0.095,0.115) → **(0.050,0.058,0.078)**，`Glow` 0.02
  - Mid：(0.105,0.130,0.160) → **(0.040,0.048,0.068)**，`Glow` 0.05
  - Far：(0.150,0.185,0.220) → **(0.034,0.042,0.062)**，`Glow` 0.08
- 结果见 `C:/dy_build/shots/mtn_dark.png` 与真机 `s137-w01.png`：山体退回夜空里的暗剪影，不再抢主体。

### 17.5 打包与回归台账
| Run | 内容 | 产物 | 文件/字节 | SourceMapSHA256 |
| --- | --- | --- | --- | --- |
| Run133 | 格窗外移 + 纸面 | PASS | 31 / 754,078,703 | `DA1C23F5…945164D1` |
| Run134 | 格窗纸自发光 | PASS | 31 / 754,078,703 | `DA1C23F5…945164D1`（只改 MI） |
| Run135 | 树干竖直 + 收尖网格 | PASS | 31 / 754,103,500 | 变化 |
| Run136 | 树冠重建（回归） | PASS | 31 / 754,074,828 | `EDF6C52F…E401AE98` |
| **Run137** | **树冠回滚 + 远山调暗** | **PASS** | **31 / 754,095,308** | `EDF6C52F…E401AE98`（关卡未改，只改资产内容） |

- Run137 回归：`AutomationV60.log` **176 tests / 0 fail**（`Result={Success}` 176）；`verify_sfx -Attempt Run137` 9 cue（cue1 16.2/32.2/47.6/63.0、cue2 24.2/39.6/55.0/70.5、cue0 76.5）；`verify_replay -Attempt Run137` `REPLAY_NEW_LINES=25` + `REACHED_PHASE4=True`；真机帧 `Saved/Audit-2026-10-20-V21/s137-w01..w05.png`（`PROBE 98`）。
- `NativeExeSHA256=C47EB57726E7DE069C2730ED97A01AF312E579EBBF5BCEC89926AC85E53E2867` 自 Run124 起未变。
- `Scripts/Start-FormalShipping.ps1` 指向 Run137（4,932 B，UTF-8 BOM），`-DryRun` → `PASS-PREFLIGHT-ONLY` / `ArtifactCount=31` / `ArtifactBytes=754095308.0`。

### 17.6 启动器 BOM 的坑
- 用 Node 写回启动器时若原文件已带 BOM，`fs.readFileSync(p,'utf8')` 会把它保留成 `﻿` 字符，再拼一个就写出**双 BOM**；PowerShell 只吃掉第一个，剩下的变成 `?param` → `The term '?param' is not recognized`，而且 `-DryRun` 失效、**真的把游戏启动了**。
- 正确写法：先 `t.replace(/^﻿+/, '')` 剥掉所有 BOM，再写 `'﻿' + t`；写完核对 `bytes === 4932` 且首三字节是 `ef bb bf`。


## 18. Run138：门口石灯「纸罩暖光化」与去冗余宝顶（2026-10-22）

### 18.1 问题定位（一张近景图解决）
- 用 55° 近景机位（(-3400,-330,330) → (-2700,-560,300)）拍单根灯柱，顶部结构是：柱身（`DYTheater_PathLantern_i_j`，Cube 34×34×250/286，`MI_DY_RockTex`）→ 木托（`ART_A5_LanternBase_i_j`，`MI_DY_FramePost_Wood`，z=270）→ 发光核心（`DYTheater_PathLamp_i_j`，Sphere，`MI_DY_PathLantern`，z=284）→ 灯纸（`ART_A5_LanternPaper_i_j`，Cube，`MI_DY_LanternPaper`，z=287）→ 灯源（`DYTheater_PathLight_i_j`，z=300）→ 木顶（`ART_A5_LanternRoof_i_j`，z=305）→ 铜帽（`DYExt32_Cap_i_j`，`MI_DY_AgedBrass`，z=306）→ 铜宝顶（`ART_A5_LanternFinial_i_j`，z=311.5）→ **`DYExt32_Finial_i_j`（Sphere，`MI_DY_PathLantern`，z=324）**。
- 最后那颗 z=324 的**发光球体**高过木顶/铜帽/宝顶 13–18 cm，悬在灯顶之上——近景读作「灯帽上飘着一颗火苗」，远景读作「黑柱 + 白帽 + 白点」，是门口灯柱最明显的假。
- 同时灯纸 `MI_DY_LanternPaper` 的 `Tint` 是 (1.0,0.95,0.88)——**接近纯白**，`Glow` 3.06，所以整条灯径在夜景里是一排**白灰色**纸罩，与全台暖光（(1.0,0.72,0.42) 系）不统一。

### 18.2 处理
- `C:/dy_build/pass434_lampfix.py`：删除全部 **16 件 `DYExt32_Finial_*`**（8 对灯柱各一件）；actor 1809 → **1793**。
- `C:/dy_build/pass435_lampwarm.py`：`MI_DY_LanternPaper` 的 `Tint` (1.0,0.95,0.88) → **(1.0,0.70,0.40)**、`Glow` 3.06 → **3.9**；`MI_DY_PathLantern` 的 `Glow` (1.0,0.55,0.2) → (1.15,0.577,0.19)（内部核心略提亮偏暖）。
- `MI_DY_PlasterTex` 的 `Roughness` 0.9 → 0.95（墙面更哑光）；`DYExt30_Uplight_00..04` 试过 3600 → 2600 → 3200，最终**回到 3600**（编辑器视口与 Shipping 曝光不同，不能只靠编辑器判断）。

### 18.3 结果
- 近景 `C:/dy_build/shots/lamp_warm.png`：灯纸变成**暖琥珀色竖棱罩**，顶上是平整木顶 + 铜帽 + 铜宝顶，不再有悬空火苗。
- 真机 `Saved/Audit-2026-10-20-V21/s138-w02.png`：整条灯径读成**一排暖灯**，与门脸、匾额、灯笼的光色统一；对比 `s137-w02.png` 明显不再是「黑柱白帽」。
- 打包 `-Attempt Run138`：`PASS-BUILD-COOK-STAGE-ARCHIVE`、`UATExit=0`、31 文件 / **754,095,308** B、`SourceMapSHA256=0C86EB7F2AAD1A0B6E9EF9100ECE6EA75DBAFEF7C2AEA3D8DB8CC5D36DDDE27B`（关卡已改：删 16 件）、`NativeExeSHA256=C47EB577…E53E2867`（未变）。
- 回归：`AutomationV61.log` **176 tests / 0 fail**；`verify_sfx -Attempt Run138` 9 cue（cue1 16.3/32.4/48.1/63.5、cue2 24.4/40.0/55.5/71.2、cue0 77.2）；`verify_replay -Attempt Run138` `REPLAY_NEW_LINES=25` + `REACHED_PHASE4=True`；真机帧 `s138-w01..w05.png`（`PROBE 98`）。

### 18.4 教训
- **灯柱/灯笼这类「成套小构件」必须用近景机位单独看**：远景只能看出「黑柱白帽」，看不出顶上多了一颗悬空发光球；一颗 z 偏移 13 cm 的球在整幅画面里就是一整片错误的高光。
- 发光材质要跟场景光色**同温**：白纸罩配暖光 = 一排冷白块；`Tint` 改成暖琥珀、`Glow` 提到 3.9 之后，纸罩自己就成了光源。
- 编辑器视口的曝光与 Shipping（`M2_PostProcess_ExposureLock`，AEM_MANUAL，bias 3.5）不同，**亮暗结论只能来自真机帧**，编辑器图只用于判断结构与材质。


## 19. Run139：门口台基去「绿霉」改灰石（2026-10-22）

### 19.1 问题
- 真机 `s138-w02.png` 裁切（`C:/dy_build/crop_base138.png`）显示门脸底部台基是一条**深绿色、发霉混凝土质感**的横带，夹在暖色木地槛与灰泥墙之间，颜色与全台暖调不协调。
- 普查脚本 `C:/dy_build/pass436_plinth.py`（写 `C:/dy_build/pass436.json`）列出 `x∈(-2300,-1700)` 且 `z<260` 的全部 actor，确认这条绿带就是三件 **Cube + `MI_DY_RockTex`** 的台基：`ART_A3_RearPlinth_L`、`ART_A3_RearPlinth_R`、`ART_EXT_RearBase`（另外 `DYTheater_GateStep` 用 `MI_DY_M03_FrameWood`，正常）。
- 关键约束：**`MI_DY_RockTex` 同时被 49 块山石使用**（`SM_DY_Rock_A..D` 等），不能直接改它，否则整片山石一起变。

### 19.2 处理（三次迭代）
1. `C:/dy_build/pass437_plinthmi.py`：以 `MI_DY_RockTex` 的父材质 `M_DY_RockTex` 为父新建 **`MI_DY_PlinthStone`**（`Tint` (0.62,0.60,0.55)、`Roughness` 0.95、`Specular` 0.05），赋给三件台基并保存关卡 —— 近景 `C:/dy_build/shots/plinth.png` 里绿味减轻，但整体偏暗。
2. `C:/dy_build/pass438_plinth2.py`：`Tint` 提到 (0.80,0.77,0.70)、`TileU/TileV` 160 —— 图 `base139.png` 变中性深灰，仍有少量绿色苔点（岩石纹理自带的苔色）。
3. 又试过 `C:/dy_build/pass439_plinthtex.py`：改用 `M_DY_GroundTex` + `T_DY_StonePathTex_BaseColor` 做世界坐标石板（`TileU/V` 110）—— 结果 `base139b.png` 台基变成**竖直条纹板**（世界 UV 在这个尺寸下把石板拉成竖条），判定失败，**回退**。
4. 最终 `C:/dy_build/pass440_plinth3.py`：回到 `MI_DY_PlinthStone`（父 `M_DY_RockTex`），`Tint` **(0.86,0.83,0.76)**、`TileU/TileV` **90**、`Roughness` 0.96 —— 图 `C:/dy_build/shots/base139c.png` 台基读成**中性暖灰石基**，绿味消失，与木地槛、灰泥墙衔接。

### 19.3 结果
- 真机 `Saved/Audit-2026-10-20-V21/s139-w02.png` 裁切 `C:/dy_build/crop_base139.png`：底部横带由「发绿霉斑混凝土」变成**深灰石基**。
- 资产新增：`/Game/DengYingShanHai/Dev/ArtPolish_20261022/Materials/MI_DY_PlinthStone`；另有 `MI_DY_PlinthTex`（石板世界坐标版本，本轮未采用，保留待用）。
- 打包 `-Attempt Run139`：`PASS-BUILD-COOK-STAGE-ARCHIVE`、`UATExit=0`、31 文件 / **754,095,567** B、`SourceMapSHA256=69B02ADB7DB3D3F3F8E850EA55A823131C7C551D9D769EA22003A6A7F09998C9`、`NativeExeSHA256=C47EB577…E53E2867`（未变）。
- 回归：`AutomationV62.log` **176 tests / 0 fail**；`verify_sfx -Attempt Run139` 9 cue（cue1 16.2/32.2/47.6/63.1、cue2 24.2/39.6/55.1/70.8、cue0 76.8）；`verify_replay -Attempt Run139` `REPLAY_NEW_LINES=25` + `REACHED_PHASE4=True`；真机帧 `s139-w01..w05.png`（`PROBE 98`）。

### 19.4 教训
- **共享材质不能就地改**：`MI_DY_RockTex` 被 49 块山石共用，任何「只改台基」的诉求都必须新开一个 MI 子实例。
- **世界坐标 UV 在大尺寸构件上会把纹理拉成条纹**：`M_DY_GroundTex` 石板用在 4–10 m 长的台基上，`Tile` 只有 110 时每块石板被拉成一根竖条，读作「木板墙」；尺寸越大 `Tile` 要越小（或干脆不用世界坐标纹理）。
- 编辑器脚本里 `def find(n)` 却被无参调用会抛 `TypeError: find() missing 1 required positional argument`，此时脚本不写 JSON → `run_py.ps1` 只会报 `RUNPY TIMEOUT`，真正原因要去 `D:/灯影山海/Saved/Logs/DengYingShanHai.log` 的 `LogPython: Error: DY_HOOK FAILED` 看。
- **一次只能跑一个 `run_py.ps1`**：脚本第 9 行会 `Stop-Process` 所有 `UnrealEditor*`，两个并发任务会互相杀死对方，表现为两个都报 `RUNPY editor exited early` 且日志时间戳不更新。


## 20. Run140：门内后墙加两幅挂屏（2026-10-22）

### 20.1 问题
- 从大厅看向后墙（`C:/dy_build/shots/rearpanel.png` 之前的机位：相机 (500,-200,340) → (-1850,-210,700)），后墙是一整片 26 m 宽的灰泥，只有 6 盏壁灯与一条红带，门洞两侧各 4 m 宽完全空白；侧墙有 4 幅挂屏，后墙却没有，读作「没做完的墙」。

### 20.2 先试错：竖向木筋（已回滚）
- `C:/dy_build/pass441_batten.py`：在 x=-1766 处加 4 根竖向木筋（Cube 20×20×1500，`MI_DY_M03_FrameWood`，z 150–1650，y=-900/-300/300/900）—— 截图 `C:/dy_build/shots/batten.png` 里读成**四根悬在天花板上的细棍**（上下都不与梁/地脚相接），比空墙更差。
- 处理：`C:/dy_build/pass442_rearbeam.py` 删除这 4 根，并试加一根通长上梁 `ART_A3_RearBeam_Top`（26.2 m 长、z=1560）—— 截图 `rearbeam.png` 里几乎被天花板吃掉，**也删掉**（同脚本内 `pass443` 删除）。

### 20.3 采用：两幅带木框的挂屏
- 模板：直接复用侧墙挂屏 `ART_HALL_Art_L_0..3` / `_R_0..3` 的构成 —— `/Engine/BasicShapes/Cube.Cube`、`MI_DY_HallFrame_Kuafu` / `_Xingtian`、scale (1.36,0.03,2.06)、z=820。
- `C:/dy_build/pass443_rearpanel.py`：在门洞两侧 `x=-1760`、`y=∓620`、z=880 各放一块「画心」（scale (0.03,1.36,2.06)，X 方向薄），共 2 件 `ART_A3_RearHangPanel_0/1` —— 截图 `rearpanel.png` 里画心**像贴上去的白纸**，没有边框。
- `C:/dy_build/pass444_rearframe.py`：在画心后 2 cm（x=-1762）各加一块更大的木框板 `ART_A3_RearHangFrame_0/1`（scale (0.02,1.46,2.22)，`MI_DY_M03_FrameWood`）→ 截图 `C:/dy_build/shots/rearpanel2.png` 读作**带木框的挂屏**，与侧墙 4 幅同款同色调。
- actor 1793 → **1797**。

### 20.4 结果
- 打包 `-Attempt Run140`：`PASS-BUILD-COOK-STAGE-ARCHIVE`、`UATExit=0`、31 文件 / **754,095,567** B、`SourceMapSHA256=97A1E87094109FBB57DF5B980227FA4240751EC3D958B2506D9933E14A9FB127`、`NativeExeSHA256=C47EB577…E53E2867`（未变）。
- 回归：`AutomationV63.log` **176 tests / 0 fail**；`verify_sfx -Attempt Run140` 9 cue（cue1 16.2/32.4/48.3/63.8、cue2 24.4/40.3/55.8/71.2、cue0 77.2）；`verify_replay -Attempt Run140` `REPLAY_NEW_LINES=25` + `REACHED_PHASE4=True`（**第一次跑被「game window is not foreground」中止，杀掉残留 Shipping 进程后重跑通过**）；真机帧 `s140-w01..w05.png`（`PROBE 98`）。

### 20.5 教训
- **夜景里细长的竖向构件（木筋、杆、绳）一律读成「悬空棍」**：它们不与上下结构相接时，人眼只看到孤立的亮线。要么做成有厚度、有收头的「块」，要么不做。
- 想填补大墙面，用**已存在的成套构件**（侧墙挂屏）复制过去最稳：体量、材质、色调天然一致；只放画心会读成「贴纸」，必须带木框板。
- `verify_replay.ps1` 会检查游戏窗口是否前台；真机帧/自动化跑完后残留的 `DengYingShanHai-Win64-Shipping.exe` 会导致 `game window is not foreground`，先杀进程再跑即可。


## 21. Run141：檐口封板 + 檐木改木纹（2026-10-22）

### 21.1 问题（一次低机位仰拍暴露的）
- 用「远机位仰拍屋顶」的机位（相机 (-4600,-210,1500) → 目标 (-1900,-210,1750)，FOV 50）出图 `C:/dy_build/shots/eave.png`，看到两个硬伤：
  1. 屋顶檐口与墙体之间有一道 **1.5 m 宽、贯穿全宽的亮蓝天空缝**：墙头 `DYTheater_RearWall_Head` 顶面在 z=1900，檐板 `DYExt30_Eave_00` 底面在 z≈1929，中间 29 cm 没有任何构件封住；
  2. 檐口三片 `DYExt30_Eave_00/01/02` 与两端翘角 `DYExt30_EaveTip_0/1` 的材质是 **`MI_DY_RockTex`（石头）**，而整座建筑其余部分是木构，屋顶用石头纹理与结构不符。

### 21.2 处理
- `C:/dy_build/pass447_eave.py`：把 5 件檐木（3 片檐板 + 2 个翘角）的材质换成 `MI_DY_M03_FrameWood`（木纹）。
- `C:/dy_build/pass450_fascia.py`：新增两件封檐板
  - `ART_A6_EaveFascia_Front`：Cube (-1846,-210,1920)、scale (0.30,28.6,0.55) → 约 30 cm 厚 × 28.6 m 宽 × 55 cm 高，正面盖住 1892–1947 的缝隙；
  - `ART_A6_EaveFascia_In`：Cube (-1798,-210,1920)、scale (0.12,26.2,0.45)，从内侧再补一层，防止从室内抬头看穿。
  - 两件均 `cast_shadow=False`，避免新板在檐下投出硬边阴影。
- 出图 `C:/dy_build/shots/eave2.png`：亮蓝天缝消失，檐口变成连续深色带；檐下 3 盏 `DYExt30_RoofLamp_*` 与发光条仍在。
- actor 1797 → **1799**。

### 21.3 结果
- 打包 `-Attempt Run141`：`PASS-BUILD-COOK-STAGE-ARCHIVE`、`UATExit=0`、31 文件 / **754,095,567** B、`SourceMapSHA256=B4E8D883C40A3508FB7D813DD6278296FE2E0317F550351AC0F4EC94E77E212B`、`NativeExeSHA256=C47EB577…E53E2867`（未变）。
- 回归：`AutomationV64.log` **176 tests / 0 fail**；`verify_sfx -Attempt Run141` 9 cue（cue1 16.4/32.6/48.1/63.8、cue2 24.6/40.1/55.8/71.4、cue0 77.4）；`verify_replay -Attempt Run141` `REPLAY_NEW_LINES=25` + `REACHED_PHASE4=True`；真机帧 `s141-w01..w05.png`（`PROBE 98`）。

### 21.4 教训
- **仰拍机位是发现「天空穿缝」的唯一办法**：从玩家平视机位完全看不到那道 29 cm 的缝，只有把相机压到 1500 cm 高、朝屋顶仰拍才会暴露。
- 场景里「结构相同、材质不同」的错误比几何错误更刺眼：檐木用石头纹理，一旦把相机抬上去就非常明显；同类问题可以批量用 `get_materials` 普查（本轮就是普查 x∈(-1950,-1650)、z>1050 的 49 个 actor 才发现的）。
- `set_actor_location` 在 UE 5.8 Python 里必须传 `(loc, sweep, teleport)` 三个参数，只传一个会报 `set_actor_location() required argument 'sweep' (pos 2) not found`，脚本不写 JSON → `RUNPY TIMEOUT`。


## 22. Run142：门脸壁灯补实体（光斑终于有出处）（2026-10-22）

### 22.1 问题
- 从任何机位看门脸，墙面上都有两团很大的暖光斑（左右各一团，z≈1100），但**光斑位置没有任何灯具**。这是「有光无灯」的典型违和：玩家会读到「墙在自己发光」。
- 用 `C:/dy_build/pass454_lights.py` 普查全部灯光（输出 `C:/dy_build/pass454.json`，58 条），定位到 6 盏「只有光、没有实体」的补光灯：
  - `ART_LGT_WallFill_00..03`：(-1880, -1030/-700/330/660, 1120)，380 cd / 1000 cm；
  - `DYExt16_FacadeLamp_L/R`：(-1885, -1180/700, 780)，480 / 380 cd / 1100 cm。
- 这 6 盏灯都在墙外 45–60 cm 处，正对墙面打光，所以墙面出现亮环；而室内那 6 盏壁灯（`ART_EXT_WallLamp_00..05`，x=-1762）有实体灯罩，问题只出在室外侧。

### 22.2 处理
- `C:/dy_build/pass455_facadelamp.py`：以现有 `ART_EXT_WallLamp_00` 为模板（网格 `SM_DY_LanternFamily_Unit100` + 其全部材质、朝向），在每盏补光灯前方 47 cm 处（即 `灯.x + 47`）复制一盏实体壁灯：
  - `ART_EXT_FacadeWallLamp_00..05`，scale 0.72，`cast_shadow=False`，STATIC，跟随各自灯光的位置（含 z 780 那一对）。
  - 这样灯罩正好落在光斑中心，光从灯前方 47 cm 打过来，灯罩正面被照亮，墙面形成围绕灯罩的柔和光晕。
- actor 1799 → **1805**。
- 编辑器验证图 `C:/dy_build/shots/facade_lamp.png`（相机 (-5600,-210,300) → (-1850,-210,1000)，FOV 46）：门脸左右各两盏上灯 + 各一盏下灯，光斑全部有灯罩承接。

### 22.3 结果
- 打包 `-Attempt Run142`：`PASS-BUILD-COOK-STAGE-ARCHIVE`、`UATExit=0`、31 文件 / **754,095,567** B、`SourceMapSHA256=7F26FCF6B1E5C0AAC92E3E304E2A1BA6D55691815FDDC8CE76650A3EAC308173`、`NativeExeSHA256=C47EB577…E53E2867`（未变）。
- 回归：`AutomationV65.log` **176 tests / 0 fail**；`verify_sfx -Attempt Run142` 9 cue（cue1 16.3/32.4/48.2/64.1、cue2 24.4/40.2/56.1/71.6、cue0 77.6）；`verify_replay` `REPLAY_NEW_LINES=25` + `REACHED_PHASE4=True`；真机帧 `s142-w01..w05.png`（`PROBE 98`）。真机 `s142-w02.png` 与 `s141-w02.png` 对比：墙面从「凭空两团光」变成「两对挂牌壁灯 + 下方一对」。

### 22.4 教训
- **夜景里任何亮斑都必须有实体灯具承接**，否则读成「墙在自发光」。排查顺序：先普查灯光（位置/强度/半径），再把灯具实体复制到光斑中心；光源与灯罩的相对位置沿用已有成套灯具（本例 47 cm 正面距离），不要自己发明。
- `verify_sfx.ps1` 在 bash 里不能写 `*> file`（会被 bash 当成参数传给 `-Seconds`，报 Cannot convert "%SystemDrive%" to System.Int32）；正确写法是 `> file 2>&1`。
- `register_slate_post_tick_callback` 的回调**必须带一个参数**（delta seconds）：`def tick(dt)`；写成 `def tick()` 会每帧报 TypeError: tick() takes 0 positional arguments but 1 was given，脚本永远不写 JSON → `RUNPY TIMEOUT`。
- 截图脚本里 `json.dump` 必须放在「截图文件已存在」之后写，不能放在注册回调之后同步写：`run_py.ps1` 一看到 JSON 就立刻杀编辑器，图会丢。


## 23. Run143：入口石路石材试验（判负，已回退）（2026-10-22）

### 23.1 动机
- `s142-w02.png` 里入口石路是全画面最「占位」的元素：石板尺寸过于均匀，读成现代铺砖而不是老戏台前的旧石板路。目标是把石板改成**大小交错**的自然排布。

### 23.2 试验
- `C:/dy_build/gen_stone_v4.py` 生成 2048² 交错石板（行高 140–260 px、宽 190–430 px、深色勾缝 46、每块独立色阶 108–132、圆角倒边、细颗粒噪点、低频污渍斑），输出 `C:/dy_build/tex/T_DY_StonePathTex_BaseColor_v4.png`。
- `C:/dy_build/pass457_stone4.py` 以 `replace_existing` 覆盖 `T_DY_StonePathTex_BaseColor`，机位 (-6900,-210,180) → (-1900,-210,700) 出图 `C:/dy_build/shots/path_v4.png`。
- 判定：**比原版差**。新石板更亮、更暖，在夜景里反而抢走了门脸灯光的视觉重心；远看是一片发亮的砖墙式铺装，与「旧戏台前踏得发暗的石板」完全相反。
- 追加尝试 `C:/dy_build/pass458_tile.py`：把 `TileU/TileV` 250 → 520、`Tint` 压到 (0.72,0.705,0.675)，想靠放大石板+压暗救回来；出图 `C:/dy_build/shots/path_v4b.png` 石板尺寸没有明显变大（世界 UV 缩放的换算不是简单倍数），亮度仍然偏高 → 继续判负。

### 23.3 回退
- `C:/dy_build/pass459_revert.py`：重新导入原 `C:/dy_build/T_DY_StonePathTex_BaseColor_v3.png` 覆盖同名资产，并把 `MI_DY_StonePathTex` 的显式参数钉死为 `TileU/TileV=250`、`Tint=(0.80,0.80,0.78)`、`Roughness=0.94`、`Specular=0.02`（此前这些值只有部分有文档记录，本次写入让材质状态可复现）。
- 出图 `C:/dy_build/shots/path_rev.png`：石路回到 Run142 的暗灰石板外观。

### 23.4 结果
- 打包 `-Attempt Run143`：`PASS-BUILD-COOK-STAGE-ARCHIVE`、`UATExit=0`、31 文件 / **754,095,567** B、`SourceMapSHA256=7F26FCF6B1E5C0AAC92E3E304E2A1BA6D55691815FDDC8CE76650A3EAC308173`（与 Run142 同，关卡未改）、`NativeExeSHA256=C47EB577…E53E2867`。
- 注意：`.pak/.ucas/.utoc` 的 md5 与 Run142 **不同**（纹理重导入换了内部 GUID/序列化顺序），所以 Run143 仍按新包处理并跑完整回归。
- 回归：`AutomationV66.log` **176 tests / 0 fail**；`verify_sfx -Attempt Run143` 9 cue（cue1 15.9/32.0/47.4/63.3、cue2 24.0/39.4/55.3/70.7、cue0 76.7）；`verify_replay` `REPLAY_NEW_LINES=25` + `REACHED_PHASE4=True`；真机帧 `s143-w01..w05.png`（`PROBE 96`）。

### 23.5 教训
- **「更精细」不等于「更好」**：石板做成大小交错、颜色更丰富，在近景确实更像真石材，但夜景里亮度上去了，就把视觉重心从门脸抢走。远处的路面应当**偏暗、偏灰、低对比**。
- 程序化纹理生成后必须先放到**实际灯光环境**里看，不能只看贴图本身；贴图预览亮度和最终渲染亮度可以差一倍。
- `unreal.AssetImportTask` 在 UE 5.8.3 这个 Python 绑定里没有 `compression_settings` / `srgb` / `lod_group` 属性，赋值会直接抛 `AttributeError`；sRGB 与 LODGroup 必须在导入后对 Texture 对象用 `set_editor_property` 设置。
