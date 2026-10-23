# 《灯影山海》美术建模批次：夸父、独立木杖、厚台翼

日期：2026-10-14。项目仍由用户一人负责，Codex 作为工具辅助建模、导出与验证，不增加人类队友。此批次是美术源资产与 Dev 准入，**不是正式美术或比赛作品完成声明**。

## 已完成的实际文件

### 夸父关节皮影

源目录：`D:\灯影山海\Assets\Sources\DengYingArt\ArtBatch-20261014\Kuafu`。

- `SK_DY_Kuafu_Puppet.fbx`：单一 Skeletal Mesh，20 根骨骼，17,082 三角面；四蛇、关节铆点、发髻、赤足奔跑与短袍。
- `DY_Kuafu_Puppet_Source.blend`：可编辑源文件，参考图已打包。
- `COMPARE_StrideMid.png`、`COMPARE_StrideBack.png`、`COMPARE_Reach.png`：三个实际姿态的原图对照预览，Codex 已逐张查看。
- `MODEL_EVIDENCE.json`：原图哈希、分件、关节、文化来源与创意改编范围、导出设置。

历史图像事实来自项目已归档的公版古图，而非通用战士模型。源脸部和衣服印线使用古图矢量路径；隐藏搭接、圆润衣缘、皮革赭色、暗红、黄蛇及手蛇移至前臂，是明确标注的当代皮影改编，不宣称历史原色、人物肤色或正统流派复原。手杖来自文本母题，不伪称古图中已有此道具。

三姿态均为 30 fps、1..31 帧的有效一秒静态演出姿态；不是跑步循环、完整动作库或正式演出时长。独立木杖不合并入骨骼网格。

本批次已修复腰部断缝和僵硬衣缘。正反面保留古图 YZ 坐标；厚化侧面按实际法线投影到 XY/XZ，避免只投影 YZ 造成零面积 UV。单 UV 通道允许平铺材质复用，不冒称无重叠的烘焙/lightmap atlas。独立 Blender FBX 回读通过：20 骨及父子关系一致，17,082 真实三角形，所有实际顶点只有一个有效骨权重且为 1.0，零退化 UV。

原图 PNG 的白色区域带透明度。预览通过材质叠在白底上显示，没有反相或改写源像素；早期黑底显示和失败权重版都已保留。

UE 准入已完成：`/Game/DengYingShanHai/Dev/KuafuArt/Puppet` 中恰好 1 骨骼网格、1 骨架、3 姿态序列；不产生 PhysicsAsset、纹理或自动材质。UE 实际 20 骨及父子链正确，三序列各 1 秒/31 key，源姿态与运行时压缩数据在 0/0.5/1 秒逐骨稳定，三姿态逐骨角度与源作者记录相符且互不相同。原生第二个进程冷回读也通过，原生退出码 0；只读阶段保存 0 资产和 0 地图。

原生冷导出 FBX 再经独立 Blender 实际缓冲检查：17,082 三角形、单 UV、0 退化 UV、每个实际顶点单骨权重 1.0。UE 因材质/法线分段有 36,873 render vertices，不机械要求与源 10,982 顶点相等。UE 导出把骨骼 Root 标为 FBX eRoot，Blender 把它表示为名为 Root 的 armature 对象，因此 Blender 显示 19 子骨；这与原生已验证的完整 20 骨不矛盾。检查只在成功原生冷导出哈希、20 骨原生证据、准确 Root 对象和所有子链都匹配时接受这种表示，不允许丢失骨骼。

导入检查中的失败全部保留：Python `AnimationLibrary` 与 C++ 类名不同；`SourceAnimationName` 受保护，不绕过读取，而以确切实际资产名和逐骨源角度验证；FName 轨道返回小写造成字符串误报，实际 20 轨道全部存在；清单斜杠格式修正只影响外围报告；NullRHI 导出触发 `MeshObject` 断言，正常 RHI 冷导出成功，没有更改全局渲染配置或重存资产。前五次导入检查保存 0 资产，通过的第六次才保存五个新资产。

当前网格的六个材质槽仍未绑定正式材质，既有偶 Actor/正式地图也未替换；所以这是骨骼/几何准入，不是 UE 美术画面验收。

### 独立木杖

源目录：`D:\灯影山海\Assets\Sources\DengYingArt\Staff-20261014`。

- `SM_DY_Kuafu_Staff.fbx`、`DY_Kuafu_Staff.blend`、`Staff-ActualScale.png`。
- 1,490 源顶点、2,976 三角面、单 UV；圆钝端部，不是矛/武器。
- 实际木纹来自项目已归档 CC0 `wood_table` 材质；没有改写原始纹理像素，也不宣称具体历史木种。
- 局部边界保持 `[-50,50]`，A 是局部 -Z，B 是 +Z；现有组件缩放 `.06/.06/1.55` 与 155 cm 长度保持不变。

UE 已实际导入网格和一个复用现有木材父材质的实例到 `Dev/KuafuArt`，并通过独立第二个 UE 进程冷回读。真实 render LOD0 是 2,976 三角形、1 UV，没有 Nanite 或自动碰撞。原生 `DYPuppetActor.GetStaffGeometrySnapshot()` 的三种杖倾斜姿态，在额外带平移/旋转的 Actor 中，新旧 A/B 世界端点差值均为 0。该检查是编辑器几何检查，不代替可玩流程验收；正式地图未换杖。

### 厚台翼帷幕

源目录：`D:\灯影山海\Assets\Sources\DengYingArt\ArtBatch-20261014\Curtain`。

- `SM_DY_StageWingCurtain_BakedUV.fbx`、`DY_StageWingCurtain_BakedEditable.blend`。
- `T_DY_StageWing_BaseColor_2K.png`、`T_DY_StageWing_Roughness_2K.png`、`T_DY_StageWing_Normal_DX_2K.png`。
- `Curtain-Baked-DeepCrimson.png`、`Curtain-Baked-HemWeaveCloseup.png`：使用实际交付贴图重新渲染，Codex 已查看。

布面来自官方 CC0 Blender Studio Cube Diorama 的一个实际布岛，只取布面而非现代家居整场景。原 512 三角形的无厚度布片，保留宽缓不等距褶皱后统一到约 2.8 m 高、1.31 m 宽，再做 4 mm 实体、独立 6 mm 翻折加强和软边，总共 23,072 三角形；闭合、正体积。它是**不透明台翼**，不是主投影幕，也不能把薄纱染红冒称厚帘。

织物是可编辑的本地程序材质，非免费扫描材质或付费生成服务。实际曲面烘焙 2K 三图，UV0 为 BakeUV、UV1 保留 SourceUV。BaseColor 为 sRGB；Roughness 为线性数据；Normal_DX 为 DirectX 切线法线，UE 不再次翻转绿通道。第一次 DIFFUSE 烘焙混入 Sheen 的失败已保留，交付版改为原 Base Color 输入的 Emission 烘焙。

独立冷回读：几何最大偏差 `5.96e-8 m`；逐空间顶点的 UV 角关联误差为 0；真实 atlas 内部重叠 0、退化 UV 0、有效覆盖约 32.705%。2,954 个厚度/软边小三角没有 2K 像素中心，已如实记录并保留 12 px padding，不宣称每面都有独立 texel。

## 免费材质候选

`ArtBatch-20261014\MaterialCandidate\Leather037-2K` 保存 ambientCG Leather037 官方 2K 原始包、哈希、元数据和原始文件。已查看实际皮革颜色/预览；它仍是候选，尚未替换皮影材质，不能因为下载成功就说正式采用。后续用受控细节强度统一到皮影的图形语言，不让皮革纹理掩盖古图印线。

官方 [ambientCG 许可页](https://docs.ambientcg.com/license/) 明确资产使用 CC0，可复制、修改、用于商业项目并包含原始文件。归档原文和具体来源；本轮没有付费模型、纹理、插件、字体或图像/建模生成服务。

## 本轮没有改动的边界

- 原有 364 个项目文件保持哈希不变；新资产只位于新增 Dev 路径。
- 正式 `L_DY_Main`、旧 Dev 地图、输入 E/A/D/R、15 Hz 判定、灯/偶参数、镜头、声音、流程和现有落杖/成林事实未改。
- 没有删旧文件、覆盖用户改动、Git 提交/暂存或修改全局环境/权限。
- 没有读取或哈希受保护的既有 `Docs/LICENSES.md`；新增来源记录在本批次源目录与 Saved 审计中。
- 尝试补旧 Development 首帧时，Computer Use 实际窗口清单中没有游戏窗口；用户已报告关闭防火墙提示，但首帧仍待验。没有替用户操作安全弹窗，也没有借此宣称可玩验收通过。

## 接下来的唯一执行顺序

1. 只给新的 Dev 美术样本接入皮影主材质与三姿态表现；消费既有 `OnControlChanged`，不复制 C++ 判定。独立杖仍由既有 Staff 组件提供 A/B 事实，不能把手部动画变成判定来源。
2. 对照实际机位检查后台皮影、操杆/手杖与幕上真实投影；修好接缝、材质闪烁、握杖与提示匹配后，再替换正式地图的美术引用。
3. 接入台翼，继续主灯具、落杖成林几何及同一戏台的环境统一；不新增场景/玩法。
4. 正式场景后再做 Development/Shipping、三轮通关与展示录屏验证；本批次源模型预览不是当前游戏画面，不代替这些检查。

本轮受到 ponytail 的影响：复用已有木材父材质、一个夸父骨架/三姿态、只拆取一个布岛；不导入完整角色包或现代样例关卡，不新增泛用框架。
