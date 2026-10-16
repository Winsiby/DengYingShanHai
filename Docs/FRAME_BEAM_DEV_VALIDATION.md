# 一根横梁与右柱｜独立可玩 Dev 样本验收

完成记录日期：2026-10-13；创建/审计与归档目录仍保留原 `2026-10-12` 身份，不因跨日改名。地图、156 项原生测试、两轮真实 PIE、五态固定 POV、被动梁柱合同、41 项控制探针、独立 Development 构建/归档、实际 Cook 根诊断和原生容器全 payload 校验已完成。启动器 29 案例隔离门控、三次真实 CMD DryRun、实际包中文菜单→点击开始→首帧→正常退出均有独立证据；最终发布产品保护以本轮 `FINAL.json` 为准。未完成项不计为 PASS，原运行/检查器失败不覆盖。

唯一人类作者与项目负责人：用户本人。Codex 辅助实现、测试与文档；本步不依赖队友、WorkBuddy 或用户手工建模。承接 `FRAME_BEAM_PLACEMENT_PLAN.md` 的有依据局部接缝候选，不自动接受正式建筑尺度或完整幕框。

> 永远不要以牺牲架构设计为代价追求功能；永远不要基于猜测进行权衡——必须与我确认。

## 1. 玩家可见结果与本次范围

在独立 Dev 比较地图中，现有右侧木柱上方增加一根真实免费横梁，用原“开始—引日启幕—逐光成形—杖落成林—结束—重演”检验它是否干扰演出。梁右端与右柱顶部采用上一步真实底面裁剪所得候选；没有新增左柱。左端目前无支撑，样本不是完成的承托框或结构安全方案。

保留原 34 个 Actor 的已列举变换、组件与流程合同，只增加一个原生被动 StaticMeshActor，总计 35。旧地图、木材资产、地板、屏风、幕布、主灯、曝光、镜头、E/A/D/R、15 Hz、谜题区间与保持、提示框、跨幕取消操纵、音频、真实位移脚步及杖落成林逻辑均不修改。没有新 Blueprint、玩法组件、Director、状态机、子系统或第二时钟。

这是同一剧场的开发比较副本，不是竞赛版本增加第二关卡、核心机制或体验时长。文化创意仍由“以灯为日、以影为夸父”以及玩家第三次组合操作直接继续的“弃杖化林”承担；木构只提供可理解的演出边界，不将资产发布页描述当作特定朝代、法式、遗址或皮影流派复原证据。

## 2. 文件、入口和固定地图身份

新地图精确包名：

```text
/Game/DengYingShanHai/Dev/FrameBeamPlacement/Maps/LV_FrameBeamPlacementLab
```

本次批准修改的既有产品只有四份：

| 文件 | 修改边界 |
|---|---|
| `Source/DengYingShanHai/Private/Core/DYDevEntryPlayerController.cpp` | 仅追加新地图精确身份；旧五图、上下文和 Shipping 边界保持 |
| `Source/DengYingShanHai/Private/Tests/DYEntryLoopAutomationTests.cpp` | 追加对应独立回归测试，不替换旧测试 |
| `Docs/TECH_SPEC.md` | 原字节前缀后追加 §31 |
| `Docs/DEVELOPMENT_PLAN.md` | 原字节前缀后追加 §23 |

新增产品五份：新 `.umap`、`Scripts/Create-FrameBeamPlacementDev.py`、`Scripts/Start-FrameBeamDev.ps1`、根目录 `Start-FrameBeamDev.cmd` 和本文。创建脚本只生成该 Dev 副本，不是运行入口；测试观察器、打包/容器工具与日志保留在本次审计，不加入游戏流程。

实际固定包目录为 `D:\灯影山海\Builds\FrameBeamDev-20261012-Run1\Windows`；新入口为 `D:\灯影山海\Start-FrameBeamDev.cmd`。发布入口三次真实 CMD DryRun 和实际游戏首帧/正常退出已核验。请在资源管理器双击 `.cmd` 启动；聊天中的文件链接可能只打开代码预览。旧 `D:\灯影山海\Start-FramePostDev.cmd` 与其固定包不变，仍可作为对照和回退。

## 3. 被动 Actor、真实变换与依赖

新对象标签 `DEV_FrameBeam_RightJoint`，由当前 World 拥有。Actor 与唯一 StaticMeshComponent 的 Tick 关闭；Static、无 Overlap、无 Controllable、无 Director/Stage 绑定、无 Timer/世界扫描/复制/存档。Actor 总碰撞开关保持 true；组件与 BodyInstance 为 NoCollision、自定义 Profile、WorldStatic，公开八通道全部 Ignore。不能用 Actor 总开关关闭来掩盖组件读回，也不能把公开通道检查冒称所有未来自定义通道已验证。

CastShadow、CastHiddenShadow、AffectDynamicIndirectLighting、AffectDistanceFieldLighting 均 false。这根梁只用于被动构图比较，不验证真实梁影或物理阻挡。原玩法的 UE Movable 主灯、可投影皮影及真实树影保留；这些标志也不等于所有 GI、反射或屏幕空间渲染路径完全隔离。

依赖链只有既有 `SM_DY_FrameBeam_Source` → 既有 `MI_DY_FramePost_Wood` → 既有 `M_DY_FramePost_Master` → 三张 Dark Wood 纹理，没有新材质或新模型导入。来源与既有免费 CC0 取得/派生证据仍见 `FRAME_BEAM_ASSET_SOURCES.md`、`FRAME_BEAM_ASSET_VALIDATION.md` 与 `FRAME_POST_ASSET_SOURCES.md`。本轮未下载新资产，不读取或哈希受限许可登记文件。

```text
Location cm = (950,23.22415363604682,816.7876838516025)
Rotation    = Pitch0 / Yaw90 / Roll0
Scale XYZ   = 0.39290377163557627
World bounds X [928.171408001,971.828591999]
             Y [-493.551692728,540]
             Z [800,856.078061015]
```

梁源长轴 X 等比缩放后长约 1033.552 cm、深约 43.657 cm、高约 56.078 cm；底面 Z800，距原幕顶 50 cm、核心保护盒顶 30 cm。既有右柱位置和 8m 候选高度不动，梁与柱使用同一源件缩放比例，不对截面单轴拉伸。

上一步实读源梁最低 polygon 9 与柱顶 32 边 polygon 30 得到约 421.829 cm² 共面交集；本次实际 Actor 变换与冷读 bounds 对应该候选。数值不是榫卯、UE 物理接触、承重或近景接缝画质认证。居中候选的整梁 AABB 虽看似重叠，真实底面仍离柱顶 11.301 cm，因此未采用；没有通过移动幕布或右柱迁就它。

材质保持 QuarterTurn1 `(V,1-U)` 与 NormalDX 基底 `(-Ny,Nx,Nz)`。同一旧实例不意味着密度一致：柱约 259.60 源 texel/m、梁顶约 140.11、两侧/底约 198.15。现有父材质没有 Tiling 参数。本次不通过修改共享材质“修复”密度；这些是 2K 源纹理采样覆盖，不是实际 mip、屏幕像素、美术目标或近中远质量验收。

## 4. 已完成的真实检查

审计根：`D:\灯影山海\Saved\Audit-2026-10-12-FrameBeamPlacementDev`。各运行输出不覆盖，保存实际可执行路径、启动参数、先取得的原生 Handle、非 null 实际退出码、执行脚本和输入哈希。

| 阶段 | 实际结果与范围 |
|---|---|
| Editor Development 构建 | 构建实际退出 0；没有执行 Shipping |
| 原生项目自动化 | 156 succeeded / 0 failed / 0 notRun；新增 `DengYingShanHai.EntryLoop.FrameBeamExactMapIdentityAndContexts` 成功 |
| `probe-Run1` | 1476 条审计检查，旧图 34 Actor；保存 0 |
| `create-Run1` | 2242 条审计检查，新图 35 Actor；只保存指定新地图，无旧资产保存 |
| `verify-Run1` | 真实 D3D12/SM6 冷加载，1498 条审计检查、35 Actor；保存 0 |
| `VisiblePlay-Run2` | 65 流程 + 35 环境检查，2 次实际成林、1 次真实 OpenLevel 重演；原观察器判据未放宽 |
| 被动梁柱运行时合同 | 两轮各五态，原柱 10 次、新梁 10 次独立观察；不计入或膨胀 65/35 原计数 |
| 实际游戏音频混音 | `AUDIO_RESULT.json` PASS；两轮 WAV 导出完整，第一轮有声与第二轮静音事件/状态关系保留 |
| `ControlProbe-Run1` | 41 项真实控制探针检查、2 次实际成林、1 次重演、位移行走及真实 EndPlay 清理；未录制音频混音 |

1476/2242/1498 是审计断言，包含冻结文件和对象合同，不是 156 之外又新增数千项游戏单元测试。保存指定新地图两次是模板初建与最终写回同一地图，不是创建两张场景。

新增精确身份测试覆盖 Game/PIE 的合法规范身份和 PIE 名称、错误路径/后缀/上下文拒绝、旧五图不回归、Shipping 拒绝；没有把整个 Dev 目录或任意相似地图名放行。Shipping 的纯身份规则测试不等于构建或运行过 Shipping 包。

五态对照由 `VisiblePlay-Run2/ENVIRONMENT_RESULT.json` 的实际 PlayerCameraManager 读回与五张截图共同证明：Dormant → SunAwakened → ChaseAwakened → FinaleReady → ForestComplete。实际 POV 都是 Location `(-1260,-155,178.1500015258789)`、Rotation `(0,0,0)`、FOV 70、同一最终 POV Owner；观察器没有相机写入。固定 POV 阈值仍是位置 0.1 cm、旋转/FOV 1e-5，没有改为视觉近似。

`ControlProbe-Run1` 为验证真实 Collision Focus 而暂时瞄准灯/偶，再恢复视线，`no_camera_writes=false`；它不冒充固定 POV 证据。驱动只设置控制值与语义请求，不直接 BeginControl、不伪造 Focus、不驱动 Cue；真实会话、跨幕清除、映射上下文、R/失焦恢复、重演及最终销毁按原探针合同验证。角色真实行走约 1037.94 cm，不是瞬移。这仍不是物理键盘/鼠标或首次玩家盲测。

音频证据只录游戏 Master Mix，`AudioMix-Cycle1.wav`、`AudioMix-Cycle2.wav` 导出完成；耳朵听感和 Windows 输出设备检查均 false，不能用有 WAV 代签用户“听到声音”。控制探针的 `audio_mix_recorded=false` 也不能复用上一次文件称为其自身音频验证。

## 5. 保留失败及判断边界

`VisiblePlay-Run1` 真实达到第一次成林，但“五态同实际最终 POV”严格断言失败，只有 33 项流程检查、1 次成林及 5 次梁/柱观察，不能计作完整通过。四个前态的 POV 相同，ForestComplete 时 PlayerController 朝向变了、角色位置没变，导致 PlayerCameraManager 位置变化；证据不支持“镜头延迟”。没有原始输入来源记录，不能确认是人工鼠标、捕获残留或其他输入。

该失败记录、截图、混音与实际原生退出 0 均原样保留；测试失败与进程正常退出是不同事实。随后 `VisiblePlay-Run2` 在不改产品、不改观察器 POV 判据、不强制复位相机的情况下完整重跑成功。后一次 PASS 不抹除第一次 FAIL，也不将未知输入来源写成已修复 Bug。

旧阶段的源节点计数、创建/WorldMemoryLeaks、Zen 松散文件检查器和通用 smoke 断言记录仍保留。本轮没有以新样本通过宣称全部日志零错误。接缝近景、端头法线、木纹割裂、主灯光锥、反射及 GPU 开销各有自己的证据边界，不能从 AABB、低面数或不投影标志直接推定。

## 6. 独立打包、实际默认 Cook 根与容器

仅在本轮运行时门槛实际通过后，执行一次新 Windows Development/Game/Win64 Cook/Stage/Archive，Engine 5.8.3。实际 UAT 退出 0，构建成功；独立 Cook、Stage、日志与归档目录，不删除/覆盖旧包、不选“最新目录”、不改全局环境或应用权限。

`Package-Run1/RESULT.json` 原样仍为 FAIL：后置检查错误要求“实际只 Cook 一张显式地图”，报 `Exact set mismatch: sole explicit cooked map`。这与 UAT 真正退出 0 是不同事实，不能为了交付把原 RESULT 改成 PASS，也不是凭日志成功便跳过依赖门控。

只读 `PackageManifestRecovery-Run1` 实查本机 UE 5.8.3 的 CookCommandlet/CookOnTheFlyServer 与两级 Config，确认本次没有传 `NoDefaultMaps`，默认对象由引擎独立加入 Cook 根。实际 UFS 恰好有三图：

| 实际 Cook 地图 | 来源与入口约束 |
|---|---|
| `/Game/DengYingShanHai/Dev/FrameBeamPlacement/Maps/LV_FrameBeamPlacementLab` | 唯一显式 CLI Cook 根，也是本启动器唯一提供的可玩入口 |
| `/Game/DengYingShanHai/Dev/Interaction/LV_InteractionLab` | 项目现有 DefaultEngine.ini 的 GameDefaultMap；未改旧 Config，也不提供选择 |
| `/Engine/Maps/Entry` | Engine BaseEngine.ini 继承的 ServerDefaultMap；不是缺失 GameDefaultMap 回退，也不提供选择 |

Recovery 精确验证这个三图集合与 42 条冻结核心依赖，状态 `PASS-EXACT-THREE-MAP-MANIFEST-RECOVERY-ONLY`；不重跑 UAT、不改 Source/Config、不写包内容。核心 42 条是原 41 依赖中的旧主地图换成新地图后再加旧梁 Mesh；两份原生默认地图另列，不能把 Cook 内容称为“仅一图”。本次只提供一个开发样本入口，不等于包中只有一个地图文件。

随后 `PackageContainer-Run1` 真正执行三次只读原生工具：IoStore 列表、主容器全 payload 校验和 global 全 payload 校验，三个实际退出均 0。实际主 2029 个 chunk/global 1 个 chunk 全哈希通过，读入主 299,312,275 B/global 3,224,104 B；42 核心加 2 默认共 44 个指定 ExportBundleData 均绑定实际 ContainerFilename/ChunkId/原生哈希。UFS 与原生容器共同验证，不要求 Zen 输出不存在的松散 `.umap`，脚本未解析 ProjectStore 代替原生工具。

容器结果为 `PASS-BUILD-COOK-STAGE-ARCHIVE-AND-CONTAINERS`，生成固定 `FRAME-BEAM-DEV-BUILD.json` 后封存 50 个归档文件、总 1,070,522,460 B（含身份文件）。来源与容器输入/字节保持、原 Package FAIL 哈希、Recovery 记录分别绑定；没有从以后首帧结果反写历史身份。身份的 FirstFrameVerified、GameplayVerified、PackageAudioVerified、HumanVisualAcceptance、ShippingExecuted 当前均 false，分别对应未在生成时完成的验收，而非空值默认为成功。

### 6.1 新启动器隔离门控与三次真实 CMD DryRun

默认启动器只打开固定新包，显式 `EditorGame` 仅作诊断；无静默编辑器回退、扫描最新目录或自动创建另一个预览构图。Package 校验最终容器结果、包身份、唯一实际归档集合/字节/哈希和原生 EXE；EditorGame 则按冻结 Source/Content/Config/.uproject 精确集合与哈希拒绝实时工程漂移。Docs 新增不会误使诊断入口失效，固定 Package 也不因之后源码改变而偷偷重建。

Windows PowerShell 5 首轮隔离门控暴露 JSON 顶层数组经包装辅助函数读取后成为嵌套数组的兼容问题；保留首轮脚本、fixture 与失败记录，不把它写成游戏 Bug。发布前仅对两处数组读取改为直接 ConvertFrom-Json，未改游戏/C++/资产或降低包/工程门控。

修正后的实际启动器 SHA `D24E5E00050F25FCCD68A5945DE7163ADEABAB473DCCC459B9B83EBF93821A6E`，原生 Windows PowerShell 5.1.26100.9444 解析错误 0。`LauncherPreflight-Isolated-Run2` 从真实 TryStatementAst 提取完整 try/catch，只替换受限 fixture 路径/一个惰性编辑器字节文件，强制 DryRun，29 个案例（4 正例 / 25 负例）全部得到预期结果：正例实际 exit0，负例实际 exit1 且命中对应门控。负例包含容器失败/缺证/空值与字符串伪布尔、chunk 不符、归档多/缺/重复/被改/受限路径、工程基线空/重复/新增/删除/改字节。期间没有 D 盘产品写入、游戏日志目录创建或 UE/游戏启动。

这是隔离的真实谓词兼容/反例测试，fixture 不是实际游戏包验收。随后 `EntryPreflight-Run1` 真正执行发布的 CMD/Windows PowerShell 5 默认 Package、显式 Package、显式 EditorGame 三次 DryRun；三个原生实际退出均 0，状态 `PASS-THREE-PUBLIC-NATIVE-PS5-DRYRUNS`，产品与固定包身份保持，没有启动 UE/游戏或创建游戏 Run 目录。DryRun 输出的 PID/退出为空只表示没有执行，不能把空值冒充游戏成功。

### 6.2 真实包首帧、正常退出和审计变量错误补充

`PackageFirstFrame-Run2` 实际由发布 CMD 启动固定包，原生游戏 PID 37448。官方 Computer Use 针对返回的唯一游戏窗口 3277942 观察中文开始菜单、实际点击“开始复演”、确认含横梁/右柱与幕后灯偶/幕上投影的场景首帧，保存 `Menu.png`、`Started.png`、`VISUAL.json`；以该窗口 Alt+F4 请求正常关闭，不强制结束其他进程。开始的两次点击被人工输入保护阻止，等窗口就绪后才成功，不把未成功点击当成操作完成。

`FrameBeamPlay/Run2/Launch.json`、`Exit.json` 实读新图包路径与及时取得的原生 Handle，游戏实际退出 0；`PackageFirstFrame-Run2/CMD-EXIT.json` 原生 CMD 实际退出也为 0。Session.log 确实 LoadMap 新梁图并出现 Win RequestExit/Exiting；未匹配本轮 Fatal error/Unhandled Exception 信号，不因此宣称全部日志零告警或全部玩法已过。

首帧测试后的审计检查器新增 `[int]Run` 参数，却用本地 `$run` 保存目录；PowerShell 变量大小写不敏感，导致真实游戏已正常结束后的结果收集报 Int32 转换错误。`PackageFirstFrame-Run2/RESULT.json` 原 FAIL 保留，其未验证字段/空 GameExit 不能解释为游戏未运行或产品真的被改。仅修正审计变量名，没有改产品逻辑、重跑游戏或追改原结果。

独立 `Complete-FirstFrameEvidence.ps1` 实读上述可执行/地图/PID/窗口/截图/真实退出及原失败哈希绑定，核验当时 331 产品与 50 个封存归档 SHA 保持，生成 `SUPPLEMENTARY-RESULT.json`：`PASS-PUBLIC-PACKAGE-MENU-START-FIRSTFRAME-NORMAL-EXIT`，FirstFrameVerified=true、GameExit=0、NativeCMDExit=0、IdentityUnchanged=true；原失败 SHA `23D38D5BDE05DAEBE5A4AF7C69FB4B0BE966966A5C53B153F87F07A671277A73` 保留。历史固定包身份的 FirstFrame=false 仍不改，首帧证据只在补充记录为 true。

本次只是实际菜单/开始/首帧/正常退出冒烟；FullGameplayVerified=false、PackageAudioVerified=false、HumanVisualAcceptance=false。没有包内完整两轮/三轮通关、用户耳朵听感或正式艺术签收，不从 PIE 两轮自动推定包内玩法全部相同。

## 7. 保护、回退与尚未关闭的项目

`BEFORE.json` 冻结 327 个产品、926 个旧归档、15 个原来源及 24 个隔离来源，Git HEAD `dda43f2c8970c10680173387b963d1c730649f06`、暂存区为空。两源码已按批准范围发布，新地图创建后 `AFTER-CREATE.json` 有 328 个产品，入口发布后首帧补充核验当时 331 个产品。最终发布合同为 332 个产品、只修改四份既有产品、只新增五份产品；最终集合、字节/hash、旧归档/来源与 Git 只读保护以 `Saved/Audit-2026-10-12-FrameBeamPlacementDev/FINAL.json` 为准，本文不提前生成最终 PASS。

原产品备份在审计 `Before/`；每个阶段验证输入字节和新地图唯一性。只读 Git 状态不是 Git 写入，本轮不提交/暂存/回滚，不清理用户已有改动，不读取/哈希受限登记。旧包/地图/入口继续可用，无需强制替换；对照打开 `Start-FramePostDev.cmd` 即可。

本步即使全部软件检查完成，也只关闭“独立单梁/右柱 Dev 集成与回归”。下列事项仍未完成：完整左右支撑幕框、布质台翼准入、正式建筑尺度/近中远接缝与端面质量、真实梁碰撞/投影/承重、整场空间叙事、作者审美与耳朵听感、物理键鼠和 5–8 分钟首次玩家盲测、GPU 性能、打包三轮通关与 Shipping。没有新增每日排期。

下一最小工作由用户作为唯一负责人、Codex辅助：先补齐近中远接缝/端头与木纹密度的真实比较，再依据实图决定最小构图或有界独立材质修订；不能为凑完整框而自动补左柱、扩环境、改旧灯光/幕布/谜题。正式设计取舍仍遵循事实依据和项目范围。
