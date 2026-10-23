# B 摆放：独立可玩 Dev 样本

2026-10-13。唯一人类作者与负责人：用户本人；Codex 辅助实现、测试与文档。接 `FRAME_BEAM_JOINT_AB.md`，把已拍摄对照的 B 摆放做成可独立比较的开发样本，不把它升级为正式美术定稿。

> B 独立 Dev 候选已完成本轮技术回归与真实 Development 包首帧／正常退出检查。157 项原生测试、完整演出与控制回归、固定包和实际中文菜单 → 点击开始 → B 场景已分别留证。B 仍非正式美术定稿，包内完整三轮、包音频与人工体验仍待验；最终产品发布保护以本轮 FINAL 为准。

## 1. 这一版看什么、怎样打开

目的只有一个：在原“开始—三幕—落杖成林—结束—重演”里，观察横梁右移后，右梁柱关系与幕左端是否仍读得清楚。文化创新仍是“以灯为日、以影为夸父”和玩家动作直接造成成林；木构只服务演出，不宣称历史复原、真实榫卯或承重合格。

新入口为 `D:\灯影山海\Start-FrameBeamCandidate.cmd`，默认只启动固定的 `D:\灯影山海\Builds\FrameBeamCandidate-20261013-Run1\Windows`。三种 CMD DryRun 与**真实包中文菜单、点击开始后的 B 场景、正常退出**均已实际通过。在文件资源管理器双击 CMD；聊天点击若显示代码，使用文件位置打开。

原样 A 仍可从 `D:\灯影山海\Start-FrameBeamDev.cmd` 打开，原图和 `FrameBeamDev-20261012-Run1` 包不被覆盖。图文报告位置为 `D:\灯影山海\Docs\FRAME_BEAM_CANDIDATE_DEV.html`；上轮同机位 A/B 原图仍见 `FRAME_BEAM_JOINT_AB.html`。

## 2. 精确变化与代价

| 条件 | A 原样 | 本轮 B 候选 |
|---|---:|---:|
| 横梁 Actor Y | 23.22415363604682 cm | 66.77584636395318 cm |
| 相对 Y 位移 | 0 | +43.55169272790636 cm |
| 真实柱顶共同平面覆盖 | 421.828972 cm² / 8.754% | 2323.173235 cm² / 48.212% |
| 全梁 Y 范围 | −493.551693～540 cm | −450～583.551693 cm |
| 梁底左端相对幕左缘 | 覆盖有余量 | 短 27.367484 cm |

新图精确身份：`/Game/DengYingShanHai/Dev/FrameBeamCandidate/Maps/LV_FrameBeamCandidateLab`。由旧 `LV_FrameBeamPlacementLab` 复制，**仍是 35 个 Actor，没有增加或删除 Actor**。梁 X950、Z816.7876838516025、Pitch0/Yaw90/Roll0、XYZ 等比 .39290377163557627 保持。旧柱、幕、木地板、屏风、主灯、曝光、音频、输入与全部旧地图保持。

“保幕宽”只指全梁外轮廓仍跨原 900 cm 幕宽，左端刚到边缘；不表示梁底全宽覆盖、完整柱顶覆盖或完整幕框。B 消耗左端余量，窄 X 截面和未完成左支撑也没有被修复。大幅 +66.657861 cm 候选不在本轮采用范围。

## 3. 架构和生命周期保持什么

横梁仍为本 World 拥有的原生、被动 `StaticMeshActor` 与唯一网格组件。Static、Actor/组件 Tick 关闭；Actor 总碰撞 true，组件与 BodyInstance NoCollision、公开八通道 Ignore、Overlap false；投影、HiddenShadow、动态间接与距离场影响标志关闭。它不实现 Controllable，不引用 Director 或 Stage，不新增 Timer、扫描、状态、BP、复制、存档或网络能力。这些标志不等于所有 GI／反射路径零影响，GPU 与实际游戏 mip 仍需另测。

既有职责不变：Director 持有谜题与幕次事实；Stage Presentation 消费事实并显式调用同世界 Environment；UI 只发按钮意图、显示玩家反馈；PlayerController 仍为菜单输入和游戏最终 POV 的既有所有者。梁没有通信需求，不为静态陈设搭建接口、Subsystem 或全局消息系统。重演沿用精确同图 OpenLevel：旧 World 清理委托、计时器、交互和音频，新 World 重建；不保留旧状态或假造林形。

依赖仍为旧梁 SM → 旧常量 `MI_DY_FramePost_Wood` → 旧 `M_DY_FramePost_Master` → 三张 Dark Wood 纹理，无新模型、材质、纹理、音频、字体或插件；复用已有免费／CC0 来源与适配证据，不新增采购或生成服务。UV QuarterTurn1 `(V,1-U)` 与 NormalDX `(-Ny,Nx,Nz)` 不改，源 texel/m 不冒充运行时 mip。受限许可登记本轮不读取或哈希。

E/A/D/R、灯速 .2625、偶速 .28、15 Hz、目标／容差／保持、2 秒 Dev 题签、第二幕身形参考、A 杖尖／Z70、跨幕退出操纵、脚步同步、大厅尾音与 Drop → Contact → Forest → Complete 全部沿用。没有新机制、输入、镜头或竞赛场景，仍不绑定每日开发计划。

## 4. 本轮验证进度：不能混用证据

| 验证层 | 本轮实际状态 | 能证明与不能证明 |
|---|---|---|
| Editor Development 构建 | 实际退出 0 | 可编译，不代表画面／包通过 |
| 原生项目自动化 | 157 成功 / 0 失败 / 0 未执行 | 包含本图精确身份用例；旧身份、上下文拒绝与 Shipping 门控保留 |
| 新图 probe / create / cold verify | 3772 / 9035 / 6025 审计断言通过 | 实读 35 Actor、仅保存指定新图；数字不是数千个游戏单元测试 |
| 可见两轮三幕／成林／重演、五态最终 POV、混音 | `VisiblePlay-Run1` 实际退出 0；65 流程／35 环境通过，旧柱 10／新梁 10 观察，两次成林、一次 OpenLevel 重演 | 两 cycle UE Master Mix WAV 已导出，不代表 Windows 输出／人工听感 |
| 控制／跨幕释放／R／行走与 EndPlay | `ControlProbe-Run1` 实际退出 0，41 项通过；两次成林、一次真实重演及旧 World 清理 | 语义驱动不等于物理键盘或首次玩家盲测，聚焦取景与固定 POV 分组 |
| UAT Build/Cook/Stage/Package、IoStore 与封存 | UAT 实际退出 0；三个原生 IoStore 检查均 0，50 文件封存 | 实际新图／依赖与全部 payload 已查；仍必须另验实际包启动 |
| CMD／PS5 DryRun | 默认 Package、显式 Package、显式 EditorGame 实际退出均 0 | 未启动 UE／游戏，不等于首帧或全包通关 |
| PS5 解析／隔离门控反例 | 原生 PS5.1.26100.9444 解析 0；Run2 实际 31 例全匹配，4 正／27 负、非 null 子进程退出 | 首轮 29 例另保留；fixture 不等于实际包首帧 |
| 真实包首帧／正常退出 | `PackageFirstFrame-Run1` 实际 PASS；同 PID10892／窗口591026，中文菜单 → 点击开始 → B 场景 → 正常 Alt+F4，Game 0／CMD 0 | 同一实例继续验收、无重新启动／重建包，仍非完整包通关／包音频 |
| 包内完整三轮、Windows 输出／人工听感、正式美术、Shipping | 未通过／未执行 | 保持待验，不代用户签收 |

地图读取只准 7 个明确 Y 标量与旧冷读不同：Actor 位置 Y、组件 relative/world 位置 Y、beam 位置 Y、bounds origin/min/max Y。每项只接受精确 +43.55169272790636 cm，浮点容差 1e-7 cm；归一化新旧地图包名前缀后，其他键、值、列表严格保持，不能整体豁免 Actor／Transform。创建和另进程冷读分开，避免把内存 B 状态当作已序列化。

编图元数据初版少了 Actor Label，主代理在运行静态识别后只补该 key；保留 `PLACEMENT-AUTHORING.json` 和独立补充记录。未发生该问题的原生 FAIL，不把工具静态补全说成产品修复或失败重跑。

五态实际最终 PlayerCameraManager POV 均为位置 `(-1260,-155,178.1500015258789)`、旋转 `(0,0,0)`、FOV70、同一所有者；主代理已逐张查看原生 PNG。它们是 Editor 实例中的 viewport 截图，包含开发界面，不是 standalone／正式镜头定稿。控制探针因聚焦而临时调整视线，不能替代该固定 POV 组。全过程 338 产品精确集合／SHA 保持，无相机、灯、材质或谜题产品修改。

## 5. 包与入口的验收合同

本步只交付 Win64 Game Development，不做 Shipping 或发布渠道变更。使用本机 UE 5.8.3 的原生 UAT `BuildCookRun`，记录实际命令、PID、非 null 退出码和分阶段日志；本次独立输出不覆盖旧包。UAT 日志只对子进程隔离到本轮 Saved，不提权、不改全局环境或应用权限。

显式 Cook 根为本精确 B 图；保持 Config 不变，本次实查 Cooked 精确三图：B 图、项目 GameDefaultMap `/Game/DengYingShanHai/Dev/Interaction/LV_InteractionLab`、引擎继承 ServerDefaultMap `/Engine/Maps/Entry`。后两图不提供玩家选择，不说“包内只有一图”。依赖随已有硬引用进入 Cook；不使用 `-cookall`、广泛 AlwaysCook 或手工复制缺失资产。三个原生 IoStore 检查分别验证列表、主 payload、global payload，实际退出均 0；2029 主 chunk／1 global、299312275／3224104 B 全部哈希通过，42 核心＋2 默认 export 实查。

本包封存 50 文件／1,070,536,087 B，绑定本轮实际身份。身份文件生成时 FirstFrame／Gameplay／PackageAudio／HumanVisual／Shipping 均 false，保持历史值；后续首帧只另存补充证据，不追改身份。实际编译工具链为 MSVC14.51.36260（安装目录 14.51.36231）、SDK10.0.26100.0；UE 非首选编译器警告保留，不说零警告、不为本轮改环境。

启动器固定包身份，不选“最新”目录、不静默回退 Editor；只在显式 EditorGame 诊断时使用编辑器。原生 PS5.1.26100.9444 解析 0，隔离 Run2 的 31 例（4 正／27 负）实际退出均符合门控；启动器 SHA256 `2118791870CE2E2A691EC2182A2304E215488F4D238E692F0A74307273D7B018`。三种 CMD／PS5 DryRun 已实测退出 0，未运行 UE 或游戏；真实包验收为另一组证据。首轮 29 例与 PS5 作者编码、Package 静态工具 encoding／EOL 检查 FAIL 原样保留，后续仅修审计工具，未因此改产品，不把工具失败伪称游戏失败或覆盖为 PASS。首帧不代替完整包通关、干净无编辑器机器、音频输出、不同显示比例或 Shipping。

首帧检查曾因 Windows 防火墙许可弹窗而 PENDING；官方 Computer Use 技能禁止操作系统安全／权限弹窗，交由用户手动处理，未修改防火墙、权限或系统设置。用户反馈窗口已关闭后，只读核查当刻原 PID10892 仍在，官方插件返回同窗口591026为最小化，不能把先前关闭反馈当成已证实退出。主代理只恢复这一现有窗口：系统弹窗已消失，中文菜单完整可见；实际点击开始、留 B 梁场景原图，再对该窗口正常 Alt+F4，实际 Game 0／CMD 0。没有重复启动、新 Run2、重建或更换包，UAT 仅一次；早先 PENDING 作为历史留存，不覆盖为当时已成功。

当前 `PackageFirstFrame-Run1/RESULT.json` 为 `PASS-PUBLIC-PACKAGE-MENU-START-FIRSTFRAME-NORMAL-EXIT`，`IdentityUnchanged`／`ProductsUnchanged` 为 true，`FullGameplayVerified`／`PackageAudioVerified` 仍 false。`Menu.jpg`／`Started.jpg` 为官方原生 JPEG，保留原文件；配套 PNG 只是将其解码后转封装，逐行比较完整 1922×1248 的 32bpp 像素一致，没有裁剪、提亮或改色，不谎称原生 PNG／无损恢复 JPEG 压缩前图像。

实际 Session log 绑定同 PID10892 的精确候选图 `LoadMap …LV_FrameBeamCandidateLab?Name=Player`、Windows `RequestExit` 与 `Exiting`，不是只凭截图或窗口消失推定退出。最初截图包装工具的 MIME guard 不接受原生 JPEG，失败在任何文件写入之前，未运行／修改游戏；随后保留 JPEG 并验证 PNG 包装，属于工具格式检查，不称游戏首帧 FAIL。

## 6. 文件范围、保护和回退

- 修改两现有 C++：`DYDevEntryPlayerController.cpp` 仅追加本图精确身份；`DYEntryLoopAutomationTests.cpp` 追加独立身份／上下文测试，不宽泛放行 Dev 目录。
- 新增六产品：本图 `.umap`、`Scripts\Create-FrameBeamCandidateDev.py`、`Scripts\Start-FrameBeamCandidate.ps1`、根 CMD、本 MD 和 HTML。
- `TECH_SPEC.md` §34 与 `DEVELOPMENT_PLAN.md` §26 仅保留原字节前缀后追加；其他旧产品、976 旧归档文件、15 源文件、24 隔离来源保护。

冻结 336 产品；创建后 338、入口发布后 340，最终计划 342。精确集合、四旧文件变更、其余 332 旧产品不变、旧包／来源和 Git HEAD／空暂存区是否保护，以本轮最终 `Saved\Audit-2026-10-13-FrameBeamCandidateDev\FINAL.json` 为准；本稿不提前写最终 PASS。保留所有正常、失败和修订记录，不清理／提交／暂存或改写旧身份。新旧 `.uasset` 不靠猜测节点验收，读取实际原生字段和完整契约。

运行回退最简单：正常关闭新样本后，双击原 `Start-FrameBeamDev.cmd`，使用封存旧包；不要求回滚源码或删除新样本。源码变更和文档回退由白名单前后文件留证，不使用 Git reset／checkout 或覆盖用户脏改动。

## 7. 尚未关闭、下一步由谁负责

负责人仍为用户；Codex 辅助后续实施与验证，不增加制作成员。本轮技术回归、固定包及首帧／正常退出已留证，发布保护另由 FINAL 检查，用户可从新旧入口实际比较。B 始终是候选：右接合暗面、内部无缝／穿模、端纹／normal、实际纹理密度、左支撑、布质台翼、完整幕框、正式尺度与空间叙事、GPU、5–8 分钟首次玩家盲测、包内三轮和 Shipping 不随技术样本自动通过。

> *永远不要以牺牲架构设计为代价追求功能；永远不要基于猜测进行权衡——必须与我确认。*

