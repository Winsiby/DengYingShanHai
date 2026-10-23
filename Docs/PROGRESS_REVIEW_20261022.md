# 灯影山海 · 项目进度复核（2026-10-22）

负责人：用户本人；Codex 辅助核查、实现与验证。本文不使用整体完成百分比。

本报告第1节保留本轮美术修改前已核实的 **Run100 Shipping** 基线：只读核对工程、打包身份、原生自动化日志、已有截图与运行探针。第5节同步主代理随后已核验的A5实现与新Shipping构建结果；两轮辅助四幕、重演、音效事件、正常退出与真实CMD入口已完成技术核验，人工验收与当前性能仍开放。

## 1. 修改前基线与进度（Run100）

| 项目 | 状态 | 已有证据与实际边界 |
| --- | --- | --- |
| Windows Shipping 包与公开入口 | 已核对 | `Start-ReleaseEntry-Shipping.cmd` → `Scripts/Start-FormalShipping.ps1` 实际指向 Run100。原生 EXE、源主图哈希与包内 identity 一致，实测31产物 / 751,237,006字节；不是仅凭文件夹名称判断。 |
| 原生自动化 | 已有通过记录 | `Saved/Logs/AutomationV31.log` 本次独立统计176 Success / 0 Fail，日志含176 tests performed及退出0。未把原生自动化等同真人试玩。 |
| 四幕连演与声音事件 | 自动接口回归通过 | FORMAL §9.32记 Run100 四幕到 `phase=4 chapter=4/4`；本次读到运行探针内两次完整终态。SfxProbe确有9条，与Run100记载时刻一致。 |
| 同图复演 | 自动接口闭环通过 | 既有回归记录 `REACHED_PHASE4=True`、追加25行，运行探针含两次完整终态；后续取景又追加第三轮部分，因此当前通用CampaignProbe不能再描述为“正好50行”。 |
| A组美术 | 部分落地 | A1影窗、A2台口、A4门楼走廊、A3墙体/壁柱/栏杆、A6贴图拼板和A5十二盏路径纸灯已集成；Glow已由2.6降为1.7。落地不等于全部原brief要求或最终审美签收。 |
| B/C组美术 | 未完成 | B1/B2试作失败后整体隐藏回退；B3山石、C1三具新偶、C2器乐、C3图鉴插图的实现仍待完成。24张概念图本身不等于UE资产实现。 |
| 当前包性能 | 部分 / 当前未验证 | 有旧D2 Development的1080p CSV，当前Run100新增美术后的帧时间未复测；没有当前Shipping GPU帧时间证据。 |
| 首次玩家与目标时长 | 未验证 | 未查到当前四幕版独立首次玩家5–8分钟、目标机三轮真人无阻塞完成的证据。纯按键计算、自动演出耗时及有人协助流程不能替代。 |
| 许可、AI记录与提交件 | 部分 | 字体FONT-001/002/003及SELF-001–006有登记，包内附SourceHanSans许可文本；新A组纹理与概念图记录尚未在主清单逐项同步，最终提交核验未关闭。 |

### Run100身份（本次实际复算）

包：`D:/灯影山海/Builds/FormalMain-Shipping-20261020-Run100/Windows`

原生EXE SHA256：

`1710A30AD8FC8E6488ADE4A60AC8855A88D5A656783B66B9BD90927172D9A8E4`

主图 `Content/DengYingShanHai/Maps/L_DY_Main.umap` SHA256：

`67B5E713693EF86A3EE99B7410C1A3B99866C836972C93D4E83C3B3C621C3449`

31产物 / 751,237,006字节，与identity一致。Run96为751,121,991字节，两者差额为 **115,015字节**；FORMAL §9.32旧写26,648字节是算术笔误。

## 2. 性能与体验的未覆盖项

[D2性能报告](D:/灯影山海/Docs/FORMAL_PERFORMANCE_20261020.md) 的实际CSV仍存在：`Saved/Audit-2026-10-20-V21/Perf-D2d/User/Saved/Profiling/CSV/Profile(20261020_110228).csv`，18,000帧，37,081,401字节。稳定态143.36 FPS、FrameTime均值6.976 ms、P99 8.103 ms、GPU均值6.202 ms。

这份数据对应2026-10-20的D2 Development内容及程序接口流程，不能替本轮A5修改后的新Shipping包、独立真人输入或赛事目标机签收。CSV运行退出777003的已知限制仍保留；Shipping外部采样权限问题没有在本次审阅中解决。

[可玩性表](D:/灯影山海/Docs/ACT_PLAYABILITY_20261021.md) 第10节才是携带机制后的口径：每幕第2/3步继承上一步定义的Target，纯按键量约24.1秒；它不含理解、瞄准、走位与过渡，不能据此推断完整体验时长。首次玩家、手感、静音可理解性、声音听感和最终美术仍需用户组织验收。

## 3. 美术进度与本轮执行边界

- **已落地但有缺项**：A1只有布纹BaseColor，NormalDX/ORM未补，旧M03框与A1框仍有共存记录；A6当前以贴图表达板缝，尚非brief要求的独立几何板缝与倒角。
- **已失败并回退**：Run99的B1/B2在真机读成青灰平板与尖刺；Run100隐藏576个ART_B1/B2演员、恢复328个球形树冠/灌木。隐藏演员仍在工程中，不能称B组已完成或已降低Cook/运行开销。
- **本轮A5局部优化已实现并完成构建**：8处外墙/檐下/屋顶装饰球形灯已换为自制八角纸灯；实际窗口两轮辅助四幕、重演和正常退出已核验。变更与边界见第5节及[本轮美术优化记录](D:/灯影山海/Docs/ART_POLISH_20261022.md)。
- 本轮不因美术任务更改四幕机制、灯偶轨道、投影净面或通行坐标，不重新启用失败的B1/B2基本体方案。

## 4. 文档口径与交接

Run100历史基线以[FORMAL SHIPPING §9.31–9.32](D:/灯影山海/Docs/FORMAL_SHIPPING_20261020.md:626)、[美术落地进度](D:/灯影山海/Docs/ART_BACKLOG_20261021.md:108)及当时实际包身份为准；本轮最新A5结果以第5节和[ART_POLISH_20261022.md](D:/灯影山海/Docs/ART_POLISH_20261022.md)的后续验收记录为准。

`DEVELOPMENT_PLAN.md` 的“最新/当前进度”仍夹有10-03/10-10段落，末尾仅追到10-19；`BASELINE-V21.md` 含旧SHA/Run27与已被替代的重置口径；ART_BACKLOG前段“Glow2.6待降”已被后段1.7完成记录替代。GDD正文三互动与附录A四幕之间、以及上层AGENTS的三互动口径仍需统一，不能由本轮美术修改擅自改玩法消除。本轮保留历史正文，仅在DEVELOPMENT_PLAN、BASELINE-V21和ART_BACKLOG顶部添加当前核查入口，并更新ART_BACKLOG已过期的A5待调行。

核查入口：

- [Run100构建结果](D:/灯影山海/Saved/Audit-2026-10-20-V21/Package-Run100/RESULT.json)
- [Run100包内身份](D:/灯影山海/Builds/FormalMain-Shipping-20261020-Run100/Windows/RELEASE-ENTRY-BUILD.json)
- [176项原生自动化日志](D:/灯影山海/Saved/Logs/AutomationV31.log)
- [Run100终态截图](D:/灯影山海/Saved/Audit-2026-10-20-V21/Run100-campaign-087s.png)、[复演终态](D:/灯影山海/Saved/Audit-2026-10-20-V21/Run100-replay3.png)
- [Run100外景](D:/灯影山海/Saved/Audit-2026-10-20-V21/s100-w01.png)、[剧场取景](D:/灯影山海/Saved/Audit-2026-10-20-V21/s100-w04.png)
- 运行探针：`C:/Users/lenovo/AppData/Local/DengYingShanHai/Saved/CampaignProbe.log`、`SfxProbe.log`。它们是会被后续运行追加/覆盖的通用文件，不是不可变的Run100封存记录。
- [许可登记](D:/灯影山海/Docs/LICENSES.md)、[单人制作规则](D:/灯影山海/Docs/SOLO_PRODUCTION.md)

## 5. 本轮A5更新（2026-10-22，技术核验完成）

本节同步主代理已经核验的实现、自动化和构建事实，保留第1节的Run100修改前证据。

| 项 | 本轮结果 | 验证边界 |
| --- | --- | --- |
| 灯具外观 | 8处外墙/檐下/屋顶装饰球形灯替换为自制八角纸灯，共用1个静态网格，768三角面 | 位置、比例及碰撞设置保持；属于A5局部优化。 |
| 灯光调整 | 仅 `DYExt16_FacadeLamp_R` 强度由2600降为650 cd | 未据此改变核心灯偶幕玩法。 |
| 原生回归 | 176项原生测试，0失败 | 自动化通过不等同实窗流程或人工审美验收。 |
| 新Shipping构建 | UAT成功；31产物 / 751,260,131字节 | 实际窗口两轮辅助四幕到终态，重演成功，18次SFX事件，原生退出0；真实CMD入口预检/首帧/退出0通过。当前性能与独立玩家验收未通过自动流程替代。 |
| A5剩余范围 | 14盏吊灯、6盏壁灯尚未制作 | 8处替换不代表A5全部完成。 |

新包目录：

`D:/灯影山海/Builds/FormalMain-Shipping-20261022-ArtPolishA5/Windows`

本轮主图SHA256：

`1ABFC443A79F42B156F36EB65DE274FC7B9C9EBA18DC13FC2BED5232245AD7A9`

黑球树占位、B3山石、C1–C3三具新影偶/器乐/图鉴插图、独立玩家5–8分钟及当前包性能仍未验收。实际窗口流程证据与美术前后对照见[ART_POLISH_20261022.md](D:/灯影山海/Docs/ART_POLISH_20261022.md)，本报告不代签用户体验或最终提交。


当前唯一公开Shipping入口：[Start-ReleaseEntry-Shipping.cmd](D:/灯影山海/Start-ReleaseEntry-Shipping.cmd)，已指向本轮新包；Run100保留为配对回退基线。真实入口首帧及退出回执见 [Public-Verification.json](D:/灯影山海/Saved/Audit-2026-10-22-ArtPolish/Public-Verification.json)。

## 追加：Run118 现状（2026-10-22 09:15）

- 当前公开包：`Builds/FormalMain-Shipping-20261020-Run118/Windows`（31 文件 / 760,801,003 字节，exe `1B0B6A4F…9AC05A73`，map `AEF5A6F9…2F8FEF75`），启动器 `Scripts/Start-FormalShipping.ps1` 已指向 Run118，`-DryRun` = `PASS-PREFLIGHT-ONLY`（31 产物 / 760,801,003 / EXIT 0）。
- 本轮改动只有配光：门脸 `DYTheater_GateLamp_L/R` 5200→3000、`DYExt30_Uplight_00..04` 5200→3600、`DYExt16_FacadeLamp_L` 600→480，门楣灰泥与斗拱投影恢复可读。
- 验证：自动化 176/0（`AutomationV45.log`）；锣鼓 9 cue 到第 4 幕；复演 `REACHED_PHASE4=True` 且探针出现 `phase=4 chapter=4/4 act=3 title=晦明同光`；实机连演到「复演已成」终局面板（`Saved/Audit-2026-10-20-V21/s118b-w07.png`）。
- **性能**：`DY_PERF_PROBE` 83 s 采样 AVG **145.3 fps** / MIN 128.4 / MAX 160.8（1920×1200，1718 actor / 76 灯）。这是"当前包性能"的第一份可复现数字，但仍不等于人工体验验收。
- 入口路面淡色带已归因：运行时生成的引导光带（Run115 mobility 对照、Run116 关灯对照、组件级扫描三条线），与 HUD 文案一致，接受。
- 仍未验收：独立玩家 5–8 分钟可解性、人工观感、BGM/SFX 听感、最终提交。B1 真山体两次失败已正式停止；C1 三具影偶以图鉴插画承载。
