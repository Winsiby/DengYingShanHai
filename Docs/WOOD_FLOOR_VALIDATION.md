# 木地板 Dev 试片｜验收记录

记录日期：2026-10-11。项目负责人及唯一人类制作作者：项目作者本人；Codex 负责本轮集成、验证与记录。

**当前状态：木地板 Dev 样本的材质冷读、154 项原生测试、固定机位完整两轮、声音/环境、真实操纵、独立 Windows Development 打包、实际首帧和四项启动器 DryRun 均通过。** Codex 已完成五态及实际包标题画面复核；最终既有文件/旧包/本轮资产保护结论以审计根 `FINAL.json` 为准。作者人工视觉认可、包内物理键鼠通关、最终剧场美术、性能与 Shipping 尚未验收。保留初版黑地板与 VisiblePlay-Run1 失败记录，不将修复覆盖成从未失败。

## 1. 本轮可见目标与冻结范围

目标仅为：现有 Dev 地面不再是默认灰盒表面，出现可信的旧木板、板缝、细法线与粗糙反射，并且不遮蔽幕布、交互对象或第三幕因果链。

唯一既有内容变更：`Content/DengYingShanHai/Dev/EnvironmentStates/Maps/LV_EnvironmentStatesLab.umap` 中 `DEV_Floor` 的材质槽 0。新增三张 2K 纹理、一个地面父材质和一个实例，准确路径见 `WOOD_FLOOR_SOURCES.md`。附属 authoring、审计、打包、启动和来源文档按本轮显式白名单记录，不扩大内容变更范围。

冻结全部既有 Actor 数量、类型、Transform、网格、碰撞、阴影标志，以及 GameMode、输入、UI、镜头、灯光、曝光、音频、皮影、谜题、落杖与成林。尤其保持 15 Hz、移动速度 360 cm/s、脚步步距 150 cm、灯/偶速率、容差、1.25 s 保持与 2 s Dev 切幕。不得用调灯、调曝光、移动玩家起点、重缩幕布或修改谜题来掩盖材质问题。

## 2. 已有场景的尺寸事实与空间风险

以下来自既有 `Audit-2026-10-11-ActEntryControlReset/ColdVerify-Run1/Result.json` 的冷加载 Actor 合同与原始灰盒生成脚本。它们是本轮保留的基线，不是正式剧场规格。

| 对象 | 位置/缩放（UE cm） | 实际空间意义 |
|---|---|---|
| `DEV_Floor` | 位置 `(0,0,-50)`；Engine Cube 缩放 `(24,18,1)` | 地面为 24 × 18 m、厚 1 m；X[-1200,1200]、Y[-900,900]、Z[-100,0]，上表面 Z0；碰撞保留 BlockAll |
| `DEV_BackScreen` | 位置 `(950,0,350)`；缩放 `(.5,9,8)` | 厚 0.5 m、宽 9 m、高 8 m；朝灯表面 X925，Y[-450,450]、Z[-50,750]；不得套用未来正式文档的 5–6 m 幕布宽度缩放 |
| `DEV_PlayerStart` | `(-900,-210,120)` | 既有出生位置；本轮不新增入场路程 |
| 主灯/皮影编辑器原点 | 灯 `(-460,-20,310)`，偶 `(600,-80,210)` | 既有 Y 轴轨道与运行位移照旧；编辑器原点不是任意时刻的运行坐标 |
| 幕上叙事地线 | `(925,0,70)` | Z70 是既定杖尖投影接触线，不是实体地板高度；不可随木纹或地板视觉改变 |

既有真实控制诊断 Run3 曾让角色通过正常 `Pawn.ApplyMoveIntent` 前进 1037.15 cm，到 `(144.91,-193.64,98.15)`，与当时皮影 `(600,-192,210)` 距离 468.64 cm，在 700 cm 聚焦半径内进入真实操纵会话；无传送。这证明该次诊断路径可达，不替代本轮回归，也不宣称物理键盘 WASD/E 已被自动化验证。

现有 `DEV_CameraWall`、拐角、低顶、台阶属于早期相机/碰撞夹具，不等于剧场壳体已完成。增加墙柱会影响 360 cm 相机臂收缩、Visibility 聚焦射线和主灯投影，因此本轮不增删或重排这些对象；空间候选仅记录，不实施。

## 3. 证据与执行结果表

本轮审计根：`D:\灯影山海\Saved\Audit-2026-10-11-WoodFloor\`。下表路径均相对该根。已经生成的报告按真实结果登记；未生成的路径仅为后续目标，不代表通过。修复后的完整流程证据为 `VisiblePlay-Run2`，不是已失败的首轮目录；最终作者脚本冷验为 `ColdVerify-Run3`。

| 项目 | 验收条件 | 记录状态/证据 |
|---|---|---|
| 基线与回退 | 既有文件 SHA256、获准地图备份、原始七份来源文件清单；不读取受限 `Docs/LICENSES.md` | `BEFORE.json` 冻结276个既有产品文件和769个旧归档文件；唯一允许既有变更为地图、TECH_SPEC与DEVELOPMENT_PLAN三项，备份位于 `Before/`。七份来源见 `RAW-SOURCES.json`。发布后保护清单、准确变化数与结论以 `AFTER.json`、`FINAL.json` 为准；Git不写、不提交、不清理 |
| 只读 Probe | `success=true`、`saved=[]`；真实 Floor bounds/mesh/槽/BlockAll、原有场景合同及反射 API | `Probe-Run1/Result.json`：`success=true`、`saved=[]`，bounds origin=(0,0,-50)、extent=(1200,900,50)，实际 Mesh=/Engine/BasicShapes/Cube.Cube、BlockAll、QueryAndPhysics、cast_shadow=true |
| 五资产创建 | 只创建精确五个新包；原资产不覆盖；地图只保存 Floor 材质槽 0 | 历史目录 `Create-Run1/Result.json`；初版虽编译无错误，Slab 路线失配导致黑地板，不视为有效材质通过 |
| 渲染路线检查 | 读取真实 Console Variable 和标准输出，不以节点可创建推定启用 | `RenderInspect-Run1/Result.json`：`r.Substrate=0`；标准 BaseColor/Normal/Roughness 输出原为空；只读 `saved=[]` |
| 有界材质修复 | 仅保存自己新建地面父材质；标准 BaseColor RGB、Normal RGB、Roughness G、AO R、Metallic0/Specular0.5；不改 Config/light/exposure | `MaterialRepair-Run1/Result.json`：`success=true`、实际标准 PBR 验证、`shader_errors=[]`；只保存 `M_DY_WoodFloor_Master` 一包；`EXIT.json` 实际 0 |
| 最终新进程冷加载 | 三纹理 2048²、sRGB/压缩/采样符合来源语义；实例真实父材质和 Floor 槽绑定；全场景合同仅允许该槽不同；核验实际启用的标准 PBR 输出；作者脚本不依赖旧 Saved 合同 helper | `ColdVerify-Run3/Result.json`：`success=true`、`saved=[]`、`root_bsdf=StandardPBR`、`substrate_enabled=false`、`standard_pbr_verified=true`、`front_material_root=null`、`shader_errors=[]`、`floor_material_only=true`；`EXIT.json` 实际 0。最终 `Create-WoodFloorDev.py` 的场景合同 helper 使用当前项目 `Scripts/Create-EnvironmentStates.py`，不再依赖旧审计 Saved 内的 `Cold-ActEntry.py`；ColdVerify-Run2 留作先前修复冷验记录 |
| 原生回归 | 本轮完整原生测试数、通过数、失败数与退出码；不把旧轮结果当成本轮结果 | `Native-Run1/RESULT.json`：154 succeeded / 0 failed / 0 notRun，`ActualProcessExit=0`，Expected=154；不代替材质画质或完整动态验收 |
| 首轮完整流程尝试 | 固定实际最终 POV 的五态截图及完整两轮流程 | `VisiblePlay-Run1/Result.json` 与 `ENVIRONMENT_RESULT.json` 为 **FAIL**；仅31项普通检查，第三幕因 `ActualPOV` 固定机位断言失配中止，未完成成林；虽然 `EXIT.json` 为0也不能视作通过；黑地板截图视觉不通过 |
| 修复后完整两轮流程 | 正常开始、三幕、真实落杖、接触、15 枝灰盒成林、结束、重演和退出；固定 POV 断言不放宽 | `VisiblePlay-Run2/Result.json`：**PASS，65 项普通检查、40 张 PNG、2 次实际成林**；`saved_assets=false`、`package_tested=false`、`physical_keys_verified=false`；`EXIT.json` 实际0。未沿用失败轮的检查或黑地板截图 |
| 五态与真实重演 | 环境状态由实际阶段事实驱动，不直接 ApplyState 或驱动演出，不移动比较镜头；真实 OpenLevel 后新世界重演 | `VisiblePlay-Run2/ENVIRONMENT_RESULT.json`：**PASS，35 项环境检查、2 次实际成林、1 次真实地图重演**，`no_camera_writes=true`、`no_environment_set_state_calls=true`、`no_cue_drivers=true`、`no_asset_saves=true`；真实五态固定最终 POV 要求保留 |
| 声音/静音数值回归 | 记录游戏 Master 两轮 PCM，音频语义与真实阶段保持；静音不是只关闭测试播放器 | `VisiblePlay-Run2/AUDIO_RESULT.json` 与 `MIX_QA.json` 均 **PASS**；两个48kHz、双声道、16bit PCM：Cycle1 70.70 s、非零波形、peak≈0.23068、rail_clips=0；Cycle2 61.97 s，8 s 尾音等待后的静音导出 peak/rms/nonzero 均0。`ear_audition_verified=false`、`os_output_verified=false`；不是桌面声卡输出或耳听验收，不作为 LUFS 匹配结论 |
| 跨幕操纵回归 | 真实聚焦后 E 语义进入；跨幕解除、同幕 R 保留、重复同步不解除新会话、结束清理；真实 LocalPlayer Mapping Context | `ControlProbe-Run1/CONTROL_RESULT.json`：**PASS，41 项检查、8 张 PNG、12 条真实 Mapping Context 检查、4 次跨幕释放（包含灯与偶）、6 次真实 E 语义重新进入、2 次同幕 R 保留、2 次实际成林、1 次真实重演、cleanup.verified=true**；`EXIT.json` 实际0。此独立诊断实际临时 aim 并正常行走，`no_camera_writes=false`、`player_walk_performed=true`、`pawn_teleported=false`；输入/相机资产未改，不冒充固定机位或物理按键验证 |
| Codex 五态视觉复核 | 历史灰盒与新木地板在相同实际最终 POV 比较，不只登记文件存在 | `VISUAL_REVIEW.json`：**PASS-DEV-SAMPLE**，Reviewer=`Codex visual inspection, not human author acceptance`；Dormant/Sun/Chase/Finale/Forest 五组 `FinalPOVEqual=true`，已保存各对图片路径/哈希。木纹及板缝正常可见，粗糙木材反射较旧灰地板镜面响应收敛，幕影、P02 提示与 Z70 接触/成林可读；`HumanVisualAcceptance=false`，不是作者人工认可 |
| Windows 包 | 本轮独立 Development 包，显式指定当前 Dev 入口；五个新包进入实际 UFS；源码/资产/报告快照匹配 | `Package-Run1/EXIT.json` 实际UAT退出0；包为 `D:\灯影山海\Builds\WoodFloorDev-20261011-Run1\Windows`。冻结86源文件、37源资产和68项验证输入；五个新材质/纹理均在UFS；49个归档产物共1,054,193,406字节，另有冻结身份JSON。实际原生EXE SHA256=`5CDCC2BA470B69FFE0732349CA0CB9C93C00A7DBCE8AD56CF22D194079FFBA77`（本轮无C++变化） |
| 原生首帧 | 真正启动打包EXE，目标地图、尺寸、身份及UE原生定时退出正确；不以首帧代完整玩法 | `FirstFrame-Run1/RESULT.json`：PASS、实际1280×800、退出0、目标EnvironmentStates地图，原生20秒定时退出原因为 `FEngineLoop::Tick.Benchmarking`；`01-Title.png` 已查看，中文菜单和木地板正常。`FullGameplayVerified=false`、`PhysicalKeysVerified=false`、`AudioCaptureVerified=false` |
| 启动器 | 独立入口Auto/Package/EditorGame/CMD实际PS5.1只读DryRun；旧入口不升级 | `Launcher-Run1/RESULT.json` PASS，4条路径实际退出均0，Auto/Package/CMD选择固定新包，EditorGame含-game且使用当前源码；没有启动游戏、执行Python或改变全局环境。新 `Start-WoodFloorDev.cmd` 不调用任意“最新包” |
| 人工视觉反馈 | 作者在新版中核验典型机位、五态地面、反射/木纹、幕上影子可读性 | 待作者实际体验；技术通过不代勾 |

运行中的测试报告不允许只依据退出码 0 推导所有断言通过；须核对报告结果、计数、失败项、来源快照和本轮进程实际输出。未测试的 Shipping、目标外电脑、最终 5–8 分钟体验不在本轮结果中冒充已验收。

实际 Cook 命令只显式指定 `LV_EnvironmentStatesLab`，但 UFS 仍包含原配置依赖的 `Dev/Interaction/LV_InteractionLab.umap` 和引擎 `Maps/Entry.umap`。因此不宣称物理包内只有一个 `.umap`；本轮没有创建新地图或新增玩家可探索场景，启动器及实际首帧都固定加载 EnvironmentStates。正式发布前的 Dev 引用/Cook 清理仍是后续独立任务，本轮不改 Config 或删除旧地图。

身份JSON记录打包当时尚未首帧/人工体验的状态，保持冻结；后续首帧的真实PASS记录在独立审计目录，不通过改写包身份文件伪造包级全流程验收。

### 首轮诊断保留原则

初版 Slab 的创建和编译成功只证明节点接口可用，未证明当前渲染路线启用。`RenderInspect-Run1` 读取真实 `r.Substrate=0`，标准输出为空，解释了全黑地板；故只修本轮新增父材质，不开启 Substrate、不改环境或照明来掩盖错误。修复后先由新进程 `ColdVerify-Run2` 验证标准 PBR，再以 `ColdVerify-Run3` 冷验最终作者脚本；首版 `ColdVerify-Run1` 不作为当前有效材质的最终证据。

`VisiblePlay-Run1` 的失败原因是第三幕取五态对比图时实际 POV 偏离已保存的固定机位，测试在该断言处中止；首轮未验证实际成林、第二轮或终止清理。不据此断定游戏存在成林故障，也不猜测是谁转动了镜头，更不推断作者人工体验已通过。失败报告、截图和日志保留；重测保持同机位要求，不放宽断言、不把控制诊断的正常 aim/walk 当作五态比较截图。

修复后 `VisiblePlay-Run2` 的完整两轮与五态固定 POV 已实际通过，不撤销或改写首轮 FAIL。独立 `ControlProbe-Run1` 另行验证真实交互会话，允许诊断过程中正常瞄准和步行，因此其 `no_camera_writes=false` 不与固定机位回归的 `true` 混用，也不构成修改产品相机资产。

## 4. 材质冷读与同机位视觉检查

最低技术合同：Surface、Opaque、Default Lit、单面、切线空间 Normal、**标准 PBR 父材质**；实际 `r.Substrate=0`，Front Material 无 Slab 根。Diffuse sRGB 的 RGB 接 BaseColor；NormalDX 线性 NormalMap 的 RGB 接 Normal；ARM 线性 Masks 的 G 接 Roughness、R 接 Ambient Occlusion；标准 Metallic=0、Specular=0.5（介电 F0=0.04）。无 Emissive、WPO、位移、透明层、运行时材质写入、新增静态参数组合或外部插件，不修改项目 Config 或渲染路线，不新增灯具或调整曝光。

`TilingU=12`、`TilingV=9` 只登记为 **候选 UV0 平铺参数**；Cube 顶面 UV 轴和真实板宽尚未核验，不能写“精确 2 m 物理尺度已通过”。需要从实际画面评估方向、大小和重复节律，如有纹理问题，只在获准材质范围内修订，不能改灯位、相机或网格绕过。

固定同一 POV、曝光、灯位、画质和窗口分辨率，登记旧灰盒参考与新样本的实际截图路径。检查：

1. 木纹/板缝不过大或过密，不出现明显棋盘、默认材质、条纹闪烁、法线反向或长距离糊块；近、中、远观看尺度合理。
2. Dormant 仍能读出可行走地面；Sun/Chase 的暖光不把地板变成油亮塑料；FinaleReady 不提前夺走杖尖焦点；ForestComplete 不剪切高光或盖住幕影。
3. 舞台依然是视觉主焦点；地板重复、磨损和反射服务层次，而非抢眼。地面间接反射可能改变环境观感，光照冻结并不保证颜色亮度像素完全相同，必须看真实阴影可读性。
4. 原有灯影实时性、P02 贴合提示、Z70 地线与 A 端接触点不变；五态图仍按本轮固定机位契约取得，不把有临时 aim/walk 的控制诊断截图当成固定 POV 比较。
5. 保存 Shader Complexity/材质编译统计、目标硬件与分辨率、可获得的同机位 GPU/内存数据；没有实测时写“未测”，不由三张 2K 或少量节点推断性能达标。

原始 PNG 总下载体积不等于运行 GPU 占用；导入压缩、Mip、流送与 Cook 结果以实际报告记录。没有透明重叠和 WPO 不代表新增材质成本为零。

### 已完成的 Codex 视觉比较

历史参考根为 `D:\灯影山海\Saved\Audit-2026-10-11-ActEntryControlReset\VisiblePlay-Run3\`，新试片根为本轮 `VisiblePlay-Run2\`。`VISUAL_REVIEW.json` 对五组图片登记历史与新图完整路径、SHA256 和实际最终 POV 数值一致性，文件名如下：

| 状态 | 两轮对应文件名 |
|---|---|
| Dormant | `02-Environment-Dormant-FixedPOV-Cycle1.png` |
| SunAwakened | `06-Environment-SunAwakened-FixedPOV-Cycle1.png` |
| ChaseAwakened | `15-Environment-ChaseAwakened-FixedPOV-Cycle1.png` |
| FinaleReady | `21-Environment-FinaleReady-FixedPOV-Cycle1.png` |
| ForestComplete | `23-Environment-ForestComplete-FixedPOV-Cycle1.png` |

Codex 已查看这五态：标准 PBR 修复后 Dormant 也能看见木纹与板缝；暖色环境状态仍保持幕布焦点和真实影子；旧灰地面的大片镜面观感收敛为粗糙木板响应；P02 贴合提示与 Z70 接触/成林仍可读。该结论只认可本轮 Dev 样本的可见效果，不认证正式剧场、夸父资产或最终竞赛画质。

尚未验证的项目明确保持为：**真实 GPU/内存性能、Cube 顶面物理 UV 轴/板宽与精确尺度、Shipping、作者人工视觉认可、操作系统输出/耳听混音**。不存在上述证据时不得由截图、PNG数量或标准 PBR 技术通过推断达标。

## 5. 建筑风格、完成边界与回退

此次木地板既不选择院落建筑，也不把场景扩为大型剧院。用户的空旷大型剧院要求目前仅保留为声场体验要求；GDD 的小剧场与院落戏台候选仍需在后续空间设计中区分。禁止将该试片写作入場短廊、幕后、台翼、台前、远景或正式夸父形象已完成。

旧 `Start-EnvironmentDev.cmd` 和 `EnvironmentDev-20261011-Run2` 包保持不变；本轮独立新入口目标为 `D:\灯影山海\Start-WoodFloorDev.cmd`，最终仅在独立包及门控完成后交付。失败时保留诊断证据，继续使用旧已验收包演示；编辑器源地图回退须使用真实备份并重新核验，不能把被改过的源地图当作旧包的视觉版本。

阶段结论：首个免费木地板集成样本的技术验收通过，已形成独立可双击入口 `D:\灯影山海\Start-WoodFloorDev.cmd`。本轮只替换地面材质槽并新增五个材质/纹理资产，主灯、幕布、偶、谜题、声音、镜头和跨幕操纵规则保持。旧 `Start-EnvironmentDev.cmd` 仍打开既有灰盒包作比较。没有删除文件、提交Git、改系统权限或读取受限许可登记表。

这不是正式戏台美术完成：仍需作者实际体验木纹与反射，随后逐项推进同图戏台框架/台翼和叙事道具的免费资产集成。UV物理尺度、真实GPU性能、包内物理键鼠完整通关、首次玩家5–8分钟盲测、正式夸父/皮影形象与Shipping仍未认证；不以本轮原生首帧或脚本回归代替这些项目。
