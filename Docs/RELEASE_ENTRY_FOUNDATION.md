# 《灯影山海》正式主地图技术入口

日期：2026-10-14。用户是本项目唯一人类作者与负责人；Codex 辅助实现、检查与归档。按 10 月 20 日内部提交目标推进。本步不声称正式美术、5–8 分钟盲测或竞赛作品已经完成。

## 本步结果

原 TopUV 批次已关闭并保留。现在有独立主地图 `/Game/DengYingShanHai/Maps/L_DY_Main` 与 `/Game/DengYingShanHai/Core/BP_DYReleaseGameMode`。默认游戏地图指向该主地图；编辑器启动图、全局 GameMode、渲染设置均保持原值。

新 `ADYReleaseEntryPlayerController` 继承已有菜单和三幕流程，仅覆盖精确地图身份。正式入口接受本主地图的 Game／PIE 身份并返回同图重演目的地，不接受任意路径或八张旧 Dev 图；旧 Dev 控制器的 Shipping 限制保留。没有复制流程状态、添加新按键、管理器、Tick 扫描或运行时 Python。

创建前已备份旧 header 与配置；原场景的 35 Actor／37 个场景、玩家及流程字段组逐项比对。唯一允许的两项场景标量差异为 `_flow.gm` 与 `_flow.controller`。GameMode 的 Pawn、HUD、中文字库、状态、会话等观察到的默认项保留。独立冷读验证成功，验证阶段零资产／地图保存。

## 已完成的实际验证

- Editor Development 编译实际退出 0；全项目 **161 succeeded／0 failed／0 notRun**。原 158 项未改，新增正式入口身份、拒绝错误上下文、真实临时世界中的继承路由三项测试。
- 正式主地图实际运行：65 项流程、35 项环境、各 10 次独立柱／梁观察通过；两轮真实成林和一次实际 OpenLevel 重演；两轮 UE 游戏 master mix 导出核验通过。
- 41 项控制／焦点／复位／跨幕释放／重演／EndPlay 清理通过。它们是语义操作测试，不等同于人手键鼠、听觉或首次玩家验收。
- 首轮 VisiblePlay 因固定机位检查失败而保留；其日志确有非零控制器视角变化。相同代码与阈值的 Run2 通过。未修改产品镜头或放宽容差，未把失败记录改成成功。
- 360 个源码、配置、资产、脚本及文档产品文件在测试前后核对一致（限制登记文件排除访问）。旧 1076 个归档文件、15 个原始来源文件及 24 个隔离来源文件已有冻结记录。

Development Game 与 Shipping Game 均已实际 Build／Cook／Stage／Archive；两次 UAT 都退出 0，分别执行一次原生容器 listing 和主／global 全读取校验。主容器各 2027 chunk、299,292,758 B 解压读取；global 各 1 chunk、3,224,289 B。42 项核心资源加 Engine Entry 的 43 个不同 export bundle 验证成功；实际 Cook 地图为主地图与继承的 Engine Entry，共两张，不把默认 Engine Entry 当作第二个可玩关卡。

Development 归档 50 文件、1,070,714,095 B；Shipping 归档 32 文件、713,062,879 B。Development 的原 RESULT.json 在所有包校验完成后，因 OrderedDictionary 的 Bytes 求和错误记录 FAIL；原记录保留，COMPLETION-REVIEW.json 逐项只读重核原生退出、全部文件／容器／源文件，确认只限统计元数据错误，没有重打包或改包。Shipping 使用已修正求和的脚本，直接完成 PASS。

启动器 9 项真实 Windows PowerShell 5.1 惯性 DryRun 通过（3 接受、6 拒绝），实际 D 盘两个包的 DryRun 都退出 0。先前沙箱／单项记录／PS5 JSON 数组与模块路径的工具失败均保留，均不代签游戏通过。启动器只给自身子进程使用 Windows PS5 模块路径，不改变全局设置或执行策略。

已真实启动 Development 包且没有传地图覆盖，日志载入主地图。窗口检查遇到 Windows 防火墙许可弹窗，按 computer-use 的安全限制停止 UI 操作并交由用户手动取消。尚不声明无遮挡的包首帧、按钮点击后画面、Shipping 实际启动或完整包通关已通过；这些状态待实际观察补记。

本轮实际构建使用 MSVC 14.51.36260（目录14.51.36231）与 SDK10.0.26100.0；UE 报 compiler 非 preferred 警告，但本轮三种构建实际完成。未自行改工具链、SDK 或全局环境，不以环境文档历史14.50记录覆盖这次实际构建事实。

## 玩家打开位置

已发布两个独立 Windows 包启动文件：

- Development：[Start-ReleaseEntry.cmd](/D:/灯影山海/Start-ReleaseEntry.cmd)。
- Shipping：[Start-ReleaseEntry-Shipping.cmd](/D:/灯影山海/Start-ReleaseEntry-Shipping.cmd)。

菜单仍是技术候选样本，尚保留真实 Dev 说明。正式美术与叙事收尾后才移除这些说明。旧固定 TopUV／B 包作为回退保留，不删除旧文件。不要把 Codex 里的脚本预览误当作执行；在资源管理器双击实际启动文件。本机先正常关闭其他 UE／游戏窗口；防火墙许可弹窗请人工处理，单机演出不要求允许网络访问。

## 免费资产准备与视觉结论

[本轮 P0 素材报告](/D:/灯影山海/Saved/SourceReadiness-20261014/Kuafu/P0_SOURCE_READINESS.md)及其同目录 SOURCE-ARCHIVE.json 已真实归档 35 个文件。Commons 原 PNG、自动矢量 SVG 和公版来源页面均有实际下载与结构检查；原插图的题名、云纹、日轮不是人偶的一部分，也没有独立手杖。全页自动描摹的 1067 条 path 不是可直接导入的关节人偶。

已检查当前结束画面：中文菜单可读，林影与同一落杖状态连续；截图包含编辑器外框，不能替代原生打包首帧。人物 Cube／Sphere、灯具基本形体、场景灰块及 Cylinder 枝形仍明显是占位美术，**高质量正式画面尚未达标**。不以截图数量或逻辑测试数量替代这一结论。

下一项按已确认冲刺顺序：把已归档古籍参考清理成可用的夸父薄片人偶和独立手杖，先验证投影轮廓、关节及实际 A 端，不改变目标参数、真实阴影或 A 端至 Z70 的接触成林链。复用已取得的免费木地板、屏风与柱梁；不重复下载、不购买资产、不引入复杂全身骨骼或新机制。

## 本轮证据与回退

总审计目录：`D:\灯影山海\Saved\Audit-2026-10-14-ReleaseEntry`。

关键记录：`Native-Run1/RESULT.json`、`probe-Run1/Result.json`、`create-Run1/Result.json`、`verify-Run1/Result.json`、`VisiblePlay-Run1`（失败原件）、`VisiblePlay-Run2`（实际通过）、`ControlProbe-Run1`、`BEFORE.json`、`AFTER-CREATE.json`、`PRESERVED-SOURCES.json` 与配置／代码发布记录。

本轮没有删除、Git 提交或暂存、覆盖原地图、读取／哈希 `Docs/LICENSES.md`、改变全局环境或安全权限。旧 header／DefaultEngine.ini 的 Before 副本保留。旧已封存打包版本可继续回退；旧需要 live 源码完全匹配的编辑器启动方式可能因当前新增源码而拒绝启动，这是已有保护策略，不能冒称所有旧启动模式均未受影响。

仍需完成：正式人偶和灯幕／剧场／林影美术、正式声音来源适配、完整 5–8 分钟首次玩家盲测、最终包三轮无阻塞通关、视频与材料、最终授权／AI 使用说明、人工比赛系统提交。不得把本步技术候选包直接标注为竞赛最终成品。
