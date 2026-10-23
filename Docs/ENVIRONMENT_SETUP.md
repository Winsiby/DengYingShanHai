# ENVIRONMENT SETUP｜开发环境基线

## 1. 固定版本基线

本项目当前 `.uproject` 采用以下 Windows 开发基线：

| 项目 | 基线 |
|---|---|
| Unreal Engine | **UE 5.8.x 正式版二进制发行版**，不使用 Preview |
| IDE | Visual Studio Community 2026 18.0 或更高 |
| MSVC | 14.50.35717 为 UE 5.8.3 首选；更新工具链必须实编译验证并保留警告记录 |
| Windows SDK | 10.0.26100.x |
| 目标平台 | Windows 64-bit，键鼠优先 |
| 图形 API | DirectX 12；出现驱动兼容问题时保留 DX11 诊断回退 |
| 源码管理 | Git + Git LFS |

选择 UE 5.8 的原因：本机已安装 UE 5.8.3、Visual Studio 2026 与 Windows SDK 26100。当前实际 MSVC 为 14.51.36260；Editor 与 Game Target 已实编译成功，但 UnrealBuildTool 明确提示其新于首选 14.50.35717。该状态可继续第一阶段开发，但不能写成“完全无警告的推荐组合”。不要在当前竞赛版本开发中途升级 UE 小版本；只有阻断性问题且有完整备份时才评估升级。

## 2. 本机盘点结果（2026-10-01）

| 项目 | 当前状态 |
|---|---|
| Windows | Windows 11，build 26200 |
| CPU | Intel Core Ultra 9 275HX，24 核 / 24 逻辑处理器 |
| 内存 | 31.4 GB 可见内存，满足 UE5 推荐级别 |
| 独立显卡 | NVIDIA GeForce RTX 5070 Laptop GPU，8151 MiB 显存 |
| NVIDIA 驱动 | 592.01 |
| Visual Studio | Community 2026 18.10.3，安装于 `D:\Visual studio` |
| C++ 工具链 | MSVC 14.51.36260，工具目录 `D:\Visual studio\VC\Tools\MSVC\14.51.36231`；UE 5.8.3 报非首选版本警告 |
| Windows SDK | 10.0.26100，安装于 `D:\Windows Kits\10` |
| Git / Git LFS | 已安装；仓库已启用本地 Git LFS |
| Epic Games Launcher | 已安装 |
| Unreal Engine | **UE 5.8.3，CL 58210709**，安装于 `C:\Program Files\Epic Games\UE_5.8` |
| 磁盘 | C 盘约 148 GB 可用，D 盘约 337 GB 可用 |

UE 编辑器当前安装在 C 盘，剩余空间仍满足本项目开发与打包。不要再并装多个 UE 大版本；若未来磁盘不足，应通过 Epic Launcher 移动/重装引擎，不手工剪切引擎目录。

### 项目路径修复

当前仓库物理路径包含中文和空格。实际 C++ 冒烟编译证明，MSVC/Unreal Build Accelerator 会把该路径错误转码，导致 PCH 文件报 `C1083`。为避免后续编译失败，已建立纯英文目录联接：

```text
C:\UEProjects\DengYingShanHai
    -> C:\Users\lenovo\Documents\ChatGPT\数媒游戏开发
```

以后创建、打开、编译和打包 `.uproject` 时，必须使用 `C:\UEProjects\DengYingShanHai` 入口。原仓库没有移动或复制；两个路径指向同一组文件。不要删除这个目录联接，也不要通过中文物理路径打开 UE 工程。

已设置用户级环境变量：

```text
DY_UE_ROOT=C:\Program Files\Epic Games\UE_5.8
DY_PROJECT_ROOT=C:\UEProjects\DengYingShanHai
```

Windows 图形首选项已将 `UnrealEditor.exe` 与 `UnrealEditor-Cmd.exe` 设置为高性能 GPU。当前 Git 仓库已启用 `core.longpaths=true` 并固定 `core.autocrlf=false`，文本换行继续由 `.gitattributes` 管理。

## 3. UE 5.8 安装状态与复核

UE 5.8.3 已安装并通过核心文件检查。当前机器无需重复执行以下安装步骤；保留本节供重装或作者换机配置使用。

1. 打开 Epic Games Launcher 并登录 Epic 账号；
2. 进入“虚幻引擎 / Unreal Engine”→“库 / Library”；
3. 添加引擎版本，选择最新 **5.8.x 正式版**，不要选择 Preview；
4. 安装位置使用 `D:\Epic Games\UE_5.8`；
5. 安装选项保留：
   - Core Components；
   - Templates and Feature Packs；
   - Windows Target Platform；
6. 当前竞赛版本初期取消：
   - Android、iOS、Linux、TV 等非 Windows 平台；
   - Editor symbols for debugging；
   - Engine Source；
   - Starter Content（项目不依赖它，可按个人需要保留）；
7. 安装完成后从引擎版本菜单执行一次 Verify；
8. 运行环境检查：

```powershell
powershell -ExecutionPolicy Bypass -File .\Scripts\Check-Environment.ps1
```

只有所有 Required 项目均为 PASS 后，才继续 C++ 工程开发。本机当前检查结果为 Required failures 0、warnings 1；唯一预期警告是 MSVC 14.51 新于 UE 5.8.3 首选工具链，详见 `ENVIRONMENT_VALIDATION.md`。

## 4. Visual Studio 组件

项目根目录的 `.vsconfig` 已固定所需组件。当前机器已安装并验证：

- Game development with C++；
- MSVC x64/x86 build tools；
- Windows 11 SDK 10.0.26100；
- CMake tools；
- AddressSanitizer；
- Visual Studio Tools for Unreal Engine；
- Unreal Engine Blueprint debugger tools；
- Unreal Engine Test Adapter。

作者在新电脑上可在 Visual Studio Installer 中选择“更多 → 导入配置”，导入项目根目录的 `.vsconfig`。

## 5. 当前工程创建决定

当前工程采用以下已确认参数：

| 选项 | 选择 |
|---|---|
| Category | Games |
| Template | 不导入完整模板；项目自建最小 C++ 第三人称载体 |
| Project Type | C++ |
| Target Platform | Desktop |
| Quality Preset | Maximum；若编辑器明显卡顿再降为 Scalable |
| Ray Tracing | 关闭；本项目不把硬件光追作为通关前提 |
| Starter Content | 关闭 |
| Project Name | `DengYingShanHai` |

当前工程已完成：

1. 记录精确 UE 版本和引擎安装路径；
2. 生成并编译一次 Development Editor Win64；
3. 创建项目自己的 `LV_InteractionLab` 并通过自动 PIE；
4. 编译 Development Game Target，并验证生成物是非零的有效 Windows PE；未 Cook 的裸 EXE 不作为独立发行包验收；
5. 保留完整 Windows Development Cook/Package 作为后续打包里程碑，不能把未 Cook 的 Game Target 等同于发行包。

## 6. 版本管理规则

- `.uasset`、`.umap`、FBX、PSD、WAV、MP4 等二进制文件已通过 `.gitattributes` 交给 Git LFS；
- `Binaries`、`Intermediate`、`DerivedDataCache`、`Saved`、`.vs` 和生成的 `.sln` 不提交；
- `Config`、`Content`、`Plugins` 源文件、`Source`、`.uproject`、文档和许可记录必须提交；
- 每次获取或恢复大文件前运行 `git lfs env`，避免把 LFS 指针错误地当成资产；
- 不在仓库中保存 Epic 账号、API 密钥、个人路径或未脱敏日志。

## 7. 首轮编辑器设置

当前工程设置只保留已验证的最小项；新增 `.ini` 配置必须说明用途并进入复核：

- Source Code Editor：Visual Studio 2026；
- Default RHI：DirectX 12；
- Shader Model：SM6；
- Enhanced Input：启用；
- Lumen：先按模板默认值验证，再依据目标机性能取舍；
- Live Coding：仅用于小范围 C++ 函数修改；改 UCLASS/USTRUCT/UENUM、构造函数或模块配置后关闭编辑器完整编译；
- Derived Data Cache：先使用默认本地缓存，不在当前竞赛版本中搭建共享 DDC；
- 自动保存不能替代 Git 提交和每日可运行备份。

## 8. 环境验收标准

环境配置只有同时满足以下条件才算完成：

- `Check-Environment.ps1` 的 Required failures 为 0；
- UE 5.8 编辑器能启动；
- 最小 C++ 项目的 Editor 与 Game Target 能完整编译；
- PIE 可运行；
- Development Game Target 能生成有效 PE；正式提交前另做 Cook/Package 和目标机独立运行；
- Git LFS 正确追踪 `.uasset` 与 `.umap`；
- 未安装项目不需要的移动端 SDK、渲染插件或大型样例。

本机已通过实际工程的 Editor/Game 编译、无界面资产验证、C++ Automation 与真实 D3D12 PIE。详细记录见 `ENVIRONMENT_VALIDATION.md` 与 `PHASE1_VALIDATION.md`。

## 9. 官方依据

- [Epic：UE 5.8 硬件与软件规格](https://dev.epicgames.com/documentation/en-us/unreal-engine/hardware-and-software-specifications-for-unreal-engine)
- [Epic：安装 Unreal Engine](https://dev.epicgames.com/documentation/unreal-engine/install-unreal-engine)
- [Epic：Visual Studio 与 UE 版本兼容性](https://dev.epicgames.com/documentation/en-us/unreal-engine/setting-up-visual-studio-development-environment-for-cplusplus-projects-in-unreal-engine)
- [Microsoft：安装 Visual Studio Tools for Unreal Engine](https://learn.microsoft.com/zh-cn/visualstudio/gamedev/unreal/get-started/vs-tools-unreal-install)
