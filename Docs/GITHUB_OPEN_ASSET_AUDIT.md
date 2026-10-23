# 《灯影山海》GitHub 开源资产与工具审计

> 审计日期：2026-10-01（仓库状态与最近提交已联网核验）  
> 适用范围：单一戏台、三次核心互动、5–8 分钟 UE5 实时光影交互叙事 Demo  
> 当前结论：采用“上游开放资产 + 项目内二次适配”的路线；不直接套用完整开源游戏，不从随机仓库搬运素材，也不为 MVP 引入不必要的运行时插件。

## 1. 为什么 GitHub 仓库公开不等于资产可以使用

GitHub 的 `Public` 只表示仓库可访问，不自动授予复制、改编、商用或再分发权利。每个候选必须同时检查：

1. 仓库根目录是否有明确许可证；
2. 许可证覆盖的是代码、目录数据，还是仓库内的每一个模型、纹理、字体和音频；
3. 仓库是否只是转载第三方素材，能否回溯到作者的官方上游；
4. 是否存在署名、同许可证分发、禁止单独转售、非商用、禁止再分发等附加条件；
5. 资产能否在 UE 5.8、Windows 打包环境中通过实际导入与 Shipping 包验证。

项目执行规则：**优先从创作者官网或官方仓库下载；GitHub 聚合仓库只作发现和对照，不作为许可证的唯一证据。** 下载时保存来源页、许可证文本、下载日期、版本或提交号和必要截图，并登记到 `Docs/LICENSES.md`。

## 2. GitHub 搜索结果总览

本轮重点搜索了夸父、皮影、传统中式戏台/建筑、树木环境、通用动画和 Blender→UE 工具。结果如下：

- 没有找到同时满足“夸父形象依据可靠、皮影媒介适配、许可清晰、可直接导入 UE、质量达到参赛展示”的成品角色；
- 没有找到适合直接复用的“中国皮影 + UE 实时光影互动”完整项目；
- GitHub 对本项目最有价值的内容，是许可证目录、官方制作工具、通用 CC0 自然资产和开源字体；
- 从别人的完整游戏仓库抽取素材，往往存在许可证覆盖不清、二次转载、依赖链复杂和风格不一致的问题，不进入主方案。

因此，GitHub 检索没有改变夸父的既定路线：依据《山海经》原文和公版历史图像，制作项目专属的 2.5D 可动皮影；通用环境资产则使用官方上游的 CC0/开放资源，再统一材质和轮廓。

## 3. 候选项目审计

| 候选 | 审计时最近提交 | 许可证/来源状态 | 可复用内容 | 部署难度 | 决策 |
|---|---:|---|---|---|---|
| [TMHSDigital/Free-Game-Dev-Assets](https://github.com/TMHSDigital/Free-Game-Dev-Assets) | 2026-09-30 | 目录本身 CC0；外链资产各自保留原许可证 | 377 个左右的来源索引、许可证核查日期、3D 包规模/面数/尺度比较 | 低；无需安装 | **采用为检索与复核目录**，不直接把目录许可证套到外链资产上 |
| [EpicGames/BlenderTools](https://github.com/EpicGames/BlenderTools) | 2026-09-03 | Epic 官方仓库，MIT；工具代码与项目美术资产分开管理 | Send to Unreal、UE to Rigify | 中；需要 Blender 插件安装和 UE 5.8 实测 | **条件采用**；仅在手工 FBX 流程明显拖慢时启用，不成为运行时依赖 |
| [xavier150/Blender-For-UnrealEngine-Addons](https://github.com/xavier150/Blender-For-UnrealEngine-Addons) | 2026-09-02 | GPL-3.0；第三方工具 | 批量导出 Static/Skeletal Mesh、动画、碰撞、Socket、相机等 | 中高；选项多，需额外学习和回归测试 | **备选**；不与 Epic 工具同时安装，主工具失败后再评估 |
| [Quaternius/quaternius.github.io](https://github.com/Quaternius/quaternius.github.io) | 2026-08-28 | 官方网站仓库；具体资源包以各下载页标注为准，常见包为 CC0 | Stylized Nature MegaKit、Universal Animation Library 等通用包的官方入口 | 低到中；需按包导入、规范尺度和材质 | **有条件采用上游资源**；仅补树木、石块、枝叶，不替代中式核心资产 |
| [adobe-fonts/source-han-serif](https://github.com/adobe-fonts/source-han-serif) | 2024-07-30 | SIL Open Font License 1.1 | 思源宋体，用于标题、字幕、说明界面 | 低；导入所需字重并构建字体回退 | **采用**；保留 OFL 文本与版权声明 |
| [NafisRayan/Animate-Rigged-Humanoid-No-Blender](https://github.com/NafisRayan/Animate-Rigged-Humanoid-No-Blender) | 2026-09-18，仅 1 次提交 | 项目组合了 Quaternius CC0 角色与动画，但需分别回溯上游 | 80+ 通用人形动画的 Web/GLB 组合思路 | 中；无 UE 5.8 验证，角色审美通用化 | **不进入 MVP**；夸父只需少量专属剪影动作，大动画库会增加重定向和风格风险 |
| [syuhei176/ai-game-assets](https://github.com/syuhei176/ai-game-assets) | 2026-04-10，仅 1 次提交 | 仓库说明为 Kenney CC0 资产转载 | 8 个低模 GLB：树、石、房屋、塔 | 低，但来源为二次转载 | **排除直接使用**；如需同类资产，去 Kenney 官方上游下载 |
| [eturner58/game-assets](https://github.com/eturner58/game-assets) | 2026-08-26 | 大型目录/镜像，包含不同许可证来源；Kenney 为 CC0，其他包不能一概而论 | Kenney 包的浏览与元数据 | 中；约数万文件，容易误取混合许可证内容 | **仅作检索参考**；不得整库导入，不使用其中非商用免费版素材 |
| [CHI-CityTech/Shadow_puppet_Unreal](https://github.com/CHI-CityTech/Shadow_puppet_Unreal) | 2025-12-11 | **仓库没有许可证**，公开可见不等于允许复用 | UE 5.5.4 Wayang Kulit 皮影展示、幕布前观看方式 | 中；需 Git LFS，且没有 UE 5.8/许可验收 | **禁止复制代码与资产**；只把公开文档当竞品/技术观察资料 |
| [Az-Rof/Unity-Shadow-Puppets-Story-Game](https://github.com/Az-Rof/Unity-Shadow-Puppets-Story-Game) | 2025-11-05 | 根目录 MIT，但美术/音频未在 README 中逐项列出第三方来源 | 爪哇 Wayang 文化叙事、手绘 2D 演出组织 | 高；Unity 2021.3，与本项目 UE 管线不兼容 | **只作创意比较**；不移植资产，不混用印尼 Wayang 造型 |

### 维护状态的解释

“最近有提交”只说明仓库活跃，不代表其适合项目。例如，一次提交的新仓库仍缺乏 UE 验证；活跃的通用动画库也不一定适合皮影。反过来，思源宋体最近一次源码发布虽为 2024 年，但它是成熟字体项目，许可证清晰，项目风险远低于一次提交的素材转载仓库。

### 两个皮影项目带来的边界结论

- `Shadow_puppet_Unreal` 证明了在 UE 中用实体幕面观看皮影动画的技术方向可行，但公开文档描述的核心体验是玩家走到幕布前观看动画，且仓库没有许可证。本项目不能复制其中 `.uasset`、模型或蓝图；我们需要保留自己的“光源参数 + 皮影参数 + 持续确认”互动闭环。
- `Anoman Obong` 有较明确的文化母题和手绘 Wayang 风格，但它是 Unity 2D 横版叙事/动作项目，采用爪哇皮影与《罗摩衍那》语境。它可提醒我们“角色、纹样、声音必须围绕具体文化母题统一”，却不能作为中国皮影或夸父造型的直接素材来源。
- 因此，竞品只贡献方法论：文化研究先行、角色轮廓统一、声音参与叙事；不贡献可导入资产。这样既规避授权风险，也避免把不同地区的皮影传统混成泛化的“东方风”。

## 4. 对《灯影山海》资产方案的实际优化

### 4.1 夸父：不采用 GitHub 成品模型

负责人：用户统一负责免费资源适配、UE 骨骼、材质、Control Rig 和阴影验收。

- 形象依据仍以《山海经》原文与公版历史图像为准，不用通用“巨人战士”模型替代；
- 制作为薄片分层的 2.5D 可动皮影，而不是完整写实人形：头、躯干、上臂、前臂、大腿、小腿、手杖和蛇形装饰按关节拆分；
- 只制作演出所需动作：启幕姿态、追日步态/重心前倾、举杖/弃杖、结尾定格；
- 通用人形动画库只能用于动作节奏参考，不能直接决定夸父的外观和表演；
- 详细视觉依据与技术指标继续以 `Docs/KUAFU_VISUAL_RESEARCH.md` 为准。

这样做的收益是：夸父、灯、影和皮影操控在同一视觉语言里，评委能够一眼看出核心创意，而不会把作品理解为“购买模型后放进 UE 的普通第三人称场景”。

### 4.2 戏台：开源结构件只作底层，核心识别由项目重构

负责人：用户统一负责外观、灰盒尺度、灯光与交互净空。

- 保留已筛选的 CC0 中式四角亭作为“戏台外壳候选”，但不是整场景一键导入；
- 用 UE 基础几何搭出幕框、幕后操作区、台口、两侧观演区和远景院落，确保幕上与幕后双空间都可读；
- 下载模型只保留可用的柱、梁、瓦和基座，删除看不见的背面、高密度装饰和无关碰撞；
- 统一为木、纸、布、漆四类主材质，增加项目自己的剪纸/皮影纹样，避免免费包拼盘感；
- 所有导入物在 `Dev/AssetAudit` 测试图中检查比例、UV、法线、碰撞、阴影、Nanite/Lumen 表现和打包引用后，才进入正式目录。

### 4.3 树林与“弃杖化林”：使用 CC0 基础形体，高潮资产项目化

负责人：用户统一负责树木外观、纹样、生成演出、性能与阴影稳定性。

- 普通远景树、石块、地表细节可从 Quaternius、KayKit、Poly Haven 或 Kenney 的官方上游选择；
- `杖落成林` 的主树不能直接用完整树包替代：以手杖为母体，让枝条沿其轴线生成，再长出具有剪纸轮廓的叶簇；
- 远景和主树可共用基础网格，但主树必须使用独立材质实例、轮廓层级和演出动画；
- 同一镜头内不要混用尺度和面数差异极大的低模树包。TMHSDigital 目录的测量显示，Kenney Nature 树常用于低预算原型，而 Quaternius 自然资产更完整但明显更重，导入前必须统一厘米尺度和性能预算；
- 最终林海使用少量 Hero 树 + HISM/实例化背景树 + 雾中剪影层，不靠堆积大量独立 Actor 制造规模。

### 4.4 动画：删去不必要的大型动画依赖

负责人：项目负责人。

- MVP 不导入 80+ 通用人形动作包；
- 夸父使用 4 组专属关键姿态和少量循环段，优先在 UE Control Rig/Sequencer 中完成；
- 若后续盲测发现步态不自然，只从 Quaternius 官方 CC0 Universal Animation Library 取一个走/跑参考片段进行重定向测试；
- 重定向失败或破坏皮影平面感时，立即回退到项目内关键帧，不让动画库阻塞主流程。

### 4.5 Blender→UE：先用最短链路，再启用插件

负责人：项目负责人。

默认链路：

```text
Blender 源文件 → FBX 导出预设 → UE 5.8 导入 → Control Rig/Sequencer → Windows 打包验证
```

只有在多次迭代中反复出现骨骼朝向、缩放、命名或批量导出错误时，才安装 EpicGames/BlenderTools。安装前记录插件提交号，在独立测试工程验证：静态网格、骨骼网格、动画、材质槽、Socket、厘米尺度和重新导入。插件不随 Shipping 包运行，因此失败时可回退到手工 FBX。

不同时安装 EpicGames/BlenderTools 与 Blender-For-UnrealEngine-Addons，避免导出规则、命名和面板选项互相干扰。

### 4.6 字体与音频

负责人：用户统一负责声音素材筛选、剪辑、UE 集成、混音、打包及字幕字体。

- 字体采用思源宋体的必要字重，保留 SIL OFL 1.1 许可证；不把整个十余 GB 源仓库克隆到项目，只下载官方 Release 中实际使用的字体文件；
- 锣鼓点、吟唱、风声、脚步和枝叶声暂未在 GitHub 找到一套文化语境、录音质量和许可证都合适的统一素材包；
- 音频继续从作者原始发布页逐条筛选，CC0 优先；CC BY 必须署名，NC/ND/研究用途素材不得进入参赛包；
- 即使是 CC0 公共音效，也做剪辑、分层、EQ、变速或音高处理，并保存工程文件，以减少常见素材造成的听感雷同和视频平台 Content ID 误判风险。

## 4.7 第二轮质量复核：低模包退出最终近景

在用户明确要求“高质量、避免廉价感”后，资产优先级调整如下：

- Kenney、KayKit、Quaternius 的通用低模内容只保留为灰盒、碰撞测试或极远景候选，不再作为最终戏台近景；
- 3DAssets.dev 等标明 AI 生成的中式套件只允许用于构图实验，不进入正式镜头；
- 正式基础材质优先来自 Poly Haven、ambientCG 等作者与许可链清晰的高质量 CC0 来源；
- 正式中式道具优先测试 Poly Haven 的 Chinese Screen Panels、Chinese Tea Table、Chinese Stool；
- 戏台建筑优先比较 CC0 BlendKit Chinese Pavilion 与 CC0 Chinese Four-corner Pavilion，前者质量高但约 896K polygons，需要 Nanite/碰撞/材质测试，后者较轻但必须重做材质；
- 高质量付费 Fab 整包不进入项目方案；若免费路线在固定比赛镜头中不足，则缩减可见范围、重组 CC0 模块、统一材质或调整镜头，不申请购买；
- 所有外部模型必须接入项目自己的木、漆、布、纸皮、铜、石主材质体系，禁止原样拼装 Demo Level。

详细质量规范见 `Docs/SCENE_ART_QUALITY_SPEC.md`。

## 4.8 `Shadow_puppet_Unreal` 的新处理方式

该仓库仍因没有许可证而禁止复制代码与资产，但允许借鉴其公开文档中可验证的制作经验。已确认它采用 UE 5.5、平面分片角色、父子层级、Level Blueprint `BeginPlay` 动画、透明幕布实验和正反角色副本；项目白皮书也主动指出枢轴、半透明投影、动画脆弱和显隐状态不一致等问题。

本项目只保留“显式关节枢轴、独立阴影实验关卡、幕布材质 A/B 测试”的思路，并升级为刚性蒙皮 Skeletal Mesh、Control Rig/Sequencer、显式 Puzzle 状态机和统一可见性控制。详细分析见 `Docs/SHADOW_PUPPET_REFERENCE_ANALYSIS.md`。

## 5. 最简单的 MVP 资产清单

| 模块 | MVP 方案 | 来源策略 | 数量上限 | 验收重点 |
|---|---|---|---:|---|
| 夸父皮影 | 项目专属 2.5D 分层角色 | 公版历史图像仅作依据，重新绘制/建模 | 1 套角色、4 组动作 | 剪影识别、关节不穿帮、真实投影稳定 |
| 手杖/主树 | 同一骨架或变形链完成杖→林因果转化 | 项目制作，通用树只作枝叶基础 | 1 根杖、1 棵 Hero 树 | 第三次互动直接触发，转化连续可读 |
| 戏台外壳 | CC0 亭/建筑构件 + UE 灰盒重构 | 官方原始页下载 | 1 套 | 幕上/幕后双空间、交互净空、统一材质 |
| 幕布/灯具/操纵杆 | UE 基础体 + 项目材质 | 项目制作 | 各 1 套 | 阴影清晰、参数变化可见、无遮挡 |
| 院落远景 | 树、石、墙、地表 | CC0 上游包择一，不混多套风格 | 1 套自然包 | 规模感、性能、不过度抢戏 |
| 纹样 | 山纹、水纹、日纹、蛇纹、桃林纹 | 公版图像研究后项目重绘 | 5 组以内 | 不照搬现代作品、服务三段叙事 |
| 字体 | 思源宋体必要字重 | Adobe 官方 Release，SIL OFL 1.1 | 1–2 个字重 | 生僻字覆盖、字幕清晰、许可随包 |
| 音频 | 锣鼓、吟唱、风、脚步、枝叶 | 官方来源逐条核验，CC0/CC BY | 每类 1–3 条母素材 | 演出节奏、署名、无 NC/ND |

这个清单不会扩大场景数量，也不会改变“三次互动复用同一机制”的范围。它把制作精力集中在评委真正能识别的差异上：夸父皮影、灯影交互、幕后/幕上关系与杖落成林。

## 6. 导入门槛与回退规则

任何外部资产进入正式 `Content/DengYingShanHai/` 前，必须通过以下门槛：

1. **许可门槛**：来源、作者、许可证、下载日期、原始链接和修改说明齐全；
2. **文化门槛**：不与先秦神话意象、皮影语言和中式戏台发生明显冲突；
3. **技术门槛**：UE 5.8 正常导入，无丢材质、坏法线、异常骨骼或不可控碰撞；
4. **视觉门槛**：统一木纸布漆材质与剪影轮廓后，不呈现“多套素材包拼接”观感；
5. **性能门槛**：目标电脑下关键镜头稳定，真实阴影不影响逻辑判定；
6. **打包门槛**：Development 与 Shipping 包均无丢失依赖、编辑器专用资源或许可文件遗漏。

回退顺序：

```text
外部高质量资产
  ↓ 导入/许可/风格失败
同许可证的更简单上游资产
  ↓ 仍失败
UE 基础几何 + 项目材质 + 剪影化处理
```

不得为了保留某个素材而修改核心玩法、增加插件依赖或延长主流程。

## 7. 最终选择

### 开发路线

**选择“基于开放资产二次开发”，不是直接使用现有项目，也不是所有内容从零制作。**

- 直接使用：思源宋体、经审计的 CC0 通用树石/基础构件；
- 二次开发：戏台构件、自然资产、材质、轮廓、灯光和演出；
- 自行制作：夸父 2.5D 皮影、手杖化林主资产、幕布、灯具交互件和核心纹样；
- 工具层：GitHub 目录用于发现与复核，Blender→UE 插件仅在测试证明有净收益后启用；
- 明确排除：随机 GitHub 游戏仓库的素材、无许可证文件、仅非商用、研究用途、禁止改编或来源不可追溯的内容。

### 当前阶段不执行的动作

本审计只完成方案收敛和来源筛选。尚未自动下载、安装或导入任何候选资产，也未改变 UE 项目插件列表。后续只按免费/开源 MVP 清单逐项下载到隔离目录、保存许可快照、测试导入，并更新 `Docs/LICENSES.md`；不执行购买流程。

## 8. 主要核验链接

- [Free Game Dev Assets 目录及其 CC0 许可](https://github.com/TMHSDigital/Free-Game-Dev-Assets)
- [EpicGames BlenderTools](https://github.com/EpicGames/BlenderTools)
- [Blender For Unreal Engine Addons](https://github.com/xavier150/Blender-For-UnrealEngine-Addons)
- [Quaternius 官方站点仓库](https://github.com/Quaternius/quaternius.github.io)
- [Adobe 思源宋体仓库](https://github.com/adobe-fonts/source-han-serif)
- [思源宋体 SIL Open Font License 1.1](https://github.com/adobe-fonts/source-han-serif/blob/release/LICENSE.txt)
- [Animate Rigged Humanoid No Blender](https://github.com/NafisRayan/Animate-Rigged-Humanoid-No-Blender)
- [ai-game-assets](https://github.com/syuhei176/ai-game-assets)
- [game-assets catalogue](https://github.com/eturner58/game-assets)
- [CHI-CityTech Shadow_puppet_Unreal](https://github.com/CHI-CityTech/Shadow_puppet_Unreal)
- [Shadow_puppet_Unreal 开启工程说明（UE 5.5.4）](https://github.com/CHI-CityTech/Shadow_puppet_Unreal/blob/main/Engineering%20document%20for%20opening%20the%20Unreal%20Engine%20project.md)
- [Anoman Obong: A Wayang Story](https://github.com/Az-Rof/Unity-Shadow-Puppets-Story-Game)
> **资产预算硬约束（2026-10-01）**：本项目不使用任何付费资产。本文若保留商业资源链接，只作为历史审计与排除依据，不代表采购候选、质量兜底或后续建议。所有正式候选必须是许可清晰的免费或开源资源；统一准入规则见 `Docs/FREE_ASSET_POLICY.md`。
