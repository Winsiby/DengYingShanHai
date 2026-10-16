# 第三幕独立包入口：当前验收状态

更新：2026-10-09。当前步骤负责人：Codex，依据用户要求直接完成。美术与参赛视频仍按 AGENTS.md 由队友负责。

**当前 `D:\灯影山海\Start-M3Runtime.cmd` 已通过目标地图启动、可见游戏画面、完整输出捕获与正常关闭退出验收。第三幕题签实际为“第三幕影形”；原生生命周期诊断另获 1 项通过、0 项失败。实际键鼠整幕通关与复位重演仍待人工验收。** 这是第三幕 Dev 灰盒入口，不能称为完整三幕或正式竞赛成品。

## 打开位置

在文件资源管理器双击 `D:\灯影山海\Start-M3Runtime.cmd`。聊天链接可能只显示代码，需要在资源管理器打开并双击 CMD。

入口固定运行已有 `Builds\M3Runtime-20261007-Run1\Windows` 的 Windows x64 Game Development / Pak+IoStore 包，并指定 `LV_M3RuntimeCandidate`；不依赖 Editor/Python。沿用 E/A/D 等已有输入和已批准 Dev 候选。15 Hz、灯偶控制和 UE Movable 实时阴影路线不变。本轮没有修改或重新打包产品。

## 已通过：启动、日志捕获与正常关闭（2C）

前一轮修复了 PS 入口对 UE 正在写入日志的共享读取问题，以及采集器在系统 PowerShell 5.1 解析退出码的重载兼容问题。产品仅 `Scripts\Start-M3Runtime.ps1` 变更，旧备份保留；CMD 与原包不变。

Run4：北京时间 10:23:01 启动，10:23:04 观察正确 GameMode、世界和加载完成；10:23:25 留存实际可见画面。Codex 正常关闭游戏后，真实游戏退出码 0、CMD 退出码 0，两路输出真实 EOF，`captureComplete=true`。两组系统 PS5.1 定向测试各 6 项通过，0 失败。277 项受保护文件匹配。

历史原件：`D:\灯影山海\Saved\Audit-2026-10-09-M3LauncherLogFix\REPORT.md`、`VERDICT.json`、`RUN4-FIRST-VISIBLE-FRAME.jpg` 与 `Run4-Capture\`。Run2、Run3 的失败原件继续保留，不被本次通过覆盖。

## 更正：不是“第二幕题签”产品缺陷

上一轮 Codex 从截图中把“三”误读为“二”，错误登记了“第二幕影形”问题。2026-10-09 冷读资产与实际打包进程的公开反射均确认：

- 地图使用 `BP_DYP03RuntimeGameMode_C`，该类指向 M3 HUD，M3 HUD 指向 `WBP_DYP03RuntimeHUD_C`。
- Widget 默认属性、实际 Widget 实例的 `ActTitle` 均为“第三幕影形”。
- **实际显示 TextBlock `DYActTitle.Text` 也是“第三幕影形”**，不是仅作者脚本中写了正确字符串。

因此撤销这项误报，不改 Widget、类引用、字体、源码或包。前一轮冻结 `REPORT.md` / `VERDICT.json` 不回写，以本页和本次审计补记说明更正。

证据：`Saved\Audit-2026-10-09-M3UIPlay\UI-COLD-PROBE.json`；`UI-Packaged-Probe.log` 第 960–963 行与第 993 行。冷读 `saved=false`，没有编译或保存资产。

## 已通过：打包地图的原生生命周期诊断

北京时间 10:41:36–10:41:52，在现有包的目标地图中执行 `DengYingShanHai.P03.Runtime.LiveMapCausalLifecycle`，JSON 报告为 **1 succeeded / 0 failed**。

覆盖：启动未自动作答、15 Hz 保留；真实落杖 Timeline；接触前无林；接触后才有林会话；15 个最终可见且设置投影的几何组件；落杖、成林和完成后三种复位；旧身份拒绝；再次成林；重复同步不重启；Director EndPlay 释放资源。测试直接调用已有控制参数和 Director 复位接口，不经 E/A/D/R 键盘链路。

本次使用 `-NullRHI`，**不验证实际 GPU 阴影、玩家按键、相机可读性或操作手感**。HTML 模板缺失，未生成 HTML；JSON 导出成功。测试条目 errors=0 不代表整份日志没有错误。日志记录退出请求状态 0，但此次调用没有持有子进程句柄取得 OS 退出码，不据此声称已捕获实际进程码。

证据：`Saved\Audit-2026-10-09-M3UIPlay\LiveMap-Lifecycle.log` 与 `LiveMap-Lifecycle\index.json`。完整范围及限制见同目录 `RUNTIME-VALIDATION.md`。

## 待人工确认：已有键鼠链路

1. 对准灯或偶，出现绿色准星后按 E，使用 A/D 调整；两者同时到位并保持后触发演出。
2. 观察青色 A 端先落到已确认的幕上 Z70 地线，随后从同一投影接触点成林，不跳构图。
3. 保持最后一个对象仍处于操纵状态，不先按 E 放开；按 R 复位，再用已有输入完成一次成林。

**R 的现有上下文语义必须区分：**操纵状态的 R 请求当前谜题复位；E 放开后的探索状态 R 只将玩家送回起点，不是全局谜题重开。此次实际单次 R 日志只证明“玩家回到起点”，不能算谜题复位。若已经放开对象，可正常关闭游戏，再双击原 CMD 从初始状态重试，不新增按键或全局复位规则。

## 仍有限制

首个可见快照不是引擎 Frame0；人工键鼠整幕与复位重演未代勾；长期 GPU 稳定性、Shipping 三轮完整流程尚未通过本轮验证。失败 pause 分支未发生。TSR 驱动警告、英文几何标签与占位美术仍存在。

下一步先收齐上述人工结果；如出现明确失败，按原范围定位修复。正式参数、演出时长、R/Skip/输入锁、POV、完整三幕编排及最终结束态仍需按 AGENTS 要求确认，不借本次诊断自动定稿。
