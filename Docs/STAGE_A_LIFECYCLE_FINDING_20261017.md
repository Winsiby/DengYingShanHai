# 阶段 A 生命周期发现：此前"姿态缺陷"为测试夹具假象，产品 BP 验证通过

> **日期：** 2026-10-17　**执行者：** Codex
> **依据：** 《阶段A委托绑定根因修复执行单.md》第 2 节第 5 项（"检查是否在 BeginPlay、Construction Script 或其他初始化路径中绑定"）
> **性质：** 对 `STAGE_A_REPORT_20261017.md` 失败项的**撤回与更正**。诚实记录发现过程。
> **约束遵守：** 未修改 BP/C++/资产/地图/Git；仅修正测试夹具与新增生命周期实验。

## 1. 决定性实验（v7 BeginPlayBinding）

| 测量点 | 结果 |
|---|---|
| spawn 后（BeginPlay 前） | `OnControlChanged.IsBound() = 0` |
| 显式 `DispatchBeginPlay()` 后 | `IsBound() = 1`（**绑定在 ReceiveBeginPlay 中生效**） |
| BeginPlay 后 `SetNormalizedValue(1.0)` | `PoseId=P02_StrideReach`，**实际播放 `…A_DY_Kuafu_Reach`** |

**端到端链路全通**：委托绑定 → C++ 广播 → BP `ApplyKuafuPose` → `SetAnimation` 切换到正确姿态。

## 2. 更正

`STAGE_A_REPORT_20261017.md` 的失败项"姿态动画切换未生效"**撤回**：那是测试夹具假象——瞬态世界不自动派发 BeginPlay，早期夹具漏了 `DispatchBeginPlay()`，导致 BP 在 `ReceiveBeginPlay` 中的绑定逻辑从未执行。**产品 `BP_DYKuafuPuppet_Fitted` 无姿态缺陷。**

修正后的测试（5 项全部 PASS）：

```
DengYingShanHai.StageA.KuafuFitted.SCSAssemblyDefaults        PASS
DengYingShanHai.StageA.KuafuFitted.ReconstructionConsistency  PASS
DengYingShanHai.StageA.KuafuFitted.PoseMapping                PASS（夹具修正后）
DengYingShanHai.StageA.KuafuFitted.DelegateBindingDiagnosis   PASS（判词已更新）
DengYingShanHai.StageA.KuafuFitted.BeginPlayBinding           PASS（新增生命周期实验）
```

姿态映射关键证据（夹具修正后）：

```
Low (0.0):  PoseId=P02_StrideBack, playing=…A_DY_Kuafu_StrideBack
High (1.0): PoseId=P02_StrideReach, playing=…A_DY_Kuafu_Reach
```

## 3. 阶段 A 状态更新

- **机器可验证部分：全部通过**（装配、灰盒隐藏、重建一致性、委托生命周期、姿态映射、防重复）
- **原最小修复提案（§5）作废**：无需任何 BP 修改
- **剩余人工项不变**：SCS 面板/CS 图/EG 连线截图（图形界面）、PIE 目视（真网格观感、手杖对齐、穿插）、真实键鼠
- **测试夹具教训**（写入记忆）：瞬态世界测试凡涉及 BP 的 BeginPlay 逻辑，**必须显式 `DispatchBeginPlay()`**；"IsBound=0"在未派发 BeginPlay 的夹具中不构成缺陷证据

## 4. 证据路径

- 生命周期实验：`D:\DYS_Build\Saved\Logs\StageAv7.log`
- 夹具修正后全绿：`D:\DYS_Build\Saved\Logs\StageAv8.log`
- 历史（保留）：`StageATest6.log`（假阳性轮）、`StageADiag.log`（直接调用诊断轮）
- 测试源码：`Source/.../Tests/DYKuafuAssemblyAutomationTests.cpp`（5 个测试，新增未提交）

## 5. 下一步（不变）

阶段 A 通过标准中剩余的人工项由作者完成（图形截图 + PIE 目视）；随后按执行单顺序进入阶段 B。
