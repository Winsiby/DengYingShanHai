# 正式 Development 包三轮三幕与重演验收

日期：2026-10-19。负责人：项目负责人；Codex 辅助实现、打包和验证。

## 结果

Run6 在 Windows cooked Game 进程中通过三轮完整三幕流程与三次真实同图重演。新增测试只通过现有程序接口设置灯偶状态和请求开始/重演，等待原来的 15 Hz Holding、Blueprint 落杖和森林生长；不写目标/容差，不快进演出，不写木杖、森林或相机变换。

正式入口：`D:\灯影山海\Start-ReleaseEntry.cmd`。
当前固定包：`D:\灯影山海\Builds\FormalMain-Development-20261019-Run6\Windows`。
旧 Run5、旧入口脚本原字节和旧证据均保留。

## 改动范围

- 仅新增源码 `Source/DengYingShanHai/Private/Tests/DYFormalMainAutomationTests.cpp`。测试完全由 `WITH_DEV_AUTOMATION_TESTS` 包围，ClientContext，必须 cooked Game、非 Editor、非 NullRHI、精确 `L_DY_Main`。
- 沿用 GameMode 的 `GetPlayerStagePresentation()` 只读注册入口，继而获取已有 Director/Forest；没有增加运行时扫描、输入或流程权力。
- `Scripts/Start-FormalMain.ps1` 两个固定 Run5 引用改成 Run6。参数、校验与普通玩家启动行为不变；普通入口不含自动测试参数。
- 地图、资产、谜题参数、玩法逻辑、输入、相机和演出时序均保持本轮前版本。

## 本轮实际证据

| 验收 | 结果 |
|---|---|
| Game Development 编译 | 实际退出 0，新测试单独编译并链接进原生 EXE；保留 MSVC 14.51 非首选警告 |
| UAT | 精确 Cook 主图和 Engine Entry，Cook/Stage/Pak/IoStore/Archive 实际退出 0；49 产物、1,081,877,869 字节，身份 JSON 另计 |
| 包内自动化 | 精确用例 `DengYingShanHai.FormalMain.PackagedThreeActsAndReplay`，1 Success、0 Warnings、0 Failed、0 NotRun，游戏实际退出 0 |
| 三轮第一幕 | 标题开始、重复开始拒绝、皮影禁用、灯 0.68、真实 Holding 与自然 Resolve、正常进第二幕 |
| 三轮第二幕 | 灯单独/偶单独各等待 1.5 秒均不 Holding/Resolve；双目标 Holding 后重置到 0.15/0.15，仍在第二幕，再次自然成功 |
| 三轮第三幕 | 灯 0.72/偶 0.85 后真实 Holding/Resolve、当前 Token 的杖尖接触、实际中间生长、完整成林和结束菜单 |
| 真实林组件 | 每轮 15 枝与 5 个 M04 叶簇，注册/可见/投影/无碰撞；枝组件与原生最终几何变换一致 |
| 三次同图重演 | 真实 OpenLevel 创建新主图世界，回到干净标题，无林资源/接触/Resolved，上一轮 Token 被拒绝 |
| 图像 | 8 张 UE 原生 1280×800 PNG 全部解码、逐张查看；第二幕 Holding、结尾菜单和重演标题可读，三轮林影一致 |
| 包完整性 | 运行前后 49 产物 SHA256 全部匹配；测试 EXE 与新编译/包身份一致，主图 SHA256 与 Run5 相同 |
| 正式入口 | Windows PowerShell 5.1 CMD 启动前校验通过并实际启动 Run6；用户恢复授权后，同一 PID 40916 已通过一轮键鼠协同三幕、结束菜单、同图重演回标题和菜单正常退出，游戏及公开 CMD 均实际退出 0，详见下方补充验收 |

本项自动化内部已包含三轮，不把 1 条测试误写成只有一轮，也不重复运行九轮。

## 证据入口

- `Saved/Audit-2026-10-19-FormalPackagedFlow/QA.json`：独立核对用例身份、三轮事件顺序、PNG 解码和包哈希。
- `Saved/Audit-2026-10-19-FormalPackagedFlow/VISUAL-REVIEW.json`：八张图的实际视觉复核。
- `Saved/Audit-2026-10-19-FormalPackagedFlow/Packaged-Run1/Report/index.json`：引擎原始报告。
- `Saved/Audit-2026-10-19-FormalPackagedFlow/Packaged-Run1/Session.log`：逐轮 `DY_FORMAL_PACKAGED` 事件和原生退出。
- `Saved/Audit-2026-10-19-FormalPackagedFlow/Packaged-Run1/Captures/`：8 张原图。
- `Saved/Audit-2026-10-19-FormalKuafu/Package-Run6/`：UAT、产物清单和包身份。
- 正式入口运行：`Saved/ReleaseEntryPlay-Development/20261019-093735-468`；恢复授权后的完整键鼠证据另存 `Saved/Audit-2026-10-19-Run6Input-Run1`。

## 补充：常规入口键鼠协同验收

2026-10-19，继续操作上述同一普通入口进程，未重打包、未启用自动化测试或作弊命令、未通过程序接口写游戏状态。用户协助向前移动、对准并进入第二幕皮影操纵，以及恢复窗口前台；Codex 使用 Computer Use 的鼠标与短按键完成其余调整、第三幕灯具选择、重演和退出。因此本次记为一轮键鼠协同流程，不记为独立首次玩家盲测或无人协助三轮。

原生 Session.log 中 P01/P02/P03 的 `resolved exactly once` 各一次；第三幕成功于 UTC 02:09:27.362，实际杖尖接触于 02:09:29.361。画面依次记录灯偶均就位的 Holding、杖尖触地后林影生长以及“林影已成 / 复演已成”菜单。按 Return 选择重新复演后，02:09:50.556–02:09:50.620 真实重新加载 `L_DY_Main`，标题与初始场景恢复。随后点击标题菜单“退出游戏”，原生 `Exit.json` 的 `ActualExitCode=0`，公开 CMD 也退出 0；最终游戏窗口数为零。

八张 1922×1248 JPEG 均已解码并逐张查看。结尾可以看见五个枝端叶簇与其投影，白色灯具和边界占位、Cylinder 枝条及簇状叶冠仍可见；流程验收不改变美术评价。工具没有持续按键接口，数百次短按与窗口中断显著拉长本次操作，不能用这次耗时评价 5–8 分钟体验。未做声音听感或逐帧连续录像验收。

完整证据：`Saved/Audit-2026-10-19-Run6Input-Run1/README.md`、`PROGRESS.json`、`QA.json`、`CAPTURES.json`、`Session-Completed.log`、`Launch.json`、`Exit.json`。原进行中记录及两份文档修改前副本保留。启动时写入的 Launch.json 两个未验收字段保持原样，本补充记录提供后续证据，不改写启动元数据。最终原生 EXE 和主地图 SHA256 均与 Run6 身份一致。

## 边界与回退

这次三轮是程序接口自动验收，不等于实体键鼠三轮通关或首次玩家 5–8 分钟盲测。此前 Run5 用 Computer Use 点击开始并尝试聚焦/移动，未完成第一幕灯具聚焦，正常退出 0；原记录在 `COMPUTER-USE-ATTEMPT.json`。

尚未完成：独立真人键鼠三轮、Shipping、目标机性能、5–8 分钟盲测、声音听感和最终美术签收。上述一轮协同流程不能替代这些项目。枝条仍是 Cylinder 占位，灯具/边界占位与分离簇状叶簇仍可见，不能称最终美术或完整机构运动已验收。本轮没有为此改变美术。

P02 Holding 截图与自然计时并行；极低帧率/慢存储可能让截图等过剩余保持时间而误失败，正常产品不因此改容差。本轮三次均在保持阶段正确截图并重置。

回退启动入口：先核查后续修改，再恢复 `Saved/Audit-2026-10-19-FormalPackagedFlow/Baseline/Start-FormalMain.ps1`，即可重新指向保留的 Run5。新测试可单独移出源码后重建；无需回退地图或资产。本轮没有 Git 提交/推送，没有额外许可或美术源文件改动。
