# 木地板 Dev 试片｜来源与适配记录

记录日期：2026-10-11。项目负责人及唯一人类制作作者：项目作者本人；Codex 负责本轮集成、验证与记录。

本记录只覆盖现有 Dev 场景的地板材质试片，不代表剧场空间、美术风格或正式比赛资产已经定稿。资源获取记录中的 `PASS` 仅表示下载文件的完整性检查通过，**不表示 UE 导入、材质、运行、打包或人工视觉验收已通过**；后续结果见 `WOOD_FLOOR_VALIDATION.md`。

## 1. 采用资源

| 项目 | 事实 |
|---|---|
| 资源 | Poly Haven — Old Wooden Floor 02 |
| 官方资源页 | https://polyhaven.com/a/old_wooden_floor_02 |
| 作者 | Charlotte Baglioni（Scanning）、Jenelle van Heerden（Processing） |
| 许可记录 | CC0-1.0；官方许可页 https://polyhaven.com/license |
| 法律文本来源 | https://creativecommons.org/publicdomain/zero/1.0/legalcode.txt |
| 原始分辨率 | 三张 PNG 均为 2048 × 2048 |
| 获取时间 | `2026-10-11T03:50:15.4888001Z`（本地 11:50:15） |
| 成本 | 0；未购买素材、订阅或生成服务 |
| 使用内容 | 原始 Diffuse、DirectX Normal、ARM 纹理；不使用网站预览渲染、商标或网页文案作为游戏资产 |
| 来源文件状态 | 下载及完整性记录已留存；原像素未修改；导入与运行状态另记，不沿用获取记录的 `Imported=false` 判断后续情况 |

项目源文件目录：`D:\灯影山海\Assets\Sources\PolyHaven\old_wooden_floor_02\`。

该目录当前共有七份文件：三张 PNG、`floor-info.json`、`floor-files.json`、`ACQUISITION.json` 和 `CC0-1.0-legalcode.txt`。获取记录保存官方 URL、文件大小、MD5、SHA256 和像素尺寸；不将文件名中的 “free” 或网站可下载视作许可证据。本文与独立来源记录不修改项目受限的 `Docs/LICENSES.md`。

## 2. 原始纹理与哈希

官方下载统一前缀：`https://dl.polyhaven.org/file/ph-assets/Textures/png/2k/old_wooden_floor_02/`。下表 SHA256 来自本轮 `ACQUISITION.json`，原始文件应保留，不能用重新编码后的文件替代来源证据。

| 原始文件 | 字节数 | SHA256 |
|---|---:|---|
| `old_wooden_floor_02_diff_2k.png` | 21,992,097 | `D60C5E6193A08536F9D51FF70A2CAD79BC16AB216D6F28F18C61A6BDBA619029` |
| `old_wooden_floor_02_nor_dx_2k.png` | 20,722,136 | `E6534B04F22ED2154C431ACD63C4D841D6DE69236494CBFDF58FA6FAC0ACA1D2` |
| `old_wooden_floor_02_arm_2k.png` | 15,409,800 | `CCCFC53F964CC55754A9FC78F6300F3CDFB0829990D113AEFCF40FD5398E512C` |

CC0 法律文本的记录 SHA256：`A2010F343487D3F7618AFFE54F789F5487602331C0A8D03F49E9A7C547CF0499`。保留作者与来源是本项目的过程证据要求，不据此把通用扫描木地板称为某时代、某地域或某流派的历史复原材料。

## 3. 精确五个新 UE 内容包

以下是 authoring 脚本的目标路径，资产是否成功生成与冷读须以当次验证报告为准。

```text
/Game/DengYingShanHai/Dev/WoodFloor/Textures/T_DY_WoodFloor_BaseColor
/Game/DengYingShanHai/Dev/WoodFloor/Textures/T_DY_WoodFloor_NormalDX
/Game/DengYingShanHai/Dev/WoodFloor/Textures/T_DY_WoodFloor_ARM
/Game/DengYingShanHai/Dev/WoodFloor/Materials/M_DY_WoodFloor_Master
/Game/DengYingShanHai/Dev/WoodFloor/Materials/MI_DY_WoodFloor_Dev
```

唯一获准的既有场景改动是 `/Game/DengYingShanHai/Dev/EnvironmentStates/Maps/LV_EnvironmentStatesLab` 中 `DEV_Floor` 的材质槽 0。不得覆写既有共享材质，也不替换幕布、皮影或灯具材质。

## 4. 本轮适配方式与限制

材质采用本机真实启用的 **标准 PBR / Default Lit 父材质 + 一个常量材质实例**；Surface、Opaque、单面、切线空间法线。`RenderInspect-Run1` 读取的 `r.Substrate=0`，不是已启用 Substrate；因此本轮不使用 Slab/Front Material 路线，也不修改 Config 开启 Substrate。它仅是地面材质，不建立全场景通用材质框架，不增加 Material Layers、MPC、RVT、动态实例、透明层或静态开关组合。

- Diffuse 的 RGB 连接标准 BaseColor，sRGB 开启、Color 采样。
- DirectX Normal 的 RGB 连接标准 Normal，使用线性 NormalMap 压缩与 Normal 采样，不叠加任意翻转绿色通道。
- ARM 以线性 Masks 导入；R 连接标准 Ambient Occlusion、G 连接标准 Roughness。木材为非金属介电体，标准 Metallic=0、Specular=0.5（对应介电 F0=0.04）；ARM 的 B 通道不作为本轮金属度控制使用。
- 纹理坐标采用既有网格 UV0；`TilingU=12`、`TilingV=9` 是 **Dev 候选平铺**。数值增加会加密重复、减小视觉纹理尺度；减小则放大。当前未核验 Cube 顶面 UV 轴方向及真实板宽，不能宣称这已实现精确 2 m 物理平铺，也不能把木纹方向定为最终建筑方向。
- 无 Emissive、无 WPO、无位移，不改变地板的几何轮廓、碰撞、角色落地高度或相机遮挡。真实可见反射与细节由原有灯光、曝光与粗糙度产生，不新增灯具或调曝光补救材质。

### 初版错误与有界修复

初版误把能创建/编译 Slab 节点当作项目已启用 Substrate 的依据，只连接了未启用路线的 Front Material，标准 BaseColor、Normal 和 Roughness 输出没有连接，造成地板全黑。无着色器编译错误不代表材质在当前渲染路线可见；初版路线及黑地板截图不作为可用试片或画质通过证据。

`RenderInspect-Run1` 实际读取到 `r.Substrate=0` 和三个标准输出为空；`MaterialRepair-Run1` 只保存本轮自己新增的 `M_DY_WoodFloor_Master` 一包，重连上述标准 PBR 输出，移除无效 Slab/F0 节点，保持原纹理、实例、UV 候选数值和场景不变，未改 Config、灯光或曝光。修复报告 `success=true`、标准 PBR 验证成立、编译错误为空、退出码 0。随后 `ColdVerify-Run2` 新进程冷读确认实际标准输出、`Front Material` 为空、`r.Substrate=0`、材质槽之外的场景合同保持，`saved=[]`、退出码 0。完整流程与人工视觉认可仍须独立验证，不能由这两份技术结果推断。

## 5. 主题契合与尚未选择的空间风格

旧木板的磨损、板缝与克制表面响应用于减少灰盒平面感，支持“久未开演、仍可复演”的虚构影戏舞台。这是通用环境材料，不能单凭纹理宣称传统戏台形制、历史年代或皮影地域流派准确。

本轮不搭建新壳体、入场短廊、观众席、远景或镜头，也不把完整现有地面都定为最终舞台木构。文档中存在“院落戏台”“小型影戏剧场”等空间候选；用户所说“空荡的大型剧院”当前作为声场要求保留，**不是本轮建筑形态定稿**。这些空间风格与规模的实质选择留在后续空间方案中说明，本次试片不替用户隐含选择院落或扩成大型剧院。

来源清晰不等于画质自动合格：高质量要由同机位对比、纹理尺度、反射稳定性、舞台焦点与打包运行共同证明。本轮结果未形成前，不将该试片写作“正式美术完成”或“廉价感已消除”。
