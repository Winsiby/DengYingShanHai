# 正式主图夸父与 B 角标接入记录

日期：2026-10-19。负责人：用户；Codex 执行本轮实现、验证、打包和入口更新。

> 后续状态：M-01 v04 掌垫/木杖、M-03 v02 完整幕框、M-02 P03 目标影形与 M-04 A v04 枝端叶簇已在该记录之后接入，正式包与入口现为 Run5。本文保留为 B 角标/首次夸父接入记录；当前状态见 `Docs/FORMAL_M02_M04_TARGETS_CANOPY_20261019.md`。

## 玩家可见结果

正式主图 `L_DY_Main` 已使用新夸父 `BP_DYKuafuPuppet_Fitted`，第二幕身体角标使用已选定的 B 方案材质 `MI_DY_P02KuafuBodyFit`。E 交互沿用该 Blueprint 内已扩大的 `PuppetInteractionBox`（约 51 × 162 × 193 cm）。P01 仍禁用皮影控制；P02 需要灯与偶协同；P03 仍从当前杖尖接触继续成林。

## 接入前的正式图事实

- Director：`DYPuzzleDirector_1`，灯 `M2_LightRig_P02`，偶 `M2_Puppet_P02_Controlled`。
- 接入前偶为原生灰盒 `DYPuppetActor`，GuideP02 为共享材质 `MI_DY_P02BodyFit`。
- 35 个 Actor；15 Hz；三幕手动开始；`DevActTransitionSeconds=2.0`。
- 旧偶与 `BP_DYKuafuPuppet_Fitted` 的轨道中心、`WorldTravelAxis`、`TravelDistance`、`InitialNormalizedValue`、`NormalizedUnitsPerSecond`、三姿态 ID、木杖 A/B 端点逐值一致。
- 相机不在地图内单独放置，由正式第三人称 Pawn 的 Spring Arm/Camera 持有；FOV 70、臂长 360、输入映射未改。

## 最小接入

只修改正式主图，原位替换偶并改 GuideP02 材质槽 0：

- 新偶实例保持原 Actor 标签、变换和标签集合，Director 的 `PuppetActor` 指向新实例。
- 新偶的 `KuafuMesh` 使用 `SK_DY_Kuafu_Refined`，`Staff` 使用 `SM_DY_Kuafu_Staff`，灰盒 Torso/Head 隐藏且不投影。
- `PuppetInteractionBox` 直接挂在继承的 `SceneRoot` 下，QueryOnly，仅 Visibility Block，游戏中隐藏、不投影。
- GuideP02 只将材质槽 0 从 `MI_DY_P02BodyFit` 换为 `MI_DY_P02KuafuBodyFit`；B 四参数保持选定的 `SpineClothing` 值。
- 三幕 Definition、目标、进入/退出容差、保持时间、15 Hz、灯偶轨道、Stage/Forest/GroundLine 绑定、森林分支布局和 GameMode 均未改。

## 实际验证

| 项 | 结果与证据 |
|---|---|
| 冷读接入 | 35 Actor、标签集合不变；除 GuideP02 材质槽 0 外，其余非替换 Actor 合约逐项一致；旧偶路径消失，Staff A/B 逐值一致。`Saved/Audit-2026-10-19-FormalKuafu/Verify-Run1/VERIFY.json` |
| 真实 RHI 三幕 | P01 禁用皮影且命中 Box 不聚焦；P02 灯单独/偶单独均不判定成功，精确目标进入 Holding；P03 接触与林资源先于完成。`Play-Run3/PLAY.json` |
| E 区域 | 三姿态 × 3×3 共 27 点全部命中并完成 E 进入/释放；27 点原始命中均为 `PuppetInteractionBox`。 |
| 重置 | P02 Holding 后调用原 `ResetCurrentPuzzle`，仍留在第二幕，灯偶回到 0.15，保持与判定清零；再次精确目标后正常推进第三幕。 |
| 重演 | 完成后同图回到干净标题；旧 Resolved Token 失效，森林会话清空。 |
| Editor/Game 编译 | 均退出 0；仅保留既有 MSVC/引擎弃用警告。 |
| 原生回归 | 170 成功、2 警告、0 失败、0 未运行。 |
| Development 包 | UAT Cook/Stage/Pak/IoStore/Archive 退出 0；49 个打包产物（另含构建身份 JSON）、1,081,155,769 字节；UFS 含 `L_DY_Main` 与 Engine Entry。 |
| 包内启动 | 正式 CMD 实际启动、菜单清晰、日志载入 `L_DY_Main`、正常退出 0；包内进入场景截图可见新夸父与 P01 引导。 |

## 正式入口与包

- 正式启动：`D:\灯影山海\Start-ReleaseEntry.cmd`
- 实际调用：`D:\灯影山海\Scripts\Start-FormalMain.ps1`
- Development 包：`D:\灯影山海\Builds\FormalMain-Development-20261019-Run2\Windows`（当时的 B 角标包；M-01 接入后正式包已切换为 Run3）
- 启动前校验：包身份、正式地图路径、原生 EXE 哈希、主图哈希、文件数/字节数和五个 Pak/IoStore 容器。
- 不传地图覆盖，使用 `GameDefaultMap=/Game/DengYingShanHai/Maps/L_DY_Main`。
- 打包 Run1 因 PCH 内存退出 6，未生成可交付包；Game 单独编译后 Run2 以 `-skipbuild` 成功。Run1 日志原样保留。

## 清理与回退

已删除三个被正式包取代的候选启动文件：

- `P02GuideAudit-20261018\Start-P02Guide-B.cmd`
- `ReenactorFormalIntegration-20261018\Start-Main-v10.cmd`
- `ReenactorFinalIntegration-20261018\Start-ReenactorMovement-v10.cmd`

三个脚本的原字节、哈希和删除理由见 `Saved/Audit-2026-10-19-FormalKuafu/CLEANUP.json`。候选游戏包、旧正式包、Build 目录、日志和回退副本均保留。

回退主图：用 `Saved/Audit-2026-10-19-FormalKuafu/Baseline/L_DY_Main.umap` 恢复，并保留旧 `Start-ReleaseEntry.ps1` 与 `Builds/ReleaseEntry-Development-20261014-Run1`。回退前先核查后续用户/队友修改，不自动覆盖新地图。

## 边界

- 本轮没有把 B 方案头部弧线、下摆或手杖重新校准；这些仍按原设计保持独立。`GuideDiagnostic-Run1/P02_GuideOnly.png` 在诊断中隐藏玩家角色后，躯干/腿部落点与 B 角标对齐；正常第三人称画面中玩家手提灯和身体会在屏幕上形成亮斑，近距离取景时可能压低角标可读性。这是表现层风险，不改变参数判定。
- 27 点 E 测试与三幕 PIE 使用原生语义入口和直接控制值，不是实体键鼠人工通关；包内完整三幕仍建议项目负责人实际游玩确认。
- 未验证 Shipping、目标机性能、5–8 分钟首次玩家盲测和最终美术签收。
