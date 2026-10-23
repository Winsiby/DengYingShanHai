# P03 双变量候选校准（Dev 几何诊断）

日期：2026-10-05
状态：Dev 候选构图校准已完成。75 组是几何诊断，不是玩家通关，不是正式 P03 全流程，不是人工验收，不是新打包版本。

责任人：Codex 唯一实现与验收责任人；用户只确认了结构选择；WorkBuddy 只记录证据。队友负责正式免费合规美术与视频。
事实来源：`Saved/Audit-2026-10-05-P03InteractionCalibration/WorkBuddy-Task.md` 与同目录 `Evidence-BeforeWorkBuddy.json`。未读取原始 .log / Console / Stderr、账号或遥测。

> 永远不要以牺牲架构设计为代价追求功能；永远不要基于猜测进行权衡——必须与我确认。

---

## 1. 用户授权范围

用户已确认**「直接双变量组合，先做 Dev 候选样本」**。

本轮因此**不新增**先锁灯、再调偶的阶段，**不新增姿态按键**。

已完成的是 **Dev 候选构图校准**，不是玩家可玩样本、不是正式 P03 全流程、不是人工通关、不是新打包版本。**本轮没有新游戏启动器。**

用户仅确认结构，**不能据此推导具体目标或时长也已获批准**。

## 2. 已有资产状态

已保存的 `BP_DYForestPresentation_Dev` **仍是原 15 枝灰盒**，布局、网格、材质、CDO 均未改。

角色仍为灰盒，薄枝仍偏 V/U 枝形，剧场为黑盒，地面偏亮。**不能称正式高质量美术通过。**

## 3. 诊断实现范围

新诊断仅在本审计的 `Calibrate-P03.py`。独立未保存的 Editor PIE 临时演员，以及 Transient package 中未保存的诊断 Definition（**不是 RF_Transient flag**）。

只使用现有 C++ 调用，**不改 C++**。

每个采样的设置：把实际灯 / 偶读回值与实际当前 pose 设为诊断目标，两个参数都启用，**exact 0 容差，Hold = 0**；由 `StartCurrentPuzzle` 产生真实 Resolve / Token。

随后实际 Staff **仅平移**，A 端**真正投影**到已确认的 Z70 高位地线，再通过**当前身份**的原生接触授权接入 Forest。

> **Hold = 0 仅用于加速几何校准**：不验证保持难度，不改变 15 Hz，**不代表用户完成谜题**。

完整几何在显示生长前预检，使用实际 Cylinder bounds 与当前接触；按实际 Torso/Head 16 角投影加幕尺寸 **2% padding** 建立保护框。

检查是**真实几何与包围框**，**不是阴影像素识别**，**不证明全部连续参数空间**。

## 4. Run4 与 Run5

Run4 冷启动 **50 组**成功完成：**39 组数值安全、11 组预计边界不可用**。

Run5 冷启动 **75 组**成功完成，**前 50 组的选定几何 / 姿态 / 接触 / 结果字段与 Run4 逐项完全一致**。

## 5. Run5 分组结果

| 分组 | 采样范围 | 结果 |
|---|---|---|
| Domain | 灯 / 偶分别 `{0, .25, .5, .75, 1}`，25 组 | 14 Clear；10 原生 Forest Begin 拒绝；1 Resolve 初始 A 已在幕外 |
| LocalReference | 灯 `{.63, .675, .72, .765, .81}` × 偶 `{.71, .755, .8, .845, .89}` | 25/25 Clear |
| ReachCandidateProbe | 灯同上 × 偶 `{.76, .805, .85, .895, .94}` | 25/25 Clear，全部 `P02_StrideReach` |

Domain 组中那 10 组的 actual pure initial geometry status 均为 **OutsideScreen**（端点越幕），另有 1 组 Resolve 初始 A 已在幕外。

**这些不是 11 个程序异常或测试失败**，而是几何上预计不可用的边界。

LocalReference 组是**旧 P02 周边参考，不等于推荐 P03 目标**。

## 6. 合计

| 项 | 数量 |
|---|---|
| 总采样组 | 75 |
| 数值安全 | 64 |
| 真实接触次数 | 74 |
| 实际枝组件验证 | 960 个组件样本 |
| 原始截图 | 10 张 1600x900 |

960 是**组件样本验证数，不是 960 个运行 Actor**。所有安全组每组验证 15 个实际枝组件。

截图**不包含完整 HUD**，不能代替中文 UI、输入、保持、复位与现场人工检查。

## 7. 每次采样的核验与收尾

每次都在截图前后核验：身份、灯偶根变换、幕与地线、Staff 接触变换、Forest token 与实际组件、POV。

会话末恢复原 Definition 与 Staff 及 Editor 引用，释放原生枝资源，拒绝旧 Token，退出 PIE。**CDO 没有运行会话。**

清理是诊断复位，**不是游戏的 R 策略**。

## 8. 本轮未做与日志

本轮**没有 Build / Cook / 新包**。**不能把上轮 Editor 70/0 与包内 NullRHI 11/0 当成本轮玩家 P03 通过。**

Run4 与 Run5 各有 **13 条** `LogAutomationTest: Error: Condition failed` 初始化错误、**3 warnings**，**0 Ensure / Unhandled / Fatal**。本次诊断自身无 error。**不声称整份日志零错误。**

## 9. 保留的失败与修正

| 轮次 | 事实 |
|---|---|
| Run1 | 参数拼接未加分组，被 PowerShell 解析成 **9 个**参数片段（正确应为 5），脚本未产出样本；Console / Stderr 保留 |
| 反射修正 | 两处新脚本反射 / 字段错误（非反射 inline getter、`ScreenLocalZ` 字段名）在 **Run2 前**经审查修正，**不修改产品 C++** |
| Run2 | 50 组 / 0 诊断异常，但**尚未有增强身份检查，不作为最终证据** |
| Run3 | 在初期 POV 一致性检查中断，**0 样本**；后来加入诊断出生稳定等待，沿用原有数值比较方式，Run4/5 通过 |

**不推断已证明 Run3 的唯一物理根因，不修改相机设置。**

## 10. 设计结论

- **灯是一个连续量**；偶的位置与姿态挡位由**同一个 A/D 连续量联动**。
- 第三幕是**两个已学控制量的组合，不是三个独立自由度**。
- 旧参考偶 `.80 ± .09` **跨 `.75` 现有姿态边界**，所以「位置仍在退出区间」**并不保证 RequiredPose 仍通过**。这是 P03 候选设计需规避的边界，**不判定已验收的 M2 有 Bug**。

## 11. 待用户确认的 Dev 候选

Codex 提出、**尚未获批准**的 Dev 候选：

| 项 | 候选值 |
|---|---|
| 灯目标 | `.72` |
| 偶目标 | `.85` |
| 进入 / 退出 | `.05` / `.09` |
| 保持 | `1.25s` |
| 偶退出区间 | `.76–.94`，**不跨姿态边界** |

已采样区域支持该提案，但**尚未实测玩家 Holding 或连续区间**。

保持与容差拟与 M2 相同，**不通过增加精度制造第三幕难度**。

另有建议：下一步 Dev **暂沿用**旧连续预览的落杖 `2s`、成林 `6s`；**未确认任何正式演出秒数**。

**上述具体 Dev 参数现在等待用户确认。** 若整理期间未收到 Codex 追加指示，仍标待确认。

## 12. 仍未确认

Q1 正式 target / tolerance / hold、Q2 drop 秒数、Q3 growth / timeout、Q4 Skip / R、Q5 整局重启、演出输入策略、正式资产。

**只有此次结构选择已批准。**

## 13. 用户可直接打开的文件

推荐候选中心图：[打开中心构图](D:/灯影山海/Saved/Audit-2026-10-05-P03InteractionCalibration/Run5/ReachCandidateProbe-L0.720-P0.850-Forest.png)。

候选边界图：[打开左侧边界](D:/灯影山海/Saved/Audit-2026-10-05-P03InteractionCalibration/Run5/ReachCandidateProbe-L0.630-P0.760-Forest.png)、[打开右侧边界](D:/灯影山海/Saved/Audit-2026-10-05-P03InteractionCalibration/Run5/ReachCandidateProbe-L0.810-P0.940-Forest.png)。

全部结果：[Results.json](D:/灯影山海/Saved/Audit-2026-10-05-P03InteractionCalibration/Run5/Results.json)、[Events.jsonl](D:/灯影山海/Saved/Audit-2026-10-05-P03InteractionCalibration/Run5/Events.jsonl)。

从 Windows 文件资源管理器打开以上 D 盘文件；PNG 是实际截图，不是游戏启动文件。本轮没有生成新游戏入口，旧 `D:\灯影山海\Start-M3ForestAsset.cmd` 仍只播放此前固定终态资源预览，不是本次双变量可玩候选。

## 14. 范围核验

基线保护 **195 个文件**，BeforeWorkBuddy 检查 **0 修改 / 0 新产品 / 0 缺失 / 0 意外变更**（本审计目录不计产品）。

Git **121 dirty 均已有**；HEAD 未变、index 为空、**无 Git 写操作**。未清理其余未提交内容。

**新文档与 Plan 末尾追加是本次唯一允许的产品变更。**

Codex 已执行 AfterWorkBuddy 复核：唯一旧产品修改是 Plan 末尾追加，唯一新产品是本文档。无缺失、无意外变更；Plan 原 67,878 字节前缀完整保留；原 121 项 dirty 全部保留，当前 122 项，HEAD 不变、index 为空。源码、Config、Content、旧 Scripts、Tools、旧启动器及既有 M2 未改变。最终修订后的复核记录另存 [Evidence-Final.json](D:/灯影山海/Saved/Audit-2026-10-05-P03InteractionCalibration/Evidence-Final.json)，不覆盖 Before/AfterWorkBuddy 记录。

## 15. 状态

本轮候选构图校准完成，整体 P03 尚未完成。75 组采样全部执行完成，其中 64 组数值安全、11 组边界不可用；不是“75 组构图全通过”。**不是玩家通关、不是正式 P03 全流程、不是人工验收、不是新打包版本。** 具体 Dev 参数仍待用户确认。本文不构成参赛作品或用户验收结论，未代签任何人工确认。

本轮架构技能促使实现保持为独立诊断：没有为了快速成林去改判定、重写 Forest 布局或增加正式演出状态机。输入结构获确认不等于具体阈值获确认；下一步先由用户接受具体 Dev 候选，再由 Codex 实现并独立验证可玩流程。

AI 记录：Codex 实施与实测，独立只读审查，WorkBuddy 文档整理。不声称已完成赛事 AI 申报。
