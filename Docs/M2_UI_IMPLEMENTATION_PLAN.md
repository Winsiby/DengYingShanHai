# M2 中文引导与状态反馈｜最小接入提案

日期：2026-10-03。状态：**Implemented / Technically Verified / User Signed-off**（用户已确认「中文 UI 正常」及 P02 11 项人工检查全部正常；不表示整个 M2 三互动里程碑或竞赛作品完成）。
项目负责人/Codex负责技术设计、实现和独立验收；桌面WorkBuddy只核对与同步文档；
队友按原分工负责后续正式美术，不将本小步同时分配给两人。

> **当前状态说明**：本章以下内容保留**提案时**的方案论证与候选文案，
> 其中「尚未实施」「未下载/未导入字体」等表述是**提案时事实**，
> 不代表本轮当前状态。当前进展见 §9 与
> `Saved/Audit-2026-10-03-M2UI/Execution-Contract.md`。
> **当前签收更新**：中文 UI 与 `M2_VALIDATION.md` §5 的 11 项已获用户明确签收。正式美术、最终主地图、音效、P03 与完整作品仍未完成。以下早期有限签收/候选分析保留为历史，不替代最新结论。

> *永远不要以牺牲架构设计为代价追求功能；永远不要基于猜测进行权衡——必须与用户确认。*

## 1. 已确认事实与本步边界

（提案时事实）用户当时明确答复“看清了，操作正常”，仅签收 Dev/M2 布局修复的主观可读性与操作手感，不能由此推定 11 项检查通过。**后续已单独确认**「11 项已逐项检查，全部正常」，当前签收见 §9；仍不把整个 M2 三互动里程碑关闭。

本提案仅处理现有M2操作提示、五种状态反馈、中文字体及布局。首次接入仍在现有Dev/M2地图中，不新增场景、菜单、背包、操作键、音效系统、第三幕或结束界面。5–8分钟目标与团队分工不变。最终主地图接入和最终视觉风格另行验收。

## 2. 源码审查结论

| 当前实现 | 已核实事实 | 正式UI不能直接照搬的原因 |
|---|---|---|
| DYDevInteractionHUD.h/.cpp | AHUD Canvas绘制；读取聚焦/操纵状态；订阅Presentation快照；英文ASCII | 没有可验证的中文字体资产；不是UMG表现层；Dev类不能直接称正式UI |
| DYStageGameMode.cpp | HUDClass设置在 !UE_BUILD_SHIPPING 中；Presentation注册同时受Dev路径限制 | Shipping默认不挂载该HUD，非Dev地图没有这条注册链 |
| DYStagePresentation.h/.cpp | baseline/Interrupted单计时器逻辑可复用；默认GetFeedbackDisplay为Dev读数；更新与计时器受Dev/Shipping门控 | 仅新建Widget并读取旧getter，在正式地图/Shipping仍会得到Hidden |
| OnFeedbackDisplayChanged | DECLARE_MULTICAST_DELEGATE，原生委托 | 不是BlueprintAssignable，不能臆造“蓝图直接绑定”节点 |
| DYInteractionComponent.h | OnFocusChanged、OnControlStateChanged是BlueprintAssignable；getter只读 | 可直接复用，Widget不得重跑射线或判断可操纵条件 |
| 模块Build.cs | 当前仅Core/CoreUObject/Engine/InputCore/EnhancedInput | UMG接入是新模块依赖，需明确确认而不是静默加入 |

以上是直接读取源码的结论，不推测任何现有.uasset事件图。已核对本机UE5.8头文件包含CreateWidget(OwnerPC, Class)、AddToPlayerScreen、NativeDestruct、Controller.OnPossessedPawnChanged；未来蓝图或资产自动化步骤须再次按本机API验证。

## 3. 方案比较与推荐

| 方案 | 优点 | 代价/限制 |
|---|---|---|
| A：只替换Dev Canvas文本并导入字体 | 变更较少；可快速验证中文字符 | 仍非Shipping可用正式UI，后续要继续迁移；Canvas排版和美术编辑能力有限 |
| B：薄C++绑定适配器 + UMG表现；推广公共玩家提示、调试继续隔离 | 复用现有反馈逻辑；可测试生命周期；BP调样式；面向Shipping | 需UMG依赖、Widget/字体资产及正式提示与Dev门控的有限迁移 |

**推荐 B（用户已于 2026-10-03 确认采用）。** 不为这个单玩家、单舞台Demo搭CommonUI、MVVM插件、全局事件总线、UI路由Subsystem或新存档系统。

## 4. 推荐方案的依赖、所有者与生命周期

```text
UDYInteractionComponent ──聚焦/操纵事件────────────┐
                                                ▼
ADYPuzzleDirector → ADYStagePresentation → 薄C++ HUD适配器 → WBP_DYInteractionHUD原型
                     │                       │                    │
                     └→ StageEnvironment     └→ 当前本地PC拥有      └→ 仅绘制中文和样式
```

- HUD适配器使用AHUD与当前OwningPlayerController关系，不另建玩家控制权；仅维护Widget实例、当前Pawn/Interaction和Presentation弱绑定。
- Widget使用当前PC创建并AddToPlayerScreen；不抢鼠标/键盘焦点、不修改Enhanced Input Context、不调用SetViewTarget，不增加操作控件。
- Presentation继续是离散状态、恢复基线与唯一Interrupted计时器的所有者。公共玩家提示只包含Hidden/Adjust/Near/Holding/Interrupted/Complete，不传Target、Tolerance、Current、精确Progress或答案数值给Widget。
- 公共玩家提示与开发诊断分开：公开玩家快照/原生变更通知可用于Development/Shipping；旧Dev读数可保留为门控包装，开发参数、目标球和射线仍仅!Shipping且-DYDebug，不整体放开Dev开关。
- 最小迁移重用一份baseline/override状态和一份计时器算法，不在Widget或新BP里复制保持/打断判定。旧Dev读取接口的兼容行为和测试要明确保留或更新契约说明，不靠删除断言通过测试。
- C++适配器订阅原生Presentation委托，转换为Widget只读快照更新或声明的Blueprint事件。Widget不直接绑定不存在的动态委托，不让多个BP分别解释导演样本。
- 初始化覆盖两种BeginPlay顺序：先订阅注册变化，再读取已注册实例的只读快照；迟到UI不调用SynchronizeFromDirector、不重放成功/环境事件。
- Presentation切换先解绑旧实例；Pawn切换解绑旧Interaction再绑新Pawn。EndPlay/Widget移除/PC销毁清绑定、清UI引用，旧Actor卸载不能清除新绑定。没有世界扫描或UI Tick属性绑定。
- 状态只是当前世界/当前本地玩家的表现信息，不入Data Asset/CDO，不存档，不复制，不做联机。

## 5. 玩家看到的内容（候选文案）

普通界面不出现开发数字。操作文案先清楚，文化含义由题签与舞台动作体现，避免诗化到看不懂。

| 场景/状态 | 候选显示 |
|---|---|
| 无聚焦、未操纵 | “对准灯具或皮影” |
| 聚焦可操作对象 | “E　操纵” |
| 正在操纵 | “A / D　调整　　E　放开　　R　复位” |
| Adjust | “继续调整” |
| Near | “影形渐合” |
| Holding | “保持此刻” |
| Interrupted | “影形未稳，再试一次” |
| Complete | “逐光成形 · 成”——仅表示当前P02完成，不称整局通关 |
| 无活动谜题/引用失效 | 隐藏状态行；引用缺失在Development日志告警，不显示错误参数 |

P02题签“逐光成形”只作段落标识，不追加长故事字幕。不添加百分比、箭头指向答案或目标值。

布局建议：准星仍在屏幕中心，保留已认可的“绿=可操纵”语义；操作提示和状态放到底部安全区、分两行，留出幕布观察空间。题签小幅放在顶部/侧上方安全区，避免遮挡关键投影。纸白正文、暗色轻底衬、少量暖金/朱红点缀，暂不加入花纹贴图或复杂动画。具体像素、字体大小、DPI曲线和淡入时长由1080p/720p实拍决定，**不宣称这些候选已验证或是最终美术**。

## 6. 字体来源与许可

沿用ASSET_SOURCES.md现有候选，不采购字体。

- UI正文：[Adobe Source Han Sans / 思源黑体官方仓库](https://github.com/adobe-fonts/source-han-sans)，优先简体中文静态字体、单常规字重；官方[2.005R发布页](https://github.com/adobe-fonts/source-han-sans/releases/tag/2.005R)可提供字体版本来源。
- 题签可用[Adobe Source Han Serif / 思源宋体官方仓库](https://github.com/adobe-fonts/source-han-serif)，首轮如果只验证功能，可先全用同一黑体以减少未验证资产；是否接入第二字体不预先扩项。
- 已联网读取[思源黑体OFL1.1许可](https://raw.githubusercontent.com/adobe-fonts/source-han-sans/master/LICENSE.txt)与[思源宋体OFL1.1许可](https://raw.githubusercontent.com/adobe-fonts/source-han-serif/master/LICENSE.txt)：允许按许可嵌入/随软件分发，须保留版权及许可；不把字体单独出售，修改版需遵守保留字体名条款。
- **（提案时事实）** 本提案撰写时尚未下载、安装或导入字体。**当前状态**：官方字体已由 Codex 导入；实施时记录确切文件名、发行版本、下载日期、SHA256、原文许可存档与发布位置，之后才进入LICENSES.md“已使用”台账。优先未经修改的官方静态文件，不首轮子集化或自制字形。
- UE必须使用项目Font/FontFace资产及显式引用，不能依赖本机Windows字体、编辑器回退或系统安装。字体导入成功不等于Cook字形可用，要在独立包中验证“逐光成形、操纵、复位、影形未稳”等全量文案与标点；若OTF实测导入不兼容，停下报告，不静默换不明字体。

## 7. 实施文件、资产与回退（候选清单）

（提案时表述）确认 B 后先做精确备份与新基线，提交逐文件执行合同。
**该合同已产出：`Saved/Audit-2026-10-03-M2UI/Execution-Contract.md`。** 实际增减清单须先说明。预计：

- 修改公共提示边界：Source/DengYingShanHai/Public与Private/Stage/DYStagePresentation.h/.cpp，Core/DYStageGameMode.h/.cpp，Stage/DYStageFeedbackTypes.h（如需）；保留导演与Evaluator不变。
- 新增薄宿主和视图C++基类：Public/Private/UI/DYInteractionHUD.h/.cpp、DYInteractionHUDWidget.h/.cpp（均为候选名）。单份中文FText映射放视图层，不在谜题层存文案。
- 模块DengYingShanHai.Build.cs：明确UMG及必要的Slate/SlateCore依赖；只有源码实际使用时加入，不启用额外插件。
- 测试：现有DYFeedbackAutomationTests.cpp保持原回归有效；新增玩家提示生命周期、适配器及中文字形/布局验收，不改输入或聚焦逻辑测试。
- 首轮表现资产留Dev/M2/UI：Widget原型、原型HUD/测试GameMode配置、Font/FontFace及许可源文件记录。仅在现有M2地图显式选择该测试GameMode，**不改DefaultEngine.ini或全局默认地图，不影响M1**。不把原型当正式主地图UI。
- Scripts中新增只处理白名单Dev/M2/UI的配置/验证工具；先核实本机UMG/Font资产API，不能猜Widget Blueprint节点或用重建共享舞台BP来接UI。
- Docs/TECH_SPEC.md、M2_VALIDATION.md、LICENSES.md及本方案同步；资产哈希、许可、截图、测试与Cook清单进Saved证据目录。

回退：退出相关UE进程，按本步逐文件备份只恢复明确改动，不reset全仓；M2测试GameMode退回原来的选择，原Dev HUD与地图修复继续可用。新增原型未被正式资产引用前保留为隔离资产，不为回退删除用户文件。既有脏工作树、未跟踪Stage资产必须独立保全，不自动commit。

## 8. 验收顺序与降级

1. 先复验旧25项与M2已保存约束，形成实施前基线；不能只用退出码。
2. 公共反馈边界：真实时间驱动打断计时器；到期恢复最新基线；Activate/Holding/Resolve/EndPlay取消；重复取消不延长；无活动谜题Hidden；Dev诊断仍隔离。
3. Widget/HUD：迟到注册、两个BeginPlay顺序、切换Presentation/Pawn、销毁重建、同一对象不重复绑定；不重演环境状态，不泄露Target或Progress。
4. 真实RHI，720p/1080p及当前屏幕：中文不缺字/不裁切；中心准星与幕上因果清楚；上下两行不遮核心图形；已认可E/A/D/R行为不变。
5. 相同M2单条件失败、组合Holding、打断再试、成功/R至少重复复验；静音仍可完成。音效接入不是本小步前提。
6. Editor与Game Development/Shipping编译通过；显式Cook M2测试地图检查UI/Font依赖；独立打包进程验证普通玩家中文提示存在、开发参数仍不存在。首次包标记技术验证包，不冒充竞赛完整Demo。
7. 用户签收UI布局与措辞，再决定正式题签风格、声音编排和正式主地图接入。

缺字体/Widget：日志说明并保留可控玩法，优先恢复已验证Dev HUD，不能静默保留两套重叠UI。如资产自动化受限，提供明确编辑器组装步骤并验收，不启用非必要插件绕过。任何需要改变镜头、谜题条件或输入上下文的改动暂停，与用户确认。

## 9. 架构决定：已确认

**用户决定（2026-10-03）**：明确答复「**采用方案B且允许**」。

**确认范围**：

- 采用**方案 B**：薄 C++ 绑定适配器 + UMG 中文视图；
- **公共玩家提示与 Dev 诊断分开** —— 玩家侧离散提示可面向 Shipping，
  开发参数、目标球与射线仍仅 `!Shipping` 且 `-DYDebug`；
- **首轮范围**：仅在现有 **Dev/M2** 验证，使用**许可清晰的免费官方字体**。

架构记录见 `ARCHITECTURE_DECISIONS.md` 的 **ADR-013（Accepted，2026-10-03）**；
逐文件白名单与禁止项见 `Saved/Audit-2026-10-03-M2UI/Execution-Contract.md`。

**当前进展：本小步已实现并通过技术验收，用户已签收 UI 布局与措辞，并明确确认 P02 的 11 项逐项人工检查全部正常。**

- 项目自动化 **30 Success / 0 Failed**（实施前 25），**新增 5 项测试**、未删旧测试；
- UI 冷读 **20 PASS**；M2 原玩法／保存约束冷读 **35 PASS**（均 0 error / 0 warning）；
- Editor / Game Development / Game Shipping **三目标编译 Succeeded**；
- M2 Development 与 Shipping **完整 Cook / Stage / Package 技术包**均 BUILD SUCCESSFUL；
- 真实 RHI 键鼠闭环已在 Editor PIE、Development 独立包（1920×1080）与
  **Shipping 独立包**上验证；720 高客户端实测 **1279×720**（DPI 舍入，非精确 1280×720）。
- UI 资产默认配置来自**原生 UMG 树 + Widget Blueprint**（字体、题签、颜色等），
  **并非**手工搭建 Designer 节点图。

**收尾补验**：同一真实 GUI Editor 会话连续执行两次配置，均 0 个产品文件哈希变化，每次 20 项 UI + 35 项 M2 检查通过；外部复核 84 个产品文件未变。见 `Saved/Audit-2026-10-03-M2Closure/Supervisor-Results.md`。不是两次独立冷启动测试，本轮未重编译或重打包。

**保留风险**：**其他机器兼容未测**、
**完整三轮竞赛流程未测**；既有引擎 smoke-test 本地化 Error、MSVC 与 RHI `TSR` 警告**保留**，
**不声称整份运行日志零警告**。

**Dev／Ship 技术包不是完整竞赛作品**，不含正式美术、最终主地图接入、音效与 P03。

**范围限制**：方案 B 当时只批准 UI 迁移；随后用户单独确认了 P02 11 项人工检查。因此该清单现已按用户报告勾选，不代表最终美术、最终主地图、音效或 P03 获得签收。下一步进入第三幕 Dev 原型准备，不把 P02 切片关闭称为整个 M2 完成。
