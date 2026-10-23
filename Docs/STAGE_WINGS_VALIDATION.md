# 台翼屏风 Dev 样本｜验收记录

记录日期：2026-10-11。负责人：用户是唯一人类制作作者，Codex 辅助实施与验证。

**当前状态：运行回归、独立 Development 包、实际首帧和四条启动器检查通过。**来源、实际网格测量、唯一陈设摆放、冷加载、两轮完整三幕和真实控制会话均有本轮证据。最终保护由审计根目录 `FINAL.json Status=PASS` 独立证明；该文件缺失或非PASS时仍不交付。以下计数不取自旧版本，不将包首帧当作包内完整通关。

## 1. 用户可见目标与变更范围

在原木地板 Dev 场景的单侧台翼增加一个原尺寸中式屏风，增加后台陈设层次；保留灯、偶、操杆及幕上真实影子的可读性。屏风不交互，不改变输入、镜头、照明、碰撞路径、声音、脚步、15 Hz、三幕参数、切幕解除操纵、落杖成林或重演逻辑。

计划只新建六个 `Dev/StageWings/` 内容包和一个原生非交互 StaticMeshActor；既有内容只允许修改 Env Dev 地图，文档既有文件只允许 `TECH_SPEC.md` 与 `DEVELOPMENT_PLAN.md`。不改 C++、Config、Blueprint 游戏逻辑、主灯、偶、幕材质或原木地板五包，不扩大到完整幕框或正式建筑定稿。

独立开发方案：`Docs/STAGE_WINGS_DEV_PLAN.md`。独立来源记录：`Docs/STAGE_WINGS_SOURCES.md`。审计根目录：`D:\灯影山海\Saved\Audit-2026-10-11-StageWings\`。

## 2. 当前已经取得的证据

| 项目 | 当前状态与实际证据 |
|---|---|
| 官方来源与免费许可 | 已查证 Poly Haven Chinese Screen Panels、Kirill Sannikov、CC0；不使用网页预览或商标 |
| 四个源资产下载 | `ACQUISITION.json Status=PASS`；四项 Bytes / 官方 MD5 / 实测 SHA256 已留存 |
| PNG / FBX 文件头 | 三张 PNG 签名及 2048 × 2048 尺寸通过；FBX 完整 23 字节二进制头通过 |
| 正式来源文件集合 | `RAW-SOURCES.json` 实际八文件、39,779,185 B；不计入两个零字节失败 API 输出 |
| 改前保护 | `BEFORE.json` 与 `Before/` 已生成；基线287个既有产品文件、822个旧归档文件、7个旧来源文件；允许既有写入三文件。包前与入口发布前已逐项通过，最终一致性只认 `FINAL.json` |
| 源码写入 | 本轮计划不改源码；最终必须以 86 个源码文件哈希核对，而不是仅凭计划文字 |
| Git 操作 | 不提交、不清理、不覆盖用户旧改动；最终 HEAD 与暂存状态仍需核对 |

实际 `AssetInspect-Run2` 只读测量：129.3967819 × 37.6891170 × 160.3126234 cm（X/Y/Z），一个 LOD、978 vertices、784 triangles、一个 UV 通道和一个材质槽；Nanite=false，简单碰撞0，网格距离场生成=false。三张纹理在原生编译等待后实际均为2048²，sRGB/NormalMap/Masks及五个实际材质输出均通过；标准PBR，不启用Substrate。

`Place-Run9` 是唯一成功地图保存：X400/Y650、uniform scale1、显式 yaw=-90，实际bounds底部Z0；原32 Actor的对象路径、组件/灯/轨道/森林/绑定完整合同保持，总33。世界bounds min=[368.8862381,583.0552063,0]，max=[406.5753551,712.4519882,160.3126234]，不侵入核心保护盒。碰撞关闭，原生全部Ignore设置后具名Profile为Custom；冷读和五态运行分别实读八个公开通道为ECR_IGNORE，不伪称读到了24个隐藏通道。

## 3. 本轮失败记录及修正边界

### 3.1 受限网络 TLS 查询失败

初次在默认受限网络中查询官方 API 出现 `Authentication failed`，生成了两个零字节元数据输出。之后使用捆绑 PowerShell Core 7.6.5，通过获准的只读外部网络查询与可识别 User-Agent 正常取回官方数据；使用正常 TLS，没有跳过证书校验，也没有修改全局 TLS、代理、凭据或权限。两份失败输出保留在 staging，不复制为正式来源证据。

这属于获取路径的环境失败记录，不是素材文件损坏证据；不能把第一次失败抹去，也不能据此把未经核验的下载声明为成功。

### 3.2 作者下载脚本的 FBX 签名长度错误

本轮作者自写检查脚本最初只取 18 字节，却按完整 FBX 二进制签名判断，导致已经下载的正确文件出现假失败。之后将断言改为完整 23 字节：

```text
4B-61-79-64-61-72-61-20-46-42-58-20-42-69-6E-61-72-79-20-20-00-1A-00
```

重新检查同一份下载得到 PASS；现有下载未被覆盖，Bytes / MD5 / SHA256 同时成立。修复的是验证脚本，不是原素材，更不是游戏产品逻辑。失败记录保留，不将它改写成“下载首次即全部成功”。

### 3.3 导入、读取与摆放工具的兼容修正

- `Probe-Run1`：C盘英文junction与D盘审计路径不同盘，守卫拦下；saved=[]。ROOT先解析realpath后 `Probe-Run2` 成功读取32 Actor。
- `Assets-Run1`：三张本轮新纹理已保存，但FbxFactory.import_ui不对Python导出。检查实际原生FbxFactory.cpp，改由AssetImportTask.Options传入配置；冻结失败记录与三纹理哈希，后续仅复用，不重导/覆盖。
- `Assets-Run2`：SM/M/MI三项已保存，与复用三纹理构成准确六资产；commandlet未初始化StaticMeshEditorSubsystem，末端观测失败，不改写为成功。六文件快照绑定失败与恢复证据，转为完整编辑器只读检查。
- `AssetInspect-Run1`：启动异步资源造成纹理尺寸检查失败。`AssetInspect-Run2` 实际记录等待前3×32²，执行原生 `Editor.AsyncAssetCompilationFinishAll` 后3×2048²，材质/网格/原32合同通过；saved=[]，六磁盘文件未改变，不修改异步/渲染配置。
- `Place-Run1–3`：碰撞Python枚举名称假设错误，均saved=[]。独立反射检查确认实际类型为CollisionResponseType.ECR_IGNORE，Channel公开成员带ECC前缀；隐藏通道cast被拒，不绕过。
- `Place-Run4–5`：原生SetAllChannels会使具名Profile失效为Custom，而NoCollision预设只对Visibility/Camera显式Ignore，重应用会恢复其他响应Block。改为实际NO_COLLISION＋Custom＋全部Ignore，不改全局Config，不把预设名称当作行为。
- `Place-Run6–7`：Tick能力属性蛇名未导出、原生bCanEverTick受保护不可读；不绕过，不填假False。以公开Actor/Component Tick关闭和精确原生StaticMeshActor类验证，能力字段记null/not observed，另加入五态真实运行观测。
- `Place-Run8`：Rotator位置参数顺序导致yaw守卫失败。使用显式pitch/yaw/roll构造后Place9成功。前八次均未保存地图；旧32对象未被覆盖或重建。

### 3.4 发布核验脚本的类型与数字文本兼容问题

首次执行打包前置核验在 `unscaled mesh` 抛出错误，实际退出1；此时尚未启动UAT，Package/Cook/Stage/Archive目录均未创建，UE进程为空。`Preflight-Run1/RESULT.json` 留存实际错误和现场复现：函数参数的1.0与JSON的1.0均为System.Double且数值相等，但前者受PowerShell包装后错误满足 `-is [pscustomobject]`。修复为精确运行时类型识别，未放宽数值、数组或对象字段比对。

进一步在真实PS5.1纯逻辑自测发现，手写展开小数与冷读原JSON的科学计数文本会被解析成相邻Double；将expected模板文本对齐实际冷读原表示，保留严格数值相等，不改任何UE资产或测量报告。两版helper自测与失败前核验脚本副本独立保留；它们不是游戏功能测试，不替代实际打包。

第二次前置执行已通过数值1.0检查，但负数调用参数 `-90.0` 在PowerShell参数模式中成为String，与真实Double yaw不一致而抛出严格错误；实际退出1。`Preflight-Run2/RESULT.json` 留存现场复现，使用括号表达式 `(-90.0)` 后为真实Double，不添加自动转型或放宽字符串/数字边界。此时仍未启动UAT、未创建任何包输出，游戏代码、资产与回归报告不变。

最终两份核验脚本在真实Windows PowerShell5.1.26100.9444及pwsh7.6.5各执行20项helper纯逻辑断言，共80项通过，AST/BOM正常；完整64,623字符只读打包前缀也通过，冻结输入79。失败前两版脚本、失败报告、原始自测与补测复制于 `Preflight-Tools/`；不把这些80项算入154项UE原生自动化。

## 4. 本轮发布门槛

| 门槛 | 计划要求 | 本轮实际结果 |
|---|---|---|
| 原生自动化 `Native-Run1` | 154 项、0 failed，实际编译及测试进程退出码 0，86 个源码文件哈希一致 | PASS，154/0/0，进程0，原生构建up-to-date；保留MSVC14.51偏离preferred14.50的警告，不改环境 |
| 来源导入 / 放置探测 | 实际 bounds、单位、轴向、UV、材质槽及 shader；冻结放置，原尺度，避免核心保护域与视觉遮挡 | PASS，AssetInspect2 saved=[] / Place9仅现有地图；六原始资产快照不变；见实际尺寸与视觉局限 |
| 新进程冷读 `ColdVerify-Run1` | 六精确内容包、材质连接/采样、原 32 Actor 完整合同、原木地板合同、无碰撞/阴影/活动Tick，`saved=[]` | PASS，33 Actor、原32完整、saved=[]、shader_errors=[]；受保护能力未读，非假False |
| 完整可见两轮 `VisiblePlay-Run1` | 65 流程项、35 环境项、40 截图、固定原 POV、两次真实落杖成林、开始—三幕—结束—重演 | PASS，65/35/40、forest2、实际OpenLevel1；独立五条屏风被动状态运行观测true，不添加原check计数 |
| 混音 | 两轮实际 WAV 与 Mix QA，无剪裁/非空，不替代听感人工验收 | PASS，70.677333s有声/peak.233887/非零6,488,180/0削波；61.952s静音全零（等待8s旧尾音）；非OS或听感证据 |
| 真实操纵 `ControlProbe-Run1` | 41 项、真实聚焦/控制/跨幕解除/新 E/同幕 R/EndPlay；测试过程而非纯几何断言 | PASS，41检查/8图/12实际映射/2次森林/1重演，cleanup.verified=true；正常行走1038.1177cm，非传送/物理按键证明 |
| Windows Development 独立包 | 43受控来源资产及新六包真实Cook/UFS，独立归档、不覆盖旧包，源码与验证输入哈希门控 | PASS，Package-Run1 UAT0；43资产/86源码/79证据输入；49归档文件、1,061,724,483B（另加身份JSON）；新六包实际UFS存在 |
| 实际启动首帧 | 新包实际进程、可识别首帧图像、实际退出码；不能推导包内完整通关 | PASS，FirstFrame-Run1进程0，1280×800，原生FEngineLoop::Tick.Benchmarking退出；主会实看中文标题/故事/开始和退出按钮，另存VISUAL_REVIEW.json，原RESULT不改 |
| 四条启动器 DryRun | PS5.1语法、合法入口、只读不启动、不代写验收；固定新包身份 | PASS，Launcher-Run1：Auto/Package/EditorGame/CMD实际退出均0，Auto与CMD选择固定新Package；四项均未启动游戏 |
| 最终保护 | 所有无关既有文件、旧包、旧raw、Git HEAD与暂存状态逐项复核 | 发布后由FINAL.json逐项执行；要求原287中284不变/仅批准3变化，新增精确12、总299，旧归档822/旧来源7/本轮来源8不变，HEAD与暂存不变；无实际PASS记录不得宣布交付 |

独立包：`D:\灯影山海\Builds\StageWingsDev-20261011-Run1\Windows\`，身份文件 `STAGE-WINGS-DEV-BUILD.json`。新入口：`D:\灯影山海\Start-StageWingsDev.cmd`。在资源管理器中双击cmd打开；聊天文件预览显示代码不等于执行。**最终保护未通过前不作为可体验交付文件。**原 `Start-WoodFloorDev.cmd` 及其固定旧包保持可用。

打包合同：UE5.8.3 / Win64 / Game / Development，UAT BuildCookRun 的Build→Cook→Stage→Pak+IoStore→Archive流程；显式Cook根是Env Dev地图，未用CookAll。实际UFS还包含既有默认Interaction地图和Engine Entry，不伪称归档物理上只有一个umap；这不是新增场景流程，默认配置未改。原生EXE SHA256=`5CDCC2BA470B69FFE0732349CA0CB9C93C00A7DBCE8AD56CF22D194079FFBA77`，本轮无C++变化，与旧版本相同不代表资产包相同。49实际归档文件独立冻结于ARTIFACTS.json，日志/清单/现有调试符号保留，身份绑定源与验证输入；FirstFrame/Game.log供失败定位，不重建替换测试过的候选包。

## 5. 人工与正式版本尚未关闭的项目

软件探测不代勾物理键鼠、作者人工画质、耳机/扬声器听感、首次玩家理解或最终时长。材质与模型来源可靠不代表“高质量戏台”自动成立；还需作者看到屏风原尺寸、彩绘细节、与木地板和影幕的风格协调以及不遮挡核心画面。

Codex已查看五张实际固定POV图，原WoodFloor对应机位/FOV逐项一致，记录于VISUAL_REVIEW.json。右台翼两片孔雀彩绘可见，未遮挡灯/偶/幕上林影；下部仍被原灰盒设施挡住、整体偏暗。仅通过Dev陈设摆放，不扩大/加灯弥补，不宣称正式高质量美术通过。

本轮不关闭完整幕框、帷幔几何、入场短廊、后台/台前/远景完整叙事、正式夸父形象、比赛美术与 5–8 分钟体验标准；不宣称历史复原、全剧场廉价感已消除或比赛完成。

包内人工完整三轮、最终性能和 Shipping 验收仍是独立门槛；本轮仅 Dev 陈设样本，状态结果产生后逐项填入本文，不把未执行步骤改写为 PASS。

尚未进行干净第二台电脑验收、包内完整自动/人工两轮以上通关、包内声音采集、物理键鼠自动化、Shipping或正式性能预算验收。运行首帧日志保留NVIDIA驱动592.01的TSR16-bit VALU禁用警告及本机既有TDR配置提示，未改驱动/系统/图形配置，也不据此宣布性能问题已解决。
