# 《灯影山海》剧院声音 Dev：来源、许可与加工

日期：2026-10-10。本文是本轮新增来源记录，不替代、覆盖或修改旧许可文档。

本项目由用户一人完成，Codex 是辅助工具，本轮素材处理、技术实现与数值验收由 Codex 直接执行，不依赖队友、WorkBuddy 或用户自行录音。

本文只确认来源、加工和候选数值。实际游戏混音的技术验证见 `THEATRE_AUDIO_VALIDATION.md`；设备出声、人耳听感和木台材质贴切程度仍待体验核验，不以本文代签。

## 1. 免费原始来源

| 来源 | 原始作者／发布者 | 明确许可 | 原文件与核验尺寸 | 采用范围 |
|---|---|---|---|---|
| [Impact Sounds 官方页](https://kenney.nl/assets/impact-sounds) | Kenney | CC0-1.0 | `kenney_impact-sounds.zip`，800850 B | 通用低 impact、轻木击、较沉木击 |
| [wind1 原发布页](https://opengameart.org/content/wind1) | Luke.RUSTLTD | CC0-1.0 | `wind1.wav`，5291948 B | 环境风声；作者说明为 PureData 合成风，不是特定戏台实地录音 |
| [20 Rustles of dry leaves 原发布页](https://opengameart.org/content/20-rustles-dry-leaves) | qubodup | CC0-1.0 | `qubodup-rustle.7z`，10565232 B；20 条 FLAC，24-bit / 96 kHz / stereo | 选 `rustle04.flac` 作枝叶簌动 Dev 候选 |
| [RPG Audio 官方页](https://kenney.nl/assets/rpg-audio) | Kenney Vleugels（Kenney.nl） | CC0-1.0 | `kenney_rpg-audio.zip`，964837 B；50 个正式声音 | 选 `footstep02.ogg`、`footstep07.ogg` 作通用 A/B 脚步 |
| [Steps in wood floor 原发布页](https://opengameart.org/content/steps-in-wood-floor) | mikeask | CC0-1.0 | 原站 `steps in wood floor.wav`，613852 B | 木地板备选，完整留存，但本轮没有采用为默认派生脚步 |

均从原站公开链接取得，不使用来源不明镜像、付费模型／音频／插件／生成服务，不创建下载账号。
Kenney `Footstep Sounds` 的具体地址 `/assets/footstep-sounds` 实际为 404；本轮使用的是确实存在的官方 **RPG Audio**，不编造独立脚步包。

Kenney 包内完整 `License.txt` 与官方发布页保留；OpenGameArt 原作者页面保留其作者、许可和原下载链接。qubodup 的原包只有 FLAC，没有附独立许可文本，许可证据来自原发布页，不冒称包内有许可证。
保留 [CC0 官方说明](https://creativecommons.org/publicdomain/zero/1.0/) 与 [完整法律文本](https://creativecommons.org/publicdomain/zero/1.0/legalcode)。
[Kenney 官方许可问答](https://kenney.nl/support) 明确其资产页素材为 CC0、可用于商业项目，署名非强制；本项目仍保留作者与加工记录，不暗示原作者对作品背书。

## 2. 七个新声音候选的映射

下表为本轮七个新声音 WAV，不意味着整个项目只有七个文件或七个资产。全部 48 kHz、mono、PCM16，无本轮导出数字削波；旧素材、旧 Dev 包与旧启动入口保留。

| 本轮文件 | 原始条目 | 时长 | 本轮实测 sample peak | 用途 |
|---|---|---:|---:|---|
| `SFX_DevWind.wav` | Luke.RUSTLTD `wind1.wav` | 12.000 s | .199982 | 风声循环 |
| `SFX_DevHoldingPulse.wav` | Kenney Impact `impactSoft_medium_001.ogg` | 1.300 s | .279999 | Holding 节奏循环，两次通用 impact 间隔 .650 s |
| `SFX_DevResolve.wav` | Kenney Impact `impactWood_light_003.ogg` | .355604 s | .479980 | 前两幕 Resolve 单次提示 |
| `SFX_DevStaffContact.wav` | Kenney Impact `impactWood_heavy_002.ogg` | .433042 s | .639984 | 已接受的杖尖接触单次提示 |
| `SFX_DevForestLeaves.wav` | qubodup `rustle04.flac` | 2.250 s | .159973 | 真实成林后枝叶循环 |
| `SFX_DevFootstepA.wav` | Kenney RPG `footstep02.ogg` | .270146 s | .449982 | 实际行走位移触发的交替变体 A |
| `SFX_DevFootstepB.wav` | Kenney RPG `footstep07.ogg` | .283583 s | .450012 | 实际行走位移触发的交替变体 B |

### 脚步命名边界

默认称 **通用 A/B 脚步**。原包没有注明实际左／右脚或具体地面材质，因此 A/B 只是逻辑上轮换的两个变体，不宣称真实左右脚认证，也不把 generic footstep 当作木地板材质鉴定。与木台地板是否贴切，仍需实际听感核验。

mikeask 的备选确实由作者称为木地板行走，但下混后的数值频谱重心约 36.6 Hz；本轮优先选择中频更明确、单条独立 attack 的 Kenney 候选（约 520/534 Hz）。这不是“原录音音质差”的主观断言，也不保证笔记本扬声器一定能清楚播放。

这些候选不是正式传统锣鼓、吟唱或历史复原录音。低 impact 只称保持节奏／通用击声，不借用文化标签提高来源可信度。

## 3. 加工链与本轮增益

### 原五声的已留存 Dev 加工

旧五声源 WAV 已有下混、DC 去除、抗混叠重采样、适量频谱滚降及淡入淡出：风声 750 ms 交叠循环，Holding 为头尾静默的 1.3 s 循环，枝叶为 200 ms 交叠循环；叶声另有平滑瞬态压缩。完整原加工记录保留，不重新构造节奏或循环。

本轮从旧五个已验证 WAV 派生 **全样本等比例增益版本**，仅增益与 PCM16 重量化，不更改帧数、时长、静默样本位置、节奏、fade 或 loop 交叠。提升约 12–16 dB；这不是无上限增益，也不是 OS 音量修改。

| 文件 | 旧 sample peak → 新 sample peak | 旧 RMS → 新 RMS | 本轮增益 |
|---|---:|---:|---:|
| Wind | .049988 → .199982 | .007641 → .030574 | +12.043 dB |
| Holding | .044983 → .279999 | .004691 → .029202 | +15.882 dB |
| Resolve | .099976 → .479980 | .008910 → .042781 | +13.627 dB |
| Contact | .159973 → .639984 | .016693 → .066785 | +12.043 dB |
| Leaves | .034973 → .159973 | .006476 → .029627 | +13.208 dB |

单声峰值上限不保证相加后的实际主混音不削波；声源叠加、实时混响和总线都须动态测量。源文件 RMS 也不能当作实际游戏混音 RMS。

### 新 A/B 脚步加工

原始 48 kHz，等增益 stereo→mono、DC 去除；0.25 ms 起始轻淡化位于主 attack 峰之前，主峰相对原音位置保留；8 ms 尾部淡化，4 ms 前置与 24 ms 后置静默；sample peak 调至约 .45，再转 PCM16。
没有压缩、变调、重低通或本轮烘焙混响。不烘焙新混响不等于原始录音绝对没有自然房间反射。

## 4. 归档、可复现性与许可保留

本轮素材与过程证据最终随审计归档到 [AudioSources 目录](D:/灯影山海/Saved/Audit-2026-10-10-TheatreAudio/AudioSources/)，由主验收者核验实际复制结果。

- [ACQUISITION.json](D:/灯影山海/Saved/Audit-2026-10-10-TheatreAudio/AudioSources/ACQUISITION.json)：新原包／备选 WAV 的原站 URL、获取时间、作者、许可、字节数、SHA256。
- [EXTRACTION.json](D:/灯影山海/Saved/Audit-2026-10-10-TheatreAudio/AudioSources/EXTRACTION.json)：解压前成员路径／类型验证及完整解压文件 hash；拒绝绝对、父级、冒号路径和链接。
- [DERIVED_MANIFEST.json](D:/灯影山海/Saved/Audit-2026-10-10-TheatreAudio/AudioSources/DERIVED_MANIFEST.json)：两条 A/B 脚步的原条目、加工、数值、hash 与材料未验收标记。
- [AUDIBILITY_MANIFEST.json](D:/灯影山海/Saved/Audit-2026-10-10-TheatreAudio/AudioSources/AUDIBILITY_MANIFEST.json)：五个新增益版本 before/after 数值、原始与旧派生 SHA256、旧许可保留位置、加工脚本 SHA256。
- [FOOTSTEP_SOURCE_NOTES.md](D:/灯影山海/Saved/Audit-2026-10-10-TheatreAudio/AudioSources/FOOTSTEP_SOURCE_NOTES.md)：新脚步来源与限制。

原始完整包、原站 HTML、CC0 证据、许可文件和可复现处理脚本均保留；旧五声的许可链仍引用已留存的旧源归档，不因生成增益版而更换作者或许可。
只把七个选定 WAV 导入对应新 Dev 声音资产，不整包 Cook。局部 soundfile/cffi/pycparser 工具、原始大包与分析数据不是游戏运行依赖。

当前不据来源或数值代签音质、木质感、传统性、扬声器实际出声或人耳舒适性；动态结果另由主验收者写入本轮 Validation。
