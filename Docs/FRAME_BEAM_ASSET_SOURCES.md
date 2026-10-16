# 免费横梁｜来源与派生记录

2026-10-12。唯一人类作者与负责人：用户。Codex辅助提取、导入、检查与文档；不作为制作成员。本阶段仅准入真实构件，尚未摆入地图。

## 1. 模型来源

[VVayToyek：Chinese Four-corner Pavilion](https://vvaytoyek.itch.io/chinese-four-corner-pavilion-free) 原页明确CC0、自动UV、多材质且无贴图，并声明未用生成式AI。源ZIP/FBX已在上一阶段合法匿名取得，未付款、登录或绕限流；本次复用同一已冻结原件，不重新下载整亭。

原FBX为 `D:\灯影山海\Saved\Audit-2026-10-12-FramePostAsset\Sources\pavilion-original.fbx`，2,040,044B，SHA256 `E5A745FCEEF8EB0E4B45230E4D964F618C64AB0981F098E1E329C982C159E89C`。完整原许可/原ZIP/作者披露见 `FRAME_POST_ASSET_SOURCES.md`。源页建筑复原宣传不作为年代、地域、文物或皮影流派考据。

实际选择“额枋1”Model824772630、独占Geometry512851073、原额枋Material450385832，父级根0、只显式平移，无源旋转/缩放。源Y-up、1单位1cm，真实局部尺寸2630.546631×142.727215×111.114189cm，长轴源X；16顶点/10多边形/48角、38 UV pair/48索引、8条纯长边都沿UV V。不是横放檐柱、放大家具或人工重建网格。

仅派生一个FBX：`Saved/Audit-2026-10-12-FrameBeamAsset/Sources/frame-beam-derived.fbx`，15,224B，SHA256 `D4CD58BDB649DB16C27D980BC9292160EF7EB69FA3B2BEF2453A0DCC3C59D628`。

派生允许变化只有删除无关Objects/Connections、Model场景平移归零、Definitions数量调整。原Geometry/Normal/UV/槽定义、原材质、GlobalSettings、Header/Footer与局部pivot属性字节保留；连接行序改变，但每条原OO字节及图集合保持，原/实际序均留证。不缩放、顶点居中、改单位或添加纹样。

独立扫描器不执行主派生脚本、不信自报哈希，逐256节点核对。源核查和验证报告位于本轮Saved审计；Run1数量断言错误与Run2成功均保留。50894是数据扫描断言，不是游戏用例或质量评分。

## 2. 材质来源与复用

唯一新UE资源 `Dev/FrameBeamAsset/Meshes/SM_DY_FrameBeam_Source`，原“额枋”槽引用既有 `MI_DY_FramePost_Wood`→`M_DY_FramePost_Master`→三张Dark Wood纹理，旧五依赖字节冻结。没有复制七份柱资产、重复纹理或新增Master。

贴图来源 [Poly Haven Dark Wood](https://polyhaven.com/a/dark_wood)，按 [Poly Haven CC0许可](https://polyhaven.com/license)；原作者角色、2K官方Bytes/MD5/SHA、颜色与NormalDX/ARM记录仍见 `FRAME_POST_ASSET_SOURCES.md`。此前实际Diffuse顺纹沿U；梁长向UV V，因此复用QuarterTurn=1：采样 `(V,1-U)`，切线法线 `(-Ny,Nx,Nz)`。UV0保留，1×1只用于方向比较，不证明26米物理贴图密度或端面真实切口。

## 3. 作者、AI与文件边界

Codex执行数据-only解析/提取、独立验证、UE原生导入/冷读、入口和文档辅助；Computer Use观察原生查看器、留存未编辑截图。不是AI原创横梁，也不以源页AI声明代替独立作者认证。

没有付费资产、生成服务、新软件安装或账户注册。原18份柱来源和15份早期来源不改；新原始帷幕候选隔离在本轮 `CurtainEvidence`，没有导入游戏。许可登记文件未读取、哈希或修改；本来源记录明确公开素材与AI辅助，不替代最终参赛登记。
