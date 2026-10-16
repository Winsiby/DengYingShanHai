# 三幕连续 Dev 接入验证

日期：2026-10-09。唯一实现与验收负责人：Codex。用户已接受 2 秒 Dev 题签过渡、入幕已有 `.15/.15` 基线、实际林影全长才结束、完成后保留画面，以及原有情境 R 当前幕复位。正式美术与视频仍由队友负责。

## 当前状态

**阶段 A：原生底层已接入，最新编译与 104 项原生回归通过。阶段 B：6 个独立 Dev 资产、逐幕中文提示、新地图和可见脚本测试已经完成；最新 24 项可见检查通过，测试窗口实际退出码 0。独立 Windows Development 包构建成功，打包版本实际第一幕画面、中文提示和正常退出通过；打包版三幕真人 E/A/D/R 全流程未代勾。**

方案：`D:\灯影山海\Docs\THREE_ACT_DEV_PLAN.md`。审计：`D:\灯影山海\Saved\Audit-2026-10-09-ThreeActIntegration\`。

## 阶段 A 改动与合同

- `DYPuzzleDirector.h/.cpp`：空序列保持旧单幕模式；三份显式引用按序激活；只在注册 Presentation 的当前身份回调后推进；当前幕复位不回退前幕；最终 Complete 不清成功身份或林资源。
- 新 `DYActSequenceTypes.h`：作者序列引用与纯显示快照；显示快照无目标、容差、数值进度或操纵引用。
- `DYStagePresentation.h/.cpp`：独立 2 秒原生表现定时器；按幕保留现有环境成果；P01/P02 不捕获落杖；Blueprint 最终回调由原生验证实际当前接触、完整枝形、可见/投影/Transform/Mesh/Owner，再允许完成。
- `DYInteractionHUD.h/.cpp` 与 `DYInteractionHUDWidget.h/.cpp`：沿既有注册链被动更新实例题签；晚绑定读当前快照；等待成林与全部完成文案分开；不改 Widget CDO 默认值，不新增输入或镜头。
- 新 `DYActSequenceAutomationTests.cpp`：16 项 native 合同测试，覆盖真实 Evaluator、控制 Actor 请求、回调重入、资源几何和 EndPlay。

额外边界：序列初次复位等待灯偶自身 BeginPlay，避免轨道中心二次偏移；手动先启动会取消旧延迟回调。成功通知栈内不能同步切幕。原通知使用现有 ActivationToken 的栈上下文，不建立第二权威身份；旧通知在重入后被拒绝，HUD 读取已绑定表现层当前值。晚同步不制造历史杖姿。

## 编译与原生回归证据

最终源码身份：`SOURCE-Run3.json`。最终构建：`Build-Run3.log`、`Build-Run3-result.json`，实际返回码 **0**，`Result: Succeeded`。

最终回归：`Automation-Run2/index.json`，**104 succeeded / 0 failed / 0 not run**。其中新增三幕测试 16 项、既有回归 88 项。`Automation-Run2/EXIT.json` 保留真实测试进程退出码 **0**。判定依据是报告中的失败数，不单凭进程返回码。

新增覆盖包括三幕顺序及旧单幕默认、错/旧/重复身份、原 Resolve 通知栈保护、当前幕真实 Reset 请求、失效重入及销毁、前两幕禁止落杖、旧阶段与反馈不覆盖新 HUD、全长且未被篡改的林才完成、完成资源与 Token 保留、Director 先 BeginPlay、初始化去重、原生 2 秒 timer，以及中文状态合同。

首轮失败保留：`Automation-Run1/index.json` 为 **101 succeeded / 2 failed**。一项暴露本轮加入的晚绑定历史 Capture 违反旧契约，最终恢复为只能由原 Resolve 事件捕获；另一项是测试使用的大 DeltaSeconds 被 UE 世界限制，改为真实跨框架帧的小步计时。未降低产品时长、修改旧断言或覆盖失败报告。

构建仍保留本机 MSVC 14.51 新于引擎首选 14.50 的既有警告及引擎头文件弃用警告；不因此更换工具链或修改引擎。

## 保存资产冷读

`ColdNativeProbe-Run1/Result.json`：新进程真实加载三份保存 Definition，P01 为灯 `.68`、不启用偶/姿态；P02 `.72/.80`；P03 `.72/.85`；组合姿态 `P02_StrideReach`；实际保持均 1.25 秒。目标和容差与原作者值相符。`saved=false`、`played=false`，未保存资产或地图。

结构 `DYActSequenceEntry` 的 definition/title 反射可用；Director 私有推进/完成未导出，Presentation 的最终证明回调可导出。

## 验收边界与后续

这 104 项是无画面的原生合同/回归测试。新三幕 fixture 的保持时间为 0、枝形为两枝、地线为测试位置，仅验证底层边界；保存地图的 1.25 秒保持、15 枝真实投影和中文画面另由下述可见测试验证，实体 E/A/D/R 仍待真人验证。自动参数操纵不等于按键验收。

本轮只在新 `/Game/DengYingShanHai/Dev/ThreeAct/` 副本接入三份定义及逐幕提示、提交真实完成，原 M1/M2/M3 地图、素材、Config、旧启动器与原包保持不变。整段正式 5–8 分钟、完整五态环境、美术/声音、全局重启/Skip、Shipping 和三轮目标电脑通关仍未签收。

源码改动前镜像在本轮 `Before/`，保护身份在 `BEFORE.json`。不执行 Git commit/reset/clean，不删除用户文件。

## 阶段 B：保存资产与可见连续测试

新资产仅在 `Content/DengYingShanHai/Dev/ThreeAct/`：

1. `Maps/LV_ThreeActDev.umap`。
2. `Stage/BP_DYThreeActPresentation.uasset`。
3. `Core/BP_DYThreeActGameMode.uasset`。
4. `UI/BP_DYThreeActHUD.uasset`。
5. `UI/WBP_DYThreeActHUD.uasset`。
6. `UI/WBP_DYThreeActCue.uasset`。

`AssetCreate-Run3` 保存 6 个资产，`MapConfigure-Run3` 只保存新地图。`AssetSourceProbe-Run6` 与 `AssetColdVerify-Run2` 在新 UE 进程核查保存后的节点、引用、绑定、数值及原有 11 项来源身份。通过官方节点文本导出核查实际成员引用，不推测二进制节点。新 Stage 仅最终 P03 执行原落杖/生长 Timeline，最后一条完成通知由原生真实林形校验；前两幕不生林。

地图复用原 M3 摄影、灯偶幕地布局及已登记中文字体；A 端的幕上地线仍为世界 Z70（地线位置 `[925, 0, 70]`），15 Hz 不变。只删除新副本中已确认的 `M3_StaffProjectionProbe_AB` 诊断实例，原地图及诊断资产未删除。

`CaptionRefine-Run1` 备份新 Stage 后，将顶部终态字幕改为中性的“林影已成”；“复演已成”只由 Director 验证后的底部原生 HUD 显示，避免表现层提前宣告流程完成。没有重新调目标、镜头、灯光或材质。

`VisiblePlay-Run3/Result.json`：**24 项通过、2 次真实成林、9 张实际截图**；`EXIT.json` 记录实际 UE 进程返回 **0**。测试只驱动公开灯偶参数和当前谜题 Reset，不直接推进 Director、不强置接触、不调用林或杖的动画驱动、不保存资产、不注入实体按键。

验证了三幕题签与入幕 `.15/.15`、入幕不会自动成功、组合幕灯单变量不能完成、P01/P02 无林、1.25 秒真实保持、约 2 秒实际题签过渡、P02 当前幕复位、P03 完成后复位并再次真实成林、15 枝完整可投影资源、原生最终 HUD、终态至少保留 4 秒。两次转幕实测约 2.006 / 2.007 秒；精确 2 秒合同另由原生 timer 测试验证。

失败过程全部保留。`VisiblePlay-Run2` 虽 24 项通过，但进程实际返回 `-1073741819`，不能记为正常退出；测试收尾修正为先等 PIE 世界销毁，再让 UE 自己的 Python 执行器安排退出，取消重复 Quit 请求后重测为 Run3。修正只在测试驱动中，不改产品玩法。首轮节点探测/创建失败均保存独立编号；未覆盖失败记录。

## 新入口与打包记录

入口：`D:\灯影山海\Start-ThreeActDev.cmd`；实现：`D:\灯影山海\Scripts\Start-ThreeActDev.ps1`。请从资源管理器双击 `.cmd`；聊天文件预览显示文本不等于运行。Auto 只选明确身份通过的独立三幕包，否则明确提示本机 UE 的 `-game` 回退，不会打开旧 M3 包或随便找最新目录。启动记录不自动等于首帧或玩法验收。

`Package-Run1`：编译与 Cook 成功，Stage 因 Cook 隔离路径未以 `Windows` 结尾而找不到项目存储记录，实际 UAT 退出 1。失败目录与日志保留，没有移动拼凑产物。

`Package-Run2`：Cook 路径已修正，但 UAT 的 Zen IPv6 健康检查失败，实际退出 1。原生 UnrealPak 当时报告服务正常，UAT 仍反复等待；继续以独立诊断对照代理路由，不因编译/Cook 成功宣称打包完成。

`ZenRouteProbe-Run1/Result.json`：同一健康地址直连 **200**、继承代理 **502**，默认 .NET 代理未绕过 IPv6 回环；只补齐诊断子进程的回环例外后，绕过检查为 true。未输出凭据或修改全局环境。基于实际对照结果，仅对下一轮 UAT 子进程追加 `localhost / 127.0.0.1 / ::1 / [::1]` 例外，保留全部既有代理设置，不更改引擎或系统权限。

`Package-Run3/EXIT.json`：实际 UAT 退出 **0**，编译、Cook、Stage、Pak/IoStore、Archive 全部成功。独立输出 `D:\灯影山海\Builds\ThreeActDev-20261009-Run3\Windows`；49 项原生归档文件共 1,041,603,216 字节（另加构建身份 JSON），11 个关键资产/字体/定义均在实际 UFS 清单。身份记录只在完整归档检查通过后生成，固定该三幕地图、Development/Win64 与运行文件 SHA256。首两轮失败目录及日志原样保留。

`PackageSmoke-Run1/Result.json`：直接运行该独立包，以 UE 原生 `Shot SHOWUI` 保存实际入口图，`SECONDS=20` 触发引擎非强制正常退出，真实返回 **0**。日志证明加载 `LV_ThreeActDev`，未发现 Fatal、缺失包或 Blueprint Runtime Error。截图经 Codex 目视确认有“引日启幕”、中文 E/A/D 引导、幕布、灰盒灯偶及实时投影；这是新包入口画面和生命周期检查，不是包内三幕通关或实体按键验收。独立 `VISUAL-REVIEW.json` 记录人工目视结论；原始 Result 与构建身份中未经检查的字段不被追溯覆盖。

最终入口固定选择 **Run3** 包；PS 5.1 的 Auto / Package DryRun 核查与最终文件保护结果见本轮审计。请用入口 `.cmd`，不要直接双击包内 exe：项目旧默认启动配置刻意保留，入口显式传入新的三幕地图。

显式 Cook 根仍只有新 `LV_ThreeActDev`；UE 可能按未修改的默认启动配置额外 Cook `LV_InteractionLab` 与 Engine Entry。以最终实际清单登记，不将“一个游戏主场景”误写为“包内只含一个地图文件”。无 CookAll、无整个 Dev 树 AlwaysCook、未改旧默认地图或旧包；本轮只做 Development，不宣称 Shipping 通过。
