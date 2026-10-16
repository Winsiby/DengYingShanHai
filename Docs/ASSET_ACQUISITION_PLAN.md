# 《灯影山海》资产获取与落地方案

> 版本日期：2026-10-01  
> 适用范围：竞赛版 5–8 分钟 Demo、单一戏台、三次核心互动  
> 决策：本项目不把个人建模能力作为开发前提，采用“公版/CC0/免费明确许可 + 必要资产定向制作 + UE 内组装与演出编排”的零付费路线。免费方案存在质量缺口时，通过缩减可见范围、统一材质、模块重组和调整镜头解决，不考虑付费资产。

## 1. 总体结论

《灯影山海》的创新重点不是从零制作每一个模型，而是：

- “光源即玩法、影子即角色”的核心机制；
- “发现规律—协同控制—综合运用”的三段学习曲线；
- “杖落成林”由玩家第三次操作直接造成的叙事因果；
- 幕前与幕后的双空间演出；
- 对合法素材进行统一的皮影化、剪影化、色彩和节奏编排。

因此允许核心角色、戏台、树木、灯具和声音来自许可清晰的免费/开源渠道。项目必须保留原始链接、许可截图或许可文本和下载日期，并在提交材料中准确区分“外部资产”与“团队完成的交互、程序、改编和演出”。

## 2. 许可与费用优先级

所有资产按以下顺序选择，不设置付费回退：

1. 公有领域/Public Domain 与 CC0；
2. 开源或自由文化许可且义务可执行的资产，例如 CC BY、OFL；
3. 官方免费但受平台许可约束的资产，例如 Fab/Quixel、Epic 示例；
4. 书面授权的免费合作/委托成果；
5. 免费方案仍不满足时，调整构图、可见范围、材质统一方式或内容数量，不购买资产。

CC BY-NC、仅供学习、仅供编辑用途、来源不明转载、无明确许可和要求不得修改的素材不进入竞赛版。CC BY-SA 需要逐项评估衍生物与分发义务，不作为默认主选。

“免费”只表示当前获取价格为零，不等于开源或无限制；仍要保存下载当日的许可。软件开源也不自动使从网络输入的图片、模型或声音获得开放许可。

## 3. 推荐的最小资产栈

| 类别 | MVP 主选 | 许可/渠道 | UE 5.8 风险 | 需要的二次处理 | 负责人 |
|---|---|---|---|---|---|
| 夸父皮影 | 以《山海经》原文和公版《古今图书集成·夸父神图》为依据，定向制作 2.5D 关节模型 | 公版 PNG/SVG；Blender/Inkscape 免费开源工具；下载时保存许可证据 | 中；需要轮廓清理、分件、薄片建模与骨架 | 保留古图依据，落实黄蛇与手杖；制作同一角色的三阶段姿态，不套用通用武士/野蛮人 | 项目负责人负责考据、建模技术规格、模型生成/整形、绑定和 UE 接入；队友可做视觉复核 |
| 皮影操控技术参考 | Epic 免费示例 `Virtual Puppeteering and Input Based Animation` | Fab / Epic 官方教育示例 | 中；先在空白 UE 5.8 工程验证 | 只借鉴 Control Rig、输入驱动和 Sequencer 工作流，不照搬项目结构 | 项目负责人 |
| 戏台主体 | CC0 `Chinese Four-corner Pavilion` + UE 基础地台、立柱和幕布 | CC0 + UE 工程自建基础几何 | 中；需要在 UE 中重组，但不需要外部建模 | 四角亭只作屋顶/木构母件，结合 Plane 幕布和基础地台形成戏台；不宣称历史复原 | 项目负责人整合；队友做美术复核 |
| 幕布 | UE Plane + 项目材质实例 | 自建引擎基础资产；噪声可用 CC0 纹理 | 低 | 米白半透/双面材质、细微纤维噪声和背光参数；无需建模 | 项目负责人 |
| 木材/地板 | Poly Haven `Old Planks 02`、`Old Wooden Floor 02`；需要单体梁时选 Quixel `Old Wooden Beam` | Poly Haven 为 CC0；Quixel/Fab 按商品许可 | 低 | 下载 2K 或 4K；建立统一父材质并控制粗糙度、色温 | 项目负责人 |
| 邓林高潮 | 当前免费的 Fab/Quixel `European Beech`；开放备选为 Poly Haven CC0 树木或 Kay Lousberg `Forest Nature Pack` 免费 CC0 层 | Fab Standard License / CC0 | 低到中；分别验证写实和风格化树在幕内外的统一性 | 只保留剪影和少量近景树；利用灯光、雾、Niagara 叶片表现“由杖生林”，不追求植物学复原 | 项目负责人 |
| 环境道具 | Sketchfab `Chinese Lantern`（低模、CC BY）或 CC0 Traditional Chinese Lantern，以及 Poly Haven CC0 家具 | CC0/CC BY；CC BY 必须完整署名 | 低到中；导入后核对比例、材质和碰撞 | 严控数量；不让道具遮挡幕布和交互信息 | 项目负责人整合；队友筛选 |
| 字体 | Adobe Source Han Serif / Source Han Sans | SIL Open Font License 1.1 | 低 | 标题可用现成字体做排版与材质效果，不声明为原创书法 | 项目负责人 |
| 锣声 | Freesound `Chinese Gong`（the_very_Real_Horst）或 `Gong.wav`（airtaxi） | 单文件 CC0 | 低 | 裁切、响度统一、添加适度混响；保存单文件许可页 | 项目负责人 |
| 风与枝叶 | Freesound `Leaves and Wind`、`Leaves`、`Soft Wind` | 单文件 CC0 | 低 | 分为常驻风、成功时枝叶扩散、结尾林海层；避免循环接缝 | 项目负责人 |
| 木台脚步/吱呀 | Freesound `wooden footstep`、`Wood creak` | 单文件 CC0 | 低 | 按幕前/幕后空间做声像和混响差异 | 项目负责人 |
| 鼓点 | Freesound `Bass Drum Hit` 等明确 CC0 的单击样本 | 单文件 CC0 | 低 | 在 UE/DAW 中重新编排节奏；只能描述为演出鼓点，不宣称复原某地域传统锣鼓谱 | 项目负责人 |
| 吟唱 | MVP 不强制加入；需要时委托真人短句录制 | 书面授权委托 | 中；主要风险是权利不清 | 交付 48 kHz/24-bit 干声，授权游戏、竞赛、公开视频、剪辑和长期展示；禁止仅口头约定 | 项目负责人联系；队友可协助剪辑 |

## 4. 具体链接

### 4.1 夸父原典、古图与皮影媒介研究

- 《山海经·海外北经》：<https://zh.wikisource.org/wiki/山海經/海外北經>
- 《山海经·大荒北经》：<https://zh.wikisource.org/wiki/山海經/大荒北經>
- 公版《夸父神图》PNG：<https://commons.wikimedia.org/wiki/File:Imperial_Encyclopaedia_-_Spirits_and_the_Supernatural_-_pic47_-_夸父神圖.png>
- 公版《夸父神图》SVG：<https://commons.wikimedia.org/wiki/File:Imperial_Encyclopaedia_-_Spirits_and_the_Supernatural_-_pic47_-_夸父神圖.svg>
- 次级古图 `Kua-fu.gif`：<https://commons.wikimedia.org/wiki/File:Kua-fu.gif>
- Wikimedia Commons / The Met 皮影 Sheet 1：<https://commons.wikimedia.org/wiki/File:Sheet_1_of_figures_for_Chinese_shadow_puppets_MET_DP875734.jpg>
- UNESCO “Chinese shadow puppetry”（只作文化与表演结构研究，网页媒体不自动视为开放资产）：<https://ich.unesco.org/en/RL/chinese-shadow-puppetry-00421?RL=00421>

造型优先级为“《山海经》原文 > 明确题名且出处可核验的公版夸父古图 > 皮影媒介结构”。The Met 皮影图版不再作为夸父身份和外轮廓的主来源，只用于研究关节、透光、镂空和操纵结构。完整证据与模型规格见 `Docs/KUAFU_VISUAL_RESEARCH.md`。

### 4.2 UE 场景、技术示例与植被

- Chinese Four-corner Pavilion（CC0，戏台主方案）：<https://vvaytoyek.itch.io/chinese-four-corner-pavilion-free>
- Chinese Lantern（低模，CC BY，需署名）：<https://sketchfab.com/3d-models/chinese-lantern-0fc4dbf7122141828c16bae9025ce47c>
- Traditional Chinese Lantern（CC0，但源文件较大，导入前应清理和降纹理）：<https://blendswap.com/blend/26978>
- Asian Traditional Props：<https://www.fab.com/listings/28b21976-e9eb-430b-b398-6226efa1fe9f>
- Chinese Lantern（可选，商品页只列到 UE 5.5，必须先测试）：<https://www.fab.com/listings/b2e1f390-496d-4b6d-a5cc-c780b1bdce9f>
- Virtual Puppeteering and Input Based Animation：<https://www.fab.com/listings/408a6c12-b302-42dd-ad46-05883996d89d>
- European Beech：<https://www.fab.com/listings/d11cc01d-9422-41b7-950f-416c9ce79caf>
- Poly Haven CC0 树木：<https://polyhaven.com/models/nature/trees>
- Kay Lousberg Forest Nature Pack（免费层 CC0）：<https://kaylousberg.com/game-assets/forest-nature-pack>
- Old Wooden Beam：<https://www.fab.com/listings/e655fa3c-19e2-463f-b897-1dad5e6bd09d>

项目只使用免费/开放资产，付费 Fab 场景包不进入候选清单，也不保留采购链接。不建议把实验性的 PVE/Nanite Foliage 植被包作为 MVP 依赖；竞赛版本优先使用成熟、许可清晰且容易控制开销的免费树木资产。

### 4.3 CC0 纹理

- Poly Haven `Old Planks 02`：<https://polyhaven.com/a/old_planks_02>
- Poly Haven `Old Wooden Floor 02`：<https://polyhaven.com/a/old_wooden_floor_02>
- Poly Haven 许可说明：<https://polyhaven.com/license>
- ambientCG 许可说明：<https://docs.ambientcg.com/license/>

MVP 默认使用 2K 纹理，只有镜头明显贴近且能证明画质收益时才升到 4K；不使用 8K 作为默认规格。

### 4.4 声音

- Chinese Gong（CC0）：<https://freesound.org/people/the_very_Real_Horst/sounds/240382/>
- Gong.wav（CC0 备选）：<https://freesound.org/people/airtaxi/sounds/76886/>
- Leaves and Wind（CC0）：<https://freesound.org/people/Cinetony/sounds/575380/>
- Leaves（CC0）：<https://freesound.org/people/ericnorcross81/sounds/570759/>
- Soft Wind（CC0）：<https://freesound.org/people/dhallcomposer/sounds/697217/>
- Wood creak（CC0）：<https://freesound.org/people/SilentStrikeZ/sounds/389645/>
- Wooden footstep（CC0）：<https://freesound.org/people/launemax/sounds/250030/>
- Bass Drum Hit（CC0）：<https://freesound.org/people/jcdecha/sounds/235453/>
- Freesound 许可说明：<https://freesound.org/help/faq/>
- Sonniss GDC Bundle：<https://gdc.sonniss.com/>
- Sonniss GDC Bundle License：<https://sonniss.com/gdc-bundle-license/>

Freesound 必须逐文件检查许可。MVP 只选择 CC0；如果以后采用 CC BY，必须在作品与文档中按要求署名。CC BY-NC 不进入可能公开展示、商业传播或权利边界不清的竞赛版。

### 4.5 字体与引擎自带资源

- Source Han Serif：<https://github.com/adobe-fonts/source-han-serif>
- UE Starter Content：<https://dev.epicgames.com/documentation/en-us/unreal-engine/starter-content-in-unreal-engine>
- Unreal Engine EULA：<https://www.unrealengine.com/eula/unreal>
- Fab Standard License：<https://www.fab.com/eula?lang=zh-cn>

## 5. 三条落地路线

### 路线 A：公版夸父古图定向建模 + CC0 戏台（推荐）

1. 以《山海经》两处原文建立造型硬约束。
2. 以公版《古今图书集成·夸父神图》PNG 为视觉依据、SVG 为轮廓处理起点。
3. 清理轮廓，按皮影结构拆成头、躯干、双臂、双腿、蛇形构件和独立手杖。
4. 在 Blender 中增加极薄厚度和简单骨架，导入 UE 后用 Control Rig/Blueprint 控制关节。
5. 使用 CC0 `Chinese Four-corner Pavilion` 的屋顶/木构，加 UE 基础地台和 Plane 幕布重组为戏台。
6. 树林优先使用当前免费的 European Beech；需要完全开放许可时换 Poly Haven 或 Kay Lousberg CC0 树木。

优点：角色身份有原典和明确题名古图依据，许可清晰，皮影媒介特征强，核心资产成本可以为零。  
缺点：需要一次定向轮廓清理、分件和薄片建模；但工作量远低于写实角色建模，也不要求面部、毛发、布料模拟或复杂贴图。

### 路线 B：公版夸父古图定向制作 + 免费/CC0 模块化古建重组

角色路线不变。如果 CC0 四角亭和 UE 基础几何无法达到关键镜头质量，则只从许可清晰的免费/CC0 古建模块中补充少量门、梁、栏杆和地台，并通过统一材质、轮廓、构图和灯光把它们重组为简化戏台；导入前逐项登记来源与许可。

优点：保持零资产预算，同时允许在固定比赛镜头中有针对性地补足结构层次。  
缺点：免费模块的风格与质量不一定统一；若直接照搬会像普通古建场景而不是皮影戏台，因此必须限制资产种类，并强化幕布、后台灯架和观演区。

### 路线 C：3D 人形资产投影为剪影（仅作降级备选）

若 2D 拆件管线在验证阶段无法稳定工作，可选许可清晰且免费的骨骼人形资产，用侧面动画和材质呈现剪影，再通过道具和姿态暗示夸父；没有可留存许可证据的免费资源不得进入正式版本。

优点：动画系统成熟，快速获得行走、奔跑和落杖姿态。  
缺点：皮影关节和材质感显著变弱；通用武士、野蛮人或神话角色容易造成文化身份误读。该路线只保流程，不作为最终推荐视觉方案。

## 6. 采购与验证顺序

任何资产进入正式项目以前，先完成以下顺序：

1. 建立 `Dev/AssetSandbox` 空白测试关卡和资产登记表。
2. 下载并归档《夸父神图》PNG/SVG、《山海经》原文页面及其公版证据。
3. 对照古图制作轮廓清理稿，用临时薄片验证关节、真实阴影和参数判定可以同时工作。
4. 下载并测试 CC0 四角亭、CC0 木材/灯笼与 UE 基础几何组成的免费戏台，先完成幕前/幕后关键镜头。
5. 将 European Beech 与至少一种 CC0 树木备选分别加入测试关卡，测量三档实例数量下的帧率、显存和 Shipping 包体。
6. 下载并归档 CC0 声音、纹理和 OFL 字体许可证据。
7. 如果免费戏台在关键镜头中仍有明确质量缺口，记录问题后调整镜头、遮挡、模块组合和材质；仍不合格则缩减装饰和建筑可见范围，不购买替代包。
8. 只有当画面中仍有明确空缺时，才按单件补购道具。
9. 每引入一项资产，立即更新 `Docs/LICENSES.md`，保存许可页面或文本到 `Docs/LicenseArchive/`，并记录修改内容。

## 7. 夸父定向建模的低门槛处理流程

这不是写实人物雕刻流程，而是“公版矢量轮廓 + 薄片建模 + 简单骨架”：

1. 下载《夸父神图》最高分辨率 PNG 和 SVG，并保留只读副本。
2. 对照 PNG 检查自动矢量化 SVG，修复断线、粘连和噪点，不凭空重画人物造型。
3. 根据《大荒北经》补齐耳侧两黄蛇，并把另外两条黄蛇转译为前臂盘绕构件；该变化登记为互动适配。
4. 按旋转关节拆成头、躯干、上臂、前臂、手、大腿、小腿与足，各段在铆点处保留重叠区域。
5. 单独制作手杖；第三幕手杖必须可以从手部释放并触发落点事件。
6. 在 Blender 中为矢量片增加极薄厚度和必要倒角，建立简单骨架并做近刚性权重。
7. 导入 UE 后建立 Control Rig，验证关节旋转、遮挡顺序、幕后实体和幕布真实投影。
8. 使用同一角色资产制作三阶段姿态，不为每一幕另造一个角色系统。
9. 在提交说明中注明《山海经》原典、公版《夸父神图》、皮影媒介参考和团队的模型重建/程序演出贡献。

详细来源边界、模型命名、性能预算和验收方法见 `Docs/KUAFU_VISUAL_RESEARCH.md`。如果轮廓清理质量不足，可只委托“矢量清稿与皮影分层”，不需要委托写实人物建模。

## 8. 委托矢量清稿或薄片建模时的最小合同要求

免费工具与现有能力无法满足质量要求时，委托范围应尽量限定为：基于指定公版底稿的夸父轮廓清理、关节分层、薄片建模、简单骨架、手杖、三个姿态示意和一套颜色稿。书面约定至少包含：

- 委托方可永久用于游戏、竞赛、宣传视频、现场演示和作品集；
- 允许裁切、改色、动画化、与其他资产合成及后续更新；
- 交付 PSD/PNG 分层源文件和字体/笔刷/纹理来源清单；
- 受托方保证未混入无授权素材，并说明是否使用生成式 AI；
- 是否要求署名、署名格式和费用已结清；
- 不获得对第三方底图本身的排他权，但交付的原创修改部分权利约定明确。

## 9. 明确不采用的素材路线

- 不从百度图片、短视频截图、影视剧、商业游戏或素材预览图中抠取资产。
- 不使用只有“可下载”而没有明确授权条款的模型、图片和声音。
- 不把 CC BY-NC、学习专用或编辑用途资产混入最终竞赛版本。
- 不使用来源不明的“古风素材包”“中国风音效包”或网盘转载包。
- 不把日本太鼓、日式神社、武士角色直接标注成中国传统元素。
- 不为追求规模导入完整城市、百余种植被或超大音效库；只导入最终关卡实际引用的内容。
- 不宣称外部下载的美术资产为团队原创；团队贡献重点写交互机制、技术实现、筛选改编和实时演出。

## 10. 当前推荐决策

采用路线 A：

> 《山海经》原文 + 公版《夸父神图》定向制作 2.5D 关节模型 + CC0 四角亭/UE 基础几何重组戏台 + 免费 European Beech 或 CC0 树木 + Poly Haven 木材 + Freesound CC0 音效 + Source Han 字体 + Epic 免费 Control Rig/虚拟木偶示例作技术参考。

这是当前最能同时保住夸父身份准确性、皮影辨识度、开发可控性、许可清晰度和竞赛创新叙事的一条路径，资产预算固定为零。下一步不是一次性下载全部资产，而是先归档夸父古图及许可、建立轮廓对照稿和关节灰盒，再验证免费戏台组合；出现画面缺口时只讨论零付费的构图、材质、模块和范围调整。
> **零付费约束（2026-10-01）**：本计划只允许获取许可清晰的免费或开源资产，不采购模型、材质、纹理、音频、字体、动画、插件、代码或生成服务。若质量不足，只能通过缩小可见范围、统一重材质、模块重组、远景平面化和调整镜头解决，不能启用付费兜底。详细规则见 `Docs/FREE_ASSET_POLICY.md`。
