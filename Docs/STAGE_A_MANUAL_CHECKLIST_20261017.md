# 阶段 A 人工验收操作卡（作者用）

> **日期：** 2026-10-17
> **用途：** 配合《下一步开发方案_阶段A生命周期更正版.md》§二 A1/A2。把每一步与已完成的机器证据关联，标注"已证实/需目视/纯目视"，缩短验收时间。
> **机器证据基线：** 5/5 自动化测试 PASS（`D:\DYS_Build\Saved\Logs\StageAv8.log`），测试源码 `Source/.../Tests/DYKuafuAssemblyAutomationTests.cpp`。

## A1. Blueprint 图形证据（编辑器截图清单）

| 截图 | 预期内容 | 与机器证据的关系 |
|---|---|---|
| ① SCS 面板 | `KuafuMesh`（SkeletalMeshComponent）为新增节点；`SK_DY_Kuafu_Refined` 已赋值；父类 Torso/Head/Staff 在继承列表 | **已被 spawn 实例断言证实**（StageAv8）；截图补齐"父级与 Transform 数值"——预期 RelativeLocation ≈ (0, -42.4, -104.6)、Yaw 180°、Scale 0.8 |
| ② KuafuMesh Details | Animation Mode = **AnimationSingleNode**；Skeletal Mesh = SK_DY_Kuafu_Refined | **已被断言证实**（AnimationSingleNode: true）；截图补齐 AnimToPlay 占位与 CastShadow 数值 |
| ③ Construction Script 图 | 装配/显隐节点的执行线；`SetVisibility` 目标（Torso/Head → 隐藏） | **结果已被断言证实**（Torso/Head visible=0）；截图补齐节点顺序 |
| ④ Event Graph：ReceiveBeginPlay | **委托绑定节点在此**（Bind OnControlChanged → ApplyKuafuPose） | **绑定行为已被生命周期实验证实**（IsBound 0→1）；截图补齐连线 |
| ⑤ Event Graph：ApplyKuafuPose | PoseId 分支（P02_StrideReach/StrideBack/StrideMid → SetAnimation）；`LastPresentedPoseId` 防重复分支 | **端到端效果已被断言证实**（0.0→StrideBack 动画、1.0→Reach 动画）；截图补齐分支结构 |

**注意**：全部截图来自编辑器实际打开状态，保存到 `Docs/StageA_Screenshots/`（建议路径）。

## A2. 完整 PIE 视觉验收（Dev 隔离关卡）

| 步骤 | 操作 | 预期结果 | 机器证据关联 |
|---|---|---|---|
| 1 | 放置 `BP_DYKuafuPuppet_Fitted`，PIE 启动 | 真实夸父骨骼网格可见；**看不到 Cube/Sphere 灰盒**（被 CS 隐藏） | 断言已证实 visible=0；目视确认观感 |
| 2 | 记录初始 PoseId 与动画 | PoseId=P02_StrideBack（NormalizedValue=0.15），**动画应为 StrideBack** | ⚠️ 机器断言测得"初始动画=StrideMid（BP 模板默认）"——**若 PIE 中初始动画已切换为 StrideBack 则一致；若仍为 StrideMid，属于"初始姿态未显式应用"的已知次要项**（绑定修复后首次控制输入会纠正），记录实际值即可 |
| 3 | 驱动轨道到另一端 | PoseId 变化 → 动画切到对应姿态（Reach/StrideBack） | **断言已证实端到端切换**；目视确认切换平滑、无跳变 |
| 4 | 重复同一姿态通知 | 不重播 | 断言已证实（防重复正常） |
| 5 | 检查手杖对齐 | `Staff`（真杖网格）与身形对齐、无穿插 | **纯目视新项**（机器无法断言视觉对齐） |
| 6 | 停止 PIE、重开关卡再跑一次 | 初始状态一致 | 重建一致性已断言通过；生命周期目视复核 |
| 7 | 真实键盘/鼠标交互路径 | 可达、可操纵 | 纯人工 |

## 阶段 A 通过判定（填完后）

- 全部目视项通过 → 阶段 A 标记通过 → 进入阶段 B（Guide 显隐 + P02 校准）
- 步骤 2 若初始动画不匹配 → 两个可选处理（由你决定）：
  - 接受现状（首次控制输入自动纠正）并在记录中注明；
  - 或在 BP BeginPlay 绑定后追加一次"应用当前姿态"调用（一行蓝图，需你批准）。
- 任一失败 → 记录复现步骤 + 截图，提出最小修复提案（不回到已撤销的委托绑定方案）。

## 快速参考

- 自动化回归命令：`Automation RunTests DengYingShanHai.StageA`（5 项，全 PASS 基线）
- 测试日志：`D:\DYS_Build\Saved\Logs\StageAv8.log`
- 沙箱工程（可编辑器打开）：`D:\DYS_Build\DengYingShanHai.uproject`（与 `D:\灯影山海` 同源）
- 原项目：`D:\灯影山海`（未动；Source 2 改 + 测试 3 新增 + Docs 10 件，未提交）

## 附：五张截图的编辑器操作路径（2026-10-17 补充）

打开沙箱工程 `D:\DYS_Build\DengYingShanHai.uproject`，在内容浏览器导航到
`Content/DengYingShanHai/Dev/KuafuAppearance/Presentation/`，**双击 `BP_DYKuafuPuppet_Fitted`** 打开 Blueprint 编辑器。截图用 `Win+Shift+S`（区域截图）后粘贴保存到 `Docs/StageA_Screenshots/`。

| # | 面板/图页 | 编辑器内操作 |
|---|---|---|
| ① | **Components（SCS）** | 打开 BP 后默认左侧 Components 面板：应见 `KuafuMesh`（新增）与继承的 `SceneRoot/Torso/Head/Staff/PuppetControl` 层级。整窗截图。 |
| ② | **Details** | 选中 `KuafuMesh` → 右侧 Details：Skeletal Mesh（SK_DY_Kuafu_Refined）、Animation Mode（AnimationSingleNode）、AnimToPlay、Cast Shadow、Transform 区（Location ≈ (0,-42.4,-104.6)、Yaw 180、Scale 0.8）。滚动截 2 张也可。 |
| ③ | **Construction Script** | 顶部工具栏标签页切到 **Construction Script**：沿白色执行线确认 KuafuMesh 赋值、`SetVisibility`（Torso/Head 隐藏）、`SetCastShadow` 的顺序。 |
| ④ | **Event Graph：ReceiveBeginPlay** | 切到 **Event Graph**：`ReceiveBeginPlay` 事件节点 → 沿执行线到 **Bind Event to OnControlChanged**（目标 = PuppetControl，委托事件 = ApplyKuafuPose）。 |
| ⑤ | **Event Graph：ApplyKuafuPose** | 找 `ApplyKuafuPose` 自定义事件（参数 NormalizedValue/PoseId）→ 三姿态分支 → `SetAnimation`（目标 KuafuMesh）→ `LastPresentedPoseId` 防重复分支。 |

PIE 验收：内容浏览器 `Dev/StageAVerify/` 双击 `LV_StageAVerify` → 点工具栏 **Play** → 按操作卡 A2 七步执行（相机默认在 PlayerStart 上方 3.6 m，正对 Kuafu）。

**一致性对照**：编辑器中看到的 Transform/模式若与上表"预期"不符，**记录实际值，不要改动**——机器断言的 Transform 来自 spawn 实例实测，差异本身是需要报告的发现。
