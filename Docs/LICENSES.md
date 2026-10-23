# LICENSES｜第三方资产与合规登记

## 1. 当前状态

本轮实际新增并登记 **1 项第三方字体资产**：免费开源中文字体 **Adobe Source Han Sans SC**
（`SourceHanSansSC-Regular.otf`，SIL OFL 1.1），登记见 §2 总表的 `FONT-001` 与 §9.1。

> **（历史断言）** 启动包阶段曾声明「不包含第三方代码、图片、模型、动画、字体、音频或插件」。
> 该描述已随 2026-10-03 导入思源黑体而**不再适用于当前状态**，仅保留为历史记录。

本轮新增字体已登记；**其他引擎／第三方内容仍须按实际使用逐项登记核验**，
本文件不作「除此之外均无第三方内容」的推断。

下表必须在真实资产进入项目时维护。没有登记不等于“无版权限制”。来源或授权不清楚的内容不得进入最终 Demo、截图或视频。

> 本文件用于项目制作管理，不替代专业法律意见或具体赛事规则。提交前应以当届比赛要求和每项资产的实际许可文本为准。

## 2. 登记总表

| ID | 名称 | 类型 | 作者/权利人 | 来源链接/商店 | 版本/下载日期 | 许可名称 | 允许修改 | 允许作品发布/参赛视频 | 是否需署名 | 署名文本 | 证据存档位置 | 使用位置 | 状态 |
|---|---|---|---|---|---|---|---:|---:|---:|---|---|---|---|
| FONT-001 | 思源黑体 Source Han Sans SC Regular | 字体 | Adobe | https://github.com/adobe-fonts/source-han-sans | 2.005／提交 a4f7cf94edfb9d7ffbdfc4841de276358bd7e0f2／2026-10-03 | SIL OFL 1.1 | 未修改、未子集化 | 允许（须随包分发许可原文） | 是（保留版权与 OFL，不等同取消本项目零付费限制） | 保留字体版权与 SIL OFL 1.1 许可全文 | `LICENSES/SourceHanSans/LICENSE.txt`（原文）、`SOURCE.md`（来源）；包内 `DengYingShanHai/LICENSES/SourceHanSans/LICENSE.txt`（NonUFS）| `Content/DengYingShanHai/Dev/M2/UI`（FontFace／UFont／WBP 原型）| **已导入并在本机独立包中显示** |
| FONT-002 | 思源宋体 Noto Serif SC Medium（静态实例 wght=500） | 字体 | Adobe / Google Noto CJK | https://github.com/notofonts/noto-cjk （本机 NotoSerifSC-VF.ttf 实例化）／2026-10-19 | SIL OFL 1.1 | 已修改（可变字体实例化为 500 字重，未子集化） | 允许（须随包分发许可原文） | 是（保留版权与 OFL） | 保留字体版权与 SIL OFL 1.1 许可全文 | `Assets/Sources/UI/MenuV2/Fonts/SOURCE.md`、`NotoSerifSC-Medium.ttf` | `Content/DengYingShanHai/UI/Menu/Fonts/FF_MenuSerif`、`FF_MenuSerif_Font`（主菜单说明牌） | **已导入，本机 720p 已渲染验证** |
| FONT-003 | 思源宋体 Noto Serif SC Bold（静态实例 wght=700） | 字体 | Adobe / Google Noto CJK | https://github.com/notofonts/noto-cjk （本机 NotoSerifSC-VF.ttf 实例化）／2026-10-19 | SIL OFL 1.1 | 已修改（可变字体实例化为 700 字重，未子集化） | 允许（须随包分发许可原文） | 是（保留版权与 OFL） | 保留字体版权与 SIL OFL 1.1 许可全文 | `Assets/Sources/UI/MenuV2/Fonts/SOURCE.md`、`NotoSerifSC-Bold.ttf` | `Content/DengYingShanHai/UI/Menu/Fonts/FF_MenuSerifBold`、`FF_MenuSerifBold_Font`（主菜单说明牌正文） | **已导入，本机 720p 已渲染验证** |
| 示例占位 | 待填写 | 模型/纹理/字体/音频/代码/插件 | 待填写 | 待填写 | 待填写 | 待核验 | 待核验 | 待核验 | 待核验 | 待填写 | 待填写 | 待填写 | 禁止发布直至核验 |

复制空行后填写，不要把“免费下载”“可商用”“来自素材站”当成完整许可。

## 3. 必须保存的证据

每项外部内容至少保存：

- 原始页面 URL；
- 作者或发布方名称；
- 资产名称和版本；
- 下载日期；
- 完整许可文本、订单/授权记录或页面截图；
- 是否要求署名以及准确署名格式；
- 是否允许修改、打包进游戏、公开展示、录制视频和参赛；
- 是否禁止转售、再分发源文件或单独提取；
- 在项目和视频中的实际使用位置。

许可证据建议放在项目外的团队合规存档中；若放入仓库，应避免提交包含账号、订单号、个人信息或不可公开文件的材料。

## 4. 分类检查

### 模型、纹理、动画与 VFX

- 核验是否允许用于交互作品和公开演示；
- 不把原始可编辑资产作为独立下载内容分发；
- 确认团队账号、个人账号和项目授权范围；
- 修改资产后仍保留原作者和许可记录；
- 引擎自带或资产商店内容也要记录来源与适用条款，不写成“无版权”。

### 字体

- 分别核验桌面/游戏嵌入、图片标题和视频使用；
- 记录字体文件名、版本和授权来源；
- 若字体要求附带许可文本，将其加入最终第三方声明；
- 不使用来源不明的网盘字体或只凭名称猜测许可。

### 音乐、音效与配音

- 区分试听、个人使用、商业使用、比赛展示和视频平台发布权限；
- 核验是否要求署名、是否限制剪辑、循环或同步到视频；
- 保存下载页面和许可版本；
- 自制录音记录创作者与参与者授权；
- 提前检查平台版权识别风险，但识别未报警不代表拥有授权。

### 插件与代码

- 记录仓库/商店来源、固定版本、许可证文件和修改内容；
- 核验二进制打包、源码分发和署名/NOTICE 要求；
- 不直接复制许可未知的博客、教程或 GitHub 代码；
- GitHub 参考项目仅用于学习时，也要避免复制其受限素材或代码；
- 最终项目应附上许可证要求的 NOTICE、版权声明或源代码提供方式（如适用）。

### AI 辅助内容

- 记录所用工具、日期、输入素材权属、输出用途和人工修改；
- 不上传无权处理的第三方素材；
- 根据当届比赛规则准备 AI 使用说明或过程记录；
- AI 生成不自动消除字体、角色、商标、训练参考或输入素材的权利风险；
- 最终由团队成员审查并承担交付内容的一致性与合规责任。

## 5. 原创资产登记

原创也应记录，便于证明团队分工和来源。

| ID | 资产 | 创作者 | 创建日期 | 源文件位置 | 使用位置 | 第三方输入/参考说明 | 状态 |
|---|---|---|---|---|---|---|---|
| 待填写 | 待填写 | 项目负责人/队友 | 待填写 | 待填写 | 待填写 | 无或详细列出 | 待确认 |

若多人共同完成，写明各自贡献。若使用了外部参考，不要把“原创”理解为无需记录参考与素材来源。

## 6. 最终署名模板

根据真实登记表删改，禁止保留没有使用的占位项目。

```text
《灯影山海》制作团队

项目负责人：技术、策划、动画、集成
队友：美术、视频

第三方资产与工具：
- [资产/工具名称] — [作者/权利人] — [许可名称] — [来源]

特别说明：
- [按许可要求加入的版权声明、NOTICE 或修改说明]
```

## 7. 发布前检查清单

- [ ] 每项非原创资产在总表中有唯一 ID；
- [ ] 所有来源链接、作者、版本和下载日期完整；
- [ ] 许可允许当前 Demo 分发、公开展示和视频使用；
- [ ] 署名、NOTICE 和许可文本已按要求放置；
- [ ] 最终包未包含无权再分发的源文件、示例工程或素材压缩包；
- [ ] 项目截图、封面和视频中出现的资产也已覆盖；
- [ ] 字体、音频、插件和代码没有被遗漏；
- [ ] 已检查当届比赛关于原创性、AI 工具和提交材料的规则；
- [ ] 删除来源不明或证据不足的临时素材；
- [ ] 团队两人完成交叉核验，并保留核验日期。

## 8. 核验记录

| 日期 | 核验人 | 范围 | 发现问题 | 处理结果 |
|---|---|---|---|---|
| 待填写 | 待填写 | 待填写 | 待填写 | 待填写 |

## 许可登记补充规则（2026-10-01）

完整候选来源与选材边界见 `Docs/ASSET_SOURCES.md`。平台名称不能替代单项许可记录；Fab、Freesound、博物馆开放藏品等均须登记到具体资产页。

实际采用前，为每项外部资源新增一条记录：

| 资产名称 | 项目内路径 | 作者/发布者 | 原始资产页 | 下载日期 | 许可名称/版本 | 许可链接 | 修改内容 | 使用位置 | 许可页存档 | 复核人 |
|---|---|---|---|---|---|---|---|---|---|---|
| 待登记 | 待登记 | 待登记 | 待登记 | 待登记 | 待登记 | 待登记 | 待登记 | 待登记 | 待登记 | 待登记 |

CC0 资源虽然通常不强制署名，本项目仍保留来源；CC BY 必须在片尾/参赛材料中给出作者、资产名、原始链接、许可链接并说明是否修改；SIL OFL 字体随分发版本保留许可文本；Fab Standard 资产不得脱离项目单独再分发。
> 候选资产不等于已使用资产。2026-10-01 已确定的优先候选包括：公版《古今图书集成·夸父神图》PNG/SVG、CC0 Chinese Four-corner Pavilion、CC0 Poly Haven 材质/树木、CC0 Kay Lousberg Forest Nature Pack 免费层、当前免费的 Fab/Quixel European Beech、CC0 Freesound 单文件和 OFL Source Han 字体。只有实际下载、导入或进入宣传物料后，才在正式清单中填写文件版本、下载日期、许可存档和修改记录。详细链接见 `Docs/KUAFU_VISUAL_RESEARCH.md` 与 `Docs/ASSET_ACQUISITION_PLAN.md`。
> **零付费许可规则（2026-10-01）**：本项目不使用付费资产。免费资源也必须有明确许可；没有许可证的公开仓库或只写“免费下载”的页面不能作为授权依据。准入、留证和署名规则见 `Docs/FREE_ASSET_POLICY.md`。

## 9. 已使用第三方资产登记（2026-10-03 起）

### 9.1 思源黑体 Source Han Sans SC

| 项 | 内容 |
|---|---|
| ID | **FONT-001**（对应 §2 登记总表） |
| 资产 | `SourceHanSansSC-Regular.otf`（单常规字重） |
| 作者／权利人 | Adobe |
| 字体家族 | Source Han Sans SC / 思源黑体 |
| 版本 | 二进制 `name` 表实读 **Version 2.005**；固定 release 提交 `a4f7cf94edfb9d7ffbdfc4841de276358bd7e0f2` |
| 来源 | 官方仓库 `https://github.com/adobe-fonts/source-han-sans`；文件取自该提交的 `OTF/SimplifiedChinese/SourceHanSansSC-Regular.otf` |
| 原始文件直链（固定提交） | `https://raw.githubusercontent.com/adobe-fonts/source-han-sans/a4f7cf94edfb9d7ffbdfc4841de276358bd7e0f2/OTF/SimplifiedChinese/SourceHanSansSC-Regular.otf` |
| 原始许可直链（固定提交） | `https://raw.githubusercontent.com/adobe-fonts/source-han-sans/a4f7cf94edfb9d7ffbdfc4841de276358bd7e0f2/LICENSE.txt` |
| 下载日期 | 2026-10-03 |
| 原始文件大小 | 16,529,832 B |
| 原始文件 SHA-256 | `F1D8611151880C6C336AABEAC4640EF434FA13CBFBF1FFE82D0A71B2A5637256` |
| 许可 | **SIL Open Font License 1.1**；允许按许可嵌入与随软件分发；**禁止字体本身单独出售**；修改版须遵守 Reserved Font Name 条款 |
| 署名义务 | **保留字体版权声明与 SIL OFL 1.1 许可全文**。本项目使用官方未修改文件，**未修改字体**，因此不触发 Reserved Font Name 的改名要求。**该署名义务不改变、不豁免本项目的零付费资产约束**（见 §1 与 ADR-P001）：字体免费开源是前提，**不将「可修改字体」等同于「取消本项目的免费／许可清晰要求」** |
| 许可原文 | `LICENSES/SourceHanSans/LICENSE.txt`（原文保存）；来源说明 `LICENSES/SourceHanSans/SOURCE.md` |
| 修改情况 | **未修改、未子集化**；未安装系统字体；未引入思源宋体或额外字重 |
| 使用位置 | `Content/DengYingShanHai/Dev/M2/UI/`：`FF_DYSourceHanSansSC` FontFace（Inline 原始负载）、`FF_DYSourceHanSansSC_Font` UFont、`WBP_DYInteractionHUD` 原型 |
| 发布路径 | `Build.cs` 的 `RuntimeDependencies` 自动把 `LICENSE.txt` 作为 **NonUFS** 放入包的 `DengYingShanHai/LICENSES/SourceHanSans/LICENSE.txt`；**不靠打包后手工补文件**。本机两个包内均已实查存在 |
| 验证 | `Saved/Audit-2026-10-03-M2UI/FontSource/Inspect-Font.py`（只读解析 name/cmap）：45 种实际文案字符（含 U+3000 全角空格）**无缺字**；另已在本机 Editor PIE 与独立 Development／Shipping 测试包**实拍验证**中文显示。**不以 cmap 检查代替显示验收** |
| 状态 | **已导入，并已在本机独立包中显示**；**不是候选** |

**未登记**：思源宋体（Source Han Serif）**未使用**，按提案不预先扩项。

> 字体原始 OTF 与检查脚本保存在 `Saved/Audit-2026-10-03-M2UI/FontSource`
> （`Saved` 默认不入 Git，交付时须保全该证据；产品 FontFace 与许可需跟随正式恢复点保存）。

### 9.2 引擎基础形状与实际默认材质：技术灰盒（GRAY-001 / GRAY-002，2026-10-04 登记）

P03 同根真实树形投影 Dev 样本使用 Unreal Engine 自带基础形状作为**技术灰盒**。
**这两项不是独立第三方资产，也不是本项目原创美术。**

| 项 | GRAY-001 | GRAY-002 |
|---|---|---|
| 资产 | `Cylinder.uasset` | `DefaultMaterial.uasset` |
| 完整路径 | `C:\Program Files\Epic Games\UE_5.8\Engine\Content\BasicShapes\Cylinder.uasset` | `C:\Program Files\Epic Games\UE_5.8\Engine\Content\EngineMaterials\DefaultMaterial.uasset` |
| 字节数 | **36,719** | **34,943** |
| SHA-256 | `0C98CD3B88EED9DA47CDA6412AADD8A3DED95339D3F90574ADF5612C6365516A` | `0E171E57611DF3AF9BF9E4B79D3B15296DE51A84E438DA014405AD2F68EBA03E` |
| 来源 | 随本机既有 **UE 5.8.3** 安装 | 同左 |
| 是否新下载 | **否**（`NewlyDownloaded = false`） | **否** |
| 是否开源 | **否**（`OpenSource = false`） | **否** |
| 官方许可页 | [UE EULA](https://www.unrealengine.com/eula/unreal)（2026-10-04 核验） | 同左 |
| 修改情况 | **未修改源资产**；仅在灰盒中以Actor/组件变换和缩放引用 | **未修改，未替换默认材质** |
| 使用位置 | P03 树形投影 Dev 样本的 10 个枝段（`Scripts/Preview-P03ForestProjection.py`） | 同上 |
| 是否进入产品资产 | **否**——只在编辑器内存中创建，**未保存** `.uasset/.umap` | **否** |

**许可判定（重要，不得弱化）**：

- 这两项属**随引擎安装的 Epic 内容**，适用 **UE EULA §1**；
- **不是 CC0，不是独立开源模型**，**不得**按「免费随引擎」推导为可任意再分发；
- **不作无条件免费/任意再分发的结论。** 是否可随参赛作品发布、
  是否需在作品或宣传材料中标注 Epic 商标/资产、是否有额外署名或审核要求，
  **必须以提交当届赛事规则与 UE EULA 条款复核为准**；
- 正式森林/桃林美术资产确定后，**必须重新逐项登记**，不得沿用本节结论。

**未登记**：候选正式森林资源**尚未采用**，不列为已使用资产。

**使用位置说明**：本轮样本的树形几何、地线与线标记**全部只在编辑器内存中创建**，
运行结束即销毁，**没有保存为游戏资产**。`Start-M3Geometry.cmd` 旧启动入口
**不包含**本样本。证据：`Saved/Audit-2026-10-04-P03ForestPreview/`
（`EngineAssetSource.json`、`Supervisor-Results.md`、`Verification-Run4.json`）。

**实际来源纠正（Codex最终复查）**：Run4的`Prepared.material_source`实读为
`/Engine/EngineMaterials/DefaultMaterial.DefaultMaterial`，不是预检猜测的BasicShapeMaterial。
Run3的过严名称假设检查失败并安全结束；没有更换材质来迎合登记。预检JSON及WorkBuddy原稿保留，
最终`EngineAssetSource.json`只登记上述实际枝段网格与材质。BasicShapeMaterial虽已存在于旧灯/偶源码中，
**本节不把它冒称为本轮树枝默认材质**。本文历史前缀原样保留，新增登记位于末尾，不改旧总表。

## 10. 本项目自制与 AI 辅助内容登记（2026-10-20）

V2.3 要求登记「外部合法资源」与「AI 使用记录」。当前工程内美术/材质/关卡均为**本项目自制或由本项目使用生成式工具产出后人工调整**，未引入第三方素材包：

| ID | 名称 | 类型 | 产出方式 | 使用位置 | 许可/署名状态 |
|---|---|---|---|---|---|
| SELF-001 | 主菜单背景图 `T_MenuBackground` | 纹理 | 本项目生成式图像产出 + 人工裁切/适配 | `Content/DengYingShanHai/UI/Menu`，C++ 菜单底图 | 本项目所有；无第三方署名义务 |
| SELF-002 | 菜单牌位九宫格 `T_PlqNormal/Hover/Pressed/Disabled` | 纹理 | 本项目生成式图像产出 + 人工九宫格切边 | 同上，`SButton` 样式 | 本项目所有；无第三方署名义务 |
| SELF-003 | 戏台/外景/材质（`M_DY_SkyGradient`、`MI_DY_Moon`、`DYTheater_*`、`DYExt*`） | 材质/关卡 | 本项目 C++ 与编辑器脚本程序化生成 | `Content/DengYingShanHai`、`L_DY_Main` | 本项目所有 |
| SELF-004 | 影偶与器物网格 | 模型 | 本项目自制（基础几何 + 程序化组合） | `Content/DengYingShanHai/Puppets`、`Stage` | 本项目所有 |
| SELF-005 | 背景乐 `BGM_DY_MountainSea` | 音频 | 本项目**纯程序生成**（`C:\dy_build\make_bgm.py`：56 BPM、8 小节、五声音阶 Karplus-Strong 拨弦 + 低音长音 + 大鼓 + 锣），无任何第三方采样、loop 包或生成服务 | `Assets/Sources/Audio/BGM_DY_MountainSea.wav` → `/Game/DengYingShanHai/Dev/Audio/Music`，由 `ADYDevEntryPlayerController::StartTheatreAmbience()` 播放 | 本项目所有；无第三方署名义务，可复现 |
| SELF-006 | 段落提示音 `SFX_DY_Gong` / `SFX_DY_Drum` / `SFX_DY_Resolve` | 音频 | 本项目**纯程序合成**（`C:\dy_build\make_sfx.py`）：锣 = 98 Hz 非谐分音 + 噪声起振 3.4 s；鼓 = 76 Hz 下滑鼓皮 + 低通噪声 1.0 s；结算音 = 523/784/1046/1318 Hz 叠音 + 弱锣 2.2 s。无第三方采样 | `Assets/Sources/Audio/` → `/Game/DengYingShanHai/Dev/Audio/SFX`，由 `ADYDevEntryPlayerController::PlayStageCue()` 在章/幕/剧终状态变化时各触发一次 | 本项目所有；无第三方署名义务，可复现 |

- 生成式工具只用于**静态图像底图与牌位纹理**；运行时不调用任何在线生成服务，包内不含外部模型/贴图/音频。
- SELF-005 的音频不是采样素材：波形全部由 `make_bgm.py` 内的合成器算出（噪声激励 + 延迟线拨弦、正弦低音、噪声包络鼓与锣），脚本与 WAV 一并留存，任何人可重跑复现同一文件。
- SELF-006 同理，由 `make_sfx.py` 合成；提示音只做气氛点缀，不是通关判定通道（`DY_MUTE_SFX=1` 可全部静音，谜题仍可完成）。
- 若后续替换为外部素材（例如 GitHub 开源资产），必须在 §2 总表逐项登记来源、许可、下载日期与署名，并保存许可原文。
- 字体仅 `FONT-001/002/003`（SIL OFL 1.1），许可原文随包分发（`DengYingShanHai/LICENSES/SourceHanSans/LICENSE.txt`）。

## 11. A5 灯具外观补齐（2026-10-22）

| ID | 内容 | 实际来源与 AI 辅助 | 使用位置 | 复用关系 |
| --- | --- | --- | --- | --- |
| SELF-007 | 八角纸灯专用网格 `SM_DY_LanternFamily_Unit100` | Codex 辅助编写 Python 标准库几何脚本，在项目内生成 OBJ/MTL；没有下载外部模型、调用付费生成服务或加入运行时在线生成。脚本与自检保留于 `Assets/Sources/DengYingArt/A5-LanternFamily-20261022/` | `Dev/ArtPolish_20261022/Meshes`；主图原有门楼2、檐口3、屋顶3个装饰灯 Actor 的网格引用 | 复用现有 `MI_DY_LanternPaper`、`MI_DY_FramePost_Wood`、`MI_DY_AgedBrass`，没有新增外部纹理或素材包 |

- 原始 OBJ SHA256：`B16817CCC97C05036069AD4F0C4D6D0B6F5DE8AEABBAD89B2435A4E5182D44EE`。单网格768三角形、Paper/Wood/Brass三个材质槽，源网格有限数值/索引/非退化三角/法线/100cm包络自检通过，UE导入后重验材质槽与包络。
- 2026-10-21 的24张概念图及其生成/修订提示词保存在 `Assets/Sources/DengYingArt/Concept-20261021/`；它们是内置 imagegen 辅助的设计参考，没有作为本轮纸灯 BaseColor 或新外部贴图导入。2048版是按用户授权放大导出，原生图另存 Originals。
- 人类作者与最终责任人为用户；AI 是建模脚本、概念图与核查的辅助工具，不列为制作成员。本文旧“仅用于底图与牌位”的描述是当时历史范围，本节补充后续实际使用。

## 12. 三具新增影偶模型（2026-10-22）

| ID | 内容 | 实际来源与 AI 辅助 | 使用位置 | 验证范围 |
| --- | --- | --- | --- | --- |
| SELF-008 | 精卫、刑天、烛龙分件实体影偶、骨骼、姿态及皮面贴图 | 基于本项目既有 Concept-20261021 三张 C1 概念图，Codex 辅助分件、轮廓建模、真实厚度/镂空、刚性骨骼、操杆和材质整理；原参考不改写，源图SHA记录于模型manifest。没有下载第三方角色模型、调用新的图像生成服务或加入付费资产 | Assets/Sources/DengYingArt/ThreePuppets-20261022/Run2；UE Dev/ThreePuppets_20261022 | 三具源模型、FBX冷读、UE骨骼/姿态/材质与独立验证图；不代表正式四幕换偶已完成 |

- 图色由本项目已有AI辅助概念图整理，移除文字、尺寸标线和图例后形成风格化皮面彩图；NormalDX/ORM为本轮本地脚本生成。没有把它们描述为人工扫描或历史复原。
- 制作工具：Blender 4.5.14 LTS、Python、NumPy/Pillow、OpenCV、Shapely和Triangle；仅用于离线生成及验证，不作为新增UE运行时插件或交付库。模型与图稿是输出内容，不包含工具库代码。
- 全部角色文件保留原生可编辑源、FBX/OBJ、分件定义、制作脚本、源图哈希和验证回执。源目录README与Docs/THREE_PUPPETS_MODELS_20261022.md说明交付边界。
- 唯一人类作者与最终责任人为用户，Codex为建模与核查辅助工具。既有概念图历史许可/赛事AI要求仍以主记录为准，本轮没有重新作出法律授权结论。
