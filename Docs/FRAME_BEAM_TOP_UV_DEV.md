# 横梁顶面 UV：独立可玩 Dev 样本

2026-10-14 · 唯一人类作者与项目负责人：用户本人；Codex 辅助实施与验证。

本轮把上一阶段的梁顶 UV 候选放入独立 Dev 地图，沿用现有“开始—三幕—杖落成林—结束—重演”流程，让玩家在实际演出中比较木构观感。旧 B 地图与旧包仍可用于对照。

> 当前状态：技术样本、包内菜单／开始画面及原生正常退出已核实。新图冷验、原生 Editor 编译、158 项项目测试、三幕演出、控制回归和独立 Development 包通过。原首帧收集 FAIL 保留，并以同轮 COMPLETION-REVIEW.json 补充核实结果；未代包内全流程或真人验收。

## 打开与比较

新入口位置：`D:\灯影山海\Start-FrameBeamTopUV.cmd`。请在资源管理器中双击这个文件；聊天里的链接可能只显示脚本代码。新入口固定绑定 `Builds\FrameBeamTopUV-20261013-Run1\Windows` 的本轮 Windows Development 包。

旧 B 版本入口：`D:\灯影山海\Start-FrameBeamCandidate.cmd`。旧包保留，打开它仍显示原横梁 UV。

图文报告位置：`D:\灯影山海\Docs\FRAME_BEAM_TOP_UV_DEV.html`。上一阶段的原梁／TopUV 近中远、Lit／Unlit 同条件比较见 [独立资产图册](FRAME_BEAM_TOP_UV.html)。

## 本轮改动

新地图精确路径为 `/Game/DengYingShanHai/Dev/FrameBeamTopUV/Maps/LV_FrameBeamTopUVLab`，以已保存的 `LV_FrameBeamCandidateLab` 为模板，仍有 35 个 Actor。只将现有 `DEV_FrameBeam_RightJoint` 的网格引用替换为 `SM_DY_FrameBeam_TopUV`。

横梁仍位于 B 的 `(950,66.77584636395318,816.7876838516025)` cm，Yaw 90°、等比缩放 `0.39290377163557627`。同一木材材质、右柱、灯、幕布与游戏机位保持，所以本轮观察的是 UV 候选在原构图中的表现。

两个 C++ 文件仅追加这个精确地图身份与一项对应测试，复用原菜单和重演逻辑。C++ 不扩大 Dev 路径放行范围；旧七张已支持地图的身份、世界上下文拒绝和 Shipping 边界保留。

玩法继续使用 E/A/D/R 与 15 Hz 参数判定，三幕仍是“发现规律—协同控制—综合运用”。第三幕从实际杖尖接触继续生长真实林影；本轮木构候选服务“灯为日、影为夸父、玩家杖落成林”，没有新增互动或改变文化故事。

## 已核实结果

| 验证层 | 本轮证据 | 结论 |
|---|---|---|
| Editor 构建与原生项目测试 | 实际编译退出 0；158 成功、0 失败、0 未执行 | 新身份测试及原有测试通过 |
| 只读原图探针 | probe-Run2 实际退出 0；8,533 项审计检查 | 原 B 输入、35 Actor 与保存边界通过 |
| 独立新图创建 | create-Run1 实际退出 0；19,749 项审计检查 | 仅保存指定新地图，保留其他场景合同 |
| 独立进程冷读 | verify-Run1 实际退出 0；13,168 项审计检查，35 Actor，零保存 | 从磁盘读回新图；仅两个合同网格字段变化 |
| 三幕、成林与重演 | VisiblePlay-Run1 实际退出 0；65 流程、35 环境检查 | 两次真实成林、一次 OpenLevel 重演，固定 POV 五态原图完成 |
| 操纵、复位、步行及跨幕释放 | ControlProbe-Run1 实际退出 0；41 项控制检查 | 真实控制语义、两次成林、一次重演与 EndPlay 清理通过 |
| Development 包与原生容器 | UAT-Run1 实际退出 0；三个原生容器操作实际退出 0 | 42 个核心导出与 2 个默认导出通过；主／global 全 payload 校验通过，50 个文件封存 |
| 启动器门控与公开入口 | PS5 解析通过；33 隔离案例通过；默认 Package、显式 Package、EditorGame 三个真实 CMD DryRun 均退出 0 | 入口调用与拒绝边界通过，DryRun 没有运行游戏 |
| 已发布入口与包首帧 | 官方 Computer Use 观察中文菜单、点击开始、实际场景；同一 GameRun1 游戏及 CMD 实际退出 0 | 原生日志证实 ViewportClosed 正常退出；独立补充核验保留原收集 FAIL，未代包内全流程 |

审计检查数量用于说明工具实际完成了哪些合同检查，不是成千上万项 UE 游戏单元测试。已确认的 158 项才是本轮项目自动化测试数量。

本轮 VisiblePlay 的旧柱与候选梁各 10 项独立五态观察通过，350 个此阶段产品文件在回归前后保持。两轮 UE Master Mix 导出通过，包括静音流程；这不代替 Windows 实际音频输出和人耳听感。ControlProbe 使用真实控制语义并临时调整聚焦视线，与固定 POV 演出分组执行，不冒充物理键鼠或人工通关。

包内实际 Cook 三张地图：显式 TopUV 样本、既有项目默认 Interaction 图和继承的引擎 Entry 图；玩家入口固定进入 TopUV，不提供额外地图选择。原生 IoStore 检查覆盖 2,029 个主 chunk 与 1 个 global chunk，分别实际读取并验证 299,312,266 B 与 3,224,104 B；封存包 50 个文件、1,070,559,651 B。构建和容器检查不代替包内完整通关，包首帧证据独立记录。

包内中文菜单和点击开始后的实际场景已留存 `PackageFirstFrame-Run1\Menu.jpg`、`Started.jpg`，以及逐像素一致封装的 PNG。随后用户按 Escape 中止 Computer Use，后续未重开游戏。只读核实同一 GameRun1（PID 26204）原始日志精确加载 TopUV，`UGameEngine::Tick.ViewportClosed` 后出现 `RequestExitWithStatus(0,0)` 与 `Exiting`，游戏及 CMD 实际退出码均为 0。

原 `PackageFirstFrame-Run1\RESULT.json` 因未生成 `VISUAL.json` 留下 FAIL，原记录保留；同轮 `COMPLETION-REVIEW.json` 补充两幅图像哈希、退出日志和产品／构建身份核验。Codex 未发起本次关窗（`NormalCloseRequestedByCodex=false`），不推断关窗者。正常原生退出已核实，但没有据此代签包内完整流程、人耳听感或真人通关。

首次 probe 因审计工具将 35 个实际 Actor 与 37 个合同键混为一谈而失败：合同另外包含 `_pawn` 与 `_flow`。原失败保留；修正审计计数后，probe-Run2 使用原条件重新通过。没有因此修改场景或降低玩法判据。

## 在画面中看什么

优先观察横梁顶部是否比原 B 少一些长向木纹拉伸，再观察右柱接合与整体幕框轮廓。上一阶段已经证明源顶面仅两个非共享 V 值变化，长向源 2K 度量约 140.114→198.152 texel/m，横向维持约 198.152；同条件近景差异较明显，中远景和暗光下差异有限。

本轮可玩证据用于检查演出流程和木构候选共存，不能据此确定实际木纹尺寸、正常运行 mip 或 GPU 成本，也不等于正式美术采用。右接合仍是局部构图候选，左端仍未完整支撑；不把它称为历史建筑、榫卯或特定皮影流派复原。

本轮 VisiblePlay-Run1 已取得并查看第一轮五个环境状态的固定 POV 原生截图，依次为 Dormant、SunAwakened、ChaseAwakened、FinaleReady、ForestComplete，见 [本轮五态画面](FRAME_BEAM_TOP_UV_DEV.html)。完整观察器和实际退出均通过。画面仍包含 Editor 开发界面，木梁局部差异有限；梁顶的近中远 UV 比较仍查看上一阶段图册。

## 交付边界与下一步

本轮只增加独立 Dev 样本和入口，继续复用已有免费／开源资产、木材材质及纹理。没有新资产下载或付费依赖。完整剧场美术、实际纹理尺度、5–8 分钟首次玩家盲测、包内三轮完整通关及 Shipping 尚未完成。

用户要求 10 月 21 日前提交，每天投入 6–8 小时。下一步按提交冲刺计划优先完成正式作品入口、可投影的夸父皮影和完整戏台：18 日冻结内容、20 日完成提交。梁顶 UV 等局部细化暂停，现有候选与原 B 图册留作参考；不因增加 Dev 样本扩建场景。

完整证据目录：`D:\灯影山海\Saved\Audit-2026-10-13-FrameBeamTopUVDev`。目录及包名沿用已冻结的 `20261013` 身份，实际本轮进展日期按 2026-10-14 记录。

回退入口就是原 `Start-FrameBeamCandidate.cmd` 和其固定旧包。原地图、原网格、旧封存包与失败证据保留；最终文件集合、旧产品保护、文档旧前缀和 Git 状态以本轮 `FINAL.json` 实际核验为准。本报告不预先宣告最终发布成功。

*永远不要以牺牲架构设计为代价追求功能；永远不要基于猜测进行权衡——必须与我确认。*
