# 阶段 A 根因报告：姿态动画未切换

> **日期：** 2026-10-17　**执行者：** Codex
> **依据：** 《Codex下一步执行指令_阶段A姿态动画.md》
> **本轮边界遵守：** 未修改 Blueprint、C++ 产品代码、资产、地图或 Git 状态。新增/扩展的仅是自动化测试文件（上轮已存在的测试文件的追加，属测试代码）。
> **执行环境限制（如实声明）：** 无头环境无编辑器图形界面（§2 Event Graph 节点级核验阻塞）、无渲染（§3 完整 PIE 阻塞）。**根因通过扩展自动化测试的二分实验查明**——这不是符号扫描，是运行时行为实测。

## 1. 检查范围

- **实际执行的检查**：① 只读 Git 状态记录；② 扩展自动化测试 `DYKuafuAssemblyAutomationTests.cpp`，新增 `DelegateBindingDiagnosis` 测试：瞬态世界 spawn 实例 → `OnControlChanged.IsBound()` 实测 → **`ProcessEvent` 直接调用 BP 的 `ApplyKuafuPose`（绕过委托）** → 验证重复通知与切换分支。
- **未能执行的检查（阻塞）**：Blueprint 编辑器节点连线核验（无图形界面）；完整 PIE（无渲染与人工）。

## 2. 根因结论

### 已证实（运行时实测证据）

**根因：`OnControlChanged` 委托从未被绑定，C++ 广播时无任何接收者——BP 的 `ApplyKuafuPose` 事件逻辑本身完全正常。**

证据链（`D:\DYS_Build\Saved\Logs\StageADiag.log`）：

```
DIAG OnControlChanged.IsBound=0                                    ← 委托零绑定
DIAG after direct ApplyKuafuPose(1.0, P02_StrideReach):
    playing=…A_DY_Kuafu_Poses_Armature_A_DY_Kuafu_Reach            ← 直接调用 → 正确切到 Reach
DIAG after repeat same-pose call: playing=…Reach                   ← 重复同姿态不重播（防重复正常）
DIAG after direct ApplyKuafuPose(0.0, P02_StrideBack):
    playing=…A_DY_Kuafu_Poses_Armature_A_DY_Kuafu_StrideBack       ← 切换回来 → 正确切到 StrideBack
VERDICT: the BP event itself works when called directly. The broken link
         is the OnControlChanged delegate binding (hypothesis 1).
```

**假设判定**：

| 假设 | 判定 | 依据 |
|---|---|---|
| 1. 委托未在正确时机绑定 | **已证实** | `IsBound()=0` + 直接调用事件即正常工作（二分实验） |
| 2. `LastPresentedPoseId` 防重复短路 | **排除** | 直接调用下重复同姿态不重播、姿态变化必切换，防重复行为正确 |
| 3. 初始姿态未显式应用 | **已证实（次要）** | 初始 PoseId=`P02_StrideBack` 但初始动画=StrideMid（BP 模板默认 AnimToPlay），无初始应用调用；绑定修复后此问题应一并消失（若 BeginPlay 绑定后立即应用一次当前姿态） |
| 4. 完整 PIE 与瞬态世界生命周期差异 | **未证实（无法本机验证）** | 需作者在编辑器 PIE 复测；但"广播正常+零绑定+事件本身正常"的组合与生命周期差异无关 |

### 未证实 / 留给图形核验

- 绑定节点在 Event Graph 中的确切位置与执行前提（为何保存态有 `K2Node_AddDelegate` 符号但运行时零绑定——节点可能挂在未执行的路径上，或绑定时机早于/晚于正确生命周期）——**需要图形界面看连线**，Python 已定案无法读取。

## 3. PIE 结果

**阻塞**：完整 PIE 需要编辑器图形会话与人工目视，当前无头环境无法执行。建议作者按以下最小步骤复测（修复后）：

1. 打开 BP 确认绑定节点位置 → PIE 观察 `PoseId` 初始值与动画
2. 触发 StrideBack / StrideReach → 目视动画切换
3. 重复同姿态 → 确认不重播
4. 重启 PIE → 初始姿态与 PoseId 一致

## 4. 证据路径（全部真实存在）

| 证据 | 路径 |
|---|---|
| 根因诊断日志（IsBound / 直接调用 / VERDICT） | `D:\DYS_Build\Saved\Logs\StageADiag.log` |
| 上轮姿态映射失败日志（对照） | `D:\DYS_Build\Saved\Logs\StageATest6.log` |
| 诊断测试源码（新增扩展） | `Source/DengYingShanHai/Private/Tests/DYKuafuAssemblyAutomationTests.cpp` |
| 过滤器 | `DengYingShanHai.StageA.KuafuFitted.DelegateBindingDiagnosis`（本轮新增）+ 既有 3 项 |

## 5. 最小修复提案（待作者批准，不直接执行）

**修复目标：只改 `BP_DYKuafuPuppet_Fitted` 内的委托绑定生命周期，一处。**

1. **提案内容**：在 BP 的 `BeginPlay`（或 Construction Script 末尾，取决于现有设计意图）中，确保 `OnControlChanged` → `ApplyKuafuPose` 的 **Bind Event** 节点在正确生命周期实际执行；并在 `EndPlay` 路径对称 **Unbind**（防重复绑定/遗留委托——与既有 `K2Node_RemoveDelegate` 符号对齐）。
2. **顺带修正（同一缺陷族）**：绑定完成后**立即用当前 `PoseId` 调用一次 `ApplyKuafuPose`**，消除"初始 PoseId 与初始动画不一致"（假设 3）。
3. **预期行为变化**：修复前——广播无人接收，动画永远停留 BP 模板默认（StrideMid）；修复后——每次轨道姿态变化立即切换到对应姿态动画，初始即匹配。
4. **回归命令**：`Automation RunTests DengYingShanHai.StageA`（4 项测试：3 项既有 + 1 项诊断。修复后 PoseMapping 应转 PASS，DelegateBindingDiagnosis 中 `IsBound` 应为 1——若测试通过 EnvironmentSpawner 先绑定的话；至少 PoseMapping 转绿是硬标准）。
5. **回退方式**：BP 修改前在编辑器中复制该蓝图资产为备份（或依赖 Git 未跟踪状态直接还原）；C++/资产零改动，测试文件删除即回退。

**边界重申**：提案不涉及 C++、正式主图、Transform、手杖、谜题参数。`P02_StrideBack/Reach/Mid` 与委托生命周期以外的图逻辑不动。

## 6. 是否修改文件

**产品文件：否**（Blueprint/C++/资产/地图零修改）。**测试文件：是**（扩展既有自动化测试文件以完成根因诊断——属测试代码，上轮已建立此类新增的先例与授权语境）。

## 7. 等待作者批准的事项

1. **批准最小修复提案**（§5）：在 BP 内补绑定生命周期 + 初始姿态应用。
2. 批准后由谁执行：BP 节点修改需要编辑器图形界面（作者/作者授权的编辑器会话）。
3. 修复完成后：阶段 A 剩余人工项（SCS 面板截图、PIE 目视、手杖对齐）与阶段 A 通过标准判定。
4. Git 提交与远端策略（既有 `GIT_INVENTORY_20261017.md` 决策清单仍然有效）。
