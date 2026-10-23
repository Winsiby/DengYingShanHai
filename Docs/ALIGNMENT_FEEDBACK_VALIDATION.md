# 灯速与就位反馈｜独立 Dev 样本

日期：2026-10-10。唯一人类作者及负责人：用户；实施、自动验证与文档辅助：Codex。

## 实际变化与架构

- 新地图灯速 0.2625 归一化单位／秒，是冷读旧 Readability 实例 0.35 的 75%；偶保持 0.28。不是全局输入倍率，不改 E/A/D/R、惯性、吸附、镜头或 Input Action。
- 原底部区域显示灯／偶“已就位／待调整”。灯单独正确提示“灯已就位，继续调偶”；偶的位置及所需姿态共同正确提示“偶已就位，继续调灯”。第一幕只显示灯。
- 联合有效提示“灯偶已到位，松开 A / D，保持此刻”，就位文字暖金强调；细进度条仅读取原 Holding 时钟的比例，不是像素重合率或 Result.Progress。打断后提示“贴合被打断，轻调后再保持”，条隐藏归零；换幕、复位、非 Playing、结束与重演清理旧显示。
- `Evaluator/Director → Stage 只读投影 → HUD 显式订阅 → UMG`。Stage 实例 opt-in 默认关闭，仅新地图启用。同 Near 的单项状态变化与同 Holding 的计时变化仍更新；旧 Blueprint 离散事件去重不变。无 Widget Tick、世界扫描、第二判定器或第二成功时钟。HUD 迟到读取当前快照，替换／销毁解绑，通知重入时重读 settled getter。
- 未修改三幕目标、容差、15 Hz、1.25 秒 Dev 保持、2 秒 Dev 题签、A 端＋Z70、主灯／曝光或落杖→真实接触→真实成林→Complete。没有新增 paid 资源、插件或正式美术。

独立地图 `/Game/DengYingShanHai/Dev/AlignmentFeedback/Maps/LV_AlignmentFeedbackLab` 只是开发副本，不增加竞赛场景。新旧地图 31 个 Actor 的类与数值 Transform 相同，只有新灯速度和新 Stage 开关不同。冷加载确认 Director、环境、forest 和 3 guides 都属于新世界；共享 BP CDO opt-in 仍为 false。

## 分层验证与证据边界

- 原生 Editor Development 编译实际退出 0，全量 **125 succeeded / 0 failed / 0 notRun**，测试进程退出 0。原 113 项保留，新增 12 项覆盖投影、位置＋姿态、非有限数、保持计时分离、同 Near 更新、去重、激活清理、EndPlay、HUD 迟到／替换／解绑和多播重入。
- `AssetCreate-Run3` 成功、`ColdVerify-Run1` 成功，旧 Content／Config 哈希一致。早期 AssetCreate-Run1/2 错把 Python Struct 临时内存地址作为 geometry 字符串比较，改为数值数组后通过；GeometryInspect-Run1 因未保存新地图不存在而失败。失败记录保留，未为通过检查改场景。
- `VisiblePlay-Run1` 观察器在 base entry 初始化前访问 step_time，3 checks 后失败，0 forests；实际退出 0 不等于测试通过。仅修复观察器初始与重演状态 guard，不改游戏产品逻辑。
- `VisiblePlay-Run2` 初始化已修好，但观察器调用未向 Python 暴露的 ProgressBar.GetPercent，4 checks 后失败；经本机 UE5.8 ProgressBar.h 核实，改为读取反射 Percent 属性。仅修工具，不改产品，失败证据保留。
- `VisiblePlay-Run3` **PASS：53 checks、2 轮完整三幕、2 次真实15枝成林、1 次实际 OpenLevel 重演、4 次 Holding 打断归零、33 张截图**；实际进程退出 0。每轮 P02/P03 都强制验证灯单独就位、偶单独就位、真实保持条和打断；不能因完整通关而跳过这些覆盖。首次／重演开始等待、真实按钮、0.15/0.15 入幕、P02 当前幕复位、非 Playing 隐藏／归零与旧 Token 拒绝均沿用真实路径。
- 已视觉检查 Run3 的灯单项、偶单项、联合保持与打断截图：中文清晰，底部同一提示区无裁切，细条出现／隐藏与状态一致。此为 2560×1528 Editor 截图，不冒充独立包不同窗口比例验证；真实物理 E/A/D/R 手感仍须用户体验。
- `Package-Run1` Win64 Game Development 经原生 UAT fresh Build/Cook/Stage/Pak/IoStore/Archive 成功，实际退出0，49个产物共1,042,883,010字节，逐项SHA登记；显式Cook根为新地图，15个预期依赖均在实际UFS清单。没有 CookAll／Config 修改；现有默认配置仍附带旧 InteractionLab 与 Engine Entry，不能把它们误报为本次新增竞赛场景。
- `FirstFrame-Run1` 独立原生包实际运行，1280×800截图，原生20秒正常退出0；已视觉检查开始面板中文与按钮同字号，无文字裁切。开始前尚能看到原题签／引导字幕属于保留的旧Cue行为，本轮未改其时序。截图和首帧证明不是包内完整通关签收。构建身份保持不可变，首帧验证另存审计结果，不重打包已测产物。
- `Launcher-Run1` Auto／Package／EditorGame／CMD 四项只读 DryRun 全通过，实际退出均0。前三项通过 Windows PowerShell5.1 实际解析／执行；EditorGame 明确带 -game，其余均固定选择新 Development 包。CMD 包装链实际读取同一精确地图，未启动游戏、执行Python或改全局环境。发布的PS1使用UTF8 BOM以支持中文路径。

可见脚本通过真实 UButton OnClicked 和公开参数请求，由原 Director／Stage／Blueprint 完成演出，不伪造 Resolve、接触、Token、forest 或 Complete，不写相机、保存资产或驱动演出时间。它验证保存速度，不是物理 A/D 按键测速；Editor 全流程也不是 Windows 包内真人签收。物理键鼠、不同显示比例、首次游玩理解度、5–8 分钟、包内完整真人通关与 Shipping 均未签收。

## 打开、对照与回退

新版入口 `D:\灯影山海\Start-AlignmentDev.cmd`，在资源管理器双击；聊天链接可能只预览代码。默认固定新包，不选“最新包”；-EditorGame 明确使用本机 UE -game，-DryRun 不启动。不要直接打开包内裸 exe，它未显式选择本次地图。

旧版对照 `D:\灯影山海\Start-ReadabilityDev.cmd` 仍固定旧 ReadabilityDev-20261009-Run1 包，旧 EntryLoop 也保留。源码默认 off 使旧地图 UI 文案保持。

备份与 228 个原文件基线位于 `D:\灯影山海\Saved\Audit-2026-10-10-AlignmentFeedback\Before` 和 BEFORE.json。优先用旧不可变包回退；源级回退仅处理本轮白名单并重编译，不覆盖无关未提交文件。本轮无 Git 写操作、删除、系统权限／全局环境修改。完整证据、失败记录与实际退出码均保留在同审计根目录。
