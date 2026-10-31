# 《灯影山海》落杖成林：影戏剪影树林重新建模

任务身份日期：2026-10-28；完成核查日期：2026-10-30。**本轮R5重新建模已采用至正式Shipping Run174。源模型、主地图保存/冷加载与真实接触生长、187项自动化、Development/Shipping两包、候选自身四幕/重玩、森林专项实图、受保护晋升及实际公开CMD入口均已验证。本轮指定任务无剩余实现项。** 当前交接见 [CURRENT-HANDOFF.json](D:/灯影山海/Saved/ForestRedesign-2026-10-28/Attempt1/CURRENT-HANDOFF.json)。本结论不包含独立玩家盲测、任意角度美术或帧时间性能验收。

## 玩家可见结果与范围

按用户选择的“影戏剪影：多株树干、镂空枝叶”，本轮将旧版细叉上层叠叶团改为同一个真实杖尖接触点展开的根脉、三株主干和带孔尖叶。左主干增加弯折，冠内曲枝渐细，34片较大叶形与主叉间留白形成剪影。孔隙来自实体网格，没有Alpha卡片、透明背板或椭球叶团。

改动限于两个新网格、一个局部常量材质，以及主图 `M3_RuntimeForest` 的七项表现配置：BranchMesh、BranchMaterial、BranchLayout、CanopyMesh、CanopyMaterial、CanopyBranches、CanopyScales。表现端点、直径和父子拓扑重新设计，仍保留15个BranchComponents、原逐行GrowthBegin/End进度窗、同一个Contact/Token授权、落杖触地到长林的因果与重玩清理。核心C++、谜题主判定、演出时长、相机、灯光、大门和其他场景内容没有因此扩项。

唯一人类作者与最终责任人为用户；Codex提供程序建模、整合和核查辅助。造型是影戏主题的创意设计，不表述为人工逐面雕刻、特定流派正统复现或历史文物复原。

## 最终R5资产

| 内容 | 实际采用与证据 |
| --- | --- |
| `SM_DY_ForestStem_Silhouette_v3` | 110源顶点/216三角形，20×20×100cm，Z=-50..50cm；XY bounds中心和两端中心在生长轴上，中段弧度、渐细轮廓。UE实际bounds及生长连接由保存/冷加载和After-PIE独立验证 |
| `SM_DY_ForestCrown_Pierced_v3` | 2244源顶点/4288三角形，40×180×140cm，根(0,0,0)、底Z0；34片大镂空尖叶/34个真实孔，50段内部木段含22叶柄，主叉间保留大透光区 |
| `M_DY_ForestLeather_Silhouette` | 本轮局部Opaque/DefaultLit常量PBR，BaseColor(.012,.009,.006)、Roughness.88、Specular.12，墨褐色；不使用新贴图，不依赖Unlit或改灯光来替代真实受光/投影 |
| 三树表现布局 | [LAYOUT.json](D:/灯影山海/Saved/ForestRedesign-2026-10-28/Attempt1/Tools/LAYOUT.json)仍15条；三冠索引[3,4,5]、缩放[1.75,1.75,1.65]；左低主干4终点[-16,26]并同步子7起点，根0/1/2采用低Z，根1/2直径10cm。新拓扑经真实接触、生长、原生避让及终态检查 |

源内部木段不是运行时枝干，也不是新增Actor。源三角形/顶点不冒称UE渲染统计。34个源叶孔不等于组合后必然有102个独立可见投影孔；实际孔隙与重叠以本轮舞台实图解释。枝叶在接点相交组成渲染网格，并非全局布尔焊接或碰撞实体。

[MODEL.json](D:/灯影山海/Saved/ForestRedesign-2026-10-28/Attempt1/Source/MODEL.json)、[GEOMETRY-CHECK.json](D:/灯影山海/Saved/ForestRedesign-2026-10-28/Attempt1/Source/GEOMETRY-CHECK.json)记录源尺寸、枢轴、叶面朝向、真实孔及FBX独立Blender回读。导出为FBX_SCALE_NONE、Forward=-Y、Up=Z，源保留Wood/Leaf两槽，UE接入时采用上述局部材质。源文件、接入与采用身份见 [FOREST-ASSET-SOURCES-FINAL.json](D:/灯影山海/Saved/ForestRedesign-2026-10-28/Attempt1/FOREST-ASSET-SOURCES-FINAL.json)；[DRAFT](D:/灯影山海/Saved/ForestRedesign-2026-10-28/Attempt1/FOREST-ASSET-SOURCES-DRAFT.json)保留为阶段快照。[CPU墨色源预览](D:/灯影山海/Saved/ForestRedesign-2026-10-28/Attempt1/SourcePreview/Crown-Ink-Silhouette.png)仅用于源检查，检查材质覆盖没有烘焙进源文件，不是游戏截图。

## 实际画面与生长保持项

修改前与保存后冷加载使用同一普通游玩机位，经实际落杖接触和长林后，仅在全部长成时暂停以便诊断；没有传送玩家或改最终POV。

修改前：

![Run173基线树林](D:/灯影山海/Saved/ForestRedesign-2026-10-28/Attempt1/Before/Player-Full.png)

保存后冷加载的R5：

![R5三树镂空剪影](D:/灯影山海/Saved/ForestRedesign-2026-10-28/Attempt1/After/Player-Full.png)

[Forest-Apply.json](D:/灯影山海/Saved/ForestRedesign-2026-10-28/Attempt1/Forest-Apply.json)为ok/saved=true；[Cold-After.json](D:/灯影山海/Saved/ForestRedesign-2026-10-28/Attempt1/Cold-After.json)与[After-PIE.json](D:/灯影山海/Saved/ForestRedesign-2026-10-28/Attempt1/After-PIE.json)确认15枝、3冠，实际最终15枝全部可见且portion≈1，冠根相对枝端误差为零，原逐行生长窗口、单一物理/幕上接触根和全部1809 Actor的变换/组件/材质保持项通过。地图仅上述森林authoring字段发生指定变更，不把“BranchLayout完全未改”作为本轮结论。

实际Shipping Run174画面：

![Run174包内树林](D:/灯影山海/Saved/ForestRedesign-2026-10-28/Attempt1/Runtime-Run174-Assisted-ForestReview2/Forest-Shipping.png)

此图来自候选自己的[Assisted-ForestReview2会话](D:/灯影山海/Saved/ForestRedesign-2026-10-28/Attempt1/Runtime-Run174-Assisted-ForestReview2/Launch.json)，使用既有可选ReviewView9移动/隐藏玩家后的近处固定审查视角，随后正常开始演出并经历实际Contact/Growth。它与PIE前后对照不是同机位，也不是步行证明。捕获UTC为 `2026-10-30T06:34:15.569Z`，SHA256为 `61FEC54FA3561E38B6AA2FD03E416487FFDB4916ED508EE4DD333B750691105B`；[Forest-Capture.json](D:/灯影山海/Saved/ForestRedesign-2026-10-28/Attempt1/Runtime-Run174-Assisted-ForestReview2/Forest-Capture.json)绑定本轮原生EXE、时间和运行目录，[会话退出](D:/灯影山海/Saved/ForestRedesign-2026-10-28/Attempt1/Runtime-Run174-Assisted-ForestReview2/Exit.json)为0、无强退。

[Forest-Visual-Review-Run174.json](D:/灯影山海/Saved/ForestRedesign-2026-10-28/Attempt1/Forest-Visual-Review-Run174.json)专项复核通过：新剪影风格、主干与枝叶连接、15枝/生长契约、多株及镂空可读性、夸父/杖尖可读性和终局连续性均有本轮证据。复核为根代理与独立AI看图，不冒充独立人工盲测；连续时序由实际生长样本及下述候选流程支持，静态图本身只证明最终画面。

## 自动化、构建与候选流程

[Scope-Delta.json](D:/灯影山海/Saved/ForestRedesign-2026-10-28/Attempt1/Scope-Delta.json)确认相对Run173的693项完整输入，只修改主地图并加入三项本轮美术资产。保存后工作地图SHA256为 `EFA89946579C87A9261314561460DB9D2C8FC5844214BDEF10A8394CA3D43F15`；112个Source文件、旧配置与既有材质保持。

| 实际阶段 | 本轮结果 |
| --- | --- |
| RunD17自动化 | [RESULT.json](D:/灯影山海/Saved/ForestRedesign-2026-10-28/Attempt1/Automation-RunD17/RESULT.json)：187成功、0失败，实际exit0及TEST COMPLETE标记 |
| Development RunD17 | [RESULT.json](D:/灯影山海/Saved/ForestRedesign-2026-10-28/Attempt1/Package-RunD17/RESULT.json)：Build/Cook/Stage/Archive通过，UAT与wrapper均0，49文件/1,221,281,716字节 |
| Shipping Run174 | [RESULT.json](D:/灯影山海/Saved/ForestRedesign-2026-10-28/Attempt1/Package-Run174/RESULT.json)：Build/Cook/Stage/Archive通过，UAT与wrapper均0，31文件/862,850,719字节 |
| 输入与产物复核 | [PACKAGES-REHASH-CHECK.json](D:/灯影山海/Saved/ForestRedesign-2026-10-28/Attempt1/PACKAGES-REHASH-CHECK.json)：两包各693项BEFORE/AFTER/当前输入一致、差异0；49/31项产物逐项重算SHA/字节全部匹配，archive身份与各自RESULT一致，Cook正式主地图及引擎Entry |
| Development自身SkipFlow | [FLOW-RESULT.json](D:/灯影山海/Saved/ForestRedesign-2026-10-28/Attempt1/Runtime-RunD17-SkipFlow/FLOW-RESULT.json)：两轮四幕、12步骤、跳过及真实重玩，原生与wrapper均退出0 |
| Shipping自身FullFlow | [FLOW-RESULT.json](D:/灯影山海/Saved/ForestRedesign-2026-10-28/Attempt1/Runtime-Run174-FullFlow/FLOW-RESULT.json)：两轮四幕、12步骤、完整演出及真实重玩，原生与wrapper均退出0 |
| Shipping自身SkipFlow | [FLOW-RESULT.json](D:/灯影山海/Saved/ForestRedesign-2026-10-28/Attempt1/Runtime-Run174-SkipFlow/FLOW-RESULT.json)：两轮四幕、12步骤、跳过及真实重玩，原生与wrapper均退出0 |

三组运行原生FlowVerifyResult均为Succeeded=true、CompletedRuns=2、StepMasks=[4095,4095]及PerformanceMasks=[15,15]；[D17原生结果](D:/灯影山海/Saved/ForestRedesign-2026-10-28/Attempt1/Runtime-RunD17-SkipFlow/User/Saved/FlowVerifyResult.json)和[Run174跳过结果](D:/灯影山海/Saved/ForestRedesign-2026-10-28/Attempt1/Runtime-Run174-SkipFlow/User/Saved/FlowVerifyResult.json)另有SkippedMasks=[15,15]，[Run174完整结果](D:/灯影山海/Saved/ForestRedesign-2026-10-28/Attempt1/Runtime-Run174-FullFlow/User/Saved/FlowVerifyResult.json)为[0,0]。实际重玩通过正常OpenLevel；没有强制结束程序。它们使用项目已有可选自动辅助入口，不冒充首次玩家独立操作。普通移动/重玩证据与固定审查视角图片分开。

Development原生EXE SHA256为 `ED1B1BCD112B3DCDBE13F9BA0E93D14AA9E26B6E668B975BBFAA76D8236B71E5`，必须使用本包身份，不能借D16；Shipping原生EXE SHA256为 `D87E1ACA7513215576786578CD53E874C9BFB933C35509AED7FA333A7E0142EF`。候选仍固定为 `FormalMain-Development-20261028-RunD17` / `FormalMain-Shipping-20261028-Run174`，跨日续办不重命名历史尝试。调用说明见[Run174-Tools-README.md](D:/灯影山海/Saved/ForestRedesign-2026-10-28/Attempt1/Tools/Run174-Tools-README.md)。

原始构建、Launch、Exit与FLOW阶段的FirstFrameVerified、GameplayVerified、HumanVisualAcceptance或ScreenshotReviewPending等字段保留创建时语义；后续运行、图片和公开入口通过由对应独立证据说明，不回写历史字段。

## 正式Run174入口与回退

现在可使用 [Start-ReleaseEntry-Shipping.cmd](D:/灯影山海/Start-ReleaseEntry-Shipping.cmd) → `Scripts/Start-FormalShipping.ps1` → `Builds/FormalMain-Shipping-20261028-Run174/Windows`。正式脚本SHA256为 `15E23B2C84E0982B8F2A540C3D842FD308840F05FBF76A7C3D3C29A409244AC7`，与实际公开烟测记录及当前文件一致。

[Promotion-DryRun.json](D:/灯影山海/Saved/ForestRedesign-2026-10-28/Attempt1/Promotion-DryRun.json)只作预检；真正切换见 [Promotion-Run174-20261030-144752-124/RESULT.json](D:/灯影山海/Saved/ForestRedesign-2026-10-28/Attempt1/Promotion-Run174-20261030-144752-124/RESULT.json)。晋升严格只把Run173包目录和对应审计目录替换成Run174，其余正式脚本文字、地图/EXE/产物哈希守卫与标准公开日志路由保留。晋升记录创建时发生在公开烟测之前，后续完成由独立PUBLIC-ENTRY-SMOKE说明。

[PUBLIC-ENTRY-SMOKE.json](D:/灯影山海/Saved/ForestRedesign-2026-10-28/Attempt1/PUBLIC-ENTRY-SMOKE.json)为实际公开CMD启动、菜单显示与点击退出通过。审计目录是 [ReleaseEntryPlay-Shipping/20261030-144851-829](D:/灯影山海/Saved/ReleaseEntryPlay-Shipping/20261030-144851-829)，[Launch.json](D:/灯影山海/Saved/ReleaseEntryPlay-Shipping/20261030-144851-829/Launch.json)绑定正确Run174 Shipping原生EXE、PID40136、MapOverride=false。根代理看到菜单并点击“退出游戏”，[游戏退出](D:/灯影山海/Saved/ReleaseEntryPlay-Shipping/20261030-144851-829/Exit.json)和[外层CMD退出](D:/灯影山海/Saved/ForestRedesign-2026-10-28/Attempt1/PUBLIC-CMD-EXIT.json)均为0，CMD PID37064，无强制终止。

[公开菜单实图](D:/灯影山海/Saved/ForestRedesign-2026-10-28/Attempt1/Public-Entry-Menu-Run174.png)捕获UTC为 `2026-10-30T06:49:34.863Z`，SHA256为 `930E8FCE0C35B2010C110AEF3CC0F4F887FB7C0B209E29D7ED456507C3DDC8E9`；其时间位于实际原生会话内。没有用预检、后台进程存在或Responding API代替真实菜单/输入/正常退出。

Run173旧包、模型、材质及[备份地图](D:/灯影山海/Saved/ForestRedesign-2026-10-28/Attempt1/Backup/L_DY_Main.umap)、[旧正式脚本](D:/灯影山海/Saved/ForestRedesign-2026-10-28/Attempt1/Backup/ReleaseEntry-Run173-PrePromotion/Start-FormalShipping.ps1)完整保留。旧地图SHA256为 `1DCF90ED7CE255C76FE9CC32374D62A50DB81B0E41DA176765417560890B51EF`，旧脚本SHA256为 `40E9650A82C09E47C768E9BAC4F71B2F9022324AA904104A24E6F6F7759EC32C`。回退应先保全本轮，再精确恢复匹配地图与包路由，不全仓reset/clean、不绕守卫；本轮没有执行回退。

## 迭代、来源与验收边界

早期R2的66片小孔叶与7872三角形是历史源。R3/R4已在PIE实际生长，但R4图中细碎孔叶/自身投影叠为褐色纹理，下部直杆和低根脉仍显支架，不因ok=true认定最终美术通过。R5减少并放大叶片、保留大留白、左主干增加弯折、局部材质压深后，才进入当前保存与包内验收。原源/预览及资产分别保留 [Before-R5-Coarse](D:/灯影山海/Saved/ForestRedesign-2026-10-28/Attempt1/Source/Before-R5-Coarse)、[Before-R5-Authoring](D:/灯影山海/Saved/ForestRedesign-2026-10-28/Attempt1/Backup/Before-R5-Authoring) 和 [R4图](D:/灯影山海/Saved/ForestRedesign-2026-10-28/Attempt1/Preview-R4/Player-Full.png)，不覆盖为后来成功记录。

诊断时曾临时加入C++日志；112个Source文件已与Run173冻结输入逐项哈希一致，临时日志源恢复后[Editor-Restored-Recompile.log](D:/灯影山海/Saved/ForestRedesign-2026-10-28/Attempt1/Editor-Restored-Recompile.log)实际成功，随后本轮两包完整输入再次复核。原生接触、避让、bounds、会话授权和完成资源检查没有放松。[捕获接触数学回放](D:/灯影山海/Saved/ForestRedesign-2026-10-28/Attempt1/CAPTURED-CONTACT-LAYOUT-CHECK.json)只用于诊断，实际授权仍由原生运行路径决定。

本轮来源已按SELF-013登记，见 [LICENSES.md §17](D:/灯影山海/Docs/LICENSES.md)、[ASSET_SOURCES.md §11](D:/灯影山海/Docs/ASSET_SOURCES.md)及[AI-USAGE-FOREST-REDESIGN.md](D:/灯影山海/Saved/ForestRedesign-2026-10-28/Attempt1/AI-USAGE-FOREST-REDESIGN.md)。来源是本地自建程序几何与常量PBR，没有第三方模型/纹理下载、在线图像生成、付费素材、新插件或运行时在线服务。旧模型与上游资产来源身份不改。MODEL、DRAFT、早期诊断及构建运行的原始阶段字段保持，不把源的创建时false值改成后来通过。

本轮验收限于选定造型与保持项：根连接仍是低位图形根线，不是写实土壤根系；右冠重叠更密，且受原右台翼裁切；左弯干靠近头饰左上方，但不遮躯干，不继续向内移动。没有为画面改相机或台翼。没有宣称任意角度美术、独立玩家盲测或帧时间性能验收；旧DevD13两次CSV Profile退出777003仍为历史限制。