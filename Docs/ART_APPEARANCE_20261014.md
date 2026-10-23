# 《灯影山海》皮影实景与灯具 PBR 美术进展

2026-10-14。唯一人类作者：用户本人；Codex 为建模、资产适配与技术验证辅助。本次仍属于剩余建模美术，不增加玩法、场景数量或制作成员。

## 当前结论

夸父皮影的六种材质已在 UE 实际保存、冷读取验证；三种姿态与真实 Movable 光源的幕面阴影已实际捕获。灯具完成可编辑源、低面数运行时变体，以及可导入的六张 2K PBR atlas 与两件 FBX。它们不是参赛成品：正式地图的灰盒偶/灯尚未替换，本轮未生成新 Development/Shipping 包，也未进行新版三幕人工通关或性能验收。

## 玩家可见美术与依据

皮影沿用已核实的古图夸父形象及原有头发、耳蛇、手蛇、奔行与赤足特征；颜料、皮革与漆色是本项目创意配色，不宣称古图原始颜色或文物复原。真实 UE 图中可辨古图印线、漆红衣装、赭色皮革、黄蛇与关节。印线是表面表现，不应额外产生大量离体投影碎点。

灯具是服务“以灯为日”的当代舞台投影灯创意改编，不是凭空认定的先秦灯具：旧铜空心灯罩、反射罩、转轴、木柱和稳定底座。造型和尺寸依据现有 KeyLight 的 +X 出光、光源 X45 cm、Actor world Z310 cm 与地板顶面 Z0。实体最前 X42，保留 3 cm 前向净空。

全部为许可清晰的免费原料或本地程序制作：皮革为已归档的 ambientCG Leather037 / CC0；木纹为已归档的 Poly Haven Wood Table / Dimitrios Savva / CC0；古图依据、原始素材和许可快照保留在既有来源档案中。没有付费模型、生成服务或插件；没有改写外部原始图片。本轮未访问现有 LICENSES.md。

## 真实 UE 验证

资产范围：`/Game/DengYingShanHai/Dev/KuafuAppearance/`。一个有边界的 Surface / Opaque / DefaultLit 父材质、六个实例、三个 2K 纹理与 Painted Mesh 共 11 项已保存。原 Skeletal Mesh、Skeleton 和三动画只读复用；未引入材质层、RVT、WPO、动态材质或新判定系统。

冷验记录：`D:\灯影山海\Saved\Audit-2026-10-14-ArtAppearance\Materials-verify-Run2\RESULT.json`。BaseColor=sRGB/TC_DEFAULT；NormalDX=linear/TC_NORMALMAP/不翻绿；Roughness=linear/TC_MASKS。冷加载初值 32×32 是异步占位，等待加载资产编译后真实 2048×2048；未因此重写纹理。

捕获图和原生证据：`D:\灯影山海\Saved\Audit-2026-10-14-ArtAppearance\Capture-Diagnostic-Run1\Captures\`。三姿态彩色图、三组 CastShadow On/Off、三个固定曝光候选共 12 张 PNG。九张正式对照图的解码检查已通过：非全黑/全白、三姿态图不同、真实骨点不同，阴影 A/B 超过 8 灰度的变化区域约 15.90%–16.03%，整体变暗方向正确。主任务已逐图看过；这是独立中性实验，不是正式游戏截图或目标硬件性能验收。

根因与修复证据：

- Python Rotator 的位置参数是 Roll/Pitch/Yaw；错误测试机位出现 180° 翻转。当前测试使用具名参数并检查实际方向，不改游戏镜头。
- 同一 SingleNode 模式下，OverrideAnimationData 只更新保存数据，不更新当前动画实例。原生诊断实际复现“保存 Mid，实例仍 Back”；SetAnimation 后再刷新骨骼，实例和三个真实姿态恢复一致。
- HDR 本来有真实直接光照与几何阴影，物理曝光 LDR 捕获却非常暗。HDR CastShadow A/B 改变 43,057/262,144 像素；DirectLighting Off 归零。独立预览比较 -4/-6/-8 stops 后使用中间候选，保留全部灯强。正式曝光、Lumen 和配置未更改。

相关失败和诊断保留在项目 Saved 的独立 Run 目录；不能把原生退出 0、导入成功或 PNG 存在等同画面通过。

## 印线投影检查

`D:\灯影山海\Saved\Audit-2026-10-14-ArtAppearance\Print-Diagnostic-Run1\PrintShadow-20261014-212025\` 保存三姿态真实阴影与 Mid 彩色外观的 8 张 A/B 图。通过公开 LOD/Section/Material 映射找到 MI_DY_Ink，不猜 section 编号；仅在内存关闭该印线 section 的额外投影，其他五种实体材料仍投影，印线可见性不改。

实测去掉了大部分手旁、头顶的离体碎点，彩色印线仍可见；仍有少量轮廓碎点，需进一步整理源几何。恢复后的 section/材质映射与原始相同，源资产哈希全部相同。该候选尚未保存到 Painted Mesh 或正式场景，不宣称最终皮影美术全部通过。

## 灯具烘焙成果与 UE 导入契约

已发布：`D:\灯影山海\Assets\Sources\DengYingArt\LampBaked-20261014\`。

灯身 20,016 三角形、支架 13,088，总 33,104；完整母源 93,712 保留。新 FBX 按原渲染三角形固定 N-gon，几何与 UV0 对源最大误差均 0；两个 BakeUV1 全部有效且 0 重叠。BaseColor/ORM/NormalDX 共六张 2048×2048，原铜斑、木纹和源材质区分已实际用 FILE 贴图重新渲染。

UV1 法线切线问题已处理：FBX 主 Layer0 使用 BakeUV1 的 Tangent/Binormal，与 Blender 实算最大分量误差 1.788139e-7。UE 必须 Import Normals and Tangents，关闭 N/T 重算和 Generate Lightmap UVs；材质使用 TexCoord1，NormalDX 不翻绿。ORM=白 AO / Roughness G / Metallic B。木色与源法线强度已烘入，不重复乘色或减强。

主任务已看最终灯具全景与灯头近景：铜、木可区分，灯口厚度、转轴接触和结构完整，无明显 atlas 空白、紫色材质或接缝。此结论限于源资产重渲染；UE 导入、法线实际解码、碰撞与灯轨端点尚待验证。光学窗的 Transmission .38 / IOR 1.46 / Emission .15 是独立源语义，不在三张 atlas 中，接入不能假称 PNG 自动还原这些属性。

## 下一步与不变边界

继续在 Dev 中清理皮影投影轮廓、校准握杖外观，并完成表现 Blueprint 和灯具原生材质接入；通过实际画面后再替换正式场景。不可移动原生 Staff 来凑握点，不能以动画骨点取代 A 端投影接触来源。当前单手拟合只是候选，还未完成游戏机位下握杖验收。

本轮不改正式地图、Source、Config、15 Hz、E/A/D/R、谜题目标/容差、三幕流程和旧包。目标仍是完整剩余美术与可靠竞赛版本，不把这份实验验证当作整个建模美术目标完成。
