> 历史阶段草稿：已由 [GATE_REPAIR_20261025.md](D:/灯影山海/Docs/GATE_REPAIR_20261025.md) 替代。以下待项反映当时进度，不代表当前状态；Run171现已完成本轮候选视觉与正式公开入口烟测。

# 灯影山海门楼修复交付草稿

**状态：门地图、Development/Shipping两包构建、PIE辅助穿门、5条胶囊冷验和三份候选流程已核实。候选独立门外图片受Windows防火墙权限弹窗阻挡，等待用户处理；正式入口烟测待完成。本文件仍为阶段草稿，不是Run171正式发布验收。**

任务基线为2026-10-25，本文记录时间为2026-10-26 00:19:08（北京时间）。虽然已跨日，候选命名保持 `FormalMain-Development-20261025-RunD14` 与 `FormalMain-Shipping-20261025-Run171`，不改包名。唯一人类作者与最终责任人为用户；Codex提供程序建模、UE集成和核查辅助，不列为制作成员。

## 已保存的实际范围

[Gate-Apply.json](D:/灯影山海/Saved/GateRepair-2026-10-25/Attempt1/Gate-Apply.json)记录 `ok=true`、`saved=true`，Actor从1806到1809：恰好修改13个既有Actor、新增3个Actor。脚本对两份名单作精确断言，报告没有白名单之外的Actor变化；这不是打包或通行通过证明。

| 既有Actor | 数量 | 本次实际修改 |
| --- | ---: | --- |
| `M05_EntryBeam_Rear`、`M05_EntryBeam_Front` | 2 | 隐藏原横木，并将其网格可见性关闭、碰撞设为NoCollision，避免仅视觉隐藏仍挡路。 |
| `M05_EntryRearGuard` | 1 | 从Z35降至Z4，Z缩放0.7改0.08；复用现有 `MI_DY_RockTex`。PIE辅助CharacterMovement已跨过该处；包内独立手动/反向通行不在本证据范围。 |
| `DYTheater_GatePost_L/R` | 2 | 换用本次新实例 `MI_DY_GatePostWood`；实例继承AudienceWood，写入 `UVQuarterTurn=1`，不改原共享母材质。 |
| `DYTheater_GateLintel`、`ART_A4_GateRoof_Front/Rear`、`ART_A4_GateEaveTip_L/R` | 5 | 改用已有 `M_DY_AudienceWood`，统一门头、屋檐木件外观。 |
| `ART_EXT_RearPilaster_1/2` | 2 | Z移至1275，Z缩放15改5.5，缩短并抬高外立柱下端。 |
| `ART_EXT_PanelBottom_0` | 1 | Y由-725移至-850，Y缩放8.7改6.2，收回穿入入口区域的底条。 |

| 新增Actor | 用途与资产 |
| --- | --- |
| `ART_GATE_OpenLeaf_L` | 左侧静态敞开门扇，使用本次程序生成网格，Yaw=-60度。 |
| `ART_GATE_OpenLeaf_R` | 右侧静态敞开门扇，复用同一网格，Yaw=-120度。 |
| `ART_GATE_Transom` | 门洞上横格，引用现有 `/Engine/BasicShapes/Cube` 和AudienceWood；不是另一个自制新网格。 |

本次不新增开关门交互、动画或输入。没有在门修复脚本中修改谜题参数、相机、主投影灯、章节、演出时长或稳定的15枝成林链路。门扇FBX导入启用自动碰撞，Actor使用BlockAll；门扇敞开外观不能替代通行证据；目前已获得PIE实际CharacterMovement辅助穿门和胶囊冷验，未冒称独立人测。

## 模型与材料来源

新门扇 `SM_DY_GateLeaf_20261025` 由本地Blender Python基础几何组合生成，包含门框、下板、上格栅、铰链和拉环。不是下载来的第三方门模型，也不是手工逐面建模或某一历史门制的复原。

[MODEL.json](D:/灯影山海/Saved/GateRepair-2026-10-25/Attempt1/Source/MODEL.json)的源网格记录为2520顶点、4896三角形，包围盒约0.411×2.870×8.400米，三个槽为Timber/Lacquer/Brass。该顶点数是Blender源网格数据，不冒充UE渲染顶点实读。

| 文件或资产 | 来源与用途 |
| --- | --- |
| [GateLeaf.blend](D:/灯影山海/Saved/GateRepair-2026-10-25/Attempt1/Source/GateLeaf.blend) | 原生可编辑程序几何源。 |
| [SM_DY_GateLeaf_20261025.fbx](D:/灯影山海/Saved/GateRepair-2026-10-25/Attempt1/Source/SM_DY_GateLeaf_20261025.fbx) | 本地导出、供UE导入的同一门扇。 |
| [Build-Door-Leaf.py](D:/灯影山海/Saved/GateRepair-2026-10-25/Attempt1/Tools/Build-Door-Leaf.py) | 实际Blender生成/导出脚本，无外部模型导入。 |
| [Gate-Changes.py](D:/灯影山海/Saved/GateRepair-2026-10-25/Attempt1/Tools/Gate-Changes.py) | UE静态网格导入、三槽赋材质、13+3组装和白名单快照核对。 |
| `M_DY_GateLacquer`、`M_DY_GateBrass` | 本次在UE本地建立的常量材质，没有新位图或在线生成服务。 |
| `MI_DY_GatePostWood` | 新建的已有AudienceWood实例，主要设置木纹方向参数。 |
| `M_DY_AudienceWood`与FramePost纹理链 | 复用工程已有材质；[FRAME_POST_ASSET_SOURCES.md](D:/灯影山海/Docs/FRAME_POST_ASSET_SOURCES.md)已记录上游Poly Haven `dark_wood` 的2K Diffuse/NormalDX/ARM来源与CC0材料。本轮没有新增下载，不能把上游摄影木纹写成项目原创。 |
| `MI_DY_RockTex`及Engine Cube | 沿用既有工程材料/引擎基础形状。Engine Cube不写为自制或CC0，本草稿不重新作出授权结论。 |

新网格、两个常量材质和新实例位于 `Content/DengYingShanHai/Stage/GateRepair_20261025/`。来源、源文件与四个UE资产的字节数/SHA256保存在 [GATE-ASSET-SOURCES-DRAFT.json](D:/灯影山海/Saved/GateRepair-2026-10-25/Attempt1/GATE-ASSET-SOURCES-DRAFT.json)。本轮未引入新的第三方模型、付费资产、贴图包或运行时在线服务。

## 已追加的来源与AI登记

本次来源与AI辅助补记已经追加；两包构建、PIE辅助实走和候选辅助流程已核实，候选独立门外图与正式入口烟测仍待完成。旧记录与本草稿登记前版本已备份，原AI说明Word/PDF没有修改。

1. `Docs/LICENSES.md`末尾新增§14/**SELF-010**，登记自制门扇、新常量材质、既有木纹/Engine Cube复用边界与AI辅助。
2. `Docs/ASSET_SOURCES.md`末尾新增§8门楼实际采用记录；前文外部候选状态未改。
3. [AI-USAGE-GATE.md](D:/灯影山海/Saved/GateRepair-2026-10-25/Attempt1/AI-USAGE-GATE.md)记录本次Codex辅助程序建模、UE集成与验证，引用既有AI说明DOCX/PDF；没有展开Word/PDF编辑或排版。

登记变更及前后哈希见 [GATE-ASSET-REGISTRATION.json](D:/灯影山海/Saved/GateRepair-2026-10-25/Attempt1/GATE-ASSET-REGISTRATION.json)。来源登记本身只证明来源与实际辅助的记载；已完成的运行核查另见下文，仍不代表作品全面验收。

## 回退原件与操作边界

- 原地图：[Backup/L_DY_Main.umap](D:/灯影山海/Saved/GateRepair-2026-10-25/Attempt1/Backup/L_DY_Main.umap)，SHA256 `97CD401167E3DCB4B1B9E350794B2CAE37A8FD923DC9141E28BBBF3C760FC2F1`，对应已验证Run170门修复前基线。
- 草稿实读当前候选地图SHA256：`771ED81572B5DC05C784E0C66D1E610898F29EAC8F2DC466095AB67B1BCD9877`。如打包前再次改图，必须以新冻结输入与包身份更新，不能借用此处旧哈希。
- 原正式脚本：[Backup/Start-FormalShipping.ps1](D:/灯影山海/Saved/GateRepair-2026-10-25/Attempt1/Backup/Start-FormalShipping.ps1)，另有工具晋升前Run170脚本副本。
- 如果随后已出现其他工作，优先按Gate-Apply的before快照恢复上述13个Actor并移除三个新增Actor，保护其他变化；只有确认候选地图没有混入后续改动时，才整图恢复备份。不得reset/clean仓库或清理无关资产。
- `Gate-Changes.apply`按1806基线断言；当前已保存1809，不能直接把重跑脚本当作回退。新增资产先检查引用再决定处理，源模型、失败预览和过程证据保留。
- 正式路由当前仍为Run170。工作主图已变化，原有地图/包哈希保护会阻止旧包与新工作图混用；不关闭保护。Run171已拥有自己的构建、辅助实走及完整/跳过流程证据；独立候选门外图与正式入口烟测仍待补齐，不能借用旧包画面推进。

## 已核实的构建与辅助验证

本段更新于2026-10-26 00:56:26（北京时间），依据磁盘结果重新核对，不以进程启动或静态图片推断通过。

| 验证 | 已核实结果 | 证据边界 |
| --- | --- | --- |
| Development RunD14构建 | Build/Cook/Stage/Archive实际UAT退出0，49文件 | [Package-RunD14/RESULT.json](D:/灯影山海/Saved/GateRepair-2026-10-25/Attempt1/Package-RunD14/RESULT.json)。不是画面验收。 |
| Shipping Run171构建 | Build/Cook/Stage/Archive实际UAT退出0，31文件 | [Package-Run171/RESULT.json](D:/灯影山海/Saved/GateRepair-2026-10-25/Attempt1/Package-Run171/RESULT.json)。不是正式入口已晋升。 |
| 两包输入 | 各687项完全一致；相对Run170仅正式地图修改和4个Gate资产新增；代码、Config与既有材质文件不变 | [Runtime-Gate-Candidate-Summary.json](D:/灯影山海/Saved/GateRepair-2026-10-25/Attempt1/Runtime-Gate-Candidate-Summary.json)的完整输入快照比较。 |
| PIE辅助穿门 | 实际BP_DYTheatreOperator_C使用AddMovementInput与CharacterMovement，从x约-6900穿过入口、过渡区域到约-648，17.625秒；无Actor变换/POV写入、未保存地图 | [Walk-PIE.json](D:/灯影山海/Saved/GateRepair-2026-10-25/Attempt1/Walk-PIE.json)。是真实CharacterMovement的辅助步行，不是独立真人测试。 |
| 冷重载胶囊检查 | 5条路线均clear；半径42、半高96，8cm门槛上方11cm脚平面 | [Cold-Verify.json](D:/灯影山海/Saved/GateRepair-2026-10-25/Attempt1/Cold-Verify.json)。静态胶囊检查不单独替代CharacterMovement或包内图片。 |
| Shipping Run171 FullFlow | 两轮四章、真实Replay；StepMasks=[4095,4095]、PerformanceMasks=[15,15]；实际原生退出0 | [FullFlow结果](D:/灯影山海/Saved/GateRepair-2026-10-25/Attempt1/Runtime-Run171-FullFlow/FLOW-RESULT.json)。辅助流程。 |
| Shipping Run171 SkipFlow | 两轮四章、每章跳过、真实Replay；steps/perf完整，SkippedMasks=[15,15]；实际原生退出0 | [Shipping SkipFlow结果](D:/灯影山海/Saved/GateRepair-2026-10-25/Attempt1/Runtime-Run171-SkipFlow/FLOW-RESULT.json)。辅助流程。 |
| Development RunD14 SkipFlow | 两轮四章、每章跳过、真实Replay；steps/perf完整，SkippedMasks=[15,15]；实际原生退出0，无CSV启动参数 | [Development SkipFlow结果](D:/灯影山海/Saved/GateRepair-2026-10-25/Attempt1/Runtime-RunD14-SkipFlow/FLOW-RESULT.json)。不是新增Profile性能通过。 |

上述PIE、胶囊与包流程分别保留，不写成独立人测，也不从自动走到幕后的结果推断所有侧路、反向行走或近景美术已经通过。

## 候选门外图和正式入口仍待完成

独立门外会话 `Runtime-Run171-Manual-GateExterior` 已记录Shipping PID26428，1600×1000。当前系统Windows防火墙权限弹窗遮挡游戏，根代理已请用户点取消并等待回复；没有代点权限、关闭进程或推进路由。[Launch.json](D:/灯影山海/Saved/GateRepair-2026-10-25/Attempt1/Runtime-Run171-Manual-GateExterior/Launch.json)只证明启动，不作为门外画面或该会话正常退出的证明。

- 待用户处理系统弹窗后，继续候选自身的独立门外图片，核对异常横木消失、门框与敞开门扇组成完整入口、没有新增遮挡；Editor Before/After不能替代该候选包图片。
- 候选图片及正常退出核验完成后，再由根按既有完整性流程判断推进正式路由，并从真正公开CMD入口烟测。当前没有执行Promote或修改正式路由。
- Run170的已完成公开烟测与本次门候选验收分开；既有两次Development Profile退出777003仍作为历史开放限制保留，本轮没有重跑Profile或宣称问题已解决。
