# 正式夸父 M-01 v04 掌垫/木杖接入记录

日期：2026-10-19。负责人：用户；Codex 执行本轮导入、接入、验证、打包和入口更新。

> 后续状态：M-03 完整幕框、M-02 P03 目标影形与 M-04 A v04 枝端叶簇已在该记录之后接入，正式包与入口现为 Run5。本文保留为 M-01 接入记录，当前状态见 `Docs/FORMAL_M02_M04_TARGETS_CANOPY_20261019.md`。

## 结果

正式 `BP_DYKuafuPuppet_Fitted` 的 `KuafuMesh` 已换为 M-01 v04 角色网格，`Staff` 已换为同包木杖。正式主地图 `L_DY_Main` 不需要改：实例直接从 Blueprint 继承新网格。木杖 A/B 端点、灯偶轨道、三幕参数、15 Hz、E 交互区和森林因果链均未改。

## 新资产

- 角色：`/Game/DengYingShanHai/Dev/KuafuAppearance/Puppet/SK_DY_Kuafu_M01_LeftGrip_v04`
- 木杖：`/Game/DengYingShanHai/Dev/KuafuAppearance/Meshes/SM_DY_Kuafu_Staff_M01_v04`
- Blueprint：`/Game/DengYingShanHai/Dev/KuafuAppearance/Presentation/BP_DYKuafuPuppet_Fitted`

角色沿用原 `SK_DY_Kuafu_Puppet_Skeleton`（20 骨），6 个原材质槽顺序不变；UE 导入后 45,540 顶点、6 个 section。木杖 1,615 顶点、2,976 三角面，局部包围仍为 ±50 cm，木杖材质仍为 `MI_DY_Kuafu_Staff_Wood`。

M-01 源包记录：掌片 840 顶点、1,676 三角面；三姿态掌片/杖余隙约 4.06 / 0.92 / 4.47 mm，363 次姿态采样无交叉；这是“短宽钝圆掌垫”候选，不是零间隙贴杖完成稿。

来源包：`D:\灯影山海\Saved\Audit-2026-10-19-FormalKuafu\ResourceIntake-StaticCandidates\Extracted\DY_M01_Kuafu_PalmHeel_v04`；原始 7z SHA256 `92F23491AD1A3ADB0704225AF59EA029AE8570501D4B6F6392308D9809A3DDB7`，M-01 ZIP SHA256 `66BBA5C9AF737910D89EF91D5F805EB0D13EF23F817FDE7D763F0A9F9701793A`。该包沿用项目既有夸父源与木杖材质，没有新增付费或外部资产。

## 实际验证

| 项 | 结果 |
|---|---|
| 导入 | 新角色/木杖只新增两个 Dev 资产；角色使用原骨骼，六槽材质重新绑定原 MI |
| Blueprint | 只改 `KuafuMesh` 和 `Staff` 两个组件模板；编译保存成功；主地图无改动 |
| 木杖几何 | 替换前后 A=`(600, -101.05118, 161.29312)`、B=`(600, -148.94882, 308.70688)`，逐值一致；局部包围 ±50 |
| 三幕 PIE | 15 项检查通过：P01 禁用、P02 灯偶协同、27/27 E 区域、P02 重置、P03 接触成林、同图重演 |
| 近景 | `M01-HandCapture-Run1` 四张 UE 实际 PIE 图；正面/侧面可见短宽掌片包住杖身，杖从掌后通过 |
| 原生回归 | 170 成功、2 警告、0 失败、0 未运行；夸父装配测试已改为 M-01 v04 身份 |
| Development 包 | `Builds/FormalMain-Development-20261019-Run3/Windows`；UAT 退出 0；49 个产物、1,081,221,393 字节；UFS 含新角色、新木杖和更新后的 BP |
| 包内启动 | 正式 CMD 实际启动、菜单清晰、日志载入 `L_DY_Main`、正常退出 0 |

关键证据：

- `Saved/Audit-2026-10-19-FormalKuafu/M01-Import-Run2/IMPORT.json`
- `Saved/Audit-2026-10-19-FormalKuafu/M01-Apply-Run1/APPLY.json`
- `Saved/Audit-2026-10-19-FormalKuafu/M01-Play-Run1/PLAY.json`
- `Saved/Audit-2026-10-19-FormalKuafu/M01-HandCapture-Run1/CAPTURE.json` 与四张 PNG
- `Saved/Audit-2026-10-19-FormalKuafu/M01-NativeTests-Run1/index.json`

## 正式入口

`D:\灯影山海\Start-ReleaseEntry.cmd` → `Scripts\Start-FormalMain.ps1`，已切换到：

`D:\灯影山海\Builds\FormalMain-Development-20261019-Run3\Windows`

旧 Run2 包保留为回退。正式入口实际启动、菜单显示和正常退出 0 已复核。

## 回退

`Saved/Audit-2026-10-19-FormalKuafu/M01-Baseline/` 保存接入前的 `BP_DYKuafuPuppet_Fitted.uasset` 和 `L_DY_Main.umap`。回退时先核查后续用户/队友修改，再恢复 BP；新角色/木杖资产可保留但不再被引用。旧 `FormalMain-Development-20261019-Run2` 包可直接用于回退比较。

## 边界

- 掌片仍是项目原有板片式低多边形手型；短宽钝圆已改善，但未达到写实交握或三姿态零间隙。
- 新增掌片有较密圆角拓扑和小三角面；本轮未做专门低模预算优化或生产级 UV 重排。
- PIE 三幕与 E 采样使用原生语义入口/直接控制值；包内已验证启动、菜单和退出，未在包内重复整段三幕。
- 未验证实体键鼠全流程、Shipping、目标机性能、5–8 分钟盲测和最终美术签收。
