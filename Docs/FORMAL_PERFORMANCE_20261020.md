# 灯影山海 · Development 1080p 性能复测（2026-10-20 / D2 包）

> 目的：V2.1 剧场外壳、外景、外景起步与结束态修完之后，确认本机 1080p 帧率没有倒退。方法与 2026-10-19 的正式采样（`Docs/FORMAL_PERFORMANCE_20261019.md`）一致：同一套打包版三幕自动化、同一组 CSV 采样参数、同一台机器。

## 1. 采集对象与参数

| 项 | 值 |
|---|---|
| 包 | `D:\灯影山海\Builds\FormalMain-Development-20261020-D2\Windows`（Development / Win64 / Game） |
| 包身份 | `Builds\FormalMain-Development-20261020-D2\Windows\DEVELOPMENT-BUILD.json`（UAT `ExitCode=0 (Success)`，`BuildCookRun time: 116.25 s`） |
| 可执行文件 | `DengYingShanHai.exe` |
| 分辨率 | 1920×1080（`-ForceRes`），D3D12 / SM6 |
| GPU | NVIDIA GeForce RTX 5070 Laptop GPU |
| CSV | `Saved/Audit-2026-10-20-V21/Perf-D2d/User/Saved/Profiling/CSV/Profile(20261020_110228).csv`（18,000 帧，37 MB） |
| 运行日志 | `Saved/Audit-2026-10-20-V21/Perf-D2d/Session.log` |
| 启动脚本 | `Saved/Audit-2026-10-20-V21/Perf-D2d/Capture-D2d-Perf.ps1`（`Launch.json` / `Exit.json` 同目录） |
| 分析脚本 | `Saved/Audit-2026-10-20-V21/Perf-D2d/summarize.py` |

命令要点（与 10-19 完全同构，只换包与输出目录）：

```text
DengYingShanHai.exe -windowed -ResX=1920 -ResY=1080 -ForceRes -nosplash -unattended -nowrite
  -ForceDPCVars=r.Shadow.Virtual.OnePassProjection=0
  -UserDir=D:\灯影山海\Saved\Audit-2026-10-20-V21\Perf-D2d\User
  -abslog=...\Perf-D2d\Session.log -ReportExportPath=...\Perf-D2d\Report
  -csvCaptureFrames=18000 -csvGpuStats -csvCompression=0 -ExitAfterCsvProfiling
  "-ExecCmds=Automation RunTests DengYingShanHai.FormalMain.PackagedThreeActsAndReplay"
```

自动化在采集中真实跑完：`cycle=3 PASS ThreeCompleteFlowsAndThreeSameMapReplays; programmatic interfaces only`，`Test Completed. Result={Success}`（见 Session.log）。进程退出码 777003 是 10-19 报告已记录的 UE 崩溃报告线程退出码，CSV 与日志均完整落盘，按上次口径不写成"正常退出"。

## 2. 结果

| 区间 | 帧数 | 秒 | 平均 FPS | 帧时间均值 ms | P95 ms | P99 ms | 最长单帧 ms | >16.67 ms | >33.3 ms | GPU 均值 ms | GPU P99 ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 全部 18,000 帧 | 18,000 | 128.172 | 140.44 | 7.121 | 7.801 | 8.109 | 2482.705 | 10 | 8 | 6.203 | 6.601 |
| 去掉前 300 帧（稳定态） | 17,700 | 123.468 | 143.36 | 6.976 | 7.797 | 8.103 | 79.414 | 7 | 6 | 6.202 | 6.592 |

- FPS 定义沿用上次：`1000 / mean(FrameTime)`；GPU 取 UE CSV 的 `GPUTime` 列。
- 全部帧里的 2482.7 ms 单帧是一次地图载入/切换（`-ExitAfterCsvProfiling` 结束前的一次重载），不是演出中的卡顿；稳定态最长单帧 79.4 ms，>16.67 ms 只有 7 帧（占 0.04%）。
- 与 2026-10-19 正式采样对比（同为该自动化、1080p、RTX 5070 Laptop）：上次三幕合计 130.46 FPS / GPU 6.938 ms / P99 9.349 ms；本次稳定态 143.36 FPS / GPU 6.202 ms / P99 8.103 ms。外景、天穹与结束态改动之后没有倒退，反而略优（本次样本为整段三循环 + 三次同图重演，含标题画面）。

## 3. 限制（不能据此宣称已验收的部分）

- 驱动来自 `FormalMain.PackagedThreeActsAndReplay` 的程序化接口，**不是真人按键/瞄准**，不含真人操作手感与视线停留。
- 采样是 Development 包，不是 Shipping 包；Shipping 外部采样权限问题（ETW / Performance Log Users）在 10-19 报告里仍未解决。
- 样本包含标题画面与三次同图重演的载入窗口，未像 10-19 报告那样按幕切窗；因此这里给的是"整段体验"口径，不是单幕口径。
- 本机配置（RTX 5070 Laptop）不代表赛事现场机器。

## 4. 结论

- V2.1 的全部改动（剧场外壳 226 个 actor、外景、外景起步、HUD 分层、结束态菜单一致性）在本机 1080p Development 包内维持 **>60 FPS 的明显余量**：稳定态平均 143 FPS、GPU 6.2 ms、P99 8.1 ms。
- 没有出现新的每帧开销来源（外景灯为无阴影点光、门径灯 4 盏、天穹为 Unlit 单材质）。
- 仍缺 Shipping 侧外部采样与真人通关性能，作为已知未覆盖项保留。

