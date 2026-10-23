# 阶段 A 核验报告：`BP_DYKuafuPuppet_Fitted` 装配与姿态动画

> **日期：** 2026-10-17　**执行者：** Codex
> **依据：** 《下一步执行安排_Git盘点修订2.md》阶段 A
> **方法：** 装配断言自动化测试（瞬态游戏世界 spawn → 组件状态断言 → `RerunConstructionScripts` 重建一致性 → 委托驱动姿态映射）。**只读**：未保存/覆盖正式主图，未修改任何 UE 资产，未执行 Git 写操作。
> **证据边界（先读）：** 本核验是**运行时组件状态断言**（NullRHI 无头环境），不是人眼视觉验收。手杖对齐、穿插、动画观感仍需作者在编辑器 PIE 中目视确认。瞬态世界与完整 PIE 的环境差异（无 GameMode/GameInstance）已在 §5 说明。

## 1. 通过项（运行时断言证据）

| 项 | 断言 | 结果 |
|---|---|---|
| **SCS 装配存在** | spawn 实例上存在名为 `KuafuMesh` 的 SkeletalMeshComponent | **PASS**（CDO 看不到的 SCS 组件在实例化时由 CS 创建，证实） |
| **网格赋值** | `KuafuMesh.SkeletalMesh == SK_DY_Kuafu_Refined` | **PASS** |
| **父类组件保留** | `Torso`/`Head`/`Staff` 三个继承组件在实例上存在 | **PASS** |
| **手杖真网格** | `Staff.StaticMesh == SM_DY_Kuafu_Staff`（非 Engine Cylinder） | **PASS** |
| **灰盒显隐** | `Torso.IsVisible() == 0` 且 `Head.IsVisible() == 0` | **PASS——CS 隐藏了灰盒**（"新旧同时显示"风险排除） |
| **动画模式** | `GetAnimationMode() == AnimationSingleNode` | **PASS** |
| **重建一致性** | `RerunConstructionScripts()` 后：KuafuMesh 仍存在且不重复（SkeletalMeshComponent 计数仍为 1）、SK 赋值不变、Torso/Head/Staff 保留 | **PASS** |
| **轨道机制** | `SetNormalizedValue(0.0/1.0)` 驱动 `PoseId` 正确变化（`P02_StrideBack` ↔ `P02_StrideReach`），委托广播发生 | **PASS**（C++ 侧 PuppetControl 正常） |

**Transform 记录**（A1 证据值，不判定）：

```
KuafuMesh RelativeLocation = (X=-0.000, Y=-42.441, Z=-104.574)
KuafuMesh RelativeRotation = (P=0, Y=180.0, R=0)   ← 面向翻转 180°
KuafuMesh RelativeScale3D  = (0.8, 0.8, 0.8)
```

## 2. 失败项（运行时缺陷，非符号推断）

### FAIL：姿态动画切换未生效

**现象**（运行时 `AnimSingleNodeInstance.GetAnimationAsset()` 实测，非编辑器属性）：

| NormalizedValue | PoseId（正确变化） | 实际播放动画（错误） |
|---|---|---|
| 0.15（初始） | `P02_StrideBack` | `A_DY_Kuafu_Poses_Armature_A_DY_Kuafu_StrideMid` |
| 0.0 | `P02_StrideBack` | `…StrideMid`（未切换） |
| 1.0 | `P02_StrideReach` | `…StrideMid`（**未切换**） |

**判定**：`PoseId` 轨道映射正常，但 **BP 的 `ApplyKuafuPose` 未把 `KuafuMesh` 切到对应姿态动画**——运行时当前动画始终停留在 StrideMid。两个具体疑点（从 name table 符号推断，需图形确认）：

1. `OnControlChanged` 委托**未实际绑定**到 `ApplyKuafuPose`（`K2Node_AddDelegate` 符号在场但绑定分支/时机可能未执行）；
2. 或绑定成功但 `ApplyKuafuPose` 内的 `SetAnimation` 分支被 `LastPresentedPoseId` 防重复逻辑拦截（该变量在 name table 中在场）。

另有一个观察：初始 NormalizedValue=0.15 → PoseId=`P02_StrideBack`，但初始动画是 StrideMid——**初始状态即不匹配**（若 BP 意图"初始即正确姿态"，这也是同一缺陷的一部分）。

**环境限制说明**：此缺陷在**瞬态世界自动化环境**中证实；完整 PIE（有 GameMode/正式流程）是否同样复现，需作者在编辑器 PIE 中确认。但"委托广播正常 + 委托接收端无效果"的组合强烈指向 BP 内部绑定/分支问题，与测试环境无关的可能性较高。

## 3. 阻塞项（当前环境无法执行）

| 项 | 阻塞原因 |
|---|---|
| Components/SCS 面板截图、CS/Event Graph 连线截图 | 无头环境无编辑器图形界面；UE 5.8 Python 反射不暴露蓝图图数据（已定案） |
| 人眼视觉验收（真网格观感、手杖对齐、穿插、动画观感） | 无渲染（NullRHI）、无人类目视 |
| 录屏 | 同上 |

**未把符号扫描当作通过证据**：本报告的通过项全部来自 spawn 实例的运行时断言；失败项同样来自运行时实测。

## 4. 证据路径

| 证据 | 路径 |
|---|---|
| 测试日志（3 项结果 + AddInfo 证据行） | `D:\DYS_Build\Saved\Logs\StageATest6.log`（最终轮）、`StageATest5.log`（AnimationData 误读轮，保留） |
| 测试源码（新增，未提交） | `Source/DengYingShanHai/Private/Tests/DYKuafuAssemblyAutomationTests.cpp` |
| 测试过滤器 | `DengYingShanHai.StageA.KuafuFitted.{SCSAssemblyDefaults, ReconstructionConsistency, PoseMapping}` |
| 构建命令 | `Build.bat DengYingShanHaiEditor Win64 Development -project="D:/DYS_Build/DengYingShanHai.uproject" -WaitMutex -NoUBA` → `Result: Succeeded` |
| 回退 | 删除测试文件即完整回退；不影响任何资产 |

## 5. 建议的最小修复方案（待作者批准后执行，先在 BP 编辑器确认）

1. **打开 BP 的 Event Graph**，定位 `ApplyKuafuPose` 自定义事件与其上游 `OnControlChanged` 绑定节点（`K2Node_AddDelegate`）。
2. 若绑定节点存在但未执行：检查绑定时机（是否在 BeginPlay/CS 中，瞬态测试是否因缺少该时机而未绑定——对照完整 PIE 复测）。
3. 若绑定正常但 `SetAnimation` 未触发：检查 `LastPresentedPoseId` 防重复分支是否在每次切换时错误短路。
4. 修复应**只在 `BP_DYKuafuPuppet_Fitted` 内**（它是 Dev 候选蓝图，非正式主图直接引用物）；修复后重跑本测试（`DengYingShanHai.StageA` 过滤器）回归，再进 PIE 视觉确认。
5. **不要**因该缺陷改 C++ `DYPuppetControlComponent`（其广播行为经本测试证实正常）。

## 6. 阶段 A 通过标准判定

| 通过标准 | 判定 |
|---|---|
| 组件层级/Transform 核实 | **机器证据通过**（§1 Transform 记录；父级关系需 SCS 面板截图补齐——留人工） |
| CS 顺序核实 | **部分**：装配结果经运行时证实；节点顺序需图形核验 |
| 姿态映射 | **FAIL**（§2） |
| 委托生命周期 | **部分**：广播正常；绑定/解绑路径需图形核验 |
| PIE 真网格/灰盒/手杖/重建 | **部分**：装配与重建一致性机器通过；视觉部分待人工 PIE |

**阶段 A 总体：未通过（姿态映射缺陷阻塞），但装配机制本身已被运行时证据证实，剩余问题聚焦到 BP 内部的委托绑定/姿态分支。**
