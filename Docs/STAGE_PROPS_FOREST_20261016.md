# 后台木器与成林枝形接入记录

日期：2026-10-16。唯一人类作者/负责人：用户；Codex 辅助建模、接入和验证。本轮只修改独立 Dev 美术组合样本，不是正式参赛版本签收。

## 玩家可见目标与实现边界

将旧相机/移动测试墙、低顶和台阶从新美术组合图完整移除（包含碰撞），用有后台用途的操杆挂架、候演长凳替代。四根挂杆只是被动模型，不是可交互手杖，也不增加谜题、收集或新按键。

成林枝段改用有收尖与轻微纵向起伏的新实体网格，沿用原生森林表现 Actor、原 15 段布局及 Stage 的显式引用；不把成林改成贴图，也不改变落杖触发因果。

Director 仍拥有谜题事实，Stage 仍在真实杖尖接触后授权森林并控制生长。新增木器只用 StaticMeshActor；森林 BP 只配置原生表现类的网格、材质和布局，无新 Tick、全局扫描、存档或流程所有者。现有 E/A/D/R、15 Hz、灯/偶轨道、Z70 地线、镜头和正式地图均不在本轮改动范围。

## 源文件与材质

- 操杆挂架：180×55×185 cm，1,472 点 / 2,888 三角面，14 个真实木件的独立简单碰撞盒。
- 后台长凳：180×45×45 cm，1,248 点 / 2,444 三角面，13 个真实木件的独立简单碰撞盒。
- 两件均为厘米制、落地 Z0、单 UV0/单 Wood 槽，0.4 cm 几何倒角；34 处连接已用实际几何内部点检查，不是仅比较包围盒。构件是相交的闭合木件壳，不冒称布尔合并或真实承重榫卯。
- 每个木件拥有自己的窄碰撞盒，不用包住整个架子/长凳的空气墙。盒形碰撞对倒角、圆杆拐角有近似误差；源报告登记误差，不冒称逐表面精确碰撞。
- 木器和枝形复用现有 `MI_DY_FramePost_Wood`；继承原项目的免费 Poly Haven Dark Wood 来源记录，不创建材质通用框架，不修改共享材质或上游纹理。
- 新几何为项目创意程序化建模、Codex 辅助，不是下载模型、付费生成服务或特定皮影流派/历史实物复原。AI 辅助需计入最终参赛披露，不能写成第二位人类作者。

## 实际验证记录

森林源网格和 BP 已分别在新的 UE 进程中创建、冷读，两个进程均实际退出 0；新增恰好两个 Dev 资产，原 414 个产品不变，产品基线变为 416。该结果仅是资产准入，不代表场景成林美术已验收。

木器第一次原生导入在碰撞门控处失败，保存前即停止，仍为 416 个产品。UE 进程本身退出 0 不等于任务成功，脚本 `success=false` 与失败日志均保留。核查本机 UE 5.8 `FbxStaticMeshImport.cpp::ImportCollisionModels` 和 `StaticMeshImportUtils.cpp::AddBoxGeomFromTris` 后，定位到解析碰撞盒时对三角面顺序的依赖；修正仅作用于新源碰撞三角面顺序，不能改引擎、放宽尺寸验证或回退整块自动碰撞。

修正后的 Source-Run4 保留原视觉点、拓扑、UV0 和角法线浮点签名，27 个碰撞盒的几何尺寸也保持不变。其原始 FBX 面序通过本机算法复现检查；随后 `StagePropsCreate-Run2` 实际原生导入成功、`StagePropsVerify-Run1` 在全新 UE 进程冷读成功，两次实际退出均为 0。保存恰好两个网格，原 416 个产品均不变，产品基线变为 418；简单碰撞实际为 14 / 13 个 Box，其他形状数组全部为零。

源文件保存在 `Assets/Sources/DengYingArt/StageProps-20261016-R2`；第一版失败源和日志仍保留，没有覆盖。

`StagePropsMapRevise-Run10` 仅保存已备份的 `LV_StageArtCompositionLab`，41−9+2=34 Actor；原森林实例替换为新 BP，并只重绑 Stage 的显式森林引用。`StagePropsMapVerify-Run1` 全新进程冷读通过、零保存；其余 417 产品不变。核心全量合同逐值一致，额外核查 Tags、隐藏/碰撞、灯光通道、Owner/AttachParent 和已加载的空/无连接 Level Blueprint；这不是任意 UObject 全反射扫描。引用设置不触发无关的 Stage 编辑器 Billboard 重建，未改运行时流程。

四项真实简单碰撞查询同时在保存前及冷读通过：架柱命中、架内空隙不命中、凳面命中、凳下空隙不命中。它们不代表玩家胶囊体实际走动手感。

`StagePropsCapture-Run1` 实际全 RHI PIE 生成 11 张安全 ImageWrite PNG，全部 CRC/IEND/零尾字节检查通过、实际 EndPIE、零产品保存。Codex 逐图查看全部 11 图：旧测试障碍已消失，框架/厚帘仍可读；两个新木器近景几乎全黑，所以本轮不能签认整体美术。主灯开关对比沿用相同物体与机位，不能当作纯阴影像素 Mask 或艺术质量证明。

`StageForestCapture-Run1` 用原三幕 DataAsset 目标和 15 Hz 实际判定运行 P01→P02→P03。新 Dev 图不在开始菜单精确白名单内，因此只对临时 PIE Director 打开自动开始并调用原公共开始接口；没有假称玩家菜单/键鼠验收。原 Blueprint 自行落杖、接触、成林，测试未写 Staff、Token、接触/森林增长接口。已拍实际 Resolve 接触前、实际接触后的成长中、实际成林主灯开/关四张图，逐图查看完成。真实当前 Token、15 个新网格分枝、增长中与完成态、玩家 POV 未接管均通过，实际 EndPIE、全部产品不变。主灯开关超过8灰阶变化 1,004,229 / 2,359,296 像素，是整盏灯 A/B，不是纯森林影子 Mask。

画面结论：因果链、真实实体枝形及投影已可运行，但当前像稀疏枝架，尚不是最终茂密林冠。`BranchLayout` 的偏移是幕布局部 Y/Z 单位，必须乘实际幕缩放并投影，不能误当世界厘米盲目整体放大。后续先改善后台局部工作光和林冠轮廓，不能因为上述验证通过而把正式美术、包内运行或竞赛作品标成完成。

## 后台工作光实际对比与接入

按灯光技能的“固定曝光、先看真实视角、限制影响范围”流程，不修改材质来掩盖照明问题。首组中央 Point 0/6k/18k/36k lm 仍不能让木器近景可读，未采用。第二次诊断实际记录木器在 PIE 中的位置、边界、Actor/组件显示/MainPass/SceneCapture 标志均正常，相机与中央光到木料的射线均先命中相应木器；未把未显示原因归为资产丢失或隐藏。

`StageWorkLightCapture-Run3` 对两盏局部 Spot 进行 0/4k/12k/24k lm 比较，共 12 张固定机位 PNG，Codex 全部逐图查看：4k 仍过暗；12k 能读出木纹、挂杆、凳腿和接地；24k 地面与灰墙光斑偏亮。因此先选 12k 作为 Dev 工作样本，不宣称最终电影级照明。

| Actor | 位置 cm | 朝向 | 参数 |
|---|---|---|---|
| ART_Worklight_RodRack | (-240,-470,300) | 操杆架实际 bounds 中心 | Movable Spot，12,000 lm |
| ART_Worklight_Bench | (-100,470,260) | 长凳实际 bounds 中心 | Movable Spot，12,000 lm |

两灯均采用 inverse-square，SourceRadius12cm、Attenuation600cm、inner30°/outer50°、真实阴影、默认通道0、Indirect0、Volumetric0、关闭 MegaLights。距各木器约3.8–4.1m，不能脱离距离/曝光把 lm 当通用推荐。两灯至主幕最近X距离分别1165/1025cm，主幕完整位于600cm影响球之外；原 Manual/physical-camera/+3.5、主灯和已存三盏帘/框灯不变。尚未测目标机 GPU 开销，不声称达到帧率预算。

`StagePropsMapLightCreate-Run1` 仅保存已备份 Dev 图，34+2=36 Actor；`StagePropsMapLightVerify-Run1` 全新 UE 进程实际退出0、冷读零保存，原34 Actor完整合同与原417其他产品均不变。新增的是被动原生灯 Actor，不增加流程、世界扫描或运行时脚本依赖。

`StagePropsCapture-Run2` 在实际保存态生成11图并实际 EndPIE，全部产品不变。两盏保存灯在 BeginPlay 后实际为12000lm、Actor Tick关闭；没有 RAM 补光、隐藏夹具、改曝光或接管玩家POV。Codex逐图查看全部11图：木器外形、顺纹木材、挂杆与落地可读；左右框接缝和原皮影实时投影保持。主灯 A/B 同姿态/同机位，超过8灰阶变化272,730 / 2,359,296像素（11.56%），不是纯阴影Mask。总体仍有大面积暗背景、简单灰墙与玩家占位外观，故只签认本步木器/接入改善，不签认最终剧场高质量美术。

## 资产位置

| 内容 | 实际 UE 路径 |
|---|---|
| 本轮独立美术地图 | `/Game/DengYingShanHai/Dev/StageArtComposition/Maps/LV_StageArtCompositionLab` |
| 操杆挂架 | `/Game/DengYingShanHai/Dev/StageProps/Meshes/SM_DY_OperatorRodRack` |
| 后台长凳 | `/Game/DengYingShanHai/Dev/StageProps/Meshes/SM_DY_BackstageBench` |
| 收尖枝段 | `/Game/DengYingShanHai/Dev/ForestArt/Meshes/SM_DY_ForestBranch_Tapered` |
| 数据型森林表现 BP | `/Game/DengYingShanHai/Dev/ForestArt/Presentation/BP_DYForestArt_Tapered` |

文件实体位于 `D:\灯影山海\Content` 下对应目录。`.umap/.uasset` 应在 UE 中打开，不是可双击直接游玩的 exe。本图尚未进入开始/重演的精确地图白名单，不替换旧可玩入口。

## 仍需完成

场景中走动/近看与真实主灯投影、枝形尺度及长势可读性、新皮影引导轮廓、暗部一致性、最终可玩入口及 Development/Shipping 包内全流程。安全 SceneCapture 图不代替玩家最终视口、实体键鼠输入、目标机性能或完整三轮通关。

新增后续交付目标：完成剩余建模美术和实际运行验收后，再建立 GitHub 私有仓库并上传可复现的游戏工程。当前尚未创建远程仓库或推送；届时先整理免费资产/AI记录、忽略缓存日志临时包并排查敏感配置，不把原有未完成美术或一整份 Saved 审计当作最终游戏上传完成。

回退：保留改图前精确备份，旧测试图、正式图、启动器和包不动。本轮被移除的 9 个夹具仅位于可恢复的新 Dev 样本中；不自动回滚覆盖或删除失败证据。
