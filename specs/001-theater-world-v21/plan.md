# 实施计划：V2.1 剧场世界重构（P0）

**Spec**: `specs/001-theater-world-v21/spec.md`
**Branch**: `001-theater-world-v21`
**日期**: 2026-10-20 ｜ **工期**: 至 2026-10-20 23:59

## 技术上下文

- 引擎：UE 5.8（`D:\灯影山海\DengYingShanHai.uproject`），Windows x64，C++ + Blueprint
- 正式图：`/Game/DengYingShanHai/Maps/L_DY_Main`（`GameDefaultMap`）
- 隔离图：`/Game/DengYingShanHai/Dev/WorldV2/Maps/LV_DY_TheaterWorld_Preview`（新建）
- 菜单：`Source/DengYingShanHai/Private/UI/DYDevEntryWidget.cpp` + `DYDevEntryPlayerController.cpp`（视觉冻结）
- 表现层：`BP_DYStagePresentation` 既有阶段事件；新增 `BP_DY_ExteriorReaction` 仅订阅
- 构建：`C:\dy_build\rebuild.cmd`（复制源码→UBT→回填 DLL）
- 打包：`Saved/Audit-2026-10-19-FormalShipping/Package-Shipping.ps1`（UAT BuildCookRun，Shipping）
- 既有基线：Shipping Run3（31 产物 / 733,971,876 字节 / NativeExe SHA256 `C8CA8F56…`）

## 宪法校验

| 条款 | 落实方式 |
|---|---|
| 单一主图 | 只在 `L_DY_Main` 收口；开发期在 `Dev/WorldV2` 隔离 |
| 三幕不变 | 不改 Director、容差、保持时长；扩景仅在外围加 Actor |
| 判定/视觉分离 | 枯树反馈只读阶段事件，不参与判定 |
| 菜单冻结 | 只加逻辑分支与面板，不改布局常量 |
| 可回退 | 每阶段写 `BASELINE.md` 增量 + 地图副本 + git 分支 |
| 真机证据 | 每阶段输出截图/日志到 `Saved/Audit-2026-10-20-V21/` |

## 目录与命名

```text
Content/DengYingShanHai/
  Dev/WorldV2/Maps/LV_DY_TheaterWorld_Preview.umap
  Dev/WorldV2/BP/BP_DY_ExteriorReaction.uasset      # 可选
  Art/WorldV2/Theater/  Forest/  Village/  Materials/
ExternalAssetStaging/                                # 项目外暂存，不入库
Saved/Audit-2026-10-20-V21/                          # 证据
```

## 实施阶段

### 阶段 0 · 基线与回退（30 min）
- 记录 `git status`、`L_DY_Main.umap` SHA256、关键 Actor 包围盒；生成 `Docs/BASELINE-V21.md`。
- 复制 `L_DY_Main.umap` 到 `Saved/Audit-2026-10-20-V21/backup/`；建本地分支 `codex/v21-theater-world`。

### 阶段 1 · 入口闭环（2–3 h，最高风险）
- `DYDevEntryWidget`：接"继续/篇章/说明/设置"四项；设置面板复用现有说明牌样式。
- `L_DY_Main`：冷启动先出菜单，开始 → P01；Esc 暂停 → 回菜单；继续 → 恢复会话。
- 验收：冷启动→P01→P02 截图；Esc→菜单→继续 截图。

### 阶段 2 · 剧场外壳（4–5 h）
- 隔离图摆剧场：台口加高、柱梁、观众席台阶、侧幕、后台、入口大厅。
- 只以"包围盒外包"方式生长，不改谜题 Actor。
- 验收：三张固定机位截图（观众席后区 / 台口内望 / 门外外望）。

### 阶段 3 · 外景世界（4–5 h）
- 地面 + 路径 + 2–4 栋中式轮廓房屋 + 树/石/草 + SkyAtmosphere/体积云/雾 + 远山。
- 先 A 圈真实，B 圈体块，C 圈远景平面。
- 验收：两张"门内望外 / 外望剧场"截图；无黑边、无地面截断。

### 阶段 4 · 成林反馈（1–2 h）
- `BP_DY_ExteriorReaction` 订阅 P03 完成事件 → 门外枯树换材质/换 Mesh + 风动。
- 验收：成林前后对比截图；重演回初始态。

### 阶段 5 · 合并、回归、打包（3–4 h）
- 合并进 `L_DY_Main`；跑三幕回归；出 Shipping 包并实测。
- 验收：包内一次通关录屏 + `LAUNCH-VERIFY.json`。

## 风险与降级

| 风险 | 概率 | 降级 |
|---|---|---|
| 菜单接入主图破坏既有开局流程 | 中 | 菜单作为独立 HUD 层叠加，不接管 Director；失败则退化为"启动即 P01 + 片区按钮" |
| 外景体量拖垮帧率 | 高 | A 圈保真，B/C 圈去碰撞、去动态光、合并静态网格 |
| KayKit 导入失败 | 中 | 45 分钟止损，改 UE 原生几何 + 现有材质 |
| 剧场外壳穿帮遮挡主灯投影 | 中 | 外壳只做三面，台口上方留空；先测主灯投影再定墙高 |
