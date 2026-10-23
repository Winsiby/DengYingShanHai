# 横梁顶面 UV 校准：独立对照资产

2026-10-13 · 唯一人类作者：用户本人；Codex 辅助实施与验证。

> 独立资产阶段已完成：源派生、新网格导入、独立冷验和十二张原生对照图均有实际结果；原梁、B 地图与旧游戏包保留。通过的是数据、原生接口和摄影合同，不是正式美术采用、实际通关或打包验收。

本步只处理上一轮发现的**梁顶木纹长向拉伸**。原梁、B 地图和共享木材材质保留；生成一个独立 Dev 网格，供同位置、同材质的原梁／TopUV 对照。**这里的候选是 UV 校准，不是再次改变 B 的横梁位置。**

快速入口：图册为 `D:\灯影山海\Docs\FRAME_BEAM_TOP_UV.html`。独立 UE 网格为 `D:\灯影山海\Content\DengYingShanHai\Dev\FrameBeamTopUV\Meshes\SM_DY_FrameBeam_TopUV.uasset`。现有可玩版本仍从 `D:\灯影山海\Start-FrameBeamCandidate.cmd` 启动；本轮没有新游戏包或新地图，打开旧游戏不会自动看到新 UV。

## 1. 实际改了什么

| 项目 | 原梁 | TopUV 候选 |
|---|---|---|
| 源 polygon 0 顶面长向 UV | 约 140.114444 texel/m | 约 198.151686 texel/m |
| 顶面横向 UV traversal | 约 198.151686 texel/m | 不变 |
| 顶面 V 倍率 | 1 | `1.4142131281943933` |
| 锚点 | chart 的 `minV = 0.030432701110839844` | 固定此锚；新 maxV 约 `0.999912420356238` |
| 变更数据 | 原 UV 数组 | 只改两个 V doubles：数组 47、51，即 direct UV 对 23、25 的 V |
| 其他九面、全部 U、UVIndex | 原数据 | 逐角／逐 double 不变 |
| 源拓扑 | 16 顶点、10 面、48 角、28 fan 三角形、38 UV 对 | 不变 |
| 几何、法线、轴、单位、Model、材质定义、Header/Footer | 原数据 | 非 UV 属性原字节不变 |

这些密度是 **2K 纹理、当前等比灰盒尺度下的离线 UV traversal**，不是实际木纹尺寸、运行 mip、GPU 成本或正式统一密度标准。目标取自当前梁顶自身保留的横向度量，与梁侧约 198.15 的局部度量相近；未把柱身当作正确纹理标准。

实际共享关系决定了锚点：顶面 minV 的两个角通过 UV indices 33、35 与其他面共享，而 maxV 的 indices 23、25 仅顶面使用。固定 minV 只需要改变两个非共享角，不追加 UV 对、不改 UVIndex，并使新 chart 仍在 `[0,1]`。这是最小数据改动候选，不是纹理相位正式定稿。

## 2. 同条件看图，而不是只看参数

[打开六组原梁／TopUV 图册](FRAME_BEAM_TOP_UV.html)。Render-Run1 实际取得十二张 1920 × 1080 原生 PNG：近景 3.516513 m、中景 9 m、远景 22 m，分别提供 Lit 与 Unlit，每组原梁／TopUV 两张。原图不提亮、不裁切、不改色，图册使用磁盘原图的绝对 file 链接；点击可打开原图。

| 观察方式 | 应看什么 | 不能据此宣称什么 |
|---|---|---|
| Unlit 近／中／远 | 去掉主要光照响应后，比较顶面 UV／BaseColor 的拉伸比例和木纹可读性 | 不是最终灯光、美术、法线贴图或游戏画面验收 |
| Lit 近／中／远 | 同一木材、B 位姿和观察方向下的实际表面观感 | 不认证实际 EV 完全锁定；不把不同时间截图的像素差异全部归因为 UV |
| 冷合同与原生 UV 数据 | 检查只有预期顶角 UV 变化，其他场景事实与导入设置保留 | 不等同于无暗接缝、无穿模、正确建筑榫卯或承重 |

摄影使用诊断 Editor 视口，不进入 PIE。每对保持相同目标、方向、距离和实读水平 FOV 90°；只在内存中替换同一个被动梁 Actor 的网格引用，之后恢复原网格及视口。Render-Run1 实际退出 0，35 Actor 全冷合同通过，零位姿／游戏镜头／灯／材质／曝光属性写入、零资产保存，原网格与原视口完全恢复。高分辨率摄影使用 forced loading、ScreenPercentage off，不能据此认证实际运行 mip／GPU。

聊天 high 预览一度把 TopUV Unlit 背景误呈为黑色，但不能据此认定 UE 摄影失败：磁盘核对显示 Run1 的三张 TopUV Unlit 与独立 Render-Run2-TopUV 的对应三图 **byte-identical**；近景原梁／TopUV 的 `y = 800..1080` 背景区域像素差为 0。original-detail 展示正常。两个独立 process 的 Render-Run2-Original／TopUV 各六图也实际退出 0，合同、零保存及完整恢复均通过。本轮没有“UE 缓存修复”、重新合成原图或处理游戏画面的操作；不把预览误呈现写成产品故障或已修复的渲染缺陷。

Codex 已按 original-detail 查看全部十二张原图：近景顶面木纹更密，局部拉伸度量已校准；侧面和背景保持，整体轮廓不变。在中远景和当前暗光下差别有限，因此不将本轮称为全面消除“廉价感”。独立只读 PNG 检查实际退出 0、115 项通过，Original 与 TopUV 两组各三张 Unlit 均与各自独立复拍字节一致；这些检查不是美术采用或游戏测试。

## 3. 材质、UV 与 TBN 边界

选择的架构仍是现有木材 Parent + Material Instance：`M_DY_FramePost_Master` → `MI_DY_FramePost_Wood`。本步不新建 Master、材质函数、全局参数、纹理或统一平铺倍率；全局倍率会连带改变其他面和柱，不能修复只发生在梁顶的长横向比例差。

原生 probe-Run3 实际退出 0，实读既有材质为 Surface / Opaque / DefaultLit / SingleSided / Tangent Space Normal，`r.Substrate = 0`，`UVQuarterTurn = 1`。图结构和参数没有修改。现有路径仍为 UV0 经既有转向映射后采样 BaseColor、NormalDX 与 ARM，再送入既有表面输入；没有新的 shader 静态分支。

| 现有纹理 | 原生实读尺寸 | 色彩／压缩／采样要求 |
|---|---|---|
| BaseColor | 2048 × 2048 | sRGB，Default，Color sampler |
| NormalDX | 2048 × 2048 | 非 sRGB，NormalMap，Normal sampler |
| ARM | 2048 × 2048 | 非 sRGB，Masks，Masks sampler |

三者沿用实际 Wrap addressing 和既有 sampler。探针中 BaseColor 在完成异步资产编译前曾返回 32 × 32，完成后为 2048 × 2048；NormalDX、ARM 前后均为 2048 × 2048。这是已记录的原生编译观察，**不是把原纹理升采样、修改纹理属性，或证明运行时常驻全 2K mip**。

原网格实读 48 个 render vertices、28 三角形、1 UV channel；MeshDescription 为 84 个 vertex instances，是导入后 28 三角形的角实例，不能当成新增面。实际源到 UE 的数据匹配得到位置轴序 `(sourceX, sourceZ, sourceY)`、三个正号，以及 `nativeV = 1 - sourceV`；不是凭名称猜测导入轴。

源法线保持原字节并不能单独证明导入 TBN 正确；因此另做了实际 create 与独立冷 verify。原／新 bounds、拓扑、材质槽、导入／Build／collision flags 的精确比较通过；全部 native normals 和非顶面 UV／tangent 不变；顶面 tangent 方向满足实际基精度量化界、handedness 不变。仅两个原生 render V 按实测 V flip、float／half 精度变化，并对应三个三角形 MeshDescription 角实例；角实例的重复是三角化结果，不是第三个源 UV 角被修改。这证明预期导入数据与切线方向合同，不认证 NormalDX 最终视觉、暗接缝或纯像素因果。

## 4. 平台、成本和镜头所有权

本轮目标仍是 Windows、UE 5.8.x 当前工程原生 Editor／D3D12 诊断。不改变视觉阴影与 15 Hz 参数判定的分离，不改 E/A/D/R、谜题、声音、游戏镜头、演出时序或三幕状态。

只增加一个 Dev 网格磁盘资产，复用三张现有纹理和现有材质。不增加透明 overdraw、WPO、RVT、Material Layer 或新的 shader permutation；未测 GPU 时间、峰值内存、streaming、运行 mip 或正式纹理预算，不能写“性能已优化”。

诊断相机只属于 Editor 视口，目标是比较梁顶，较近距离更便于观察木纹，远距离检查整体可读性。它不接管玩家 POV，不 pilot 世界中的相机，不创建 Camera Actor／Sequencer Cuts／过渡／shake／lag。视口按“目标与方向 → Editor camera → 诊断 view mode → 截图”工作；本轮正常结束后原网格与原视口完全恢复。异常分支分别尝试恢复并记录错误，截图任务仍 pending 时不认证最终视口恢复；不能把正常通过推广为所有错误时必然恢复。玩家原有 PlayerController／PlayerCameraManager 链保持不变。此步不新增剧情相机或宣布新的无障碍／多帧率验收。

## 5. 当前证据与限制

- 源派生已完成：新 FBX SHA256 `9D67085097B6EA5D18E098BFD5002D74148943F681182E2C17598EDC7835F999`，15,211 B。
- 独立离线 Run2 已完成：实际退出 0，256 全树节点、8,568 项数据断言；不是 8,568 项 UE 游戏测试。
- 离线 native comparator Run2：10 个实际 case 通过；它测试比较器，不是 UE 游戏行为。
- 原生只读 probe-Run3：实际退出 0、5,766 项检查、零资产保存。
- 原生 create-Run1：实际退出 0、6,284 项检查，只保存一个新的独立 Dev 网格。
- 独立冷 verify-Run1：实际退出 0、6,280 项检查，零保存；冷读磁盘候选与原网格的数据合同通过。
- Render-Run1：实际退出 0、十二张原图，35 Actor 合同、零保存、原网格及原视口完全恢复。
- Render-Run2-Original／TopUV：两个独立原生 process 各实际退出 0、各六张原图，合同、零保存、恢复通过；图册仍使用 Run1 原图。
- 上述离线断言、比较器 case、原生资产检查和摄影合同均不计为新的 UE 游戏自动化测试，不代替体验或正式美术评价。
- 没有新 Cook、打包、实际通关、Shipping、clean-machine、GPU 或人工美术通过记录。现有旧入口及封存包不升级为新 UV 版本。

保留工具失败证据：离线 Run1 的 mapping hash 失败源于 Windows CRLF 文件与 LF 内存文本 hash 的混用；Run2 和 `MAPPING-METADATA-CLARIFICATION.json` 分别验证两种 hash，原 manifest、mapping、FBX 和 FAIL 不覆盖。这是证据元数据修正，不是模型修复或测试降级。

资产来源仍复用此前封存的 CC0 仿古四角亭额枋源与已登记的免费 DarkWood 纹理。此轮没有新增资产获取、付费服务或新许可登记；不读取或哈希受限许可登记册。文化表达仍服务“灯为日、影为夸父、玩家杖落成林”，不宣称历史榫卯、建筑尺度、特定影戏流派或承重复原。

## 6. 最小后续与回退

先根据实际同条件十二图说明顶面拉伸是否改善、顶／侧纹理是否更协调；若仍有接界问题，按“BaseColor／UV → NormalDX／TBN”的独立分支诊断，不自动扩大到柱、斜端、左支撑、台翼、正式比例或世界灯光。B 构图和本 UV 候选均未正式采用。

回退是保留／恢复原梁网格引用；本步不保存旧 B 地图、不覆盖原 FBX 或原 UE 网格，因此旧可玩流程无需修改。单独 Dev 候选继续保留，不删除失败证据、不 commit、不清理用户已有更改。

完整证据根目录：`D:\灯影山海\Saved\Audit-2026-10-13-FrameBeamTopUV`。

`Scripts\Create-FrameBeamTopUVAsset.py` 是本次冻结批次的原生实施记录，不是供玩家双击的启动器。它按 `BEFORE.json` 精确保护输入，并拒绝覆盖已存在的新资产；文档发布后直接重跑也会因冻结基线改变而拒绝。后续再验证应建立新的明确审计基线，不跳过保护或复用旧结果冒充新验证。无需用户手工重新导入模型。
