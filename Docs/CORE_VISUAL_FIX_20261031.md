# 灯影山海：核心画面修复与 Run176 交付记录

日期：2026-10-31（Asia/Shanghai）。唯一人工负责人：用户；本轮实现、检查与记录工具：Codex。

本轮完成精卫碎影、共同操作镜头与三位角色高度、四幕提示三项修复，正式 Shipping 入口已从 Run175 切换至 Run176。其余美术建议继续保留在上一轮审查中，本记录只验收本轮实际修改。

证据目录：[CoreVisualFix Attempt1](D:/灯影山海/Saved/CoreVisualFix-2026-10-31/Attempt1)。以下本地链接全部指向项目 D 盘目录。

## 1. 玩家可见变化

| 项目 | 修改和原因 | 本轮验收结果 |
| --- | --- | --- |
| 精卫影子 | 精卫使用局部 BoundsScale=1.5，其他角色切换时恢复 1.0，避免羽翼动画范围之外留下分离的碎影 | 同场景局部比较、冷启动 PIE 和 Run176 实际渲染截图中未再见原来的游离碎影 |
| 操作构图 | 共用跟随镜头拉远、抬高并横向偏移；精卫、刑天、烛龙显示位置抬高 160 cm，同步交互代理 | 已检查操作位四幕截图；刑天斧盾及主体、烛龙头部与盘曲更易辨认，灯具与幕上结果可同时观察 |
| 四幕提示 | 当前表现蓝图的“依次复演三幕”改为“依次复演四幕”，保留原本地化键 | Run176 实际截图已显示“依次复演四幕 · 操作沿用 E / A / D” |

主地图、谜题参数、输入语法、控制轨道、夸父落杖和树林几何保持原值。相机仍由原 Pawn 的 CameraBoom/Camera 负责；FOV=70、碰撞探测启用、ProbeSize=28 cm，没有增加第二套 POV 或每帧扫描逻辑。

入口较远位置的画面仍会带入前景门板；本轮的操作位构图通过实际 PIE 单独核验，不能据入口截图宣称所有行走位置均无任何遮挡。

## 2. 实际修改的生产输入

冻结输入仍为 697 项（uproject、Source、Config、Content），相对 Run175 基线仅以下 6 项发生变化。另有正式启动脚本的两处路径切换；报告与审计文件单独存放。

| 文件 | 具体变化 |
| --- | --- |
| [DYPuppetActor.cpp](D:/灯影山海/Source/DengYingShanHai/Private/Interaction/DYPuppetActor.cpp) | 应用角色数据时同步 Torso 查询代理位置；仅精卫 BoundsScale=1.5，其他角色恢复 1.0 |
| [DYPuppetCastTypes.h](D:/灯影山海/Source/DengYingShanHai/Public/Interaction/DYPuppetCastTypes.h) | FigureEntry 新增默认零向量的 ControlProxyRelativeLocation，职责限于交互射线代理随显示构图移动 |
| [DYStageOperatorPawn.cpp](D:/灯影山海/Source/DengYingShanHai/Private/Player/DYStageOperatorPawn.cpp) | Arm 360→800 cm；TargetOffset (0,0,70)→(0,0,240)；SocketOffset (0,55,10)→(0,-180,10) |
| [DYPhase1AutomationTests.cpp](D:/灯影山海/Source/DengYingShanHai/Private/Tests/DYPhase1AutomationTests.cpp) | 两个已有相机臂长度断言随正式构图同步为 800；移动速度 360、碰撞和输入断言保留 |
| [DA_DYPuppetCast.uasset](D:/灯影山海/Content/DengYingShanHai/Puppets/DA_DYPuppetCast.uasset) | 索引 1/2/3 的显示 Z=-104.57→55.43，查询代理=(0,-42.44,160)；夸父索引 0 保持原值；模型、动画引用、旋转、缩放均未替换 |
| [BP_DYReadabilityPresentation.uasset](D:/灯影山海/Content/DengYingShanHai/Dev/Readability/Stage/BP_DYReadabilityPresentation.uasset) | 精确修改 ShowActGuidance / K2Node_CallFunction_3 / Text 内一处“复演三幕”为“四幕”；本地化键 B40AE6124E66FA883E9298A2DBCD75CA 保留 |

源代码补丁和前后哈希见 [SOURCE-DIFF.patch](D:/灯影山海/Saved/CoreVisualFix-2026-10-31/Attempt1/SOURCE-DIFF.patch)、[CURRENT-CHANGES.json](D:/灯影山海/Saved/CoreVisualFix-2026-10-31/Attempt1/CURRENT-CHANGES.json)。资产精确前后值见 [ASSETS-APPLY2.json](D:/灯影山海/Saved/CoreVisualFix-2026-10-31/Attempt1/ASSETS-APPLY2.json)。

精卫修复采用局部边界调整，生产配置保留 VSM 缓存。调试中的 Always、关闭全局缓存并未作为生产方案。Epic 文档说明了虚拟阴影缓存与投影物体边界的关系；局部方案的选择依据是本项目实际对照图与运行结果。[Epic Virtual Shadow Maps 文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/virtual-shadow-maps-in-unreal-engine)

## 3. 验证记录及其边界

| 验证 | 当前证据 | 结果 |
| --- | --- | --- |
| Editor 编译 | Build-Editor、Build-Editor2 / RESULT.json | 原生编译退出 0 |
| 现有自动化测试 | [Automation-RunD19-CameraContract/RESULT.json](D:/灯影山海/Saved/CoreVisualFix-2026-10-31/Attempt1/Automation-RunD19-CameraContract/RESULT.json) | 188 成功、0 失败，原生退出 0 |
| 冷启动实际 PIE | [PIE-AFTER5.json](D:/灯影山海/Saved/CoreVisualFix-2026-10-31/Attempt1/PIE-AFTER5.json) | 8 张四幕画面；灯/偶各一次，共 8/8 实际聚焦与开始控制检查通过 |
| Development 构建 | [Package-RunD19/RESULT.json](D:/灯影山海/Saved/CoreVisualFix-2026-10-31/Attempt1/Package-RunD19/RESULT.json) | Build/Cook/Stage/Archive 完成，UAT 原生退出 0 |
| Shipping 构建 | [Package-Run176/RESULT.json](D:/灯影山海/Saved/CoreVisualFix-2026-10-31/Attempt1/Package-Run176/RESULT.json) | Build/Cook/Stage/Archive 完成，UAT 原生退出 0 |
| RunD19 跳过演出回归 | [Development FLOW-RESULT.json](D:/灯影山海/Saved/CoreVisualFix-2026-10-31/Attempt1/Runtime-RunD19-SkipFlow-Regression/FLOW-RESULT.json) | 辅助流程完成两轮四幕、换幕、重新开始；StepMasks=[4095,4095]，SkippedMasks=[15,15]，正常退出 0 |
| Run176 完整演出回归 | [Shipping FLOW-RESULT.json](D:/灯影山海/Saved/CoreVisualFix-2026-10-31/Attempt1/Runtime-Run176-FullFlow-Visual/FLOW-RESULT.json) | 辅助流程完成两轮四幕及重新开始；StepMasks=[4095,4095]，SkippedMasks=[0,0]，正常退出 0 |
| 正式公开入口 | [PUBLIC-ENTRY-SMOKE.json](D:/灯影山海/Saved/CoreVisualFix-2026-10-31/Attempt1/PUBLIC-ENTRY-SMOKE.json) | 从 Start-ReleaseEntry-Shipping.cmd 启动，菜单实际显示，点击“退出游戏”；Native PID=34320、CMD PID=12668，实际退出码均 0；窗口和 UE/game 进程已关闭 |
| 完整性核对 | [PROMOTION.json](D:/灯影山海/Saved/CoreVisualFix-2026-10-31/Attempt1/PROMOTION.json)、[FINAL-CHECK.json](D:/灯影山海/Saved/CoreVisualFix-2026-10-31/Attempt1/FINAL-CHECK.json) | 两包全部 49/31 项产物重算哈希；冻结输入一致，地图未改；启动器仅两处路由变化 |

PIE 聚焦检查在可到达位置隔离验证射线与控制接入，临时暂停 Director 判定 Tick 后恢复；独立的原生打包流程负责验证未暂停的流程衔接。自动化及辅助运行不等同于首次玩家盲测。

FlowVerify 中的 PerformanceMasks 是各幕演出完成位掩码，不是 GPU/CPU 性能测量。本轮未取得新的 FrameTime/GPUTime 性能验收、5–8 分钟首次玩家体验结论、完整音效混音试听或三轮人工通关结论。入口与贴墙时的长镜头舒适度仍需独立人工走位确认。

## 4. 画面证据

刑天操作位，下图为冷启动实际 PIE；可同时观察前景灯具与幕上主体，不是 Shipping 近景验收图。

![刑天操作位实际 PIE](D:/灯影山海/Saved/CoreVisualFix-2026-10-31/Attempt1/PIE-After5/Chapter-2-Interaction.png)

精卫与四幕提示，下图来自原生 Run176 Shipping 的第二轮流程；位置靠近入口，左侧门板作为前景进入画面。

![精卫与四幕提示 Shipping](D:/灯影山海/Saved/CoreVisualFix-2026-10-31/Attempt1/Captures/CoreVisual-Shipping-Replay-0.jpg)

另有 [精卫演出截图](D:/灯影山海/Saved/CoreVisualFix-2026-10-31/Attempt1/Captures/CoreVisual-Shipping-Replay-2.jpg)、[烛龙操作位 PIE](D:/灯影山海/Saved/CoreVisualFix-2026-10-31/Attempt1/PIE-After5/Chapter-3-Show.png)、[夸父成林 PIE](D:/灯影山海/Saved/CoreVisualFix-2026-10-31/Attempt1/PIE-After5/Chapter-0-Show.png)、[正式入口主菜单](D:/灯影山海/Saved/CoreVisualFix-2026-10-31/Attempt1/Captures/CoreVisual-Public-Menu.jpg)。截图来源、时间、进程路径及哈希登记在 [CAPTURES.json](D:/灯影山海/Saved/CoreVisualFix-2026-10-31/Attempt1/CAPTURES.json)。

## 5. 当前入口、构建身份与回退

可用 [启动灯影山海.bat](D:/灯影山海/启动灯影山海.bat) 或 [Start-ReleaseEntry-Shipping.cmd](D:/灯影山海/Start-ReleaseEntry-Shipping.cmd) 启动当前正式 Run176。两者均调用 Scripts/Start-FormalShipping.ps1；本轮实际烟测使用后者。旧技术 Development 入口 Start-ReleaseEntry.cmd 保持原用途。

| 构建 | 目录 | 原生 EXE SHA256 |
| --- | --- | --- |
| Shipping Run176 | D:/灯影山海/Builds/FormalMain-Shipping-20261031-Run176/Windows | 3007A7817D4C633B93B24BB51E241A299D39132ACACCF3C1965319318B202BB8 |
| Development RunD19 | D:/灯影山海/Builds/FormalMain-Development-20261031-RunD19/Windows | 29FB9C0E0D2DAA6C71DA6DE89ACCDE8102A08ABF911F137891FA5AAA493B4627 |

正式启动脚本 SHA256：69656CF0A3AC2BF60046015EC1795E2B6C875203CD76E8BEFFEFBD6D59FAD08C。

L_DY_Main.umap SHA256 仍为 BBD838FA64D705E8F6C485B367AD5A27802BECE0DBCAD709B85AB4101C2CF763。Shipping 内仍有一张项目主地图与引擎 Entry，未增加可玩地图。发布前哈希守卫保留。

回退责任人：项目负责人（用户），Codex 可按明确指令执行。回退公开试玩只需在游戏正常关闭后恢复 [原启动脚本副本](D:/灯影山海/Saved/CoreVisualFix-2026-10-31/Attempt1/Backup/Scripts/Start-FormalShipping.ps1) 至 Scripts/Start-FormalShipping.ps1，原 Run175 包仍在。若回退源工程，同时恢复 Backup 中本轮 6 项输入，再核对基线哈希；源码与旧包需保持对应，重新构建后再用于后续开发验证。不要删除 Run176 或已存审计证据。

## 6. 保留的失败或无效尝试

以下记录保留原始状态，均未作为本轮成功证据：

- CAMERA-PREVIEW.json：暂停状态下 CameraManager 未刷新，无法构成有效机位比较；CameraPreview/VALIDITY-NOTE.txt 已注明。CAMERA-PREVIEW2.json 改用极低时间倍率短暂恢复更新后再截图。
- ASSETS-APPLY.json：保存前的保护断言因 Rotator 字符串包含对象地址而失败，saved=[]。ASSETS-APPLY2.json 改为数值角度比较后成功保存两项资产。
- PIE-AFTER 至 PIE-AFTER4：测试工具的瞄准参数、Rotator 位置参数顺序以及相机碰撞回缩导致不完整检查。PIE-AFTER5 使用显式角度命名、按实际 POV 校正；8/8 通过。没有通过关闭相机碰撞规避检查。
- Automation-RunD19：首次为 186 成功、2 失败，两项仍断言旧相机臂 360。同步正式构图期望为 800 后，Automation-RunD19-CameraContract 为 188/0；未改谜题、移动或碰撞验收要求。
- 最早的组合打包外层调用：在 Development UAT 实际成功后误读 PowerShell 脚本的 LASTEXITCODE，外层报错。Development 原生 UAT=0 与包身份有效；Shipping 随后独立打包成功，不把该外层失败记成成功。
- 一次启动 Development 回归的自动审批因旧的进程状态证据拒绝。重新读取 Shipping 原生 Exit=0 与独立进程检查后，原启动操作获准；无强制结束进程。
- 本次公开菜单归档先遇到会话辅助函数未保留，未执行输入；随后直接归档已观察的原始截图。退出后刷新旧窗口返回进程不存在，已通过新窗口列表、原生 Exit=0 和 CMD Exit=0 交叉确认正常关闭。

## 7. AI 与资源记录、后续责任

本轮使用 Codex 辅助修改既有 C++、角色显示参数与一处蓝图文字，编写检查脚本、运行现有工具并整理报告。输入是本地工程及已有运行证据；没有新增生成图片、模型、纹理、音频、字体、第三方插件或付费素材，也未替换队友的美术源文件。已阅读 Docs/LICENSES.md 和 FREE_ASSET_POLICY.md；既有资源许可继续按原登记执行，本记录不重新证明整个历史资源库的授权状态。

用户仍是唯一人工负责人。上述检查由工具执行，不冒充独立人工验收。本轮记录可供之后更新参赛 AI 使用说明，未擅改既有官方 Word/PDF。

本轮三个修改目标已交付，无待处理的技术阻塞。后续人工走位与首次体验验收由项目负责人负责；如开展新的树林造型或环境材质制作，由负责美术资产的队友作为唯一资产负责人，项目负责人负责集成，另行明确范围后执行。