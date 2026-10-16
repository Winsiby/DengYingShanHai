# 跨幕 E 操纵释放修复与验收

日期：2026-10-11。唯一任务负责人为用户，Codex 协助实现、测试与证据整理。本轮仅修正“上一幕进入 E 操纵后，下一幕开始时仍在操纵”的问题；不进入其他项目开发步骤。

## 玩家可见结果

P01→P02、P02→P03 正式进入新的 Playing 幕时，结束上一幕灯或偶的操纵；进入普通行走／观察状态。新一幕需重新靠近、对准目标并按 E。同幕 R、重复同步、Holding、打断、成功题签停留和第三幕真实落杖成林均不额外退出操纵。既有入幕 .15/.15 参数复位不改变。

## 根因和最小实现

成功时禁用能力并不等同于结束交互会话；旧 Interaction.ActiveControlledActor、能力 UnderControl 和 Controller Manipulate 模式会保留，下一幕重新启用能力后旧会话又能继续使用。

在现有 ADYDevEntryPlayerController 的 Stage 显示事实通知中观察有效且前进的 Playing 幕序号。只读取当前注册同世界 Stage 和 Director 的一致快照；新幕序号先消费，再调用当前占有 Pawn 的 Interaction.EndActiveControl。通过原有 EndControl→OnControlStateChanged(false)→Explore Context 链释放，不向 Director、Pawn 或能力组件添加新的依赖，不新增 Tick、世界扫描、代理会话或判定逻辑。迟到首次附着只记录当前幕基线，不误释放。

没有 Flush／压制物理按键：入幕后若玩家仍按住 A/D，既有 Explore 移动映射仍可能响应；它不会再调整上一幕的灯或偶。现有 0.10 秒聚焦刷新负责恢复新幕可交互焦点，不新增计时器。

修改三份 C++ 文件：DYDevEntryPlayerController.h/.cpp、DYEntryLoopAutomationTests.cpp；现有 TECH_SPEC 记录边界；既有 Start-EnvironmentDev.ps1 仅固定到新 Run2 包。根 CMD、Content、Config、输入资产、镜头、15Hz、目标容差／保持、题签时间、灯速、偶速、声音和脚步组件全部保护。

## 验证层级

实际结果及 SHA256 以审计根 `D:\灯影山海\Saved\Audit-2026-10-11-ActEntryControlReset` 内报告为事实源。

- Native-Run2：154 成功、0 失败、0 未运行，真实编译和测试退出 0；新增两项前进／非法快照策略测试，原测试不删减。这些纯策略测试不冒充 LocalPlayer 操纵证明。
- ColdVerify-Run1：冷读现有地图成功、零资产保存、退出 0；原地图参数、类、Transform、显式引用和 32 份依赖资产保持原样。
- VisiblePlay-Run3：独立原流程／环境／音频回归，固定最终 POV 的门槛不放松；完整结果见 Result、ENVIRONMENT_RESULT、AUDIO_RESULT、MIX_QA、EXIT。
- ControlProbe：独立实际 PIE 操纵专项，E/R 通过当前占有 Pawn 的真实 Interaction 语义请求，必须由现有射线和聚焦计时器选中实际目标；不伪造 Focus、ActiveActor 或调用能力 BeginControl。检查灯和偶跨幕释放、实际 LocalPlayer 映射互斥、无会话时轴请求不动旧目标、同幕 R 与重复同步保留操纵。
- 专项第二轮正常 ApplyMoveIntent 走近偶，并仅临时改变运行中 ControlRotation 瞄准实际碰撞部件，随后恢复；没有传送、改相机资产或保存地图。它不是固定机位对比，也不是物理键鼠验证。真实保持、成功、落杖、接触、生长和终态由原产品代码和 Blueprint 执行；真实菜单按钮委托重演，真实 EndPlay 清理。
- 新 Development 包、20 秒真实首帧、四种只读启动 DryRun 和原文件保护结果以 Package、FirstFrame、Launcher、FINAL 为准。未通过对应门控不得交付完成结论。

实际成功结果：VisiblePlay-Run3 为 65 项流程、35 项环境、40 张导出图、两次真实成林及一次重演，退出 0；有声主混音 70.656 秒、峰值 .23376465、无削波，静音主混音 61.994667 秒、非零样本 0。模型逐张检查五態固定 POV 图，背景、灯偶、阴影和题签可读，不代表正式美术签收。

ControlProbe-Run3 为 41 项、8 张实际图、12 组所属 LocalPlayer Context 检查、两次真实成林、一次实际菜单重演、退出 0。四次释放的实际顺序为“第一轮灯 P01→P02、灯 P02→P03；第二轮灯 P01→P02、偶 P02→P03”。每次释放后 ActiveActor 为空、Manipulate 模式关闭、Explore 优先级 0 生效且 Manipulate 优先级 10 不在；无会话的轴请求不能改变原 .15/.15 值。两轮 P02 的真实 R 请求保持同幕和真实当前会话；六次新 E 和三次重复同步均保有新会话。EndPlay 前真实偶会话仍活跃，之后六个精确路径对象全部消失，明确为实际销毁，不伪称读到了销毁对象的属性。

Package-Run1：UAT 退出 0，新 `EnvironmentDev-20261011-Run2` Development 归档成功。86 份原生源、32 份源资产和 68 份实际验证输入打包前后哈希一致。49 份初始归档文件合计 1,045,513,908 字节，另有独立 ENVIRONMENT-DEV-BUILD.json。Cook 根仍是现有 EnvironmentStates 地图，Config／引擎带入的 InteractionLab 与 Entry 支持地图是旧依赖，不是新增场景。第一帧和启动验收另列于对应报告。

FirstFrame-Run1：新包实际载入指定地图，1280×800 干净标题图已逐张查看；引擎原生 20 秒 Benchmarking 退出、退出 0，exe 哈希前后相同。VISUAL_REVIEW 另记录五态和首帧的模型图像检查，不能替代用户物理按键或视觉签收。

## 保留的失败记录

Native-Run1 新测试的 initializer-list 混合 int 与 UE INDEX_NONE 类型编译失败；只将测试改为显式 int32 数组，产品修复逻辑未改。

VisiblePlay-Run1 在 22 项检查后固定 POV 断言失败，原记录缺少失败时相机数值，原因尚不能确定，不归因于用户操作。新增失败前只读实际 POV／Pawn／ControlRotation 记录，不放宽断言。VisiblePlay-Run2 的新增诊断误用未 Python 导出的 pc.get_pawn，在 8 项后失败；改用实际 GameplayStatics.get_player_pawn。Run3 在同一源代码下已越过 Run1 失败点，实际相机位置、旋转、FOV、所有者均与锚点相同。各轮失败记录、截图、初始快照均保留。

ControlProbe-Run1 在开始前因诊断读取 protected Player 属性失败，零通过项；改用真实已创建菜单的公开 GetOwningPlayer / GetOwningLocalPlayer，再根据该 LocalPlayer 的 Outer 关联 Enhanced Input Subsystem，不新增产品接口。ControlProbe-Run2 实际完成 40 项、两次真实成林和一次重演，但最后将 EndPlay 后失效 Python UObject 包装传入 IsValid，触发 NativizeObject 异常。只修诊断：在对象活着时记录精确路径，真实 EndPlay 后通过公开 find_object 重新观察；不存在即对象已销毁，仍存在则读取实际运行状态，不吞掉 TypeError 当成功。保留 object_presence 和 exact_live_paths，不把“已销毁”说成读到了 false 属性。Run3 是最终专项运行编号。

## 交付与回退

当前入口仍为 `D:\灯影山海\Start-EnvironmentDev.cmd`；仅在新包验收后将 helper 固定为 `EnvironmentDev-20261011-Run2\Windows`，不随意选最新目录。旧 Run1 归档与本轮 Before 五份备份原样保留；若需回退，应按明确备份／包身份操作，不混合新旧源码和包。

保护与变更精确数字以 FINAL 为准：基线 275 份原文件，只允许五份现有文件修改；270 份其他原文件和 376 份旧归档文件必须哈希一致。新增产品文件仅本验证文档。受限旧 LICENSES.md 不读取、不改写。无 Git 写操作、删除、模型／音频／字体下载、插件、付费资产或许可变更。

## 限制与 AI 过程记录

自动化证明实际 Editor PIE 会话和原生逻辑，不代勾新包物理 E/A/D/R、系统扬声器听感、真人全流程、首次玩家盲测、Shipping、正式美术或 5–8 分钟体验。包本轮验证为编译／Cook／身份、首帧与启动检查，不声称包内完整操纵专项已完成。

Codex 协助范围：最小源码修复、原生策略测试、只读 UE API 核验、实际 PIE 诊断、打包门控和文档。子代理只分担测试／审查／脚本，不代表项目存在队友。UE 输入、架构及 C++ 技能使本修复复用原会话生命周期和局部输入 Context，不建立新框架；打包技能使本次采用新归档、精确 Cook／身份与原版保留。没有操作 WorkBuddy 或改变用户个人开发分工。
