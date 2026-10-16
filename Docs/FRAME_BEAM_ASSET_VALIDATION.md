# 横梁Dev资产｜实际验收与查看入口

2026-10-12。唯一人类作者：用户；Codex辅助。状态只覆盖独立资产准入，不是新可玩版本或完整幕框。

## 1. 如何打开

文件资源管理器中双击 `D:\灯影山海\Start-FrameBeamAssetReview.cmd`。聊天链接若只显示代码，请到该目录双击CMD。它打开UE原生网格查看器，不进入游戏、不按E、不摆放或缩放模型。需要先正常关闭已有UE/游戏；入口不会强杀进程。

点三维视口后按F可完整聚焦，滚轮缩放观察；只查看，不点保存、重新导入或修改属性。右下“正在执行Python脚本”是查看会话保持机制，不是下载/编译卡死。查看后正常关闭资产子窗口和UE主窗口。查看器场景背景为引擎内置预览环境，不是新游戏场景。

实际资产：`D:\灯影山海\Content\DengYingShanHai\Dev\FrameBeamAsset\Meshes\SM_DY_FrameBeam_Source.uasset`。UE内容路径 `/Game/DengYingShanHai/Dev/FrameBeamAsset/Meshes/SM_DY_FrameBeam_Source`。当前可玩仍打开 `D:\灯影山海\Start-FramePostDev.cmd`，旧包/地图/源码/输入/镜头/灯光/声音保持。

## 2. 实际数据与最小架构

原生FbxFactory、ImportNormals、uniform_scale=1/场景单位转换，只保存这一新StaticMesh。实际2630.546631×111.114189×142.727215cm、长轴UE X、origin `(0,0,28.636393)`cm；一LOD、28tri/48render vertices/1UV/1section/原“额枋”槽。源16顶点是拆分前数据，未重造几何或修改轴心。26.31m是源尺寸，不是正式戏台尺度。

网格→原常量木材MI→原父材质→原三纹理；无Actor/BP、Director通信、状态、Tick/Timer/Subsystem、运行时动态MI、保存进度或网络复制。还没有地图引用、Cook包含或新包。将来单个摆放采用原生StaticMeshActor，须单独冻结实际碰撞/投影/间接影响与core保护盒，不从资源“无simple collision”推断玩家阻挡或全部渲染隔离。

复用Surface/Opaque/DefaultLit单面木材族，r.Substrate=0；V-long UV采用原QuarterTurn=1及法线逆基底。旧五依赖SHA和当前源纹理解释保留，不启用新透明、WPO、MPC、Emissive或补光。查看中长向木纹/完整梁形可见；没有代签端头/纹理物理密度、近中远舞台光照、接缝或性能。

## 3. 门槛与失败证据

审计 `D:\灯影山海\Saved\Audit-2026-10-12-FrameBeamAsset`。

| 检查 | 实际结果 | 范围 |
|---|---|---|
| 源/派生独立比对 | 256节点原属性字节与允许差异核对PASS | 自有二进制扫描器，不执行主派生脚本；不是UE/艺术验收 |
| probe-Run1 | 1447检查、保存0、实际退出0 | 可用原生API/材质依赖/319旧产品保护 |
| create-Run1 | 1464检查、仅保存1新网格、实际退出0 | 没有地图/材质/纹理或Actor生成 |
| verify-Run1 | 1457检查、真实D3D12/SM6、保存0、实际退出0 | 新mesh/旧依赖真实冷读、尺寸/轴/槽/UV/字节保护 |
| 原生查看会话 | 真正打开网格编辑器，近景木纹与F聚焦全梁截图留存 | 预发布辅助通道，不冒充普通CMD完整交互/游戏或作者审美 |
| 入口发布 | 精确1mesh+唯一5依赖、SHA与AFTER绑定，PS5中文BOM/模块局部隔离 | 正常CMD DryRun、修正验证与GUI非null退出另认本轮实际补充证据 |

上述1447/1464/1457及50894为数据/资产/文件断言，不是游戏测试数量。本轮不重编译C++、不重跑旧155/65/35/41、不Cook或重建旧包；旧结果不改称本轮重测。

保留失败/中断：

- 独立比对Run1把分类计数163当Objects总数，遗漏Null NodeAttribute，实际164。属检查器错误；修正以新Run2验原/派生字节，未改模型、未覆盖FAIL。
- Prepare首次在来源manifest收集把一个FileInfo当数组相加而失败；此前仅写Saved备份与来源，没有产品变更。只补清单，原BEFORE/失败脚本保留，PREPARE-RECOVERY.json核对319旧产品不变。
- 帷幕检查器首次把.blend当未压缩BLENDER头而拒绝；实际Zstandard封装，保留Run1检查脚本，修正仅承认编码、不解码或猜UV/材质。
- 入口预审发现仅count=5不能排除重复依赖，发布前加入精确路径集合与唯一性；不靠此修复重导入资产。修正前GUI的实际脚本指纹不追改，后续补证分开。
- 预览中用户Esc停止Computer Use，立即停止输入；用户“继续”后刷新窗口状态。关闭主编辑器一度被安全检查阻止，不绕过、不强杀；只在获明确授权或用户自行关闭后确认真实EXIT，窗口关闭以补充记录为准。
- 原生启动仍有13条通用smoke断言，导入保留无smoothing-group警告；没有足够根因栈，不宣布全日志零错误。ImportNormals/原法线字节核对不等于所有硬边、端头与光向都合格。

关闭补证：用户明确允许正常关闭本轮PID35684，刷新并置前实际UE窗口后才发送Alt+F4。原生EXIT实际0、Handle在Wait前保持，日志为UUnrealEdEngine::CloseEditor→Editor shut down→Exiting，结束后UE/游戏进程为空，未强杀。一次被遮挡的捕获显示Codex，已弃用且未对其发送输入；CIM元数据读取被拒，没有提权或改权限。源近景/完整梁两张未编辑截图保留。校验修订的9个实际Python谓词隔离用例、7个原生PS5谓词隔离用例通过，未用伪造游戏或修改真实DEPENDENCIES做负例；普通CMD的最终只读预检另见FINAL_POST_GATE.json，不把预发布GUI追称为普通CMD整段测试。

## 4. 保护、回退与尚未关闭项

最终以 `FINAL.json`、`AFTER.json`、入口补充门为准：319旧产品只允许TECH_SPEC/DEVELOPMENT_PLAN两份原字节前缀保留的附录变化，新7产品为1网格、3查看器文件和3记录。其余317旧产品、926旧归档、15旧来源、18已冻结柱来源、6新隔离来源和新mesh/五依赖逐文件保护；原HEAD与空暂存区保持，无Git写入、清理、文件删除或旧包重建。中断与早期FAIL留证，不追改历史null退出码。

无需回退游戏，继续旧 `Start-FramePostDev.cmd` 即可。横梁无运行引用，不把删除新文件当默认回退。

尚未关闭：梁与柱/幕的等比接合、端头与柱顶缝、净口、纹理物理密度、主灯投影保护、近中远舞台画质、GPU预算、帷幕、正式建筑尺度/全剧场叙事、首次玩家5–8分钟、完整包内三轮/Shipping。下一步只先计算几个bounds/等比接合候选，必要设计权衡与作者确认后再冻结独立Dev摆放，完整玩法/音频/包回归另行执行。
