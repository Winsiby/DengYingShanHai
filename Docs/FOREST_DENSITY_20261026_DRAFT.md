> 当前来源更新（2026-10-26）：宽冠已定稿为60×240×100cm并由Forest-Apply保存至候选主地图；8冠、两项新UE资产及新Leaf已经按SELF-011登记。当前清单见 [FOREST-ASSET-SOURCES-FINAL.json](D:/灯影山海/Saved/ForestDensity-2026-10-26/Attempt1/FOREST-ASSET-SOURCES-FINAL.json)。下文保留首次150cm宽阶段记录，涉及“尚未采用/拟SELF-011”的句子仅反映初始进度，不代表最新状态。包内流程、林影画面及正式入口仍待验。

# 灯影山海林影加密交付草稿

**状态：源模型与FBX回读、修改前证据、冠根偏移修复及自动测试已核实；尚未纳入最终UE导入/地图保存、候选打包、包内林影与公开入口验收。本文不是Run172发布通过记录。**

任务日期2026-10-26；候选沿用 `FormalMain-Development-20261026-RunD15` 和 `FormalMain-Shipping-20261026-Run172`。唯一人类作者与最终责任人为用户，Codex作为程序建模、脚本与核查辅助工具，不列为制作成员。

本轮目标是增强“弃杖化林”的冠叶密度与枝端衔接，仍在同一主地图表现链内完成。约定地图范围只有 `M3_RuntimeForest` 的冠配置；15项 `BranchLayout`、主判定、时长、相机、灯光和已验收大门保持原范围。最终不变项须由保存后的对照证据确认，不能仅凭约定判为已通过。

## 源模型与复用来源

[MODEL.json](D:/灯影山海/Saved/ForestDensity-2026-10-26/Attempt1/Source/MODEL.json)记录本地确定性程序几何：3136个Blender源顶点、5076三角形、60×150×100cm、Wood/Leaf两槽。源网格内部有44段枝、15个不规则叶簇和240片实体叶；这些数字不是运行时Actor数量，也不是场景15项BranchLayout。根原点为零、底部Z为零，几何没有烘焙世界偏移。

- [ForestCrownDense.blend](D:/灯影山海/Saved/ForestDensity-2026-10-26/Attempt1/Source/ForestCrownDense.blend)：原生可编辑源。
- [SM_DY_ForestCrown_Dense_v1.fbx](D:/灯影山海/Saved/ForestDensity-2026-10-26/Attempt1/Source/SM_DY_ForestCrown_Dense_v1.fbx)：本地导出交换文件，Blender导出后回读尺寸通过。
- [Build-Forest-Crown.py](D:/灯影山海/Saved/ForestDensity-2026-10-26/Attempt1/Tools/Build-Forest-Crown.py)：实际生成与导出脚本，seed=20261026；没有第三方模型/贴图导入。
- [FOREST-ASSET-SOURCES-DRAFT.json](D:/灯影山海/Saved/ForestDensity-2026-10-26/Attempt1/FOREST-ASSET-SOURCES-DRAFT.json)：上述文件字节数与SHA256。本次实读的blend/FBX哈希均与原MODEL一致；源顶点数不替代UE渲染顶点实读。

拟导入目录为 `/Game/DengYingShanHai/Stage/ForestDensity_20261026`，不覆盖旧 `Dev/ForestCanopyM04`。拟复用 `MI_DY_M04_CanopyWood` / `MI_DY_M04_CanopyLeaf`；[20261019接入记录](D:/灯影山海/Docs/FORMAL_M02_M04_TARGETS_CANOPY_20261019.md)明确两者为常量PBR、无新贴图。本轮没有新增下载、付费模型/贴图或运行时在线服务。若最终采用新的深绿色本地常量材质，应补其实际名称/节点来源和资产哈希；目前只记为待确认方案，不写为已采用。

来源登记拟使用下一个 `SELF-011`；正式LICENSES/ASSET_SOURCES的“实际采用”条目待最终接入路径确定后追加，当前不把拟用资源写成已发布。AI补记见 [AI-USAGE-FOREST.md](D:/灯影山海/Saved/ForestDensity-2026-10-26/Attempt1/AI-USAGE-FOREST.md)，既有Word/PDF未改。

## 冠根偏移修复及现有验证

[Before-PIE.json](D:/灯影山海/Saved/ForestDensity-2026-10-26/Attempt1/Before-PIE.json)记录一次实际PIE接触/生长取样，`ok=true`、`saved=false`，15枝、5冠；五个冠根相对对应实际枝尖均偏移X=-40cm。这份修改前诊断不是新树冠或修改后美术通过证据。

`DYForestPresentationActor.cpp`仅把冠位置从 `TipWorld + BaseOffset + WorldOffset` 改为 `TipWorld + BaseOffset`，因为TipWorld已经来自加过WorldOffset的枝组件。枝组件本身的WorldOffset计算保留。对应测试 `CanopyAnchorsApplyWorldOffsetOnce` 使用(-40,17,5)非零XYZ偏移，检查0.8/1.0生长时冠根贴枝尖、可见且投影，重置后冠/枝清理；测试用Engine Cube验证锚点，不代表新网格美术验收。

[Editor-Build.log](D:/灯影山海/Saved/ForestDensity-2026-10-26/Attempt1/Editor-Build.log)尾部显示 `Result: Succeeded`。[Automation-RunD15/RESULT.json](D:/灯影山海/Saved/ForestDensity-2026-10-26/Attempt1/Automation-RunD15/RESULT.json)记录实际exit0、187成功/0失败，同时明确不覆盖实体输入或打包流程。

| 验收项 | 本草稿已核事实与待项 |
| --- | --- |
| 源与交换文件 | 源文件齐、哈希吻合、Blender FBX回读通过；UE最终导入计数/槽/材质实读待补 |
| 代码/自动逻辑 | 一行冠定位修复与新增测试已对照；187/0，actual exit0 |
| 地图与不变项 | 修改前冷读1809 Actor、15项BranchLayout已存；最终冠配置与白名单保存对照待补 |
| Development / Shipping | RunD15 / Run172独立打包、输入前后相等与产物身份待完成 |
| 候选流程 | 本轮包自己的FullFlow/SkipFlow、Replay和原生exit0待完成，不借用Run171 |
| 林影画面 | 修改前图已存；新包同阶段密度、枝冠贴合、落杖到林影连续性前后对照待完成 |
| 正式入口 | 仍以Run171为历史已验基线；Run172候选尚未据此发布，实际CMD烟测待完成 |

## 回退与证据边界

修改前地图、C++、测试和启动脚本保存在 [本轮Backup目录](D:/灯影山海/Saved/ForestDensity-2026-10-26/Attempt1/Backup)。基线地图SHA256为 `771ED81572B5DC05C784E0C66D1E610898F29EAC8F2DC466095AB67B1BCD9877`，基线正式脚本SHA256为 `DB07C8FE04CB57C4589022D756FB352103001037D1DE4FE0C7E40505A9861699`。这些是变更前身份，不冒充修改后的地图哈希。

如需回退，应先保全本轮当前文件，再精确恢复本轮备份的地图与两份源码；旧M04网格/材质未覆盖，新目录保持可审查，不能使用全仓reset/clean。地图/代码回退之后仍须匹配重建包和完整性守卫，不能直接让旧包运行不匹配输入。这里只记录回退方法，没有执行回退。

[Run171门楼交付](D:/灯影山海/Docs/GATE_REPAIR_20261025.md)与其所有原始JSON保持历史，不修改或借作本轮通过证据。本轮交接由 [Forest CURRENT-HANDOFF.json](D:/灯影山海/Saved/ForestDensity-2026-10-26/Attempt1/CURRENT-HANDOFF.json)独立维护。早先两次DevD13 CSV Profile退出777003仍未解决；本轮不据此宣称性能验收，也不宣称独立人测或全面美术已完成。
