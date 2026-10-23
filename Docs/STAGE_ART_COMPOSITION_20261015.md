# 《灯影山海》独立 Dev 美术组合图

日期：2026-10-15。唯一人类作者及负责人为用户，Codex 辅助实施。状态：**技术接入通过，整场美术未验收，未更新正式游戏包。**

## 本轮实际成果与打开位置

- 新地图：`D:\灯影山海\Content\DengYingShanHai\Dev\StageArtComposition\Maps\LV_StageArtCompositionLab.umap`。
- 新灯具表现：`D:\灯影山海\Content\DengYingShanHai\Dev\StageArtComposition\Presentation\BP_DYHeroLampRig.uasset`。
- 实际 PIE 图片目录：`D:\灯影山海\Saved\Audit-2026-10-14-ArtAppearance\StageCompositionCapture-Run3`。
- 建议先查看 `04_Mid_Oblique.png`（原光照）与 `10_Wash90k_Oblique.png`（仅临时 PIE 补光，不在保存的地图中）。`02_WholeTheater.png` / `09_Wash90k_Whole.png` 是同样边界的全景对比。

这是当前 FrameBeamTopUV 戏台的独立 Dev 副本，不是额外的正式关卡。UE Content Browser 的地图路径为 `/Game/DengYingShanHai/Dev/StageArtComposition/Maps/LV_StageArtCompositionLab`。本轮没有加入菜单/重演的精确 C++ 地图白名单，**不要把它当成已完成的新双击试玩入口**。旧启动器、旧包仍显示原版本，不会自动显示本轮美术。

## 实现：只换表现，不重写玩法

新灯 BP 直接继承 `DYLightRigActor`。原生 SceneRoot、LampBody/LampStand 查询碰撞、KeyLight、LightControl 都保留。仅隐藏旧 Body/Stand 图形并关闭其阴影，新增两个 Movable / NoCollision 显示组件，直接挂 SceneRoot：Body identity，Stand local Z=-95cm，均 unit scale，使用现有两网格的全部 6/5 材质槽。无 Tick、BeginPlay 更新图、新委托、控制逻辑或管理器。整个 Actor 继续沿原轨道移动。

复制图内的灯与偶实例保持原 Actor 中心、旋转、缩放、Tags 和作者控制参数；皮影使用已准入的 `BP_DYKuafuPuppet_Fitted`。只重接同图 `PuzzleDirector.LightRig` 与 `PuzzleDirector.PuppetActor`，不依赖 `convert_actors` 的引用副作用。Stage、Environment、Forest、Audio 和三个 Guide 的原有关系保持。Source 图没有 StaffProjectionProbe 实例，防止遗漏该类额外引用。

| 保持的合同 | 实际值或验证 |
|---|---|
| 灯原中心 | (-460,-20,310)cm；KeyLight local(45,0,0) |
| 灯轨 | world(0,1,0)，600cm，初值 .15，速率 .2625 |
| 偶原中心 | (600,-80,210)cm |
| 偶轨 | world(0,1,0)，320cm，初值 .15，速率 .28；原三 PoseId |
| 主灯 | 原 Movable Spot、30000lm、2200cm衰减半径、20°/38°、SourceRadius4cm、原色、真实投影 |
| 玩法 | E/A/D/R、15Hz、谜题定义、持续判定、地线Z70、Staff A/B因果规则不改 |
| 非替换 Actor | 原 33 Actor 的观察合同及 Pawn/Flow逐值保持；原35替换两件后再增加两帷幕，共37 |

三个 Guide 仍是旧灰盒轮廓参数，**没有随新夸父外形自动对齐**。本轮没有将保持 Guide 引用当成新目标提示已验收。

## 两片厚台翼的真实比例

保留现有主投影幕、柱梁和旧屏风，新增两个被动 StaticMeshActor，使用已准入的厚帷幕及 Cloth 实例。根据冷读的地板顶面0、梁底800、主幕半宽450和真实源bounds计算，等比2.8592667144，Yaw90，无反向缩放、非均匀拉伸或碰撞阻挡。

两者世界X范围约848.1666–920.0379cm、Z0–800cm；左Y[-849.1286,-475]、右Y[475,849.1286]。内沿在既有核心操作范围Y±470之外5cm，外沿仍在边界内面Y±850以内。原2.8m帘被放大适配8m灰盒戏台，这是 Dev 比例候选，**不等于真实建筑尺度或织物纹理密度已通过**。

静态网格 Actor 会继承 mesh 的外部默认碰撞；只 SetCollisionEnabled 不足。实际失败后按项目已有方式显式设 NoCollision profile、全部通道 Ignore、关闭 overlap，读回 `use_default_collision=False` 后才保存。没有降低验收条件。

## 实际运行与图像证据

灯 BP 创建、独立冷加载；新图的原生组合保存、独立冷加载；最终真实 PIE 捕获均完成，最后这些独立进程实际退出码0，结果也明确 success。源35 Actor、组合37 Actor，实际冷读合同等于创建后的合同；不是只凭文件存在声明成功。

最终 `StageCompositionCapture-Run3` 实际生成十张1536² PNG，PIE确已结束，411个产品文件哈希/集合不变，无产品保存。前六图与主执行者已经逐张查看的Run2六图字节完全一致；主执行者另打开查看Run3的Off及三张补光图，覆盖最终全部十张的实际画面。

1. 第一图读取实际 PlayerCameraManager 的位置、旋转、FOV，再由独立 SceneCapture 拍摄；没有切 ViewTarget、移动玩家或接管最终POV。
2. 第二图以实测灯/偶/幕/柱梁/台翼bounds校验全景入画；三种姿态通过既有公有Control setter驱动，在真正BeginPlay后核对实际SingleNode资产、Pose缓存、世界位置、骨和Staff A/B。
3. 第六/七图固定Mid几何与构图，仅将真实主灯Visibility开/关。解码后有202392/2359296像素变化超过8灰阶，约8.5785%。证明主灯确实影响画面，不冒称已经隔离全部阴影贡献或通关。
4. 最后三图仅在PIE RAM增加两个无投影Movable Point工作灯，位置(450,±620,650)cm，SourceRadius20cm、Attenuation1100cm，比较每盏30000/90000lm。主投影灯与世界Manual/physical-camera/+3.5曝光不变；两灯IndirectIntensity=0。结束随PIE销毁，**未保存进地图**。
5. 全部图使用同步 ImageWrite，逐块CRC与IEND零尾部检查；主灯Off图接近全黑是预期实验结果，仍严格检查容器、解码和像素，不适用美术图“必须非黑”的条件。未用旧PNG helper导出含内存尾部的图。

限制：1536方图不是玩家视口比例、UI或PlayerCameraManager完整后期效果的逐像素复现。自动Control setter不代替人工按键、首次游玩、三幕通关、重演、成林、GPU/FPS或打包验收。

## 视觉 QA 结论：未通过正式美术验收

- 新夸父与真实木杖、幕上影子已能在实际场景同时出现；三姿态都形成相应影子，本组未见孤立耳蛇碎影，不外推到全部灯位。
- 原光照下灯体、台翼、柱梁与空间层次明显过暗；不能以“渲染成功”签认高质量场景。
- 90000lm临时补光使梁、地板、幕面和阴影更易辨认，但侧帘仍暗，灰盒障碍、柱/框不完整和幕面亮斑很显眼。不能通过继续全局提亮掩盖，应先分离实际材质/法线/曝光与遮挡原因，再做有边界的环境照明。
- 皮影平片媒介特征明确，但握杖手指的前后交握线索、操作载体占位模型、帘与主幕比例及正式演出构图均未验收。
- 两档补光都只作对比，不直接采用正式方案，不修改旧图或既有主灯参数。

## 失败与回退保留

原409产品未变；新增灯BP后410，新图后411，本记录发布后412。第一次new_level_from_template保存了原始克隆，组合检查失败并未保存后续改动；随后每次都先备份这张本轮新图，验证仍与原始源观察合同一致再恢复制作。有效组合是 `StageCompositionPopulate-Run3`，冷读 `StageCompositionVerify-Run1`。

两项工具/接入缺陷如实保留：最初将Unreal Color包装对象直接用Python相等比较误判；最终实际RGBA8读回 source/new_before/new_after均[255,229,191,255]，不是发现了新灯色差。另一项为前述mesh默认碰撞覆盖。源码、输入、正式光照没有为通过断言而改。最初捕获脚本用了未公开的Controller.get_pawn，改为本机公开GameplayStatics.get_player_pawn；Run2主灯Off被错误套用非黑门，最终按意图分离完整性与美术亮度检查。失败证据未覆盖。

当前可运行的旧FrameBeamTopUV入口继续保留。新图的原始模板备份位于 `Saved/Audit-2026-10-14-ArtAppearance/StageCompositionPopulate-Run3/Before-PristineTemplate.umap`；不会自动覆盖当前组合或删除文件。无Git写操作，无新下载/付费资产，无系统或全局环境修改。

## 接下来继续

由Codex辅助用户依次完成：剧场定向照明与帘面暗色根因检查、用场景结构替代测试障碍/完整幕框，再适配新皮影的目标提示和成林美术；保持一个戏台、原输入和因果规则。视觉通过后才接新图精确菜单路径/测试、真实可玩回归、Development/Shipping与录屏，不把本轮模型组合图当比赛成品。

本轮ponyTail原则使改动限于一个静态表现BP和一张副本；Blueprint技能限定显式引用/组件所有权；Lighting与Camera技能使补光保留原曝光、以真实距离/单位对比、只读玩家POV，不新增镜头系统或渲染框架。
