# 第二幕身形提示校准与分层验收（2026-10-10）

## 玩家可见结果与范围

项目为独立开发者《灯影山海》的 UE 实时光影交互叙事 Dev 样本。用户已体验上一版，反馈“效果不错”，同时指出第二幕幕上提示框不贴偶影；此反馈不是本次修订后的人工签收，也不代勾其他未检查项目。本轮唯一目标：让第二幕目标身形参考更贴合实际躯干影子。

负责人：用户为唯一项目负责人；本轮 Codex 实施与验证，没有新增团队成员或交给 WorkBuddy 修改产品。没有新增场景、按键、外部素材或付费依赖。

保留头部弧线，身体用更紧的开放角标；杖影不要求进入身体框。角标是构图参考，不是像素重合率，也不是全部容差内状态的空间包络。玩家仍以底部灯／偶“已就位”和保持条判断当前逻辑条件，容差内即可成功，不必逐像素贴框。

## 根因及实测

原第二幕框把头部＋躯干包围范围、单变量容差位移余量和留白混合在一起；不含手杖，却容易被理解成完整偶的轮廓。其宽度约为头身投影包围范围的 1.94 倍，框的上边也被头部抬高，因此不是整体偏移，而是范围和视觉语义不一致。

新测量来自本轮实际 PIE 世界：生产投影函数、实际主灯发射点、幕布面 X925、目标 `.72/.80`、姿态 `P02_StrideReach`。躯干实际网格为引擎 Cube，投影其 8 个真实顶点，固定加 8 cm 留白。采样同帧恢复先前控制值，未请求 Resolve 或伪造成功。另测四个联合容差邻点，保留原始记录，不把它们扩大为新参考框。

| 材质参数（cm） | 原 P02 实例 | 新独立实例 |
|---|---:|---:|
| BodyY | -15.209475 | -15.261056 |
| BodyZ | 246.356720 | 176.080990 |
| BodyHalfWidth | 60.113148 | 32.133706 |
| BodyHalfHeight | 158.008759 | 87.733026 |

框外尺寸由约 120.23 × 316.02 cm 变为约 64.27 × 175.47 cm。新的 Y/Z 中心和宽高按躯干测量，不追随玩家当前位置，不通过动态移动提示去伪装贴合。

原始数值：`Saved/Audit-2026-10-10-P02GuideFit/ProjectionBefore-Run2/FIT.json`。

## 修改、保护与回退

修改范围只有：

- 新 `Content/DengYingShanHai/Dev/AlignmentFeedback/Guides/MI_DY_P02BodyFit.uasset`：复制既有免费项目内 P02 实例，仅四项 Body 标量不同；父材质和其他参数不变。
- 既有 `Content/DengYingShanHai/Dev/AlignmentFeedback/Maps/LV_AlignmentFeedbackLab.umap`：只换 `GuideP02` 的材质槽 0，不改变 Actor 类或 Transform。
- `Scripts/Start-AlignmentDev.ps1`：固定指向新 Run2 包，菜单和按键不变；根 `Start-AlignmentDev.cmd` 不修改。
- 新旧包比较入口 `Start-AlignmentDev-Run1.cmd` 与 `Scripts/Start-AlignmentDev-Run1.ps1`，后者是本轮前 helper 的原始字节副本；默认 Auto/Package 使用旧 Run1 包，EditorGame 则使用当前工程，不是旧源码回退。
- `Docs/TECH_SPEC.md` §18 与本文。

本轮未改 C++、Config、DataAsset、Input、Blueprint 图、旧 Readability 实例／共享父材质、P01/P03、阴影、相机、灯具／偶的 Transform、灯速 `.2625`、偶速 `.28`、15 Hz、目标／容差／保持、三幕转换、重演、A 端＋Z70 或 Drop→Contact→Forest→Complete。没有删文件，没有写 Git 暂存区或提交。旧版本包保留。

前置快照：审计 `BEFORE.json` 与 `Before/`，234 项既有文件，只有当前地图、helper、TECH_SPEC 三项允许差异；另外 231 项必须哈希一致（不读取许可登记文件）。恢复源码入口与地图之前，先核验没有后续编辑，再使用准确 `Before/` 文件，不覆盖后续用户改动。仅体验比较时直接启动固定旧 Run1 包，无须回写项目。

## 验收证据

审计根为 `Saved/Audit-2026-10-10-P02GuideFit/`。以下结果分层记录，不混合为人工盲测结论：

| 层级 | 本轮实际结果 | 证据目录／记录 |
|---|---|---|
| 原生构建与自动化 | 编译完成；125 succeeded / 0 failed / 0 notRun；实际测试进程退出 0；78 个原生文件哈希冻结 | `Native-Run1/RESULT.json`、`SOURCE.json`、Build/Test 日志 |
| 实测与原版对照 | 成功测量目标躯干实际顶点，恢复控制；原图为首次 Holding，非新图精确目标的逐像素对照 | `ProjectionBefore-Run2/FIT.json`、`Result.json`、原 PNG |
| 资产与冷加载 | 创建成功仅保存新 MI＋当前地图；新进程冷验证成功且无资产保存；P01/P03、父材质、非 Body 参数及速度未变 | `AssetCreate-Run1/Result.json`、`ColdVerify-Run1/Result.json` |
| 实际可见流程 | 57 项检查、35 张非空原始 PNG；两轮三幕、一次实际同地图重载、两次真实成林、4 次保持打断；目标贴合检查与精确目标截图各两次；实际 UE 退出 0 | `VisiblePlay-Run2/Result.json`、`EXIT.json`、`EVENTS.jsonl` |
| 画面审阅 | 已检查两轮精确 `.72/.80` 原图；角标贴躯干、头弧保留，实际杖影独立；幕后原因／幕上影子与原就位反馈同时可见 | `10-P02-ExactTarget-Fit-Cycle1.png`、`27-P02-ExactTarget-Fit-Cycle2.png`、`VISUAL-REVIEW.json` |
| 独立打包 | UAT 实际退出 0；固定新 Run2，49 个归档文件、1,042,885,072 bytes；Pak／IoStore／两份 manifest 完整，实际 UFS 包含新 MI、共享父材质、三组题目、林形和中文字体 | `Package-Run1/EXIT.json`、`ARTIFACTS.json`、`LAUNCH.json`；Run2 `ALIGNMENT-DEV-BUILD.json` |

打包仍附带既有默认 `LV_InteractionLab` 与引擎 `Entry`，没有修改 Config 去清理这些旧引用；启动器明确进入 AlignmentFeedback 地图。不把 Cook 附带项算作新竞赛场景。包身份记录在构建结束时冻结；首帧、启动器和画面审阅另记，不回写包身份的 `GameplayVerified=false`。

独立包真实首帧检查 `FirstFrame-Run1/RESULT.json`：PASS，1280 × 800 PNG，原生 `-seconds=20` 退出 0，无 Fatal／Unhandled；已实际查看标题、中文菜单和一致的按钮字号。`ReviewPending=true` 是初始机器报告字段，后续人工式图像审阅单独见 `VISUAL-REVIEW.json`，不覆写原报告。没有启动包内 Python，也没有声明包内第二幕键鼠验收。

四项实际启动 DryRun `Launcher-Run1/RESULT.json` 全部退出 0：Windows PowerShell 5.1 下 Auto、Package、EditorGame，以及实际 `.cmd` 包装链。前三种打包选择（Auto／Package／CMD）精确断言 Run2 的 PackageRoot 与内部 Exe；EditorGame 明确携带 `-game` 与当前地图，不误入仅编辑器界面；所有 DryRun 均未启动游戏。

旧版比较入口另有 `ComparisonLauncher-Run1/RESULT.json`：helper 的 Auto 与实际 `.cmd` 两项 DryRun 均通过，精确指向原 Run1 包；没有运行额外游戏。

交付保护记录为 `FINAL.json`：核验 231 项未经批准的原文件、78 个原生文件、22 个 Cook 源资产（包括当前地图＋新 MI）、5 个已发布文本文件及旧 Run1／旧 Readability／新 Run2 三套各 49 个归档文件。检查所有真实 PNG、冷加载、流程实际退出、新 Content 仅一项及 Git HEAD／暂存区未变化。最终结果以该记录的实际 `Status` 为准，不以文档代替哈希验证。

## 保留的失败记录

- `ProjectionBefore-Run1`：测试启动器漏复制 `Watch-AlignmentFeedback.py`，导入失败；没有产品资产改动。补齐测试依赖后 `ProjectionBefore-Run2` 成功测量并跑完两轮流程。
- `VisiblePlay-Run1`：产品完成两次真实成林、实际 UE 退出 0，但同帧两次 Shot 请求使两张 JointHoldBar PNG 缺失，证据检查正确判 FAIL。修正子类截图排队：父类本帧已有截图则下一帧再请求精确目标截图；仅测试工具变化，用新 Run2 目录重跑。失败日志及结果保留，不覆写或改成 PASS。

## 仍需区分的边界

脚本使用真实原生流程、公开参数请求和菜单委托，未验证物理 E/A/D/R 或鼠标，未替用户签收本轮体验。独立包首帧仅证明包可启动、字体／开始面板存在与正常退出，不等于包内第二幕全流程人工通过。正式美术、声音、5–8 分钟首次玩家盲测、其他屏幕比例和 Shipping 仍在后续里程碑，不由本次视觉校准扩项。

## 打开方法

新版：在资源管理器中双击 `D:\灯影山海\Start-AlignmentDev.cmd`，点击“开始复演”。聊天文件预览可能显示代码，实际运行应在资源管理器双击 `.cmd`。

旧版对比：双击 `D:\灯影山海\Start-AlignmentDev-Run1.cmd`。先正常关闭正在运行的游戏，再打开另一版，避免新旧版本混淆；入口不强行结束进程。

新归档：`D:\灯影山海\Builds\AlignmentDev-20261010-Run2\Windows`。所有审计保存在 `D:\灯影山海\Saved\Audit-2026-10-10-P02GuideFit`，开发测试资产仍在 `Dev/`，不自动进入正式竞赛地图。

## 后续作者反馈（2026-10-10）

用户在体验后明确回复“效果可以，进入下一步”，记录为本轮第二幕身形提示的作者体验接受。上文原机器报告与历史 `FINAL.json` 不覆写；此反馈不等于新增首次玩家盲测、5–8 分钟、其他显示比例或 Shipping 签收。

后续基础声音 Dev 继续保留本轮 `MI_DY_P02BodyFit` 四项参数、头部弧线和实际躯干参考，旧 Run2 包／启动器不改。当前源码地图会增加一个独立声音表现 Actor，原入口 EditorGame 回退属于当前源码，不是旧无声源码；需比较原版时使用原入口固定打包版本。新声音范围与证据见 `AUDIO_DEV_VALIDATION.md`。
