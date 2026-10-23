# 新夸父 E 交互选区修复记录（2026-10-18）

负责人：项目负责人（Codex 协助实现与验证）。

## 玩家可见结果与原因

当前新夸父的可见网格 `KuafuMesh` 使用 NoCollision，E 的 Visibility 射线实际命中隐藏的旧 Torso 代理。旧代理的局部尺寸约为 48 × 16 × 115 cm，与新人物可见范围不匹配，因此需要精确瞄准很窄的区域才能操控。

本次在现有 `BP_DYKuafuPuppet_Fitted` 中增加独立的 `PuppetInteractionBox`，覆盖三姿态的可见网格联合范围。玩家瞄准人物身体、衣片附近即可通过原来的 E 入口操控。

## 最小资产变更

- 资产：`Content/DengYingShanHai/Dev/KuafuAppearance/Presentation/BP_DYKuafuPuppet_Fitted.uasset`。
- 新 Box 直接挂到继承的 SceneRoot，局部旋转为零、缩放为一。
- 局部中心：`(-0.160004, -48.278649, -7.824226)` cm。
- Box Extent：`(25.573041, 81.204117, 96.254249)` cm，即完整尺寸约 **51 × 162 × 193 cm**。
- Y/Z 使用三个实际姿态的可见网格包围范围，无额外留白；X 厚度沿用旧 Torso 的最大深度，避免扩大到前后远处。
- QueryOnly；仅 Visibility 为 Block，其他通道为 Ignore；无 overlap 事件、无阴影、游戏中隐藏。

未改 C++、姿态动画、皮影几何、材质、谜题判定、控制距离或地图。独立 Box 避免改变原 Torso 被角标与成林保护使用的范围。当前正式主图仍使用原有灰盒偶；本次验收针对新夸父 Dev 候选与其 B 方案包。

保存后资产 SHA256：`76ED0EFE2D890FE31A94A73F8FB52AA9E84CC4C50F327C76B82BFF809734B82A`。

## 验证结果

1. 原生 UE 冷加载复核通过：新 Box 配置正确，旧组件、父类、控制参数与 Blueprint 图行为保留；未再次编译或保存。四个隐藏且未连接的 ErrorTolerance PinId 属于加载时重建的临时标识，比较时只对这些标识作限定规范化。
2. 实际 RHI PIE、原 Pawn 和 CameraManager、原生 0.10 秒焦点定时器下，三姿态各九个采样点，**27/27 命中新 Box，并通过 E 所调用的 `ToggleControl` 进入和退出操控**。
3. 另四项通过：P01 禁用时虽命中新 Box 但无法聚焦；选区外不聚焦偶；约 809 cm 外不聚焦；附近灯具正常聚焦并进入和退出操控。合计 **31 项**。实际 EndPIE 后 dirty maps/assets 均为空。
4. 现有 `DengYingShanHai.M1.Focus` **5/5 自动测试通过**，涵盖镜头偏移、700 cm 操作半径、接口契约、无 Tick 生命周期和真实射线/遮挡。
5. Windows Development Run2 的 Cook、Stage、Pak/IoStore、Archive 成功，ExitCode=0；UFS 清单含 B 候选地图、修复后的 Fitted BP 和专用角标 MI。
6. 实际启动 Run2 包，载入指定候选地图、生成 1280×800 截图并查看，标题界面与场景正常显示；15 秒后正常退出，ExitCode=0，未发现 Fatal/Unhandled/Assertion 日志。

测试边界：27 个点使用 E 的原生语义入口，未注入实体键盘按键；Run2 包完成启动冒烟，本轮未在包内重复整段三谜题通关。809 cm 样本的原始射线未命中，不单独作为“命中后半径拒绝”的证明；该规则由现有 RuntimeTrace 与 OperatorRadiusGate 测试验证。未新增专门针对 Box 的墙体测试。

## 入口、证据与回退

- 已更新原入口：`P02GuideAudit-20261018/Start-P02Guide-B.cmd`，指向 `C:/UEProjects/DYBuilds/P02Guide-B-20261018-Run2/Windows`；原 Run1 包保留。
- 作者、冷加载、真实焦点和回归证据：`D:/灯影山海/Saved/Audit-2026-10-18-InteractionReach/` 下的 `Author-Run2`、`Cold-Run2`、`Focus-Run1`、`NativeFocusTests-Run1`。
- 打包日志与结果：`InteractionReach-20261018/Package-Run2.log`、`PACKAGE.json`、`VERIFICATION.json`。
- 打包启动证据：`C:/UEProjects/DYBuilds/P02Guide-B-20261018-Run2/Smoke-Run1/`。
- 修改前资产与启动脚本备份：`D:/灯影山海/Saved/Audit-2026-10-18-InteractionReach/Baseline/`。需要回退时由项目负责人恢复其中的 BP 与启动脚本备份；Run1 包无需重新生成。

后续手感由项目负责人在该入口实际游玩确认；本次没有新增功能或美术制作任务。
