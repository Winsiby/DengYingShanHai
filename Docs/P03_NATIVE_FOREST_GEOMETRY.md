# P03 原生成林几何接口（无状态 Blueprint/C++ 库）

日期：2026-10-04
状态：**原生几何接口已实现并通过自动化与三目标实编验证（58 Success / 0 Failed = 10 新 + 48 原有）。库尚未挂接 Blueprint / Forest Actor，现有 Python 连续预览仍是旧实现。**
负责人：Codex 负责实现、测试与验收（含独立只读代理审查）；WorkBuddy 仅整理事实文档。
依据：根 `AGENTS.md`，以及本机 `Saved/Audit-2026-10-04-P03NativeForest/` 内
`Supervisor-Results.md`（脱敏摘要）、`Execution-Contract.md`、`Plan-Before.md`；
新增几何源码只读核对。

> **本文档事实以 Supervisor 脱敏摘要与源码为准。**
> 未读取原始 UE 日志，未转录 HTTP 账号或遥测字段。

> *永远不要以牺牲架构设计为代价追求功能；永远不要基于猜测进行权衡——必须与我确认。*

---

## 1. 用户反馈与本轮定位

- 用户测试独立连续 Dev 预览后表示**「测试完毕，勉强达到效果，可以继续下一步」**。
- 该反馈记录为：**连续因果基本可读，视觉仍须提升**。
- **不是**正式美术签收、**不是**完整 P03、**不是**秒数签收、**不是**目标参数签收。
  **「勉强达到效果」不构成正式视觉或节奏验收通过。**
- **后续视觉提升目标明确保留**；正式 **Q1–Q5**（目标/容差、落杖与成林秒数/超时、
  Skip/R 与整局重启等）**仍待确认**。
- 本步只交付**几何节点库**，不接表现入口、不交付演出。

## 2. 新增文件（仅 3 个源码）

| 文件 | 字节 |
|---|---|
| `Source/DengYingShanHai/Public/Stage/DYForestGeometryLibrary.h` | 4,228 |
| `Source/DengYingShanHai/Private/Stage/DYForestGeometryLibrary.cpp` | 8,546 |
| `Source/DengYingShanHai/Private/Tests/DYForestGeometryAutomationTests.cpp` | 20,571 |

**源码仅新增上述 3 个文件；文档另新增本文并追加接入计划**。不改 M2、地图、主灯、镜头、曝光、输入、15Hz 或旧预览入口；
**不新增 Actor、模块或插件**。

## 3. 职责与寿命

`UDYForestGeometryLibrary` 是**无状态** `UBlueprintFunctionLibrary`：

- **无 World、无 Actor 引用、无时钟、无资源加载、无输入、无委托、无 Tick、无持久状态**；
- **不生长 Actor、不推进谜题、不推进 Finale、不消费 Token**；
- **不硬编码** 15 枝、Z70、正式林相或演出时长。

**两个公开函数**：

| 函数 | 职责 |
|---|---|
| `IsForestLayoutValid(Definition)` | 校验作者提供的枝段定义是否合法 |
| `SampleForestGeometry(Contact, Definition, NormalizedGrowth, MeshLocalMin, MeshLocalMax)` | 输出真实 A 物理根处连通的枝段变换与投影包络 |

## 4. 数据字段与局部坐标单位

### 4.1 `FDYForestBranchDefinition`（作者输入）

| 字段 | 含义与约束 |
|---|---|
| `ParentIndex` | **首枝必须是唯一根（`INDEX_NONE`）**；其余父索引必须**先于**子枝出现 |
| `StartScreenOffset` | **接收面局部 `+Y`/`+Z` 单位**——**不是 UV，也不是世界厘米** |
| `EndScreenOffset` | 同上；**不得为零** |
| `DiameterWorld` | A 端源深度处的**物理直径**（`Units = cm`）；必须**有限且 > 0**；**不隐含任何默认美术尺寸** |
| `GrowthBegin` / `GrowthEnd` | **归一化表现进度**，`0 ≤ Begin < End ≤ 1`；**绝不是秒数或谜题阈值** |

### 4.2 `FDYForestBranchGeometry`（输出）

| 字段 | 含义 |
|---|---|
| `bVisible` | 长度 > epsilon 才可见 |
| `Portion` | 该枝段在当前归一化进度下的完成比例（钳位 0–1） |
| `StartWorld` / `EndWorld` | 实际世界端点；`EndWorld` 是**按 Portion 插值后的当前终点** |
| `MeshWorldTransform` | **网格组件的世界变换**——**不是其 owner Actor 的变换**；隐藏枝段未定义 |
| `ProjectedMin` / `ProjectedMax` | **八个局部 bounds 角的保守投影**（幕局部 Y/Z）——**不是阴影像素、不是遮挡** |

### 4.3 `FDYForestGeometrySample`（输出容器）

`Status` / `ContactToken` / `PhysicalRoot` / `ShadowRoot` / `Branches`。

### 4.4 `EDYForestGeometryStatus`（7 态）

```text
InvalidContactGeometry | InvalidLayout | InvalidMeshBounds
InvalidProgress | OutsideScreen | InvalidComputedGeometry | Valid
```

## 5. 关键实现事实

### 5.1 接触复核（`CheckContact`）

进入几何计算前**重新验证**接触快照，而非信任输入：

- `bHasContact`、`Token` 有效、`Projection.bHasGeometry`、`Staff.bIsValid`；
- 变换**无 NaN 且旋转已归一化**；Staff bounds 可用；`EndA.Status == OnScreen`；
- **由 Staff 自身实际 bounds 与组件变换重建 A/B 两端**，与 `EndAWorld`／`EndBWorld` 比对；
- **物理根取 `Staff.EndAWorld`**，**幕上根取接触投影**；
- 两者按**实际 `ScreenTransform` 与重算 `RayParameter`** 逆解到**同一源深度**。

### 5.2 屏幕偏移反解（`Lift`）

把**接收面局部 `+Y`/`+Z` 偏移**沿射线反解回物理源深度：
`Source = Emitter + (Target − Emitter) / Root.RayParameter`，并**回投影验证命中**。

### 5.3 枝段朝向与网格对齐

- 枝段网格**以局部 Z 为成长轴**；
- **偏心 bounds 用完整中心补偿**，使实际 bounds 两端**精确落在计划起点与当前终点**；
- 使用 `MakeFromZ(Direction / Length)` 传入**单位轴**——源码注释说明：
  安全归一化使用长度平方阈值，若直接传方向向量，**刚萌发的极短枝会得到零基**。

### 5.4 隐藏枝段

`Length ≤ epsilon` 时输出**隐藏标志 + 未应用的单位变换**，
**不生成可见的零长度网格**。

## 6. 失败闭合（fail-closed）

| 触发条件 | 返回状态 |
|---|---|
| 接触快照任一复核不通过 | `InvalidContactGeometry` |
| 定义非法（空数组、根不唯一、父索引越界、连接点不匹配、`GrowthEnd ≤ GrowthBegin`、直径非正、**向梢增粗**、**重复终点**、**回到根**） | `InvalidLayout` |
| 网格 bounds 不可用 | `InvalidMeshBounds` |
| 进度非有限 | `InvalidProgress` |
| 任一端点或任一 8 角投影越幕 | `OutsideScreen` |
| 长度非有限或变换校验失败 | `InvalidComputedGeometry` |

**失败时返回空枝数组，不泄漏早先结果**（源码以 `Failure(...)` 构造全新样本）。

**合法非空随机身份也能得到数学 `Valid`**——测试明确证明该边界。
库**只复制诊断身份**（`ContactToken` 为**诊断身份副本**），**不确认 Token 当前有效**。

## 7. 通信与授权边界

- `SampleForestGeometry` 是 `BlueprintPure`，**输出纯值**；
- **未来调用方必须经 Presentation 接受并再次核对当前接触/Resolve 身份**；
- **`TryAccept` 返回 `true` 后仍可能被同步回调复位**；
- 因此**本库不构成身份授权**；`ValuePurityAndAuthorityBoundary` 测试锁定该边界。

## 8. 验证结果

### 8.1 三目标实编（均退出码 0、`Result: Succeeded`）

| 日志 | 目标 |
|---|---|
| `Build-Editor-Verified.log` | `DengYingShanHaiEditor` Win64 **Development** |
| `Build-GameDevelopment-Final.log` | `DengYingShanHai` Win64 **Development** |
| `Build-GameShipping.log` | `DengYingShanHai` Win64 **Shipping** |

- 均使用本机 **UE 5.8.3**、英文 junction、`-NoUBA -WaitMutex`、
  Windows SDK 10.0.26100.0、MSVC 14.51.36260；
- 保留**非首选编译器**与 **Engine `Character.h` 既有弃用警告**；**不改引擎或环境**。
- **Game 编译不是 Cook / Package / 运行成功证据。**

### 8.2 自动化：**58 Success / 0 Failed**

`Automation-Final.log`：`UnrealEditor-Cmd -NullRHI -unattended`、
`Automation RunTests DengYingShanHai`、`TestExit="Automation Test Queue Empty"`；
**58 tests performed、正常 TestExit、0 ensure**。

整日志另有 13 条本机既有 Condition failed Error；0 Failed 不等于整日志零 Error。

**10 项新测试**（前缀 `DengYingShanHai.P03.ForestGeometry`）：

1. `PhysicalRootAndInverseProjection`
2. `RotatedScaledReceiver`
3. `ActualAndOffCenterMeshBounds`（**加载实际 Engine Cylinder**）
4. `NormalizedParentBeforeChild`
5. `InvalidTopologyAndAuthoring`
6. `InvalidInputFailsClosed`
7. `EightCornerEnvelopeAndReceiverLimits`
8. `ValuePurityAndAuthorityBoundary`
9. `TinyEmergenceKeepsValidAxis`
10. `TransformedStaffAndOppositeReceiverFace`

### 8.3 首轮 56 不是最终

- 首次仅 8 项新测试时**全 56 Success**；
- 审查发现 `MakeFromZ` 默认 `GetSafeNormal` 的**长度平方阈值可能把微小萌发 Direction 清成零**；
- **已改为传 `Direction`／`Length`**，**不改变可见 epsilon**；
- 随后**新增**极小根/子枝、Staff 自身旋转/负缩放、反向接收面、
  首段有效但后段角体积失败等用例，**再复编全 58 Success**；
- **初轮日志留存**，**不把首轮通过冒称已经覆盖微小生长**。

### 8.4 独立只读审查

独立代理只读审查；**源码修改、构建与验收均由 Codex 负责**。

## 9. 没有做的测试（本步未覆盖）

- **无新增 GUI / 阴影画面验证**；
- **无 Cook、无 Stage、无 Package**；
- **无性能测量**（帧率 / GPU）；
- **无人工第三幕检查**；
- **旧包不含新接口**；
- **八角包络不是像素、半影、遮挡或视觉质量验收**；
  **`Valid` 仅指当前进度样本**；**隐藏枝段只检查完整中心线，不检查未来全部进度的八角体积**；
- 现有 **Python 连续预览仍是旧实现，未改为调用本库**。

### 后续 Development 包验证程序（未执行）

1. 先完成 Dev/M3 表现接入，明确包含新表现实例的地图、资源引用与可重复测试入口。
2. 显式选择该地图作为 Cook 根，Build → Cook → Stage → Package 到新的隔离目录；不使用 cookall，不覆盖旧包。
3. 脱离 Editor/Python 启动该 Development 包，验证实际 A 接触后才生长、实体根/幕上根对应、枝段连通、真实主灯阴影及正常退出。
4. 验证身份失效/对象卸载时停止更新并清理；正式 Skip/R/重启行为须先确认后再验收，不能把 Dev 清理冒称正式终态。保留运行日志、构建身份和目标机检查记录。

上述为后续验证顺序，不代表本轮已打包或已接入表现 Actor。

## 10. 真实 Engine Cylinder 的使用边界

测试 `ActualAndOffCenterMeshBounds` **加载实际 Engine Cylinder**。
**这只发生在自动化测试中，不是新运行库的硬资产依赖。**

- 本库是**纯代码库**，不加载资产；
- **未下载新资产、未付费**；
- 本轮**不新增许可条目**（沿用已登记的引擎灰盒登记）。

## 11. 待接 Blueprint 小步（下一技术步，本轮未实现）

**下一小步**：在 `Dev/M3` 用**显式 Presentation 调用**接入一个**仅负责**：

- 枝段显示；
- 归一化进度；
- 清理；

的**表现 Actor**，**复用本库**，并**继续保留真实同主灯投影**。

**具体 Actor 生命周期与中断清理需列出后再实现。**

**明确未完成**：

- 新库**未挂接 Blueprint**；
- **Forest Actor 不存在**（本轮不新增 Actor）；
- 正式目标/容差、落杖与成林秒数/超时、Skip/R 与整局重启**仍按 Q1–Q5 逐项确认**；
- **视觉廉价感仍需正式免费合规美术、林相与剧场材质层改善**，
  **不以几何库验收替代**。

> 本文档**不臆造** Blueprint 已接入、Forest Actor 存在、Token 被纯库授权，
> 或正式终态/秒数/P03 容差已定。

## 12. 范围与保护

- 文档前哈希：**144 个原产品 SHA 全相同、0 缺失**；**新增 3 个源码**；
- `Source`（新增 3 个除外）、`Content`、`Config`、`Scripts`、`.uproject`、启动器**未写入**；
- **无 Git 写入、无删除、无提交**；用户脏工作区不覆盖；
- **打包验证程序未执行**；
- **不开启下步开发**；最终五项产品白名单、原 Plan 完整字节前缀、HEAD 与空 index
  由 Codex 在本文档交付后检查。

## 13. 状态

**部分完成**：**原生无状态几何接口**已实现并通过 **58 Success / 0 Failed** 与三目标实编。
**尚未挂接 Blueprint / Forest Actor，现有 Python 连续预览仍是旧实现。**
本步不交付演出、正式美术、正式时长或 P03 目标参数。
本文档不构成参赛作品、视觉质量或节奏验收结论，**未代签任何人工确认**。

AI 使用记录：Codex 实现 / 测试 / 独立只读代理审查；WorkBuddy 只整理两份白名单文档，
Codex 终审。仅项目路径与脱敏技术摘要授权交接，**不传密钥账号，不读取原始 UE 遥测日志**。
**不冒充已完成赛事 AI 申报。**
