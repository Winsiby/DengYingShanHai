# 成林 Dev 资源持久化

日期：2026-10-04
状态：独立 Dev 数据型 Blueprint 已保存、冷读并通过隔离包加载验证。本步只完成 Dev 资源持久化，不改画面设计，不是正式美术、正式时长或正式第三幕。

责任人：Codex 唯一技术责任人，负责实现与验收；独立只读审查负责复查；WorkBuddy 只整理本文档。
事实来源：`Saved/Audit-2026-10-04-P03ForestAsset/WorkBuddy-Docs-Request.md` 与同目录 `Supervisor-Results.md` 脱敏摘要。未读取原始 UE 日志、账号、设备遥测或其他工作空间。

工程物理目录 `D:\灯影山海`，英文 junction `C:\UEProjects\DengYingShanHai` 指向同一目录。

> 永远不要以牺牲架构设计为代价追求功能；永远不要基于猜测进行权衡——必须与我确认。

---

## 1. 用户确认的范围

用户本轮「没问题，进入下一步」是**上一版原生成林 Dev 预览的人工确认**。

不是正式 P03 艺术签收、不是正式目标或时间签收、不是整局或现场包画面与性能签收。

本步保存资源**不会自动改善灰盒质感**。

## 2. 新资产

路径：`D:\灯影山海\Content\DengYingShanHai\Dev\M3\Forest\BP_DYForestPresentation_Dev.uasset`，28,558 bytes。

- 父类 `ADYForestPresentationActor`
- 保存从**真实 Resolve / A 接触**采集的 15 枝 authoring
- Engine Cylinder `/Engine/BasicShapes/Cylinder.Cylinder`
- material override = NULL，实际 fallback `/Engine/EngineMaterials/DefaultMaterial.DefaultMaterial`

Engine 灰盒形状只属 Dev 灰盒，**不是最终高质量树林美术**。

## 3. 蓝图只保存 authoring

保存内容：mesh、null material override、15 个 branch definitions（**normalized intervals，不是秒数**）。

不保存：运行 token / contact / session、动态组件、演出秒数。

未新增可执行图表链路。实际 Editor 测试 AddInfo：

```text
status=3（BS_UpToDate）
UbergraphPages=1, FunctionGraphs=1, recursive graphs=2
nodes=4, exec pins=4, exec links=0
```

即**有 2 个图表、4 个节点、4 个 exec pins、0 条 exec 连接**。
必须表述为「没有连接的执行逻辑」，**不是「没有图表/节点」**。

## 4. 完整链路

```text
新进程真实 Capture
  → 另一个进程单独创建 / 保存
    → 冷读已保存类实例
      → Presentation 用真实 Resolve 与 A 接触授权
        → C++ 原生组件 / 变换 / 真实投影
          → Clear / Reset / EndPlay 释放
```

不绕过授权，**不动态重写已保存类的布局**。

## 5. 三阶段真实证据

### 阶段一 CaptureRun1 / Capture.log

新 UE 进程完成真实 P02 Dev fixture Resolve，实际 Staff A 接触已接受 Z70 叙事地线，采集 15 枝投影布局。`Authoring-FromLiveContact.json` 与日志中唯一 `AuthoringCaptured` 结构一致，不保存资产。

原始 P02 fixture **不是正式 P03 谜题数据**。

### 阶段二 Asset-Save.log

另一个 UE commandlet 创建、编译、重读 CDO，然后**只保存这一个新 BP**。文件存在检测拒绝覆盖。不保存地图或旧资产。

### 阶段三 Preview-Run1 / Preview-Run2

分别启动新编辑器进程实际加载已保存 GeneratedClass，生成临时实例，**不写 mesh / layout**，只校验保存的 15 枝与同一真实接触样本一致。

由现有 Presentation 授权，C++ 应用实际枝组件变换，主灯提供真实投影，重复 Begin 拒绝。结束前复核 CDO 无 session / 组件、authoring 未污染，Clear 释放全部实际组件，恢复临时 Staff / 引用，旧 token 拒绝，End PIE 并退出。不保存资产。

| 预览 | 临时 Drop/Growth/FinalHold | 实际重复组件检查 | 结果 |
|---|---|---:|---|
| Run1 | 4/12/30 秒 | 54,402 | Completed(error=null)，全部组件已释放 |
| Run2 | 2/6/6 秒 | 19,210 | Completed(error=null)，全部组件已释放 |

Run2 补强终态断言：除 15 枝布局不变、CDO 会话和组件为空外，还复核 CDO mesh 仍为 Cylinder、material override 仍为 NULL。

两次是 Editor/Python 驱动的未保存地图 Dev 自动连续预览，**不是独立打包的连续演出，不是正式秒数或游戏 Restart 策略**。Codex 在 Run1 用官方 Computer Use 看到同版灰盒末态，**没有代签用户对新运行或正式美术/性能的验收**。

## 6. 编译、自动化与 Cook

| 项目 | 实际结果 | 证据 |
|---|---|---|
| 首次 Editor 编译 | exit6，测试 3 处 `FArrayProperty::Identical` 缺 `PortFlags`；仅补第三参 0 后重编 | `Build-Editor.log` |
| Editor 最终编译 | Result: Succeeded，exit0 | `Build-Editor-Final.log` |
| Game Development 编译 | Result: Succeeded，exit0 | `Build-GameDevelopment.log` |
| Game Shipping 编译 | Result: Succeeded，exit0；**未生成新 Shipping 包** | `Build-GameShipping.log` |
| 全量 Editor 自动化 | **70 succeeded / 0 failed / 0 warnings / 0 notRun / 0 inProcess** | `EditorTests/index.json` |
| Windows Development Cook/Stage/IoStore/Archive | UAT exit0，完整成功 markers；真实 Cook 命令含狭窄 Forest CookDir | `Package-UAT.log` |
| 独立包 Runtime 自动化 | **11 succeeded / 0 failed / 0 warnings / 0 notRun / 0 inProcess** | `PackagedTests/index.json` |

旧 68 项 Editor 测试集合全部保留且再次成功，只新增两项 ForestAsset。旧 10 项 ForestPresentation RunTest 正文与 Before 逐字符相等。

新 Runtime 资产测试实际读取保存类 / CDO，使用真实 Resolve / A 接触授权，检查 0/0.5/1 的实际 15 组件、资源、可见性、世界变换、投影端点和八角包络，以及 Clear / 重建 / Reset 与 CDO / 实例 authoring 隔离。Editor 另一新测试实际递归检查保存 Blueprint 图表。

包内 11 项 = 原 ForestPresentation 10 项 + 新 ForestAsset 运行测试 1 项。图表测试为 Editor-only，**不应声称包内跑了图表测试**。

## 7. Cook 与资产引用

旧地图**没有持久引用**新 BP。本步真实 Cook 指定 `/Game/DengYingShanHai/Dev/M3/Maps/LV_M3GeometryProbe`，并加额外实体目录 `Content/DengYingShanHai/Dev/M3/Forest`。

不改 Config、不 CookAll、**不宣称地图单独能带入该资产**。

最终包 exe 与本步 Game Development exe 的 SHA256 均为 `69CC74710775F91B90F1048F7D68F83118588197C29D81CA1E2019E81F58C8A7`。

## 8. NullRHI 的局限（不可混为一谈）

包用 NullRHI，不依赖 Editor/Python。

它证明：类、资源、几何、清理可以加载运行。

它**不证明**：屏幕渲染、森林画面、FPS、正式 P03 流程。

**本步包是 NullRHI 类加载 / 资源验收，不作成林图形验收，也不作正式可玩第三幕。**

## 9. 日志噪声

编译器 14.51.36260 高于 UE preferred 14.50.35717，**保留环境警告，不改工具链**。

原始日志**不是零 Error**：EditorTests 13、PackagedTests 1、Preview-Run1/2 各 13、Package-UAT 0；各日志 Ensure 统计 0。自动化报告的 0 失败与这些 Engine 初始化 / 非项目日志**不得混为一谈**。Preview 各 3 条 Warning，其他上述日志 Warning 0。**不得笼统写「所有日志零错误」。**

包内的 1 条 Error 已由 Codex 核实：AutomationController 无法加载 test-report HTML template，因此 HTML 报告没有生成；`PackagedTests/index.json` 实际存在且 11 项结果已解析。不能声称 HTML 报告生成成功。编辑器 13 条初始化自测 Error 不对应项目测试名失败。

## 10. 启动地址

`D:\灯影山海\Start-M3ForestAsset.cmd`

在文件资源管理器双击，先关闭 UE。它调用 Windows PowerShell 5.1，再启动本机 UE 预览，自动运行 / 恢复 / 退出。默认 2/6/6 秒只是预览值。

脚本为 ASCII，检查英文 junction 指向 D 物理目录、已有输出拒绝覆盖，环境变量仅对子进程临时设置后还原。

Codex 链接可能打开源代码。**不要把「看到代码」当执行成功，不要双击 PS1 期待执行。** 旧入口未改。

此入口**仍需本机 UE，不是独立游戏包**。

本步包的 runtime exe 仅作资源验收，不提供正式第三幕通关入口：
`Saved\Audit-2026-10-04-P03ForestAsset\DevelopmentPackage\Windows\DengYingShanHai\Binaries\Win64\DengYingShanHai.exe`

## 11. 本轮范围

8 个产品文件：测试 cpp 修改；新增 BP、`Create-P03ForestDevAsset.py`、`Preview-P03ForestAsset.py`、`Start-M3ForestAsset.ps1`、根 CMD、本文档；Plan 仅追加。

Build/FileOpenOrder 的两份工具日志在生成物白名单中单列；实测仅 `EditorOpenOrder.log` 哈希变化，`CookerOpenOrder.log` 哈希不变。不冒称整个 Build 目录未变化。

代码未改玩法。旧入口、地图、资产、配置不得变。未 Git 提交、未删用户文件。

Codex 已实际执行范围核验：191 个基线文件中修改 2 个产品文件、变化 1 份工具日志，其余 188 个哈希不变；新增 6 个产品文件，现有审计范围共 197 个文件，无缺失或越界修改。Plan 原 60,237 字节前缀完整保留。Git HEAD 不变、index 为空、原 86 项 dirty 全部保留，当前 91 项；未提交或清理用户改动。首次范围结果保留为 `FinalEvidence.json`，本次口径修订后的复核结果为 `FinalEvidence-Reviewed.json`，不覆盖旧证据。

## 12. 证据与回退

Before 保留 cpp 与 Plan 完整基线：`D:\灯影山海\Saved\Audit-2026-10-04-P03ForestAsset\Before\`

回退仅恢复本轮增量或移出本轮 6 个新增产品，并重新构建。**必须先确认，不执行删除 / reset / checkout。** 不动原 86 项 dirty，不 reset / checkout / commit，不删用户文件。

证据目录：`D:\灯影山海\Saved\Audit-2026-10-04-P03ForestAsset\`

## 13. 协作约定

WorkBuddy 输入框有限制，**上限未知**。后续一律短摘要加本地脱敏任务文件，**不把长报告粘入输入框**。

## 14. 未完成

按 Q1–Q5 逐项确认：

- Q1 正式 target / tolerance / hold
- Q2 落杖秒数
- Q3 成林秒数 / 超时
- Q4 Skip / R
- Q5 整局重启方式

仍待后续：正式皮影 / 林影 / 剧场免费合规美术与声音、完整三幕 5–8 分钟、性能、**包内图形**与现场人工验收。

**不得自行把灰盒当正式艺术成果，团队美术负责人不变。**

## 15. 状态

本步骤完成，整体 P03 计划仍未完成。成林 Dev 资源已保存、冷读并通过隔离包 NullRHI 加载验证。本步不交付正式演出、正式美术、正式时长或 P03 目标参数。本文未代签正式参赛作品或尚未进行的人工验收；上一版 Dev 预览的用户确认按第 1 节记录。

AI 记录：Codex 实施，独立只读审查，WorkBuddy 文档整理。不声称已完成赛事 AI 申报。
