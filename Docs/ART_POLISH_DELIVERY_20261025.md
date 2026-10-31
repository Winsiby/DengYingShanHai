# 灯影山海美术整理交付记录（2026-10-25）

**状态：本轮美术修改已交付 Shipping Run170，正式入口完整性预检与真正 CMD 入口实机烟测均通过，原生进程及外层 CMD 实际退出均为0。用户后续门楼修复已独立交付Run171，详见末尾后续任务指针；未宣称全部美术/UI或性能验收通过。**

本文据本轮磁盘证据整理；唯一人类作者与最终责任人为用户，Codex辅助实现、比较和验证。历史原始报告、失败取样和包均保留；当前接续状态同步至 CURRENT-HANDOFF。

## 本轮实际变化

| 项目 | 实现与玩家可见结果 | 范围边界 |
| --- | --- | --- |
| 菜单遮幅 | 保留现有插画与 ScaleToFit，完整视口始终绘制不透明黑色背景，非16:9窗口上下留黑边，避免夜空、树梢从菜单边缘露出。按钮位置和插画安全区保留。 | 没有重新生成菜单图或引入新的布局系统。 |
| 演出 HUD | 操作态保留操作、对齐与保持信息；演出态隐藏操作提示、阶段名、进度和中心准星，突出一条字幕与空格跳过提示。完成、跳过和取消后恢复操作态。底牌复用现有暗木、暖纸与暖金色系。 | 表现状态独立于临时行走提示，不改变谜题判定和演出事实。 |
| 字幕根与多实例修复 | 字幕优先交给本地 ADYInteractionHUD 的真实 View；备用路径才寻找可见 Widget。其他实例演出态无字幕时不画空底牌。PC 隐藏 Blueprint 提示时避开原生字幕根，修复整根被一起隐藏的问题；Blueprint 操作提示同时降低整根透明度，避免单改可见性又出现。 | 不增加第二个字幕系统；具体演出字幕视觉覆盖见下文。 |
| 八张观众长凳 | 仅 ART_AUD_Bench_0_L/R 至 3_L/R 八个 Actor 改用 M_DY_AudienceWood，收敛灰白亮横条，保留木纹。应用记录明确没有改变 Actor 位置、旋转、缩放或灯光。 | 不修改原共享木材实例，不扩展到全场木件。稳定的15枝成林链路保持；没有重新启动120枝密林方案。 |

源码差异与回退原件见 [Source-Delta.json](D:/灯影山海/Saved/ArtPolish-2026-10-25/Source-Delta.json) 和 [Backup目录](D:/灯影山海/Saved/ArtPolish-2026-10-25/Backup)。本轮八份源码白名单含菜单、HUD、Performance、PC及其接口、已有夸父装配自动化基线核对；不是重写角色模型或玩法。

长凳应用依据为 [Bench-Apply.json](D:/灯影山海/Saved/ArtPolish-2026-10-25/Bench-Apply.json)。[Before](D:/灯影山海/Saved/ArtPolish-2026-10-25/Bench-Matte-Compare/Before.png) 与 [Candidate](D:/灯影山海/Saved/ArtPolish-2026-10-25/Bench-Matte-Compare/Candidate.png) 同机位中，候选横档和支脚不再成片灰亮，靠背/座板纹理仍可见，前排暗部细节比原图减少。该对比不是整场材质验收。

## 候选包与一致性

- Development：D盘 FormalMain-Development-20261025-RunD13。
- Shipping：D盘 FormalMain-Shipping-20261025-Run170。
- 两份包的 INPUTS-BEFORE 各记录683个输入，按 Relative、Bytes、SHA256比较零差异；各自 INPUTS-BEFORE 与 INPUTS-AFTER 也零差异。即两个配置使用相同记录输入，不代表两个配置原生EXE相同。
- 候选主地图 SHA256：`97CD401167E3DCB4B1B9E350794B2CAE37A8FD923DC9141E28BBBF3C760FC2F1`。
- Run170原生Shipping EXE SHA256：`DCEFE6C67B5FF3F2C819A93F254C37023F787079A9B528EC25AFD60FD185C612`。
- RunD13原生Development EXE SHA256：`7A93D781967480C6880F411F4AECC582499FC406AFEEB211B2470FBFEE83F0FA`。

构建身份分别见 [Package-RunD13/RESULT.json](D:/灯影山海/Saved/ArtPolish-2026-10-25/Package-RunD13/RESULT.json) 与 [Package-Run170/RESULT.json](D:/灯影山海/Saved/ArtPolish-2026-10-25/Package-Run170/RESULT.json)。二者 UAT 实际退出为0。构建身份中 FirstFrame/Gameplay/HumanVisualAcceptance 的旧false字段不是本轮后续运行报告的替代品，也不应回写成无条件的艺术验收。

## 已执行的验证

| 验证 | 实际结果 | 证据与限度 |
| --- | --- | --- |
| 最终Editor Build R4 | 原生退出0 | [R4结果](D:/灯影山海/Saved/ArtPolish-2026-10-25/Editor-Build-Final-R4-Result.json)。 |
| 最终自动化 | 186成功、0失败，进程退出0 | [Automation-RunD14](D:/灯影山海/Saved/ArtPolish-2026-10-25/Automation-RunD14/RESULT.json)。NullRHI逻辑测试，不代表物理输入或画面验收。 |
| Shipping Run170 FullFlow | 两轮四幕流程、真实Replay，原生正常退出0 | [FullFlow结果](D:/灯影山海/Saved/ArtPolish-2026-10-25/Runtime-Run170-FullFlow/FLOW-RESULT.json)。两轮StepMasks均4095、PerformanceMasks均15、SkippedMasks均0。 |
| Shipping Run170 SkipFlow | 两轮四幕流程、每幕跳过、真实Replay，原生正常退出0 | [SkipFlow结果](D:/灯影山海/Saved/ArtPolish-2026-10-25/Runtime-Run170-SkipFlow/FLOW-RESULT.json)。两轮StepMasks均4095、PerformanceMasks/SkippedMasks均15。 |
| Development RunD13无CSV退出对照 | 同一EXE无CSV启动参数的SkipFlow，两轮四幕、Replay、原生正常退出0 | [NoCSV对照](D:/灯影山海/Saved/ArtPolish-2026-10-25/Runtime-RunD13-SkipFlow-NoCsvExitControl/NO-CSV-EXIT-CONTROL.json)。流程模式和时长与Profile不同，不能据此认定CSV是唯一原因。 |

上述流程由现有显式启用的辅助输入路径执行，不能写成独立真人盲测。公开入口烟测已另行从真正 Start-ReleaseEntry-Shipping.cmd 执行，见 [PUBLIC-ENTRY-SMOKE.json](D:/灯影山海/Saved/ArtPolish-2026-10-25/PUBLIC-ENTRY-SMOKE.json)，没有用候选EXE直接启动替代。

## 已看见的画面与证据边界

[Shipping独立图片复核](D:/灯影山海/Saved/ArtPolish-2026-10-25/Resume-Run170/Shipping-Visual-Review-Independent.json)记录了原图名单、25帧哈希与时间分组。

- `Run170-Menu16x10.png`：黑色上下遮幅完整，插画、六按钮与右说明可见，没有3D露底。
- FullFlow `010.png`为演出前对照；`013.png`、`018.png`中的精卫演出只保留一条字幕底牌，阶段名、操作句和中心十字准星隐藏；`019.png`显示自然结束后操作HUD与准星恢复。右侧蓝色描边箭头为鼠标指针，和中心准星分开计。
- FullFlow `000.png`、`013.png`、`019.png`右侧所见长凳是暖暗木色，没有旧灰白横条抢眼；Shipping图是远景，不能据此验八张长凳所有近景木纹。
- 拼图名称 FullFlow-Sheet.jpg 不等于全为同一会话：`Run170-FullFlow-000.png`至`022.png`的捕获时间落于 FullFlow启动/退出区间；`023.png`、`024.png`捕获于06:34:52/54 UTC，已晚于FullFlow的06:31:05退出，属于06:31:33–06:34:56的SkipFlow末尾。末两图SHA256相同，不能算两份独立终态证据。
- 这批Shipping图直接确认精卫演出HUD变化；首幕前10帧为成林后状态，不能补充成首幕演出字幕验收；没有由此宣称刑天、烛龙全部动作或字幕已逐帧复核。
- [Development定点复核](D:/灯影山海/Saved/ArtPolish-2026-10-25/Resume-Run170/Development-Visual-Review.json)确认精卫五段字幕变化、单底牌、自然结束恢复及刑天一段字幕；采用诊断机位9与辅助流程，不能用于认证正常玩家机位。其手动空格尝试未获执行，不算新的跳过证据。
- Scene-Review的Inside/Operate证明两个取样机位能完整读出幕面并保留彩偶/操杆；不等于正常全程POV或四幕视觉全部通过。本轮没有为截图而瞬移玩家或改相机所有权。

## 未解决的Profile退出失败

**两次Development Profile原生退出均为777003，均为FAIL-NATIVE-EXIT。问题未解决，不计正常退出，也不计完整性能验收通过。**

两份CSV各18,000帧、约164–165秒，仅是Development 1280×720、D3D12/SM6、RTX 5070 Laptop下的有界FrameTime/GPUTime样本。全样本FrameTime P95分别约10.207/10.319ms，正值GPUTime P95约9.061/9.148ms；首帧包含约2.8–3.1秒尖峰，去前10秒后仍有126–141ms级最大帧时。不能表述为Shipping全流程稳定帧率，也不能用CSV完整落盘覆盖退出失败。

统计口径、列名独立解析、有效帧数、原始哈希与完整性详见 [Performance-Sample-Analysis.md](D:/灯影山海/Saved/ArtPolish-2026-10-25/Resume-Run170/Performance-Sample-Analysis.md) 及其JSON。无CSV对照仅缩小已观察到的失败情景，原始失败调用栈/根因仍未确定。

## 保留的P2与后续任务边界

- P2：恢复操作HUD后的左上旧cue仍出现“依次复演三幕”；四幕结束页底行贴近或超出窗口下沿。保留为后续文案/安全区工作，不能写“全部UI通过”。
- 已完成本轮范围内的菜单、演出HUD抽样与公开入口实机核对；四幕全部动作、全部UI文案与近景材质仍按前述证据边界，不新增全面验收结论。
- 已完成：核对683输入、31产物和回退原件后，将正式启动脚本仅两条归档/审计路径切至Run170；所有原始校验和标准日志路由保留。公开入口-DryRun返回PASS-PREFLIGHT-ONLY。
- 已完成：真正调用公开CMD入口，标准会话PID4388，首个已归档可见菜单截图与正常Alt+F4退出；原生与外层CMD退出均0。证据保存在 [PUBLIC-ENTRY-SMOKE.json](D:/灯影山海/Saved/ArtPolish-2026-10-25/PUBLIC-ENTRY-SMOKE.json)。

Run170正式入口已通过预检与实际重启烟测。该结论对应门楼修复之前的Run170基线；后续Gate任务若修改正式地图，仍须重新打包并保持入口/包/地图身份一致，不能借用本次截图认证新地图。不得关闭或绕过地图/包哈希保护。地图、源码及原启动脚本回退原件位于本轮Backup；切换与回退必须让入口、包身份和地图完整性链保持一致，不单独恢复一份旧脚本后就声称回退可运行。

## 正式入口烟测完成与独立门楼任务

正式入口：`D:/灯影山海/Start-ReleaseEntry-Shipping.cmd` → `Scripts/Start-FormalShipping.ps1` → `FormalMain-Shipping-20261025-Run170/Windows`。本次只替换归档与审计两条路径，没有关闭地图、EXE、文件数量/大小、容器或已有进程保护。更新时唯一活动程序是本轮隔离诊断窗口PID31160，未发送窗口输入、未关闭程序、未改运行包或游戏状态。路由更新不需要结束该进程；再次公开启动仍须按原guard先正常关闭已有游戏。

路由审计：`Saved/ArtPolish-2026-10-25/Promotion-RouteOnly-20261025-171657-265/`，含旧脚本、全部预检查、修改结果与实际公开脚本预检输出。预检目标明确是Run170、Shipping、MapOverride=false、31文件/862604663B。

此前最小化与用户输入保护导致的窗口阻塞已经解除。用户还原窗口后，根代理正常关闭旧诊断进程，再实际调用 Start-ReleaseEntry-Shipping.cmd。标准公开会话为 Saved/ReleaseEntryPlay-Shipping/20261025-201615-305，Launch/Exit同为PID4388，目标为Run170原生Shipping EXE、MapOverride=false；原生退出0、外层CMD退出0。

[原样归档截图](D:/灯影山海/Saved/GateRepair-2026-10-25/Attempt1/Run170-PublicEntry-Baseline.png)的源CaptureFile修改时间为2026-10-25 12:22:19.161 UTC，处于标准Launch记录12:16:15.441与Exit记录12:28:34.825之间；SHA256为C799579DD36744F2E49031DDB95ED4584527D3902C8E12D138B9816BA9977570。实际查看2560×1600原图可见完整菜单与上下不透明遮幅。它是该会话首个归档可见取样，不是引擎第1帧计数。响应依据是Sky截图成功后Alt+F4正常生效并退出0；没有采样或伪造Win32 Responding标志。

用户随后提出的门楼修复已作为独立任务完成，并交付当前正式Shipping Run171，详见 [门楼最终交付](D:/灯影山海/Docs/GATE_REPAIR_20261025.md) 和 [Gate CURRENT-HANDOFF](D:/灯影山海/Saved/GateRepair-2026-10-25/Attempt1/CURRENT-HANDOFF.json)。该任务拥有自己的候选门外图与实际公开CMD烟测；本文Run170基线烟测仍按历史原样保留，没有借用于新门地图。
