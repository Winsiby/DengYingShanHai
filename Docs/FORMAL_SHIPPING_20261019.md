# 正式内容 Windows Shipping 技术候选

日期：2026-10-19。负责人：项目负责人；Codex 辅助实施、构建与验证。

## 结果

`FormalMain-Shipping-20261019-Run2` 已完成 Windows x64 Shipping Game 的 Build/Cook/Stage/Pak/IoStore/Archive，UAT 实际退出 0。包通过公开入口 `Start-ReleaseEntry-Shipping.cmd` 实际启动，显示完整标题菜单，点击“开始复演”进入 `L_DY_Main` 第一幕，灯、皮影、幕布与实时影子正常渲染，键盘输入有实际反应；正常关闭后原生退出码 0，CMD 也退出 0。

包路径：`D:\灯影山海\Builds\FormalMain-Shipping-20261019-Run2\Windows`。
入口：`D:\灯影山海\Start-ReleaseEntry-Shipping.cmd` → `Scripts\Start-FormalShipping.ps1`。

本项只关闭“Shipping 能构建并实际运行当前正式主图”这一项技术验收，不关闭三轮真人、首次玩家盲测、目标机性能、声音听感和最终美术。

## Run1 失败与修正

第一轮 UAT 在编译阶段失败，退出 6：

- `c1xx: fatal error C1076` 与 `C3859`，PCH 内存不足；
- `UbaSessionServer - Killed process ... Low on memory (35.0gb/35.9gb)`，本机 31.4 GB 物理内存，24 逻辑核并行编译同时构建 Editor Development 与 Game Shipping；
- 完整日志保留在 `Saved/Audit-2026-10-19-FormalShipping/Package-Run1/`。

修正只针对构建命令：`-ubtargs` 增加 `-MaxParallelActions=2`，限制并行编译动作数，不改源码、资产、Cook 内容或产品行为。Run1 原始打包脚本另存 `Baseline/Package-Shipping.Run1-original.ps1`。

## Run2 构建事实

| 项目 | 实际结果 |
|---|---|
| UAT `BuildCookRun` | 退出 0，`BUILD SUCCESSFUL`，119.33 s |
| 编译 | Editor Development 与 Game Shipping 均完成，仅保留 MSVC 14.51 非首选与引擎弃用警告 |
| Cook | 精确主图 `L_DY_Main`，`Success - 0 error(s), 0 warning(s)`；UFS 含 `L_DY_Main` 与 `Engine/Content/Maps/Entry` |
| Stage / Pak / IoStore / Archive | 全部 `COMPLETED` |
| 产物 | 31 个文件、723,792,472 字节 |
| 原生 EXE SHA256 | `C8CA8F56FB3CB34C9968D43736AE8448EBB4D6D964861AF9A4F75B0C2ECBE4C6` |
| 源主图 SHA256 | `DE8D3C4C905359D3C977D2C2498B326BFFE6AEF32CA67AFC2BEFF085A6965A56` |

证据：`Saved/Audit-2026-10-19-FormalShipping/Package-Run2/`（`COMMAND.json`、`UAT-stdout.log`、`UAT-EXIT.json`、`ARTIFACTS.json`、`NativeLogs/`）与包内 `RELEASE-ENTRY-BUILD.json`。

## 唯一产品配置改动

`Config/DefaultEngine.ini` 增加：

```ini
[SystemSettings]
r.Shadow.Virtual.OnePassProjection=0
```

原因是 `-ForceDPCVars` 在 `UE_BUILD_SHIPPING` 下不生效，Development 启动器验证过的值必须成为 Shipping 可读取的持久配置。包内 UFS 清单列出项目 `DengYingShanHai/Config/DefaultEngine.ini`，时间戳 `2026-10-19T04:11:35Z` 晚于该修改；实际运行画面中幕布、木框和皮影的实时投影可见。

本轮没有改动 C++、地图、资产、谜题参数、容差、输入或演出时序，也没有把开发自动化测试加入 Shipping。

## 入口与运行记录

`Scripts/Start-FormalShipping.ps1` 在启动前校验包身份、原生 EXE 与源主图 SHA256、产物数量/总字节和五个容器，然后以 `-windowed -ResX=1280 -ResY=800 -nosplash -nowrite` 启动，并写下 `Launch.json` 与 `Exit.json`。`Start-ReleaseEntry-Shipping.cmd` 现在只委托该脚本。

首次 CMD 尝试报“身份缺失”，原因是新脚本被 Windows PowerShell 5.1 按 ANSI 读取中文路径；补 UTF-8 BOM 后同一校验通过。这个编码要求已随文件保留。

| 验收 | 实际结果 |
|---|---|
| 公开 CMD 启动 | 12:34:20 启动成功，PID 30460 |
| 标题画面 | 完整显示《灯影山海》说明、“开始复演”“退出游戏”，画面与 Run6 Development 标题一致 |
| 进入主图 | 点击“开始复演”后进入 `L_DY_Main` 第一幕，HUD 显示“灯：待调整” |
| 输入响应 | 持续按 D 800 ms 后视角/灯位发生可见变化 |
| 实时阴影 | 幕布上的皮影投影、木框与台面投影正常 |
| 正常退出 | `Exit.json` 记录 `ActualExitCode: 0`，CMD 退出 0 |

运行证据：`Saved/ReleaseEntryPlay-Shipping/20261019-123420-809/Launch.json`、`Exit.json`；截图在 `Saved/Audit-2026-10-19-FormalShipping/Runtime-Run1/`。

截图为 DPI 感知修正后的窗口原图（1944×1259 含边框，客户区 1922×1248）：`official-menu-dpi.png`（标题）、`official-playing.png`（进入主图）、`official-lamp-adjusted.png`（按键后）。修正前的 `first-frame.png`、`menu.png`、`menu-1700.png` 等是 DPI 虚拟化导致右侧裁切的早期截图，保留但不得作为菜单裁切的证据。

## 尚未完成与已知限制

- Shipping 包不含自动化测试，也没有产出 `Session.log`（带 `-log -abslog` 的审计运行同样没有生成文件），因此 Shipping 侧只有截图、进程与退出码证据，没有逐事件日志。
- Shipping 只实际观察到第一幕进入与一次按键反应，未在 Shipping 中走完三幕、落杖成林与同图重演；这些仍以 Run6 Development 程序接口与一轮键鼠协同证据为准。
- 未做 Shipping 三轮真人、5–8 分钟盲测、目标机性能、声音听感与最终美术签收。
- 枝条仍为 Cylinder 占位，灯具、边界与叶簇等占位仍可见，本次不改美术。

## 回退

- 旧 Shipping 包 `Builds/ReleaseEntry-Shipping-20261014-Run1/Windows` 与旧 `Start-ReleaseEntry.ps1` 未删除；原 `Start-ReleaseEntry-Shipping.cmd` 与 `DefaultEngine.ini` 副本在 `Saved/Audit-2026-10-19-FormalShipping/Baseline/`。
- 如需回到旧 Shipping，恢复 Baseline 的 CMD 即可；新脚本与 Run2 包可独立留存。
- 本轮没有 Git 提交、推送或发布。
