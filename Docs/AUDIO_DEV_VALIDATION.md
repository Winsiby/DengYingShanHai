# 基础演出声音 Dev｜分层验证与运行说明

日期：2026-10-10。用户此前明确接受第二幕身形提示“效果可以，进入下一步”；本轮将基础声音接入同一 Dev 演出，不代表完整 Alpha、5–8 分钟、正式文化音色或 Shipping 完成。用户是唯一人类作者，Codex 辅助实现和监督验证；本轮没有 WorkBuddy 操作。

## 玩家能体验到什么

双击 `D:\灯影山海\Start-AudioDev.cmd`，点击“开始复演”，仍用原来的 E／A／D／R。

| 现有演出事实 | 新声音 |
|---|---|
| 已开始，演出有效 | 克制的微风底层 |
| 实际 Holding | 轻碰节奏循环；打断／复位／换幕立即停 |
| 第一、二幕成功题签 | 每幕一次木击 |
| 第三幕参数 Resolve | 不提前播放落杖重音 |
| Stage 真正接受 A 端幕上接触 | 一次较重木击，按当前 Token 去重 |
| 实际林形已完成并进入 Complete | 轻枝叶循环 |

声音不是唯一通关提示；静音仍用原就位／保持／题签。当前音色是 CC0 Dev 占位，不称传统锣鼓、吟唱、实地风或正式配乐。来源与处理见 `AUDIO_DEV_SOURCES.md`。

## 实现与冻结范围

新增 `DYStageAudioPresentationActor.h/.cpp` 和 `DYStageAudioAutomationTests.cpp` 三个原生文件；已有 78 个原生文件不修改。Audio Actor 被动消费现有 Stage 事实，无 Tick、世界扫描、Director 查询、目标／容差或新成功时钟。五个自有 AudioComponents 默认不自动播放，Actor 类默认 opt-in=false。

当前地图仍是 `/Game/DengYingShanHai/Dev/AlignmentFeedback/Maps/LV_AlignmentFeedbackLab`，只新增显式启用、引用同世界 Stage 与五段 SoundWave 的一名 Actor。冷读共 32 个关卡 Actor。五个新资源仅在 `Dev/Audio/Sounds`，不导入整个音效包。原 Blueprint 图、配置、P02 body-fit MI、父材质、Actor 类与 Transform 都保持基线。

灯速 `.2625`、偶速 `.28`、15 Hz、目标／容差、约 1.25 秒保持、2 秒 Dev 题签、输入、菜单、相机、曝光、A 端／Z70、Drop→Contact→Forest→Complete 时序均不改。Stage 单独 EndPlay、引用失效、同图重演和 Audio Actor EndPlay 均清理订阅与声音；不带旧世界循环或补播旧单次声。

不新增锣鼓谱／吟唱／脚步／音乐、暂停、Skip、设置菜单、镜头、场景、玩法或插件。Dev `-DYAudioMuted` 只控制音频，不改变游戏事实。

## 证据层级

审计根：`D:\灯影山海\Saved\Audit-2026-10-10-AudioDev`。机器报告、原始日志与失败轮不覆写；以下描述必须与实际记录一起阅读。

| 层级 | 实际结果／证据边界 | 记录 |
|---|---|---|
| 原生构建与自动化 | 134 succeeded / 0 failed / 0 notRun；实际进程退出 0；81 份源码哈希冻结 | `Native-Run3/RESULT.json`、`SOURCE.json`、完整 Build/Test 日志 |
| 新增九项测试 | Holding 有限迁移、Resolve 去重、晚加入不补播、接受接触身份、Complete 才有叶声、会话复位、默认关闭／无 Tick、缺引用安全、真实 Stage 绑定／单独销毁清理 | 同上；纯函数身份测试不等于实际接触几何证明 |
| 资产与冷读 | 五 SoundWave／循环标志／同世界引用成功；冷进程 PASS，没有保存资产；已有 C++ 未变 | `AssetCreate-Run1/Result.json`（尾部测试缺陷见下）、`ColdVerify-Run1/Result.json` |
| 实际两轮演出 | 65 项检查、35 张非空 PNG；有声与完全静音各完成三幕、两次真实成林、一次实际同地图 OpenLevel、四次保持打断及当前幕复位；实际 UE 退出 0 | `VisiblePlay-Run4/Result.json`、`EXIT.json`、`Events.jsonl` |
| 实际音频事实 | 每轮 HoldStarts／Stops 各 5，P01/P02 Resolve 2，实际接触重音 1，实际 Complete 叶声 1；有声请求 10，静音请求 0 且五组件均非播放 | `VisiblePlay-Run4/AUDIO_RESULT.json`；不是听感或 OS 出声证明 |
| 完整游戏混音 | 两真实 WAV 的 RIFF／data／帧数完整，写入稳定后退出；独立数值 QA PASS，有声非零无样本削波，静音全零 | `VisiblePlay-Run4/MIX_QA.json`、两 WAV |
| 独立 Development 包 | UAT Build/Cook/Stage/Pak＋IoStore/Archive；精确新 AudioDev Run1，原包不覆盖；实际 UFS 逐项包含五新声、当前图、P02 MI／父材质、三题目、林形及中文字体 | `Package-Run1/EXIT.json`、`ARTIFACTS.json`、`LAUNCH.json`，包内 `AUDIO-DEV-BUILD.json` |
| 包首帧与正常退出 | 原生包 1280×800 首屏、引擎原生 20 秒退出；不在包内运行 Python，也不称包内完整物理操作通过 | `FirstFrame-Run1/RESULT.json` 与原始 PNG／log |
| 实际入口 DryRun | Windows PowerShell 5.1：Auto、Package、EditorGame 和 `.cmd` 包装链四项；默认选择固定 AudioDev Run1，EditorGame 明确 `-game`；均不启动游戏 | `Launcher-Run1/RESULT.json` |

首帧／流程图像审阅另记于 `VISUAL-REVIEW.json`，不覆写原机器报告 `ReviewPending` 或构建身份中的 `GameplayVerified=false`。最终保护核验以 `FINAL.json` 的实际 Status 为准。

包本体冻结清单为 49 文件、1,043,614,570 bytes（构建身份 JSON 另存，不计入该原始 ARTIFACTS 清单）；Cook 仍附带既有默认 `LV_InteractionLab` 和引擎 Entry，未改 Config 去清理。启动入口精确进入 AlignmentFeedback，附带旧根不算新增竞赛场景。本次真实工具链为 UE 5.8.3／MSVC 14.51.36260（family 14.51.36231）／SDK 10.0.26100.0；UBT 保留“比首选 14.50.35717 更新”的告警，另有引擎 Character.h 内部 API 弃用告警，不在本步改工具链或引擎。构建／Cook／首帧实际成功，不据此宣称未来版本兼容。

### 主混音数值

两份都是本次专用新编辑器关联游戏音频设备的 master output，未采桌面 loopback、麦克风或别的应用。记录时没有并行资源试听；master 不是逐 Actor 独占隔离。

| 指标 | 有声 Cycle1 | 静音 Cycle2 |
|---|---:|---:|
| 格式 | 48 kHz／双声道／PCM16 | 同左 |
| 实际帧数 | 3402752 | 2980864 |
| 混音录制时长 | 70.890667 s | 62.101333 s |
| 峰值（线性样本） | 0.0618286133 | 0 |
| RMS | 0.0027672731 | 0 |
| 非零样本 | 6470974 | 0 |
| 满幅正／负 rail 样本 | 0 | 0 |

这不是 5–8 分钟作品时长验收，脚本主动通过公开参数请求驱动设备，不是首次玩家。没有 integrated LUFS／true peak／循环接缝人耳证明。单看非零主混音不能证明五段声音都被听到，需结合原始事件及后续试听。

额外源波形证据 `VisiblePlay-Run4/SOURCE_MATCH.json` 与可复用 `Match-GameMixSources.py`：使用已留存的原派生波形，只在内存拟合并减去风声，再在真实事件附近进行归一化滑动点积；风声、三幕 Holding 首脉冲、两次 Resolve、接受接触和 Complete 枝叶的相关性约 0.962–0.998。输入 WAV／事件／模板哈希与窗口完整留存。这补充“对应源波形进入真实混音”，不是主观评分；世界时间与音频样本无共同精确 t0，约 -0.187 至 +0.131 秒的匹配差不能解释为接触前响声或 sample 级因果证明，也不证明所有停止／额外声次数。原波形、产品增益与 MIX_QA 不修改。

## 测试环境与保留的失败记录

- `Native-Run1`：一个测试直接调用 Actor BeginPlay，违反引擎生命周期，132 成功／1 失败／实际退出 255；改为正确 DispatchBeginPlay 后 Run2 为 133 成功。随后新增 Stage 单独 EndPlay 清理与真实绑定销毁测试，最终 Run3 为 134 成功。既有产品代码未修改。
- `AssetCreate-Run1`：五声与当前地图已实际保存，但尾部速度校验使用浮点严格等号而失败；只把验证改为小误差比较。新 ColdVerify-Run1 独立冷读 PASS 且 saved=[]，没有覆写重建资产。
- `VisiblePlay-Run1`：测试工具误用 C++ 类名 `AudioMixerBlueprintLibrary`；本机 header 明确 Python ScriptName 为 `AudioMixerLibrary`。修正仅测试工具，失败记录保留。
- `VisiblePlay-Run2`：两轮流程 65 项 PASS／退出 0，但完全静音 submix 自动停用，使录音“No audio data”，第二 WAV 缺失；不能称完整音频 PASS。后续工具等待实际 WAV 完整与稳定后才允许结束。
- `VisiblePlay-Run3`：完整双 WAV、流程 PASS，但独立 MIX_QA 为 FAIL：有声轮与静音轮都为零。编辑器失焦后把 App 总音量设 0，IsPlaying 与请求计数不能证明混音有声；打包前门槛正确阻止。原 FAIL 不覆写。
- `VisiblePlay-Run4`：只对测试子进程使用 UE 原生 `au.NeverDisableSubmixes=1`（持续渲染真实静音）和临时 ini 的 bAllowBackgroundAudio／EnableGameSound／UnfocusedVolumeMultiplier；工具实际读回前两偏好与 CVar 再录音。本机源码证明命令行 override 排除持久写回。本轮数值与流程均通过，不注入静音素材，不伪造 WAV。上述设置不进入交付启动器、Source Config 或包；不拿该轮测产品性能。

当前原生声音代码在这些录音工具修正期间没有再变。第三幕接触／成林仍由原生产几何和原流程负责，脚本不伪造成功、接触或林形完成。

## 保护与回退

基线 `BEFORE.json` 记录 238 个原文件；只允许当前地图＋TECH_SPEC＋DEVELOPMENT_PLAN＋P02 验证文档四项差异，另 234 个原文件应哈希一致。新内容精确五声，新原生精确三文件。最终核验既有 78 源码、当前 81 源码、Cook 源引用、新发布文本、35 PNG、两 WAV、原无声 Run1／Readability／P02 Run2 与新声音归档、Git HEAD 和空暂存区；无删除或 Git 写操作。

旧 `Start-AlignmentDev.cmd` 仍固定原 P02 Run2 无声包，适合比较。旧 helper 的显式 EditorGame 使用当前源码地图，已经含声音，不是历史源码回退。新入口固定 `Builds\AudioDev-20261010-Run1\Windows`；缺包才明确 EditorGame 回退，不挑“最新目录”或随意旧包。已有 UE／游戏窗口时不硬杀进程。

源码回退先检查有无后续用户编辑，再用精确 Before 地图／文档与本轮新增文件清单处理；不能整体 reset/clean。只比较体验时启动旧固定包即可，不须回写地图或删除声音。

## 仍未验收

本轮机器验证不代替用户试听、系统音量／耳机扬声器出声、包内物理键鼠、运行中静音再解除静音的实际声音恢复、首次玩家、正式文化音色、完整剧场美术、5–8 分钟、其他屏幕比例、Skip／异常中断、三轮目标机竞赛通关或 Shipping。当前声音偏克制，是否清楚而不干扰操作由实际体验判断；没有基于猜测继续增大音量。

## 文件位置

- 新入口：`D:\灯影山海\Start-AudioDev.cmd`。
- 固定包：`D:\灯影山海\Builds\AudioDev-20261010-Run1\Windows`。
- 本轮证据：`D:\灯影山海\Saved\Audit-2026-10-10-AudioDev`。
- 有声录音：审计 `VisiblePlay-Run4\AudioMix-Cycle1.wav`；静音对照同目录 Cycle2。

聊天点链接可能显示脚本代码；运行应在资源管理器进入 `D:\灯影山海`，双击 `.cmd`，再点“开始复演”。
