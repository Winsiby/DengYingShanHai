# P03 中央留空同根树形构图对照（无时长 Dev 样本）

日期：2026-10-04
状态：**技术与中央留空对照通过；画面局部改善，构图仍待优化；正式演出未完成。本文件不是正式第三幕完成，也不是 P03 可玩完成。**
负责人：Codex 负责实现、实机 PIE 取证与视觉复核；WorkBuddy 仅整理事实文档。
依据：`AGENTS.md`、`TECH_SPEC.md`，以及本机 `Saved/Audit-2026-10-04-P03ForestComposition/` 内
`Execution-Contract.md`、`Supervisor-Results.md`、`Verification-Run2.json`、
`ImportAndTopologyChecks.json`、`Preview-Run1.log`、`Preview-Run2.log`；
旧森林样本对照见 `Saved/Audit-2026-10-04-P03ForestPreview/Run4/`。

> *永远不要以牺牲架构设计为代价追求功能；永远不要基于猜测进行权衡——必须与我确认。*

---

## 1. 用户确认范围

- 用户回复**「按照你的想法来」**，批准上一轮建议：**同根更早分叉、两侧展开、中央留空**。
- **仅确认这一步未保存的 Dev 构图。**
- **未批准**：正式连续动画、正式美术、P03 参数与容差、任何秒数、Skip、整体重启。
- 本轮**未扩展**场景、输入、玩法、镜头、资产采购或团队关键路径；
  未保存地图 / BP / 材质 / Definition，未做 Forest Actor、Finale、三幕整合或新包。
- 接触守卫与成功事实**仍归现有 C++**；Python 只生成未保存几何与取证，**不新增游戏规则**。

## 2. 图与来源

**本轮 6 张原图**（`Saved/Audit-2026-10-04-P03ForestComposition/Run2/`）：
实际 PIE 玩家视口 `HighResShot`，**1600×900，无 HUD**，未合成/编辑；字节与 SHA-256 见 `Verification-Run2.json`。
**图片未编辑，旧对照 `Audit-2026-10-04-P03ForestPreview/Run4/` 未被覆盖。**

| 序 | 文件 | 字节 | 含义 |
|---|---|---|---|
| 01 | `Run2/01-Start.png` | 883,084 | 原姿态（真实 Resolve 起点） |
| 02 | `Run2/02-Drop50.png` | 875,748 | 落杖中点（归一化 50%，无接触、无树） |
| 03 | `Run2/03-Contact.png` | 871,729 | 真实接触成立 |
| 04 | `Run2/04-Tree50.png` | 872,766 | 半展开（可见 **5** 段） |
| 05 | `Run2/05-Tree100.png` | 877,184 | 全展开（**9** 段） |
| 06 | `Run2/06-Tree100-NoTreeShadow.png` | 869,852 | 全展开、仅树 `CastShadow=false` 的诊断对照 |

**05 与 06 的证据意义**：全部树变换与端点保持不变，**最后一帧只改树 `CastShadow`**；
结果是对应幕上枝影消失、**实体树形仍在**。
正常帧的枝影**不是幕材质图案**，也**不是靠隐藏实体伪造因果**，没有切镜。
06 帧确实关闭树投影，**仅作为诊断对照**，实体与相机保持不变。

**旧对照**：本轮 6 张与旧森林 `Run4` 全展开图比较；旧 `NODES/EDGES/PHASES` 未改，旧 Run4 证据完整保留。

## 3. 真实 A 与幕上根（不可互换）

`Verification-Run2.json` 实录：

| 项 | 值 |
|---|---|
| 审计记录 | `ContactAccepted`（Python 日志记录，反映原生接触接受结果；未伪造 Contact 快照） |
| 本轮 Token | `5DB65B1C49D07D57CF6E9B96E93C6CC8` |
| `identity.native_token_current` | **`true`**（contact 与 resolve Token 同值） |
| 实体 A（物理根） | `(600.0, 18.713764, 128.208955)` |
| 幕上根（布面接触点） | `(925.0, -11.156212598, 70.0)` |
| 投影倍率（射线参数） | `1.3201970443349753` |
| `source_is_actual_A` | **`true`** |
| `formal_art_approved` | **`false`** |

> **本 Run2 的 Token 只对本 Run2 的接触/Resolve 有效**，
> **不与旧 Run4 或本 Run1 混写**——不同轮次的 Token 不可互相引用。

- 树根取 `contact.Projection.Staff.EndAWorld`（**实体 A**），**不取**幕上 `ContactWorldPosition`。
- **真实 A 物理根与幕布接触点不等同**，二者不可互换。
- 本轮树与现有幕之间的实际投影来自**同一 Movable 主灯**。

## 4. 9 边拓扑

`Verification-Run2.json` 的 `central_gap` 与 `accepted_contact` 实录：
`branch_count = 9`、`connected_edges = 9`、`ImportAndTopologyChecks.json` 另确认
`connected_roots = 1`、`parent_before_child = true`、`no_central_upright = true`。

单根连通顺序：**短根 → 低位左右 → 两侧上行 → 四个枝尖**。
10 个实测节点、9 条边（节点 X 恒为 `600.0`，即实体 A 所在平面）：

| 节点 | Y | Z |
|---|---|---|
| `root` | 18.713764 | 128.208955 |
| `fork` | 18.713764 | 129.362866 |
| `left_base` | −60.731389 | 130.709095 |
| `right_base` | 92.018528 | 130.709095 |
| `left_mid` | −73.820344 | 338.977493 |
| `right_mid` | 105.107483 | 338.977493 |
| `left_outer` | −119.631688 | 415.620597 |
| `left_inner` | −67.275867 | 441.168299 |
| `right_outer` | 150.918827 | 415.620597 |
| `right_inner` | 98.563006 | 441.168299 |

**半展开 5 段、全展开 9 段、投影关闭对照 9 段。**
**父边先于子边出现**；归一化展开**不是演出秒数**。

## 5. 实际角色保护框与体积检查

不只检查端点——**每个可见 Cylinder 的实际 bounds 8 角逐个投影验证**。

| 项 | 值 |
|---|---|
| 实际轮廓组件 | `actual_silhouette_components = 2`（**Torso + Head**） |
| 轮廓角数 | `silhouette_corner_count = 16`（两组件各 8 角，经实际组件变换投影） |
| 屏幕局部角色包络 | `[-5.1332743728, 1.7533910876, -31.7065044353, 5.7956849080]` |
| 诊断 padding（局部 Y/Z 各 2.0） | 本幕局部尺寸的 **2%** |
| 保护框 | `[-7.1332743728, 3.7533910876, -33.7065044353, 7.7956849080]` |
| 根部屏幕局部 | `(-50.0, -1.2395791776, -35.0)` |
| 低位连接可用高度 `low_clearance`（预扣枝段半径预算） | `0.634745564676462`（幕布局部单位，不是全树实测最小净距） |
| `gameplay_tolerance_changed` | **`false`** |

- **保护框取自真实 Torso/Head 的 8 角**；`padding` **仅是诊断净距**。
- **不是游戏容差**（`gameplay_tolerance_changed = false`）。
- **体积理想射线包络留空 ≠ VSM 像素 / 半影 / POV 遮挡已全部解决**
  （`ideal_point_projection_not_shadow_pixel_proof = true`）。
- 每次身份守卫都校验 **Torso/Head** 网格、局部边界与组件变换不变。
  枝干持续守卫校验 Actor 变换、隐藏状态与 CastShadow；实际枝段 bounds 八角和端点在布置各样本时复核。
- 继承字段 `sample_width_fraction = .48` 与 `sample_available_height_fraction = .62`
  是**构图坐标基准**；**新图实际跨度由角色保护框与左右扩展共同决定**，
  **不得写成实测树宽 48%**。

## 6. 接触与清理

| 事件 | 结果 |
|---|---|
| 落杖 0% / 50% | **无树** |
| 落杖 100% | 原生接受接触后**才允许**树展开（`native_contact_reused = true`） |
| 重复接触请求 | **拒绝** |
| 主成功事实 | **未撤销** |
| Staff 变换 | 完整相对变换**已恢复**（`full_staff_restored = true`） |
| 旧 Token | **拒绝**（`stale_token_rejected = true`） |
| 结束顺序 | 9 枝先隐去 → 再结束 PIE；Editor 会话临时 Actors 清理 |
| 完成状态 | `Completed(error = null)`、`editor_exited = true`、LogExit 正常 |

## 7. Run1 路径拒绝与 Run2 成功（失败证据保留）

- **Run1 在进入 PIE 前被输出路径守卫拒绝**：
  `RuntimeError: Evidence output must stay within this composition audit`。
  原因是 Launch 传入中文实体路径，而入口限定英文 junction 下的审计路径。
- **未放宽守卫**——修正的是 **Saved 启动脚本的输出路径**，守卫逻辑本身未变。
- `Preview-Run1.log` 失败日志保留；Run1 未进入 PIE，**没有 Run1 图像目录**。
  Run2 的图像与日志另存，未覆盖或删除失败证据。
- **Run2 正常完成并自动还原退出**：`Completed(error = null)`、Editor 正常 LogExit。

## 8. 局部视觉改善与仍存不足

Codex 已查看本轮全部 6 张原图，并与旧森林 Run4 全展开图比较。

**改善（有据可查）**：
- 新图**中央不再有旧版中央上行枝**（`no_central_upright = true`）；
- **角色轮廓更清楚**，中央重叠减少；
- **低位同根连接可追溯**。

**仍存不足（不得弱化）**：
1. **U 形框 / 支架感**——低位连接近水平、两侧近竖直，形成 U 形框；
2. **裸枝稀疏**，远不够桃林高潮；
3. **实体与影子双线**未消除；
4. **锯齿**未消除（**不猜锯齿成因**）；
5. 后台灰盒、反光地板、标记**仍非正式美术**。

**结论：技术与中央留空对照通过，画面局部改善；不是最终成林构图，不是用户视觉验收。**
**不宣称**高质量桃林、连续演出、用户视觉验收或 P03 可玩完成。

## 9. 未改动项（保护）

- **灯**、**幕**、**偶根**、**Staff 旋转与缩放**、**POV/FOV**、**曝光**、**材质**均不改。
  主灯实测：Lumens `42000`、半径 `2200cm`、`SourceRadius 4cm`、内/外角 `20/38`、
  `CastShadows = true`、`adjusted = false`。曝光保持既有 Manual 锁定（`Bias 3.5`）。
- 渲染器沿用既有 **DX12/SM6 + Lumen/VSM，硬件光追关闭**；**无 GPU/帧率测量**
  （`fps_measured = false`），**不宣称性能通过**。
- **P02 夹具仍是夹具**：谜题 `P02_ChaseForm`、灯 `0.72`、偶 `0.80`、Hold `1.25s`、`15 Hz`，
  `invented_p03_parameters = false`、`no_new_time_parameters = true`
  ——**不是 P03 新参数**。
- `Source` / `Config` / `Content` / `.uproject` / 旧启动器 **零改变**；
  两份获准末尾追加的旧文档及新增本文档之外，其余 Docs **零改变**。
- 资产沿用**已登记**的 Engine Cylinder 与实际 DefaultMaterial：
  **未下载新资产、未付费**，**无新的许可条目必要**。
- 旧森林诊断脚本只改 **2 个默认保持原行为的 hook**，新增独立构图诊断入口；
  旧 `NODES/EDGES/PHASES` 不变。
- 原 Computer Use 插件**仍卸载**、`STOP` 保持；原生 PowerShell 仅作既有桌面交接方式，
  **不称为官方插件**，**不改 WorkBuddy 模型或权限**。
- **未编译 / 未 Cook / 未 Package**；**无新 C++ Automation**（`new_automation_suite = false`），
  历史 **48 Success** 仅为历史基线，**不作为本轮重跑结果引用**。

## 10. 日志噪声（如实记录）

- `Preview-Run2.log` 仍有 **13 条**既有本地化 smoke-test `Condition failed` Error
  与 **1 条** NVIDIA TSR 驱动兼容 Warning。
- **Run2 诊断成功 ≠ 整日志零 Error。** 本轮不改驱动或配置。
- **无性能结论**（未测 GPU/帧率），**无打包结论**（未 Cook/Stage/Package）。

## 11. 未完成项

- **未保存**任何资产：无地图 / BP / 材质 / Definition，`saved_assets = false`。
- **未实现**：正式连续落杖编排、正式生长动画、Forest Actor、正式美术与声音、
  P03 Definition 与目标/容差、正式秒数、Finale 结束态、三幕队列、Skip、统一整局重启、
  两种新环境态、玩家 GUI 手动通关、新 Windows 包与性能验证。
- **不是用户视觉验收**：本轮仅 Codex 视觉复核，用户未验收。
- 下一步建议（**未实施、未自动批准**）：保留本轮开口方向，但
  **不要直接把这 9 个圆柱保存为最终 Forest**；后续用更自然的渐缩/侧枝构图样本
  克服 U 形框，同时保持实测 A 根、角色留空与同灯投影。
  **不为视觉改进擅自移动灯/偶/幕/镜头或隐藏幕后实体。**
- 正式连续落杖/生长、秒数、P03 容差、终态/Skip/重启**须按既定待决流程确认**。

## 12. 状态

**部分完成**：中央留空同根树形的**技术与对照通过**，画面**局部改善**；
**构图仍待优化，正式演出未完成**。
本文件不构成正式第三幕、参赛作品或用户验收结论，**未代签任何人工确认**。
最终全文件保护哈希由 Codex 在本文档交付后复核，**本文不预写最终文件数量**。

AI 使用记录：Codex 负责脚本实现、两次独立 Editor 启动（Run1 进入 PIE 前拒绝，Run2 完成 PIE 取证）、原图视觉复核与范围审计；
WorkBuddy 本轮核对证据后按白名单整理三份文档，Codex 最终复核并修正上述事实口径。
WorkBuddy 原稿保留在本审计 `WorkBuddy-Output/`。**不冒充已完成赛事 AI 申报。**

## 13. Codex 最终复核与交付边界

- 独立只读复查者已打开全部六张原图并重算 SHA-256，6/6 一致；另从原始日志独立核对
  6 次采样、23 次枝实例检查、184 个体积角、一次接触与清理，结论与本文一致。
- 文档交付后全文件 SHA 审计：**136 个旧产品文件，133 相同、3 项白名单改变、0 缺失；新增 2 项，总 138**。
  三项改变为旧森林诊断脚本及两份仅末尾追加的旧文档；新增为独立构图入口与本文档。
  精确路径和最终哈希见本审计 `ProductScopeAudit.json`，不含 Saved 生成证据。
- `HistoryPrefixChecks.json` 确认两个旧文档修改前全文字节作为完整前缀保留，历史待确认段落没有回改。
  Git HEAD 未变、暂存区为空；没有提交、删除或清理用户改动。
- 两个默认保持 hook 的原节点/直径计算与备份只读比较一致；导入/拓扑/语法检查通过。
  **没有额外重跑旧森林入口的实机回归**，不把静态比较写成实机旧版验收。
- WorkBuddy 实际按三份白名单文档交付；Codex 保留原稿并修正节点数量、日志来源、
  低位预算含义与 Run1 未进入 PIE 等口径。不是用其它代理冒充 WorkBuddy。
- 本轮只取得无时长 Dev 对照，**旧 `Start-M3Geometry.cmd` 不包含新树样本**；
  不提供“新游戏包已完成”结论，不代签用户画面验收。

## 14. 后续对照进展（2026-10-04 低位转折与分段外展枝形）

> **本文件 §1–§13 全部内容为中央留空对照轮的历史记录，保持原样、不被擦除或改写。**
> §11 中「后续用更自然的渐缩/侧枝构图样本克服 U 形框」是**当时的历史事实**——
> **该方向本轮已获用户批准并实施**（用户回复「继续按照你的想法来进行」）。
> 本节只**追加**对照进展，**不回改历史「未实施」文字**。

### 本轮已完成

- 取得 **6 张 1600×900 无 HUD 真实 PIE 原图**（`Saved/Audit-2026-10-04-P03BranchRefinement/Run1/`），
  无编辑合成；旧 U 形对照 `Audit-2026-10-04-P03ForestComposition/Run2/` **未被覆盖**。
- 拓扑由 9 边 16 节点中的 **9 边**升级为 **15 边 16 节点单根连通**：
  实际 A → 极短 fork；左右 near → exit 低位逃逸；exit → lower → upper → tip 弯折上行；
  lower/upper 侧枝**错位展开**。半展开 **11** 段、全展开 **15** 段、关影 **15** 段。
- **41 枝实例检查（11+15+15）／82 个实际中心端点／328 个实际 Cylinder bounds 投影角**
  ——**不是 41 项 Automation 测试**。
- 分段直径因子递减、**原末梢 `.42` 保守保持**；**分段减细不是平滑连续 taper**，
  **不是真实生物桃树模型**。
- 视觉：**U 形近垂直双柱与直角托架感减轻**，改为**外展 V 形/浅弧 + 错位侧枝**，
  **中央留空保持**。

### 仍未完成 / 仍不成立

- **必要的短横根仍存在且可见**（`low_connection_retained = true`），
  **不能声称 U 形框观感完全消除**。
- **裸枝稀疏**（无林层/叶片/桃林语义）、**双线增加**（更多侧枝也增加双线数量）、
  **锯齿明显**；分段折线与直径台阶**仍是灰盒**。
- **不是**参赛高质量林相，**不是**正式连续演出，**不是**用户视觉验收，
  **不是** P03 可玩完成，**不是**正式第三幕完成。
- **本 Run1 Token `E897B2094D231613DF7D85BB3FDCD62D` 只同本轮 Resolve/Contact 相等，
  不跨旧 Run2 / Run4 混写。** `ContactAccepted` **是 Python 审计标签**，不是原生事件名称。
- **实体 A 根与幕上接触点不等同、不可互换**；**原生射线投影与实际 8 角留空
  ≠ VSM 像素/半影/POV 无遮挡**。
- 中心节点局部包络是**节点范围**，不是树体积或阴影像素宽度；`.48/.62` 是**坐标基准，
  不是实测总宽**；`low_clearance` 是**预扣半径的低位预算，不是全树最小实际净距**。
- **本轮 Run1 成功，没有失败的 UE Run**；上一轮 Run1 的路径失败**不混入本轮**。
- 未保存任何资产；未实现正式连续落杖/生长、P03 Definition 与容差、正式秒数、Finale、
  三幕队列、Skip、统一整局重启、两新环境态、声音、正式美术资产、新包、性能验证与人工通关。
- **未编译 / 未 Cook / 未 Stage / 未 Package**、**无新 C++ Automation**；
  历史 48 Success **不是本轮重跑**。日志仍有 **13 条**既有 Error 与 **1 条** TSR Warning
  ——**不等于全日志 0 Error**。
- 旧 `Start-M3Geometry.cmd` **仍不包含**本样本；新 Python 是自动取证入口，
  **不是双击即可手动可玩的第三幕**。
- 建议保留本轮**低位逃逸 / 外展 / 中央留空**作为结构候选，
  **不继续靠堆裸枝假装成林**（**建议，未实施 / 未自动批准**）。

逐项核对见 [`P03_BRANCH_REFINEMENT_PREVIEW.md`](P03_BRANCH_REFINEMENT_PREVIEW.md)。
