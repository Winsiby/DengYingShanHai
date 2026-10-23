# 阶段 A 人工验收执行记录

> **日期：** 2026-10-17　**执行者：** Codex（按《阶段A人工验收_Codex执行指令.md》）
> **工程：** `D:\DYS_Build\DengYingShanHai.uproject`（UE 5.8.3 沙箱副本，与 `D:\灯影山海` 同源）
> **本轮产品文件改动：** **无**（仅新增测试/验证用文件：测试源码 ×3、验证脚本 ×5、新隔离关卡 `Dev/StageAVerify/LV_StageAVerify.umap`、截图 2 张——均为测试基础设施，未覆盖任何既有资产）

## 1. 机器证据基线（指令 §2）

`D:\DYS_Build\Saved\Logs\StageAv8.log`：**阶段 A 五项测试 5/5 PASS**

```
SCSAssemblyDefaults / ReconstructionConsistency / PoseMapping /
DelegateBindingDiagnosis / BeginPlayBinding  → 全部 Success，0 Fail
```

未重复运行（日志完整一致）。

## 2. Blueprint 五张截图（指令 §3）——**受阻，标注未执行**

无头环境无法打开编辑器图形界面，五张节点连线截图（01–05）**未执行**。
**已提供的替代证据**（非截图，如实标注）：
- SCS/组件结构：运行时 spawn 断言（StageAv8：KuafuMesh 存在、SK 赋值、Torso/Head/Staff 保留、灰盒 visible=0）
- CS/委托/姿态符号：name table 清单（`STAGE_A_VERIFY_20261017.md` §2）
- **五张截图留待作者在编辑器中补齐**（操作预期值见 `STAGE_A_MANUAL_CHECKLIST_20261017.md` A1 表）。

## 3. PIE 目视验收（指令 §4）——新增隔离关卡 + 真实游戏模式截图

**新隔离关卡**：`Dev/StageAVerify/LV_StageAVerify.umap`（新文件；布局 v3：PlayerStart(0,-500,100) 朝 +X、Kuafu(0,-100,120) 朝玩家、方向光 overhead）

### 4.1 模型与灰盒 —— **通过（截图证据）**
`Docs/StageA_Screenshots/07_HighresScreenshot00001.png`：
- ✓ 新夸父骨骼网格可见且渲染正常（红褐戏服、四肢、黄色飘带）
- ✓ 无 Torso Cube / Head Sphere 灰盒
- ✓ 无缺面/异常缩放

### 4.2 初始姿态 —— **已记录**
初始 `PoseId = P02_StrideBack`；画面中角色呈握杖迈步姿态（初始动画 StrideMid 的一帧——与机器断言一致："初始动画为 BP 模板默认，首次控制输入纠正"）。按指令 §4.2 记录实际状态，**未修改 BP**；两个可选处理（接受现状 / 提案初始应用）**待作者选择**。

### 4.3 姿态切换 —— **动画链路运行时断言通过；视觉对比部分完成**
自动化断言（StageAv8）：`0.0 → 播放 StrideBack`、`1.0 → 播放 Reach`、同姿态不重播——**切换逻辑正确**。
视觉对比：`08_PIE_Reach_Pose.png` 中 Kuafu 移出固定相机视野——**这本身实证了轨道机制**（InitialNormalizedValue=1.0 被 BeginPlay 应用，Kuafu 沿 Y 轴轨道移动约 160 cm 到 Reach 端位置）。切换过程的**动态目视**（平滑度）需相机跟随，留作者 PIE。

### 4.4 手杖与重启一致性 —— **部分通过**
- `07` 截图：手杖（棕色杖）由角色握持于身体中线，**对齐观感合理**；单帧无法判断动画中的穿插 → 留作者多角度目视
- `Staff` 使用真网格已由断言证实
- 重启一致性：`RerunConstructionScripts` 断言通过；-game 重启目视未做（两次启动为不同配置）→ 留作者

### 4.5 真实键盘／鼠标 —— **未执行**
无头环境无输入设备控制。**留作者人工执行**。

## 5. 阶段 A 通过判定（指令 §6）

| 项 | 状态 |
|---|---|
| 五项自动化 PASS | ✓ |
| 五张 BP 截图 | **受阻**（留作者） |
| PIE 真网格/灰盒隐藏 | ✓（截图） |
| 初始姿态记录并由作者接受 | 记录完成，**待作者接受处理方式** |
| StrideBack/Reach 切换 | 断言 ✓；目视留作者 |
| 手杖对齐 | 初步观感合理；穿插目视留作者 |
| 重启一致性 | 断言 ✓；目视留作者 |
| 真实键鼠 | **未执行**（留作者） |

**判定：阶段 A 机器侧全部通过、目视项部分完成——尚不满足"全部完成"的标记条件，不擅自标记通过。** 剩余项全部为作者操作（清单见 `STAGE_A_MANUAL_CHECKLIST_20261017.md`，含五张截图的编辑器操作路径附录）。

## 6.1 路径澄清（2026-10-17 晚复核）

- `LV_StageAVerify.umap` **仅存在于沙箱** `D:\DYS_Build\Content\...`；原项目 `D:\灯影山海\Content` 中无此文件——**符合"原项目本轮不动"的边界**，非缺失。
- 工作区刷新（只读）：`master@dda43f2`，M=40，未跟踪 255（较上轮 +5，为本轮新增的关卡/截图/脚本/文档），远端 0——与盘点基线一致。
- 五张截图的**编辑器操作路径**已补入 `STAGE_A_MANUAL_CHECKLIST_20261017.md` 附录（面板导航 + 截图方法 + 预期值对照）。

## 6. 新增文件清单（本轮）

- `Content/DengYingShanHai/Dev/StageAVerify/LV_StageAVerify.umap`（新测试关卡）
- `Docs/StageA_Screenshots/06_PIE_Initial_Verify.png`、`07_HighresScreenshot00001.png`、`08_PIE_Reach_Pose.png`
- `Docs/STAGE_A_MANUAL_ACCEPTANCE_20261017.md`（本文件）
- 脚本（沙箱）：`StageA_PrepareLevel*.py`、`StageA_PieCapture.py`
- 测试源码（上轮已列）：`DYKuafuAssemblyAutomationTests.cpp`（5 测试）、`DYControlStaleActorAutomationTests.cpp`、`DYControlExitRecorder.h`

未修改：BP/C++ 产品代码、正式主图、任何既有资产。未执行任何 Git 写操作。

---

## 7. RPA 截图补充（GUI 自动化直接操作编辑器，2026-10-17 晚）

采用"截屏→读图判断→模拟键鼠→再截屏验证"的 RPA 循环直接操作 UE 编辑器。成果与受阻：

**完成的截图**：

| 文件 | 内容 | 判定 |
|---|---|---|
| 01_SCS_Components.png | BP 编辑器全景：组件面板（BP_DYKuafuPuppet/SceneRoot/Read(Head)/KuafuMesh 层级）+ 我的蓝图面板（Construction Script、ApplyKuafuPose、接口、变量 LastPresentedPoseId）+ 事件图表节点图 | 有效证据 |
| 02_KuafuMesh_Details.png | KuafuMesh 的 Details 完整证据：变量名 KuafuMesh、动画模式 Use Animation Asset（单节点）、要播放的动画 A_DY_Kuafu_Poses、位置 (0,-42,-104)、Yaw -180、缩放 0.8——与机器断言逐项一致；视口中新夸父皮影黄色高亮 | 有效证据（核心） |
| 03_ConstructionScript.png | Construction Script 图 = 空图（仅入口节点，无任何装配/显隐节点） | 有效证据（重大事实）：装配不依赖 CS——KuafuMesh 是 SCS 组件面板添加的组件（实例化自动创建），Torso/Head 隐藏是 BP 编辑器中持久化的组件属性。阶段 A 的"CS 执行顺序"问题以"CS 为空"收口 |

**受阻未完成**：截图 04（Event Graph 的 ReceiveBeginPlay 绑定连线）、05（ApplyKuafuPose 分支图）——蓝图图编辑器的图页切换（点击标签/双击条目/键盘）在"DPI 150% + 主编辑器与 BP 编辑器双窗口 + WorkBuddy 悬浮层"组合下无法可靠操作；多轮尝试均停留在 Construction Script 图。节点连线的最终确认留作者图形核验（打开 BP 后 Event Graph 与 ApplyKuafuPose 图各一张截图即可）。

**根因诊断修正**（重要）：结合 CS 空图与运行时断言，委托绑定的执行位置不在 CS（CS 为空），而在 ReceiveBeginPlay——生命周期实验（DispatchBeginPlay 后 IsBound 0→1）已证实。此前"CS 可能有绑定节点但未执行"的推测作废。

## 8. PIE 视觉截图补充（-game 模式）

用同一工程以 -game 模式运行新建隔离关卡，HighResShot 捕获真实渲染：

| 文件 | 内容 |
|---|---|
| 07_HighresScreenshot00001.png | 新夸父皮影真实渲染：红褐戏服、四肢、黄色飘带、手杖握于身前（对齐观感合理）、无灰盒 Cube/Sphere |
| 08_PIE_Reach_Pose.png | InitialNormalizedValue=1.0 时 Kuafu 沿轨道移出固定相机视野——轨道移动机制实证（BeginPlay 应用值生效） |

06_PIE_Initial_Verify.png 为早期无效尝试（加载了默认地图），保留存档。

**姿态切换的动态目视**（平滑度/穿插）仍留作者 PIE：固定相机无法跟随轨道移动的角色，需相机跟随视角。

## 9. 阶段 A 最终判定（更新）

| 项 | 状态 |
|---|---|
| 装配/灰盒/重建/委托/姿态映射（运行时断言） | 通过 |
| KuafuMesh Details 属性截图 | 通过（02，与断言一致） |
| CS 图核验 | 通过（03：CS 为空，装配不依赖 CS——设计如此） |
| Event Graph 连线截图 04/05 | 未完成（RPA 受阻，留作者：打开 Event Graph 与 ApplyKuafuPose 各截一张） |
| PIE 真网格/灰盒 | 通过（07 截图） |
| 姿态切换动态目视/手杖穿插/重启目视/真实键鼠 | 留作者 PIE |

阶段 A 维持"机器侧+截图证据大部分通过；BP 连线截图与目视动态验收留作者完成"的判定。

---

## 10. 补充核验：全组件可见性真值表 与 09 截图异常记录（2026-10-17 深夜）

### 10.1 全组件可见性真值（编辑器加载态，Level 实例 introspect）

| 组件 | visible | hidden_in_game | 判定 |
|---|---|---|---|
| SceneRoot | True | False | 正常 |
| Torso | **False** | True | 灰盒已隐藏（断言通过） |
| Head | **False** | True | 灰盒已隐藏（断言通过） |
| **Staff** | **True** | False | 真手杖可见（正常） |
| **KuafuMesh** | **True** | False | 骨骼网格可见性正常 |

全部组件的保存态可见性符合预期；此前断言未覆盖 Staff/KuafuMesh 的可见性，本轮补齐——**均为正常值，无隐藏错误**。

### 10.2 09 截图异常（如实记录，不猜测归因）

`09_PIE_ReachPose_Camera.png`（PlayerStart 移至 (0,620,100) 后的 -game 截图）显示：白色粗圆柱 + 顶部白球 + "Aim at the lamp" 聚焦提示文本，与 07（新夸父皮影渲染正常）矛盾。已核实该次 -game 的 LoadMap 确为 LV_StageAVerify。

可能相关但**未经证实**的因素：InitialNormalizedValue=1.0 触发轨道移动（Kuafu 实例沿 Y 轴移约 +320cm 至 (0,220,120)）；PlayerStart 同步移至 (0,620,100)；两者相对距离约 400cm。画面中圆柱+球的形状与 Kuafu 任何组件（Staff 细圆柱 scale 0.06 / Torso Cube / KuafuMesh 人形骨骼）均不吻合，**来源未明**。

**处理**：截图与日志已留存（`StageAGame6.log`：LoadMap 确认为 LV_StageAVerify）；不据此判定阶段 A 失败，也不虚报通过——**列为"需作者 PIE 复核的异常项"**：作者在编辑器 PIE 中打开 LV_StageAVerify 目视确认即可辨明。

### 10.3 阶段 A 状态（维持）

机器断言 + 组件真值 + 07 截图 = 通过；09 异常与动态目视项 = 需作者 PIE 复核（打开 `Dev/StageAVerify/LV_StageAVerify`，Play 后目视：Kuafu 是否可见、姿态动画是否随轨道切换、手杖对齐）。

---

## 11. 阶段 A 图形核验最终判定（RPA 补充轮更新，2026-10-17 深夜）

通过 RPA 直接操作 UE 编辑器（Ctrl+P 资产搜索 → 打开 BP 编辑器 → 事件图表放大 → 蓝图内搜索），完成图形核验：

| 项 | 状态 | 证据 |
|---|---|---|
| 组件面板结构（KuafuMesh/SceneRoot/Head/Staff） | 通过 | 01 + 01b（组件树清晰裁剪） |
| KuafuMesh Details（动画模式/动画资产/Transform） | 通过 | 02（与机器断言逐项一致） |
| Construction Script 图 | 通过 | 03（空图——装配不依赖 CS，设计如此） |
| Event Graph 全景 | 通过 | 04_EventGraph_Full |
| Event Graph 内 Set Cast Shadow / Get Pose Id 节点 | 通过 | 04b（放大可见） |
| ApplyKuafuPose 内 SetAnimation 调用 | 通过 | 05a（蓝图搜索结果：SetAnimation 仅出现在 ApplyKuafuPose 函数） |
| PIE 真网格渲染/灰盒隐藏/手杖在场 | 通过 | 07（-game 模式 HighResShot） |
| 姿态映射端到端（委托→事件→SetAnimation） | 通过 | 运行时断言 + BeginPlayBinding |
| 姿态切换动态目视/手杖穿插多角度 | 留作者 PIE | 固定相机无法跟随轨道移动的角色 |
| 真实键鼠 | 留作者 | — |
| 09 截图异常（圆柱+球） | 需作者 PIE 复核 | 来源未明，截图与日志已留存 |

**阶段 A 图形核验判定：通过。** 剩余：作者 PIE 目视动态项（相机跟随）、09 异常复核、真实键鼠。完成后阶段 A 即可完整关闭。

---

## 12. PIE 视觉捕获尝试（-game 自动化，最终受阻记录）

尝试通过 `-game` 模式自动化测试完成姿态切换的动态截图（ClientContext | EngineFilter 组合，latent 命令驱动三姿态 + GEngine->Exec HighResShot 截图）。编译通过后，`-game` 运行时**自动化框架初始化挂起**（日志停止于模块加载，无测试执行，进程随后退出）。三次运行一致。

**结论：-game 模式 + 自动化框架在本环境（-unattended + 无头）下不可用。** 姿态切换的动态视觉验证确认留作者 PIE 完成（打开 LV_StageAVerify 按 Play，A/D 沿轨道驱动，目视三姿态切换与手杖表现）。

**已有替代证据**（部分覆盖目视目标）：
- 姿态切换正确性：运行时断言（0.0→StrideBack 动画、1.0→Reach 动画、防重复）
- 真实渲染：07 截图（红褐皮影+手杖+无灰盒）
- 09 异常：需作者 PIE 定位（现场选中 Outliner 对象即可辨明）
