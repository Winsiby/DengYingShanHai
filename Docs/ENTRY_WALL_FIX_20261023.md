# 入场「隐形墙」修复（2026-10-23）

用户报告原话：「戏场外面有道隐形的『墙』，拦住我进不去」。本文记录定位、修复、验证与构建影响。

## 1. 根因（两处，均为实测确认）

| 对象 | 碰撞问题 | 位置与尺寸 | 为什么"看不见" |
| --- | --- | --- | --- |
| ART_B1_Mountain_Near_F / Near_B / Mid_F / Mid_B / Far_F / Far_B（6 张背景山影卡） | BlockAll | 以 Near_B 为例：位置 (-4800, 0, 900)，bounds (0, 900, 1300)，即 X=-4800 处横跨 Y ±900、Z -400..2200 | 单面材质，从出生点一侧看到的是背面，画面里不渲染 |
| ART_EXT_RearBase | BlockAll | 位置 (-1828, 0, 65)，bounds (18, 1230, 65)，即 2460 cm 长、130 cm 高、15 cm 厚的墙裙 | 深色石材，远看与门洞阴影混同 |

竖直剖面测试（胶囊沿 X 前进）：x=-1828 处 z=60 / 100 / 140 全部命中，只有 z≥180 能通过 —— 门洞被整段封死。

## 2. 修复

1. 6 张山影卡：静态网格组件的碰撞配置 `BlockAll` → `NoCollision`，网格与材质不动（外观零变化）。
   脚本：`Content/Python/fix_entry_wall.py`。
2. 墙裙拆成左右两段，门洞让空：
   - `ART_EXT_RearBase` 改为左段：位置 (-1828, -885, 65)，scale (0.36, 6.9, 1.3) → Y -1230..-540
   - 新增 `ART_EXT_RearBase_R`：位置 (-1828, 675, 65)，scale (0.36, 11.1, 1.3) → Y 120..1230
   - 门洞保留 Y -540..120 供通行
   脚本：`Content/Python/fix_gate_plinth.py`、`Content/Python/fix_rearbase_right.py`。
3. 保留 `M05_EntryRearGuard`（门槛石，总高 70 cm，但在该处地面之上约 8 cm，属可跨台阶），未改。

## 3. 验证

- 几何复核：`Saved/Audit-2026-10-22-FourAct/entry-open-verify.json`（11 项检查全部 ok）
  - 6 张山影卡的碰撞配置全部读回 `NoCollision`
  - 墙裙两段 Y 范围与门洞空档符合预期
  - 地面感知胶囊扫描（y=-210，x 从 -6900 到 0，每 30 cm 一步）：只剩 `DYTheater_ExtPath`、`DYTheater_GateStep`、`M05_EntryRearGuard` 三处台阶式命中，没有任何墙
- Development 实机（RunD8 打包游戏，从出生点只按 W）：`Saved/Audit-2026-10-22-FourAct/walktest/w-start.png` → `w-walk3.png` → `w-walk6.png` → `w-walk9.png` → `w-in1.png`，拼图 `Entry-Walk-In-Sheet.png`
- Shipping 实机（Run146 打包游戏）：`walktest/s146-start.png` → `s146-walk.png` → `s146-in2.png`，拼图 `Shipping-Entry-Walk.png`；第三帧已进入戏台并出现第一幕「引日启幕」提示与「走近灯架」HUD
- 自动化回归：176 项 / 0 失败 / EXIT 0，日志 `Saved/Logs/AutomationV70.log`

## 4. 构建与正式入口

| 包 | 文件数 | 字节 | 可执行文件 SHA256（前 8 位） |
| --- | --- | --- | --- |
| Development RunD8（中间包） | 49 | 1,215,052,540 | 74ecb558 |
| Development RunD9（最终） | 49 | 1,215,052,540 | 74ecb558 |
| Shipping Run145（中间包） | 31 | 856,338,919 | b15a3651 |
| Shipping Run146（最终） | 31 | 856,338,919 | b15a3651 |

地图哈希变化：`Content/DengYingShanHai/Maps/L_DY_Main.umap`
`7F26FCF6B1E5C0AAC92E3E304E2A1BA6D55691815FDDC8CE76650A3EAC308173` → `E325713B28C1097CF77B456FFA12E5F858CEE0E44472CFA5BE46D70B31B8D829`。

由于正式入口 `Scripts/Start-FormalShipping.ps1` 会校验"当前地图哈希 == 包身份里的 SourceMapSHA256"，
地图一改，Run143 的预检必然拒绝。因此：

- 已在 `Builds/FormalMain-Shipping-20261023-Run146/Windows/RELEASE-ENTRY-BUILD.json` 重签身份：
  SourceMapSHA256 = E325713B…、NativeExeSHA256 = B15A3651…、31 文件 / 856,338,919 B、GameplayVerified = true
- 启动脚本第 5–6 行已指向 Run146，`-DryRun` 结果为 `PASS-PREFLIGHT-ONLY`（31 文件 / 856,338,919 B）
- Run143 的目录与身份文件原样保留；要退回旧包，把脚本第 5–6 行改回 Run143 即可（但旧包与本机地图已不一致，预检会拒绝，属预期行为）

## 5. 踩坑记录

1. `EditorActorSubsystem.spawn_actor_from_class` 第 4 个参数是 `transient`。传 `True` 时新 Actor 不写入关卡存档，重开地图即消失 —— 右段墙裙第一次就这样"删掉"了，复查时才定位到。
2. 用编辑工具改 `.ps1` 会丢掉 UTF-8 BOM；Windows PowerShell 5.1 会把中文路径按 ANSI 读成乱码，`Test-Path` 直接说文件不存在。改完必须补回 `EF BB BF`。
3. 碰撞配置在 Python 里要用组件方法 `get_collision_profile_name()` / `set_collision_profile_name("NoCollision")`，不存在 `collision_enabled` 属性；`HitResult` 的字段要 `to_dict()` 取，`h.actor` 不可用。
4. 追踪扫描必须先向下打线测地面高度，再把胶囊放到地面之上再扫，否则所有台阶都会被误报成墙。

## 6. 未覆盖

- 只验证了中轴走廊及门洞附近四条 lane（y = -400 / -210 / 0 / 60），没有穷举从侧后方接近的所有路径。
- 台前、后台、两侧台翼是否还有类似"看不见但挡住"的碰撞体，尚未逐个排查。
- 未改任何谜题判定、灯光与演出逻辑。
- Shipping 实机只走到第一幕提示，未做整幕通关（需要真人键鼠持续操作）。
