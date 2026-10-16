# 第三幕 Dev：向可打包运行时迁移

更新：2026-10-06。负责人：Codex，负责 C++、Blueprint 集成、验收与本步文档。队友负责后续免费合规正式美术与视频；WorkBuddy 本轮未收发任务，短摘要加本地文件的输入限制约定保留。

## 当前结论

**已保存真正的运行时 Blueprint、独立 Dev 地图，并生成 Windows Development 包；不再依赖 Editor Python 驱动落杖与成林。但默认图形路径尚未通过稳定性验收，不能按竞赛成品或稳定交付入口发布。**

候选规则不变：灯 .72、偶 .85、进入 .05 / 退出 .09、保持 1.25 秒、Reach、15 Hz、暂用落杖 2 秒 / 生长 6 秒。仍是已批准的 Dev 候选，不定稿正式 Q1–Q5、输入锁、Skip/R 改义、整局重启、环境结束态或三幕队列。没有新增按键、POV、场景、美术、声音、付费资源或插件。

“以灯为日、以影为夸父”的因果链保持：本次成功姿态 → 实际 Staff A 的幕上投影接触原 Z70 地线 → 原接触点展开真实枝网格 → 同一 Movable 主灯投出林影。没有成功后瞬移、黑屏换构图或独立树林片段。

## 本轮实际架构与接线

| 层 | 本轮结果 | 权限边界 |
|---|---|---|
| Director | 沿用原生参数判定、15 Hz 保持和 Resolve 身份 | 不管理动画时间或林枝 |
| Stage Presentation | 新只读 `GetForestPresentationActor`；新增携带真实旧 Token 的 `ReceiveStaffPresentationInvalidated` BP hook | getter 不寻找/生成资源；hook 不是新的失效授权 |
| StaffDropLibrary | 读取冻结成功快照，纯数学输出 Staff 位移 | 只移动表现位置；不核验当前授权、不接触判定、不决定秒数 |
| 新 ForestPreflightLibrary | 纯值完整最终 15 枝 bounds、Torso/Head 共 16 角投影、幕尺寸 2% padding 检查 | Valid 不是当前 Token 授权；失败无部分有效 payload |
| 新 RuntimePresentation BP | 保存两个无自动播放 Timeline，使用实际 world time；处理一次身份、落杖、接触、预检、生长与局部清理 | 不写 Definition、输入、核心评分、灯/偶根变换或 POV |
| 原 Forest Actor | 经原生 Stage 授权创建/更新/清理真实可投影枝网格 | 不是 Finale、ForestComplete 环境或游戏结束 |
| 新 Cue Widget | `OnPaint` 只绘制存储的中文文案；使用现有 OFL 字体 | 无 Tick 扫描、输入、评分、计时或事实回写 |

Drop 的每个应用先核验当前身份与冻结场景。Finished 调用真实 `TryAcceptStaffContact`，同步回调后再读接触/当前身份，才 BeginForest。Begin 的 p0 隐藏资源不能代替完整最终预检；完整预检成功后才播放 Growth。Completed 明确应用 p1 并保持真实林影，不调用 FinishFinale。

相同 Resolve 的迟到同步不重启 Timeline；旧失效 Token 不清理新会话。Release 先撤本地所有权、停两张表、清所属资源，最后只恢复 owner-relative Staff 平移，不恢复完整旧姿态。Stage EndPlay 有清理接线；独立运行测试已覆盖 Drop/Growth/Completed 的 Reset 和完成态 Director EndPlay，**未单独证明每个活动阶段的 Stage/World EndPlay**。

新地图绑定的 DevReceiver/DevGround 与原生 Screen/Ground 配置已冷启动验证为同一对象；没有通过世界扫描选择对象。作者脚本只用公开反射 API，明确保存白名单；运行包不需要 Python。

## 本轮验证与必须保留的失败

- Editor 自动化接线集合 **87 Success / 0 Failed**：原 78 项，加 8 项纯 ForestPreflight 和 1 项 Stage 只读边界。后续新增隔离组件诊断后，最新 `EditorTests-MicroSetter` 为 **88 Success / 0 Failed / 0 Warnings / 0 NotRun / 0 InProcess**。这些是 EditorContext，不冒充包内 88 项，隔离候选成功也不代表真实 Forest 已修复。
- Editor Development、Game Development、Game Shipping 均实编成功。初次 Game 编译因测试调用 Editor-only metadata 失败，已用 `WITH_EDITOR` 修复并保留失败日志；新增测试采用 `-NoUBTMakefiles` 确认重新枚举，不能用一次错误的 Up-to-date 作证。
- 保存图的冷审查与自然 PIE：Run2 检查 9 个阶段通过；追加全部可见/Portion=1 与实际变换数值后，Run3 检查 10 个阶段通过，15 枝均完全展开。Python 只提供诊断输入，没有推进时间线或写 Staff。不是实际键鼠验收。
- UAT Package Run1：Cook 成功，Stage 因 CookOutputDir 缺 `Windows` 末级失败。Run2 修正目录后，Zen 的 IPv6 本机健康请求被代理返回 502。Run3/4 仅对子进程增加 localhost NO_PROXY、finally 恢复，Cook/Stage/Pak/IoStore/Package/Archive 成功；未改全局代理、引擎或 Config。
- 包 Run3 的 NullRHI：**12/0**。新增 live-map 测试覆盖真实 Timeline、三阶段复位、旧回调隔离与 Director 退出；尚未补强全部可见/Portion=1 的独立断言。
- 包 Run4 的严格 NullRHI：**11 Success / 1 Failed**，失败为实际组件与原生最终样本的组合断言不成立。旧包日志没有分枝原始值，**当时不能区分变换、可见性或投影标记**。阈值保持 `UE_DOUBLE_SMALL_NUMBER`，没有放宽或删断言。后续成功 PIE 的 15 枝平移/缩放差为 0、四元数差约 1e-16 至 3e-12；成功值不解释旧失败。增强日志后的实际复现见下一小节，不能把新诊断版本当作 Run4 包。
- 默认 D3D12：Graphics Run1/Run3 首帧 `DXGI_ERROR_DEVICE_HUNG`；Run2 单次完整流程通过。Run3 崩溃在延时截图/测试执行前，排除了“仅开场 Shot 导致”这一过早归因。不能以一次通过抵销两次 GPU 崩溃。
- Graphics Run4 `-d3ddebug`：实际完整成林、截图取得，但报告 **11/1**；失败为两条截图 BackBuffer ResourceBarrier 调试错误。不能把进程退出码 0 当测试通过。
- Graphics Run5 仅 `-norhithread`：D3D12 包内 **12/0**。Graphics Run6 保留正常线程，仅 `r.Shadow.Virtual.OnePassProjection=0`：D3D12 包内 **12/0**，正常起点/成林含 UI 截图取得。二者均为隔离诊断，**未获用户批准前，不自动成为默认或正式渲染方案**。

照明诊断沿用既有固定曝光、灯具参数与 D3D12/SM6 基线；没有通过降亮度、关闭真实阴影、换 DX11、修改 TDR/注册表或驱动来隐藏故障。现有日志指向 VSM 投影步骤，属于进一步定位依据，**不是已经证明驱动/引擎某处唯一根因**。Epic 的诊断说明也要求从 GPU breadcrumbs 等证据定位，CPU 栈不能直接给出 GPU 根因：[UE 5.8 GPU Crash 指南](https://dev.epicgames.com/documentation/unreal-engine/dealing-with-a-gpu-crash-when-using-unreal-engine?application_version=5.8)。

仍保留：8 个新注释节点的 NodeGuid Cook 警告、既有初始化 Automation 错误、独立包缺 HTML 报告模板（JSON 仍生成）、MSVC 高于 preferred、旧 NVIDIA 驱动的 TSR 警告。没有声称整份日志零错误或零警告。

### 严格终态问题的最新复现与隔离验证

- `PrecisionProbe-Run1` 为 Editor 二进制 `-game / -NullRHI` 的 **1/0**；其成功没有解释旧包失败。
- 同一实际 RuntimeCandidate 中的 `PrecisionProbe-Run2` 为 **0/1**：第 0 枝 actual visible=1、CastShadow=1、Portion=1，平移只在 Z 轴落后 `6.4902002264943803e-5 cm`；缩放差为 0，四元数差约 1e-16。**此次真实复现已确定是平移，而不是可见性或投影开关。**
- 增强只读尾段观测后，`PrecisionProbe-Run3` 再次 **0/1**，第二次最终保持（Phase 4）的第 0 枝 Z 残差为 `1.6279472532687578e-5 cm`。最后一次诊断观测 Frame 64062 与最终 Frame 64063 的实际 Z 均为 `128.40125737669067`，样本目标均为 `128.4012736561632`；目标位置/旋转都落在 UE 默认 `1e-4` 近似区间。该观测不是紧邻 Setter 的调用边界，不冒称捕获了其立即前后。
- 本机 UE 5.8.3 `SceneComponent.cpp` 的 `InternalSetWorldLocationAndRotation` 用默认 `1e-4` 比较位置和 Euler 旋转，二者近似相等时不赋新位置。它与上述实际保留值高度吻合；不是纯数学计算输出错误，也不能据此断言旧 Run4 的唯一原因已被逐次采样证明。
- 新 **Editor-only** `EngineMicroTransformObservation` 创建独立 transient world 和真实已注册 Movable、absolute、无碰撞、不模拟物理的组件，没有操作真实 Forest 或 Timeline。分别保持/改变缩放时，普通 `SetWorldTransform` 都保留 `5e-5 cm` 的小位移；公开 `SetWorldLocationAndRotationNoPhysics` 则使误差归零，并通过原 `1e-8` **全变换**检查。正常较大位移仍通过普通 Setter。这个测试通过只证明引擎行为和候选 API，**不是产品修复**。
- NoPhysics 是公开正常场景更新接口；它由引擎内部赋 relative 值并走 `UpdateComponentToWorld(SkipPhysicsUpdate)`、bounds/渲染变换通知，不是项目直接写内部缓存或用抖动强刷。当前林枝没有物理需求，因此是最小修复候选；任意物理组件不自动适用，四元数转换仍须实际全 15 枝严格验收。
- 新测试失败后立即停止，不再同帧 Reset/Destroy；保留失败原值。新增被动观测只读组件/样本，不推进 Timeline。诊断版本标记为 `20261006-MicroSetterProbe`。Editor Development / Game Development / Game Shipping 三目标实编成功，**最新增强代码尚未进入 Run4 包**。
- 已向用户请求：额外允许修改旧 `DYForestPresentationActor.cpp`，仅为这些无碰撞表现枝采用候选公开更新接口；**未收到确认前不修改该文件**。数学、接触、原 `1e-8`、会话授权、缩放、布局、15 Hz、落杖/生长时间和旧资产全部不变。即使获准，也必须复测实际 Forest、重置/重演/拆卸，并生成另一个隔离包，不能直接宣称已解决。

## 当前位置与下一步门槛

- 新地图：`D:\灯影山海\Content\DengYingShanHai\Dev\M3\Maps\LV_M3RuntimeCandidate.umap`；6 个新资产在同级 `Runtime/` 目录。
- 独立包：`D:\灯影山海\Builds\M3Runtime-20261006-Run4\Windows\`。**必须显式指定 RuntimeCandidate 地图；双击裸 exe 可能进入旧默认地图，不能以此代替新入口。** 本轮新启动器尚未作为稳定默认交付。
- 最新正常诊断画面：`D:\灯影山海\Saved\Audit-2026-10-06-P03RuntimeWiring\PackagedGraphics-Run6-Captures\UnsolvedStartup.png` 与 `CompletedHolding.png`。
- 包内报告：同审计目录 `PackagedGraphics-Run6/index.json`；严格失败报告 `PackagedTests-Final2/index.json`。完整失败日志均保留，不删除或覆盖。
- IoStore 目录已实查新地图、6 个新资产、旧 Forest/字体依赖；引擎按未改的默认配置也 Cook 了旧 `LV_InteractionLab` 与 Engine Entry。是显式新 Dev Cook 根及必要依赖，**不是仅含一张 map，更不是 CookAll**。包身份及 8 个关键文件大小/SHA256 在 `Package-Run4-Artifact.json`；最新测试的失败数值日志已编译三目标，但未再次封装进 Run4，包测试版本明确登记为 Final2。
- 现有玩家入口 `D:\灯影山海\Start-M3Candidate.cmd` 保持原样，只是旧 Editor-only 候选，不是本次新包。聊天链接可能只预览代码，应在资源管理器双击已有 CMD。

下一步由 Codex 负责，当前有两项独立确认门槛：允许旧 Forest 源码的最小精确表现更新；允许只对新 Dev 入口使用 VSM 非单遍投影候选（性能代价未测，不断言无代价）。收到对应确认后才实施、重打独立包、制作新入口并追加实键鼠、中文 UI、重进/关闭及多次图形通关检查。默认图形稳定性、全部活动 EndPlay、正式美术/声音、三幕串联、5–8 分钟和三轮目标机 Development/Shipping 全流程仍未完成。

现有 204 文件/131 dirty 基线已保留；本步旧产品只允许 Stage 两源码和两文档（Plan 仅追加），其他为新增 Dev 文件和隔离构建产物。没有 Git 写操作、删除、付费下载、旧资产覆盖或队友文件修改。回退应先确认，再按审计 Before 备份恢复这两源码/文档并移出本轮新资产、源码/脚本，重新构建；不 reset/checkout/clean 用户工作。

最终范围核验通过：**4 个旧产品修改、13 个新产品、0 旧文件缺失、0 非白名单变化**；原 Plan 82,342 字节前缀完整，217 个当前产品；131 个原 dirty 全保留，182 个当前 dirty（含两个独立包的未跟踪生成物），HEAD 不变、index 空。该范围通过不是游戏功能/图形通过，详情 `Scope-Final.json`。

---

## 以下为 2026-10-05 数学基础的历史记录

以下“未接线/未打包”等描述只对应 10 月 5 日当时状态；当前事实以上面 10 月 6 日结果为准，原始历史与证据保留。

更新：2026-10-05。负责人：Codex，负责源码、集成、测试和本步文档。队友继续负责免费合规正式美术与视频；没有增加关键路径共同负责人。

## 当前结果与范围

用户完成候选入口检测后要求“检测完毕直接开始下一步”。下一技术目标是让已确认的双变量 Dev 候选不再依赖 Editor Python 来驱动落杖、接触与生长。本步先完成其中可独立验证的 **C++ 落杖数学基础**，没有接入新的可玩地图、Blueprint 执行图或打包入口。

> 永远不要以牺牲架构设计为代价追求功能；永远不要基于猜测进行权衡——必须与我确认。

这是技术迁移，不是正式 Q1–Q5 或体验重设计。暂时不定稿正式目标/容差/保持、落杖秒数、生长秒数/超时、Skip/R、整局重启或输入锁；不改变 M2、15 Hz、相机、按键、现有地图及 15 枝 authoring BP。

文化与因果目标保持不变：“以灯为日、以影为夸父”；玩家综合运用灯与偶后，**从本次真实成功姿态继续，A 端的幕上影子接触原地线，才在同一位置因果连续地成林**。不是成功后换构图或播放独立树林片段，也不是文物/流派复原。

## 已实现的接口

源码位置：

- `D:\灯影山海\Source\DengYingShanHai\Public\Stage\DYStaffDropLibrary.h`
- `D:\灯影山海\Source\DengYingShanHai\Private\Stage\DYStaffDropLibrary.cpp`
- `D:\灯影山海\Source\DengYingShanHai\Private\Tests\DYStaffDropAutomationTests.cpp`

`UDYStaffDropLibrary::SampleStaffDrop(Resolved, NormalizedProgress)` 是运行时模块中的静态 `BlueprintPure` 函数，返回 `FDYStaffDropSample`。

| 输出 | 含义与限制 |
|---|---|
| Status | Valid 或明确失败原因；不是谜题成功/实际接触状态 |
| Token / PuzzleId | 只复制输入身份；不发行、不核验当前身份、不消费授权 |
| NormalizedProgress | 有限值截断到 0–1；NaN/Inf 拒绝，不包含秒数 |
| StaffWorldTransform | 从固定成功快照计算的组件世界变换；保持原旋转和有符号缩放，仅改变平移 |
| FullTranslationWorld | 起点到完整落点的平移量，不是每次累加量 |
| ShadowTargetWorld | 幕上的影子目标，不是实体杖尖或后台地板目标 |
| Projection | 根据输出变换、真实局部 bounds 重建 A/B 并重新投影的值快照 |

计算先复核输入实际 mesh bounds、组件变换、端点、投影与原地线；A 必须从地线上方、幕内开始。B 可以在幕外，不新增第二端接触要求。目标保留本次 A 的 **幕局部 X/Y**，只取原地线 Z，再沿原射线深度反解实体位移。因此不把 A 横向吸附到地线锚点，不硬编码世界 Z70，也不把实体手杖放到幕面。

终点进度 1 再用既有 `IsStaffAOnNarrativeGround` 与原幕局部 X/Y 复核实际重建结果。严格数值精度无法满足时失败闭合，不放宽判定 epsilon。失败不导出有效 Token、Projection 或部分可用位移；大坐标检查只证明“有效结果符合契约，否则拒绝”，不是无限坐标范围保证。

函数不访问 World、不移动 Actor/Component、不加载资产、不管理计时/CDO/会话，也不能完成演出或恢复 owner-relative 初始平移。后续表现层应读取 Status；不能把默认 Identity 变换当作失败时的可用姿态。

## 权限与接线边界

| 层 | 唯一责任 | 不允许承担的责任 |
|---|---|---|
| Puzzle Director | 两变量参数、姿态与 15 Hz 保持；当前 Resolve 身份 | 不管理枝组件或落杖动画 |
| Stage Presentation | 冻结 Resolve、接受真实 A 接触、授权/清理 Forest | 不复制谜题评分 |
| 新 StaffDropLibrary | 纯值落杖样本 | 不接受接触、不判 Token 当前有效、不决定秒数 |
| 后续 Dev Blueprint / Timeline | 已知对象表现接线、归一化时间、局部清理 | 不制造成功、不绕过接触、不争夺 POV |
| Forest Actor / ForestGeometryLibrary | 同主灯下真实枝网格、几何、归一化生长与释放 | 不决定谜题、完整游戏结束或重启 |
| PlayerController / Pawn | 保持现有输入上下文与唯一最终 POV | 本次不增按键或自动转镜头 |

### 已存在的真实接口

Stage Presentation 的 live 成功路径先原生冻结 Resolve，再触发 `ReceivePuzzleResolved`；可读取 `GetResolvedStaffPresentationSnapshot`。该 hook 也可能在 `SynchronizeFromDirector` 读取已成功状态时再次触发，同步路径不重建 Staff 起始快照，不能把 hook 本身当作新的落杖起点。接触使用 `TryAcceptStaffContact`，随后可读取 `GetStaffContactPresentationSnapshot`；成林只能经 `BeginForestPresentation`、`SetForestNormalizedGrowth`、`ClearForestPresentation`。Director 可通过 `IsResolvedTokenCurrent` 核验当前身份。

`ReceiveStaffContactAccepted` 是 Blueprint 事件；原生失效 delegate 目前不是 BlueprintAssignable。不能在搭图说明里虚构一个可直接绑定的 BP 失效事件。`ForestPresentationActor` 是现有显式配置引用，但不是 BlueprintReadOnly；后续完整预检如需读取其 authoring，应先列出最小只读接口或独立 Dev 显式引用方案再实施，不猜私有字段可见性。

### 后续接入顺序（尚未实施，不把计划当成果）

1. 在独立 `Dev/M3` 入口保存候选接线；保留当前已保存 `LV_M3GeometryProbe` 与现有启动器，不把临时 Python 夹具直接保存覆盖旧地图。候选 .72/.85、.05/.09、1.25 秒及暂用 2/6 秒仍是 Dev，不是正式参数。
2. Blueprint 从真实 Resolve 事件读取并冻结快照；必须确认 `bHasSnapshot`、当前 Token，以及该 Token 尚未启动同一演出。迟到同步不能合成起始快照，同 Token 重复 hook 不重启 Timeline。缓存其自身负责的 Staff 原 owner-relative 平移，并保持唯一会话身份。调用前/应用前检查当前 Token，不以数学输出中的 GUID 代替授权。
3. Timeline 只输出归一化进度。每个样本调用新库，Valid 才设置 **Staff 的世界位置**；不逐次累加 Delta，不重设旋转/缩放，不改灯与偶根变换、不另开评分循环。
4. 落杖结束用实际场景调用 `TryAcceptStaffContact`。它同步广播后可能因重入复位失效；返回 true 后仍须重新读接触快照与当前 Token，才请求原生 Forest Begin。
5. 迁移当前 Python 的完整预检：15 枝实际网格最终 bounds；当前 Torso/Head 的 16 个角点投影及幕尺寸 2% padding。原生 Forest Begin 仅预检初始进度，不能冒称已替代完整最终边界与身体保护区检查。
6. 生长只调用原生归一化接口。失效、复位、EndPlay 停止 Timeline，清理所属表现资源并恢复该会话负责的平移；保持原生新复位姿态，避免旧会话恢复覆盖新姿态。Blueprint 未接入前，这些清理不能算已完成。
7. Dev 题签与阶段显示只消费事实；不写 HUD/CDO 核心状态、不承担评分。完成保持林影不等于已有 FinishFinale、ForestComplete 环境状态或三幕队列；当前这些全流程功能没有实现。
8. 狭窄 Cook 独立 Dev 入口和真实引用；在不依赖 Editor/Python 的 Windows Development 包中核验可玩连续演出、清理及图形。游戏包验收与 Editor/NullRHI 数学验收分开。

## 本步验证

最终 Editor Automation **78 Success / 0 Failed / 0 Warnings / 0 NotRun / 0 InProcess**，退出码 0。原有 70 项集合全部保留且成功；新增 8 项 `DengYingShanHai.P03.StaffDrop.*`：

- CausalEndpoints：本次姿态、半程/终点、原横向落点与真实地线；
- RotationScaleAndInputPurity：姿态保持、确定性、输入只读、三轴镜像 Staff 与偏心 bounds；
- RotatedScaledReceiver：旋转/非均匀尺度、X/Y/Z 镜像幕布、大坐标有效结果或失败闭合；
- ProgressBoundary：有限截断、NaN/Inf 拒绝及实际结果状态/变换；
- InvalidSnapshot：缺失事实或身份拒绝；
- CachedGeometryNotTrusted：端点/射线缓存不一致、退化几何、非有限光源、B 幕外与失败 payload；
- GroundAndInitialHeight：原地线一致性与起点高度；
- RuntimeBlueprintContract：反射、BlueprintPure/read-only、非 Editor-only 接口与无需 World 的执行。

新增测试 flags 为 EditorContext：**不能说新 8 项已在独立包运行**。Editor Development、Game Development、Game Shipping 三目标实编均 `Result: Succeeded`、退出码 0。本步只执行 Build；没有 Cook/Stage/Package/Deploy 或新包 Run，也没有新的 Cook 根/容器/分块/插件/先决条件配置。Game 编译不是游戏包或实际画面运行证据。当前可玩 Python 脚本尚未调用新库。

测试日志保留 13 条既有 Automation 初始化 Error；本轮报告项目测试 0 失败，0 ensure/Unhandled/Fatal。MSVC 14.51.36260 高于 UE preferred 14.50.35717，首轮 Editor 与 Game 编译仍有引擎 Character.h 弃用警告；未修改引擎或工具链，不称整个环境“零警告”。

## 位置、资产与恢复

当前游戏仍在文件资源管理器双击：`D:\灯影山海\Start-M3Candidate.cmd`。链接可能只预览代码。本步没有新启动器、没有新的画面或包可验收，也不要求重复旧入口人工检测。

证据根：`D:\灯影山海\Saved\Audit-2026-10-05-P03RuntimePreparation\`。完整原文文档备份在 `Before/`；Before/After 哈希、构建、自动化及最终报告单列保存。不改 Content/Config/已有 Source/Scripts/启动器，不下载新资产、付费资源或插件，不新增许可条目。最终范围以 `Scope-After.json` 为准，不使用旧包替代本步证据。

回退只针对本步 3 个新源码及文档增量：先确认，再从本步备份恢复文档/移出新增源码并重新构建。没有执行删除、Git reset/checkout/clean/commit；用户已有地图和未提交改动保持原样。后续完整 runtime 接线、正式美术/声音、三幕串联、5–8 分钟、性能与现场包验收仍是未完成项。
