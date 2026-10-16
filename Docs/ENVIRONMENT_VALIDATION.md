# ENVIRONMENT VALIDATION｜环境验收记录

## 1. 验收结论

验收日期：2026-10-01

《灯影山海》的 Windows UE 5.8 C++ 开发环境已达到继续第一阶段开发的状态。这里的“环境可用”不等于比赛发行包已经完成：Editor/Game Target、资产验证与 PIE 已通过；正式 Windows Cook/Package、目标机盲测和键鼠手感仍属于后续验收。

- `Check-Environment.ps1`：Required failures 0，warnings 1；
- 唯一环境警告：本机 MSVC 14.51.36260 新于 UE 5.8.3 首选 14.50.35717；
- UE 5.8.3 编辑器、UnrealBuildTool、RunUAT 与 Windows 构建脚本存在；
- `DengYingShanHaiEditor Win64 Development` 编译成功；
- `DengYingShanHai Win64 Development` 在 `-NoUBA` 下完成链接；
- 生成的 `DengYingShanHai.exe` 为非零文件，有有效 `MZ` 与 `PE\0\0` 签名，已修复“Windows 无法识别应用程序”的 0 字节问题；
- 项目模块成功被 Unreal Editor 加载；
- 引擎初始化成功；
- `LV_InteractionLab` 地图检查为 0 错误、0 警告；
- C++ Phase 1 Automation 为 4/4 通过，`Project.Maps.PIE` 为 1/1 通过；
- Python 资产验证出现 `DY_PHASE1_VERIFIED`；
- Git LFS 已启用并正确匹配 Unreal 二进制资产。
- Unreal Editor 已设置为使用 Windows 高性能 GPU 偏好；
- 用户级 `DY_UE_ROOT` 与 `DY_PROJECT_ROOT` 已持久化；
- 当前仓库已启用 Git 长路径支持。

## 2. 已验证版本

| 组件 | 实际版本/位置 |
|---|---|
| Unreal Engine | 5.8.3，CL 58210709，`C:\Program Files\Epic Games\UE_5.8` |
| Visual Studio | Community 2026 18.10.3，`D:\Visual studio` |
| MSVC | 编译器 14.51.36260，工具目录 14.51.36231；非 UE 5.8.3 首选版本 |
| Windows SDK | 10.0.26100.0，`D:\Windows Kits\10` |
| UE bundled .NET | 10.0 win-x64 |
| Git | 2.55.0.windows.3 |
| Git LFS | 3.7.1 |
| GPU | NVIDIA GeForce RTX 5070 Laptop GPU，8151 MiB，驱动 592.01 |

当前机器只发现 `D:\Visual studio\VC\Tools\MSVC\14.51.36231`。因为实际工程已通过 Editor 与 Game 编译，本阶段不为消除警告而自动改装 Visual Studio；若以后出现编译器相关异常，再安装并选择 UE 5.8.3 首选 14.50.35717，随后重跑全部验收。

## 3. 发现并修复的问题

### 中文项目路径导致 C++ 编译失败

直接通过以下物理路径编译：

```text
C:\Users\lenovo\Documents\ChatGPT\数媒游戏开发
```

MSVC/UBA 将中文目录错误转码，最终在共享 PCH 编译阶段产生 `C1083`，无法创建中间文件。工具链版本、SDK 和源码本身均正常。

修复方式是在不移动、不复制仓库的前提下建立纯英文目录联接：

```text
C:\UEProjects\DengYingShanHai
    -> C:\Users\lenovo\Documents\ChatGPT\数媒游戏开发
```

通过英文入口重新编译后成功。以后所有 UE 命令、Visual Studio 工程、编辑器启动和打包都必须使用英文入口。

## 4. Game Target 的 0 字节可执行文件问题

### 症状

一次 Game Target 链接失败后，`Binaries\Win64\DengYingShanHai.exe` 留下了 0 字节占位文件；随后 UBT 根据旧回执报告“Target is up to date”，但 Windows 启动时报“不是此 OS 平台的有效应用程序”。因此，仅看 UBT 的增量成功文字不足以证明可执行文件有效。

### 根因

链接日志记录了 Unreal Build Accelerator 会话目录清理/访问被拒绝以及 `LINK fatal error LNK1109`。失败产物和 Target receipt 同时残留，造成后续增量判定误报。

### 修复与规则

1. 对 `DengYingShanHai Win64 Development` 执行 `-Clean`；
2. 从第一次重建起加入 `-NoUBA`，而不是等失败后才切换；
3. 检查 EXE 文件长度与 `MZ`/`PE\0\0` 签名；
4. 当前机器的 Game Target 构建命令保留 `-NoUBA`，直到单独证明 UBA 链接稳定。

修复后 Game Target 完成 10 个动作，链接步骤显示 `[NoUba]`，结果为 `Succeeded`。

## 5. 已验证的运行链

当前实际工程而非临时模板已完成：

1. UHT/反射与项目模块编译；
2. `UnrealEditor-DengYingShanHai.dll` 链接；
3. `DengYingShanHai.exe` 链接与 PE 有效性验证；
4. `LV_InteractionLab` 加载与 Map Check；
5. `DYStageGameMode` 创建；
6. Enhanced Input Local Player Subsystem 初始化；
7. `IMC_DY_Explore` 以优先级 0 应用一次；
8. PIE 正常进入与退出；
9. Phase 1 的类默认值、镜头装配、精确键位修饰器、运行时 Pawn 复位自动化测试。

日志中 `aqProf.dll`、VTune DLL 等未找到属于未安装的可选分析工具，不是项目运行依赖。它们不能掩盖真正的项目 Error，但自身不构成当前验收失败。

## 6. 非目标平台与配置清理

Win64 SDK 有效。Android、Linux、iOS、TVOS、VisionOS 等平台 SDK 未安装，符合项目只面向 Windows 的范围。`DefaultEngine.ini` 中自动生成且本项目不用的 Android File Server 段及 SecurityToken 已删除；项目没有将移动端文件服务纳入开发或发行架构。

## 7. 后续硬性规则

- `.uproject` 必须通过 `C:\UEProjects\DengYingShanHai` 打开；
- 不在当前竞赛版本开发中升级 UE 5.8.3；
- 当前机器的 Editor/Game 完整构建优先使用 `-NoUBA`；
- 正式提交前仍需完成 Windows Development Cook/Stage/Package、无开发环境目标机冷启动和键鼠手感验收；
- 不能把“第一阶段技术骨架可用”表述为“比赛版本已可发布”。

直接启动未 Cook 的 Development Game 裸 EXE 会因缺少可用的 premade Asset Registry 在 `BufferReader.h:52` 断言并以 3 退出。这不是再次出现“无效 Windows 应用程序”，但也不能算独立运行通过；必须在后续 Cook/Stage/Package 里解决并复验。

## 8. 持久化配置

```text
DY_UE_ROOT=C:\Program Files\Epic Games\UE_5.8
DY_PROJECT_ROOT=C:\UEProjects\DengYingShanHai
Git core.longpaths=true
Git core.autocrlf=false
UnrealEditor.exe GPU preference=High performance
UnrealEditor-Cmd.exe GPU preference=High performance
```

详细测试命令、报告路径和人工待验清单见 `PHASE1_VALIDATION.md`。
