# 精卫、刑天、烛龙影偶模型交付记录

日期：2026-10-22。唯一负责人：项目负责人（用户）；执行：Codex。当前交付版本：`ThreePuppets-20261022/Run2`。

本轮已完成三具可编辑、可导出、可刚性分件运动的皮影角色模型，并导入 UE 独立 Dev 目录、保存专用检查地图。三具均使用真实厚度与真实镂空，保留各自的角色轮廓、纹样、关节及操杆源文件。

**本记录交付的是三具模型及其 Dev 检查资产。当前正式四幕仍沿用现有夸父影偶，本轮尚未完成精卫、刑天、烛龙在正式四幕中的换偶、输入驱动、镜头构图、目标影形及打包接入。不能把本轮模型交付记为四幕角色接入完成。**

## 1. 源文件与版本边界

本轮源文件根目录：[ThreePuppets-20261022](D:/灯影山海/Assets/Sources/DengYingArt/ThreePuppets-20261022)。`Run2/` 是当前交付；此前 `Run1/` 保留作本轮回退及差异核对。没有覆盖原概念图，模型与检查资产均使用本轮新目录。

| 角色 | 可编辑 Blender 源 | 骨骼 FBX | 静态 Rest OBJ | 操杆 OBJ |
|---|---|---|---|---|
| 精卫 | [Jingwei_Puppet_Source.blend](D:/灯影山海/Assets/Sources/DengYingArt/ThreePuppets-20261022/Run2/Jingwei/Jingwei_Puppet_Source.blend) | [SK_DY_Jingwei.fbx](D:/灯影山海/Assets/Sources/DengYingArt/ThreePuppets-20261022/Run2/Jingwei/SK_DY_Jingwei.fbx) | [SM_DY_Jingwei_Rest.obj](D:/灯影山海/Assets/Sources/DengYingArt/ThreePuppets-20261022/Run2/Jingwei/SM_DY_Jingwei_Rest.obj) | [SM_DY_Jingwei_ControlRods.obj](D:/灯影山海/Assets/Sources/DengYingArt/ThreePuppets-20261022/Run2/Jingwei/SM_DY_Jingwei_ControlRods.obj) |
| 刑天 | [Xingtian_Puppet_Source.blend](D:/灯影山海/Assets/Sources/DengYingArt/ThreePuppets-20261022/Run2/Xingtian/Xingtian_Puppet_Source.blend) | [SK_DY_Xingtian.fbx](D:/灯影山海/Assets/Sources/DengYingArt/ThreePuppets-20261022/Run2/Xingtian/SK_DY_Xingtian.fbx) | [SM_DY_Xingtian_Rest.obj](D:/灯影山海/Assets/Sources/DengYingArt/ThreePuppets-20261022/Run2/Xingtian/SM_DY_Xingtian_Rest.obj) | [SM_DY_Xingtian_ControlRods.obj](D:/灯影山海/Assets/Sources/DengYingArt/ThreePuppets-20261022/Run2/Xingtian/SM_DY_Xingtian_ControlRods.obj) |
| 烛龙 | [Zhulong_Puppet_Source.blend](D:/灯影山海/Assets/Sources/DengYingArt/ThreePuppets-20261022/Run2/Zhulong/Zhulong_Puppet_Source.blend) | [SK_DY_Zhulong.fbx](D:/灯影山海/Assets/Sources/DengYingArt/ThreePuppets-20261022/Run2/Zhulong/SK_DY_Zhulong.fbx) | [SM_DY_Zhulong_Rest.obj](D:/灯影山海/Assets/Sources/DengYingArt/ThreePuppets-20261022/Run2/Zhulong/SM_DY_Zhulong_Rest.obj) | [SM_DY_Zhulong_ControlRods.obj](D:/灯影山海/Assets/Sources/DengYingArt/ThreePuppets-20261022/Run2/Zhulong/SM_DY_Zhulong_ControlRods.obj) |

各角色目录同时保留 `.mtl`、BaseColor、NormalDX、ORM、GeometryMask、prepared.json、MODEL_VERIFICATION.json、姿态 FBX 和预览图。烛龙另有 `T_DY_Zhulong_ClosedBaseColor.png`，供实体眼睑皮片使用。

## 2. 建模方式、厚度与实际尺寸

模型沿既有设定图制作皮革分片的真实轮廓、孔壁和侧壁，每个顶点刚性绑定到一根骨骼；叠片、关节铆钉与操杆保留可编辑结构。镂空属于网格拓扑孔洞，皮片单层实体厚度为 **0.65 cm**。整体前后厚度还包含叠片偏移和铆钉，不能把总深度误报成 0.65 cm。

下表取 Run2 的 `MODEL_VERIFICATION.json` 中 Rest 世界包围盒；UE 导入后的高度读回与其一致，误差在验收阈值内。坐标约定为 Z 向上、X 为皮片法向，宽度由 Y 范围计算。

| 角色 | Rest 实际高 | Rest 实际宽／翼展 | 含叠片与铆钉的总深度 | 骨骼 | 三角面 | 真实镂空统计 |
|---|---:|---:|---:|---:|---:|---:|
| 精卫 | 159.78 cm | **273.31 cm 翼展** | 3.545 cm | 17 | 15,772 | 99 |
| 刑天 | 179.74 cm | 205.79 cm（含斧盾） | 2.965 cm | 14 | 7,916 | 33 |
| 烛龙 | 199.74 cm | 102.03 cm | 3.505 cm | 8 | 7,776 | 32 |

精卫按当前概念图比例和约 160 cm 高建成后，实际翼展约 273 cm；**没有宣称或验证为 240 cm**。后续若要求收至 240 cm，需要明确调整翼长或整体缩放，并重新检查投影构图与尺寸，不能直接改记录。

精卫分头、躯干、左右三段翼、尾羽与双腿关节。刑天保留无头轮廓、胸眼腹口、持斧握手、独立斧盾及腿足分节。烛龙分头、颈、三段躯干和尾片，并加入第 8 根 `Eyelid` 骨骼及真实眼睑皮片；睁眼时保留眼内开孔，闭眼时由皮片遮合，从几何上改变眼部透光。

## 3. 十个姿态片段

以下均已导出独立动画 FBX，并在 UE 中导入为对应角色自身 Skeleton 的 `AnimSequence`。UE 读回每段时长为 1.0 秒；这十段是固定姿态片段，用于角色姿态与关节展示，尚非完整演出动画或动作循环。

| 角色 | 已交付姿态／文件名 |
|---|---|
| 精卫 | `A_DY_Jingwei_Rest.fbx`、`A_DY_Jingwei_Flight.fbx`、`A_DY_Jingwei_Reach.fbx` |
| 刑天 | `A_DY_Xingtian_Rest.fbx`、`A_DY_Xingtian_Guard.fbx`、`A_DY_Xingtian_Reach.fbx` |
| 烛龙 | `A_DY_Zhulong_Rest.fbx`、`A_DY_Zhulong_Day.fbx`、`A_DY_Zhulong_Night.fbx`、`A_DY_Zhulong_Reach.fbx` |

烛龙 Night 的闭眼同时包含局部图色和实体眼睑运动，不只依赖贴图变化；该骨骼属于模型内部表现，不增加玩法输入。

## 4. 造型、图色与来源

本轮使用项目内已有三张概念设定图作为造型与图色事实源：

- [C1_Jingwei_Ortho_v01.png](D:/灯影山海/Assets/Sources/DengYingArt/Concept-20261021/C1_Jingwei_Ortho_v01.png)
- [C1_Xingtian_Ortho_v01.png](D:/灯影山海/Assets/Sources/DengYingArt/Concept-20261021/C1_Xingtian_Ortho_v01.png)
- [C1_Zhulong_Ortho_v01.png](D:/灯影山海/Assets/Sources/DengYingArt/Concept-20261021/C1_Zhulong_Ortho_v01.png)

BaseColor 沿用这些图的样式化彩绘、纹样和色彩，经角色区清理、尺寸标记排除与 UV 图集整理后使用；烛龙闭眼局部来自同张设定图中的夜态眼睛。图色属于样式化绘制来源，不能描述为实物皮革扫描反照率、历史文物复原或特定皮影流派的正统复刻。

本轮未购买模型、材质、插件或生成服务，也未新增图像生成调用。本轮只核对现有概念图文件与 SHA256，没有重新核实其历史创作及授权来源；正式参赛材料应与项目来源登记相符，本记录不替代来源核验。三份 `MODEL_VERIFICATION.json` 保留参考图和分件规格的 SHA256，可追溯本轮输入。

## 5. UE 资源与专用检查地图

导入证据：[UE-Import.json](D:/灯影山海/Saved/Audit-2026-10-22-ThreePuppets/UE-Import.json)。本次记录为 `ok: true`、`map_saved: true`、`warnings: []`，数量为 **3 个 SkeletalMesh、10 个 AnimSequence、10 张纹理**。骨骼读回分别为 17／14／8；烛龙 `Eyelid` 实际导入。

资源统一放在 `/Game/DengYingShanHai/Dev/ThreePuppets_20261022`：

| 类型 | UE 路径 |
|---|---|
| 精卫骨骼网格 | `/Game/DengYingShanHai/Dev/ThreePuppets_20261022/Meshes/SK_DY_Jingwei` |
| 刑天骨骼网格 | `/Game/DengYingShanHai/Dev/ThreePuppets_20261022/Meshes/SK_DY_Xingtian` |
| 烛龙骨骼网格 | `/Game/DengYingShanHai/Dev/ThreePuppets_20261022/Meshes/SK_DY_Zhulong` |
| 角色专用 Skeleton | 同一 `Meshes/` 目录内，各 `SK_DY_<角色>_Skeleton` |
| 十段动画 | 同一根目录下的 `Animations/A_DY_<角色>_<姿态>` |
| 纹理 | 同一根目录下的 `Textures/T_DY_<角色>_BaseColor`、`NormalDX`、`ORM`；烛龙另有 `ClosedBaseColor` |
| 材质 | 同一根目录下的 `Materials/`；Skin、CutEdge、Brass，烛龙另有 EyelidSkin |
| 专用检查地图 | `/Game/DengYingShanHai/Dev/ThreePuppets_20261022/L_ThreePuppetsReview` |

地图已保存三具 SkeletalMeshActor、各自幕面和 Movable PointLight，采用固定的手动曝光检查基线。当前导入记录证明资源类型、材质槽分配、骨骼、动画时长、厘米尺寸与保存结果；灯光参数存在不等于已完成 UE 投影美术验收。

## 6. 已完成的验证与可直接查看的图

三份模型验证均为 `PASS-MODEL-SOURCE-FBX-ROUNDTRIP`：

- [精卫 MODEL_VERIFICATION.json](D:/灯影山海/Assets/Sources/DengYingArt/ThreePuppets-20261022/Run2/Jingwei/MODEL_VERIFICATION.json)
- [刑天 MODEL_VERIFICATION.json](D:/灯影山海/Assets/Sources/DengYingArt/ThreePuppets-20261022/Run2/Xingtian/MODEL_VERIFICATION.json)
- [烛龙 MODEL_VERIFICATION.json](D:/灯影山海/Assets/Sources/DengYingArt/ThreePuppets-20261022/Run2/Zhulong/MODEL_VERIFICATION.json)

记录中的验证包括：分片封闭且具有正体积、顶点一骨刚性权重、姿态几何有限、骨骼与三角面数一致、FBX 在全新场景中冷导入、世界厘米包围盒差小于 0.02 cm。**这里的 FBX 冷读是源模型往返验证，不等同于 UE 编辑器重启后对 `.uasset` 的冷重载。**

Codex 已逐图查看 Run2 三具 Rest／Oblique，以及烛龙 Night：角色主体、装饰轮廓、斧盾与翼羽可读；镂空能透出背景；烛龙睁闭眼可分，Run1 中右下尺寸延长线残片在 Run2 正面和斜视图中已去除。此检查不替代用户最终美术验收，三份模型记录仍保留 `human_art_acceptance: false`。

| 角色 | 正面 | 斜视 | 补充状态 |
|---|---|---|---|
| 精卫 | [Preview_Rest](D:/灯影山海/Assets/Sources/DengYingArt/ThreePuppets-20261022/Run2/Jingwei/Preview_Rest.png) | [Preview_Oblique](D:/灯影山海/Assets/Sources/DengYingArt/ThreePuppets-20261022/Run2/Jingwei/Preview_Oblique.png) | 同目录另有 Flight、Reach、RealShadow |
| 刑天 | [Preview_Rest](D:/灯影山海/Assets/Sources/DengYingArt/ThreePuppets-20261022/Run2/Xingtian/Preview_Rest.png) | [Preview_Oblique](D:/灯影山海/Assets/Sources/DengYingArt/ThreePuppets-20261022/Run2/Xingtian/Preview_Oblique.png) | 同目录另有 Guard、Reach、RealShadow |
| 烛龙 | [Preview_Rest](D:/灯影山海/Assets/Sources/DengYingArt/ThreePuppets-20261022/Run2/Zhulong/Preview_Rest.png) | [Preview_Oblique](D:/灯影山海/Assets/Sources/DengYingArt/ThreePuppets-20261022/Run2/Zhulong/Preview_Oblique.png) | [Preview_Night](D:/灯影山海/Assets/Sources/DengYingArt/ThreePuppets-20261022/Run2/Zhulong/Preview_Night.png) |

以上 `Run2/*/Preview_*.png` 为模型制作环境预览。文件名中的 RealShadow 不应被引用为正式 UE 运行时或 Shipping 的投影证据。

## 7. UE 最终可视核验补记

<!-- UE_FINAL_VERIFICATION_BEGIN -->

最终 UE 实际截图与冷重载检查已取得证据。采集结果：[UE-Projection.json](D:/灯影山海/Saved/Audit-2026-10-22-ThreePuppets/UE-Projection.json)，`ok: true`、`i: 12`、`stage: done`，包含 12 条截图记录。最终批次的截图时间为北京时间 2026-10-22 **22:17:16–22:18:45**，JSON 于 22:18:47 写完；12 张图均晚于本轮修正后的截图脚本时间，文件实际存在且非空。

每条记录均包含实际 `AnimSingleNodeInstance` 使用的 `actual_animation` 和已求值的 `evaluated_pose`，角色／姿态与目标资源逐条对应。脚本显式更新 live 动画实例、定位时间并验证当前动画资产；最终批精卫 Flight／Reach、刑天 Guard／Reach、烛龙 Day／Night／Reach 的关节与轮廓变化均在实际图像中可分。

Codex 已逐图检查全部 12 张最终 UE 图：皮影本体与偏移投到幕面的阴影同时可见；翼羽、斧刃、裙片及龙身镂空能形成透光变化；没有用空幕布图替代投影证据。烛龙 DayEye 的眼内孔透出幕色，NightEye 由实体眼片闭合；整身 Day／Night 图的眼部透光也随之变化。眼片近景仍能看到局部片缘与图色拼接，这部分留待用户最终美术验收。

| 角色 | 本轮 UE 实际投影截图 |
|---|---|
| 精卫 | [Rest](D:/灯影山海/Saved/Audit-2026-10-22-ThreePuppets/UE-Projection-Jingwei-Rest.png)、[Flight](D:/灯影山海/Saved/Audit-2026-10-22-ThreePuppets/UE-Projection-Jingwei-Flight.png)、[Reach](D:/灯影山海/Saved/Audit-2026-10-22-ThreePuppets/UE-Projection-Jingwei-Reach.png) |
| 刑天 | [Rest](D:/灯影山海/Saved/Audit-2026-10-22-ThreePuppets/UE-Projection-Xingtian-Rest.png)、[Guard](D:/灯影山海/Saved/Audit-2026-10-22-ThreePuppets/UE-Projection-Xingtian-Guard.png)、[Reach](D:/灯影山海/Saved/Audit-2026-10-22-ThreePuppets/UE-Projection-Xingtian-Reach.png) |
| 烛龙 | [Rest](D:/灯影山海/Saved/Audit-2026-10-22-ThreePuppets/UE-Projection-Zhulong-Rest.png)、[Day](D:/灯影山海/Saved/Audit-2026-10-22-ThreePuppets/UE-Projection-Zhulong-Day.png)、[Night](D:/灯影山海/Saved/Audit-2026-10-22-ThreePuppets/UE-Projection-Zhulong-Night.png)、[Reach](D:/灯影山海/Saved/Audit-2026-10-22-ThreePuppets/UE-Projection-Zhulong-Reach.png) |
| 烛龙眼部近景 | [DayEye](D:/灯影山海/Saved/Audit-2026-10-22-ThreePuppets/UE-Projection-Zhulong-DayEye.png)、[NightEye](D:/灯影山海/Saved/Audit-2026-10-22-ThreePuppets/UE-Projection-Zhulong-NightEye.png) |

此前一批截图没有更新 live 单节点动画实例，Flight／Night 等仍停在 Rest，已经归档至 `Saved/Audit-2026-10-22-ThreePuppets/Rejected-RestPoseCaptures/`，不计入通过证据。旧 `UE-Shadow` 纯幕布空图同样为 Rejected，不得引用为投影通过。当前记录仅使用上表 `UE-Projection-*` 最终批。拍摄期间的灯光／机位调整为检查用途，未保存为正式场景构图。

UE 编辑器重启后的独立冷重载证据：[UE-ColdReload-Final.json](D:/灯影山海/Saved/Audit-2026-10-22-ThreePuppets/UE-ColdReload-Final.json)，`ok: true`、`fix_mode: false`。已读回三具 17／14／8 根骨骼及持久化 Rest 状态，十个 1 秒姿态在实际更新动画后逐一读回关节；烛龙 Eyelid 的 Day 缩放约 0.0001、Night 为 1。两份父材质及十份角色 MI 共 12 项的骨骼网格用途标记均持久化，四张 BaseColor（含闭眼图）的 `never_stream` 均为 true。

正式范围保护证据：[Formal-Unchanged.json](D:/灯影山海/Saved/Audit-2026-10-22-ThreePuppets/Formal-Unchanged.json)，`ok: true`，`L_DY_Main.umap`、`Start-FormalShipping.ps1`、`DYPuzzleDirector.cpp` 三项前后 SHA256 全部一致。该结果证明本轮三个核查文件未改动，不扩展解释为已完成正式四幕接入或打包测试。

<!-- UE_FINAL_VERIFICATION_END -->

## 8. 后续责任与当前限制

当前模型的 `runtime_integration` 为 false，与正式四幕尚未换偶的事实一致。本轮完成三具模型和 Dev 检查，未完成正式四幕换偶，也未进行这批模型接入后的 Development／Shipping 打包验证。十个固定的 1 秒姿态片段不能记为完整演出动画。后续工作的唯一负责人仍为项目负责人（用户），Codex 执行已授权的工作；角色与章节绑定、投影构图、重置／重播及正式打包验证另行记录。

本轮回退保留 `Run1/`，重新生成或复导入使用独立 Dev 命名空间；不得为了回退这批模型而重置正式地图、覆盖队友资产或禁用公开入口完整性检查。



注：本批10个动画资产均为1秒固定姿态片段，用于模型关节检查及后续接入，不冒称完整表演动画。

## 9. 本轮交付归档

- [三具源模型交付 ZIP](D:/灯影山海/Assets/Sources/DengYingArt/ThreePuppets-20261022/Deliverables/DY_ThreePuppets_20261022_Run2.zip)：三份原生 Blender、三份骨骼网格 FBX、十份姿态 FBX、Rest 与操杆 OBJ/MTL、贴图、分件规格、制作脚本、参考图及最终验证证据。ZIP 不作为可独立迁移的 UE 工程包；当前工程内的 Dev 资产已经导入保存。
- [模型制作环境总览](D:/灯影山海/Assets/Sources/DengYingArt/ThreePuppets-20261022/Deliverables/Overview_Models.png)、[UE 实体与实时投影总览](D:/灯影山海/Assets/Sources/DengYingArt/ThreePuppets-20261022/Deliverables/Overview_UE.png)。总览仅拼排真实截图，没有生成或替换角色画面。
- [源文件 SHA256 清单](D:/灯影山海/Assets/Sources/DengYingArt/ThreePuppets-20261022/Deliverables/MANIFEST.json)、[ZIP 完整性校验](D:/灯影山海/Assets/Sources/DengYingArt/ThreePuppets-20261022/Deliverables/PACKAGE_VERIFICATION.json)：已校验 ZIP CRC、逐文件 SHA256 和 3 份 Blender／3 份网格 FBX／10 份姿态 FBX 数量。
## 10. Run4 与四幕接入（2026-10-23）

Run4 在 Run3（4K 贴图 + 杆件并入）基础上再改三处：主杆与支杆的握持几何（支杆改成藏在皮片后的短杆、主杆末端加黄铜握把球）、烛龙头部按 Neck 锚点整体放大 1.18、刑天三个固定姿态加基准偏移使斧柄竖起并收拢双臂。计数为精卫 16,024 面/17 骨/99 镂空、刑天 8,168 面/14 骨/33 镂空、烛龙 8,028 面/8 骨/32 镂空。

接入方式（不改判定链）：`ADYPuppetActor` 新增独立的 `CastMesh` 组件承载后三幕影偶，绕开夸父 Blueprint 的 AnimBP；`DA_DYPuppetCast` 四条 entry 存网格、姿态片段与相对变换；`DYPuzzleDirector::StartCurrentPuzzle` 同时调用 `ApplyChapterFigure` 与 `ApplyChapterTitlePlaque`。`CastMesh` 必须 `SetMobility(Movable)`，否则 `SetRelativeLocation/Rotation/Scale3D` 会被静默忽略。

打包与实机：RunD7 前所有 Development 包都缺这些资产——`DA_DYPuppetCast` 与题签 MI 都是 C++ 固定路径 `LoadObject`，cooker 不会从地图发现，需在 `Config/DefaultGame.ini` 的 `[/Script/UnrealEd.ProjectPackagingSettings]` 显式 `+DirectoriesToAlwaysCook`。修好后 `Builds/FormalMain-Development-20261023-RunD7` 的 utoc 里可见三具网格、cast 数据、题签 MI 与 BaseColor 贴图；在打包 exe 里从「演出篇章」逐幕进入，实拍到第二幕「填海」+精卫、第三幕「舞干戚」+刑天、第四幕「昼夜」+烛龙（`Saved/Audit-2026-10-22-FourAct/Packaged-Acts234.png`）。

`runtime_integration` 自本轮起为 true（Development 包内四幕已换偶）；公开 Shipping 入口仍是 Run143，尚未用这批资产重打，属于需要用户拍板的部署动作。

归档：`Deliverables/DY_ThreePuppets_20261022_Run4.zip`（119 文件，441,460,493 B，SHA256 `ab02513b817377f022bd5b894b8288a528c689216c491a11f20291c158fe9ad3`），`MANIFEST_Run4.json`、`PACKAGE_VERIFICATION_Run4.json` 记录逐文件哈希与验证结论。
