# PHASE 1 VALIDATION｜最小 C++ 第三人称技术骨架验收

自动化验收日期：2026-10-01  
人工验收完成日期：2026-10-02  
工程：`DengYingShanHai`  
引擎：Unreal Engine 5.8.3  
范围：可编译 C++ 工程、最小第三人称操作载体、Dev 灰盒测试地图、输入/镜头/复位验证。

## 1. 当前验收结论

第一阶段的自动化与 9 项人工 PIE 检查均已通过，已满足继续开发 Dev 垂直切片的技术前提：

| 验收项 | 结果 | 证据 |
|---|---|---|
| Development Editor 编译 | PASS | `DengYingShanHaiEditor Win64 Development`，新增测试源实际进入编译 |
| Development Game 编译 | PASS | 清理旧产物后使用 `-NoUBA`，10 个动作完成 |
| Game EXE 文件有效性 | PASS | 非零文件，`MZ` + `PE\0\0`；已消除 0 字节/Windows 无法识别问题 |
| 未 Cook EXE 独立运行 | NOT ACCEPTED | 裸 EXE 缺少可用 premade Asset Registry，退出码 3；留待 Cook/Stage/Package |
| C++ Phase 1 Automation | PASS | 4/4，0 failed |
| Python 保存资产复核 | PASS | `DY_PHASE1_VERIFIED` |
| 地图/PIE | PASS | `Project.Maps.PIE` 1/1，Map Check 0 error / 0 warning |
| 物理键鼠与镜头手感 | PASS | 用户于 2026-10-02 确认下列 9 项人工 PIE 检查全部正常 |
| Windows Cook/Stage/Package | OUT OF PHASE | 进入后续打包里程碑，不能由 Game Target 代替 |

因此，本结论是“Phase 1 技术骨架自动化与人工操作验收通过”，不是“比赛版本完成”。Cook/Stage/Package、M1 灯影互动和正式美术仍按各自里程碑验收。

## 2. 自动化测试覆盖

测试源码：`Source/DengYingShanHai/Private/Tests/DYPhase1AutomationTests.cpp`

### `DengYingShanHai.Phase1.ClassDefaults`

- `ADYStageGameMode` 默认 Pawn 为 `ADYStageOperatorPawn`；
- 默认 PlayerController 为 `ADYStagePlayerController`；
- Explore Mapping Context 路径和优先级正确。

### `DengYingShanHai.Phase1.OperatorComponents`

- Capsule、CharacterMovement、Spring Arm、Follow Camera 存在；
- 碰撞体尺寸、移动速度与朝向策略正确；
- Spring Arm 长度、相机碰撞、Probe、旋转所有权和无 Lag 基线正确；
- Camera 连接到 Spring Arm 的 `SpringEndpoint`，FOV 为 70。

### `DengYingShanHai.Phase1.InputContract`

- Move/Look 为 Axis2D，Reset 与 M1 Interact 为 Boolean；
- Phase 1 初验时恰好存在 6 个 Dev 映射；M1 接入后回归口径为 7 个，其中新增 `E → Interact`；
- W = Swizzle YXZ；S = Negate → Swizzle YXZ；A = Negate；D = 无修饰器；
- Mouse2D → Look；R → Reset。

### `DengYingShanHai.Phase1.ResetContract`

- 在临时 Game World 中真实 Spawn `ADYStageOperatorPawn`；
- BeginPlay 捕获初始状态；
- 位移并施加速度后执行手动复位；
- 初始 Transform 恢复、速度清零、MovementMode 恢复为 Falling、计数增加一次；
- 测试结束销毁 WorldContext，不污染编辑器世界。

## 3. 测试先行发现并修复的问题

初次运行 `DengYingShanHai.Phase1` 时，自动化框架发现 4 个测试，其中 3 个通过、`InputContract` 失败。失败证据是 W/S/A 三个映射的 `Modifiers.Num()` 全为 0。

根因不是 C++ 移动逻辑，而是 `Create-Phase1Assets.py` 把 `map_key()` 返回的 `FEnhancedActionKeyMapping` 当成持久引用。UE Python 暴露的是结构体值副本，对副本添加 Modifier 不会自动写回 Mapping Context 数组。

修复方式：先创建六个映射，再读取 `default_key_mappings.mappings`，修改数组中的结构体副本，并把完整数组回写到 profile/context 后保存。脚本同时增加保存前的 Modifier 数量断言。修复后：

- C++ Automation 4/4 通过；
- 独立 Python 验证从磁盘重新加载资产，确认每个 Key/Action/Modifier 组合；
- `Project.Maps.PIE` 复跑通过。

## 4. 构建命令

### Development Editor

```powershell
& 'C:\Program Files\Epic Games\UE_5.8\Engine\Build\BatchFiles\Build.bat' `
  DengYingShanHaiEditor Win64 Development `
  '-Project=C:\UEProjects\DengYingShanHai\DengYingShanHai.uproject' `
  -WaitMutex -NoHotReloadFromIDE -NoEngineChanges -NoUBA
```

新增 `.cpp` 文件但 UBT 仍报告“Target is up to date”时，补一次 `-NoUBTMakefiles` 强制重新扫描；不能以没有编译动作作为新测试已编译的证据。

### Development Game

```powershell
& 'C:\Program Files\Epic Games\UE_5.8\Engine\Build\BatchFiles\Build.bat' `
  DengYingShanHai Win64 Development `
  '-Project=C:\UEProjects\DengYingShanHai\DengYingShanHai.uproject' `
  -WaitMutex -NoHotReloadFromIDE -NoEngineChanges -NoUBA
```

当前机器必须保留 `-NoUBA`。此前 UBA 链接失败留下 0 字节 EXE 和旧回执，导致后续增量构建误报 up-to-date；修复细节见 `ENVIRONMENT_VALIDATION.md`。该命令只构建 Game Target，不执行 Cook/Stage，不能用来证明独立发行包可运行。

## 5. 自动化复跑命令

### C++ Phase 1 Tests

```powershell
& 'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe' `
  'C:\UEProjects\DengYingShanHai\DengYingShanHai.uproject' `
  -Unattended -NullRHI -NoSound -NoSplash -stdout -FullStdOutLogOutput `
  '-ExecCmds=Automation RunTests DengYingShanHai.Phase1;Quit' `
  '-ReportExportPath=C:\UEProjects\DengYingShanHai\Saved\Automation\Phase1-Automation' `
  '-TestExit=Automation Test Queue Empty'
```

### 保存资产独立验证

```powershell
& 'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe' `
  'C:\UEProjects\DengYingShanHai\DengYingShanHai.uproject' `
  -Unattended -NullRHI -NoSound -NoSplash -stdout -FullStdOutLogOutput `
  '-ExecutePythonScript=C:\UEProjects\DengYingShanHai\Scripts\Verify-Phase1Assets.py'
```

成功标志必须包含 `DY_PHASE1_VERIFIED`，不能只依赖进程退出码。

### 真实渲染路径 PIE

```powershell
& 'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe' `
  'C:\UEProjects\DengYingShanHai\DengYingShanHai.uproject' `
  -Unattended -NoSound -NoSplash -stdout -FullStdOutLogOutput `
  '-ExecCmds=Automation RunTests Project.Maps.PIE;Quit' `
  '-ReportExportPath=C:\UEProjects\DengYingShanHai\Saved\Automation\Phase1-MapsPIE' `
  '-TestExit=Automation Test Queue Empty'
```

此项故意不加 `-NullRHI`，用于验证 D3D12/SM6 下地图可加载、GameMode 可启动、Enhanced Input Context 可应用、PIE 可退出。

报告位于 `Saved/Automation/`，属于本机生成证据，按 `.gitignore` 不提交仓库。

## 6. 人工键鼠验收单

下列项目已由用户在编辑器 PIE 中人工操作确认，自动化通过不作为替代证据：

- [x] 窗口获得输入焦点后，W 前进、S 后退、A 左移、D 右移，方向与镜头朝向一致；
- [x] 同时按 W+D 时可斜向移动，没有轴交换或单轴丢失；
- [x] 鼠标水平移动控制 Yaw，垂直移动控制 Pitch，方向符合使用者预期；
- [x] Pitch 被限制在 -60° 到 45°，不会翻转或看到模型内部；
- [x] 靠墙后转动镜头，Spring Arm 碰撞缩短有效，不穿墙、不出现严重抖动；
- [x] 角色移动一段距离后按 R，角色回到 PlayerStart，速度清零；
- [x] 从 KillZ 下落时角色可复位且不会卡死或无限重复计数；
- [x] 输入上下文只应用一次，没有重复绑定造成的双倍移动或双倍复位；
- [x] 连续操作至少 3 分钟，没有失去控制、相机漂移或明显卡顿。

记录：测试日期为 2026-10-02；操作者为用户；使用键盘与鼠标，具体设备型号未记录；用户报告 9 项全部正常；录像路径未提供。若后续替换 Pawn、Spring Arm、输入修饰器或映射上下文，必须重新执行受影响项目。

## 7. 架构与范围边界

- 当前 `R` 只复位操作载体，不决定整局体验复位策略；
- 当前 WASD/Mouse/R 是 Dev 物理映射，不等于最终比赛按键方案；
- 当前基础形体只是灰盒操作载体，不是夸父或正式玩家模型；
- 自动化测试放在 Runtime 模块并用 `WITH_DEV_AUTOMATION_TESTS` 守卫，不增加 Shipping 行为；
- Python Script Plugin 仅限 Editor，用于可重复生成和验证，不进入 Game runtime；
- 阴影、幕布、判定频率和整局复位继续只允许在 `Content/DengYingShanHai/Dev/` 内实验，正式采用仍需提交证据并由用户确认。

最高优先级限制继续有效：*永远不要以牺牲架构设计为代价追求功能；永远不要基于猜测进行权衡——必须与我确认。*
