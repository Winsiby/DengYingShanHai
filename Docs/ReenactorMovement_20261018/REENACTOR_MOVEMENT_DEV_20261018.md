# 复演者第三人称 Dev 样本 · 2026-10-18

唯一人类作者与最终负责人：用户。Codex 仅作本轮实现、验证和文档辅助。

## 这个样本是什么

把用户提供的复演者模型接到现有第三人称操作载体上，先在独立 Dev 关卡验证待机、行走、镜头、复位和脚步时钟。它不是新的正式游戏入口，也不替换主剧情里的角色或镜头。

入口：双击 `D:\灯影山海\Start-ReenactorMovementDev.cmd`。

操作：`W/A/S/D` 移动，鼠标转向，`R` 回到起点；关闭窗口退出。`E/A/D` 谜题操作在本样本中不启用。

## 实现边界

- 新增 `ADYReenactorOperatorPawn`，继承现有 `ADYTheatreOperatorPawn`。输入、碰撞、交互组件、镜头跟随和复位逻辑继续复用父类。
- 仅把可视层换成用户的复演者网格；旧圆柱/球占位体在运行时隐藏，不删除原资产。
- 新 Dev 候选速度：`180 cm/s`；脚步距离：`75 cm`。原有版本仍为 `360 cm/s` 与 `150 cm`。两者每秒约 `2.4` 次脚步。
- 脚步左右声源沿用现有 `SFX_DevFootstepA/B`，不新建第二套声音系统。
- 复演者可视网格使用 `NoCollision`，角色运动仍由原胶囊负责。
- 新 Dev 镜头仅调整候选参数：臂长 `460 cm`、目标上移 `20 cm`、Socket 偏移 `(0,55,30)`。正式游戏镜头不变。
- 新 Dev GameMode 隐藏通用 Dev HUD，避免在无谜题的移动场里显示“Aim at the lamp”。

## 动画与同步

新增资产：

- `/Game/DengYingShanHai/Dev/ReenactorMovement_20261018/Animation/A_DY_Reenactor_Idle`（4 秒）
- `/Game/DengYingShanHai/Dev/ReenactorMovement_20261018/Animation/A_DY_Reenactor_Walk`（0.833 秒）
- `/Game/DengYingShanHai/Dev/ReenactorMovement_20261018/Animation/ABP_DYReenactorMovement_V2`

AnimBP 读取现有 `UDYFootstepAudioComponent::GetFootstepDiagnostics()` 的实际位移相位，用 `TwoWayBlend` 在待机与行走之间过渡；没有另开计时器、没有重复音效通知、没有根位移。停止时冻结上一行走姿势再淡出到待机，避免脚部瞬间弹回。

## 已实际验证

- UE 5.8.3 英文物理路径独立工程编译成功，无 C++ 编译错误。
- 自动化测试 2/2 成功：
  - `DengYingShanHai.ReenactorMovement.CompiledDefaults`
  - `DengYingShanHai.ReenactorMovement.GameModeComposition`
- 主工程全量自动化：`171` 项成功、`0` 项失败，测试命令退出码为 `0`。
- 真实 `-game` 窗口：待机完整角色入镜；按住 `W` 时动画调试显示 `TwoWayBlend Alpha=98.9%`，`SequenceEvaluator` 行走时间推进；释放后回到待机。
- 运行时默认值：180 cm/s、75 cm、左右脚步声源均已绑定、镜头 460/20、可视网格无碰撞、HUD 为空。
- 截图和自动化日志保存在 `Docs/ReenactorMovement_20261018/Evidence/`。
- 发布到主工程后，又从 `D:\灯影山海\Start-ReenactorMovementDev.cmd` 启动真实窗口复核：待机和按住 `W` 的行走均正常；主工程截图保存在同一 Evidence 目录。

## 还没有完成

- 还没有把复演者接入正式三幕关卡或正式剧情镜头。
- 还没有 Shipping/Development 打包验证、目标机帧率、LOD、重拓扑、全身 IK 或脚掌贴合。
- 单方向行走循环遇到急转、倒退和复杂台阶仍需人工盲测；当前只验证平地移动。
- 没有战斗、跳跃、冲刺、蹲伏、攀爬或多人同步。
- 用户提供的模型授权/第三方组成仍待补全，本样本仅作本地 Dev 验证，不据此公开发布。

## 回退

不使用新入口即回到原流程。发布前已把旧编辑器 DLL 备份到 `Saved/ReenactorMovement_20261018/PrePublish/`。新增内容位于 `Content/DengYingShanHai/Dev/ReenactorMovement_20261018/`，不引用正式主地图；删除该目录和入口即可撤销本次 Dev 样本。旧资产和用户源模型未被覆盖。

## 下一步

先人工确认第三人称视距、转身和脚步节奏；通过后再做复演者到正式入场/幕后场景的挂接，并处理夸父独立手杖与第三幕真实投影。不要用本移动样本替代对三幕谜题或正式美术的验收。

## 追加修复：后背衣物闭合（同日）

原模型不是透明材质问题。`SK_Short_Vest_l` 与 `SK_Short_Vest_r` 两块短背心在脊柱中间留下一条约 11 cm 的开口，露出整片米色内衫；从游戏第三视角看会像衣服后背没有扣合。

修复做法：

- 保留 v03 原文件，另存为 `Assets/Sources/DengYingArt/ReenactorBackFix-20261018/DY_Reenactor_Cue_v04_backfix.blend`。
- 从 `SK_Ivory_Tunic` 的后背曲面复制出 `SK_Vest_Back_Closure`，保留原 40 个骨骼顶点组和 Armature 修改器。
- 新后片位于 `y > 0.060、0.995 <= z <= 1.376` 的背心范围内，整体向后偏移 5 mm，仍藏在左右背心片内侧，避免 z-fighting。
- 赋予 `M_Deep_BlueGray` 深蓝灰背心材质；新片为 41 顶点、28 面、单一材质分区。
- UE 中以独立骨骼网格衣物层 `SK_DY_Reenactor_VestBack_Closure` 加载，使用 `SetLeaderPoseComponent` 复制主体网格姿态，不创建第二套 AnimBP 或脚步时钟。

验证：

- Blender 前后同机位渲染：`Docs/ReenactorMovement_20261018/Evidence/back_before.png`、`back_after.png`。
- UE 真实窗口待机和行走：`ue_back_fixed_idle.png`、`ue_back_fixed_walk.png`。
- 复演者专项自动化 2/2 成功，新增检查确认衣物组件存在、网格已绑定、无碰撞。

当前衣物后片是独立 Dev 层，增加一个绘制批次；正式优化阶段可在确认外观后合并回主体网格。没有覆盖用户的 v03 原始 ZIP 或原始 blend。


## 追加：移动样本独立 Development 包与运行时核验（2026-10-18）

本轮沿用已有复演者和背片，补齐了本移动样本的 Windows Development 独立打包与包内运行时技术核验。上文“还没有 Development 打包验证”是本次更新前的历史状态；正式三幕/Shipping/目标机性能和作者观感验收仍未完成。

- Editor 完整回归 172 成功、0 失败；包内 RuntimeLifecycle 1 成功、0 失败；真实 D3D12 SM6 渲染与进程退出 0 均有证据。
- 测试覆盖真实地面移动/停止/复位/换方向、运行时动画与脚步位移相位、背片 LeaderPose、占位体隐藏和销毁清理。程序化输入不代替人工键鼠/听感确认。
- 修复了现有夸父 Editor 测试缺少 WITH_EDITOR 编译条件而阻塞 Game 构建的问题；保留五项 Editor 覆盖，未改玩法、蓝图、正式 Config 或资产。
- 新入口：`C:\Users\lenovo\Documents\ChatGPT\数媒游戏开发 2\ReenactorValidation-20261018\Start-ReenactorMovement-Package.cmd`。固定指向该目录的 `Build-Run2\Windows`，与旧入口并存。
- 最终记录、30 项包内关键资源核对、281 项原工程文件核对、失败尝试及 AI 使用记录见 `C:\Users\lenovo\Documents\ChatGPT\数媒游戏开发 2\ReenactorValidation-20261018\RESULT.md` 和 `VERIFICATION.json`。

负责人仍为用户；下一步由用户确认第三人称视距、转身与脚步节奏，再决定正式场景挂接。

## 追加：v09 单一网格接入（2026-10-18 晚）

已把去除肩后蓝披布的 v09 修正网格接入现有复演者 Dev 角色，默认网格从 v03 主体加独立后背补片改为单一的 `SK_DY_Reenactor_NoShoulderDrape_v09`。同步删除 `VestBackVisual` 组件和其运行时 LeaderPose 绑定，自动化断言改为角色只存在一个骨骼网格组件。输入、移动速度、步距、镜头参数、脚步音频和正式三幕流程均未改动。

验证证据：

- Editor 编译退出 0；构建快照工程回归 167 成功、0 失败（快照测试集合少于主工作副本此前的 172 项，不能直接等同）。
- Game 编译退出 0；Windows Development 包重新打出，UAT `BUILD SUCCESSFUL`。
- 包内 `RuntimeLifecycle` 1 成功、0 失败；两秒前进 353.53 cm，复位后再次移动通过。
- `ReenactorIntegration-20261018/InGame-Idle.png` 为 Dev 入口真实游戏窗口；`Packaged-Idle-v09.png` 为包内进程真实窗口。两张均为待机画面，不代替急转、倒退、台阶和真人键鼠手感验收。

入口：`D:\灯影山海\Start-ReenactorMovementDev.cmd` 仍是编辑器 Dev 入口；独立包使用 `ReenactorIntegration-20261018\Start-ReenactorMovement-Package.cmd`。旧 DLL 备份在 `D:\灯影山海\Saved\ReenactorIntegration_20261018\PrePublish\`，旧 Pawn 源码快照在 `C:\UEProjects\DYReenactorCheck-20261018\Source\DengYingShanHai\Private\Player\DYReenactorOperatorPawn.cpp`。

本轮仍不包含正式三幕挂接、Shipping、目标机帧率、LOD、重拓扑或全身 IK 验收；用户模型的授权与第三方组成仍待补记。
