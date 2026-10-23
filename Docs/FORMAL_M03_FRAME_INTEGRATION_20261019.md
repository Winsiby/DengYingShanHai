# 正式舞台 M-03 v02 完整幕框接入记录

日期：2026-10-19。负责人：用户；Codex 执行导入、装配、验证、打包和入口更新。

> 后续状态：M-02 P03 目标影形与 M-04 A v04 枝端叶簇已在该记录之后接入，正式包与入口现为 Run5。当前舞台/目标/林冠状态见 `Docs/FORMAL_M02_M04_TARGETS_CANOPY_20261019.md`。

## 结果

正式主图 `L_DY_Main` 已替换旧的右柱/右梁占位，装配 M-03 v02 的 18 件完整幕框：左右柱、柱头、角撑、卷轴支架、轴颈、拉绳、挂钩、顶梁、顶轨、上卷轴和下配重。舞台现在从玩家 POV 是一个完整木框，而不是“一根梁加一根柱”。

## 空间对齐

- 幕框按 CSV/模块清单的世界厘米坐标装配，整体加 `X=950` 对齐主幕平面。
- 原幕网格中心 `Z=350`、范围 `Z-50..750`；M-03 净开口为 `Y±450 / Z24..824`。为了让幕面真正填满开口，只把 `DEV_BackScreen` 上移到 `Z=424`，保持 `X=950 / Y=0` 和 `(0.5,9,8)` 缩放。
- 三组角标 `Readability_GuideP01/P02/P03` 仍保持 `Z=350`，影子投影平面未移动；`M03-GuideDiagnostic-Run1` 确认 B 身体角标仍与影子对齐。
- 18 件保守包围盒均不侵入 900×800 净开口；旧 `DEV_FramePost_Right`、`DEV_FrameBeam_RightJoint` 已删除。

## 资产与材质

- 网格：`/Game/DengYingShanHai/Dev/StageFrameM03/Meshes/SM_DY_Frame*`（18 件）
- 木材 MI：`MI_DY_M03_FrameWood`，复用 `M_DY_FramePost_Master`，`UVQuarterTurn=0`；避免对已烘入四分之一转的柱身再转一次。
- 底座：复用 `MI_DY_FramePost_Base`。
- 金属/绳：`M_DY_M03_FrameConstantPBR` + `MI_DY_M03_FrameIron` / `MI_DY_M03_FrameRope`，常量 PBR，无新贴图。
- 18 件 FBX 的实际上传槽以 FBX 为准；柱/梁/卷轴为木材，支架/轴/钩为铁，拉绳为绳材质。FBX 未实际携带第二个底座槽，底座 MI 保留为后续可替换槽位。
- 幕框全部 `NO_COLLISION`、不投影、无动态间接光/距离场，保持原占位的运行时边界；净开口和玩家路线不被碰撞阻挡。

## 实际验证

| 项 | 结果 |
|---|---|
| 冷读 | 51 Actor；旧占位消失；18 件位置、网格、材质、包围盒逐项通过；开口无侵入 |
| 幕面 | `DEV_BackScreen` 在 `Z424`，实际包围 `Z24..824`、`Y±450`；三组 Guide 仍在 Z350 |
| Director/Stage | 灯、偶、Stage、Forest、StaffProjectionScreen、NarrativeGroundLine 绑定全部保留 |
| 三幕 PIE | 15 项通过：P01 禁用、P02 灯偶协同、27/27 E 区域、P02 重置、P03 接触成林、同图重演 |
| 视觉 | `M03-Play-Run1` 与 `M03-GuideDiagnostic-Run1` 实图确认完整木框、幕面填满开口、B 角标对影 |
| 原生回归 | 170 成功、2 警告、0 失败、0 未运行 |
| Development 包 | `Builds/FormalMain-Development-20261019-Run4/Windows`；UAT 0；49 个产物、1,081,500,006 字节；UFS 含全部 M03 网格/材质和主图，不含旧 FramePost/Beam 占位 |
| 正式入口 | `Start-ReleaseEntry.cmd` 已切 Run4；实际启动、菜单显示、日志载入 `L_DY_Main`、正常退出 0 |

关键证据：

- `Saved/Audit-2026-10-19-FormalKuafu/M03-Author-Run3/AUTHOR.json`
- `Saved/Audit-2026-10-19-FormalKuafu/M03-Verify-Run2/VERIFY.json`
- `Saved/Audit-2026-10-19-FormalKuafu/M03-Play-Run1/PLAY.json`
- `Saved/Audit-2026-10-19-FormalKuafu/M03-GuideDiagnostic-Run1/P02_GuideOnly.png`
- `Saved/Audit-2026-10-19-FormalKuafu/Package-Run4/Smoke-PrintWindow-Run1/Packaged-Menu-PrintWindow.png`
- `Saved/Audit-2026-10-19-FormalKuafu/OfficialEntry-Run4/RESULT.json`

## 来源

M-03 v02 来自 `D:\灯影山海\Saved\Audit-2026-10-19-FormalKuafu\ResourceIntake-StaticCandidates\Extracted\DY_Frame_M03_Cue_v02`。原始 7z SHA256 `92F23491AD1A3ADB0704225AF59EA029AE8570501D4B6F6392308D9809A3DDB7`；M-03 ZIP SHA256 `BBC5765D681FBFF229D001F9BAD881D48BA28EA613B25342716011EBCED85D8F`。柱体上游 CC0、木材 Poly Haven CC0，详见包内 README 与来源记录。

## 回退

`Saved/Audit-2026-10-19-FormalKuafu/M03-Baseline/L_DY_Main.umap` 是接入前主图；旧 `FormalMain-Development-20261019-Run3` 包保留。回退前先核查后续用户/队友修改；M03 新资产可保留但不再被主图引用。

## 边界

- 幕框是静态视觉构造，不代表卷轴可运动、绳索可承重或木构连接可制造；轴孔/间隙不是机械公差。
- 为保持原玩法和性能，18 件全部无碰撞、无投影；若后续需要碰撞或幕框阴影，需另立验收。
- 包内已验证启动、菜单和退出；三幕完整流程在真实 RHI PIE 中通过，未在包内重复整段三幕。
- 未验证实体键鼠全流程、Shipping、目标机性能、5–8 分钟盲测和最终美术签收。
