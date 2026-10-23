# 基础声音 Dev｜免费来源与处理记录

记录日期：2026-10-10。唯一人类作者／负责人：用户；Codex 辅助来源核验、数值筛选、适配与技术实现。本次未用付费资产、注册账号、付费音频生成或来源不明转载；本文件是新增音频的独立许可证据，不读取或替换旧 `LICENSES.md`。

## 具体来源

| 原包／原音 | 作者与官方来源 | 许可 | 本轮用途与限制 |
|---|---|---|---|
| Impact Sounds | Kenney，[原站资产页](https://kenney.nl/assets/impact-sounds) | CC0 1.0；原包完整 License.txt 已留存 | 只选 soft medium 001、wood light 003、wood heavy 002 三个文件；是通用 impact，不称传统锣鼓／曲牌 |
| wind1.wav | Luke.RUSTLTD，[OpenGameArt 原作者条目](https://opengameart.org/content/wind1) | CC0 1.0 | 原作者用 PureData 合成的风，不称实地风录音 |
| 20 rustles of dry leaves | qubodup，[原条目](https://opengameart.org/content/20-rustles-dry-leaves)、[同站可访问镜像](https://lpc.opengameart.org/content/20-rustles-dry-leaves) | CC0 1.0 | 只选 rustle04.flac；干叶音经处理，听起来是否仍像枝叶而非火焰尚须试听 |

许可文本：[CC0 1.0 法律正文](https://creativecommons.org/publicdomain/zero/1.0/legalcode)。CC0 不是对一切商标／肖像或第三方权利的额外担保；本次仅采用条目明确发布的非人声通用音效，不作作者背书或文化复原声明。虽然 CC0 不要求署名，仍保留作者、原页和修改记录。

## 本地许可证据与复现

证据根：`D:\灯影山海\Saved\Audit-2026-10-10-AudioDev\AudioSources`，不在 Content/Cook 内。

- `ACQUISITION.json`：原作者页／直连 URL、下载时间、字节与 SHA256；`Evidence/` 保存本轮网页许可 HTML；Kenney 包内 License.txt 全文留存。
- `Original/`：原 ZIP、wind1 WAV 和 leaves 7z；`EXTRACTION.json` 保存路径／格式核验，只在新目录解压，无绝对路径、逃逸段、驱动器冒号或符号链接。
- `SOURCE_AUDIO_ANALYSIS.json`：151 段源音数值检查；只说明频谱、峰值、长度等数值，不当作听感判断。
- `DERIVED_MANIFEST.json`：每个原成员哈希、派生哈希、处理步骤与局限；`Derived/` 保留实际导入的五个 WAV。
- `Build-DevAudio.py` 复现处理；脚本 SHA256 为 `38020C560DBC1809512442B5674296F4A9CE87622C3B20BC42046B7F9DF7D6A8`。

原包 SHA256：

| 原文件 | 字节 | SHA256 |
|---|---:|---|
| kenney_impact-sounds.zip | 800850 | `029D734AF1582474EDF3A694D1B0CEBC97C1C152F2F39FA34D4C2BAFC5DE77F8` |
| wind1.wav | 5291948 | `A2856F794FBF77E05F8241DC4ADEADE7F62FA21C3C9DC49F7725B6C6218060C3` |
| qubodup-rustle.7z | 10565232 | `C5D7458085E9B208009388B832184BDDC0045482F6FA67A1EB6EA09335BB7A43` |

## 派生音频

统一 48 kHz、单声道 PCM16 WAV；音量已写入波形，Actor 对五声的实例倍率均为 1.0，避免二次压低。全部派生文件数值削波样本为 0，但这不等于主混音也无削波或音量主观合适。

| 派生 SoundWave | 时长 | 循环 | 样本峰值 dBFS | 本地处理 |
|---|---:|---|---:|---|
| SFX_DevWind | 12.00 s | 是 | -26.023 | 去 DC／柔和低通／重采样；源 6 s 起取窗，750 ms 首尾交叉淡化 |
| SFX_DevHoldingPulse | 1.30 s | 是 | -26.939 | soft impact，0.08／0.73 s 两次轻碰，间隔 0.65 s；循环边缘静音 |
| SFX_DevResolve | 0.3556 s | 否 | -20.002 | light wood；短 attack/release、前后静音 |
| SFX_DevStaffContact | 0.4330 s | 否 | -15.919 | heavy wood，峰值与前两幕成功声有层次区分；短 attack/release |
| SFX_DevForestLeaves | 2.25 s | 是 | -29.125 | rustle04；柔化尖锐瞬态／低通，200 ms 首尾交叉淡化 |

循环接缝样本差、RMS 和频谱不证明人耳无接缝；没有计算 integrated LUFS 或 oversampled true peak。当前 `auditioned=false`、`final_art_audio_approved=false`，这是 Dev 占位声音，不是正式文化音色锁定。

## 开发依赖与 AI 使用

本地转换用 NumPy、[SoundFile 0.13.1](https://pypi.org/project/soundfile/0.13.1/)／libsndfile 与系统 bsdtar；SoundFile 的开发依赖局部安装在 AudioDevStage/AudioTools，不安装到全局，不作为游戏运行依赖，不 Cook，不复制 DLL 修补包。

Codex 本轮辅助编写三份新声音 Actor／测试文件和 Editor 组装／验证脚本，依据现有 Stage 事实契约处理；协作审阅与数值分析仍属 AI 辅助，不增加人类队友。五段声音来自上述 CC0 原音的确定性处理，没有使用声音克隆或生成式音频。用户此前接受的是 P02 视觉效果，不自动接受本轮声音听感。过程证据与尚未验收项见 `AUDIO_DEV_VALIDATION.md`。
