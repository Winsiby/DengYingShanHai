# 临时查询脚本清理记录

日期：2026-10-18。负责人：项目负责人；Codex 执行清理。

范围：删除下列 5 个已产出 JSON 结果的独立查询探针。删除前已读取脚本、核对结果文件，并检索项目文本中的调用和文档引用，未发现依赖这些脚本的其他入口。保留全部 JSON 结果、日志、模型源文件和验证记录。

| 删除脚本 | 原用途 | 保留结果 |
|---|---|---|
| `KuafuModeling-20261018/list_objects.py` | 临时 Blender 对象和骨骼清单查询 | `KuafuModeling-20261018/KUAFU_OBJECT_LIST.json` |
| `KuafuModeling-20261018/list_component_methods.py` | 临时 UE 骨骼组件 API 枚举 | `KuafuModeling-20261018/SKELETAL_COMPONENT_METHODS.json` |
| `ReenactorChestBandRemoval-20261018/inspect_objects.py` | 胸带修正前的临时网格清单查询 | `ReenactorChestBandRemoval-20261018/OBJECTS.json` |
| `ReenactorPlayable-20261018/probe_carrier.py` | 旧角色载体默认值查询 | `ReenactorPlayable-20261018/CARRIER_DEFAULTS.json` |
| `ReenactorPlayable-20261018/probe_reenactor_runtime.py` | 固定 ASCII 候选工程的编译默认值查询 | `ReenactorPlayable-20261018/RUNTIME_PROBE.json` |

恢复备份：`C:\Users\lenovo\AppData\Local\Temp\CodexScriptCleanup-20261018-230422\removed-scripts.zip`。ZIP 内保留相对路径；解压到项目根目录即可恢复，逐项 SHA256 见同目录 `manifest.json`。备份位于本机临时目录，可能被系统清理。

验证：删除前逐项核验 ZIP 中的脚本 SHA256 与原文件一致；删除后确认 5 个脚本已不存在、5 个结果文件 SHA256 未变。保留仍被调用的材质探针、美术工具副本，以及文档明确用于版本对比的旧启动入口。

未启动 UE、未编译或打包；此次仅清理外部查询脚本。没有修改 C++、配置、地图或美术资产。后续如需重做这些临时查询，由项目负责人从备份恢复。

## 2026-10-19 冗余入口与误生成缓存清理

删除 5 个启动文件：C 工作区根目录中与 D 项目原件逐字节一致的 `Start-M2Lab.cmd`、`Start-M3Geometry.cmd`、`Start-M3Continuous.cmd` 三个重复副本，以及已被当前 Alignment 入口取代的 `Start-AlignmentDev-Run1.cmd`、`Scripts/Start-AlignmentDev-Run1.ps1`。旧 Alignment Run1 包本身未删除。

同时删除 C 工作区根目录下误生成的 `%SystemDrive%/ProgramData/Microsoft/Windows/Caches` 目录，共 4 个 Windows 缓存数据库、989,728 字节；项目文本中没有该路径引用。正式 Development/Shipping 入口、当前 P02 B 入口、D 项目中的 M2/M3 原件、所有游戏包、源码、资产和验证结果均保留。

可恢复备份：`C:\Users\lenovo\AppData\Local\Temp\CodexExtraCleanup-20261019-001438\removed-files.zip`；同目录 `manifest.json` 记录 9 个文件的原始路径、大小和 SHA256。备份已逐项哈希核验；临时目录可能被系统清理。

## 2026-10-19 当前启动文件整理

负责人：项目负责人；Codex 执行清理。按用户本轮“整理现有脚本启动文件，把不需要的全部清理掉”的要求，清理过往阶段入口并保留当前可用的 Shipping 入口。所有新清理证据和备份存入 D 盘项目目录。

### 保留的当前入口

| 文件 | 用途 |
|---|---|
| `D:\灯影山海\Start-ReleaseEntry-Shipping.cmd` | 根目录唯一日常游戏启动入口 |
| `D:\灯影山海\Scripts\Start-FormalShipping.ps1` | 入口所必需的启动前校验与进程退出记录 |

固定目标为 `Builds/FormalMain-Shipping-20261019-Run3/Windows`，Windows x64 Shipping、正式主地图 `/Game/DengYingShanHai/Maps/L_DY_Main`。清理前后 Windows PowerShell 5.1 `-DryRun` 均退出 0；当前包包含 31 个身份文件以外的产物、733,971,876 字节。启动器、主图、配置、`.uproject` 及非启动类 Scripts 文件的 SHA256 均保持一致。

`Start-ReleaseEntry.cmd` 与 `Scripts/Start-FormalMain.ps1` 指向 Development Run6，其启动前校验实际退出 1，原因是现有主地图 SHA256 与该包不一致。本轮将该失效入口归档，没有改写校验、修复地图、重建包或将旧包冒充最新版本。

### 已从原位置清理的文件

共 **54 个文件，215,059 字节**：

| 位置 | 数量 | 清理范围 |
|---|---:|---|
| D 项目根目录 | 25 | 除 Shipping 外的全部 `Start-*.cmd`：M2/M3、三幕、音频、可读性、环境、木地板、台翼、梁柱/UV 审查与候选、角色移动、模型查看及失效 Development 入口 |
| D 项目 `Scripts/` | 24 | 除 `Start-FormalShipping.ps1` 外的全部 `Start-*.ps1`，包含旧 `Start-ReleaseEntry.ps1` |
| 原 C 工作区 `ReenactorValidation-20261018/` | 1 | `Start-ReenactorMovement-Package.cmd` |
| 原 C 工作区 `ReenactorIntegration-20261018/` | 1 | `Start-ReenactorMovement-Package.cmd` |
| 原 C 工作区 `ReenactorPlayable-20261018/` | 1 | `Start-ReenactorMovementDev.cmd` |
| 原 C 工作区 `ModelIntake-20261018/` | 2 | `Start-UserModelsReview.cmd`、`Start-UserModelsReview.ps1` |

完整原始路径、大小、SHA256、归档条目与逐项理由见 `D:\灯影山海\Saved\LauncherCleanup-20261019\manifest.json`。不删除游戏包、源码、地图、美术、历史测试记录；环境检查、资产创建/配置/验证脚本、独立美术工具及 Computer Use 控制工具保留。

### 备份、恢复与历史依赖

备份为 `D:\灯影山海\Saved\LauncherCleanup-20261019\removed-launchers.zip`。ZIP 已逐项核对 54 个文件的长度与 SHA256，确认与原件一致后才删除原位置文件；该备份位于项目目录，不依赖临时文件夹。

ZIP 内的 `project/` 保存 D 项目的相对路径，`legacy-workspace/` 保存原 C 工作区的相对路径。恢复时先解压到临时查看目录，按 `manifest.json` 选择需要的条目，再把对应前缀下的文件恢复到原项目根目录；遇到已有同名文件先比较，不覆盖后续修改。旧启动器依赖原路径与旧包身份，不能直接在压缩包解压目录里运行，也不能保证恢复后适配当前工程。

以下固定日期的历史脚本仍保留原文；重放这些历史流程前，需要从本归档恢复对应入口：

- `ReenactorValidation-20261018/Verify-Final.ps1` 会执行旧移动包入口的 `--check`。
- `ReenactorPlayable-20261018/Publish-ReenactorMovement.ps1` 会复制旧角色移动启动文件。
- `ModelIntake-20261018/Publish-Models.ps1` 会复制旧模型查看启动文件。
- `ModelIntake-20261018/Finalize-Models.ps1` 的旧清单包含模型查看入口。
- `Scripts/Watch-P03RuntimeTest.py` 的历史错误提示提及 `Start-M3AutoTest.cmd`；它不是当前正式入口的执行调用。

当前 Shipping 启动器不调用上述旧启动文件，不读取旧启动器基线 manifest。历史报告中的入口路径视为当时状态，未为本次清理重写旧验证结论。

### 本轮验证与边界

清理脚本先验证目标在指定的 D 项目或 C 工作区路径内，并拒绝重解析点；没有递归删除目录。逐项备份校验通过后删除 54 个原文件，确认原位置全部不存在；根目录剩 1 个游戏启动 CMD，`Scripts/` 剩 1 个游戏启动 PS1。保留文件哈希核对通过，当前 Shipping 预检前后均通过。

原始证据：`Saved/LauncherCleanup-20261019/manifest.json`、`preflight-shipping-before.txt`、`preflight-shipping-after.txt`、`README.before.md` 与 `cleanup-launchers.ps1`。README 只补充当前入口和清理说明。

本轮未启动 UE 或游戏，未编译、Cook、打包或通关。预检通过只证明当前入口检查成立，不能替代 Run3 首帧、操作或完整流程验收；旧 Run2 的通关报告不移用为 Run3 证据。

## 后续磁盘清理说明（2026-10-19）

用户随后要求按当前 V2.2 修改方案筛选 C、D 盘及下载目录，只保留后续仍用的内容。过时的候选工程、旧运行包和构建副本已进一步清理；本文件上文所述“当时保留全部旧包”是当时状态，不能作为它们现在仍存在的承诺。

54 份启动文件 ZIP 仍保留为小型历史记录；恢复其中脚本不会自动恢复已退役的旧包。当前只保留 Shipping Run3、Shipping Run2 回退基线与 Development Run6，现用模型/动画源已整理到 D 盘。完整去留依据和实际校验见 `Docs/STORAGE_CLEANUP_20261019.md` 与 `Saved/StorageCleanup-20261019/final-summary.json`。
