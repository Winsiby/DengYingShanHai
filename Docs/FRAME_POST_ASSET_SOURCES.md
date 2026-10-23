# 单柱Dev资产｜免费来源与派生记录

2026-10-12。唯一人类作者与负责人：用户；Codex是来源/实现/验证辅助，不是制作成员。本步只准入一个现成柱件与木纹方向，不导入整亭，不改变游戏。

## 1. 原始模型

[Chinese Four-corner Pavilion（VVayToyek）](https://vvaytoyek.itch.io/chinese-four-corner-pavilion-free) 发布页标注 CC0、多材质/无贴图/自动UV，声明“No generative AI was used”。这是发布方的AI声明，不是独立作者身份或传统建筑考证。只作为一座虚构影戏台的构件来源，不采用其“80%复原”宣传，不声称特定时代、地区或皮影流派复原。

通过正常匿名“不付款、直接下载”入口取得 ZIP，不登录、不填邮箱、不支付、不绕过限制。旧2026-10-11的429失败留在原研究审计；新下载成功只追加，不追溯改写。首次浏览器截图超时，未将其虚称截图证据；来源HTML、原ZIP与实际下载文件留下。

| 文件 | Bytes | SHA256 |
|---|---:|---|
| 原 ZIP：仿古四角亭(Chinese Four-corner Pavilion).zip | 2,777,866 | 008FB5C4508CE57C4203E5763FD01A177DED16CA94FD5DE34EA26C422B483EFA |
| 原 FBX：四角亭.fbx | 2,040,044 | E5A745FCEEF8EB0E4B45230E4D964F618C64AB0981F098E1E329C982C159E89C |
| 仅派生一柱：frame-post-derived.fbx | 20,772 | 8E83F84DAAA55DCD794B5138A8C776784669CA3393832EE113A1633DE5EDE1AB |

实际 ZIP 22个文件：1FBX+21张名称含UV的PNG，后者是UV-layout图，不是颜色/法线/粗糙度贴图。FBX7400，70Geometry/71Model/22Material，无Texture或Video对象。文件名保留真实Unicode；初次CP437误解码作为工具失败记录保留，原字节未改。原文件不执行代码、不作为软件安装。

派生仅选择 Model813316417（檐柱1）→Geometry134604809及原材质465935122/959631505；删去其他Objects/Connections，将原场景 Model 平移[1100,0,1100]置零、更新Definitions计数。Geometry/Normals/UV属性原字节保留；Header/Footer/GlobalSettings与轴、单位、缩放保持。不重建网格、UV或造型，原文件永远保留。

源Y向上、1单位1cm；UE按原声明转换为Z向上。实读源128顶点、98多边形、252三角面，UV0 232pair/448corner，448法线、两个槽；UE渲染顶点384是法线/UV拆分，不能误写“增加了原造型”。实际导入尺寸285.278×285.278×2036.122cm，高20.36m：**没有自动缩放或摆入关卡**。

## 2. 木纹PBR

采用 [Dark Wood（Poly Haven）](https://polyhaven.com/a/dark_wood)，遵循 [Poly Haven CC0 许可](https://polyhaven.com/license)。作者角色：Dario Barresi（Baking）、Dimitrios Savva（Photography）、Rico Cilliers（Tiling）。实际获取官方2K PNG Diffuse/NormalDX/ARM，原API/info响应保留；与API实际Bytes、MD5、2048×2048 dimensions核对一致。没有下载收费预览渲染图，也没有把网页图片当游戏贴图。

| 图 | Bytes | MD5 |
|---|---:|---|
| dark_wood_diff_2k.png | 21,249,991 | 2ee776ee90dc522dc9949f992e2b199c |
| dark_wood_nor_dx_2k.png | 18,636,146 | 624152d95434db959b090bd4050f9c3f |
| dark_wood_arm_2k.png | 16,354,635 | 5025524bd1c6746ac83e7c4f4bbcacfe |

完整SHA/URL见审计 `Sources/DarkWood/POST-TEXTURES.json`。实际查看原Diffuse为沿U连续木纹；选择用于未定稿的木柱材质方向样本，而不是根据资源名称认定近景质量。

[Wood Table](https://polyhaven.com/a/wood_table) 同样CC0、作者Dimitrios Savva；先取得三图/API并校验，但实际原图明显有桌板拼缝。只在隔离Sources保留比较，不导入UE、不作为柱身。免费不代表适配主题；不以拼板接缝充当纵向完整木柱。

## 3. 存放、许可与AI记录边界

原始来源、官方页、CC0文本、两材质的原图/API、派生FBX全部隔离于 `D:\灯影山海\Saved\Audit-2026-10-12-FramePostAsset\Sources`，18文件有独立哈希冻结；未移动/覆写正式Assets/Sources中的15份旧来源。本记录为本步来源披露，**没有读取、哈希或修改受限制的Docs/LICENSES.md**。CC0文本说明不替代上游真实性/权利/质量判断；正式提交仍需如实列出第三方与AI使用。

AI辅助：Codex编写数据-only解析/提取、UE导入与材质检查脚本、独立数学/文件复核、文档；Computer Use观察本机原生UE查看器并留图。不是AI原创柱形，不把AI列为人类作者。本步无生成服务、付费软件/素材、账户注册或新建模工具安装。

后续若改尺度、UV、柱脚材质或参考造型，另留派生记录；不要将此原始柱件外观自动命名为夸父、山海纹样或正统皮影道具。
