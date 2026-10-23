# 建模美术清单（2026-10-21）

> 2026-10-22 现状核查：[项目进度](PROGRESS_REVIEW_20261022.md) / [本轮美术优化](ART_POLISH_20261022.md)。本文历史数量与基线不作为当前验收结论。

> 用途：把「还没有建模、仍是引擎基本体或根本不存在」的美术项一次列清，供后续按概念图排产。
> 依据：`C:\dy_build\pass61_art.py` → `ext61_art.json`（actor/材质分组）、`C:\dy_build\pass62_slots.py` → `ext62_slots.json`（每个槽位实测 bounds）、`C:\dy_build\pass63_classes.py` → `ext63_classes.json`（actor 类分布）。均在 `L_DY_Main` 上实跑。
> 尺寸单位一律 UE 厘米；坐标取关卡世界坐标。

## 0. 结论（先看这段）

- 关卡共 **803 个 actor**：`StaticMeshActor` 734、灯 2+1+47+5、`TextRenderActor` 2、`PostProcessVolume` 1、`DYLightRigActor` 1、`DYPuzzleDirector` 1、`TargetPoint` 1、`ExponentialHeightFog` 2、蓝图 actor 4（`BP_DYStageEnvironment`、`BP_DYForestPresentation_Dev`、`BP_DYReadabilityPresentation`、`BP_DYKuafuPuppet_Fitted`）。
- 734 个 `StaticMeshActor` 里，**自制网格只有 24 种 / 26 个 actor**；其余 **708 个是引擎基本体**（Sphere 414、Cube 164、Cone 107、Cylinder 22、Plane 1）。
- 最该先补的一件不是外景，而是**影窗本体**：`DEV_BackScreen`（Cube 50×900×800）挂的是引擎默认 `BasicShapeMaterial_Inst`——整出戏的影子都投在这块默认灰面上。
- **完全不存在**的：精卫 / 刑天 / 烛龙三具影偶（关卡里只有一具 `BP_DYKuafuPuppet_Fitted`）、锣鼓器乐类道具、纸灯笼与竹骨、楹联匾额、图鉴插图。
- 已有可复用的建模流水线（`Assets\Sources\DengYingArt\*` 的 Blender 脚本 + FBX + 2K PBR 贴图），新增模型照这条线走即可。

## 1. 已经建好的模型（24 种网格 / 26 个 actor）

| 资产 | actor | 尺寸（cm） | 用途 |
| --- | --- | --- | --- |
| `SM_DY_StageWingCurtain` | `ART_MainlineThickCurtain_L/R` ×2 | 901 长边 | 台侧厚幕（2K 贴图） |
| `SM_DY_LampBody` / `SM_DY_LampStand` | `ART_MainLampBody` / `ART_MainLampStand` | 463 / 464 | 主角提灯与灯架 |
| `SM_DY_FramePost/Capital/Brace/RollerBracket/Axle/PullRope/Hook` ×L/R、`FrameHeader`、`FrameTopRail`、`FrameUpperRoller`、`FrameLowerWeight` | `M03_*` ×18 | 907–995 | 台口木构（斗拱、轴、绳、钩、配重） |
| `SM_DY_BackstageBench` | `M06_AudienceBench_L/R` ×2 | 1350 | 观众条凳 |
| `SM_DY_WingScreen` | `DEV_WingScreen_Right` | 648 | 侧幕影窗 |
| `SM_DY_Target_P03` | `Readability_GuideP03` | 924 | 第三幕幕上目标图 |

库里还有 **28 个网格资产未在关卡摆放**（不全是遗漏）：`SM_DY_OperatorRodRack`、`SM_DY_Target_P01/P02`、`SM_DY_FrameBeam_Source/TopUV/FullSpan`、`SM_DY_ForestBranch_Tapered`、`SM_DY_ForestBranch_Leafed`、`SM_DY_ForestBranch_WideLeaf`、`SM_DY_M04_Canopy_A_v04`（后四者由 `BP_DYForestPresentation_Dev` 在结局运行时挂载，属正常）、`SK_DY_Kuafu_*` 多版、`SK_DY_Reenactor_*` 多版。

## 2. 仍是引擎基本体、需要建模的名单

### P0 · 观众正中视线（先做这批，画面收益最大）

| 待建模 | 当前 actor | 实测尺寸 / 位置 | 说明 |
| --- | --- | --- | --- |
| **影窗幕面 + 幕框** | `DEV_BackScreen` | Cube 50×900×800 @(950,0,424)，幕面 y±450、z24–824 | 引擎默认灰材质；整出戏的投影面 |
| 台口大幕 | `DYTheater_Curtain_L/R` | Cube 30×300×1300 @x890 | 与自制 `SM_DY_StageWingCurtain` 两套并存，需统一 |
| 台口柱 | `DYTheater_Proc_Col_L/R` | 120×120×1400 @(880,±820) | 正面立柱 |
| 侧墙 | `DYTheater_Wall_L/R` | 4000×50×1900 @y=±1300 | 四面墙全是方块 |
| 台前墙 / 台后墙 | `DYTheater_FrontWall_L/R`、`RearWall_L/R` | 50×1000×1900 @x2200 / 50×790×1900 @x-1800 | |
| 壁柱 | `DYTheater_Pilaster_L/R` | 70×70×1900 ×8 | 每侧 4 根 |
| 椽 / 檐口 | `DYTheater_Rafter`、`DYExt30_Eave` | 4000×40×40 ×8 @z1800 / 72×2600×34 ×3 @z1946 | 顶部轮廓 |
| 台基 / 台阶 | `DYTheater_Riser` ×3、`DEV_Step_1..3` | 280×2500×30 / 90×150×25 | |
| 栏杆柱 | `DYTheater_RailPost` | 40×40×520 ×5 | |
| 地板 | `DYTheater_Floor`、`DEV_Floor`、`DYTheater_FloorApron` | 4000×2600×100 / 2400×1800×100 / 600×2600×80 | 木地板已有 2K 贴图，可改网格做板缝 |

### P0 · 门楼与入场走廊

| 待建模 | 当前 actor | 尺寸 | 说明 |
| --- | --- | --- | --- |
| 门柱 | `DYTheater_GatePost_L/R` | 80×80×920 ×2 @x-1800（y=-540/+120，净宽 620） | 入场第一眼 |
| 门楣 | `DYTheater_GateLintel` | 90×720×90 @z950 | |
| 门槛 | `DYTheater_GateStep` | 140×700×20 | |
| 台前大门 | `DYTheater_FrontGateDoor` | 40×560×1400 @x2180 | |
| 走廊墙 / 柱 / 梁 / 顶 | `M05_EntryWall_L/R`、`M05_EntryPost_*` ×4、`M05_EntryBeam_*` ×2、`M05_EntryRoof` | 500×30×400 / 30×30×420 / 30×640×20 / 500×680×18 | 走廊净宽 610 |

### P0 · 灯具（47 个 PointLight 的可见载体）

| 待建模 | 当前 actor | 尺寸（cm） | 说明 |
| --- | --- | --- | --- |
| **吊灯笼（纸面 + 竹骨）** | `DYTheater_Lantern_L/R` | 球 60×60×90 ×7 每侧 | 现在是发光球，没有纸面、骨架、上下圈 |
| 吊绳 | `DYTheater_LanternCord_L/R` | 8×8×500 ×7 | 方块细柱 |
| 壁灯 | `DYTheater_Sconce_L/R` | 球 40×40×40 ×3 | |
| 路径灯 | `DYTheater_PathLantern_0..5_L/R` + `PathLamp_*` | 柱 34×34×250–286 ×12；灯球 30×30×34 ×12 | 沿路 6 对 |
| 檐灯 / 屋顶灯 / 门楼灯 | `DYExt30_EaveLamp`、`RoofLamp`、`GateLamp` | 球 66×3、50×3、115×2 | |

### P1 · 外景山海（当前是锥 + 球）

| 待建模 | 当前 actor | 尺寸（cm） |
| --- | --- | --- |
| 主山组 | `DYTheater_Mountain_0..15` | 锥 2600×2600×1800 ×16 |
| 山脊 | `DYTheater_Ridge_0..9` | 锥 3600×3600×1200 ×10 |
| 远山 | `DYExt30_RidgeFar_*`、`DYExt35_FarRidge_*` | 锥 2200 ×14、2400 ×6 |
| 中景山 | `RidgeMid`、`RidgeBehind`、`RidgeRight`、`RidgeRightFar`、`RidgeEast` | 1440×1500 ×8、2800×2400 ×3、1400×1600 ×6、1900×2600 ×4、2500×3100 ×4 |
| 山裙 | `DYExt33_Skirt_*` | 锥 4200×4200×780 ×8 |
| 枯树（干 + 冠） | `DYTheater_DeadTree_0..13` + `DeadCanopy_0..13` | 柱 62×62×620；冠球 417×374×310 |
| 树变体 | `DYExt12_Trunk/Crown`、`DYExt30_Snag/Lobe/Lobe2`、`DYExt31_Shrub`、`DYExt35_TreeTrunk/TreeCrown` | 锥 92×92×560 ×16、球 274–354 ×28、球 138 ×4、方 50×50×600 ×8 |
| 山石 | `DYTheater_Rock`、`DYExt30_Rock`、`DYExt31_Boulder` | 球 300×260×160 ×10、90 ×10、90 ×4 |
| 天穹 | `DYSky_Dome` | 球 26000（贴图渐变，基本可用） |

### P2 · 库里完全没有（要先做美术）

1. **精卫 / 刑天 / 烛龙 三具影偶**：关卡里只有一具 `BP_DYKuafuPuppet_Fitted`，四幕演出共用这具夸父网格；另外三具只有图鉴文字。这是叙事上最明显的缺口。
2. **锣鼓器乐与戏班道具**：堂鼓、大锣、小锣、钹、鼓架、戏箱、竹签与签架、台前桌案——V2.3 的非遗清单里有「锣鼓器乐」，目前只有新补的文字，没有任何实体。
3. **纸灯笼**：14 盏吊灯 + 6 盏壁灯 + 12 盏路径灯全是发光球，没有纸面、竹骨、上下圈。
4. **楹联 / 匾额**：现在只有一张 Plane（`ART_ZhuRiTitleGlyph`）当标题贴图。
5. **图鉴插图**：影偶图鉴现在纯文字，没有造型图、没有制作七步分解图。

## 3. 概念图需求（画这几张就能开工）

技术约定：UE 单位 cm、Z 向上、模型正面统一朝 **+X**（与角色前进方向、`SM_DY_LampBody` 一致）；贴图 2K PNG（`T_DY_*`，BaseColor / NormalDX / ORM 三张）；尺寸按上表实测值，允许 ±10% 造型夸张但**碰撞与投影面尺寸不能变**（`DEV_BackScreen` 幕面、台口柱、门楼净宽都参与玩法与构图）。

| 编号 | 要画什么 | 视角 | 必须标出的信息 |
| --- | --- | --- | --- |
| A1 | 影窗：幕框断面 + 幕布垂褶 | 正立面 + 上/下杆断面 | 幕面净尺寸 900×800、幕布离框距离、上下杆直径 |
| A2 | 台口：柱、梁、斗拱、檐口 | 正立面 + 侧剖 | 台口净宽、檐口出挑、与幕面关系 |
| A3 | 侧墙、壁柱、栏杆、台基、台阶 | 横剖（俯视）+ 侧立面 | 墙厚 50、壁柱 70 间距、栏杆高度 |
| A4 | 门楼与入场走廊 | 正立面 + 轴测 | 净宽 620（门）/610（走廊）、门楣高度 950 |
| A5 | 灯具三件套：吊灯笼、壁灯、路径灯 | 正面 + 侧面 + 发光面 | 灯笼 60×60×90、纸面色温、竹骨数量 |
| A6 | 地板与台基铺装 | 俯视纹理 | 板宽、板缝、磨损程度 |
| B1 | 山体三层剪影（近/中/远） | 正面剪影 | 每层高度、峰形差异、层间雾感 |
| B2 | 枯树：干、枝、冠 | 正面剪影 | 干高 620、冠径 417、枝分叉数 |
| B3 | 山石组合（大/小/苔石） | 45° 轴测 | 300 / 90 两档尺寸 |
| C1 | 精卫、刑天、烛龙皮影造型 | 正面平铺，1:1 | 关节位置（肩/肘/膝/翅节）、杆位、镂空处 |
| C2 | 锣鼓班子：堂鼓、大锣、小锣、钹、鼓架、戏箱 | 正面 + 侧面 | 鼓径、锣径、摆放关系 |
| C3 | 图鉴插图：四偶造型图 + 制作七步分解 | 版式 | 每格画面内容 |

> 逐张交稿说明（视图、必须标注的尺寸、建模判据、不要做什么、AI 提示词）见 `Docs/ART_CONCEPT_BRIEF_20261021.md`。
### 3.1 落地进度（2026-10-21）

- **A1 影窗：已落地（Run88）**。幕面 2 mm 薄 Cube（900 × 800，正面 x = 925，不投影）+ `M_DY_Cloth` / `MI_DY_ScreenCloth` + PIL 现生成的 2048² 布纹；框料按 A1 概念图：上下 16 × 924 × 12 朱漆、左右 16 × 12 × 800 深木、上卷杆 Ø12 / 配重杆 Ø10 带黄铜端帽与朱漆环、四角 44 × 44 黄铜角花，框料正面比布面凸 3 cm。见 `FORMAL_SHIPPING_20261020.md` §9.28、`THEATER_WORLD_V21_20261020.md` §11.33；真机 `Saved/Audit-2026-10-20-V21/ship88-w04.png`。
- A1 遗留两项，随下一批一起做：① 幕面 UV 仍是单张 BaseColor，没有 NormalDX / ORM；② M03 的旧幕框套件（`M03_Frame*`）仍与 A1 框共存于同一位置附近，等 A2 台口建模时一并收掉。
- **A4 门楼与入场走廊：已落地（Run91）**。先量旧灰盒：门楼柱心距 660 / 净宽 580 / 门楣 905–995 / 门槛 140 × 700 × 20、走廊墙心距 610 / 顶棚 500 × 680 × 18，与概念图逐项一致 → 不改槽位，只补 33 个构件（门楼两坡屋面 + 脊 + 翘头 + 匾额 + 楹联 + 雀替 + 门楣金线；走廊柱础条 + 墙帽 + 每侧 3 根壁柱 + 屋脊 + 4 条瓦垄）与青绿瓦材质 `MI_DY_RoofTileTeal`。见 §9.30 / §11.35。
- **A2 台口：已落地（Run89）**。两侧共 20 个构件：柱础（168² 基座 20 高 + 144² 础身 40 高，石材）、柱头 132² 托、三层斗拱（144 / 168 / 192 见方、各 18 厚，累计出跳 36，顶到横梁底 z = 1375）、额枋 8 × 1520 × 40 朱漆 + 8 厚黄铜带、柱梁交接黄铜板、两侧挂幕杆 10 × 300 × 10。柱础 60 高含在原 1400 柱包络内，柱位与台口净宽 1520 未动。见 §9.29 / §11.34。
- **A5 路径灯：已落地（Run90）**。12 根灯柱顶四件套：底圈 38 × 38 × 4（深木）、纸身 30 × 30 × 30（新材质 `MI_DY_LanternPaper`）、顶盖 40 × 40 × 6（深木）、顶饰 Ø5 × 7（黄铜）；两张 1024² 纸灯贴图（BaseColor + Emissive）由 `C:/dy_build/gen_lantern_tex.py` 生成后导入 `Dev/WorldV2/Textures`；旧发光球 12 个 `set_actor_hidden_in_game(True)` 保留。真机 `s90-w01.png` / `s90-w02.png`。
- A5 历史待调项已更新：Glow 已于 Run100 降为 1.7；门楼/檐下/屋顶 8 个球灯已于 2026-10-22 换为自制八角纸灯，共用 768 三角面网格、保留原 Transform 与碰撞；右侧装饰补光改为 650 cd。14 盏室内吊灯与 6 盏壁灯仍未替换，A5 尚未整体完成。详见 ART_POLISH_20261022.md。
- A4 待复核：门楼屋面在 50 m 外只有十几像素，游戏距离读不出细节；等 A3 墙体做立面浮雕时一起看近景机位。
- **A3 剧场围合：已落地（Run96）**。侧墙 / 壁柱 / 观众栏杆 / 台前墙 / 台后墙 / 台阶的槽位全部不动，只补表面层次：每侧墙四件（石墙裙 z 0–150、米白墙面 z 150–1580、黄铜压条 z 1584、朱漆上带 z 1580–1700）、16 根壁柱各加黄铜团花 + 柱头箍 + 石柱脚、栏杆补下横枋与 5 个黄铜柱头、台前 / 台后墙内表面加石墙裙 + 米白墙板 + 朱漆带、台阶改石；新材质 `MI_DY_PlasterCream`，共 82 个构件。见 §9.31 / §11.36。
- **A6 木地板：已落地（Run96）**。PIL 生成的 2048² 拼板贴图（板宽 40 cm、板长 160–480 随机、缝 0.8、错缝）+ `M_DY_WoodFloorPlank` / `MI_DY_WoodFloorPlank`，指派给 `DEV_Floor`、`M06_AudienceApron`、`DYTheater_Floor`、`DYTheater_FloorApron`；只换材质不抬行走面，真机 `s96-w04.png` 已见拼板缝。
- A6 待复核：地面拼板是贴图而非几何，近距离没有倒角与板高差；若将来有贴地机位再考虑每块板的几何。
- **A5 复调：已落地（Run100）**。纸灯 `Glow` 2.6 → **1.7**，纸身不再过曝、暖光仍透竹骨。
- **B1 山体三层剪影 / B2 枯树：试过、失败、已回退（Run97–Run100）**。山体做过三层 Unlit+Masked 剪影面片（`M_DY_MountainSilhouette` + 三张 PIL 现生成 alpha 贴图 + 6 块平面），枯树用圆柱段程序化分枝做过 290 个 actor；真机 `s99-w01.png` 证明两层都没成：剪影读成戏台上方一条青灰平板（Unlit 不接雾），分枝读成一排尖刺。`pass148_revertb.py` 已把 576 个 `ART_B1_*`/`ART_B2_*` 隐藏、328 个球形树冠恢复显示，actor 与材质留在工程里等真网格替换。见 §9.32 / §11.37。
- **B1/B2 的正确做法（下次开工照这条走）**：① 山体远景不要用 Unlit 面片，改用**接雾、参与光照**的分层（或直接做成天幕/背景图的一部分）；② 枯树必须是真分枝网格（本机无 Blender → 等外部建模，或改用「主干网格 + 挂枝 alpha 卡片」三视图折中）；③ 判定标准写死：远景色块必须与天空有大气透视差，否则一律不算过。
- 其余 B3（山石）与 C1–C3（三具影偶 / 锣鼓 / 图鉴版式）尚未开始，等待下一批建模；概念图位于 `Assets/Sources/DengYingArt/Concept-20261021/`（12 组共 24 张）。

## 4. 执行方式（概念图到位后）

1. 在 `Assets\Sources\DengYingArt\<批次>-<日期>\` 建目录，放 `.blend` + `build_*.py`（参照 `ForestBranch-20261016\build_branch.py`）。
2. Blender 内按上表尺寸建模，导出 FBX 到同目录。
3. UE Python 导入到 `Content/DengYingShanHai/Dev/<批次>/Meshes/`，赋 `MI_*` 材质。
4. 关卡里只 **替换网格引用**（保留 actor 的 Transform、碰撞盒、PointLight 挂点与所有玩法坐标），逐项截图对比后再存图。
5. 每次批量替换后跑 `verify_sfx.ps1` / `verify_replay.ps1` / `ci_run13.ps1`，避免动到四幕判定。

## 5. 不在本次建模范围

- 角色本体（`SK_DY_Reenactor_*`）与夸父影偶（`SK_DY_Kuafu_*`）已有可用版本，本清单不重做。
- 外景「山海」的美术改造此前已回退过四轮（pass44–pass52 的山肩/峰锥/地面石板均被判为更差），再改必须先出概念图，不再盲调。
- **B2 枯枝剪影：已落地（Run101）**。322 个 `MI_DY_TreeDead` 球冠换成 `SM_DY_BranchCrown_A/B_Unit100`（bounds 50 cm，scale = 原 extent / 50），旋转由标签字符和决定；剩余 6 个球冠是真灌木，保留。原先失败的程序化分枝 actor（`ART_B2_*`）仍隐藏留档。
- **B3 山石：已落地（Run101）**。17 块 `ART_B3_Rock_00..16`（Sphere，150–230 × 130–200 × 100–150 cm，20% 埋深，材质 `MI_DY_RockTex`），沿路缘与林下分布。待复核：近景石形仍是圆球，需要用真网格或再加棱角化处理。
- **C2 锣鼓与戏班道具：已落地（Run101）**。27 件：戏箱（100 × 60 × 55 + 盖）、案桌（160 × 65 × 8 + 4 腿）、堂鼓（Ø80 × 60 + Ø82 米白鼓面 + 4 腿）、大锣架（立柱 + 横梁 + Ø90 锣）、小锣 Ø35、钹一对 Ø30、4 根鼓槌；材质朱漆 / 木 / 黄铜 / 布面。待复核：锣片在暗部会读成黑片，需要给黄铜加环境反射或用更亮的 brass 实例。
- **B1 三层山体剪影：已落地（Run102）**。91 个 Cone 改挂 `M_DY_MountainFlat` 的三个分层实例（近/中/远 tint 0.075/0.105/0.150 + Glow 0.7/0.9/1.2，纯色自发光，不采样贴图）；半径 <5000 的 36 个近场尖峰隐藏；43 件远景按 label 哈希做确定性随机缩放与旋转；6 块 `ART_B1_Mountain_*` 平面确认无剪影 alpha，永久隐藏。**待复核/待升级：几何仍是 Cone**，需要真山形网格或带 alpha 的剪影卡片才能达到概念图的三层墨色轮廓。
- **C1 三具影偶：三维实体化放弃，改由图鉴插画承载（Run103/Run104）**。primitive 版试过一版（93 件方块影偶挂北墙，真机读成"乐高小人"），整批回退（删 96 件，actor 回 1651）——判断是皮影剪影必须真网格或 alpha 卡片，无 DCC 时 primitive 只会拉低观感。改为四张概念图裁切贴进结束页图鉴：夸父（绝对像素框 (300,255)-(898,898)，598×643）、精卫 962×607、刑天 798×724、烛龙 424×737，走 `DYDevEntryWidget` 的插图槽。**库里仍只有 `BP_DYKuafuPuppet_Fitted` 一具实体影偶**，精卫/刑天/烛龙不做关卡内实体。
- **C3 图鉴版式：已落地（Run103）**。16:9 版式放进图鉴页：标题带 + 左侧造型图（高 330，宽度按长宽比 Clamp 200–520）+ 右侧正文六段 + 四条影偶选择行（游标跟随 CodexIndex）+ 页脚提示；卡片定尺 1040×1000 + ScaleToFit。**待补：制作七步的图片版**（`art_steps.png` 1628×1202 已裁好），因卡片留给正文的宽度不足以让七格读清，暂以正文一行替代；要做需把图鉴改成二级页。
- 外景贴图与壁饰：已在 Run101 落地（6 张贴图 / 5 个世界坐标 UV 母材质 / 18 件外墙壁饰），详见 `FORMAL_SHIPPING_20261020.md` §9.33。
- 运行 102（B1 定稿）补充：山体材质四代（世界坐标 UV 采样 / 加自发光 / 自发光不乘贴图 / 纯色 Flat）+ 两组对照实验（全隐藏、全染红）证明「黑」是缺光与贴图基色过暗，不是材质没换；过程记录见 `FORMAL_SHIPPING_20261020.md` §9.34。
- 运行 105（树干树皮 / 灰泥 / B1 卡片二次失败）补充：树皮走**世界坐标 UV 贴图**（`M_DY_TrunkTex` + `MI_DY_TrunkTex`，Tile 220、Tint (1.05,0.95,0.82)），632 个树干全部换掉，入场视角树干出现木纹暖色；灰泥 `MI_DY_PlasterTex` 的 Tile 130→95、Tint (0.62,0.575,0.515)，墙面不再像细密网格。B1 又试了一版**三层墨色剪影卡片**（2048×1024 RGBA、Unlit+Translucent、8 张/层、半径 8.2/11.5/16 km、高 3.4/4.0/4.6 km）：9 个机位完全看不见，改 `BLEND_MASKED` 仍看不见，只有把 Tint 改饱和红 (3.0,0.2,0.2)、相机抬到 (2400,1629,1660) 才看到纯黑锯齿剪影 —— 结论是**远景雾 + 自发光链路**把卡片吃掉了，材质参数调不出来，已整批回退（删 24 张，actor 回 1651）。回退顺带把近场尖峰放出来，改由 `pass210_hidenear.py` 按「距 (200,0) <5200」隐藏 39 座、保留 47 座、6 块 `ART_B1_Mountain*` 平面永久隐藏 —— **回退脚本不能一律 unhide，隐藏集本身就是设计**。B1 后续若再动，仍应是真山体几何或"接雾的分层平面"，不是 2D 卡片。


## 运行 106 补充（2026-10-22）

- **B3 山石：已从球换成真棱面几何**。`SM_DY_Rock_{A..D}`（二十面体细分 + 顶点随机位移 + 每面摊平成独立三角做硬棱，900–3600 三角）经 `AssetImportTask` 导入，49 件石构件（`ART_B3_Rock_*` 17 + `DYTheater_Rock_*` 32）全部替换，缩放用 `get_bounds().box_extent` 反算。B3 从此不再依赖引擎 Sphere。
- **枝叶**：322 个枝冠 BaseColor 压到 (0.09,0.065,0.045)，夜里读成深色枯枝。真分枝枯树（`SM_DY_BranchTree_A/B/C`，7.7k 三角/棵）试过替换 592 树干，四机位判定更差（细黑刺、失体量），已回退；网格留在 `Dev/ArtPolish_20261022/Meshes/` 备用。
- **C2 已修**（Run108）：新建 `MI_DY_AgedBrassProp`（Metallic 0.6 / RoughnessLevel 0.52 / Pigment (0.78,0.58,0.26)）覆盖锣钹 4 件，另加 2 盏乐班暖点光；锣已是可读铜盘。
- **C3 七步图版：已落地（Run110）**。图鉴叶扩成五行，第 5 行「制作七步」在同一页内切换插图：`C3_CraftSevenSteps_v01.png` 绝对像素框 (0.0128W,0.105H)–(0.9846W,0.900H) → 1990×1085（裁掉顶部标题带与底部「每格 512 px」版式标注，保留 01–07 + 材料示例），导入 `/Game/DengYingShanHai/UI/Codex/T_DY_Codex_Steps`；插图框改「宽定高」(`ArtWidth=Clamp(WantHeight*Aspect,200,520)`、`ArtHeight=ArtWidth/Aspect`)，宽图不再压扁，七步图版落在 520×284。判定：不另起二级页，用第 5 行切换即可，行标签与焦点同步。
- **A5 观众厅吊灯与内顶（Run110）**：`ART_LGT_HallLantern_*` 7 盏 220→2600 cd（半径 900→1400）、`ART_LGT_HallWall_*` 6 盏 150→1200（700→900）；屋顶下补两块望板 `ART_A6_HallCeiling`（Plane 42×27 m，z=1865）+ `ART_A6_HallCeiling_Stage`（14×13 m，z=1830），材质 `MI_DY_HallCeiling`（Tint (1.10,0.96,0.80)）。抬头不再全黑，梁架之间读到暖褐木顶。**14 盏室内吊灯本体仍是 `SM_DY_LanternFamily_Unit100` 复用件**，纸面/竹骨细化未做。
- **仍未做**：A5 吊灯/壁灯本体细节（纸面、竹骨、上下圈）、外景润色（m14358）、人工体验验收。
- **B1 真山体几何：正式停止（Run113/Run114）**。两次尝试都失败并回退——① 三层 Unlit+Masked 剪影面片（卡片），看不出任何卡片；② 程序化山脊网格 `SM_DY_Ridge_A..F` + 20 个 `ART_B1_Ridge2_*`，Shipping 实机帧里变成头顶巨大白色碎片（朝向/尺度/光照全不对）。结论：无 DCC 条件下远景山体保留 Cone + `M_DY_MountainFlat` 分层墨色 + 按距隐藏（43 座可见 / 64 座隐藏），这是当前最稳的做法。详见 `FORMAL_SHIPPING_20261020.md` §9.45。
- 运行 114（B1 山脊二次失败回退）补充：编辑器 `take_high_res_screenshot` 一次 3 机位只落 1 张且构图常错，**不能当验收**；Shipping 实机帧是唯一可信通道。另记录 `is_hidden_ed()` 读不到 `set_actor_hidden_in_game()` 状态、`run_py.ps1` 是「WaitFile 一出现就 Stop-Process」两个坑。

## Run120 补充（门外匾额）
- 门脸正中原本只有三道上照灯池、没有可读物件；本轮用 Noto Serif SC Bold（OFL）生成 1024x320 的「燈影」匾贴图，做成 420x130 cm 的真实几何匾挂在 ART_EXT_RearBand 前 3 cm，4 根黄铜边框收边。
- 材质 M_DY_PlaqueBoard：BaseTexxTint→BaseColor、贴图xGlow(0.45)→Emissive，夜里靠自发光读字；Roughness 0.45 / Metallic 0.2。
- 首版（Run119）匾身 z=1330 落进檐影、实机只剩一条暗板，已作废；正确高度取自门脸构件枚举（墙 900-1900、门槛 950、横梁 1150）。

## Run121–Run128 补充（美术推进总览）

- **Run121/122 路面青石板**：重画 1024² 不规则石板（行高 84–142 px、板宽 96–236、缝 4 px、45% 磨角、26 条裂纹、冷灰偏色），覆盖 `T_DY_StonePathTex_BaseColor`；`MI_DY_StonePathTex` 的 `TileU/TileV` 170→**250**、`Tint`→(0.80,0.80,0.78)。Run121 首版放大后偏亮已作废，Run122 定稿。
- **Run123 门脸木格窗**：`pass314_lattice.py` 生成 26 件 `ART_EXT_Lattice_{L,R}_{Top,Bot,Left,Right,M1..M7,H0,H1}`（x=-1818、z 1250–1560、框 24×14 cm / 棂 16×5 cm、`MI_DY_FramePost_Wood`），补上门脸两跨 6 扇窗的棂条。
- **Run124 入口白片改嵌石**：`DYStageEnvironment.cpp` 的 `LayReadableEntry()` 原来用 `Plane` + `BasicShapeMaterial`（纯白、浮在路面 4 cm），改成 `Cube` + `MI_DY_StonePathTex` 的 MID（`Tint` (1.46,1.34,1.12)、Rough 0.94、Spec 0.02）、尺寸 224–236×114–119×**2 cm**、抬升 1.1 cm、`FRandomStream InlayJitter(20261022)` 抖动。
- **Run125 后台锣鼓曲面化**：`gen_props_c2.py` 写 11 个 OBJ（堂鼓桶身/鼓皮/鼓钉/鼓架、大锣/锣架、小锣、钹、戏箱/箱箍、案桌）→ `SM_DY_C2_*`；替换 23 件旧 `ART_C2_*` 基本体。材质真实路径：朱漆 `/Game/DengYingShanHai/Dev/WorldV2/Materials/MI_DY_LacquerVermilion`、木 `Dev/StageFrameM03/Materials/MI_DY_M03_FrameWood`、黄铜 `Dev/KuafuAppearance/Materials/MI_DY_AgedBrass`、鼓皮新做 `MI_DY_C2_DrumHead`（父 `M_DY_PlasterTex`，Tint (0.62,0.52,0.38)）。
- **Run126 影窗绢面 + 灰泥细化**：新贴图 2048×1820（暖米底 + 两组低频噪声 + **5 幅软竖缝** + 幅内鼓起 + 顶部两道折痕 + 16 个模糊污渍）覆盖 `T_DY_ScreenCloth_BaseColor`；12 幅硬直缝首版读作彩钢板已弃用。`MI_DY_PlasterTex` 的 `TileU/TileV` 95→**240**。
- **Run127 观众厅影偶挂屏**：`gen_frame.py` 生成空心框 `SM_DY_PuppetFrame`（160×230 cm、框条 12、深 8、**无背板**）；4 幅图鉴插画做薄 Cube 画面（scale (1.36,0.03,2.06)），x=-1430/-900/-370/150、z=**820**、左墙 y=-1269 / 右墙 y=+1269 yaw 180；`MI_DY_HallFrame_*` 父 `M_DY_PlaqueBoard`（Glow 0.20）；每屏一盏 120 cd / 半径 340 暖灯。
- **Run128 观众席长凳**：`gen_bench.py` → `SM_DY_AudBench`（沿 Y 420、深 40、座面 z 40–46、双段靠板 52–74/72–94）；4 排 × 2 侧（x=250/90/-70/-230、y=±560）+ 8 块朱漆坐垫（薄 Cube、z=52）+ 8 盏 320 cd 座位灯；中央走道 |y|<350 保持通畅。
- **通用教训**：材质路径写错时 `load_asset` 只返回 None，`if mat is not None` 会静默留默认灰材质 → 批量导入必须把材质解析结果打进 JSON；`set_actor_label()` 不改对象名，清理/统计按 `get_actor_label()`；≤2 cm 薄片必须离承载面 2–3 cm 并倾斜，否则斜俯视读作贴花。

## 2026-10-23 更新：C1 三具影偶已实体化并接入正式四幕

上文「C1 三具影偶：三维实体化放弃」是 Run103/Run104 当时的结论，现在已被推翻，保留原文作为历史记录。

- 三具影偶（精卫 17 骨 / 刑天 14 骨 / 烛龙 8 骨含眼睑）用 Blender 脚本从概念三视图生成真实厚度与几何镂空，最新为 Run4：16,024 / 8,168 / 8,028 三角面，99 / 33 / 32 个真实镂空，操杆已并入网格。
- 已导入生产库 `/Game/DengYingShanHai/Puppets`，`DA_DYPuppetCast` 四条目（夸父/精卫/刑天/烛龙），`ADYPuppetActor::ApplyChapterFigure` 按章节换偶，`ADYPuzzleDirector::ApplyChapterTitlePlaque` 同步换题签。
- 打包验证：`Builds/FormalMain-Development-20261023-RunD7`（补了 `DirectoriesToAlwaysCook` 才把资产 cook 进去），实机「演出篇章」逐幕进入已拍到精卫/刑天/烛龙与对应题名。
- 详见 `Docs/THREE_PUPPETS_MODELS_20261022.md` 第 10 节、`Docs/FOURACT_CAST_20261022.md` 第 7–9 节、`Docs/ART_AUDIT_20261022_FOURACT.md` 第 7 节。

仍未完成：公开 Shipping 入口仍是 Run143（未用新资产重打）；四幕完整通关需真人用键鼠走一遍。
