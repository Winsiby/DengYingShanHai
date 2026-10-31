# 《灯影山海》枝叶成林美术迭代

2026-10-16。用户是唯一人类作者／负责人；Codex 辅助建模、集成与验证。本记录区分“技术兼容”与“美术通过”，不能把测试绿灯等同成品。

## 当前结论

窄叶候选的技术链路已验证，但美术未通过：在真实分枝的非均匀缩放后，完成画面仍接近针线，未形成清楚的叶簇与林冠。它只保留为独立 Dev 对照，没有替换旧可玩入口或正式包。

第二个宽叶候选也已完成 Blender 导出／回读、UE 冷读与真实成林测试，保持包围盒、木干、叶柄、布局、直径和时序。技术测试通过，但实际完成态仍是细线分叉、空隙过大的林形，不能签认最终林冠。两版均只保留为独立 Dev 对照。

## 1. 本轮范围

保留原生 A 端接触 Z70 地线、同一主灯真实投影和现有成林资源所有者。没有新增 C++、输入、Tick、判定频率、谜题状态、镜头所有者或独立萌叶系统。

新窄叶资源：

- `/Game/DengYingShanHai/Dev/ForestCanopy/Meshes/SM_DY_ForestBranch_Leafed`
- `/Game/DengYingShanHai/Dev/ForestCanopy/Materials/M_DY_ForestLeaf`
- `/Game/DengYingShanHai/Dev/ForestCanopy/Presentation/BP_DYForestCanopy_Leafed`
- `/Game/DengYingShanHai/Dev/ForestCanopy/Maps/LV_ForestCanopyLab`

新宽叶资源：

- `/Game/DengYingShanHai/Dev/ForestCanopyWide/Meshes/SM_DY_ForestBranch_WideLeaf`
- `/Game/DengYingShanHai/Dev/ForestCanopyWide/Presentation/BP_DYForestCanopy_WideLeaf`
- `/Game/DengYingShanHai/Dev/ForestCanopyWide/Maps/LV_ForestCanopyWideLab`（首次保存后进程异常；独立新进程冷验已通过，未重存地图）
- 复用上述叶材质，不复制材质、不改旧木材 MI。

源资产保存在 `Assets/Sources/DengYingArt/ForestCanopy-20261016` 与 `ForestCanopyWide-20261016`。两版独立保留，不覆盖旧 ForestArt 源或游戏启动脚本。

## 2. 几何与表面

两版均为370控制点、704三角：木材320、叶面384；1条 UV0、2个材质分区，9个闭合壳体（木干、4叶柄、4叶面）。壳体通过有意的实体相交连接，不宣称布尔并成单壳。实际三方向封闭体射线检查证明叶柄连接，而非凭截图推测。

实际局部 bounds 均为 `[-34,-28,-50] → [34,28,50]cm`，真实木干根／尖仍在 `(0,0,±50)`。宽叶只把两个原始叶半宽3/2.7cm改为18/16.2cm，镜像得到四叶；位置、朝向、厚度、原木干、叶柄和 UV 定义规则未改。实际不满足原 bounds 就失败，不用自动缩放或重心修正掩盖变化。

叶材质为一次性的直接 Surface / Opaque / DefaultLit / 单面表面：线性 BaseColor约(.08,.18,.045)、Metallic0、Roughness.85，Specular不接线保留默认。没有纹理、透明、发光、WPO、风、静态开关或动态材质实例。木槽0仍由原 BranchMaterial 覆盖；叶槽1由网格默认材质提供，并在真实动态组件上核验。

这是原创程序化风格化植物意象，不宣称桃树物种、历史原貌或特定皮影流派复原。未购买或下载新模型、纹理、动画或生成服务；使用已有免费 Blender4.5.14LTS 与 UE。旧木材资源未改，许可沿用既有来源记录；本轮不读取或哈希受限许可登记。

## 3. 已完成的技术核验：窄叶

| 证据 | 结论 | 边界 |
|---|---|---|
| 本地 SourceNative-Run1 | Blender实际退出0，FBX重新导入及两张实际 Cycles 预览 | 不是 UE 外观验收 |
| ForestCanopyAssetCreate-Run1 | 原生创建exact3；704个源三角／逐角与FBX／UE双分区完整对应，导入变换X,-Y,Z | 未改旧419产品 |
| ForestCanopyAssetVerify-Run1 | 新进程冷读通过，零Save、零重导入／编译 | 原CDO和旧资源不变 |
| ForestCanopyMapVerify-Run1 | 36 Actor冷验，原35个非森林Actor／Stage流程／15枝布局／6盏Spot／PP／LevelBP保持 | 新Dev地图不是正式菜单／重演入口 |
| ForestCanopyCapture-Run3 | 原三幕目标各保持1.25s、15Hz，实际P03 Resolve→接触→15枝原生会话，真实EndPIE，零Save | 用公共操纵值供给目标，不是人工首次游玩或菜单验收 |
| 同轮36组纯几何采样 | 每枝边界、极小、局部1%/10%/50%/100%所对应进度有效，根点／端点／八角包络成立 | 纯函数输出未应用到运行组件，不能认证游戏Token本身 |
| 同轮7张1536²PNG | 主代理逐张实际查看；完成态开／关原主灯、同构图／同几何对照 | 方图SceneCapture，不是最终玩家UI或全部机位 |

实际根点为 `(600,34.7137643377,128.2089552239)`；幕上接触点为 `(925,9.9669401109,70)`。它们不是同一物理位置，前者真实投影到后者。实际Token字符串一致且仍由Director判定current，未由脚本捏造／推进。全部15动态组件保留wood0／leaf1，无碰撞。

开／关主灯对照中，灰度变化大于8的像素为1,007,672 / 2,359,296。这是整盏主灯的画面响应，不是单独提取的森林影子Mask，不能用该数字宣称叶簇质量通过。

## 4. 已发现并修正的测试工具问题

- FBX节点记录包含已建立管线的180°轴转换。初版误要求节点旋转为零；现与旧已冷验 Tapered FBX 的真实节点／全局坐标框架对照，再独立核验所有原生三角转换，不放宽几何门。
- 新地图首次另存成功，但SaveMap没有切换当前编辑器World。首轮创建报告保留失败；随后独立冷读新地图验证通过，未重复保存或覆盖该文件。以后保存后显式加载目标。
- 宽叶地图首次创建实际退出码3：目标地图已保存，随后加载时旧地图的 Python UPackage 引用触发 World Memory Leaks。保留原 Session.log、退出记录及磁盘差异；该轮没有 RESULT.json，不补造。独立冷读工具只在跨地图时保留纯数据契约，实际退出0、36 Actor检查通过、零保存，原有425项产品和新增地图共426项均未变。未来创建工具已将临时脏包列表改为路径字符串，但未重建现有地图，不能宣称该创建修正已通过原生重跑。
- Unreal GUID 包装对象的Python `==` 在实测中为False，即使两者GUID字符串完全相同。测试改为比较真实GUID值字符串，并分别核对物理A点与幕上根点，不更改产品身份规则。
- QA相机恢复产生约1e-18量级四元数舍入差，严格字典相等误拒。现仅对QA构图比较记录1e-7cm位置／1e-10尺度与四元数容差，实际玩家POV不改，玩法／投影容差未动。

窄叶 Capture-Run1/2 的失败记录均保留，不伪称整轮通过。Run3才是完整成功的技术对照。

## 5. 美术审核：没有通过的项

主代理实看完整完成态和幕后斜视后，窄叶仍几乎是针线；比原木干变得更细，叶簇没有形成足够可读的面积。原始窄叶预览不能代表运行时成品。

原因中可实算的一项：现有算法用整个mesh的XY bounds归一到 DiameterWorld，新68×56cm横截面包围盒让同直径木干变为原 Tapered 横宽的约42%。轴向会随实际枝长拉伸，进一步把窄叶拉成长条。

内存2.4倍直径对照 Capture-Run4 仅到P03后触发180s测试截止，未得到可验收的成林图；已真实EndPIE、零保存。没有足够终态观测定位原因，不能把它说成通过，也不能把超时直接归咎于产品几何或渲染。该值未接入任何保存的地图／CDO／正式入口。

本轮随后实际检验了“只加宽叶面且不改bounds”的宽叶源；并未通过调亮曝光、移动主灯、换截图角度或直接放大整片森林来掩盖轮廓问题。其技术通过但美术仍未通过，不能替换正式采用所需的成林外观与完整玩家流程验收。

## 6. 宽叶最终核验

| 证据 | 实际结果 | 边界 |
|---|---|---|
| SourceNative-Run2 | Blender实际退出0；宽叶 FBX重新导入及两张Cycles预览通过 | 源预览不是运行时外观 |
| ForestCanopyWideAssetCreate/Verify-Run1 | 两轮实际退出0；仅新增Mesh和BP两项；冷读零Save | 复用原叶材质；创建前423项不变；新增两项后共425，独立冷读零Save |
| ForestCanopyWideMapCreate-Run1 | 实际退出3，原因与保留记录见上 | 不声称创建轮成功 |
| ForestCanopyWideMapColdRecovery-Run1 | 独立原生进程退出0，36 Actor契约与完整426项冻结检查通过，零Save | 没有覆盖或修补已保存地图 |
| ForestCanopyWideCapture-Run1 | 实际退出0、success=true、actual_pie_ended=true、saved=[]；36组纯几何样本有效 | 只在独立Dev地图供给原目标值，不是人工盲测 |
| 同轮真实流程 | 原P01/P02/P03依次满足；15Hz、保持1.25s；Director真实Resolve后才接触／展开／成林；15个原生动态组件核对新宽叶Mesh与wood0/leaf1 | 未改原生会话所有权、玩家POV、布局、直径或时序 |
| 同轮8张1536²PNG | 主代理逐张实际查看：Resolve前、接触、早／中／上层生长、完成态主灯开／关与斜视 | SceneCapture方图，非最终玩家UI和目标屏幕比例 |

证据目录：`D:\灯影山海\Saved\Audit-2026-10-14-ArtAppearance\ForestCanopyWideCapture-Run1`。主视为 `03_ActualForestComplete_MainOn.png`，斜视为 `05_ActualForestComplete_Oblique.png`。本轮累计逐张查看两版源预览4张、窄叶成功轮7张、宽叶成功轮8张，共19张成功轮图像，未把失败轮排除后伪称其通过。

宽叶完成态开／关主灯，同一几何与构图中灰度变化大于8的像素为1,005,563 / 2,359,296；这是整盏灯的响应，不是森林阴影独立质量指标。完成态15枝Portion均为1，八张PNG验证及真实EndPIE后，全部426项产品保持不变。

视觉结论：宽叶较窄叶有少许更长的尖端面积，但运行时非均匀缩放仍形成细线分叉与较大空隙，未达到清楚叶簇／林冠的目标。保留可复现候选及过程记录，不改旧可玩入口、不接正式包，不宣称最终美术通过。

## 7. 下一步与未完成范围

本轮有边界的双候选建模／对照已收尾，最终林冠仍未完成。剩余美术包括可读成林轮廓、统一剧场空间层次、引导物和仍可见的占位外观。正式菜单／开始—三幕—结束—重演、目标分辨率、声音、性能、Development／Shipping三轮及录屏需在最终集成后重新核验。

按用户最新顺序：本轮收尾后，下一项先建立 GitHub 私有仓库并上传当前工程快照，不再等全部剩余美术完成。备份时保留源工程、原创源资产与本轮未通过美术验收的真实状态；排除可再生成缓存、大体积打包目录、测试日志和受限文件。仓库的创建／上传结果另行核验记录。本记录发布时尚未创建远程仓库、提交或推送；不能把备份、新增Dev候选或审计通过当作整个项目完成。

Blueprint架构技能让新资产只配数据并复用现有会话所有权；Materials技能限定为有限不透明表面，避免透明／风／通用材质框架。两材质分区会增加渲染分区成本，本轮没有声称实测GPU或最终帧率。
