# 脚步与移动同步修复记录

日期：2026-10-10。请求：脚步声没有与人的移动同步，修改。唯一人类负责人为用户；Codex 辅助实现、测试、审计与打包。本轮不委派 WorkBuddy 修改产品。

## 玩家可见结果与根因

从站立开始走动或短距离点按时尽快听到第一步，后续步频随实际行程变化；真正停住后不再有直接脚步，空剧院只剩自然回响。人物速度、输入、镜头和三幕机制保持不变。

旧逻辑要累计 150 cm 才发第一步，并且普通静止回调不停止当前直接声源。旧 `Audit-2026-10-10-TheatreAudio/Footsteps-Run3/Footstep_RESULT.json` 中，实际移动首次采样为 2.016 秒，首个 Play 请求为 2.500 秒，相差约 484 ms；Dry 零水平速度采样为 3.079 秒，直接声源仍持续至 3.329 秒。素材仅约 4 ms 前置静默，无须重新生成素材。

## 修改、边界与回退

- 修改三份原生文件：`DYFootstepAudioComponent.h/.cpp` 和 `DYFootstepAudioAutomationTests.cpp`。其余原生文件、全部 Content（含地图／Blueprint／声音）、Config 和根 CMD 不改。
- 起步采用锚点 2 cm 净水平位移；之后每 150 cm 一声。起步 overshoot 保留，避免相位随帧分割变化；同更新最多一声。亚阈值往返抖动不能累加出假起步。
- 普通真实停步返回一次停止决定，只停当前 owned 直达声、清空运动债务，保留 Stage 独立房间混响。松开输入后按原移动组件正常减速，不强停人物或改输入。
- 增加只读 `moving / movement_start_events / stop_events / last_*_seconds` 诊断。播放请求不是系统声卡／人耳播放证据。
- 更新固定包选择的 `Scripts/Start-AudioDev.ps1` 和 `TECH_SPEC.md`，新增本记录。启动仍为 `D:\灯影山海\Start-AudioDev.cmd`，选择 `Builds/AudioDev-20261010-Run3/Windows`。
- 旧 Run2 及此前包保持不变；旧三份源码、启动 helper 和 TECH_SPEC 精确副本在 `Saved/Audit-2026-10-10-FootstepSync/Before`。未进行 Git 写操作，未删除旧证据、资产或包。

## 验证分层

1. Editor Development 编译实际退出 0；原生自动化 **145 succeeded / 0 failed / 0 notRun**。11 项脚步测试中，新增短步起停再起步、净位移抗抖动；旧分帧／连续性／低帧／静音／复位／真实生命周期契约同步更新。原有其他模块测试继续通过。
2. ColdVerify-Run1 冷读实际地图与 Pawn/GameMode，保存资产列表为空；步距 150、移动速度 360、输入资产与相机合同、音源引用、15 Hz 与第二幕材质仍正确。
3. Footsteps-Run2 为真实 PIE CharacterMovement 驱动，**15 项通过**。每模式 10 秒：0–2 秒静止，2–2.15 秒短点按，4–5 秒再起步行走，其后停稳。Dry/Room/Muted 三模式均真实位移；短点按各一声，长走各三声；Muted 有真实步数但零 Play 请求。模式间真实复位并至少 4 秒静置。
4. Dry/Room 首个实际移动采样 2.015 秒，第一步请求 2.046 秒；再起步亦相差约 **31 ms**。最大观察间隔约 32 ms，每次观察一个原生更新。非静音首次 onset 和 Play 的原生世界时间相同，证明同一移动更新提交，不宣称音频回调或端点延迟为 31 ms。
5. 实际碰撞阻挡独立标记 PASS：最后约 2 秒位移 0、新步数 0、直接声源不播放。腾空无步、实际 R 复位清零并停声、真实 Pawn 销毁释放 voice 均通过。未用 SetActorLocation、改速度或伪造 movement delegate 驱动人物；临时墙只在所属 PIE World，不保存。
6. 三份完整 PCM16／48 kHz／双声道 master WAV 无 rail clipping。预定义 6 组静默窗口全为 0：起步前、短点按停稳后、长走停稳后、Dry/Room 最终静默及 Muted 全段。5.6–6.6 秒 Dry 完全为 0，Room 有限尾音 RMS 约 -83.05 dBFS、peak 0.0005188；8–9.8 秒 Room 也为 0。只证明数值尾音保留／消散，不证明真实大厅声学或人耳品质。
7. VisiblePlay-Run1 **65 项检查、35 张过程截图**，两轮完整三幕、一次同地图实际重演和两次真实成林回归，实际进程退出 0；包含正常／静音演出与第二幕参考检查。正常整段混音无削波，静音重演 WAV 全为 0。原始 Result/AUDIO_RESULT/MIX_QA 为事实源。
8. 新独立 Win64 Development 包须使用以上当前源码验证结果，显式 Cook 当前地图。包装输出、源码／资产／验证输入哈希在 Package-Run1；真实包启动首帧／原生 20 秒正常退出在 FirstFrame-Run1，Auto/Package/EditorGame/CMD 四项 PS5.1 只读 DryRun 在 Launcher-Run1。最终结案闸门为审计根 FINAL.json；闸门失败时不能据本文件提前宣称完成。

## 保留的测试工具失败

- Footsteps-Run1：后台编辑器仅稀疏更新，整个 0.15 秒点按窗口没有被调用，测试失败，未算产品通过。重试仅在**测试子进程**设置 `-unattended`、后台 CPU throttle=false、Slate throttle=0、t.MaxFPS=60 并读回；未保存全局配置，也未加入玩家启动器。该测试不作为性能测量。
- 数值检查最初误用系统 Python 3.14，而已有 soundfile/cffi 扩展为 cp312，导入失败且未生成 QA 报告；改用已配置 Python 3.12.14 运行成功。没有安装新依赖或改变用户 Python 环境。

## 尚未代表的验收

当前人物仍为无骨骼步行动画的灰盒，本次只与真实位移起停同步，不是足落地帧同步。录音只有 UE 游戏内 master，不是桌面声卡回录；WAV 原点和观察器 wall time 非 sample-exact，Room 第二段可能含前段尾音，不拿其第一个非零点充当重新起步攻击。包内完整物理键鼠／听感、新骨骼动画、不同设备、Shipping 和最终 5–8 分钟盲测仍未由本次自动验证代签。

真实电脑试听建议：双击根 Start-AudioDev.cmd，开始后短点按 W、持续前进再松开、停住再走、顶墙、E 操纵灯偶。应为起步迅速有声、停稳只有大厅尾音、顶墙不新增脚步；原三幕和菜单正常。此说明是交付验收提示，不是新增开发审批。
