# 五态环境 Dev：实施边界

2026-10-11。用户要求进入下一步。唯一人类负责人为用户，Codex 辅助实现与验证。本步不是关闭 M3/M4：首次玩家盲测、5–8 分钟、完整剧场及正式美术均仍待完成。

## 玩家可见结果与验收

现有同一戏台随三次操作形成“沉寂 → 引日 → 逐光 → 落杖前收束 → 真实成林后恢复”五态。只先验证两个无阴影强调灯的有限对照，不能宣称灰盒变成完整高质量剧场。正式柱梁、幕布、台翼、道具、远景与文化造型接入在该稳定合同之后推进。

新 Dev 地图：`/Game/DengYingShanHai/Dev/EnvironmentStates/Maps/LV_EnvironmentStatesLab`。它是现有单舞台的隔离测试副本，不是第二个竞赛场景。旧地图、AudioDev Run3 包与 Start-AudioDev.cmd 完全保留。

## 布局、所有权与通信

`Puzzle Director 已成立的三幕事实 → ADYStagePresentation → 显式 ADYStageEnvironment → 两盏既有表现强调灯`。

Director 的判断、身份及完整林影接受规则不变。Presentation 默认关闭新 opt-in，仅新地图实例开启；Environment 仍是当前 World 的可放置表现 Actor，只接受明确状态，不引用 Director、不决定成功、不控制相机/输入/声音、不 Tick 扫描世界。没有新增 Subsystem、全局事件总线或独立流程机。之所以使用直接引用，是现有稳定的一对一关系，不需要发现/广播路由。

## 状态合同

| 已成立事实 | 环境状态 |
|---|---|
| 未开始、Inactive、P01 Playing | Dormant |
| P01 成功/AwaitingTransition、P02 Playing | SunAwakened |
| P02 成功/AwaitingTransition、P03 Playing | ChaseAwakened |
| P03 真实成功/AwaitingFinale | FinaleReady |
| 实际杖尖接触、真实满生长林影通过现有检查后 Complete | ForestComplete |

接触、首次生长和未完成林影都不能冒充 ForestComplete。本步不把 Holding 的每次进入/打断追加为新环境切换；P03 Resolve 才开始落杖前收束。当前幕 R 仍返回当前幕基线；重新复演仍 OpenLevel，新的 World 重新 Dormant。迟到同步只读当前终态，不重播落杖/接触/声音或创建分枝。

广播环境状态后重新核验 ActivationToken、生命周期及完整序列快照；Complete 保留激活身份时也不能尾随旧 AwaitingFinale 通知。监听者若重入复位或销毁，旧通知不能继续覆盖新快照。缺失、销毁或跨 World 环境引用不产生环境调用或成功授权；本轮保持已配置环境的现有同步边界，不宣称重构了缺失引用时的全部 UI 降级。原枚举 0/1/2 保留，新值附加。

## 光照候选与冻结边界

沿用 UE 5.8.3 Win64 Development、当前渲染配置、手动曝光、原灯位置/颜色/范围/光源尺寸和两盏 Movable Point Light（Lumens，无阴影）。不启用 MegaLights、不增灯或改变主灯投影。前三态数值保持；FinaleReady 只把已验证 Chase 两灯强度乘 .5/.25，ForestComplete 重组已用过的 Sun 5000 lm 和 Wing 4500 lm 上限。数值只用于这套现有距离与曝光下的 Dev 对照，不是正式戏台照明建议或物理声光复原。固定机位验证可读性，不把测试后台设置下的帧率当目标机性能验收。

E/A/D/R、WASD、人物360cm/s、灯速.2625、偶速.28、15Hz、目标/容差/保持、2秒题签、相机、A端/Z70、Drop→Contact→Forest→Complete、菜单及重演、声音和已修复脚步冻结。不增加时长、场景、输入或玩法；不导入任何新第三方资产/付费内容。

## 文件白名单和回退

源码改 StageEnvironment.h/.cpp、StagePresentation.h/.cpp 和现有 DYActSequenceAutomationTests.cpp；实际诊断发现独立新地图不在精确菜单白名单，额外只登记 DYDevEntryPlayerController.cpp 的该新路径并补 DYEntryLoopAutomationTests.cpp 原身份测试。此范围增量单列 SCOPE_EXTENSION.json，不修改初始 BEFORE.json。新增地图、创建/验证脚本、独立 Start-EnvironmentDev.cmd/helper 和本步方案/验证文档；更新 TECH_SPEC、DEVELOPMENT_PLAN。所有 .uasset、旧 .umap、Config、其他源码、原启动器、旧包及用户未提交改动受哈希保护。

原文件副本与全保护清单在 `Saved/Audit-2026-10-11-EnvironmentStates/Before`、BEFORE.json。新构建固定身份 `EnvironmentDev-20261011-Run1`，不覆盖旧包、不随意选择“最新包”；无 Git 写操作或删除。源音与许可证链沿用既有文件，不读取或修改之前受限的许可登记表。

## 顺序与退出门槛

1. 保留基线；实现默认关闭的五态纯映射及幂等环境表现。
2. 原生原145项继续通过，新增真实三幕/接触/部分生长/几何篡改/最终接受/重入/迟到/复位/默认兼容测试。
3. 复制仅一张 Dev 地图，只开启新 opt-in，冷读确保全部引用重定位到新 World、几何/相机/参数不变。
4. 真实现有控制请求完成两轮三幕和重演，记录五态与主灯/影子同框截图；未通过不能以手工 ApplyState 冒充流程证据。
5. UAT 显式地图 Cook、Stage、Package、Archive，冻结源码/资产/验证输入及产物哈希；独立包实际启动与正常退出、启动 DryRun。
6. 更新验证文档，交付直接可打开地址。机器验证不代签正式美术、首次玩家、人耳、包内真人完整通关、Shipping或最终性能。
