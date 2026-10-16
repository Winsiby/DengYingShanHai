# 《灯影山海》主灯具与支架源资产

本次完成的是可编辑的舞台聚光灯外观源资产：空心旧铜灯罩、内置反射罩、后木把手、调角夹轮、铜轭架、木立柱、铜套与落地滑橇支架。共 57 个命名源部件。全部几何由本地 Blender 脚本制作，没有付费资产或图像／3D 生成服务。

这是“当代创意改编中的传统演出空间”道具，不是先秦油灯、文物复刻或某一皮影流派的历史复原。主体方向依据当前源码和地图记录中的 Movable SpotLight 功能：灯罩和反射罩朝 +X 开口，侧轴与轭架提供明确承重路径，所有实体均位于光源前向半空间之后。

## 可编辑成果

- `DY_HeroSpotlight_Source.blend`：57 个部件分别可编辑，根节点 `Root_Back_Source`；已打包三张原始木材 PNG；含中性审查灯光、相机、地面，审查对象不在 FBX 中。
- `SM_DY_LampBody_Source.fbx`：灯身、夹轮、后把手，53,680 triangles，6 个材质槽。
- `SM_DY_LampStand_Source.fbx`：轭架、柱、铜套、滑橇支脚，40,032 triangles，5 个材质槽。
- `Lamp_Head_Review.png`：1920×1440 近景。
- `Lamp_Full_Review.png`、`Lamp_Side_Review.png`：1440×1920 全景与侧面。
- `build_lamp.py`：本地制作脚本；`verify_lamp_fbx.py`：冷启动 FBX 回读验证。
- `LAMP_SOURCE_MANIFEST.json`：每个部件的角色、边界和事实来源。
- `LAMP_EXPORT_CONTRACT.json`、`LAMP_FBX_COLD_READBACK.json`：枢轴、槽位、UV、单位与回读结果。
- `RuntimeVariant/`：保留完整源后，另以解析重采样制作的33,104 triangles视觉保真变体；两件FBX、派生可编辑blend、三图、同机位近景A/B、参数差异、源文件SHA256保全与独立冷回读记录均已保存。不是几何无损版本，未使用Decimate。详见该目录 `LAMP_RUNTIME_HANDOFF.md`。

## 尺寸、坐标与功能依据

Blender 使用米，FBX 导出单位换算为 UE 厘米。源资产的 `Root_Back_Source` 对应 `ADYLightRigActor.SceneRoot`，灯口沿 +X。

| 项目 | 尺寸或坐标（cm） |
|---|---|
| 整体 Actor 局部包围盒 | X[-45.7,42]，Y[-49.5,49.5]，Z[-310,27.2] |
| 整体宽深高 | 87.7 × 99 × 337.2 |
| 灯身 Actor 局部包围盒 | X[-45.7,42]，Y[-34.75,34.75]，Z[-27.2,27.2] |
| 灯罩最前实体 | X=42 |
| 实际 KeyLight 中心 | (45,0,0)，Movable SpotLight，零旋转，+X 出光 |
| 光源前向净空 | 从最前实体到发光中心 3 cm；X≥45 的整个前向半空间无本资产几何 |
| 木柱主体 | Actor-local Z[-295,-61]，底直径12.6，顶直径9.4 |
| 底面 | Actor-local Z=-310；当前 Actor world Z=310 时对应 world Z=0 |
| LampStand 独立 FBX 枢轴 | 原 Actor-local (0,0,-95)，导出后 mesh-local 底面 Z=-215 |

事实来自：

1. `D:/灯影山海/Docs/SCENE_ART_QUALITY_SPEC.md`：幕后采用克制写实木／布／铜；时空定位明确为当代创意改编。
2. `D:/灯影山海/Source/DengYingShanHai/Private/Interaction/DYLightRigActor.cpp`：KeyLight local (45,0,0)、Movable、SpotLight、锥角20°/38°、SourceRadius4 cm；原身是 BasicShapes Cone，原支架是 Cylinder。
3. `D:/灯影山海/Saved/Audit-2026-10-12-FramePostPlacementDev/verify-Run1/Result.json` 的 `scene_contract.M2_LightRig_P02` 与 `DEV_Floor`：Actor world Z=310；Floor cube center Z=-50、Z scale1，标准100 cm Cube 的顶面为0；本轮未重新启动 UE 验证当前地图。

源造型比原占位锥体更长、更宽，因此未来应在固定核心机位和灯轨两端复查遮挡、与玩家/幕偶的间隔及交互查询碰撞。没有改变光、判定、轨道或输入逻辑。

## 后续 UE 接入（Codex 技术执行，人类作者确认体验）

只在获准的独立 Dev 审查资产与地图中接入；此 stage 不包含 UE 工程修改。

| 原组件 | 新网格 | 必须设置的组件变换 |
|---|---|---|
| LampBody | `SM_DY_LampBody_Source` | location (0,0,0)，rotation (0,0,0)，scale (1,1,1)，不能沿用旧 Cone 的 Yaw90 与 (.45,.45,.55) |
| LampStand | `SM_DY_LampStand_Source` | location (0,0,-95)，rotation (0,0,0)，scale (1,1,1)，不能沿用旧 Cylinder 的 (.12,.12,1) |
| KeyLight | 原组件保留 | 无需改变任何属性 |

材质槽位顺序以 `LAMP_EXPORT_CONTRACT.json` 为准：铜使用拟建铜材质；木复用经核验的木材父材质；黑金属、反射罩、橡胶与凹入光学片按槽位重建项目材质。规范中的 `M_DY_Bronze_Master`、`M_DY_Wood_Master` 是方向与示意名字，本轮没有核验它们是已存在资产，接入时以真实资产路径为准。当前 C++ 构造函数给 Body 和 Stand 的 **slot0 显式设置 BasicShapeMaterial**，只替换 StaticMesh 可能仍保留默认灰色覆盖，接入时必须显式清除／替换组件覆盖并给全部槽位赋材质。

FBX 保存几何、UV 与材质分区，不能完整还原 Blender 程序节点。本次铜锈／粗糙度／微表面是本地程序材质，尚未烘焙为铜纹理；不能把 Blender 预览当成 UE PBR 导入已通过。凹入光学片位于 X=27 cm，远在实际 KeyLight X=45 cm 之后，只是可编辑外观，不承担额外发光玩法。

保留原 `QueryOnly + Visibility Block` 交互策略，导入审查时建立简化查询碰撞；不要用一个巨大凸包把开放灯口／轭架和玩家移动空间全部封死。FBX 本次没有自定义 UCX 碰撞，也未设置新的碰撞策略。

UV0：铜罩为解析圆柱展开，木件采用物理尺寸投影；木立柱沿杆长取材，避免把木板横缝做成竹节状环纹。UV1：两件合并导出网格分别 Smart Project 打包到 [0,1]。已通过回读确认两层 UV 均存在且 UV1 位于范围内；未做逐像素 Lightmap 烘焙检验。

## 免费材质来源与原图保全

木材使用 [Poly Haven Wood Table](https://polyhaven.com/a/wood_table)，作者 Dimitrios Savva，官方标记 [CC0](https://polyhaven.com/license)。来源通过官方页面核实，2026-10-14 查阅。`Sources/` 保留已有本地原图、原许可文本及获取记录。三张 2048×2048 PNG 均与 D 盘来源 SHA256 一致，没有改动像素；木色调整和 DX 法线绿色通道转换仅在 Blender 节点中发生。

铜、边缘铜、黑金属、反射罩、橡胶、光学片材质与几何均为本项目本地程序制作。成本0。没有下载或复用外站预览渲染，没有声称其为外部 PBR 原材质。

## 验证与交接边界

已完成源几何断言、独立冷启动 FBX 回读、单位与双枢轴、所有面非零、单位法线、UV0/UV1存在、UV1范围、前向出光净空、底面接地坐标，以及三张本地渲染逐图检查。初轮回读发现薄件倒角产生退化面，已限制倒角至最小厚度35%并清理退化面后通过；全景检查发现立柱木纹横缝形成环纹，已沿杆长重新映射 UV 并重导出。

视觉结论限于源资产：连续圆润轮廓、卷边和反射罩厚度清晰、铜轭架与侧轴有接触、木／铜材质可区分、底面接地、无明显默认锥／柱占位外观。中性审查灯光亮于夜间剧场，正式 UE 铜色仍需服从幕布最高视觉优先级。

尚未检查：UE实际导入、Engine Master Material、运行时灯轨极值、实时阴影、核心镜头、性能、Development/Shipping。人类作者一人负责创意选择与体验确认；Codex 负责本轮建模与技术集成。本次建模子任务未启动 UE，后续技术接入与地图验证由主任务在获准范围内执行。本次没有写 D 盘产品工程，也没有读取或哈希 `D:/灯影山海/Docs/LICENSES.md`。
