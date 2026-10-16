# `Shadow_puppet_Unreal` 方法借鉴与技术审计

> 审计对象：[CHI-CityTech/Shadow_puppet_Unreal](https://github.com/CHI-CityTech/Shadow_puppet_Unreal)  
> 审计日期：2026-10-01  
> 用途：只借鉴可验证的方法和实验结论，不复制没有许可证授权的代码、Blueprint、模型、贴图、关卡或音频。

## 1. 审计结论

该仓库适合作为“UE 皮影实验记录”参考，不适合作为《灯影山海》的代码或资产基础。

值得借鉴的核心方法只有四项：

1. 把皮影拆成具有明确关节枢轴的平面部件；
2. 用独立测试关卡比较幕布、角色和灯光方案；
3. 明确记录半透明幕布、背面显示、枢轴和可见性带来的问题；
4. 把表演动画从简单关卡触发迁移到 Sequencer、Animation Blueprint 或显式状态机。

不能照搬的部分包括：Level Blueprint 的 `BeginPlay` 串行动画、手动复制前后两个角色、散落的显隐开关、第三人称模板残留、试验性材质命名，以及把半透明幕布表现和玩法判定绑定在一起。

《灯影山海》应在它的实验基础上向前推进：角色采用项目专属的刚性蒙皮 2.5D 骨骼皮影；动画由 Sequencer 和状态机驱动；真实 UE 阴影保留，但逻辑判定继续使用参数区间；核心流程不写在 Level Blueprint。

## 2. 可验证的仓库事实

### 2.1 工程类型

- `.uproject` 的 `EngineAssociation` 为 UE 5.5；
- 只启用了编辑器插件 `ModelingToolsEditorMode`，没有发现必须随游戏运行的第三方插件；
- 仓库中没有 `Source/` 目录，也没有 C++ 源文件；
- 工程主体是 Blueprint、关卡、材质、模型和动画等 `.uasset`；
- `DefaultInput.ini` 使用 Enhanced Input 的 PlayerInput/InputComponent，但当前工程仍保留大量第三人称模板配置；
- `DefaultGame.ini` 的项目名仍是 `Third Person BP Game Template`，且启动时添加 Starter Content，说明其定位仍是研究原型，不是清理完成的发布工程。

因此，“分析源代码”在这个仓库中主要指可读的配置、Markdown 工程文档和资产目录结构；不能把二进制 Blueprint 当作已经读过的文本源码。

### 2.2 渲染配置

`Config/DefaultEngine.ini` 可确认：

- 使用 Lumen GI/反射；
-启用 Virtual Shadow Maps；
- 生成 Mesh Distance Fields；
- 启用 DX12 SM6；
- 禁用静态光照；
- 项目设置中启用了 Ray Tracing；
- 默认图形目标为 Desktop / Maximum；
- 默认地图和 GameMode 仍来自第三人称模板。

这套设置体现了“动态光影实验优先”，但不能直接照搬到《灯影山海》。尤其是硬件 Ray Tracing 不应成为比赛包的默认刚性依赖；本项目应先以 Lumen、Virtual Shadow Maps 和标准动态灯光完成稳定版本，再把硬件光追作为目标电脑上的可选质量档。

### 2.3 资产结构

联网读取 Git 树得到：

- 767 个文件节点，其中 737 个 `.uasset`、7 个 `.umap`；
- 大量内容来自 UE4/UE5 Mannequin、StarterContent、ThirdPerson 和 LevelPrototyping；
- 项目特有内容主要集中在 `Content/Imported_files/`、`Content/Materials/` 和两个皮影测试关卡；
- 皮影目录能看到 `Arm`、`Hand`、`Body`、`Rigged_older_Bro`、`Older_animation` 等分片和动画命名；
- 存在 `BP_OpacityController`，但其节点图不能从文件名推断；
- 存在多个 `Opacity`、`Translucent` 和试验性材质，说明作者确实比较过透明/不透明显示路线；
- 同一角色存在 25、40、50、70、100 等多个比例或透明度试验版本，表现出手工实验痕迹，但不适合作为正式内容目录范式。

### 2.4 Git LFS 与审查边界

仓库的 `.gitattributes` 把 `Content/**`、`.uasset`、`.umap` 全部交给 Git LFS。GitHub API 中约 129–133 字节的文件不是资产本体，而是 LFS 指针。例如：

- `BP_OpacityController.uasset` 指向约 28 KB 的 LFS 对象；
- `Rigging_Enclosed_Puppet_show.umap` 指向约 53 KB 的 LFS 对象；
- `Rigged_older_Bro.uasset` 指向约 29 KB 的 LFS 对象；
- `Older_animation.uasset` 指向约 17 KB 的 LFS 对象。

这些数字只能说明对象规模较小，不能说明节点、参数、材质公式或骨骼结构。加之仓库根目录没有 LICENSE，本项目不能下载后复制其中内容。本审计不会臆测 `.uasset` 内部节点。

## 3. 仓库确认的制作方法

根据仓库白皮书和工程说明，可以确认以下实现方式。

### 3.1 角色构成

- 用薄矩形/平面 Static Mesh 作为身体和四肢；
- 各部件通过父子层级组成角色；
- 部分角色同时存在正面和背面副本；
- Quick Add 的矩形枢轴不适合铰链式旋转；
- 作者建议在 Blender/Maya 中制作带显式枢轴的单面平面，再导入 UE；
- 厚度、法线、单/双面显示会影响侧面观看和阴影稳定性。

### 3.2 动画

- 原型用 Level Blueprint 的 `Event BeginPlay` 驱动程序化动作序列；
- 文档明确认为这种方式脆弱、难以混合、难以重复；
- 作者建议迁移到 Sequencer、Animation Blueprint 或显式状态机；
- 不同关卡中的父子 Actor 可见性标志不一致，存在意外隐藏风险。

### 3.3 幕布与阴影

- 初衷是从幕后向半透明幕布投影；
- UE 5.5 半透明材质在该实验中没有得到作者需要的物理背投效果；
- 原型尝试过把角色放到幕布前，以及复制镜像角色到幕布另一侧；
- 研究文档还提出 Fake Shadow Mesh 和 Decal 两种替代方案，但不能确认所有方案都已实现；
- 白皮书建议比较 Masked/Opaque 薄幕布与半透明幕布。

这些结论对本项目很有价值：皮影“可见本体”、真实阴影、幕布视觉和玩法判定必须分层，而不能指望一个半透明材质同时解决全部问题。

### 3.4 用 UE 5.8 重新解释其 UE 5.5 结论

参考项目所说的“Translucent 不支持 specularity”对应普通 Translucent 路线，不能直接当作 UE 5.8 所有透明材质的最终结论。UE 5.8 官方资料显示：

- 普通 Translucent Blend Mode 仍有动态光照和高光限制；
- Thin Translucent Shading Model 可提供白色高光与带色透光背景，值得用于幕布视觉层 A/B 测试；
- Translucent 材质可以选择 `Cast Dynamic Shadow as Masked`，可作为皮影彩色表面与稳定投影之间的折中实验；
- 彩色半透明阴影目前仍以 Static Light + Lightmass 为前提，不适用于玩家实时移动的主灯；
- 透明层叠会产生 Overdraw 和排序成本，因此不能把幕布、皮影、雾、粒子全部做成多层 Translucent。

所以，Masked/Opaque 薄幕布仍是动态互动的稳定基线，Thin Translucent 只作为可关闭的视觉叠层；是否采用以 UE 5.8 实测为准。

## 4. 《灯影山海》的改进实现

### 4.1 皮影资产：分片思想保留，技术载体升级

采用一个刚性蒙皮的 Skeletal Mesh，而不是在关卡里手工管理十几个 StaticMeshActor：

```text
SK_Kuafu_Puppet
├─ root
├─ pelvis / torso / head
├─ upperarm_l / lowerarm_l / hand_l
├─ upperarm_r / lowerarm_r / hand_r
├─ thigh_l / calf_l / foot_l
├─ thigh_r / calf_r / foot_r
├─ staff_root
└─ snake_or_ribbon_controls
```

要求：

- 每个部件保持平面或极薄厚度；
- 每片几何刚性绑定到对应骨骼，避免皮影像橡胶一样拉伸；
- 关节枢轴在 DCC 源文件中确认，不依赖 UE Quick Add primitive；
- 正面保留皮革/纸质色彩和透光细节；
- 阴影投射使用相同骨架驱动的稳定几何；
- Control Rig 只提供项目所需控制，不构建通用人形大系统。

### 4.2 角色 Actor

建议结构：

```text
ADYPuppetActor / BP_DYKuafuPuppet
├─ VisiblePuppetMesh        // 玩家在幕后看到的彩色皮影
├─ ShadowCasterMesh         // 可选：同骨架的简化、稳定投影代理
├─ InteractionAnchor
├─ StaffAnchor
├─ AudioComponent
└─ DebugBillboard（Development Only）
```

`ShadowCasterMesh` 不是预渲染假影子。它仍参与 UE 的实时光照和阴影，只是在彩色皮影材质需要半透明时，用不透明/Masked 的同骨架代理保证真实阴影轮廓稳定。若 `VisiblePuppetMesh` 本身已经能稳定投影，则禁用代理，避免重复阴影。

是否需要代理必须由 A/B 测试决定，不能预设为永久依赖。

### 4.3 幕布测试矩阵

在 `Content/DengYingShanHai/Dev/ShadowLab/` 建立独立测试图，只比较同一灯、同一皮影和同一镜头下的三种幕布：

| 方案 | 用途 | 优点 | 风险 | MVP 状态 |
|---|---|---|---|---|
| Opaque/Masked Thin Screen | 真实阴影接收基线 | 稳定、易调、阴影清晰 | 背投感需要材质和双面照明辅助 | 主方案 |
| Masked Fiber Screen | 增加布纤维与边缘透光 | 保留稳定深度与布感 | Mask 密度过高会闪烁 | 主方案候选 |
| Thin Translucent Visual Overlay | 只提供薄纱透光、高光和背景染色 | 幕布更柔和，UE 5.8 表现优于普通 Translucent | 排序、Overdraw、动态阴影风险 | 视觉叠层，不承担判定 |

验收不以“完全符合真实光学模拟”为唯一目标，而以观众正面能读清轮廓、幕后空间可见、移动灯源时阴影趋势真实、打包版本稳定为准。

### 4.4 动画与流程

不使用 Level Blueprint `BeginPlay` 串联完整演出。职责划分如下：

- C++ Puzzle Director：三段状态、成功条件、持续确认、重置；
- Puppet Actor/Component：姿态 ID、当前可操纵轴、角色事件；
- Blueprint：Actor 组装、材质实例、音效和轻量反馈；
- Sequencer：开场、段间转场、弃杖化林、结尾镜头；
- Event Dispatcher / BlueprintImplementableEvent：状态变更通知表现层；
- Level Blueprint：只允许一次性关卡入口转发，不保存核心游戏状态。

推荐事件流：

```text
PuzzleManager 进入阶段
  → 设置灯/角色可控制参数
  → 玩家调整
  → 参数区间评分 + HoldDuration
  → OnTrendChanged / OnPuzzleSolved
  → Blueprint 反馈
  → Sequencer 播放阶段收束
  → PuzzleManager 进入下一阶段
```

这样既吸收了参考项目的皮影分片经验，又规避其 BeginPlay 编排和手工可见性状态的脆弱性。

### 4.5 可见性与重置

- 不在关卡中分别修改每个肢体的 `Visible` 和 `Actor Hidden In Game`；
- 显隐由角色根 Actor 的统一函数或组件状态控制；
- 编辑器校验检查：部件缺失、骨骼映射、材质槽、Cast Shadow、Hidden Shadow、碰撞和父级；
- 每次谜题重置恢复灯光归一化参数、姿态 ID、Sequencer 时间和 VFX；
- Development 调试层显示实际输入值、目标区间、容差、持续时间和当前状态；
- Shipping 包默认关闭全部调试显示。

## 5. 从参考项目反推的质量问题

以下特征容易让作品显得像课程实验或廉价原型，本项目必须主动消除：

- 默认第三人称角色和 Starter Content 出现在最终画面；
- `Attempt_1`、`copy`、`Imported_files` 等试验性命名进入正式目录；
- 同一角色保留多套比例/透明度副本；
- 透明幕布、角色本体和阴影边缘出现重影；
- 通过复制角色到幕布另一侧制造显眼的同步误差；
- 动画只靠线性 `BeginPlay`，没有节奏、停顿和缓入缓出；
- 场景全局开启高开销特性，却没有镜头级质量收益；
- 皮影部件关节穿帮或随视角消失；
- 资产没有明确的原始来源与许可台账。

《灯影山海》的高质量标准应是“少量内容做到统一与可控”，不是把所有高级渲染开关打开。

## 6. 实施与验收

负责人：

- 项目负责人：ShadowLab、C++ 状态与判定、Puppet Actor、材质/阴影 A/B、Sequencer 接入、性能和打包；
- 同一作者负责夸父文化依据、免费资源适配、分片源文件、关节枢轴、正反面纹样、幕布纹理和动作参考；不预设手工建模能力。

验收项：

1. 夸父可在正面、侧前方和幕后镜头中保持皮影结构，不发生部件消失；
2. 灯源移动时使用 UE 实时阴影，轮廓变化连续，没有双影；
3. 关闭所有视觉阴影后，参数判定仍可独立工作；
4. 四组必要动作可被 Sequencer/状态机重复播放和重置；
5. 不依赖 Level Blueprint 保存核心状态；
6. Development 和 Shipping 包分别完成一次全流程验证；
7. 任何参考项目内容都没有被复制进仓库。

## 7. 参考链接

- [Shadow_puppet_Unreal 仓库](https://github.com/CHI-CityTech/Shadow_puppet_Unreal)
- [工程 README](https://github.com/CHI-CityTech/Shadow_puppet_Unreal/blob/main/README.md)
- [Virtual Wayang Kulit 工程白皮书](https://github.com/CHI-CityTech/Shadow_puppet_Unreal/blob/main/Read%20me%20The%20Unreal%20Engine%20project%20wayang%20kulit.md)
- [Shadow-Casting Approaches](https://github.com/CHI-CityTech/Shadow_puppet_Unreal/blob/main/possibilities/Shadow-Casting%20Approaches.md)
- [2D 图像转换为网格的调查文档](https://github.com/CHI-CityTech/Shadow_puppet_Unreal/blob/main/possibilities/Investigating%20techniques%20to%20convert%20a%202d%20image%20to%20a%20mesh.md)
- [UE 5.8 Material Properties](https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-engine-material-properties)
- [UE 5.8 Using Transparency in Materials](https://dev.epicgames.com/documentation/en-us/unreal-engine/using-transparency-in-unreal-engine-materials)
- [UE 5.8 Using Colored Translucent Shadows](https://dev.epicgames.com/documentation/en-us/unreal-engine/using-colored-translucent-shadows-in-unreal-engine)
