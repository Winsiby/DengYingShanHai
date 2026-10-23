# 幕框与帷幕｜免费资产准入审查

日期：2026-10-11。唯一人类作者与负责人：用户本人；Codex负责辅助调查、离线文件检查和文档。不引入队友或WorkBuddy依赖。

## 1. 结论与当前状态

本轮完成来源查询、两个GLB的实际隔离下载与二进制几何检查，**没有将候选导入UE、修改现有关卡或生成新游戏包**。当前体验入口仍为 `D:\灯影山海\Start-StageWingsDev.cmd`。

结论：不直接采用现成西式镜框；两个无UV、无布料纹理的帷幕不能直接作为正式近景资产。改按“木构承重框与布质侧幕分离”的路线继续筛选并适配免费构件，不用纯色模型或拉伸家具替代质量验收。不认定所有无UV模型都永远不可用；其后续UV/材质适配需要独立开发与验收，当前没有完成。

审计根目录：`D:\灯影山海\Saved\Audit-2026-10-11-StageFrameResearch`。原始GLB、API响应、网页、CC0文本均隔离于该审计的Sources目录，不进入Content或正式Assets/Sources。

## 2. 当前真实尺度，不是正式建筑定稿

上一已验收冷读显示 `DEV_BackScreen` 为100cm Engine Cube，scale=[.5,9,8]，中心[950,0,350]；当前Dev接收体外尺寸50×900×800cm，正面X925、Y[-450,450]、Z[-50,750]。这只是现有Dev几何，不是古代影戏台尺度，也不把旧ENV规格中5–6m×3–3.5m的建议当作已实现事实。

本轮不更改接收体、主灯、皮影、镜头或谜题参数以迁就新模型。核心保护盒仍是X[-440,975]/Y[-470,470]/Z[-70,770]；它不代表整盏灯的光锥，未来仍必须做实际投影与同POV非遮挡检查。

## 3. 官方来源比较

| 候选 | 核验层级与来源 | 结论 |
|---|---|---|
| [Stage Leg Drape](https://3dassets.dev/assets/theatre-stage-and-backstage-stage-leg-drape-a99e970d) | 发布方3D Assets，CC0，明确标注AI；官方直链匿名获取。GLB实测1.89999998×6.10400602×.25635548m（X/Y/Z，Y向上）、1384三角面、2926顶点、3mesh/材质 | 所有primitive没有TEXCOORD；texture/image均0，仅材质常量。拒绝直接正式近景接入，保留隔离源作结构参考 |
| [Stage Border Drape](https://3dassets.dev/assets/theatre-stage-and-backstage-stage-border-drape-88789270) | 同发布方与许可/AI说明。GLB实测8.30000019×1.50358901×.24928996m、4400三角面、9826顶点、3mesh/材质 | 同样无UV/纹理；宽度与9m当前接收体不一致，不预先用缩放解决。拒绝直接近景接入 |
| [Proscenium Arch Frame](https://3dassets.dev/assets/theatre-stage-and-backstage-proscenium-arch-frame-f9dcb7bb) | 仅查官网，未下载；官方外尺寸10.12×6.44×1.02m、净口7.2×5.2m；CC0/AI，镀金柱、槽线、中央牌饰 | 原开口不容纳当前9×8m接收体，风格偏西式镜框。排除直接使用，不把它改名为中式史制 |
| [Curtain — MZiemys](https://blendswap.com/blend/16983) | 官网CC0、Blender2.7x/Cycles2.87MB；作者说明有UV但减面失真。下载页实见“Sign in to download”；未登录、未取得文件 | 普通布帘候选，非已取得或已导入；真实尺寸、拓扑、转换与近景质量均未验证，不绕登录要求 |
| [Chinese Four-corner Pavilion — VVayToyek](https://vvaytoyek.itch.io/chinese-four-corner-pavilion-free) | 官网标注CC0、多材质无贴图、自动UV、“No generative AI was used”、Zip2.6MB；这些是发布方说明，不是本机实测。免费页面有不付款下载选项 | 只留作木构件候选，不加载整亭。Computer Use浏览器下载页实际429限流、没有取得ZIP；不绕限流、不填邮箱、不支付，也不采用页面无依据的“80%复原”宣传作为文化事实 |

3DAssets的[官方许可页](https://3dassets.dev/license)允许CC0模型复制、修改、再分发与商业使用，同时不提供权利/质量保证。资产AI来源仍需如实记录，不能把开放许可当作文化准确性认证。官网通用说明提及WebP，但**本轮两个实际GLB均没有图像或纹理负载**，不把通用文案写成当前文件事实。

## 4. 实际文件与检查方法

| 文件 | Bytes | SHA256 |
|---|---:|---|
| stage-leg.glb | 57,892 | 406E2ACFC470D8DAFDE476802AF9C646918793AC53315244E7DDB9804572933F |
| stage-border.glb | 186,488 | 6CBE096F19056A15BF3B2E959C212B2671893C7D4A8C003AE0240ECF0D9240B6 |

八份获取文件保留于Sources；ACQUISITION.json记录URL/大小/哈希/正常TLS与未导入状态。两份API保存的是HTTP响应文件，没有重新序列化；发布方没有提供本轮可核对的官方校验和，实测SHA仅用于本地留证与后续不变检查，不伪称官方SHA匹配。

Inspect-FrameCandidates.py仅离线解析GLB2头、JSON/BIN边界、dense accessor、量化/normalized数值、实际三角索引、节点translation/scale。拒绝未处理的rotation/matrix、循环、稀疏accessor和外部buffer，绝不执行模型描述中的脚本或网络请求。逐顶点解码并应用层级TRS后，bounds与官方API匹配；两组面数/顶点数与API一致。检查primitive属性、材质根引用与实际images/textures列表，不用Shell的 `@($null).Count` 判断资源存在。

实际材质为velvet/black/metal的BaseColor与粗糙度常量，无织物Normal/AO/粗糙度贴图。细节、背面阅读和近景质感尚不成立；KHR_mesh_quantization确实存在，但UE5.8实际导入兼容尚未测试。没有为它安装额外插件、转换器或启用新渲染路线。

报告 `GLB_INSPECTION.json` 的PASS只证明本次离线检查执行成功，资产决策仍是 `REJECT-DIRECT-NEAR-FIELD-USE`；不是材质、UE导入、人工画质或运行验收PASS。

独立复核首轮35项中32通过、3失败，发现检查工具未拒绝有符号正索引、VEC3索引和过短的声明buffer；这是工具的边界校验缺陷，不是两个真实模型的UV/材质结论变化。已修复并补充normalized索引与正数过短buffer，使用本机bundled Python 3.12.14重新实跑37项，37通过、0失败、退出码0。GLB_INSPECTION-RUN2.json重新实读两模型，结论与首轮一致。原失败报告、Python314带RuntimePrelude的额外运行记录都原样保留；最终以REVIEW_PARSER_TEST_REPORT-RUN2.json的实际bundled运行记录为准。检查前后八份源、主解析器和两份原报告共11文件哈希一致；不修改网格，也不把解析工具测试当UE画质测试。

## 5. 本轮保护与下一入口

只发布本记录、STAGE_FRAME_NEXT_PLAN.md，以及TECH_SPEC/DEVELOPMENT_PLAN的范围同步；其余既有产品、所有旧包和来源逐文件保持。未读取/修改受限许可登记文件，不操作Git提交/暂存/清理，不改Content、Source、Config、启动器、声音或系统权限。

没有新包，因而没有新的首帧/玩法/音频/Shipping结果；上一台翼版本的154/65/35/41等结果是历史基线，不改称本轮重测。实际保护结果只认本轮FINAL.json，文件缺失或非PASS时不宣布本轮文档交付。

下一步范围与准入退出条件见STAGE_FRAME_NEXT_PLAN.md。项目仍以一座虚构剧场承载山海意象，不以免费模型的国别标签或AI造型替代文化依据。

## 6. 后续更新：亭台来源已取得、单柱已通过Dev准入（2026-10-12）

§1–5和上表是2026-10-11阶段的真实研究结果，原429失败不改写。本次通过发布方正常匿名“不付款下载”入口实际取得2,777,866B ZIP，SHA256=008FB5C4508CE57C4203E5763FD01A177DED16CA94FD5DE34EA26C422B483EFA；没有登录、邮件、支付或绕限制。ZIP为一FBX及21张UV-layout PNG，PNG不是PBR材质；实际FBX无Texture/Video对象。

只从原FBX提取既有“檐柱1” Geometry/Model/两个材质槽，不改原几何/法线/UV字节、单位或缩放。派生FBX20,772B，SHA256=8E83F84DAAA55DCD794B5138A8C776784669CA3393832EE113A1633DE5EDE1AB，独立96项核对通过。UE导入后真实高度20.36m，不把它虚称为合适的戏台柱，也不默默更改单位。

采用Poly Haven免费CC0 Dark Wood实际2K Diffuse/NormalDX/ARM；Wood Table实际原图有拼板接缝，排除用于连续柱身近景。完成侧面UV长轴实读、90度采样及配套切线法线逆基底、两个实例分槽。七份Dev资产实际保存、D3D12冷读与真实查看器画面留证。这个准入不是完整幕框/近景材质/剧场画质认可，1×1物理纹理密度、柱脚与端面、比例、固定机位遮挡和性能尚待验证。

原33Actor/主地图/旧启动器/全部旧包不变，无新游戏包。来源/派生与准确分层结果见 `FRAME_POST_ASSET_SOURCES.md`、`FRAME_POST_ASSET_VALIDATION.md`，本次新审计 `Saved/Audit-2026-10-12-FramePostAsset`；上一研究审计保持历史原样。
