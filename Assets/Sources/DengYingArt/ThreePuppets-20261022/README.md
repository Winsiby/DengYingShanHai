# 灯影山海 · 精卫 / 刑天 / 烛龙影偶模型

当前交付：Run2。唯一负责人为用户，Codex 执行制作与验证。所有内容放在 D 盘。

本批是薄皮分件的 2.5D 实体影偶：有封闭前后面与 0.65 cm 切边厚度、真实几何镂空、独立关节、单骨刚性权重、黄铜铆钉。正面为 +X，主面为 YZ，Z 向上，厘米制。

## 文件

- Run2/Jingwei、Run2/Xingtian、Run2/Zhulong：每具含可编辑分件的 *_Puppet_Source.blend、SK_DY_*.fbx、静态Rest OBJ及MTL、独立操杆OBJ及MTL、2K BaseColor/NormalDX/ORM、各姿态FBX、实际渲染预览和 MODEL_VERIFICATION.json。
- 烛龙额外含 ClosedBaseColor；第8根 Eyelid 骨控制真实眼睑皮片。Day眼孔开放，Night皮片闭合。
- AUTHORING_PIECES 是 Blender 源文件中隐藏保留的独立分件集合；主骨骼网格用于导出。操杆另存，不强迫合入主网格投影。
- 10个 A_DY_* 文件是各 1 秒的固定姿态片段，用来检查关节和提供接入姿态，尚非完整演出动画或动作循环。
- 原始概念图只读保留在 ../Concept-20261021/。模型轮廓、分件和皮面图色由该批既有图稿整理，移除了标题、尺寸线、箭头和分解说明；细节为风格化绘制，不冒称真实皮料扫描。

## UE

资源在 /Game/DengYingShanHai/Dev/ThreePuppets_20261022/。
验证地图是 L_ThreePuppetsReview；Meshes 下是3具骨骼网格，Animations 下是10个姿态，Textures 下是10张贴图。
本批没有修改 L_DY_Main、四幕谜题定义、夸父资产或公开 Shipping 启动器。当前正式包仍使用原来的夸父影偶；按幕切换角色与相应投影适配属于下一步接入工作。

## 重现

1. 使用 Python 3.12，安装 numpy、Pillow、opencv-python-headless、shapely、triangle 到本目录 Tooling（或可用Python环境）。这些是离线制作工具，未加入UE运行时。
2. python prepare_meshes.py RunN：按 *_spec.json 产生闭合皮片、孔洞、UV和皮面贴图。
3. Blender 4.5 LTS --background --factory-startup --disable-autoexec --python-exit-code 1 --python build_blender.py -- RunN。
4. 检查所有 MODEL_VERIFICATION.json 和实际预览；脚本校验封闭流形、非退化三角形、正体积、刚性权重、有限姿态、FBX冷读后骨骼/面数/尺寸一致。
5. import_ue.py 只导入专用Dev目录。它会更新该目录的同名资产；不会修改正式主图。重新生成若使用新RunN，应先更新其中SOURCE。
6. capture_projection_ue.py 通过项目已有 DY_SCRIPT 异步编辑器钩子执行，重载 Dev 地图并生成本体与偏移投影同画面的 UE 实际截图。它显式更新 live AnimSingleNodeInstance、设置动画与时间，并核对 actual_animation 和已求值骨骼；用新鲜且完整的 UE-Projection.json 和12张图验收。异步截图需要编辑器持续执行，不能以一次性脚本返回作为截图完成证据。

Run1是修订前回退；Run2是本批定稿。模型改动可通过删除对专用Dev目录的新引用回退，无须恢复正式主图。

## 本轮实际 UE 验证

2026-10-22 的最终 `UE-Projection.json` 为 `ok: true`、`i: 12`、`stage: done`。截图于北京时间22:17:16–22:18:45生成，JSON于22:18:47完成；12条记录中的实际动画资产均与目标姿态一致，包含已求值骨骼。Codex已逐图检查本批全部12张图，确认本体及其幕上实时阴影同时可见、姿态与镂空变化可读。

- [UE 导入记录](D:/灯影山海/Saved/Audit-2026-10-22-ThreePuppets/UE-Import.json)：3具 SkeletalMesh、10个 AnimSequence、10张纹理；专用 Dev 地图保存。
- [最终投影记录](D:/灯影山海/Saved/Audit-2026-10-22-ThreePuppets/UE-Projection.json)：精卫 Rest／Flight／Reach、刑天 Rest／Guard／Reach、烛龙 Rest／Day／Night／Reach，以及 DayEye／NightEye近景，共12张。
- [精卫 Flight 实际投影](D:/灯影山海/Saved/Audit-2026-10-22-ThreePuppets/UE-Projection-Jingwei-Flight.png)、[刑天 Guard 实际投影](D:/灯影山海/Saved/Audit-2026-10-22-ThreePuppets/UE-Projection-Xingtian-Guard.png)、[烛龙 Day 实际投影](D:/灯影山海/Saved/Audit-2026-10-22-ThreePuppets/UE-Projection-Zhulong-Day.png)、[烛龙 Night 实际投影](D:/灯影山海/Saved/Audit-2026-10-22-ThreePuppets/UE-Projection-Zhulong-Night.png)。
- [DayEye](D:/灯影山海/Saved/Audit-2026-10-22-ThreePuppets/UE-Projection-Zhulong-DayEye.png)可见眼内开孔，[NightEye](D:/灯影山海/Saved/Audit-2026-10-22-ThreePuppets/UE-Projection-Zhulong-NightEye.png)可见实体皮片闭合；眼片近景仍有局部片缘与图色拼接，用户最终美术验收保持未完成。
- [UE 编辑器重启后冷重载](D:/灯影山海/Saved/Audit-2026-10-22-ThreePuppets/UE-ColdReload-Final.json)：`ok: true`、`fix_mode: false`，17／14／8骨，10个1秒姿态实际更新动画后回读关节；Day眼睑缩放约0.0001、Night为1；12项材质骨骼用途标记与4张BaseColor的never_stream持久化通过。
- [正式文件未变记录](D:/灯影山海/Saved/Audit-2026-10-22-ThreePuppets/Formal-Unchanged.json)：正式主图、Shipping启动脚本、Puzzle Director三项前后SHA256一致。

旧的未正确求值动画的截图已归档至 `Saved/Audit-2026-10-22-ThreePuppets/Rejected-RestPoseCaptures/`，不计入通过。旧 `UE-Shadow` 纯幕布空图也为 Rejected。当前证据使用上述 `UE-Projection-*` 最终批，不能引用旧眼部截图代替。`Run2/*/Preview_*.png` 属于源模型制作环境预览，应与 UE 实际截图区分。

## 交付边界

本轮完成三具模型、真实厚度与镂空、十个固定姿态及专用Dev验证。当前正式四幕仍使用夸父；尚未进行精卫、刑天、烛龙的正式换偶与投影适配，也未进行模型接入后的Development／Shipping打包。各1秒姿态片段尚非完整演出动画或动作循环。用户是唯一负责人，Codex执行；用户最终美术验收仍保持未完成。

实际 Rest 尺寸：精卫高159.78cm、翼展273.31cm；刑天高179.74cm、含斧盾宽205.79cm；烛龙高199.74cm、宽102.03cm。精卫不能按概念目标误写成240cm翼展。更多源文件、统计与验证细节见[完整交付记录](D:/灯影山海/Docs/THREE_PUPPETS_MODELS_20261022.md)。


## 归档

Deliverables/DY_ThreePuppets_20261022_Run2.zip 已包含源模型、导出、规格、制作脚本、参考图、完整交付记录和最终UE验证截图。Overview_Models.png 为源模型渲染总览，Overview_UE.png 为实际UE投影总览。MANIFEST.json 记录各文件SHA256；PACKAGE_VERIFICATION.json 记录 ZIP CRC、逐文件哈希与数量检查。ZIP是源模型交付，不作为独立UE迁移工程；UE资源已在当前项目专用Dev目录保存。
## Run4（2026-10-23）：操杆并入网格、头身比与姿态修正

Run4 是三具影偶的最新版本，生成命令与 Run2/Run3 相同（`prepare_meshes.py Run4` → `build_blender.py -- Run4`），三份 `MODEL_VERIFICATION.json` 均为 `PASS-MODEL-SOURCE-FBX-ROUNDTRIP`。

| 项 | 精卫 | 刑天 | 烛龙 |
| --- | --- | --- | --- |
| 三角面 | 16,024 | 8,168 | 8,028 |
| 骨骼 | 17 | 14 | 8 |
| 真实镂空 | 99 | 33 | 32 |

三处改动：操杆并入角色网格（权重绑骨、复用 CutEdge 材质槽、主杆末端加黄铜握把球、支杆改为藏在皮片后的短杆）；烛龙头部按 Neck 锚点放大 1.18；刑天三个姿态叠加 `Axe:-35 / Arm_L_Upper:-14 / Arm_R_Upper:-10 / Leg_L_Upper:4 / Leg_R_Upper:-4` 的基准偏移，斧柄竖起、双臂收拢。

Run4 已导入生产库 `/Game/DengYingShanHai/Puppets`，四条 `DA_DYPuppetCast` entry 分别绑定夸父/精卫/刑天/烛龙；`ADYPuppetActor::ApplyChapterFigure` 按章节换网格，`ADYPuzzleDirector::ApplyChapterTitlePlaque` 同步换匾额。实机验证见 `Docs/FOURACT_CAST_20261022.md` 第 8、9 节与 `Saved/Audit-2026-10-22-FourAct/Packaged-Acts234.png`。

归档：`Deliverables/DY_ThreePuppets_20261022_Run4.zip`（119 文件，441,460,493 B，SHA256 `ab02513b817377f022bd5b894b8288a528c689216c491a11f20291c158fe9ad3`），含 Run4 全部源文件、导出、验证 JSON、四幕成片与打包实机截图。Run2/Run3 保留回退。
