# 新夸父 P02 身形提示 B：独立 Dev 候选验证

2026-10-18。用户明确选择 **B：躯干＋上衣前后片**。负责人：项目负责人；Codex 执行实现、构建和验证。此记录接 `P02_NEW_KUAFU_GUIDE_MEASUREMENT_20261018.md`，不替代之前的原始测量或失败记录。

## 玩家可见结果

第二幕身体开放角标按新夸父的 `TorsoSkin + RobeBack + RobeFront` 三个分件校准。目标参考保留原 8 cm 留白；头部弧线、下摆和手杖保持独立。只改变参考的中心和半宽高，谜题成功仍由原参数区间与保持时间判定。

| 参数 | 保存的 B 值（幕面世界 cm，显示近似值） |
|---|---:|
| BodyY | -78.25275 |
| BodyZ | 187.87287 |
| BodyHalfWidth | 65.97075 |
| BodyHalfHeight | 64.91701 |

使用原共享父材质的独立 Material Instance，没有新 shader graph、static 分支、贴图、WPO 或透明层。其他 scalar/vector/texture/static switch 有效值、override 状态、父材质与 base overrides 都经过比较。static mask/layer 由原样 duplication 保留，未单独反射读取，也没有任何对应 setter 调用。

## 实际修改与隔离

- 新图：`/Game/DengYingShanHai/Dev/P02KuafuGuide/Maps/LV_P02KuafuGuideLab`。
- 新 MI：`/Game/DengYingShanHai/Dev/P02KuafuGuide/Guides/MI_DY_P02KuafuBodyFit`。
- 源为 `ForestCanopyWide` 图，只将 P02 Guide 的材质槽 0 换成新 MI；36 个 Actor 的场景、显式依赖、三幕 Definition、15 Hz、控件、轨道、灯光、镜头、Forest 和 GameMode 都经过源/新快照比较。
- `DYDevEntryPlayerController.cpp` 只在既有 Dev 精确地图名单中增加新图，保证菜单开始和重演可用。仍限制 Game/PIE 上下文，Shipping 继续拒绝 Dev 菜单。
- `DYEntryLoopAutomationTests.cpp` 扩展现有身份测试，覆盖新图 Game、PIE、Editor 拒绝、后缀和查询串拒绝。

原 `L_DY_Main`、原 `ForestCanopyWide` 图、共享 `MI_DY_P02BodyFit` 的磁盘哈希保持。没有采用夸父 v12、改骨架/姿态/杖端点或替换正式地图。

## 验证

| 项 | 结果与原始证据 |
|---|---|
| Editor / Game 编译 | 均退出 0；工作区 `P02GuideAudit-20261018/EditorBuild-B-Run1.log`、`GameBuild-B-Run1.log` |
| 入口自动化 | 15 succeeded / 0 warnings / 0 failed / 0 notRun；`EntryTests-B-Run1/Report/index.json` |
| 保存候选 | `Author-B-Run3` 只保存新 MI 和新图；原产品 577 项未变 |
| 独立进程冷读 | `Cold-B-Run1`，36 Actor，场景和材质差异列表均为空；579 项文件与精确集合未变 |
| 实际 RHI PIE | `Play-B-Run1/PLAY.json`，10 项实测检查、4 张原始 PNG、实际 EndPIE、零脏包；579 项未变 |
| P02 控制反馈 | 实际灯单独到位、偶单独到位、精确目标 Holding、保持中断归零，然后由原逻辑成功推进 |
| 原三幕因果 | 原 Director 正常按序推进，实际杖尖接触和森林资源产生后进入完成态，再通过原 Controller 重演回同图干净标题状态 |
| Windows Development 包 | UAT Cook/Stage/Package/Archive 退出 0；49 文件、1,091,560,627 bytes；清单含新图、新 MI、`SK_DY_Kuafu_Refined` |
| 包内启动 | `Smoke-Run1`，实际加载新图，1280×800 菜单 PNG 已解码和目视检查，无 Fatal/Unhandled，运行 15 秒后原生退出 0 |

原生日志根：`D:\灯影山海\Saved\Audit-2026-10-18-P02Guide`。本轮完整包：`C:\UEProjects\DYBuilds\P02Guide-B-20261018-Run1\Windows`。包内 smoke 在其相邻 `Smoke-Run1` 目录，不修改所测包的资源和 exe。

实际 PIE 截图包含编辑器外框，包内菜单截图是独立游戏的 1280×800 画面。已查看 P02 精确目标、完成态与菜单；这不是最终美术签收。PIE 驱动只提交原公共控制意图，不驱动 Resolve、Contact、Growth 或完成回调，不改变 POV、目标、容差或保持时间。完成门控还要求 P02 Holding/中断检查和专用截图确实存在，不能只因最终成林就报告 P02 通过。

## 启动与回退

在资源管理器双击：`C:\Users\lenovo\Documents\ChatGPT\数媒游戏开发 2\P02GuideAudit-20261018\Start-P02Guide-B.cmd`。它固定打开以上 Development 包和新图，不依赖 Editor 或运行时 Python。点击“开始复演”，沿用 E / A / D / R。

回退可直接使用原开发图或原包。必要时从 `Candidate-B-Baseline` 恢复本轮两处源码与旧 Editor DLL，并同步重建对应目标；该目录保留了修改前文件。本轮没有覆盖已有资产或旧构建。

## 尚未验证

本轮没有替用户验证包内实体键鼠完整三幕、首次玩家可读性、5–8 分钟、其他分辨率、目标设备性能、三轮完整通关或 Shipping。正式地图的新夸父/舞台美术集成仍为后续任务。

保留的工具失败：Author Run1 因 UE 未反射 `expression_guid` 在保存前停止；Run2 因本机 UE 5.8 scalar setter 实际写值但始终返回 false，在保存前停止。核对安装源码后改用实际值和 override 读回验证，Run3 成功。原始报告均保留。包 smoke 的第一次后处理元数据写入有 PowerShell 布尔字面量错误；从原生退出和日志补写摘要，没有重跑或改写原始证据。
