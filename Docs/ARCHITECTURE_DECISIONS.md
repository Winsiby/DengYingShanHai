# 《灯影山海》架构决策记录

> 用途：记录所有会影响架构、体验、性能、许可、范围或维护成本的权衡。  
> 硬约束：*永远不要以牺牲架构设计为代价追求功能；永远不要基于猜测进行权衡——必须与我确认。*

## 使用规则

1. 未确认的条目状态为 `Proposed`，不得作为正式实现依据。
2. 用户明确同意后改为 `Accepted`，并记录确认日期和确认范围。
3. 被替换的决定改为 `Superseded`，保留历史，不删除理由。
4. 实测否定的方案改为 `Rejected`，附证据和可复现条件。
5. 每项决定必须写明影响文件、资产、测试方法和回退方式。

## 决策状态

| ID | 标题 | 状态 | 当前建议 | 用户确认 | 证据/备注 |
|---|---|---|---|---|---|
| ADR-001 | 流程事实源采用关卡 Actor | Accepted | `ADYPuzzleDirector` 显式放置 | 2026-10-01 已确认 | 允许基础实现 |
| ADR-002 | 设备无关输入意图 | Accepted | Pawn → `FDYControlIntent` → `IDYControllable` | 2026-10-01 已确认 | 不预设最终按键 |
| ADR-003 | 夸父皮影骨架结构 | Accepted | 刚性分片 Skeletal Mesh | 2026-10-01 已确认 | 允许结构与枢轴测试 |
| ADR-004 | 独立 Shadow Caster | Proposed | 仅在视觉 Mesh 阴影不稳定时启用 | 仅批准 `Dev/` 实验 | 需 `LV_ShadowLab` A/B 证据；正式采用待确认 |
| ADR-005 | 幕布承影层 | Proposed | 稳定承影层 + 可选薄透明视觉叠层 | 仅批准 `Dev/` 实验 | 需 UE 5.8 实测；正式采用待确认 |
| ADR-006 | 判定采样频率 | Accepted | 15 Hz 作为竞赛版本统一逻辑采样基线 | 2026-10-02 已确认 | 10/15/20 Hz 纯逻辑测试均通过；Holding 使用真实世界时间累计，15 Hz 只影响反馈延迟而不改变成功时长；用户完成 PIE 操作检查后明确确认 15 Hz |
| ADR-007 | 三幕共用谜题管线 | Accepted | Data Asset + Evaluator + Director | 2026-10-01 已确认 | 禁止三套独立 Blueprint |
| ADR-008 | 演出完成协议 | Accepted | Token 回调 + 超时降级 | 2026-10-01 已确认 | 防止重复和卡死 |
| ADR-009 | 整局复位方式 | Proposed | 重载与原地重建实测后决定 | 仅批准 `Dev/` 实验 | 正式方案待确认 |
| ADR-010 | 玩家输入与控制切换 | Accepted | PC 键鼠基线采用 `E` 进入/退出、`A/D` 操纵当前对象、`R` 情境复位 | 2026-10-02 已确认 | 用户完成 PIE 检查并确认键鼠映射无问题；底层仍使用语义 Action 与互斥 Context，未来如增加手柄只新增映射，不改谜题与可控对象逻辑 |
| ADR-011 | Level Blueprint 核心逻辑禁入 | Accepted | 不保存流程事实、不复制判定 | 2026-10-01 已确认 | 作为正式架构硬边界 |
| ADR-012 | UE 工程启动内容 | Accepted | 建立最小 C++ 第三人称技术骨架，不导入完整官方模板变体与共享大包 | 2026-10-01 已确认并执行 | Editor/Game 编译、4 项 C++ Automation、资产验证和 PIE 均已有证据 |
| ADR-013 | 玩家中文反馈与 Dev 诊断分离 | **Accepted** | 采用方案 B：薄 C++ 绑定适配器 + UMG 中文视图；公共玩家提示与 Dev 诊断分离，首轮仅在 Dev/M2 验证并使用许可清晰的免费官方字体 | 2026-10-03 用户明确“采用方案B且允许” | 已实现并技术验收（30 Success / 0 Failed，新增 5 项）；用户随后确认「中文 UI 正常」及 P02 11 项逐项正常。方案见 [`M2_UI_IMPLEMENTATION_PLAN.md`](M2_UI_IMPLEMENTATION_PLAN.md)，签收见 `M2_VALIDATION.md` §0.11；不表示完整 M2/竞赛版本完成 |

## 2026-10-01 用户确认记录

用户确认接受以下基础架构：

- 显式 `ADYPuzzleDirector`；
- 设备无关控制意图；
- 刚性分片 Skeletal Mesh 皮影结构；
- 三幕共用 Data Asset + Evaluator + Director；
- Token 化表现桥；
- Level Blueprint 不承担核心流程和判定。

用户同时授权只在 `Content/DengYingShanHai/Dev/` 中实验：

- 视觉 Mesh 与独立 Shadow Caster 的阴影对比；
- 稳定承影层与薄透明幕布叠层；
- 谜题判定采样频率；
- 关卡重载与原地状态重建两种复位方式。

该授权不等于批准任何实验结论。实验完成后必须提交画面、性能、稳定性、操作手感和回退成本，再由用户确认正式方案。实验资产不得被正式地图引用，正式结论确认前不得迁出 `Dev/`。

## 决策模板

```markdown
### ADR-XXX：标题

- 状态：Proposed / Accepted / Rejected / Superseded
- 提出日期：YYYY-MM-DD
- 确认日期：YYYY-MM-DD 或待确认
- 背景：
- 不确定信息：
- 方案 A：
- 方案 B：
- 推荐及证据：
- 用户决定：
- 影响文件/资产：
- 验收方法：
- 回退方式：
```

## 已确认的项目级约束

### ADR-P001：零付费资产

- 状态：Accepted
- 确认日期：2026-10-01
- 决定：项目只使用团队自制或许可清晰的免费/开源资产，不采购任何资产、插件、代码或生成服务。
- 影响：资产搜集、场景质量策略、许可登记与技术选型。
- 依据：`Docs/FREE_ASSET_POLICY.md`。
- 回退：无付费回退；质量不足时缩减可见范围、统一材质、重组模块、调整镜头和演出。

### ADR-P002：架构与权衡确认原则

- 状态：Accepted
- 确认日期：2026-10-01
- 决定：永远不要以牺牲架构设计为代价追求功能；永远不要基于猜测进行权衡，必须与用户确认。
- 影响：所有功能、性能、输入、表现、许可和范围决策。
- 回退：若已发生未确认实现，停止扩展，隔离改动，列出影响与回退方案，等待用户决定。

### ADR-P003：允许删除已审计确认无用的旧版文件

- 状态：Accepted
- 确认日期：2026-10-01
- 决定：允许删除旧版且后续不会使用的文件，但删除前必须核对引用、迁移仍有效的唯一内容并明确精确目标。
- 本次目标：删除已由 `ARCHITECTURE_DESIGN.md` 与 ADR 完整取代的 `Docs/ARCHITECTURE.md`。
- 恢复说明：当前仓库尚无首次提交，文件删除后不能通过 Git 恢复；历史决定保留在本 ADR 和对话记录中。

## 已确认：ADR-012 工程启动内容

### 已验证事实

- 当前仓库已有 `DengYingShanHai.uproject`、单一 Runtime 模块、最小 C++ 第三人称操作载体、Enhanced Input 资产和 `Dev/Interaction/LV_InteractionLab`。
- `Docs/ENVIRONMENT_SETUP.md` 已确定项目名 `DengYingShanHai`、UE 5.8.3、C++、Desktop、DX12、关闭硬件光追与 Starter Content，并以第三人称移动/相机为起点。
- UE 5.8 官方 `TP_ThirdPerson` 模板目录包含 583 个 `.uasset`、4 个 `.umap`，以及 Combat、Platforming、SideScrolling 三套变体源码/内容。
- 官方模板模块还声明 `AIModule`、`StateTreeModule`、`GameplayStateTreeModule`、`UMG` 和 `Slate` 等当前核心实验不需要的依赖，并在 `.uproject` 启用 StateTree/GameplayStateTree。
- 模板的基础第三人称内容本身很小，但官方共享 `Characters` 内容包包含大量战斗、枪械与非本项目动画；完整导入会扩大资产审计与 Cook 范围。

### 已执行方案

已创建 `DengYingShanHai.uproject` 和单一 Runtime 模块，保留 Third Person 所需的 `ACharacter`、Spring Arm、Camera 与 Enhanced Input 能力，但未复制变体源码、未启用 StateTree/GameplayStateTree、未导入完整共享角色包。首轮角色只使用引擎基础形体作为灰盒占位；Input Action、Mapping Context 与测试地图均位于项目命名空间和 `Dev/` 边界内。

### 影响

- 优点：依赖最小、编译和 Cook 更快、不会把战斗或横版逻辑带入比赛工程、许可与资产台账更清楚。
- 代价：不直接使用官方模板的现成 Mannequin Blueprint；正式第三人称角色模型仍需从许可清晰的免费/开源渠道导入并适配。
- 回退：若最小骨架无法满足第三人称移动验证，可在独立临时工程中生成官方模板，按 Reference Viewer 只迁移被确认需要的免费引擎模板资产，而不是整包复制。

### 确认证据与边界

- 用户于 2026-10-01 明确要求执行第一阶段，并在复查整改方案后回复“按你的思路来”；
- `DengYingShanHaiEditor` 与 `DengYingShanHai` Development Target 可编译；
- Phase 1 C++ Automation 4/4 通过，`Project.Maps.PIE` 1/1 通过；
- Python 独立验证从保存后的资产中确认精确 W/S/A/D、Mouse2D、R 映射及镜头装配；
- `PythonScriptPlugin` 仅以 Editor TargetAllowList 保留，用于可重复生成和验收，不成为 Game runtime 依赖；
- 该决定只确认技术骨架，不预先确认最终角色资产、最终玩家按键、整局复位或阴影/幕布实验结论。

## 已确认：ADR-013 玩家中文反馈与 Dev 诊断分离

> 当前实现附注（2026-10-03，既有 ADR-008 的部分落地，不新增架构决定）：用户在 P02 签收后选择真实投影树形灰盒；Director 已实现成功真实控制快照及不透明 FGuid 身份核验，原成功事件签名不变。最新 34 项项目测试、三目标编译与既有 UI/地图冷读通过。完整 Token 化演出回调消费/超时、FinaleLocked、成林与三幕顺序仍未实现，不把 ADR Accepted 当作全部接口完成。见 `P03_DEV_IMPLEMENTATION_PLAN.md` 与 `Saved/Audit-2026-10-03-P03Foundation/Supervisor-Results.md`。

- 状态：**Accepted**
- 提出日期：2026-10-03
- 确认日期：**2026-10-03**（用户明确答复“采用方案B且允许”）
- 背景：
  - Dev/M2 布局修复后，用户于 2026-10-03 给出**有限签收**「看清了，操作正常」，
    仅覆盖主观可读性与操作手感，不等于 `M2_VALIDATION.md` §5 的 11 项逐项人工检查通过；
  - 现有玩家提示为 `ADYDevInteractionHUD` 的 `AHUD` Canvas 英文 ASCII 占位，
    字体未验证中文字形，且该类在 Shipping 下默认 GameMode 并不挂载；
  - `FDYStageFeedbackDisplayChangedSignature` 是**原生** `DECLARE_MULTICAST_DELEGATE`，
    不是 `BlueprintAssignable`，不能臆造蓝图直接绑定节点；
  - **（提案时事实）** 提案撰写时模块 `DengYingShanHai.Build.cs` 无 UMG/Slate 依赖，
    接入属新依赖。**当前实际状态见下方「影响依赖」**。

- 不确定信息（提案时事实，**实施前尚未验证**）：
  - 具体像素、字体大小、DPI 曲线与淡入时长尚未由实拍决定；
  - 是否接入第二字体（思源宋体）不预先扩项；
  - OTF 在本机 UE 5.8 的导入与 Cook 字形可用性当时未验证。

- 方案 A：仅替换 Dev Canvas 文本并导入许可清晰的免费中文字体。
  - 优点：变更较少，可快速验证中文字符；
  - 代价：仍非 Shipping 可用的正式 UI，后续需继续迁移；Canvas 排版与美术编辑能力有限。

- 方案 B（**用户已确认采用**）：薄 C++ 绑定适配器 + UMG 中文视图；
  将**公共玩家提示**与**Dev 诊断**分离。
  - 玩家侧离散提示（Hidden/Adjust/Near/Holding/Interrupted/Complete）可面向 Shipping；
  - 开发参数、目标球与射线**仍需** `!Shipping` **且** `-DYDebug`（此为**诊断输出**门控，
    与下方两个读取口的门控不同，勿混为一谈）；不整体放开 Dev 开关；
  - Presentation 仍是离散状态、恢复基线与唯一 Interrupted 计时器的唯一所有者，
    不在 Widget 或新蓝图里复制保持/打断判定；
  - Widget 不得重跑射线或重判可操纵条件，不给 Target、Tolerance、Current、精确 Progress；
  - 不引入 CommonUI、MVVM、全局事件总线、UI 路由 Subsystem 或新存档系统。

- 用户决定：**采用方案 B，并允许实施。** 首轮范围为薄 C++ 适配器 + UMG，
  公共玩家提示与 Dev 诊断分开，仅在现有 Dev/M2 验证，使用许可清晰的免费官方字体。
  逐文件白名单与禁止项见 `Saved/Audit-2026-10-03-M2UI/Execution-Contract.md`。

- 影响依赖（**按 Build.cs 只读核实**）：
  - 实际新增公共依赖 **`UMG`**、私有依赖 **`SlateCore`**；没有加入 `Slate`；
  - 原工程 `Source/DengYingShanHai/DengYingShanHai.Build.cs` 与隔离打包副本的同名文件均含上述依赖及 `RuntimeDependencies` 许可 NonUFS 分发规则；不是只改副本；
  - Codex 最终逐文件核验两者 SHA256 相同：`F4157A71C3C4FA5B4EE39B3C1BBB2B0A7893DD4418B5DD1C90C676BF034B8978`。备份中的旧 Build.cs 不代表当前源码；
  - 不启用额外插件。
- 影响文件（按执行合同白名单）：
  `Source/.../Stage/DYStagePresentation.h/.cpp`、`Core/DYStageGameMode.h/.cpp`、
  `Stage/DYStageFeedbackTypes.h`（注释更新，不改枚举值）；
  新增 `Public|Private/UI/DYInteractionHUD.h/.cpp`、`DYInteractionHUDWidget.h/.cpp`；
  `Tests/DYFeedbackAutomationTests.cpp` 更新已获准的玩家提示契约并新增 UI 测试；
  新增 `Scripts/Configure-M2UI.py`、`Verify-M2UI.py`；
  `Content/DengYingShanHai/Dev/M2/UI` 放置原型 HUD/GameMode/Widget 配置与简体中文字体。
  **禁止修改**：导演/Evaluator、交互输入与聚焦逻辑、镜头、灯光、15 Hz、谜题参数、
  M1、全局 Config、旧 HUD、共享 Stage 蓝图。
- 回退：退出本步启动的 UE 进程，从 `Backup` 按**明确单文件**恢复已修改文件与 M2 地图；
  新增原型保留隔离但不挂载；**绝不清理或重置用户工作树**；旧 Dev HUD 保留。
- 字体：使用 Adobe 官方未修改单常规字重，许可原文随发布分发；
  实施时才记录文件名、版本、下载日期、SHA256 与发布位置。
- 当前状态：**用户决定 Accepted；本小步已实现，Codex 技术验收完成，用户已确认「中文 UI 正常」。P02 11 项人工检查亦获用户后续明确签收。**
  - 项目自动化：**30 Success / 0 Failed**（实施前为 25）；**新增 5 项测试**
    （文案、绑定、非 Dev 真实计时器、EndPlay 清理等），**未删除旧测试**；
  - UI 冷读 **20 PASS**；M2 原玩法／保存约束冷读 **35 PASS**（均 0 error / 0 warning）；
  - Editor / Game Development / Game Shipping **三目标编译 Succeeded**；
  - M2 Development 与 Shipping **完整 Cook / Stage / Package 技术包**均 BUILD SUCCESSFUL；
  - 真实 RHI 键鼠闭环：Shipping 独立包、Development 独立包（1920×1080）与 Editor PIE 均已验证。
- **保留风险（未测，不得写成已通过）**：
  - 同一真实 GUI 会话二次配置已实测：均零产品文件哈希变化，每次 20 UI + 35 M2 PASS。见 `Saved/Audit-2026-10-03-M2Closure/Supervisor-Results.md`；**跨版本/其他机器的幂等性未测**；
  - **其他机器兼容未测**；
  - **完整三轮竞赛流程未测**；
  - 既有引擎 smoke-test 本地化 Error、MSVC 版本建议与 RHI `TSR 16-bit VALU` 警告均保留，
    **不声称整份运行日志零警告**；项目 30 项 Success 不等于整份日志零错误。
- **本 ADR 不表示 M2 三互动里程碑完成**：P02 与 UI 已签收，但正式美术、最终主地图、音效、P03 和完整流程仍未完成；第三幕已进入准备/源码审查，尚未实施。第三幕具体数值和演出取舍仍须确认。
