# P03 低位转折与分段外展枝形对照（无时长 Dev 样本）

日期：2026-10-04
状态：**技术与对照有效；轮廓局部改善，构图仍待优化；正式演出未完成。本文件不是正式第三幕完成，也不是 P03 可玩完成。**
负责人：Codex 负责实现、实际 Run1/PIE 取证、原图复核与实机验收；WorkBuddy 仅整理事实文档。
依据：`AGENTS.md`、`TECH_SPEC.md`，以及本机 `Saved/Audit-2026-10-04-P03BranchRefinement/` 内
`Execution-Contract.md`、`Supervisor-Results.md`、`Verification-Run1.json`、
`ImportAndTopologyChecks.json`、`Preview-Run1.log`；
旧 U 形对照见 `Saved/Audit-2026-10-04-P03ForestComposition/Run2/`。

> *永远不要以牺牲架构设计为代价追求功能；永远不要基于猜测进行权衡——必须与我确认。*

---

## 1. 用户确认范围

- 用户回复**「继续按照你的想法来进行」**，批准上一轮建议：
  仍在 Dev 无时长样本中，用**分段渐缩、转折与侧枝轮廓**减轻 U 形框。
- **仅批准这一步未保存的 Dev 对照。**
- **未自动批准**：正式美术、演出秒数、P03 目标/容差、Skip、整局重启、相机/输入、三幕整合。
- 本轮**未新增** Skip、整局重启或输入；**未保存**任何资产；**未编译 / 未 Cook / 未 Package**。
- 队友美术源**未触碰**。

## 2. 实现、所有权与依赖

- **原生 C++ Resolve / 接触接口继续是事实源**；诊断 Python 会话持有临时 Editor/PIE 实体，
  **没有生产 Actor Tick**，**没有新游戏规则**，**未复制 C++ 判定**。
- 派生链（固定显式引用，**无每帧扫描、无消息总线、无新增 Subsystem**）：

  ```text
  Preview-P03BranchRefinement.py（新）
    → Preview-P03ForestComposition.py（中央留空诊断）
      → Preview-P03ForestProjection.py（树形诊断）
        → Preview-P03StaffDrop.py（落杖生命周期）
          → 原生只读快照 / 一次性接触接口
  ```

- 临时枝干 Actors **预先创建、隐藏且关闭投影**；原生接触接受后，才计算并布置可见枝形目标点。
- 结束顺序：先隐去本次枝干 → 完整 Staff 恢复 → 清空 PIE refs → `EndPIE`
  → 销毁**仅本会话** Editor 临时 Actors。
- 候选越界则**守卫否决并清理**；**不移动灯/偶/幕/POV、不放宽保护框、不隐藏实体来过检**。
- **旧 9 段入口保留**为诊断对照候选，**未实现自动降级**；本轮**未重新实机回归**旧入口，
  只做 **AST / 导入 / 拓扑 / 语法**比较（`previous_default_nodes_ast_identical = true`、
  `previous_nine_edges_unchanged = true`）。
- 旧 `Scripts/Preview-P03ForestComposition.py` **只把既有 `local_nodes` 字典抽成默认保持 hook**，
  保护框/体积守卫/清理逻辑**未改**。

## 3. 15 边 16 节点与分段减细

`Verification-Run1.json` 的 `refinement_layout` 与 `ImportAndTopologyChecks.json` 实录：
`branch_count = 15`、`node_count = 16`、`single_root = true`、`parent_before_child = true`、
`thickness_nonincreasing = true`。

**结构**：实际 A → 极短 `fork`；左右 `near` → `exit` 低位逃逸；
`exit` → `lower` → `upper` → `tip` 弯折上行；`lower` 侧枝与 `upper` 侧枝**错位展开**
（`asymmetry_is_diagnostic = true`）。

**16 节点（实体世界坐标，X 恒为 `600.0`）**：

| 节点 | Y | Z | 节点 | Y | Z |
|---|---|---|---|---|---|
| `root` | 18.713764 | 128.208955 | `right_lower` | 137.829871 | 236.786687 |
| `fork` | 18.713764 | 128.593592 | `right_upper` | 177.096737 | 351.751343 |
| `left_near` | −10.410271 | 129.055156 | `right_tip` | 222.908080 | 437.974836 |
| `right_near` | 53.632190 | 129.285938 | `left_side` | −160.534673 | 262.334388 |
| `left_exit` | −46.006314 | 130.516776 | `left_twig` | −111.451091 | 402.846746 |
| `right_exit` | 82.201812 | 130.670631 | `right_side` | 200.002409 | 297.462478 |
| `left_lower` | −108.178852 | 217.625910 | `right_twig` | 235.997036 | 396.459821 |
| `left_upper` | −150.717956 | 326.203642 | | | |
| `left_tip` | −176.895867 | 428.394448 | | | |

**分段直径因子（15 条边，实录顺序）**：

```text
1.0, .80, .80, .72, .72, .68, .68, .58, .58, .42, .42, .46, .46, .42, .42
```

- 根/near/exit/lower/upper/tip = `1 / .80 / .72 / .68 / .58 / .46`；侧枝 = `.42`。
- **这是分段 Cylinder 直径递减，不是平滑连续 taper，也不是真实生物桃树模型**
  （`stepped_diameters_not_smooth_taper = true`、`biological_model_claim = false`）。
- **主枝末梢 `.46`、侧枝末梢 `.42`**，保守保持可读宽度，不因追求细而缩成不可读像素。
- 候选比早期建议向外弯折更明显；实际 bounds/变换由 UE 反射读取，投影调用原生库；
  端点一致、8 角 OnScreen 与保护框分离的否决检查是 **Python 诊断断言**，失败则停止并清理。
  **不是新增原生 C++ 体积契约，保护框未放宽。**
- 实体点由**真实幕变换 + 原生投影根射线参数**反算，**不硬编码 X600**。

## 4. 真实 A 与幕上根（不可互换）

| 项 | 值 |
|---|---|
| 事件标签 | `ContactAccepted` |
| 本轮 Token | `E897B2094D231613DF7D85BB3FDCD62D` |
| `identity.native_token_current` | **`true`**（contact 与 resolve 同轮相等） |
| 实体 A（物理根） | `(600.0, 18.713764, 128.208955)` |
| 幕上根（布面接触点） | `(925.0, -11.156212598, 70.0)` |
| 根射线倍率 | `1.3201970443349753` |
| `source_is_actual_A` | **`true`** |
| `connected_edges` | `15` |
| `formal_art_approved` | **`false`** |

> **`ContactAccepted` 是 Python 审计标签**，反映原生 `TryAcceptStaffContact` 接受与
> 真实 Contact 快照，**不是原生事件名称**。

> **本 Run1 Token 只同本轮 Resolve/Contact 相等，不跨旧 Run2 / Run4 混写。**

- 树根取 `contact.Projection.Staff.EndAWorld`（**实体 A**），**不取**幕上 `ContactWorldPosition`。
- **实体 A 根与幕布接触点不等同**，二者不可互换。

## 5. 六图与来源

**本轮 6 张原图**（`Saved/Audit-2026-10-04-P03BranchRefinement/Run1/`）：
实际 PIE 玩家视口 `HighResShot`，**1600×900，无 HUD**，**未经合成或编辑**；
字节与 SHA-256 见 `Verification-Run1.json`。旧 U 形对照未被覆盖。

| 序 | 文件 | 字节 | 该帧可见枝段 |
|---|---|---|---|
| 01 | `Run1/01-Start.png` | 882,746 | 0（原姿态） |
| 02 | `Run1/02-Drop50.png` | 875,437 | 0（落杖 50%） |
| 03 | `Run1/03-Contact.png` | 872,569 | 0（真实接触成立） |
| 04 | `Run1/04-Tree50.png` | 875,107 | **11** |
| 05 | `Run1/05-Tree100.png` | 883,910 | **15** |
| 06 | `Run1/06-Tree100-NoTreeShadow.png` | 873,701 | **15**（仅关树投影） |

**6 个原采样位置与上一轮一致**：原姿态、50% 落杖、接触、50% 展开、100% 展开、仅关闭树投影对照。

**05 与 06 的证据意义**：**只改树 `CastShadow`**，**实体不隐藏**，
**15 枝变换与实际端点完全保持**。对应幕上枝影来自真实几何投影，**不是幕材质林影图案**；
对照**没有切镜或隐藏实体**，关投影帧**仅供诊断**。不据此否认整帧所有材质/渲染伪影。

**独立只读复核**：另一复查者查看 6 张原图、**重算 SHA 6/6 相同**，独立日志计数一致。

## 6. 实机检查与静态检查必须分开

**实机（UE PIE）**：6 张真实原图、1 次原生 `TryAcceptStaffContact` 接受、
0/50% 落杖无树、100% 接触后才展开、重复接触拒绝、守卫未撤销主成功、
完整 Staff 恢复、旧 Token 拒绝、15 枝先隐去、`Completed(error = null)`、LogExit 正常。

**静态/导入检查**（`ImportAndTopologyChecks.json`）：
`import_without_editor_actions`、`previous_default_nodes_ast_identical`、
`previous_nine_edges_unchanged`、`single_root`、`parent_before_child`、
`thickness_nonincreasing`、`syntax_no_asset_save_checked`、
`unreal_runtime_test = false`。

**本轮计数（务必按此口径）**：
**41 枝实例检查（11 + 15 + 15）／82 个实际中心端点／328 个实际 Cylinder bounds 投影角**。
**不是 41 项 Automation 测试**；`new_automation_suite = false`。

**几何守卫**：
- 真实 Torso/Head **每次 identity 锁网格、bounds 与组件变换**（16 角投影保护框，
  `actual_silhouette_components = 2`、`silhouette_corner_count = 16`）；
- 枝干**每次布置核验端点与 8 角**；全部实际 bounds 角 `OnScreen` 且与保护框**左/右/下分离**；
- 持续身份守卫 Actor 变换、hidden 状态与 `CastShadow`；
- **低位连接仍必需**（`low_connection_retained = true`），
  **保护框不放宽**；`gameplay_tolerance_changed = false`。

> **原生射线投影与实际 8 角留空 ≠ VSM 像素/半影/POV 无遮挡**
> （`ideal_point_projection_not_shadow_pixel_proof = true`）。

**三个字段的准确含义（不得误写）**：
- `projected_center_node_bounds = [-29.9332743728, 30.6333910876, -35, 16.119]`
  是**中心节点范围**，**不是实际树体积或阴影像素占用宽度**；
- 继承的 `.48 / .62` 是**构图坐标基准**，**不是实测树总宽 48%**；
- `low_clearance = 0.634745564676462` 是**预扣半径的低位预算**，
  **不是全树最小实际净距**（该值为旧夹具事实，**不是新容差**）。

## 7. 接触与清理

| 事件 | 结果 |
|---|---|
| 落杖 0% / 50% | **无树** |
| 落杖 100% | 原生接受接触后**才允许**展开 |
| 重复接触请求 | **拒绝** |
| 主成功事实 | **未被守卫撤销** |
| Staff 变换 | 完整恢复（`full_staff_restored = true`） |
| 旧 Token | 拒绝（`stale_token_rejected = true`） |
| 结束顺序 | 15 枝先隐去 → 清 PIE refs → EndPIE → 销毁本会话临时 Actors |
| 完成 | `Completed(error = null)`、`editor_exited = true` |
| 资产保存 | **未保存**地图 / BP / 材质 / Definition |

## 8. 视觉优劣（如实记录）

**改善（有据可查）**：
- U 形**近垂直双柱与直角托架感减轻**，改为**外展 V 形 / 浅弧**；
- **错位侧枝**替代双柱对称（`asymmetry_is_diagnostic = true`）；
- **中央留空保持**——头/躯干中央空隙仍在（`no_central_upright = true`）；
- 与旧 Composition/Run2 全展开原图比较后确认。

**仍存不足（不得弱化）**：
1. **必要的短横根仍存在且可见**——`low_connection_retained = true`；
   **不能声称 U 框观感完全消除**；
2. **裸枝稀疏**，没有林层、叶片与桃林语义；
3. **双线增加**——更多侧枝也**增加双线数量**；
4. **锯齿明显**；
5. **分段折线与直径台阶仍是灰盒**；
6. 后台灰盒、反光地板、标记**仍非正式美术**。

**结论：技术/对照有效，轮廓局部改善；不是参赛高质量林相，
不是正式连续演出，不是用户视觉验收，不是 P03 可玩完成。**
不猜锯齿成因；不为视觉改进擅自移动灯/偶/幕/镜头或隐藏幕后实体。

## 9. 未改动项

- **主灯**42000 Lumens、半径 `2200cm`、`SourceRadius 4cm`、内/外角 `20/38`、
  Manual 曝光 `Bias 3.5`、**幕 / 偶根 / Staff 旋转缩放 / POV / FOV / 曝光**均不改；
  `adjusted = false`。
- 渲染器沿用既有 **DX12/SM6 + Lumen/VSM，硬件光追关闭**；`fps_measured = false`
  ——**无性能结论**。
- **P02 夹具仍是夹具**：`P02_ChaseForm`、灯 `0.72`、偶 `0.80`、Hold `1.25s`、`15 Hz`，
  `invented_p03_parameters = false`、`no_new_time_parameters = true`
  ——**不等于 P03 参数**，**无新时长**。
- **无 Source / 资产 / Config / `.uproject` / 旧启动器变化**；
  旧 Composition 脚本**仅默认保持 hook**。
- 资产**只用已登记 Engine Cylinder 与实际 Engine `DefaultMaterial`**；
  **未引入新网格/材质，未下载、未付费**，**不改 `LICENSES.md`**。
- 原 Computer Use **仍停用**、`STOP` 保持；WorkBuddy 沿用用户既定模型与权限，
  原生桌面方式交接需正常审核。
- **本轮由 Codex 启动一次完整 Editor 进入 PIE 取证**，**不混写上一轮两次启动**。

## 10. 日志噪声（如实记录）

- `Preview-Run1.log` 仍有 **13 条**既有本地化 smoke-test `Condition failed` Error
  与 **1 条** NVIDIA TSR 驱动兼容 Warning。
- **诊断成功 ≠ 全日志 0 Error。** 本轮不改驱动或配置。
- **无新 C++ Automation、无编译 / Cook / Package、无 GPU/帧率测试**；
  历史 **48 Success** 不是本轮重跑，**不构成本轮性能或可玩结论**。

## 11. 未完成项

- **未保存** Forest 资产或地线实例；**不是**正式 Forest Actor。
- **未实现**：正式连续落杖/生长、P03 Definition 与容差、正式秒数、Finale 结束态、
  三幕队列、Skip、统一整局重启、两种新环境态、声音、正式美术资产、新包、性能验证、人工通关。
- **不是**用户视觉验收；本轮仅 Codex 与独立只读复查者复核原图。
- 旧 `Start-M3Geometry.cmd` **不包含本样本**；新的 Python 是**自动取证入口**，
  **不是双击即可手动可玩的第三幕**。
- 下一步建议（**未实施、未自动批准**）：
  - 保留本轮**低位逃逸 / 外展 / 中央留空**作为结构候选，
    **不继续靠堆裸枝假装成林**；
  - 再确认 Dev 连续表现样本与节奏比较方式；
  - 正式秒数、是否允许新增样本入口、统一终态等**按既定待决流程处理**。

## 12. 状态

**部分完成**：低位转折与分段外展枝形的**技术与对照有效**，轮廓**局部改善**；
**构图仍待优化，正式演出未完成**。
本文件不构成正式第三幕、参赛作品或用户验收结论，**未代签任何人工确认**。
最终全文件哈希由 Codex 在本文档交付后复核，**本文不预写最终文件数量**。

AI 使用记录：Codex 负责脚本实现、一次完整 Editor/PIE 取证、原图复核与范围审计；
WorkBuddy 本轮核对证据后按白名单整理三份文档（新增本文档、两份旧文档仅末尾追加），Codex最终复核。
原稿保留在本审计 `WorkBuddy-Output/`。
**本记录事实保存，不冒充已完成赛事 AI 申报。**
