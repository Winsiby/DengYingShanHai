# 《灯影山海》落杖成林加密优化记录

任务身份日期：2026-10-26；核查续办日期：2026-10-27。**当前状态：森林加密修改已保存并通过冷加载PIE、编译、187项自动化、Development/Shipping打包、Development SkipFlow与Shipping FullFlow/SkipFlow。Run172实际Shipping林影画面对照通过；正式入口已切换到Run172，并完成公共CMD实际启动、菜单响应和正常退出验证。**

唯一人类作者与最终责任人为项目负责人（用户）；Codex作为程序建模、整合和核查辅助工具，不列为团队制作成员。原[交付草稿](D:/灯影山海/Docs/FOREST_DENSITY_20261026_DRAFT.md)及早期150cm冠幅记录保留为历史；本记录描述最终240cm宽树冠候选。

## 玩家可见修改与范围

本轮只增强夸父“落杖成林”的树林密度。树冠从5组改为8组，并采用更宽的多叶簇网格，使上部冠层相互衔接；保留下方夸父、手杖及接触点的可读空间。新树冠使用深绿色常量PBR材质，与既有木质枝干衔接。

地图修改仅涉及 `M3_RuntimeForest` 的 `CanopyMesh`、`CanopyBranches` 与 `CanopyScales`。15项 `BranchLayout` 保持不变，树冠仍属于表现组件。没有新增主地图、玩法、流程判定、输入方式或游览区域；本轮未修改相机、灯光及已修复的大门。

最终冠索引为 `[7,8,9,10,11,12,13,14]`，逐冠比例为 `[0.85,0.90,0.90,0.88,1.05,1.05,1.55,1.45]`。新资产位于 `/Game/DengYingShanHai/Stage/ForestDensity_20261026/`，未覆盖旧M04资产：

- `SM_DY_ForestCrown_Dense_v1`：根原点为零、底部Z为零的实体树冠网格。
- `M_DY_ForestLeafDense`：本地常量PBR；BaseColor=(0.055,0.115,0.04)、Roughness=0.88、Specular=0.12，无新贴图。

## 源模型、导入与来源

[最终来源清单](D:/灯影山海/Saved/ForestDensity-2026-10-26/Attempt1/FOREST-ASSET-SOURCES-FINAL.json)记录源文件和实际采用资产的SHA256。[可编辑Blender源](D:/灯影山海/Saved/ForestDensity-2026-10-26/Attempt1/Source/ForestCrownDense.blend)与[最终FBX](D:/灯影山海/Saved/ForestDensity-2026-10-26/Attempt1/Source/SM_DY_ForestCrown_Dense_v1.fbx)均保留。

最终源模型为3136个Blender顶点、5076三角形、60×240×100cm。单个源网格内部含44段细枝、15个叶簇和240片实体叶；这44段不是运行时新增的诊断枝，也不改变场景15项BranchLayout。宽冠修改仅扩展上部横向尺寸，底部20cm根部位置不变，20–35cm平滑过渡，不增加三角形。

FBX采用 `FBX_SCALE_NONE` 导出单位烘焙，UE导入后实读尺寸约60×240×100cm；采用此结果依据实际UE边界，不依据导出面板数值推断。木质槽复用既有 `MI_DY_M04_CanopyWood`，叶片槽采用新材质。该网格不新增碰撞行为。

本次几何由本地确定性Blender脚本生成，没有下载模型、纹理或付费资源。来源已登记于 [LICENSES.md](D:/灯影山海/Docs/LICENSES.md) 第15节SELF-011与 [ASSET_SOURCES.md](D:/灯影山海/Docs/ASSET_SOURCES.md) 第9节；AI辅助记录见 [AI-USAGE-FOREST.md](D:/灯影山海/Saved/ForestDensity-2026-10-26/Attempt1/AI-USAGE-FOREST.md)。

## 冠根定位修复

修改前实测5组树冠的冠根相对实际枝尖均偏移X=-40cm。`DYForestPresentationActor.cpp`只将树冠定位由 `TipWorld + BaseOffset + WorldOffset` 改为 `TipWorld + BaseOffset`；`TipWorld` 已来自带世界偏移的枝组件，原表达式对树冠重复添加了偏移。枝本身的世界偏移计算保持原实现。

新增回归测试 `DengYingShanHai.P03.ForestPresentation.CanopyAnchorsApplyWorldOffsetOnce`，在XYZ均非零的WorldOffset下检查生长中的冠根贴合实际枝尖、可见及投影状态，并检查重置清理。此测试验证定位逻辑，不代替美术画面验收。

## 已执行验证

| 项目 | 当前实际结果与证据 |
| --- | --- |
| Editor编译 | 实际成功；[Editor-Build.log](D:/灯影山海/Saved/ForestDensity-2026-10-26/Attempt1/Editor-Build.log) |
| 自动化 | 实际退出0，187成功、0失败；[RESULT.json](D:/灯影山海/Saved/ForestDensity-2026-10-26/Attempt1/Automation-RunD15/RESULT.json)；不覆盖实体输入与打包流程 |
| 地图保存 | [Forest-Apply.json](D:/灯影山海/Saved/ForestDensity-2026-10-26/Attempt1/Forest-Apply.json)记录保存；当前地图SHA256为 `232E8CB47AFB41D9D0F150DDC4E5DEAEBAEA52DC2B18EACE89EF2E9E11AF5E2C` |
| 保存后冷加载 | [Cold-After.json](D:/灯影山海/Saved/ForestDensity-2026-10-26/Attempt1/Cold-After.json)：1809 Actor，15枝、8冠，BranchLayout不变，全部Actor变换/组件/材质对照不变 |
| 冷加载PIE接触与生长 | [After-PIE.json](D:/灯影山海/Saved/ForestDensity-2026-10-26/Attempt1/After-PIE.json)：ok=true、errors=[]，8组冠根相对枝尖误差为零；该捕获脚本不另存地图，因此saved=false不表示先前保存失败 |
| Development打包 | [Package-RunD15/RESULT.json](D:/灯影山海/Saved/ForestDensity-2026-10-26/Attempt1/Package-RunD15/RESULT.json)：Build/Cook/Stage/Archive通过，UAT退出0，49文件、1,221,419,546字节 |
| Shipping打包 | [Package-Run172/RESULT.json](D:/灯影山海/Saved/ForestDensity-2026-10-26/Attempt1/Package-Run172/RESULT.json)：Build/Cook/Stage/Archive通过，UAT退出0，31文件、862,988,549字节 |
| 变更范围 | [Scope-Delta.json](D:/灯影山海/Saved/ForestDensity-2026-10-26/Attempt1/Scope-Delta.json)：689项冻结输入；相对Run171仅主地图、一个生产CPP、一个测试CPP及两项新增资产变化 |
| Development SkipFlow | [FLOW-RESULT.json](D:/灯影山海/Saved/ForestDensity-2026-10-26/Attempt1/Runtime-RunD15-SkipFlow/FLOW-RESULT.json)：两轮四幕及真实重玩通过、原生退出0；实际StepMasks=[4095,4095]、PerformanceMasks=[15,15]、SkippedMasks=[15,15]，未强制终止 |

Development候选为 `Builds/FormalMain-Development-20261026-RunD15/Windows`，原生EXE SHA256为 `0953B77823CD58F1B5F545A1CFA58C6F3DF03ED226D905D7358F12234EAA3B8E`。Shipping候选为 `Builds/FormalMain-Shipping-20261026-Run172/Windows`，原生EXE SHA256为 `D87E1ACA7513215576786578CD53E874C9BFB933C35509AED7FA333A7E0142EF`。两者源地图SHA均与保存地图一致。

PIE阶段前后对照见下图。After为重新加载已保存地图后的实际接触、生长结果，在长成后暂停以便诊断；该图不是Shipping实际画面的替代证据，也不是未经辅助的玩家通关证明。

修改前：

![修改前5组树冠](D:/灯影山海/Saved/ForestDensity-2026-10-26/Attempt1/Before/Player-Full.png)

修改后候选：

![冷加载后8组宽树冠](D:/灯影山海/Saved/ForestDensity-2026-10-26/Attempt1/After/Player-Full.png)

## Shipping流程与画面验收

Run172使用本候选自己的原生Shipping EXE完成两种辅助流程验证；每种均完成两轮四幕、全部12步骤及真实重玩，原生正常退出0，未强制终止：

| 模式 | 两轮实际结果 | 证据 |
| --- | --- | --- |
| FullFlow | CompletedRuns=2；StepMasks=[4095,4095]；PerformanceMasks=[15,15]；SkippedMasks=[0,0] | [FLOW-RESULT.json](D:/灯影山海/Saved/ForestDensity-2026-10-26/Attempt1/Runtime-Run172-FullFlow/FLOW-RESULT.json)、[原生FlowVerifyResult.json](D:/灯影山海/Saved/ForestDensity-2026-10-26/Attempt1/Runtime-Run172-FullFlow/User/Saved/FlowVerifyResult.json) |
| SkipFlow | CompletedRuns=2；StepMasks=[4095,4095]；PerformanceMasks=[15,15]；SkippedMasks=[15,15] | [FLOW-RESULT.json](D:/灯影山海/Saved/ForestDensity-2026-10-26/Attempt1/Runtime-Run172-SkipFlow/FLOW-RESULT.json)、[原生FlowVerifyResult.json](D:/灯影山海/Saved/ForestDensity-2026-10-26/Attempt1/Runtime-Run172-SkipFlow/User/Saved/FlowVerifyResult.json) |

[Forest-Visual-Review-Run172.json](D:/灯影山海/Saved/ForestDensity-2026-10-26/Attempt1/Forest-Visual-Review-Run172.json)记录实际修改前图与Run172 Shipping图的对照，Status=PASS、ComparedBeforeAfter=true，DensityImproved、BranchLayoutUnchanged、FinaleContinuityPreserved均为true。观察确认原先5组稀疏小冠已变为8组重叠宽冠，上部形成连续冠层，下部层次增密，夸父轮廓、手杖/接触区域与“逐日”题签仍可辨认。

下图直接来自 `Runtime-Run172-FullFlow` 的Run172原生Shipping窗口，捕获UTC为 `2026-10-27T05:08:46.017Z`，SHA256为 `CEB6C7C2818A3C4136FA27383A2E31398F85CC24CB3DE7620F4D4BF3559C3DDA`；截图所属RuntimeAudit、EXE路径及配置记录在上述视觉验收JSON中。

![Run172 Shipping实际森林效果](D:/灯影山海/Saved/ForestDensity-2026-10-26/Attempt1/Runtime-Run172-FullFlow/Forest-Shipping.png)

静态画面用于密度和构图核对；落杖到生长连续性结论结合保存后实际接触/生长PIE取样、15枝配置对照及Run172 FullFlow完成记录。此次核查由根代理及独立AI图像审查完成，不等于独立人类视觉验收或首次玩家通关。原始FLOW-RESULT中的ScreenshotReviewPending仍保留该运行结束阶段的原值；后续画面对照结论由独立视觉验收JSON记录，不改写原始运行记录。

## 正式入口与发布

[晋升预检](D:/灯影山海/Saved/ForestDensity-2026-10-26/Attempt1/Promotion-DryRun.json)为 `PASS-DRYRUN-NO-ENTRY-CHANGE`，实核689项冻结输入及31项包产物哈希、FullFlow/SkipFlow与视觉验收。随后[晋升执行记录](D:/灯影山海/Saved/ForestDensity-2026-10-26/Attempt1/Promotion-Run172-20261027-131904-003/RESULT.json)确认只替换了包目录和对应构建审计目录两个路径，其余启动脚本文本与标准日志路径保持不变，地图/EXE/包容器完整性保护保留。

现在仍使用原[正式启动入口](D:/灯影山海/Start-ReleaseEntry-Shipping.cmd)，经 `Scripts/Start-FormalShipping.ps1` 指向 `Builds/FormalMain-Shipping-20261026-Run172/Windows`。正式脚本SHA256实测为 `EC23FCA09E25602601D179E413753251101C63542D291B87AF9F754FFF4AF838`；晋升前Run171脚本备份与旧包均保留。

[PUBLIC-ENTRY-SMOKE.json](D:/灯影山海/Saved/ForestDensity-2026-10-26/Attempt1/PUBLIC-ENTRY-SMOKE.json)记录 `PASS-ACTUAL-PUBLIC-CMD-RENDER-MENU-INPUT-NORMAL-EXIT`，对应实际公共启动审计目录为 [20261027-132006-800](D:/灯影山海/Saved/ReleaseEntryPlay-Shipping/20261027-132006-800)。该次没有地图参数覆盖；实际Run172菜单已渲染，根代理在真实窗口点击退出按钮后观察到按钮响应，原生游戏PID36124正常退出0、外层CMD PID24840退出0，未强制终止。原生退出见[Exit.json](D:/灯影山海/Saved/ReleaseEntryPlay-Shipping/20261027-132006-800/Exit.json)，CMD退出见[PUBLIC-CMD-EXIT.json](D:/灯影山海/Saved/ForestDensity-2026-10-26/Attempt1/PUBLIC-CMD-EXIT.json)。未采样Responding API，输入响应依据实际菜单操作与正常退出记录。

菜单实图捕获UTC为 `2026-10-27T05:21:14.394Z`，SHA256为 `DA6DDB3FBF8A55797F3270858E046626EF907C7FE7262D96DFA8C5A3F839012C`：

![正式公共入口实际Run172菜单](D:/灯影山海/Saved/ForestDensity-2026-10-26/Attempt1/Public-Entry-Menu-Run172.png)

晋升RESULT中的 `PUBLIC-SMOKE-PENDING` / `PublicEntrySmokeVerified=false` 是晋升时点的原始阶段状态；后续实际公共启动结果由PUBLIC-ENTRY-SMOKE单独记录，不回写该历史记录。打包RESULT内的FirstFrameVerified、GameplayVerified等原始阶段标记同样不改写，运行及画面证据分别见本记录各项链接。
## 回退与边界

[Backup目录](D:/灯影山海/Saved/ForestDensity-2026-10-26/Attempt1/Backup)保留修改前地图、生产CPP、测试CPP和正式脚本；Run171旧包完整保留。旧地图SHA256为 `771ED81572B5DC05C784E0C66D1E610898F29EAC8F2DC466095AB67B1BCD9877`。如需回退，先保全当前候选，再精确恢复本次备份并核对包身份；不运行全仓reset/clean，不关闭地图哈希守卫。这里仅记录方法，没有执行回退。

既有[大门修复记录](D:/灯影山海/Docs/GATE_REPAIR_20261025.md)及其原始证据保持历史。最终收尾应同步本轮[CURRENT-HANDOFF.json](D:/灯影山海/Saved/ForestDensity-2026-10-26/Attempt1/CURRENT-HANDOFF.json)，不能改写早期原始运行记录为后来状态。

本轮只验收森林密度与指定保持项。原有右台翼对画面边缘的裁切未调整；没有进行全角度树林审美验收或独立首次玩家测试。此前两次DevD13 CSV Profile退出777003仍未解决，本次编译、自动化和打包成功不代表帧时间/GPU性能验收通过。