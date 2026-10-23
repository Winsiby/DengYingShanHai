# 单柱独立可玩 Dev 样本验收

日期：2026-10-12。唯一人类作者与负责人：用户；Codex辅助实现、核查与文档整理，无队友或WorkBuddy关键路径。

## 1. 打开方式与本步边界

在文件资源管理器双击 `D:\灯影山海\Start-FramePostDev.cmd`。它默认启动固定包 `D:\灯影山海\Builds\FramePostDev-20261012-Run1\Windows`，不需要先打开编辑器，不选择“最新”包，不静默回退。旧对照入口 `D:\灯影山海\Start-StageWingsDev.cmd` 保留。`Start-FramePostAssetReview.cmd` 仍只是网格查看器，不是本次游戏入口。

新地图精确路径：`/Game/DengYingShanHai/Dev/FramePostPlacement/Maps/LV_FramePostPlacementLab`。用户选择“完整可玩样本：追加精确路径及测试”，本步只改两份现有C++：

- `Source/DengYingShanHai/Private/Core/DYDevEntryPlayerController.cpp`：追加该地图精确身份，不扩大目录/前缀授权，旧四地图与Shipping限制保持。
- `Source/DengYingShanHai/Private/Tests/DYEntryLoopAutomationTests.cpp`：新增 `DengYingShanHai.EntryLoop.FramePostExactMapIdentityAndContexts`，测试Game/原生PIE/包名PIE和错误身份；旧测试体未改。Shipping条件保留但本轮没有执行Shipping。

新地图由既有EnvironmentStatesLab模板制作，原33Actor的已列举变换、组件、主灯/轨道、流程、音频与成林合同保留，增加唯一 `DEV_FramePost_Right` 原生StaticMeshActor。33→34是作者地图对象数，不是PIE运行时生成对象总数；检查合同不声称逐个读取全部UPROPERTY。不是第二座戏台或正式新增关卡。

仅新增地图、一次性创建脚本、PS1/CMD入口和本文五项产品；只追加TECH_SPEC/DEVELOPMENT_PLAN两文档。原Config、输入/镜头、15Hz、灯偶幕、目标/保持参数、声音/脚步、跨幕解除与真实落杖成林不变。一次性创建脚本带审计与目标已存在即拒绝门，不是游戏运行依赖。

## 2. 免费来源与候选尺度

模型源为VVayToyek CC0 Chinese Four Corner Pavilion的“檐柱1”派生，未导入整亭；木纹为Poly Haven CC0 Dark Wood实得2K Diffuse/NormalDX/ARM。完整原许可、作者与文件核查指向 `FRAME_POST_ASSET_SOURCES.md`、`FRAME_POST_ASSET_VALIDATION.md`；本步不新增付费/生成资产，不把下载页历史“复原”宣传作考据，也未读取受保护的LICENSES登记文件。

原2036.121966cm高度、252三角面、384渲染顶点、UV0和两原槽保留。Dev XYZ等比 `.39290377163557627`，柱高800cm，位置约 `(950,540,0)`cm、旋转0；底座世界宽112.09cm，最近Y483.9566cm，距核心保护盒Y470边界13.96cm、距幕边Y450约33.96cm。来源尺寸、缩放与间隙见 `FRAME_POST_PLACEMENT_PLAN.md` 和审计PLACEMENT.json；8m不是正式建筑尺度承诺。

新柱Static、Actor/组件Tick关闭；Actor总碰撞仍true，组件/BodyInstance均NoCollision、公开八通道Ignore、Overlap关闭、不实现DYControllable；不投影、不影响动态间接光/距离场光照，无新BP/Director/谜题/世界扫描职责。未借Actor总开关掩盖组件碰撞，不推断32通道或所有GI/屏幕空间影响均为零。

沿用既有七资产，柱槽UV `(V,1-U)`、切线法线 `(-Ny,Nx,Nz)`，基座原UV不变；1×1方向检查不是物理纹理密度验收。整框接缝、端面/柱脚、近景和正式比例尚未完成。

## 3. 实际验证及保留的失败

本轮审计根：`D:\灯影山海\Saved\Audit-2026-10-12-FramePostPlacementDev`。结果表的数字各属不同门槛，不相加当单元测试总数。

| 门槛 | 实际结果 | 证据与界限 |
|---|---|---|
| C++ Editor Development | 原生Build退出0；155成功/0失败/0未运行 | `Native-Run1/RESULT.json`，新精确身份测试Success；未执行Shipping |
| 创建与真实图形冷读 | Create-Run2成功，只保存新地图；D3D12/SM6冷读退出0、未保存，1468审计断言 | 模板初存+最终存为同一新文件的2次保存；2203创建断言/1468冷读断言不是额外游戏测试 |
| 完整PIE流程/环境 | 65流程与35环境检查PASS，两次真实成林、一次OpenLevel重演、五态固定POV | `VisiblePlay-Run1/Result.json`、`ENVIRONMENT_RESULT.json`及五图；未改变原探针成功谓词 |
| 实际控制 | 41检查PASS，真实聚焦、灯/偶会话、R语义、跨幕/EndPlay清理和映射互斥 | `ControlProbe-Run1/RESULT.json`；含临时视线瞄准，不冒充无镜头写入或物理键盘验收 |
| 独立柱合同 | 两轮五态共10观察PASS | `VisiblePlay-Run1/FRAME_POST_RESULT.json`，与65/35分开，不改旧判据；固定机位中主影/林影未被柱遮挡的截图证据不等于审美定稿 |
| 声音回归 | 有声/静音事件一致，两轮各1接触/成林事件；静音实际播放0，WAV导出留存 | `AUDIO_RESULT.json`，旧尾音等待8秒；未证明实际扬声器输出、耳朵听感或所有移动脚步物理同步 |
| Windows Development包 | UAT实际退出0，41必需依赖、主2027/global 1个chunk原生只读payload哈希通过 | `PackageContainer-Run2/RESULT.json`、CSV、3次原生exit及日志；为读取完整性，不是GPU/运行性能 |
| 启动器 | 三次真实CMD→Windows PS5 DryRun退出0，Package默认/显式及EditorGame显式均正确，无游戏进程或新增运行目录 | `ENTRY-TESTS.json`，固定包/地图、立即取得nativeHandle、不伪造退出码；EditorGame仅诊断 |
| 真实包首帧/开始 | 中文标题→实际点击“开始复演”→真实场景、右柱/幕/偶影可见；正常关闭game/CMD均0 | `FirstFrame-Run1/RESULT.json`、Title.png/Scene.png；只验首帧与菜单开始，未完成整段包内通关 |

失败原证据不覆盖、不清理：

- API探针1–5保存0，受保护MapBuildData getter明确不可读，未绕过；改为可访问的过滤原生对象库存/外部Actor合同，不声称直接读取成功。探针6通过且保存0。
- Create-Run1用duplicate_asset后切关卡触发WorldMemoryLeaks，原生退出3，无最终地图保存；保留refchain/crash。释放源引用后使用UE原生 `new_level_from_template`，独立Create-Run2成功。只允许一新map输出，禁止旧map/BuildData/外部Actor写入。
- Package-Run1真实UAT成功，但后置检查器错误要求ZenStoreWriter生成松散umap，RESULT仍FAIL。没有重跑UAT或回写FAIL；通过原生IoStore索引、UFS路径和全部payload哈希补证。manifest时间戳不当文件存在证明，未读取或复制含认证内容的projectstore。
- PackageContainer-Run1因PowerShell自动 `$Args` 名冲突未传实参，保留原生help/exit1；Run2改任务专用参数名后3原生操作均0，哈希日志也检验，不单凭原生exit0。
- EntryTests-Run1因PS7遗留模块路径进入Windows PS5使Get-FileHash不可用而失败。R2仅CMD setlocal内设置系统PS5模块目录，并固定子进程UTF8输出；未安装模块、不改用户/系统环境。Run2三次原生DryRun通过。
- 编辑器启动日志的13条通用smoke断言保留，没有在本步处置或将原生项目155成功表述成“全部日志零错误”。首次遮挡截图显示Codex而非游戏，已弃用；刷新目标游戏窗口后才截图/点击，不作为游戏证据。

打包后的FRAME-POST-DEV-BUILD.json及50归档文件保持原字节；身份中的历史FirstFrameVerified=false不追改，后续首帧成功由独立FirstFrame-Run1补证。没有用冷读或假时间推进代替两次真实成林，没有强制结束其他UE窗口。

## 4. 发布、保护与回退

`FINAL.json` 是最后保护门：预期314原产品加5新产品=319，仅2C++和2附录文档共4个旧文件变化；旧876归档、15原始文件、18隔离来源和旧入口/原map/七柱资产逐文件保护，新包50归档固定。AFTER.json列出最终产品哈希；原HEAD `dda43f2c8970c10680173387b963d1c730649f06` 和空暂存区保持，未commit、清理或覆盖用户其他变动。技术/计划文档原字节前缀和历史失败记录保留，许可登记从收集之前就排除。

源码原件在审计 `Before/`，本步新包独立于旧包；无需删除或覆盖文件即可回退体验：打开旧 `Start-StageWingsDev.cmd`。源码回退必须再次明确授权，不以本报告自动执行撤销。新包默认启动不依赖未来源码/文档保持同一哈希；显式EditorGame需要当时有效编辑器与源产品门，不是发布版本。

## 5. 尚未关闭的里程碑与下一最小工作

本步只关闭“被动单柱独立可玩Dev样本的软件/容器/首帧门”。没有代勾作者审美、完整包内三幕/重演/三轮物理键鼠、耳朵听感、近中远纹理密度/接缝/端面、正式建筑尺度、玩家阻挡、GPU预算、完整幕框/帷幕、空间叙事、首次玩家5–8分钟盲测或Shipping。

下一最小工作由用户负责作品判断、Codex辅助：先以此入口检查候选构图和实际玩法下的柱材质，再做下一免费幕框构件/布质台翼的独立准入与样本。不能顺带移动旧灰盒、修改主灯/镜头/谜题，不能把一根柱升级成完整剧院或把素材许可当质量认证。依旧遵守“永远不要以牺牲架构设计为代价追求功能；永远不要基于猜测进行权衡——必须与我确认”，无每日排期与隐含团队成员。
