# 第三幕可见自动测试

日期：2026-10-09。负责人：Codex，依据用户“你来写脚本测试吧，让我看到过程”实现并实际运行。功能边界：现有第三幕 Dev 候选的观察与诊断。

## 打开方式

在文件资源管理器中双击 **`D:\灯影山海\Start-M3AutoTest.cmd`**。聊天链接可能只预览代码，需要在资源管理器执行 CMD。先正常关闭其他 UE 编辑器窗口；入口会保留已有窗口并拒绝重复启动。

此入口使用本机 UE 5.8.3 Editor 加载已经保存的 `LV_M3RuntimeCandidate`，在 PIE 画面内显示中文步骤、实际灯偶值、保持计时和真实演出阶段。它与普通独立包入口 `D:\灯影山海\Start-M3Runtime.cmd` 分开。普通入口继续供实际键鼠操作；自动入口由脚本缓慢输入测试参数。

进入实际游戏与 HUD 后有 8 秒倒计时。观看期间无需按游戏键。F11 可放大或恢复视口。全过程约一分钟，结束后保留第二次成林画面，不自动关闭。

重看时按 Esc 停止 PIE，正常关闭本次测试编辑器，然后再次双击 CMD。每次使用新的 `RunN` 证据目录。右下角“正在执行 Python 脚本”是为保留当前窗口的启动运行状态；以游戏内“自动测试通过”及 `Result.json` 判断本轮已完成。

## 自动过程

| 步骤 | 玩家可见内容 | 实际检查 |
|---|---|---|
| 初始与倒计时 | 灯和偶保持原初始构图 | `.15/.15`、未 Resolve、无林会话、15 Hz |
| 调灯 | 灯在 4 秒内缓慢到 `.72` | 使用已有参数 setter，原生 Actor 更新位置与影子 |
| 灯单条件 | 灯到位后观察 3 秒，偶仍 `.15` | 不能提前成功；保持计时为 0 |
| 调偶 | 偶在 5 秒内缓慢到 `.85` | 姿态沿已有轨道联动，未新增姿态按键 |
| 保持与落杖 | 实际保持达到 1.25 秒后，杖从当前姿态下落 | 原生 Director Resolve；现有 BP Timeline 执行；接触前无林 |
| 接触与成林 | A 端接触后出现枝形并逐步展开 | 当前真实接触快照、15 个实际分枝、原生有效最终几何 |
| 停留与复位 | 第一遍成林停留 4 秒后，枝形消失，灯偶返回基线 | Director 公开复位：旧 token 失效、枝条清除、杖相对平移恢复 |
| 第二遍 | 再调灯偶，重新保持、落杖、接触和成林 | 新 token，第二次 Completed；画面最终保留 |

Resolve 一旦成立，脚本立即停止调参。Staff 位移、接触授权、枝条生长、Timeline 和 Blueprint 状态均由现有实现负责；脚本只读取它们。不换 Definition、不保存资产或地图、不变更 POV 所有者。

## 当前实际结果

最终代码运行 **Run2：PASS，10 条检查点记录，完成 2 次成林及 1 次完成态复位**。10 条包含两遍相同阶段的重复检查，不称作 10 个不同 C++ Automation 测试。

北京时间 11:15:32 实际 Ready，第一遍保持约 `1.333334 s`，第二遍约 `1.266839 s`。第一遍、第二遍均记录 Dropping 时无接触、无林；随后实际接触成立、15 个分枝进入 Growing，最终 Completed。完成态复位清除了分枝和旧身份，第二遍使用新身份。

`Start-M3AutoTest.cmd` 的本次调用返回 0；`Launch.json` 状态 PASS，Editor PID 15488 在结果生成时继续运行，因此没有声称该 Editor 已退出或获取其退出码。最终图像实际保留，中文步骤文字已直接截图查看。

证据根：`D:\灯影山海\Saved\Audit-2026-10-09-M3VisibleAutoTest\Run2\`

- `Result.json`：检查点和实际结果。
- `Events.jsonl`：实际数值、保持、落杖、接触、Completed 与复位事件。
- `Launch.json`：精确启动参数与 Editor 身份。
- `Session.log`：完整本轮 UE 日志；`Stdout.log` / `Stderr.log` 保留。
- `01-Initial.png`、`02-FirstForest.png`、`03-Reset.png`、`04-FinalForest.png`：原始实际 UE 视口截图，包含 HUD，未合成或编辑。
- 审计根 `SCOPE-CHECK.json`：旧保护范围与本次新增文件身份。

Run1 在调参前因两个 C++ getter 未导出给 Python 而失败。失败日志、Result、启动记录和初版脚本均保留。最终版读取已反射的 `light_control` / `puppet_control` 组件引用，采用既有 verifier 的实测路径；没有为测试修改 C++ 接口。

Run2 启动日志保留既有的 13 条 `LogAutomationTest: Error: Condition failed` 初始化记录；自动脚本自身 `error=null`。不将脚本通过描述为整份 UE 日志没有错误。

## 证据边界

该测试证明当前 Editor Dev 地图中，缓慢调参、真实保持、现有运行时 Blueprint 演出、完成态复位和重演能连续工作；这次实际 RHI 画面中的中文文字和枝影已查看。

脚本通过公开 setter 输入数值，并通过 Director 接口复位。`physical_keys_verified=false`：此次没有代按实体 E/A/D/R，没有验证真实键盘聚焦/操纵链路。`package_tested=false`：本次没有重新打包或运行独立包自动测试，不能替代先前独立包原生测试或待完成的人工体验验收。正式美术、正式节奏、三幕完整流程与 Shipping 三轮通关也不由本结果签收。

## 文件与回退

新增：

- `D:\灯影山海\Start-M3AutoTest.cmd`
- `D:\灯影山海\Scripts\Start-M3AutoTest.ps1`
- `D:\灯影山海\Scripts\Watch-P03RuntimeTest.py`
- 本说明 `D:\灯影山海\Docs\M3_VISIBLE_AUTOTEST.md`

停止本次 PIE、关闭本次编辑器即可结束测试，再使用原 `Start-M3Runtime.cmd` 进入普通独立包版本。既有源码、地图、Config、原启动器、DLL 与包均保留；不删除文件或进行 Git 写操作。

## 用户确认及后续边界（2026-10-09）

用户对上述可见自动测试回复：“没有问题，进入下一步”。登记为对本次观察步骤的认可及继续开发授权。Run2 原始日志、两次成林和一次完成态复位证据保持原样；不改写过去的 Result 或 Scope 记录。

该确认不扩大为实体 E/A/D/R 已逐项验证，也不把 Dev 参数、演出秒数、正式美术、三幕完整流程或 Shipping 验收视为定稿。下一步是最小三幕连续 Dev 方案及接入，方案见 `D:\灯影山海\Docs\THREE_ACT_DEV_PLAN.md`。涉及幕间推进、入幕复位和 Dev 结束方式的具体体验选择，按项目限制条件另行确认后实施。
