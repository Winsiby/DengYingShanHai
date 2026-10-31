# 《灯影山海》林影茂密感与枝叶衔接优化

任务日期：2026-10-27。**当前已核证：v2树冠与10冠配置已保存，冷加载与真实接触/生长PIE通过，187项自动化、RunD16/Run173两包构建及完整输入/产物复核通过；Shipping完整与跳过流程各完成两轮四幕及真实重玩并正常退出，森林专项画面复核通过。Development RunD16跳过/重玩也已通过；正式入口已晋升至Run173，实际公开CMD菜单与输入响应、游戏和外层CMD正常退出均已核证。本轮指定森林优化已交付。** 最新阶段以本轮 [CURRENT-HANDOFF.json](D:/灯影山海/Saved/ForestPolish-2026-10-27/Attempt1/CURRENT-HANDOFF.json) 为准。

唯一人类作者与最终责任人为用户，Codex提供程序建模、整合和核查辅助。上一轮正式基线为Run172；本轮仅回应“继续优化树林的茂密感和枝叶衔接”。

## 修改与范围

新建 `Stage/ForestPolish_20261027/SM_DY_ForestCrown_Connected_v2`，增加中央和中下部过渡叶簇，错开上层叶簇高度，并加强渐细支撑枝。相同机位的最终画面较Run172叶团更厚、外缘起伏更多，冠下细长枝到叶团之间的大块露空减少，夸父躯干、四肢与落杖区域仍可辨认。

最终选用10组装饰冠：索引 `[5,6,7,8,9,10,11,12,13,14]`，缩放 `[0.60,0.62,0.85,0.90,0.90,0.88,1.05,1.05,1.55,1.45]`。原8冠改用v2，额外在原branch5/6末端挂两枚较小的低位冠，将裸露长叉分成下、中、上层次。地图只改 `M3_RuntimeForest` 的CanopyMesh、CanopyBranches、CanopyScales；本轮只新增这一项网格。

[Scope-Delta.json](D:/灯影山海/Saved/ForestPolish-2026-10-27/Attempt1/Scope-Delta.json)确认690项冻结输入中，仅主地图修改和一个新网格加入；Source、Config及既有材质全部不变。[Forest-Apply.json](D:/灯影山海/Saved/ForestPolish-2026-10-27/Attempt1/Forest-Apply.json)与保存后[Cold-After.json](D:/灯影山海/Saved/ForestPolish-2026-10-27/Attempt1/Cold-After.json)确认原15条BranchLayout及全部1809 Actor变换、组件、材质保持，包括已修复的大门。落杖接触、判定、生长时序、重玩清理、相机、灯光及四幕流程没有新增实现。

## 模型与来源

新网格已按 **SELF-012** 登记于 [LICENSES.md §16](D:/灯影山海/Docs/LICENSES.md) 与 [ASSET_SOURCES.md §10](D:/灯影山海/Docs/ASSET_SOURCES.md)。源为本地Blender Python程序几何：3706源顶点、6064三角形，51段内部枝、22叶簇、264片实体叶；它们是单个装饰冠网格结构，不是新增51条运行时枝干。源尺寸60×240×100cm、根原点(0,0,0)、底Z=0，FBX_SCALE_NONE导出及Blender回读通过。保存后UE实际包围尺寸约59.999994×240×100cm，Wood/Leaf两槽。

Wood继续复用 `MI_DY_M04_CanopyWood`，Leaf复用Run172/SELF-011的 `M_DY_ForestLeafDense`，没有新建或覆盖旧材质、纹理；没有第三方下载、付费素材、在线图像生成或新增运行时在线服务。旧材质的来源身份与许可边界继续适用，不另称新的原创纹理。

源、新UE网格、接入脚本及阶段证据哈希见 [FOREST-ASSET-SOURCES-FINAL.json](D:/灯影山海/Saved/ForestPolish-2026-10-27/Attempt1/FOREST-ASSET-SOURCES-FINAL.json)。FINAL是源与采用清单，发布状态须由候选运行和公开入口另证。原 [MODEL.json](D:/灯影山海/Saved/ForestPolish-2026-10-27/Attempt1/Source/MODEL.json) 与 [来源草稿](D:/灯影山海/Saved/ForestPolish-2026-10-27/Attempt1/FOREST-ASSET-SOURCES-DRAFT.json)保留原阶段字段；旧预览网格2912407C…哈希不冒充最终保存网格。AI范围与过程记录见 [AI-USAGE-FOREST-POLISH.md](D:/灯影山海/Saved/ForestPolish-2026-10-27/Attempt1/AI-USAGE-FOREST-POLISH.md)。

最终保存地图SHA256为 `1DCF90ED7CE255C76FE9CC32374D62A50DB81B0E41DA176765417560890B51EF`。新UE网格为410077字节，SHA256为 `0321C54A8C5EBD72F571001C95D0467BBEBD9FCCCB88DF04ABB736C6121AB6DA`。原生源、交换文件和生成器均留在本轮Saved目录，原Run172模型与源不覆盖。

## 已执行验证

| 项目 | 实际结果与证据 |
| --- | --- |
| 源检查 | 尺寸、根原点、两材质槽、有限顶点、≤7000三角形及FBX回读通过；[MODEL.json](D:/灯影山海/Saved/ForestPolish-2026-10-27/Attempt1/Source/MODEL.json)。源计数不是UE渲染计数 |
| 保存主地图 | [Forest-Apply.json](D:/灯影山海/Saved/ForestPolish-2026-10-27/Attempt1/Forest-Apply.json)：ok/saved=true，最终v2/10冠；属性写入使用notify_mode=NEVER并保留场景/布局断言 |
| 保存后冷加载 | [Cold-After.json](D:/灯影山海/Saved/ForestPolish-2026-10-27/Attempt1/Cold-After.json)：ok=true、1809 Actor、15枝、10冠，BranchLayout及全部Actor变换/组件/材质不变 |
| 冷加载实际接触/生长 | [After-PIE.json](D:/灯影山海/Saved/ForestPolish-2026-10-27/Attempt1/After-PIE.json)：ok=true、errors=[]，实际触地后长林，10冠根与实际枝尖对齐，长成后暂停诊断截图；主代理原生等待退出0，[日志](D:/灯影山海/Saved/ForestPolish-2026-10-27/Attempt1/After-PIE.log)正常关闭。此捕获脚本本身不保存地图，saved=false不推翻先前保存 |
| 自动化 | [Automation-RunD16/RESULT.json](D:/灯影山海/Saved/ForestPolish-2026-10-27/Attempt1/Automation-RunD16/RESULT.json)：187成功、0失败、实际退出0，不覆盖实体输入与包内流程 |
| Development构建 | [Package-RunD16/RESULT.json](D:/灯影山海/Saved/ForestPolish-2026-10-27/Attempt1/Package-RunD16/RESULT.json)：Build/Cook/Stage/Archive通过、UAT退出0；49文件、1,221,468,778字节 |
| Shipping构建 | [Package-Run173/RESULT.json](D:/灯影山海/Saved/ForestPolish-2026-10-27/Attempt1/Package-Run173/RESULT.json)：Build/Cook/Stage/Archive通过、UAT退出0；31文件、863,037,781字节 |
| 输入与产物复核 | [PACKAGES-REHASH-CHECK.json](D:/灯影山海/Saved/ForestPolish-2026-10-27/Attempt1/PACKAGES-REHASH-CHECK.json)：两包前/后/当前均690输入、差异0，49/31项产物重新哈希通过，UAT与wrapper实际退出0。两包Cook为正式主图及引擎Entry，不借用Run172产物证明本轮 |
| Shipping完整流程 | [FullFlow/FLOW-RESULT.json](D:/灯影山海/Saved/ForestPolish-2026-10-27/Attempt1/Runtime-Run173-FullFlow/FLOW-RESULT.json)：两轮四幕、12步骤、真实重玩及原生正常退出0 |
| Shipping跳过流程 | [SkipFlow/FLOW-RESULT.json](D:/灯影山海/Saved/ForestPolish-2026-10-27/Attempt1/Runtime-Run173-SkipFlow/FLOW-RESULT.json)：两轮四幕、12步骤、真实重玩、全部演出跳过及原生正常退出0 |
| 森林专项图像复核 | [Forest-Visual-Review-Run173.json](D:/灯影山海/Saved/ForestPolish-2026-10-27/Attempt1/Forest-Visual-Review-Run173.json)：PASS；DensityImproved、CanopyBranchConnectionImproved、BranchLayoutUnchanged、FinaleContinuityPreserved为true；根与独立AI复核，不冒充人类视觉验收 |

Development候选为 `Builds/FormalMain-Development-20261027-RunD16/Windows`，原生EXE SHA256为 `0953B77823CD58F1B5F545A1CFA58C6F3DF03ED226D905D7358F12234EAA3B8E`。Shipping候选为 `Builds/FormalMain-Shipping-20261027-Run173/Windows`，原生EXE SHA256为 `D87E1ACA7513215576786578CD53E874C9BFB933C35509AED7FA333A7E0142EF`。两包源地图哈希一致；生产C++未改，原生EXE与上轮相同不代表包内地图/网格相同，完整包身份与产物已独立复核。

## 同机位前后与Shipping画面

本轮Run172修改前同机位：

![Run172基线8冠](D:/灯影山海/Saved/ForestPolish-2026-10-27/Attempt1/Before/Player-Full.png)

保存后重新加载地图，再经过实际接触/生长所得10冠结果。截图仅在长成后暂停用于诊断，不冒充独立玩家通关：

![保存后冷加载10冠PIE](D:/灯影山海/Saved/ForestPolish-2026-10-27/Attempt1/After/Player-Full.png)

实际Run173原生Shipping窗口的树林画面：

![Run173实际Shipping树林](D:/灯影山海/Saved/ForestPolish-2026-10-27/Attempt1/Runtime-Run173-Assisted-ForestReview/Forest-Shipping.png)

Shipping图像SHA256为 `A76968706E1AE6334EBE7A98B779A8F9C6339686126DF1F359598836A9148A52`，CapturedUtc为 `2026-10-27T14:37:32.731Z`，记录见 [Forest-Capture.json](D:/灯影山海/Saved/ForestPolish-2026-10-27/Attempt1/Runtime-Run173-Assisted-ForestReview/Forest-Capture.json)。其独立[Launch.json](D:/灯影山海/Saved/ForestPolish-2026-10-27/Attempt1/Runtime-Run173-Assisted-ForestReview/Launch.json)与[Exit.json](D:/灯影山海/Saved/ForestPolish-2026-10-27/Attempt1/Runtime-Run173-Assisted-ForestReview/Exit.json)确认本轮Shipping原生EXE、会话内捕获及原生退出0/无强退。

该Shipping截图使用现有可选 `DY_DEBUG_VIEW=9` 固定审查视角移动并隐藏玩家，根点击Start后经历实际接触/长林。它与Before/After PIE不是相同机位，只用于包内冠形、层次、材质和可读性检查，不能用作步行或严格像素量化对照。入场与四幕流程证明来自以下独立FullFlow/SkipFlow会话。

## Shipping完整、跳过与重玩

[FullFlow原生结果](D:/灯影山海/Saved/ForestPolish-2026-10-27/Attempt1/Runtime-Run173-FullFlow/User/Saved/FlowVerifyResult.json)为Succeeded=true、CompletedRuns=2、StepMasks=[4095,4095]、PerformanceMasks=[15,15]、SkippedMasks=[0,0]；[原生退出](D:/灯影山海/Saved/ForestPolish-2026-10-27/Attempt1/Runtime-Run173-FullFlow/Exit.json)为0。

[SkipFlow原生结果](D:/灯影山海/Saved/ForestPolish-2026-10-27/Attempt1/Runtime-Run173-SkipFlow/User/Saved/FlowVerifyResult.json)为Succeeded=true、CompletedRuns=2、StepMasks=[4095,4095]、PerformanceMasks=[15,15]、SkippedMasks=[15,15]；[原生退出](D:/灯影山海/Saved/ForestPolish-2026-10-27/Attempt1/Runtime-Run173-SkipFlow/Exit.json)为0。两组都是候选自己的现有可选自动辅助入口，包含实际重玩/OpenLevel；没有强制终止，不冒充独立首次玩家操作。

静态图片证明最终茂密感、枝叶衔接与主体可读性；连续时序另由保存后实际接触/生长样本和候选自身完整/跳过流程支持。原始构建、Launch、Exit及FLOW阶段的FirstFrameVerified、ScreenshotReviewPending等字段保留，不回写成后来验收。

## 正式入口、Development流程与回退

正式入口现为 [Start-ReleaseEntry-Shipping.cmd](D:/灯影山海/Start-ReleaseEntry-Shipping.cmd) → `Scripts/Start-FormalShipping.ps1` → `Builds/FormalMain-Shipping-20261027-Run173/Windows`。新正式脚本SHA256为 `40E9650A82C09E47C768E9BAC4F71B2F9022324AA904104A24E6F6F7759EC32C`，源地图SHA256为 `1DCF90ED7CE255C76FE9CC32374D62A50DB81B0E41DA176765417560890B51EF`。原地图/包完整性守卫及标准公开日志路由保留。

[Promotion-DryRun.json](D:/灯影山海/Saved/ForestPolish-2026-10-27/Attempt1/Promotion-DryRun.json)已通过，核对690项输入、31项Shipping产物、两组流程和森林专项画面。该次历史DryRun仍记录1个Development运行实例及ExecuteRequested=false；后续Development实例正常退出后，根才执行[实际晋升](D:/灯影山海/Saved/ForestPolish-2026-10-27/Attempt1/Promotion-Run173-20261027-224300-691/RESULT.json)。实际变更只替换包目录及对应构建审计两条路由，旧Run172脚本保存在同晋升目录；不把预检当成真正发布。

Development候选自己的[SkipFlow结果](D:/灯影山海/Saved/ForestPolish-2026-10-27/Attempt1/Runtime-RunD16-SkipFlow/FLOW-RESULT.json)和[原生结果](D:/灯影山海/Saved/ForestPolish-2026-10-27/Attempt1/Runtime-RunD16-SkipFlow/User/Saved/FlowVerifyResult.json)为Succeeded=true、CompletedRuns=2、StepMasks=[4095,4095]、PerformanceMasks=[15,15]、SkippedMasks=[15,15]，真实重玩；[原生退出](D:/灯影山海/Saved/ForestPolish-2026-10-27/Attempt1/Runtime-RunD16-SkipFlow/Exit.json)为0，无强制终止。此项是Development自身证据，没有借用Shipping结果。

[PUBLIC-ENTRY-SMOKE.json](D:/灯影山海/Saved/ForestPolish-2026-10-27/Attempt1/PUBLIC-ENTRY-SMOKE.json)已记录真正从原公开CMD入口启动Run173，Configuration=Shipping、MapOverride=false，原生PID30852、外层CMD PID38348。实际公开会话目录为 [20261027-224324-957](D:/灯影山海/Saved/ReleaseEntryPlay-Shipping/20261027-224324-957)；根观察菜单并点击“退出游戏”，目标窗口正常关闭，原生和外层CMD均退出0，无强退。响应依据实际菜单输入和退出，不伪造未采样的Responding API。

![Run173实际公开入口菜单](D:/灯影山海/Saved/ForestPolish-2026-10-27/Attempt1/Public-Entry-Menu-Run173.png)

菜单图CapturedUtc为 `2026-10-27T14:43:53.957Z`，SHA256为 `D5183204AFFF60780FF60D50834065D9B1D57B1816D006B1C3DD7F7646A3B784`。实际晋升原RESULT中的PublicEntrySmokeVerified=false、各构建/Launch/Exit的阶段false字段均保留原样；公开入口的后来通过由独立PUBLIC-ENTRY-SMOKE证据说明。

[Backup](D:/灯影山海/Saved/ForestPolish-2026-10-27/Attempt1/Backup)保留Run172地图及正式脚本，原Run172包/源/材质与上一轮证据保留。回退须先保全本轮，再精确恢复地图和匹配旧包路由；不执行全仓reset/clean，不绕过完整性守卫。来源登记前的两份Docs、AI和旧FINAL快照保留于 [Before-SELF012-20261027-160857](D:/灯影山海/Saved/ForestPolish-2026-10-27/Attempt1/Backup/Before-SELF012-20261027-160857)；公开入口最终收尾前的五份文件亦另存Backup。

## 验收边界

本轮只改善同一戏台树林的茂密感与枝叶衔接。原右台翼仍裁切部分右冠，Shipping偏右审查视角对此更明显；没有为图像好看而改相机或台翼。低位左冠靠近夸父头饰，但没有吞没躯干/四肢，当前.60/.62缩放不继续放大。原下部细枝保持，改进的是过渡和层次，不声称消除所有长细线、任意机位的写实森林或全角度审美完成。

旧DevD13两次CSV Profile原生退出777003仍未解决；本轮没有新增帧时间性能结论或独立玩家盲测。原MODEL、构建及运行阶段字段继续保留，原始失败/预览不回写为后来成功版本。