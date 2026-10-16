# 单柱Dev资产｜实际验证与未关闭门槛

2026-10-12。唯一人类作者与负责人：用户；Codex辅助实施/验证。状态为 **Dev资产准入，不是新的可玩场景或正式美术完成**。最终发布/保护以本轮审计FINAL.json为准。

审计根：`D:\灯影山海\Saved\Audit-2026-10-12-FramePostAsset`。UE5.8.3 CL58210709，Win64；原项目、C++、Config、地图、灯偶/镜头、输入、15Hz、声音/脚步、跨幕解除及落杖成林未改。不重编译C++或Cook，不把旧154/65/35/41等结果改称本轮重测。

## 1. 实际执行与失败留证

| 层级/记录 | 实际结果 | 证明范围 |
|---|---|---|
| FRAME_POST_INDEPENDENT_REVIEW-RUN2.json | 96项独立源核对PASS | 原FBX→一柱派生字节/轴/单位/法线/UV/槽位；不是UE或画质 |
| FRAME_POST_UV_DIRECTION_REVIEW.json | 实读64侧面长轴边/64侧面三角面方向 | 柱身长轴对应V；基座不同，不盲目全模型转UV |
| FRAME_POST_MATERIAL_STATIC_REVIEW-RUN2.json | 51静态AST＋1108纯数学PASS | 脚本图结构和UV/法线逆基底数学；不是GPU/帧率 |
| probe-Run1 | 1351检查，退出0，保存0 | 实际全Editor API/源/目的不存在 |
| create-Run1 | 707检查后失败，进程0但runner1，保存0 | ComponentMask单输入pin不能使用猜测“Input”名称；按原生API改为空名 |
| create-Run2 | 771检查后失败，进程0但runner1，保存0 | 检查器误以为GetInputs只返已连接pin；实际含null输入，修正检查器 |
| create-Run3 | 1490检查，退出0，保存7 | 七份新Dev资产已实际创建/持久化 |
| verify-Run1（真实RHI） | 1395检查，退出0，保存0/重导入0 | 独立冷读、D3D12/SM6、实际槽/纹理/图/尺寸及编译接口 |
| 原生查看器会话 | 实际打开Mesh Editor，纹理可见，正常退出0 | 在实际D3D12查看器看见纵向连续木纹与柱脚，不是剧场画质签收 |
| FRAME_POST_RUN3_READONLY_REVIEW.json | 22项独立只读PASS | 七资产/脚本SHA/原生启动错误发生顺序与接口边界 |

1351/1490/1395等是实际脚本断言数，包含逐文件保护，不是游戏自动化用例数量。不覆盖旧失败日志，不能只凭UnrealEditor退出0判断Python任务成功，runner同时检查Result.success。

创建导入使用原生FbxFactory、uniform_scale=1、convert_scene/convert_scene_unit=true，ImportNormals，combine_meshes=true；不自动碰撞、LightmapUV、Nanite、材质或纹理生成。临时子进程Interchange.FBX开关恢复，未写Config/全局设置；精确7新资产白名单、replace_existing=false/save=false后，先完成检查，再单独保存自己的资产。

## 2. 资产依赖、参数与可见结果

资产目录 `/Game/DengYingShanHai/Dev/FramePostAsset/`：

```text
Meshes/SM_DY_FramePost_Source
  → Materials/MI_DY_FramePost_Wood（原槽0）
  → Materials/MI_DY_FramePost_Base（原槽1）
      → Materials/M_DY_FramePost_Master
          → Textures/T_DY_FramePost_BaseColor
          → Textures/T_DY_FramePost_NormalDX
          → Textures/T_DY_FramePost_ARM
```

没有新Actor、Blueprint运行逻辑、Director/Stage状态依赖、Tick、Timer、全局MPC或第二流程所有者；当前地图没有引用这七资产，不影响旧包Cook依赖。实际252tri/384render vertex/1LOD/1UV/2section，无simple collision、Nanite或mesh distance-field生成选项。

材质选择有界木材父＋常量实例，不做万能Master、Layers/Substrate/透明/WPO/RVT。Surface/Opaque/DefaultLit、单面、切线Normal；延续项目r.Substrate=0/Deferred、真实会话D3D12 SM6。颜色sRGB，NormalDX线性NormalMap，ARM线性Masks；采样UV→颜色/ARM通道→正常法线逆基底→PBR输出。

`UVQuarterTurn`只有0、1两个受支持端点（基座0/柱身1），不是连续艺术旋钮：中间Lerp会改变向量长度。侧面采样(V,1-U)、切线normal(-Ny,Nx,Nz)保持已实读UV0基底；基座原UV0。当前tiling=1×1，Specular=.5；没加任意增亮/饱和/Emissive或全局渲染开关。以后贴图密度需实测独立参数，不能用提升平铺任意掩盖尺度。

实际Computer Use查看原生Mesh Editor：纵向连续木纹、柱脚、两个实例和真实252面/384顶点/2036cm字段可见，截图为 `UE_FRAME_POST_PREVIEW.png`；仅点击/聚焦/拉远/放大窗口，不点击保存/重导入，不运行PIE。屏幕背景是UE内置查看器环境，不是本项目正式剧场或新素材来源。画面为AI技术观察，不代替作者审美验收。查看后七asset哈希与OWN-ASSETS一致。

## 3. 日志缺口，不能夸大验收

FullEditor启动时仍有13条LogAutomationTest“Condition failed”；probe（资产尚不存在）、create和真实RHI verify都有，发生在InitializingEngine与本Python执行之前。原生LaunchEngineLoop启动RunSmokeTests，LowLevelTestAdapter CHECK只输出通用消息，本Python执行器须Engine/World/AssetRegistry准备后才运行。不是主资产脚本节点/保存错误，但没有testname/callstack，不能逐条确定全部根因。

中文本地化是有证据的根因候选：实际zh-CN/zh-Hans与原UnifiedError测试的硬编码英文FText比较不一致，但11条比较不能证明13条全部由它产生。本轮不为此改产品或系统语言，不宣布“全日志零错误”。独立源码位置/上下文保存在只读审查报告。

首次查看器的原生SharedProfiles自动保存意外产生58,482B Config/DefaultEditor.ini（基线不存在，仅AdvancedPreviewScene.SharedProfiles）。发布前精确文件集合护栏因此中止，尚未写任何产品文档；核实源代码与哈希后将这一新文件可恢复地移到Audit/UnexpectedViewerConfig-Run1，不删除、不覆盖作者配置。后续查看子进程加原生 `-nowrite`：ConfigCacheIni的AreWritesAllowedGlobally/WriteInternal检查该flag，SharedProfiles的TryUpdateDefaultConfigFile→UpdateSections→WriteInternal走同一出口。只限制这一UE进程的配置落盘，未改Windows权限/安全或全局设置。最终需在关闭后的实测中再次确认Config仍是原三文件，而非仅凭参数名宣布通过。

入口预发布独立审查发现WindowsPS5把无BOM中文路径读成乱码；发布时机械加UTF8 BOM，再用原生PS5/CMD实测，不用pwsh7结果替代。正常入口强制运行已发布助手并绑定AFTER哈希，七资产固定唯一名称并交叉AFTER；PreviewTest明确只是开发验收门，最终正常DryRun也要通过。首次FINDINGS报告保留，不改成假PASS。

原生PS5首轮DryRun又实际发现ConvertFrom-Json数组输出差异：额外使用@(...)使整个7项JSON数组成为1个元素，误触exact7门。实读WrappedCount=1/DirectCount=7，改用直接赋值；本轮两次启动均在进程创建前停止（exit1），没有打开UE或写Config。只修正新查看助手，不改七份已通过资产/游戏，保留发布初版与故障记录；最终以ENTRY-PS5-DRYRUN.json、发布路径新真实查看会话、ENTRY-NORMAL-DRYRUN.json为准。

跨轮查看会话review-20261012-013239-8661在用户Esc中断后恢复观察并正常关闭；实际Result成功、UE日志Exiting、Config仍原三文件，但PS5的Start-Process重定向+PassThru在WaitForExit后取得null退出码，父助手因此exit1。原EXIT/null保留，不追认0。独立42个良性已装cmd子进程诊断（7方式×exit0/7×3）实证带重定向且不保持Handle的6/6为null；立即读取Process.Handle后6/6正确返回0/7。新助手最小修复为Start-Process返回后保持原生Handle，并一次采集退出码、显式拒绝null，不强转int。最终查看器是否通过仍须看修复后新会话的非null实际退出码，不用42项诊断代验UE。

FBX导入另有“No smoothing group”告警。原法线与ImportNormals已核查，查看器柱身可渲染；并未完成所有切线/绿通道、硬边、端面/柱脚近景与多光向验收，告警保留。MEL.recompile_material在没有平台MaterialResource时也可返回空数组，因此NullRHI的[]不证明GPU编译；追加真实RHI与实际纹理查看，也不等于Shader Complexity/Overdraw/VRAM/GPU毫秒预算已通过。

## 4. 如何打开，不要把脚本当游戏

在Windows文件资源管理器中双击 `D:\灯影山海\Start-FramePostAssetReview.cmd`，先正常关闭已有UE/游戏窗口。新入口只打开原生静态网格查看器；不按E、不启动三幕。若Codex内点击只显示代码，请复制上述绝对路径去资源管理器打开。已有UE窗口时入口会提示并停止，不强杀任何进程。

鼠标点查看器三维视口后按F聚焦，可滚轮缩放查看柱身；只观察，不点“保存”“重新导入”、不改右侧属性。查看完关闭网格子窗口，再正常退出UE主窗口；右下“正在执行Python脚本”是keep-alive查看模式，并非下载/编译卡住。入口此会话的预览/配置偏好不写盘；它不是通用UE开发启动器。可玩仍用 `D:\灯影山海\Start-StageWingsDev.cmd`，旧固定包完全不变。本阶段没有新游戏包。

## 5. 回退、保护与下一实际门槛

旧游戏不依赖新资产，无需回退源码/地图；继续打开旧入口即可。新增家族/查看器与本记录独立，原三个Docs已备份至本Audit/Before；不自动删除来源、失败或产品，不操作Git提交/暂存/清理。许可证登记文件明确排除在枚举后的哈希读取范围之外。

发布前后核对301份产品：只允许TECH_SPEC/DEVELOPMENT_PLAN/STAGE_FRAME_ASSET_REVIEW三份文档变化；新七资产、三查看器文件及两记录，共12新产品文件。其余298份既有产品、876份旧包、15旧来源、18隔离来源和已冻结7资产应逐文件相符；最终数量/结果只认FINAL.json。

尚未关闭：源20.36m柱件的最终比例与横向位置、框顶承托/接缝、端面和柱脚材质、物理纹理密度、近中远真实光照、固定POV的五态非遮挡、主灯光锥/林影保护、Shader Complexity/Overdraw/显存/GPU，以及显式地图Cook后新Development包/实际启动。先冻结尺寸和摆放方案，再写独立Dev构图样本；不缩放幕布、改主灯/镜头或顺便清理旧灰盒设施，不用更亮灯光补偿资产问题。

完整帷幕/戏台、正式夸父文化形象、5–8分钟首次玩家、三轮打包通关/Shipping、第二电脑和参赛成品仍未完成。本步不安排固定每日计划，不增加制作成员或付费资源。
