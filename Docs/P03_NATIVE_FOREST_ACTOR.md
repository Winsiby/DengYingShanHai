# P03 原生成林表现 Actor（Dev 资源层）

日期：2026-10-04
状态：Dev 成林表现 Actor 与隔离包验证已完成。本步只完成表现资源层与独立 Dev 入口，不是正式第三幕演出。

责任人：Codex 实施与验收；独立只读审查负责复查；WorkBuddy 只整理本文档。
依据：本轮脱敏任务事实（`Saved/Audit-2026-10-04-P03NativeActor/WorkBuddy-Docs-Request.md`）与 Codex 最终复核。WorkBuddy 未读取原始 UE 日志、自动化报告的设备/账号/遥测字段，未读取密钥或设置文件。

> 永远不要以牺牲架构设计为代价追求功能；永远不要基于猜测进行权衡——必须与我确认。

工程已迁移：物理根 `D:\灯影山海`，英文 junction `C:\UEProjects\DengYingShanHai` 指向同一目录。旧 C 工作区仅保留兼容目录与根文件副本。给用户的启动地址一律使用 D 盘。

---

## 1. 本步定位

用户前次对连续 Dev 预览的反馈「勉强达到效果」保留为：旧预览因果可读、视觉仍需提升。本轮自动化与包验证不能替代用户对新画面的确认。

本轮从「只有纯几何库」推进到「原生表现 Actor 可运行」，但仍是 Dev 资源层：不含正式演出、正式美术、正式时长或 P03 目标参数。

`Docs/P03_NATIVE_FOREST_GEOMETRY.md` 保留为历史步报告，其中「当步未接入」的事实不被本轮覆盖。

## 2. ADYForestPresentationActor 职责

只管理枝形 StaticMeshComponents、冻结 authoring 内容、归一化进度与清理。

不具备的能力（均未实现）：

- 无 Tick、无 timer
- 无世界扫描、无 Director 读取、无输入
- 无谜题评分、无演出秒数、无完成游戏权力
- 不硬编码美术默认资源

## 3. 资源与变换规则

mesh/material/layout 全部由外部作者配置。运行会话使用内容副本与真实 mesh bounds。

- mesh 局部 Z 为生长轴
- 库输出的是组件 world transform，不重复乘 Actor 变换
- Movable、NoCollision
- visible 时 cast shadow
- 失败与清理：先隐藏关投影，再 DestroyComponent

## 4. API 与调用顺序

Actor 侧 Begin / Apply / Clear 为私有，`friend ADYStagePresentation` 才能调用，绑定 weak owner 与 token。

Presentation 新增三个公开接口与一个显式可空引用 `ForestPresentationActor`：

```text
BeginForestPresentation(Token)
  → SetForestNormalizedGrowth(Token, p)
  → ClearForestPresentation(Token)
```

Begin / Set 的接受条件：必须真实 Resolve、真实 A 接触、当前同一 token。先由当前 Resolve 的控制状态继续落杖，经 `TryAcceptStaffContact` 接受实际 A 的接触，再读取已接受接触与当前 token，才能 Begin；不能把纯几何样本或任意 Guid 当作授权。

Clear 则只按 Presentation 已拥有会话的有效 token 清理，不要求重新满足接触或 Resolve 条件；失效通知与拆卸也必须能够释放资源。清理权限不等于成功或完成游戏权限。

Begin 与 Set 会再次捕获实际灯、Staff、幕布、地线几何；几何变化时拒绝，更新失败清除旧树，且不撤销谜题成功。

对外行为：活动期间重复 Begin、外来 owner/token、跨 World 一律只拒绝，不抹掉当前会话。

## 5. 授权边界

几何库中的 Guid 只是诊断值，不是授权。数学 Valid 不是阴影像素、遮挡、半影、美术或 FPS 证明。

Clear 后若仍是真实当前接触，可以显式重建 Dev 资源。这不是正式 Skip、R、RestartExperience 或 FinishFinale 的决定。

## 6. Director 新增通知

新增 native resolved-invalidation 通知，规则如下：

- 先清事实，再通知旧 token
- serial 防重入覆盖；EndPlay 禁止复活
- Reset 的两处控制复位在广播后再查 serial
- Presentation 只清与旧 token 匹配的会话；延迟的旧通知不能抹掉新的 Resolve

## 7. 事件与清理

三类测试都先证明可见与投影存在，再证明清理，避免真空通过：

- Dev 预览正常完成：Python 预览负责调用清理、恢复完整 Staff 变换并检查旧 token 被拒绝；Actor 只释放自身枝形资源，不负责 Staff 复位或宣布游戏完成
- 无效激活：仍执行清理
- Actor / Presentation / Director 拆卸：完整清理

临时原生 Actor 与地线只在独立 Editor/PIE 内生成，不保存地图、BP 或资产。

## 8. 独立 Dev 入口

新入口：`D:\灯影山海\Start-M3NativeForest.cmd`，在文件资源管理器双击，不在 Codex 点开读代码。

使用前先关闭 UE，不要操作鼠标键盘。自动结束。

默认 2s 落杖 / 6s 生长 / 6s 留帧，仅为临时比较值，可从新的 PowerShell 参数调整。正式时长未定。

预览脚本 `Scripts/Preview-P03NativeForest.py` 派生旧连续预览但替换枝段管理，复用真实 P02 Resolve 夹具、实际 Staff A、已确认 Z70 地线、15 枝 16 节点、旧主灯/曝光/POV/保护区。

流程是 contact → Presentation 授权 → C++ 应用 normalized。Python 不直接变换 branch 网格。15 个枝形的实体根是实际后台 A，不是幕面接触点。

新 launcher 只允许 D 根或英文 alias，拒绝已有 UE 与已有证据覆盖；使用新的 output env，清理并恢复旧 env，避免导入父脚本时把旧 audit 守卫绕过。

旧 C 根的老 continuous launcher 可能报 junction workspace mismatch，本轮未改它。

## 9. 成功测试

| 项 | 结果 |
|---|---|
| Editor 自动化最终 | 68 Success / 0 Failed / 0 NotRun（58 旧 + 10 新 ForestPresentation） |
| 三目标实编 | Editor Development、Game Development、Game Shipping 均 Succeeded、exit 0 |
| Run1 实际渲染预览 | 4/12/20 秒（临时），Completed |
| Run1 接触 | 单次 contact、重复拒绝、15 枝 |
| Run1 回调 | drop 240 + growth 721 = 961 motion callbacks |
| Run1 检查 | 31339 次实际组件检查 |
| Run1 清理 | 全部释放、Staff 恢复、旧 token 拒绝、未 save 资产 |
| 隔离 DevelopmentPackage | Cook 根明确 `/Game/DengYingShanHai/Dev/M3/Maps/LV_M3GeometryProbe`，非 cookall、不覆盖旧包；BuildCookRun exit 0，Cook/Stage/Pak/IoStore/Archive 成功 |
| 脱离 Editor/Python 启动包 exe | `-NullRHI` 执行 ForestPresentation，10 Success / 0 Failed / 0 NotRun，exit 0 |

包测试证明的是：包内的原生资源、几何、授权与生命周期代码，以及 cooked Cube/Cylinder 可以执行。无图形渲染，不证明包中连续成林镜头。

既有 `LV_M3GeometryProbe` 地图文件存在且未修改；新 Actor、地线及成林接线只在未保存的 Editor/PIE 夹具中生成，未写入该地图。包内没有已接线的正式 P03 演出，双击包 exe 不会自动播放新成林预览。该包不交付为正式游戏入口，用户应打开新 cmd 看 Editor 预览。

首尾 Engine HighResShot：`Saved\Audit-2026-10-04-P03NativeActor\Run1\01-Start.png` 与 `02-ForestComplete.png`，1600x900，无 UI 叠层。

回调频率未被冒充为 FPS。

## 10. 失败测试

首编出现参数 Owner 遮蔽 `AActor::Owner` 的 C4458，改名 `PresentationOwner` 后解决。失败日志保留，不说一次成功。

首轮 Editor 自动化为 67 Success / 0 Failed；补场景守卫与真可见前置断言后为 68 Success / 0 Failed / 0 NotRun。

原始日志存在既有错误、警告，以及新 InvalidActivation 测试的预期错误。测试通过不等于原始日志零错误。

新增 10 项测试（`DengYingShanHai.P03.ForestPresentation`）：

| 测试名 | 覆盖 |
|---|---|
| AuthorizationAndContact | 授权与接触条件 |
| ActualMeshWorldTransforms | 实际 mesh world transform |
| InvalidSamplesClearAllResources | 无效样本清除全部资源 |
| ResetAndOldTokenIsolation | Reset 与旧 token 隔离 |
| InvalidActivationStillClears | 无效激活仍清理 |
| ActorPresentationDirectorTeardown | 三者拆卸 |
| SharedActorCannotBeHijacked | 共享 Actor 不可被劫持 |
| InvalidationReentryPreservesNewSession | 重入通知保留新会话 |
| InvalidationDestroyCannotResurrect | 销毁后不可复活 |
| CurrentSceneMustMatchAcceptedContact | 当前场景必须匹配已接受接触 |

最后一项分别移动实际灯、幕、地线、Staff 后拒绝更新与重建，并清除旧枝。

## 11. 画面评价

Codex 已查看林影终帧。细直枝、灰盒舞台、环境与形象仍有廉价感。

未签正式美术、文化或用户视觉验收。

## 12. 证据路径

- 审计目录：`D:\灯影山海\Saved\Audit-2026-10-04-P03NativeActor\`
- 原文备份：`Saved\Audit-2026-10-04-P03NativeActor\Before\Docs\P03_DEV_IMPLEMENTATION_PLAN.md`
- 原图：`Run1\01-Start.png`、`Run1\02-ForestComplete.png`
- 最终隔离包：本 audit 目录下的 `DevelopmentPackage-Verified`；完整打包输出 `Package-UAT-Verified.log`，包测试 `Packaged-Verified-Report/index.json` 与 `Packaged-Verified-Automation.log`
- 历史几何步：`Docs\P03_NATIVE_FOREST_GEOMETRY.md`

细分计数与最终范围哈希由 Codex 终审，本文不编造。

## 13. 协作约定

WorkBuddy 输入框存在限制。后续交接只发送短摘要与本地任务路径。具体上限未测。

## 14. 本轮范围

4 个原源码改动 + 3 个新源码；新 py / ps1 / cmd 三入口；新文档 1 份 + 计划追加 1 处，合计 12 个产品文件。

零 `.uasset` / `.umap`、零 Config、零旧脚本或启动器修改。无 Git 写、commit、删除，无付费或新资产下载。

实编正常更新本机 `Binaries/Intermediate/Saved` 和缓存。Cook 还自动更新了两份未跟踪生成日志 `Build/Windows/FileOpenOrder/CookerOpenOrder.log` 与 `EditorOpenOrder.log`，与上述 12 个产品文件分开登记；不宣称整个 Build 目录未变，不为恢复日志而覆盖既有用户状态。

Engine 免费灰盒沿用既有许可登记，不把引擎内容叫开源。

## 15. 回退

回退时先恢复 `Before/` 中 4 个旧源码，再经用户确认移出新增的 3 个源码和 3 个入口，重新编译。本机二进制已经随实编更新，不能只删新源码就宣称二进制已回退。旧隔离包和旧预览历史证据未被覆盖。文档追加有原文备份可整文件恢复，WorkBuddy 初稿另存于 `WorkBuddy-Output/`。本轮没有实际执行回退、删除、reset 或 checkout 脏工作树。

## 16. 未完成与下一步

仍待逐项按 Q1–Q5 确认：正式 P03 target / tolerance / hold、落杖与成林秒数及超时、Skip / R / 全局重启。

仍待后续：免费合规美术与剧场质感、声音、完整三幕、5–8 分钟体验、性能、人工 PIE 与现场包视觉验收。

本步只完成表现 Actor 资源层与独立 Dev 入口。未新增或保存 Blueprint 子类，但接口已可供 BP 调用，且已由真实 Python 反射验证。不自行开启下一功能。

不得宣称 Blueprint 资产已保存、正式演出已完成、包的渲染已验收，或时长与目标已确认。本消息不是第三幕目标参数授权。

## 17. 状态

部分完成。原生表现 Actor、独立 Dev 入口、隔离包编译与 NullRHI 执行验证已完成。本步不交付正式演出、正式美术、正式时长或 P03 目标参数。本文不构成参赛作品或用户验收结论，未代签任何人工确认。

AI 记录：Codex 实施，独立只读审查，WorkBuddy 文档整理。不声称已完成赛事 AI 申报。

## 18. Codex 最终复核补记

- 第二个独立 `DevelopmentPackage-Verified` 已实际完成 Cook/Stage/Pak/IoStore/Archive，exit 0，并以 Tee 保存完整打包输出；其 exe 与当前 Development exe 的 SHA-256 一致。该包脱离 Editor/Python、使用 `-NullRHI` 再次执行 10 项 ForestPresentation 测试：10 Success / 0 Failed / 0 NotRun，exit 0。这仍不是包画面验收。
- 真实根 `.cmd → Windows PowerShell 5.1` 链路已通过 Run3；修正无 BOM 中文路径字面量在 PS5 中误读的问题，改为 ASCII 字符码构造 D 根，未更改执行策略。Run3 临时 4/12/30 秒，458 个 motion callbacks，31259 次重复组件一致性检查；Computer Use 已观察前台 UE 的林影终帧，未代替用户验收。
- Run2 非前台稀疏回调下，50 个 motion callbacks、3031 次重复检查仍到达正确端点并清理。这仅支持按 elapsed 推进的鲁棒性，不支持 FPS 或正式演出节奏结论。
- 284 字符短提示已成功发送到 WorkBuddy，详细内容留在本地 `.md` 文件。此长度是一次成功样本，不是输入框最大上限。
- 最终核查通过：5 个既有产品文件修改、7 个新增产品文件，另有 2 个 Cook 生成日志变化；177 个其余基线文件哈希不变，无删除。计划原有 52354 字节完整前缀保持；HEAD 不变、暂存区为空，原 79 项脏状态均保留，当前 86 项（多出 7 个新增产品文件）。详细哈希与报告统计记录在本 audit 的 `FinalEvidence.json`，可由 `Verify-Final.ps1` 复核。
