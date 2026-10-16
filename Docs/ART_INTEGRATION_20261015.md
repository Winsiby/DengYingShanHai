# 《灯影山海》美术接入进展：皮影、灯具与厚台翼

日期：2026-10-15。唯一人类作者仍为用户本人，Codex 提供建模、接入和验证辅助。本记录不是作品完成声明，不增加制作成员或场景。

## 本轮实际完成

原 386 个产品文件保持不变。累计新增 22 个 Dev 资产后为 408 个产品文件；本记录发布后为 409。本次分别先备份，再仅修订刚新增的 Refined mesh 和台翼 mesh。没有修改正式 `L_DY_Main`、旧 Dev 地图、C++、Config、旧启动器或比赛包，也没有删除原文件、Git 暂存/提交或修改系统权限。

| 内容 | 原生资产 | 当前证据与边界 |
|---|---|---|
| 灯具 | `Dev/HeroLampArt`：2 网格、6 张 2K 贴图、2 个有限父材质、3 个实例 | 创建、独立冷加载、实际 render-buffer FBX 逐面/UV/TBN 比较通过；8 张安全 UE 截图与曝光/主灯 A/B。正式戏台光照、交互碰撞与打包未验收 |
| 皮影表现 | `Dev/KuafuAppearance/Presentation/BP_DYKuafuPuppet` | 只消费既有控制事件，3 姿态真实 PIE 与生命周期测试通过；原始不适配的装配仍保留，不作为最终放置 |
| 新派生皮影 | `Dev/KuafuAppearance/Puppet/SK_DY_Kuafu_Refined` | 耳蛇数值微面修复后原路径重导入；17,886 面冷导出逐面对应，0 几何/UV 退化，20 骨/6 材质保留；旧资产已备份 |
| 实测装配 | `Dev/KuafuAppearance/Presentation/BP_DYKuafuPuppet_Fitted` | 事件、实际三姿态与握点标记数值通过；九张真实 PIE 图已逐图查看，独立几何确认左手接触成立但被杖遮住；抓握视觉可读性仍未通过 |
| 厚台翼 | `Dev/StageWingArt`：1 网格、3 张 2K 图、1 Cloth 父材质和 1 实例 | 创建/冷读/编译通过；修复后实际 23,072 面/双 UV/逐角 TBN 对应，六张最终网格原生图已查看；正式舞台比例/质感/GPU 仍未验收 |

## 皮影表现架构与实际测试

`DYPuppetActor` 继续拥有交互代理和独立 Staff 几何。新 BP 只增加 `KuafuMesh`，BeginPlay 绑定一次 `PuppetControl.OnControlChanged(double, FName)` 并读取当前状态初始化，EndPlay 仅移除自身 handler。没有 Tick 扫描、核心判定副本、新输入或新管理器。

每次实际 PoseId 改变时走 `SetAnimation → OverrideAnimationData(false,false,0,0)`，随后更新表现缓存。已证明只调用 Override 在 SingleNode 模式不会替换 CurrentAsset，故保留这个必要刷新链。三动作仍是既有源序列，未重写骨骼/动画。

真实 PIE 使用动态生成在 `UEDPIE` 世界的 child 与 native parent 对照，操作 `.15/.5/.6/.9/.5/.15`。实际 SingleNode 资产与组件空间骨姿态均正确，三姿态互异，预期的五次变化广播正确；六步中 child/native 的 Staff A/B 与 bounds 相同。销毁前原生及表现 handler 均存在；真正 DestroyActor 后 guard 清除，独立仍存活的 observer 未被清掉。销毁对象的弱引用 `Contains` 返回 false，不再错误地把它当“某条订阅被清空”的证据；individual Remove 由独立冷图审查证明。

当前 Dev 视觉装配：统一缩放 .8、Yaw 180°，平移来自真实 PIE 握点与三条既有 Staff 轴的最小二乘拟合，而不是目测挪杖。新装配真实运行后，左 StaffGrip 到杖轴距离 Back/Mid/Reach 为约 .302/.567/.302 cm，落在 3 cm 杖半径内。右手不强行贴同一根杖。原 Staff 的位置、旋转、缩放、SceneRoot 挂接及 A/B 规则没有变，只在新装配中换成已验证同边界的独立木杖网格与木材实例。

证据：`Saved/Audit-2026-10-14-ArtAppearance/PuppetVerify-Run3`、`PuppetPIE-Run2`、`RefinedCreate-Run1`、`RefinedVerify-Run1`、`PuppetPIEFitted-Run1`。冷图、CDO、源渲染、真实 PIE 与完整游戏流程是不同验收范围。

## 派生源几何与反证

新源目录：`D:\灯影山海\Assets\Sources\DengYingArt\KuafuRefined-20261015`。保留可编辑 blend、FBX、作者脚本、逐部件/逐骨证据与 QA-Run3 的 12 张原/新源对照。新源 10,636 顶点、17,902 三角形，20 骨、六材质、一套 UV；原 50 个非印纹/非蛇主片的几何/UV/法线不变，三动作全部 20 骨在 1/16/31 帧的矩阵不变。

实际修复四条黄蛇的闭合体，并使蛇眼/印纹贴到对应皮面。重要反证：原 212 组印纹在 YZ 平面内，最初逐面裁剪仅移除约 2.45e-11 cm² 数值噪声；最终保留原印纹三角形，没有把“裁掉越界纹样”当已证根因。旧/新源三姿态完整真实射线影子均未复现 UE 零散影点，故仍需 native 同灯、同材质 A/B；不能宣称源几何修订已彻底消除碎影，也不靠透明/Mask 或禁用整条蛇的投影掩盖。

原五个源/证据/作者文件哈希不变。文化依据沿用原公版夸父古图与《山海经》文本；皮色、衣色和媒介厚化均是当代创意改编，不宣称历史原色、古物或流派复原。

独立 native 已构建 LOD 冷导出复核曾发现：源 17,902 面导入后为 17,892 面，丢失的十面全在耳蛇微小并集残片；导出还含两个零面积 UV 面。未放宽阈值。续进仅在两条耳蛇中合并 8 个近重复点，移除 16 个索引退化面；实际最大位移 0.307551 微米，低于 1 微米边界，其余 264 分件的几何、UV、原始压缩法线和硬边逐值不变，原 20 骨/三动作完整曲线及 1/16/31 帧矩阵不变。

有效源 `D:\灯影山海\Assets\Sources\DengYingArt\KuafuClean-20261015` 为 10,628 顶点、17,886 面、20 骨、6 材质、1 UV。原 Refined 源继续保留。先备份既有新增 mesh，再仅重导入这个 mesh：`PuppetCleanRepair-Run1` 实际退出 0，其余 401 产品文件哈希与 402 文件集合不变；`PuppetCleanVerify-Run1` 冷加载/实际导出退出 0，402 产品全不变。回退原件在 `Saved/Audit-2026-10-14-ArtAppearance/PuppetCleanRepair-Run1/Before-SK_DY_Kuafu_Refined.uasset`，本轮未自动回退或删除文件。

独立 Blender 读取新 native FBX 后，源/native/唯一匹配均恰好 17,886 面，0 缺面、额外面、反绕序或匹配歧义；原始和冷导入均 0 几何/UV 退化。最大位置分量误差 4.00543213e-5 cm、UV 误差 5.70435077e-8；逐角单骨权重 1、20 骨层级和六材质逐面归属一致。该报告位于本地 `ArtIntegration-20261014/PuppetClean/Native-Run1/PUPPET_CLEAN_NATIVE_AUDIT.json`。骨骼 exporter 读取 constructed Imported LOD，不冒称 GPU 最终绘制缓冲。

发布源根目录可直接打开 blend/FBX；其中作者/冷读脚本是过程证据副本，原冷读脚本按工作区 `Clean-Run2/` 布局运行，不宣称扁平发布副本可直接执行。独立 native 审计和实际原生运行的完整命令、stdout、ExitCode 与输入哈希均保留，不以不完整的发布脚本复现替代上述实测。

## 灯具材质、UV 与代价

采用两个有限材质族，而非万能材质：普通铜/木/黑金属/反射罩为 Surface / Opaque / DefaultLit；独立光学窗为 Surface / Translucent / ThinTranslucent / Surface ForwardShading。Windows UE5.8 标准材质路径，未启用 Substrate、WPO、RVT、Material Layers、全局 MPC 或动态 MI。

普通表面按 `UV1 → BaseColor / ORM / NormalDX → PBR` 求值：BaseColor 为 sRGB；ORM 为线性 R=AO(白)/G=粗糙度/B=金属度；NormalDX 为线性 Normal compression、Normal sampler、不翻绿、强度 1。源木色 tint 与木/铜法线强度已烘焙，不重复乘色或削法线。材质纹理采样固定 UV1，原 UV0 保留。导入 Normals and Tangents，关闭重算法线/切线及自动 lightmap UV；灯具实际 TBN 为 UV1，不允许后续悄悄按 UV0 重算。

冷导出的灯具实际 render buffers 保持 Body 20,016 / Stand 13,088 三角形，位置最大误差小于 .00001 cm，两 UV 误差小于 6e-8；N/T/B 方向最大误差小于 .397°。另冷读 blend 重算证实主 TBN 来自 BakeUV1，UV0/UV1 切线中位差约 90°，不是仅检查导入选项。主灯具共 33,104 三角形，分区仍为灯身六槽/支架五槽；共享实例不会自动把分区合成一个 draw call。

光学窗不使用 `Opacity=1-Transmission` 的简单假等价。当前 UE 薄片候选保留原发光色 (.8,.37,.10)、强度 .15，以源 IOR1.46 推出正入射 F0，以 atlas tint × .38 控制透射；这是跨渲染器的 Dev 视觉适配，不宣称与 Blender 混合 BSDF 能量等价。发光只是表面外观，不替代现有 Movable SpotLight。[Epic 的 ThinTranslucent 设置说明](https://dev.epicgames.com/documentation/unreal-engine/lit-translucency-in-unreal-engine)支持该独立透射路径。

有意保留的美术参数：TransmittanceScale ∈[0,1]，增大使窗后颜色更透；EmissionStrength ≥0，增大只增强窗面自发光。现值来自源，不作为新的玩法参数。两个父材质不加静态开关，避免无意义排列；透射仍有过绘成本，六张 2K 三通道 atlas 未压缩像素约 72 MiB，实际压缩显存与整场景 GPU 开销待目标游戏测量。

## UE 截图复核与安全导出

最初测试截图铜木过亮，不通过美术验收；进一步证明旧捕捉器请求 -6/-8/-10 时，三图实际解码像素相同，不能凭不同文件哈希声称曝光生效。已安装 UE 的旧 PNG helper 用分配容量而不是有效字节数导出，IEND 之后含多余内存尾部；这些原始审计 PNG 不对外作为交付图，不将尾部字节当有效画面或新内容。

新捕捉脚本显式设置固定 Manual 非物理曝光、PP weight=1、持久渲染状态及 EyeAdaptation/PostProcessing/Tonemapper，逐镜头读回实际属性；输出改为 `ImageWriteBlueprintLibrary.export_to_disk` 同步 PNG，并逐块 CRC / IEND 严格验证零尾部。未修改引擎、系统、全局环境或产品材质以绕过问题。

最终安全图片在 `D:\灯影山海\Saved\Audit-2026-10-14-ArtAppearance\LampCapture-Run5`。八张 PNG 已实际打开检查；-4/-2/0 三档灯头平均 RGB 分别约 4.74/10.59/14.98，实际像素随曝光变化。-4 档能读出铜面低频色差、黑金属、内反射罩与局部木色；0 档过亮，不选作美术展示。主灯开/关超过 8 灰阶的变化面积约 54.57%，证实主灯仍真实出光。中性黑背景与临时补光仅作模型检查，不是最终戏台照明。

此处姿态/材质/渲染验收不代替玩法主镜头、目标提示对齐、阴影稳定性、P03 连续落杖成林、目标硬件 FPS 或新 Development/Shipping 包的终验。

## 修复后夸父的真实 PIE 图

`FittedCapture-Run1` 在实际光组件方向门处失败，未产出图。原因查到 UE 的 `ASpotLight` 构造会令根光组件 Pitch=-90；项目自建 SceneRoot/KeyLight 没有这个默认值。仅将临时 PIE QA 光组件设置世界方向，并逐镜头读 `get_forward_vector()==(1,0,0)`，没有修改产品灯。`FittedCapture-Run2` 完成六图，但 -2 外观严重过曝，视觉不通过。

`FittedCapture-Run3` 在真实 BeginPlay 后，通过既有 `set_normalized_value(.15/.5/.9)` 驱动，不直接调用动画切换；确认实际 CurrentAsset、组件空间三姿态、有限杖段握点、Staff A/B 对照和原生/表现订阅。采集前先固定 Mid/灯/构图，比较 -6/-8/-10 的实际解码均值 155.4656/59.1103/2.8553；数值算法选 -6 后同档完成三姿态外观/真实阴影六图。九图均同步 ImageWrite、CRC 正确、IEND 后零尾部，原 402 产品不变，临时 PIE 已结束，无产品包/地图保存。

主执行者已逐图查看全部九图。-6 可看清刻线和手杖，-8 保留较深的红/褐色，-10 过暗；这只是中性测试曝光，不修改正式游戏。固定主灯下三姿态全身/杖完整入画，投影轮廓可读，本样本未见离散耳蛇碎影，不能外推到全灯位稳定性。

**几何接触成立，抓握视觉可读性未验收。** 初看木杖位于腹前，不能仅由骨标记近轴推断手面接触。独立按实际三姿态源 Hand 皮片、native 五骨与有限杖段核对后，左手皮片到轴最近距离均约 .3400 cm，小于真实杖半径 3 cm；StaffGrip_L 本身也在该皮片上，不是 marker 放错或皮手悬空。右手离杖约 60–67 cm，并非双手握杖方案。

射线实测三姿态的左手接触区，第一交点都是独立木杖，手面比杆首交点深约 2.58–2.67 cm；按面片中心投影面积求积估计，杆遮左手约 48.0%/55.7%/58.8%（近似数，不冒充逐像素遮盖）。有限结论是接触成立但源手形为平片、缺少前后交握线索；不能将其等同于自然抓握或凭肉眼怀疑擅改骨/动画。证据在本地 `ArtIntegration-20261014/PuppetBP/HandAudit-Run7`，输入前后哈希相同，source→native 用实际五骨确定的 `(X,-Y,Z)` 最大骨误差 .00005424 cm。本轮未引入 IK/新骨/新输入，也没有为迎合手形移动真实 Staff A/B。正式幕前/幕后机位、可玩提示和落杖连续性仍须后续整场景验证。

## 厚台翼已进入 UE，但不越过准入问题

`CurtainCreate-Run2` 新建恰好六资产，实际退出 0，原 402 产品不变；`CurtainVerify-Run1` 独立冷读退出 0，408 产品不变、保存数 0。网格 23,072 三角形、14,015 native split vertices、BakeUV0/SourceUV1 两 UV、两个原材质槽，无自动碰撞和 Nanite。原顶部枢轴/厘米尺度保留，不把台翼当主投影幕。

材质为单一 Surface/Opaque/Cloth，闭合厚几何、单面、切线法线。UV0 直接采样 sRGB BaseColor、线性 Roughness R 和 NormalDX/Normal compression、不翻绿、不重复叠加 tint 或 Bump 强度。只用一个 MakeMaterialAttributes 聚合节点连接现有输入；ClothAmount=.12 走其公开 ClearCoat 通道（该属性在 Cloth 中即 CustomData0），白 Fuzz 走 SubsurfaceColor。真实 transient API 探针已证明图边、参数值 .1199999973 和 shader 零错误；没有用隐藏枚举整数强转、DefaultLit 兜底、Layers、Substrate、WPO、透明、动态布或新增全局参数框架。

源 Sheen Roughness=.85 仍保留，但 UE Legacy Cloth 共用底层 Roughness，不能宣称跨渲染器完整 BSDF 等价。ClothAmount ∈[0,1] 增大纤维 lobe 占比；FuzzColor 为线性 RGB。三张 2K 的实际压缩显存与整场景 GPU 开销未测。原 source FBX 没有 T/B 层，因此首次 native 采用 Mikk UV0 重算。

首次独立实际 StaticMesh render-buffer FBX 检查保留了 23,072 面和双 UV，但 35 个 native 角的 T/B 偏差超过 1°，最大约 8.089°，当时未通过 TBN 门，未放宽门槛。进一步只读因果对照证明：9170 个实际 native 三角剖分不同于原 blend 的 loop_triangles；仅把原位置/UV/N 按 native 拓扑在内存重组再作 Mikk，全部 native 角 T<.383°、B<.440°。问题不是材质参数或候选角点误认，而是不同三角化及 Mikk 输入语义；不能因此把不匹配原烘焙的基底判成合格。

最终从原 quad 烘焙基底独立导出 TBN，再仅用 Blender 自带 FBX parse/encode，按原 `loop_triangles` 展开位置索引/角属性，完全不第二次重算 Mikk。新源在 `D:\灯影山海\Assets\Sources\DengYingArt\CurtainFrozenTBN-20261015`，FBX SHA256 `72F3EFB9CED5E0CABCAFA8D80D711C7FE71B26D6D20DE32834EEA55591B9C0CD`。所有源位置、逐角 N/T/B、双 UV 和原两槽归属均保留原值，面/绕序明确等于原烘焙拓扑；原十源/纹理保持不变。

`CurtainRepair-Run1` 备份后只保存原路径新台翼 mesh，实际退出 0，其余 407 产品不变、文件集合仍 408；`CurtainFrozenVerify-Run1` 独立冷启动/实际 render-buffer FBX 导出退出 0，408 产品全不变。Native 按 ImportNormalsAndTangents，recompute N/T 均 False、Full Precision UV=True，不再让 UE 重算已烘焙基底。

独立实际 render FBX 逐面复核得到 23,072 面唯一对应、0 缺面/多面/反面/身份歧义；逐角 N/T/B 最大约 .371627°/.369926°/.442551°，旧 35 个异常已消除，原 <1°/.001cm/2e-6 UV 门未放宽。BakeUV0 始终 0 退化。未使用 SourceUV1 的精确零面积数原源 1458、native 1564：它的全部角值都由已证实的 UE float32 V 双翻转流水线逐值精确预测，新增 106 个归零面完全匹配量化结果，无新 UV 改动；原值→native 最大分量误差两 UV 均 2.98023224e-8。错误地要求浮点前后零面积集合恒等的额外审计门已纠正，不为此修改原 UV 或纹理。

最终检查执行独立冻结 runner 与两个依赖，执行前后代码哈希相同，实际 Blender 退出 0；正常/切线用正确 row-vector 全局传递公式，不在两个 mesh 之间拟合形变。最终报告 `FROZEN_NATIVE_TBN_AUDIT.json`、退出记录、数值流水线证明与冻结脚本在本次 `IntegrationPublication-Run1` 审计目录一并留存。早期并发改审计脚本、过严 Gram/UV 集合门的失败证据不覆盖为通过。

修复前 `CurtainCapture-Run1`、修复后 `CurtainCapture-Run2` 均实际退出 0，408 产品不变。每组六张 1536² 图是独立 Editor RAM fixture，不是 PIE/正式游戏截图：全帘、实际底折边约 23.1 cm 掠射近景和背面，各 -4/-6 两档。Spot/Capture 实际 forward、物理光单位/距离、固定局部曝光均读回，45 捕获帧后同步 ImageWrite；PNG CRC/IEND 零尾部与像素响应通过。主执行者已逐图查看两组全部十二图：-4 可读深红波折、边缘和厚度，-6 过暗不作展示；不能据此签认完整舞台的近景织物质感、比例或最终照明。最终网格原始图片在 `D:\灯影山海\Saved\Audit-2026-10-14-ArtAppearance\CurtainCapture-Run2`。

## 接下来继续的实际顺序

1. 将灯具、皮影、厚台翼与主幕及当前柱梁组合到独立 Dev 样本，优先交付整体舞台画面，保持现有 E/A/D/R、15 Hz、谜题区间与真实 Staff 因果链。
2. 在实际操纵机位检查手指轮廓/抓握可读性、布料与场景比例；必要时只对已有手片局部轮廓作最小美术修订，不先新建 IK、骨或动画体系。再处理成林几何与同一戏台环境层次。
3. 美术/碰撞/提示/三幕连续性通过后再更新正式地图引用、Development/Shipping 和通关录屏，不把 Dev 模型图当新游戏成品。

本轮使用 ponytail 使接入只复用既有控制组件、事件、骨架、动作与材质实例；UE 材质与 Blueprint 技能帮助明确普通/透射族、一次绑定与生命周期边界。没有为未来功能提前搭大型框架。
