# 灯影山海：完整台口与侧幕照明

日期：2026-10-16。唯一人类作者、负责人：用户；Codex辅助资产适配、摆放与验证。本轮只接入独立Dev美术组合图，不是正式参赛包签收。

## 已做的美术改动

1. 从现有免费CC0亭台横梁派生FullSpan梁，只延长中间直段；保留右端、截面、削角、法线、原木材实例。左端UV岛平移以保持木纹密度，不做非均匀拉伸。
2. 在本轮自建图添加左柱Y=-540，与既有右柱组成完整台口。实际柱顶与梁底Z800接合，两柱均在核心Y±470区域之外。
3. 真实看图发现侧幕位于柱前，照亮也看不见柱身。将两帘X880→1060，保持YZ、旋转、均匀缩放、材质和碰撞；帘最前面比柱最后面留22.123cm，形成“木框在前、帘布在后”。不动主影幕、灯偶轨道或Z70地线。
4. 增加两盏帘幕Spot和一盏木框Spot，采用UE原生Lighting Channels分开布景补光；不新增运行时逻辑、Blueprint执行链、Tick或POV所有者。

地图：`/Game/DengYingShanHai/Dev/StageArtComposition/Maps/LV_StageArtCompositionLab`。

地图文件：`D:\灯影山海\Content\DengYingShanHai\Dev\StageArtComposition\Maps\LV_StageArtCompositionLab.umap`。

新梁：`/Game/DengYingShanHai/Dev/StageArtComposition/Frame/SM_DY_FrameBeam_FullSpan`。

这是编辑器源地图，不是双击即可玩的EXE。旧根启动器和旧包未切到它，新图尚未加入菜单/重演的精确路径白名单。

## 灯光和材质设置

保留既有深红帘、木材材质与原世界后处理，没有提亮贴图或改全局曝光。原PP仍为Manual、物理相机曝光开关及+3.5补偿；未声称测得玩家最终完整曝光。

| 作用 | 位置/目标 | 参数 | 隔离 |
|---|---|---|---|
| 左右帘幕灯 | (630,实际帘中心Y,650)，朝实际组件中心，约5m | 每灯90000 Lumens；inner35°/outer55°；SourceRadius12cm；Attenuation1200cm | 只Channel1 |
| 柱梁灯 | (250,0,950)，朝(950,0,650) | 90000 Lumens；inner40°/outer60°；SourceRadius20cm；Attenuation1500cm | 只Channel2 |

三灯均Movable、逆平方、真实阴影，Indirect0、Volumetric0、MegaLights关闭。帘保留Channel0再开1；三件木框保留0再开2。其余原对象不加入1/2，主灯30000 Lumens和原光锥等参数不改。数值来自本机固定机位候选比较，不是历史灯具数据、布料实测反射率或最终性能结论。

灯是原生SpotLight类，实际Actor Tick关闭；安装版AActor构造默认不能Tick，Light/SpotLight未启用它。StartWithTickEnabled是仅类默认可编辑的标志，未修改其默认值；不能冒称该标志也已关闭。真实BeginPlay另核验实际Tick状态。

## 原生验证与回退

新横梁导入和独立冷读核对48个实际渲染顶点的位置、法线、UV0/半精度存储及源对应，28三角形、单LOD/单槽、原材质、导入和构建配置；右端源及渲染位置/UV不变。

框架接入后38 Actor；帘深度及灯光实装后41 Actor。除两帘纯X平移、五组件通道、三盏新灯外，其他36个原Actor一般合同、显式引用、原可见性、完整PP设置、Staff端点、Pawn/输入/镜头/Flow保持，15Hz不变。只保存本轮自建组合图；每次改图前备份当时原件与哈希，旧地图/旧梁柱/材质/源码/Config/启动器/包未修改。

实际失败记录保留。工具问题在保存前被门控阻止：观察函数位于try内部；UE复制Actor会将scale文本舍入，需回填精确Transform；UE Python3.11与本地3.12的AST字符串不一致，改用固定源文件SHA；Tick起始标志不能写实例，最终用原生类与实际Tick读回。没有以放宽产品合同来“通过”。

证据根目录：`D:\灯影山海\Saved\Audit-2026-10-14-ArtAppearance`。

- `FrameFullSpanCreate-Run1` / `FrameFullSpanVerify-Run1`：新梁导入/冷读。
- `FrameFullSpanMapRevise-Run4` / `FrameFullSpanMapVerify-Run1`：完整柱梁保存/冷读。
- `StageCompositionCurtainLightPreview-Run1`：5张帘布亮度比较。
- `StageCompositionFrameLightPreview-Run1`：发现帘遮柱的9图。
- `StageCompositionFrameLightPreview-Run2`：后移帘的9图，包含全景、左右接合和三姿态。ClearWide只在RAM隐藏测试障碍，未保存隐藏。
- `FrameFullSpanLightsCreate-Run4` / `FrameFullSpanLightsVerify-Run1`：最终帘/灯保存/冷读。
- `StageCompositionSavedCapture-Run1`：最终保存图的真实PIE源场景截图，无临时美术灯，无障碍隐藏，玩家POV所有权不变。

PNG使用原生ImageWrite导出并核验CRC/IEND、零尾随数据、尺寸及解码；不使用旧的有额外进程内存尾部风险的导出路径。SceneCapture为1536方图，继承世界PP，但不是玩家视口完整后处理、宽高比或UI，不能替代包内画面验收。

## 来源、AI记录与剩余美术

源文件目录：`D:\灯影山海\Assets\Sources\DengYingArt\FrameFullSpan-20261015`。保留FBX、完整派生报告、README及可复现工具。

继承既有CC0 VVayToyek四角亭柱梁和Poly Haven Dark Wood；详见`Docs/FRAME_BEAM_ASSET_SOURCES.md`、`Docs/FRAME_POST_ASSET_SOURCES.md`。没有新下载、付费资产或生成服务。不声称上游作者身份、历史榫卯复原或承重设计；未访问受限既有许可登记。Codex辅助的几何/UV适配、摆放、照明与验证需计入最终AI使用材料，AI不是第二名制作成员。

看图结论：完整木框与侧帘已能共同阅读，柱身覆盖问题已解决，三姿态仍可见真实主灯投影。**整体暗部、幕后灯具阅读、焦点和环境表面仍需收尾，整场美术未验收。** 保存图仍有旧测试物，不能只隐藏表面留下空气墙。地板已绑定免费木地板实例，并非尚未换材质。

继续顺序：与碰撞范围一致的木栏/背板等剧场环境 → 新夸父目标提示对齐 → 正式枝形/成林画面 → 新图完整流程及包内验证。旧指南的Cube躯干提示不能冒称已与新夸父匹配。

成林木枝第二版源候选位于本地`ArtIntegration-20261014/ForestArt/Source-Run2`：一个中心Z轴、闭合、渐细不规则的224三角形枝段，保留原15枝系统。两张Blender中性形体预览已看，仍是待UE材质与真阴影比较的候选，不是正式树皮或成林验收，未覆盖旧森林。

本轮未生成新Development/Shipping包，未完成整局5–8分钟复测、GPU性能、录屏或最终艺术签收。建模美术总目标保持未完成。
