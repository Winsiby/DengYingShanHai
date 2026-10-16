# 开始—三幕—结束—重演：最小 Dev 闭环

日期：2026-10-09。状态：独立 Dev 闭环已接入，原生回归、两轮可见流程、同地图重载和独立 Windows Development 包首帧已通过；真人按钮与键盘全流程仍待作者验收。唯一人类负责人为用户，Codex 按授权辅助实现、核查和文档。

## 1. 已批准的可见结果

1. 在同一 Dev 地图中显示开始面板。点击前第一幕保持未启动，不是已经运行的谜题上覆盖一层 UI。
2. 点击开始后只启动一次，移除面板，恢复原有游戏输入和鼠标视角；不改 E/A/D/R。
3. 三幕保持现有参数和流程。只有 Director 验证真实杖尖接触和完整林影后，才显示结束面板。
4. 点击重演重新加载当前这一张 Dev 地图，清除全部旧 Token、定时器、委托和林资源；回到开始面板。
5. 重演允许短暂加载。不是原地状态重建，不跳过落杖或成林，不新增暂停/Skip。

## 2. 已核实的接入点与依赖

- 当前 DYPuzzleDirector::BeginPlay 会直接调用 StartCurrentPuzzle；必须增加仅在新 Dev 地图启用的启动门控，默认保留旧行为。
- 现有 ADYStageGameMode 仅登记舞台 Presentation；HUD 通过明确注册链读取被动显示状态，不扫描世界、不判断谜题。
- 当前 ADYStagePlayerController 管理本 LocalPlayer 的 Explore/Manipulate 输入 Context；菜单输入焦点仍应由 PlayerController 唯一负责，不交给 HUD 或关卡蓝图。
- 当前 Stage 的最终完成回调已经原生校验真实林形；结束 UI 只消费已成立的 Complete，不能自己宣告成功。

推荐边界：独立 Dev PlayerController 负责菜单请求与焦点；独立被动 Widget 负责布局和按钮意图；Director 仍唯一保存三幕事实和启动/完成状态；Presentation 仍只驱动演出与显示。仅用明确引用、事件和生命周期清理，不增加 GameInstance 持久进度、全局消息框架或第二个流程 Director。

菜单只拥有本世界、单机本玩家的短期显示与请求状态。保存 Definition/CDO 不存运行进度，不做存档或联机。新 Widget 的字体继续使用已登记的免费 OFL 中文字体，不引入插件或付费资源。

## 3. 范围与回退

底层具体白名单：仅修改 `Public/Puzzles/DYPuzzleDirector.h` 与 `Private/Puzzles/DYPuzzleDirector.cpp`；新增 `Public/Core/DYDevEntryPlayerController.h`、`Private/Core/DYDevEntryPlayerController.cpp`、`Public/UI/DYDevEntryWidget.h`、`Private/UI/DYDevEntryWidget.cpp`、`Private/Tests/DYEntryLoopAutomationTests.cpp`。共 7 个源码/测试文件。独立 `/Dev/EntryLoop/` 只新增地图与 GameMode 副本；原三幕 Presentation、Definition、字体和林影资产复用，不重新调参或保存原件。新入口使用单独名称，不覆盖 Start-ThreeActDev。

实施前冻结具体源码、测试、Dev 资产和新入口白名单。新入口与测试地图独立于已通过的 ThreeAct Dev，不覆盖 M1/M2/M3、旧启动器、旧包、Config 或用户美术源文件。优先保持单幕与旧三幕自动启动的回归。

本轮原文及两份 Director 源码前镜像：D:\灯影山海\Saved\Audit-2026-10-09-SoloEntryLoop\Before。人员规则修正不与游戏源码修改混在一次未核查回写中；不 commit/reset/clean、不删除失败记录。

## 4. 实施与验收顺序

1. 单人责任规则先回写并检查旧保护文件。
2. 核查本机 UE 菜单、焦点和重载 API，明确精确文件白名单。
3. 最小 C++ 启动门控和菜单请求；验证延迟启动、重复点击、错误/旧引用、Complete 前拒绝重演、销毁与重入，旧自动模式不回归。
4. 独立 Dev Blueprint 参数及 UI 表现；冷读保存引用与默认值。
5. 可见开始/完成/重载过程测试，确认旧世界和林资源销毁、返回首幕待演、输入上下文及焦点恢复。
6. 独立 Windows Development 包；显式新 Cook 根、依赖清单、实际画面和正常退出；不把编译成功当成玩法通过。
7. 真人鼠标按钮和原 E/A/D/R 各自验收，不用脚本回调替代实体操作。

当前闭环包的真人全流程仍待确认；脚本不代勾实体按钮或键盘检查，不能提前改为竞赛完成。正式 5–8 分钟、成品美术/声音、Shipping、暂停/Skip 与目标机三轮通关仍单独验收。

## 5. 实施结果与启动入口

独立新入口：`D:\灯影山海\Start-EntryLoopDev.cmd`。资源管理器中双击运行，当前默认选择字号修复包 `Builds/EntryLoopDev-20261009-Run2/Windows` 中身份匹配的 Development 包，显式传入新地图。原 Run1 保留为初次闭环证据。不要直接双击包内 exe，避免落入旧 Config 默认地图。

地图：`/Game/DengYingShanHai/Dev/EntryLoop/Maps/LV_EntryLoopDev`。仅新增这张 Dev 副本及独立 GameMode；演出、参数与素材复用原三幕。Director 的自动启动默认仍为 true，只有新地图实例置为 false。

菜单由独立 PlayerController 管理本地焦点与请求；Widget 仅转发按钮意图，不持有 Director、谜题答案或成功状态。菜单显示时 UIOnly，开始后 GameOnly 并清理旧按键状态；原 Explore/Manipulate Context 与游戏键位不变。真实 Complete 前不提供重演，重复开始/重演请求拒绝。重演由原生 OpenLevel 重新载入精确的同一地图；不原地伪造清状态。

通过：原生 110/0（104 项原有＋6 项新增）；可见检查 37 项、两轮完整三幕、一次实际同地图重载、两次真实 15 枝成林、15 张截图、实际 UE 退出码 0；新包 UAT 退出码 0，11 项实际依赖纳入，首帧及正常退出通过；四项启动器 DryRun 退出码 0。可见脚本广播真实按钮的 OnClicked 并使用公开参数调整口，不等于真人鼠标/键盘操作。详细区分与检查表见 `DEV_ENTRY_LOOP_VALIDATION.md`。

原 `Start-ThreeActDev`、M3Runtime、旧包和原 ThreeAct 资产保留；未修改 Config、镜头、采样 15 Hz、谜题参数、Z70 地线或正式美术/声音。原文件备份、失败及成功测试均留在 `Saved/Audit-2026-10-09-SoloEntryLoop`。

字号增量修复：开始/重演与退出按钮统一使用既有中文字体的 24 号 Regular。原生回归更新为 111/0；修复包在 1280×800 和本机较大窗口的实际标题画面已复核，游戏正常退出。较大窗口请求 1920×1080，实际尺寸以原生截图及 VISUAL-REVIEW.json 为准，不假定系统接受了请求尺寸。记录见 `Saved/Audit-2026-10-09-MenuFontFix` 及验收文档末节；不增加真人全流程签收。
