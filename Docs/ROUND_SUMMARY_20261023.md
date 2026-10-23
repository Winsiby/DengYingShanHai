# 本轮收尾清单（2026-10-23）

## 已完成

| # | 事项 | 结果 |
| --- | --- | --- |
| 1 | 美术第 3/4/5 条（刑天剪影、烛龙比例、精卫翼杆） | Run4 重建：刑天姿态基准偏移、烛龙头 ×1.18、支杆改短藏进翼皮，三份 MODEL_VERIFICATION 全 PASS |
| 2 | 影偶换偶接入正式四幕 | C++ `ApplyChapterFigure` + 独立 CastMesh（Movable），四条 DA entry，yaw 180 / scale 0.8+1.1×3 |
| 3 | 幕上题签按幕切换 | M_DY_TitleGlyph_Master + MI_Act1..4 + 三张新纹理，`ApplyChapterTitlePlaque` 接线，6/6 回读通过 |
| 4 | cook 漏资产（RunD1–D6 全中招） | DefaultGame.ini 增加两条 DirectoriesToAlwaysCook，cook 包数 720→767 |
| 5 | Development 包 | RunD7：49 文件 / 1,215,052,540 B，实机四幕换偶+题签已拍 |
| 6 | Shipping 包 | Run144：31 文件 / 856,338,919 B，实机拍到第二、三幕新影偶 |
| 7 | 自动化回归 | 176 项 / 0 失败 / EXIT 0（AutomationV69.log） |
| 8 | 文档与台账 | FOURACT_CAST §7–10、ART_AUDIT §6–7、THREE_PUPPETS §10、README、ASSET_LIST SELF-012、ART_BACKLOG C1 更新 |
| 9 | Run4 交付包 | DY_ThreePuppets_20261022_Run4.zip：119 文件 / 441,460,493 B / SHA256 ab02513b…9ad3 |

## 证据图

- `Saved/Audit-2026-10-22-FourAct/Packaged-Acts234.png`：Development RunD7 实机，第二/三/四幕题签与影偶同框
- `Saved/Audit-2026-10-22-FourAct/Shipping144-Acts.png`：Shipping Run144 实机，第二幕精卫、第三幕刑天
- `Saved/Audit-2026-10-22-FourAct/Final-Act1..4.png`：编辑器内四幕成片

## 需要人工/拍板

1. 四幕完整通关（键盘焦点被系统弹窗与自动化抢走，脚本只能进菜单/选幕，走不完全程）。
2. 公开入口 `Scripts/Start-FormalShipping.ps1` 仍指向 Run143；是否切到 Run144 属部署决定。
3. Builds 下 RunD1–RunD6 缺新资产（不可用于演示），是否删掉由用户定。

## 未变（截至 10:40）

- 正式地图 `L_DY_Main.umap` SHA256 `7F26FCF6…C308173` 当时未变；公开入口 `-DryRun` 仍 PASS（31 文件 / 754,095,567 B）。

## 补充：入场「隐形墙」修复（10:40–11:05，已推翻上面的"地图未变"）

用户 m02507 报告「戏场外面有道隐形的墙，拦住我进不去」。定位到两处碰撞，均已修复并实机验证：

1. 6 张背景山影卡（`ART_B1_Mountain_*`）是 BlockAll + 单面材质，从出生点一侧看不见，却在 X=-4800 处横跨整条走廊 → 改成 NoCollision。
2. `ART_EXT_RearBase` 的 2460 cm 长、130 cm 高墙裙横穿门洞 → 拆成左右两段，门洞 Y -540..120 让空。

- 地图哈希：`7F26FCF6…` → `E325713B28C1097C…B31B8D829`
- 新包：Development `RunD9`（49 文件 / 1,215,052,540 B）、Shipping `Run146`（31 文件 / 856,338,919 B）
- 正式入口已改指 `Run146` 并重签 `RELEASE-ENTRY-BUILD.json`，`-DryRun` = PASS-PREFLIGHT-ONLY（31 文件 / 856,338,919 B）；Run143 目录与身份原样保留
- 实机证据：`Saved/Audit-2026-10-22-FourAct/Shipping-Entry-Walk.png`、`Entry-Walk-In-Sheet.png`
- 自动化：176 项 / 0 失败（`Saved/Logs/AutomationV70.log`）
- 详见 `Docs/ENTRY_WALL_FIX_20261023.md`

## 补充：动态皮影演出系统（12:30–17:40）

按 `DYS_SHADOW_PUPPET_GAMEPLAY_UPGRADE_20261023.md` 落地"解谜成功 → 关节反馈 → 整幕连续演出 → 再推进"：

| 项 | 结果 |
| --- | --- |
| 动画 | Blender 程序化生成 17 条表演片段（夸父 6 / 精卫 4 / 刑天 5 / 烛龙 4），导入 `Puppets/Animations/A_DY_*_Perf_*` |
| 数据 | `DA_DYPuppetPerformance`：四幕各 5 段 + 1 反馈 + 字幕，12.0 / 12.4 / 12.2 / 12.6 s |
| C++ | `UDYPuppetPerformanceComponent`（播段/反馈/跳过/进度）、`ADYPuzzleDirector` 延迟发布通知、`Space` 跳过 |
| 回归事故 | 组件里固定路径回落加载 DA，自动化夹具也随之启用 → 8 个流程测试失败；改为实例显式挂接后 `AutomationV71.log` 180/0 |
| Development | `RunD10`：56 文件 / 1,215,421,639 B，日志连续三章演出（12.00 s / 12.40 s 播完）、空格 3.79 s 跳过、`feedback beat` 反复触发 |
| Shipping | `Run147`：31 文件 / 856,412,694 B，公开入口已改指 Run147，`-DryRun` = PASS-PREFLIGHT-ONLY |
| 证据 | `Saved/Audit-2026-10-23-Performance/`：PerfUE-Act1..4.png、Packaged/RunD10-Captions.png、Packaged/Shipping147-Captions.png、Packaged/Shipping145-Skip.png、Packaged/RunD10-performance.log |
| 文档 | 新增 `Docs/SHADOW_PERF_20261023.md`；FOURACT §11、ASSET_LIST SELF-013、本文件 |
| 交付包 | `Assets/Sources/DengYingArt/ThreePuppets-20261022/DY_Performance_20261023.zip`：131 文件 / 38,118,228 B / SHA256 8E965B75…EFDD |
