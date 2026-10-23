# 独立 Dev 开始—三幕—结束—重演：验收记录

日期：2026-10-09。唯一人类作者与负责人：用户。Codex 按授权辅助实现、测试与记录，不是制作成员。本记录不代替作者的实体输入、盲测或参赛签收。

## 1. 直接打开

资源管理器中打开 `D:\灯影山海`，双击 `Start-EntryLoopDev.cmd`。如果聊天中的文件链接显示代码，请在资源管理器中双击，不需要编辑脚本。

当前默认使用字号修复包 `Builds/EntryLoopDev-20261009-Run2/Windows`，新地图 `/Game/DengYingShanHai/Dev/EntryLoop/Maps/LV_EntryLoopDev`。不要直接双击包内 exe：源 Config 未改变，裸 exe 可能打开旧默认灰盒。下文初次闭环的构建、校验和流程结果仍对应保留的 Run1；本次增量结果见末节。

启动后先看到开始面板。点击“开始复演”，再使用原有 E 操纵/放开、A/D 调整、R 当前规则复位。第一、二幕成功后题签仍停留既有 2 秒；第三幕保持既有 1.25 秒候选判定，实际落杖和林影完成后显示“复演已成”。点击“重新复演”会短暂加载，重新显示开始面板。没有暂停或 Skip。

已有 UE/游戏窗口时启动器会提示正常关闭，不强行终止任何进程。启动记录位于 `Saved/Audit-2026-10-09-EntryLoopPlay`，运行编号自动递增，旧记录保留。

## 2. 精确实现范围

源码修改 2 项：DYPuzzleDirector.h/.cpp 的延迟启动与原生可信入口；新增 5 项：DYDevEntryPlayerController.h/.cpp、DYDevEntryWidget.h/.cpp、DYEntryLoopAutomationTests.cpp。

仅新增 2 个 Dev 资产：独立 GameMode Blueprint 与 LV_EntryLoopDev 地图。没有编辑旧 ThreeAct Presentation/HUD/Cue、三个 Definition、中文字体或森林资产。新菜单原生 UMG 使用既有 OFL 中文字体，无新资产采购、插件或外部服务。

Director 唯一拥有三幕事实；默认自动启动保持旧行为。新控制器只在精确 EntryLoop Dev 世界且非 Shipping 下启用菜单；经本世界 GameMode 注册链读 Stage，不扫描世界。Widget 只转发开始、重演和退出意图，没有答案、完成或裸 Director 接口。UIOnly/GameOnly 与 cursor/focus 归该 LocalPlayer 的控制器；不写 POV，不修改 Explore/Manipulate 映射。

标题阶段无采样计时器，不产生第一个 Activation Token，灯偶不能操纵。普通 StartCurrentPuzzle/ResetCurrentPuzzle 不能绕过初次开始门控。最终菜单只消费真实 Complete；AwaitingFinale 期间隐藏。重演消耗一次请求，正常结束操纵后下一帧 OpenLevel 精确同地图。EndPlay 清理计时器、委托和 View；TravelFailure 可恢复原结束菜单保留林形，但该失败分支仅源码审查，未制造实际丢包故障。

## 3. 验证结果

| 检查层 | 实际结果 | 不代表什么 |
|---|---|---|
| Editor 原生编译与回归 Native-Run3 | 构建退出码 0；110 succeeded / 0 failed / 0 notRun，104 项原有＋6 项新增 | 不等于真人操作 |
| 资产冷读 AssetColdVerify-Run1 | 成功；保存 0；11 个原依赖哈希一致；灯偶/地线/机位/三幕配置与旧场景一致 | 不等于最终美术 |
| 可见流程 VisiblePlay-Run1 | 37 项检查；两轮完整流程；两次真实 15 枝成林；15 张截图；UE 实际退出码 0 | 不是打包流程，也不是物理键鼠 |
| 新包 Build/Cook/Stage/Archive | 原生 UAT 实际退出码 0，49 个打包产物共 1,042,329,044 字节（不含后来写入的身份 JSON）；11 项真实运行依赖均在 UFS manifest | 不等于完整包内通关 |
| 打包首帧 PackageSmoke-Run1 | 精确新地图加载、中文标题及两按钮清晰、截图存在；20 秒后 UE 自身正常退出，退出码 0；未检出 Fatal/Error 行 | 未点击按钮、未通关 |
| 启动器只读 LauncherDryRun-Run1 | Windows PowerShell 5.1 的 Auto/Package/EditorGame 和 CMD 包装器均退出 0；Auto 选固定新包 | 没有通过启动器进行真人通关 |

新增 6 项原生覆盖：真实待演、可信单次开始、错误调用方/引用/未就绪、旧自动启动不回归、重入与销毁、公开 UI 边界及中文标签。

动态脚本等候标题 3 秒后广播真实 Primary 按钮的 OnClicked，通过生产请求链开始，而非直接改 Phase。仅使用公开灯偶参数请求触发原有原生判定、落杖、接触与成林。第一轮结束后同一按钮请求真实 OpenLevel；第二轮在新 World 返回待演，旧完成 Token 无效，旧林不残留，重新完成三幕。过程校验包括单条件拒绝、中途复位、既有保持及题签、Complete 前不显示结束菜单、重复请求拒绝和最终画面保留。

## 4. 留存失败与更正，未降低断言

- Native-Run1 编译失败：新控制器局部 Pawn 命名触发继承成员遮蔽 C4458；只改为 ControlledPawn 并补显式 include，NativeFix-Run1 留有修正前镜像。
- Native-Run2 为 105 成功/5 失败：新测试夹具漏了 Stage 强制要求的 Environment 引用。TestFixtureFix-Run1 补全真实依赖后，Native-Run3 全部通过，没有降低断言或用伪造状态填补。
- Package-Run1 的 UAT 成功，但包装脚本核查多要求旧 ThreeAct GameMode。新 GameMode 是 native-base Blueprint 的独立副本，不继承或引用旧文件；冷读和实际 manifest 证明旧 GameMode 不属于运行依赖。PackageVerify-Run1 修正清单、复验原文件哈希、生成新包身份；未重建或改变包，原脚本和失败记录保留。

新包 native exe SHA256：`D69FA2803CD84A9287007B48F56755230163E60EC0A8288749A1A1FC60A64201`。引擎 UE 5.8.3、Win64 Game Development、By-the-Book、Pak＋IoStore。精确 UAT 参数、编译器记录、匹配 PDB、日志、manifests 和完整文件校验保存在本轮审计。

Cook 显式根仅 EntryLoop；现有 Config 同时纳入旧 LV_InteractionLab 和 Engine Entry。未改默认地图、CookAll 或全局目录。这是 Dev 包中的已有配置附带地图，不新增竞赛场景；新启动器显式选择 EntryLoop，正式 Cook 收敛另行验收。

本次只对 UAT 子进程隔离日志目录和追加 localhost NO_PROXY 排除，沿用已证实的本机 Zen 路由。未提权、改 ACL、系统代理或全局环境。

## 5. 仍待作者真人检查

以下是闭环初次交付时的待验清单，未由脚本代勾。用户后续已明确签收整套正常流程，覆盖与未单独覆盖的项目见第 8 节；不追溯把一个整体回复解释成全部边界测试：

- [ ] 新入口确实打开开始面板，静置后不会自行开演；鼠标点击“开始复演”有效。
- [ ] 进入第一幕后鼠标视角、E/A/D 正常；没有菜单 cursor 或焦点截留。
- [ ] 第一、二幕仍按原规则完成、停题签并切幕；各幕入场不能自动通关。
- [ ] R 按当前幕/当前操纵规则复位，不跳回整段或绕过开始面板。
- [ ] 第三幕仍由玩家状态连续落杖、A 端接触 Z70、真实投影成林；完成前没有结束面板。
- [ ] 成林后“重新复演”能点击，短暂加载后回开始；第二轮没有旧影、旧成功或自动完成。
- [ ] 第二轮可完整结束，菜单“退出游戏”正常关闭，无残留游戏进程或异常退出。

原生旅行失败恢复、不同显示比例、目标机三轮完整包内通关和 Shipping 均未全验。正式美术、声音、周围剧场、5–8 分钟时长及文化资产接入尚未完成，不因为本闭环通过而自动验收。

## 6. 文件、责任与回退

总审计：`D:\灯影山海\Saved\Audit-2026-10-09-SoloEntryLoop`；实现前镜像 `Before`；修正镜像 NativeFix/TestFixtureFix；Native-Run3、AssetColdVerify-Run1、VisiblePlay-Run1、Package-Run1、PackageVerify-Run1、PackageSmoke-Run1、LauncherDryRun-Run1 均独立保留。

源码还原需要使用对应前镜像并先核实后续用户编辑，不建议一键覆盖。新测试资产与入口独立命名，旧入口和旧包可继续作为对照。未 commit/reset/clean、删除文件、覆盖用户原始美术或操作 WorkBuddy。最终范围核查以 `SCOPE-FINAL.json` 为准，不因本记录文字而臆称无改动。

单人规则已进入 AGENTS、SOLO_PRODUCTION 及主要策划/资产文档。许可模板的一项读取曾被权限审批拒绝，保留未修改；其余历史责任表尚未逐项改写，以最新单人规则为当前准则。外部资产署名义务不能据此视为已完成。

当时的下一动作是由用户签收实体流程。用户现在已明确完成正常闭环检查，详见第 8 节；后续仍按单人、免费资产和文化依据推进可读性，不自动扩玩法、场景或资产采购。

## 7. 菜单按钮字号修复（2026-10-09）

用户报告两个开始按钮字号不一。已核实原因：PrimaryLabel 为 24，QuitLabel 为 20；画面中的退出按钮实际文案为“退出游戏”，本轮不改文案和行为。两个按钮改为共用同一 `ButtonFontSize=24`，继续同一中文字体及 Regular 字重，开始、重演及退出字号一致。

只改 DYDevEntryWidget.cpp 的这两处字号入口，DYEntryLoopAutomationTests.cpp 增加一个真实原生 WidgetTree 样式测试。覆盖 Start/End/Reloading 的完整 FontInfo 一致、24 号及退出文案不变；全量回归 111 succeeded / 0 failed / 0 notRun，实际进程退出 0。没有改判定、流程、输入、镜头、按钮颜色、地图或素材。

独立重建 Win64 Development Run2，原 Run1 完整保留。只有新包字体画面复核通过后才将 Scripts/Start-EntryLoopDev.ps1 的固定包路径切换到 Run2；CMD 入口地址不变。打包、原生截图、启动只读验证和前镜像位于 `Saved/Audit-2026-10-09-MenuFontFix`。最终是否已推广及实际图像结果以该目录 PUBLISH.json、VISUAL-REVIEW.json 与 FINAL.json 为准，不用这里的计划性描述代替实际证据。

字体修复的技术测试本身没有新增真人操作签收。用户后续明确完成新版正常流程，独立记录在第 8 节，不改写本轮技术审计为物理输入脚本测试。

## 8. 用户人工签收：新版正常闭环（2026-10-09）

字体修复后，用户明确“字体修复完成，继续下一步”；针对“是否已在新版中检查完开始复演 → 三幕操作 → 成林 → 重新复演 → 第二轮 → 退出游戏”的问题，明确回答“整套流程已检查，全部正常”。当前默认入口对应保留的 Run2 字号修复包。该结论来自用户反馈，不冒称 Codex 观察到物理键鼠操作。

- [x] 开始复演及三幕正常操作完成。
- [x] 第三幕成林结果正常。
- [x] 重新复演及第二轮正常流程完成。
- [x] 退出游戏正常。
- [x] 菜单按钮字号修复得到用户确认。

此回复不单独覆盖新包中的 R 局部复位、标题静置、失焦恢复、重复点击、旅行失败注入、三轮目标机通关、首次玩家盲测或性能测量；已有客观测试与过往单幕检查分别保留，不由此扩大签收。正式美术、声音、5–8 分钟和 Shipping 仍未完成。

闭环正常路径的技术证据与人工签收已齐，可推进下一项“目标可读性”专题准备。M2 完整表中的占位声音、Skip/中断和文化感知等未完成项仍独立列账，不宣称整个 M2/M3 或竞赛成品全部通过。下步方案见 `ALPHA_VISUAL_GUIDANCE_PLAN.md`，呈现方式及独立地图的菜单边界调整需确认后实施。
