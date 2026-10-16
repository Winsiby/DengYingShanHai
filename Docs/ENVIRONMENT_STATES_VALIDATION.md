# 五态被动环境 Dev 验证（2026-10-11）

负责人：用户为唯一人类作者与体验验收者，Codex 辅助实现与测试。此轮为已闭环灰盒后的环境架构准备，不代表正式剧院美术、文化造型或完整竞赛版本已完成。

## 可打开交付

- 新独立入口：`D:\灯影山海\Start-EnvironmentDev.cmd`，固定 `EnvironmentDev-20261011-Run1\Windows`，不任意选择最新包。
- 新 Dev 地图：`D:\灯影山海\Content\DengYingShanHai\Dev\EnvironmentStates\Maps\LV_EnvironmentStatesLab.umap`。
- 旧可玩入口 `D:\灯影山海\Start-AudioDev.cmd` 及已验收 AudioDev Run3 保持不变，可直接对照／回退。
- 完整证据根：`D:\灯影山海\Saved\Audit-2026-10-11-EnvironmentStates`。首帧、图像、测试、混音与完整最终保护汇总单列。

## 玩家可见变化和实现边界

五态分别为沉寂、引日亮起、逐光扩展、落杖前收束、真实成林完成后的恢复。只改变现有两个不投影环境强调灯：`0/0 → 5000/0 → 3500/4500 → 1750/1125 → 5000/4500 lm`。幕后灯偶和幕上真实阴影依然同框；不修改主投影灯、曝光、灯的位置／颜色／衰减、树形或 UI 布局。

Stage 的新开关默认 false；新地图实例显式 opt-in。旧地图继续三态。环境仍是被动 Actor，无 Tick、Director 依赖、世界扫描或判定。Director 事实经 Stage 映射到环境；第三幕等待结尾、真实接触、开始或中段生长均不能提前变成 ForestComplete，只有旧流程接受真实完整林影才能进入终态。

广播后核对生命周期、激活身份与完整序列快照，处理“Complete 保留同一激活身份”时的阶段陈旧回调。该同 token 环境动态委托重入路径做过独立源码复核并补保护，**尚无直接绑定该动态委托的运行时压力用例**；现有原生实际重入测试覆盖另一条 Stage display 监听者复位路径，不把两者混称。

E/A/D/R、WASD、360 cm/s、灯速 .2625、偶速 .28、15 Hz、目标／容差／保持、2 秒 Dev 题签、镜头、第二幕参考、A 端／Z70、Drop→Contact→Forest→Complete、开始／结束／重演和声音／脚步同步全冻结。菜单代码只额外登记新 Dev 地图的精确身份，不改操作或重演规则。

## 实际验证

| 层级 | 当前实际结果 | 证据 |
|---|---|---|
| 原生编译及全套自动化 | Native-Run2：152 成功，0 失败，0 未运行，进程退出 0 | `Native-Run2/RESULT.json`、Automation、Build/Test-EXIT |
| 地图隔离创建 | 仅复制新 .umap、仅新 Stage 开关打开 | `AssetCreate-Run1/Result.json` |
| 最终冷读 | ColdVerify-Run3：成功、零保存、退出 0；原参数、Actor Transform/class、同世界显式引用、手动三幕、音频与菜单类一致 | `ColdVerify-Run3/Result.json`、SOURCE、EXIT |
| 实际参数驱动 PIE | 65 项既有流程、35 项环境检查；2 次真实成林、1 次 OpenLevel 重演；退出 0 | `VisiblePlay-Run3/Result.json`、ENVIRONMENT_RESULT、EXIT |
| 五态观察 | 两轮均依次 Dormant、SunAwakened、ChaseAwakened、FinaleReady、ForestComplete；真实接触前／初生长／中生长仍 FinaleReady；Complete 后迟到同步不重造树或重放音效 | `ENVIRONMENT_RESULT.json` 的实际检查与 state_changes |
| 固定真实 POV | 40 张真实导出图中包含 5 张五态图；实际 PlayerCameraManager 位置、旋转、FOV 与第一轮所有者相同；模型逐张审查五态可读性 | `fixed_pov_screenshots`、PNG、VISUAL_REVIEW |
| 有声／静音主混音 | 48 kHz 双声道 PCM16；第一轮 70.72 秒，峰值 .24503，RMS -38.84 dBFS，无削波；旧尾音衰减后第二轮 62.08 秒，非零样本 0 | `AUDIO_RESULT.json`、MIX_QA、两段完整 WAV |
| Development 打包 | UAT 退出 0；86 份原生源、32 份资产、53 份验证输入均冻结；49 个归档文件共 1,045,482,676 字节，另加独立身份 JSON | `Package-Run1` 的 EXIT、LAUNCH、ARTIFACTS；ENVIRONMENT-DEV-BUILD |
| 包首帧 | 真实运行新地图，干净 1280×800 标题画面已检查；引擎原生 20 秒退出，日志确认 Benchmarking 原因、退出 0；exe 前后哈希一致 | `FirstFrame-Run1/RESULT.json`、Game.log、01-Title.png |
| 固定入口 DryRun／最终保护 | 发布后最后执行，结果以 `Launcher-Run1/RESULT.json` 与 `FINAL.json` 为准；未通过不交付完成声明 | 两份最终报告 |

原生 fixture 使用零保持的独立测试世界，真实控制、接触与几何证明，不代表真实鼠标／键盘。可见 PIE 驱动当前公开控制值与真实 UButton 委托；不伪造 Resolve、不直接 ApplyState、不驱动落杖／长树、不改相机或保存资产。真实保存地图内 1.25 秒保持与既有 Blueprint Timeline 均由产品执行。录音只来自 UE 游戏主混音，不是桌面或麦克风。

显式 Cook 根为新 EnvironmentStates 地图；实际 manifest 同时保留既有 Config／依赖带入的 InteractionLab 与引擎 Entry 支持地图。它们不是本轮新增可探索空间或第二个竞赛场景。7 个 SoundWave、剧院 Pawn／GameMode、三幕 UI、参考材质、字体、谜题数据和树形 BP 的实际 manifest 条目均已核验。

本轮没有重做实际行走脚步 PCM 专项，组件、Pawn、SoundWave 和之前包哈希冻结；前一步 15 项行走／碰撞／停步／尾音验证仍是历史证据，见 FOOTSTEP_SYNC_VALIDATION，不冒充当前新源码专项。

## 保留的失败与修正

1. VisiblePlay-Run1：独立新地图遗漏 Controller 精确菜单白名单，附着未开始，300 秒诊断超时；正常退出，零通过项，不计入成功。随后只登记该新地图完整路径并补原身份测试，不采用 Contains／短文件名放宽。
2. ColdVerify-Run2：初始哈希保护尚未纳入已登记的两个菜单身份源码，被保守拦截；改为读取单列 SCOPE_EXTENSION，不覆写初始 BEFORE，再冷读成功。
3. VisiblePlay-Run2：Python 不能读取引擎 protected `bCanEverTick`，立即失败，零通过项；改为观察真实 runtime Tick 是否禁用。CDO 的 CanEverTick=false 由原生测试证明，不把访问异常当产品失败或跳过验证。Run3 实际成功。

所有失败记录原样保留，不覆盖 Run1/Run2、截图、日志或初始快照。另有 MapDiagnosis-Run1 的只读双地图手动启动／三幕／Controller 核查，源码快照与最终 Run2 一致。

## 文件、资产、文化与 AI 使用记录

修改七份源码／测试和两份现有文档；另增新 .umap、地图创建脚本、独立 CMD/helper、方案与验证文档共六份产品文件。原文件在 Before；菜单身份额外两文件范围在 SCOPE_EXTENSION。无 Git 写操作、删除、Config 改动或新 .uasset。之前用户未提交改动保留。

没有新增模型、材质、纹理、音效、字体、插件、下载或付费服务。沿用此前许可已明确的资源与源链，不读取／改写受限的旧许可登记表。此轮文化含义仍是“以灯为日、以影为夸父”的演出状态与落杖因果，不宣称历史皮影流派复原或正式声景。

Codex 辅助：环境枚举／事实映射与护栏、原生测试、新地图隔离脚本、参数驱动验证、证据与文档；子代理分工为原生测试、UE Python API／源码只读复核、打包脚本门控。脚本与执行日志保存在审计目录；主体架构按 UE Blueprint architecture 技能维持显式一对一引用、被动环境与不重复判定。Computer Use 只检查并激活过本轮 UE 窗口；尝试关闭时窗口已由脚本退出，未终止其他进程。自动化的工程图像审查不是用户或首次玩家签收。

## 未验收及下一段

本步不代勾用户新版本视觉接受、包内真人全流程／物理键鼠、新版本脚步听感与 Windows 输出、首次玩家盲测、5–8 分钟完整体验、Shipping、最终性能或高质量美术。测试子进程的后台音频／限帧控制仅为记录可靠性，不是性能证明；正式启动器不带测试脚本或录音控制。

五态样本只提供后续美术整合的事实接口。后续同图环境层次、久未开演的场景线索、免费／开源正式美术仍须在不遮挡灯—偶—幕关系的前提下分步集成；不因本次通过扩成第二地图或探索系统。
