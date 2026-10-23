# 灯具本地 PBR 烘焙交付

本目录已完成可信自产 RuntimeVariant 灯具的本地 shader 烘焙、全部 FILE 贴图重建渲染与独立冷读。未启动 UE，未写 D 盘源文件，未访问禁止的 LICENSES.md。

交付资产：`DY_HeroSpotlight_Baked.blend`、`SM_DY_LampBody_Baked.fbx`、`SM_DY_LampStand_Baked.fbx`，以及 Body / Stand 各自的 `T_DY_*_BaseColor.png`、`T_DY_*_ORM.png`、`T_DY_*_NormalDX.png`。六张 PNG 均为 2048×2048。`Lamp_Baked_Full.png` 与 `Lamp_Baked_Head.png` 是最终 FILE 材质全景和近景。

冷读实测如下：

| 项目 | 灯身 | 支架 |
|---|---:|---:|
| 顶点 | 10,113 | 6,592 |
| 三角形 | 20,016 | 13,088 |
| 对源 FBX 顶点坐标最大误差 | 0 m | 0 m |
| 对源 FBX UV0 最大误差 | 0 | 0 |
| 对源 FBX corner normal 最大角误差 | 0.045383° | 0.030335° |
| BakeUV1 非零 UV 三角形 | 20,016 | 13,088 |
| BakeUV1 严格三角形重叠 | 0 | 0 |
| FBX UV1 主切线分量误差 | 1.788139e-7 | 1.788139e-7 |

总数仍为 33,104 三角形。源 N-gon 被按原渲染 `loop_triangles` 固定为相同的渲染三角形；冷读确认源三角形集合与绕向一致，顶点、原 UV0 和材质分区保留。BODY 保持 6 槽、STAND 保持 5 槽。灯身原枢轴 0、支架原 Actor-local Z=-95 cm；两件 FBX 的导出对象局部位置为 0，UE 支架组件仍按原 -95 cm 装配。

使用每组一套有限 atlas，沿用原材质分区。普通铜、黑金属、反射罩、木和橡胶使用 Surface / Opaque / Default Lit 的 PBR 输入即可；光学窗保留独立材质语义，其源 Transmission=.38、IOR=1.46、EmissionColor=(.8,.37,.10)、EmissionStrength=.15 不在三张 atlas 中。不能把这些语义误称为已经由 PNG 自动携带；透射实际 UE 路径需要原生材质重建时确认。

UE 导入与连接契约：

- UV0 索引 0 是完全保留的原 `UVMap`；atlas 固定用 UV1 索引 1 的 `BakeUV1`。FBX 主 Layer 0 的 Tangent/Binormal TypedIndex 0 实际写入 BakeUV1 的 TBN。
- 选择 **Import Normals and Tangents**，关闭 Recompute Normals / Recompute Tangents，关闭 Generate Lightmap UVs，避免重写或改用原 UV0 的切线。不得只选择 Import Normals 后让 UE 按 UV0 重建切线。
- BaseColor：sRGB 颜色采样，直接连接 BaseColor。木源 tint 已烘入，无需再乘 (.31,.25,.19)。
- ORM：关闭 sRGB，R=1 白 AO、G=原 Roughness、B=原 Metallic。木源 ARM 只有 G 参与源 shader，烘焙木 Metallic 仍为 0。
- NormalDX：关闭 sRGB，Normal compression / Normal sampler，R +X / G -Y / B +Z，**Flip Green Channel=False**，直接连接 Normal，强度 1。源木 Strength=.35 与铜 Bump=.22 已计入烘焙。
- 核心实时光仍由现有 UE Movable SpotLight 提供，贴图中不含场景灯光。没有引入 WPO、RVT、材质层或额外插件。六张 2K atlas 的未压缩 RGB 像素数据约 72 MiB；UE 实际压缩显存和 shader 成本需导入后测量。

源 .blend、RuntimeVariant .blend、两组源 FBX 共 4 件、原始木纹 PNG 共 3 件合计 9 文件的前后 SHA256 全部一致；原 packed 木纹三图哈希也与原文件一致。铜为自产 Object 坐标程序 shader，木源为 Poly Haven Wood Table / Dimitrios Savva / CC0。没有改写外部原图。来源与原哈希记录在 `LAMP_BAKE.json`。

检查报告：`LAMP_BAKE_COLD_READ.json` 是最终冷读 PASS；`LAMP_BAKE_FINALIZE.json` 记录法线方向不变的单位化、TBN 实测与前次诊断。灯身最初 60 个长度误差 >4% 的像素全在 UV 覆盖外 padding，覆盖内没有坏法线；单位化后全图严格检查通过。`LAMP_BAKE_VISUAL_QA.json` 记录已实际打开并检查的最终两镜头和源图比较结论。

本地视觉结论：灯具全身结构完整，铜斑、木纹、轮廓和光学分区保留；两镜头未发现明显 atlas 接缝、空白/紫色材质、断裂边缘或重复 tint。2K atlas 不是无限程序细节的像素级无损保证。

后续唯一责任人：项目负责人完成原生 UE 材质接入，并在 Development、目标硬件和打包版本验证法线、透射、实时主灯与实际场景表现。本次仅本地烘焙交付，尚未验证 UE 导入和打包。
