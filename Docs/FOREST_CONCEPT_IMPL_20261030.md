# 批准概念树林落地与Run175交付

用户批准的树林概念已落实到主地图的“杖落成林”，2026-10-31完成本轮实施、验证和正式入口切换。启动：[原正式游戏入口](D:/灯影山海/Start-ReleaseEntry-Shipping.cmd)，当前为 **FormalMain-Shipping-20261030-Run175**；Development对应RunD18。唯一人类制作责任人与最终决定人为用户，Codex负责辅助实现和核查。

## 玩家能看到的变化

旧环状叶冠与细直杆布局替换为连成片的弯曲粗干树林。源模型含两株主干、三株次干，600片实体阔叶组成60组；三处不等高冠峰和群间留白避免单一平顶。运行时合为一个装饰grove，保留15枝。树林围绕夸父留出中央通道，根部从实际落杖位置接续；移除旧-40cm平面偏移，实测到杖根仅Z约+.364cm差，不能写成严格全零。

原生BranchLayout端点/直径/父子拓扑按新造型调整，15行GrowthBegin/End、接触、Token、proof、谜题输入与完成流程保持。只修改森林作者属性；保存后冷读确认1809 Actor变换/组件/材质未改其他场景。没有调整门、相机、灯和其他角色。

## 生长表现修正

整体缩放的初版会让原本的中央留白收缩后扫过人物。实际导入网格几何投影诊断在Progress≈.654时躯干矩形命中16521三角，在≈.808时头部6768；这些是矩形相交估算，不是逐像素遮挡面积。失败诊断保留。

最小修正只涉及3个Source：ForestPresentationActor.h/.cpp与同组自动化测试。新增默认false的可选高度显现，仅本轮森林启用true；grove保持.85完整尺寸，原G=clamp((Progress-.55)/.45,0,1)写CPD0，两个局部Masked材质按LocalPosition.Z/560自下而上显现。旧false路径保持。实际接触采样的中段与终态，导入全网格投影到夸父头部/躯干保护矩形均0命中，幕外顶点0，原生15枝preflight有效。不是五株分别计时的自然生长。

## 实图与证据边界

以下是采用模型后的**实际PIE暂停终态**，不是概念图，也不称Shipping终态截图：

![采用后PIE终态](D:/灯影山海/Saved/ForestConceptImpl-2026-10-30/Attempt1/After/Player-Full.png)

本轮 **Run175 Shipping包内生长阶段**（独立审查机位9，隐藏/移动Pawn，仅用于视觉审查）：

![Run175树林生长阶段](D:/灯影山海/Saved/ForestConceptImpl-2026-10-30/Attempt1/Runtime-Run175-Assisted-ForestReview3/Run175-Forest-1.jpg)

原始Run174同机位PIE对照：[修改前图](D:/灯影山海/Saved/ForestConceptImpl-2026-10-30/Attempt1/Before/Player-Full.png)。候选截图时间、native路径/SHA、正常退出关联及具体限制见 [视觉核查](D:/灯影山海/Saved/ForestConceptImpl-2026-10-30/Attempt1/Forest-Visual-Review-Run175.json)。源CPU预览与批准图仅作源形状和设计参考。首次续接的旧Assisted会话缺少Exit.json，保留为INCOMPLETE，不计通过；Review2/3正常退出0，第三轮保留5帧，后3帧已进入精卫章，不冒称森林图。

## 验证结果

|检查|结果|
|---|---|
|保存、冷加载、实际PIE接触/生长|通过；15枝/1grove、原窗口与无关Actor保持|
|自动化|188成功/0失败，实际退出0；包括高度显现尺寸、CPD、会话冻结与重置测试|
|Development RunD18|49文件 / 1,223,081,521字节；构建/UAT/包装退出0|
|Shipping Run175|31文件 / 864,624,924字节；构建/UAT/包装退出0|
|冻结输入|697项，与两包前后输入及最终重哈希一致，差异0|
|Shipping完整演出+重玩|两轮四幕，StepMasks[4095,4095]、PerformanceMasks[15,15]、Skipped[0,0]，原生/包装退出0|
|Shipping跳过+重玩|两轮四幕，所有演出跳过mask[15,15]，原生/包装退出0|
|Development跳过+重玩|两轮四幕、真实重载，原生/包装退出0|
|正式入口|仅替换2处Run174→Run175路由，守卫保持；实际原CMD显示菜单、点击退出，原生和外层CMD退出0|

主地图SHA256：`BBD838FA64D705E8F6C485B367AD5A27802BECE0DBCAD709B85AB4101C2CF763`。Shipping native：`BABDD7BF2D56276DF107D959916F9BE1C9C7D0365FE834828AF26F97728653D9`。正式脚本SHA256：`2FBF4338797320AD6EA14AA4D81293C3EAEF7130DAFBBAFD1B0C3D2D9B49B410`。完整证据：[两包核验](D:/灯影山海/Saved/ForestConceptImpl-2026-10-30/Attempt1/PACKAGES-REHASH-CHECK.json)、[自身流程](D:/灯影山海/Saved/ForestConceptImpl-2026-10-30/Attempt1/RUNTIME-CHECKS.json)、[公开入口实启](D:/灯影山海/Saved/ForestConceptImpl-2026-10-30/Attempt1/PUBLIC-ENTRY-SMOKE.json)、[最终一致性](D:/灯影山海/Saved/ForestConceptImpl-2026-10-30/Attempt1/FINAL-CHECK.json)。

## 来源、范围与回退

SELF-014已登记：[许可登记](D:/灯影山海/Docs/LICENSES.md)、[资产来源](D:/灯影山海/Docs/ASSET_SOURCES.md)、[源与采用SHA清单](D:/灯影山海/Saved/ForestConceptImpl-2026-10-30/Attempt1/FOREST-ASSET-SOURCES-FINAL.json)、[AI辅助说明](D:/灯影山海/Saved/ForestConceptImpl-2026-10-30/Attempt1/AI-USAGE-FOREST-CONCEPT.md)。源由本地确定性Blender程序生成，无第三方模型/纹理下载及外部付费素材；批准图为内置image_gen概念参考，未成为运行时贴图，模型/计费不猜写。原始.blend/.fbx、生成器、R2/R3/R4-Draft、失败材质/采集/缩放诊断与阶段false均保留。

生产变化准确为主图+4个新UE资产+3个Source；Config/旧资产保持，详见 [范围差异](D:/灯影山海/Saved/ForestConceptImpl-2026-10-30/Attempt1/Scope-Delta.json)。回退文件：[Run174主图](D:/灯影山海/Saved/ForestConceptImpl-2026-10-30/Attempt1/Backup/L_DY_Main.umap)、[Run174正式脚本](D:/灯影山海/Saved/ForestConceptImpl-2026-10-30/Attempt1/Backup/ReleaseEntry-Run174-PrePromotion/Start-FormalShipping.ps1)、[3项Source改前清单](D:/灯影山海/Saved/ForestConceptImpl-2026-10-30/Attempt1/Backup/Before-Height-Reveal/BACKUP-SHA256.json)。Source恢复后须重新编译/打包，不能用旧二进制冒充当前源。旧包与旧原始验收不删，旧handoff仅加本轮指针。

## 保留的表现限制

生长中可见水平高度显现边缘；当前远景冠团较实，概念图细叶、树皮纹理与多层色阶只做了简化。右台翼仍裁掉一部分树冠，普通机位不能逐株数清源里的五株。实现是按概念造型改编的游戏几何，不是画稿逐像素还原。没有独立人类首次盲玩、全游戏美术和帧时性能验收；旧D13 Profile777003诊断不由本轮重分类或解决。以上是明确限制，不作为本任务未接入或未发布的待办。
