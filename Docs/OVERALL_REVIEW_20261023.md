# 灯影山海整体复核（2026-10-23）

本轮对象：DeepSeek 美术及四幕换偶接入后的当前工程、Shipping Run146、Development RunD9。负责人：项目负责人；执行与检查辅助：Codex。只做审查及新建证据归档，没有修改游戏代码、模型、材质、正式地图或公开启动器。

## 1. 当前结论

三具新影偶、操杆修订、题签切幕及入口两处碰撞修复已有成果。后续工作重点应转到演出与玩家操作的一致性、核心幕面可读性和完整流程回归。本轮没有发现依据足够的新增场景或新增角色需求。

当前公开入口确为 `Start-ReleaseEntry-Shipping.cmd` → `Scripts/Start-FormalShipping.ps1` → `FormalMain-Shipping-20261023-Run146/Windows`。本轮重新计算主图与原生EXE的SHA256，均与身份文件相同；31文件、856338919字节一致。见[本轮身份复核](D:/灯影山海/Saved/Audit-2026-10-23-OverallReview/Baseline-Verified.json)。

## 2. 优先处理的具体问题

### P1-01 新影偶动画播放入口未进入单节点模式

**类型：源码与正式关卡实际Actor的不保存调用已复现；不是Shipping可见实拍。** [DYPuppetActor.cpp:207](D:/灯影山海/Source/DengYingShanHai/Private/Interaction/DYPuppetActor.cpp:207)新建CastMesh后没有设置AnimationSingleNode；[同文件:275](D:/灯影山海/Source/DengYingShanHai/Private/Interaction/DYPuppetActor.cpp:275)只调用SetAnimation/SetPosition/Play，UE5.8这些接口不会自动切换组件模式。

本轮先用临时原生Actor验证，再加载正式地图的`M2_Puppet_P02_Controlled`（实际BP_DYKuafuPuppet_Fitted），不保存地调用当前换偶入口。偶位0.15、0.50、0.86分别返回Back/Mid/Reach，但CastMesh三次均为`ANIMATION_BLUEPRINT`、`anim_instance=None`，眼睑骨世界缩放恒为1.1。见[正式Actor回读](D:/灯影山海/Saved/Audit-2026-10-23-OverallReview/Formal-Pose-Probe.json)。地图SHA256复算保持E325713B…B31B8D829。

这解释了为什么“模型成功显示、动画资源导入成功”不足以证明三具新偶已经实际演出姿态。问题位于三具共用的新显示组件播放入口。

**最小处理建议：** 创建/切入烘焙姿态网格时明确设置AnimationSingleNode，或使用会设置该模式的PlayAnimation；缓存当前Clip，避免每次偶位微调都从第0帧重启同一姿态。**唯一负责人：项目负责人，Codex可执行。**

**验收：** 在真实PIE及Development/Shipping各验证精卫翼、刑天斧盾、烛龙眼睑有实际骨骼变化，当前实例使用目标Clip；再做切章/重试/重演回归。
### P1-02 烛龙眼睑与“夜伏→睁眼为昼”错接

**类型：代码与当前真实资产核查确认，尚未在本轮Shipping实操复现。**

- [DYPuzzleDirector章节定义](D:/灯影山海/Source/DengYingShanHai/Private/Puzzles/DYPuzzleDirector.cpp:935)：夜伏的偶位目标为0.86、进入容差0.12，即0.74–0.98；下一步“睁眼为昼”偶位仍是0.86。
- [偶位转姿态](D:/灯影山海/Source/DengYingShanHai/Private/Interaction/DYPuppetControlComponent.cpp:122)：`RoundToInt(Value × 2)` 将偶位划为Back/Mid/Reach三档，0.25起即Mid，0.75起为Reach。
- 本轮用UE独立进程只读加载真实`DA_DYPuppetCast`，[Current-CastState.json](D:/灯影山海/Saved/Audit-2026-10-23-OverallReview/Current-CastState.json)确认烛龙Back为Night、Mid与Reach都为Day；不只是据导入脚本猜测uasset。
- 因此按这套映射，修复上述播放入口后，“夜伏”的全部成功窗口都会使用Day，玩家会在夜伏尚未成功前睁眼；随后携带到下一步，缺少新的开眼变化。天空则在StepIndex≥1才变昼。这是需要与播放入口一起修的第二层错接，不能把当前没有动画实例的状态描述为已经实时播出了Day。

**最小处理建议：** 将本章眼睑表现与当前段落及已成立的灯偶状态关联，明确夜伏闭眼、昼段开眼的可见过渡；保留现有参数判定、目标、容差和输入语法。先在独立检查中验证，再做四幕实机回归。**唯一负责人：项目负责人，Codex可执行。**

**验收：** 夜伏初态、调节、保持、成功时闭眼语义一致；进入昼段后能实际看见开眼与光变的因果，暂停/恢复、重试与选幕后也一致。

### P1-03 主操作画面仍存在实体、影子与灯杆重叠

**类型：当前Run146已保存实机图可见。** [s146-in2.png](D:/灯影山海/Saved/Audit-2026-10-22-FourAct/walktest/s146-in2.png)中，灯杆穿过夸父本体与影子区域，彩偶与黑影重叠，棚顶占据画面上方。能够同框说明幕后与幕上关系，但玩家辨认当前要调的对象、影子和目标的负担仍高。

**最小处理建议：** 先从现有合法操作区确认一个能清楚分开灯、偶和幕上结果的站位，并覆盖调节全过程；梳理重复表现框件与无功能遮挡。相机、灯偶轨道和关键投影不在本次审查中调整。**唯一负责人：项目负责人。**

**验收：** 正常操作距离、不开调试、不开长说明、静音时，也能读出“当前操纵对象→影子变化→目标趋势”。

### P1-04 当前版本的完整体验尚未闭环

**类型：验收缺口，不据此断言游戏无法通关。** [ENTRY_WALL_FIX](D:/灯影山海/Docs/ENTRY_WALL_FIX_20261023.md:67)明确记录Run146只走到第一幕提示；[ROUND_SUMMARY](D:/灯影山海/Docs/ROUND_SUMMARY_20261023.md:25)说明尚未四幕完整通关。较早D7/Run144的选幕图证明新角色和题签能出现在打包程序，不能替代Run146的完整操作、终局与重演。

176项自动化成功是已有事实，但该批测试结束早于最终墙裙保存；新角色切换、题签、眼睑与提示的一致性也不能仅由旧测试数代替。后续几何回读11项通过证明入口修复，未证明全程节奏。

**最小处理建议：** 以当前包逐幕记录“初态→调节→保持→成功”，走完四幕与结局，再测暂停恢复、章节切换、重新复演及正常退出，测量5–8分钟体验，按项目完成标准补目标电脑三轮。重点复核新角色轮廓与现有目标影形/提示是否匹配。**唯一负责人：项目负责人，Codex辅助。**

## 3. 第二优先级

### P2-01 四幕收尾仍共用夸父文案

**类型：源码确认的表现层一致性问题。** [DYInteractionHUDWidget.cpp:97](D:/灯影山海/Source/DengYingShanHai/Private/UI/DYInteractionHUDWidget.cpp:97)在AwaitingFinale时无章判断，统一显示“影形已合，静待杖落成林”；[Director:434](D:/灯影山海/Source/DengYingShanHai/Private/Puzzles/DYPuzzleDirector.cpp:434)使每章第三步均进入该阶段，因此新三幕也走到夸父收尾文案。

**最小处理建议：** 用已有ChapterIndex选择四幕各自的收尾短句，保持同一UI和流程，逐幕验证。无需新增玩法或叙事系统。**唯一负责人：项目负责人，Codex可执行。**

### P2-02 步骤成功音去重没有区分章节

**类型：源码确认，当前正式场景也启用了该音频Actor；未做本轮实听。** [DYStageAudioPresentationActor.cpp:25](D:/灯影山海/Source/DengYingShanHai/Private/Stage/DYStageAudioPresentationActor.cpp:25)的ResolvedActCues仅记录ActIndex，四幕都复用0/1/2，集合只在BeginPlay或整个音频会话结束时清空。连续演出进入第二幕以后，前两步成功音会被第一幕留下的0/1去重记录挡住。控制器另一路章开/章末/总末锣鼓不能补这两次步骤音。

[本轮场景回读](D:/灯影山海/Saved/Audit-2026-10-23-OverallReview/Presentation-Probe.json)确认AudioDev_Presentation的bEnableDevelopmentAudio为true、StagePresentation和ResolveSound实际赋值，不能当未使用的代码忽略。

**最小处理建议：** 去重键加入ChapterIndex，或在真正换章时清掉本章步骤集合，保留现有音源和事件触发方式。**唯一负责人：项目负责人，Codex可执行。** 验收覆盖连续四幕及同会话重复选幕/重试，避免漏播与重复播。
| 项目 | 当前依据与建议 | 唯一负责人 |
| --- | --- | --- |
| P2 入口近场树山轮廓 | [s146-start](D:/灯影山海/Saved/Audit-2026-10-22-FourAct/walktest/s146-start.png)两侧锥状山体、粗枝截面与密排黑树线仍明显。只处理入口固定镜头最醒目的2–3组，收住露出的锥尖、让树干与冠衔接可信、留出天空空隙。无需扩建场景。 | 队友负责局部美术；项目负责人负责集成验收，关键资产制作责任归队友 |
| P2 当前性能复测 | 最新性能材料早于三具新影偶接入。应在D9/Run146实际路线采FrameTime、GPUTime、P95/P99、换幕卡顿和峰值显存；没有新采样前不引用旧帧率，也不直接建议降画质。今日两份显存不足记录属于UnrealEditor，不能误称Shipping崩溃。 | 项目负责人，Codex辅助采样 |
| P2 发布元数据与文档 | 身份写GameplayVerified=true，引用的是入场证据；BuildAudit路径实际不存在，但真实UAT成功日志在C:/dy_build/cook_s146.log。补齐D盘构建证据链接，区分入场通过与全程通过。FOURACT_CAST/ASSET_LIST等历史段仍写Run143，需要明确当前Run146、D9及Run4源模型。 | 项目负责人，Codex可执行 |
| P2 新题签字体来源登记 | FOURACT_CAST写华文楷体，而LICENSES旧段仅列OFL字体。这里只确认来源台账不一致，不作侵权判断；核对实际使用与登记，或复用项目已登记字体。 | 项目负责人负责资源准入 |

## 4. 本轮检查范围与限制

- 已读最新交接、修复记录、版本身份、相关源代码与UE真实换偶数据资产，完成正式影偶Actor的不保存姿态回读，并逐图复核当前Run146入口/入场图与较早打包新偶证据。
- 本轮真实公开CMD已调用，产生[Launch.json](D:/灯影山海/Saved/ReleaseEntryPlay-Shipping/20261023-122622-698/Launch.json)；界面采集被中断，未取得本轮新首帧、完整操作与正常退出回执。不以窗口出现或PID证明通关，也不将未取得退出回执推断为游戏崩溃。
- 本轮未修改现有项目文件，未重建包，未重新测性能，未做独立人类盲测。不能把这份审查写成最终艺术验收或全流程验收通过。
- 建议顺序：先修新影偶动画入口及烛龙眼睑与段落语义；再验证四幕操作、提示/声音与核心画面；随后按实测处理少量遮挡/近场轮廓与性能问题；最后统一交付记录。