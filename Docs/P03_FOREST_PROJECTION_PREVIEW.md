# P03 同根真实树形投影样本（无时长 Dev 取证）

日期：2026-10-04
状态：**技术取证通过；构图待优化；正式演出未完成。本文件不是正式第三幕完成，也不是可玩 P03 完成。**
负责人：Codex 负责实现、实机取证与技术验收；WorkBuddy 仅整理事实文档。
依据：`AGENTS.md`、`TECH_SPEC.md`、`P03_DEV_IMPLEMENTATION_PLAN.md`、
`P03_DROP_COMPOSITION_PREVIEW.md`、`P03_STAFF_CONTACT_VALIDATION.md`、`LICENSES.md`，
以及本机 `Saved/Audit-2026-10-04-P03ForestPreview/` 内 `Execution-Contract.md`、
`Supervisor-Results.md`、`Verification-Run2.json`、`EngineAssetSource.json`、
`ProductScopeAudit.json`、`ImportAndTopologyChecks.json`、四份运行日志及最终`Verification-Run4.json`。

> *永远不要以牺牲架构设计为代价追求功能；永远不要基于猜测进行权衡——必须与我确认。*

---

## 1. 用户确认与本轮定位

- 用户此前确认 **A 端 ＋ 幕上叙事地线**，并选择**真实树形几何投影**方向。
- 本轮用户确认 **高位地线：幕布底部以上 15%，本灰盒幕上世界 Z = 70**。
  **用户不再需要选择地线**——该项已确认，不再作为待决项。
- 本轮只做**无时长静态样本**：从同一次真实 Resolve 起点采样原姿态、落杖中点、
  真实接触、枝干半展开、全展开，并加一张「全展开但关闭树形投影」的诊断对照。
- **这不是正式连续落杖动画，不是参赛高质量画面，不是用户视觉验收，不是 P03 可玩完成。**
- 未扩展场景、输入、玩法、镜头、资产采购或团队关键路径。

## 2. 六张原图（Run2）

全部为实际 PIE 玩家视口 `HighResShot`，1600×900，**无 HUD**，未合成或编辑，
分目录保存、**不覆盖**。路径与 SHA-256 见 `Verification-Run2.json`：

| 序 | 文件 | 字节 | 含义 |
|---|---|---|---|
| 01 | `Run2/01-Start.png` | 883,649 | 原姿态（真实 Resolve 起点） |
| 02 | `Run2/02-Drop50.png` | 875,790 | 落杖中点（归一化 50%，无接触、无树） |
| 03 | `Run2/03-Contact.png` | 872,335 | 真实接触成立 |
| 04 | `Run2/04-Tree50.png` | 871,182 | 枝干半展开（可见 4 段） |
| 05 | `Run2/05-Tree100.png` | 880,591 | 全展开（10 段） |
| 06 | `Run2/06-Tree100-NoTreeShadow.png` | 873,433 | 全展开、仅 `CastShadow=false` 的诊断对照 |

**对照图的证据意义**：05 与 06 的实际枝段端点与组件变换**完全相同**，仅树形
`CastShadow` 不同；结果是对应的**幕上枝影消失**，而实体树形仍在。
因此**不是材质贴图**，也**不是靠隐藏实体制造的假原因**。

Codex 已查看全部六张原图；独立复查者另检查了接触、半展开、全展开与投影关闭四张，
并复算六张 SHA-256 一致。**不把静态图片称为本轮正式第三幕验收。**

## 3. 真实接触根与投影（关键事实）

`Verification-Run2.json` 的 `accepted_contact` 实录：

| 项 | 实测值 |
|---|---|
| 事件 | `ContactAccepted`（原生，非 Python 伪造） |
| Token | `2301949944D6949461E27FA33E94ECE9`（Run2 **内部接触与Resolve相同**；不同运行Token不相同） |
| 实体 A（真实组件） | `(600.0, 18.713764, 128.208955)` |
| 幕上投影根 | `(925.0, -11.156213, 70.0)` |
| 投影倍率（射线参数） | `1.3201970443349753` |
| 连通边数 | **10**（单根连通图） |
| 样本宽度 / 可用高度占比 | `0.48` / `0.62` |
| `native_contact` / `source_is_actual_A` | `true` / `true` |
| `formal_art_approved` | **`false`** |

**必须区分两个坐标**：
- **幕上根 `(925, -11.156213, 70)`** 是幕布接收面上的**投影点**；
- **实体根 `(600, 18.713764, 128.208955)`** 是后台的**实体 A 端**。

树根取 `contact.Projection.Staff.EndAWorld`（**实体 A**），
**不取**幕上的 `ContactWorldPosition`。**幕上投影点不能直接拿来当幕后几何生成点。**

- 枝干是一组**以实际实体 A 为唯一源的连通图**（`ImportAndTopologyChecks.json`：
  `connected_root_count = 1`、`branch_count = 10`、`parent_before_child = true`），
  **不是多个凭空出现的根点**。
- 枝段尺寸使用真实网格 bounds 与实际组件变换复核，原生 `ProjectPointToScreen` 逐端验证。
- 原生中心射线证明**根点映射**，截图与树 `cast_shadow` 对照证明**可见投影**，**二者不能互相替代**。

## 4. 因果守卫与完整清理

`Verification-Run2.json`、实际运行日志与`ImportAndTopologyChecks.json`联合验证：

| 事件 | 结果 |
|---|---|
| 落杖 0% / 50% | 日志记录**无接触、无树**；导入/拓扑静态检查`ImportAndTopologyChecks.json`另有`no_growth_before_drop_endpoint = true` |
| 落杖 100% | **一次接触之后**才允许树展开 |
| 重复接触请求 | **拒绝** |
| 清理 | `full_staff_restored = true`、`stale_token_rejected = true` |
| Editor | `editor_exited = true`，`Completed(error = null)` |
| 枝段实体验证 | **24 次**（4 + 10 + 10），**48 个端点检查** |

> **计数口径必须准确**：24 是**枝段实体验证次数**（含 48 个端点检查），
> **不是 24 个独立自动化测试**。本轮**没有新增 Automation 测试套件**
> （`new_automation_suite = false`）。

**每一次修改与截图前后都校验**：Token、Staff、灯/偶根、发光点、幕布变换与边界、地线、实际 POV。
结束时**显式恢复完整 Staff 变换**、还原临时引用、销毁**仅本会话**创建的 Editor Actors。

## 5. 夹具来源：不是新 P03 参数

`Verification-Run2.json` 的 `fixture` 实录：

| 项 | 值 |
|---|---|
| 谜题 | **`P02_ChaseForm`**（沿用既有 P02 沙盒） |
| 灯目标 / 偶目标 | **0.72 / 0.80** |
| Holding | **1.25 s** |
| 评估频率 | **15 Hz** |
| `invented_p03_parameters` | **`false`** |

**这些是 P02 既有夹具值，沿用为取证条件，不是本轮批准的 P03 目标/容差。**
本轮**未设置任何新的 P03 目标、容差、落杖时长、生长时长或超时数字**，
也**未绑定任何时长**——0% / 50% / 100% 是**归一化位移采样**，不是动画时长或谜题评分。

## 6. 杖 / 灯 / 幕 / POV / FOV 保护

- 实际 Staff **只做平移**：不改旋转、缩放，不改灯/偶 Actor 根、主灯或幕布。
- 起始位置来自 live Resolve 的真实 Staff 世界变换；**不用固定预制成功姿态替换最终构图**。
- PIE POV = `(-1260, -155, 178.150002)`、**FOV 70**，所有取证前后保持。
  **没有新相机、没有 Camera Cut、没有改最终 POV 所有权。**
- 主灯为既有 Movable Spot：`Lumens 42000`（原有 Resolve 反馈）、半径 `2200cm`、
  `SourceRadius 4cm`、内/外角 `20/38`、`CastShadows = true`。
  `adjusted = false`——**不是本轮建议的新强度**。
- 曝光保持既有 Manual 锁定（`Bias 3.5`、`physical camera exposure = true`），**本步未调灯/曝光/材质**。
- 渲染器沿用既有 **DX12/SM6 + Lumen/VSM，硬件光追关闭**（启动日志佐证，不仅依赖脚本自报）。
- **没有 GPU/帧率测量，不宣称性能通过**（`fps_measured = false`）。

## 7. Run1 失败与修正（失败证据保留）

Run1 在**接触已由原生 `TryAccept` 返回 true 之后**，停止在一个 Python `FGuid` wrapper 比较断言上。
Run2 改用 `GUID.to_string` 值相等 + Director 原生当前 Token 守卫。

- **源码与原生接触判定未改**——本轮修正的是**测试断言的写法**。
- Run2 实际 `has_contact = true`，同轮contact_token与resolve_token均为`2301949944D6949461E27FA33E94ECE9`；Run1独立Resolve Token为`D7A6C0F2428056687F0286A8E2076DF8`，**不是跨轮相同**。
- `Preview-Run1.log` 与 `Run1/` 目录**保留**，未覆盖为「从未出错」的证据。
- `Verification-Run2.json` 由独立脚本 `Verify-ForestPreview.py` 读取日志与 PNG 头/SHA 独立确认。

**本轮既有噪声仍在**：`Preview-Run2.log` 仍有 **13 条**本地化 smoke-test
`Condition failed` Error 与 **1 条** NVIDIA TSR 驱动兼容 Warning。
**Run2 无诊断失败，不等于整日志零 Error。** 本轮不改驱动或配置。

## 8. 视觉不足（必须如实记录，构图待优化）

Codex 与独立复查者对六张原图的结论——**技术成立，画面不成立**：

1. **裸枝稀疏**——不是正式桃林；
2. **主干与夸父轮廓中央重叠**，根部因中央重叠**不够醒目**；
3. **实体与影子形成双线**，实际影子有明显**锯齿**。

因此该样本**不能**定为参赛高质量画面，**不能**称用户视觉验收完成，
**不能**称连续生长动画完成。**构图待优化。**

## 9. 文件保护与工具分工

- 文档写入**前**的范围审计（`ProductScopeAudit.json`）：
  **134 旧产品文件 → 133 相同 / 1 改变 / 0 缺失**，**仅新增 1 个脚本**。
- **唯一改变的原产品文件**：`Scripts/Preview-P03StaffDrop.py`
  （获准复用，**只加 `__main__` 保护与 2 个默认保持原行为的 hook**；修改前原文在 `Backup/Scripts`）。
- **唯一新增产品脚本**：`Scripts/Preview-P03ForestProjection.py`
  （派生自既有诊断基类，**不复制玩法判断**）。
- **Source / Content / Config / .uproject / 旧启动入口零变化**；本轮**不保存**地图/BP/材质/Definition，
  **未保存新的游戏资产**。所有树形几何、地线与标记**只在编辑器内存中创建**。
- **最终哈希由Codex交付复查后生成**：134旧文件131相同/3白名单改变/0缺失；新增2个产品文件，总136。精确逐文件记录见`ProductScopeAudit.json`；不包含Saved生成证据。
- WorkBuddy文档交接请求首次粘贴审核被数据披露策略拒绝，**未执行**；用户随后明确授权该具体负载后正常审核通过并实际粘贴/发送。
  **没有绕过审核。** 本轮独立 UE 启动审核通过；**此前额度阻塞是历史**。
- 已卸载的 Computer Use **未启用**，`STOP` 保持；原生 PowerShell 仅用于截图与交接，
  **不改模型、不改权限模式**。**不删除文件、不做 Git 写操作。**

## 10. 未完成项

- 建议的对照构图 **「同根更早分叉、两侧展开、中央留空」是建议且待用户确认，未实施**。
  本轮**不自行批准**节奏、终态或重启策略。
- **未保存**地线关卡实例、Forest 表现资产、正式落杖编排与连续生长动画。
- **未实现/未完成**：P03 Definition 与目标/容差、Finale 结束态、三幕队列、Skip、
  统一整局重启、两种新环境态、正式美术与声音、玩家 GUI 手动通关、
  新 Windows 包与性能验证。
- **本轮未重跑**旧 48 项 Automation、**未重新编译**、**未 Cook/Stage/Package**。
  旧 **48 Success** 与三目标编译是**历史回归基线**。
- **`Start-M3Geometry.cmd` 旧启动入口不包含本样本**——**不谎称双击即可玩到森林**。
- 正式美术资产许可与登记仍待完成（见 `LICENSES.md` 本轮追加的引擎灰盒登记）。

## 11. 状态

**部分完成**：同根（单一实体 A 源）真实树形几何在既有 Movable 主灯下的**真实投影静态样本**已取证，
因果守卫与完整清理已验证；**构图待优化，正式演出未完成**。
本文件不构成正式第三幕、参赛作品或用户验收结论，**未代签任何人工确认**。

AI 使用记录：Codex负责脚本实现、四次独立Editor执行（Run1/Run3诊断失败、Run2/Run4取证成功）、原图复查与范围审计；WorkBuddy整理初稿，Codex最终纠正Token、材质、字段出处并恢复历史前缀。**不冒充已完成赛事AI申报。**

## 12. 最终补检 Run3 / Run4 与文档复核

- Run3为严格材质来源补检：Cylinder默认材质并非预期BasicShapeMaterial，名称断言失败，自动还原并退出；没有保存资产、没有改游戏材质。失败日志保留。
- Run4不猜名称，而是读取真实Engine路径：Cylinder.Cylinder与EngineMaterials/DefaultMaterial.DefaultMaterial；实际材质文件34,943B与SHA见`LICENSES.md` §9.2及`EngineAssetSource.json`。
- Run4再次完成6张原生1600×900PIE截图、24次枝段实体验证（48端点）、1接触/重复拒绝及清理/旧Token拒绝；`Completed(error=null)`，正常Editor退出。新的树投影关闭帧**只改CastShadow，完全不重写几何变换**，与全展开图是严格对照。
- 最新原图在审计`Run4/`，名称与Run2同序但不覆盖历史；精确尺寸、SHA与实际Token见`Verification-Run4.json`。本节不把Run2 Token冒充Run4 Token。
- Run4同样存在13既有Error/1TSR Warning，无GPU预算、连续动画、打包或人工通关结论；视觉重叠/稀疏/双线/锯齿仍未解决，技术完成不是正式视觉完成。
- WorkBuddy原稿在`WorkBuddy-Output/`保留。Codex将两个旧Docs恢复到`Backup/Docs`完整历史前缀，本轮只在末尾追加，不覆盖历史。恢复仅限白名单文档，没有Git写操作。

## 13. 后续对照更新（2026-10-04，由 WorkBuddy 追加）

> **本文件 §1–§12 全部内容为同根几何投影样本轮的历史记录，保持原样、不被擦除或改写。**
> §10 中「早分叉/两侧展开/中央留空是建议且待用户确认，未实施」是**当时的历史事实**——
> **该建议已于本轮获用户批准并实施**（用户回复「按照你的想法来」）。
> 本节只**追加**对照结果，**不重写上述历史**。

### 本轮已完成

- 取得 **6 张 1600×900 无 HUD 真实 PIE 原图**（`Saved/Audit-2026-10-04-P03ForestComposition/Run2/`），未编辑图片；旧对照 `Audit-2026-10-04-P03ForestPreview/Run4/` **未被覆盖**。
- **9 边单根连通**拓扑（短根→低位左右→两侧上行→四个枝尖），`no_central_upright = true`；半展开 5 段、全展开 9 段、投影关闭对照 9 段。
- **23 次枝实体验证 / 46 个实际中心线端点 / 184 个实际 Cylinder bounds 投影角检查**——**不是 23 个 Automation 测试**。
- 角色保护框取**真实 Torso/Head 各 8 角**共 16 角投影；诊断 padding 仅局部 Y/Z 各 2.0；`gameplay_tolerance_changed = false`。
- 1 次真实原生接触（本 Run2 Token `5DB65B1C49D07D57CF6E9B96E93C6CC8`，contact/resolve 同值、`native_token_current = true`）、1 次完整 Staff 变换恢复与旧 Token 拒绝、`Completed(error = null)`。
- 视觉上中央重叠**减少**、角色轮廓更清楚、低位同根连接可追溯。

### 仍未完成 / 仍不成立

- **不是**最终成林构图，**不是**用户视觉验收，**不是** P03 可玩完成，**不是**正式第三幕完成。**U 形框/支架感、裸枝稀疏、实体影子双线、锯齿仍在。**
- **本 Run2 Token 只对本 Run2 有效**，不与旧 Run4 或本 Run1 混写。
- **体积理想射线包络留空不等于 VSM 像素 / 半影 / POV 遮挡已全部解决。**
- `sample_width_fraction = .48` 是**构图坐标基准**，**不得写成实测树宽 48%**。
- 未保存任何资产（`saved_assets = false`）；未实现正式连续动画、Forest Actor、P03 参数与容差、正式秒数、Finale、三幕队列、Skip、统一整局重启、两种新环境态、正式美术声音、新 Windows 包与性能验证。
- Run1 在**进入 PIE 前**被输出路径守卫拒绝（`RuntimeError: Evidence output must stay within this composition audit`）；**未放宽守卫**，只修正 Saved 启动脚本输出路径，失败日志保留。
- 本轮**未编译 / 未 Cook / 未 Stage / 未 Package**、**无新 C++ Automation**；历史 48 Success 仅为历史基线。日志仍有 **13 条**既有 Error 与 **1 条** TSR Warning——**不等于整日志零 Error**。
- 资产沿用**已登记**的 Engine Cylinder 与实际 DefaultMaterial，未下载新资产、未付费。
- 旧 `Start-M3Geometry.cmd` 启动入口仍**不包含**本对照样本。

逐项核对见 [`P03_FOREST_COMPOSITION_COMPARISON.md`](P03_FOREST_COMPOSITION_COMPARISON.md)。
