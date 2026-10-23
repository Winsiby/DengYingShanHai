# 四幕换偶接入记录（2026-10-22）

本记录说明把精卫、刑天、烛龙三具影偶接入正式四幕的改动、证据和未完成项。正式地图 `L_DY_Main` 的关卡文件未改，谜题判定链未改。

## 1. 改动

| 文件 | 改动 |
|---|---|
| `Source/DengYingShanHai/Public/Interaction/DYPuppetCastTypes.h` | 新增 `FDYPuppetFigureEntry`（Label、SkeletalMesh、PoseAnimations、bHideStaff、相对位移/旋转/缩放）与 `UDYPuppetCastData`（Figures 数组） |
| `Source/DengYingShanHai/Public/Interaction/DYPuppetActor.h` | 新增 `ApplyChapterFigure(int32, bool)`、`ApplyPoseAnimation(FName)`、`GetActiveFigureIndex()`；新增 `CastMesh` 显示组件与 `FigureCast` 软引用 |
| `Source/DengYingShanHai/Private/Interaction/DYPuppetActor.cpp` | 章节外观切换：有烘焙姿态片段的角色用独立 `DYChapterCastMesh` 组件显示，绕开夸父 Blueprint 的 AnimBP；无片段的夸父继续用原 `KuafuMesh` |
| `Source/DengYingShanHai/Private/Puzzles/DYPuzzleDirector.cpp` | `StartCurrentPuzzle` 内在 `LastEvaluationTimeSeconds` 赋值后调用 `PuppetActor->ApplyChapterFigure(CurrentChapterIndex, true)`；纯表现，不参与判定 |

设计约束：判定仍由光源、皮影位置/朝向、姿态 ID 与持续时间决定，四幕共用同一套 pose ID（`P02_StrideBack/Mid/Reach`），换偶只替换可见网格与姿态片段。

## 2. 资产

- 生产命名空间：`/Game/DengYingShanHai/Puppets`（Meshes / Animations / Textures / Materials）
- 数据资产：`/Game/DengYingShanHai/Puppets/DA_DYPuppetCast`，四条目：夸父、精卫、刑天、烛龙
- 姿态片段：精卫 Rest/Flight/Reach，刑天 Rest/Guard/Reach，烛龙 Rest/Day/Night/Reach，各 1 秒固定姿态
- 条目变换与夸父原生一致：位移 (0, -42.44, -104.57)、yaw 180、缩放 0.8，保证同一台面尺度

## 3. 验证

| 项 | 结果 | 证据 |
|---|---|---|
| 生产导入 | 217 项断言通过，四条目 | `Saved/Audit-2026-10-22-FourAct/cast-import.json` |
| 编辑器内换偶 | 精卫正立、单份、幕上有完整翼羽镂空阴影 | `Op-Close3.png` |
| 四幕场景截图 | 第二幕精卫、第四幕烛龙正立可读 | `Saved/Audit-2026-10-22-FourAct/Act2-Audience.png`、`Act4-Audience.png` |
| 自动化回归 | 176 项，0 失败，退出码 0 | `Saved/Logs/AutomationV67.log` |
| Development 打包 | BUILD SUCCESSFUL，产物 1.1 GB | `Builds/FormalMain-Development-20261022-RunD1/Windows` |
| 打包程序启动 | 窗口出现，进入主菜单、演出篇章面板、第二幕开场 | `Saved/Audit-2026-10-22-FourAct/d5-enter.png`、`d10-acts.png`、`d11-act2.png` |

启动时 Windows 防火墙会弹出"是否允许公用网络和专用网络访问此应用"，该弹窗会抢走焦点并遮住窗口；本次用 `C:\dy_build\close_dialog.ps1`（向 `Shell_SystemDialogProxy` 发 WM_CLOSE）关闭后用 PrintWindow 抓图。焦点被系统对话框与前台策略限制，脚本无法稳定驱动 WASD 行走，因此四幕完整通关仍需人工操作。

## 4. 未完成

- 四幕完整通关（含三次谜题解谜与结尾）未由本轮跑完，需要可交互的实机操作。
- Shipping 包未用本批资产重打；当前公开入口仍指向 Run143。
- 十个姿态片段是 1 秒固定片段，不是表演动画。
- 夸父在编辑器非 PIE 状态下显示残缺（依赖其 AnimBP），游戏内正常；不能据编辑器截图判其缺陷。


## 5. 舞台显示比例（2026-10-23 补）

观众机位对比 0.8 与 1.1 两种显示比例后，精卫、刑天、烛龙统一改为 1.1，夸父保持 0.8。依据是同一机位同角色的成对截图：

- 烛龙：`Saved/Audit-2026-10-22-FourAct/Scale-Small-Act4.png` → `Scale-Big-Act4.png`
- 精卫：`Scale-Small-Act2.png` → `Scale-Big-Act2.png`
- 刑天：`Scale-Small-Act3.png` → `Scale-Big-Act3.png`

放大后三具影偶在幕面上的高度占比明显提升，翼羽、鳞身与盾面细节在 1600 像素画面里可读；判定位、交互盒与灯偶坐标未改。

写入结果见 `Saved/Audit-2026-10-22-FourAct/cast-scale-final.json`：`requested` 为 0.8/1.1/1.1/1.1，`readback` 读回一致，`saved: true`。

改完后重打 Development 包：`BuildCookRun` 87.55 s，`BUILD SUCCESSFUL`，产物 `Builds/FormalMain-Development-20261023-RunD2/Windows`（1.1 GB）。RunD2 启动到主菜单的实际截图：`Saved/Audit-2026-10-22-FourAct/d13-runD2-menu.png`。


## 6. 幕框题签按幕切换（2026-10-23）

现状问题：幕框上的题签是 `ART_ZhuRiTitleGlyph`（Plane，位置 895,0,880，缩放 3.2/0.8/1.0，yaw 90、roll 90，世界尺寸约 320×80 cm），材质 `M_DY_TitleGlyph` 采样 32×32 的 `T_DY_ZhuRiTitle`，乘以常量 60 输出到自发光，BLEND_MASKED + MSM_UNLIT + 双面。四幕共用这一张，所以第二至四幕的匾额仍写「逐日」。

做法（只改表现，不动判定）：

| 资产 | 作用 |
|---|---|
| `M_DY_TitleGlyph_Master` | 新的题签母材质：TextureSampleParameter2D `TitleGlyph` + ScalarParameter `Gain`（默认 60），自发光 + 不透明遮罩，参数与旧材质同构 |
| `MI_DY_TitleGlyph_Act1` | 沿用原纹理 `T_DY_ZhuRiTitle`，Gain 60，第一幕外观与旧版一致 |
| `MI_DY_TitleGlyph_Act2/3/4` | 新纹理，Gain 50，与第一幕的亮度/色相逐像素比对后收敛 |
| `T_DY_TitleGlyph_Act2/3/4` | 2048×512，华文楷体，金色 (243,205,150)，字形掩膜做轻度膨胀，内容为「填海」「舞干戚」「昼夜」 |

代码：`ADYPuzzleDirector::ApplyChapterTitlePlaque(int32 ChapterIndex)`（BlueprintCallable）按 `ART_ZhuRiTitleGlyph` 标签找到匾额，把 0 号材质槽换成对应幕的实例；可选 `ChapterTitleMaterials` 数组覆盖，留空时回落到四条固定路径。调用点只有一处：`StartCurrentPuzzle` 里 `ApplyChapterFigure` 之后，章节切换的两条路径（`StartCampaignChapter` / `AdvanceCampaignChapter`）都会经过它。

验证：

- `Saved/Audit-2026-10-22-FourAct/title-swap-calls.json`：依次调用 0/1/2/3/1/0，材质分别落到 Act1/Act2/Act3/Act4/Act2/Act1，6/6 通过。
- 同机位成片 `Title3-Act1..4.png`（观众机位 -980,-80,250 → 760,-80,250，FOV 62），匾额依次显示「逐日 / 填海 / 舞干戚 / 昼夜」；亮度与色相对比：第一幕 p95 (187,167,112)，二至四幕 p95 (187,164,119)。
- 自动化回归 176 项 0 失败（`Saved/Logs/AutomationV68.log`，EXIT 0）。
- Development 包 `Builds/FormalMain-Development-20261023-RunD5`，52 文件 / 1,112,916,744 B，exe SHA256 `74ecb55826e81eef9a51d7b1e8d5ab09071355697a08e9d75fc818f026bbc532`，启动到主菜单与设置面板实拍 `d14-runD5-menu.png`、`d16-runD5-act2.png`。


打包记录：RunD1（22:37）为换偶首版，RunD2（00:06）为比例 1.1 版，RunD3/RunD4（08:45 / 08:48）是题签改造过程中的中间包，**RunD5（08:58）是当前最新 Development 包**，其余可删。四幕完整通关仍需人工键鼠操作：防火墙弹窗会抢焦点，脚本能到主菜单与设置/演出篇章面板，长距离行走不稳定。

- 四幕同框成片：`Saved/Audit-2026-10-22-FourAct/Final-Act1..4.png`，每帧由 `ApplyChapterFigure` 与 `ApplyChapterTitlePlaque` 一起驱动，幕上影偶与匾额题名一致（第一幕夸父—逐日、第二幕精卫—填海、第三幕刑天—舞干戚、第四幕烛龙—昼夜）；记录 `final-acts.json`。

## 7. 影偶模型 Run4：剪影、头身比例、操杆（2026-10-23）

美术检查剩下三条（刑天正面剪影、烛龙头身比例、精卫翼杆）在 Run4 一次解决。判定方式是距离可读性：先用 `Assets/Sources/DengYingArt/ThreePuppets-20261022/pose_probe.py` 等探针只加载分片顶点，渲染 420 px 与 180 px 黑轮廓，确认改法在远景仍能读出角色，才动源模型。

| 条目 | 源改动 | UE 表现 |
| --- | --- | --- |
| 刑天剪影 | `xingtian_spec.json` 三个姿态统一叠加 `Axe:-35, Arm_L_Upper:-14, Arm_R_Upper:-10, Leg_L_Upper:4, Leg_R_Upper:-4` | 斧柄竖起形成垂直重音，双臂收拢，正面读作站立持械 |
| 烛龙头身 | `zhulong_spec.json` 增 `part_scale=[{bones:['Head'],anchor:'Neck',factor:1.18}]`；`build_blender.py` 按锚点缩放顶点并同步子树骨骼 pivot | 身高 213.92 cm，头部占比约 15%，鳞身盘绕层次清楚 |
| 精卫翼杆 | 杆 spec 增 `spar_px`：翼杆改为藏在翼皮后的短支杆，主杆收向 `min_z-6` 的握把并加黄铜握把球 | 幕面只剩一根主杆，不再有跨翼间空隙的细天线 |

Run4 计数：精卫 16,024 面 / 17 骨 / 99 镂空，刑天 8,168 面 / 14 骨 / 33 镂空，烛龙 8,028 面 / 8 骨 / 32 镂空，三份 `MODEL_VERIFICATION.json` 均为 `PASS-MODEL-SOURCE-FBX-ROUNDTRIP`；Run2、Run3 保留回退。

导入与姿态：

- 生产库 `/Game/DengYingShanHai/Puppets`（Meshes / Animations / Textures / Materials）与 `DA_DYPuppetCast` 四条 entry 全部重写；`Saved/Audit-2026-10-22-FourAct/cast-import.json` ok=true、checks=236、errors=[]。
- 冷验证 `verify_run4.py` → `run4-verify.json`：ok=true、60 项断言全过（四条 entry 的 loc/yaw/scale、四个 pose 片段各 1 s 且位移不同、烛龙 Day 眼片 scale 0.0001 / Night 1.0、BaseColor 纹理 never_stream、10 个材质实例保留 SkeletalMesh usage）。

朝向与比例定稿：四条 entry 统一 `loc=(0,-42.44,-104.57)`、`yaw=180`、夸父 0.8 / 其余 1.1。yaw 180 的依据是概念图朝向（刑天斧在画面左、盾在右；烛龙侧脸朝左），以及 `Final-Y180-*` 与 `Final-Y0-*` 两组同机位成片的对照（`YawCompare-Zoom.png`）。

三条踩坑记录：

1. `import_cast_ue.py` 每次导入都会重建 `DA_DYPuppetCast`，旧版写死 `(0.0, 0.0, 0.0)` 旋转与 0.8 缩放，把已校准的 yaw/scale 冲掉。现在脚本内固定 `XF = dict(loc=(0,-42.44,-104.57), rot=(0,0,180), scale=(0.8,…), cast_scale=(1.1,…))`，三条 `entry(...)` 共用。
2. UE Python 的 `unreal.Rotator(a, b, c)` 位置参数顺序是 (roll, pitch, yaw)。写 `Rotator(0.0, 180.0, 0.0)` 得到的是 pitch 180（整体倒立），正确写法是 `unreal.Rotator(0.0, 0.0, 180.0)`。
3. 截图脚本若以文件存在且大于 20 KB 作为完成判据，必须先 `rm -f` 旧图，否则会立刻判定完成而不重拍。

## 8. 打包与 cook 范围（2026-10-23）

RunD6 的 pak/ucas 与 RunD5 逐字节相同（ucas 277,847,600 B），说明这批资产根本没进包：`DA_DYPuppetCast` 与题签材质实例都是 C++ 按固定路径 `LoadObject` 读取的，cooker 不会从任何地图里发现它们，`Config/DefaultGame.ini` 里也没有对应目录。

修法是在 `[/Script/UnrealEd.ProjectPackagingSettings]` 里显式登记两个目录：

```ini
+DirectoriesToAlwaysCook=(Path="/Game/DengYingShanHai/Puppets")
+DirectoriesToAlwaysCook=(Path="/Game/DengYingShanHai/Stage/ArtMainline/Materials")
```

重打后 cook 包数 720 → 767，ucas 277,847,600 → 380,036,496 B，`DengYingShanHai-Windows.utoc` 中可见 `SK_DY_Jingwei`、`SK_DY_Xingtian`、`SK_DY_Zhulong`、`DA_DYPuppetCast`、`MI_DY_TitleGlyph_Act2`、`T_DY_Jingwei_BaseColor`。产物 `Builds/FormalMain-Development-20261023-RunD7`，49 文件 / 1,215,052,540 B。

这条是四幕换偶能不能真的出现在玩家面前的决定项：在此之前打出的 Development 包在运行时 `LoadObject` 会失败，四幕角色实际只看得到夸父。

## 9. 实机验证：RunD7 包内四幕换偶与题签（2026-10-23）

RunD7 是用修好 cook 范围的配置重打的 Development 包。在没有编辑器、没有调试控制台的纯运行时环境里，从主菜单「演出篇章」直接点选各幕进入，用真实鼠标点击（`mouse_event`）驱动，逐幕截图：

| 幕 | 匾额 | 影偶 | 截图 |
| --- | --- | --- | --- |
| 第二幕 | 填海 | 精卫（双翼展开） | `Saved/Audit-2026-10-22-FourAct/r7-act2.png` |
| 第三幕 | 舞干戚 | 刑天（盾 + 斧） | `Saved/Audit-2026-10-22-FourAct/r7-act3.png` |
| 第四幕 | 昼夜 | 烛龙（盘身侧脸） | `Saved/Audit-2026-10-22-FourAct/r7-act4.png` |

对应的 4 倍局部放大图 `r7-act{2,3,4}-zoom.png` 与三联对比图 `Packaged-Acts234.png` 把匾额题名与幕上影偶放在同一帧内，可以直接读出「题名与角色一致」。证据清单 `Saved/Audit-2026-10-22-FourAct/packaged-acts-verify.json` 记录每张图的字节数、尺寸、SHA256。

这一步的意义：第 8 节修的是 cook 范围，但「包里到底跑不跑得起来」必须在真机上验证。实拍结果同时证明了三件事——

1. `DA_DYPuppetCast` 在运行时按固定路径 `LoadObject` 能成功（否则会静默回落到夸父网格）；
2. 章节切换会同时驱动影偶与题签（`ApplyChapterFigure` + `ApplyChapterTitlePlaque` 都由 `StartCurrentPuzzle` 触发）；
3. 三具影偶的骨骼网格、动画片段、材质在打包后都没有丢（没有 T-pose、没有丢材质变紫）。

### 实机抓图的三条硬经验

1. **截图坐标与屏幕坐标是 1:1 的，别按 DPI 换算。** 窗口 `GetWindowRect` = `45,-22,1661,1017`，`GetClientRect` = `1600x1000`，DPI=96；`PrintWindow(PW_RENDERFULLCONTENT=2)` 出来的图正好 1616x1039，等于窗口尺寸。屏幕坐标 = 窗口左上角 + 图内坐标。之前按 `2402x1548` 的 DPI 虚拟边界换算，点到了窗口外，表现为「点了没反应」。
2. **packaged 窗口必须先拿到前台，`SendInput`/`mouse_event` 才生效。** 自动化进程本身不是前台时 `SetForegroundWindow` 会被系统拒绝（本次反复出现 `FG=False`）。可用组合：先 `keybd_event(VK_MENU)` 按一下放开以释放前台锁，再 `AttachThreadInput` 到当前前台线程，随后 `ShowWindow(SW_RESTORE)` + `BringWindowToTop` + `SetActiveWindow` + `SetForegroundWindow`，最后 `DetachThreadInput`。全程要在一个进程里做完，跨进程调用之间焦点会再被抢走。
3. **篇章列表要点两下。** 第一次点击只是选中（行变成高亮红），第二次点击才进入游戏；脚本里写成连点两次即可。另外「已演」标记会出现在已完成的幕上，这是存档进度，不是脚本状态残留。

另外记录一条环境坑：每次启动 packaged exe，Windows 防火墙都会弹一次「是否要允许网络访问」并抢走焦点（窗口类 `Shell_SystemDialogProxy`）。它不关掉的话游戏窗口永远拿不到前台；用真实鼠标点它的「取消」即可，之后 `SetForegroundWindow` 才会成功。

## 10. Shipping 包 Run144（2026-10-23）

Development 验证通过后，用同一套资产与配置打了一版 Shipping，放在新的目录，`Builds/FormalMain-Shipping-20261023-Run143`（公开入口）原样未动。

| 项 | Run143（旧公开包） | Run144（本次） |
| --- | --- | --- |
| 文件数 | 31 | 31 |
| 总字节 | 754,095,567 | 856,338,919 |
| ucas | — | 380,036,496 B |
| utoc | — | 289,673 B |
| exe | — | 166,355,968 B，SHA256 `B15A3651741A2CDF70DA163C30C9D4849CA799A1FECBAF3C5F36A629C977996` |

uatoc 内可见 `SK_DY_Zhulong`、`DA_DYPuppetCast`、`MI_DY_TitleGlyph_Act3`，说明第 8 节的 cook 修复对 Shipping 同样生效。

实机验证（Shipping 配置，非 Development）：启动到主菜单 → 「演出篇章」→ 逐幕进入，第二幕拍到「填海」+精卫、第三幕拍到「舞干戚」+刑天，见 `Saved/Audit-2026-10-22-FourAct/Shipping144-Acts.png` 与 `shipping144-verify.json`、`shipping144-archive.json`。

### 打包流程里必须注意的一步

Shipping 游戏可执行文件这次的编译仍然只能在纯 ASCII 路径做（中文路径的 PCH 坑见第 7 节的经验）：

1. 把 `Source/`、`Config/`、`.uproject` 复制到 `C:\dy_compile`；
2. `Build.bat DengYingShanHai Win64 Shipping -project='C:\dy_compile\DengYingShanHai.uproject' -NoUBA -MaxParallelActions=6 -waitmutex`（本次 90 s）；
3. 把 `C:\dy_compile\Binaries\Win64\DengYingShanHai-Win64-Shipping.exe` 与同名 `.target` 拷回 `D:\灯影山海\Binaries\Win64`（旧文件先备份）；
4. 再跑 `BuildCookRun` 且**不带 `-build`**，只做 cook/stage/pak/archive，避免 UAT 在中文路径上重新编译。

公开入口 `Scripts/Start-FormalShipping.ps1` 当时仍指向 Run143；后续入场墙修复已切到 Run146，再由第 11 节切到 Run147。

## 11. 动态皮影演出接入（2026-10-23 晚）

按 `DYS_SHADOW_PUPPET_GAMEPLAY_UPGRADE_20261023.md` 把"静态影偶 + 解谜判定"升级为"解谜 → 即时关节反馈 → 整幕连续皮影演出 → 再推进"。详见 `Docs/SHADOW_PERF_20261023.md`，这里只记与影偶相关的事实。

- 动画：Blender 侧程序化生成 17 条（夸父 6 / 精卫 4 / 刑天 5 / 烛龙 4），平面内关节绕世界 X 轴四元数旋转；导入 `/Game/DengYingShanHai/Puppets/Animations/A_DY_<角色>_Perf_*`。刑天骨架没有 Head 骨，首版 spec 里写 Head 会直接报 `unknown bones`。
- 数据：`DA_DYPuppetPerformance` 四幕各 5 段（12.0 / 12.4 / 12.2 / 12.6 s）+ 1 条 1.2 s 反馈 + 每段字幕。
- 挂接：`UDYPuppetPerformanceComponent` 挂在影偶 Actor 上；DA **只通过实例上的 `PerformanceData` 显式指定**（关卡里 `M2_Puppet_P02_Controlled`）。早期写过固定路径回落，结果自动化夹具也捡到该资产、把 `OnPuzzleResolved` 延迟，8 个流程测试失败；改为显式挂接后 180 项全过。
- 时间语义：只有每章**最后一幕**解谜成功才播整幕演出并延迟发布通知，前两场只播 1.2 s 反馈；播完与空格跳过走同一收尾，因此对流程等价。
- 幕布取样（幕后机位，编辑器内）：`Saved/Audit-2026-10-23-Performance/PerfUE-Act1..4.png`，每幕 5 段 × 2 帧，影偶姿态逐段不同、题签同框。
- 打包证据：Development `RunD10` 日志连续三章进入演出（12.00 / 12.40 s 播完，第三轮 3.79 s 空格跳过）；Shipping `Run147` 为公开入口包，帧证据 `Packaged/Shipping147-Captions.png`；utoc 含 DA 与 17 条动画。
- 自动化：`AutomationV71.log` 180 Success / 0 Fail。
