# 三幕目标可读性：独立 Dev 样本

日期：2026-10-09 起实施，2026-10-10 完成最终候选回归。唯一人类作者/负责人为用户，Codex 辅助实现与核验。方案 A 及精确地图/同图重演已由用户确认；已确认范围内直接推进，不再逐项请示。本文只覆盖可读性 Dev 候选，不宣布正式美术、首次玩家理解或最终竞赛版本完成。

## 可打开的入口

- 双击 `D:\灯影山海\Start-ReadabilityDev.cmd`；聊天链接如显示代码，请在资源管理器打开 D 盘“灯影山海”目录，再双击此文件。
- 独立地图：`/Game/DengYingShanHai/Dev/Readability/Maps/LV_ReadabilityLab`。
- 旧对照仍为 `D:\灯影山海\Start-EntryLoopDev.cmd` 和 EntryLoopDev-20261009-Run2，不覆盖。
- 开始/结束菜单按钮保持 24 号字。E 操纵/放开，A/D 调整，R 沿用当前幕复位语义。没有新姿态键、跳幕或自动吸附。

## 玩家可见变化与架构

第一幕提供局部弧线缺口，引导观察灯动与头部影子的关系；第二幕增加开放角标，要求沿用灯偶协同；第三幕保留这些线索并加已确认地线上的短标，成功后从真实最终状态继续落杖、接触和成林。

残日/角标是舞台提示，不是真实角色阴影或精确答案描边。原 Movable 主灯、皮影、操杆、真实投影和 15 Hz 参数判定保持不变。提示使用一套原生 Substrate Unlit 的 Masked 材质、三个实例和三个明确引用的被动表面；不投影、不碰撞、不导航。没有外部纹理、插件或额外运行时 Python。

Director 唯一决定幕次、保持、成功；Stage 副本在真实事件后读既有无答案快照并应用幕上线索可见性。只有 Playing 的当前幕几何线索可见，标题、段间成功、落杖/成林和结束态均隐藏。同图重演销毁旧 World，重新建立引用与初始隐藏状态。原落杖/成林的两个 Timeline 和可信 Token/接触提交链保留。既有 Cue/HUD 的标题期刷新语义不变，开始菜单后方仍可见第一幕短动作句，不把本步称为完整 UI 排版收尾。

原生修改只有 3 个已批准文件：DYDevEntryPlayerController.h/.cpp、DYEntryLoopAutomationTests.cpp。解析器精确允许 EntryLoop 与 Readability 两个完整包名，规范化 PIE 前缀；拒绝短名、后缀/目录近似、其他工程地图、Editor/Preview/Inactive 以及 Shipping。实际重演使用当前已允许包名，不固定回旧图。

## 资产与合规记录

保存前已冻结 7 个包，均位于 Readability：

| 包 | 内容 |
|---|---|
| Maps/LV_ReadabilityLab | 独立 Dev 地图副本，替换一个 Stage，新增 3 个被动提示表面 |
| Core/BP_DYReadabilityGameMode | 复用现有原生菜单控制器和已登记 HUD |
| Stage/BP_DYReadabilityPresentation | 保留原演出，增加事件式提示与短动作句 |
| Guides/M_DYReadabilityGuide | 代码构建的局部弧、开放角标和地线短标，无贴图/复杂透明叠层 |
| Guides/MI_DYReadability_P01 | 第一幕实际头部投影参考 |
| Guides/MI_DYReadability_P02 | 第二幕实际头部/身体区域参考 |
| Guides/MI_DYReadability_P03 | 第三幕区域参考与 A 端目标地线短标 |

几何复用 `/Engine/BasicShapes/Cube`，属于 UE 自带资源、按引擎许可使用，不能称为 CC0 或开源资产。Cue/HUD/Source Han Sans 中文字体沿用原登记资源，不新增字体或外部资产。本轮没有付费采购、素材下载或图像生成服务。资产授权总表未在本轮重读/覆盖。

AI 使用记录：Codex 辅助地图白名单/重演代码、自动测试、Blueprint 图编辑脚本、解析材质表达式、运行观察与本文；没有 AI 生成的夸父造型、文化复原声明或代写真人盲测结论。赛事最终披露仍需由作者汇总真实使用记录。

## 验证与证据边界

审计根：`D:\灯影山海\Saved\Audit-2026-10-09-Readability`。

1. Native-Run1：Editor 编译成功，113 succeeded / 0 failed / 0 notRun，真实进程退出 0。旧 111 项保留，新 2 项核查精确身份、PIE、否定路径、世界类型与私有边界；纯函数测试不冒充真实 OpenLevel 验收。
2. ProjectionSamples-Run1：在实际逐幕配置下采样起点、目标与容差邻域；旧 EntryLoop 完整复演两轮、真实成林两次、实际按钮委托及一次 OpenLevel 重演，37 检查通过，退出 0。采样同帧恢复，不制造成功。
3. AssetColdVerify-Run4：保存后冷读通过，7 包与显式引用已核验；其余 Actor 变换/类别、原定义、15 Hz、Z70 与演出 Timeline 保留。原 Content 哈希不变；无保存原件。
4. VisiblePlay-Run2：修正提前显示门控后，50 检查通过、两轮完整复演、两次真实 15 分枝成林、一次新图重演、23 张截图。窗口真实退出 0。截图复核发现提示偏暗及“高光亮点”措辞不准确，后续仅修提示材质/文字/局部摆位；本次记录保留，不把旧截图当最终美术签收。

5. 最终 AssetColdVerify-Run6：冷读通过，三处 NoCollision、关闭投影/间接照明/距离场参与均已持久化；一个原生 Unlit 根、一个 GIReplace 节点与三个实例的实际颜色读回已核验。局部头部参考来自真实投影而非高光亮点。
6. 最终 VisiblePlay-Run4：50 检查通过、两轮完整复演、两次真实成林、一次同图重演、23 张原始截图，真实退出 0。开始前/段间/Resolve/结束态隐藏，当前幕与 Holding 可见，P02 复位后恢复；原持杖接触与 15 分枝树影链仍由生产流程驱动。既有编辑器启动日志的 13 条框架 Condition failed 与旧 EntryLoop 基线相同，当前和旧基线均未出现 Blueprint Runtime Error / Accessed None / Fatal error / Unhandled Exception；不宣称原始日志零警告。
7. 提示亮度专项 GuideContrast-Run2：实际 Holding 截图已生成，属于视觉专项而非完整流程。Run1 存在同帧重复 Shot 导致元数据中一个文件缺失，保留记录后修正观察器，并要求所有请求的原始截图实际存在。最终 Run4 又完整覆盖隔离后的同一提示材质。

独立打包和原生首帧证据在下节记录。所有失败 Run 保留，测试没有强杀窗口、自动注入键鼠或把 .uasset 节点按猜测写入。实际 UButton 委托不等于人手点击，控制参数脚本也不等于物理键盘验收。

## 已查明并修正的问题

- UE 图编辑没有先前生成器尝试的 sequence 便捷方法，改用已有分支的明确连接；这是生成脚本问题，不新增产品机制。
- 当前安装版 MaterialEditingLibrary 的标量写入返回 false，但实际写入发生；以实际参数读回值验收，不忽略实际失败。
- 运行式碰撞开关在重载后恢复，改为持久化 NoCollision 配置，重新冷读确认。
- 开始界面曾观察到提示提前可见，新增既有 Playing 快照门控后完整两轮验证通过；不从该现象臆测所有原生激活时序。
- 当前幕布高光亮点不等于灯锥几何轴心；最终候选按真实头部投影摆缺口、文字指向影子。没有更改主灯、曝光或原目标。
- 只加发光亮度会影响间接照明，最终使用原生 GIReplace 的零间接输入，并关闭新提示表面的动态间接/距离场参与；截图复核恢复影子和环境的对比，原灯与曝光未改。反射中的提示线条可见，不宣称渲染像素完全不受新增表面影响。

## 独立打包与启动器交付

本次打包在 2026-10-10 完成，Build ID 保留本轮启动日期 `ReadabilityDev-20261009-Run1`。唯一根地图显式指定为 ReadabilityLab；原 Config 没有改动，因此 Cook 另含原默认 InteractionLab 和 Engine/Entry。没有采用 CookAll 掩盖引用问题。

- Package-Run1：原生 UAT Build/Cook/Stage/Pak/IoStore/Archive 成功，真实退出 0；核验 15 项明确地图/表现/提示/HUD/定义/森林/字体依赖，49 个文件、1,042,446,090 字节。SourceAssets 记录 20 个源包，Cook 前后哈希一致。
- 归档：`D:\灯影山海\Builds\ReadabilityDev-20261009-Run1\Windows`。包含原生游戏、运行依赖、Pak/UTOC/UCAS、UFS/NonUFS 清单与对应调试符号；这是本地 Development 候选，不是可公开发布的 Shipping 成品。
- 原生 EXE SHA256：`8E0B1D4F20CA3D17AEDBD1FE2D69144FED833E9304D1BA5FB81AE0E8894B729F`，由 READABILITY-DEV-BUILD.json 绑定。
- FirstFrame-Run1：不执行 Python，显式加载新地图，原生 `-seconds=20` 正常请求退出，退出 0；实际首帧 1280×800。图像复核显示中文开始面板、单人制作说明、两个同字号按钮，幕上线索尚未出现。没有据此代签完整打包版通关。
- 新启动器固定选择这一身份匹配的包，不猜测“最新目录”；缺包时才明确使用本地 EditorGame，始终显式指定同一地图。已有 UE/游戏窗口时不强杀，正常关闭后再打开。
- 发布后进行 Windows PowerShell 5.1 解析、Auto/Package/EditorGame 只读 DryRun 与 CMD 链检查；其结果和最终保护校验分别存入 LAUNCHER-CHECKS.json 与 FINAL.json。

该包的完整物理键鼠流程、不同窗口比例、干净目标电脑与三轮无阻塞验证尚待后续实测，不能把编辑器两轮回归或打包首帧写成已完成这些项目。

## 仍需真人与后续专题的证据

作者下一次打开本入口时重点观察：浅色线索与真实黑影是否可分辨；第一幕能否找到头部影子应进入的缺口；第二、三幕能否结合“影形渐合/保持此刻”完成灯偶组合；成功后提示是否撤下；成林与重演是否正常。物理按键、鼠标点击和真实首次游玩不由脚本替代验收。

局部影形未必唯一反解两变量。这一步没有盲测数据，所以未断言提示已解决所有理解问题。正式高质量皮影/剧场、声音节奏、Skip/中断、性能、5–8 分钟和 Shipping 三轮仍单独保留。Windows 包首帧/编辑器两轮证据也不能替代干净目标电脑的整流程验证。

## 回退与保留

旧入口、旧地图和旧不可变包不变；原生 3 文件有 BEFORE 前镜像。新资产各次修正前副本及生成/验证日志在审计中保留，回退前必须检查后续编辑，不执行 reset/clean 或自动覆盖用户改动。无 Git 提交、清理或文件删除。
