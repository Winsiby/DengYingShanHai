# 《灯影山海》脚步与空剧院声音 Dev 验证

日期：2026-10-10。唯一人类作者与体验负责人为用户；Codex 辅助实现与技术核查。本轮没有使用 WorkBuddy 执行，也没有新增付费资产、插件、地图、输入、设置菜单或团队成员。

## 1. 结果与启动

已生成固定 Windows Development 包 `Builds/AudioDev-20261010-Run2/Windows`。资源管理器双击 `D:\灯影山海\Start-AudioDev.cmd`；同一个入口已从旧声音 Run1 更新为 Run2。不要直接点击旧 AlignmentDev 入口期待声音，也不要直接启动裸 EXE 期待其自动选择 Dev 地图。聊天文件预览可能显示脚本，应从资源管理器运行。

旧包、旧五个声音资产、原 Alignment 入口和本轮失败记录均保留。回退旧声音版本可使用本轮 Before 保存的旧启动 helper，它明确指向仍保留的 Run1 包；恢复原工程地图需要同时考虑新的声音引用／GameMode，不在本轮自动回退。

## 2. “听不到”的诊断

- 用户实际旧运行日志证明启动的是 AudioDev Run1、正确 AlignmentFeedback 地图，`Muted=0`，有 Resolve 与真实 StaffContact 播放事件；不能归因为用户点错无声包。
- 旧主混音 RMS `.0027672731`，约 **-51.16 dBFS**，过于保守；非零不等于可闻。新五声按有限增益派生，时长、保持节奏和循环交叉不变。
- 两次只读 Windows 查询都实际返回默认 Console／Multimedia 播放端点 `Muted=true`、`MasterScalar=0`、`MasterDb=-65.25`；后一次有准确开始／结束 UTC，见 `Diagnostics/ENDPOINT_RECHECK.json`。这只能证明查询当刻，不回溯断言用户先前体验时同样静音。
- Codex 未调整系统音量、应用混音器、默认设备或驱动。用户需解除 Windows 静音，将音量调到舒适水平。游戏技术修复不替代最终设备检查。

## 3. 编译与冷启动

审计根：`D:\灯影山海\Saved\Audit-2026-10-10-TheatreAudio`。

- 最终 `Native-Run3`：Build 实际退出 0；自动化 **143 succeeded / 0 failed / 0 notRun / exit 0**。包含新增 9 项脚步距离、停走／零位移、空中、连续性／传送、低帧率、无效参数、默认关闭、无效拥有者与真实生命周期测试。
- 原有 `Character.h` 引擎弃用和本机工具链建议警告保留，不修改引擎或安装环境。本轮无编译错误。
- `ColdVerify-Run3`：只读冷加载通过、`saved=[]`。32 个原场景 Actor；新 Pawn 与旧 Pawn 的 6 个输入资产、360 cm/s、360 cm 相机臂、偏移、碰撞和 FOV70 数值相同；只增加脚步能力。新 GameMode 沿用原 PC／HUD／流程配置。
- 七条 SoundWave 和两份 Dev BP 位于 `Dev/TheatreAudio`；原 P02BodyFit 参考、15 Hz、灯／偶速度、目标／容差／保持、三幕次序、A 端／Z70 和真实落杖成林保持。

## 4. 实际三幕、重演与主混音

最终 `VisiblePlay-Run2` 使用与 Native-Run3 相同的 86 个源码哈希；实测 **65 项检查、2 次真实成林、1 次真实 OpenLevel 重演、进程退出 0**。真实控件事件和公开操纵请求驱动既有流程，不绕过谜题判定，不伪造成功／接触／成林事件；不是物理键鼠验收。

实际 UE game master 导出，不是麦克风、桌面回环或 OS 录音：

| 记录 | 时长 | Peak | RMS | 削波 |
|---|---:|---:|---:|---:|
| 有声三幕 Cycle1 | 70.9333 s | .2485046 | .01140682 / -38.8567 dBFS | 0 |
| 静音三幕 Cycle2 | 62.1013 s | 0 | 0，全部样本零 | 0 |

有声周期相对旧整段 RMS 约提高 **12.30 dB**。这是不同周期时长／内容的样本统计，不是 LUFS、人耳响度匹配或耳听通过。静音重演先等待旧混响尾音 8 秒自然衰减，再开始记录，不声称 stop 能瞬间清空 DSP。

测试子进程允许后台音频、EnableGameSound、NeverDisableSubmixes 与 UnfocusedVolumeMultiplier 的临时覆盖，只为确保实际零缓冲也可导出；不写源 Config，不作为产品性能证据，也不加入用户启动器。

## 5. 真实脚步与干／湿／静音补测

最终 `Footsteps-Run3`：**8 项动态检查、退出 0**，对应 Native-Run3 源码。每段 10 秒：前 2 秒静止，2–3 秒真实 ApplyMoveIntent，之后停止，等待尾音。没有设置人物坐标来伪造脚步。

| 模式 | 实际移动 | 步数 | 播放请求 | 录音 |
|---|---:|---:|---:|---|
| Dry | 339.210 cm | 2 | 2 | 非零，peak .1608887，无削波 |
| Room | 339.185 cm | 2 | 2 | 非零，peak .1608887，无削波 |
| Muted | 339.185 cm | 2 | **0** | **整个实际录音全零** |

另有真实临时 PIE Cube 阻挡：最后连续 2 秒位移 0、新步数 0；夹具仅在临时世界创建／销毁，不保存资产。实际 LaunchCharacter 离地无步，既有 Reset 在累计 **20.481 cm** 时立即清零并停止干声；真实 Pawn 销毁释放 Voice。不会把原 Run2 的 blocker SKIP 写成通过。

原生混响诊断读取设备实际 Tag 登记；日志中每次 NativeTagRegistered=1 都有对应同 Tag 的 NativeTagRemaining=0。Stage 使用自己的原设备 Handle 清理，不删除其他效果，不依赖已结束 World 的播放许可。

`THEATRE_MIX_QA.json`：完整 RIFF、48 kHz stereo PCM16、实帧数、无削波、定义窗口全部通过。Dry 源终止后的 **3.5–4.5 秒**全零；Room 同窗有有限尾音，RMS约 **-79.23 dBFS**、peak `.00076294`；**5–7 秒两者全零**。3.5–4.5 是样本窗口而不是精确世界／音频帧同步；-85 dBFS 是低电平路由检测底线，不是“明显空旷感”听感标准。

当前为清楚干声＋轻混响候选，2.4 秒／35 ms 是引擎算法参数，不是真实剧院 RT60 或体积还原。总体空间感、木台材质契合、远近与耳机／扬声器舒适性仍需体验反馈，不据尾音非零代签高质量声景。

## 6. 打包、首帧与入口

- Package-Run1 实际 UAT 退出 **0**，生成 AudioDev Run2；31 个冻结源资产、86 个源码、16 个验证输入在 Cook 前后哈希一致。
- **49 个打包产物、1,045,275,214 B**，另有独立构建身份 JSON。实际 UFS 包含当前地图、两份新 BP、七声音，未把原始素材包、局部音频 Python 依赖或整个 RPG 音频包 Cook。
- 实际 Cook 仍包含原有 Engine Entry、InteractionLab 和当前 AlignmentFeedbackLab；这是现有工程依赖／默认地图，不是新增可玩场景。正式 Shipping 的 Dev 引用／Cook 收敛仍属后续里程碑。
- FirstFrame-Run1 原生 Windows 包：目标新 GameMode、1280×800、中文开始菜单，20 秒引擎正常退出 **0**；原生 Room Tag 实际登记和清理均记录。主代理已查看实际 PNG，按钮字号／位置保持，画面不是新黑屏错误。
- Launcher-Run1：Windows PowerShell5.1 Auto／Package／EditorGame 和 CMD 四种 DryRun 全部退出0。Auto/CMD 固定打开 Run2；EditorGame 明确 `-game`。不运行 Python、录音或修改系统声音。
- 新包只验首帧／加载／退出，不代签包内物理行走、全程通关或人耳。完整流程与实际脚步输出证据来自上述真实 PIE 子世界；最终包体验仍应在用户目标电脑核验。

## 7. 失败与修复记录

保留 AssetCreate-Run1（误用顶层 load_blueprint_class，未保存）、AssetCreate-Run2（七新 Wave 保存成功，但旧 Pawn 是原生类不能复制为 BP）、AssetAssemble-Run1／ColdVerify-Run1（向量 debug repr 含内存地址，测试过严）和 Footsteps-Run1（GetCharacterMovement 未反射 Python）。前者改用正式 EditorAssetLibrary、原生继承 BP，向量改比真实数值，移动组件通过反射属性读取。

Footsteps-Run2 原 blocker 使用内部 Blueprint helper／MakeTransform 被 Python 排除，明确 SKIP；Run3 改为引擎原生 Dev Summon 创建唯一临时静态网格 Actor 后得到真实阻挡通过。没有改产品来迁就测试。

旧 source、脚步与五声原始加工、许可链、AI 辅助过程和本轮审计保留。不读取或修改旧 LICENSES.md，无 Git commit／add／reset／clean。最终保护哈希和当前风险见本审计 `FINAL.json`。

## 8. 未代签事项

系统解除静音后的最终设备出声／人耳、强烈空大剧院听感、脚步木材贴切性、正式锣鼓／吟唱、首次玩家 5–8 分钟盲测、Shipping 三轮通关、性能定稿与参赛声景仍未验收。技术证据通过不等于这些全部完成。
