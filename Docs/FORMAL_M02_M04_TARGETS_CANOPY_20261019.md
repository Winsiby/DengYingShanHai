# 正式舞台 M-02 P03 目标影形与 M-04 A v04 叶簇接入

> 后续状态（2026-10-19）：Run6 已补齐独立 Development 包内三轮程序接口三幕/接触成林/同图重演，正式入口现固定 Run6。详见 FORMAL_PACKAGED_FLOW_20261019.md。本文以下保留首次 Run5 集成证据；实体键鼠、Shipping、盲测、性能与最终美术仍待验。

日期：2026-10-19。负责人：用户；Codex 执行导入、装配、验证、打包和入口更新。

## 结果

按用户确认的方向，P01/P03 评估 M-02 目标影形，P02 保留 B 身体角标；M-04 选 A v04 椭叶密簇，作为枝端叶簇。实测后 P03 目标可用；P01 新目标与当前影子构图不匹配，保留原校准角标。

## M-02：P03 使用，P01 保留

- 资产：`/Game/DengYingShanHai/Dev/StageTargetsM02/Meshes/SM_DY_Target_P03`
- 材质：`M_DY_Target_Ink`、`M_DY_Target_Sun`（unlit、双面、无新贴图）
- P03 Guide 改为该目标网格，Actor 位于 `(923.5, 0, 0)`、缩放 1；网格本地坐标已包含目标屏幕位置。
- P02 继续使用 `MI_DY_P02KuafuBodyFit` 和原 `(923.5,0,350)` 缩放 `(0.008,9,8)`。
- P01 的 M-02 目标实际比当前影子更大且偏中，直接替换会错位；因此恢复原 `Readability_GuideP01` 的 Cube/`MI_DYReadability_P01` 校准。P01/P02 目标资产保留为独立候选，不影响正式图。
- 目标网格无碰撞、不投影；三组 Guide 的显示/隐藏逻辑不变。

## M-04：A v04 枝端叶簇

- 资产：`/Game/DengYingShanHai/Dev/ForestCanopyM04/Meshes/SM_DY_M04_Canopy_A_v04`
- 材质：`MI_DY_M04_CanopyWood`、`MI_DY_M04_CanopyLeaf`，常量 PBR，无新贴图。
- 在正式森林 `M3_RuntimeForest` 的枝号 `9,10,11,12,13` 挂 5 个叶簇，`CanopyWorldScale=0.9`；15 段 `BranchLayout`、接触点、生长时序和原 BranchMesh 未改。
- C++ `ADYForestPresentationActor` 新增可选 `CanopyMesh`、`CanopyBranches`、`CanopyWorldScale`；叶簇在 Progress >0.55 后出现并从 5% 长到全尺寸，随对应枝条可见性隐藏/显示，可见时投真实阴影。
- 叶簇组件与枝组件分离，`GetBranchMeshComponents` 仍只返回 15 段枝，原有的结束门控和测试契约不变。

## 实际验证

| 项 | 结果 |
|---|---|
| 冷读 | 51 Actor；P01 原 Guide、P02 B、P03 M02 目标、森林 5 枝端叶簇与 15 段布局逐项通过 |
| M-02 实图 | P03 目标环位于地线/落杖区；P01 新目标实测错位，已恢复原 Guide |
| M-04 实图 | `M04-Play-Run2` 最终林影可见 5 个叶簇；仍为风格化树枝，不是写实森林 |
| 三幕 PIE | 15 项通过：P01 禁用、P02 灯偶协同、27/27 E 区域、P02 重置、P03 接触成林、同图重演 |
| 原生回归 | 169 成功、3 警告、0 失败、0 未运行；3 个警告均为网络/EOS 连接，不是逻辑失败 |
| Development 包 | `Builds/FormalMain-Development-20261019-Run5/Windows`；UAT 0；49 产物、1,081,732,973 字节；UFS 含 P03 目标、M04 叶簇/材质、M03 幕框和主图 |
| 正式入口 | 已切 Run5；实际启动、菜单显示、日志载入 `L_DY_Main`、正常退出 0 |

关键证据：

- `Saved/Audit-2026-10-19-FormalKuafu/M02-Capture-Run3/`
- `Saved/Audit-2026-10-19-FormalKuafu/M04-Play-Run2/PLAY.json`
- `Saved/Audit-2026-10-19-FormalKuafu/M02M04-Verify-Run1/VERIFY.json`
- `Saved/Audit-2026-10-19-FormalKuafu/M04-NativeTests-Run1/index.json`
- `Saved/Audit-2026-10-19-FormalKuafu/Package-Run5/Smoke-PrintWindow-Run1/Packaged-Menu-PrintWindow.png`
- `Saved/Audit-2026-10-19-FormalKuafu/OfficialEntry-Run5/RESULT.json`

## 来源

- M-02 ZIP SHA256 `CCC53335AF985F802A1593B8490EDB6CD6ED9B76BF395BCFA03DC51D77B65964`
- M-04 A v04 ZIP SHA256 `F19A417ECF2B8DCFCE760BC5351CF13AE4634A6563B043490664D5ABE5996F6C`
- 原始完整包 SHA256 `92F23491AD1A3ADB0704225AF59EA029AE8570501D4B6F6392308D9809A3DDB7`

## 回退

- `M02-Baseline/L_DY_Main.umap` 保存 M-02 接入前主图。
- `M04-Baseline/L_DY_Main.umap` 保存 M-04 接入前主图。
- 旧 `FormalMain-Development-20261019-Run4` 包保留；M-02/M-04 新资产可保留但不再引用。
- 森林 C++ 回退需恢复 `DYForestPresentationActor.h/.cpp` 的对应改动并重建 Editor/Game；先核查后续用户/队友修改。

## 边界

- P01 M-02 目标未采用，原因有实际 PIE 截图；不是所有 M-02 目标都自动通过。
- M-04 只在 5 个枝端挂叶簇，原枝仍是 Cylinder 占位，整体仍是风格化林影，不是写实树林；若要更密需要继续调叶簇数量/尺寸或替换枝网格。
- 包内已验证启动、菜单和退出；三幕完整流程在真实 RHI PIE 中通过，未在包内重复整段三幕。
- 未验证实体键鼠全流程、Shipping、目标机性能、5–8 分钟盲测和最终美术签收。
