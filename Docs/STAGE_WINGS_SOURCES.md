# 台翼屏风 Dev 样本｜来源与适配记录

记录日期：2026-10-11。项目负责人及唯一人类制作作者：用户本人；Codex 辅助本轮资源集成、验证与记录。不依赖虚构队友，不要求用户手工建模。

本记录只覆盖一个原尺寸、非交互的单侧台翼陈设样本，不代表整座剧场、完整幕框、正式比赛美术或历史皮影器具已经完成。来源下载的 `PASS` 只表示原始文件完整性检查通过；**UE 导入、冷读、材质、运行、打包和人工画质必须分别验证**，不能沿用下载结论代替。

## 1. 采用来源及事实边界

| 项目 | 本轮事实 |
|---|---|
| 资源 | Poly Haven — Chinese Screen Panels |
| 官方资源页 | https://polyhaven.com/a/chinese_screen_panels |
| 作者 | Kirill Sannikov |
| 许可 | CC0-1.0；官方许可页 https://polyhaven.com/license |
| 法律文本原来源 | https://creativecommons.org/publicdomain/zero/1.0/legalcode.txt |
| 获取记录时间 | `2026-10-11T05:00:33.1332541Z`，本地 13:00:33 |
| 成本 | 0；未购买、登录、订阅或使用付费生成服务 |
| 采用文件 | 一个官方 2K FBX、Diffuse / DirectX Normal / ARM 三张 2048 × 2048 PNG |
| 网站标称规格 | 1.6 m 高、784 tris；**这是官方页面标称，不是本项目 UE 导入测量** |
| 本轮 UE 实测 | AssetInspect-Run2 / ColdVerify-Run1：129.3967819 × 37.6891170 × 160.3126234 cm，784三角面、978顶点、1 LOD / UV / 材质槽；来源页面标称与实测分别留证 |
| 不作为游戏资产 | 网站预览渲染、网页文案、商标与 Logo |

来源文件目录：`D:\灯影山海\Assets\Sources\PolyHaven\chinese_screen_panels\`。

官网许可将模型和纹理作为 CC0 资产提供；这不是对网页预览和商标的许可。本项目仍主动保留作者、许可与获取链，用于过程证据。CC0 法律文本复用此前从官方来源留存的同一文件，SHA256 为 `A2010F343487D3F7618AFFE54F789F5487602331C0A8D03F49E9A7C547CF0499`，没有将网站页面简单视为许可证。

本轮未读、未改受限的 `Docs/LICENSES.md`；许可记录独立留存在本文、来源目录与审计目录。官网/API 可访问与来源许可明确，不意味着最终材质或场景效果已经通过。

## 2. 四个实际源资产文件

以下值来自本轮 `ACQUISITION.json` 与 `RAW-SOURCES.json`，不是猜测的 URL，也不是重新编码后的文件哈希。四个源资产文件合计 **39,725,354 B**。

| 文件 | Bytes | MD5 | SHA256 |
|---|---:|---|---|
| `chinese_screen_panels_2k.fbx` | 55,212 | `61a5108edaa2fadd03abe6fd94ab965b` | `FF84163E810A87CCD6AC9C08242FF366F0F0CC803A4D1DBF22CCF7FE6BC58CEF` |
| `chinese_screen_panels_diff_2k.png` | 16,016,213 | `89ffe8a283b96e252ad6dd508e64af56` | `AEC2B65FC1021F971C448C6493C4511B75468A2E7BE54C956D69401A55A29769` |
| `chinese_screen_panels_nor_dx_2k.png` | 12,984,763 | `2ef7db9fc2098d8ccf16fbcfddbfd3ef` | `10A850D22A15011185C840C8E3B04506B328DFF2C2E30FC66AAD004DF91CF146` |
| `chinese_screen_panels_arm_2k.png` | 10,669,166 | `71b1fed3490342a84d0699d5275cb7e8` | `B03AA44728E30BB0B591E66C9EC82D18BB302D1C6E90AD4D3E039C793BCC2939` |

精确官方下载地址：

```text
https://dl.polyhaven.org/file/ph-assets/Models/fbx/2k/chinese_screen_panels/chinese_screen_panels_2k.fbx
https://dl.polyhaven.org/file/ph-assets/Models/png/2k/chinese_screen_panels/chinese_screen_panels_diff_2k.png
https://dl.polyhaven.org/file/ph-assets/Models/png/2k/chinese_screen_panels/chinese_screen_panels_nor_dx_2k.png
https://dl.polyhaven.org/file/ph-assets/Models/png/2k/chinese_screen_panels/chinese_screen_panels_arm_2k.png
```

文件大小和 MD5 与实时官方 `/files/chinese_screen_panels` 响应一致；三张 PNG 签名与 IHDR 尺寸均通过，FBX 完整 23 字节二进制头通过。文件原字节未覆盖、未重编码；导入后仍保留以上原始来源文件。

## 3. 八份原始来源与证据文件

正式来源目录实际保存八份文件，合计 **39,779,185 B**：上述四个资产文件，另加以下四个记录。两个零字节的首次失败 API 输出只留在 staging 作为失败记录，**不计入、不复制到正式来源目录**。

| 记录文件 | Bytes | SHA256 |
|---|---:|---|
| `ACQUISITION.json` | 2,207 | `D53D2A3F9BEAEAD3DD26EB419476AE80E6047F19657558B1BCED6438007DAF4F` |
| `CC0-1.0-legalcode.txt` | 7,048 | `A2010F343487D3F7618AFFE54F789F5487602331C0A8D03F49E9A7C547CF0499` |
| `chinese-screen-files.json` | 43,397 | `28CD10732B451097FA2451197D9826C7102D5EA58053CDF5B469A788E5923AE4` |
| `chinese-screen-info.json` | 1,179 | `510022F0137ABF46FF5C1C594F152784AAEC52214D724F03DDB2C55171A53B10` |

`chinese-screen-info.json` 与 `chinese-screen-files.json` 是正常 HTTPS 查询得到的官方 API 数据的重新序列化副本，`MetadataReserialized=true`，不是 HTTP 原始字节流。下载查询使用可识别本项目的 User-Agent；没有跳过证书、修改全局代理、TLS 策略或凭据。`ACQUISITION.json` 中 `Imported=false` 描述获取时刻，不代表以后导入未发生；后续状态只以独立验收结果为准。

## 4. 六个实际 UE 内容包与适配合同

本轮已在 `Dev/StageWings/` 中新建以下六包，并完成只读冷加载，不覆盖原共享材质或现有木地板资产：

```text
/Game/DengYingShanHai/Dev/StageWings/Meshes/SM_DY_WingScreen
/Game/DengYingShanHai/Dev/StageWings/Textures/T_DY_WingScreen_BaseColor
/Game/DengYingShanHai/Dev/StageWings/Textures/T_DY_WingScreen_NormalDX
/Game/DengYingShanHai/Dev/StageWings/Textures/T_DY_WingScreen_ARM
/Game/DengYingShanHai/Dev/StageWings/Materials/M_DY_WingScreen_Master
/Game/DengYingShanHai/Dev/StageWings/Materials/MI_DY_WingScreen_Dev
```

适配目标采用实际已启用的 **标准 Default Lit PBR**（当前 `r.Substrate=0`），Surface / Opaque / 单面 / 切线空间法线；不是 Substrate 迁移，不改变 Config、灯光或曝光。材质连接与采样设置必须在冷读中实际核验：

- Diffuse RGB → BaseColor：sRGB 开启，Color 采样。
- DirectX Normal RGB → Normal：sRGB 关闭，NormalMap 压缩及 Normal 采样；不任意翻转绿色通道。
- ARM R → Ambient Occlusion、G → Roughness、B → Metallic：线性 Masks 采样。B 只保留原作者对该模型表面的金属标记，不添加新的发光或金属装饰，不把所有木框设成金属。
- 保留原作 UV0，以 1 × 1 原生 UV 使用；不套地板 12 × 9 平铺，不拉伸彩绘来铺满幕框。
- 无 WPO、位移、透明、布料模拟、RVT、新 Material Layers 或动态材质实例。

场景只计划新增 `DEV_WingScreen_Right` 单个非交互 StaticMeshActor。其导入后实际 bounds、底部位置、统一 scale=1 与轴向必须实测并冻结为放置记录。新增对象关闭碰撞、所有通道 Ignore、关闭阴影及动态间接/距离场光照影响，无 Tick，不监听谜题或驱动流程。**这些配置不自动证明视觉不遮挡**：还须实际检查主灯、偶、操杆、影幕、落杖与成林画面及玩家路径。

实际集成已核验：129.3967819 × 37.6891170 × 160.3126234 cm，784三角面/978顶点/1UV/1LOD/1材质槽；没有Nanite、自动简单碰撞或网格距离场。AssetInspect2只读六包后Place9只保存现有Dev地图；原尺度1、yaw=-90、X400/Y650，以实际bounds对齐Z0。冷加载及五态运行保留公开Actor/Component Tick关闭、无影/间接/距离场影响。原生全部Ignore设置使具名Profile为Custom，而CollisionEnabled实际NO_COLLISION；八个公开通道实读ECR_IGNORE。隐藏24通道不导出，Tick能力bCanEverTick受保护，两者均不伪称实际读取/不绕过。源PNG/FBX、六磁盘资产及原木地板均未重写；实际画面局限见验证记录。

## 5. 文化创意与尚未完成项

这是一件孔雀/花卉彩绘的通用中式家具，作用是为虚构后台补充旧演出空间的陈设层次；它不是《山海经》角色、夸父形象、山海经专属纹样、某时代戏台或某皮影流派的正统器具。文档不得把该资产名称中的 “Chinese” 转换成历史准确性认证。

仅以接近原尺度的小型台翼陈设使用，不把官网约 1.6 m 高的屏风拉到当前 8 m 影幕高度，也不把多件堆叠当作完整幕框。完整幕框、帷幕几何、正式建筑风格及大范围环境叙事仍是缺口；本轮不新增院落、亭子、观众席、第二幕台或可探索房间。原木地板、核心灯—偶—幕关系、核心机制与三幕因果链必须保持不变。

是否成为正式资产还取决于实际导入细节、同机位视觉可读性、与全场风格是否协调、Windows 包运行及作者人工画质判断。本轮只制作可独立回退的 Dev 样本，不宣布“高质量剧场完成”或“廉价感已消除”。
