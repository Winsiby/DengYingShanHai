# 正式 Shipping 三幕、成林、重演与性能采样

日期：2026-10-19。负责人：项目负责人；Codex 辅助操作、采样与留证。

## 结果

使用公开入口实际委托的 `D:\灯影山海\Scripts\Start-FormalShipping.ps1`
启动 `FormalMain-Shipping-20261019-Run2`，在一次真实键鼠输入流程中完成：

- 第一幕：主灯 0.68 区间、1.25 秒保持、自然 Resolve 并进入第二幕；
- 第二幕：主灯 0.72、皮影 0.80、`P02_StrideReach` 姿态，画面进入“灯偶已到位”保持并自然完成；
- 第三幕：皮影 0.85、主灯 0.72，画面进入“灯偶已到位”保持，随后出现杖落成林与“复演已成”结束菜单；
- 同图重演：点击“重新复演”后回到干净标题界面；
- 正常退出：官方启动器记录原生退出码 0，启动命令退出 0。

本项关闭“Shipping 只验证到第一幕”的技术缺口，不代替独立真人三轮、
首次玩家盲测、声音听感或最终美术签收。

## 运行身份与输入边界

- 包：`D:\灯影山海\Builds\FormalMain-Shipping-20261019-Run2\Windows`
- 实际启动脚本：`D:\灯影山海\Scripts\Start-FormalShipping.ps1`；
  `Start-ReleaseEntry-Shipping.cmd` 仅作为该脚本的公开委托入口。
- 运行目录：`D:\灯影山海\Saved\ReleaseEntryPlay-Shipping\20261019-141236-159`
- PID：15892；窗口化 1280×800；无地图覆盖；无自动化测试参数。
- 输入通过实际 UnrealWindow 的 Windows 键鼠事件完成，未使用游戏控制台、
  作弊命令或程序接口写入谜题状态。
- 原生 EXE SHA256：
  `C8CA8F56FB3CB34C9968D43736AE8448EBB4D6D964861AF9A4F75B0C2ECBE4C6`
- 源主图 SHA256：
  `DE8D3C4C905359D3C977D2C2498B326BFFE6AEF32CA67AFC2BEFF085A6965A56`

以上两项与 Shipping Run2 身份一致。本轮未改源码、地图、资产、谜题参数、
输入映射、相机或演出时序。

## 实际画面节点

| 节点 | 证据图 |
|---|---|
| 标题菜单 | `00_menu.png` |
| 第一幕开始 | `03_P01_started.png` |
| 第一幕操纵 | `05_P01_control.png` |
| 第一幕完成、第二幕进入 | `07_P02_entry.png` |
| 第二幕灯已就位 | `08_P02_lamp_ready.png` |
| 第二幕灯偶均到位并保持 | `13_P02_both_ready.png` |
| 第三幕开始 | `14_P02_complete.png` |
| 第三幕皮影已就位 | `15_P03_puppet_ready.png` |
| 第三幕灯偶均到位并保持 | `20_P03_both_ready.png` |
| 成林与结束菜单 | `22_forest_complete_menu.png` |
| 同图重演后的干净标题 | `23_same_map_replay_title.png` |

关键节点均已人工查看。第二幕和第三幕的“灯偶已到位”文字、保持进度条、
成林结束菜单和重演标题均可读。

## 时长与性能

点击“开始复演”的时间为 `14:13:39.987`，结束菜单截图时间为
`14:18:16.902`，间隔 276.9 秒，即 4 分 36.9 秒。进程启动到结束菜单为
340.7 秒。

这不是盲测时长结论：本轮使用了脚本化短时按键、鼠标转向和人工判断，
存在工具暂停，且不是首次玩家独立游玩。该结果说明当前内容可在 5 分钟以内
被熟悉路径的操作者完成，不能据此宣称已达到 5–8 分钟目标。

重演后进入第一幕，进行了 48.7 秒、12 个样本的运行采样：

| 指标 | 结果 |
|---|---|
| CPU 平均占用 | 15.2% |
| GPU Engine 利用率平均 | 62.6% |
| GPU Engine 利用率峰值 | 64.0% |
| 工作集峰值 | 1368 MB |
| 私有内存平均 | 约 3484 MB |
| FPS | 未测量 |

GPU 数值是该进程 Windows GPU Engine 计数器之和，不等于帧率；Shipping
没有生成可用的控制台统计。原始逐样本数据见 `Performance.csv`。

## 证据

完整证据目录：
`D:\灯影山海\Saved\Audit-2026-10-19-ShippingFullFlow\Run2`

- `QA.json`：运行身份、节点、时长、性能、退出码、截图尺寸与 SHA256；
- `Official-Launch.json`、`Official-Exit.json`：官方启动器原始记录；
- `Performance.csv`、`Performance-Summary.json`：性能采样；
- `00_menu.png` 至 `24_P01_after_performance_sample.png`：运行画面。

图片为 DPI 感知后的完整窗口原图，尺寸 1944×1259，包含窗口边框。
同目录上级的 `00_current.png` 至 `46_*` 是首次尝试和校准过程记录，
不与 `Run2` 的成品证据混用。

## 尚未完成

- 独立真人三轮无阻塞通关；
- 首次玩家 5–8 分钟盲测；
- Shipping FPS 与目标机 GPU 帧时间；
- 声音听感与静音/有声一致性验收；
- 最终美术签收；枝条、灯具和叶簇等占位仍可见。

## 回退

本轮没有改产品文件。若需重新验证，保持 Run2 包与入口不变，再次从
`Start-ReleaseEntry-Shipping.cmd` 启动即可。旧 Shipping 包、旧入口与
构建基线仍保留。
